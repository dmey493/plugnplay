"use client";

import { useState } from "react";
import type { Question, QuestionKind } from "@/lib/science";
import { questionLabel } from "@/lib/science";

const LETTERS = "abcdefgh".split("");

const KIND_TONE: Record<QuestionKind, string> = {
  mc: "bg-[var(--pnp-blue)]/10 text-[var(--pnp-blue)]",
  ms: "bg-[var(--pnp-green)]/15 text-[var(--pnp-green)]",
  seq: "bg-[var(--pnp-orange)]/15 text-[var(--pnp-orange)]",
  dropdown: "bg-[var(--pnp-accent)]/10 text-[var(--pnp-accent)]",
  match: "bg-[var(--pnp-blue)]/10 text-[var(--pnp-blue)]",
  hottext: "bg-[var(--pnp-orange)]/15 text-[var(--pnp-orange)]",
  tf: "bg-[var(--pnp-green)]/15 text-[var(--pnp-green)]",
};

function isCorrectMc(correct: Question["correct"], i: number): boolean {
  if (typeof correct === "number") return correct === i;
  if (Array.isArray(correct)) return (correct as number[]).includes(i);
  return false;
}

/** Split a hottext item like "prey [ rise / fall ]." into text + a bracket group. */
function renderHotItem(text: string, answer: string | undefined, reveal: boolean) {
  const parts = text.split(/(\[[^\]]*\])/g);
  return parts.map((p, i) => {
    const m = p.match(/^\[(.*)\]$/);
    if (!m) return <span key={i}>{p}</span>;
    const opts = m[1].split("/").map((o) => o.trim());
    return (
      <span key={i} className="mx-0.5 inline-flex gap-1 rounded bg-[var(--pnp-gray-100)] px-1.5 py-0.5">
        {opts.map((o, j) => (
          <span
            key={j}
            className={
              reveal && answer && o.toLowerCase() === answer.toLowerCase()
                ? "font-bold text-[var(--pnp-green)]"
                : reveal
                ? "text-[var(--pnp-gray-400)] line-through"
                : "text-[var(--pnp-gray-700)]"
            }
          >
            {o}
            {j < opts.length - 1 && <span className="ml-1 text-[var(--pnp-gray-400)]">/</span>}
          </span>
        ))}
      </span>
    );
  });
}

function QuestionBody({ q, reveal }: { q: Question; reveal: boolean }) {
  switch (q.kind) {
    case "mc":
    case "ms":
      return (
        <ul className="mt-2 space-y-1.5">
          {(q.options ?? []).map((opt, i) => {
            const correct = isCorrectMc(q.correct, i);
            return (
              <li
                key={i}
                className={`flex gap-2 rounded-md border px-2.5 py-1.5 text-sm ${
                  reveal && correct
                    ? "border-[var(--pnp-green)] bg-[var(--pnp-green)]/8 font-medium text-[var(--pnp-navy)]"
                    : "border-[var(--pnp-gray-200)] text-[var(--pnp-gray-800)]"
                }`}
              >
                <span className="font-semibold text-[var(--pnp-gray-500)]">{LETTERS[i]}.</span>
                <span>{opt}</span>
                {reveal && correct && <span className="ml-auto text-[var(--pnp-green)]">✓</span>}
              </li>
            );
          })}
        </ul>
      );

    case "seq": {
      const items = q.items ?? [];
      const order = q.order ?? [];
      // order[i] = rank of items[i]; build correct sequence
      const ranked = items
        .map((t, i) => ({ t, rank: order[i] ?? i + 1 }))
        .sort((a, b) => a.rank - b.rank);
      return (
        <ol className="mt-2 space-y-1.5">
          {(reveal ? ranked.map((r) => r.t) : items).map((t, i) => (
            <li key={i} className="flex gap-2 rounded-md border border-[var(--pnp-gray-200)] px-2.5 py-1.5 text-sm text-[var(--pnp-gray-800)]">
              <span className={`font-semibold ${reveal ? "text-[var(--pnp-green)]" : "text-[var(--pnp-gray-400)]"}`}>
                {reveal ? i + 1 : "•"}
              </span>
              <span>{t}</span>
            </li>
          ))}
        </ol>
      );
    }

    case "dropdown": {
      const dd = q.dd ?? [];
      const chosen = (q.correct as string[]) ?? [];
      return (
        <ul className="mt-2 space-y-1.5">
          {dd.map(([label, choices], i) => {
            const opts = choices.split("|").map((o) => o.trim());
            return (
              <li key={i} className="rounded-md border border-[var(--pnp-gray-200)] px-2.5 py-1.5 text-sm">
                <span className="font-semibold text-[var(--pnp-accent)]">{label}:</span>{" "}
                {opts.map((o, j) => (
                  <span
                    key={j}
                    className={
                      reveal && o.toLowerCase() === (chosen[i] ?? "").toLowerCase()
                        ? "font-bold text-[var(--pnp-green)]"
                        : "text-[var(--pnp-gray-700)]"
                    }
                  >
                    {o}
                    {j < opts.length - 1 && <span className="mx-1 text-[var(--pnp-gray-400)]">·</span>}
                  </span>
                ))}
              </li>
            );
          })}
        </ul>
      );
    }

    case "match": {
      const rows = q.rows ?? [];
      const opts = (q.optset ?? "").split("/").map((o) => o.trim());
      const ans = (q.correct as string[]) ?? [];
      return (
        <div className="mt-2 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-[var(--pnp-gray-500)]">
                <th className="py-1 pr-4 font-semibold">{q.left ?? "Item"}</th>
                <th className="py-1 font-semibold">{q.right ?? "Match"}</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i} className="border-t border-[var(--pnp-gray-100)]">
                  <td className="py-1.5 pr-4 text-[var(--pnp-gray-800)]">{r}</td>
                  <td className={`py-1.5 ${reveal ? "font-medium text-[var(--pnp-green)]" : "text-[var(--pnp-gray-400)]"}`}>
                    {reveal ? ans[i] : "____"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!reveal && opts.length > 0 && (
            <p className="mt-1.5 text-xs text-[var(--pnp-gray-500)]">Options: {opts.join(" · ")}</p>
          )}
        </div>
      );
    }

    case "hottext": {
      const items = q.items ?? [];
      const ans = (q.correct as string[]) ?? [];
      return (
        <ul className="mt-2 space-y-1.5">
          {items.map((t, i) => (
            <li key={i} className="rounded-md border border-[var(--pnp-gray-200)] px-2.5 py-1.5 text-sm text-[var(--pnp-gray-800)]">
              {renderHotItem(t, ans[i], reveal)}
            </li>
          ))}
        </ul>
      );
    }

    case "tf": {
      const rows = q.rows ?? [];
      const ans = (q.correct as string[]) ?? [];
      return (
        <ul className="mt-2 space-y-1.5">
          {rows.map((r, i) => (
            <li key={i} className="flex items-center gap-2 rounded-md border border-[var(--pnp-gray-200)] px-2.5 py-1.5 text-sm">
              <span className="flex-1 text-[var(--pnp-gray-800)]">{r}</span>
              <span className={`rounded px-2 py-0.5 text-xs font-semibold ${
                reveal
                  ? ans[i] === "True"
                    ? "bg-[var(--pnp-green)]/15 text-[var(--pnp-green)]"
                    : "bg-[var(--pnp-red)]/10 text-[var(--pnp-red)]"
                  : "bg-[var(--pnp-gray-100)] text-[var(--pnp-gray-400)]"
              }`}>
                {reveal ? ans[i] : "T / F"}
              </span>
            </li>
          ))}
        </ul>
      );
    }

    default:
      return null;
  }
}

export default function QuestionList({ questions }: { questions: Question[] }) {
  const [reveal, setReveal] = useState(false);
  return (
    <div className="mt-5">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="font-heading text-sm font-bold uppercase tracking-wide text-[var(--pnp-gray-500)]">
          Items ({questions.length})
        </h4>
        <button
          type="button"
          onClick={() => setReveal((r) => !r)}
          data-no-print
          className="rounded-full border border-[var(--pnp-accent)] px-3 py-1 text-xs font-semibold text-[var(--pnp-accent)] transition-colors hover:bg-[var(--pnp-accent-soft)]"
          aria-pressed={reveal}
        >
          {reveal ? "Hide answers" : "Show answers"}
        </button>
      </div>
      <ol className="space-y-4">
        {questions.map((q, i) => (
          <li key={i} className="rounded-lg border border-[var(--pnp-gray-200)] bg-white p-3.5">
            <div className="mb-1.5 flex items-center gap-2">
              <span className="text-sm font-bold text-[var(--pnp-navy)]">{i + 1}</span>
              <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${KIND_TONE[q.kind]}`}>
                {questionLabel(q.kind)}
              </span>
              {q.td != null && (
                <span className="text-[11px] text-[var(--pnp-gray-400)]">Task demand {q.td}</span>
              )}
            </div>
            <p className="text-sm text-[var(--pnp-gray-900)]">{q.stem}</p>
            <QuestionBody q={q} reveal={reveal} />
            {reveal && q.rationale && (
              <p className="mt-2.5 rounded-md bg-[var(--pnp-green)]/8 px-2.5 py-1.5 text-xs text-[var(--pnp-gray-700)]">
                <span className="font-semibold text-[var(--pnp-green)]">Why: </span>
                {q.rationale}
              </p>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}
