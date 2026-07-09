"use client";

import { useState } from "react";
import { getStandardsByDomain } from "@/lib/standards";
import type { LessonNav } from "@/lib/lessons";
import Button from "@/components/ui/Button";
import Tag from "@/components/ui/Tag";

/**
 * StandardPicker — the shared "pick a standard" control used by both the
 * Problem Generator and the Skill Intervention page.
 *
 * Two lenses on the same set of standards:
 *   - By strand: standards grouped under their domain (AF / NS / GM / DSP),
 *     shown as a scannable board of chips instead of a long dropdown.
 *   - By lesson: the teacher's textbook modules → lessons; picking a lesson
 *     selects the standard that lesson teaches. Easier to find for teachers
 *     who think in lesson numbers ("1-3 Scientific Notation") not codes.
 *
 * Once a standard is chosen the board COLLAPSES to a one-line summary with a
 * "Change" button, so the long list doesn't push the page's next step way
 * down. Re-open with "Change" or by switching grade.
 *
 * Controlled: the parent owns `grade` and `standard`. `isEnabled` lets the
 * intervention page grey out standards that don't have authored skills yet;
 * the generator omits it (every standard is generatable).
 */

const GRADES = [6, 7, 8] as const;

interface Props {
  grade: number;
  standard: string;
  onGradeChange: (grade: number) => void;
  /** `lessonLabel` is passed only when the pick came from the By-lesson
   *  view, so the caller can highlight that specific lesson. */
  onStandardChange: (code: string, lessonLabel?: string) => void;
  lessonNav: LessonNav;
  /** When present, standards for which this returns false are shown disabled. */
  isEnabled?: (code: string) => boolean;
  /** Suffix shown on disabled entries. */
  disabledNote?: string;
}

function Chevron({ open }: { open: boolean }) {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className={`transition-transform duration-150 ${open ? "rotate-180" : ""}`}
    >
      <path d="M6 9l6 6 6-6" />
    </svg>
  );
}

export default function StandardPicker({
  grade,
  standard,
  onGradeChange,
  onStandardChange,
  lessonNav,
  isEnabled,
  disabledNote = "coming soon",
}: Props) {
  const [mode, setMode] = useState<"strand" | "lesson">("strand");
  // Single-open accordion for by-lesson. null = "first module open by
  // default"; a non-matching sentinel = "all collapsed".
  const [openModuleId, setOpenModuleId] = useState<string | null>(null);
  // Board collapses to a summary once a standard is picked; "Change" reopens.
  const [expanded, setExpanded] = useState(false);

  const enabled = (code: string) => (isEnabled ? isEnabled(code) : true);
  const domainGroups = getStandardsByDomain(grade);
  const modules = lessonNav[grade] ?? [];
  const activeOpenId = openModuleId ?? modules[0]?.id ?? null;

  const selectedText = Object.values(domainGroups)
    .flat()
    .find((s) => s.code === standard)?.text;

  const showBoard = expanded || !standard;

  const handleGrade = (g: number) => {
    onGradeChange(g);
    setOpenModuleId(null);
    setExpanded(false);
  };

  // Picking a standard collapses the board so the page's next step rises up.
  const selectStandard = (code: string, lessonLabel?: string) => {
    onStandardChange(code, lessonLabel);
    setExpanded(false);
  };

  return (
    <div>
      {/* Grade — always visible */}
      <div>
        <span className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
          Grade
        </span>
        <div className="mt-2 flex gap-2" role="radiogroup" aria-label="Grade">
          {GRADES.map((g) => {
            const active = grade === g;
            return (
              <button
                key={g}
                type="button"
                role="radio"
                aria-checked={active}
                onClick={() => handleGrade(g)}
                className={`rounded-md border-2 px-5 py-2.5 text-base font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 ${
                  active
                    ? "border-pnp-accent bg-pnp-accent text-white"
                    : "border-pnp-gray-200 bg-white text-pnp-gray-700 hover:border-pnp-gray-400"
                }`}
              >
                {g}th
              </button>
            );
          })}
        </div>
      </div>

      {/* Standard */}
      <div className="mt-6">
        {showBoard ? (
          <>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <span className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
                Standard
              </span>
              <div
                role="tablist"
                aria-label="Choose how to find a standard"
                className="inline-flex items-center gap-1 rounded-lg border border-pnp-gray-200 bg-white p-1"
              >
                {(["strand", "lesson"] as const).map((m) => {
                  const active = mode === m;
                  return (
                    <button
                      key={m}
                      type="button"
                      role="tab"
                      aria-selected={active}
                      onClick={() => setMode(m)}
                      className={`inline-flex h-8 select-none items-center rounded-md px-3 text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 ${
                        active
                          ? "bg-pnp-accent text-white"
                          : "text-pnp-gray-700 hover:bg-pnp-gray-100"
                      }`}
                    >
                      {m === "strand" ? "By strand" : "By lesson"}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="mt-4">
              {mode === "strand" ? (
                <div className="space-y-6">
                  {Object.entries(domainGroups).map(([domainName, standards]) => (
                    <div key={domainName}>
                      <div className="mb-2 flex items-center gap-2">
                        <Tag variant="code">{standards[0]?.domain}</Tag>
                        <h3 className="font-heading text-sm font-extrabold text-pnp-navy">
                          {domainName}
                        </h3>
                      </div>
                      <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
                        {standards.map((s) => {
                          const en = enabled(s.code);
                          const selected = s.code === standard;
                          return (
                            <button
                              key={s.code}
                              type="button"
                              disabled={!en}
                              aria-pressed={selected}
                              onClick={() => en && selectStandard(s.code)}
                              className={`flex flex-col rounded-md border-2 p-3 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 ${
                                selected
                                  ? "border-pnp-accent bg-pnp-accent-soft"
                                  : en
                                    ? "border-pnp-gray-200 bg-white hover:border-pnp-accent"
                                    : "cursor-not-allowed border-pnp-gray-100 bg-pnp-gray-50"
                              }`}
                            >
                              <span
                                className={`font-heading text-sm font-bold ${
                                  en ? "text-pnp-navy" : "text-pnp-gray-400"
                                }`}
                              >
                                {s.code}
                              </span>
                              <span
                                className={`mt-0.5 text-xs leading-snug ${
                                  en ? "text-pnp-gray-600" : "text-pnp-gray-400"
                                }`}
                              >
                                {s.text}
                                {!en ? ` (${disabledNote})` : ""}
                              </span>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              ) : modules.length === 0 ? (
                <p className="rounded-md border-2 border-dashed border-pnp-gray-200 px-4 py-6 text-center text-sm text-pnp-gray-500">
                  No lessons are mapped for this grade yet. Try{" "}
                  <span className="font-semibold">By strand</span>.
                </p>
              ) : (
                <div className="space-y-2">
                  {modules.map((mod) => {
                    const open = activeOpenId === mod.id;
                    return (
                      <div
                        key={mod.id}
                        className="overflow-hidden rounded-md border-2 border-pnp-gray-200"
                      >
                        <button
                          type="button"
                          aria-expanded={open}
                          onClick={() =>
                            setOpenModuleId(open ? "__collapsed__" : mod.id)
                          }
                          className="flex w-full items-center justify-between gap-3 px-4 py-3 text-left transition-colors hover:bg-pnp-gray-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-pnp-accent"
                        >
                          <span className="font-heading text-sm font-extrabold text-pnp-navy">
                            Module {mod.moduleNumber}: {mod.title}
                          </span>
                          <span className="flex flex-shrink-0 items-center gap-2 text-xs font-medium text-pnp-gray-500">
                            {mod.lessons.length} lessons
                            <Chevron open={open} />
                          </span>
                        </button>

                        {open && (
                          <ul className="border-t-2 border-pnp-gray-200">
                            {mod.lessons.map((lesson, i) => {
                              const en = enabled(lesson.standard);
                              const selected = lesson.standard === standard;
                              return (
                                <li
                                  key={`${lesson.label}-${i}`}
                                  className="border-t border-pnp-gray-100 first:border-t-0"
                                >
                                  <button
                                    type="button"
                                    disabled={!en}
                                    aria-pressed={selected}
                                    onClick={() =>
                                      en &&
                                      selectStandard(lesson.standard, lesson.label)
                                    }
                                    className={`flex w-full items-center justify-between gap-3 px-4 py-2.5 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-pnp-accent ${
                                      selected
                                        ? "bg-pnp-accent-soft"
                                        : en
                                          ? "hover:bg-pnp-gray-50"
                                          : "cursor-not-allowed"
                                    }`}
                                  >
                                    <span
                                      className={`text-sm ${
                                        en
                                          ? "font-medium text-pnp-navy"
                                          : "text-pnp-gray-400"
                                      }`}
                                    >
                                      {lesson.label}
                                    </span>
                                    <span className="flex flex-shrink-0 items-center gap-2">
                                      {!en && (
                                        <span className="text-xs text-pnp-gray-400">
                                          {disabledNote}
                                        </span>
                                      )}
                                      <Tag variant="code">{lesson.standard}</Tag>
                                    </span>
                                  </button>
                                </li>
                              );
                            })}
                          </ul>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </>
        ) : (
          // Collapsed summary — keeps the chosen standard visible without the
          // full board taking up the screen.
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-md border-2 border-pnp-accent bg-pnp-accent-soft px-4 py-3">
            <div className="min-w-0">
              <span className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
                Standard
              </span>
              <div className="mt-1 flex flex-wrap items-center gap-2">
                <Tag variant="code">{standard}</Tag>
                {selectedText && (
                  <span className="text-sm font-medium text-pnp-navy">
                    {selectedText}
                  </span>
                )}
              </div>
            </div>
            <Button
              tier="secondary"
              size="small"
              onClick={() => setExpanded(true)}
            >
              Change
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
