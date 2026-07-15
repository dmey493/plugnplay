import type { Item, Kind } from "./types";
import { itemSize } from "./constants";
import ItemShape from "./ItemShape";

// Distributive Omit so each union member keeps its own discriminant props.
type DistributiveOmit<T, K extends keyof T> = T extends unknown ? Omit<T, K> : never;
/** A piece template minus its placement fields (id/x/y/z assigned on drop). */
export type Sample = DistributiveOmit<Item, "id" | "x" | "y" | "z">;

/** A single draggable source in the tray. `make` builds a fresh instance
 *  centred at world point `at`; the board assigns the final id and z. */
export interface Variant {
  id: string; // stable key within its kind
  label: string;
  /** Sample instance used both to render the tray preview and as the
   *  template `make` fills in. */
  sample: Sample;
}

export interface KindDef {
  kind: Kind;
  label: string;
  variants: Variant[];
}

export const KINDS: KindDef[] = [
  {
    kind: "counter",
    label: "Counters",
    variants: [
      { id: "yellow", label: "+1", sample: { kind: "counter", color: "yellow", rot: 0 } },
      { id: "red", label: "−1", sample: { kind: "counter", color: "red", rot: 0 } },
    ],
  },
  {
    kind: "fraction",
    label: "Fraction tiles",
    variants: [1, 2, 3, 4, 5, 6, 8, 10, 12].map((d) => ({
      id: `f${d}`,
      label: d === 1 ? "1" : `1/${d}`,
      sample: { kind: "fraction", denominator: d, rot: 0 } as Sample,
    })),
  },
  {
    kind: "algebra",
    label: "Algebra tiles",
    variants: [
      { id: "x2p", label: "x²", sample: { kind: "algebra", tile: "x2", sign: 1, rot: 0 } },
      { id: "xp", label: "x", sample: { kind: "algebra", tile: "x", sign: 1, rot: 0 } },
      { id: "up", label: "1", sample: { kind: "algebra", tile: "unit", sign: 1, rot: 0 } },
      { id: "x2n", label: "−x²", sample: { kind: "algebra", tile: "x2", sign: -1, rot: 0 } },
      { id: "xn", label: "−x", sample: { kind: "algebra", tile: "x", sign: -1, rot: 0 } },
      { id: "un", label: "−1", sample: { kind: "algebra", tile: "unit", sign: -1, rot: 0 } },
    ],
  },
  {
    kind: "baseten",
    label: "Base-ten blocks",
    variants: [
      { id: "unit", label: "1", sample: { kind: "baseten", block: "unit", rot: 0 } },
      { id: "rod", label: "10", sample: { kind: "baseten", block: "rod", rot: 0 } },
      { id: "flat", label: "100", sample: { kind: "baseten", block: "flat", rot: 0 } },
    ],
  },
  {
    kind: "numberline",
    label: "Number lines",
    variants: [
      { id: "0-10", label: "0 to 10", sample: { kind: "numberline", min: 0, max: 10, rot: 0 } },
      { id: "n10-10", label: "−10 to 10", sample: { kind: "numberline", min: -10, max: 10, rot: 0 } },
      { id: "0-20", label: "0 to 20", sample: { kind: "numberline", min: 0, max: 20, rot: 0 } },
    ],
  },
  {
    kind: "colortile",
    label: "Color tiles",
    variants: (["red", "blue", "green", "yellow"] as const).map((c) => ({
      id: c,
      label: c[0].toUpperCase() + c.slice(1),
      sample: { kind: "colortile", color: c, rot: 0 } as Sample,
    })),
  },
  {
    kind: "linkingcube",
    label: "Linking cubes",
    variants: (["blue", "red", "green", "yellow", "orange", "purple"] as const).map((c) => ({
      id: c,
      label: c[0].toUpperCase() + c.slice(1),
      sample: { kind: "linkingcube", color: c, rot: 0 } as Sample,
    })),
  },
  {
    kind: "cuisenaire",
    label: "Cuisenaire rods",
    variants: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => ({
      id: `r${n}`,
      label: String(n),
      sample: { kind: "cuisenaire", length: n, rot: 0 } as Sample,
    })),
  },
  {
    kind: "fractioncircle",
    label: "Fraction circles",
    variants: [1, 2, 3, 4, 5, 6, 8, 10, 12].map((d) => ({
      id: `c${d}`,
      label: d === 1 ? "1" : `1/${d}`,
      sample: { kind: "fractioncircle", denominator: d, rot: 0 } as Sample,
    })),
  },
  {
    kind: "patternblock",
    label: "Pattern blocks",
    variants: [
      { id: "hex", label: "Hexagon", sample: { kind: "patternblock", shape: "hexagon", rot: 0 } },
      { id: "trap", label: "Trapezoid", sample: { kind: "patternblock", shape: "trapezoid", rot: 0 } },
      { id: "rhom", label: "Rhombus", sample: { kind: "patternblock", shape: "rhombus", rot: 0 } },
      { id: "tri", label: "Triangle", sample: { kind: "patternblock", shape: "triangle", rot: 0 } },
      { id: "sq", label: "Square", sample: { kind: "patternblock", shape: "square", rot: 0 } },
      { id: "thin", label: "Thin rhombus", sample: { kind: "patternblock", shape: "thinRhombus", rot: 0 } },
    ],
  },
  {
    kind: "pvdisk",
    label: "Place value disks",
    variants: [3, 2, 1, 0, -1, -2, -3].map((exp) => ({
      id: `e${exp}`,
      label: exp >= 0 ? String(10 ** exp) : (10 ** exp).toFixed(-exp),
      sample: { kind: "pvdisk", exp, rot: 0 } as Sample,
    })),
  },
  {
    kind: "rekenrek",
    label: "Rekenrek",
    variants: [
      { id: "frame2", label: "Frame (2 rows)", sample: { kind: "rekenrek", rows: 2, rot: 0 } },
      { id: "frame1", label: "Frame (1 row)", sample: { kind: "rekenrek", rows: 1, rot: 0 } },
      { id: "beadr", label: "Red bead", sample: { kind: "bead", color: "red", rot: 0 } },
      { id: "beadw", label: "White bead", sample: { kind: "bead", color: "white", rot: 0 } },
    ],
  },
  {
    kind: "clock",
    label: "Clock",
    variants: [
      { id: "face", label: "Face", sample: { kind: "clock", part: "face", rot: 0 } },
      { id: "hour", label: "Hour hand", sample: { kind: "clock", part: "hour", rot: 0 } },
      { id: "minute", label: "Minute hand", sample: { kind: "clock", part: "minute", rot: 0 } },
    ],
  },
  {
    kind: "hundredboard",
    label: "Hundred board",
    variants: [{ id: "board", label: "1–100", sample: { kind: "hundredboard", rot: 0 } }],
  },
  {
    kind: "geoboard",
    label: "Geoboards",
    variants: [
      { id: "5", label: "5 × 5", sample: { kind: "geoboard", pegs: 5, rot: 0 } },
      { id: "10", label: "10 × 10", sample: { kind: "geoboard", pegs: 10, rot: 0 } },
    ],
  },
  {
    kind: "xyboard",
    label: "XY coordinate board",
    variants: [
      { id: "q1", label: "Quadrant I", sample: { kind: "xyboard", quadrants: 1, rot: 0 } },
      { id: "q4", label: "4 quadrants", sample: { kind: "xyboard", quadrants: 4, rot: 0 } },
    ],
  },
];

let counter = 0;
export function nextId(): string {
  // Deterministic within a session; combined with a per-mount prefix so
  // ids stay unique across reloads without needing Date.now/random here.
  counter += 1;
  return `m${counter.toString(36)}`;
}

/** Build a placed instance from a variant sample. */
export function makeItem(sample: Variant["sample"], at: { x: number; y: number }, id: string, z: number): Item {
  return { ...sample, id, x: at.x, y: at.y, z } as Item;
}

/** A small SVG preview of a variant, fit into a square tray chip. */
export function VariantPreview({ sample, box = 44 }: { sample: Variant["sample"]; box?: number }) {
  const item = { ...sample, id: "preview", x: 0, y: 0, z: 0 } as Item;
  const { w, h } = itemSize(item);
  const pad = 4;
  const scale = (box - pad * 2) / Math.max(w, h);
  const vw = box / scale;
  return (
    <svg
      width={box}
      height={box}
      viewBox={`${-vw / 2} ${-vw / 2} ${vw} ${vw}`}
      aria-hidden="true"
      style={{ display: "block" }}
    >
      <ItemShape item={item} />
    </svg>
  );
}
