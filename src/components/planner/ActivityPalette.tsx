"use client";

/**
 * The activity palette — generic types, not specific resources.
 *
 * Each tile is draggable onto the schedule and clickable to drop into the
 * first open gap. The click path matters: it is the only route for keyboard
 * and screen-reader users, and it is faster than dragging when the schedule
 * is still mostly empty.
 */

import { useDraggable } from "@dnd-kit/core";
import { ACTIVITY_TYPES, GROUP_LABEL } from "@/lib/activity-types";
import type { ActivityGroup, ActivityType } from "@/lib/activity-types";

export const PALETTE_PREFIX = "type:";

function PaletteTile({
  type,
  onAdd,
}: {
  type: ActivityType;
  onAdd: (type: ActivityType) => void;
}) {
  const { attributes, listeners, setNodeRef, isDragging } = useDraggable({
    id: `${PALETTE_PREFIX}${type.id}`,
    data: { source: "palette", type },
  });

  return (
    <li className="relative">
      <button
        ref={setNodeRef}
        type="button"
        {...listeners}
        {...attributes}
        onClick={() => onAdd(type)}
        style={{ backgroundColor: type.fill }}
        className={`w-full cursor-grab touch-none rounded-lg border-2 border-pnp-navy px-2.5 py-2 text-left shadow-[2px_2px_0_var(--pnp-navy)] transition-transform hover:-translate-x-px hover:-translate-y-px active:cursor-grabbing focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-pnp-accent ${
          type.onFill === "white" ? "text-white" : "text-pnp-navy"
        } ${isDragging ? "opacity-40" : ""}`}
        title={`${type.hint} · drag onto the schedule, or click to drop it in the next gap`}
      >
        <span className="flex items-baseline justify-between gap-2">
          <span className="text-[13px] font-bold leading-tight">{type.label}</span>
          <span className="shrink-0 text-[11px] font-semibold tabular-nums opacity-90">
            {type.defaultMinutes}m
          </span>
        </span>
        <span className="mt-0.5 block text-[11px] leading-snug opacity-90">
          {type.hint}
        </span>
      </button>
    </li>
  );
}

export default function ActivityPalette({
  onAdd,
  targetLabel,
}: {
  onAdd: (type: ActivityType) => void;
  /** In the week view, names the day a click will drop into, since a click
   *  has no column to infer it from. Omitted in the day view. */
  targetLabel?: string;
}) {
  const groups: ActivityGroup[] = ["phase", "format", "blank"];

  return (
    <div className="flex flex-col gap-4 p-3">
      <p className="text-xs leading-snug text-pnp-gray-600">
        Drag onto the schedule, or click to drop into the next open gap
        {targetLabel ? ` on ${targetLabel}` : ""}. Click a placed activity to
        open its details.
      </p>

      {groups.map((g) => (
        <div key={g}>
          <h2 className="mb-1.5 text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
            {GROUP_LABEL[g]}
          </h2>
          <ul className="flex flex-col gap-1.5">
            {ACTIVITY_TYPES.filter((t) => t.group === g).map((t) => (
              <PaletteTile key={t.id} type={t} onAdd={onAdd} />
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
