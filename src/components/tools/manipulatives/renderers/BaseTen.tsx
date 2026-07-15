import type { BaseTenItem } from "../types";
import { GRID, NAVY, STROKE_W } from "../constants";

const FILL = "var(--pnp-blue)";

function dims(block: BaseTenItem["block"]) {
  if (block === "flat") return { w: GRID * 10, h: GRID * 10 };
  if (block === "rod") return { w: GRID, h: GRID * 10 };
  return { w: GRID, h: GRID };
}

/** Base-ten block — a filled rectangle scored into unit cells so the place
 *  value (1 / 10 / 100) is readable at a glance. Centred on the origin. */
export default function BaseTen({ item }: { item: BaseTenItem }) {
  const { w, h } = dims(item.block);
  const x0 = -w / 2;
  const y0 = -h / 2;
  const cols = Math.round(w / GRID);
  const rows = Math.round(h / GRID);
  const lines: React.ReactNode[] = [];
  for (let c = 1; c < cols; c++) {
    lines.push(
      <line key={`c${c}`} x1={x0 + c * GRID} y1={y0} x2={x0 + c * GRID} y2={y0 + h} stroke={NAVY} strokeWidth={1} opacity={0.55} />
    );
  }
  for (let r = 1; r < rows; r++) {
    lines.push(
      <line key={`r${r}`} x1={x0} y1={y0 + r * GRID} x2={x0 + w} y2={y0 + r * GRID} stroke={NAVY} strokeWidth={1} opacity={0.55} />
    );
  }
  return (
    <g>
      <rect x={x0} y={y0} width={w} height={h} rx={2} fill={item.tint ?? FILL} stroke={NAVY} strokeWidth={STROKE_W} />
      {lines}
    </g>
  );
}
