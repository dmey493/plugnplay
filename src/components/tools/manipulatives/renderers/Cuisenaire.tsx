import type { CuisenaireItem } from "../types";
import { GRID, NAVY, STROKE_W } from "../constants";

/** Standard Cuisenaire rod colours by length — teachers expect these, so
 *  raw hexes are used where the brand palette has no equivalent. */
const ROD_FILLS: Record<number, string> = {
  1: "#ffffff",
  2: "var(--pnp-red)",
  3: "#86efac", // light green
  4: "#a855f7", // purple
  5: "var(--pnp-yellow)",
  6: "#16a34a", // dark green
  7: "#374151", // black
  8: "#92400e", // brown
  9: "var(--pnp-blue)",
  10: "var(--pnp-orange)",
};

/** Cuisenaire rod — a solid bar `length` units long with faint unit
 *  scoring so lengths compare at a glance. */
export default function Cuisenaire({ item }: { item: CuisenaireItem }) {
  const w = item.length * GRID;
  const h = GRID;
  const x0 = -w / 2;
  const ticks: React.ReactNode[] = [];
  for (let i = 1; i < item.length; i++) {
    ticks.push(
      <line key={i} x1={x0 + i * GRID} y1={-h / 2} x2={x0 + i * GRID} y2={h / 2} stroke={NAVY} strokeWidth={1} opacity={0.25} />
    );
  }
  return (
    <g>
      <rect
        x={x0}
        y={-h / 2}
        width={w}
        height={h}
        rx={4}
        fill={item.tint ?? ROD_FILLS[item.length] ?? "var(--pnp-gray-200)"}
        stroke={NAVY}
        strokeWidth={STROKE_W}
      />
      {ticks}
    </g>
  );
}
