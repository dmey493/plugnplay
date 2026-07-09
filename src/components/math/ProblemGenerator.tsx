"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { useSearchParams } from "next/navigation";
import Button from "@/components/ui/Button";
import ReviewPanel from "./ReviewPanel";
import StandardPicker from "./StandardPicker";
import type { LessonNav } from "@/lib/lessons";

type Mode = "exit_ticket" | "mms" | "proficiency" | null;

interface ReviewData {
  format: string;
  standard: string;
  seed: number;
  questions: Array<{
    question_id: string;
    stem_text: string;
    answer_text: string;
    proficiency_level: string;
    difficulty: string;
    item_type: string;
    stem_index: number;
    variant_index: number;
  }>;
  tiers?: Record<string, number[]>;
  mms_axis?: string;
}

const MODES = [
  {
    id: "exit_ticket" as const,
    title: "Exit Ticket",
    description: "Single problem for a quick check",
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M15 5H9a2 2 0 00-2 2v10a2 2 0 002 2h6a2 2 0 002-2V7a2 2 0 00-2-2z" />
        <line x1="9" y1="9" x2="15" y2="9" />
        <line x1="9" y1="13" x2="13" y2="13" />
      </svg>
    ),
  },
  {
    id: "mms" as const,
    title: "Mild / Medium / Spicy",
    description: "Tiered difficulty practice set",
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="18" y1="20" x2="18" y2="10" />
        <line x1="12" y1="20" x2="12" y2="4" />
        <line x1="6" y1="20" x2="6" y2="14" />
      </svg>
    ),
  },
  {
    id: "proficiency" as const,
    title: "Proficiency Set",
    description: "Multiple problems at one level",
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="7" height="7" />
        <rect x="14" y="3" width="7" height="7" />
        <rect x="3" y="14" width="7" height="7" />
        <rect x="14" y="14" width="7" height="7" />
      </svg>
    ),
  },
];

export default function ProblemGenerator({ lessonNav }: { lessonNav: LessonNav }) {
  const searchParams = useSearchParams();

  const [grade, setGrade] = useState<number>(6);
  const [standard, setStandard] = useState<string>("");
  const [mode, setMode] = useState<Mode>(null);

  // Query-param pre-fill so a teacher arriving from a Unit page lands on
  // an already-configured generator:
  //
  //   ?standard=7.NS.1   → pre-selects grade (inferred from the leading
  //                        digit) and the standard.
  //   ?mode=mms          → pre-selects the Mild/Medium/Spicy worksheet
  //                        mode. Also accepts "exit_ticket" and
  //                        "proficiency"; anything else is ignored.
  //
  // First-render only — we don't want to fight the teacher's manual
  // selections after the page is open.
  useEffect(() => {
    const stdParam = searchParams?.get("standard");
    if (stdParam) {
      const m = /^(\d)\./.exec(stdParam);
      if (m) {
        const g = Number(m[1]);
        if (g >= 6 && g <= 8) setGrade(g);
      }
      setStandard(stdParam);
    }
    const modeParam = searchParams?.get("mode");
    if (
      modeParam === "exit_ticket" ||
      modeParam === "mms" ||
      modeParam === "proficiency"
    ) {
      setMode(modeParam);
    }
    // intentionally empty deps — first-render only
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Mode-specific options
  const [exitProficiency, setExitProficiency] = useState("any");
  const [exitDifficulty, setExitDifficulty] = useState("any");
  const [mmsAxis, setMmsAxis] = useState("difficulty");
  const [mmsPerTier, setMmsPerTier] = useState(1);
  const [profLevel, setProfLevel] = useState("at");
  const [profCount, setProfCount] = useState(4);
  const [generating, setGenerating] = useState(false);
  const [reviewData, setReviewData] = useState<ReviewData | null>(null);
  // Inline error banner replaces the old browser alert() calls. Plays
  // in product voice; dismisses on next attempt.
  const [generateError, setGenerateError] = useState<string | null>(null);

  // Scroll the "Next step" panel into view once a standard is picked, so
  // the teacher doesn't have to hunt for it below the standard board. Only
  // fires on a user pick (scrollPending), not on the ?standard= deep-link.
  const nextStepRef = useRef<HTMLDivElement>(null);
  const scrollPending = useRef(false);

  const handleGradeChange = (g: number) => {
    setGrade(g);
    setStandard("");
  };

  const handleStandardChange = (code: string) => {
    setStandard(code);
    scrollPending.current = true;
  };

  useEffect(() => {
    if (standard && scrollPending.current) {
      scrollPending.current = false;
      nextStepRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [standard]);

  const canGenerate = standard !== "" && mode !== null && !generating;

  const buildRequestBody = useCallback(() => {
    const body: Record<string, unknown> = {
      standard,
      format: mode,
    };
    if (mode === "exit_ticket") {
      body.exit_proficiency = exitProficiency;
      body.exit_difficulty = exitDifficulty;
    } else if (mode === "mms") {
      body.mms_axis = mmsAxis;
      body.questions_per_tier = mmsPerTier;
    } else if (mode === "proficiency") {
      body.proficiency_level = profLevel;
      body.prof_count = profCount;
    }
    return body;
  }, [standard, mode, exitProficiency, exitDifficulty, mmsAxis, mmsPerTier, profLevel, profCount]);

  const handleGenerate = async () => {
    if (!canGenerate) return;
    setGenerateError(null);
    setGenerating(true);

    try {
      const body = buildRequestBody();
      const res = await fetch("/api/review-generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        setGenerateError(
          "We couldn't build that set just now. Give it another try — your selections are still here."
        );
        return;
      }

      const data: ReviewData = await res.json();
      setReviewData(data);
    } catch {
      setGenerateError(
        "We couldn't build that set just now. Give it another try — your selections are still here."
      );
    } finally {
      setGenerating(false);
    }
  };

  const handleRegenerate = async () => {
    setReviewData(null);
    setGenerateError(null);
    setGenerating(true);
    try {
      const body = buildRequestBody();
      const res = await fetch("/api/review-generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (res.ok) {
        const data: ReviewData = await res.json();
        setReviewData(data);
      } else {
        setGenerateError(
          "We couldn't rebuild that set. Your selections are still here — try again."
        );
      }
    } catch {
      setGenerateError(
        "We couldn't rebuild that set. Your selections are still here — try again."
      );
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div
      className="rounded-lg bg-white p-6 shadow-sm md:p-8"
      style={{ borderLeft: "4px solid var(--pnp-accent)" }}
    >
      {/* Card heading retained but trimmed — the page banner already
          says "Problem Generator", so the on-card subhead is now a
          quiet step cue rather than a duplicate H2. */}
      {/* Section label only — the previous "Step 1 of 3" eyebrow was
          frozen at 1/3 even though four steps reveal progressively, so
          it was inaccurate and useless. Dropped in favour of a quiet
          "Build a set" cue. */}
      <p className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
        Build a set
      </p>

      {/* Steps 1 & 2: Grade + Standard (by strand or by lesson) */}
      <div className="mt-6">
        <StandardPicker
          grade={grade}
          standard={standard}
          onGradeChange={handleGradeChange}
          onStandardChange={handleStandardChange}
          lessonNav={lessonNav}
        />
      </div>

      {/* Next step — choose a format. Broken into its own bordered panel so
          it clearly reads as the stage AFTER picking a standard, and the
          panel is scrolled into view the moment a standard is selected. */}
      {standard && (
        <div
          key={standard}
          ref={nextStepRef}
          className="pnp-reveal mt-8 scroll-mt-24 rounded-lg border-2 border-pnp-gray-200 bg-pnp-gray-50 p-5 md:p-6"
        >
          <p className="text-xs font-bold uppercase tracking-widest text-pnp-accent">
            Next step · Choose a format
          </p>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            {MODES.map((m) => (
              <button
                key={m.id}
                onClick={() => setMode(m.id)}
                className={`group relative flex flex-col items-center overflow-hidden rounded-lg border-2 p-4 text-center transition-all ${
                  mode === m.id
                    ? "border-pnp-accent bg-pnp-accent text-white"
                    : "border-pnp-gray-200 bg-white text-pnp-navy hover:border-pnp-accent/50"
                }`}
              >
                <div className={`mb-2 ${mode === m.id ? "text-white" : "text-pnp-accent"}`}>
                  {m.icon}
                </div>
                <span className="text-sm font-bold">{m.title}</span>
                <span className={`mt-1 text-xs ${mode === m.id ? "text-white/70" : "text-pnp-gray-500"}`}>
                  {m.description}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Step 4: Mode-specific options */}
      {mode === "exit_ticket" && (
        <div className="mt-6 flex flex-wrap gap-4">
          <div>
            <label className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
              Proficiency
            </label>
            <select
              value={exitProficiency}
              onChange={(e) => setExitProficiency(e.target.value)}
              className="mt-2 block rounded-lg border-2 border-pnp-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-pnp-navy outline-none focus:border-pnp-accent"
            >
              <option value="any">Any</option>
              <option value="below">Below</option>
              <option value="approaching">Approaching</option>
              <option value="at">At</option>
              <option value="above">Above</option>
            </select>
          </div>
          <div>
            <label className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
              Difficulty
            </label>
            <select
              value={exitDifficulty}
              onChange={(e) => setExitDifficulty(e.target.value)}
              className="mt-2 block rounded-lg border-2 border-pnp-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-pnp-navy outline-none focus:border-pnp-accent"
            >
              <option value="any">Any</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="difficult">Difficult</option>
            </select>
          </div>
        </div>
      )}

      {mode === "mms" && (
        <div className="mt-6 flex flex-wrap gap-4">
          <div>
            <label className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
              Tier Axis
            </label>
            <div className="mt-2 flex gap-2">
              {["difficulty", "proficiency"].map((axis) => (
                <button
                  key={axis}
                  onClick={() => setMmsAxis(axis)}
                  className={`rounded-lg border-2 px-4 py-2 text-sm font-semibold capitalize transition-all ${
                    mmsAxis === axis
                      ? "border-pnp-accent bg-pnp-accent text-white"
                      : "border-pnp-gray-200 text-pnp-gray-700 hover:border-pnp-gray-300"
                  }`}
                >
                  {axis}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
              Questions Per Tier
            </label>
            <div className="mt-2 flex gap-2">
              {[1, 2].map((n) => (
                <button
                  key={n}
                  onClick={() => setMmsPerTier(n)}
                  className={`rounded-lg border-2 px-4 py-2 text-sm font-semibold transition-all ${
                    mmsPerTier === n
                      ? "border-pnp-accent bg-pnp-accent text-white"
                      : "border-pnp-gray-200 text-pnp-gray-700 hover:border-pnp-gray-300"
                  }`}
                >
                  {n}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {mode === "proficiency" && (
        <div className="mt-6 flex flex-wrap gap-4">
          <div>
            <label className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
              Proficiency Level
            </label>
            <select
              value={profLevel}
              onChange={(e) => setProfLevel(e.target.value)}
              className="mt-2 block rounded-lg border-2 border-pnp-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-pnp-navy outline-none focus:border-pnp-accent"
            >
              <option value="below">Below</option>
              <option value="approaching">Approaching</option>
              <option value="at">At</option>
              <option value="above">Above</option>
            </select>
          </div>
          <div>
            <label className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
              Number of Questions
            </label>
            <select
              value={profCount}
              onChange={(e) => setProfCount(Number(e.target.value))}
              className="mt-2 block rounded-lg border-2 border-pnp-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-pnp-navy outline-none focus:border-pnp-accent"
            >
              {[2, 3, 4, 5, 6].map((n) => (
                <option key={n} value={n}>{n} questions</option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* Inline error banner — replaces the old alert() popups when a
          generation request fails. Stays in product voice and reassures
          the teacher that their selections are intact. */}
      {generateError && (
        <div
          role="alert"
          className="mt-6 rounded-md border border-pnp-red/30 bg-pnp-red/5 px-4 py-3 text-sm text-pnp-gray-900"
        >
          {generateError}
        </div>
      )}

      {/* Build CTA — labelled "Build my set" to match what actually
          happens (opens a review modal where the teacher can swap and
          reorder before downloading the PDF). The lime/hot-pink magic
          colors were retired in favor of the design-system accent
          (teal-600) via the shared Button component. */}
      <div className="mt-8">
        <Button
          tier="primary"
          onClick={handleGenerate}
          disabled={!canGenerate}
        >
          {generating ? "Building your set…" : "Build my set"}
        </Button>
        {canGenerate && !generating && (
          <p className="mt-2 text-xs text-pnp-gray-500">
            You&rsquo;ll be able to swap and reorder problems before you print.
          </p>
        )}
      </div>

      {/* Review Panel overlay */}
      {reviewData && (
        <ReviewPanel
          reviewData={reviewData}
          requestParams={buildRequestBody()}
          onClose={() => setReviewData(null)}
          onRegenerate={handleRegenerate}
        />
      )}
    </div>
  );
}
