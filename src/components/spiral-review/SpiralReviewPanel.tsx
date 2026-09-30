"use client";

import { useEffect, useRef, useState } from "react";
import Badge, { type BadgeTone } from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Tag from "@/components/ui/Tag";
import {
  PROFICIENCY_LABELS,
  PROFICIENCY_LEVELS,
  type ProficiencyLevel,
} from "@/lib/standards/plds";
import {
  ITEM_TYPE_LABELS,
  isEngineError,
  planRefs,
  weekRefs,
  weeksLabel,
  type PdfReport,
  type SpiralPlan,
  type SpiralProblem,
  type SpiralWeek,
} from "@/lib/generators/spiral-review";

/**
 * SpiralReviewPanel — review a built spiral set before printing.
 *
 * Week tabs across the top of the list; the selected week's problems in
 * print order, each with Swap and a level menu (changing the level swaps in
 * a problem at that level). The right pane previews that week's PDF, redrawn
 * after every change; a newer request cancels an older one. Downloads cover
 * this week (for the copier routine) or every week.
 *
 * The plan itself lives in the builder, so closing this panel and coming
 * back keeps every swap.
 */

const PROF_TONE: Record<string, BadgeTone> = {
  below: "red",
  approaching: "yellow",
  at: "emerald",
  above: "blue",
};

const PREVIEW_DEBOUNCE_MS = 300;

interface Props {
  plan: SpiralPlan;
  onPlanChange: (update: (plan: SpiralPlan) => SpiralPlan) => void;
  onClose: () => void;
  /** Rebuild every week; resolves to an error message, or null. */
  onNewSet: () => Promise<string | null>;
  newSetBusy: boolean;
  onDownloaded: (weekNumbers: number[]) => void;
}

type Busy = { kind: "swap"; position: number } | { kind: "week" } | { kind: "download" } | null;

function nonce() {
  return Math.floor(Math.random() * 1_000_000_000) + 1;
}

/** The stem as a short preview: no figure markers, no blank lines. */
function previewText(stem: string) {
  return stem
    .replace(/\[FIGURE\]/g, "")
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean)
    .join("\n");
}

function readReport(res: Response): PdfReport | null {
  const raw = res.headers.get("X-Spiral-Report");
  if (!raw) return null;
  try {
    return JSON.parse(decodeURIComponent(raw)) as PdfReport;
  } catch {
    return null;
  }
}

function fitCaption(week: SpiralWeek) {
  const fit = week.fit;
  if (!fit) return "";
  if (fit.pages === 1) return "1 page";
  return `${fit.pages} pages`;
}

function fitSentence(week: SpiralWeek) {
  const fit = week.fit;
  if (!fit) return null;
  if (fit.pages === 1) return `Week ${week.week_number} fits on one page.`;
  return `Week ${week.week_number} prints on ${fit.pages} pages (${fit.problems_per_page.join(" + ")} problems), breaking between rows. Print it double-sided.`;
}

function ProblemCard({
  question,
  singleType,
  warning,
  busy,
  disabled,
  onSwap,
  onLevel,
}: {
  question: SpiralProblem;
  singleType: boolean;
  warning: string | null;
  busy: boolean;
  disabled: boolean;
  onSwap: () => void;
  onLevel: (level: ProficiencyLevel) => void;
}) {
  const selectId = `spiral-level-${question.position}`;
  return (
    <li className="rounded-lg border-2 border-pnp-gray-200 bg-white p-3">
      <div className="flex items-start gap-3">
        <span
          className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-pnp-yellow font-heading text-sm font-extrabold text-pnp-navy"
          aria-hidden="true"
        >
          {question.position}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="sr-only">Problem {question.position}:</span>
            <Tag variant="code">{question.standard}</Tag>
            <Badge tone={PROF_TONE[question.proficiency_level] ?? "neutral"}>
              {PROFICIENCY_LABELS[question.proficiency_level] ?? question.proficiency_level}
            </Badge>
            <span className="text-xs text-pnp-gray-500">
              {ITEM_TYPE_LABELS[question.item_type] ?? question.item_type}
              {question.has_figure ? " · has a figure" : ""}
            </span>
          </div>
          <p className="mt-2 line-clamp-3 whitespace-pre-line text-sm leading-relaxed text-pnp-gray-700">
            {previewText(question.stem_text)}
          </p>
          {warning && (
            <p className="mt-2 rounded-md border border-pnp-orange/40 bg-pnp-orange/10 px-2 py-1 text-xs font-semibold text-pnp-navy">
              {warning}
            </p>
          )}
          {singleType && (
            <p className="mt-1.5 text-xs text-pnp-gray-500">
              One problem type at this level, so each week has new numbers but
              the same kind of problem.
            </p>
          )}
          <div className="mt-2.5 flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={onSwap}
              disabled={disabled}
              className={`inline-flex items-center gap-1.5 rounded-lg border border-pnp-gray-200 px-3 py-1.5 text-xs font-semibold text-pnp-gray-600 transition-colors hover:border-pnp-accent hover:text-pnp-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${
                busy ? "cursor-wait" : ""
              }`}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <polyline points="23 4 23 10 17 10" />
                <polyline points="1 20 1 14 7 14" />
                <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15" />
              </svg>
              {busy ? "Swapping..." : "Swap"}
            </button>
            <label htmlFor={selectId} className="sr-only">
              Level for problem {question.position}
            </label>
            <select
              id={selectId}
              value={question.proficiency_level}
              disabled={disabled}
              onChange={(e) => onLevel(e.target.value as ProficiencyLevel)}
              className="h-8 rounded-lg border border-pnp-gray-200 bg-white px-2 text-xs font-semibold text-pnp-gray-700 focus-visible:border-pnp-accent focus-visible:outline-none disabled:opacity-50"
            >
              {PROFICIENCY_LEVELS.map((l) => (
                <option key={l} value={l}>
                  {PROFICIENCY_LABELS[l]}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
    </li>
  );
}

export default function SpiralReviewPanel({
  plan,
  onPlanChange,
  onClose,
  onNewSet,
  newSetBusy,
  onDownloaded,
}: Props) {
  const [activeWeek, setActiveWeek] = useState(plan.weeks[0]?.week_number ?? 1);
  const [includeKey, setIncludeKey] = useState(true);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loadingPdf, setLoadingPdf] = useState(true);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [busy, setBusy] = useState<Busy>(null);
  const [error, setError] = useState<string | null>(null);
  const [savedNote, setSavedNote] = useState<string | null>(null);
  const closeRef = useRef<HTMLButtonElement>(null);

  const week = plan.weeks.find((w) => w.week_number === activeWeek) ?? plan.weeks[0];
  const standardInfo = new Map(plan.standards.map((s) => [s.code, s]));
  const locked = busy !== null || newSetBusy;

  // Esc closes; the page behind stops scrolling while the panel is open.
  useEffect(() => {
    closeRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = prevOverflow;
    };
  }, [onClose]);

  // Preview the selected week. The key only changes when the week's problems
  // or the answer-key switch change, so a fit update does not refetch.
  const previewBody = JSON.stringify({
    grade: plan.grade,
    include_answer_key: includeKey,
    weeks: week ? [weekRefs(week)] : [],
  });
  useEffect(() => {
    if (!week) return;
    const controller = new AbortController();
    const weekNumber = week.week_number;
    setLoadingPdf(true);
    setPreviewError(null);
    const timer = setTimeout(async () => {
      try {
        const res = await fetch("/api/spiral-pdf", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: previewBody,
          signal: controller.signal,
        });
        if (!res.ok) {
          const data = await res.json().catch(() => null);
          throw new Error(data?.message ?? "The preview could not be drawn.");
        }
        const report = readReport(res);
        const blob = await res.blob();
        if (controller.signal.aborted) return;
        setPdfUrl((prev) => {
          if (prev) URL.revokeObjectURL(prev);
          return URL.createObjectURL(blob);
        });
        const fit = report?.weeks?.[0];
        if (fit) {
          onPlanChange((p) => ({
            ...p,
            weeks: p.weeks.map((w) =>
              w.week_number === weekNumber
                ? {
                    ...w,
                    fit: {
                      pages: fit.pages,
                      problems_per_page: fit.problems_per_page,
                      scale: fit.scale,
                      warnings: fit.warnings,
                    },
                  }
                : w
            ),
          }));
        }
        setLoadingPdf(false);
      } catch (e) {
        if (controller.signal.aborted) return;
        setPreviewError(e instanceof Error ? e.message : "The preview could not be drawn.");
        setLoadingPdf(false);
      }
    }, PREVIEW_DEBOUNCE_MS);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
    // previewBody captures the week's problems and the answer-key switch.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [previewBody]);

  // Release the last preview when the panel goes away.
  const urlRef = useRef<string | null>(null);
  useEffect(() => {
    urlRef.current = pdfUrl;
  }, [pdfUrl]);
  useEffect(
    () => () => {
      if (urlRef.current) URL.revokeObjectURL(urlRef.current);
    },
    []
  );

  const replaceWeek = (next: SpiralWeek) =>
    onPlanChange((p) => ({
      ...p,
      weeks: p.weeks.map((w) => (w.week_number === next.week_number ? next : w)),
    }));

  const swap = async (question: SpiralProblem, level?: ProficiencyLevel) => {
    if (!week) return;
    setBusy({ kind: "swap", position: question.position });
    setError(null);
    try {
      const res = await fetch("/api/spiral-swap", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          plan: planRefs(plan),
          target: { week_number: week.week_number, position: question.position },
          level,
          nonce: nonce(),
        }),
      });
      const data = await res.json();
      if (!res.ok || isEngineError(data)) {
        setError(
          data?.message ??
            "No other problem fits there right now. Try another level, or get new problems for the week."
        );
        return;
      }
      replaceWeek({
        ...week,
        questions: week.questions.map((q) =>
          q.position === question.position ? (data.question as SpiralProblem) : q
        ),
        fit: data.fit ?? week.fit,
      });
    } catch {
      setError("That swap didn't go through. Try again; the rest of the sheet is unchanged.");
    } finally {
      setBusy(null);
    }
  };

  const regenerateWeek = async () => {
    if (!week) return;
    setBusy({ kind: "week" });
    setError(null);
    try {
      const res = await fetch("/api/spiral-regenerate-week", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          plan: planRefs(plan),
          week_number: week.week_number,
          nonce: nonce(),
        }),
      });
      const data = await res.json();
      if (!res.ok || isEngineError(data)) {
        setError(data?.message ?? "New problems for this week could not be made. Try again.");
        return;
      }
      replaceWeek(data.week as SpiralWeek);
    } catch {
      setError("New problems for this week could not be made. Try again.");
    } finally {
      setBusy(null);
    }
  };

  const download = async (weeks: SpiralWeek[]) => {
    setBusy({ kind: "download" });
    setError(null);
    setSavedNote(null);
    try {
      const res = await fetch("/api/spiral-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          grade: plan.grade,
          include_answer_key: includeKey,
          weeks: weeks.map(weekRefs),
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => null);
        throw new Error(data?.message ?? "The PDF could not be made.");
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const numbers = weeks.map((w) => w.week_number);
      const a = document.createElement("a");
      a.href = url;
      a.download = `Spiral Review, Grade ${plan.grade}, ${weeksLabel(numbers)} (Plug N Play).pdf`;
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 10_000);
      onDownloaded(numbers);
      setSavedNote(`${weeksLabel(numbers)} saved to your downloads.`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "The PDF could not be made.");
    } finally {
      setBusy(null);
    }
  };

  const newSet = async () => {
    setError(null);
    setSavedNote(null);
    const message = await onNewSet();
    if (message) setError(message);
  };

  const allNumbers = plan.weeks.map((w) => w.week_number);
  const fitWarnings = new Map(
    (week?.fit?.warnings ?? []).map((w) => [
      w.position,
      w.code === "too_tall"
        ? "This one is too long to fit well on a page. Swap it for a shorter problem."
        : "Part of this problem runs past the edge of its box. Swap it.",
    ])
  );
  const planNotes = plan.warnings
    .map((w) => {
      if (w.message) return w.message;
      if (w.code === "content_repeat" && w.standard) {
        return `${w.standard} has only a few different problems at this level, so some repeat from another week.`;
      }
      return null;
    })
    .filter((m, i, all): m is string => Boolean(m) && all.indexOf(m) === i);

  return (
    <div
      className="fixed inset-0 z-50 flex items-stretch justify-center bg-black/60 sm:p-4 lg:p-6"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="spiral-review-title"
        className="flex h-full w-full max-w-[1400px] flex-col overflow-y-auto bg-white shadow-2xl sm:rounded-2xl lg:flex-row lg:overflow-hidden"
      >
        {/* Problems */}
        <div className="flex w-full flex-col border-pnp-gray-200 bg-pnp-gray-50 lg:min-h-0 lg:w-[420px] lg:flex-shrink-0 lg:border-r">
          <div className="flex items-start justify-between gap-3 border-b border-pnp-gray-200 bg-white px-5 py-4">
            <div>
              <h2
                id="spiral-review-title"
                className="font-heading text-lg font-extrabold text-pnp-navy"
              >
                Spiral review, grade {plan.grade}
              </h2>
              <p className="text-xs text-pnp-gray-500">
                {weeksLabel(allNumbers)} · {week?.questions.length ?? 0} problems a week
              </p>
            </div>
            <button
              ref={closeRef}
              type="button"
              onClick={onClose}
              aria-label="Close review"
              className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg text-pnp-gray-500 hover:bg-pnp-gray-100 hover:text-pnp-navy focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Week tabs */}
          <div
            role="tablist"
            aria-label="Weeks"
            className="flex gap-1.5 overflow-x-auto border-b border-pnp-gray-200 bg-white px-4 py-2.5"
          >
            {plan.weeks.map((w) => {
              const active = w.week_number === week?.week_number;
              const flagged = (w.fit?.warnings.length ?? 0) > 0;
              return (
                <button
                  key={w.week_number}
                  type="button"
                  role="tab"
                  aria-selected={active}
                  onClick={() => setActiveWeek(w.week_number)}
                  className={`flex flex-shrink-0 flex-col items-start rounded-md border-2 px-3 py-1.5 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 ${
                    active
                      ? "border-pnp-accent bg-pnp-accent-soft"
                      : "border-pnp-gray-200 bg-white hover:border-pnp-accent"
                  }`}
                >
                  <span className="flex items-center gap-1.5 font-heading text-sm font-bold text-pnp-navy">
                    Week {w.week_number}
                    {flagged && (
                      <span
                        className="h-2 w-2 rounded-full bg-pnp-orange"
                        title="A problem here needs a look"
                      />
                    )}
                  </span>
                  <span className="text-[11px] font-semibold text-pnp-gray-500">
                    {fitCaption(w)}
                  </span>
                </button>
              );
            })}
          </div>

          {/* The week */}
          <div className="flex-1 px-4 py-4 lg:min-h-0 lg:overflow-y-auto">
            {week && (
              <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
                <p className="text-xs leading-snug text-pnp-gray-600">{fitSentence(week)}</p>
                <Button
                  tier="secondary"
                  size="small"
                  onClick={regenerateWeek}
                  disabled={locked}
                >
                  {busy?.kind === "week" ? "Making new problems..." : "New problems for this week"}
                </Button>
              </div>
            )}
            {planNotes.length > 0 && (
              <ul className="mb-3 space-y-1 rounded-md border border-pnp-gray-200 bg-white px-3 py-2 text-xs text-pnp-gray-700">
                {planNotes.map((m) => (
                  <li key={m}>{m}</li>
                ))}
              </ul>
            )}
            <ol className="space-y-3">
              {week?.questions.map((q) => (
                <ProblemCard
                  key={q.uid}
                  question={q}
                  singleType={standardInfo.get(q.standard)?.stem_count === 1}
                  warning={fitWarnings.get(q.position) ?? null}
                  busy={busy?.kind === "swap" && busy.position === q.position}
                  disabled={locked}
                  onSwap={() => swap(q)}
                  onLevel={(level) => swap(q, level)}
                />
              ))}
            </ol>
          </div>

          {/* Print */}
          <div className="border-t border-pnp-gray-200 bg-white px-4 py-4">
            {error && (
              <div
                role="alert"
                className="mb-3 rounded-md border border-pnp-red/30 bg-pnp-red/5 px-3 py-2 text-xs text-pnp-gray-900"
              >
                {error}
              </div>
            )}
            {savedNote && (
              <div
                role="status"
                className="mb-3 rounded-md border border-pnp-accent/30 bg-pnp-accent-soft px-3 py-2 text-xs font-semibold text-pnp-accent-press"
              >
                {savedNote}
              </div>
            )}
            <label className="mb-3 flex cursor-pointer items-center gap-3 text-sm font-medium text-pnp-gray-600">
              <button
                type="button"
                role="switch"
                aria-checked={includeKey}
                onClick={() => setIncludeKey((v) => !v)}
                className={`relative h-6 w-11 flex-shrink-0 rounded-full transition-colors duration-200 ${
                  includeKey ? "bg-pnp-accent" : "bg-pnp-gray-300"
                }`}
              >
                <span
                  className={`absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform duration-200 ${
                    includeKey ? "translate-x-5" : "translate-x-0"
                  }`}
                />
              </button>
              <span>Include answer key</span>
            </label>
            <div className="flex flex-wrap gap-2">
              <Button
                tier="secondary"
                onClick={() => week && download([week])}
                disabled={locked || !week}
                className="flex-1"
              >
                Download this week
              </Button>
              <Button
                tier="primary"
                onClick={() => download(plan.weeks)}
                disabled={locked}
                className="flex-1"
              >
                {busy?.kind === "download" ? "Making the PDF..." : "Download all weeks"}
              </Button>
            </div>
            <div className="mt-2 flex justify-center">
              <Button tier="tertiary" size="small" onClick={newSet} disabled={locked}>
                {newSetBusy ? "Building a new set..." : "New set, all weeks"}
              </Button>
            </div>
          </div>
        </div>

        {/* Preview */}
        <div className="flex min-h-[75vh] flex-1 flex-col bg-pnp-gray-100 lg:min-h-0">
          <div className="flex items-center border-b border-pnp-gray-200 bg-white px-5 py-3">
            <span className="text-sm font-semibold text-pnp-navy">
              Preview: Week {week?.week_number}
              {includeKey ? ", with its answer key" : ""}
            </span>
          </div>
          <div className="relative flex-1 p-3">
            {pdfUrl && (
              <iframe
                src={pdfUrl}
                className={`h-full w-full rounded-lg border border-pnp-gray-200 bg-white transition-opacity ${
                  loadingPdf ? "opacity-40" : ""
                }`}
                title={`Preview of week ${week?.week_number}`}
              />
            )}
            {(loadingPdf || previewError || !pdfUrl) && (
              <div
                className="absolute inset-0 flex items-center justify-center p-6 text-center text-sm text-pnp-gray-600"
                role="status"
              >
                {previewError
                  ? previewError
                  : loadingPdf
                    ? pdfUrl
                      ? "Updating the preview..."
                      : "Drawing the preview..."
                    : "No preview yet."}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
