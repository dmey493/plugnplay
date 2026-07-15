"use client";

import { useCallback, useRef } from "react";

/**
 * Docked text-tool controls, anchored above the bottom tool palette.
 *
 * Plain text is typed directly on the canvas (an inline caret at the click
 * point — see CanvasEngine's foreignObject editor); this dock carries the
 * Text/Math toggle and the symbol chips. In Math mode the dock grows into
 * the LaTeX editor: input + template chips + live preview, committed to the
 * anchor point on Enter.
 */

/** Symbol-palette chip. `insert` is spliced at the caret; `caret` (if set)
 *  positions the cursor that many chars into `insert` — e.g. inside braces. */
interface Chip {
  label: string;
  insert: string;
  title: string;
  caret?: number;
}

// Plain-text mode: real Unicode characters.
const TEXT_CHIPS: Chip[] = [
  { label: "×", insert: "×", title: "Times" },
  { label: "÷", insert: "÷", title: "Divide" },
  { label: "±", insert: "±", title: "Plus/minus" },
  { label: "≤", insert: "≤", title: "Less than or equal" },
  { label: "≥", insert: "≥", title: "Greater than or equal" },
  { label: "≠", insert: "≠", title: "Not equal" },
  { label: "≈", insert: "≈", title: "Approximately" },
  { label: "π", insert: "π", title: "Pi" },
  { label: "√", insert: "√", title: "Square root" },
  { label: "°", insert: "°", title: "Degree" },
  { label: "x²", insert: "²", title: "Squared" },
  { label: "x³", insert: "³", title: "Cubed" },
  { label: "½", insert: "½", title: "One half" },
  { label: "¼", insert: "¼", title: "One quarter" },
  { label: "¾", insert: "¾", title: "Three quarters" },
];

// Math mode: LaTeX snippets. Templates drop the caret between the braces.
const MATH_CHIPS: Chip[] = [
  { label: "a⁄b", insert: "\\frac{}{}", title: "Fraction", caret: 6 },
  { label: "xⁿ", insert: "^{}", title: "Exponent", caret: 2 },
  { label: "xₙ", insert: "_{}", title: "Subscript", caret: 2 },
  { label: "√", insert: "\\sqrt{}", title: "Square root", caret: 6 },
  { label: "ⁿ√", insert: "\\sqrt[]{}", title: "nth root", caret: 6 },
  { label: "π", insert: "\\pi ", title: "Pi" },
  { label: "×", insert: "\\times ", title: "Times" },
  { label: "÷", insert: "\\div ", title: "Divide" },
  { label: "±", insert: "\\pm ", title: "Plus/minus" },
  { label: "≤", insert: "\\le ", title: "Less than or equal" },
  { label: "≥", insert: "\\ge ", title: "Greater than or equal" },
  { label: "≠", insert: "\\ne ", title: "Not equal" },
  { label: "≈", insert: "\\approx ", title: "Approximately" },
  { label: "°", insert: "^{\\circ}", title: "Degree" },
  { label: "·", insert: "\\cdot ", title: "Dot multiply" },
];

export default function TextDock({
  isMath,
  value,
  onChange,
  onSetMath,
  onCommit,
  onCancel,
  onInsertPlain,
  mathPreview,
  katexReady,
}: {
  isMath: boolean;
  /** LaTeX source while in math mode (plain text lives in the canvas caret). */
  value: string;
  onChange: (value: string) => void;
  onSetMath: (math: boolean) => void;
  onCommit: () => void;
  onCancel: () => void;
  /** Insert a unicode snippet at the inline canvas caret (plain-text mode). */
  onInsertPlain: (snippet: string) => void;
  /** Pre-rendered KaTeX HTML for the live preview (null until katex loads). */
  mathPreview: string | null;
  katexReady: boolean;
}) {
  const inputRef = useRef<HTMLInputElement | null>(null);

  // Insert a snippet at the LaTeX input's caret (replacing any selection).
  // `caretInside` places the caret N chars into the snippet — e.g. inside
  // \frac{|}{} — so the teacher can keep typing the numerator immediately.
  const insertAtCursor = useCallback(
    (snippet: string, caretInside?: number) => {
      const el = inputRef.current;
      const start = el?.selectionStart ?? value.length;
      const end = el?.selectionEnd ?? start;
      const next = value.slice(0, start) + snippet + value.slice(end);
      const caret = start + (caretInside ?? snippet.length);
      onChange(next);
      requestAnimationFrame(() => {
        const e2 = inputRef.current;
        if (e2) {
          e2.focus();
          e2.setSelectionRange(caret, caret);
        }
      });
    },
    [value, onChange]
  );

  return (
    <div
      className="fixed bottom-24 left-1/2 z-[235] flex w-[30rem] max-w-[calc(100vw-2rem)] -translate-x-1/2 flex-col gap-1.5 rounded-lg border-2 border-pnp-navy bg-white/95 p-2 shadow-[3px_3px_0_var(--pnp-navy)] backdrop-blur-md"
      onPointerDown={(e) => e.stopPropagation()}
    >
      {/* Mode toggle + hint */}
      <div className="flex items-center gap-1">
        <div className="flex rounded-md border border-pnp-gray-200 p-0.5 text-xs font-semibold">
          <button
            type="button"
            onMouseDown={(e) => e.preventDefault()}
            onClick={() => onSetMath(false)}
            className={`rounded px-2 py-0.5 ${!isMath ? "bg-pnp-navy text-white" : "text-pnp-gray-600 hover:bg-pnp-gray-100"}`}
          >
            Text
          </button>
          <button
            type="button"
            onMouseDown={(e) => e.preventDefault()}
            onClick={() => onSetMath(true)}
            className={`rounded px-2 py-0.5 ${isMath ? "bg-pnp-navy text-white" : "text-pnp-gray-600 hover:bg-pnp-gray-100"}`}
          >
            Math
          </button>
        </div>
        <span className="ml-auto text-[0.7rem] text-pnp-gray-400">
          {isMath ? "Enter to place · Esc to cancel" : "Type on the board · Enter to place"}
        </span>
      </div>

      {/* Math mode: live preview + LaTeX input */}
      {isMath && (
        <>
          <div className="min-h-[2.25rem] overflow-x-auto rounded border border-pnp-gray-100 bg-pnp-gray-50 px-2 py-1 text-pnp-gray-900">
            {value.trim() ? (
              mathPreview ? (
                <span dangerouslySetInnerHTML={{ __html: mathPreview }} />
              ) : (
                <span className="text-xs text-pnp-gray-400">
                  {katexReady ? "…" : "Loading math…"}
                </span>
              )
            ) : (
              <span className="text-xs text-pnp-gray-400">Preview</span>
            )}
          </div>
          <input
            ref={inputRef}
            autoFocus
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                onCommit();
              } else if (e.key === "Escape") {
                e.preventDefault();
                onCancel();
              }
              e.stopPropagation();
            }}
            placeholder="LaTeX — e.g. \frac{3}{4}x^2"
            className="w-full rounded border border-pnp-accent px-2 py-1 font-mono text-sm text-pnp-gray-900 outline-none"
          />
        </>
      )}

      {/* Symbol / template palette */}
      <div className="flex flex-wrap gap-1">
        {(isMath ? MATH_CHIPS : TEXT_CHIPS).map((c) => (
          <button
            key={c.label}
            type="button"
            title={c.title}
            onMouseDown={(e) => e.preventDefault()}
            onClick={() => (isMath ? insertAtCursor(c.insert, c.caret) : onInsertPlain(c.insert))}
            className="flex h-7 min-w-[1.75rem] items-center justify-center rounded border border-pnp-gray-200 px-1.5 text-sm text-pnp-gray-800 hover:bg-pnp-gray-100 hover:text-pnp-navy"
          >
            {c.label}
          </button>
        ))}
      </div>
    </div>
  );
}
