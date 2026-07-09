"use client";

import { useState, useEffect } from "react";

interface SkillForSelection {
  skill_id: string;
  name: string;
  column: string;
}

interface DiagnosticModalProps {
  standardCode: string;
  mode: "diagnostic" | "progress";
  skills: SkillForSelection[]; // only used in progress mode
  onClose: () => void;
}

const COLUMN_LABELS: Record<string, string> = {
  foundation: "Foundation",
  looking_back: "Looking Back",
  on_grade: "On Grade",
  looking_forward: "Looking Forward",
};

const COLUMN_ORDER = ["foundation", "looking_back", "on_grade", "looking_forward"];

export default function DiagnosticModal({
  standardCode,
  mode,
  skills,
  onClose,
}: DiagnosticModalProps) {
  const [studentCopies, setStudentCopies] = useState(1);
  const [includeTeacherCompanion, setIncludeTeacherCompanion] = useState(true);
  const [selectedSkillIds, setSelectedSkillIds] = useState<string[]>([]);
  // How many questions per selected skill in progress mode. Diagnostic
  // mode tests every skill so this control isn't relevant there.
  const [questionsPerSkill, setQuestionsPerSkill] = useState<1 | 2 | 3>(2);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const isProgress = mode === "progress";
  const canGenerate = !isProgress || selectedSkillIds.length > 0;

  // Generate PDF whenever settings change
  useEffect(() => {
    if (!canGenerate) {
      setPdfUrl(null);
      return;
    }
    let cancelled = false;
    const generate = async () => {
      setLoading(true);
      try {
        const res = await fetch("/api/generate-diagnostic", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            standard: standardCode,
            mode,
            skill_ids: isProgress ? selectedSkillIds : [],
            student_copies: studentCopies,
            include_teacher_companion: includeTeacherCompanion,
            questions_per_skill: questionsPerSkill,
          }),
        });
        if (cancelled) return;
        if (!res.ok) return;
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        setPdfUrl((prev) => { if (prev) URL.revokeObjectURL(prev); return url; });
      } catch {
        // ignore
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    generate();
    return () => { cancelled = true; };
  }, [standardCode, mode, isProgress, selectedSkillIds, studentCopies, includeTeacherCompanion, questionsPerSkill, canGenerate]);

  const handleDownload = () => {
    if (!pdfUrl) return;
    const a = document.createElement("a");
    a.href = pdfUrl;
    a.download = `PlugNPlay_${standardCode.replace(/\./g, "_")}_${mode}.pdf`;
    a.click();
  };

  const toggleSkill = (skillId: string) => {
    setSelectedSkillIds((prev) =>
      prev.includes(skillId) ? prev.filter((id) => id !== skillId) : [...prev, skillId]
    );
  };

  const selectAllSkills = () => setSelectedSkillIds(skills.map((s) => s.skill_id));
  const clearAllSkills = () => setSelectedSkillIds([]);

  // Group skills by column
  const skillsByColumn: Record<string, SkillForSelection[]> = {};
  for (const s of skills) {
    if (!skillsByColumn[s.column]) skillsByColumn[s.column] = [];
    skillsByColumn[s.column].push(s);
  }

  const title = isProgress ? "Progress Check" : "Class Diagnostic";
  const accentBg = isProgress ? "bg-emerald-500" : "bg-red-500";
  const accentText = isProgress ? "text-emerald-700" : "text-red-700";

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-6 animate-[fadeIn_200ms_ease-out]"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="flex h-[88vh] w-full max-w-[1400px] overflow-hidden rounded-2xl bg-white shadow-2xl animate-[scaleIn_300ms_ease-out]">
        {/* Left panel - controls */}
        <div className="flex w-[360px] flex-shrink-0 flex-col border-r border-pnp-gray-200 bg-pnp-gray-50">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-pnp-gray-200 bg-white px-5 py-4">
            <div>
              <h3 className={`font-heading text-lg font-bold ${accentText}`}>{title}</h3>
              <p className="text-xs text-pnp-gray-500">{standardCode}</p>
            </div>
            <button
              onClick={onClose}
              className="flex h-8 w-8 items-center justify-center rounded-lg text-pnp-gray-500 hover:bg-pnp-gray-100 hover:text-pnp-navy"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Scrollable controls */}
          <div className="flex-1 overflow-y-auto px-5 py-5">
            {/* Skill selector (progress mode only) */}
            {isProgress && (
              <div className="mb-6">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
                    Select Skills
                  </label>
                  <span className="text-xs text-pnp-gray-500">
                    {selectedSkillIds.length} of {skills.length}
                  </span>
                </div>
                <div className="mt-1 flex gap-3 text-xs">
                  <button onClick={selectAllSkills} className="font-semibold text-pnp-blue hover:underline">
                    Select All
                  </button>
                  <button onClick={clearAllSkills} className="font-semibold text-pnp-gray-500 hover:underline">
                    Clear
                  </button>
                </div>

                <div className="mt-3 space-y-3">
                  {COLUMN_ORDER.map((col) => {
                    const colSkills = skillsByColumn[col];
                    if (!colSkills || colSkills.length === 0) return null;
                    return (
                      <div key={col}>
                        <p className="mb-1 text-xs font-bold uppercase tracking-wider text-pnp-gray-500">
                          {COLUMN_LABELS[col]}
                        </p>
                        <div className="space-y-1">
                          {colSkills.map((skill) => {
                            const checked = selectedSkillIds.includes(skill.skill_id);
                            const shortId = skill.skill_id.split("-")[1] ?? "";
                            return (
                              <label
                                key={skill.skill_id}
                                className="flex cursor-pointer items-start gap-2 rounded-md px-2 py-1.5 text-xs hover:bg-white"
                              >
                                <input
                                  type="checkbox"
                                  checked={checked}
                                  onChange={() => toggleSkill(skill.skill_id)}
                                  className="mt-0.5 h-4 w-4 rounded border-pnp-gray-300"
                                />
                                <div className="flex-1">
                                  <span className="font-bold text-pnp-navy">{shortId}</span>
                                  <span className="ml-2 text-pnp-gray-600">{skill.name}</span>
                                </div>
                              </label>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Questions per skill — progress mode only. Applies to every
                selected skill. Default 2. */}
            {isProgress && (
              <div className="mb-6">
                <label className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
                  Questions per Skill
                </label>
                <p className="mt-1 text-xs text-pnp-gray-500">
                  How many items each selected skill gets
                </p>
                <div className="mt-3 inline-flex rounded-lg border-2 border-pnp-gray-200 bg-white p-1">
                  {([1, 2, 3] as const).map((n) => (
                    <button
                      key={n}
                      onClick={() => setQuestionsPerSkill(n)}
                      className={`rounded-md px-5 py-1.5 text-sm font-semibold transition-colors ${
                        questionsPerSkill === n
                          ? "bg-pnp-navy text-white"
                          : "text-pnp-gray-500 hover:text-pnp-navy"
                      }`}
                    >
                      {n}
                    </button>
                  ))}
                </div>
                <p className="mt-2 text-xs text-pnp-gray-500">
                  {selectedSkillIds.length > 0
                    ? `${selectedSkillIds.length * questionsPerSkill} total question${selectedSkillIds.length * questionsPerSkill === 1 ? "" : "s"}`
                    : "Pick skills to see total"}
                </p>
              </div>
            )}

            {/* Student copies */}
            <div className="mb-6">
              <label className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
                Student Copies
              </label>
              <p className="mt-1 text-xs text-pnp-gray-500">
                How many students are taking this?
              </p>
              <div className="mt-3 flex items-center gap-3">
                <button
                  onClick={() => setStudentCopies(Math.max(1, studentCopies - 1))}
                  className="flex h-9 w-9 items-center justify-center rounded-lg border-2 border-pnp-gray-200 text-pnp-navy transition-colors hover:border-pnp-blue hover:text-pnp-blue"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                    <line x1="5" y1="12" x2="19" y2="12" />
                  </svg>
                </button>
                <span className="w-10 text-center text-2xl font-bold text-pnp-navy">{studentCopies}</span>
                <button
                  onClick={() => setStudentCopies(Math.min(30, studentCopies + 1))}
                  className="flex h-9 w-9 items-center justify-center rounded-lg border-2 border-pnp-gray-200 text-pnp-navy transition-colors hover:border-pnp-blue hover:text-pnp-blue"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                    <line x1="12" y1="5" x2="12" y2="19" />
                    <line x1="5" y1="12" x2="19" y2="12" />
                  </svg>
                </button>
              </div>
              <div className="mt-2 flex gap-2">
                {[1, 5, 10, 25].map((n) => (
                  <button
                    key={n}
                    onClick={() => setStudentCopies(n)}
                    className={`rounded px-3 py-1 text-xs font-semibold transition-colors ${
                      studentCopies === n
                        ? "bg-pnp-navy text-white"
                        : "bg-pnp-gray-100 text-pnp-gray-500 hover:bg-pnp-gray-200"
                    }`}
                  >
                    {n}
                  </button>
                ))}
              </div>
            </div>

            {/* Teacher companion toggle */}
            <div className="mb-6">
              <label className="flex cursor-pointer items-center gap-3">
                <button
                  type="button"
                  role="switch"
                  aria-checked={includeTeacherCompanion}
                  onClick={() => setIncludeTeacherCompanion(!includeTeacherCompanion)}
                  className={`relative h-6 w-11 flex-shrink-0 rounded-full transition-colors duration-200 ${
                    includeTeacherCompanion ? "bg-[#c8e600]" : "bg-pnp-gray-300"
                  }`}
                >
                  <span
                    className={`absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform duration-200 ${
                      includeTeacherCompanion ? "translate-x-5" : "translate-x-0"
                    }`}
                  />
                </button>
                <div>
                  <span className="text-sm font-semibold text-pnp-navy">Teacher Answer Key</span>
                  <p className="text-xs text-pnp-gray-500">
                    Includes skill tracker and answer key with skill tags
                  </p>
                </div>
              </label>
            </div>

            {/* Empty state for progress mode */}
            {isProgress && selectedSkillIds.length === 0 && (
              <div className="rounded-lg border-2 border-dashed border-pnp-gray-200 p-4 text-center">
                <p className="text-xs text-pnp-gray-500">
                  Select at least one skill above to generate a progress check.
                </p>
              </div>
            )}
          </div>

          {/* Bottom action */}
          <div className="border-t border-pnp-gray-200 bg-white px-5 py-4">
            <button
              onClick={handleDownload}
              disabled={!pdfUrl || loading || !canGenerate}
              className={`w-full rounded-lg py-3 text-sm font-semibold transition-colors ${
                !canGenerate
                  ? "bg-pnp-gray-200 text-pnp-gray-500 cursor-not-allowed"
                  : "bg-[#c8e600] text-pnp-navy hover:bg-[#b5d000] disabled:opacity-50"
              }`}
            >
              {loading ? "Generating..." : !canGenerate ? "Select Skills First" : "Download PDF"}
            </button>
          </div>
        </div>

        {/* Right panel - PDF preview */}
        <div className="flex flex-1 flex-col bg-pnp-gray-100">
          <div className="flex items-center justify-between border-b border-pnp-gray-200 bg-white px-5 py-3">
            <span className="text-sm font-semibold text-pnp-navy">
              {standardCode} &mdash; {title}
            </span>
            <button
              onClick={onClose}
              className="flex h-8 w-8 items-center justify-center rounded-lg text-pnp-gray-500 hover:bg-pnp-gray-100 hover:text-pnp-navy"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="flex-1 p-3">
            {!canGenerate ? (
              <div className="flex h-full flex-col items-center justify-center text-center text-pnp-gray-500">
                <div className={`mb-3 h-12 w-12 rounded-full ${accentBg} opacity-20`} />
                <p className="text-sm font-semibold">Select skills to assess</p>
                <p className="mt-1 text-xs">Check the skills you want to include in this progress check.</p>
              </div>
            ) : loading ? (
              <div className="flex h-full items-center justify-center text-pnp-gray-500">
                Generating {title.toLowerCase()}...
              </div>
            ) : pdfUrl ? (
              <iframe
                src={pdfUrl}
                className="h-full w-full rounded-lg border border-pnp-gray-200 bg-white"
                title={`${title} Preview`}
              />
            ) : (
              <div className="flex h-full items-center justify-center text-pnp-gray-500">
                Failed to generate preview
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
