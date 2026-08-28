"use client";

import { useState, useEffect, useCallback } from "react";
import Button from "@/components/ui/Button";
import Badge, { type BadgeTone } from "@/components/ui/Badge";

interface ReviewQuestion {
  question_id: string;
  stem_text: string;
  answer_text: string;
  proficiency_level: string;
  difficulty: string;
  item_type: string;
  stem_index: number;
  variant_index: number;
}

interface ReviewData {
  format: string;
  standard: string;
  seed: number;
  questions: ReviewQuestion[];
  tiers?: Record<string, number[]>;
  mms_axis?: string;
}

interface ReviewPanelProps {
  reviewData: ReviewData;
  requestParams: Record<string, unknown>;
  onClose: () => void;
  onRegenerate: () => void;
}

// Proficiency / difficulty → brand Badge tones (no vanilla Tailwind
// health colors). Color is paired with the text label, never alone.
const PROF_TONE: Record<string, BadgeTone> = {
  below: "red",
  approaching: "yellow",
  at: "emerald",
  above: "blue",
};

const DIFF_TONE: Record<string, BadgeTone> = {
  easy: "emerald",
  medium: "yellow",
  difficult: "red",
};

function ArrowUp() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 19V5M5 12l7-7 7 7" />
    </svg>
  );
}

function ArrowDown() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 5v14M19 12l-7 7-7-7" />
    </svg>
  );
}

function QuestionCard({
  question,
  index,
  onSwap,
  swapping,
  onMoveUp,
  onMoveDown,
  canMoveUp,
  canMoveDown,
}: {
  question: ReviewQuestion;
  index: number;
  onSwap: (index: number) => void;
  swapping: boolean;
  onMoveUp?: () => void;
  onMoveDown?: () => void;
  canMoveUp?: boolean;
  canMoveDown?: boolean;
}) {
  return (
    <div className="group/card flex gap-2 rounded-lg border border-pnp-gray-200 bg-white p-3 transition-shadow hover:shadow-sm">
      {/* Reorder buttons */}
      {(onMoveUp || onMoveDown) && (
        <div className="flex flex-col justify-center gap-0.5">
          <button
            onClick={onMoveUp}
            disabled={!canMoveUp}
            className={`flex h-6 w-6 items-center justify-center rounded transition-colors ${canMoveUp ? "text-pnp-gray-500 hover:bg-pnp-gray-100 hover:text-pnp-navy" : "text-pnp-gray-200 cursor-not-allowed"}`}
            aria-label="Move up"
          >
            <ArrowUp />
          </button>
          <button
            onClick={onMoveDown}
            disabled={!canMoveDown}
            className={`flex h-6 w-6 items-center justify-center rounded transition-colors ${canMoveDown ? "text-pnp-gray-500 hover:bg-pnp-gray-100 hover:text-pnp-navy" : "text-pnp-gray-200 cursor-not-allowed"}`}
            aria-label="Move down"
          >
            <ArrowDown />
          </button>
        </div>
      )}

      {/* Card content */}
      <div className="flex-1 min-w-0">
        <div className="mb-2 flex flex-wrap gap-1.5">
          <Badge tone={PROF_TONE[question.proficiency_level] ?? "neutral"} className="capitalize">
            {question.proficiency_level}
          </Badge>
          <Badge tone={DIFF_TONE[question.difficulty] ?? "neutral"} className="capitalize">
            {question.difficulty}
          </Badge>
        </div>
        <p className="text-sm leading-relaxed text-pnp-gray-700 line-clamp-3">
          {question.stem_text}
        </p>
        <button
          onClick={() => onSwap(index)}
          disabled={swapping}
          className={`mt-2 inline-flex items-center gap-1.5 rounded-lg border border-pnp-gray-200 px-3 py-1.5 text-xs font-semibold text-pnp-gray-500 transition-colors hover:border-pnp-accent hover:text-pnp-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 ${swapping ? "cursor-wait opacity-50" : ""}`}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="23 4 23 10 17 10" />
            <polyline points="1 20 1 14 7 14" />
            <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15" />
          </svg>
          {swapping ? "Swapping..." : "Swap"}
        </button>
      </div>
    </div>
  );
}

export default function ReviewPanel({
  reviewData,
  requestParams,
  onClose,
  onRegenerate,
}: ReviewPanelProps) {
  const [questions, setQuestions] = useState(reviewData.questions);
  const [tiers, setTiers] = useState(reviewData.tiers);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loadingPdf, setLoadingPdf] = useState(true);
  const [swappingIndex, setSwappingIndex] = useState<number | null>(null);
  const [includeAnswerKey, setIncludeAnswerKey] = useState(true);
  const [pdfVersion, setPdfVersion] = useState(0);
  // Inline error banner for swap failures — replaces the raw alert()
  // that contradicted the no-alert standard the generate flow already
  // adopted. Auto-dismisses on next successful swap.
  const [swapError, setSwapError] = useState<string | null>(null);
  // Brief confirmation after Download fires so the teacher can tell
  // the click actually produced an artifact.
  const [downloadConfirm, setDownloadConfirm] = useState(false);

  // Rebuild tier ID lists from current questions + tier indices
  const buildTierQuestionIds = useCallback(
    (qs: ReviewQuestion[], t?: Record<string, number[]>) => {
      if (!t) return undefined;
      const result: Record<string, string[]> = {};
      for (const [name, indices] of Object.entries(t)) {
        result[name] = indices.map((i) => qs[i]?.question_id).filter(Boolean);
      }
      return result;
    },
    []
  );

  // Load PDF whenever questions change
  useEffect(() => {
    let cancelled = false;
    const doLoad = async () => {
      setLoadingPdf(true);
      try {
        const tierIds = buildTierQuestionIds(questions, tiers);
        const res = await fetch("/api/review-pdf", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            ...requestParams,
            seed: reviewData.seed,
            question_ids: questions.map((q) => q.question_id),
            include_answer_key: includeAnswerKey,
            tiers_by_id: tierIds,
          }),
        });
        if (cancelled) return;
        if (!res.ok) throw new Error("PDF generation failed");
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        setPdfUrl((prev) => {
          if (prev) URL.revokeObjectURL(prev);
          return url;
        });
      } catch {
        if (!cancelled) setPdfUrl(null);
      } finally {
        if (!cancelled) setLoadingPdf(false);
      }
    };
    doLoad();
    return () => { cancelled = true; };
  }, [questions, includeAnswerKey, pdfVersion, requestParams, tiers, buildTierQuestionIds]);

  const handleSwap = async (index: number) => {
    setSwappingIndex(index);
    try {
      const q = questions[index];
      const res = await fetch("/api/swap-question", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          standard: reviewData.standard,
          seed: reviewData.seed,
          question_id: q.question_id,
          exclude_ids: questions.map((x) => x.question_id),
          proficiency_level: q.proficiency_level,
          difficulty: q.difficulty,
          // When the set was built from chosen stems, a replacement has to come
          // from those same stems. Otherwise Swap quietly hands back a problem
          // for a different practice than the one the teacher picked.
          stems: requestParams.stems,
        }),
      });
      const replacement = await res.json();
      if (replacement.error || !res.ok) {
        setSwapError(
          "No other problem fits that level right now. Try a different difficulty, or use Regenerate to rebuild the whole set."
        );
        return;
      }
      setSwapError(null);
      setQuestions((prev) => {
        const next = [...prev];
        next[index] = replacement;
        return next;
      });
      setPdfVersion((v) => v + 1);
    } catch {
      setSwapError(
        "We couldn't swap that question just now. Try again — your other selections are still here."
      );
    } finally {
      setSwappingIndex(null);
    }
  };

  // Move question within a list of indices (for MMS tiers) or the full array (for proficiency)
  const moveQuestion = (fromIdx: number, toIdx: number) => {
    setQuestions((prev) => {
      const next = [...prev];
      const [moved] = next.splice(fromIdx, 1);
      next.splice(toIdx, 0, moved);
      return next;
    });
    // Also update tier indices if MMS
    if (reviewData.tiers) {
      // Rebuild tiers based on new question order — tiers track by position
      // Since we only move within a tier, the tier boundaries stay the same
    }
  };

  // Move within a tier (MMS) — swaps positions of two indices within the same tier
  const moveTierQuestion = (tierIndices: number[], posInTier: number, direction: -1 | 1) => {
    const newPos = posInTier + direction;
    if (newPos < 0 || newPos >= tierIndices.length) return;
    const fromIdx = tierIndices[posInTier];
    const toIdx = tierIndices[newPos];
    setQuestions((prev) => {
      const next = [...prev];
      [next[fromIdx], next[toIdx]] = [next[toIdx], next[fromIdx]];
      return next;
    });
  };

  const handleDownload = () => {
    if (!pdfUrl) return;
    // Teacher-readable filename — spell out the mode, keep the dotted
    // standard so it still alphabetises sanely in a Downloads folder.
    const modeLabel =
      reviewData.format === "mms"
        ? "Mild-Medium-Spicy"
        : reviewData.format === "exit_ticket"
          ? "Exit Ticket"
          : "Proficiency Set";
    const a = document.createElement("a");
    a.href = pdfUrl;
    a.download = `${reviewData.standard} ${modeLabel} — Plug N Play.pdf`;
    a.click();
    setDownloadConfirm(true);
    setTimeout(() => setDownloadConfirm(false), 2200);
  };

  // Render sidebar questions grouped by tier for MMS, flat for others
  const renderQuestions = () => {
    if (reviewData.format === "mms" && tiers) {
      return Object.entries(tiers).map(([tierName, indices]) => (
        <div key={tierName} className="mb-4">
          <h4 className="mb-2 flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-pnp-gray-500">
            <SignalIcon
              level={
                tierName === "Mild" ? 1 : tierName === "Medium" ? 2 : 3
              }
            />
            <span>
              {tierName} ({indices.length})
            </span>
          </h4>
          <div className="space-y-3">
            {indices.map((posInTier, i) => (
              <QuestionCard
                key={questions[posInTier]?.question_id ?? posInTier}
                question={questions[posInTier]}
                index={posInTier}
                onSwap={handleSwap}
                swapping={swappingIndex === posInTier}
                onMoveUp={() => moveTierQuestion(indices, i, -1)}
                onMoveDown={() => moveTierQuestion(indices, i, 1)}
                canMoveUp={i > 0}
                canMoveDown={i < indices.length - 1}
              />
            ))}
          </div>
        </div>
      ));
    }

    return (
      <div className="space-y-3">
        {questions.map((q, i) => (
          <QuestionCard
            key={q.question_id}
            question={q}
            index={i}
            onSwap={handleSwap}
            swapping={swappingIndex === i}
            onMoveUp={() => moveQuestion(i, i - 1)}
            onMoveDown={() => moveQuestion(i, i + 1)}
            canMoveUp={i > 0}
            canMoveDown={i < questions.length - 1}
          />
        ))}
      </div>
    );
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-6 animate-[fadeIn_200ms_ease-out]"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      {/* Modal box */}
      <div className="flex h-[85vh] w-full max-w-[1400px] overflow-hidden rounded-2xl bg-white shadow-2xl animate-[scaleIn_300ms_ease-out]">
        {/* Left sidebar */}
        <div className="flex w-[340px] flex-shrink-0 flex-col border-r border-pnp-gray-200 bg-pnp-gray-50">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-pnp-gray-200 bg-white px-5 py-4">
            <div>
              <h3 className="font-heading text-lg font-bold text-pnp-navy">
                {reviewData.format === "mms" ? "Mild / Medium / Spicy" :
                 reviewData.format === "exit_ticket" ? "Exit Ticket" :
                 "Proficiency Set"}
              </h3>
              <p className="text-xs text-pnp-gray-500">{reviewData.standard}</p>
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

          {/* Question list */}
          <div className="flex-1 overflow-y-auto px-4 py-4">
            {renderQuestions()}
          </div>

          {/* Footer controls */}
          <div className="border-t border-pnp-gray-200 bg-white px-4 py-4">
            {/* Inline swap-error banner replaces the raw alert() that
                fired here previously. Stays in product voice and
                dismisses on the next successful swap. */}
            {swapError && (
              <div
                role="alert"
                className="mb-3 rounded-md border border-pnp-red/30 bg-pnp-red/5 px-3 py-2 text-xs text-pnp-gray-900"
              >
                {swapError}
              </div>
            )}
            {/* Download confirmation — brief teacher-facing receipt
                that the click actually produced a file. */}
            {downloadConfirm && (
              <div className="mb-3 rounded-md border border-pnp-accent/30 bg-pnp-accent-soft px-3 py-2 text-xs font-semibold text-pnp-accent-press">
                Worksheet saved to your downloads.
              </div>
            )}
            <label className="mb-3 flex cursor-pointer items-center gap-3 text-sm font-medium text-pnp-gray-600">
              <button
                type="button"
                role="switch"
                aria-checked={includeAnswerKey}
                onClick={() => setIncludeAnswerKey(!includeAnswerKey)}
                className={`relative h-6 w-11 flex-shrink-0 rounded-full transition-colors duration-200 ${includeAnswerKey ? "bg-pnp-accent" : "bg-pnp-gray-300"}`}
              >
                <span
                  className={`absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform duration-200 ${includeAnswerKey ? "translate-x-5" : "translate-x-0"}`}
                />
              </button>
              <span>Include answer key</span>
            </label>
            <div className="flex gap-2">
              <Button tier="secondary" onClick={onRegenerate} className="flex-1">
                New set
              </Button>
              <Button
                tier="primary"
                onClick={handleDownload}
                disabled={!pdfUrl}
                className="flex-1"
              >
                Download PDF
              </Button>
            </div>
          </div>
        </div>

        {/* Right: PDF preview */}
        <div className="flex flex-1 flex-col bg-pnp-gray-100">
          {/* Right pane header — the duplicate X close button that used
              to sit here was removed. The sidebar header already carries
              a close button, and backdrop-click already closes too. */}
          <div className="flex items-center border-b border-pnp-gray-200 bg-white px-5 py-3">
            <span className="text-sm font-semibold text-pnp-navy">
              {reviewData.standard} &mdash;{" "}
              {reviewData.format === "mms" ? "Mild / Medium / Spicy" :
               reviewData.format === "exit_ticket" ? "Exit Ticket" : "Proficiency Set"}
            </span>
          </div>
          <div className="flex-1 p-3">
            {loadingPdf ? (
              <div className="flex h-full items-center justify-center text-pnp-gray-500">
                Generating PDF preview...
              </div>
            ) : pdfUrl ? (
              <iframe
                src={pdfUrl}
                className="h-full w-full rounded-lg border border-pnp-gray-200 bg-white"
                title="PDF Preview"
              />
            ) : (
              <div className="flex h-full items-center justify-center text-pnp-gray-500">
                Failed to load PDF preview
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Mild/Medium/Spicy difficulty bars. Replaced the 🌱🔥🌶️ emojis that
// were sitting in the chrome (banned per the design system and the
// blueprint's anti-emoji rule).
function SignalIcon({ level }: { level: 1 | 2 | 3 }) {
  const on = "fill-pnp-accent";
  const off = "fill-pnp-gray-300";
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true">
      <rect x="3" y="14" width="4" height="6" rx="1" className={level >= 1 ? on : off} />
      <rect x="10" y="9" width="4" height="11" rx="1" className={level >= 2 ? on : off} />
      <rect x="17" y="4" width="4" height="16" rx="1" className={level >= 3 ? on : off} />
    </svg>
  );
}
