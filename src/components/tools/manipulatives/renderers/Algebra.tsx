import type { AlgebraItem } from "../types";
import { GRID, NAVY, STROKE_W } from "../constants";

// Positive tiles are brand-coloured by type; negative tiles are red
// (the standard algebra-tile convention).
const POS_FILL: Record<AlgebraItem["tile"], string> = {
  x2: "var(--pnp-blue)",
  x: "var(--pnp-green)",
  unit: "var(--pnp-yellow)",
};

function dims(tile: AlgebraItem["tile"]) {
  if (tile === "x2") return { w: GRID * 4, h: GRID * 4 };
  if (tile === "x") return { w: GRID, h: GRID * 4 };
  return { w: GRID, h: GRID };
}

function label(item: AlgebraItem) {
  const base = item.tile === "x2" ? "x²" : item.tile === "x" ? "x" : "1";
  return item.sign < 0 ? `−${base}` : base;
}

/** Algebra tile — a rectangle sized to the term it represents, filled by
 *  type (positive) or red (negative), with the term label centred. */
export default function Algebra({ item }: { item: AlgebraItem }) {
  const { w, h } = dims(item.tile);
  const fill = item.tint ?? (item.sign < 0 ? "var(--pnp-red)" : POS_FILL[item.tile]);
  return (
    <g>
      <rect
        x={-w / 2}
        y={-h / 2}
        width={w}
        height={h}
        rx={3}
        fill={fill}
        stroke={NAVY}
        strokeWidth={STROKE_W}
      />
      <text
        x={0}
        y={0}
        textAnchor="middle"
        dominantBaseline="central"
        fontSize={item.tile === "unit" ? 16 : 22}
        fontWeight={800}
        fill={NAVY}
        style={{ fontFamily: "var(--font-heading), sans-serif", pointerEvents: "none" }}
      >
        {label(item)}
      </text>
    </g>
  );
}
