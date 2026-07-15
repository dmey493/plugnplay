import type { BeadItem, RekenrekItem } from "../types";
import { GRID, NAVY, REKENREK_ROD_W, REKENREK_ROW_H, STROKE_W } from "../constants";

/** Rekenrek frame — side rails and one or two horizontal rods. Beads are
 *  separate pieces that drag along a rod; rods sit on GRID rows so snapped
 *  beads line up on them. */
export default function Rekenrek({ item }: { item: RekenrekItem }) {
  const w = REKENREK_ROD_W + GRID;
  const h = item.rows * REKENREK_ROW_H;
  const railW = GRID / 2;
  const rods: React.ReactNode[] = [];
  for (let r = 0; r < item.rows; r++) {
    const y = -h / 2 + REKENREK_ROW_H / 2 + r * REKENREK_ROW_H;
    rods.push(
      <line key={r} x1={-w / 2 + railW / 2} y1={y} x2={w / 2 - railW / 2} y2={y} stroke={NAVY} strokeWidth={5} strokeLinecap="round" />
    );
  }
  return (
    <g>
      <rect x={-w / 2} y={-h / 2} width={railW} height={h} rx={6} fill={item.tint ?? "var(--pnp-orange)"} stroke={NAVY} strokeWidth={STROKE_W} />
      <rect x={w / 2 - railW} y={-h / 2} width={railW} height={h} rx={6} fill={item.tint ?? "var(--pnp-orange)"} stroke={NAVY} strokeWidth={STROKE_W} />
      {rods}
    </g>
  );
}

/** Rekenrek bead — a rounded bead sized to sit on a frame rod. */
export function Bead({ item }: { item: BeadItem }) {
  const rx = GRID / 2 - 2;
  const ry = GRID / 2 - 6;
  const fill = item.tint ?? (item.color === "red" ? "var(--pnp-red)" : "#ffffff");
  return (
    <g>
      <ellipse rx={rx} ry={ry} fill={fill} stroke={NAVY} strokeWidth={STROKE_W} />
      <ellipse rx={rx * 0.45} ry={ry * 0.4} cx={-rx * 0.25} cy={-ry * 0.3} fill="#ffffff" opacity={0.35} />
    </g>
  );
}
