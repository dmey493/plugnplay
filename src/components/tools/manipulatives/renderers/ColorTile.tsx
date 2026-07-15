import type { ColorTileItem } from "../types";
import { GRID, NAVY, STROKE_W } from "../constants";

const FILL: Record<ColorTileItem["color"], string> = {
  red: "var(--pnp-red)",
  blue: "var(--pnp-blue)",
  green: "var(--pnp-green)",
  yellow: "var(--pnp-yellow)",
};

/** Color tile — a plain unit square in one of the four classic colours. */
export default function ColorTile({ item }: { item: ColorTileItem }) {
  return (
    <rect
      x={-GRID / 2}
      y={-GRID / 2}
      width={GRID}
      height={GRID}
      rx={3}
      fill={item.tint ?? FILL[item.color]}
      stroke={NAVY}
      strokeWidth={STROKE_W}
    />
  );
}
