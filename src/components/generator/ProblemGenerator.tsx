"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { useSearchParams } from "next/navigation";
import Button from "@/components/ui/Button";
import ReviewPanel from "./ReviewPanel";
import StandardPicker from "@/components/standards/StandardPicker";
import Badge, { type BadgeTone } from "@/components/ui/Badge";
import {
  formatRevised,
  getPlds,
  PROFICIENCY_LABELS,
  PROFICIENCY_LEVELS,
  type ProficiencyLevel,
} from "@/lib/standards/plds";
import {
  findStems,
  getStemsByLevel,
  type StemsByLevel,
} from "@/lib/generators/stem-picker";
import type { LessonNav } from "@/lib/library/lessons";
import type { CheckpointNav } from "@/lib/standards/checkpoints";

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

// Same level-to-tone pairing the review panel uses on generated questions,
// so a level reads the same colour wherever a teacher meets it.
const PLD_TONE: Record<ProficiencyLevel, BadgeTone> = {
  below: "red",
  approaching: "yellow",
  at: "emerald",
  above: "blue",
};

const NO_STEMS: StemsByLevel = {
  below: [],
  approaching: [],
  at: [],
  above: [],
};

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

export default function ProblemGenerator({
  lessonNav,
  checkpointNav,
}: {
  lessonNav: LessonNav;
  checkpointNav?: CheckpointNav;
}) {
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
  // Difficulty is a display-only label on generated problems, not a teacher
  // input: forcing a difficulty a proficiency level doesn't offer (e.g. Below +
  // Difficult on 7.NS.1) produced mismatched questions and confused the axis
  // with proficiency. Exit tickets always request "any" difficulty, and the
  // Mild/Medium/Spicy set always tiers by proficiency.
  const [exitDifficulty] = useState("any");
  const [mmsAxis] = useState("proficiency");
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
    setSelectedStems([]);
  };

  const handleStandardChange = (code: string) => {
    setStandard(code);
    // Stem indices are per standard, so carrying a selection across would
    // filter the new standard's questions by an unrelated stem number.
    setSelectedStems([]);
    scrollPending.current = true;
  };

  useEffect(() => {
    if (standard && scrollPending.current) {
      scrollPending.current = false;
      nextStepRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [standard]);

  const canGenerate = standard !== "" && mode !== null && !generating;

  // The assessment's own words for what each level demands. Shown under the
  // standard so the format choice is made against the level's actual demand,
  // not just its name. Null for 6.NS.2, which has no item specification in
  // the repo; that standard simply shows no descriptors.
  const plds = standard ? getPlds(standard) : null;
  const pldRevised = formatRevised(plds?.revised);

  // The stems behind each level, and what the teacher has opened and picked.
  // Picking a stem is what makes "practise this one thing" possible: the
  // engine then draws only from that stem instead of the whole level.
  const stemsByLevel = standard ? getStemsByLevel(standard) : NO_STEMS;
  const [selectedStems, setSelectedStems] = useState<number[]>([]);
  const pickedStems = standard ? findStems(standard, selectedStems) : [];

  const toggleStem = (index: number) =>
    setSelectedStems((prev) =>
      prev.includes(index) ? prev.filter((i) => i !== index) : [...prev, index]
    );

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
    // Chosen stems supersede the level dropdown on the engine side: a stem
    // already sits at one level, so filtering by both would only ever narrow
    // to the same pool or to nothing. Not sent for Mild/Medium/Spicy, which
    // has to span levels to build its tiers.
    if (mode !== "mms" && selectedStems.length > 0) {
      body.stems = selectedStems;
    }
    return body;
  }, [standard, mode, exitProficiency, exitDifficulty, mmsAxis, mmsPerTier, profLevel, profCount, selectedStems]);

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
          checkpointNav={checkpointNav}
        />
      </div>

      {/* Everything downstream of picking a standard. The scroll target sits
          on the wrapper so the proficiency descriptors land in view first and
          the format panel follows, rather than the teacher scrolling past
          them. */}
      {standard && (
        <div key={standard} ref={nextStepRef} className="scroll-mt-24">
          {/* What the assessment asks for at each level. Sits between the
              standard and the format choice because it is context for that
              choice: a teacher picking Proficiency Set should see what "At" means
              for this standard before picking it. */}
          {plds && (
            <div className="pnp-reveal mt-8 rounded-lg border-2 border-pnp-gray-200 bg-white p-5 md:p-6">
              <p className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
                What ILEARN asks for at each level
              </p>
              {/* IDOE is rewriting these on a rolling basis and the rewrites
                  change what a level asks for, so the date earns its place on
                  the page rather than sitting in the build. */}
              {pldRevised && (
                <p className="mt-1 text-xs text-pnp-gray-500">
                  Indiana revised this standard&rsquo;s descriptors on {pldRevised}.
                </p>
              )}
              {/* Four columns so the levels can be read across as a ladder:
                  what changes from Below to Above is the point, and that only
                  shows when they sit side by side. Scrolls inside its own box
                  on narrow screens rather than squeezing the columns. */}
              <div className="mt-4 overflow-x-auto">
                <table className="w-full min-w-[46rem] table-fixed border-collapse">
                  <thead>
                    <tr>
                      {PROFICIENCY_LEVELS.map((level) => (
                        <th
                          key={level}
                          className="border-b-2 border-pnp-gray-200 px-4 pb-2 text-left align-bottom first:pl-0 last:pr-0"
                        >
                          <Badge tone={PLD_TONE[level]}>
                            {PROFICIENCY_LABELS[level]}
                          </Badge>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      {PROFICIENCY_LEVELS.map((level) => (
                        <td
                          key={level}
                          className="px-4 pt-3 align-top text-sm font-normal leading-relaxed text-pnp-gray-700 first:pl-0 last:pr-0"
                        >
                          {plds[level] ?? (
                            <span className="text-pnp-gray-400">
                              Not published for this standard.
                            </span>
                          )}
                        </td>
                      ))}
                    </tr>
                    {/* Every level's practices, always visible. A teacher can
                        read the whole ladder at once and click straight to the
                        one they want, with no disclosure step in the way. */}
                    <tr>
                      {PROFICIENCY_LEVELS.map((level) => (
                          <td
                            key={level}
                            className="px-4 pb-1 pt-4 align-top first:pl-0 last:pr-0"
                          >
                            {stemsByLevel[level].length === 0 ? (
                              <p className="text-xs text-pnp-gray-400">
                                No practice available at this level.
                              </p>
                            ) : (
                              <ul className="flex flex-col gap-2">
                                {stemsByLevel[level].map((stem) => {
                                  const picked = selectedStems.includes(stem.index);
                                  return (
                                    <li key={stem.index}>
                                      <button
                                        type="button"
                                        onClick={() => toggleStem(stem.index)}
                                        aria-pressed={picked}
                                        className={`w-full rounded-lg border-2 px-3 py-2 text-left transition-colors ${
                                          picked
                                            ? "border-pnp-accent bg-pnp-accent-soft"
                                            : "border-pnp-gray-200 bg-white hover:border-pnp-accent/50"
                                        }`}
                                      >
                                        <span
                                          className={`block text-sm font-semibold leading-snug ${
                                            picked ? "text-pnp-accent-press" : "text-pnp-navy"
                                          }`}
                                        >
                                          {stem.describes}
                                        </span>
                                        {stem.itemType && (
                                          <span className="mt-0.5 block text-xs text-pnp-gray-500">
                                            {stem.itemType}
                                          </span>
                                        )}
                                      </button>
                                    </li>
                                  );
                                })}
                              </ul>
                            )}
                          </td>
                        ))}
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <div className="pnp-reveal mt-8 rounded-lg border-2 border-pnp-gray-200 bg-pnp-gray-50 p-5 md:p-6">
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
        </div>
      )}

      {/* Step 4: Mode-specific options */}
      {mode === "exit_ticket" && selectedStems.length === 0 && (
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
        </div>
      )}

      {mode === "mms" && (
        <div className="mt-6 flex flex-wrap gap-4">
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
          {selectedStems.length === 0 && (
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
          )}
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

      {/* What the set will be built from. Mild/Medium/Spicy has to span the
          levels to make its tiers, so it says plainly that the choice does not
          apply there rather than silently ignoring it. */}
      {mode !== null && pickedStems.length > 0 && (
        <div className="mt-6 rounded-lg border-2 border-pnp-accent/30 bg-pnp-accent-soft/40 px-4 py-3">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <p className="text-xs font-bold uppercase tracking-widest text-pnp-accent-press">
              {mode === "mms"
                ? "Not used for Mild / Medium / Spicy"
                : `Building from ${pickedStems.length === 1 ? "this practice" : "these practices"}`}
            </p>
            <button
              type="button"
              onClick={() => setSelectedStems([])}
              className="text-xs font-semibold text-pnp-accent underline underline-offset-2 hover:text-pnp-accent-press"
            >
              Clear
            </button>
          </div>
          <ul className="mt-2 flex flex-col gap-1">
            {pickedStems.map((stem) => (
              <li
                key={stem.index}
                className="flex flex-wrap items-baseline gap-2 text-sm text-pnp-navy"
              >
                <Badge tone={PLD_TONE[stem.level]}>
                  {PROFICIENCY_LABELS[stem.level]}
                </Badge>
                <span className="font-medium">{stem.describes}</span>
              </li>
            ))}
          </ul>
          {mode === "mms" && (
            <p className="mt-2 text-xs text-pnp-gray-600">
              A tiered set draws one problem from each level, so it ignores this
              choice. Use Exit Ticket or Proficiency Set to practise just these.
            </p>
          )}
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
