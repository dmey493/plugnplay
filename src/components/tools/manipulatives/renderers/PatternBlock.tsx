import type { PatternBlockItem, PatternBlockShape } from "../types";
import { GRID, NAVY, STROKE_W } from "../constants";

/** Standard pattern-block colours (yellow hexagon, red trapezoid, …). */
const FILL: Record<PatternBlockShape, string> = {
  hexagon: "var(--pnp-yellow)",
  trapezoid: "var(--pnp-red)",
  rhombus: "var(--pnp-blue)",
  triangle: "var(--pnp-green)",
  square: "var(--pnp-orange)",
  thinRhombus: "#d2b48c", // tan — the physical block's colour
};

const S = GRID; // common side length so every block tiles with the others
const H = (Math.sqrt(3) / 2) * S;

/** Vertex list per shape, centred on the shape's bounding-box centre.
 *  Exported so snap logic can lock blocks together vertex-to-vertex. */
export function patternBlockPoints(shape: PatternBlockShape): [number, number][] {
  switch (shape) {
    case "hexagon":
      return [
        [S, 0],
        [S / 2, H],
        [-S / 2, H],
        [-S, 0],
        [-S / 2, -H],
        [S / 2, -H],
      ];
    case "trapezoid":
      return [
        [-S, H / 2],
        [S, H / 2],
        [S / 2, -H / 2],
        [-S / 2, -H / 2],
      ];
    case "rhombus": {
      // 60° rhombus: bbox is 1.5S × H.
      const w = 0.75 * S;
      return [
        [-w, -H / 2],
        [w - S / 2, -H / 2],
        [w, H / 2],
        [-w + S / 2, H / 2],
      ];
    }
    case "triangle":
      return [
        [-S / 2, H / 3],
        [S / 2, H / 3],
        [0, (-2 * H) / 3],
      ];
    case "square":
      return [
        [-S / 2, -S / 2],
        [S / 2, -S / 2],
        [S / 2, S / 2],
        [-S / 2, S / 2],
      ];
    case "thinRhombus": {
      // 30° rhombus: bbox is S(1+cos30) × S/2.
      const c = S * Math.cos(Math.PI / 6);
      const w = (S + c) / 2;
      const h = S / 4; // half of S·sin30
      return [
        [-w, -h],
        [-w + S, -h],
        [w, h],
        [w - S, h],
      ];
    }
  }
}

/** Pattern block — one of the six classic shapes, all with GRID-length
 *  sides so combinations tile exactly. */
export default function PatternBlock({ item }: { item: PatternBlockItem }) {
  const pts = patternBlockPoints(item.shape)
    .map(([x, y]) => `${x},${y}`)
    .join(" ");
  return (
    <polygon
      points={pts}
      fill={item.tint ?? FILL[item.shape]}
      stroke={NAVY}
      strokeWidth={STROKE_W}
      strokeLinejoin="round"
    />
  );
}
