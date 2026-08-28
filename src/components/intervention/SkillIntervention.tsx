"use client";

import { useState, useRef, useEffect } from "react";
import {
  AVAILABLE_STANDARDS,
  COLUMN_META,
  isPacketReady,
  isV2,
  progressionIndex,
  progressionStep,
  PLD_BAND_LABELS,
  PLD_BAND_ORDER,
  type PldBand,
  type Skill,
  type SkillColumn,
  type SkillData,
} from "@/lib/intervention/skills";
import type { LessonNav } from "@/lib/library/lessons";
import type { CheckpointNav } from "@/lib/standards/checkpoints";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import Tag from "@/components/ui/Tag";
import DiagnosticModal from "./DiagnosticModal";
import SkillPacketModal from "./SkillPacketModal";
import StandardPicker from "@/components/standards/StandardPicker";

/**
 * SkillIntervention — the Tier 2 progression view.
 *
 * A standard is presented as a logical learning progression (v2 data):
 * numbered steps flowing through the buckets Looking Back → On Grade →
 * Looking Forward, with Foundation holding the far-below prerequisites.
 *
 * Layout follows what a teacher should read first, not the progression's
 * chronological order: On Grade leads at full width, the two adjacent
 * grades sit side by side under it, and Foundation runs last. Four equal
 * columns made Foundation look like the starting point, which is the
 * wrong emphasis for a grade-level class.
 */

/**
 * One bucket and its skills.
 *
 * `gridClass` controls how the skills lay out inside the card: the
 * full-width buckets run them across the page, the paired ones keep to
 * two. Everything else about a bucket is identical wherever it sits.
 */
function BucketCard({
  col,
  data,
  gridClass,
  highlightedSkillIds,
  lessonActive,
}: {
  col: SkillColumn;
  data: SkillData;
  gridClass: string;
  highlightedSkillIds: Set<string>;
  lessonActive: boolean;
}) {
  const colConfig = data.skill_columns[col];
  if (!colConfig) return null;

  const meta = COLUMN_META[col];
  const colSkills = data.skills.filter((s) => s.column === col);

  // The On Grade column is a ladder, not a list: group it under the
  // proficiency band each skill answers so a teacher can see that the first
  // skills are the standard's least complex entry point, not full mastery.
  const grouped =
    col === "on_grade"
      ? PLD_BAND_ORDER.map((band) => ({
          band,
          skills: colSkills.filter((sk) => sk.pld_band === band),
        })).filter((g) => g.skills.length > 0)
      : null;
  const descriptors = data.pld_descriptors;

  return (
    <Card accent={meta.accent} className="p-4 pt-5">
      <div className="mb-4 border-b border-pnp-gray-100 pb-3">
        <h3 className="font-heading text-base font-extrabold text-pnp-navy">
          {colConfig.label}
        </h3>
        <p className="mt-0.5 text-xs text-pnp-gray-500">{colConfig.description}</p>
      </div>

      {grouped ? (
        <div className="grid gap-5">
          {grouped.map(({ band, skills }) => (
            <div key={band}>
              <div className="mb-2 flex items-baseline gap-2">
                <h4 className="font-heading text-xs font-extrabold uppercase tracking-wide text-pnp-navy">
                  {PLD_BAND_LABELS[band]}
                </h4>
                <span className="text-[11px] text-pnp-gray-500">
                  {skills.length} {skills.length === 1 ? "skill" : "skills"}
                </span>
              </div>
              {descriptors && (
                <p className="mb-2.5 border-l-0 text-[11px] leading-relaxed text-pnp-gray-600">
                  {descriptors[band]}
                </p>
              )}
              <div className={`grid items-start gap-3 ${gridClass}`}>
                {skills.map((skill) => (
                  <SkillCard
                    key={skill.skill_id}
                    skill={skill}
                    data={data}
                    highlighted={highlightedSkillIds.has(skill.skill_id)}
                    dimmed={lessonActive && !highlightedSkillIds.has(skill.skill_id)}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className={`grid items-start gap-3 ${gridClass}`}>
          {colSkills.map((skill) => (
            <SkillCard
              key={skill.skill_id}
              skill={skill}
              data={data}
              highlighted={highlightedSkillIds.has(skill.skill_id)}
              dimmed={lessonActive && !highlightedSkillIds.has(skill.skill_id)}
            />
          ))}
        </div>
      )}

      {colSkills.length === 0 && (
        <p className="py-4 text-center text-xs text-pnp-gray-500">
          No skills in this category
        </p>
      )}
    </Card>
  );
}

/** Light-to-dark ramp: the darker the chip, the higher the band. */
const PLD_BAND_STYLE: Record<PldBand, string> = {
  below: "bg-pnp-gray-100 text-pnp-gray-700",
  approaching: "bg-sky-100 text-sky-800",
  at: "bg-sky-200 text-sky-900",
  above: "bg-pnp-navy text-white",
};

function SkillCard({
  skill,
  data,
  highlighted = false,
  dimmed = false,
}: {
  skill: Skill;
  data: SkillData;
  highlighted?: boolean;
  dimmed?: boolean;
}) {
  const [showModal, setShowModal] = useState(false);

  const ready = isPacketReady(skill);
  const v2 = isV2(data) && !!skill.practice_problems;
  const step = progressionStep(data, skill.skill_id);
  const stepNumber = progressionIndex(data, skill.skill_id);
  const accent = COLUMN_META[skill.column]?.accent;

  // v2 cards lead with the progression rationale; v1 cards keep the old
  // sample-item preview (sample_items[0] is typically the I-Do item).
  const previewItem = skill.sample_items?.[1] ?? skill.sample_items?.[0];

  return (
    <>
      {/* The whole card is the button: one skill, one action — generate its
          worksheet. Activities, the detail page, and projection are off. */}
      <button
        type="button"
        onClick={() => ready && setShowModal(true)}
        disabled={!ready}
        title={
          ready
            ? `Generate the worksheet for ${skill.name}`
            : "Not enough authored items or engine mapping for this skill yet"
        }
        className={`w-full rounded-lg bg-white p-4 text-left transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 ${
          highlighted
            ? "border-2 border-pnp-accent pnp-lesson-flash"
            : "border border-pnp-gray-200"
        } ${dimmed ? "opacity-50" : ""} ${
          ready
            ? "cursor-pointer hover:border-pnp-accent hover:shadow-md"
            : "cursor-not-allowed"
        }`}
      >
        {highlighted && (
          <span className="mb-2 inline-flex items-center rounded-md bg-pnp-accent px-2 py-0.5 text-[11px] font-bold uppercase tracking-wide text-white">
            This lesson
          </span>
        )}
        {/* Spans, not divs/headings: a button may only contain phrasing
            content, so every block here is a span set to flex/block. */}
        <span className="flex items-start gap-3">
          {stepNumber !== null && (
            <span
              className="mt-0.5 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full text-xs font-bold text-white"
              style={{ backgroundColor: accent }}
              aria-label={`Step ${stepNumber}`}
            >
              {stepNumber}
            </span>
          )}
          <span className="min-w-0 flex-1">
            <span className="block font-heading text-sm font-bold leading-snug text-pnp-navy">
              {skill.name}
            </span>

            {/* The band travels with the card, so it still reads correctly
                when a card is seen outside its column (search, lesson
                highlight, projection). */}
            {skill.pld_band && (
              <span
                className={`mt-1.5 inline-block rounded px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide ${PLD_BAND_STYLE[skill.pld_band]}`}
              >
                {PLD_BAND_LABELS[skill.pld_band]}
              </span>
            )}

            {v2 && step ? (
              <span className="mt-1.5 block text-xs leading-relaxed text-pnp-gray-600">
                {step.rationale}
              </span>
            ) : (
              previewItem && (
                <span className="mt-2 block whitespace-pre-wrap break-words rounded bg-pnp-gray-50 px-3 py-2 text-xs italic text-pnp-gray-600">
                  {previewItem.stem}
                </span>
              )
            )}

            <span className="mt-3 flex items-center justify-end gap-1.5 text-xs font-bold text-pnp-navy">
              {ready ? "Generate worksheet" : "Coming soon"}
              {ready && (
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              )}
            </span>
          </span>
        </span>
      </button>

      {showModal && (
        <SkillPacketModal
          skillName={skill.name}
          skillId={skill.skill_id}
          standardCode={data.standard_code}
          hasArtifact={!!skill.printable_artifact}
          artifactTitle={skill.printable_artifact?.title}
          onClose={() => setShowModal(false)}
        />
      )}
    </>
  );
}

/** All textbook lessons (across the grade's modules) that map to a standard.
 *  A standard commonly spans 2–3 lessons — this is the reverse lookup. */
interface LessonRef {
  label: string;
  moduleNumber: number;
  moduleTitle: string;
  skillIds: string[];
}

function lessonsForStandard(
  lessonNav: LessonNav,
  grade: number,
  code: string,
): LessonRef[] {
  const out: LessonRef[] = [];
  for (const mod of lessonNav[grade] ?? []) {
    for (const lesson of mod.lessons) {
      if (lesson.standard === code) {
        out.push({
          label: lesson.label,
          moduleNumber: mod.moduleNumber,
          moduleTitle: mod.title,
          skillIds: lesson.skillIds,
        });
      }
    }
  }
  return out;
}

export default function SkillIntervention({
  lessonNav,
  checkpointNav,
}: {
  lessonNav: LessonNav;
  checkpointNav?: CheckpointNav;
}) {
  const [grade, setGrade] = useState<number>(6);
  const [standard, setStandard] = useState<string>("");
  const [diagnosticOpen, setDiagnosticOpen] = useState(false);
  const [progressOpen, setProgressOpen] = useState(false);
  // When the standard was chosen via a specific textbook lesson, remember it
  // so the progression header can highlight that lesson.
  const [selectedLesson, setSelectedLesson] = useState<string | undefined>(undefined);

  const selectedSkillData = standard ? AVAILABLE_STANDARDS[standard] : null;
  const lessons = standard ? lessonsForStandard(lessonNav, grade, standard) : [];

  // Skills the picked lesson targets — highlighted in the progression, with
  // the rest of the standard's skills dimmed but still visible for context.
  const highlightedSkillIds = new Set(
    (selectedLesson && lessons.find((l) => l.label === selectedLesson)?.skillIds) || [],
  );
  const lessonActive = highlightedSkillIds.size > 0;

  // Scroll the progression into view once a standard is picked, so it isn't
  // stranded below the standard board. Only on a user pick.
  const progressionRef = useRef<HTMLDivElement>(null);
  const scrollPending = useRef(false);

  const handleGrade = (g: number) => {
    setGrade(g);
    setStandard("");
    setSelectedLesson(undefined);
  };

  const handleStandardChange = (code: string, lessonLabel?: string) => {
    setStandard(code);
    setSelectedLesson(lessonLabel);
    scrollPending.current = true;
  };

  useEffect(() => {
    if (standard && scrollPending.current) {
      scrollPending.current = false;
      progressionRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [standard]);

  return (
    <div>
      {/* Grade + Standard selectors (by strand or by lesson). Standards
          without authored skills are shown disabled — the intervention
          progression only exists once a standard is built. */}
      <Card className="p-6">
        <StandardPicker
          grade={grade}
          standard={standard}
          onGradeChange={handleGrade}
          onStandardChange={handleStandardChange}
          lessonNav={lessonNav}
          checkpointNav={checkpointNav}
          isEnabled={(code) => code in AVAILABLE_STANDARDS}
        />
      </Card>

      {selectedSkillData && (
        <div key={standard} ref={progressionRef} className="pnp-reveal mt-8 scroll-mt-24">
          {/* Standard header: code, text, and (v2) the progression narrative */}
          <Card accent="var(--pnp-accent)" className="mb-6 p-6">
            <div className="flex flex-wrap items-center gap-3">
              <Tag variant="code">{selectedSkillData.standard_code}</Tag>
              <h2 className="font-heading text-xl font-extrabold text-pnp-navy">
                Skill progression
              </h2>
            </div>
            <p className="mt-2 text-sm font-medium text-pnp-gray-700">
              {selectedSkillData.standard_text}
            </p>
            {isV2(selectedSkillData) && selectedSkillData.progression && (
              <p className="mt-3 border-t border-pnp-gray-100 pt-3 text-sm leading-relaxed text-pnp-gray-600">
                {selectedSkillData.progression.narrative}
              </p>
            )}

            {/* Lessons this standard maps to. A standard commonly spans 2–3
                textbook lessons; showing them here makes the connection
                visible. If the teacher arrived via a specific lesson, that
                one is highlighted with a quick flash. */}
            {lessons.length > 0 && (
              <div className="mt-4 border-t border-pnp-gray-100 pt-3">
                <span className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
                  Lessons for this standard
                </span>
                <div className="mt-2 flex flex-wrap gap-2">
                  {lessons.map((l) => {
                    const active = l.label === selectedLesson;
                    return (
                      <span
                        key={l.label}
                        title={`Module ${l.moduleNumber}: ${l.moduleTitle}`}
                        className={`inline-flex items-center rounded-md border-2 px-2.5 py-1 text-xs font-semibold ${
                          active
                            ? "border-pnp-accent bg-pnp-accent text-white pnp-lesson-flash"
                            : "border-pnp-gray-200 bg-white text-pnp-gray-700"
                        }`}
                      >
                        {l.label}
                      </span>
                    );
                  })}
                </div>
                {selectedLesson && (
                  <p className="mt-2 text-xs text-pnp-gray-500">
                    Highlighted is the lesson you picked. Its skills run through the
                    progression below.
                  </p>
                )}
              </div>
            )}
          </Card>

          {/* Assessment actions */}
          <div className="mb-8 flex flex-wrap items-center gap-3">
            <Button tier="primary" onClick={() => setDiagnosticOpen(true)}>
              Generate diagnostic
            </Button>
            <Button tier="secondary" onClick={() => setProgressOpen(true)}>
              Progress monitoring
            </Button>
            <p className="text-sm text-pnp-gray-500">
              Diagnose gaps across every skill, or re-assess specific skills after intervention.
            </p>
          </div>

          {/* On Grade leads, full width, its skills running across. The two
              adjacent grades pair up beneath it, and Foundation closes the
              page so far-below prerequisites read as a fallback rather than
              the starting point. */}
          <div className="space-y-6">
            <BucketCard
              col="on_grade"
              data={selectedSkillData}
              gridClass="sm:grid-cols-2 xl:grid-cols-3"
              highlightedSkillIds={highlightedSkillIds}
              lessonActive={lessonActive}
            />

            <div className="grid gap-6 lg:grid-cols-2">
              <BucketCard
                col="looking_back"
                data={selectedSkillData}
                gridClass="sm:grid-cols-2"
                highlightedSkillIds={highlightedSkillIds}
                lessonActive={lessonActive}
              />
              <BucketCard
                col="looking_forward"
                data={selectedSkillData}
                gridClass="sm:grid-cols-2"
                highlightedSkillIds={highlightedSkillIds}
                lessonActive={lessonActive}
              />
            </div>

            <BucketCard
              col="foundation"
              data={selectedSkillData}
              gridClass="sm:grid-cols-2 xl:grid-cols-4"
              highlightedSkillIds={highlightedSkillIds}
              lessonActive={lessonActive}
            />
          </div>
        </div>
      )}

      {/* Diagnostic Modal — spans all four columns, foundation included. */}
      {diagnosticOpen && selectedSkillData && (
        <DiagnosticModal
          standardCode={selectedSkillData.standard_code}
          mode="diagnostic"
          skills={selectedSkillData.skills.map((s) => ({
            skill_id: s.skill_id,
            name: s.name,
            column: s.column,
          }))}
          onClose={() => setDiagnosticOpen(false)}
        />
      )}

      {/* Progress Monitoring Modal */}
      {progressOpen && selectedSkillData && (
        <DiagnosticModal
          standardCode={selectedSkillData.standard_code}
          mode="progress"
          skills={selectedSkillData.skills.map((s) => ({
            skill_id: s.skill_id,
            name: s.name,
            column: s.column,
          }))}
          onClose={() => setProgressOpen(false)}
        />
      )}
    </div>
  );
}
