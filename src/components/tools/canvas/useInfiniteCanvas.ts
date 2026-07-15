"use client";

import { useCallback, useEffect, useRef, useState } from "react";

/**
 * Reusable infinite-canvas camera for SVG tools.
 *
 * The math and gesture handling are lifted from the projection whiteboard's
 * DrawingOverlay (world point (wx, wy) renders at screen (wx*zoom + tx,
 * wy*zoom + ty)) and packaged as a standalone hook so any canvas tool can
 * pan/pinch/wheel-zoom without dragging in any drawing state.
 *
 * The camera lives in a ref so pointer/wheel gestures can update it at 60+
 * fps without thrashing React; callers re-render by reading `tick` (bumped
 * via `bump()`). The owning component wires the SVG's pointer handlers and
 * decides gesture precedence (item drag vs. pan) — this hook only exposes
 * the primitives (screenToWorld, zoomAt, two-finger pan/pinch, spacebar
 * pan, wheel) and the shared refs.
 */

export interface Camera {
  tx: number;
  ty: number;
  zoom: number;
}

export const ZOOM_MIN = 0.2;
export const ZOOM_MAX = 6;

export interface InfiniteCanvas {
  svgRef: React.RefObject<SVGSVGElement | null>;
  cameraRef: React.RefObject<Camera>;
  tick: number;
  bump: () => void;
  /** Screen pixel (relative to the SVG rect) → world coordinate. */
  screenToWorld: (sx: number, sy: number) => { x: number; y: number };
  /** Convert a screen-pixel delta to a world-unit delta (÷ zoom). */
  toWorldScale: (px: number) => number;
  /** Screen point of a pointer event relative to the SVG's top-left. */
  localPoint: (e: { clientX: number; clientY: number }) => { sx: number; sy: number };
  zoomAt: (anchorX: number, anchorY: number, factor: number) => void;
  resetView: () => void;
  fitToBounds: (b: { x: number; y: number; width: number; height: number }) => void;
  spaceHeldRef: React.RefObject<boolean>;
  pointersRef: React.RefObject<Map<number, { x: number; y: number }>>;
  gestureRef: React.RefObject<GestureState | null>;
  panDragRef: React.RefObject<PanDrag | null>;
  /** Register/update/drop a pointer for pinch + two-finger tracking. */
  trackPointer: (id: number, sx: number, sy: number) => void;
  dropPointer: (id: number) => void;
  /** Begin a two-finger gesture from the current two tracked pointers. */
  beginGesture: () => void;
  /** Drive camera from a live two-finger move. Returns true if it acted. */
  updateGesture: () => boolean;
}

type GestureState = {
  startCam: Camera;
  startMid: { x: number; y: number };
  startDist: number;
};
type PanDrag = { startX: number; startY: number; startCam: Camera };

export function useInfiniteCanvas(active = true): InfiniteCanvas {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const cameraRef = useRef<Camera>({ tx: 0, ty: 0, zoom: 1 });
  const [tick, setTick] = useState(0);
  const bump = useCallback(() => setTick((t) => t + 1), []);

  const pointersRef = useRef<Map<number, { x: number; y: number }>>(new Map());
  const gestureRef = useRef<GestureState | null>(null);
  const spaceHeldRef = useRef(false);
  const panDragRef = useRef<PanDrag | null>(null);

  const localPoint = useCallback((e: { clientX: number; clientY: number }) => {
    const rect = svgRef.current?.getBoundingClientRect();
    return { sx: e.clientX - (rect?.left ?? 0), sy: e.clientY - (rect?.top ?? 0) };
  }, []);

  const screenToWorld = useCallback((sx: number, sy: number) => {
    const c = cameraRef.current;
    return { x: (sx - c.tx) / c.zoom, y: (sy - c.ty) / c.zoom };
  }, []);

  const toWorldScale = useCallback((px: number) => px / cameraRef.current.zoom, []);

  const zoomAt = useCallback((anchorX: number, anchorY: number, factor: number) => {
    const c = cameraRef.current;
    const newZoom = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, c.zoom * factor));
    const wx = (anchorX - c.tx) / c.zoom;
    const wy = (anchorY - c.ty) / c.zoom;
    cameraRef.current = { zoom: newZoom, tx: anchorX - wx * newZoom, ty: anchorY - wy * newZoom };
    setTick((t) => t + 1);
  }, []);

  const resetView = useCallback(() => {
    cameraRef.current = { tx: 0, ty: 0, zoom: 1 };
    setTick((t) => t + 1);
  }, []);

  const fitToBounds = useCallback(
    (b: { x: number; y: number; width: number; height: number }) => {
      const svg = svgRef.current;
      if (!svg || b.width <= 0 || b.height <= 0) return;
      const rect = svg.getBoundingClientRect();
      const zoom = Math.max(
        ZOOM_MIN,
        Math.min(ZOOM_MAX, Math.min(rect.width / b.width, rect.height / b.height) * 0.92)
      );
      const cx = b.x + b.width / 2;
      const cy = b.y + b.height / 2;
      cameraRef.current = { zoom, tx: rect.width / 2 - cx * zoom, ty: rect.height / 2 - cy * zoom };
      setTick((t) => t + 1);
    },
    []
  );

  const trackPointer = useCallback((id: number, sx: number, sy: number) => {
    pointersRef.current.set(id, { x: sx, y: sy });
  }, []);

  const dropPointer = useCallback((id: number) => {
    pointersRef.current.delete(id);
    if (pointersRef.current.size < 2) gestureRef.current = null;
  }, []);

  const beginGesture = useCallback(() => {
    const pts = Array.from(pointersRef.current.values());
    if (pts.length < 2) return;
    const [p0, p1] = pts;
    const midX = (p0.x + p1.x) / 2;
    const midY = (p0.y + p1.y) / 2;
    const dist = Math.max(1, Math.hypot(p1.x - p0.x, p1.y - p0.y));
    gestureRef.current = {
      startCam: { ...cameraRef.current },
      startMid: { x: midX, y: midY },
      startDist: dist,
    };
    setTick((t) => t + 1);
  }, []);

  const updateGesture = useCallback(() => {
    if (pointersRef.current.size < 2 || !gestureRef.current) return false;
    const pts = Array.from(pointersRef.current.values());
    const [p0, p1] = pts;
    const midX = (p0.x + p1.x) / 2;
    const midY = (p0.y + p1.y) / 2;
    const dist = Math.max(1, Math.hypot(p1.x - p0.x, p1.y - p0.y));
    const g = gestureRef.current;
    const newZoom = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, (g.startCam.zoom * dist) / g.startDist));
    const wx = (g.startMid.x - g.startCam.tx) / g.startCam.zoom;
    const wy = (g.startMid.y - g.startCam.ty) / g.startCam.zoom;
    cameraRef.current = { tx: midX - wx * newZoom, ty: midY - wy * newZoom, zoom: newZoom };
    setTick((t) => t + 1);
    return true;
  }, []);

  // Spacebar → pan mode. Ref (no re-render) but bump tick so the cursor
  // flips between default and grab.
  useEffect(() => {
    if (!active) return;
    const onDown = (e: KeyboardEvent) => {
      if (e.repeat) return;
      if (e.code === "Space" || e.key === " ") {
        // Don't hijack space while typing in a field.
        const t = e.target as HTMLElement | null;
        if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
        if (spaceHeldRef.current) return;
        spaceHeldRef.current = true;
        setTick((n) => n + 1);
        e.preventDefault();
      }
    };
    const onUp = (e: KeyboardEvent) => {
      if (e.code === "Space" || e.key === " ") {
        spaceHeldRef.current = false;
        panDragRef.current = null;
        setTick((n) => n + 1);
      }
    };
    window.addEventListener("keydown", onDown, true);
    window.addEventListener("keyup", onUp, true);
    return () => {
      window.removeEventListener("keydown", onDown, true);
      window.removeEventListener("keyup", onUp, true);
    };
  }, [active]);

  // Wheel: zoom toward the cursor. Spinning the wheel (or trackpad
  // pinch, which browsers report as ctrl+wheel) zooms in/out rather than
  // scrolling the canvas — panning is right-click / space / two-finger
  // drag. Raw listener with {passive:false} so we can preventDefault the
  // page.
  useEffect(() => {
    if (!active) return;
    const svg = svgRef.current;
    if (!svg) return;
    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      const rect = svg.getBoundingClientRect();
      const sx = e.clientX - rect.left;
      const sy = e.clientY - rect.top;
      zoomAt(sx, sy, Math.exp(-e.deltaY * 0.0015));
    };
    svg.addEventListener("wheel", onWheel, { passive: false });
    return () => svg.removeEventListener("wheel", onWheel);
  }, [active, zoomAt]);

  return {
    svgRef,
    cameraRef,
    tick,
    bump,
    screenToWorld,
    toWorldScale,
    localPoint,
    zoomAt,
    resetView,
    fitToBounds,
    spaceHeldRef,
    pointersRef,
    gestureRef,
    panDragRef,
    trackPointer,
    dropPointer,
    beginGesture,
    updateGesture,
  };
}
