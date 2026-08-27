import type { Question, Stimulus } from "@/lib/library/science";
import Figure from "./Figure";

/**
 * A clean, print-first rendering of one stimulus — formatted like a real
 * assessment page, not the interactive web card. Black-on-white, plain
 * numbered items, a Name/Date header. `showAnswers` bolds the key inline for
 * a teacher copy. Used inside the print modal and by the print stylesheet.
 */

const LETTERS = "ABCDEFGH".split("");

function correctSet(correct: Question["correct"]): Set<number> {
  if (typeof correct === "number") return new Set([correct]);
  if (Array.isArray(correct) && typeof correct[0] === "number")
    return new Set(correct as number[]);
  return new Set();
}

function PrintQuestion({
  q,
  n,
  showAnswers,
}: {
  q: Question;
  n: number;
  showAnswers: boolean;
}) {
  const num = <span className="font-bold">{n}.</span>;

  const body = (() => {
    switch (q.kind) {
      case "mc":
      case "ms": {
        const correct = correctSet(q.correct);
        return (
          <div className="mt-1.5 grid grid-cols-1 gap-x-8 gap-y-1 sm:grid-cols-2">
            {(q.options ?? []).map((opt, i) => {
              const isC = showAnswers && correct.has(i);
              return (
                <div key={i} className={isC ? "font-bold" : ""}>
                  <span className="mr-1.5">
                    {q.kind === "ms" ? (isC ? "☑" : "☐") : `${LETTERS[i]}.`}
                  </span>
                  {opt}
                </div>
              );
            })}
          </div>
        );
      }
      case "seq": {
        const items = q.items ?? [];
        const order = q.order ?? [];
        return (
          <div className="mt-1.5 space-y-1">
            {items.map((t, i) => (
              <div key={i} className="flex gap-2">
                <span className="inline-block w-8 border-b border-black text-center font-bold">
                  {showAnswers ? order[i] ?? "" : " "}
                </span>
                <span>{t}</span>
              </div>
            ))}
          </div>
        );
      }
      case "dropdown": {
        const dd = q.dd ?? [];
        const chosen = (q.correct as string[]) ?? [];
        return (
          <div className="mt-1.5 space-y-0.5 text-[0.95em]">
            {dd.map(([label, choices], i) => {
              const opts = choices.split("|").map((o) => o.trim());
              return (
                <div key={i}>
                  <span className="font-semibold">{label}:</span>{" "}
                  {opts.map((o, j) => (
                    <span key={j}>
                      <span className={showAnswers && o.toLowerCase() === (chosen[i] ?? "").toLowerCase() ? "font-bold underline" : ""}>
                        {o}
                      </span>
                      {j < opts.length - 1 && <span className="mx-1">/</span>}
                    </span>
                  ))}
                </div>
              );
            })}
          </div>
        );
      }
      case "match": {
        const rows = q.rows ?? [];
        const opts = (q.optset ?? "").split("/").map((o) => o.trim());
        const ans = (q.correct as string[]) ?? [];
        return (
          <div className="mt-1.5">
            <table className="w-full text-[0.95em]">
              <tbody>
                {rows.map((r, i) => (
                  <tr key={i}>
                    <td className="py-0.5 pr-4 align-top">{r}</td>
                    <td className="w-1/2 border-b border-black py-0.5 align-top">
                      {showAnswers ? <span className="font-bold">{ans[i]}</span> : " "}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!showAnswers && (
              <p className="mt-1 text-[0.85em] italic">Options: {opts.join(" · ")}</p>
            )}
          </div>
        );
      }
      case "hottext": {
        const items = q.items ?? [];
        const ans = (q.correct as string[]) ?? [];
        return (
          <div className="mt-1.5 space-y-1">
            {items.map((t, i) => {
              const parts = t.split(/(\[[^\]]*\])/g);
              return (
                <div key={i}>
                  {parts.map((p, j) => {
                    const m = p.match(/^\[(.*)\]$/);
                    if (!m) return <span key={j}>{p}</span>;
                    const os = m[1].split("/").map((o) => o.trim());
                    return (
                      <span key={j}>
                        (
                        {os.map((o, k) => (
                          <span key={k}>
                            <span className={showAnswers && ans[i] && o.toLowerCase() === ans[i].toLowerCase() ? "font-bold underline" : ""}>
                              {o}
                            </span>
                            {k < os.length - 1 && <span className="mx-1">/</span>}
                          </span>
                        ))}
                        )
                      </span>
                    );
                  })}
                </div>
              );
            })}
          </div>
        );
      }
      case "tf": {
        const rows = q.rows ?? [];
        const ans = (q.correct as string[]) ?? [];
        return (
          <div className="mt-1.5 space-y-1">
            {rows.map((r, i) => (
              <div key={i} className="flex items-baseline justify-between gap-4">
                <span>{r}</span>
                <span className="whitespace-nowrap font-semibold">
                  <span className={showAnswers && ans[i] === "True" ? "font-bold underline" : ""}>T</span>
                  <span className="mx-1">/</span>
                  <span className={showAnswers && ans[i] === "False" ? "font-bold underline" : ""}>F</span>
                </span>
              </div>
            ))}
          </div>
        );
      }
      default:
        return null;
    }
  })();

  return (
    <li className="mb-3 break-inside-avoid">
      <p className="leading-snug">
        {num} {q.stem}
      </p>
      {body}
      {showAnswers && q.rationale && (
        <p className="mt-1 text-[0.82em] italic text-neutral-600">Key: {q.rationale}</p>
      )}
    </li>
  );
}

export default function PrintSheet({
  stimulus,
  pe,
  peText,
  showAnswers = false,
}: {
  stimulus: Stimulus;
  pe: string;
  peText: string;
  showAnswers?: boolean;
}) {
  return (
    <div className="print-sheet mx-auto max-w-[7.5in] bg-white px-2 text-[13px] leading-relaxed text-black">
      {/* Header */}
      <div className="flex items-end justify-between gap-6 border-b-2 border-black pb-2">
        <div>
          <p className="text-[11px] font-bold uppercase tracking-wide">
            Biology · {pe}
            {showAnswers && <span className="ml-2 font-normal italic">(Answer key)</span>}
          </p>
          <p className="mt-0.5 text-[10.5px] leading-tight text-neutral-600">{peText}</p>
        </div>
        <div className="shrink-0 text-[11px] text-neutral-700">
          <div>Name: ______________________</div>
          <div className="mt-1">Date: __________________</div>
        </div>
      </div>

      {/* Title */}
      <h1 className="mt-3 text-lg font-bold">{stimulus.title}</h1>

      {/* Phenomenon */}
      <p className="mt-1.5 whitespace-pre-line leading-relaxed">{stimulus.phenomenon}</p>

      {/* Figure */}
      <div className="print-figure">
        <Figure figure={stimulus.figure} />
      </div>

      {/* Items */}
      <ol className="mt-3 list-none">
        {stimulus.questions.map((q, i) => (
          <PrintQuestion key={i} q={q} n={i + 1} showAnswers={showAnswers} />
        ))}
      </ol>
    </div>
  );
}
