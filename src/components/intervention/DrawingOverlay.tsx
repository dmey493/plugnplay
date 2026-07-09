"use client";

import { useCallback, useEffect, useRef, useState } from "react";

/**
 * Whiteboard-style drawing overlay for the projection.
 *
 * SVG strokes captured from pointer events (mouse / finger / stylus).
 * Rendered as <polyline> elements so we can erase per-stroke and undo
 * cheaply. Lives above the projection content card via fixed positioning;
 * pointer-events toggle on/off so the underlying problem stays clickable
 * when the teacher isn't actively drawing.
 *
 * Strokes persist per slide: when `wipeKey` changes, the current strokes
 * are stashed under the old key and the new key's strokes (if any) are
 * restored — so a teacher can flip back to a problem and their annotations
 * are still there. "Clear" wipes only the current slide.
 */

type Tool = "pen" | "highlighter" | "eraser";

interface Stroke {
  id: string;
  points: string;          // SVG points attribute string: "x,y x,y x,y"
  color: string;
  width: number;
  opacity: number;
  tool: Tool;
}

const PEN_COLORS = ["#111827", "#dc2626", "#2563eb", "#16a34a"]; // black, red, blue, green
const HIGHLIGHTER_COLOR = "#facc15";

interface Props {
  active: boolean;
  /** Setter for the parent's drawing-active state — used by the palette's
   *  Done button to flip the toggle off without touching parent internals. */
  setActive: (next: boolean) => void;
  /** Slide identity. When this string changes, the current strokes are
   *  stashed under the old key and the new key's strokes are restored.
   *  Pass `${item}-${session}-${mode}` from the parent. */
  wipeKey: string;
  /** When true, the canvas is an infinite world: strokes are stored in
   *  world coordinates, the view supports pan + pinch/wheel zoom, and a
   *  dot grid scrolls behind the strokes. Defaults to false so existing
   *  callers (the projection draw mode) keep the fixed-viewport
   *  behaviour they were built for. */
  infinite?: boolean;
}

// Camera model for infinite mode. World point (wx, wy) renders at
// screen point (wx*zoom + tx, wy*zoom + ty). Pan moves (tx, ty); pinch
// changes zoom. Stored in a ref to avoid React-state churn during
// gestures — we `setTick` to re-render when needed.
interface Camera {
  tx: number;
  ty: number;
  zoom: number;
}
const ZOOM_MIN = 0.2;
const ZOOM_MAX = 6;

export default function DrawingOverlay({
  active,
  setActive,
  wipeKey,
  infinite = false,
}: Props) {
  const [strokes, setStrokes] = useState<Stroke[]>([]);
  const [tool, setTool] = useState<Tool>("pen");
  const [color, setColor] = useState<string>(PEN_COLORS[0]);
  const drawingRef = useRef<{ id: string; pts: string } | null>(null);
  const svgRef = useRef<SVGSVGElement | null>(null);
  // Stroke updates during a drag should re-render but not at react-state
  // throughput — we batch via a tick counter so the in-progress stroke
  // appears live while pointermove fires.
  const [tick, setTick] = useState(0);
  // Palette position. `null` = default bottom-center placement. After a
  // drag we store explicit {x, y} viewport pixels. The position resets
  // whenever drawing is toggled off (see effect below), so the next time
  // the teacher opens the palette it's back in the default spot — easy
  // recovery if they ever drag it somewhere awkward.
  const [paletteXY, setPaletteXY] = useState<{ x: number; y: number } | null>(null);
  const paletteDragOffset = useRef<{ x: number; y: number } | null>(null);
  const paletteRef = useRef<HTMLDivElement | null>(null);

  // Infinite-canvas camera. Lives in a ref so pan/pinch/wheel can update
  // it at 60+ fps without thrashing React state; we bump `tick` to
  // re-render the SVG transform. Initial origin is (0,0) at top-left of
  // the viewport with zoom = 1 (1 screen px = 1 world px), so when
  // `infinite=false` the math is identity and behaves like the legacy
  // viewport-locked mode.
  const cameraRef = useRef<Camera>({ tx: 0, ty: 0, zoom: 1 });
  // Multi-pointer tracking for pinch + two-finger pan. Maps pointerId →
  // last-seen screen coords. Only consulted when `infinite=true`.
  const pointersRef = useRef<Map<number, { x: number; y: number }>>(new Map());
  // Cached two-finger gesture origin so each move computes a delta
  // relative to gesture start, not pointermove-to-pointermove (which
  // would drift). Null when fewer than 2 pointers are down.
  const gestureRef = useRef<
    | null
    | {
        startCam: Camera;
        startMid: { x: number; y: number };
        startDist: number;
      }
  >(null);
  // Spacebar-held flag — while held, primary pointer pan instead of
  // drawing. Two-finger pan still works without space.
  const spaceHeldRef = useRef(false);
  // True while the pen is currently driving a pan (space+drag). When
  // active we render a grab cursor and skip stroke creation.
  const panDragRef = useRef<null | { startX: number; startY: number; startCam: Camera }>(null);

  // Convert a screen pixel coord (relative to the SVG bounding rect) to
  // a world coordinate via the inverse camera transform. When
  // infinite=false this is identity, so the legacy code path is
  // unchanged.
  const screenToWorld = useCallback((sx: number, sy: number) => {
    if (!infinite) return { x: sx, y: sy };
    const c = cameraRef.current;
    return { x: (sx - c.tx) / c.zoom, y: (sy - c.ty) / c.zoom };
  }, [infinite]);

  // Apply a zoom delta about a screen-pixel anchor (keeps the world
  // point under the cursor stationary). Clamped to [ZOOM_MIN, ZOOM_MAX].
  const zoomAt = useCallback(
    (anchorX: number, anchorY: number, factor: number) => {
      const c = cameraRef.current;
      const newZoom = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, c.zoom * factor));
      const wx = (anchorX - c.tx) / c.zoom;
      const wy = (anchorY - c.ty) / c.zoom;
      cameraRef.current = {
        zoom: newZoom,
        tx: anchorX - wx * newZoom,
        ty: anchorY - wy * newZoom,
      };
      setTick((t) => t + 1);
    },
    []
  );

  const resetView = useCallback(() => {
    cameraRef.current = { tx: 0, ty: 0, zoom: 1 };
    setTick((t) => t + 1);
  }, []);

  // Reset palette to default placement whenever drawing turns off.
  useEffect(() => {
    if (!active) setPaletteXY(null);
  }, [active]);

  // Per-slide stroke persistence: on navigation, stash the outgoing
  // slide's strokes and restore the incoming slide's (empty for a slide
  // never drawn on). strokesRef mirrors state so the stash sees the
  // latest strokes without making this effect depend on `strokes`.
  const strokesRef = useRef<Stroke[]>([]);
  useEffect(() => { strokesRef.current = strokes; }, [strokes]);
  const strokeStore = useRef<Record<string, Stroke[]>>({});
  const prevKeyRef = useRef(wipeKey);
  useEffect(() => {
    const prev = prevKeyRef.current;
    if (prev === wipeKey) return;
    strokeStore.current[prev] = strokesRef.current;
    prevKeyRef.current = wipeKey;
    setStrokes(strokeStore.current[wipeKey] ?? []);
    drawingRef.current = null;
  }, [wipeKey]);

  // Esc exits draw mode (without leaving the projection page).
  useEffect(() => {
    if (!active) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        e.stopPropagation();
        setActive(false);
      }
    };
    window.addEventListener("keydown", onKey, true);
    return () => window.removeEventListener("keydown", onKey, true);
  }, [active, setActive]);

  // Spacebar tracking — only meaningful in infinite mode where space+drag
  // pans the camera. Tracked via a ref (no re-render) but we bump tick
  // on transitions so the cursor flips between crosshair and grab.
  useEffect(() => {
    if (!infinite || !active) return;
    const onDown = (e: KeyboardEvent) => {
      // Ignore key repeats so the cursor swap only happens on first
      // press. Some browsers will also fire Space as " " — handle both.
      if (e.repeat) return;
      if (e.code === "Space" || e.key === " ") {
        if (spaceHeldRef.current) return;
        spaceHeldRef.current = true;
        setTick((t) => t + 1);
        // Prevent scroll-page-on-space; we own the canvas.
        e.preventDefault();
      }
    };
    const onUp = (e: KeyboardEvent) => {
      if (e.code === "Space" || e.key === " ") {
        spaceHeldRef.current = false;
        panDragRef.current = null;
        setTick((t) => t + 1);
      }
    };
    window.addEventListener("keydown", onDown, true);
    window.addEventListener("keyup", onUp, true);
    return () => {
      window.removeEventListener("keydown", onDown, true);
      window.removeEventListener("keyup", onUp, true);
    };
  }, [infinite, active]);

  // SVG viewBox tracks viewport so coordinates land at pointer location.
  // Refs the SVG width/height directly via 100% / 100%; the viewBox we
  // compute on the fly so points use raw pixel coords.
  const onPointerDown = useCallback(
    (e: React.PointerEvent<SVGSVGElement>) => {
      if (!active) return;
      const svg = svgRef.current;
      if (!svg) return;
      const rect = svg.getBoundingClientRect();
      const sx = e.clientX - rect.left;
      const sy = e.clientY - rect.top;

      // INFINITE MODE — track every pointer for two-finger pan/pinch.
      // When 2+ pointers are down, ANY in-progress single-pointer stroke
      // gets abandoned and the two-finger gesture takes over.
      if (infinite) {
        pointersRef.current.set(e.pointerId, { x: sx, y: sy });
        if (pointersRef.current.size >= 2) {
          // Drop any in-progress stroke; starting gesture instead.
          drawingRef.current = null;
          panDragRef.current = null;
          const pts = Array.from(pointersRef.current.values());
          const p0 = pts[0];
          const p1 = pts[1];
          const midX = (p0.x + p1.x) / 2;
          const midY = (p0.y + p1.y) / 2;
          const dx = p1.x - p0.x;
          const dy = p1.y - p0.y;
          const dist = Math.max(1, Math.hypot(dx, dy));
          gestureRef.current = {
            startCam: { ...cameraRef.current },
            startMid: { x: midX, y: midY },
            startDist: dist,
          };
          setTick((t) => t + 1);
          return;
        }

        // Single pointer + space held = pan-drag (mouse-friendly).
        if (spaceHeldRef.current) {
          svg.setPointerCapture(e.pointerId);
          panDragRef.current = {
            startX: sx,
            startY: sy,
            startCam: { ...cameraRef.current },
          };
          return;
        }
      }

      // STROKE PATH — convert screen coords to world coords (identity in
      // legacy mode) and begin a polyline. Store points as world-space
      // strings; the camera transform on the rendered group handles
      // putting them on screen.
      svg.setPointerCapture(e.pointerId);
      const w = screenToWorld(sx, sy);
      const id = `s-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
      drawingRef.current = { id, pts: `${w.x},${w.y}` };
      setTick((t) => t + 1);
    },
    [active, infinite, screenToWorld]
  );

  const onPointerMove = useCallback(
    (e: React.PointerEvent<SVGSVGElement>) => {
      if (!active) return;
      const svg = svgRef.current;
      if (!svg) return;
      const rect = svg.getBoundingClientRect();
      const sx = e.clientX - rect.left;
      const sy = e.clientY - rect.top;

      // INFINITE MODE — update pointer tracking + handle gestures first.
      if (infinite) {
        if (pointersRef.current.has(e.pointerId)) {
          pointersRef.current.set(e.pointerId, { x: sx, y: sy });
        }

        // Two-finger pan + pinch: drive camera from the change in
        // midpoint (pan) and distance (zoom) since gesture start.
        if (pointersRef.current.size >= 2 && gestureRef.current) {
          const pts = Array.from(pointersRef.current.values());
          const p0 = pts[0];
          const p1 = pts[1];
          const midX = (p0.x + p1.x) / 2;
          const midY = (p0.y + p1.y) / 2;
          const dx = p1.x - p0.x;
          const dy = p1.y - p0.y;
          const dist = Math.max(1, Math.hypot(dx, dy));
          const g = gestureRef.current;
          const factor = dist / g.startDist;
          const newZoom = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, g.startCam.zoom * factor));
          // Anchor zoom on the gesture-start midpoint so the world
          // point under the user's fingers stays under them.
          const wx = (g.startMid.x - g.startCam.tx) / g.startCam.zoom;
          const wy = (g.startMid.y - g.startCam.ty) / g.startCam.zoom;
          const tx = midX - wx * newZoom;
          const ty = midY - wy * newZoom;
          cameraRef.current = { tx, ty, zoom: newZoom };
          setTick((t) => t + 1);
          return;
        }

        // Single-pointer pan (space+drag).
        if (panDragRef.current) {
          const p = panDragRef.current;
          cameraRef.current = {
            ...p.startCam,
            tx: p.startCam.tx + (sx - p.startX),
            ty: p.startCam.ty + (sy - p.startY),
          };
          setTick((t) => t + 1);
          return;
        }
      }

      if (!drawingRef.current) return;
      const w = screenToWorld(sx, sy);
      drawingRef.current.pts += ` ${w.x},${w.y}`;
      setTick((t) => t + 1);
    },
    [active, infinite, screenToWorld]
  );

  const finishStroke = useCallback(() => {
    if (!drawingRef.current) return;
    const cur = drawingRef.current;
    drawingRef.current = null;
    if (tool === "eraser") {
      // Eraser hit-test in world coords: a 18px screen radius becomes
      // 18 / zoom world units, so the eraser "feels" the same size at
      // any zoom level. Hits at end-of-stroke for predictability.
      const eraserPts = pointsToList(cur.pts);
      if (eraserPts.length === 0) return;
      const screenRadius = 18;
      const worldRadius = infinite
        ? screenRadius / cameraRef.current.zoom
        : screenRadius;
      setStrokes((cur) =>
        cur.filter((s) => !strokeIntersectsAny(s.points, eraserPts, worldRadius))
      );
      setTick((t) => t + 1);
      return;
    }
    const newStroke: Stroke = {
      id: cur.id,
      points: cur.pts,
      color: tool === "highlighter" ? HIGHLIGHTER_COLOR : color,
      width: tool === "highlighter" ? 18 : 3,
      opacity: tool === "highlighter" ? 0.4 : 1,
      tool,
    };
    setStrokes((s) => [...s, newStroke]);
  }, [tool, color, infinite]);

  const onPointerUp = useCallback(
    (e: React.PointerEvent<SVGSVGElement>) => {
      // Clean up pointer tracking on release / cancel / leave. End any
      // in-flight gesture when fewer than 2 pointers remain.
      if (infinite) {
        pointersRef.current.delete(e.pointerId);
        if (pointersRef.current.size < 2) {
          gestureRef.current = null;
        }
        if (panDragRef.current) {
          panDragRef.current = null;
          return;
        }
      }
      finishStroke();
    },
    [finishStroke, infinite]
  );

  // Wheel handling for infinite mode. Ctrl/Cmd + wheel = zoom toward
  // cursor; plain wheel = pan (vertical + horizontal). Attached via
  // raw addEventListener with {passive: false} so we can preventDefault
  // and stop the page from scroll-jacking; React's synthetic onWheel
  // is passive in current versions and can't do that.
  useEffect(() => {
    if (!infinite || !active) return;
    const svg = svgRef.current;
    if (!svg) return;
    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      const rect = svg.getBoundingClientRect();
      const sx = e.clientX - rect.left;
      const sy = e.clientY - rect.top;
      if (e.ctrlKey || e.metaKey) {
        // Smoother zoom: ~10% per typical wheel notch (deltaY ≈ ±100).
        const factor = Math.exp(-e.deltaY * 0.0015);
        zoomAt(sx, sy, factor);
      } else {
        // Plain wheel scrolls the camera. Shift+wheel for horizontal is
        // browser-conventional but we just respect deltaX/deltaY as-is.
        cameraRef.current = {
          ...cameraRef.current,
          tx: cameraRef.current.tx - e.deltaX,
          ty: cameraRef.current.ty - e.deltaY,
        };
        setTick((t) => t + 1);
      }
    };
    svg.addEventListener("wheel", onWheel, { passive: false });
    return () => svg.removeEventListener("wheel", onWheel);
  }, [infinite, active, zoomAt]);

  const undo = useCallback(() => {
    setStrokes((s) => s.slice(0, -1));
  }, []);

  const clear = useCallback(() => {
    setStrokes([]);
    drawingRef.current = null;
    setTick((t) => t + 1);
  }, []);

  // Build the in-progress stroke preview from the ref's current state.
  const previewStroke =
    drawingRef.current
      ? {
          points: drawingRef.current.pts,
          color: tool === "highlighter" ? HIGHLIGHTER_COLOR : tool === "eraser" ? "#9ca3af" : color,
          width: tool === "highlighter" ? 18 : tool === "eraser" ? 18 : 3,
          opacity: tool === "highlighter" ? 0.4 : tool === "eraser" ? 0.3 : 1,
          dashed: tool === "eraser",
        }
      : null;

  // Pointer-events: only on the SVG when active. When inactive, clicks
  // pass through to the underlying problem (we still render the strokes
  // so they remain visible until wiped — but the canvas doesn't intercept).
  const interactive = active;

  // Camera transform for the rendered stroke layer. In legacy mode this
  // is "translate(0,0) scale(1)" — a no-op — so existing callers render
  // identically. In infinite mode the camera ref drives the transform.
  // `vector-effect="non-scaling-stroke"` keeps strokes the same width
  // on screen regardless of zoom; otherwise zooming would make a 3px
  // pen turn into a 18px bar.
  const cam = cameraRef.current;
  const groupTransform = infinite
    ? `translate(${cam.tx} ${cam.ty}) scale(${cam.zoom})`
    : undefined;
  const cursor = !interactive
    ? "default"
    : infinite && (panDragRef.current || spaceHeldRef.current)
      ? "grab"
      : tool === "eraser"
        ? "cell"
        : "crosshair";

  return (
    <>
      {/* SVG canvas — full viewport. Stays mounted always so existing
          strokes don't disappear when the teacher toggles draw off, but
          pointer-events flips to "none" so the projection is interactive
          underneath. */}
      <svg
        ref={svgRef}
        // Width/height = 100% of the fixed-positioned wrapper so the
        // coordinate system matches the viewport. Without these, an inline
        // SVG defaults to 300x150 user units regardless of CSS sizing,
        // which clips drawing to the top-left corner.
        width="100%"
        height="100%"
        className="fixed inset-0 z-[200]"
        style={{
          pointerEvents: interactive ? "auto" : "none",
          touchAction: interactive ? "none" : "auto",
          cursor,
        }}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerCancel={onPointerUp}
        onPointerLeave={onPointerUp}
        // tick is intentionally tracked so React re-renders the in-progress
        // stroke even though we mutate the ref instead of state.
        data-tick={tick}
      >
        {/* Dot-grid background in infinite mode so the teacher has
            visual cues during pan + zoom — a blank white field plus
            mouse motion is disorienting. The pattern is anchored to
            the camera so dots scroll with the canvas. Plain white in
            legacy mode (don't render a pattern at all). */}
        {infinite && (
          <defs>
            <pattern
              id="pnp-wb-dots"
              x={cam.tx}
              y={cam.ty}
              width={40 * cam.zoom}
              height={40 * cam.zoom}
              patternUnits="userSpaceOnUse"
            >
              <circle
                cx={20 * cam.zoom}
                cy={20 * cam.zoom}
                r={Math.max(0.6, 1 * cam.zoom)}
                fill="#d4d4d8"
                opacity={0.6}
              />
            </pattern>
          </defs>
        )}
        {infinite && (
          <rect x="0" y="0" width="100%" height="100%" fill="url(#pnp-wb-dots)" />
        )}

        {/* All strokes live inside this group so the camera transform
            moves them together. `vector-effect="non-scaling-stroke"`
            keeps pen / highlighter widths constant on screen. */}
        <g transform={groupTransform}>
          {strokes.map((s) => (
            <polyline
              key={s.id}
              points={s.points}
              fill="none"
              stroke={s.color}
              strokeWidth={s.width}
              strokeOpacity={s.opacity}
              strokeLinecap="round"
              strokeLinejoin="round"
              vectorEffect={infinite ? "non-scaling-stroke" : undefined}
            />
          ))}
          {previewStroke && (
            <polyline
              points={previewStroke.points}
              fill="none"
              stroke={previewStroke.color}
              strokeWidth={previewStroke.width}
              strokeOpacity={previewStroke.opacity}
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeDasharray={previewStroke.dashed ? "4 4" : undefined}
              vectorEffect={infinite ? "non-scaling-stroke" : undefined}
            />
          )}
        </g>
      </svg>

      {/* Camera HUD — only in infinite mode. Shows the current zoom
          level, lets the teacher reset the view, and provides discrete
          +/- buttons for keyboard/no-trackpad scenarios. Bottom-right
          so it doesn't fight the tool palette (bottom-centre). */}
      {infinite && active && (
        <div
          className="fixed bottom-6 right-6 z-[220] flex items-center gap-1 rounded-md border border-pnp-gray-200 bg-white/95 px-2 py-1.5 text-xs font-semibold text-pnp-gray-700 shadow-lg backdrop-blur"
          // Don't let the HUD steal pointerdowns from the canvas in
          // case the teacher reaches for it mid-gesture.
          onPointerDown={(e) => e.stopPropagation()}
        >
          <button
            type="button"
            onClick={() => {
              const rect = svgRef.current?.getBoundingClientRect();
              if (!rect) return;
              zoomAt(rect.width / 2, rect.height / 2, 1 / 1.25);
            }}
            title="Zoom out"
            aria-label="Zoom out"
            className="flex h-7 w-7 items-center justify-center rounded hover:bg-pnp-gray-100"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <path d="M5 12h14" />
            </svg>
          </button>
          <span className="min-w-[3.25rem] text-center tabular-nums">
            {Math.round(cam.zoom * 100)}%
          </span>
          <button
            type="button"
            onClick={() => {
              const rect = svgRef.current?.getBoundingClientRect();
              if (!rect) return;
              zoomAt(rect.width / 2, rect.height / 2, 1.25);
            }}
            title="Zoom in"
            aria-label="Zoom in"
            className="flex h-7 w-7 items-center justify-center rounded hover:bg-pnp-gray-100"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <path d="M12 5v14M5 12h14" />
            </svg>
          </button>
          <div className="mx-1 h-5 w-px bg-pnp-gray-200" />
          <button
            type="button"
            onClick={resetView}
            title="Reset view"
            className="rounded px-2 py-1 hover:bg-pnp-gray-100"
          >
            Reset view
          </button>
        </div>
      )}

      {/* Floating tool palette — visible only while drawing is active.
          Draggable via the grip on the left so it can be moved out of the
          way of whatever the teacher wants to highlight. z is intentionally
          above the chrome bars (z-220) so dragging near the top or bottom
          edge can't hide the grip behind the top/bottom controls. */}
      {active && (
        <div
          ref={paletteRef}
          className="fixed z-[230] flex items-center gap-2 rounded-full border border-pnp-gray-200 bg-white/95 px-2 py-2 shadow-2xl backdrop-blur-md"
          style={
            paletteXY
              ? { left: paletteXY.x, top: paletteXY.y }
              : { bottom: "6rem", left: "50%", transform: "translateX(-50%)" }
          }
          // Stop pointerdowns from starting a stroke on the SVG.
          onPointerDown={(e) => e.stopPropagation()}
        >
          {/* Drag handle — grip on the left. */}
          <button
            type="button"
            className="flex h-9 w-7 cursor-move items-center justify-center rounded-md text-pnp-gray-500 hover:bg-pnp-gray-100 hover:text-pnp-gray-700"
            title="Drag to move palette"
            aria-label="Drag palette"
            onPointerDown={(e) => {
              // Start a drag. Use current bounding rect as the anchor so the
              // first move snaps from wherever the palette currently lives.
              e.stopPropagation();
              const rect = paletteRef.current?.getBoundingClientRect();
              if (!rect) return;
              paletteDragOffset.current = {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top,
              };
              (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
            }}
            onPointerMove={(e) => {
              if (!paletteDragOffset.current) return;
              const w = paletteRef.current?.offsetWidth ?? 400;
              const h = paletteRef.current?.offsetHeight ?? 50;
              const nx = e.clientX - paletteDragOffset.current.x;
              const ny = e.clientY - paletteDragOffset.current.y;
              setPaletteXY({
                x: Math.max(4, Math.min(window.innerWidth - w - 4, nx)),
                y: Math.max(4, Math.min(window.innerHeight - h - 4, ny)),
              });
            }}
            onPointerUp={(e) => {
              paletteDragOffset.current = null;
              (e.currentTarget as HTMLElement).releasePointerCapture(e.pointerId);
            }}
            onPointerCancel={(e) => {
              paletteDragOffset.current = null;
              (e.currentTarget as HTMLElement).releasePointerCapture(e.pointerId);
            }}
          >
            {/* 6-dot grip icon */}
            <svg width="10" height="16" viewBox="0 0 10 16" aria-hidden="true">
              <circle cx="2" cy="3"  r="1.2" fill="currentColor" />
              <circle cx="8" cy="3"  r="1.2" fill="currentColor" />
              <circle cx="2" cy="8"  r="1.2" fill="currentColor" />
              <circle cx="8" cy="8"  r="1.2" fill="currentColor" />
              <circle cx="2" cy="13" r="1.2" fill="currentColor" />
              <circle cx="8" cy="13" r="1.2" fill="currentColor" />
            </svg>
          </button>

          <ToolButton
            label="Pen"
            active={tool === "pen"}
            onClick={() => setTool("pen")}
          >
            <PenIcon />
          </ToolButton>
          <ToolButton
            label="Highlighter"
            active={tool === "highlighter"}
            onClick={() => setTool("highlighter")}
          >
            <HighlighterIcon />
          </ToolButton>
          <ToolButton
            label="Eraser"
            active={tool === "eraser"}
            onClick={() => setTool("eraser")}
          >
            <EraserIcon />
          </ToolButton>

          <div className="mx-1 h-7 w-px bg-pnp-gray-200" />

          {PEN_COLORS.map((c) => (
            <button
              key={c}
              onClick={() => {
                setTool("pen");
                setColor(c);
              }}
              title={`Pen color`}
              className={`h-7 w-7 rounded-full border-2 transition-all ${
                color === c && tool === "pen"
                  ? "border-pnp-navy scale-110"
                  : "border-pnp-gray-200 hover:scale-105"
              }`}
              style={{ backgroundColor: c }}
            />
          ))}

          <div className="mx-1 h-7 w-px bg-pnp-gray-200" />

          <button
            onClick={undo}
            title="Undo last stroke"
            className="rounded-md px-3 py-1.5 text-xs font-semibold !text-pnp-gray-700 hover:bg-pnp-gray-100 hover:!text-pnp-navy"
          >
            Undo
          </button>
          <button
            onClick={clear}
            title="Wipe whiteboard"
            className="rounded-md px-3 py-1.5 text-xs font-semibold !text-pnp-gray-700 hover:bg-pnp-gray-100 hover:!text-pnp-navy"
          >
            Clear
          </button>
          {/* Note: no "Done" button here — drawing toggles off via the same
              Draw button in the projection chrome (or by pressing Esc). */}
        </div>
      )}
    </>
  );
}

function ToolButton({
  active,
  onClick,
  label,
  children,
}: {
  active: boolean;
  onClick: () => void;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      title={label}
      aria-label={label}
      className={`flex h-9 w-9 items-center justify-center rounded-md border-2 transition-colors ${
        active
          ? "border-pnp-navy bg-pnp-navy/5 text-pnp-navy"
          : "border-transparent text-pnp-gray-500 hover:bg-pnp-gray-100 hover:text-pnp-navy"
      }`}
    >
      {children}
    </button>
  );
}

// ────────── helpers ──────────

function pointsToList(s: string): Array<[number, number]> {
  return s
    .trim()
    .split(/\s+/)
    .map((pt) => {
      const [a, b] = pt.split(",");
      return [parseFloat(a), parseFloat(b)] as [number, number];
    })
    .filter(([a, b]) => !Number.isNaN(a) && !Number.isNaN(b));
}

/** True if any point in `strokePts` is within `radius` of any point in `eraserPts`.
 *  We sample the stroke densely enough that this is a fine approximation;
 *  proper segment-distance is overkill for a whiteboard. */
function strokeIntersectsAny(
  strokePtsStr: string,
  eraserPts: Array<[number, number]>,
  radius: number
): boolean {
  const r2 = radius * radius;
  const strokePts = pointsToList(strokePtsStr);
  for (const [sx, sy] of strokePts) {
    for (const [ex, ey] of eraserPts) {
      const dx = sx - ex;
      const dy = sy - ey;
      if (dx * dx + dy * dy <= r2) return true;
    }
  }
  return false;
}

// ────────── icons ──────────

function PenIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 19l7-7 3 3-7 7-3-3z" />
      <path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z" />
      <path d="M2 2l7.586 7.586" />
      <circle cx="11" cy="11" r="2" />
    </svg>
  );
}
function HighlighterIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 11l-6 6v3h3l6-6" />
      <path d="M22 12l-9 9" />
      <path d="M11 13l9-9 4 4-9 9-4-4z" fill="currentColor" fillOpacity="0.3" />
    </svg>
  );
}
function EraserIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 20H7L3 16a2 2 0 010-2.8L13 3.5a2 2 0 012.8 0L21 9a2 2 0 010 2.8L13 20" />
      <line x1="18" y1="13" x2="9" y2="22" />
    </svg>
  );
}
