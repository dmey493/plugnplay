"use client";

import React from "react";

// Render-data shapes the engine emits. Only fields we actually consume
// today are typed; anything else passes through.
export interface RenderData {
  type?: string;
  value?: number;
  circle_type?: "open" | "closed";
  direction?: "left" | "right";
  x_range?: [number, number];
  y_range?: [number, number];
  points?: Array<{ x: number; y: number; label?: string }>;
  svg_html?: string;
  // number_line_point: labeled ticks + an optional marked point. A null
  // point_value renders a blank line for the student to mark.
  ticks?: number[];
  point_value?: number | null;
  point_label?: string;
  // hundredths_grid: a 10×10 grid with `shaded` cells filled row-major.
  shaded?: number;
  label?: string;
  // bar_model (percent bar / tape diagram): segments laid left-to-right,
  // each with a relative span; shaded segments fill. `end_labels` prints
  // under the bar's two ends (e.g. ["0%", "100%"]).
  segments?: Array<{ span: number; label?: string; shaded?: boolean }>;
  end_labels?: [string, string];
  // fraction_bars: stacked bars, each split into `parts` with `shaded`
  // filled from the left.
  bars?: Array<{ parts: number; shaded?: number; label?: string }>;
  // double_number_line: two parallel lines whose ticks align vertically —
  // tick values are labels (numbers or strings like "?", "25%"), evenly
  // spaced, NOT positioned by value. Mirrors the engine's drawer.
  top_ticks?: Array<number | string>;
  bottom_ticks?: Array<number | string>;
  top_label?: string;
  bottom_label?: string;
  // data_table: headers + string rows; orientation "horizontal" renders
  // headers as row labels down the first column.
  headers?: string[];
  rows?: string[][];
  title?: string;
  orientation?: "vertical" | "horizontal";
}

// Tokenizer regexes. We split the stem into "math runs" — contiguous
// sequences of math tokens (numbers, operators, fractions, single-letter
// variables, parens) — and "prose runs" — the surrounding words.
//
// Math runs render with `white-space: nowrap` so a single expression like
// `t > -1 1/3` is never split across lines. Inside a math run, `a/b`
// pieces render as stacked Frac components.

// One fraction inside a string. Lookarounds keep us from catching m/s,
// dates, multi-slash paths, etc.
const FRACTION_RE = /(?<![A-Za-z\d_/.])(-?\d+)\/(\d+)(?![\d./])/g;

// What counts as a math "core" token — one of these MUST start the math
// run (so prose words don't accidentally trigger one). Order matters
// inside the alternation: longer patterns first.
//
//   • numeric coefficient stuck to a variable (e.g. `4n`, `2x`)
//   • signed/unsigned number with optional decimal AND optional /denom
//   • math operator
//   • paren / bracket
const MATH_CORE = "(?:-?\\d+(?:\\.\\d+)?(?:/\\d+)?(?:[a-zA-Z](?![a-zA-Z]))?|[+\\-*/=()\\[\\]<>≤≥×÷])";

// A "variable" is a single letter standing alone (not part of a word).
// Surrounded by non-letters on both sides so we don't pluck the trailing
// 's' of 'represents' into a math run.
const VARIABLE = "(?<![A-Za-z])[a-zA-Z](?![A-Za-z])";

// A math run: starts with a CORE token (digit / operator / paren — not a
// lone letter, since those are too common in prose). The run can extend
// across single spaces or commas to swallow further cores or variables.

/**
 * Render a string with stacked fractions and prose-friendly wrapping.
 *
 * Strategy:
 *   1. Find each math run in the string. A run starts with a number,
 *      operator, paren, or fraction (NOT a lone letter, to avoid pulling
 *      the trailing 's' of 'represents' into a math run).
 *   2. Once started, the run can extend across spaces to swallow further
 *      numbers, operators, parens, AND standalone single-letter variables
 *      ('t' in 't > -1 1/3').
 *   3. Wrap each run in `whitespace-nowrap` so it never splits across lines.
 *   4. Inside each run, render fractions stacked with <Frac>.
 *   5. Prose between runs is plain wrappable text.
 *
 * This handles `t > -1 1/3` as one indivisible math run with `1/3` stacked,
 * but `represents` doesn't get co-opted because the run only seeds on a
 * core math token (`>` here, then extends LEFT? — no, regex matches
 * left-to-right, so the run actually seeds on `-1`, then... hmm.
 *
 * Right, the regex is greedy left-to-right: it'll match `-1 1/3.` from
 * `-1` onward, but won't pull `t > ` because that's BEFORE the match
 * start. To get the `t > ` included we need the run to seed earlier.
 * Solution: also detect operator-led runs by using a positive lookbehind
 * on the optional leading variable when it sits next to an operator.
 */
export function MathText({ text, className }: { text: string; className?: string }) {
  if (!text) return <span className={className} />;
  const out: React.ReactNode[] = [];
  // Find runs by scanning. A run starts at the earliest index where a
  // core math token sits, then we walk LEFT one step to optionally pull
  // in a leading standalone variable, and walk RIGHT to extend.
  type Run = { start: number; end: number };
  const runs: Run[] = [];
  const seedRe = new RegExp(MATH_CORE, "g");
  // A "tail token" — used when extending a run to the right.
  // Allows a leading separator that's any of: space, tab, or `, ` (so
  // ordered pairs like (4, 3) stay glued together as one run).
  //
  // NOTE: a standalone variable can only attach to the run if it's then
  // followed by a math-context character (operator / digit / paren / EOL /
  // sentence-ending punct), not by a word. This stops `a` in `Is x = 7 a
  // solution` from being absorbed.
  const VAR_IN_MATH_CTX =
    `${VARIABLE}(?=[ \\t]*(?:$|[+\\-*/=()\\[\\]<>≤≥×÷.,?!;:]|\\d))`;
  const tailRe = new RegExp(
    `(?:[ \\t]|,[ \\t]?)?(?:${MATH_CORE}|${VAR_IN_MATH_CTX})`,
    "y" /* sticky */
  );
  let seed: RegExpExecArray | null;
  while ((seed = seedRe.exec(text)) !== null) {
    let start = seed.index;
    let end = start + seed[0].length;
    // Try to expand LEFT to grab a leading standalone variable like the
    // `t` in `t > 5`. Pattern: optional `[ \t]?` then a single letter
    // that's surrounded by non-letters.
    const beforeIdx = start - 1;
    if (beforeIdx > 0) {
      // Walk back over a single space.
      let probe = beforeIdx;
      while (probe >= 0 && (text[probe] === " " || text[probe] === "\t")) probe--;
      if (probe >= 0 && /[a-zA-Z]/.test(text[probe])) {
        // The candidate letter must itself be preceded by non-letter (or BOS)
        // — otherwise it's mid-word.
        const beforeLetter = probe - 1;
        const charBefore = beforeLetter < 0 ? "" : text[beforeLetter];
        if (charBefore === "" || !/[a-zA-Z]/.test(charBefore)) {
          start = probe;
        }
      }
    }
    // Extend RIGHT.
    tailRe.lastIndex = end;
    let tail: RegExpExecArray | null;
    while ((tail = tailRe.exec(text)) !== null) {
      end = tail.index + tail[0].length;
      tailRe.lastIndex = end;
    }
    // If this run overlaps with the previous one, merge.
    const prev = runs[runs.length - 1];
    if (prev && start <= prev.end) {
      prev.end = Math.max(prev.end, end);
    } else {
      runs.push({ start, end });
    }
    // Advance the seed regex past this run so we don't re-find inner cores.
    seedRe.lastIndex = end;
  }

  let cursor = 0;
  for (let i = 0; i < runs.length; i++) {
    const r = runs[i];
    if (r.start > cursor) {
      out.push(<span key={`p-${cursor}`}>{text.slice(cursor, r.start)}</span>);
    }
    const runText = text.slice(r.start, r.end);
    out.push(
      <span key={`m-${r.start}`} className="inline-block whitespace-nowrap">
        {renderFractionsInRun(runText, i)}
      </span>
    );
    cursor = r.end;
  }
  if (cursor < text.length) {
    out.push(<span key={`p-${cursor}`}>{text.slice(cursor)}</span>);
  }
  return <span className={className}>{out}</span>;
}

/**
 * Walk a math run, replacing each `a/b` with a stacked Frac. Returns an
 * array of nodes the caller can drop into the run's <span>.
 */
function renderFractionsInRun(run: string, runIdx: number): React.ReactNode[] {
  const out: React.ReactNode[] = [];
  let last = 0;
  let m: RegExpExecArray | null;
  const re = new RegExp(FRACTION_RE.source, "g");
  while ((m = re.exec(run)) !== null) {
    if (m.index > last) out.push(run.slice(last, m.index));
    out.push(
      <Frac key={`f-${runIdx}-${m.index}`} numerator={m[1]} denominator={m[2]} />
    );
    last = m.index + m[0].length;
  }
  if (last < run.length) out.push(run.slice(last));
  return out;
}

function Frac({ numerator, denominator }: { numerator: string; denominator: string }) {
  return (
    <span className="inline-flex flex-col items-center align-middle leading-none mx-0.5 text-[0.85em]">
      <span className="px-1">{numerator}</span>
      <span className="block w-full border-t-2 border-current" />
      <span className="px-1">{denominator}</span>
    </span>
  );
}

/**
 * Render a number-line diagram from `{value, circle_type, direction}`.
 *
 * Mirrors the engine's `_draw_number_line`: 7 ticks centered on `value`,
 * a circle (open/closed) at `value`, and an arrow (a thicker line + arrow-
 * head) extending in `direction`. SVG-based so it scales cleanly for
 * projection.
 */
export function NumberLine({
  data,
  width = 320,
  height = 56,
  strokeColor = "currentColor",
}: {
  data: RenderData;
  width?: number;
  height?: number;
  strokeColor?: string;
}) {
  const value = data.value ?? 0;
  const center = Math.round(value);
  const tickStart = center - 3;
  const ticks = 7;

  // Layout — match the engine's geometry roughly so PDF and projection
  // feel like the same artifact. Pixel space here.
  const pad = 30;
  const tickSpan = width - 2 * pad;
  const tickStep = tickSpan / (ticks - 1);
  const lineY = height * 0.45;

  // x position of the active circle (where `value` sits).
  const activeX = pad + (value - tickStart) * tickStep;
  const r = 7;

  // Arrow region (thicker line) extends from circle to the arrow side.
  const arrowEndX = data.direction === "left" ? pad : width - pad;

  return (
    <svg
      width="100%"
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      preserveAspectRatio="xMidYMid meet"
      className="block max-w-[420px]"
      role="img"
    >
      {/* Main horizontal line + end arrows */}
      <line x1={pad} y1={lineY} x2={width - pad} y2={lineY}
            stroke={strokeColor} strokeWidth={1.5} />
      <polyline
        points={`${pad + 6},${lineY - 4} ${pad},${lineY} ${pad + 6},${lineY + 4}`}
        fill="none" stroke={strokeColor} strokeWidth={1.5}
      />
      <polyline
        points={`${width - pad - 6},${lineY - 4} ${width - pad},${lineY} ${width - pad - 6},${lineY + 4}`}
        fill="none" stroke={strokeColor} strokeWidth={1.5}
      />

      {/* Tick marks + labels */}
      {Array.from({ length: ticks }).map((_, i) => {
        const tx = pad + i * tickStep;
        const tval = tickStart + i;
        return (
          <g key={i}>
            <line x1={tx} y1={lineY - 3} x2={tx} y2={lineY + 3}
                  stroke={strokeColor} strokeWidth={1} />
            <text x={tx} y={lineY + 16}
                  textAnchor="middle"
                  fontSize={11}
                  fill={strokeColor}>
              {tval}
            </text>
          </g>
        );
      })}

      {/* Bold arrow region from circle outward */}
      <line
        x1={activeX} y1={lineY}
        x2={arrowEndX} y2={lineY}
        stroke={strokeColor}
        strokeWidth={3}
      />

      {/* Open or closed circle at `value` */}
      <circle
        cx={activeX} cy={lineY} r={r}
        stroke={strokeColor}
        strokeWidth={2}
        fill={data.circle_type === "closed" ? strokeColor : "white"}
      />
    </svg>
  );
}

/**
 * Render a ticks-based number line (`number_line_point`): labeled ticks
 * plus an optional marked point. With `point_value: null` it renders a
 * blank line — used for "mark your answer on the line" items.
 */
export function NumberLinePoint({
  data,
  width = 360,
  height = 56,
  strokeColor = "currentColor",
}: {
  data: RenderData;
  width?: number;
  height?: number;
  strokeColor?: string;
}) {
  const ticks = data.ticks ?? [];
  if (ticks.length < 2) return null;
  const pad = 30;
  const tickSpan = width - 2 * pad;
  const min = ticks[0];
  const max = ticks[ticks.length - 1];
  const toX = (v: number) => pad + ((v - min) / (max - min)) * tickSpan;
  const lineY = height * 0.45;
  const pv = data.point_value;

  return (
    <svg
      width="100%"
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      preserveAspectRatio="xMidYMid meet"
      className="block max-w-[460px]"
      role="img"
    >
      <line x1={pad} y1={lineY} x2={width - pad} y2={lineY}
            stroke={strokeColor} strokeWidth={1.5} />
      <polyline
        points={`${pad + 6},${lineY - 4} ${pad},${lineY} ${pad + 6},${lineY + 4}`}
        fill="none" stroke={strokeColor} strokeWidth={1.5}
      />
      <polyline
        points={`${width - pad - 6},${lineY - 4} ${width - pad},${lineY} ${width - pad - 6},${lineY + 4}`}
        fill="none" stroke={strokeColor} strokeWidth={1.5}
      />
      {ticks.map((tval, i) => (
        <g key={i}>
          <line x1={toX(tval)} y1={lineY - 4} x2={toX(tval)} y2={lineY + 4}
                stroke={strokeColor} strokeWidth={1} />
          <text x={toX(tval)} y={lineY + 17} textAnchor="middle"
                fontSize={11} fill={strokeColor}>
            {tval}
          </text>
        </g>
      ))}
      {pv !== null && pv !== undefined && (
        <g>
          <circle cx={toX(pv)} cy={lineY} r={6} fill={strokeColor} />
          {data.point_label && (
            <text x={toX(pv)} y={lineY - 10} textAnchor="middle"
                  fontSize={12} fontWeight={700} fill={strokeColor}>
              {data.point_label}
            </text>
          )}
        </g>
      )}
    </svg>
  );
}

/**
 * Render a coordinate grid (x_range, y_range, points). Currently used for
 * 6.AF.5 looking-forward items where the engine emits a `coordinate_grid`
 * render_data block describing the axes and the points to plot/highlight.
 *
 * If the engine emits an `svg_html` block instead (some 6.AF.5 stems),
 * use <SvgFigure /> below.
 */
export function CoordinateGrid({
  data,
  size = 320,
  strokeColor = "currentColor",
}: {
  data: RenderData;
  size?: number;
  strokeColor?: string;
}) {
  const [xMin, xMax] = data.x_range ?? [-10, 10];
  const [yMin, yMax] = data.y_range ?? [-10, 10];
  const points = data.points ?? [];

  const pad = 24;
  const inner = size - 2 * pad;
  const xToPx = (x: number) => pad + ((x - xMin) / (xMax - xMin)) * inner;
  const yToPx = (y: number) => pad + ((yMax - y) / (yMax - yMin)) * inner;

  // Tick labels every 2 units to keep the grid uncluttered at projection size.
  const xTicks: number[] = [];
  for (let v = Math.ceil(xMin / 2) * 2; v <= xMax; v += 2) xTicks.push(v);
  const yTicks: number[] = [];
  for (let v = Math.ceil(yMin / 2) * 2; v <= yMax; v += 2) yTicks.push(v);

  const x0 = xToPx(0);
  const y0 = yToPx(0);

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="block" role="img">
      {/* Grid lines (light) */}
      {xTicks.map((v) => (
        <line key={`gx-${v}`} x1={xToPx(v)} y1={pad} x2={xToPx(v)} y2={size - pad}
              stroke={strokeColor} strokeOpacity={0.15} strokeWidth={0.6} />
      ))}
      {yTicks.map((v) => (
        <line key={`gy-${v}`} x1={pad} y1={yToPx(v)} x2={size - pad} y2={yToPx(v)}
              stroke={strokeColor} strokeOpacity={0.15} strokeWidth={0.6} />
      ))}

      {/* Axes */}
      <line x1={pad} y1={y0} x2={size - pad} y2={y0}
            stroke={strokeColor} strokeWidth={1.5} />
      <line x1={x0} y1={pad} x2={x0} y2={size - pad}
            stroke={strokeColor} strokeWidth={1.5} />

      {/* Tick labels (skip the origin) */}
      {xTicks.filter((v) => v !== 0).map((v) => (
        <text key={`tx-${v}`} x={xToPx(v)} y={y0 + 14}
              textAnchor="middle" fontSize={10} fill={strokeColor}>
          {v}
        </text>
      ))}
      {yTicks.filter((v) => v !== 0).map((v) => (
        <text key={`ty-${v}`} x={x0 - 6} y={yToPx(v) + 4}
              textAnchor="end" fontSize={10} fill={strokeColor}>
          {v}
        </text>
      ))}

      {/* Plotted points */}
      {points.map((p, i) => (
        <g key={`p-${i}`}>
          <circle cx={xToPx(p.x)} cy={yToPx(p.y)} r={4}
                  fill={strokeColor} />
          {p.label && (
            <text
              x={xToPx(p.x) + 6}
              y={yToPx(p.y) - 6}
              fontSize={11}
              fill={strokeColor}
            >
              {p.label}
            </text>
          )}
        </g>
      ))}
    </svg>
  );
}

/**
 * Embed an engine-generated SVG. The string comes from the Python side
 * already escaped — we trust it because it's our own engine output.
 */
export function SvgFigure({ html, maxWidth = 360 }: { html: string; maxWidth?: number }) {
  return (
    <div
      className="inline-block"
      style={{ maxWidth }}
      // eslint-disable-next-line react/no-danger
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}

/**
 * A 10×10 hundredths grid with `shaded` cells filled row-major (full rows
 * first). The workhorse model for percent/decimal/fraction equivalence —
 * "30 shaded squares IS 30/100 IS 0.30 IS 30%". `shaded: 0` (or omitted)
 * renders a blank grid for students to shade.
 */
export function HundredthsGrid({
  data,
  size = 240,
  strokeColor = "currentColor",
}: {
  data: RenderData;
  size?: number;
  strokeColor?: string;
}) {
  const shaded = Math.max(0, Math.min(100, data.shaded ?? 0));
  const pad = 4;
  const cell = (size - 2 * pad) / 10;
  const cells = Array.from({ length: 100 }, (_, i) => i);
  return (
    <div className="inline-flex flex-col items-center gap-1">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="block" role="img">
        {cells.map((i) => {
          const col = i % 10;
          const row = Math.floor(i / 10);
          return (
            <rect
              key={i}
              x={pad + col * cell}
              y={pad + row * cell}
              width={cell}
              height={cell}
              stroke={strokeColor}
              strokeOpacity={0.45}
              strokeWidth={0.75}
              fill={i < shaded ? strokeColor : "none"}
              fillOpacity={i < shaded ? 0.55 : 0}
            />
          );
        })}
        <rect x={pad} y={pad} width={cell * 10} height={cell * 10}
              stroke={strokeColor} strokeWidth={1.75} fill="none" />
      </svg>
      {data.label && <span className="text-sm font-semibold opacity-80">{data.label}</span>}
    </div>
  );
}

/**
 * A percent bar / tape diagram: one horizontal bar split into segments,
 * each with a relative `span`, optional label inside, and optional shading.
 * `end_labels` prints under the two ends (e.g. ["0%", "100%"] or
 * ["$0", "$150"]). This is the model for reverse-percent, tax/tip bases,
 * and ratio tape diagrams.
 */
export function BarModel({
  data,
  width = 380,
  strokeColor = "currentColor",
}: {
  data: RenderData;
  width?: number;
  strokeColor?: string;
}) {
  const segments = data.segments ?? [];
  if (segments.length === 0) return null;
  const totalSpan = segments.reduce((a, s) => a + (s.span || 1), 0);
  const pad = 6;
  const barH = 40;
  const height = barH + (data.end_labels ? 24 : 10) + 2 * pad;
  const innerW = width - 2 * pad;
  let x = pad;
  const rects = segments.map((s, i) => {
    const w = ((s.span || 1) / totalSpan) * innerW;
    const r = { x, w, label: s.label, shaded: !!s.shaded, key: i };
    x += w;
    return r;
  });
  return (
    <div className="inline-flex flex-col items-center gap-1">
      <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}
           preserveAspectRatio="xMidYMid meet" className="block max-w-[440px]" role="img">
        {rects.map((r) => (
          <g key={r.key}>
            <rect x={r.x} y={pad} width={r.w} height={barH}
                  stroke={strokeColor} strokeWidth={1.25}
                  fill={r.shaded ? strokeColor : "none"}
                  fillOpacity={r.shaded ? 0.35 : 0} />
            {r.label && (
              <text x={r.x + r.w / 2} y={pad + barH / 2 + 4}
                    textAnchor="middle" fontSize={13} fontWeight={600}
                    fill={strokeColor}>
                {r.label}
              </text>
            )}
          </g>
        ))}
        {data.end_labels && (
          <>
            <text x={pad} y={pad + barH + 16} textAnchor="start" fontSize={12} fill={strokeColor}>
              {data.end_labels[0]}
            </text>
            <text x={width - pad} y={pad + barH + 16} textAnchor="end" fontSize={12} fill={strokeColor}>
              {data.end_labels[1]}
            </text>
          </>
        )}
      </svg>
      {data.label && <span className="text-sm font-semibold opacity-80">{data.label}</span>}
    </div>
  );
}

/**
 * Stacked fraction bars: each bar splits into `parts` equal pieces with
 * `shaded` filled from the left. Two bars with the same shaded width and
 * different parts make equivalence visible; a 3-vs-3/4 pair grounds
 * "how many 3/4s fit in 3?" measurement division.
 */
export function FractionBars({
  data,
  width = 380,
  strokeColor = "currentColor",
}: {
  data: RenderData;
  width?: number;
  strokeColor?: string;
}) {
  const bars = data.bars ?? [];
  if (bars.length === 0) return null;
  const pad = 6;
  const barH = 30;
  const gap = 12;
  const labelW = 44;
  const height = bars.length * (barH + gap) - gap + 2 * pad;
  const innerW = width - 2 * pad - labelW;
  return (
    <div className="inline-flex flex-col items-center gap-1">
      <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}
           preserveAspectRatio="xMidYMid meet" className="block max-w-[440px]" role="img">
        {bars.map((b, bi) => {
          const y = pad + bi * (barH + gap);
          const parts = Math.max(1, b.parts);
          const cw = innerW / parts;
          return (
            <g key={bi}>
              {b.label && (
                <text x={pad + labelW - 8} y={y + barH / 2 + 4}
                      textAnchor="end" fontSize={13} fontWeight={600} fill={strokeColor}>
                  {b.label}
                </text>
              )}
              {Array.from({ length: parts }).map((_, i) => (
                <rect key={i}
                      x={pad + labelW + i * cw} y={y} width={cw} height={barH}
                      stroke={strokeColor} strokeOpacity={0.6} strokeWidth={0.9}
                      fill={i < (b.shaded ?? 0) ? strokeColor : "none"}
                      fillOpacity={i < (b.shaded ?? 0) ? 0.45 : 0} />
              ))}
              <rect x={pad + labelW} y={y} width={innerW} height={barH}
                    stroke={strokeColor} strokeWidth={1.5} fill="none" />
            </g>
          );
        })}
      </svg>
      {data.label && <span className="text-sm font-semibold opacity-80">{data.label}</span>}
    </div>
  );
}

/**
 * Two parallel number lines whose ticks align vertically — THE ratio/unit-
 * rate model. Ticks are evenly spaced labels (numbers, "?", "25%"…), so a
 * missing value renders as its own tick for students to reason about.
 */
export function DoubleNumberLine({
  data,
  width = 400,
  strokeColor = "currentColor",
}: {
  data: RenderData;
  width?: number;
  strokeColor?: string;
}) {
  const top = data.top_ticks ?? [];
  const bottom = data.bottom_ticks ?? [];
  const n = Math.max(top.length, bottom.length);
  if (n < 2) return null;
  const labelW = Math.max((data.top_label ?? "").length, (data.bottom_label ?? "").length) > 0 ? 78 : 8;
  const pad = 14;
  const height = 84;
  const topY = 26;
  const botY = 64;
  const x1 = labelW + pad;
  const x2 = width - pad;
  const step = (x2 - x1) / (n - 1);
  const fmt = (v: number | string) =>
    typeof v === "number" ? (Number.isInteger(v) ? String(v) : String(Math.round(v * 100) / 100)) : String(v);

  const line = (y: number, ticks: Array<number | string>, label: string | undefined, labelAbove: boolean) => (
    <g>
      {label && (
        <text x={labelW - 4} y={y + 4} textAnchor="end" fontSize={12} fontWeight={600} fill={strokeColor}>
          {label}
        </text>
      )}
      <line x1={x1 - 6} y1={y} x2={x2 + 6} y2={y} stroke={strokeColor} strokeWidth={1.5} />
      <polyline points={`${x2 + 1},${y - 4} ${x2 + 7},${y} ${x2 + 1},${y + 4}`}
                fill="none" stroke={strokeColor} strokeWidth={1.5} />
      {ticks.map((t, i) => (
        <g key={i}>
          <line x1={x1 + i * step} y1={y - 4} x2={x1 + i * step} y2={y + 4}
                stroke={strokeColor} strokeWidth={1.25} />
          <text x={x1 + i * step} y={labelAbove ? y - 9 : y + 17}
                textAnchor="middle" fontSize={12} fontWeight={fmt(t) === "?" ? 700 : 400}
                fill={strokeColor}>
            {fmt(t)}
          </text>
        </g>
      ))}
    </g>
  );

  return (
    <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}
         preserveAspectRatio="xMidYMid meet" className="block max-w-[480px]" role="img">
      {/* faint alignment guides tie the paired ticks together */}
      {Array.from({ length: n }).map((_, i) => (
        <line key={`g-${i}`} x1={x1 + i * step} y1={topY + 4} x2={x1 + i * step} y2={botY - 4}
              stroke={strokeColor} strokeOpacity={0.18} strokeWidth={0.8} strokeDasharray="2 3" />
      ))}
      {line(topY, top, data.top_label, true)}
      {line(botY, bottom, data.bottom_label, false)}
    </svg>
  );
}

/**
 * Simple data table (frequency tables, ratio tables, coordinate tables).
 * Inherits the slide's text color; borders ride on currentColor so it works
 * on every projection theme.
 */
export function DataTable({ data }: { data: RenderData }) {
  const headers = data.headers ?? [];
  const rows = data.rows ?? [];
  if (headers.length === 0 && rows.length === 0) return null;
  const horizontal = data.orientation === "horizontal";
  return (
    <div className="inline-flex flex-col items-center gap-1">
      {data.title && <span className="text-sm font-semibold opacity-80">{data.title}</span>}
      <table className="border-collapse text-current" style={{ fontVariantNumeric: "tabular-nums" }}>
        {horizontal ? (
          <tbody>
            {headers.map((h, r) => (
              <tr key={r}>
                <th className="border border-current/40 bg-current/10 px-3 py-1.5 text-left text-sm font-bold">
                  {h}
                </th>
                {rows.map((row, c) => (
                  <td key={c} className="border border-current/40 px-3 py-1.5 text-center text-sm">
                    {row[r]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        ) : (
          <>
            <thead>
              <tr>
                {headers.map((h, i) => (
                  <th key={i} className="border border-current/40 bg-current/10 px-3 py-1.5 text-sm font-bold">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, r) => (
                <tr key={r}>
                  {row.map((cell, c) => (
                    <td key={c} className="border border-current/40 px-3 py-1.5 text-center text-sm">
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </>
        )}
      </table>
    </div>
  );
}

/**
 * Top-level dispatch: given a render_data block, returns the right
 * component. Used by ProblemsStage so it doesn't have to switch on type.
 */
export function InlineDiagram({
  data,
  strokeColor,
}: {
  data: RenderData | null | undefined;
  strokeColor?: string;
}) {
  if (!data) return null;
  const type = data.type;
  if (type === "number_line") {
    return <NumberLine data={data} strokeColor={strokeColor} />;
  }
  if (type === "number_line_point") {
    return <NumberLinePoint data={data} strokeColor={strokeColor} />;
  }
  if (type === "coordinate_grid") {
    return <CoordinateGrid data={data} strokeColor={strokeColor} />;
  }
  if (type === "hundredths_grid") {
    return <HundredthsGrid data={data} strokeColor={strokeColor} />;
  }
  if (type === "bar_model" || type === "percent_bar" || type === "tape_diagram") {
    return <BarModel data={data} strokeColor={strokeColor} />;
  }
  if (type === "fraction_bars") {
    return <FractionBars data={data} strokeColor={strokeColor} />;
  }
  if (type === "double_number_line") {
    return <DoubleNumberLine data={data} strokeColor={strokeColor} />;
  }
  if (type === "data_table") {
    return <DataTable data={data} />;
  }
  if (type === "svg_html" || data.svg_html) {
    return <SvgFigure html={data.svg_html ?? ""} />;
  }
  return null;
}
