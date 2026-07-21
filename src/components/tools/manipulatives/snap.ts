import type { Item, PatternBlockItem } from "./types";
import { GRID, itemSize, rotatedHalfExtent } from "./constants";
import { patternBlockPoints } from "./renderers/PatternBlock";

/** Snap a value to the nearest grid line. */
export function snapToGrid(v: number): number {
  return Math.round(v / GRID) * GRID;
}

/** Rotation snap in `step`° increments (90 for boxy pieces, 30 for pattern
 *  blocks so triangles/hexagons land on tiling angles, 15 with fine control). */
export function snapRotation(deg: number, step: number): number {
  return ((Math.round(deg / step) * step) % 360 + 360) % 360;
}

/** Rotation step for a piece: pattern blocks tile at 30° multiples;
 *  everything else keeps the boxy 90° default. Shift = 15° fine control. */
export function rotationStep(item: Item, fine: boolean): number {
  if (fine) return 15;
  return item.kind === "patternblock" ? 30 : 90;
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

/** World-space polygon vertices of a pattern block (rotation applied). */
function worldVertices(item: PatternBlockItem): [number, number][] {
  const rad = (item.rot * Math.PI) / 180;
  const cos = Math.cos(rad);
  const sin = Math.sin(rad);
  return patternBlockPoints(item.shape).map(([px, py]) => [
    item.x + px * cos - py * sin,
    item.y + px * sin + py * cos,
  ]);
}

/**
 * Vertex-to-vertex snapping for pattern blocks: shift the moving block so
 * its nearest vertex coincides with the nearest vertex of a neighbouring
 * block, within `threshold` world units. Because every block has GRID-length
 * sides, locking one vertex pair makes edges sit flush whenever rotations
 * are compatible — the pieces "click" together like the physical blocks.
 *
 * Returns a full 2D offset (unlike the axis-independent box snapping) plus
 * a flag; when snapped, callers should skip grid snapping entirely so the
 * lock between shapes always beats the board.
 */
export function snapToVertices(
  moving: Item,
  others: Item[],
  threshold: number
): { dx: number; dy: number; snapped: boolean } {
  if (moving.kind !== "patternblock") return { dx: 0, dy: 0, snapped: false };
  const mv = worldVertices(moving);
  let best: { d: number; dx: number; dy: number } | null = null;
  for (const o of others) {
    if (o.kind !== "patternblock" || o.id === moving.id) continue;
    // Cheap reject: centres further apart than both circumradii + threshold
    // can't have vertices in range (largest block spans ~2·GRID).
    if (Math.hypot(o.x - moving.x, o.y - moving.y) > 4 * GRID + threshold) continue;
    for (const [ox, oy] of worldVertices(o)) {
      for (const [mx, my] of mv) {
        const dx = ox - mx;
        const dy = oy - my;
        const d = Math.hypot(dx, dy);
        if (d <= threshold && (!best || d < best.d)) best = { d, dx, dy };
      }
    }
  }
  return best ? { dx: best.dx, dy: best.dy, snapped: true } : { dx: 0, dy: 0, snapped: false };
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
