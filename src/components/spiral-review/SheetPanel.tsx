"use client";

import { useState } from "react";
import {
  getPlds,
  PROFICIENCY_LABELS,
  PROFICIENCY_LEVELS,
  type ProficiencyLevel,
} from "@/lib/standards/plds";
import { getStandardsForGrade } from "@/lib/standards/standards";
import {
  MAX_PROBLEMS,
  MAX_START_WEEK,
  MAX_WEEKS,
  problemCount,
  type GradeSetup,
} from "@/lib/generators/spiral-review";
import Button from "@/components/ui/Button";
import Tag from "@/components/ui/Tag";

/**
 * SheetPanel — "Your sheet": what the next build will contain.
 *
 * One row per picked standard, with its problem count (1 or 2) and its
 * level (At by default) plus that level's PLD, so the teacher sees what
 * the level actually asks for. Below the rows: how many weeks to build and
 * which week number to start at, then the one primary action, Build.
 */

interface Props {
  grade: number;
  setup: GradeSetup;
  onCount: (code: string, count: 1 | 2) => void;
  onLevel: (code: string, level: ProficiencyLevel) => void;
  onRemove: (code: string) => void;
  onWeeks: (weeks: number) => void;
  onStartWeek: (week: number) => void;
  onBuild: () => void;
  building: boolean;
  buildError: string | null;
  /** Present when a review of exactly this sheet is still open in memory. */
  onResume?: () => void;
  onCopyLink: () => void;
  linkState: "idle" | "copied" | "failed";
  restoredNote?: string | null;
  onStartOver?: () => void;
}

function Stepper({
  label,
  value,
  min,
  max,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  onChange: (n: number) => void;
}) {
  const btn =
    "flex h-9 w-9 items-center justify-center rounded-md border-2 border-pnp-gray-200 bg-white text-lg font-bold text-pnp-navy transition-colors hover:border-pnp-accent disabled:cursor-not-allowed disabled:opacity-40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2";
  return (
    <div>
      <span className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
        {label}
      </span>
      <div className="mt-1.5 flex items-center gap-2">
        <button
          type="button"
          className={btn}
          onClick={() => onChange(value - 1)}
          disabled={value <= min}
          aria-label={`Fewer ${label.toLowerCase()}`}
        >
          -
        </button>
        <span
          className="w-8 text-center font-heading text-lg font-extrabold text-pnp-navy"
          aria-live="polite"
        >
          {value}
        </span>
        <button
          type="button"
          className={btn}
          onClick={() => onChange(value + 1)}
          disabled={value >= max}
          aria-label={`More ${label.toLowerCase()}`}
        >
          +
        </button>
      </div>
    </div>
  );
}

/** A number box that lets the teacher clear it while typing. */
function WeekNumberField({
  value,
  onCommit,
}: {
  value: number;
  onCommit: (n: number) => void;
}) {
  const [draft, setDraft] = useState<string | null>(null);
  const commit = () => {
    if (draft === null) return;
    const n = Math.round(Number(draft));
    if (Number.isFinite(n) && draft.trim() !== "") {
      onCommit(Math.min(MAX_START_WEEK, Math.max(1, n)));
    }
    setDraft(null);
  };
  return (
    <label className="block">
      <span className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
        Start at week
      </span>
      <input
        type="number"
        inputMode="numeric"
        min={1}
        max={MAX_START_WEEK}
        value={draft ?? String(value)}
        onChange={(e) => setDraft(e.target.value)}
        onBlur={commit}
        onKeyDown={(e) => {
          if (e.key === "Enter") commit();
        }}
        className="mt-1.5 block h-9 w-24 rounded-md border-2 border-pnp-gray-200 bg-white px-3 font-heading text-lg font-extrabold text-pnp-navy focus-visible:border-pnp-accent focus-visible:outline-none"
      />
    </label>
  );
}

export default function SheetPanel({
  grade,
  setup,
  onCount,
  onLevel,
  onRemove,
  onWeeks,
  onStartWeek,
  onBuild,
  building,
  buildError,
  onResume,
  onCopyLink,
  linkState,
  restoredNote,
  onStartOver,
}: Props) {
  const total = problemCount(setup.picks);
  const textByCode = new Map(getStandardsForGrade(grade).map((s) => [s.code, s.text]));
  const weeks = setup.weeks;

  const buildLabel = building
    ? "Building your sheet..."
    : `Build ${weeks} ${weeks === 1 ? "week" : "weeks"}`;

  // On wide screens the panel is capped to the room on screen (--sheet-max,
  // set by the builder as the page scrolls). The top part (count, weeks,
  // Build) stays put and only the list of standards scrolls, so Build is
  // always in reach however long the list gets.
  return (
    <div className="flex flex-col overflow-clip rounded-xl border-2 border-pnp-navy bg-white shadow-[4px_4px_0_var(--pnp-navy)] lg:max-h-[var(--sheet-max,calc(100vh-136px))]">
      <div data-sheet-pinned className="shrink-0 border-b-2 border-pnp-gray-100 p-5">
        <div className="flex items-baseline justify-between gap-3">
          <h2 className="font-heading text-xl font-extrabold text-pnp-navy">Your sheet</h2>
          <span className="text-sm font-semibold text-pnp-gray-600" aria-live="polite">
            {total} of {MAX_PROBLEMS} problems
          </span>
        </div>
        <div className="mt-2 flex gap-1" aria-hidden="true">
          {Array.from({ length: MAX_PROBLEMS }, (_, i) => (
            <span
              key={i}
              className={`h-2 flex-1 rounded-full ${i < total ? "bg-pnp-accent" : "bg-pnp-gray-200"}`}
            />
          ))}
        </div>

        <div className="mt-4 flex flex-wrap items-end gap-x-6 gap-y-3">
          <Stepper label="Weeks" value={weeks} min={1} max={MAX_WEEKS} onChange={onWeeks} />
          <WeekNumberField value={setup.startWeek} onCommit={onStartWeek} />
        </div>

        {/* Small screens build from the bar pinned to the bottom of the page. */}
        <div className="mt-4 hidden lg:block">
          {buildError && (
            <div
              role="alert"
              className="mb-3 rounded-md border border-pnp-red/30 bg-pnp-red/5 px-3 py-2 text-sm text-pnp-gray-900"
            >
              {buildError}
            </div>
          )}
          <Button
            tier="primary"
            fullWidth
            onClick={onBuild}
            disabled={setup.picks.length === 0 || building}
          >
            {buildLabel}
          </Button>
        </div>
        {onResume && (
          <Button tier="secondary" fullWidth className="mt-3" onClick={onResume}>
            Back to your review
          </Button>
        )}
        <div className="mt-2 flex justify-center">
          <Button
            tier="tertiary"
            size="small"
            onClick={onCopyLink}
            disabled={setup.picks.length === 0}
          >
            {linkState === "copied"
              ? "Link copied"
              : linkState === "failed"
                ? "Could not copy the link"
                : "Copy link to this set"}
          </Button>
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto p-5">
        {restoredNote && (
          <p className="mb-3 text-xs text-pnp-gray-600">
            {restoredNote}{" "}
            {onStartOver && (
              <button
                type="button"
                onClick={onStartOver}
                className="font-semibold text-pnp-accent underline-offset-2 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent"
              >
                Start over
              </button>
            )}
          </p>
        )}
        {setup.picks.length === 0 ? (
          <p className="rounded-md border-2 border-dashed border-pnp-gray-200 px-4 py-6 text-center text-sm leading-relaxed text-pnp-gray-500">
            Pick standards to fill the sheet. Each one adds a problem; set it to 2
            for more practice.
          </p>
        ) : (
          <ul className="space-y-3">
            {setup.picks.map((p) => {
              const pld = getPlds(p.code)?.[p.level];
              const canAddOne = total < MAX_PROBLEMS;
              return (
                <li key={p.code} className="rounded-md border-2 border-pnp-gray-200 p-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <Tag variant="code">{p.code}</Tag>
                      <p className="mt-1.5 text-xs leading-snug text-pnp-gray-600">
                        {textByCode.get(p.code)}
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => onRemove(p.code)}
                      aria-label={`Remove ${p.code}`}
                      className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-md text-pnp-gray-500 transition-colors hover:bg-pnp-gray-100 hover:text-pnp-navy focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
                        <path d="M18 6 6 18M6 6l12 12" />
                      </svg>
                    </button>
                  </div>

                  <div className="mt-2.5 flex flex-wrap items-center gap-x-4 gap-y-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-pnp-gray-600">Problems</span>
                      <div
                        role="radiogroup"
                        aria-label={`Problems for ${p.code}`}
                        className="inline-flex rounded-md border border-pnp-gray-200 bg-white p-0.5"
                      >
                        {([1, 2] as const).map((n) => {
                          const active = p.count === n;
                          const blocked = n === 2 && !active && !canAddOne;
                          return (
                            <button
                              key={n}
                              type="button"
                              role="radio"
                              aria-checked={active}
                              disabled={blocked}
                              title={blocked ? "The sheet is full" : undefined}
                              onClick={() => onCount(p.code, n)}
                              className={`h-7 w-8 rounded text-sm font-bold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent ${
                                active
                                  ? "bg-pnp-accent text-white"
                                  : "text-pnp-gray-700 hover:bg-pnp-gray-100 disabled:cursor-not-allowed disabled:opacity-40"
                              }`}
                            >
                              {n}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                    <label className="flex items-center gap-2 text-xs font-semibold text-pnp-gray-600">
                      Level
                      <select
                        value={p.level}
                        onChange={(e) => onLevel(p.code, e.target.value as ProficiencyLevel)}
                        className="h-8 rounded-md border-2 border-pnp-gray-200 bg-white px-2 text-sm font-semibold text-pnp-navy focus-visible:border-pnp-accent focus-visible:outline-none"
                      >
                        {PROFICIENCY_LEVELS.map((l) => (
                          <option key={l} value={l}>
                            {PROFICIENCY_LABELS[l]}
                          </option>
                        ))}
                      </select>
                    </label>
                  </div>
                  {pld && (
                    <p className="mt-2 line-clamp-2 text-xs leading-snug text-pnp-gray-500" title={pld}>
                      <span className="font-semibold text-pnp-gray-600">
                        {PROFICIENCY_LABELS[p.level]}:
                      </span>{" "}
                      {pld}
                    </p>
                  )}
                </li>
              );
            })}
          </ul>
        )}

        <p className="mt-4 text-xs leading-snug text-pnp-gray-500">
          Same standards every week, new problems each week. Problems from the same
          standard are spaced apart on the page.
        </p>
      </div>
    </div>
  );
}
