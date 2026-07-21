"use client";

import type { ShapeSpec } from "@/lib/fluency-gen";

/**
 * Inline labeled-shape diagram for geometry fluency problems.
 *
 * Each shape kind draws a simple SVG sized to fit comfortably next to a
 * single problem in a two-column worksheet. Strokes use `currentColor`
 * so the figure inherits the surrounding text color (black on the
 * worksheet, dimmed on the answer key).
 *
 * Label slots are shape-specific. Missing labels are tolerated — if a
 * label key isn't present in `spec.labels`, the slot simply renders blank.
 */

interface Props {
  spec: ShapeSpec;
  size?: "normal" | "small";
}

const LABEL_FONT = "0.85rem";
const SMALL_LABEL_FONT = "0.7rem";

export default function ShapeRenderer({ spec, size = "normal" }: Props) {
  const fs = size === "small" ? SMALL_LABEL_FONT : LABEL_FONT;
  switch (spec.kind) {
    case "rectangle":
      return <RectangleSVG labels={spec.labels} fs={fs} />;
    case "square":
      return <SquareSVG labels={spec.labels} fs={fs} />;
    case "triangle":
      return <TriangleSVG labels={spec.labels} fs={fs} />;
    case "right-triangle":
      return <RightTriangleSVG labels={spec.labels} fs={fs} />;
    case "parallelogram":
      return <ParallelogramSVG labels={spec.labels} fs={fs} />;
    case "trapezoid":
      return <TrapezoidSVG labels={spec.labels} fs={fs} />;
    case "circle":
      return <CircleSVG labels={spec.labels} fs={fs} />;
    case "rect-prism":
      return <RectPrismSVG labels={spec.labels} fs={fs} />;
    case "cube":
      return <CubeSVG labels={spec.labels} fs={fs} />;
    case "tri-prism":
      return <TriPrismSVG labels={spec.labels} fs={fs} />;
    case "cylinder":
      return <CylinderSVG labels={spec.labels} fs={fs} />;
    case "cone":
      return <ConeSVG labels={spec.labels} fs={fs} />;
    case "sphere":
      return <SphereSVG labels={spec.labels} fs={fs} />;
    case "pyramid":
      return <PyramidSVG labels={spec.labels} fs={fs} />;
    case "grid":
      return <CoordinateGridSVG spec={spec} fs={fs} />;
    case "numberline":
      return <NumberLineSVG spec={spec} size={size} />;
  }
}

type LabelMap = Record<string, string>;

const STROKE = "currentColor";
const STROKE_WIDTH = 2;
const DASH = "4 3"; // dashed style for height lines

function RectangleSVG({ labels, fs }: { labels: LabelMap; fs: string }) {
  // Rectangle: 100 wide × 60 tall. Length labeled below, width on the right.
  return (
    <svg width="160" height="100" viewBox="0 0 160 100" style={{ overflow: "visible" }} role="img" aria-label="Rectangle">
      <rect
        x="20" y="15" width="100" height="60"
        fill="none" stroke={STROKE} strokeWidth={STROKE_WIDTH}
      />
      <text x="70" y="92" textAnchor="middle" fontSize={fs} fill={STROKE}>
        {labels.length ?? ""}
      </text>
      <text x="128" y="49" textAnchor="start" fontSize={fs} fill={STROKE}>
        {labels.width ?? ""}
      </text>
    </svg>
  );
}

function SquareSVG({ labels, fs }: { labels: LabelMap; fs: string }) {
  return (
    <svg width="120" height="100" viewBox="0 0 120 100" style={{ overflow: "visible" }} role="img" aria-label="Square">
      <rect
        x="20" y="15" width="60" height="60"
        fill="none" stroke={STROKE} strokeWidth={STROKE_WIDTH}
      />
      <text x="50" y="92" textAnchor="middle" fontSize={fs} fill={STROKE}>
        {labels.side ?? ""}
      </text>
    </svg>
  );
}

function TriangleSVG({ labels, fs }: { labels: LabelMap; fs: string }) {
  // Generic triangle. Height label sits OUTSIDE the right edge so the
  // dimension text never lands on top of the triangle's outline.
  return (
    <svg width="190" height="100" viewBox="0 0 190 100" style={{ overflow: "visible" }} role="img" aria-label="Triangle">
      <polygon
        points="80,10 20,75 140,75"
        fill="none" stroke={STROKE} strokeWidth={STROKE_WIDTH}
      />
      {/* Dashed perpendicular height from apex to base */}
      <line
        x1="80" y1="10" x2="80" y2="75"
        stroke={STROKE} strokeWidth="1.5" strokeDasharray={DASH}
      />
      {/* Short horizontal leader so the external label reads as the height */}
      <line
        x1="80" y1="45" x2="148" y2="45"
        stroke={STROKE} strokeWidth="1" strokeDasharray="2 2"
      />
      <text x="80" y="92" textAnchor="middle" fontSize={fs} fill={STROKE}>
        {labels.base ?? ""}
      </text>
      <text x="152" y="49" textAnchor="start" fontSize={fs} fill={STROKE}>
        {labels.height ?? ""}
      </text>
    </svg>
  );
}

function RightTriangleSVG({ labels, fs }: { labels: LabelMap; fs: string }) {
  // Right angle at lower-left. Legs along bottom (a) and left (b),
  // hypotenuse (c) from upper-left to lower-right.
  return (
    <svg width="170" height="120" viewBox="0 0 170 120" style={{ overflow: "visible" }} role="img" aria-label="Right triangle">
      <polygon
        points="20,100 140,100 20,20"
        fill="none" stroke={STROKE} strokeWidth={STROKE_WIDTH}
      />
      {/* Small right-angle square at the corner */}
      <polyline
        points="20,90 30,90 30,100"
        fill="none" stroke={STROKE} strokeWidth="1.5"
      />
      <text x="80" y="115" textAnchor="middle" fontSize={fs} fill={STROKE}>
        {labels.a ?? ""}
      </text>
      <text x="14" y="63" textAnchor="end" fontSize={fs} fill={STROKE}>
        {labels.b ?? ""}
      </text>
      <text x="90" y="55" textAnchor="middle" fontSize={fs} fill={STROKE}>
        {labels.c ?? ""}
      </text>
    </svg>
  );
}

function ParallelogramSVG({ labels, fs }: { labels: LabelMap; fs: string }) {
  // Parallelogram with the height label clearly OUTSIDE the right edge,
  // connected to the internal dashed perpendicular by a faint leader so
  // it still reads as the height.
  return (
    <svg width="200" height="100" viewBox="0 0 200 100" style={{ overflow: "visible" }} role="img" aria-label="Parallelogram">
      <polygon
        points="40,75 140,75 120,15 20,15"
        fill="none" stroke={STROKE} strokeWidth={STROKE_WIDTH}
      />
      {/* Internal dashed perpendicular (the actual height) */}
      <line
        x1="120" y1="15" x2="120" y2="75"
        stroke={STROKE} strokeWidth="1.5" strokeDasharray={DASH}
      />
      {/* Faint horizontal leader from the dashed line out to the label */}
      <line
        x1="120" y1="48" x2="155" y2="48"
        stroke={STROKE} strokeWidth="1" strokeDasharray="2 2"
      />
      <text x="90" y="92" textAnchor="middle" fontSize={fs} fill={STROKE}>
        {labels.base ?? ""}
      </text>
      <text x="158" y="52" textAnchor="start" fontSize={fs} fill={STROKE}>
        {labels.height ?? ""}
      </text>
    </svg>
  );
}

function TrapezoidSVG({ labels, fs }: { labels: LabelMap; fs: string }) {
  // Trapezoid with longer base on bottom. Height label sits OUTSIDE the
  // right edge with a faint leader from the internal dashed perpendicular.
  return (
    <svg width="220" height="100" viewBox="0 0 220 100" style={{ overflow: "visible" }} role="img" aria-label="Trapezoid">
      <polygon
        points="20,75 160,75 130,15 50,15"
        fill="none" stroke={STROKE} strokeWidth={STROKE_WIDTH}
      />
      <line
        x1="90" y1="15" x2="90" y2="75"
        stroke={STROKE} strokeWidth="1.5" strokeDasharray={DASH}
      />
      <line
        x1="90" y1="45" x2="175" y2="45"
        stroke={STROKE} strokeWidth="1" strokeDasharray="2 2"
      />
      <text x="90" y="92" textAnchor="middle" fontSize={fs} fill={STROKE}>
        {labels.base1 ?? ""}
      </text>
      <text x="90" y="9" textAnchor="middle" fontSize={fs} fill={STROKE}>
        {labels.base2 ?? ""}
      </text>
      <text x="178" y="49" textAnchor="start" fontSize={fs} fill={STROKE}>
        {labels.height ?? ""}
      </text>
    </svg>
  );
}

// ───── 3-D shapes (oblique projections) ─────

function RectPrismSVG({ labels, fs }: { labels: LabelMap; fs: string }) {
  // Front rectangle + parallelogram top + parallelogram right side.
  return (
    <svg width="170" height="130" viewBox="0 0 170 130" style={{ overflow: "visible" }} role="img" aria-label="Rectangular prism">
      {/* Top face */}
      <polygon
        points="20,45 100,45 130,25 50,25"
        fill="none" stroke={STROKE} strokeWidth={STROKE_WIDTH}
      />
      {/* Right side face */}
      <polygon
        points="100,45 130,25 130,85 100,105"
        fill="none" stroke={STROKE} strokeWidth={STROKE_WIDTH}
      />
      {/* Front face — drawn last so its edges sit on top */}
      <rect
        x="20" y="45" width="80" height="60"
        fill="none" stroke={STROKE} strokeWidth={STROKE_WIDTH}
      />
      {/* Labels */}
      <text x="60" y="120" textAnchor="middle" fontSize={fs} fill={STROKE}>
        {labels.length ?? ""}
      </text>
      <text x="90" y="18" textAnchor="middle" fontSize={fs} fill={STROKE}>
        {labels.width ?? ""}
      </text>
      <text x="138" y="70" textAnchor="start" fontSize={fs} fill={STROKE}>
        {labels.height ?? ""}
      </text>
    </svg>
  );
}

function CubeSVG({ labels, fs }: { labels: LabelMap; fs: string }) {
  return (
    <svg width="140" height="130" viewBox="0 0 140 130" style={{ overflow: "visible" }} role="img" aria-label="Cube">
      {/* Top */}
      <polygon
        points="20,45 85,45 110,25 45,25"
        fill="none" stroke={STROKE} strokeWidth={STROKE_WIDTH}
      />
      {/* Right */}
      <polygon
        points="85,45 110,25 110,90 85,110"
        fill="none" stroke={STROKE} strokeWidth={STROKE_WIDTH}
      />
      {/* Front */}
      <rect
        x="20" y="45" width="65" height="65"
        fill="none" stroke={STROKE} strokeWidth={STROKE_WIDTH}
      />
      <text x="52" y="125" textAnchor="middle" fontSize={fs} fill={STROKE}>
        {labels.side ?? ""}
      </text>
    </svg>
  );
}

function TriPrismSVG({ labels, fs }: { labels: LabelMap; fs: string }) {
  // Horizontal triangular prism: front triangular face + back triangular
  // face offset up-right, connected by edges.
  return (
    <svg width="180" height="120" viewBox="0 0 180 120" style={{ overflow: "visible" }} role="img" aria-label="Triangular prism">
      {/* Back triangle */}
      <polygon
        points="60,75 150,75 105,20"
        fill="none" stroke={STROKE} strokeWidth={STROKE_WIDTH}
      />
      {/* Front triangle */}
      <polygon
        points="20,100 110,100 65,45"
        fill="none" stroke={STROKE} strokeWidth={STROKE_WIDTH}
      />
      {/* Connecting edges from front-vertices to back-vertices */}
      <line x1="20"  y1="100" x2="60"  y2="75" stroke={STROKE} strokeWidth={STROKE_WIDTH} />
      <line x1="110" y1="100" x2="150" y2="75" stroke={STROKE} strokeWidth={STROKE_WIDTH} />
      <line x1="65"  y1="45"  x2="105" y2="20" stroke={STROKE} strokeWidth={STROKE_WIDTH} />
      {/* Dashed triangle-height inside the front face + leader out to label */}
      <line x1="65" y1="45" x2="65" y2="100" stroke={STROKE} strokeWidth="1.5" strokeDasharray={DASH} />
      <line x1="65" y1="72" x2="5"  y2="72"  stroke={STROKE} strokeWidth="1" strokeDasharray="2 2" />
      {/* Labels */}
      <text x="65"  y="115" textAnchor="middle" fontSize={fs} fill={STROKE}>{labels.base ?? ""}</text>
      <text x="2"   y="76"  textAnchor="end"    fontSize={fs} fill={STROKE}>{labels.triHeight ?? ""}</text>
      <text x="125" y="93"  textAnchor="start"  fontSize={fs} fill={STROKE}>{labels.length ?? ""}</text>
    </svg>
  );
}

function CylinderSVG({ labels, fs }: { labels: LabelMap; fs: string }) {
  // Top ellipse solid; bottom ellipse split: front half solid, back dashed.
  return (
    <svg width="160" height="140" viewBox="0 0 160 140" style={{ overflow: "visible" }} role="img" aria-label="Cylinder">
      {/* Top ellipse */}
      <ellipse cx="70" cy="20" rx="40" ry="10" fill="none" stroke={STROKE} strokeWidth={STROKE_WIDTH} />
      {/* Side vertical lines */}
      <line x1="30"  y1="20" x2="30"  y2="110" stroke={STROKE} strokeWidth={STROKE_WIDTH} />
      <line x1="110" y1="20" x2="110" y2="110" stroke={STROKE} strokeWidth={STROKE_WIDTH} />
      {/* Bottom: front half (visible, solid) */}
      <path
        d="M 30,110 A 40,10 0 0 0 110,110"
        fill="none" stroke={STROKE} strokeWidth={STROKE_WIDTH}
      />
      {/* Bottom: back half (hidden, dashed) */}
      <path
        d="M 30,110 A 40,10 0 0 1 110,110"
        fill="none" stroke={STROKE} strokeWidth="1.5" strokeDasharray={DASH}
      />
      {/* Radius line on top ellipse */}
      <line x1="70" y1="20" x2="110" y2="20" stroke={STROKE} strokeWidth="1.5" />
      <circle cx="70" cy="20" r="2" fill={STROKE} />
      {/* Labels: radius lifted ABOVE the top ellipse so the text doesn't
          land on the curve. Height sits to the right of the cylinder. */}
      <text x="90"  y="3"   textAnchor="middle" fontSize={fs} fill={STROKE}>{labels.radius ?? ""}</text>
      <text x="118" y="68"  textAnchor="start"  fontSize={fs} fill={STROKE}>{labels.height ?? ""}</text>
    </svg>
  );
}

function ConeSVG({ labels, fs }: { labels: LabelMap; fs: string }) {
  // Apex + base ellipse + two slant lines + dashed center height.
  return (
    <svg width="160" height="140" viewBox="0 0 160 140" style={{ overflow: "visible" }} role="img" aria-label="Cone">
      {/* Base: front half solid, back half dashed */}
      <path d="M 30,110 A 40,10 0 0 0 110,110" fill="none" stroke={STROKE} strokeWidth={STROKE_WIDTH} />
      <path
        d="M 30,110 A 40,10 0 0 1 110,110"
        fill="none" stroke={STROKE} strokeWidth="1.5" strokeDasharray={DASH}
      />
      {/* Slant edges */}
      <line x1="70" y1="15" x2="30"  y2="110" stroke={STROKE} strokeWidth={STROKE_WIDTH} />
      <line x1="70" y1="15" x2="110" y2="110" stroke={STROKE} strokeWidth={STROKE_WIDTH} />
      {/* Dashed center height from apex to center of base + leader to label */}
      <line
        x1="70" y1="15" x2="70" y2="110"
        stroke={STROKE} strokeWidth="1.5" strokeDasharray={DASH}
      />
      <line
        x1="70" y1="62" x2="10" y2="62"
        stroke={STROKE} strokeWidth="1" strokeDasharray="2 2"
      />
      {/* Radius line on base */}
      <line x1="70" y1="110" x2="110" y2="110" stroke={STROKE} strokeWidth="1.5" />
      <circle cx="70" cy="110" r="2" fill={STROKE} />
      {/* Labels — the radius label sits well BELOW the base ellipse
          (bottom edge ≈ y=120) so the text never overlaps the dashed
          back curve. */}
      <text x="90"  y="136" textAnchor="middle" fontSize={fs} fill={STROKE}>{labels.radius ?? ""}</text>
      <text x="7"   y="66"  textAnchor="end"    fontSize={fs} fill={STROKE}>{labels.height ?? ""}</text>
    </svg>
  );
}

function SphereSVG({ labels, fs }: { labels: LabelMap; fs: string }) {
  // Full circle + equator ellipse (front half solid, back half dashed) +
  // radius line.
  return (
    <svg width="140" height="130" viewBox="0 0 140 130" style={{ overflow: "visible" }} role="img" aria-label="Sphere">
      <circle cx="60" cy="65" r="45" fill="none" stroke={STROKE} strokeWidth={STROKE_WIDTH} />
      {/* Equator: front arc */}
      <path d="M 15,65 A 45,12 0 0 0 105,65" fill="none" stroke={STROKE} strokeWidth="1.5" />
      {/* Equator: back arc (hidden) */}
      <path
        d="M 15,65 A 45,12 0 0 1 105,65"
        fill="none" stroke={STROKE} strokeWidth="1.5" strokeDasharray={DASH}
      />
      {/* Radius line */}
      <line x1="60" y1="65" x2="105" y2="65" stroke={STROKE} strokeWidth="1.5" />
      <circle cx="60" cy="65" r="2" fill={STROKE} />
      <text x="110" y="69" textAnchor="start" fontSize={fs} fill={STROKE}>
        {labels.radius ?? ""}
      </text>
    </svg>
  );
}

function PyramidSVG({ labels, fs }: { labels: LabelMap; fs: string }) {
  // Square base shown as parallelogram (top-down oblique) + apex + edges.
  return (
    <svg width="160" height="140" viewBox="0 0 160 140" style={{ overflow: "visible" }} role="img" aria-label="Square pyramid">
      {/* Base parallelogram */}
      <polygon
        points="25,100 100,100 125,75 50,75"
        fill="none" stroke={STROKE} strokeWidth={STROKE_WIDTH}
      />
      {/* Apex + 4 slant edges */}
      <line x1="75" y1="15" x2="25"  y2="100" stroke={STROKE} strokeWidth={STROKE_WIDTH} />
      <line x1="75" y1="15" x2="100" y2="100" stroke={STROKE} strokeWidth={STROKE_WIDTH} />
      <line x1="75" y1="15" x2="125" y2="75"  stroke={STROKE} strokeWidth={STROKE_WIDTH} />
      <line x1="75" y1="15" x2="50"  y2="75"  stroke={STROKE} strokeWidth={STROKE_WIDTH} />
      {/* Dashed height from apex to base center + leader out to label */}
      <line
        x1="75" y1="15" x2="75" y2="88"
        stroke={STROKE} strokeWidth="1.5" strokeDasharray={DASH}
      />
      <line
        x1="75" y1="50" x2="145" y2="50"
        stroke={STROKE} strokeWidth="1" strokeDasharray="2 2"
      />
      {/* Labels */}
      <text x="62" y="115" textAnchor="middle" fontSize={fs} fill={STROKE}>
        {labels.side ?? ""}
      </text>
      <text x="148" y="54" textAnchor="start"  fontSize={fs} fill={STROKE}>
        {labels.height ?? ""}
      </text>
    </svg>
  );
}

function CircleSVG({ labels, fs }: { labels: LabelMap; fs: string }) {
  // Circle of radius 35 centered at (60, 50). Show whichever of
  // radius/diameter the spec supplies.
  const hasDiameter = labels.diameter != null;
  return (
    <svg width="140" height="100" viewBox="0 0 140 100" style={{ overflow: "visible" }} role="img" aria-label="Circle">
      <circle
        cx="60" cy="50" r="35"
        fill="none" stroke={STROKE} strokeWidth={STROKE_WIDTH}
      />
      {hasDiameter ? (
        <>
          <line
            x1="25" y1="50" x2="95" y2="50"
            stroke={STROKE} strokeWidth="1.5"
          />
          <text x="100" y="54" textAnchor="start" fontSize={fs} fill={STROKE}>
            {labels.diameter}
          </text>
        </>
      ) : (
        <>
          <line
            x1="60" y1="50" x2="95" y2="50"
            stroke={STROKE} strokeWidth="1.5"
          />
          <circle cx="60" cy="50" r="2" fill={STROKE} />
          <text x="100" y="54" textAnchor="start" fontSize={fs} fill={STROKE}>
            {labels.radius ?? ""}
          </text>
        </>
      )}
    </svg>
  );
}

/**
 * Number-line SVG for inequality worksheets. The worksheet variant is a
 * blank line with ticks (students graph on it); the answer-key variant
 * draws boundary circles (open/closed) and shaded rays/segments.
 */
function NumberLineSVG({ spec, size }: { spec: ShapeSpec; size: "normal" | "small" }) {
  const nl = spec.numberline ?? { min: -5, max: 5 };
  const { min, max } = nl;
  const step = nl.step ?? 1;
  const span = max - min;
  const unit = size === "small" ? 16 : 22; // px per tick
  const pad = 16;                          // room for the arrowheads
  const width = span * unit + pad * 2;
  const axisY = 22;
  const height = 44;
  const px = (v: number) => pad + (v - min) * unit;

  const ticks: number[] = [];
  for (let v = min; v <= max; v++) ticks.push(v);

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      style={{ overflow: "visible" }}
      role="img"
      aria-label="Number line"
    >
      <defs>
        <marker
          id="nl-arrow"
          viewBox="0 0 10 10"
          refX="8"
          refY="5"
          markerWidth="6"
          markerHeight="6"
          orient="auto-start-reverse"
        >
          <path d="M0,0 L10,5 L0,10 z" fill={STROKE} />
        </marker>
      </defs>

      {/* Shaded segments/rays UNDER the axis line so circles stay crisp */}
      {(nl.segments ?? []).map((s, i) => {
        const x1 = s.from === "-inf" ? 2 : px(s.from as number);
        const x2 = s.to === "+inf" ? width - 2 : px(s.to as number);
        return (
          <line
            key={`seg-${i}`}
            x1={x1} y1={axisY} x2={x2} y2={axisY}
            stroke={STROKE} strokeWidth="4.5" strokeLinecap="butt"
          />
        );
      })}

      {/* Axis with arrowheads on both ends */}
      <line
        x1={2} y1={axisY} x2={width - 2} y2={axisY}
        stroke={STROKE} strokeWidth="1.5"
        markerEnd="url(#nl-arrow)" markerStart="url(#nl-arrow)"
      />

      {/* Ticks + labels */}
      {ticks.map((v) => (
        <g key={`t-${v}`}>
          <line
            x1={px(v)} y1={axisY - 5} x2={px(v)} y2={axisY + 5}
            stroke={STROKE} strokeWidth={v === 0 ? 1.75 : 1}
          />
          {((v - min) % step === 0 || v === 0) && (
            <text
              x={px(v)} y={axisY + 17} textAnchor="middle"
              fontSize="0.6rem" fill={STROKE}
            >
              {v}
            </text>
          )}
        </g>
      ))}

      {/* Boundary circles — open (unfilled) or closed (filled). Drawn
          last so they cover the ray underneath. */}
      {(nl.points ?? []).map((p, i) => (
        <circle
          key={`p-${i}`}
          cx={px(p.x)} cy={axisY} r="5"
          fill={p.open ? "white" : STROKE}
          stroke={STROKE} strokeWidth="1.75"
        />
      ))}
    </svg>
  );
}

/**
 * Coordinate-grid SVG. Draws an x/y plane with light gridlines, axes with
 * arrowheads, integer tick labels, and any plotted points / lines / curve
 * passed in via spec.grid.
 *
 * Coordinate range defaults to [-6, 6]. The SVG sizes itself to the range
 * so the unit length stays roughly constant per square.
 */
function CoordinateGridSVG({ spec, fs }: { spec: ShapeSpec; fs: string }) {
  const g = spec.grid ?? {};
  const range = g.range ?? 6;
  const unit = 14; // pixels per grid unit
  const pad = 18;  // pixels of padding around the grid
  const span = range * 2;
  const innerSize = span * unit;
  const total = innerSize + pad * 2;

  // World -> SVG transforms (origin = center)
  const tx = (x: number) => pad + (x + range) * unit;
  const ty = (y: number) => pad + (range - y) * unit;

  // Build tick arrays excluding 0 (zero label clutters the origin)
  const ticks: number[] = [];
  for (let i = -range; i <= range; i++) if (i !== 0) ticks.push(i);

  return (
    <svg
      width={total}
      height={total}
      viewBox={`0 0 ${total} ${total}`}
      style={{ overflow: "visible" }}
      role="img"
      aria-label="Coordinate grid"
    >
      <defs>
        <marker
          id="grid-arrow"
          viewBox="0 0 10 10"
          refX="8"
          refY="5"
          markerWidth="6"
          markerHeight="6"
          orient="auto-start-reverse"
        >
          <path d="M0,0 L10,5 L0,10 z" fill={STROKE} />
        </marker>
        <clipPath id="grid-clip">
          <rect x={pad} y={pad} width={innerSize} height={innerSize} />
        </clipPath>
      </defs>

      {/* Gridlines */}
      {Array.from({ length: span + 1 }, (_, i) => {
        const v = i * unit + pad;
        return (
          <g key={`grid-${i}`}>
            <line
              x1={pad} y1={v} x2={pad + innerSize} y2={v}
              stroke="#cbd5e1" strokeWidth="0.75"
            />
            <line
              x1={v} y1={pad} x2={v} y2={pad + innerSize}
              stroke="#cbd5e1" strokeWidth="0.75"
            />
          </g>
        );
      })}

      {/* Axes with arrowheads */}
      <line
        x1={pad} y1={ty(0)} x2={pad + innerSize} y2={ty(0)}
        stroke={STROKE} strokeWidth="1.25"
        markerEnd="url(#grid-arrow)" markerStart="url(#grid-arrow)"
      />
      <line
        x1={tx(0)} y1={pad} x2={tx(0)} y2={pad + innerSize}
        stroke={STROKE} strokeWidth="1.25"
        markerEnd="url(#grid-arrow)" markerStart="url(#grid-arrow)"
      />

      {/* Tick labels (only every other one if range >= 6 to avoid clutter) */}
      {ticks.map((n) => {
        const skip = range >= 8 && n % 2 !== 0;
        if (skip) return null;
        return (
          <g key={`tick-${n}`}>
            <text
              x={tx(n)} y={ty(0) + 11} textAnchor="middle"
              fontSize="0.55rem" fill={STROKE}
            >
              {n}
            </text>
            <text
              x={tx(0) - 5} y={ty(n) + 3} textAnchor="end"
              fontSize="0.55rem" fill={STROKE}
            >
              {n}
            </text>
          </g>
        );
      })}

      {/* Clipped drawing region — anything that could extend past the grid
          (lines, curves, verticals) is clipped to stay on the plot. */}
      <g clipPath="url(#grid-clip)">
        {/* Curve (polyline) — for non-linear shapes */}
        {g.curve && g.curve.length > 1 && (
          <polyline
            points={g.curve.map(([x, y]) => `${tx(x)},${ty(y)}`).join(" ")}
            fill="none" stroke={STROKE} strokeWidth="1.75"
          />
        )}

        {/* Lines (full line through the two points, extended to plot edges) */}
        {(g.lines ?? []).map((ln, i) => {
          const dx = ln.x2 - ln.x1;
          const dy = ln.y2 - ln.y1;
          if (dx === 0 && dy === 0) return null;
          const t = 50;
          const x1 = ln.x1 - dx * t;
          const y1 = ln.y1 - dy * t;
          const x2 = ln.x2 + dx * t;
          const y2 = ln.y2 + dy * t;
          return (
            <line
              key={`ln-${i}`}
              x1={tx(x1)} y1={ty(y1)} x2={tx(x2)} y2={ty(y2)}
              stroke={STROKE} strokeWidth="1.75"
            />
          );
        })}

        {/* Vertical test lines (for VLT problems) — drawn semi-transparent */}
        {(g.verticals ?? []).map((x, i) => (
          <line
            key={`v-${i}`}
            x1={tx(x)} y1={pad} x2={tx(x)} y2={pad + innerSize}
            stroke={STROKE} strokeWidth="1" strokeDasharray="3 2" opacity="0.6"
          />
        ))}
      </g>

      {/* Plotted points */}
      {(g.points ?? []).map((p, i) => (
        <g key={`pt-${i}`}>
          <circle cx={tx(p.x)} cy={ty(p.y)} r="3" fill={STROKE} />
          {p.label && (
            <text
              x={tx(p.x) + 5} y={ty(p.y) - 5}
              fontSize={fs} fill={STROKE}
            >
              {p.label}
            </text>
          )}
        </g>
      ))}
    </svg>
  );
}
