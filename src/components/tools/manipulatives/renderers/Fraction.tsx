import type { FractionItem } from "../types";
import { FRACTION_BAR_W, FRACTION_BAR_H, FRACTION_FILLS, NAVY, STROKE_W } from "../constants";

/** Fraction tile — a labelled bar segment. Width is the whole-bar width
 *  divided by the denominator; the label reads "1" for a whole or "1/n". */
export default function Fraction({ item }: { item: FractionItem }) {
  const w = FRACTION_BAR_W / item.denominator;
  const h = FRACTION_BAR_H;
  const label = item.denominator === 1 ? "1" : `1/${item.denominator}`;
  // Hide the label once the slice gets too narrow to hold it legibly.
  const showLabel = w >= 28;
  return (
    <g>
      <rect
        x={-w / 2}
        y={-h / 2}
        width={w}
        height={h}
        rx={4}
        fill={item.tint ?? FRACTION_FILLS[item.denominator] ?? "var(--pnp-gray-200)"}
        stroke={NAVY}
        strokeWidth={STROKE_W}
      />
      {showLabel && (
        <text
          x={0}
          y={0}
          textAnchor="middle"
          dominantBaseline="central"
          fontSize={18}
          fontWeight={700}
          fill={NAVY}
          style={{ fontFamily: "var(--font-heading), sans-serif", pointerEvents: "none" }}
        >
          {label}
        </text>
      )}
    </g>
  );
}
