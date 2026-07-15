import type { Item, Size } from "./types";

/** One "unit" in world units. Every piece dimension is a multiple of this,
 *  so grid-snapping alone makes pieces tile cleanly. */
export const GRID = 40;

/** Fraction whole-bar geometry. A 1/n tile is FRACTION_BAR_W / n wide. */
export const FRACTION_BAR_W = 480;
export const FRACTION_BAR_H = 60;

/** Brand palette references (CSS custom properties resolve on :root, and
 *  work as SVG fill/stroke values). Strokes are always navy per the design
 *  system's comic-book language. */
export const NAVY = "var(--pnp-navy)";
export const STROKE_W = 2;

/** Denominator → fill, cycling brand tokens so each fraction size reads as
 *  a distinct colour (matches the per-item BRAND_CYCLE convention). */
export const FRACTION_FILLS: Record<number, string> = {
  1: "var(--pnp-gray-200)",
  2: "var(--pnp-blue)",
  3: "var(--pnp-orange)",
  4: "var(--pnp-green)",
  5: "var(--pnp-accent)",
  6: "var(--pnp-yellow)",
  7: "var(--pnp-teal)",
  8: "#a855f7", // amethyst — extends the ramp without a purple *interactive* surface
  9: "#ec4899",
  10: "#f43f5e",
  11: "#14b8a6",
  12: "#84cc16",
};

/** Fraction circle radius — a whole circle is comparable to the whole bar. */
export const FRACTION_CIRCLE_R = 80;

/** Clock face radius and hand lengths (hands pivot at their local origin). */
export const CLOCK_R = 120;
export const CLOCK_HOUR_LEN = 62;
export const CLOCK_MINUTE_LEN = 96;

/** XY board scale — half a GRID unit per integer keeps a ±10 board compact. */
export const XY_UNIT = GRID / 2;
export const XY_PAD = 20; // room for axis labels / arrowheads

/** Geoboard peg spacing is one GRID unit; PAD is the border margin. */
export const GEOBOARD_PAD = 20;

/** Rekenrek frame geometry: 10 beads per rod plus slack to slide them. */
export const REKENREK_ROD_W = GRID * 12;
export const REKENREK_ROW_H = GRID * 2;

/** Return the on-board footprint (unrotated) of an item, centred on origin. */
export function itemSize(item: Item): Size {
  switch (item.kind) {
    case "counter":
      return { w: GRID, h: GRID };
    case "fraction":
      return { w: FRACTION_BAR_W / item.denominator, h: FRACTION_BAR_H };
    case "algebra":
      return item.tile === "x2"
        ? { w: GRID * 4, h: GRID * 4 }
        : item.tile === "x"
          ? { w: GRID, h: GRID * 4 }
          : { w: GRID, h: GRID };
    case "baseten":
      return item.block === "flat"
        ? { w: GRID * 10, h: GRID * 10 }
        : item.block === "rod"
          ? { w: GRID, h: GRID * 10 }
          : { w: GRID, h: GRID };
    case "numberline":
      // One GRID unit per integer, plus room for arrowheads and labels.
      return { w: (item.max - item.min) * GRID + 24, h: 72 };
    case "colortile":
    case "linkingcube":
    case "bead":
      return { w: GRID, h: GRID };
    case "cuisenaire":
      return { w: item.length * GRID, h: GRID };
    case "fractioncircle":
      // Full-circle box regardless of sector size so the origin stays on
      // the circle centre — sectors assemble into a whole by rotation.
      return { w: FRACTION_CIRCLE_R * 2, h: FRACTION_CIRCLE_R * 2 };
    case "patternblock": {
      const s = GRID; // side length
      const h = (Math.sqrt(3) / 2) * s;
      switch (item.shape) {
        case "hexagon":
          return { w: 2 * s, h: 2 * h };
        case "trapezoid":
          return { w: 2 * s, h };
        case "rhombus":
          return { w: 1.5 * s, h };
        case "triangle":
          return { w: s, h };
        case "square":
          return { w: s, h: s };
        case "thinRhombus":
          return { w: s * (1 + Math.cos(Math.PI / 6)), h: s / 2 };
      }
      return { w: s, h: s };
    }
    case "pvdisk":
      return { w: GRID * 1.4, h: GRID * 1.4 };
    case "hundredboard":
      return { w: GRID * 10, h: GRID * 10 };
    case "xyboard": {
      const units = item.quadrants === 4 ? 20 : 10;
      const side = units * XY_UNIT + XY_PAD * 2;
      return { w: side, h: side };
    }
    case "geoboard": {
      const side = (item.pegs - 1) * GRID + GEOBOARD_PAD * 2;
      return { w: side, h: side };
    }
    case "clock":
      if (item.part === "face") return { w: CLOCK_R * 2, h: CLOCK_R * 2 };
      // Hands pivot at the origin but the box stays origin-centred so the
      // selection outline covers the full sweep.
      return item.part === "hour"
        ? { w: 16, h: CLOCK_HOUR_LEN * 2 }
        : { w: 16, h: CLOCK_MINUTE_LEN * 2 };
    case "rekenrek":
      return { w: REKENREK_ROD_W + GRID, h: item.rows * REKENREK_ROW_H };
  }
}

/** Right-click palette of fill overrides — brand tokens only. */
export const TINTS: string[] = [
  "var(--pnp-blue)",
  "var(--pnp-teal)",
  "var(--pnp-green)",
  "var(--pnp-yellow)",
  "var(--pnp-orange)",
  "var(--pnp-red)",
  "var(--pnp-gray-200)",
];

/** Axis-aligned bounding box (centred on the item origin) after rotation.
 *  Exact for 90° multiples; a conservative circumscribing box otherwise. */
export function rotatedHalfExtent(size: Size, rotDeg: number): Size {
  const rad = (rotDeg * Math.PI) / 180;
  const c = Math.abs(Math.cos(rad));
  const s = Math.abs(Math.sin(rad));
  return {
    w: (size.w * c + size.h * s) / 2,
    h: (size.w * s + size.h * c) / 2,
  };
}
