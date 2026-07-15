import type { CounterItem } from "../types";
import { GRID, NAVY, STROKE_W } from "../constants";

const R = GRID / 2;
const FILL: Record<CounterItem["color"], string> = {
  yellow: "var(--pnp-yellow)",
  red: "var(--pnp-red)",
};

/** Two-colour counter — a filled disc with a subtle inner ring so the
 *  chip reads as a physical token. Drawn centred on the local origin. */
export default function Counter({ item }: { item: CounterItem }) {
  return (
    <g>
      <circle r={R} fill={item.tint ?? FILL[item.color]} stroke={NAVY} strokeWidth={STROKE_W} />
      <circle r={R - 5} fill="none" stroke={NAVY} strokeWidth={1} opacity={0.35} />
    </g>
  );
}
