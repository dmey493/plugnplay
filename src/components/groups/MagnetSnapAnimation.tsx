"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { Student } from "@/lib/classroom/classes";

/**
 * Magnet-snap randomization animation.
 *
 * Four phases, driven by a tiny state machine plus CSS transitions:
 *
 *   1. SCATTERING (0–1200ms)   — student names appear scattered across
 *      the upper half of the viewport as small white pills. Each name
 *      drifts in from off-screen to a stable per-name scatter position,
 *      then sits there with a subtle float loop.
 *   2. REVEALING (1200–1700ms) — coloured group cards fade in along
 *      the lower half, one per group. Group cards already match the
 *      result-screen design so the animation flows into it visually.
 *   3. MAGNETIZING (1700–3200ms) — every name flies to its assigned
 *      group card, snapping into a vertical stack inside. Each name
 *      carries its own random stagger delay so the snap looks like a
 *      swarm pulling apart, not a synchronized march.
 *   4. DONE — onFinish fires; parent swaps to the result screen.
 *
 * Skip jumps straight to done at any time.
 *
 * The student → group assignment is decided upstream and passed in via
 * `groups`. We never re-randomize here; the animation just unveils.
 */

interface Props {
  groups: Student[][];
  onFinish: () => void;
  onSkip: () => void;
}

type Phase = "scattering" | "revealing" | "magnetizing" | "done";

interface NameDot {
  studentId: string;
  name: string;
  groupIdx: number;
  posInGroup: number;
  /** Stable random scatter position in viewport % (set once at mount). */
  scatter: { x: number; y: number; rot: number };
  /** Per-name stagger (ms) for the magnetize phase. Spreads the snap
   *  across ~1100ms so names don't all leave at once. */
  magnetDelay: number;
}

const GROUP_COLORS = [
  "#0d9488", // teal-600 (pnp-accent)
  "#f97316",
  "#0ea5e9",
  "#16a34a",
  "#dc2626",
  "#475569",
  "#facc15",
  "#3f42d9",
  "#ec4899",
];
const COL_FOR = (i: number) => GROUP_COLORS[i % GROUP_COLORS.length];

export default function MagnetSnapAnimation({ groups, onFinish, onSkip }: Props) {
  // Flat list of all names with metadata + per-name random scatter and
  // magnet-stagger values. Computed once per mount so the same student
  // doesn't jump to a new random scatter position between phase changes.
  //
  // Scatter zone shrinks when we'll need two rows of group cards so
  // the scattered pills never sit on top of (or inside) where the
  // top-row cards will appear during the reveal phase.
  const dots = useMemo<NameDot[]>(() => {
    const willHaveTwoRows = groups.length > 5;
    // Scatter zone vertical extent. Upper edge stays at 8% (under the
    // stage label); lower edge stops above where the top row of cards
    // will land: y=50 in one-row mode, y=38 in two-row mode (top of
    // baseY=40 minus margin).
    const scatterYMin = 8;
    const scatterYMax = willHaveTwoRows ? 32 : 48;
    const flat: NameDot[] = [];
    groups.forEach((g, gi) => {
      g.forEach((s, si) => {
        flat.push({
          studentId: s.id,
          name: s.name,
          groupIdx: gi,
          posInGroup: si,
          scatter: {
            x: 8 + Math.random() * 84,
            y: scatterYMin + Math.random() * (scatterYMax - scatterYMin),
            rot: (Math.random() - 0.5) * 24, // ±12°
          },
          // Stagger so the magnet phase looks like a swarm. Total
          // window ~1100ms; per-name delay 0..1100.
          magnetDelay: Math.random() * 1100,
        });
      });
    });
    return flat;
  }, [groups]);

  const [phase, setPhase] = useState<Phase>("scattering");
  // Cancel-able timers so Skip stops them all.
  const timersRef = useRef<ReturnType<typeof setTimeout>[]>([]);
  const after = (ms: number, fn: () => void) => {
    timersRef.current.push(setTimeout(fn, ms));
  };

  // After every pill has landed, we hold on the final layout for
  // ~3 seconds so a projected class can read the assignment before
  // the result screen takes over. The teacher can click Continue at
  // any time during this hold to advance immediately.
  const RESULT_HOLD_MS = 3000;
  // The last pill lands at: magnetize-start (1700) + max stagger
  // (~1100) + snap duration (900) ≈ 3700ms. We mark the phase "done"
  // at 3700 so the Continue button + hold timer kick in right when
  // the swarm has finished assembling.
  const DONE_AT_MS = 3700;

  useEffect(() => {
    after(1200, () => setPhase("revealing"));
    after(1700, () => setPhase("magnetizing"));
    after(DONE_AT_MS, () => setPhase("done"));
    after(DONE_AT_MS + RESULT_HOLD_MS, () => onFinish());
    return () => {
      timersRef.current.forEach((t) => clearTimeout(t));
      timersRef.current = [];
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSkip = () => {
    timersRef.current.forEach((t) => clearTimeout(t));
    timersRef.current = [];
    onSkip();
  };
  // Continue = same effect as the natural finish but fires now and
  // cancels the auto-advance timer so the parent doesn't get two
  // setState calls back-to-back.
  const handleContinue = () => {
    timersRef.current.forEach((t) => clearTimeout(t));
    timersRef.current = [];
    onFinish();
  };

  // Group card target positions in % of viewport.
  //
  // Two layouts:
  //   - One row (n ≤ 5): tall cards across the lower half, scatter
  //     gets the upper half.
  //   - Two rows (n ≥ 6): shorter cards in two cleanly-separated rows
  //     that span the middle-to-bottom, scatter gets the upper third.
  //
  // The row pitch is `cardHeight + gap` (NOT half-height) so the rows
  // never overlap. Earlier versions used a half-height pitch which
  // made the bottom name slots of row-1 cards land inside the visual
  // space owned by row-2 cards — the snap looked like a mis-assign.
  //
  // Each row is centred horizontally independently, so a partial
  // second row (e.g. 1 card when there are 6 groups) sits in the
  // middle rather than aligned-left.
  const groupCards = useMemo(() => {
    const n = groups.length;
    const perRow = Math.min(5, n);
    const rows = Math.ceil(n / perRow);
    const out: { x: number; y: number; width: number; height: number }[] = [];
    const cardWidth = 16;
    const gap = 2;
    // Shorter cards in two-row mode so both rows fit without bleeding
    // off the bottom or eating into the scatter zone.
    const cardHeight = rows === 1 ? 32 : 26;
    const baseY = rows === 1 ? 58 : 40;
    const rowPitch = cardHeight + gap; // full card + gap — no overlap
    for (let i = 0; i < n; i++) {
      const row = Math.floor(i / perRow);
      const col = i % perRow;
      // Cards remaining in THIS row — for row 0 it's at most perRow,
      // for row 1 it's whatever's left over. Used to centre each row
      // independently.
      const cardsInThisRow = row === 0 ? Math.min(n, perRow) : n - perRow;
      const rowWidth = cardsInThisRow * cardWidth + (cardsInThisRow - 1) * gap;
      const startX = 50 - rowWidth / 2;
      const x = startX + col * (cardWidth + gap);
      const y = baseY + row * rowPitch;
      out.push({ x, y, width: cardWidth, height: cardHeight });
    }
    return out;
  }, [groups.length]);

  return (
    <section
      className="relative overflow-hidden bg-pnp-navy"
      style={{ minHeight: "calc(100vh - var(--header-h, 0px))" }}
    >
      <div className="relative h-[85vh] w-full">
        {/* Stage label */}
        <div className="pointer-events-none absolute left-1/2 top-6 z-30 -translate-x-1/2 text-center">
          <p className="text-xs font-bold uppercase tracking-[0.3em] text-white/50">
            {phase === "scattering" && "Randomizing…"}
            {phase === "revealing" && "Forming groups"}
            {phase === "magnetizing" && "Assigning"}
            {phase === "done" && "Done"}
          </p>
        </div>

        {/* Group cards — appear in the lower half. Each is a coloured
            header strip on top of a translucent body the name pills
            will land in. */}
        {groupCards.map((card, gi) => {
          const visible =
            phase === "revealing" || phase === "magnetizing" || phase === "done";
          return (
            <div
              key={`g-${gi}`}
              className="absolute overflow-hidden rounded-xl bg-white/95 shadow-2xl"
              style={{
                left: `${card.x}%`,
                top: `${card.y}%`,
                width: `${card.width}%`,
                height: `${card.height}%`,
                opacity: visible ? 1 : 0,
                transform: visible ? "translateY(0) scale(1)" : "translateY(20px) scale(0.95)",
                transition: "opacity 500ms ease-out, transform 500ms cubic-bezier(0.22, 0.61, 0.36, 1)",
              }}
            >
              {/* Coloured header strip */}
              <div
                className="flex items-center justify-between px-3 py-2 text-white"
                style={{ backgroundColor: COL_FOR(gi) }}
              >
                <span className="font-heading text-[1.4vmin] font-extrabold uppercase tracking-wider">
                  Group {gi + 1}
                </span>
                <span className="text-[1vmin] font-semibold opacity-80">
                  {groups[gi].length}
                </span>
              </div>
              {/* Soft glow behind the body that pulses subtly during
                  the magnetize phase — telegraphs the "this is a magnet"
                  metaphor without being a literal magnet icon. */}
              <div
                className="absolute inset-x-0 bottom-0 top-[18%]"
                style={{
                  background: `radial-gradient(circle at 50% 30%, ${COL_FOR(gi)}33 0%, transparent 65%)`,
                  opacity:
                    phase === "magnetizing" ? 1 : phase === "done" ? 0.55 : 0,
                  transition: "opacity 600ms ease-out",
                }}
              />
            </div>
          );
        })}

        {/* Name pills — every student is a small pill. The pill stays
            mounted the whole time; its left/top/transform changes per
            phase so the CSS transition does the work. */}
        {dots.map((dot, i) => {
          const target = computeTarget(dot, phase, groupCards[dot.groupIdx], groups[dot.groupIdx].length);
          // Float loop while scattered — adds gentle drift so the
          // pre-magnet phase isn't dead-still.
          const floatY = phase === "scattering" ? `${Math.sin(i * 1.7) * 0.5}vh` : "0";
          return (
            <div
              key={dot.studentId}
              className="absolute z-10 -translate-x-1/2 -translate-y-1/2"
              style={{
                left: `${target.x}%`,
                top: `${target.y}%`,
                transform: `translate(-50%, -50%) translateY(${floatY}) rotate(${target.rot}deg) scale(${target.scale})`,
                opacity: target.opacity,
                // Magnet phase carries a per-name delay so names leave
                // in a wave. Other phases are simultaneous.
                transition: [
                  `left 900ms cubic-bezier(0.34, 1.2, 0.5, 1) ${target.delay}ms`,
                  `top 900ms cubic-bezier(0.34, 1.2, 0.5, 1) ${target.delay}ms`,
                  `transform 900ms cubic-bezier(0.34, 1.2, 0.5, 1) ${target.delay}ms`,
                  `opacity 600ms ease-out`,
                ].join(", "),
                // Names that have landed get a higher z so later-landing
                // names don't render under them.
                zIndex: 10 + dot.posInGroup,
              }}
            >
              {/* Color reveal — pills stay neutral grey until the
                  magnetize phase fires. Each pill's color transition
                  uses the SAME per-name stagger as its motion, so the
                  reveal cascades with the snap rather than coloring
                  every name simultaneously. Effect: the "magnet" is
                  visibly claiming each name one at a time. */}
              <NamePill
                name={dot.name}
                groupIdx={dot.groupIdx}
                size={phase === "magnetizing" || phase === "done" ? "small" : "large"}
                colored={phase === "magnetizing" || phase === "done"}
                colorDelay={
                  phase === "magnetizing" || phase === "done" ? dot.magnetDelay : 0
                }
              />
            </div>
          );
        })}

        <button
          type="button"
          onClick={handleSkip}
          className="absolute right-6 top-6 z-40 rounded-md border border-white/20 bg-white/5 px-3 py-1.5 text-xs font-semibold text-white/80 backdrop-blur transition-colors hover:bg-white/10 hover:text-white"
        >
          Skip animation
        </button>

        {/* Continue button — appears at the bottom-centre during the
            done-state hold so the teacher can advance to the result
            screen on their own time instead of waiting out the
            3-second auto-advance. Fades in so it doesn't pop. */}
        <button
          type="button"
          onClick={handleContinue}
          className="absolute bottom-6 left-1/2 z-40 -translate-x-1/2 rounded-md bg-pnp-accent px-5 py-2.5 text-sm font-bold text-white shadow-lg transition-all hover:bg-pnp-accent-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-pnp-navy"
          style={{
            opacity: phase === "done" ? 1 : 0,
            pointerEvents: phase === "done" ? "auto" : "none",
            transition: "opacity 400ms ease-out",
          }}
          aria-hidden={phase !== "done"}
        >
          Continue &rarr;
        </button>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────
// Per-name target computation
// ─────────────────────────────────────────────────────────────────────

interface DotTarget {
  x: number; // %
  y: number; // %
  rot: number; // degrees
  scale: number;
  opacity: number;
  delay: number; // ms — applied only during magnetize so others snap together
}

function computeTarget(
  dot: NameDot,
  phase: Phase,
  groupCard: { x: number; y: number; width: number; height: number } | undefined,
  groupSize: number
): DotTarget {
  if (phase === "scattering" || phase === "revealing") {
    return {
      x: dot.scatter.x,
      y: dot.scatter.y,
      rot: dot.scatter.rot,
      scale: 1,
      opacity: 1,
      delay: 0,
    };
  }
  // Magnetize + done: snap to slot inside the assigned group card.
  if (!groupCard) {
    return { x: 50, y: 50, rot: 0, scale: 1, opacity: 1, delay: dot.magnetDelay };
  }
  // Stack names vertically inside the card's body (the area below the
  // 18%-tall header). For a group of size N, lay names from top to
  // bottom with equal spacing.
  const bodyTop = groupCard.y + groupCard.height * 0.22;
  const bodyBottom = groupCard.y + groupCard.height * 0.95;
  const slotCount = Math.max(groupSize, 1);
  // Centre slots vertically when there are fewer than the max.
  const slotPitch = (bodyBottom - bodyTop) / slotCount;
  const slotY = bodyTop + slotPitch * (dot.posInGroup + 0.5);
  const slotX = groupCard.x + groupCard.width / 2;
  return {
    x: slotX,
    y: slotY,
    rot: 0,
    scale: 1,
    opacity: 1,
    delay: dot.magnetDelay,
  };
}

// ─────────────────────────────────────────────────────────────────────
// Name pill — the visual unit. Large during scatter, smaller after
// snap so a full group of 3 fits the card neatly.
// ─────────────────────────────────────────────────────────────────────

function NamePill({
  name,
  groupIdx,
  size,
  colored,
  colorDelay,
}: {
  name: string;
  groupIdx: number;
  size: "small" | "large";
  /** Whether to show this pill in its assigned group's colour. False
   *  during the scatter/reveal phases so no group hint leaks early. */
  colored: boolean;
  /** Per-pill stagger (ms) for the colour reveal — matches the snap
   *  motion's delay so the colour appears at the moment the pill
   *  starts flying toward its group. */
  colorDelay: number;
}) {
  // Neutral "before claim" palette — slate grey so the pill reads as
  // a generic name tag, not part of any group yet. Switches to the
  // assigned group's colour once `colored` flips true.
  const NEUTRAL = "#94a3b8"; // slate-400
  const groupColor = COL_FOR(groupIdx);
  const activeColor = colored ? groupColor : NEUTRAL;

  const padding = size === "large" ? "0.75vmin 1.4vmin" : "0.4vmin 0.9vmin";
  const fontSize = size === "large" ? "1.8vmin" : "1.1vmin";
  const dotSize = size === "large" ? "2.2vmin" : "1.4vmin";
  const dotFont = size === "large" ? "1.2vmin" : "0.8vmin";

  // The colour transition pops faster than the layout transitions —
  // 250ms feels like a "claim" rather than a slow tint shift. The
  // per-pill delay is what creates the cascade across the swarm.
  const colorTransition = `background-color 250ms ease-out ${colorDelay}ms, border-color 250ms ease-out ${colorDelay}ms`;

  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-md bg-white font-heading font-bold text-pnp-navy shadow-lg"
      style={{
        padding,
        fontSize,
        border: `2px solid ${activeColor}`,
        transition: `padding 400ms ease, font-size 400ms ease, ${colorTransition}`,
      }}
    >
      <span
        aria-hidden="true"
        className="flex items-center justify-center rounded-full text-white"
        style={{
          backgroundColor: activeColor,
          width: dotSize,
          height: dotSize,
          fontSize: dotFont,
          fontWeight: 800,
          transition: `width 400ms ease, height 400ms ease, font-size 400ms ease, ${colorTransition}`,
        }}
      >
        {name.charAt(0).toUpperCase()}
      </span>
      {name}
    </span>
  );
}
