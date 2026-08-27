"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { Student } from "@/lib/classroom/classes";

/**
 * Slot-reels randomization animation.
 *
 * Each group is its own miniature slot machine. Inside each group,
 * there's one vertical reel per student slot — three reels for a
 * group of three, two reels for a group of two. Every reel spins at
 * the same time. Reels then stop one at a time, in order:
 *
 *   G1.R1 → G1.R2 → G1.R3 → G2.R1 → G2.R2 → G2.R3 → …
 *
 * Each stop reveals one assigned student. Reading left-to-right and
 * top-to-bottom, you watch each group fill up in turn — that's the
 * dramatic beat. Settle time per reel is ~800ms (deceleration).
 *
 * Mechanics:
 *   - The reel "strip" is a vertical column of name pills containing
 *     the assigned student name at a known index plus randomly-drawn
 *     filler from the roster. The strip is rendered twice so a CSS
 *     `translateY` animation can loop seamlessly during spin.
 *   - When a reel's stop time fires, JS captures the current animated
 *     transform value, locks it via inline style, then transitions
 *     translateY to the final position (target slot centred).
 *   - At the end, the screen holds for 3 seconds before auto-
 *     advancing. A Continue button lets the teacher advance early.
 */

interface Props {
  groups: Student[][];
  onFinish: () => void;
  onSkip: () => void;
}

const GROUP_COLORS = [
  "#0d9488",
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

// Reel dimensions + strip layout (vmin = % of viewport's smaller dim).
const SLOT_HEIGHT_VMIN = 5.4; // per-name slot height
const HALF_LENGTH = 18;       // names in the first half of the strip
const TARGET_INDEX = 12;      // where the assigned name sits in the half
const STRIP_NAMES = HALF_LENGTH * 2; // strip = half + duplicate half (for seamless loop)
const SPIN_LOOP_VMIN = HALF_LENGTH * SLOT_HEIGHT_VMIN;
const SPIN_DURATION_S = 0.4; // one full strip-cycle in seconds (faster = blurrier)

// Stagger timings (ms).
const BASE_SPIN_MS = 1500;
const REEL_STAGGER_MS = 250;
const GROUP_STAGGER_MS = 400;
const SETTLE_MS = 800;
const RESULT_HOLD_MS = 3000;

export default function SlotReelsAnimation({ groups, onFinish, onSkip }: Props) {
  // Flat list of all names — used as filler in each reel strip so
  // teachers see "lots of names cycling" rather than the same target
  // name repeated.
  const allNames = useMemo(
    () => groups.flatMap((g) => g.map((s) => s.name)),
    [groups]
  );

  // Per-reel stop time map: stopMs[groupIdx][reelIdx].
  const stopMs = useMemo(() => {
    return groups.map((g, gi) =>
      g.map((_, ri) => BASE_SPIN_MS + gi * GROUP_STAGGER_MS + ri * REEL_STAGGER_MS)
    );
  }, [groups]);

  // Total animation time = last reel's stop + settle. The done-state
  // hold + Continue button kicks in at exactly this point.
  const finalReelDoneMs = useMemo(() => {
    let max = 0;
    for (const row of stopMs) for (const t of row) max = Math.max(max, t);
    return max + SETTLE_MS;
  }, [stopMs]);

  const [phase, setPhase] = useState<"spinning" | "done">("spinning");
  const timersRef = useRef<ReturnType<typeof setTimeout>[]>([]);

  useEffect(() => {
    timersRef.current.push(setTimeout(() => setPhase("done"), finalReelDoneMs));
    timersRef.current.push(
      setTimeout(() => onFinish(), finalReelDoneMs + RESULT_HOLD_MS)
    );
    return () => {
      timersRef.current.forEach((t) => clearTimeout(t));
      timersRef.current = [];
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [finalReelDoneMs]);

  const handleSkip = () => {
    timersRef.current.forEach((t) => clearTimeout(t));
    timersRef.current = [];
    onSkip();
  };
  const handleContinue = () => {
    timersRef.current.forEach((t) => clearTimeout(t));
    timersRef.current = [];
    onFinish();
  };

  // Group machine layout — 1 row (≤5 groups) or 2 rows (6+).
  const perRow = Math.min(5, groups.length);
  const rows = Math.ceil(groups.length / perRow);

  return (
    <section
      className="relative overflow-hidden bg-pnp-navy"
      style={{ minHeight: "calc(100vh - var(--header-h, 0px))" }}
    >
      {/* Shared keyframe for every reel. translateY from 0 to half the
          strip — since the strip's second half duplicates the first,
          the loop is visually seamless. */}
      <style>{`
        @keyframes pnp-reel-spin {
          0% { transform: translateY(0); }
          100% { transform: translateY(-${SPIN_LOOP_VMIN}vmin); }
        }
      `}</style>

      <div className="relative flex h-[85vh] w-full flex-col items-center justify-center px-6">
        {/* Stage label */}
        <div className="pointer-events-none absolute left-1/2 top-6 z-30 -translate-x-1/2 text-center">
          <p className="text-xs font-bold uppercase tracking-[0.3em] text-white/50">
            {phase === "spinning" && "Spinning…"}
            {phase === "done" && "Locked in"}
          </p>
        </div>

        {/* Group-machine grid */}
        <div
          className="grid w-full max-w-[1400px] gap-4"
          style={{
            gridTemplateColumns: `repeat(${perRow}, minmax(0, 1fr))`,
            gridTemplateRows: rows > 1 ? `repeat(${rows}, minmax(0, 1fr))` : undefined,
          }}
        >
          {groups.map((g, gi) => (
            <GroupMachine
              key={gi}
              groupIdx={gi}
              students={g}
              allNames={allNames}
              stopTimes={stopMs[gi]}
            />
          ))}
        </div>

        <button
          type="button"
          onClick={handleSkip}
          className="absolute right-6 top-6 z-40 rounded-md border border-white/20 bg-white/5 px-3 py-1.5 text-xs font-semibold text-white/80 backdrop-blur transition-colors hover:bg-white/10 hover:text-white"
        >
          Skip animation
        </button>

        {/* Continue button — fades in once all reels have settled. */}
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
// One group machine — header strip + a row of reels (one per slot).
// ─────────────────────────────────────────────────────────────────────

function GroupMachine({
  groupIdx,
  students,
  allNames,
  stopTimes,
}: {
  groupIdx: number;
  students: Student[];
  allNames: string[];
  stopTimes: number[];
}) {
  const color = COL_FOR(groupIdx);
  return (
    <article className="overflow-hidden rounded-xl bg-white/5 ring-1 ring-white/10">
      {/* Header strip — the slot machine's "marquee". */}
      <div
        className="flex items-center justify-between px-3 py-2 text-white"
        style={{ backgroundColor: color }}
      >
        <span className="font-heading text-[1.4vmin] font-extrabold uppercase tracking-wider">
          Group {groupIdx + 1}
        </span>
        <span className="text-[1vmin] font-semibold opacity-80">
          {students.length}
        </span>
      </div>
      {/* Reels — stacked vertically (one per slot). Each cell is a
          single-name window with its own spinning strip inside. */}
      <div className="flex flex-col gap-1 bg-black/20 p-2">
        {students.map((s, ri) => (
          <Reel
            key={s.id}
            targetName={s.name}
            allNames={allNames}
            stopMs={stopTimes[ri]}
            accentColor={color}
            seed={s.id}
          />
        ))}
      </div>
    </article>
  );
}

// ─────────────────────────────────────────────────────────────────────
// One reel — single-name window + spinning strip inside.
// ─────────────────────────────────────────────────────────────────────

function Reel({
  targetName,
  allNames,
  stopMs,
  accentColor,
  seed,
}: {
  targetName: string;
  allNames: string[];
  /** Time (ms from mount) when this reel should start its settle. */
  stopMs: number;
  /** Group colour — used for the side-bar accent and the "locked-in"
   *  highlight that lights up the slot when it stops. */
  accentColor: string;
  /** Stable seed (e.g. student id) so the strip filler doesn't
   *  re-shuffle on every parent re-render. */
  seed: string;
}) {
  const stripRef = useRef<HTMLDivElement>(null);
  const [locked, setLocked] = useState(false);

  // Build the strip once per reel: HALF_LENGTH random filler with the
  // target name at TARGET_INDEX, then a duplicate of the same half
  // appended. The duplicate makes the CSS-animation loop seamless —
  // translateY(0) and translateY(-HALF_LENGTH × SLOT_HEIGHT) display
  // exactly the same content.
  const strip = useMemo(() => {
    const rng = mulberry32(stringHash(seed));
    const half: string[] = [];
    for (let i = 0; i < HALF_LENGTH; i++) {
      if (i === TARGET_INDEX) {
        half.push(targetName);
      } else {
        // Avoid drawing the target name as filler so the spinning
        // window doesn't show the actual answer multiple times.
        let candidate = allNames[Math.floor(rng() * allNames.length)];
        let guard = 0;
        while (candidate === targetName && guard++ < 4) {
          candidate = allNames[Math.floor(rng() * allNames.length)];
        }
        half.push(candidate);
      }
    }
    return [...half, ...half];
  }, [targetName, allNames, seed]);

  useEffect(() => {
    const stripEl = stripRef.current;
    if (!stripEl) return;

    const timer = setTimeout(() => {
      // Capture the current animated translateY value, lock the strip
      // to that position via inline style, then transition to the
      // target position. Without this capture the strip would snap
      // back to translateY(0) the instant we remove the animation.
      const matrix = window.getComputedStyle(stripEl).transform;
      let currentY = 0;
      if (matrix && matrix !== "none") {
        // CSS computed transform is "matrix(a, b, c, d, tx, ty)" — we
        // want ty (6th value, 0-indexed at 5).
        const inner = matrix.slice(matrix.indexOf("(") + 1, matrix.lastIndexOf(")"));
        const vals = inner.split(",").map((s) => parseFloat(s.trim()));
        if (vals.length === 6 && Number.isFinite(vals[5])) currentY = vals[5];
      }

      // Stop the animation. Lock to current position in px so there's
      // no visible jump.
      stripEl.style.animation = "none";
      stripEl.style.transform = `translateY(${currentY}px)`;
      // Force a reflow so the browser registers the locked position
      // BEFORE we apply the transition + new transform.
      void stripEl.offsetHeight;

      // Final position — slot at TARGET_INDEX should sit at the top of
      // the window. translateY in vmin so it scales with the viewport.
      const finalYVmin = -(TARGET_INDEX * SLOT_HEIGHT_VMIN);
      stripEl.style.transition = `transform ${SETTLE_MS}ms cubic-bezier(0.16, 0.84, 0.3, 1)`;
      stripEl.style.transform = `translateY(${finalYVmin}vmin)`;
      // Trigger the "locked-in" highlight at the moment the settle
      // begins so the colour pop coincides with the deceleration.
      setLocked(true);
    }, stopMs);

    return () => clearTimeout(timer);
  }, [stopMs]);

  return (
    <div
      className="relative overflow-hidden rounded-md ring-1 transition-shadow"
      style={{
        height: `${SLOT_HEIGHT_VMIN}vmin`,
        background: "white",
        // Locked state lights up the slot with the group's colour —
        // the "you won" flash on a slot machine.
        boxShadow: locked ? `0 0 0 2px ${accentColor}, 0 4px 12px ${accentColor}55` : "none",
      }}
    >
      <div
        ref={stripRef}
        style={{
          willChange: "transform",
          animation: `pnp-reel-spin ${SPIN_DURATION_S}s linear infinite`,
        }}
      >
        {strip.map((name, i) => (
          <div
            key={i}
            className="flex w-full items-center justify-center px-2 font-heading font-bold text-pnp-navy"
            style={{
              height: `${SLOT_HEIGHT_VMIN}vmin`,
              fontSize: `${SLOT_HEIGHT_VMIN * 0.42}vmin`,
              // While spinning, slight motion blur on the strip so the
              // rapid cycling reads as motion, not strobe.
              filter: locked ? "none" : "blur(0.6px)",
              transition: "filter 200ms ease-out",
            }}
          >
            {name}
          </div>
        ))}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// Tiny seeded RNG so each reel's filler is stable across renders.
// ─────────────────────────────────────────────────────────────────────

function stringHash(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  // mulberry32 expects an unsigned 32-bit seed.
  return h >>> 0;
}

function mulberry32(seed: number) {
  let a = seed;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
