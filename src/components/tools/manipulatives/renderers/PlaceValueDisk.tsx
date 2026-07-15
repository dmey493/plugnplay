import type { PlaceValueDiskItem } from "../types";
import { GRID, NAVY, STROKE_W } from "../constants";

/** Fill per power of ten, cycling brand tokens so each place value reads
 *  as a distinct colour. */
const FILLS: Record<number, string> = {
  3: "var(--pnp-orange)", // 1000
  2: "var(--pnp-green)", // 100
  1: "var(--pnp-red)", // 10
  0: "var(--pnp-yellow)", // 1
  [-1]: "var(--pnp-teal)", // 0.1
  [-2]: "var(--pnp-blue)", // 0.01
  [-3]: "#a855f7", // 0.001
};

export function diskLabel(exp: number): string {
  if (exp >= 0) return String(10 ** exp);
  return (10 ** exp).toFixed(-exp);
}

/** Place value disk — a labelled token, one colour per power of ten. */
export default function PlaceValueDisk({ item }: { item: PlaceValueDiskItem }) {
  const R = (GRID * 1.4) / 2;
  const label = diskLabel(item.exp);
  // Dark fills need light text; yellow/teal keep navy.
  const dark = item.exp === 1 || item.exp === -2 || item.exp === -3;
  return (
    <g>
      <circle r={R} fill={item.tint ?? FILLS[item.exp] ?? "var(--pnp-gray-200)"} stroke={NAVY} strokeWidth={STROKE_W} />
      <text
        x={0}
        y={0}
        textAnchor="middle"
        dominantBaseline="central"
        fontSize={label.length >= 5 ? 11 : label.length === 4 ? 12 : 15}
        fontWeight={800}
        fill={dark ? "#ffffff" : NAVY}
        style={{ fontFamily: "var(--font-heading), sans-serif", pointerEvents: "none" }}
      >
        {label}
      </text>
    </g>
  );
}
