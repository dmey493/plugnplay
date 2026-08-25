"use client";

/**
 * The expanded activity card.
 *
 * A 5-minute block is 30px tall, so the details cannot live inside it.
 * Clicking a block opens this card anchored beside it — the same move as
 * Outlook's appointment peek — with every field the block carries.
 *
 * Anchoring: the card is `position: fixed` and finds its block through the
 * `data-block-id` attribute, which lets it escape the grid's horizontal
 * scroll container. Position is recomputed on scroll and resize while open.
 */

import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { ACTIVITY_TYPES, activityType } from "@/lib/activity-types";
import type { Grouping, PlanBlock } from "@/lib/lesson-plans";
import { GROUPING_LABEL, SLOT_MIN, blockEnd } from "@/lib/lesson-plans";

const CARD_W = 320;
const GAP = 10;
/** Used only to keep the card on screen before it has been measured. */
const CARD_H_ESTIMATE = 460;

const FIELD =
  "w-full rounded-lg border-2 border-pnp-gray-300 px-2 py-1.5 text-sm text-pnp-navy placeholder:text-pnp-gray-400 focus-visible:border-pnp-accent focus-visible:outline-none";

const LABEL =
  "mb-1 block text-xs font-bold uppercase tracking-wide text-pnp-gray-500";

interface Props {
  block: PlanBlock;
  /** Shown in the card header for context, e.g. the lesson title. */
  contextLabel: string;
  periodMinutes: number;
  onChange: (id: string, patch: Partial<PlanBlock>) => void;
  onRemove: (id: string) => void;
  onClose: () => void;
}

export default function BlockDetails({
  block,
  contextLabel,
  periodMinutes,
  onChange,
  onRemove,
  onClose,
}: Props) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState<{ top: number; left: number } | null>(null);

  const place = useCallback(() => {
    const anchor = document.querySelector<HTMLElement>(
      `[data-block-id="${block.id}"]`
    );
    if (!anchor) return;
    const r = anchor.getBoundingClientRect();
    const h = cardRef.current?.offsetHeight ?? CARD_H_ESTIMATE;

    // Prefer the right of the block; flip left when it would run off.
    const left =
      r.right + GAP + CARD_W <= window.innerWidth
        ? r.right + GAP
        : Math.max(GAP, r.left - GAP - CARD_W);

    const top = Math.min(
      Math.max(GAP, r.top),
      Math.max(GAP, window.innerHeight - h - GAP)
    );

    setPos({ top, left });
  }, [block.id]);

  useLayoutEffect(place, [place, block.startMin, block.minutes]);

  useEffect(() => {
    window.addEventListener("scroll", place, true);
    window.addEventListener("resize", place);
    return () => {
      window.removeEventListener("scroll", place, true);
      window.removeEventListener("resize", place);
    };
  }, [place]);

  // Escape closes, matching every other transient surface in the app.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const type = activityType(block.typeId);
  const set = (patch: Partial<PlanBlock>) => onChange(block.id, patch);

  return (
    <>
      {/* Click-away layer. Transparent: the schedule stays readable. */}
      <div className="fixed inset-0 z-40" onClick={onClose} aria-hidden="true" />

      <div
        ref={cardRef}
        role="dialog"
        aria-label={`Details for ${block.label}`}
        style={{
          top: pos?.top ?? -9999,
          left: pos?.left ?? -9999,
          width: CARD_W,
        }}
        className="fixed z-50 max-h-[85vh] overflow-y-auto rounded-xl border-2 border-pnp-navy bg-white shadow-[4px_4px_0_var(--pnp-navy)]"
      >
        <div
          className="flex items-center gap-2 border-b-2 border-pnp-navy px-3 py-2"
          style={{ backgroundColor: type.fill }}
        >
          <span
            className={`text-xs font-bold ${
              type.onFill === "white" ? "text-white" : "text-pnp-navy"
            }`}
          >
            {contextLabel ? `${contextLabel} · ` : ""}minute {block.startMin} to {blockEnd(block)}
          </span>
          <button
            type="button"
            onClick={onClose}
            className={`ml-auto rounded p-0.5 ${
              type.onFill === "white"
                ? "text-white hover:bg-white/20"
                : "text-pnp-navy hover:bg-black/10"
            }`}
            aria-label="Close details"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" aria-hidden="true">
              <path d="M18 6 6 18M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="grid gap-3 p-3">
          <label className="block">
            <span className={LABEL}>Activity name</span>
            <input
              value={block.label}
              onChange={(e) => set({ label: e.target.value })}
              placeholder={type.label}
              className={FIELD}
              autoFocus
            />
          </label>

          <label className="block">
            <span className={LABEL}>Type</span>
            <select
              value={block.typeId}
              onChange={(e) => {
                const next = activityType(e.target.value);
                // Rename along with the type only if the teacher never
                // customised the name, so their words always survive.
                const untouched = block.label === type.label;
                set({ typeId: next.id, ...(untouched ? { label: next.label } : {}) });
              }}
              className={FIELD}
            >
              {ACTIVITY_TYPES.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.label}
                </option>
              ))}
            </select>
          </label>

          <div className="grid grid-cols-2 gap-3">
            <label className="block">
              <span className={LABEL}>Starts at (min)</span>
              <input
                type="number"
                min={0}
                max={Math.max(0, periodMinutes - SLOT_MIN)}
                step={SLOT_MIN}
                value={block.startMin}
                onChange={(e) => set({ startMin: Number(e.target.value) || 0 })}
                className={FIELD}
              />
            </label>
            <label className="block">
              <span className={LABEL}>Length (min)</span>
              <input
                type="number"
                min={SLOT_MIN}
                max={periodMinutes}
                step={SLOT_MIN}
                value={block.minutes}
                onChange={(e) =>
                  set({ minutes: Number(e.target.value) || SLOT_MIN })
                }
                className={FIELD}
              />
            </label>
          </div>

          <label className="block">
            <span className={LABEL}>Grouping</span>
            <select
              value={block.grouping ?? ""}
              onChange={(e) => set({ grouping: e.target.value as Grouping })}
              className={FIELD}
            >
              <option value="">Not set</option>
              {Object.entries(GROUPING_LABEL).map(([k, v]) => (
                <option key={k} value={k}>
                  {v}
                </option>
              ))}
            </select>
          </label>

          <label className="block">
            <span className={LABEL}>Summary</span>
            <input
              value={block.note ?? ""}
              onChange={(e) => set({ note: e.target.value })}
              placeholder="One line, shown on the block itself"
              className={FIELD}
            />
          </label>

          <label className="block">
            <span className={LABEL}>Details</span>
            <textarea
              value={block.details ?? ""}
              onChange={(e) => set({ details: e.target.value })}
              rows={4}
              placeholder="What happens, teacher moves, what to watch for"
              className={FIELD}
            />
          </label>

          <label className="block">
            <span className={LABEL}>Materials</span>
            <input
              value={block.materials ?? ""}
              onChange={(e) => set({ materials: e.target.value })}
              placeholder="Just for this activity"
              className={FIELD}
            />
          </label>

          <button
            type="button"
            onClick={() => onRemove(block.id)}
            className="justify-self-start rounded-lg border-2 border-pnp-red px-3 py-1.5 text-sm font-bold text-pnp-red transition-colors hover:bg-pnp-red/10"
          >
            Remove activity
          </button>
        </div>
      </div>
    </>
  );
}
