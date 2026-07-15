import type { XYBoardItem } from "../types";
import { NAVY, STROKE_W, XY_PAD, XY_UNIT } from "../constants";

/** XY coordinate board — first quadrant (0..10) or four quadrant
 *  (−10..10), with axes, unit grid, and labels every 5. Points and lines
 *  are plotted with the ink tools on top. */
export default function XYBoard({ item }: { item: XYBoardItem }) {
  const four = item.quadrants === 4;
  const min = four ? -10 : 0;
  const max = 10;
  const span = (max - min) * XY_UNIT;
  const side = span + XY_PAD * 2;
  const x0 = -side / 2 + XY_PAD; // world x of grid-min
  const y0 = -side / 2 + XY_PAD; // world y of grid-max (svg y grows down)
  const toX = (v: number) => x0 + (v - min) * XY_UNIT;
  const toY = (v: number) => y0 + (max - v) * XY_UNIT;
  // Axis positions: through 0 on a four-quadrant board, along the edge otherwise.
  const axX = toX(0);
  const axY = toY(0);

  const grid: React.ReactNode[] = [];
  const labels: React.ReactNode[] = [];
  for (let v = min; v <= max; v++) {
    const gx = toX(v);
    const gy = toY(v);
    grid.push(
      <line key={`v${v}`} x1={gx} y1={toY(max)} x2={gx} y2={toY(min)} stroke={NAVY} strokeWidth={v === 0 && four ? 0 : 1} opacity={0.18} />,
      <line key={`h${v}`} x1={toX(min)} y1={gy} x2={toX(max)} y2={gy} stroke={NAVY} strokeWidth={v === 0 && four ? 0 : 1} opacity={0.18} />
    );
    if (v !== 0 && v % 5 === 0) {
      labels.push(
        <text key={`lx${v}`} x={gx} y={axY + 14} textAnchor="middle" fontSize={11} fontWeight={600} fill={NAVY} style={{ pointerEvents: "none" }}>
          {v}
        </text>,
        <text key={`ly${v}`} x={axX - 8} y={gy} textAnchor="end" dominantBaseline="central" fontSize={11} fontWeight={600} fill={NAVY} style={{ pointerEvents: "none" }}>
          {v}
        </text>
      );
    }
  }

  const arrow = 6;
  return (
    <g>
      <rect x={-side / 2} y={-side / 2} width={side} height={side} rx={4} fill={item.tint ?? "#ffffff"} stroke={NAVY} strokeWidth={STROKE_W} />
      {grid}
      {/* axes */}
      <line x1={toX(min)} y1={axY} x2={toX(max)} y2={axY} stroke={NAVY} strokeWidth={STROKE_W} />
      <line x1={axX} y1={toY(max)} x2={axX} y2={toY(min)} stroke={NAVY} strokeWidth={STROKE_W} />
      <path d={`M ${toX(max)} ${axY} l ${-arrow} ${-arrow / 2} v ${arrow} Z`} fill={NAVY} />
      <path d={`M ${axX} ${toY(max)} l ${-arrow / 2} ${arrow} h ${arrow} Z`} fill={NAVY} />
      <text x={toX(max) + 4} y={axY - 6} fontSize={12} fontWeight={700} fill={NAVY} fontStyle="italic" style={{ pointerEvents: "none" }}>
        x
      </text>
      <text x={axX + 6} y={toY(max) + 6} fontSize={12} fontWeight={700} fill={NAVY} fontStyle="italic" style={{ pointerEvents: "none" }}>
        y
      </text>
      {labels}
    </g>
  );
}
