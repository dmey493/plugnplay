import type { LinkingCubeItem } from "../types";
import { GRID, NAVY, STROKE_W } from "../constants";

const FILL: Record<LinkingCubeItem["color"], string> = {
  blue: "var(--pnp-blue)",
  red: "var(--pnp-red)",
  green: "var(--pnp-green)",
  yellow: "var(--pnp-yellow)",
  orange: "var(--pnp-orange)",
  purple: "#a855f7",
};

/** Linking cube — a unit square with an inset connector nub so a stacked
 *  row/column reads as snapped-together cubes. */
export default function LinkingCube({ item }: { item: LinkingCubeItem }) {
  const s = GRID;
  const fill = item.tint ?? FILL[item.color];
  return (
    <g>
      <rect x={-s / 2} y={-s / 2} width={s} height={s} rx={4} fill={fill} stroke={NAVY} strokeWidth={STROKE_W} />
      {/* connector nub */}
      <circle r={s * 0.22} fill={fill} stroke={NAVY} strokeWidth={1.5} opacity={0.9} />
      <circle r={s * 0.1} fill="none" stroke={NAVY} strokeWidth={1} opacity={0.4} />
    </g>
  );
}
