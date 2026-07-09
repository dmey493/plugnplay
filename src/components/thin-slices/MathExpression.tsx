"use client";

import React from "react";

interface Props {
  /**
   * Author markup. Supports:
   *   - `\frac{numerator}{denominator}` — stacked fraction
   *   - `\sqrt{contents}`               — square root with overhead bar
   * Everything else renders as plain text. Braces nest correctly:
   * `\frac{x + 3}{2}` works, `\sqrt{\frac{1}{2}}` (nested) works.
   */
  text: string;
  className?: string;
}

/**
 * Tiny renderer that turns `\frac{a}{b}` into a stacked fraction (a / b with
 * a horizontal bar between them) and leaves the rest of the string alone.
 *
 * Why a custom parser rather than KaTeX/MathJax: thin-slice content is short,
 * the syntax we care about is just `\frac{}{}`, and a 50-line parser keeps the
 * bundle small and the styling under our direct control.
 */
export default function MathExpression({ text, className = "" }: Props) {
  const nodes = parse(text);
  return (
    <span className={`math-expression inline-flex flex-wrap items-center justify-center gap-x-1 ${className}`}>
      {nodes.map((n, i) => (
        <Node key={i} node={n} />
      ))}
    </span>
  );
}

// =====================
// Node types
// =====================

type Node =
  | { kind: "text"; value: string }
  | { kind: "frac"; num: Node[]; den: Node[] }
  | { kind: "sqrt"; inner: Node[] };

function Node({ node }: { node: Node }) {
  if (node.kind === "text") {
    // Preserve internal spaces but allow line wrap on space.
    return <span className="whitespace-pre-wrap">{node.value}</span>;
  }
  if (node.kind === "frac") {
    return (
      <span className="math-frac inline-flex flex-col items-center align-middle leading-none">
        <span className="math-frac-num px-1.5 pb-0.5">
          {node.num.map((n, i) => (
            <Node key={i} node={n} />
          ))}
        </span>
        <span className="math-frac-bar h-[2px] w-full bg-current" />
        <span className="math-frac-den px-1.5 pt-0.5">
          {node.den.map((n, i) => (
            <Node key={i} node={n} />
          ))}
        </span>
      </span>
    );
  }
  // Square root: radical sign + content under an overhead bar.
  return (
    <span className="math-sqrt inline-flex items-center align-middle leading-none">
      <span className="math-sqrt-radical pr-0.5" aria-hidden="true">√</span>
      <span className="math-sqrt-inner border-t-2 border-current px-1 pt-0.5">
        {node.inner.map((n, i) => (
          <Node key={i} node={n} />
        ))}
      </span>
    </span>
  );
}

// =====================
// Parser
// =====================

/**
 * Walk the source string. When we hit `\frac{`, consume the balanced numerator,
 * then expect `{` and consume the balanced denominator. Recurse into both so
 * nested fractions work. Anything else accumulates into a text node.
 */
function parse(src: string): Node[] {
  const out: Node[] = [];
  let i = 0;
  let buf = "";

  while (i < src.length) {
    if (src.startsWith("\\frac{", i)) {
      if (buf) {
        out.push({ kind: "text", value: buf });
        buf = "";
      }
      i += 6; // past \frac{
      const numEnd = matchBrace(src, i);
      if (numEnd < 0) {
        buf += "\\frac{";
        continue;
      }
      const numSrc = src.slice(i, numEnd);
      i = numEnd + 1;

      if (src[i] !== "{") {
        buf += "\\frac{" + numSrc + "}";
        continue;
      }
      i += 1;
      const denEnd = matchBrace(src, i);
      if (denEnd < 0) {
        buf += "\\frac{" + numSrc + "}{";
        continue;
      }
      const denSrc = src.slice(i, denEnd);
      i = denEnd + 1;

      out.push({ kind: "frac", num: parse(numSrc), den: parse(denSrc) });
    } else if (src.startsWith("\\sqrt{", i)) {
      if (buf) {
        out.push({ kind: "text", value: buf });
        buf = "";
      }
      i += 6; // past \sqrt{
      const innerEnd = matchBrace(src, i);
      if (innerEnd < 0) {
        buf += "\\sqrt{";
        continue;
      }
      const innerSrc = src.slice(i, innerEnd);
      i = innerEnd + 1;
      out.push({ kind: "sqrt", inner: parse(innerSrc) });
    } else {
      buf += src[i];
      i += 1;
    }
  }
  if (buf) out.push({ kind: "text", value: buf });
  return out;
}

/**
 * Given the index just *past* an opening `{`, return the index of the matching
 * closing `}`. Returns -1 if unbalanced. Handles nested braces.
 */
function matchBrace(src: string, start: number): number {
  let depth = 1;
  for (let i = start; i < src.length; i++) {
    if (src[i] === "{") depth += 1;
    else if (src[i] === "}") {
      depth -= 1;
      if (depth === 0) return i;
    }
  }
  return -1;
}
