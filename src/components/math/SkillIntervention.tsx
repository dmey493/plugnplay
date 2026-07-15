"use client";

import { useState, useRef, useEffect } from "react";
import {
  AVAILABLE_STANDARDS,
  BUCKET_ORDER,
  COLUMN_META,
  isPacketReady,
  isV2,
  progressionIndex,
  progressionStep,
  type Skill,
  type SkillData,
} from "@/lib/skills";
import type { LessonNav } from "@/lib/lessons";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import Tag from "@/components/ui/Tag";
import DiagnosticModal from "./DiagnosticModal";
import SkillPacketModal from "./SkillPacketModal";
import StandardPicker from "./StandardPicker";

/**
 * SkillIntervention — the Tier 2 progression view.
 *
 * A standard is presented as a logical learning progression (v2 data):
 * numbered steps flowing through the three buckets Looking Back → On
 * Grade → Looking Forward. Foundation skills stay in the data (and in
 * the diagnostic) but are intentionally not rendered here yet.
 */

function ProjectorIcon({ size = 13 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="2" y="4" width="20" height="13" rx="2" />
      <path d="M8 21h8M12 17v4" />
    </svg>
  );
}

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

  const counts = v2
    ? [
        `${skill.practice_problems?.length ?? 0} problems`,
        `${skill.activities?.length ?? 0} activities`,
        `${skill.strategy_links?.length ?? 0} strategies`,
      ].join(" · ")
    : null;

  return (
    <>
      <div
        className={`rounded-lg bg-white p-4 transition-opacity ${
          highlighted
            ? "border-2 border-pnp-accent pnp-lesson-flash"
            : "border border-pnp-gray-200"
        } ${dimmed ? "opacity-50" : ""}`}
      >
        {highlighted && (
          <span className="mb-2 inline-flex items-center rounded-md bg-pnp-accent px-2 py-0.5 text-[11px] font-bold uppercase tracking-wide text-white">
            This lesson
          </span>
        )}
        <div className="flex items-start gap-3">
          {stepNumber !== null && (
            <div
              className="mt-0.5 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full text-xs font-bold text-white"
              style={{ backgroundColor: accent }}
              aria-label={`Step ${stepNumber}`}
            >
              {stepNumber}
            </div>
          )}
          <div className="min-w-0 flex-1">
            <h4 className="font-heading text-sm font-bold leading-snug text-pnp-navy">
              {skill.name}
            </h4>

            {v2 && step ? (
              <p className="mt-1.5 text-xs leading-relaxed text-pnp-gray-600">
                {step.rationale}
              </p>
            ) : (
              previewItem && (
                <div className="mt-2 whitespace-pre-wrap break-words rounded bg-pnp-gray-50 px-3 py-2 text-xs italic text-pnp-gray-600">
                  {previewItem.stem}
                </div>
              )
            )}

            {counts && (
              <p className="mt-2 text-xs font-semibold text-pnp-gray-500">{counts}</p>
            )}

            <div className="mt-3 flex flex-wrap items-center justify-end gap-2">
              {v2 && (skill.activities?.length ?? 0) > 0 && (
                <Button
                  href={`/math/intervention/${skill.skill_id}?tab=Activities`}
                  tier="tertiary"
                  size="small"
                  title="Jump straight to this skill's activities, with printable materials"
                >
                  {`Activities · ${skill.activities?.length}`}
                </Button>
              )}
              {v2 && (
                <Button
                  href={`/math/intervention/${skill.skill_id}`}
                  tier="tertiary"
                  size="small"
                  trailingIcon={
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                      <path d="M5 12h14M12 5l7 7-7 7" />
                    </svg>
                  }
                >
                  Open
                </Button>
              )}
              {ready && (
                <Button
                  href={`/math/intervention/${skill.skill_id}/project`}
                  target="_blank"
                  rel="noopener noreferrer"
                  tier="secondary"
                  size="small"
                  icon={<ProjectorIcon />}
                  title="Project problems and digital activity for whole-class display"
                >
                  Project
                </Button>
              )}
              <Button
                tier="secondary"
                size="small"
                onClick={() => ready && setShowModal(true)}
                disabled={!ready}
                title={ready ? "Generate skill packet PDF" : "Not enough authored items or engine mapping for this skill yet"}
              >
                {ready ? "Generate" : "Coming soon"}
              </Button>
            </div>
          </div>
        </div>
      </div>

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

export default function SkillIntervention({ lessonNav }: { lessonNav: LessonNav }) {
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

          {/* Three buckets: Looking Back / On Grade / Looking Forward */}
          <div className="grid gap-6 lg:grid-cols-3">
            {BUCKET_ORDER.map((col) => {
              const colConfig = selectedSkillData.skill_columns[col];
              if (!colConfig) return null;
              const meta = COLUMN_META[col];
              const colSkills = selectedSkillData.skills.filter((s) => s.column === col);

              return (
                <Card key={col} accent={meta.accent} className="p-4 pt-5">
                  <div className="mb-4 border-b border-pnp-gray-100 pb-3">
                    <h3 className="font-heading text-base font-extrabold text-pnp-navy">
                      {colConfig.label}
                    </h3>
                    <p className="mt-0.5 text-xs text-pnp-gray-500">{colConfig.description}</p>
                  </div>

                  <div className="space-y-3">
                    {colSkills.map((skill) => (
                      <SkillCard
                        key={skill.skill_id}
                        skill={skill}
                        data={selectedSkillData}
                        highlighted={highlightedSkillIds.has(skill.skill_id)}
                        dimmed={lessonActive && !highlightedSkillIds.has(skill.skill_id)}
                      />
                    ))}
                  </div>

                  {colSkills.length === 0 && (
                    <p className="py-4 text-center text-xs text-pnp-gray-500">
                      No skills in this category
                    </p>
                  )}
                </Card>
              );
            })}
          </div>
        </div>
      )}

      {/* Diagnostic Modal — includes foundation skills even though they
          aren't rendered above; the diagnostic is where foundation gaps
          surface. */}
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
