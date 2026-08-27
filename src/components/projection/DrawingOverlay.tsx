"use client";

import { useCallback, useEffect, useRef, useState } from "react";
// Stroke model, renderer, and geometry helpers are shared with the
// standalone canvas tools (whiteboard / manipulatives) via canvas/ink.
import {
  StrokeShape,
  pointsToList,
  eraserHits,
  PEN_COLORS,
  HIGHLIGHTER_COLOR,
  type Stroke,
} from "@/components/tools/canvas/ink";

/**
 * Whiteboard-style drawing overlay for the projection.
 *
 * SVG strokes captured from pointer events (mouse / finger / stylus),
 * rendered via the shared StrokeShape so we can erase per-stroke and undo
 * cheaply. Lives above the projection content card via fixed positioning;
 * pointer-events toggle on/off so the underlying problem stays clickable
 * when the teacher isn't actively drawing.
 *
 * Strokes persist per slide: when `wipeKey` changes, the current strokes
 * are stashed under the old key and the new key's strokes (if any) are
 * restored — so a teacher can flip back to a problem and their annotations
 * are still there. "Clear" wipes only the current slide.
 *
 * The infinite-canvas whiteboard that used to live in here (camera,
 * shapes, text/KaTeX, PDF pages, autosave) moved to the unified
 * tools/canvas/CanvasEngine — this overlay is deliberately just the
 * pen / highlighter / eraser annotator the projection views need.
 */

type Tool = "pen" | "highlighter" | "eraser";

interface Props {
  active: boolean;
  /** Setter for the parent's drawing-active state — used by the palette's
   *  Done button to flip the toggle off without touching parent internals. */
  setActive: (next: boolean) => void;
  /** Slide identity. When this string changes, the current strokes are
   *  stashed under the old key and the new key's strokes are restored.
   *  Pass `${item}-${session}-${mode}` from the parent. */
  wipeKey: string;
}

export default function DrawingOverlay({ active, setActive, wipeKey }: Props) {
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

  // Fixed viewport: screen pixels ARE the stroke coordinates, so points
  // land exactly at the pointer location.
  const onPointerDown = useCallback(
    (e: React.PointerEvent<SVGSVGElement>) => {
      if (!active) return;
      const svg = svgRef.current;
      if (!svg) return;
      const rect = svg.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      svg.setPointerCapture(e.pointerId);
      const id = `s-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
      drawingRef.current = { id, pts: `${x},${y}` };
      setTick((t) => t + 1);
    },
    [active]
  );

  const onPointerMove = useCallback(
    (e: React.PointerEvent<SVGSVGElement>) => {
      if (!active || !drawingRef.current) return;
      const svg = svgRef.current;
      if (!svg) return;
      const rect = svg.getBoundingClientRect();
      drawingRef.current.pts += ` ${e.clientX - rect.left},${e.clientY - rect.top}`;
      setTick((t) => t + 1);
    },
    [active]
  );

  const onPointerUp = useCallback(() => {
    if (!drawingRef.current) return;
    const cur = drawingRef.current;
    drawingRef.current = null;
    if (tool === "eraser") {
      // Hit-test at end-of-stroke for predictability: any stroke within
      // an 18px radius of the eraser path is removed whole.
      const eraserPts = pointsToList(cur.pts);
      if (eraserPts.length === 0) return;
      setStrokes((s) => s.filter((st) => !eraserHits(st, eraserPts, 18)));
      setTick((t) => t + 1);
      return;
    }
    const newStroke: Stroke = {
      id: cur.id,
      kind: "path",
      points: cur.pts,
      color: tool === "highlighter" ? HIGHLIGHTER_COLOR : color,
      width: tool === "highlighter" ? 18 : 3,
      opacity: tool === "highlighter" ? 0.4 : 1,
      tool,
    };
    setStrokes((s) => [...s, newStroke]);
  }, [tool, color]);

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
          kind: "path" as const,
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
  const cursor = !interactive ? "default" : tool === "eraser" ? "cell" : "crosshair";

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
        {strokes.map((s) => (
          <StrokeShape key={s.id} item={s} nonScaling={false} />
        ))}
        {previewStroke && <StrokeShape item={previewStroke} nonScaling={false} />}
      </svg>

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
                setColor(c);
                // Colour applies to the pen — only the eraser has no colour,
                // so switch to pen if that was selected.
                if (tool === "eraser") setTool("pen");
              }}
              title={`Colour`}
              className={`h-7 w-7 rounded-full border-2 transition-all ${
                color === c && tool !== "eraser"
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
