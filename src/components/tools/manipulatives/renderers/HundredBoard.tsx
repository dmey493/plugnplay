import type { HundredBoardItem } from "../types";
import { GRID, NAVY, STROKE_W } from "../constants";

/** Hundred board — a static 10×10 grid numbered 1–100. Circling and
 *  shading happen with the ink tools on top. */
export default function HundredBoard({ item }: { item: HundredBoardItem }) {
  const w = GRID * 10;
  const x0 = -w / 2;
  const y0 = -w / 2;
  const cells: React.ReactNode[] = [];
  for (let n = 1; n <= 100; n++) {
    const c = (n - 1) % 10;
    const r = Math.floor((n - 1) / 10);
    cells.push(
      <text
        key={n}
        x={x0 + c * GRID + GRID / 2}
        y={y0 + r * GRID + GRID / 2}
        textAnchor="middle"
        dominantBaseline="central"
        fontSize={14}
        fontWeight={600}
        fill={NAVY}
        style={{ fontFamily: "var(--font-heading), sans-serif", pointerEvents: "none" }}
      >
        {n}
      </text>
    );
  }
  const lines: React.ReactNode[] = [];
  for (let i = 1; i < 10; i++) {
    lines.push(
      <line key={`v${i}`} x1={x0 + i * GRID} y1={y0} x2={x0 + i * GRID} y2={y0 + w} stroke={NAVY} strokeWidth={1} opacity={0.4} />,
      <line key={`h${i}`} x1={x0} y1={y0 + i * GRID} x2={x0 + w} y2={y0 + i * GRID} stroke={NAVY} strokeWidth={1} opacity={0.4} />
    );
  }
  return (
    <g>
      <rect x={x0} y={y0} width={w} height={w} rx={4} fill={item.tint ?? "#ffffff"} stroke={NAVY} strokeWidth={STROKE_W} />
      {lines}
      {cells}
    </g>
  );
}
