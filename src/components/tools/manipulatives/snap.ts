import type { Item } from "./types";
import { GRID, itemSize, rotatedHalfExtent } from "./constants";

/** Snap a value to the nearest grid line. */
export function snapToGrid(v: number): number {
  return Math.round(v / GRID) * GRID;
}

/** Rotation snap: 90° steps by default, 15° with fine control. */
export function snapRotation(deg: number, fine: boolean): number {
  const step = fine ? 15 : 90;
  return ((Math.round(deg / step) * step) % 360 + 360) % 360;
}

interface Box {
  left: number;
  right: number;
  top: number;
  bottom: number;
  cx: number;
  cy: number;
}

function boxOf(item: Item): Box {
  const { w, h } = rotatedHalfExtent(itemSize(item), item.rot);
  return { left: item.x - w, right: item.x + w, top: item.y - h, bottom: item.y + h, cx: item.x, cy: item.y };
}

/**
 * Neighbour-edge snapping (used when grid-snap is off). Nudges the moving
 * item so a horizontal/vertical edge or centre coincides with a nearby
 * static item's, within `threshold` world units. Only the moving item's
 * position changes; O(n²) over a few dozen pieces is fine.
 *
 * Rotated pieces (rot not a multiple of 90°) use a circumscribing box, so
 * their snapping is approximate — good enough for visual alignment.
 */
export function snapToNeighbors(
  moving: Item,
  others: Item[],
  threshold: number
): { x: number; y: number; snappedX: boolean; snappedY: boolean } {
  const m = boxOf(moving);
  // Held in a container object so the closures below can mutate them
  // without TS narrowing the locals to `null` via control-flow analysis.
  const best: { dx: { d: number; off: number } | null; dy: { d: number; off: number } | null } = {
    dx: null,
    dy: null,
  };

  const considerX = (movingEdge: number, staticEdge: number) => {
    const off = staticEdge - movingEdge;
    const d = Math.abs(off);
    if (d <= threshold && (!best.dx || d < best.dx.d)) best.dx = { d, off };
  };
  const considerY = (movingEdge: number, staticEdge: number) => {
    const off = staticEdge - movingEdge;
    const d = Math.abs(off);
    if (d <= threshold && (!best.dy || d < best.dy.d)) best.dy = { d, off };
  };

  for (const o of others) {
    if (o.id === moving.id) continue;
    const b = boxOf(o);
    // Left/right/centre alignments (X axis).
    for (const me of [m.left, m.right, m.cx]) {
      for (const se of [b.left, b.right, b.cx]) considerX(me, se);
    }
    // Edge-to-edge abutment (right→left, left→right).
    considerX(m.right, b.left);
    considerX(m.left, b.right);
    // Top/bottom/centre alignments (Y axis).
    for (const me of [m.top, m.bottom, m.cy]) {
      for (const se of [b.top, b.bottom, b.cy]) considerY(me, se);
    }
    considerY(m.bottom, b.top);
    considerY(m.top, b.bottom);
  }

  return {
    x: moving.x + (best.dx ? best.dx.off : 0),
    y: moving.y + (best.dy ? best.dy.off : 0),
    snappedX: best.dx !== null,
    snappedY: best.dy !== null,
  };
}

/** Does item's rotated bounding box intersect an axis-aligned world rect? */
export function intersectsRect(
  item: Item,
  rect: { x1: number; y1: number; x2: number; y2: number }
): boolean {
  const b = boxOf(item);
  const rx1 = Math.min(rect.x1, rect.x2);
  const rx2 = Math.max(rect.x1, rect.x2);
  const ry1 = Math.min(rect.y1, rect.y2);
  const ry2 = Math.max(rect.y1, rect.y2);
  return b.left <= rx2 && b.right >= rx1 && b.top <= ry2 && b.bottom >= ry1;
}
