"use client";

/**
 * Shared ink primitives for SVG canvas tools.
 *
 * Extracted from the projection DrawingOverlay so the whiteboard /
 * manipulatives canvas engine and the projection annotator render strokes,
 * shapes, and text with one implementation. Everything here is pure
 * (no hooks, no state): the stroke data model, the renderer, and the
 * geometry helpers used for shape constraints and eraser hit-testing.
 */

export type Tool = "pen" | "highlighter" | "eraser" | "line" | "rect" | "ellipse" | "text";

/** Freehand paths and highlighter are "path"; the shape tools and the text
 *  tool tag their items so the renderer and eraser know the geometry. */
export type StrokeKind = "path" | "line" | "rect" | "ellipse" | "text";

export interface Stroke {
  id: string;
  kind: StrokeKind;
  // path:  polyline points  "x,y x,y x,y …"
  // shape: start + end       "x0,y0 x1,y1"
  // text:  anchor            "x,y"
  points: string;
  color: string;
  width: number;
  opacity: number;
  tool: Tool;
  text?: string;             // text kind only (plain text, or LaTeX if isMath)
  fontSize?: number;         // text kind only, in world units
  isMath?: boolean;          // text kind only — render `text` as LaTeX via KaTeX
}

export const isShapeTool = (t: Tool): boolean =>
  t === "line" || t === "rect" || t === "ellipse";
// Default text size in world units. Scales with zoom via the group transform.
export const TEXT_FONT_WORLD = 28;

export const PEN_COLORS = ["#111827", "#dc2626", "#2563eb", "#16a34a"]; // black, red, blue, green
export const HIGHLIGHTER_COLOR = "#facc15";

// ────────── rendered item ──────────

/** Renders one stroke/shape/text item in world coordinates. Used for both
 *  committed strokes and the live preview (dashed for the eraser). */
export function StrokeShape({
  item,
  nonScaling,
  mathHtml,
}: {
  item: {
    kind: StrokeKind;
    points: string;
    color: string;
    width: number;
    opacity: number;
    dashed?: boolean;
    text?: string;
    fontSize?: number;
    isMath?: boolean;
  };
  nonScaling: boolean;
  /** Pre-rendered KaTeX HTML for a math text item (null until katex loads). */
  mathHtml?: string | null;
}) {
  const stroke = {
    fill: "none" as const,
    stroke: item.color,
    strokeWidth: item.width,
    strokeOpacity: item.opacity,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    strokeDasharray: item.dashed ? "4 4" : undefined,
    vectorEffect: (nonScaling ? "non-scaling-stroke" : undefined) as
      | "non-scaling-stroke"
      | undefined,
  };
  const pts = pointsToList(item.points);

  switch (item.kind) {
    case "line": {
      if (pts.length < 2) return null;
      const [[x0, y0], [x1, y1]] = pts;
      return <line x1={x0} y1={y0} x2={x1} y2={y1} {...stroke} />;
    }
    case "rect": {
      if (pts.length < 2) return null;
      const [[x0, y0], [x1, y1]] = pts;
      return (
        <rect
          x={Math.min(x0, x1)}
          y={Math.min(y0, y1)}
          width={Math.abs(x1 - x0)}
          height={Math.abs(y1 - y0)}
          {...stroke}
        />
      );
    }
    case "ellipse": {
      if (pts.length < 2) return null;
      const [[x0, y0], [x1, y1]] = pts;
      return (
        <ellipse
          cx={(x0 + x1) / 2}
          cy={(y0 + y1) / 2}
          rx={Math.abs(x1 - x0) / 2}
          ry={Math.abs(y1 - y0) / 2}
          {...stroke}
        />
      );
    }
    case "text": {
      if (pts.length < 1 || !item.text) return null;
      const [[x, y]] = pts;
      // Math: render KaTeX HTML inside a world-space foreignObject so it pans
      // and zooms with everything else. Until katex has loaded (mathHtml null)
      // we fall through to plain text showing the raw LaTeX.
      if (item.isMath && mathHtml) {
        return (
          <foreignObject
            x={x}
            y={y}
            width={2400}
            height={600}
            style={{ overflow: "visible", pointerEvents: "none" }}
          >
            <div
              style={{
                display: "inline-block",
                color: item.color,
                fontSize: item.fontSize ?? TEXT_FONT_WORLD,
                lineHeight: 1.2,
                whiteSpace: "nowrap",
              }}
              dangerouslySetInnerHTML={{ __html: mathHtml }}
            />
          </foreignObject>
        );
      }
      return (
        <text
          x={x}
          y={y}
          fill={item.color}
          fontSize={item.fontSize ?? TEXT_FONT_WORLD}
          fontFamily="var(--font-sans, system-ui, sans-serif)"
          dominantBaseline="hanging"
          style={{ whiteSpace: "pre" }}
        >
          {item.text}
        </text>
      );
    }
    default:
      return <polyline points={item.points} {...stroke} />;
  }
}

// ────────── geometry helpers ──────────

export function pointsToList(s: string): Array<[number, number]> {
  return s
    .trim()
    .split(/\s+/)
    .map((pt) => {
      const [a, b] = pt.split(",");
      return [parseFloat(a), parseFloat(b)] as [number, number];
    })
    .filter(([a, b]) => !Number.isNaN(a) && !Number.isNaN(b));
}

/** Constrain a shape's end point while Shift is held: lines snap to the
 *  nearest 0/45/90°, rect + ellipse become square / circle. */
export function constrainShape(
  tool: Tool,
  startStr: string,
  ex: number,
  ey: number
): [number, number] {
  const [sx, sy] = startStr.split(",").map(Number) as [number, number];
  const dx = ex - sx;
  const dy = ey - sy;
  if (tool === "line") {
    const step = Math.PI / 4;
    const snapped = Math.round(Math.atan2(dy, dx) / step) * step;
    const len = Math.hypot(dx, dy);
    return [sx + Math.cos(snapped) * len, sy + Math.sin(snapped) * len];
  }
  const m = Math.max(Math.abs(dx), Math.abs(dy));
  return [sx + (dx < 0 ? -m : m), sy + (dy < 0 ? -m : m)];
}

function sampleSegment(
  a: [number, number],
  b: [number, number],
  n: number
): Array<[number, number]> {
  const out: Array<[number, number]> = [];
  for (let i = 0; i <= n; i++) {
    const t = i / n;
    out.push([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]);
  }
  return out;
}

/** Points along an item's geometry, used for eraser hit-testing so shapes
 *  and text can be erased by dragging over any part of them (not just their
 *  defining corners). */
export function sampleGeometry(item: {
  kind: StrokeKind;
  points: string;
  text?: string;
  fontSize?: number;
}): Array<[number, number]> {
  const pts = pointsToList(item.points);
  switch (item.kind) {
    case "line":
      return pts.length < 2 ? pts : sampleSegment(pts[0], pts[1], 24);
    case "rect": {
      if (pts.length < 2) return pts;
      const [[x0, y0], [x1, y1]] = pts;
      const a: [number, number] = [Math.min(x0, x1), Math.min(y0, y1)];
      const b: [number, number] = [Math.max(x0, x1), Math.min(y0, y1)];
      const c: [number, number] = [Math.max(x0, x1), Math.max(y0, y1)];
      const d: [number, number] = [Math.min(x0, x1), Math.max(y0, y1)];
      return [
        ...sampleSegment(a, b, 16),
        ...sampleSegment(b, c, 16),
        ...sampleSegment(c, d, 16),
        ...sampleSegment(d, a, 16),
      ];
    }
    case "ellipse": {
      if (pts.length < 2) return pts;
      const [[x0, y0], [x1, y1]] = pts;
      const cx = (x0 + x1) / 2;
      const cy = (y0 + y1) / 2;
      const rx = Math.abs(x1 - x0) / 2;
      const ry = Math.abs(y1 - y0) / 2;
      const out: Array<[number, number]> = [];
      const N = 32;
      for (let i = 0; i < N; i++) {
        const t = (i / N) * Math.PI * 2;
        out.push([cx + Math.cos(t) * rx, cy + Math.sin(t) * ry]);
      }
      return out;
    }
    case "text": {
      if (pts.length < 1) return pts;
      const [[x, y]] = pts;
      const fs = item.fontSize ?? TEXT_FONT_WORLD;
      const w = Math.max(fs, (item.text?.length ?? 1) * fs * 0.55);
      return [
        [x, y],
        [x + w, y],
        [x, y + fs],
        [x + w, y + fs],
        [x + w / 2, y + fs / 2],
      ];
    }
    default:
      return pts;
  }
}

/** True if the eraser path comes within `radius` of any sampled point of the
 *  item. Sampling density is a fine approximation for a whiteboard. */
export function eraserHits(
  item: { kind: StrokeKind; points: string; text?: string; fontSize?: number },
  eraserPts: Array<[number, number]>,
  radius: number
): boolean {
  const r2 = radius * radius;
  for (const [sx, sy] of sampleGeometry(item)) {
    for (const [ex, ey] of eraserPts) {
      const dx = sx - ex;
      const dy = sy - ey;
      if (dx * dx + dy * dy <= r2) return true;
    }
  }
  return false;
}
