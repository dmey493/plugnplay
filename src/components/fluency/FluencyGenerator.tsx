"use client";

import { useEffect, useState, useMemo } from "react";
import { useSearchParams } from "next/navigation";
import {
  generateProblems,
  TOPIC_LABELS,
  TOPIC_CATEGORIES,
  type FluencyOptions,
  type FluencyTopic,
  type Difficulty,
  type Problem,
} from "@/lib/fluency-gen";
import ShapeRenderer from "./ShapeRenderer";

const DEFAULT_OPTS: FluencyOptions = {
  topic: "add-fractions",
  difficulty: "easy",
  formats: { proper: true, whole: false, mixed: false, improper: false },
  maxDenominator: 12,
  allowNegatives: false,
  requireSimplification: true,
  count: 20,
  distributeIncludeFractions: false,
  distributeIncludeDecimals: false,
};

// Distribute topics surface two extra toggles ("Add fractions" / "Add
// decimals") that let teachers mix rational outside coefficients into
// the rotation alongside integers.
const DISTRIBUTE_TOPICS: ReadonlySet<FluencyTopic> = new Set([
  "distribute-expand",
  "distribute-combine",
]);

const FRACTION_TOPICS: ReadonlySet<FluencyTopic> = new Set([
  "add-fractions",
  "subtract-fractions",
  "multiply-fractions",
  "divide-fractions",
]);

// Inherently-signed topics — the generators force allowNegatives on
// regardless of the toggle. Hiding the toggle keeps the UI honest.
// Rational topics use the same fraction format toggles as plain
// fractions, so they ARE still treated as fraction topics for the
// "Number formats" group below.
const INHERENTLY_SIGNED_TOPICS: ReadonlySet<FluencyTopic> = new Set([
  "add-integers",
  "subtract-integers",
  "multiply-integers",
  "divide-integers",
  "integer-mixed",
  "add-rationals",
  "subtract-rationals",
  "multiply-rationals",
  "divide-rationals",
  "rational-mixed",
]);

// Rational topics share the fraction generators internally, so the
// fraction format and max-denominator controls apply to them.
const RATIONAL_TOPICS: ReadonlySet<FluencyTopic> = new Set([
  "add-rationals",
  "subtract-rationals",
  "multiply-rationals",
  "divide-rationals",
  "rational-mixed",
]);

export default function FluencyGenerator() {
  // Two view modes: "picker" (category landing) and "generator" (work
  // surface). The picker is the entry; choosing a topic switches modes
  // and the back button returns.
  const [mode, setMode] = useState<"picker" | "generator">("picker");
  const [opts, setOpts] = useState<FluencyOptions>(DEFAULT_OPTS);
  const [problems, setProblems] = useState<Problem[]>([]);
  const [showAnswers, setShowAnswers] = useState(false);

  // ?topic=add-integers → skip the picker and land straight on the
  // generator with that topic selected. Teachers arriving from a unit
  // section's "Fluency Practice" button get pre-configured this way.
  // First-render only so we don't fight subsequent manual selections.
  const searchParams = useSearchParams();
  useEffect(() => {
    const param = searchParams?.get("topic");
    if (!param) return;
    if (param in TOPIC_LABELS) {
      const topic = param as FluencyTopic;
      setOpts((o) => ({ ...o, topic }));
      setMode("generator");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Plain fractions OR rationals (which use the fraction generators
  // under the hood) both expose the fraction-format and max-denominator
  // controls.
  const isFractionTopic =
    FRACTION_TOPICS.has(opts.topic) || RATIONAL_TOPICS.has(opts.topic);
  // Hide the "Allow negatives" toggle for any topic where negatives are
  // structurally baked in (all integers, all rationals).
  const isInherentlySigned = INHERENTLY_SIGNED_TOPICS.has(opts.topic);
  // Every fluency topic paginates at 10 problems per page. The user can
  // still generate any total they want — the worksheet view splits into
  // additional pages and each page lays out evenly so 10 problems fill
  // the page cleanly.
  const PROBLEMS_PER_PAGE = 10;

  // ALL hooks must be called every render (rules of hooks). The picker
  // branch is rendered AFTER the hooks below, not before, so we never
  // skip a useMemo / useState between renders.
  //
  // For fraction topics we paginate at 10 per page. Each page chunk gets
  // split into its own 2-column left/right pair. Decimals render as a
  // single page (no chunking).
  const pages = useMemo(() => {
    if (problems.length === 0) return [];
    const out: { left: Problem[]; right: Problem[] }[] = [];
    for (let i = 0; i < problems.length; i += PROBLEMS_PER_PAGE) {
      const chunk = problems.slice(i, i + PROBLEMS_PER_PAGE);
      const half = Math.ceil(chunk.length / 2);
      out.push({ left: chunk.slice(0, half), right: chunk.slice(half) });
    }
    return out;
  }, [problems]);

  // If every problem carries the same non-empty `instruction`, hoist it
  // to a single line at the top of the worksheet instead of repeating it
  // next to every shape.
  const sharedInstruction = useMemo<string | null>(() => {
    if (problems.length === 0) return null;
    const first = problems[0].instruction;
    if (!first) return null;
    return problems.every((p) => p.instruction === first) ? first : null;
  }, [problems]);

  // Pick a topic from the landing page. Doesn't clamp count — count is
  // total problems across all pages; the worksheet view paginates.
  const pickTopic = (topic: FluencyTopic) => {
    setOpts((o) => ({ ...o, topic }));
    setProblems([]);
    setShowAnswers(false);
    setMode("generator");
  };

  if (mode === "picker") {
    return <TopicPicker onPick={pickTopic} />;
  }

  const generate = () => {
    setProblems(generateProblems(opts));
  };

  const print = () => {
    window.print();
  };

  const today = new Date().toLocaleDateString();

  return (
    <div className="flex flex-col gap-6 lg:flex-row">
      {/* ───── Settings panel ───── */}
      <aside className="print:hidden lg:w-80 lg:shrink-0">
        <div className="rounded-lg border border-pnp-gray-200 bg-white p-5 shadow-sm">
          <button
            type="button"
            onClick={() => setMode("picker")}
            className="mb-3 inline-flex items-center gap-1 text-xs font-semibold text-pnp-gray-500 hover:text-pnp-navy"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 12H5M12 19l-7-7 7-7" />
            </svg>
            All topics
          </button>
          <h2 className="mb-4 font-heading text-lg font-bold text-pnp-navy">
            Generator
          </h2>

          {/* Topic */}
          <Field label="Topic">
            <select
              value={opts.topic}
              onChange={(e) =>
                setOpts((o) => ({ ...o, topic: e.target.value as FluencyTopic }))
              }
              className="w-full rounded-md border border-pnp-gray-300 bg-white px-2 py-1.5 text-sm"
            >
              {(Object.keys(TOPIC_LABELS) as FluencyTopic[]).map((t) => (
                <option key={t} value={t}>
                  {TOPIC_LABELS[t]}
                </option>
              ))}
            </select>
          </Field>

          {/* Difficulty */}
          <Field label="Difficulty">
            <Segmented
              value={opts.difficulty}
              onChange={(v) => setOpts((o) => ({ ...o, difficulty: v }))}
              options={[
                { value: "easy", label: "Easy" },
                { value: "medium", label: "Medium" },
                { value: "hard", label: "Hard" },
              ]}
            />
            <p className="mt-1 text-xs text-pnp-gray-500">
              {isFractionTopic ? (
                opts.difficulty === "easy" ? (
                  "Same denominator (no LCD)."
                ) : opts.difficulty === "medium" ? (
                  "One denom divides the other."
                ) : (
                  "Coprime denominators (full LCD)."
                )
              ) : opts.difficulty === "easy" ? (
                "1 decimal place."
              ) : opts.difficulty === "medium" ? (
                "2 decimal places."
              ) : (
                "1–3 decimal places, mixed."
              )}
            </p>
          </Field>

          {/* Fraction format toggles */}
          {isFractionTopic && (
            <Field label="Number formats">
              <div className="grid grid-cols-2 gap-2">
                <CheckBox
                  label="Proper"
                  checked={opts.formats.proper}
                  onChange={(b) =>
                    setOpts((o) => ({
                      ...o,
                      formats: { ...o.formats, proper: b },
                    }))
                  }
                />
                <CheckBox
                  label="Whole numbers"
                  checked={opts.formats.whole}
                  onChange={(b) =>
                    setOpts((o) => ({
                      ...o,
                      formats: { ...o.formats, whole: b },
                    }))
                  }
                />
                <CheckBox
                  label="Mixed"
                  checked={opts.formats.mixed}
                  onChange={(b) =>
                    setOpts((o) => ({
                      ...o,
                      formats: { ...o.formats, mixed: b },
                    }))
                  }
                />
                <CheckBox
                  label="Improper"
                  checked={opts.formats.improper}
                  onChange={(b) =>
                    setOpts((o) => ({
                      ...o,
                      formats: { ...o.formats, improper: b },
                    }))
                  }
                />
              </div>
            </Field>
          )}

          {/* Max denominator */}
          {isFractionTopic && (
            <Field label={`Max denominator: ${opts.maxDenominator}`}>
              <input
                type="range"
                min={2}
                max={20}
                value={opts.maxDenominator}
                onChange={(e) =>
                  setOpts((o) => ({
                    ...o,
                    maxDenominator: parseInt(e.target.value, 10),
                  }))
                }
                className="w-full"
              />
            </Field>
          )}

          {/* Negatives — hidden on inherently-signed topics (integers,
              rationals). The toggle would be misleading: it suggests
              positives-only is an option, but those generators always
              emit signed values. */}
          {!isInherentlySigned && (
            <Field label="Sign">
              <CheckBox
                label="Allow negatives"
                checked={opts.allowNegatives}
                onChange={(b) => setOpts((o) => ({ ...o, allowNegatives: b }))}
              />
            </Field>
          )}

          {/* Simplification (fractions only) */}
          {isFractionTopic && (
            <Field label="Answers">
              <CheckBox
                label="Simplify the answer"
                checked={opts.requireSimplification}
                onChange={(b) =>
                  setOpts((o) => ({ ...o, requireSimplification: b }))
                }
              />
            </Field>
          )}

          {/* Distribute topics only — mix unit-fraction or friendly-
              decimal outside coefficients into the rotation alongside
              integers. Inside terms are picked divisible by the
              denominator so answers stay clean. */}
          {DISTRIBUTE_TOPICS.has(opts.topic) && (
            <Field label="Include rational numbers">
              <div className="space-y-2">
                <CheckBox
                  label="Add fractions"
                  checked={!!opts.distributeIncludeFractions}
                  onChange={(b) =>
                    setOpts((o) => ({ ...o, distributeIncludeFractions: b }))
                  }
                />
                <CheckBox
                  label="Add decimals"
                  checked={!!opts.distributeIncludeDecimals}
                  onChange={(b) =>
                    setOpts((o) => ({ ...o, distributeIncludeDecimals: b }))
                  }
                />
              </div>
            </Field>
          )}

          {/* Count */}
          <Field label={`Number of problems: ${opts.count}`}>
            <input
              type="range"
              min={4}
              max={60}
              step={2}
              value={opts.count}
              onChange={(e) =>
                setOpts((o) => ({ ...o, count: parseInt(e.target.value, 10) }))
              }
              className="w-full"
            />
            {opts.count > PROBLEMS_PER_PAGE && (
              <p className="mt-1 text-xs text-pnp-gray-500">
                {Math.ceil(opts.count / PROBLEMS_PER_PAGE)} pages — worksheets
                paginate at {PROBLEMS_PER_PAGE} per page.
              </p>
            )}
          </Field>

          {/* Actions — primary action uses the teal accent so it
              matches the One Button design system across the app.
              Routing through raw <button>s here (rather than the shared
              <Button> component) keeps the print/preview layout stable;
              the colour + focus treatment are aligned with tier="primary"
              and tier="secondary" tokens. */}
          <div className="mt-4 flex flex-col gap-2">
            <button
              type="button"
              onClick={generate}
              className="w-full rounded-md bg-pnp-accent px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-pnp-accent-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2"
            >
              {problems.length === 0 ? "Generate" : "Regenerate"}
            </button>
            {problems.length > 0 && (
              <>
                <button
                  type="button"
                  onClick={() => setShowAnswers((s) => !s)}
                  className="w-full rounded-md border border-pnp-gray-300 bg-white px-4 py-2 text-sm font-semibold text-pnp-navy transition-colors hover:bg-pnp-gray-50 hover:border-pnp-gray-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2"
                >
                  {showAnswers ? "Hide" : "Show"} answer key
                </button>
                <button
                  type="button"
                  onClick={print}
                  className="w-full rounded-md border border-pnp-gray-300 bg-white px-4 py-2 text-sm font-semibold text-pnp-navy transition-colors hover:bg-pnp-gray-50 hover:border-pnp-gray-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2"
                >
                  Print worksheet
                </button>
              </>
            )}
          </div>
        </div>
      </aside>

      {/* ───── Worksheet preview ───── */}
      <div className="min-w-0 flex-1">
        {problems.length === 0 ? (
          <EmptyState onGenerate={generate} />
        ) : (
          <div className="rounded-lg border border-pnp-gray-200 bg-white shadow-sm">
            {pages.map((pg, i) => (
              <div key={i}>
                {i > 0 && <div className="page-break-before" />}
                <Worksheet
                  title={
                    pages.length > 1
                      ? `${TOPIC_LABELS[opts.topic]} — Page ${i + 1} of ${pages.length}`
                      : TOPIC_LABELS[opts.topic]
                  }
                  date={today}
                  leftCol={pg.left}
                  rightCol={pg.right}
                  tallRows
                  showNameHeader={i === 0}
                  sharedInstruction={sharedInstruction}
                  headerInstruction={worksheetInstruction(opts.topic)}
                />
              </div>
            ))}
            {showAnswers && (
              <>
                <div className="page-break-before" />
                <AnswerKey
                  title={`${TOPIC_LABELS[opts.topic]} — Answer Key`}
                  problems={problems}
                />
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ───── Worksheet renderer ─────

// Worksheet typography. Inter is already loaded via next/font; we lean on
// it for a slick modern look. `tabular-nums` keeps digit widths even so
// the fractions and decimals line up cleanly across rows. Falls through to
// system sans on machines where Inter hasn't loaded yet.
const WORKSHEET_FONT =
  'var(--font-inter), "Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
const WORKSHEET_NUM_STYLE: React.CSSProperties = {
  fontFamily: WORKSHEET_FONT,
  fontVariantNumeric: "tabular-nums lining-nums",
  fontFeatureSettings: '"tnum", "lnum"',
};

function Worksheet({
  title,
  date,
  leftCol,
  rightCol,
  tallRows,
  showNameHeader = true,
  sharedInstruction,
  headerInstruction,
}: {
  title: string;
  date: string;
  leftCol: Problem[];
  rightCol: Problem[];
  /** Fractions: stacked digits need more vertical room. Flex rows fill the
   *  page evenly so 10 problems sit nicely on a single page. */
  tallRows?: boolean;
  /** Only the first page in a multi-page set shows the Name/Date/Period
   *  strip; continuation pages get a slim title-only header. */
  showNameHeader?: boolean;
  /** Optional shared instruction (e.g., "Find the area.") drawn once
   *  beneath the header instead of next to every problem. */
  sharedInstruction?: string | null;
  /** Topic-aware print header instruction. Falls back to a generic
   *  "Solve each problem." if not provided. */
  headerInstruction?: string;
}) {
  return (
    <article
      className="worksheet bg-white p-8 text-black"
      style={WORKSHEET_NUM_STYLE}
    >
      {/* First page gets the full header strip; continuation pages get
          nothing at all and simply continue the problem flow. */}
      {showNameHeader && (
        <header className="mb-6 border-b-2 border-black pb-3">
          <div className="flex items-start justify-between gap-6">
            {/* LEFT: publisher slug + concept title */}
            <div>
              <div className="font-sans text-xs font-bold uppercase tracking-[0.2em] text-pnp-gray-700">
                Plug N Play
              </div>
              <h1
                className="mt-1 text-2xl font-bold leading-tight"
                style={WORKSHEET_NUM_STYLE}
              >
                {title}
              </h1>
            </div>
            {/* RIGHT: student info */}
            <div className="text-right text-sm leading-tight">
              <div className="mb-2">
                <span className="font-semibold">Name </span>
                <span className="inline-block min-w-[180px] border-b border-black align-bottom" />
              </div>
              <div className="flex justify-end gap-4">
                <span>
                  <span className="font-semibold">Date </span>
                  <span className="inline-block min-w-[90px] border-b border-black align-bottom">
                    {date}
                  </span>
                </span>
                <span>
                  <span className="font-semibold">Period </span>
                  <span className="inline-block min-w-[50px] border-b border-black align-bottom" />
                </span>
              </div>
            </div>
          </div>
          <p className="mt-3 text-sm italic text-pnp-gray-700">
            {headerInstruction ?? "Solve each problem."}
          </p>
        </header>
      )}

      {/* Shared instruction (e.g., "Find the area.") — drawn once at the
          top of the page when every problem on the worksheet uses the
          same prompt. Keeps geometry worksheets clean. */}
      {sharedInstruction && (
        <p className="mb-5 text-center text-lg font-semibold">
          {sharedInstruction}
        </p>
      )}

      <div
        className={`grid grid-cols-2 gap-x-12 ${
          tallRows
            // tallRows: distribute the (≤10) problems evenly down the page
            // by giving each row equal flex share within a tall container.
            // gap-y stays generous so the visual rhythm reads even.
            ? "gap-y-12 [grid-auto-rows:1fr]"
            : "gap-y-6"
        }`}
        style={{
          ...WORKSHEET_NUM_STYLE,
          fontSize: "1.05rem",
          // Fraction worksheets target a page-fill min-height (~ letter
          // page height minus margins + header). Rows then flex evenly.
          ...(tallRows ? { minHeight: "8.5in" } : null),
        }}
      >
        {leftCol.map((p) => (
          <ProblemRow key={p.num} p={p} />
        ))}
        {rightCol.map((p) => (
          <ProblemRow key={p.num} p={p} />
        ))}
      </div>
    </article>
  );
}

function ProblemRow({ p }: { p: Problem }) {
  // Multi-line displays (systems of equations) split on `\n`. Geometry
  // forward problems carry an empty `display` because the prompt is hoisted
  // to a single instruction at the top — in that case we just show the
  // number + shape with no per-problem text.
  const lines = p.display.split("\n").filter((l) => l.length > 0);
  const hasText = lines.length > 0;
  // Coordinate-grid problems read top-down (prompt above the grid), unlike
  // labeled-geometry shapes which sit inline next to short labels.
  const stackVertical = p.shape?.kind === "grid";
  if (p.shape && stackVertical) {
    return (
      <div className="flex items-start gap-3">
        <span className="w-6 shrink-0 pt-1 text-right font-bold">{p.num})</span>
        <div className="flex flex-1 flex-col gap-2">
          {hasText && (
            <span className="tracking-wide">
              {lines.map((line, i) => (
                <span key={i} className="block">
                  <MathExpr text={line} />
                </span>
              ))}
            </span>
          )}
          <div>
            <ShapeRenderer spec={p.shape} />
          </div>
        </div>
      </div>
    );
  }
  return (
    <div className="flex items-start gap-3">
      <span className="w-6 shrink-0 pt-1 text-right font-bold">{p.num})</span>
      {p.shape ? (
        <div className="flex flex-1 flex-wrap items-center gap-3">
          <div className="shrink-0">
            <ShapeRenderer spec={p.shape} />
          </div>
          {hasText && (
            <span className="tracking-wide">
              {lines.map((line, i) => (
                <span key={i} className="block">
                  <MathExpr text={line} />
                </span>
              ))}
            </span>
          )}
        </div>
      ) : (
        <span className="tracking-wide">
          {lines.map((line, i) => (
            <span key={i} className="block">
              <MathExpr text={line} />
            </span>
          ))}
        </span>
      )}
    </div>
  );
}

function AnswerKey({
  title,
  problems,
}: {
  title: string;
  problems: Problem[];
}) {
  const half = Math.ceil(problems.length / 2);
  const left = problems.slice(0, half);
  const right = problems.slice(half);
  return (
    <article
      className="worksheet bg-white p-8 text-black"
      style={WORKSHEET_NUM_STYLE}
    >
      <header className="mb-6 border-b-2 border-black pb-3">
        <h1 className="text-center text-2xl font-bold">{title}</h1>
      </header>
      <div className="grid grid-cols-2 gap-x-12 gap-y-4 text-base">
        {left.map((p) => (
          <AnswerRow key={p.num} p={p} />
        ))}
        {right.map((p) => (
          <AnswerRow key={p.num} p={p} />
        ))}
      </div>
    </article>
  );
}

function AnswerRow({ p }: { p: Problem }) {
  const displayLines = p.display.split("\n");
  // Use the answer-key shape variant (e.g., grid with the line drawn) when
  // the generator provides one. Otherwise fall back to the worksheet shape.
  const shape = p.answerShape ?? p.shape;
  const stackVertical = shape?.kind === "grid";
  if (shape && stackVertical) {
    return (
      <div className="flex items-start gap-3">
        <span className="w-6 shrink-0 pt-1 text-right font-bold">{p.num})</span>
        <div className="flex flex-1 flex-col gap-2">
          <span className="text-pnp-gray-600">
            {displayLines.map((line, i) => (
              <span key={i} className="block">
                <MathExpr text={line} />
              </span>
            ))}
          </span>
          <div>
            <ShapeRenderer spec={shape} size="small" />
          </div>
        </div>
      </div>
    );
  }
  return (
    <div className="flex items-start gap-3">
      <span className="w-6 shrink-0 pt-1 text-right font-bold">{p.num})</span>
      {shape && (
        <div className="shrink-0">
          <ShapeRenderer spec={shape} size="small" />
        </div>
      )}
      <span className="text-pnp-gray-600">
        {displayLines.map((line, i) => (
          <span key={i} className="block">
            <MathExpr text={line} />
          </span>
        ))}
      </span>
      <span className="mx-2 text-pnp-gray-500">⇒</span>
      <span className="font-bold">
        <MathExpr text={p.answer} />
      </span>
    </div>
  );
}

// ───── Stacked-fraction rendering ─────
//
// Parse the generator's display strings (e.g., "3/4 + (−1/2)" or "2 3/4")
// and render anything that looks like a fraction stacked vertically.
//
// Tokens we recognize, in priority order:
//   "[sign]W A/B"  → mixed number  (e.g., "2 3/4", "-2 3/4")
//   "[sign]A/B"    → simple fraction (e.g., "3/4", "−3/4")
// Parens around either are preserved.

type ExprToken =
  | { kind: "text"; text: string }
  | { kind: "op"; text: string }
  | { kind: "overline"; text: string }
  | { kind: "sup"; text: string }
  | { kind: "frac"; num: number; den: number; sign: 1 | -1; paren: boolean }
  | { kind: "mixed"; whole: number; num: number; den: number; sign: 1 | -1; paren: boolean };

function tokenizeMath(s: string): ExprToken[] {
  const out: ExprToken[] = [];
  let i = 0;
  const pushText = (ch: string) => {
    const last = out[out.length - 1];
    if (last && last.kind === "text") last.text += ch;
    else out.push({ kind: "text", text: ch });
  };
  while (i < s.length) {
    const rest = s.slice(i);
    // Repeating-decimal marker: |digits| renders with an overline above
    // the digits (the standard "bar" notation for repeating decimals).
    let m = /^\|([0-9]+)\|/.exec(rest);
    if (m) {
      out.push({ kind: "overline", text: m[1] });
      i += m[0].length;
      continue;
    }
    // Superscript: `^X` where X is one or more letters or digits, or a
    // parenthesized group. Used by exponentials (2^x → 2ˣ) and any place
    // where a power needs to render visually as a sup tag.
    m = /^\^\(([^)]+)\)/.exec(rest);
    if (m) {
      out.push({ kind: "sup", text: m[1] });
      i += m[0].length;
      continue;
    }
    m = /^\^([a-zA-Z0-9]+)/.exec(rest);
    if (m) {
      out.push({ kind: "sup", text: m[1] });
      i += m[0].length;
      continue;
    }
    // Top-level operator (binary + / −) with optional spaces. We pull these
    // out so the renderer can give them extra margin — easier to read at
    // worksheet sizes. Only matches when surrounded by spaces, so it can't
    // catch a leading sign inside an operand.
    m = /^\s+([+−])\s+/.exec(rest);
    if (m) {
      out.push({ kind: "op", text: m[1] });
      i += m[0].length;
      continue;
    }
    // Mixed number: optional ( then optional sign, digits, single space, digits / digits, optional )
    m = /^(\()?([-−])?(\d+) (\d+)\/(\d+)(\))?/.exec(rest);
    if (m) {
      const openParen = Boolean(m[1]);
      const closeParen = Boolean(m[6]);
      const paren = openParen && closeParen;
      out.push({
        kind: "mixed",
        sign: m[2] ? -1 : 1,
        whole: parseInt(m[3], 10),
        num: parseInt(m[4], 10),
        den: parseInt(m[5], 10),
        paren,
      });
      i += m[0].length;
      continue;
    }
    // Simple fraction.
    m = /^(\()?([-−])?(\d+)\/(\d+)(\))?/.exec(rest);
    if (m) {
      const openParen = Boolean(m[1]);
      const closeParen = Boolean(m[5]);
      const paren = openParen && closeParen;
      out.push({
        kind: "frac",
        sign: m[2] ? -1 : 1,
        num: parseInt(m[3], 10),
        den: parseInt(m[4], 10),
        paren,
      });
      i += m[0].length;
      continue;
    }
    pushText(s[i]);
    i++;
  }
  return out;
}

function MathExpr({ text }: { text: string }) {
  const tokens = tokenizeMath(text);
  return (
    <span className="inline-flex items-center">
      {tokens.map((t, i) => {
        if (t.kind === "text") return <span key={i}>{t.text}</span>;
        if (t.kind === "op")
          return (
            <span key={i} className="mx-3">
              {t.text}
            </span>
          );
        if (t.kind === "overline")
          return (
            <span
              key={i}
              style={{ textDecoration: "overline", textDecorationThickness: "1.5px" }}
            >
              {t.text}
            </span>
          );
        if (t.kind === "sup")
          return (
            <sup
              key={i}
              style={{ fontSize: "0.75em", verticalAlign: "super", lineHeight: 1 }}
            >
              {t.text}
            </sup>
          );
        if (t.kind === "frac")
          return (
            <Frac
              key={i}
              num={t.num}
              den={t.den}
              sign={t.sign}
              paren={t.paren}
            />
          );
        return (
          <Mixed
            key={i}
            whole={t.whole}
            num={t.num}
            den={t.den}
            sign={t.sign}
            paren={t.paren}
          />
        );
      })}
    </span>
  );
}

function Frac({
  num,
  den,
  sign,
  paren,
}: {
  num: number;
  den: number;
  sign: 1 | -1;
  paren: boolean;
}) {
  return (
    <span className="inline-flex items-center" style={{ verticalAlign: "middle" }}>
      {paren && <span className="mr-0.5">(</span>}
      {sign === -1 && <span className="mr-0.5">−</span>}
      <span className="inline-flex flex-col items-center text-center leading-none">
        <span className="border-b border-current px-1 pb-px">{num}</span>
        <span className="px-1 pt-px">{den}</span>
      </span>
      {paren && <span className="ml-0.5">)</span>}
    </span>
  );
}

function Mixed({
  whole,
  num,
  den,
  sign,
  paren,
}: {
  whole: number;
  num: number;
  den: number;
  sign: 1 | -1;
  paren: boolean;
}) {
  return (
    <span className="inline-flex items-center gap-1" style={{ verticalAlign: "middle" }}>
      {paren && <span>(</span>}
      {sign === -1 && <span>−</span>}
      <span>{whole}</span>
      <Frac num={num} den={den} sign={1} paren={false} />
      {paren && <span>)</span>}
    </span>
  );
}

// ───── Topic-aware worksheet instruction ─────
//
// The print header used to always read "Solve each problem. Simplify
// your answer." regardless of topic, which was odd on geometry,
// graphing, factoring, and converting worksheets where there is
// nothing to simplify. This helper picks the right verb for the topic
// family. Topics are grouped by prefix (the engine's naming scheme is
// disciplined enough that prefix is a reliable signal).
function worksheetInstruction(topic: FluencyTopic): string {
  if (FRACTION_TOPICS.has(topic) || RATIONAL_TOPICS.has(topic)) {
    return "Solve each problem. Simplify your answer.";
  }
  if (topic === "combine-like-terms") return "Simplify each expression.";
  if (topic === "distribute-expand") return "Expand each expression using the distributive property.";
  if (topic === "distribute-combine") return "Distribute and simplify by combining like terms.";
  if (topic === "prime-factorization") return "Find the prime factorisation of each number.";
  if (topic === "perfect-square-roots") return "Find each square root.";
  if (topic.startsWith("eq-")) return "Solve for the variable. Show your work.";
  if (topic.startsWith("ineq-")) return "Solve and graph the solution on a number line.";
  if (topic.startsWith("geo-")) return "Find the requested measure. Include units.";
  if (topic.startsWith("gr-")) return "Answer each problem. Show your work.";
  if (
    topic === "percent-of-change" ||
    topic === "percent-application" ||
    topic === "simple-interest"
  ) {
    return "Solve each problem. Round money to the nearest cent.";
  }
  if (
    topic.startsWith("frac-to-") ||
    topic.startsWith("dec-to-") ||
    topic.startsWith("percent-to-")
  ) {
    return "Convert each value to the requested form.";
  }
  return "Solve each problem.";
}

// ───── Empty state ─────

function EmptyState({ onGenerate }: { onGenerate: () => void }) {
  return (
    <div className="rounded-lg border-2 border-dashed border-pnp-gray-300 bg-white p-12 text-center">
      <h3 className="font-heading text-xl font-bold text-pnp-navy">
        Pick your options and generate a worksheet.
      </h3>
      <p className="mx-auto mt-2 max-w-md text-sm text-pnp-gray-500">
        Choose a topic, difficulty, and number formats on the left, then click
        Generate. Print-ready in one click.
      </p>
      <button
        type="button"
        onClick={onGenerate}
        className="mt-6 inline-flex items-center rounded-md bg-pnp-accent px-6 py-3 text-base font-semibold text-white transition-colors hover:bg-pnp-accent-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2"
      >
        Generate now
      </button>
    </div>
  );
}

// ───── Small reusable controls ─────

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="mb-4">
      <label className="mb-1 block text-xs font-bold uppercase tracking-wider text-pnp-gray-500">
        {label}
      </label>
      {children}
    </div>
  );
}

function CheckBox({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (b: boolean) => void;
}) {
  return (
    <label className="flex cursor-pointer items-center gap-2 text-sm">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="h-4 w-4 rounded border-pnp-gray-300"
      />
      <span>{label}</span>
    </label>
  );
}

function Segmented<T extends string>({
  value,
  onChange,
  options,
}: {
  value: T;
  onChange: (v: T) => void;
  options: { value: T; label: string }[];
}) {
  return (
    <div className="flex rounded-md border border-pnp-gray-300 bg-white">
      {options.map((opt, i) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => onChange(opt.value)}
          className={`flex-1 px-2 py-1.5 text-sm font-semibold transition-colors ${
            i === 0 ? "rounded-l-md" : ""
          } ${i === options.length - 1 ? "rounded-r-md" : ""} ${
            value === opt.value
              ? "bg-pnp-accent text-white"
              : "text-pnp-gray-700 hover:bg-pnp-gray-100"
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

// ───── Topic picker (landing) ─────
//
// Each category renders as a collapsible block. Closed by default to keep
// the page compact; click the header to expand. Categories with tiered
// topics (Converting, Equations) show small tier sub-headers inside.

// Tier-label → grade key. The engine encodes grade in the tier labels
// (e.g. "Tier 1 — One-Step (grade 6)", "Tier 4 — Compound (Algebra 1)").
// Tiers without an explicit grade tag (Geometry shapes) belong to all
// grades — they aren't grade-gated and we want them visible in every
// filter view.
type GradeKey = "all" | "6" | "7" | "8" | "alg1";

function tierGradeKey(label: string): GradeKey | null {
  if (/grade\s*6/i.test(label)) return "6";
  if (/grade\s*7/i.test(label)) return "7";
  if (/grade\s*8/i.test(label)) return "8";
  if (/Algebra\s*1|Alg\s*1/i.test(label)) return "alg1";
  return null;
}

function TopicPicker({ onPick }: { onPick: (t: FluencyTopic) => void }) {
  // Start with all closed. The user clicks to expand whichever they want.
  const [open, setOpen] = useState<Set<string>>(new Set());
  // Grade filter — default is "all of 6-8", which hides Algebra 1 tiers
  // by default so a 6-8 teacher isn't scrolling past quadratics/radicals.
  // The Algebra 1 chip is opt-in for the teachers who want it.
  const [grade, setGrade] = useState<GradeKey>("all");
  const [query, setQuery] = useState("");
  const toggle = (label: string) => {
    setOpen((prev) => {
      const next = new Set(prev);
      if (next.has(label)) next.delete(label);
      else next.add(label);
      return next;
    });
  };

  // Returns true if a tier label is visible under the current grade filter.
  // Untagged tiers (no "(grade X)" hint) belong to every grade — Geometry
  // shapes, for example, are skills used across the whole 6-8 ladder.
  const tierVisible = (tierLabel: string): boolean => {
    const key = tierGradeKey(tierLabel);
    if (key === null) return true;
    if (grade === "all") return key !== "alg1";
    return key === grade;
  };

  // Topic search — matches against TOPIC_LABELS (the user-facing names)
  // so the search box actually finds what teachers can see.
  const q = query.trim().toLowerCase();
  const matchesQuery = (t: FluencyTopic) =>
    q.length === 0 || TOPIC_LABELS[t].toLowerCase().includes(q);

  const GRADE_CHIPS: { key: GradeKey; label: string }[] = [
    { key: "all", label: "All 6–8" },
    { key: "6", label: "Grade 6" },
    { key: "7", label: "Grade 7" },
    { key: "8", label: "Grade 8" },
    { key: "alg1", label: "Algebra 1" },
  ];

  return (
    <div className="space-y-4">
      <div className="text-center">
        <h2 className="font-heading text-2xl font-bold text-pnp-navy">
          What do you want to practice?
        </h2>
        <p className="mt-2 text-sm text-pnp-gray-600">
          Filter by grade or search for a skill, then pick a topic.
        </p>
      </div>

      {/* Grade chips + topic search.  The chip row stays a single, flat
          row of toggles — design system uses Tag-style buttons (rounded-md,
          never pill) and the teal accent for selected.  Search box uses the
          same accent on focus as the rest of the app. */}
      <div className="flex flex-col items-center gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div role="group" aria-label="Grade filter" className="flex flex-wrap gap-2">
          {GRADE_CHIPS.map((c) => {
            const active = grade === c.key;
            return (
              <button
                key={c.key}
                type="button"
                onClick={() => setGrade(c.key)}
                aria-pressed={active}
                className={`rounded-md border px-3 py-1.5 text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 ${
                  active
                    ? "border-pnp-accent bg-pnp-accent text-white"
                    : "border-pnp-gray-300 bg-white text-pnp-gray-700 hover:border-pnp-accent/50 hover:text-pnp-navy"
                }`}
              >
                {c.label}
              </button>
            );
          })}
        </div>
        <label className="relative w-full sm:max-w-xs">
          <span className="sr-only">Search topics</span>
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search topics…"
            className="w-full rounded-md border border-pnp-gray-300 bg-white px-3 py-1.5 text-sm text-pnp-navy outline-none transition-colors placeholder:text-pnp-gray-500 focus:border-pnp-accent focus:ring-2 focus:ring-pnp-accent/30"
          />
        </label>
      </div>

      <div className="space-y-3">
        {TOPIC_CATEGORIES.map((cat) => {
          // Hide whole "Coming soon" categories — they were dead ends
          // that interrupted the pick-a-skill flow with no value.
          if (cat.comingSoon) return null;

          // Compute the topics this category actually offers under the
          // current grade + query filter, so we can hide the category
          // entirely when it has nothing to show.
          let visibleFlat: FluencyTopic[] = [];
          let visibleTiers: { label: string; topics: FluencyTopic[] }[] = [];
          if (cat.tiers) {
            visibleTiers = cat.tiers
              .filter((tier) => !tier.comingSoon && tier.topics.length > 0)
              .filter((tier) => tierVisible(tier.label))
              .map((tier) => ({
                label: tier.label,
                topics: tier.topics.filter(matchesQuery),
              }))
              .filter((tier) => tier.topics.length > 0);
          } else if (cat.topics) {
            visibleFlat = cat.topics.filter(matchesQuery);
          }

          const hasContent =
            cat.tiers ? visibleTiers.length > 0 : visibleFlat.length > 0;
          if (!hasContent) return null;

          // When a query is active, force-open every matching category so
          // the teacher sees their result without having to click.
          const isOpen = open.has(cat.label) || q.length > 0;
          return (
            <section
              key={cat.label}
              className="overflow-hidden rounded-lg border-2 bg-white"
              style={{ borderColor: cat.color + "60" }}
            >
              <button
                type="button"
                onClick={() => toggle(cat.label)}
                className="flex w-full items-center gap-4 px-4 py-3 text-left transition-colors hover:bg-pnp-gray-50"
              >
                <span
                  className="h-4 w-4 shrink-0 rounded-full"
                  style={{ backgroundColor: cat.color }}
                />
                <div className="min-w-0 flex-1">
                  <div className="font-heading text-lg font-bold uppercase tracking-wider text-pnp-navy">
                    {cat.label}
                  </div>
                  <div className="truncate text-sm italic text-pnp-gray-500">
                    {cat.blurb}
                  </div>
                </div>
                <Chevron open={isOpen} />
              </button>

              {isOpen && (
                <div className="border-t border-pnp-gray-200 bg-pnp-gray-50 p-4">
                  {cat.tiers ? (
                    <div className="space-y-5">
                      {visibleTiers.map((tier) => (
                        <div key={tier.label}>
                          <div className="mb-2 text-xs font-bold uppercase tracking-wider text-pnp-gray-500">
                            {tier.label}
                          </div>
                          <TopicGrid
                            topics={tier.topics}
                            color={cat.color}
                            onPick={onPick}
                          />
                        </div>
                      ))}
                    </div>
                  ) : (
                    <TopicGrid
                      topics={visibleFlat}
                      color={cat.color}
                      onPick={onPick}
                    />
                  )}
                </div>
              )}
            </section>
          );
        })}
      </div>
    </div>
  );
}

function TopicGrid({
  topics,
  color,
  onPick,
}: {
  topics: FluencyTopic[];
  color: string;
  onPick: (t: FluencyTopic) => void;
}) {
  return (
    <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
      {topics.map((t) => (
        <button
          key={t}
          type="button"
          onClick={() => onPick(t)}
          className="group flex flex-col items-start gap-0.5 rounded-md border bg-white p-3 text-left transition-all hover:-translate-y-0.5 hover:shadow-sm"
          style={{ borderColor: color + "60" }}
        >
          {/* Card subtitle was an identical "Generate →" on every card,
              which added no information and made ~150 cards harder to
              scan.  Dropped — the card itself is the affordance. */}
          <span
            className="font-heading text-sm font-bold text-pnp-navy group-hover:underline"
            style={{ textDecorationColor: color }}
          >
            {TOPIC_LABELS[t]}
          </span>
        </button>
      ))}
    </div>
  );
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
      className={`shrink-0 text-pnp-gray-500 transition-transform ${
        open ? "rotate-180" : ""
      }`}
    >
      <polyline points="6 9 12 15 18 9" />
    </svg>
  );
}

// Export type so the page can import this lazily if it wants.
export type { Difficulty };
