"use client";

import { useState, useEffect } from "react";
import Button from "@/components/ui/Button";

/**
 * SkillPacketModal — configure + preview the printable skill packet PDF.
 * Shared by the intervention progression view and the skill detail page.
 * Two-panel layout: control rail on the left, live PDF preview right.
 */
export default function SkillPacketModal({
  skillName,
  skillId,
  standardCode,
  hasArtifact,
  artifactTitle,
  onClose,
}: {
  skillName: string;
  skillId: string;
  standardCode: string;
  hasArtifact: boolean;
  artifactTitle?: string;
  onClose: () => void;
}) {
  const [studentCopies, setStudentCopies] = useState(1);
  const [includeTeacherCompanion, setIncludeTeacherCompanion] = useState(true);
  const [includePrintableArtifact, setIncludePrintableArtifact] = useState(true);
  const [session, setSession] = useState<1 | 2>(1);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Generate PDF whenever settings change. Each (skill, session) pair is
  // deterministic — Session 1 and Session 2 are 9 unique problems each,
  // 18 unique problems total per skill, so a teacher can run the same
  // skill twice without repeats.
  useEffect(() => {
    let cancelled = false;
    const generate = async () => {
      setLoading(true);
      try {
        const res = await fetch("/api/generate-skill-packet", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            standard: standardCode,
            skill_id: skillId,
            student_copies: studentCopies,
            include_teacher_companion: includeTeacherCompanion,
            include_printable_artifact: hasArtifact && includePrintableArtifact,
            session,
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
  }, [standardCode, skillId, studentCopies, includeTeacherCompanion, includePrintableArtifact, hasArtifact, session]);

  const handleDownload = () => {
    if (!pdfUrl) return;
    const a = document.createElement("a");
    a.href = pdfUrl;
    a.download = `PlugNPlay_${skillId}_session${session}_${studentCopies}copies.pdf`;
    a.click();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-6 animate-[fadeIn_200ms_ease-out]"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="flex h-[85vh] w-full max-w-[1400px] overflow-hidden rounded-2xl bg-white shadow-2xl animate-[scaleIn_300ms_ease-out]">
        {/* Left panel - controls */}
        <div className="flex w-[340px] flex-shrink-0 flex-col border-r border-pnp-gray-200 bg-pnp-gray-50">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-pnp-gray-200 bg-white px-5 py-4">
            <div>
              <h3 className="font-heading text-lg font-bold text-pnp-navy">Skill Packet</h3>
              <p className="text-xs text-pnp-gray-500">{skillName}</p>
            </div>
            <button
              onClick={onClose}
              aria-label="Close"
              className="flex h-8 w-8 items-center justify-center rounded-lg text-pnp-gray-500 transition-colors hover:bg-pnp-gray-100 hover:text-pnp-navy focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Controls */}
          <div className="flex-1 overflow-y-auto px-5 py-5">
            {/* Session — two parallel forms of the skill, 9 unique
                problems each, 18 unique problems per skill total. */}
            <div className="mb-6">
              <label className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
                Session
              </label>
              <p className="mt-1 text-xs text-pnp-gray-500">
                Two parallel forms — same skill, different problems
              </p>
              <div className="mt-3 inline-flex rounded-lg border border-pnp-gray-200 bg-white p-1" role="radiogroup" aria-label="Session">
                {[1, 2].map((n) => (
                  <button
                    key={n}
                    role="radio"
                    aria-checked={session === n}
                    onClick={() => setSession(n as 1 | 2)}
                    className={`rounded-md px-5 py-1.5 text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 ${
                      session === n
                        ? "bg-pnp-accent text-white"
                        : "text-pnp-gray-700 hover:bg-pnp-gray-100"
                    }`}
                  >
                    Session {n}
                  </button>
                ))}
              </div>
            </div>

            {/* Student copies */}
            <div className="mb-6">
              <label className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
                Student Copies
              </label>
              <p className="mt-1 text-xs text-pnp-gray-500">
                How many students are in this intervention group?
              </p>
              <div className="mt-3 flex items-center gap-3">
                <button
                  onClick={() => setStudentCopies(Math.max(1, studentCopies - 1))}
                  aria-label="Fewer copies"
                  className="flex h-9 w-9 items-center justify-center rounded-lg border border-pnp-gray-300 text-pnp-navy transition-colors hover:border-pnp-gray-400 hover:bg-pnp-gray-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                    <line x1="5" y1="12" x2="19" y2="12" />
                  </svg>
                </button>
                <span className="w-10 text-center text-2xl font-bold text-pnp-navy">{studentCopies}</span>
                <button
                  onClick={() => setStudentCopies(Math.min(30, studentCopies + 1))}
                  aria-label="More copies"
                  className="flex h-9 w-9 items-center justify-center rounded-lg border border-pnp-gray-300 text-pnp-navy transition-colors hover:border-pnp-gray-400 hover:bg-pnp-gray-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                    <line x1="12" y1="5" x2="12" y2="19" />
                    <line x1="5" y1="12" x2="19" y2="12" />
                  </svg>
                </button>
              </div>
              {/* Quick presets */}
              <div className="mt-2 flex gap-2">
                {[1, 3, 5, 8].map((n) => (
                  <button
                    key={n}
                    onClick={() => setStudentCopies(n)}
                    className={`rounded-md px-3 py-1 text-xs font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 ${
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
                  className={`relative h-6 w-11 flex-shrink-0 rounded-full transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 ${
                    includeTeacherCompanion ? "bg-pnp-accent" : "bg-pnp-gray-300"
                  }`}
                >
                  <span
                    className={`absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform duration-200 ${
                      includeTeacherCompanion ? "translate-x-5" : "translate-x-0"
                    }`}
                  />
                </button>
                <div>
                  <span className="text-sm font-semibold text-pnp-navy">Teacher Companion</span>
                  <p className="text-xs text-pnp-gray-500">
                    Includes answer key, redirect scripts, vocabulary, and next steps
                  </p>
                </div>
              </label>
            </div>

            {/* Printable activity toggle — only shown when this skill ships
                a printable_artifact. */}
            {hasArtifact && (
              <div className="mb-6">
                <label className="flex cursor-pointer items-center gap-3">
                  <button
                    type="button"
                    role="switch"
                    aria-checked={includePrintableArtifact}
                    onClick={() => setIncludePrintableArtifact(!includePrintableArtifact)}
                    className={`relative h-6 w-11 flex-shrink-0 rounded-full transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 ${
                      includePrintableArtifact ? "bg-pnp-accent" : "bg-pnp-gray-300"
                    }`}
                  >
                    <span
                      className={`absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform duration-200 ${
                        includePrintableArtifact ? "translate-x-5" : "translate-x-0"
                      }`}
                    />
                  </button>
                  <div>
                    <span className="text-sm font-semibold text-pnp-navy">Printable Activity</span>
                    <p className="text-xs text-pnp-gray-500">
                      {artifactTitle
                        ? `Adds "${artifactTitle}" as a ready-to-print page`
                        : "Adds a ready-to-print activity page"}
                    </p>
                  </div>
                </label>
              </div>
            )}

            {/* Summary */}
            <div className="rounded-lg border border-pnp-gray-200 bg-white p-4">
              <h4 className="mb-2 text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
                Print Summary
              </h4>
              <div className="space-y-1 text-sm text-pnp-gray-600">
                <p>
                  <span className="font-semibold text-pnp-navy">{studentCopies}</span> student
                  {studentCopies !== 1 ? " copies" : " copy"} (2 pages each)
                </p>
                <p>
                  <span className="font-semibold text-pnp-navy">
                    {includeTeacherCompanion ? "1" : "0"}
                  </span> teacher companion
                  {includeTeacherCompanion ? " (2-3 pages)" : ""}
                </p>
                {hasArtifact && includePrintableArtifact && (
                  <p>
                    <span className="font-semibold text-pnp-navy">1</span> printable activity (1 page)
                  </p>
                )}
                <p className="border-t border-pnp-gray-100 pt-1 font-semibold text-pnp-navy">
                  ~{studentCopies * 2 + (includeTeacherCompanion ? 3 : 0) + (hasArtifact && includePrintableArtifact ? 1 : 0)} pages total
                </p>
              </div>
            </div>
          </div>

          {/* Bottom actions */}
          <div className="border-t border-pnp-gray-200 bg-white px-5 py-4">
            <Button
              tier="primary"
              fullWidth
              onClick={handleDownload}
              disabled={!pdfUrl || loading}
            >
              {loading ? "Generating..." : "Download PDF"}
            </Button>
          </div>
        </div>

        {/* Right panel - PDF preview */}
        <div className="flex flex-1 flex-col bg-pnp-gray-100">
          <div className="flex items-center justify-between border-b border-pnp-gray-200 bg-white px-5 py-3">
            <span className="text-sm font-semibold text-pnp-navy">
              {standardCode} &mdash; {skillName}
            </span>
            <button
              onClick={onClose}
              aria-label="Close"
              className="flex h-8 w-8 items-center justify-center rounded-lg text-pnp-gray-500 transition-colors hover:bg-pnp-gray-100 hover:text-pnp-navy focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="flex-1 p-3">
            {loading ? (
              <div className="flex h-full items-center justify-center text-pnp-gray-500">
                Generating skill packet...
              </div>
            ) : pdfUrl ? (
              <iframe
                src={pdfUrl}
                className="h-full w-full rounded-lg border border-pnp-gray-200 bg-white"
                title="Skill Packet Preview"
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
