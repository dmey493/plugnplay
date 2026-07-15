import type { Camera } from "./useInfiniteCanvas";
import type { Stroke } from "./ink";
import type { Item } from "../manipulatives/types";

/**
 * The unified canvas document — one persisted board holding manipulative
 * items, ink strokes, imported pages, and the camera. Whiteboard and
 * manipulatives are two entry points over this same document shape, each
 * with its own localStorage key so teachers' boards stay separate.
 */

export type CanvasBackground = "blank" | "dots" | "grid" | "coordinate";

/** A raster placed behind everything in world coordinates — a rendered PDF
 *  page or an imported image. Pans and zooms locked to the board. */
export interface BackgroundImage {
  id: string;
  href: string; // data URL
  x: number; // world coords (top-left)
  y: number;
  width: number; // world units
  height: number;
}

export interface BoardDocV2 {
  version: 2;
  items: Item[];
  strokes: Stroke[];
  pages: BackgroundImage[];
  background: CanvasBackground;
  gridSnap: boolean;
  camera: Camera | null;
  savedAt: number;
}

export type { Camera, Stroke, Item };
