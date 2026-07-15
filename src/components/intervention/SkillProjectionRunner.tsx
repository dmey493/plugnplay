"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { PROJECTION_THEMES, THEME_ORDER, type ThemeId, type ThemeConfig } from "@/lib/projection-themes";
import { InlineDiagram, MathText, type RenderData } from "./InlineMath";
import DrawingOverlay from "./DrawingOverlay";
import GroupsButton from "@/components/groups/GroupsButton";

interface ProjItem {
  stem: string;
  answer: string;
  choices?: string[];
  /** Section label — mirrors the printed session sheet ("Let's Try
   *  Together", "Your Turn", "Remember These?", "Show What You Know"). */
  section: string;
  render_data?: RenderData;
  choices_render?: Array<RenderData | null>;
  parts?: Array<{ label: string; prompt: string; answer: string; item_type?: string }>;
  /** Conceptual item types: error_analysis renders `shown_work` as a
   *  flawed-student-work card the class critiques. */
  type?: string;
  shown_work?: string[];
}

/** Session-sheet extras from the engine payload — the projection opens
 *  with the same arc the paper prints. */
export interface SolutionStep {
  math?: string | null;
  annotation?: string;
  given?: boolean;
}
export interface WorkedSolution {
  stem: string;
  answer: string;
  steps: SolutionStep[];
  /** Figure the example reasons about, drawn at the modeling moment. */
  render_data?: RenderData | null;
}
export interface FluencyBlock {
  title?: string;
  items: Array<{ stem: string; answer: string }>;
}

type Slide =
  | { kind: "fluency"; label: string }
  | { kind: "worked"; label: string }
  | { kind: "faded"; label: string }
  | { kind: "problem"; label: string; item: ProjItem };

// `items` accepts either bare strings (sort_cards) or {label, answer}
// objects (picture_sort). The runner normalizes both into the same draggable
// card shape — the only difference today is the larger card font on
// picture_sort. answer is reserved for a future "reveal correct answers"
// affordance; not surfaced yet.
type ArtifactItem = string | { label: string; answer?: string };

interface ArtifactDef {
  title?: string;
  kind?: string;
  categories?: string[];
  items?: ArtifactItem[];
  instructions?: string;
}

/** Teacher-only lesson content pulled from the skill JSON server-side.
 *  Shown in the toggleable presenter panel — never on the student-facing
 *  stage itself. */
export interface TeacherGuide {
  i_do_script?: string;
  // `visual` puts the step's model (hundredths grid, bar model, number
  // line…) on screen instead of leaving it as words the teacher reads.
  worked_example_script?: Array<{ kind: string; text: string; visual?: RenderData }>;
  canonical_error?: { pattern: string; example: string; why?: string };
  redirect_script?: { stop: string; prompt: string; praise: string };
  sentence_starters?: string[];
}

interface Props {
  skillId: string;
  skillName: string;
  standardCode: string;
  session: 1 | 2;
  items: ProjItem[];
  artifact?: ArtifactDef;
  teacherGuide?: TeacherGuide;
  fluency?: FluencyBlock | null;
  workedSolution?: WorkedSolution | null;
  fadedExample?: WorkedSolution | null;
  sentenceStarters?: string[] | null;
}

// Phase colors mirror the printed session sheet's chip palette.
const SECTION_BADGE: Record<string, { bg: string; fg: string }> = {
  "Fluency Sprint":      { bg: "rgba(254, 243, 199, 0.9)", fg: "#92400e" },
  "Watch & Learn":       { bg: "rgba(219, 234, 254, 0.9)", fg: "#1e40af" },
  "You Finish It":       { bg: "rgba(219, 250, 219, 0.9)", fg: "#15803d" },
  "Worked Example":      { bg: "rgba(219, 234, 254, 0.9)", fg: "#1e40af" },
  "Let's Try Together":  { bg: "rgba(254, 243, 199, 0.9)", fg: "#92400e" },
  "Your Turn":           { bg: "rgba(219, 250, 219, 0.9)", fg: "#15803d" },
  "Remember These?":     { bg: "rgba(255, 237, 213, 0.9)", fg: "#9a3412" },
  "Show What You Know":  { bg: "rgba(219, 234, 254, 0.9)", fg: "#1e40af" },
};
const DEFAULT_BADGE = { bg: "rgba(229, 231, 235, 0.9)", fg: "#374151" };
const badgeFor = (label: string) => SECTION_BADGE[label] ?? DEFAULT_BADGE;

type Mode = "problems" | "activity";

export default function SkillProjectionRunner({
  skillId,
  skillName,
  standardCode,
  session,
  items,
  artifact,
  teacherGuide,
  fluency,
  workedSolution,
  fadedExample,
  sentenceStarters,
}: Props) {
  const router = useRouter();
  // sort_cards (vocabulary keywords) and picture_sort (emoji-based scenes)
  // both use the SortCardsStage drag-and-drop UI; only the card font scales up.
  const isSortActivity = artifact?.kind === "sort_cards" || artifact?.kind === "picture_sort";
  const hasActivity = isSortActivity && (artifact?.items?.length ?? 0) > 0;

  const [themeId, setThemeId] = useState<ThemeId>("light");
  const theme = PROJECTION_THEMES[themeId];

  // The slide deck mirrors the printed session sheet: fluency sprint →
  // worked example → faded example → the practice/exit problems.
  const slides = useMemo<Slide[]>(() => {
    const s: Slide[] = [];
    if (fluency && fluency.items.length > 0) s.push({ kind: "fluency", label: "Fluency Sprint" });
    if (workedSolution) s.push({ kind: "worked", label: "Watch & Learn" });
    if (fadedExample) s.push({ kind: "faded", label: "You Finish It" });
    for (const item of items) s.push({ kind: "problem", label: item.section, item });
    return s;
  }, [fluency, workedSolution, fadedExample, items]);

  const [mode, setMode] = useState<Mode>(slides.length > 0 ? "problems" : "activity");
  const [idx, setIdx] = useState(0);
  // Reveal is a counter: problems/faded/fluency toggle 0↔1; the worked
  // example steps through its annotated solution one press at a time.
  const [reveal, setReveal] = useState(0);
  const [controlsVisible, setControlsVisible] = useState(true);
  // Whiteboard-style drawing toggle. When `drawing` is true, a transparent
  // SVG overlay above the content captures pointer events. Only available
  // in problems mode — Activity mode uses drag-and-drop on the cards.
  const [drawing, setDrawing] = useState(false);
  // Presenter panel: teacher-only cues (Say/Ask/Watch script, watch-for
  // error, answer preview). Toggled with P or the Guide button.
  const hasGuide = !!(teacherGuide && (teacherGuide.worked_example_script?.length
    || teacherGuide.i_do_script || teacherGuide.canonical_error
    || teacherGuide.redirect_script));
  const [presenterOpen, setPresenterOpen] = useState(false);
  // Fluency timer (1-5 min countdown for timed sprints).
  const [timerPickerOpen, setTimerPickerOpen] = useState(false);
  const [timerLeft, setTimerLeft] = useState<number | null>(null);
  const [timerRunning, setTimerRunning] = useState(false);
  useEffect(() => {
    if (!timerRunning || timerLeft === null) return;
    if (timerLeft <= 0) { setTimerRunning(false); return; }
    const t = setTimeout(() => setTimerLeft((s) => (s === null ? null : s - 1)), 1000);
    return () => clearTimeout(t);
  }, [timerRunning, timerLeft]);
  const startTimer = (minutes: number) => {
    setTimerLeft(minutes * 60);
    setTimerRunning(true);
    setTimerPickerOpen(false);
  };
  // When the teacher switches to activity mode while drawing, exit drawing
  // so the drag-and-drop works.
  useEffect(() => { if (mode !== "problems") setDrawing(false); }, [mode]);

  // Reset reveal whenever the visible slide changes.
  useEffect(() => { setReveal(0); }, [idx]);

  const slide = slides[idx];
  // Max reveal state per slide: the worked example steps through each
  // solution line then the answer; everything else is a show/hide toggle.
  const maxReveal =
    slide?.kind === "worked" ? (workedSolution?.steps.length ?? 0) + 1 : 1;
  const advanceReveal = useCallback(() => {
    setReveal((r) => (r >= maxReveal ? 0 : r + 1));
  }, [maxReveal]);

  const next = useCallback(() => {
    if (mode !== "problems") return;
    setIdx((i) => Math.min(i + 1, Math.max(slides.length - 1, 0)));
  }, [slides.length, mode]);
  const prev = useCallback(() => {
    if (mode !== "problems") return;
    setIdx((i) => Math.max(i - 1, 0));
  }, [mode]);

  // Keyboard: Esc back, ←/→ to navigate, A to reveal, T to cycle theme,
  // D to toggle whiteboard drawing.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      // When drawing is active, the overlay owns Esc (to exit drawing,
      // not the projection). Don't capture other keys either — let typing
      // pass through if a teacher ever has a focused input.
      if (drawing) return;
      if (e.key === "Escape") {
        router.back();
        return;
      }
      if (e.key === "ArrowRight" || e.key === " ") next();
      else if (e.key === "ArrowLeft") prev();
      else if (e.key === "a" || e.key === "A") advanceReveal();
      else if (e.key === "t" || e.key === "T") {
        const i = THEME_ORDER.indexOf(themeId);
        setThemeId(THEME_ORDER[(i + 1) % THEME_ORDER.length]);
      }
      else if ((e.key === "d" || e.key === "D") && mode === "problems") {
        setDrawing(true);
      }
      else if ((e.key === "p" || e.key === "P") && hasGuide) {
        setPresenterOpen((o) => !o);
      }
      else if (e.key === "f" || e.key === "F") {
        setTimerPickerOpen((o) => !o);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [next, prev, router, themeId, drawing, mode, hasGuide, advanceReveal]);

  // Idle-fade chrome: hide top bar + side controls after 3s of no input,
  // restore on any mouse move or key press.
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

  const switchSession = (next: 1 | 2) => {
    if (next === session) return;
    const url = `/math/intervention/${skillId}/project${next === 2 ? "?session=2" : ""}`;
    router.push(url);
  };

  const item = slide?.kind === "problem" ? slide.item : undefined;
  const chromeFade = controlsVisible ? "opacity-100" : "pointer-events-none opacity-0";

  // Phase chips for jump navigation: consecutive slides sharing a label
  // collapse into one chip (Fluency Sprint · Watch & Learn · … · Show
  // What You Know), mirroring the sheet's section flow.
  const phases = useMemo(() => {
    const out: Array<{ label: string; start: number; count: number }> = [];
    slides.forEach((s, i) => {
      const last = out[out.length - 1];
      if (last && last.label === s.label) last.count += 1;
      else out.push({ label: s.label, start: i, count: 1 });
    });
    return out;
  }, [slides]);
  const revealLabel = (() => {
    if (!slide) return "";
    if (slide.kind === "worked") {
      const steps = workedSolution?.steps.length ?? 0;
      if (reveal === 0) return "Show first step";
      if (reveal < steps) return "Next step";
      if (reveal === steps) return "Show answer";
      return "Hide steps";
    }
    if (slide.kind === "fluency") return reveal ? "Hide answers" : "Show answers";
    return reveal ? "Hide answer" : "Show answer";
  })();

  return (
    <div
      className={`fixed inset-0 z-[100] flex flex-col overflow-hidden ${theme.textClass}`}
      style={{ background: theme.background }}
    >
      {/* Decorative pattern layer (polka, underwater bubbles, chalkboard dust) */}
      {theme.pattern && (
        <div
          aria-hidden
          className="pointer-events-none fixed inset-0"
          style={{ backgroundImage: theme.pattern, backgroundRepeat: "repeat" }}
        />
      )}

      {/* Top bar — segmented pill controls. Fades on idle. */}
      <div
        className={`relative z-20 flex items-center gap-3 px-6 py-4 transition-opacity duration-500 ${chromeFade}`}
      >
        <div className="min-w-0 flex-1">
          <h1 className={`truncate text-base font-bold ${theme.isDark ? "text-white" : "text-pnp-navy"}`}>
            {skillName}
          </h1>
          <p className="text-xs opacity-70">{standardCode}</p>
        </div>

        {/* Pill: Session toggle */}
        <SegmentedPill theme={theme}>
          {[1, 2].map((n) => (
            <PillButton
              key={n}
              active={session === n}
              onClick={() => switchSession(n as 1 | 2)}
              theme={theme}
            >
              Session {n}
            </PillButton>
          ))}
        </SegmentedPill>

        {/* Pill: Mode toggle */}
        <SegmentedPill theme={theme}>
          <PillButton
            active={mode === "problems"}
            disabled={slides.length === 0}
            onClick={() => setMode("problems")}
            theme={theme}
          >
            Session
          </PillButton>
          <PillButton
            active={mode === "activity"}
            disabled={!hasActivity}
            onClick={() => setMode("activity")}
            theme={theme}
          >
            Activity
          </PillButton>
        </SegmentedPill>

        {/* Theme picker — popover lists all 5 themes by name */}
        <ThemePicker theme={theme} themeId={themeId} setThemeId={setThemeId} />

        {/* Teacher guide (presenter panel) toggle */}
        {hasGuide && (
          <button
            onClick={() => setPresenterOpen((o) => !o)}
            title="Teacher guide: modeling script, watch-fors, answer preview (P)"
            aria-pressed={presenterOpen}
            className={`rounded-full border px-4 py-1.5 text-xs font-semibold backdrop-blur-sm transition-colors hover:opacity-80 ${
              presenterOpen
                ? "border-pnp-accent bg-pnp-accent text-white"
                : `${theme.isDark ? "border-white/15 bg-black/30 text-white" : "border-pnp-gray-200 bg-white/85 text-pnp-navy"}`
            }`}
          >
            Guide
          </button>
        )}

        {/* Fluency timer */}
        <div className="relative">
          <button
            onClick={() => setTimerPickerOpen((o) => !o)}
            title="Countdown timer for timed fluency sprints (F)"
            aria-expanded={timerPickerOpen}
            className={`rounded-full border px-4 py-1.5 text-xs font-semibold backdrop-blur-sm transition-colors hover:opacity-80 ${
              timerLeft !== null
                ? "border-pnp-yellow bg-pnp-yellow text-pnp-navy"
                : `${theme.isDark ? "border-white/15 bg-black/30 text-white" : "border-pnp-gray-200 bg-white/85 text-pnp-navy"}`
            }`}
          >
            Timer
          </button>
          {timerPickerOpen && (
            <div
              className={`absolute right-0 top-full z-50 mt-2 flex gap-1 rounded-xl border p-2 shadow-2xl backdrop-blur-md ${
                theme.isDark ? "border-white/15 bg-pnp-navy/95" : "border-pnp-gray-200 bg-white"
              }`}
            >
              {[1, 2, 3, 5].map((m) => (
                <button
                  key={m}
                  onClick={() => startTimer(m)}
                  className={`rounded-lg px-3 py-2 text-sm font-bold transition-colors ${
                    theme.isDark
                      ? "text-white hover:bg-white/15"
                      : "text-pnp-navy hover:bg-pnp-gray-100"
                  }`}
                >
                  {m} min
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Whiteboard draw toggle — only in problems mode (Activity uses
            drag-and-drop, which would conflict with a draw overlay). */}
        {mode === "problems" && (
          <button
            onClick={() => setDrawing((d) => !d)}
            title="Draw on the projection (D)"
            aria-pressed={drawing}
            className={`rounded-full border px-4 py-1.5 text-xs font-semibold backdrop-blur-sm transition-colors hover:opacity-80 ${
              drawing
                ? "border-pnp-yellow bg-pnp-yellow text-pnp-navy"
                : `${theme.isDark ? "border-white/15 bg-black/30 text-white" : "border-pnp-gray-200 bg-white/85 text-pnp-navy"}`
            }`}
          >
            {drawing ? "Drawing…" : "Draw"}
          </button>
        )}

        <GroupsButton
          isDark={theme.isDark}
          className={`inline-flex items-center gap-1.5 rounded-full border px-4 py-1.5 text-xs font-semibold backdrop-blur-sm transition-colors hover:opacity-80 ${theme.isDark ? "border-white/15 bg-black/30 text-white" : "border-pnp-gray-200 bg-white/85 text-pnp-navy"}`}
        />

        <button
          onClick={() => router.back()}
          className={`rounded-full border ${theme.isDark ? "border-white/15 bg-black/30" : "border-pnp-gray-200 bg-white/85"} px-4 py-1.5 text-xs font-semibold backdrop-blur-sm transition-colors hover:opacity-80 ${theme.isDark ? "text-white" : "text-pnp-navy"}`}
          title="Press Esc to exit"
        >
          Exit
        </button>
      </div>

      {/* Stage */}
      <div
        className={`relative z-10 flex flex-1 justify-center overflow-hidden pb-10 ${
          mode === "activity" ? "items-stretch px-3" : "items-center px-6"
        }`}
      >
        {mode === "problems" && slide?.kind === "fluency" && fluency && (
          <FluencyStage
            fluency={fluency}
            revealed={reveal > 0}
            onReveal={advanceReveal}
            revealLabel={revealLabel}
            theme={theme}
          />
        )}
        {mode === "problems" && slide?.kind === "worked" && workedSolution && (
          <WorkedStage
            ws={workedSolution}
            modelVisual={
              teacherGuide?.worked_example_script?.find((s) => s.visual)?.visual ?? null
            }
            reveal={reveal}
            onReveal={advanceReveal}
            revealLabel={revealLabel}
            theme={theme}
          />
        )}
        {mode === "problems" && slide?.kind === "faded" && fadedExample && (
          <FadedStage
            fe={fadedExample}
            revealed={reveal > 0}
            onReveal={advanceReveal}
            revealLabel={revealLabel}
            theme={theme}
          />
        )}
        {mode === "problems" && slide?.kind === "problem" && item && (
          <ProblemsStage
            item={item}
            revealed={reveal > 0}
            onReveal={advanceReveal}
            revealLabel={revealLabel}
            starters={
              item.section === "Let's Try Together" ? sentenceStarters ?? undefined : undefined
            }
            theme={theme}
          />
        )}
        {mode === "problems" && !slide && (
          <div className="text-center text-lg opacity-60">
            No problems available for this session.
          </div>
        )}
        {mode === "activity" && hasActivity && artifact && (
          <SortCardsStage
            shuffleSeed={skillId}
            kind={artifact.kind === "picture_sort" ? "picture_sort" : "sort_cards"}
            categories={artifact.categories ?? []}
            cards={artifact.items ?? []}
            instructions={artifact.instructions}
            title={artifact.title}
            theme={theme}
          />
        )}
        {mode === "activity" && !hasActivity && (
          <div className="text-center text-lg opacity-60">
            This skill doesn&apos;t have a digital activity yet.
          </div>
        )}
      </div>

      {/* Bottom nav cluster — phase chips (click to jump) between Prev and
          Next, mirroring the printed sheet's section flow. Fades on idle. */}
      {mode === "problems" && slides.length > 0 && (
        <div
          className={`relative z-20 flex flex-col items-center gap-3 px-6 py-5 transition-opacity duration-500 ${chromeFade}`}
        >
          {/* Phase strip — the session roadmap. Current phase is filled. */}
          <div className="flex max-w-full flex-wrap items-center justify-center gap-1.5">
            {phases.map((ph) => {
              const active = slide?.label === ph.label
                && idx >= ph.start && idx < ph.start + ph.count;
              const badge = badgeFor(ph.label);
              return (
                <button
                  key={`${ph.label}-${ph.start}`}
                  onClick={() => setIdx(ph.start)}
                  title={`Jump to ${ph.label}`}
                  className={`rounded-full px-3 py-1 text-xs font-bold backdrop-blur-sm transition-all ${
                    active ? "scale-105 shadow-md" : "opacity-55 hover:opacity-90"
                  }`}
                  style={{ backgroundColor: badge.bg, color: badge.fg }}
                >
                  {ph.label}
                  {ph.count > 1 && active && slide?.kind === "problem" && (
                    <span className="ml-1 opacity-70">
                      {idx - ph.start + 1}/{ph.count}
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          <div className="flex items-center justify-center gap-6">
            <button
              onClick={prev}
              disabled={idx === 0}
              className={`flex h-12 items-center gap-2 rounded-full border-2 ${theme.isDark ? "border-white/20 bg-black/40 text-white" : "border-pnp-gray-300 bg-white/90 text-pnp-navy"} px-6 text-base font-bold shadow-lg backdrop-blur-sm transition-all hover:scale-105 hover:opacity-95 disabled:opacity-25 disabled:hover:scale-100`}
            >
              <span className="text-xl">◀</span> Prev
            </button>

            <div className={`flex items-center gap-2 rounded-full ${theme.isDark ? "bg-black/40 text-white" : "bg-white/90 text-pnp-navy"} px-4 py-2.5 text-sm font-semibold shadow-md backdrop-blur-sm`}>
              <span className="font-bold">{idx + 1}</span>
              <span className="opacity-70">of {slides.length}</span>
            </div>

            <button
              onClick={next}
              disabled={idx >= slides.length - 1}
              className={`flex h-12 items-center gap-2 rounded-full border-2 ${theme.isDark ? "border-white/20 bg-black/40 text-white" : "border-pnp-gray-300 bg-white/90 text-pnp-navy"} px-6 text-base font-bold shadow-lg backdrop-blur-sm transition-all hover:scale-105 hover:opacity-95 disabled:opacity-25 disabled:hover:scale-100`}
            >
              Next <span className="text-xl">▶</span>
            </button>
          </div>
        </div>
      )}

      {/* Whiteboard overlay — always mounted so existing strokes stay
          visible if the teacher toggles Drawing off and back on within
          the same problem. wipeKey changes whenever we navigate, which
          clears strokes (fresh problem = fresh whiteboard). */}
      {mode === "problems" && (
        <DrawingOverlay
          active={drawing}
          setActive={setDrawing}
          wipeKey={`${idx}-${session}-${mode}`}
        />
      )}

      {/* Running countdown — big enough to read from the back of the room. */}
      {timerLeft !== null && (
        <div
          className={`fixed bottom-6 left-6 z-[240] flex items-center gap-3 rounded-2xl border-2 px-5 py-3 shadow-2xl backdrop-blur-md ${
            timerLeft === 0
              ? "border-pnp-red bg-pnp-red text-white"
              : theme.isDark
                ? "border-white/20 bg-black/60 text-white"
                : "border-pnp-gray-200 bg-white/95 text-pnp-navy"
          }`}
        >
          <span className="font-mono text-4xl font-bold tabular-nums">
            {timerLeft === 0
              ? "Time!"
              : `${Math.floor(timerLeft / 60)}:${String(timerLeft % 60).padStart(2, "0")}`}
          </span>
          {timerLeft > 0 && (
            <button
              onClick={() => setTimerRunning((r) => !r)}
              className="rounded-lg px-2 py-1 text-xs font-semibold opacity-70 hover:opacity-100"
            >
              {timerRunning ? "Pause" : "Resume"}
            </button>
          )}
          <button
            onClick={() => { setTimerRunning(false); setTimerLeft(null); }}
            aria-label="Dismiss timer"
            className="rounded-lg px-2 py-1 text-xs font-semibold opacity-70 hover:opacity-100"
          >
            ✕
          </button>
        </div>
      )}

      {/* Teacher presenter panel — corner card with the lesson script and
          answer preview. Deliberately small, dimmed chrome: fine for
          students to glimpse, aimed at the teacher at the front. */}
      {presenterOpen && hasGuide && teacherGuide && (
        <PresenterPanel
          guide={teacherGuide}
          item={mode === "problems" ? item : undefined}
          slideKind={mode === "problems" ? slide?.kind : undefined}
          answerPreview={
            mode !== "problems" || !slide ? undefined
            : slide.kind === "worked" ? workedSolution?.answer
            : slide.kind === "faded" ? fadedExample?.answer
            : slide.kind === "problem" ? slide.item.answer
            : undefined
          }
          onClose={() => setPresenterOpen(false)}
        />
      )}
    </div>
  );
}

// ───────────────────────────────────────────────────────────────
// Presenter panel — teacher-only cues in a corner card.
// ───────────────────────────────────────────────────────────────

const SCRIPT_KIND_STYLE: Record<string, string> = {
  say:   "bg-blue-500/20 text-blue-200",
  ask:   "bg-emerald-500/20 text-emerald-200",
  show:  "bg-yellow-500/20 text-yellow-100",
  watch: "bg-red-500/25 text-red-200",
};

function PresenterPanel({
  guide,
  item,
  slideKind,
  answerPreview,
  onClose,
}: {
  guide: TeacherGuide;
  item?: ProjItem;
  slideKind?: Slide["kind"];
  answerPreview?: string;
  onClose: () => void;
}) {
  const isWorkedExample = slideKind === "worked" || item?.section === "Worked Example";
  const script = guide.worked_example_script ?? [];

  return (
    <aside
      aria-label="Teacher guide"
      className="fixed bottom-6 right-6 z-[240] flex max-h-[55vh] w-[24rem] max-w-[calc(100vw-3rem)] flex-col overflow-hidden rounded-2xl border border-white/15 bg-pnp-navy/95 text-white shadow-2xl backdrop-blur-md"
    >
      <div className="flex items-center justify-between border-b border-white/10 px-4 py-2.5">
        <span className="text-xs font-bold uppercase tracking-widest text-white/60">
          Teacher guide
        </span>
        <button
          onClick={onClose}
          aria-label="Close teacher guide"
          className="rounded px-1.5 text-white/60 hover:text-white"
        >
          ✕
        </button>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto px-4 py-3 text-[13px] leading-relaxed">
        {/* Answer preview for the current slide — lets the teacher see it
            without projecting the reveal. */}
        {answerPreview && (
          <p className="rounded-lg bg-emerald-500/15 px-3 py-2 font-semibold text-emerald-200">
            Answer: {answerPreview}
          </p>
        )}

        {isWorkedExample ? (
          <>
            {guide.i_do_script && (
              <p className="italic text-white/70">{guide.i_do_script}</p>
            )}
            {script.length > 0 && (
              <ol className="space-y-2">
                {script.map((s, i) => (
                  <li key={i} className="flex gap-2">
                    <span
                      className={`mt-0.5 h-fit flex-shrink-0 rounded px-1.5 py-0.5 text-[10px] font-bold uppercase ${
                        SCRIPT_KIND_STYLE[s.kind?.toLowerCase()] ?? "bg-white/10 text-white/70"
                      }`}
                    >
                      {s.kind}
                    </span>
                    <span className="min-w-0 text-white/90">
                      {s.text}
                      {s.visual && (
                        <span className="mt-1.5 block rounded-lg bg-white/10 p-2 [&_svg]:h-auto [&_svg]:max-w-full">
                          <InlineDiagram data={s.visual} />
                        </span>
                      )}
                    </span>
                  </li>
                ))}
              </ol>
            )}
          </>
        ) : (
          <>
            {guide.canonical_error && (
              <div>
                <p className="mb-1 text-[10px] font-bold uppercase tracking-widest text-red-300">
                  Watch for
                </p>
                <p className="text-white/90">{guide.canonical_error.pattern}</p>
                <p className="mt-1 text-white/60">e.g. {guide.canonical_error.example}</p>
              </div>
            )}
            {guide.redirect_script && (
              <div className="space-y-1.5">
                <p className="text-[10px] font-bold uppercase tracking-widest text-white/50">
                  If it happens
                </p>
                <p><span className="font-bold text-red-300">Stop: </span>{guide.redirect_script.stop}</p>
                <p><span className="font-bold text-blue-300">Prompt: </span>{guide.redirect_script.prompt}</p>
                <p><span className="font-bold text-emerald-300">Praise: </span>{guide.redirect_script.praise}</p>
              </div>
            )}
          </>
        )}

        {guide.sentence_starters && guide.sentence_starters.length > 0 && (
          <div>
            <p className="mb-1 text-[10px] font-bold uppercase tracking-widest text-white/50">
              Sentence starters
            </p>
            <ul className="list-inside list-disc space-y-1 text-white/80">
              {guide.sentence_starters.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </aside>
  );
}

// ───────────────────────────────────────────────────────────────
// Segmented pill primitives — used for Session + Mode toggles.
// ───────────────────────────────────────────────────────────────

function SegmentedPill({
  children,
  theme,
}: {
  children: React.ReactNode;
  theme: ThemeConfig;
}) {
  return (
    <div
      className={`flex items-center rounded-full border ${theme.isDark ? "border-white/15 bg-black/30" : "border-pnp-gray-200 bg-white/85"} p-1 backdrop-blur-sm`}
    >
      {children}
    </div>
  );
}

// Theme picker popover — click to expand, lists all 5 themes by name.
function ThemePicker({
  theme,
  themeId,
  setThemeId,
}: {
  theme: ThemeConfig;
  themeId: ThemeId;
  setThemeId: (id: ThemeId) => void;
}) {
  const [open, setOpen] = useState(false);

  // Close popover on outside click. Captures the click on document so
  // clicks anywhere outside the picker collapse it.
  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest?.("[data-theme-picker]")) setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [open]);

  const buttonBase = `rounded-full border ${
    theme.isDark ? "border-white/15 bg-black/30 text-white" : "border-pnp-gray-200 bg-white/85 text-pnp-navy"
  } px-4 py-1.5 text-xs font-semibold backdrop-blur-sm transition-colors hover:opacity-80`;

  return (
    <div className="relative" data-theme-picker>
      <button
        onClick={() => setOpen((o) => !o)}
        title="Press T to cycle, click to pick"
        className={`flex items-center gap-1.5 ${buttonBase}`}
      >
        Theme: {theme.label}
        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" className={open ? "rotate-180 transition-transform" : "transition-transform"}>
          <path d="M6 9l6 6 6-6" />
        </svg>
      </button>
      {open && (
        <div
          className={`absolute right-0 top-full z-50 mt-2 min-w-[10rem] overflow-hidden rounded-xl border ${
            theme.isDark ? "border-white/15 bg-pnp-navy/95" : "border-pnp-gray-200 bg-white"
          } py-1 shadow-2xl backdrop-blur-md`}
        >
          {THEME_ORDER.map((id) => {
            const t = PROJECTION_THEMES[id];
            const isActive = id === themeId;
            return (
              <button
                key={id}
                onClick={() => { setThemeId(id); setOpen(false); }}
                className={`flex w-full items-center gap-3 px-4 py-2 text-left text-sm font-semibold transition-colors ${
                  isActive
                    ? theme.isDark ? "bg-white/15 text-white" : "bg-pnp-gray-100 text-pnp-navy"
                    : theme.isDark ? "text-white/85 hover:bg-white/10" : "text-pnp-gray-700 hover:bg-pnp-gray-50"
                }`}
              >
                {/* Mini swatch — quick visual preview of the theme */}
                <span
                  className="h-5 w-5 flex-shrink-0 rounded-full border border-black/15"
                  style={{ background: t.background }}
                />
                {t.label}
                {isActive && <span className="ml-auto text-xs opacity-60">●</span>}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

function PillButton({
  children,
  active,
  disabled,
  onClick,
  theme,
}: {
  children: React.ReactNode;
  active?: boolean;
  disabled?: boolean;
  onClick?: () => void;
  theme: ThemeConfig;
}) {
  // Active state: fill with the theme's accent contrast (navy on light themes,
  // accent color on dark themes). We keep this simple — always navy bg/white
  // text on light themes, accent bg on dark themes.
  const activeClass = theme.isDark
    ? "bg-white/90 text-pnp-navy shadow"
    : "bg-pnp-navy text-white shadow";
  const idleClass = theme.isDark
    ? "text-white/75 hover:text-white"
    : "text-pnp-gray-600 hover:text-pnp-navy";
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`rounded-full px-4 py-1 text-xs font-semibold transition-colors disabled:opacity-40 ${
        active ? activeClass : idleClass
      }`}
    >
      {children}
    </button>
  );
}

// ───────────────────────────────────────────────────────────────
// Problems stage — single problem in a big rounded card.
// ───────────────────────────────────────────────────────────────

function ProblemsStage({
  item,
  revealed,
  onReveal,
  revealLabel,
  starters,
  theme,
}: {
  item: ProjItem;
  revealed: boolean;
  onReveal: () => void;
  revealLabel: string;
  starters?: string[];
  theme: ThemeConfig;
}) {
  return (
    <div className="flex h-full w-full max-w-6xl flex-col items-center justify-center">
      {/* Big rounded "bubble" content card */}
      <div
        className={`w-full rounded-[2rem] border-4 ${theme.bubbleBorder} ${theme.bubbleBg} ${theme.bubbleText} px-12 py-14 shadow-xl backdrop-blur-sm`}
      >
        {/* Stem — MathText handles a/b → stacked fraction. */}
        <p className="text-center text-[clamp(1.6rem,3.5vw,3rem)] font-bold leading-tight">
          <MathText text={item.stem} />
        </p>

        {/* Error-analysis: the flawed student work, projected big so the
            class can hunt the mistake together. */}
        {item.type === "error_analysis" && item.shown_work && item.shown_work.length > 0 && (
          <div className="mx-auto mt-8 w-fit rounded-2xl border-4 border-red-300/60 bg-red-500/10 px-10 py-6 text-left">
            <p className="mb-2 text-sm font-bold uppercase tracking-widest text-red-400">
              Student work — find the mistake
            </p>
            {item.shown_work.map((line, i) => (
              <p key={i} className="font-mono text-[clamp(1.4rem,3vw,2.4rem)] font-bold leading-snug">
                <MathText text={line} />
              </p>
            ))}
          </div>
        )}

        {/* Stem-level diagram (number line, coordinate grid, SVG figure) */}
        {item.render_data && (
          <div className="mt-8 flex justify-center">
            <InlineDiagram data={item.render_data} />
          </div>
        )}

        {/* Multi-part prompts (Part A / Part B). Each has its own answer
            line that becomes visible only on reveal. */}
        {item.parts && item.parts.length > 0 && (
          <div className="mt-10 space-y-6 text-center">
            {item.parts.map((p, i) => (
              <div key={i}>
                <p className="text-2xl font-bold opacity-90">{p.label}</p>
                <p className="mt-1 text-[clamp(1.2rem,2.5vw,2rem)]">
                  <MathText text={p.prompt} />
                </p>
                {revealed && (
                  <p className="mt-2 inline-block rounded-xl bg-emerald-500/15 px-4 py-2 text-xl font-bold text-emerald-700 ring-2 ring-emerald-400/30">
                    Answer: <MathText text={p.answer} />
                  </p>
                )}
              </div>
            ))}
          </div>
        )}

        {item.choices && item.choices.length > 0 && (
          <div className="mt-12 grid gap-5 sm:grid-cols-2">
            {item.choices.map((c, i) => {
              const labels = ["A", "B", "C", "D", "E", "F"];
              const isCorrect = revealed && c === item.answer;
              const cr = item.choices_render?.[i];
              return (
                <div
                  key={i}
                  className={`flex items-center gap-4 rounded-2xl border-2 px-6 py-5 text-2xl font-semibold transition-all ${
                    isCorrect
                      ? "border-emerald-400 bg-emerald-500/15 ring-4 ring-emerald-400/30"
                      : `${theme.bubbleBorder} ${theme.bubbleBg} opacity-90`
                  }`}
                >
                  <span
                    className={`flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-full text-base font-bold ${
                      isCorrect
                        ? "bg-emerald-500 text-white"
                        : theme.isDark
                          ? "bg-white/10 text-white"
                          : "bg-pnp-gray-100 text-pnp-gray-600"
                    }`}
                  >
                    {labels[i]}
                  </span>
                  {cr ? (
                    <InlineDiagram data={cr} />
                  ) : (
                    <span><MathText text={c} /></span>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {revealed && !item.choices && !item.parts && (
          <p className="mt-12 text-center">
            <span className="inline-block rounded-2xl bg-emerald-500/15 px-8 py-4 text-3xl font-bold text-emerald-300 ring-2 ring-emerald-400/30">
              Answer: <MathText text={item.answer} />
            </span>
          </p>
        )}
      </div>

      {/* Sentence starters strip — printed on the sheet's guided section,
          echoed here so the board matches the paper. */}
      {starters && starters.length > 0 && (
        <div className="mt-6 flex max-w-4xl flex-wrap items-center justify-center gap-2">
          <span className={`text-xs font-bold uppercase tracking-widest ${theme.isDark ? "text-white/50" : "text-pnp-gray-500"}`}>
            Say it like this
          </span>
          {starters.map((s, i) => (
            <span
              key={i}
              className={`rounded-full px-4 py-1.5 text-sm italic ${theme.isDark ? "bg-white/10 text-white/85" : "bg-white/85 text-pnp-gray-700"} backdrop-blur-sm`}
            >
              &ldquo;{s}&rdquo;
            </span>
          ))}
        </div>
      )}

      {/* Reveal toggle floats below the card */}
      <RevealButton onClick={onReveal} label={revealLabel} theme={theme} />
    </div>
  );
}

function RevealButton({
  onClick,
  label,
  theme,
}: {
  onClick: () => void;
  label: string;
  theme: ThemeConfig;
}) {
  return (
    <button
      onClick={onClick}
      className={`mt-6 rounded-full border ${theme.isDark ? "border-white/15 bg-black/30" : "border-pnp-gray-200 bg-white/85"} px-6 py-2.5 text-sm font-semibold backdrop-blur-sm transition-colors hover:opacity-80 ${theme.isDark ? "text-white" : "text-pnp-navy"}`}
      title="Press A"
    >
      {label}
    </button>
  );
}

// ───────────────────────────────────────────────────────────────
// Fluency sprint stage — the timed warm-up grid, mirroring the sheet.
// ───────────────────────────────────────────────────────────────

/** Reshape a wordy stem into drill-card form so nothing wraps awkwardly:
 *  "If w = 7, what is 20 - w?"  →  given "w = 7", expr "20 - w"
 *  "What is 8 x 8?"             →  expr "8 x 8"
 *  Anything unrecognized falls back to the raw stem (kept as prose — no
 *  "=" appended, blank only). */
function fluencyParts(stem: string): { given?: string; expr: string; isExpr: boolean } {
  const s = stem.trim().replace(/\?+$/, "");
  const withGiven = s.match(/^If\s+(.+?),\s+what is\s+(?:the value of\s+)?(.+)$/i);
  if (withGiven) return { given: withGiven[1], expr: withGiven[2], isExpr: true };
  const bare = s.match(/^What is\s+(?:the value of\s+)?(.+)$/i);
  if (bare) return { expr: bare[1], isExpr: true };
  // Pure-math stems (like "|4 - 10|") count as expressions even without
  // a "What is" wrapper; anything containing real words (3+ letter runs)
  // stays prose and gets a blank without an "=".
  const mathOnly =
    /^[0-9a-z|()^+\-*/=. ]+$/i.test(s) && /\d/.test(s) && !/[a-z]{2,}/i.test(s);
  return { expr: s, isExpr: mathOnly };
}

function FluencyStage({
  fluency,
  revealed,
  onReveal,
  revealLabel,
  theme,
}: {
  fluency: FluencyBlock;
  revealed: boolean;
  onReveal: () => void;
  revealLabel: string;
  theme: ThemeConfig;
}) {
  const parsed = fluency.items.map((it) => ({ ...fluencyParts(it.stem), answer: it.answer }));
  const anyGiven = parsed.some((p) => p.given);
  // Column count adapts to how wide the items run so long prose stems
  // never overlap their neighbors.
  const maxLen = Math.max(
    ...parsed.map((p) => p.expr.length + (p.given ? p.given.length + 4 : 0))
  );
  const gridCols =
    maxLen > 22 || anyGiven
      ? "grid-cols-1 lg:grid-cols-2"
      : "grid-cols-2 md:grid-cols-3";

  return (
    <div className="flex h-full w-full max-w-6xl flex-col items-center justify-center">
      <div
        className={`w-full rounded-[2rem] border-4 ${theme.bubbleBorder} ${theme.bubbleBg} ${theme.bubbleText} px-12 py-10 shadow-xl backdrop-blur-sm`}
      >
        <p className="text-center text-lg font-semibold opacity-70">
          Warm-up on facts you already know — beat your best! Start the timer
          <span className="mx-1 rounded bg-black/10 px-1.5 font-mono text-sm">F</span>
          when everyone&rsquo;s ready.
        </p>
        <div className={`mt-8 grid gap-x-10 gap-y-6 ${gridCols}`}>
          {parsed.map((p, i) => (
            <div key={i} className="flex min-w-0 items-baseline gap-3 text-[clamp(1rem,1.8vw,1.6rem)] font-bold">
              <span className="w-7 flex-shrink-0 text-right text-sm font-semibold opacity-50">{i + 1}.</span>
              {p.given && (
                <span className="flex-shrink-0 whitespace-nowrap rounded-lg bg-black/5 px-2 py-0.5 text-[0.7em] font-semibold opacity-70">
                  <MathText text={p.given} />
                </span>
              )}
              <span className="min-w-0">
                <MathText text={p.expr} />
              </span>
              {p.isExpr && <span className="flex-shrink-0 opacity-50">=</span>}
              {revealed ? (
                <span className="flex-shrink-0 whitespace-nowrap font-extrabold text-emerald-500">{p.answer}</span>
              ) : (
                <span className="inline-block w-12 flex-shrink-0 border-b-2 border-current opacity-30" aria-hidden="true" />
              )}
            </div>
          ))}
        </div>
      </div>
      <RevealButton onClick={onReveal} label={revealLabel} theme={theme} />
    </div>
  );
}

// ───────────────────────────────────────────────────────────────
// Worked-example stage — annotated steps revealed one at a time.
// ───────────────────────────────────────────────────────────────

function WorkedStage({
  ws,
  modelVisual,
  reveal,
  onReveal,
  revealLabel,
  theme,
}: {
  ws: WorkedSolution;
  /** Ground model from the worked_example_script (first step with a
   *  `visual`). Projected when the worked solution has no visual of its
   *  own, so the representation the script talks through is actually on
   *  screen for students. */
  modelVisual?: RenderData | null;
  reveal: number;
  onReveal: () => void;
  revealLabel: string;
  theme: ThemeConfig;
}) {
  const steps = ws.steps ?? [];
  const shownSteps = Math.min(reveal, steps.length);
  const showAnswer = reveal > steps.length;
  const stageVisual = ws.render_data ?? modelVisual;

  return (
    <div className="flex h-full w-full max-w-6xl flex-col items-center justify-center">
      <div
        className={`w-full rounded-[2rem] border-4 ${theme.bubbleBorder} ${theme.bubbleBg} ${theme.bubbleText} px-12 py-10 shadow-xl backdrop-blur-sm`}
      >
        <p className="text-center text-[clamp(1.5rem,3vw,2.6rem)] font-bold leading-tight">
          <MathText text={ws.stem} />
        </p>
        {stageVisual && (
          <div className="mt-6 flex justify-center [&_svg]:h-auto [&_svg]:max-h-[36vh] [&_svg]:w-[clamp(320px,52%,560px)]">
            <InlineDiagram data={stageVisual} />
          </div>
        )}
        <div className="mx-auto mt-8 max-w-3xl space-y-4">
          {steps.slice(0, shownSteps).map((step, i) => (
            <div key={i} className="flex items-start gap-4">
              <span className="mt-1 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-blue-500/20 text-base font-bold text-blue-500">
                {i + 1}
              </span>
              <div>
                <p className="text-[clamp(1.2rem,2.4vw,2rem)] font-bold leading-snug">
                  <MathText text={step.math ?? ""} />
                </p>
                {step.annotation && (
                  <p className="mt-0.5 text-base italic opacity-65">{step.annotation}</p>
                )}
              </div>
            </div>
          ))}
          {shownSteps === 0 && (
            <p className="text-center text-lg italic opacity-50">
              Steps appear one at a time — press <span className="rounded bg-black/10 px-1.5 font-mono text-sm not-italic">A</span> or the button below.
            </p>
          )}
        </div>
        {showAnswer && (
          <p className="mt-8 text-center">
            <span className="inline-block rounded-2xl bg-emerald-500/15 px-8 py-3 text-3xl font-bold text-emerald-500 ring-2 ring-emerald-400/30">
              Answer: <MathText text={ws.answer} />
            </span>
          </p>
        )}
      </div>
      <RevealButton onClick={onReveal} label={revealLabel} theme={theme} />
    </div>
  );
}

// ───────────────────────────────────────────────────────────────
// Faded-example stage — given steps shown, blanks for the class to
// supply out loud; reveal shows the final answer.
// ───────────────────────────────────────────────────────────────

function FadedStage({
  fe,
  revealed,
  onReveal,
  revealLabel,
  theme,
}: {
  fe: WorkedSolution;
  revealed: boolean;
  onReveal: () => void;
  revealLabel: string;
  theme: ThemeConfig;
}) {
  const steps = fe.steps ?? [];
  return (
    <div className="flex h-full w-full max-w-6xl flex-col items-center justify-center">
      <div
        className={`w-full rounded-[2rem] border-4 ${theme.bubbleBorder} ${theme.bubbleBg} ${theme.bubbleText} px-12 py-10 shadow-xl backdrop-blur-sm`}
      >
        <p className="text-center text-[clamp(1.5rem,3vw,2.6rem)] font-bold leading-tight">
          <MathText text={fe.stem} />
        </p>
        {fe.render_data && (
          <div className="mt-6 flex justify-center [&_svg]:h-auto [&_svg]:max-h-[36vh] [&_svg]:w-[clamp(320px,52%,560px)]">
            <InlineDiagram data={fe.render_data} />
          </div>
        )}
        <div className="mx-auto mt-8 max-w-3xl space-y-4">
          {steps.map((step, i) => (
            <div key={i} className="flex items-start gap-4">
              <span className="mt-1 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-emerald-500/20 text-base font-bold text-emerald-600">
                {i + 1}
              </span>
              <div className="min-w-0 flex-1">
                {step.given && step.math ? (
                  <p className="text-[clamp(1.2rem,2.4vw,2rem)] font-bold leading-snug">
                    <MathText text={step.math} />
                  </p>
                ) : (
                  <div className="h-9 w-2/3 rounded border-b-4 border-dashed border-current opacity-30" />
                )}
                {step.annotation && (
                  <p className="mt-0.5 text-base italic opacity-65">{step.annotation}</p>
                )}
              </div>
            </div>
          ))}
        </div>
        {revealed && (
          <p className="mt-8 text-center">
            <span className="inline-block rounded-2xl bg-emerald-500/15 px-8 py-3 text-3xl font-bold text-emerald-500 ring-2 ring-emerald-400/30">
              Answer: <MathText text={fe.answer} />
            </span>
          </p>
        )}
      </div>
      <RevealButton onClick={onReveal} label={revealLabel} theme={theme} />
    </div>
  );
}

// ───────────────────────────────────────────────────────────────
// Sort cards activity stage — drag and drop with theme styling.
// ───────────────────────────────────────────────────────────────

interface PlacedCard {
  card: string;
  category: string | null;
}

// Deterministic Fisher-Yates shuffle. Seed = string (e.g. skill_id) so
// the order is stable across reloads but no longer in author order.
function seededShuffle<T>(arr: T[], seed: string): T[] {
  // Hash the seed string to a 32-bit int.
  let h = 2166136261 >>> 0;
  for (let i = 0; i < seed.length; i++) {
    h ^= seed.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  // mulberry32 PRNG.
  const rand = () => {
    h |= 0;
    h = (h + 0x6D2B79F5) | 0;
    let t = Math.imul(h ^ (h >>> 15), 1 | h);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  const out = arr.slice();
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

function SortCardsStage({
  kind,
  categories,
  cards,
  instructions,
  title,
  theme,
  shuffleSeed,
}: {
  kind: "sort_cards" | "picture_sort";
  categories: string[];
  cards: ArtifactItem[];
  instructions?: string;
  title?: string;
  theme: ThemeConfig;
  shuffleSeed: string;
}) {
  // Normalize bare strings into {label} objects so the rest of the stage
  // doesn't have to branch. This is also where we'd thread `answer` through
  // for a future reveal-correct affordance.
  const normalized = useMemo(
    () => cards.map((c) => (typeof c === "string" ? { label: c } : c)),
    [cards]
  );
  // Cards are typically authored grouped by category (sum/more/plus, then
  // difference/less/minus, etc). For the sort activity to be a real task
  // we shuffle them. Seeded so the order is stable across reloads — same
  // skill always gets the same scramble, which keeps "Reset" predictable
  // and avoids cards rearranging mid-session.
  const shuffled = useMemo(
    () => seededShuffle(normalized.map((it) => it.label), shuffleSeed),
    [normalized, shuffleSeed]
  );
  const initial = useMemo<PlacedCard[]>(
    () => shuffled.map((c) => ({ card: c, category: null })),
    [shuffled]
  );
  const [placed, setPlaced] = useState<PlacedCard[]>(initial);
  const [draggingCard, setDraggingCard] = useState<string | null>(null);
  const [hoverCategory, setHoverCategory] = useState<string | null>(null);
  // Correctness check: available when every card carries an authored
  // `answer` (its correct category). Any re-drag clears the marks so the
  // group can fix and re-check.
  const [checked, setChecked] = useState(false);
  const answerByLabel = useMemo(() => {
    const m = new Map<string, string>();
    for (const it of normalized) if (it.answer) m.set(it.label, it.answer);
    return m;
  }, [normalized]);
  const checkable = normalized.length > 0 && normalized.every((it) => !!it.answer);

  const reset = () => { setPlaced(initial); setChecked(false); };
  const allPlaced = placed.every((p) => p.category !== null);
  const correctCount = placed.filter(
    (p) => p.category !== null && p.category === answerByLabel.get(p.card)
  ).length;
  const cardStatus = (card: string, category: string | null): "correct" | "wrong" | null => {
    if (!checked || category === null) return null;
    return category === answerByLabel.get(card) ? "correct" : "wrong";
  };

  const onDragStart = (e: React.DragEvent, card: string) => {
    setDraggingCard(card);
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/plain", card);
  };
  const onDragEnd = () => {
    setDraggingCard(null);
    setHoverCategory(null);
  };
  const onDropTo = (e: React.DragEvent, category: string | null) => {
    e.preventDefault();
    const card = e.dataTransfer.getData("text/plain") || draggingCard;
    if (!card) return;
    setPlaced((cur) =>
      cur.map((p) => (p.card === card ? { ...p, category } : p))
    );
    setChecked(false);
    setHoverCategory(null);
    setDraggingCard(null);
  };
  const onDragOver = (e: React.DragEvent, category: string | null) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    setHoverCategory(category);
  };

  const bank = placed.filter((p) => p.category === null).map((p) => p.card);

  return (
    <div className="flex h-full w-full flex-col">
      {/* Title bar */}
      <div className="mb-4 flex items-end justify-between gap-4 px-2">
        <div className="min-w-0">
          {title && <h2 className="text-2xl font-bold">{title}</h2>}
          {instructions && (
            <p className="text-sm opacity-75">{instructions}</p>
          )}
        </div>
        <div className="flex items-center gap-2 text-sm">
          {checked ? (
            <span
              className={`rounded-full px-3 py-1 font-semibold ring-1 ${
                correctCount === placed.length
                  ? "bg-emerald-500/20 text-emerald-200 ring-emerald-400/40"
                  : "bg-amber-500/20 text-amber-200 ring-amber-400/40"
              }`}
            >
              {correctCount} of {placed.length} correct
              {correctCount < placed.length ? " — fix the red ones and check again" : "!"}
            </span>
          ) : allPlaced ? (
            <span className="rounded-full bg-emerald-500/20 px-3 py-1 font-semibold text-emerald-200 ring-1 ring-emerald-400/40">
              All cards placed
            </span>
          ) : null}
          {checkable && (
            <button
              onClick={() => setChecked(true)}
              disabled={!allPlaced}
              title={allPlaced ? "Mark each card right or wrong" : "Place every card first"}
              className={`rounded-full border px-4 py-1.5 font-semibold backdrop-blur-sm transition-colors disabled:opacity-40 ${
                theme.isDark
                  ? "border-white/15 bg-black/30 text-white hover:opacity-80"
                  : "border-pnp-gray-200 bg-white/85 text-pnp-navy hover:opacity-80"
              }`}
            >
              Check
            </button>
          )}
          <button
            onClick={reset}
            className={`rounded-full border ${theme.isDark ? "border-white/15 bg-black/30" : "border-pnp-gray-200 bg-white/85"} px-4 py-1.5 font-semibold backdrop-blur-sm transition-colors hover:opacity-80 ${theme.isDark ? "text-white" : "text-pnp-navy"}`}
          >
            Reset
          </button>
        </div>
      </div>

      {/* Category drop zones — fill most of the vertical space, big header
          glyphs, generous card padding for projection visibility. */}
      <div
        className="grid flex-1 gap-5"
        style={{ gridTemplateColumns: `repeat(${Math.max(categories.length, 1)}, 1fr)` }}
      >
        {categories.map((cat) => {
          const inThis = placed.filter((p) => p.category === cat).map((p) => p.card);
          const isHover = hoverCategory === cat;
          return (
            <div
              key={cat}
              onDrop={(e) => onDropTo(e, cat)}
              onDragOver={(e) => onDragOver(e, cat)}
              onDragLeave={() => setHoverCategory((h) => (h === cat ? null : h))}
              className={`flex flex-col rounded-3xl border-4 backdrop-blur-sm transition-all ${
                isHover
                  ? `${theme.bubbleBorder} ${theme.bubbleBg} ring-4 ${theme.accentRing}`
                  : `${theme.bubbleBorder} ${theme.bubbleBg} opacity-95`
              }`}
            >
              <div
                className={`border-b-2 ${theme.bubbleBorder} px-4 py-4 text-center text-6xl font-bold ${theme.accentText}`}
              >
                {cat}
              </div>
              <div className="flex flex-1 flex-wrap content-start gap-3 p-5">
                {inThis.map((c) => (
                  <DraggableCard
                    key={c}
                    label={c}
                    onDragStart={(e) => onDragStart(e, c)}
                    onDragEnd={onDragEnd}
                    theme={theme}
                    kind={kind}
                    status={cardStatus(c, cat)}
                  />
                ))}
                {inThis.length === 0 && (
                  <p className="w-full self-center text-center text-base italic opacity-50">
                    Drop cards here
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Bank — unsorted cards. Fixed-ish height so the drop zones stay
          visually dominant. Internal scroll if cards overflow. */}
      <div
        onDrop={(e) => onDropTo(e, null)}
        onDragOver={(e) => onDragOver(e, null)}
        onDragLeave={() => setHoverCategory((h) => (h === null ? null : h))}
        className={`mt-5 flex h-72 flex-shrink-0 flex-wrap content-start gap-3 overflow-y-auto rounded-2xl border-4 ${theme.bubbleBorder} ${theme.bubbleBg} p-4 backdrop-blur-sm transition-all ${
          hoverCategory === null && draggingCard
            ? `ring-4 ${theme.accentRing}`
            : "opacity-95"
        }`}
      >
        {bank.length === 0 ? (
          <p className="w-full self-center text-center text-sm italic opacity-60">
            All cards placed. Drag a card back here to undo.
          </p>
        ) : (
          bank.map((c) => (
            <DraggableCard
              key={c}
              label={c}
              onDragStart={(e) => onDragStart(e, c)}
              onDragEnd={onDragEnd}
              theme={theme}
              kind={kind}
            />
          ))
        )}
      </div>
    </div>
  );
}

function DraggableCard({
  label,
  onDragStart,
  onDragEnd,
  theme,
  kind,
  status = null,
}: {
  label: string;
  onDragStart: (e: React.DragEvent) => void;
  onDragEnd: () => void;
  theme: ThemeConfig;
  kind: "sort_cards" | "picture_sort";
  /** After a Check: green ring for correct placement, red for wrong. */
  status?: "correct" | "wrong" | null;
}) {
  const cardBg = theme.isDark ? "bg-white/90 text-pnp-navy" : "bg-white text-pnp-navy";
  // Picture cards get a larger glyph + more padding so emoji scenes read
  // from the back of the room. Vocabulary cards stay text-2xl.
  const sizing = kind === "picture_sort"
    ? "px-8 py-6 text-4xl"
    : "px-6 py-4 text-2xl";
  const statusRing =
    status === "correct"
      ? "border-emerald-500 ring-4 ring-emerald-400/50"
      : status === "wrong"
        ? "border-red-500 ring-4 ring-red-400/50"
        : "";
  return (
    <div
      draggable
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
      className={`cursor-grab select-none rounded-xl border-2 ${cardBg} font-bold shadow-md transition-shadow active:cursor-grabbing active:shadow-lg ${sizing} ${statusRing}`}
    >
      {label}
    </div>
  );
}
