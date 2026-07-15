/**
 * The manipulatives board object model.
 *
 * Every piece is an atomic instance positioned by its CENTRE in world
 * coordinates (x, y), with a rotation in degrees. Using the centre as the
 * origin keeps rotation and grid-snapping symmetric. Pieces are a flat,
 * fully-serialisable discriminated union keyed on `kind` — there is no
 * grouping or gluing in the MVP; snapping is purely visual alignment.
 */

export type { Camera } from "../canvas/useInfiniteCanvas";

export interface BaseItem {
  id: string;
  x: number; // world centre
  y: number;
  rot: number; // degrees
  z: number; // paint order; higher = on top
  /** Optional fill override chosen from the right-click palette. Renderers
   *  fall back to their kind's default colour when absent. */
  tint?: string;
}

/** Two-colour integer counter. Yellow = +1, red = −1. */
export interface CounterItem extends BaseItem {
  kind: "counter";
  color: "yellow" | "red";
}

/** Fraction tile. `denominator` 1 = a whole "1" bar; 2..12 = a 1/n slice. */
export interface FractionItem extends BaseItem {
  kind: "fraction";
  denominator: number; // 1..12
}

export type AlgTileType = "x2" | "x" | "unit";
/** Algebra tile. Negative tiles render red. */
export interface AlgebraItem extends BaseItem {
  kind: "algebra";
  tile: AlgTileType;
  sign: 1 | -1;
}

export type BaseTenType = "unit" | "rod" | "flat"; // 1, 10, 100
export interface BaseTenItem extends BaseItem {
  kind: "baseten";
  block: BaseTenType;
}

/** Number line segment with a tick every world GRID unit. */
export interface NumberLineItem extends BaseItem {
  kind: "numberline";
  min: number; // integer label at the left end
  max: number; // integer label at the right end
}

/** Square inch tile in one of the four classic colours. */
export interface ColorTileItem extends BaseItem {
  kind: "colortile";
  color: "red" | "blue" | "green" | "yellow";
}

/** Cuisenaire rod. `length` 1..10 units, standard rod colours. */
export interface CuisenaireItem extends BaseItem {
  kind: "cuisenaire";
  length: number; // 1..10
}

/** Fraction circle sector. `denominator` 1 = full circle; 2..12 = a 1/n
 *  sector. Centred on the CIRCLE centre so sectors dropped at the same
 *  point assemble into a whole by rotation alone. */
export interface FractionCircleItem extends BaseItem {
  kind: "fractioncircle";
  denominator: number; // 1..12
}

export type PatternBlockShape = "hexagon" | "trapezoid" | "rhombus" | "triangle" | "square" | "thinRhombus";
/** Pattern block — standard shape/colour pairs (yellow hexagon, red
 *  trapezoid, …), all sides one GRID unit so they tile. */
export interface PatternBlockItem extends BaseItem {
  kind: "patternblock";
  shape: PatternBlockShape;
}

/** Linking cube — a unit square with a connector nub. */
export interface LinkingCubeItem extends BaseItem {
  kind: "linkingcube";
  color: "blue" | "red" | "green" | "yellow" | "orange" | "purple";
}

/** Place value disk. Value is 10^exp; `exp` −3..3 (0.001 … 1000). */
export interface PlaceValueDiskItem extends BaseItem {
  kind: "pvdisk";
  exp: number; // -3..3
}

/** Static 10×10 hundred board (1–100). */
export interface HundredBoardItem extends BaseItem {
  kind: "hundredboard";
}

/** XY coordinate board — first quadrant (0..10) or four quadrant (−10..10). */
export interface XYBoardItem extends BaseItem {
  kind: "xyboard";
  quadrants: 1 | 4;
}

/** Geoboard — a square peg grid; bands are drawn with the ink tools. */
export interface GeoboardItem extends BaseItem {
  kind: "geoboard";
  pegs: number; // pegs per side (5 or 10)
}

/** Analog clock. The face and each hand are separate pieces so hands set
 *  the time via the existing rotate interaction (hands pivot at the face
 *  centre when dropped there). */
export interface ClockItem extends BaseItem {
  kind: "clock";
  part: "face" | "hour" | "minute";
}

/** Rekenrek frame (beads are separate BeadItems dragged along the rods). */
export interface RekenrekItem extends BaseItem {
  kind: "rekenrek";
  rows: 1 | 2;
}

/** Rekenrek bead — red or white, sized to sit on a frame rod. */
export interface BeadItem extends BaseItem {
  kind: "bead";
  color: "red" | "white";
}

export type Item =
  | CounterItem
  | FractionItem
  | AlgebraItem
  | BaseTenItem
  | NumberLineItem
  | ColorTileItem
  | CuisenaireItem
  | FractionCircleItem
  | PatternBlockItem
  | LinkingCubeItem
  | PlaceValueDiskItem
  | HundredBoardItem
  | XYBoardItem
  | GeoboardItem
  | ClockItem
  | RekenrekItem
  | BeadItem;
export type Kind = Item["kind"];

export interface Size {
  w: number;
  h: number;
}
