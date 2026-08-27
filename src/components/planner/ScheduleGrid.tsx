"use client";

/**
 * The lesson schedule — an Outlook-style calendar column for one period.
 *
 * The axis is ELAPSED MINUTES, 0 at the top down to the length of the
 * period, ruled every 5 minutes the way Outlook rules every 30.
 *
 * Two layers, deliberately:
 *   - slot layer: the drop targets, one per 5 minutes. dnd-kit measures
 *     droppables geometrically rather than by DOM hit-testing, so the block
 *     layer above never steals a drop.
 *   - block layer: pointer-events-none, with each block re-enabling them,
 *     so the gaps between blocks stay droppable.
 *
 * Blocks resize from EITHER end. Dragging the top edge moves the start and
 * holds the end still; dragging the bottom edge moves the end. That is the
 * Outlook behaviour and it saves a move-then-resize for "start this later".
 */

import { useCallback, useEffect, useRef } from "react";
import { useDraggable, useDroppable } from "@dnd-kit/core";
import { activityType } from "@/lib/classroom/activity-types";
import type { PlanBlock } from "@/lib/classroom/lesson-plans";
import { SLOT_MIN, blockEnd, overlaps } from "@/lib/classroom/lesson-plans";

/** Pixels per minute. 5 minutes = 30px keeps the shortest block tappable. */
export const PX_PER_MIN = 30 / SLOT_MIN;

export const SLOT_PREFIX = "slot:";

export type ResizeEdge = "top" | "bottom";

function Slot({ minute }: { minute: number }) {
  const { setNodeRef, isOver } = useDroppable({ id: `${SLOT_PREFIX}${minute}` });
  const major = minute % 15 === 0;

  return (
    <div
      ref={setNodeRef}
      style={{ height: SLOT_MIN * PX_PER_MIN }}
      className={`border-t ${
        major ? "border-pnp-gray-300" : "border-pnp-gray-200"
      } ${isOver ? "bg-pnp-accent-soft" : ""}`}
    />
  );
}

/** Two dots: the grab affordance on each end of a block. */
function Grip() {
  return (
    <span className="flex items-center justify-center gap-1" aria-hidden="true">
      <span className="h-1 w-1 rounded-full bg-black/40" />
      <span className="h-1 w-1 rounded-full bg-black/40" />
    </span>
  );
}

interface BlockProps {
  block: PlanBlock;
  conflicting: boolean;
  expanded: boolean;
  onExpand: (id: string) => void;
  onResize: (id: string, edge: ResizeEdge, deltaMin: number) => void;
  onResizeEnd: () => void;
}

function ScheduledBlock({
  block,
  conflicting,
  expanded,
  onExpand,
  onResize,
  onResizeEnd,
}: BlockProps) {
  const type = activityType(block.typeId);
  const { attributes, listeners, setNodeRef, isDragging } = useDraggable({
    id: block.id,
    data: { source: "schedule" },
  });

  const height = block.minutes * PX_PER_MIN;
  const roomForMeta = height >= 44;
  const roomForNote = height >= 68;

  // ── Resize from either edge ─────────────────────────────────────────
  // Hand-rolled: dnd-kit moves things, it does not resize them. The
  // listeners live on window so the drag survives leaving the 10px handle.
  const resizing = useRef<{ edge: ResizeEdge; startY: number } | null>(null);

  const onPointerMove = useCallback(
    (e: PointerEvent) => {
      const r = resizing.current;
      if (!r) return;
      onResize(block.id, r.edge, (e.clientY - r.startY) / PX_PER_MIN);
    },
    [block.id, onResize]
  );

  const stop = useCallback(() => {
    if (!resizing.current) return;
    resizing.current = null;
    onResizeEnd();
  }, [onResizeEnd]);

  useEffect(() => {
    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", stop);
    window.addEventListener("pointercancel", stop);
    return () => {
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", stop);
      window.removeEventListener("pointercancel", stop);
    };
  }, [onPointerMove, stop]);

  const beginResize = (edge: ResizeEdge) => (e: React.PointerEvent) => {
    e.preventDefault();
    e.stopPropagation();
    resizing.current = { edge, startY: e.clientY };
  };

  return (
    <div
      // The whole block is the draggable node (dnd-kit measures from this
      // element); the button inside is the activator carrying the listeners,
      // so the two resize handles stay clear of the drag sensor.
      ref={setNodeRef}
      data-block-id={block.id}
      style={{
        top: block.startMin * PX_PER_MIN,
        height,
        backgroundColor: type.fill,
      }}
      className={`pointer-events-auto absolute inset-x-1 overflow-hidden rounded-lg border-2 shadow-[2px_2px_0_var(--pnp-navy)] ${
        conflicting ? "border-pnp-red" : "border-pnp-navy"
      } ${isDragging ? "opacity-50" : ""} ${
        expanded ? "z-20 ring-2 ring-pnp-navy ring-offset-1" : "z-10"
      }`}
    >
      <div
        onPointerDown={beginResize("top")}
        className="absolute inset-x-0 top-0 z-10 h-2.5 cursor-ns-resize touch-none pt-0.5"
        title="Drag to change when this starts"
      >
        <Grip />
      </div>

      <button
        type="button"
        {...listeners}
        {...attributes}
        onClick={() => onExpand(block.id)}
        className={`h-full w-full cursor-grab touch-none px-2 py-2.5 text-left active:cursor-grabbing ${
          type.onFill === "white" ? "text-white" : "text-pnp-navy"
        }`}
        aria-label={`${block.label}, ${block.minutes} minutes, starting at minute ${block.startMin}. Drag to move, click for details.`}
        aria-expanded={expanded}
      >
        <span className="block truncate text-[13px] font-bold leading-tight">
          {block.label || type.label}
        </span>
        {roomForMeta && (
          <span className="block truncate text-[11px] font-medium opacity-90">
            {block.startMin}–{blockEnd(block)} min · {block.minutes} min
          </span>
        )}
        {roomForNote && block.note && (
          <span className="mt-0.5 block truncate text-[11px] italic opacity-90">
            {block.note}
          </span>
        )}
      </button>

      <div
        onPointerDown={beginResize("bottom")}
        className="absolute inset-x-0 bottom-0 z-10 h-2.5 cursor-ns-resize touch-none pb-0.5"
        title="Drag to change how long this runs"
      >
        <Grip />
      </div>
    </div>
  );
}

interface Props {
  blocks: PlanBlock[];
  periodMinutes: number;
  expandedId: string | null;
  onExpand: (id: string) => void;
  onResize: (id: string, edge: ResizeEdge, deltaMin: number) => void;
  onResizeEnd: () => void;
}

export default function ScheduleGrid({
  blocks,
  periodMinutes,
  expandedId,
  onExpand,
  onResize,
  onResizeEnd,
}: Props) {
  const slots: number[] = [];
  for (let m = 0; m < periodMinutes; m += SLOT_MIN) slots.push(m);

  const conflicted = new Set<string>();
  for (const a of blocks) {
    for (const b of blocks) {
      if (a.id !== b.id && overlaps(a, b)) conflicted.add(a.id);
    }
  }

  return (
    <div className="rounded-xl border-2 border-pnp-navy bg-white">
      <div
        className="flex"
        style={{ height: slots.length * SLOT_MIN * PX_PER_MIN }}
      >
        {/* Minute gutter — 0 at the top, counting up to the bell. */}
        <div className="w-14 shrink-0 border-r-2 border-pnp-navy">
          {slots.map((m) => (
            <div
              key={m}
              style={{ height: SLOT_MIN * PX_PER_MIN }}
              className={`border-t pr-2 text-right text-[11px] tabular-nums leading-none ${
                m % 15 === 0
                  ? "border-pnp-gray-300 font-semibold text-pnp-gray-600"
                  : "border-pnp-gray-200 text-pnp-gray-400"
              }`}
            >
              <span className="relative -top-1.5 bg-white px-0.5">{m}</span>
            </div>
          ))}
        </div>

        <div className="relative min-w-0 flex-1">
          <div className="absolute inset-0">
            {slots.map((m) => (
              <Slot key={m} minute={m} />
            ))}
          </div>

          <div className="pointer-events-none absolute inset-0">
            {blocks.map((b) => (
              <ScheduledBlock
                key={b.id}
                block={b}
                conflicting={conflicted.has(b.id)}
                expanded={expandedId === b.id}
                onExpand={onExpand}
                onResize={onResize}
                onResizeEnd={onResizeEnd}
              />
            ))}
          </div>

          {blocks.length === 0 && (
            <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
              <p className="max-w-xs text-center text-sm text-pnp-gray-500">
                Drag an activity from the left onto the minute you want it to
                start.
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="flex border-t-2 border-pnp-navy bg-pnp-gray-50">
        <div className="w-14 shrink-0 border-r-2 border-pnp-navy pr-2 text-right text-[11px] font-bold tabular-nums text-pnp-navy">
          {periodMinutes}
        </div>
        <div className="flex-1 px-2 text-[11px] font-semibold text-pnp-gray-500">
          End of period
        </div>
      </div>
    </div>
  );
}
