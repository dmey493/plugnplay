"use client";

export type OrganizerKind =
  | "venn-2"
  | "venn-3"
  | "three-column"
  | "quadrants"
  | "step-ladder"
  | "frayer";

interface Props {
  kind: OrganizerKind;
  width: number;
  height: number;
}

/**
 * Decorative graphic-organizer scaffolding drawn behind the bubbles.
 * No drop zones, no snapping — just visual structure the teacher can use to
 * give meaning to where bubbles get placed.
 *
 * Strokes and labels use currentColor so the overlay tracks the theme's text
 * color (cyan-ink underwater, white-ink chalkboard, navy on light, etc.).
 * Renders at low-ish opacity so bubbles always read as the foreground.
 */
export default function OrganizerOverlay({ kind, width, height }: Props) {
  if (width === 0 || height === 0) return null;

  const common = {
    fill: "none" as const,
    stroke: "currentColor" as const,
    strokeWidth: 2,
    strokeLinejoin: "round" as const,
    strokeLinecap: "round" as const,
  };

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      className="pointer-events-none absolute inset-0 opacity-30"
      aria-hidden="true"
    >
      {kind === "venn-2" && <Venn2 width={width} height={height} common={common} />}
      {kind === "venn-3" && <Venn3 width={width} height={height} common={common} />}
      {kind === "three-column" && <ThreeColumn width={width} height={height} common={common} />}
      {kind === "quadrants" && <Quadrants width={width} height={height} common={common} />}
      {kind === "step-ladder" && <StepLadder width={width} height={height} common={common} />}
      {kind === "frayer" && <Frayer width={width} height={height} common={common} />}
    </svg>
  );
}

interface Geom {
  width: number;
  height: number;
  common: {
    fill: "none";
    stroke: "currentColor";
    strokeWidth: number;
    strokeLinejoin: "round";
    strokeLinecap: "round";
  };
}

function Label({
  x,
  y,
  text,
  size = 18,
  anchor = "middle",
}: {
  x: number;
  y: number;
  text: string;
  size?: number;
  anchor?: "start" | "middle" | "end";
}) {
  return (
    <text
      x={x}
      y={y}
      fill="currentColor"
      fontSize={size}
      fontFamily="system-ui, sans-serif"
      fontWeight={700}
      textAnchor={anchor}
      dominantBaseline="middle"
    >
      {text}
    </text>
  );
}

// =====================
// VENN 2-CIRCLE
// =====================
function Venn2({ width, height, common }: Geom) {
  const cy = height * 0.55;
  const r = Math.min(width * 0.22, height * 0.4);
  const cx1 = width * 0.38;
  const cx2 = width * 0.62;
  return (
    <g {...common}>
      <circle cx={cx1} cy={cy} r={r} />
      <circle cx={cx2} cy={cy} r={r} />
      <Label x={cx1 - r * 0.5} y={height * 0.12} text="A" size={32} />
      <Label x={cx2 + r * 0.5} y={height * 0.12} text="B" size={32} />
      <Label x={(cx1 + cx2) / 2} y={cy + r * 0.95} text="Both" size={20} />
    </g>
  );
}

// =====================
// VENN 3-CIRCLE
// =====================
function Venn3({ width, height, common }: Geom) {
  const r = Math.min(width * 0.2, height * 0.32);
  const cx = width / 2;
  const cyTop = height * 0.4;
  const dy = r * 0.8;
  const dx = r * 0.85;
  const c1 = { x: cx, y: cyTop };
  const c2 = { x: cx - dx, y: cyTop + dy };
  const c3 = { x: cx + dx, y: cyTop + dy };
  return (
    <g {...common}>
      <circle cx={c1.x} cy={c1.y} r={r} />
      <circle cx={c2.x} cy={c2.y} r={r} />
      <circle cx={c3.x} cy={c3.y} r={r} />
      <Label x={c1.x} y={c1.y - r - 14} text="A" size={28} />
      <Label x={c2.x - r * 0.7} y={c2.y + r * 1.1} text="B" size={28} />
      <Label x={c3.x + r * 0.7} y={c3.y + r * 1.1} text="C" size={28} />
    </g>
  );
}

// =====================
// THREE COLUMN
// =====================
function ThreeColumn({ width, height, common }: Geom) {
  const top = height * 0.08;
  const bottom = height * 0.92;
  const x1 = width * (1 / 3);
  const x2 = width * (2 / 3);
  const headerY = height * 0.05;
  return (
    <g {...common}>
      <line x1={x1} y1={top} x2={x1} y2={bottom} />
      <line x1={x2} y1={top} x2={x2} y2={bottom} />
      <line x1={width * 0.04} y1={top + 30} x2={width * 0.96} y2={top + 30} />
      <Label x={x1 / 2} y={headerY + 30} text="Column A" size={22} />
      <Label x={(x1 + x2) / 2} y={headerY + 30} text="Column B" size={22} />
      <Label x={(x2 + width) / 2} y={headerY + 30} text="Column C" size={22} />
    </g>
  );
}

// =====================
// 2x2 QUADRANTS
// =====================
function Quadrants({ width, height, common }: Geom) {
  const cx = width / 2;
  const cy = height / 2;
  return (
    <g {...common}>
      <line x1={cx} y1={height * 0.06} x2={cx} y2={height * 0.94} />
      <line x1={width * 0.04} y1={cy} x2={width * 0.96} y2={cy} />
      {/* axis labels */}
      <Label x={width * 0.02} y={cy} text="←" size={20} anchor="start" />
      <Label x={width * 0.98} y={cy} text="→" size={20} anchor="end" />
      <Label x={cx} y={height * 0.04} text="↑" size={20} />
      <Label x={cx} y={height * 0.96} text="↓" size={20} />
      <Label x={cx * 0.5} y={cy * 0.5} text="Q2" size={28} />
      <Label x={cx + cx * 0.5} y={cy * 0.5} text="Q1" size={28} />
      <Label x={cx * 0.5} y={cy + cy * 0.5} text="Q3" size={28} />
      <Label x={cx + cx * 0.5} y={cy + cy * 0.5} text="Q4" size={28} />
    </g>
  );
}

// =====================
// STEP LADDER
// =====================
function StepLadder({ width, height, common }: Geom) {
  const steps = 5;
  const padX = width * 0.06;
  const padY = height * 0.08;
  const lineY = height * 0.7;
  const slotW = (width - 2 * padX) / steps;
  return (
    <g {...common}>
      {/* horizontal anchor line */}
      <line x1={padX} y1={lineY} x2={width - padX} y2={lineY} />
      {/* arrow on the right */}
      <line x1={width - padX} y1={lineY} x2={width - padX - 16} y2={lineY - 10} strokeWidth={1.5} />
      <line x1={width - padX} y1={lineY} x2={width - padX - 16} y2={lineY + 10} strokeWidth={1.5} />
      {/* step ticks + numbers */}
      {Array.from({ length: steps }).map((_, i) => {
        const x = padX + slotW * (i + 0.5);
        return (
          <g key={i}>
            <line x1={x} y1={lineY - 12} x2={x} y2={lineY + 12} strokeWidth={1.5} />
            <Label x={x} y={lineY + 36} text={`${i + 1}`} size={22} />
          </g>
        );
      })}
      {/* end labels */}
      <Label x={padX} y={padY} text="Easiest" size={20} anchor="start" />
      <Label x={width - padX} y={padY} text="Hardest" size={20} anchor="end" />
    </g>
  );
}

// =====================
// FRAYER MODEL
// =====================
function Frayer({ width, height, common }: Geom) {
  const cx = width / 2;
  const cy = height / 2;
  const ovalRx = width * 0.13;
  const ovalRy = height * 0.07;
  const padX = width * 0.04;
  const padY = height * 0.04;
  return (
    <g {...common}>
      {/* outer rectangle */}
      <rect x={padX} y={padY} width={width - 2 * padX} height={height - 2 * padY} rx={8} />
      {/* dividing cross */}
      <line x1={cx} y1={padY} x2={cx} y2={height - padY} />
      <line x1={padX} y1={cy} x2={width - padX} y2={cy} />
      {/* center oval (concept) */}
      <ellipse cx={cx} cy={cy} rx={ovalRx} ry={ovalRy} fill="currentColor" fillOpacity={0.08} />
      <Label x={cx} y={cy} text="Concept" size={20} />
      {/* quadrant labels */}
      <Label x={padX + 16} y={padY + 22} text="Definition" size={18} anchor="start" />
      <Label x={width - padX - 16} y={padY + 22} text="Characteristics" size={18} anchor="end" />
      <Label x={padX + 16} y={height - padY - 16} text="Examples" size={18} anchor="start" />
      <Label x={width - padX - 16} y={height - padY - 16} text="Non-Examples" size={18} anchor="end" />
    </g>
  );
}
