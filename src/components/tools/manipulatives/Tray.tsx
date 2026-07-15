"use client";

import { KINDS, VariantPreview, type Variant } from "./registry";

/** Left-hand palette of manipulative sources. Clicking a chip drops a fresh
 *  piece onto the board (the board decides where — at the viewport centre,
 *  offset-stacked so repeats don't perfectly overlap). Collapsible: when
 *  `onToggle` is provided a header button (open) / slim vertical tab
 *  (closed) lets the teacher tuck the tray away — the whiteboard entry
 *  point starts it closed. */
export default function Tray({
  onAdd,
  open = true,
  onToggle,
}: {
  onAdd: (sample: Variant["sample"]) => void;
  open?: boolean;
  onToggle?: () => void;
}) {
  if (!open) {
    return (
      <button
        type="button"
        onClick={onToggle}
        title="Show manipulatives"
        className="flex h-full w-9 shrink-0 items-center justify-center border-r-2 border-pnp-navy bg-pnp-blue/25 transition-colors hover:bg-pnp-blue/40"
      >
        <span className="rotate-180 font-heading text-xs font-bold uppercase tracking-wide text-pnp-navy [writing-mode:vertical-rl]">
          Manipulatives ▸
        </span>
      </button>
    );
  }
  return (
    <aside className="flex h-full w-44 shrink-0 flex-col gap-4 overflow-y-auto border-r-2 border-pnp-navy bg-pnp-blue/15 p-3">
      {onToggle && (
        <button
          type="button"
          onClick={onToggle}
          title="Hide manipulatives"
          className="flex items-center justify-between rounded-md px-1 py-0.5 font-heading text-xs font-bold uppercase tracking-wide text-pnp-navy/70 transition-colors hover:bg-pnp-blue/20 hover:text-pnp-navy"
        >
          Hide tray
          <span aria-hidden="true">◂</span>
        </button>
      )}
      {KINDS.map((k) => (
        <section key={k.kind}>
          <h2 className="mb-1.5 font-heading text-xs font-bold uppercase tracking-wide text-pnp-navy/70">
            {k.label}
          </h2>
          <div className="flex flex-wrap gap-1.5">
            {k.variants.map((v) => (
              <button
                key={v.id}
                type="button"
                onClick={() => onAdd(v.sample)}
                title={`Add ${v.label}`}
                aria-label={`Add ${k.label} ${v.label}`}
                className="flex flex-col items-center gap-0.5 rounded-md border-2 border-pnp-navy bg-white p-1 shadow-[2px_2px_0_var(--pnp-navy)] transition-transform hover:-translate-y-0.5 active:translate-x-[2px] active:translate-y-[2px] active:shadow-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent"
              >
                <VariantPreview sample={v.sample} box={40} />
                <span className="text-[0.65rem] font-semibold leading-none text-pnp-navy">{v.label}</span>
              </button>
            ))}
          </div>
        </section>
      ))}
    </aside>
  );
}
