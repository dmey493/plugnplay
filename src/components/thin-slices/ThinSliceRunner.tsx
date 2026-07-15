"use client";

import { useState, useEffect, useCallback, useRef, useMemo } from "react";
import { useRouter } from "next/navigation";
import type { ThinSliceShape, ThinSliceStep } from "@/lib/types";
import MathExpression from "./MathExpression";
import ShapeRenderer from "./ShapeRenderer";
import OrganizerOverlay, { type OrganizerKind } from "./OrganizerOverlay";
import { useBubblePhysics } from "./useBubblePhysics";
import DrawingOverlay from "@/components/intervention/DrawingOverlay";
import TimerOverlay from "@/components/tasks/TimerOverlay";
import GroupsButton from "@/components/groups/GroupsButton";

interface Props {
  sliceId: string;
  title: string;
  stem?: string;
  shape?: ThinSliceShape;
  steps: ThinSliceStep[];
  enrichmentSteps?: ThinSliceStep[];
  prerequisiteSteps?: ThinSliceStep[];
  prerequisiteLabel?: string;
}

/**
 * A step paired with a stable key + its source group. Used internally so we can
 * track which steps the teacher has excluded across the Main + Enrichment groups.
 */
interface KeyedStep {
  key: string;
  group: "main" | "enrichment";
  /** 1-based index within its group, used in the drawer's step labels. */
  groupIndex: number;
  step: ThinSliceStep;
}

type ThemeId = "light" | "dark" | "polka" | "underwater" | "chalkboard";
type Phase = "landing" | "prereq" | "main";
type BubbleSize = "sm" | "md" | "lg" | "xl" | "xxl";

interface ThemeConfig {
  id: ThemeId;
  label: string;
  /** Whether the theme is dark — drives controls, text, dimmed states. */
  isDark: boolean;
  /** Background applied to the whole runner. CSS background shorthand. */
  background: string;
  /** Optional decorative pattern as an SVG data URL or layered gradient.
   *  Renders as a fixed full-screen layer behind the stage at low opacity. */
  pattern?: string;
  /** Tailwind classes for primary text color. */
  textClass: string;
  /** Bubble border + background classes. */
  bubbleBorder: string;
  bubbleBg: string;
  bubbleText: string;
  /** Accent color for the "newest bubble" ring + answer highlight. Tailwind. */
  accentRing: string;
  accentText: string;
}

// Decorative SVG patterns as data URLs. Kept inline because they're small and
// drawn with currentColor-friendly fills so they pick up the theme's accent.
const POLKA_PATTERN = `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 80 80'><circle cx='20' cy='20' r='5' fill='%23ffe25a' opacity='0.45'/><circle cx='60' cy='60' r='5' fill='%232dd4bf' opacity='0.35'/><circle cx='60' cy='20' r='3' fill='%23f97316' opacity='0.3'/><circle cx='20' cy='60' r='3' fill='%233f42d9' opacity='0.3'/></svg>")`;
const UNDERWATER_PATTERN = `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 160 160'><circle cx='30' cy='40' r='14' fill='none' stroke='white' stroke-width='1.2' opacity='0.18'/><circle cx='110' cy='90' r='22' fill='none' stroke='white' stroke-width='1.2' opacity='0.13'/><circle cx='75' cy='130' r='9' fill='none' stroke='white' stroke-width='1.2' opacity='0.2'/><circle cx='140' cy='30' r='6' fill='none' stroke='white' stroke-width='1.2' opacity='0.22'/><circle cx='25' cy='105' r='4' fill='white' opacity='0.18'/></svg>")`;
const CHALKBOARD_PATTERN = `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240' viewBox='0 0 240 240'><g fill='white' opacity='0.04'><circle cx='30' cy='40' r='1'/><circle cx='80' cy='90' r='0.8'/><circle cx='130' cy='30' r='1.2'/><circle cx='180' cy='110' r='0.9'/><circle cx='60' cy='180' r='1'/><circle cx='200' cy='200' r='1.1'/><circle cx='100' cy='220' r='0.7'/><circle cx='10' cy='150' r='0.9'/><circle cx='220' cy='60' r='1'/></g></svg>")`;

const THEMES: Record<ThemeId, ThemeConfig> = {
  light: {
    id: "light",
    label: "Light",
    isDark: false,
    background: "#ffffff",
    textClass: "text-pnp-gray-900",
    bubbleBorder: "border-pnp-navy",
    bubbleBg: "bg-white",
    bubbleText: "text-pnp-navy",
    accentRing: "ring-pnp-yellow/40",
    accentText: "text-pnp-blue",
  },
  dark: {
    id: "dark",
    label: "Dark",
    isDark: true,
    background: "#1a1f3d", // pnp-navy
    textClass: "text-white",
    bubbleBorder: "border-pnp-yellow/70",
    bubbleBg: "bg-white/5",
    bubbleText: "text-white",
    accentRing: "ring-pnp-yellow/40",
    accentText: "text-pnp-yellow",
  },
  polka: {
    id: "polka",
    label: "Polka",
    isDark: false,
    background: "#fff8e7", // soft cream
    pattern: POLKA_PATTERN,
    textClass: "text-pnp-navy",
    bubbleBorder: "border-pnp-orange",
    bubbleBg: "bg-white",
    bubbleText: "text-pnp-navy",
    accentRing: "ring-pnp-orange/40",
    accentText: "text-pnp-orange",
  },
  underwater: {
    id: "underwater",
    label: "Underwater",
    isDark: true,
    background: "linear-gradient(180deg, #0c4a6e 0%, #075985 50%, #0e7490 100%)",
    pattern: UNDERWATER_PATTERN,
    textClass: "text-white",
    bubbleBorder: "border-cyan-200",
    bubbleBg: "bg-white/10",
    bubbleText: "text-white",
    accentRing: "ring-cyan-200/50",
    accentText: "text-cyan-200",
  },
  chalkboard: {
    id: "chalkboard",
    label: "Chalkboard",
    isDark: true,
    background: "#1f3a2d", // dark chalkboard green
    pattern: CHALKBOARD_PATTERN,
    textClass: "text-white",
    bubbleBorder: "border-white/70",
    bubbleBg: "bg-white/5",
    bubbleText: "text-white",
    accentRing: "ring-yellow-200/40",
    accentText: "text-yellow-100",
  },
};

const THEME_ORDER: ThemeId[] = ["light", "dark", "polka", "underwater", "chalkboard"];

const BUBBLE_CAP = 20;
// Multiplier on the auto-computed bubble width for each size step.
const SIZE_SCALE: Record<BubbleSize, number> = {
  sm: 0.78,
  md: 1.0,
  lg: 1.3,
  xl: 1.65,
  xxl: 2.0,
};
// Font-size multiplier — tracks SIZE_SCALE so a bigger bubble has bigger
// text inside (and a smaller bubble has correspondingly smaller text so
// the same content still fits comfortably). Tighter than SIZE_SCALE on
// the small end (text shrinks less aggressively than the box) so labels
// stay readable.
const FONT_SCALE: Record<BubbleSize, number> = {
  sm: 0.85,
  md: 1.0,
  lg: 1.18,
  xl: 1.35,
  xxl: 1.55,
};
const SIZE_LABELS: Record<BubbleSize, string> = {
  sm: "S",
  md: "M",
  lg: "L",
  xl: "XL",
  xxl: "XXL",
};
const SIZE_TOOLTIPS: Record<BubbleSize, string> = {
  sm: "Small bubbles",
  md: "Medium bubbles",
  lg: "Large bubbles",
  xl: "Extra-large bubbles",
  xxl: "XXL bubbles",
};
const SIZE_ORDER: BubbleSize[] = ["sm", "md", "lg", "xl", "xxl"];

export default function ThinSliceRunner({
  sliceId,
  title,
  stem,
  shape,
  steps,
  enrichmentSteps,
  prerequisiteSteps,
  prerequisiteLabel,
}: Props) {
  const router = useRouter();
  const hasPrereq = !!(prerequisiteSteps && prerequisiteSteps.length > 0);

  const [themeId, setThemeId] = useState<ThemeId>("light");
  const theme = THEMES[themeId];
  const isDark = theme.isDark;
  const [phase, setPhase] = useState<Phase>(hasPrereq ? "landing" : "main");
  const [revealedCount, setRevealedCount] = useState(1);
  const [showAnswers, setShowAnswers] = useState(false);
  const [bubbleSize, setBubbleSize] = useState<BubbleSize>("lg");
  const [controlsVisible, setControlsVisible] = useState(true);
  // Whiteboard drawing toggle. Mounted as a transparent SVG overlay above
  // the bubble field. Wipes whenever the visible content changes (phase
  // shift, new step revealed, picker change).
  const [drawing, setDrawing] = useState(false);
  // Draggable countdown timer (same component as the rich-task projection).
  const [timerOpen, setTimerOpen] = useState(false);
  // Picker state: which steps the teacher has unchecked.
  const [excludedKeys, setExcludedKeys] = useState<Set<string>>(new Set());
  // How many steps reveal per Next click. 1, 2, or 3.
  const [revealsPerStep, setRevealsPerStep] = useState<1 | 2 | 3>(1);
  // Drawer open state.
  const [drawerOpen, setDrawerOpen] = useState(false);
  // Background graphic organizer. Resets on phase change.
  const [organizer, setOrganizer] = useState<OrganizerKind | null>(null);

  // Build the keyed step lists. These are stable across re-renders because the
  // input arrays come from props and we just decorate them.
  const mainKeyed: KeyedStep[] = useMemo(
    () =>
      steps.map((step, i) => ({
        key: `m-${i}`,
        group: "main",
        groupIndex: i + 1,
        step,
      })),
    [steps]
  );
  const enrichmentKeyed: KeyedStep[] = useMemo(
    () =>
      (enrichmentSteps ?? []).map((step, i) => ({
        key: `e-${i}`,
        group: "enrichment",
        groupIndex: i + 1,
        step,
      })),
    [enrichmentSteps]
  );

  // The list of steps actually shown — main first, then enrichment, minus any
  // unchecked ones.
  const filteredMainEnrichment: KeyedStep[] = useMemo(
    () =>
      [...mainKeyed, ...enrichmentKeyed].filter(
        (k) => !excludedKeys.has(k.key)
      ),
    [mainKeyed, enrichmentKeyed, excludedKeys]
  );

  // For the prereq phase we don't filter — the file cabinet is its own thing.
  const prereqKeyed: KeyedStep[] = useMemo(
    () =>
      (prerequisiteSteps ?? []).map((step, i) => ({
        key: `p-${i}`,
        group: "main",
        groupIndex: i + 1,
        step,
      })),
    [prerequisiteSteps]
  );

  const activeKeyed: KeyedStep[] =
    phase === "prereq" ? prereqKeyed : filteredMainEnrichment;
  const activeSteps: ThinSliceStep[] = activeKeyed.map((k) => k.step);
  const total = activeSteps.length;
  const canAdvance = revealedCount < total;
  const canRetreat = revealedCount > 1;
  const onLastStep = revealedCount >= total;

  // If the teacher prunes steps below the current reveal pointer, snap back.
  useEffect(() => {
    if (revealedCount > total) setRevealedCount(Math.max(1, total));
  }, [total, revealedCount]);

  const exit = useCallback(() => {
    // Return to wherever the teacher launched the slice from. Most of
    // the time that's a unit page (e.g. `/math/units/grade-7-module-3`),
    // but it can also be the unified Rich Tasks library or a direct link.
    // history.back() honours all of those naturally. We fall back to the
    // library (with thin-slice pre-filter) for deep-link entries that
    // have no history — `/math/thin-slices` itself is now just a redirect
    // to the unified library, so we point straight at the destination.
    if (typeof window !== "undefined" && window.history.length > 1) {
      router.back();
    } else {
      router.push(`/math/rich-tasks?type=thin-slice`);
    }
  }, [router]);

  const advance = useCallback(() => {
    setRevealedCount((n) => Math.min(total, n + revealsPerStep));
  }, [total, revealsPerStep]);

  const retreat = useCallback(() => {
    setRevealedCount((n) => Math.max(1, n - revealsPerStep));
  }, [revealsPerStep]);

  const startPrereq = useCallback(() => {
    setPhase("prereq");
    setRevealedCount(1);
    setOrganizer(null);
  }, []);

  const startMain = useCallback(() => {
    setPhase("main");
    setRevealedCount(1);
    setOrganizer(null);
  }, []);

  const skipToMain = useCallback(() => {
    setPhase("main");
    setRevealedCount(1);
    setOrganizer(null);
  }, []);

  // Idle-fade controls
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | null = null;
    const reset = () => {
      setControlsVisible(true);
      if (timer) clearTimeout(timer);
      timer = setTimeout(() => setControlsVisible(false), 3000);
    };
    reset();
    window.addEventListener("mousemove", reset);
    window.addEventListener("keydown", reset);
    return () => {
      window.removeEventListener("mousemove", reset);
      window.removeEventListener("keydown", reset);
      if (timer) clearTimeout(timer);
    };
  }, []);

  // Keyboard: ESC exit, ← / → / Space step, A toggle answers, D toggle whiteboard.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      // While drawing, the overlay owns Esc (to exit drawing, not the projection).
      if (drawing) return;
      if (e.key === "Escape") exit();
      if (phase === "landing") return;
      if (e.key === "ArrowRight" || e.key === " ") {
        e.preventDefault();
        advance();
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        retreat();
      } else if (e.key.toLowerCase() === "a") {
        setShowAnswers((v) => !v);
      } else if (e.key.toLowerCase() === "d") {
        setDrawing(true);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [advance, retreat, exit, phase, drawing]);

  useEffect(() => {
    document.body.classList.add("project-mode");
    return () => {
      document.body.classList.remove("project-mode");
    };
  }, []);

  // ===== LANDING SCREEN =====
  if (phase === "landing") {
    return (
      <div
        className={`fixed inset-0 flex h-screen w-screen flex-col items-center justify-center px-8 transition-colors ${theme.textClass}`}
        style={{ background: theme.background }}
      >
        {theme.pattern && (
          <div
            className="pointer-events-none absolute inset-0"
            style={{ backgroundImage: theme.pattern, backgroundRepeat: "repeat" }}
          />
        )}
        <button
          onClick={exit}
          className={`absolute right-6 top-4 z-10 rounded-lg px-3 py-1.5 text-sm font-semibold transition-colors ${
            isDark
              ? "bg-white/10 text-white hover:bg-white/20"
              : "bg-pnp-gray-100 text-pnp-gray-700 hover:bg-pnp-gray-200"
          }`}
        >
          ✕ Exit
        </button>

        <div className="relative z-10 mx-auto max-w-3xl text-center">
          <div className="mb-5 text-6xl md:text-7xl">📂</div>
          <div className={`mb-3 text-sm font-bold uppercase tracking-widest ${isDark ? "text-pnp-yellow" : "text-purple-700"}`}>
            Open the File Cabinet
          </div>
          <h1
            className="font-heading font-extrabold leading-tight"
            style={{ fontSize: "clamp(2rem, 5vw, 4rem)" }}
          >
            {title}
          </h1>
          {prerequisiteLabel && (
            <p
              className={`mt-5 leading-snug ${isDark ? "text-white/80" : "text-pnp-gray-700"}`}
              style={{ fontSize: "clamp(1.1rem, 2vw, 1.5rem)" }}
            >
              {prerequisiteLabel}
            </p>
          )}
          <p className={`mt-2 text-sm ${isDark ? "text-white/50" : "text-pnp-gray-500"}`}>
            {prerequisiteSteps?.length ?? 0} warm-up problem
            {(prerequisiteSteps?.length ?? 0) === 1 ? "" : "s"}, then{" "}
            {steps.length} slice steps.
          </p>

          <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <button
              onClick={startPrereq}
              className="rounded-full bg-pnp-yellow px-7 py-3 text-lg font-bold text-pnp-navy shadow-lg transition-all hover:-translate-y-0.5 hover:bg-pnp-yellow-dark"
            >
              Run Warm-Up First →
            </button>
            <button
              onClick={skipToMain}
              className={`rounded-full px-6 py-3 text-base font-semibold transition-colors ${
                isDark
                  ? "bg-white/10 text-white hover:bg-white/20"
                  : "bg-pnp-gray-100 text-pnp-gray-700 hover:bg-pnp-gray-200"
              }`}
            >
              Skip to Slice
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ===== STAGE =====
  if (activeSteps.length === 0) {
    return (
      <div className="flex h-screen items-center justify-center text-pnp-gray-500">
        This thin slice has no steps.
      </div>
    );
  }

  const revealed = activeSteps.slice(0, revealedCount);
  const visible = revealed.slice(-BUBBLE_CAP);
  const phaseBadge = phase === "prereq" ? "📂 File Cabinet — Warm-Up" : null;
  // Shape only renders during the main phase by default (prereq problems are
  // typically the bare arithmetic warm-up — no figure needed).
  const showShape = phase === "main" && !!shape;

  return (
    <div
      key={`${sliceId}-${phase}`}
      className={`fixed inset-0 flex h-screen w-screen flex-col overflow-hidden transition-colors ${theme.textClass}`}
      style={{ background: theme.background }}
    >
      {theme.pattern && (
        <div
          className="pointer-events-none absolute inset-0 z-0"
          style={{ backgroundImage: theme.pattern, backgroundRepeat: "repeat" }}
        />
      )}
      {/* Top control bar. Above the DrawingOverlay SVG (z-200) so the
          chrome controls show a normal pointer cursor while drawing is on. */}
      <div
        className={`relative z-[220] flex shrink-0 items-center justify-between gap-4 px-6 py-2 transition-opacity duration-500 ${
          controlsVisible ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
      >
        <div className={`flex items-center gap-3 text-sm ${isDark ? "text-white/70" : "text-pnp-gray-600"}`}>
          <button
            onClick={() => setDrawerOpen(true)}
            className={`group flex items-center gap-1.5 rounded-md px-2 py-1 font-heading text-lg font-bold transition-colors ${
              isDark ? "hover:bg-white/10" : "hover:bg-pnp-gray-100"
            }`}
            title="Choose which steps to show"
          >
            {title}
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="opacity-50 group-hover:opacity-100"
              aria-hidden="true"
            >
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
            </svg>
          </button>

          {phaseBadge && (
            <span
              className={`rounded-full px-3 py-0.5 text-xs font-bold uppercase tracking-wider ${
                isDark ? "bg-pnp-yellow/20 text-pnp-yellow" : "bg-purple-100 text-purple-800"
              }`}
            >
              {phaseBadge}
            </span>
          )}
          <span className="font-mono">
            {revealedCount} / {total}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Bubble size: S / M / L / XL / XXL */}
          <div
            className={`flex rounded-lg border ${
              isDark ? "border-white/20 bg-white/5" : "border-pnp-gray-300 bg-white"
            }`}
            role="radiogroup"
            aria-label="Bubble size"
          >
            {SIZE_ORDER.map((s, i) => (
              <button
                key={s}
                role="radio"
                aria-checked={bubbleSize === s}
                onClick={() => setBubbleSize(s)}
                className={`px-2.5 py-1.5 text-sm font-semibold transition-colors ${
                  i === 0 ? "rounded-l-lg" : ""
                } ${i === SIZE_ORDER.length - 1 ? "rounded-r-lg" : ""} ${
                  bubbleSize === s
                    ? isDark ? "bg-white/20 text-white" : "bg-pnp-navy text-white"
                    : isDark ? "text-white/70 hover:bg-white/10" : "text-pnp-gray-700 hover:bg-pnp-gray-100"
                }`}
                title={SIZE_TOOLTIPS[s]}
              >
                {SIZE_LABELS[s]}
              </button>
            ))}
          </div>

          <button
            onClick={() => setShowAnswers((v) => !v)}
            className={`rounded-lg px-3 py-1.5 text-sm font-semibold transition-colors ${
              isDark ? "bg-white/10 text-white hover:bg-white/20" : "bg-pnp-gray-100 text-pnp-gray-700 hover:bg-pnp-gray-200"
            }`}
            title="Toggle answer reveal (A)"
          >
            {showAnswers ? "Hide Answers" : "Show Answers"}
          </button>

          {/* Theme: Light / Dark / Polka / Underwater / Chalkboard */}
          <div
            className={`flex rounded-lg border ${
              isDark ? "border-white/20 bg-white/5" : "border-pnp-gray-300 bg-white"
            }`}
            role="radiogroup"
            aria-label="Theme"
          >
            {THEME_ORDER.map((id, i) => (
              <button
                key={id}
                role="radio"
                aria-checked={themeId === id}
                onClick={() => setThemeId(id)}
                className={`px-2.5 py-1.5 text-sm font-semibold transition-colors ${
                  i === 0 ? "rounded-l-lg" : ""
                } ${i === THEME_ORDER.length - 1 ? "rounded-r-lg" : ""} ${
                  themeId === id
                    ? isDark ? "bg-white/20 text-white" : "bg-pnp-navy text-white"
                    : isDark ? "text-white/70 hover:bg-white/10" : "text-pnp-gray-700 hover:bg-pnp-gray-100"
                }`}
                title={THEMES[id].label}
              >
                {THEMES[id].label}
              </button>
            ))}
          </div>

          <button
            onClick={() => setTimerOpen((t) => !t)}
            aria-pressed={timerOpen}
            className={`rounded-lg px-3 py-1.5 text-sm font-semibold transition-colors ${
              timerOpen
                ? "bg-pnp-yellow text-pnp-navy"
                : isDark ? "bg-white/10 text-white hover:bg-white/20" : "bg-pnp-gray-100 text-pnp-gray-700 hover:bg-pnp-gray-200"
            }`}
            title="Toggle classroom timer"
          >
            Timer
          </button>

          {/* Whiteboard draw toggle. Press D or click to enter draw mode. */}
          <button
            onClick={() => setDrawing((d) => !d)}
            aria-pressed={drawing}
            className={`rounded-lg px-3 py-1.5 text-sm font-semibold transition-colors ${
              drawing
                ? "bg-pnp-yellow text-pnp-navy"
                : isDark ? "bg-white/10 text-white hover:bg-white/20" : "bg-pnp-gray-100 text-pnp-gray-700 hover:bg-pnp-gray-200"
            }`}
            title="Draw on the projection (D)"
          >
            {drawing ? "Drawing…" : "Draw"}
          </button>

          <GroupsButton isDark={isDark} />

          <button
            onClick={exit}
            className={`rounded-lg px-3 py-1.5 text-sm font-semibold transition-colors ${
              isDark ? "bg-white/10 text-white hover:bg-white/20" : "bg-pnp-gray-100 text-pnp-gray-700 hover:bg-pnp-gray-200"
            }`}
            title="Exit (ESC)"
          >
            ✕ Exit
          </button>
        </div>
      </div>

      {/* Stem banner */}
      {stem && (
        <div
          className={`relative z-10 shrink-0 border-b px-8 py-3 text-center ${
            isDark
              ? "border-white/10 bg-white/5 text-white/90"
              : "border-pnp-gray-200 bg-pnp-gray-50 text-pnp-gray-800"
          }`}
        >
          <div
            className="font-sans font-semibold leading-snug"
            style={{ fontSize: "clamp(1.1rem, 2vw, 1.6rem)" }}
          >
            {stem}
          </div>
        </div>
      )}

      {/* Stage */}
      <div className="relative z-10 flex min-h-0 flex-1 items-center justify-center px-8 pb-20 md:px-16">
        <BubbleStage
          sliceKey={`${sliceId}-${phase}`}
          visible={visible}
          startIndex={revealedCount - visible.length}
          showAnswers={showAnswers}
          theme={theme}
          shape={showShape ? shape : undefined}
          size={bubbleSize}
          organizer={organizer}
        />
      </div>

      {/* Bottom step controls. Above the DrawingOverlay SVG (z-200) so the
          chrome buttons show a normal pointer cursor while drawing is on. */}
      <div className="absolute inset-x-0 bottom-0 z-[220] flex items-center justify-center gap-4 pb-5">
        <button
          onClick={retreat}
          disabled={!canRetreat}
          className={`rounded-full px-5 py-2.5 text-base font-semibold transition-all ${
            canRetreat
              ? isDark ? "bg-white/10 text-white hover:bg-white/20" : "bg-pnp-gray-200 text-pnp-gray-800 hover:bg-pnp-gray-300"
              : "cursor-not-allowed opacity-30"
          }`}
          title="Previous step (←)"
        >
          ← Back
        </button>

        <div className="flex items-center gap-1.5">
          {activeSteps.map((_, i) => (
            <span
              key={i}
              className={`h-2.5 w-2.5 rounded-full transition-all ${
                i < revealedCount
                  ? isDark ? "bg-white" : "bg-pnp-navy"
                  : isDark ? "bg-white/20" : "bg-pnp-gray-300"
              }`}
            />
          ))}
        </div>

        {phase === "prereq" && onLastStep ? (
          <button
            onClick={startMain}
            className="rounded-full bg-pnp-yellow px-6 py-2.5 text-base font-bold text-pnp-navy shadow-lg transition-all hover:-translate-y-0.5 hover:bg-pnp-yellow-dark"
            title="Move on to the main slice"
          >
            Begin Slice →
          </button>
        ) : (
          <button
            onClick={advance}
            disabled={!canAdvance}
            className={`rounded-full px-6 py-2.5 text-base font-bold transition-all ${
              canAdvance
                ? isDark ? "bg-pnp-yellow text-pnp-navy hover:bg-pnp-yellow-dark" : "bg-pnp-navy text-white hover:bg-pnp-blue"
                : "cursor-not-allowed bg-pnp-gray-200 text-pnp-gray-500"
            }`}
            title="Next step (→ or space)"
          >
            {canAdvance ? "Next →" : "Done"}
          </button>
        )}
      </div>

      <div
        className={`pointer-events-none absolute right-6 top-14 z-10 text-xs transition-opacity duration-500 ${
          controlsVisible ? "opacity-50" : "opacity-0"
        } ${isDark ? "text-white/60" : "text-pnp-gray-500"}`}
      >
        ← / → step • A answers • drag bubbles • ESC exit
      </div>

      {/* Step picker drawer */}
      {drawerOpen && (
        <StepDrawer
          mainSteps={mainKeyed}
          enrichmentSteps={enrichmentKeyed}
          excludedKeys={excludedKeys}
          setExcludedKeys={setExcludedKeys}
          revealsPerStep={revealsPerStep}
          setRevealsPerStep={setRevealsPerStep}
          organizer={organizer}
          setOrganizer={setOrganizer}
          isDark={isDark}
          onClose={() => setDrawerOpen(false)}
        />
      )}

      {/* Whiteboard overlay. wipeKey changes whenever the visible content
          shifts (phase / revealedCount / picker), so each new view starts
          with a clean board. */}
      <DrawingOverlay
        active={drawing}
        setActive={setDrawing}
        wipeKey={`${phase}-${revealedCount}-${excludedKeys.size}-${sliceId}`}
      />

      {/* Draggable classroom timer. Shared component with the rich-task
          projection so any behavior change applies in both views. */}
      <TimerOverlay
        visible={timerOpen}
        onClose={() => setTimerOpen(false)}
        isDark={isDark}
      />
    </div>
  );
}

// =====================
// BUBBLE STAGE (draggable, cap 20, optional per-bubble shape)
// =====================
function BubbleStage({
  sliceKey,
  visible,
  startIndex,
  showAnswers,
  theme,
  shape,
  size,
  organizer,
}: {
  sliceKey: string;
  visible: ThinSliceStep[];
  startIndex: number;
  showAnswers: boolean;
  theme: ThemeConfig;
  shape?: ThinSliceShape;
  size: BubbleSize;
  organizer: OrganizerKind | null;
}) {
  const stageRef = useRef<HTMLDivElement | null>(null);
  const [stageSize, setStageSize] = useState({ w: 0, h: 0 });

  useEffect(() => {
    const measure = () => {
      if (!stageRef.current) return;
      const r = stageRef.current.getBoundingClientRect();
      setStageSize({ w: r.width, h: r.height });
    };
    measure();
    window.addEventListener("resize", measure);
    return () => window.removeEventListener("resize", measure);
  }, []);

  // Bubble dimensions (unchanged from prior version).
  const bubbleW = useMemo(() => {
    if (stageSize.w === 0) return 200;
    const base = shape
      ? Math.max(220, Math.min(320, stageSize.w / 5))
      : Math.max(160, Math.min(260, stageSize.w / 6));
    return Math.round(base * SIZE_SCALE[size]);
  }, [stageSize.w, shape, size]);
  const bubbleH = shape ? bubbleW * 1.15 : bubbleW * 0.7;
  const shapeWidth = bubbleW * 0.55;

  // Auto-place each step on a soft grid for its initial position. Persists across
  // navigation because we key by step index. Once Matter takes over, the body's
  // position is what matters; this is just where it spawns.
  const autoPos = useCallback(
    (stepIndex: number): { x: number; y: number } => {
      if (stageSize.w === 0) return { x: 0, y: 0 };
      const cols = shape ? 4 : 5;
      const col = stepIndex % cols;
      const row = Math.floor(stepIndex / cols);
      const padX = (stageSize.w - cols * bubbleW) / (cols + 1);
      const padY = 24;
      const x = padX + col * (bubbleW + padX);
      const y = padY + row * (bubbleH + padY);
      return { x, y };
    },
    [stageSize.w, bubbleW, bubbleH, shape]
  );

  // Estimate rendered width AND height for a given step's content. Both the
  // rendered DOM and the Matter body use this so collisions match the
  // visible edges and the box always contains its text.
  //
  // Strategy:
  //   1. Estimate per-glyph width at the current font scale.
  //   2. The natural single-line width = char count * glyph width + padding.
  //      Cap that width at 1.6 × bubbleW so super-long content doesn't span
  //      the whole stage.
  //   3. If the natural width exceeded the cap, the content WILL wrap. Compute
  //      how many lines it'll take at the capped width, and grow the height
  //      to match. Otherwise use the standard height.
  const bubbleSize = useCallback(
    (stepIndex: number): { w: number; h: number } => {
      const slot = visible[stepIndex - startIndex];
      if (!slot) return { w: bubbleW, h: bubbleH };
      const visibleText = slot.problem
        .replace(/\\frac\{([^}]*)\}\{([^}]*)\}/g, (_, n: string, d: string) =>
          n.length >= d.length ? n : d
        )
        .replace(/\\sqrt\{([^}]*)\}/g, (_, x: string) => x)
        .replace(/\s+/g, " ")
        .trim();

      // Per-glyph width scales with the font size. base ≈ 9.5px/char at
      // SIZE_SCALE=1.0; multiply by the current FONT_SCALE.
      const charPx = 9.5 * FONT_SCALE[size];
      const padPx = 48; // px-5 × 2 + border × 2
      const naturalW = visibleText.length * charPx + padPx;
      const cap = bubbleW * 1.6;
      const w = Math.max(bubbleW, Math.min(cap, naturalW));

      // If content fits in one line at the chosen width, the standard height
      // is fine. Otherwise estimate line count and grow the height.
      const innerWidth = w - padPx;
      const lineWidth = visibleText.length * charPx;
      const lines = Math.max(1, Math.ceil(lineWidth / Math.max(innerWidth, 1)));

      // Per-line height ≈ font size (1em) × line-height (~1.15) plus a 4px
      // top/bottom padding contribution. Standard bubbleH already includes
      // some breathing room — we add `(lines - 1) * lineH` for wrapped lines.
      const fontPx = 17 * FONT_SCALE[size];   // ~17px at SIZE_SCALE=1.0
      const lineH = fontPx * 1.25;
      const extraH = (lines - 1) * lineH;
      const h = bubbleH + extraH;

      return { w, h };
    },
    [visible, startIndex, bubbleW, bubbleH, size]
  );

  // Hand bubble physics off to Matter. The hook tracks bodies keyed by step index,
  // creates new ones when steps appear, drives DOM positions imperatively each
  // frame, and routes mouse drag to a Matter MouseConstraint for natural throws.
  const elementsRef = useBubblePhysics({
    stageRef,
    sliceKey,
    stageSize,
    bubbleW,
    bubbleH,
    visibleStepIndices: visible.map((_, i) => startIndex + i),
    autoPos,
    bubbleSize,
  });

  return (
    <div ref={stageRef} className="absolute inset-0 select-none">
      {organizer && (
        <OrganizerOverlay
          kind={organizer}
          width={stageSize.w}
          height={stageSize.h}
        />
      )}
      {visible.map((step, idx) => {
        const stepIndex = startIndex + idx;
        const isNewest = idx === visible.length - 1;
        // Use the same per-step size that we hand to Matter, so the rendered
        // bubble and its physics body share dimensions exactly.
        const dims = bubbleSize(stepIndex);
        return (
          // Outer wrapper: Matter writes its transform here (translate only).
          <div
            key={stepIndex}
            ref={(el) => {
              if (el) elementsRef.current.set(stepIndex, el);
              else elementsRef.current.delete(stepIndex);
            }}
            data-step-index={stepIndex}
            className="absolute"
            style={{
              left: 0,
              top: 0,
              width: dims.w,
              height: dims.h,
              touchAction: "none",
              willChange: "transform",
            }}
          >
            {/* Inner wrapper: pop animation lives here so it doesn't fight Matter. */}
            <div
              className={`thin-slice-bubble flex h-full w-full cursor-grab flex-col items-center justify-center gap-2 rounded-3xl border-4 px-5 py-4 font-heading font-extrabold shadow-lg transition-shadow active:cursor-grabbing active:shadow-2xl ${theme.bubbleBorder} ${theme.bubbleBg} ${theme.bubbleText} ${
                isNewest ? `ring-4 ${theme.accentRing}` : ""
              }`}
              // Font scales with the slider so a bigger box also gets bigger
              // text. clamp range × FONT_SCALE keeps the typographic ramp
              // working at every viewport.
              style={{
                fontSize: `clamp(${(1.1 * FONT_SCALE[size]).toFixed(2)}rem, ${(2 * FONT_SCALE[size]).toFixed(2)}vw, ${(1.6 * FONT_SCALE[size]).toFixed(2)}rem)`,
              }}
            >
              {shape && step.labels && (
                <div className="pointer-events-none flex items-center justify-center">
                  <ShapeRenderer shape={shape} labels={step.labels} width={shapeWidth} />
                </div>
              )}

              {/* Allow the problem text to wrap when bubbleSize estimated
                  it'll need multiple lines. The outer bubble's height grew
                  to match (see bubbleSize callback) so the bubble still
                  contains the wrapped content. */}
              <div className="text-center leading-tight">
                <MathExpression text={step.problem} />
              </div>

              {showAnswers && step.answer && (
                <div
                  className={`whitespace-nowrap font-sans font-semibold ${theme.accentText}`}
                  style={{ fontSize: "0.7em" }}
                >
                  = <MathExpression text={step.answer} />
                </div>
              )}
            </div>
          </div>
        );
      })}

      <style>{`
        .thin-slice-bubble {
          animation: bubble-pop 320ms cubic-bezier(0.34, 1.56, 0.64, 1) both;
        }
        @keyframes bubble-pop {
          0%   { transform: scale(0.4); opacity: 0; }
          60%  { transform: scale(1.08); }
          100% { transform: scale(1); opacity: 1; }
        }
      `}</style>
    </div>
  );
}

// =====================
// STEP PICKER DRAWER
// =====================
function StepDrawer({
  mainSteps,
  enrichmentSteps,
  excludedKeys,
  setExcludedKeys,
  revealsPerStep,
  setRevealsPerStep,
  organizer,
  setOrganizer,
  isDark,
  onClose,
}: {
  mainSteps: KeyedStep[];
  enrichmentSteps: KeyedStep[];
  excludedKeys: Set<string>;
  setExcludedKeys: (s: Set<string>) => void;
  revealsPerStep: 1 | 2 | 3;
  setRevealsPerStep: (n: 1 | 2 | 3) => void;
  organizer: OrganizerKind | null;
  setOrganizer: (o: OrganizerKind | null) => void;
  isDark: boolean;
  onClose: () => void;
}) {
  const toggle = (key: string) => {
    const next = new Set(excludedKeys);
    if (next.has(key)) next.delete(key);
    else next.add(key);
    setExcludedKeys(next);
  };
  const allKeys = [...mainSteps, ...enrichmentSteps].map((k) => k.key);
  const allChecked = allKeys.every((k) => !excludedKeys.has(k));
  const reset = () => setExcludedKeys(new Set());
  const noneAll = () => setExcludedKeys(new Set(allKeys));

  // ESC closes the drawer
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  // Total visible-step count (for the live badge in the drawer header)
  const visibleCount = allKeys.filter((k) => !excludedKeys.has(k)).length;

  const panelBg = isDark ? "bg-pnp-navy text-white" : "bg-white text-pnp-gray-900";
  const dividerColor = isDark ? "border-white/10" : "border-pnp-gray-200";
  const subtle = isDark ? "text-white/60" : "text-pnp-gray-500";
  const stepBorder = isDark ? "border-white/10" : "border-pnp-gray-200";
  const stepHover = isDark ? "hover:bg-white/5" : "hover:bg-pnp-gray-50";

  return (
    <>
      {/* Backdrop — click to close */}
      <div
        onClick={onClose}
        className="fixed inset-0 z-[230] bg-black/40 transition-opacity"
        aria-hidden="true"
      />
      {/* Panel */}
      <aside
        role="dialog"
        aria-label="Choose steps"
        className={`fixed left-0 top-0 z-[240] flex h-full w-[360px] flex-col shadow-2xl ${panelBg} animate-thin-slice-drawer`}
      >
        {/* Header */}
        <div className={`flex shrink-0 items-center justify-between border-b ${dividerColor} px-5 py-4`}>
          <div>
            <div className="font-heading text-lg font-bold">Choose Steps</div>
            <div className={`text-xs ${subtle}`}>
              {visibleCount} of {allKeys.length} step{allKeys.length === 1 ? "" : "s"} will show
            </div>
          </div>
          <button
            onClick={onClose}
            className={`rounded-lg px-3 py-1.5 text-sm font-semibold transition-colors ${
              isDark ? "bg-white/10 text-white hover:bg-white/20" : "bg-pnp-gray-100 text-pnp-gray-700 hover:bg-pnp-gray-200"
            }`}
            title="Close (ESC)"
          >
            ✕
          </button>
        </div>

        {/* Reveals-per-step counter */}
        <div className={`shrink-0 border-b ${dividerColor} px-5 py-4`}>
          <div className="mb-1 text-sm font-semibold">Reveals per click</div>
          <div className={`mb-3 text-xs ${subtle}`}>
            How many bubbles appear each time you press Next.
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setRevealsPerStep((Math.max(1, revealsPerStep - 1) as 1 | 2 | 3))}
              disabled={revealsPerStep <= 1}
              className={`flex h-9 w-9 items-center justify-center rounded-full text-lg font-bold transition-colors ${
                revealsPerStep <= 1
                  ? "cursor-not-allowed opacity-30"
                  : isDark ? "bg-white/10 text-white hover:bg-white/20" : "bg-pnp-gray-100 text-pnp-gray-700 hover:bg-pnp-gray-200"
              }`}
              title="Fewer per click"
            >
              −
            </button>
            <div
              className={`flex h-9 min-w-[3rem] items-center justify-center rounded-md border px-3 font-mono text-lg font-bold ${
                isDark ? "border-white/20" : "border-pnp-gray-300"
              }`}
            >
              {revealsPerStep}
            </div>
            <button
              onClick={() => setRevealsPerStep((Math.min(3, revealsPerStep + 1) as 1 | 2 | 3))}
              disabled={revealsPerStep >= 3}
              className={`flex h-9 w-9 items-center justify-center rounded-full text-lg font-bold transition-colors ${
                revealsPerStep >= 3
                  ? "cursor-not-allowed opacity-30"
                  : isDark ? "bg-white/10 text-white hover:bg-white/20" : "bg-pnp-gray-100 text-pnp-gray-700 hover:bg-pnp-gray-200"
              }`}
              title="More per click"
            >
              +
            </button>
            <span className={`ml-2 text-xs ${subtle}`}>(max 3)</span>
          </div>
        </div>

        {/* Step list (scrollable) */}
        <div className="min-h-0 flex-1 overflow-y-auto px-5 py-4">
          {/* Main group */}
          <SectionLabel label="Main slice" subtle={subtle} />
          <ul className={`mt-2 space-y-1 rounded-lg border ${stepBorder} p-1`}>
            {mainSteps.map((k) => (
              <StepRow
                key={k.key}
                k={k}
                checked={!excludedKeys.has(k.key)}
                onToggle={() => toggle(k.key)}
                hoverClass={stepHover}
                isDark={isDark}
              />
            ))}
          </ul>

          {/* Enrichment group */}
          {enrichmentSteps.length > 0 && (
            <>
              <div className="mt-5">
                <SectionLabel label="Enrichment" subtle={subtle} />
              </div>
              <ul className={`mt-2 space-y-1 rounded-lg border ${stepBorder} p-1`}>
                {enrichmentSteps.map((k) => (
                  <StepRow
                    key={k.key}
                    k={k}
                    checked={!excludedKeys.has(k.key)}
                    onToggle={() => toggle(k.key)}
                    hoverClass={stepHover}
                    isDark={isDark}
                  />
                ))}
              </ul>
            </>
          )}
        </div>

        {/* Background organizer picker */}
        <div className={`shrink-0 border-t ${dividerColor} px-5 py-4`}>
          <div className="mb-1 text-sm font-semibold">Background organizer</div>
          <div className={`mb-3 text-xs ${subtle}`}>
            Drop a scaffold behind the bubbles for the consolidation move.
          </div>
          <div className="grid grid-cols-3 gap-2">
            <OrganizerPickerButton
              kind={null}
              current={organizer}
              onPick={setOrganizer}
              label="None"
              isDark={isDark}
            />
            {ORGANIZER_OPTIONS.map((o) => (
              <OrganizerPickerButton
                key={o.kind}
                kind={o.kind}
                current={organizer}
                onPick={setOrganizer}
                label={o.label}
                isDark={isDark}
              />
            ))}
          </div>
        </div>

        {/* Footer actions */}
        <div className={`flex shrink-0 items-center justify-between gap-2 border-t ${dividerColor} px-5 py-3`}>
          <button
            onClick={reset}
            disabled={allChecked}
            className={`text-sm font-semibold transition-colors ${
              allChecked
                ? "cursor-not-allowed opacity-30"
                : isDark ? "text-pnp-yellow hover:underline" : "text-pnp-blue hover:underline"
            }`}
          >
            Reset to all
          </button>
          <button
            onClick={noneAll}
            className={`text-sm font-semibold transition-colors ${
              isDark ? "text-white/60 hover:text-white" : "text-pnp-gray-500 hover:text-pnp-gray-700"
            }`}
          >
            Uncheck all
          </button>
        </div>
      </aside>

      <style>{`
        @keyframes thin-slice-drawer-in {
          from { transform: translateX(-100%); }
          to   { transform: translateX(0); }
        }
        .animate-thin-slice-drawer {
          animation: thin-slice-drawer-in 220ms cubic-bezier(0.22, 1, 0.36, 1) both;
        }
      `}</style>
    </>
  );
}

function SectionLabel({ label, subtle }: { label: string; subtle: string }) {
  return (
    <div className={`text-xs font-bold uppercase tracking-wider ${subtle}`}>{label}</div>
  );
}

function StepRow({
  k,
  checked,
  onToggle,
  hoverClass,
  isDark,
}: {
  k: KeyedStep;
  checked: boolean;
  onToggle: () => void;
  hoverClass: string;
  isDark: boolean;
}) {
  return (
    <li>
      <label
        className={`flex cursor-pointer items-center gap-3 rounded-md px-2 py-1.5 transition-colors ${hoverClass}`}
      >
        <input
          type="checkbox"
          checked={checked}
          onChange={onToggle}
          className="h-4 w-4 shrink-0 cursor-pointer accent-pnp-blue"
        />
        <span
          className={`font-mono text-xs ${isDark ? "text-white/40" : "text-pnp-gray-500"}`}
          aria-hidden="true"
        >
          {k.groupIndex}.
        </span>
        <span className="flex-1 truncate text-sm">{k.step.problem}</span>
      </label>
    </li>
  );
}

// =====================
// ORGANIZER PICKER (drawer)
// =====================
const ORGANIZER_OPTIONS: { kind: OrganizerKind; label: string }[] = [
  { kind: "venn-2", label: "Venn 2" },
  { kind: "venn-3", label: "Venn 3" },
  { kind: "three-column", label: "3-Col" },
  { kind: "quadrants", label: "Quad" },
  { kind: "step-ladder", label: "Ladder" },
  { kind: "frayer", label: "Frayer" },
];

function OrganizerPickerButton({
  kind,
  current,
  onPick,
  label,
  isDark,
}: {
  kind: OrganizerKind | null;
  current: OrganizerKind | null;
  onPick: (k: OrganizerKind | null) => void;
  label: string;
  isDark: boolean;
}) {
  const selected = kind === current;
  return (
    <button
      onClick={() => onPick(kind)}
      className={`flex flex-col items-center justify-center gap-1 rounded-lg border-2 px-2 py-2 text-xs font-semibold transition-all ${
        selected
          ? isDark
            ? "border-pnp-yellow bg-white/10 text-white"
            : "border-pnp-navy bg-pnp-gray-50 text-pnp-navy"
          : isDark
          ? "border-white/10 text-white/70 hover:border-white/30 hover:bg-white/5"
          : "border-pnp-gray-200 text-pnp-gray-600 hover:border-pnp-gray-400 hover:bg-pnp-gray-50"
      }`}
      title={label}
    >
      <div className="flex h-10 w-full items-center justify-center">
        <OrganizerThumb kind={kind} />
      </div>
      <span>{label}</span>
    </button>
  );
}

/** Tiny thumbnail SVG for the picker buttons. */
function OrganizerThumb({ kind }: { kind: OrganizerKind | null }) {
  const w = 50;
  const h = 32;
  const stroke = "currentColor";
  const sw = 1.5;
  if (kind === null) {
    return (
      <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} fill="none">
        <rect x={2} y={2} width={w - 4} height={h - 4} stroke={stroke} strokeDasharray="3 3" strokeWidth={sw} rx={3} />
      </svg>
    );
  }
  if (kind === "venn-2") {
    return (
      <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} fill="none" stroke={stroke} strokeWidth={sw}>
        <circle cx={20} cy={16} r={10} />
        <circle cx={30} cy={16} r={10} />
      </svg>
    );
  }
  if (kind === "venn-3") {
    return (
      <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} fill="none" stroke={stroke} strokeWidth={sw}>
        <circle cx={25} cy={11} r={8} />
        <circle cx={20} cy={20} r={8} />
        <circle cx={30} cy={20} r={8} />
      </svg>
    );
  }
  if (kind === "three-column") {
    return (
      <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} fill="none" stroke={stroke} strokeWidth={sw}>
        <rect x={4} y={4} width={w - 8} height={h - 8} />
        <line x1={4 + (w - 8) / 3} y1={4} x2={4 + (w - 8) / 3} y2={h - 4} />
        <line x1={4 + ((w - 8) * 2) / 3} y1={4} x2={4 + ((w - 8) * 2) / 3} y2={h - 4} />
        <line x1={4} y1={9} x2={w - 4} y2={9} />
      </svg>
    );
  }
  if (kind === "quadrants") {
    return (
      <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} fill="none" stroke={stroke} strokeWidth={sw}>
        <line x1={w / 2} y1={4} x2={w / 2} y2={h - 4} />
        <line x1={4} y1={h / 2} x2={w - 4} y2={h / 2} />
      </svg>
    );
  }
  if (kind === "step-ladder") {
    return (
      <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} fill="none" stroke={stroke} strokeWidth={sw}>
        <line x1={6} y1={h - 8} x2={w - 6} y2={h - 8} />
        {[0, 1, 2, 3, 4].map((i) => (
          <line key={i} x1={6 + (i + 0.5) * ((w - 12) / 5)} y1={h - 12} x2={6 + (i + 0.5) * ((w - 12) / 5)} y2={h - 4} />
        ))}
      </svg>
    );
  }
  if (kind === "frayer") {
    return (
      <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} fill="none" stroke={stroke} strokeWidth={sw}>
        <rect x={4} y={4} width={w - 8} height={h - 8} rx={2} />
        <line x1={w / 2} y1={4} x2={w / 2} y2={h - 4} />
        <line x1={4} y1={h / 2} x2={w - 4} y2={h / 2} />
        <ellipse cx={w / 2} cy={h / 2} rx={5} ry={3} />
      </svg>
    );
  }
  return null;
}

