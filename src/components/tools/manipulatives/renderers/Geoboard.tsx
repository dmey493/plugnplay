import type { GeoboardItem } from "../types";
import { GEOBOARD_PAD, GRID, NAVY, STROKE_W } from "../constants";

/** Geoboard — a square peg grid on a board. Bands are drawn over it with
 *  the ink line/pen tools; pegs sit on GRID points so snapped line ends
 *  land exactly on a peg. */
export default function Geoboard({ item }: { item: GeoboardItem }) {
  const n = item.pegs;
  const side = (n - 1) * GRID + GEOBOARD_PAD * 2;
  const x0 = -side / 2 + GEOBOARD_PAD;
  const pegs: React.ReactNode[] = [];
  for (let r = 0; r < n; r++) {
    for (let c = 0; c < n; c++) {
      pegs.push(<circle key={`${r}-${c}`} cx={x0 + c * GRID} cy={x0 + r * GRID} r={4} fill={NAVY} />);
    }
  }
  return (
    <g>
      <rect
        x={-side / 2}
        y={-side / 2}
        width={side}
        height={side}
        rx={8}
        fill={item.tint ?? "var(--pnp-gray-100)"}
        stroke={NAVY}
        strokeWidth={STROKE_W}
      />
      {pegs}
    </g>
  );
}
