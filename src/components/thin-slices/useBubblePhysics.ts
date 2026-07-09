"use client";

import { useEffect, useRef } from "react";
import Matter from "matter-js";

interface Args {
  /** Ref to the stage container — used to attach the mouse constraint and
   *  measure for walls. */
  stageRef: React.RefObject<HTMLDivElement | null>;
  /** Stable identifier for the slice + phase. When this changes we tear down
   *  and rebuild the world (so positions reset between slices/phases). */
  sliceKey: string;
  stageSize: { w: number; h: number };
  /** Default bubble dimensions. Used for auto-positioning and as the floor
   *  for per-bubble sizing. */
  bubbleW: number;
  bubbleH: number;
  /** Step indices currently visible in the stage. We add/remove bodies to match. */
  visibleStepIndices: number[];
  /** Where a new body for a given step index should spawn. */
  autoPos: (stepIndex: number) => { x: number; y: number };
  /** Per-step rendered dimensions. Some bubbles grow horizontally to fit
   *  their content; this lets the collision body match the visual width
   *  exactly. Defaults to { bubbleW, bubbleH } when omitted. */
  bubbleSize?: (stepIndex: number) => { w: number; h: number };
}

/**
 * Wires Matter.js into a React stage. Returns a ref-keyed Map of step index
 * → DOM element; the hook writes `transform: translate3d(x,y,0)` to each
 * element on every Matter frame.
 *
 * Design choices:
 * - Gravity off — bubbles slide on a 2D plane, they don't fall.
 * - Each bubble is a rectangle body (matches the bubble's bounding box).
 * - Walls = 4 static rectangles around the stage edges. Rebuilt on resize.
 * - Restitution 0.6 + linear damping → throws decay naturally and bounce off
 *   walls and other bubbles with some energy preserved.
 * - MouseConstraint handles drag + throw velocity automatically.
 */
export function useBubblePhysics({
  stageRef,
  sliceKey,
  stageSize,
  bubbleW,
  bubbleH,
  visibleStepIndices,
  autoPos,
  bubbleSize,
}: Args) {
  // DOM elements keyed by stepIndex. The component sets these via a ref callback.
  const elementsRef = useRef<Map<number, HTMLDivElement>>(new Map());
  // Matter state. Lives across renders, recreated on sliceKey or stageSize change.
  const engineRef = useRef<Matter.Engine | null>(null);
  const wallsRef = useRef<Matter.Body[]>([]);
  // Step index → body, for fast add/remove on visibleStepIndices change.
  const bodiesRef = useRef<Map<number, Matter.Body>>(new Map());
  // Per-body actual dimensions, captured at body-creation time. We need these
  // each frame to compute the DOM offset (body position is its CENTER, the
  // rendered div is anchored top-left — different bubbles have different
  // widths, so we can't use a single constant offset).
  const bodySizesRef = useRef<Map<number, { w: number; h: number }>>(new Map());
  const rafRef = useRef<number | null>(null);
  const mouseConstraintRef = useRef<Matter.MouseConstraint | null>(null);

  // Build / rebuild the world when slice or stage size changes.
  useEffect(() => {
    if (!stageRef.current || stageSize.w === 0 || stageSize.h === 0) return;

    const engine = Matter.Engine.create({
      gravity: { x: 0, y: 0 },
    });
    engineRef.current = engine;

    // Collision categories — bubbles and walls live on different bits so we
    // can have bubbles collide with walls (stay on screen) but pass through
    // each other (cleaner visual: drifting bubbles don't bonk).
    //   category 0x0001 → walls  (collide with everything)
    //   category 0x0002 → bubbles (collide ONLY with walls)
    const WALL_CATEGORY = 0x0001;
    const BUBBLE_CATEGORY = 0x0002;

    // Walls: thick static rectangles just outside the visible area so bubbles
    // can bounce without their corners poking through.
    const wallThickness = 200;
    const { w, h } = stageSize;
    const wallFilter = {
      category: WALL_CATEGORY,
      mask: 0xFFFFFFFF,  // walls collide with everything
    };
    const walls = [
      // top
      Matter.Bodies.rectangle(w / 2, -wallThickness / 2, w + wallThickness * 2, wallThickness, {
        isStatic: true,
        collisionFilter: wallFilter,
      }),
      // bottom
      Matter.Bodies.rectangle(w / 2, h + wallThickness / 2, w + wallThickness * 2, wallThickness, {
        isStatic: true,
        collisionFilter: wallFilter,
      }),
      // left
      Matter.Bodies.rectangle(-wallThickness / 2, h / 2, wallThickness, h + wallThickness * 2, {
        isStatic: true,
        collisionFilter: wallFilter,
      }),
      // right
      Matter.Bodies.rectangle(w + wallThickness / 2, h / 2, wallThickness, h + wallThickness * 2, {
        isStatic: true,
        collisionFilter: wallFilter,
      }),
    ];
    // Stash on the engine for the bubble-creation effect to read. (We can't
    // reference inner closure constants from a different effect, so put them
    // on the engine object as plugin data.)
    (engine as unknown as { _pnpBubbleCategory: number })._pnpBubbleCategory = BUBBLE_CATEGORY;
    (engine as unknown as { _pnpWallCategory: number })._pnpWallCategory = WALL_CATEGORY;
    wallsRef.current = walls;
    Matter.Composite.add(engine.world, walls);

    // Mouse constraint — Matter handles drag + throw velocity for us.
    const mouse = Matter.Mouse.create(stageRef.current);
    const mouseConstraint = Matter.MouseConstraint.create(engine, {
      mouse,
      constraint: {
        stiffness: 0.2,
        // No render — we draw the bubbles ourselves.
        render: { visible: false },
      },
    });
    mouseConstraintRef.current = mouseConstraint;
    Matter.Composite.add(engine.world, mouseConstraint);

    // Animation loop. We can't use Matter.Runner because we want to drive DOM
    // updates each frame, so we step the engine manually inside rAF.
    let lastTs = performance.now();
    const tick = (ts: number) => {
      // Matter recommends dt <= 16.667ms. We clamp to that so a long pause
      // (e.g., tab in background) doesn't fire a giant step that tunnels through
      // walls. If real elapsed time exceeds the cap, we just lose that motion —
      // physics doesn't need to "catch up" for a thin-slice.
      const dt = Math.min(16.667, ts - lastTs);
      lastTs = ts;

      Matter.Engine.update(engine, dt);

      // Sync DOM positions from body positions. Each bubble may have a
      // different width (long-content bubbles grow horizontally), so use the
      // per-body size we captured at creation time.
      bodiesRef.current.forEach((body, stepIndex) => {
        const el = elementsRef.current.get(stepIndex);
        if (!el) return;
        const size = bodySizesRef.current.get(stepIndex);
        const w = size?.w ?? bubbleW;
        const h = size?.h ?? bubbleH;
        // Body position is its center; DOM is top-left.
        const x = body.position.x - w / 2;
        const y = body.position.y - h / 2;
        el.style.transform = `translate3d(${x}px, ${y}px, 0)`;
      });

      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);

    return () => {
      if (rafRef.current != null) cancelAnimationFrame(rafRef.current);
      Matter.Composite.clear(engine.world, false, true);
      Matter.Engine.clear(engine);
      bodiesRef.current.clear();
      bodySizesRef.current.clear();
      engineRef.current = null;
      wallsRef.current = [];
      mouseConstraintRef.current = null;
    };
    // We deliberately rebuild the world on slice/phase change OR on resize.
    //
    // IMPORTANT: bubbleW/bubbleH are NOT in the dep array. Including them
    // would tear down the entire world every time the teacher tweaks the
    // bubble-size slider, which kicks every bubble back to its spawn
    // position — destructive if they've been organizing the field. Size
    // changes are handled by a separate effect below that rescales each
    // body in place.
  }, [sliceKey, stageSize.w, stageSize.h, stageRef]);

  // Rescale existing bodies when the default size changes (bubble-size
  // slider). Walks the existing bodies and applies the size delta with
  // Matter.Body.scale, preserving each body's current center position so
  // bubbles keep wherever the teacher placed them.
  useEffect(() => {
    const engine = engineRef.current;
    if (!engine) return;
    bodiesRef.current.forEach((body, stepIndex) => {
      // Look up what the new size SHOULD be for this body. If a per-step
      // override exists, use it; otherwise the new default.
      const newSize = bubbleSize ? bubbleSize(stepIndex) : { w: bubbleW, h: bubbleH };
      const oldSize = bodySizesRef.current.get(stepIndex);
      if (!oldSize) return;
      // Skip if the size is already correct (avoids zero-delta scale calls
      // that compound floating-point drift).
      if (Math.abs(oldSize.w - newSize.w) < 0.5 && Math.abs(oldSize.h - newSize.h) < 0.5) {
        return;
      }
      const scaleX = newSize.w / oldSize.w;
      const scaleY = newSize.h / oldSize.h;
      Matter.Body.scale(body, scaleX, scaleY);
      bodySizesRef.current.set(stepIndex, { w: newSize.w, h: newSize.h });
    });
  }, [bubbleW, bubbleH, bubbleSize]);

  // Sync bodies with the visible step indices. Add bodies for new steps,
  // remove bodies for steps that left the visible window.
  useEffect(() => {
    const engine = engineRef.current;
    if (!engine) return;

    const visibleSet = new Set(visibleStepIndices);

    // Remove bodies whose step is no longer visible.
    bodiesRef.current.forEach((body, stepIndex) => {
      if (!visibleSet.has(stepIndex)) {
        Matter.Composite.remove(engine.world, body);
        bodiesRef.current.delete(stepIndex);
        bodySizesRef.current.delete(stepIndex);
      }
    });

    // Add bodies for new steps. Each body's collision rectangle matches its
    // rendered visual size — long-content bubbles get wider bodies so they
    // don't collide before their visible edges meet.
    for (const stepIndex of visibleStepIndices) {
      if (bodiesRef.current.has(stepIndex)) continue;
      const size = bubbleSize ? bubbleSize(stepIndex) : { w: bubbleW, h: bubbleH };
      const spawn = autoPos(stepIndex);
      const cx = spawn.x + size.w / 2;
      const cy = spawn.y + size.h / 2;
      // Pull the categories the world setup stashed on the engine — bubbles
      // collide with walls only, not with other bubbles.
      const bubbleCategory =
        (engine as unknown as { _pnpBubbleCategory?: number })._pnpBubbleCategory ?? 0x0002;
      const wallCategory =
        (engine as unknown as { _pnpWallCategory?: number })._pnpWallCategory ?? 0x0001;
      const body = Matter.Bodies.rectangle(cx, cy, size.w, size.h, {
        restitution: 0.6,
        friction: 0.05,
        frictionAir: 0.05,
        density: 0.002,
        // Lock rotation so the bubble text never goes upside-down.
        inertia: Infinity,
        collisionFilter: {
          category: bubbleCategory,
          // Bubbles collide ONLY with walls (so they stay on screen),
          // never with each other. They drift past one another which
          // looks much better than the old bonk-bonk physics.
          mask: wallCategory,
        },
      });
      Matter.Composite.add(engine.world, body);
      bodiesRef.current.set(stepIndex, body);
      bodySizesRef.current.set(stepIndex, size);
    }
  }, [visibleStepIndices, bubbleW, bubbleH, autoPos, bubbleSize]);

  return elementsRef;
}
