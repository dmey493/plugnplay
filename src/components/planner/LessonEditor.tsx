"use client";

/**
 * One lesson: the activity palette on the left, the minute-by-minute
 * schedule on the right.
 *
 * Owns every block mutation and hands the parent a whole-lesson patch, so
 * the library above only ever does "replace this lesson" and never has to
 * know about drag geometry.
 */

import { useCallback, useMemo, useRef, useState } from "react";
import {
  DndContext,
  DragOverlay,
  KeyboardSensor,
  PointerSensor,
  pointerWithin,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import type { DragEndEvent, DragStartEvent } from "@dnd-kit/core";

import ActivityPalette, { PALETTE_PREFIX } from "./ActivityPalette";
import BlockDetails from "./BlockDetails";
import ScheduleGrid, { SLOT_PREFIX } from "./ScheduleGrid";
import type { ResizeEdge } from "./ScheduleGrid";

import { activityType } from "@/lib/classroom/activity-types";
import type { ActivityType } from "@/lib/classroom/activity-types";
import type { Lesson, PlanBlock } from "@/lib/classroom/lesson-plans";
import {
  SLOT_MIN,
  clamp,
  findFreeStart,
  lessonMinutes,
  newBlock,
  nextOpenStart,
  snap,
} from "@/lib/classroom/lesson-plans";

const FIELD =
  "w-full rounded-lg border-2 border-pnp-gray-300 px-2 py-1.5 text-sm text-pnp-navy placeholder:text-pnp-gray-400 focus-visible:border-pnp-accent focus-visible:outline-none";

interface Props {
  lesson: Lesson;
  /** The course's period, used when the lesson has no override. */
  coursePeriod: number;
  breadcrumb: string;
  onBack: () => void;
  onChange: (patch: Partial<Lesson>) => void;
}

export default function LessonEditor({
  lesson,
  coursePeriod,
  breadcrumb,
  onBack,
  onChange,
}: Props) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [dragging, setDragging] = useState<ActivityType | PlanBlock | null>(null);

  const period = lesson.periodMinutes ?? coursePeriod;

  const setBlocks = useCallback(
    (fn: (blocks: PlanBlock[]) => PlanBlock[]) => {
      onChange({ blocks: fn(lesson.blocks) });
    },
    [lesson.blocks, onChange]
  );

  /** Normalise a block against the grid and the period bounds. */
  const fit = useCallback(
    (b: PlanBlock): PlanBlock => {
      const minutes = clamp(snap(b.minutes), SLOT_MIN, period);
      return {
        ...b,
        minutes,
        startMin: clamp(snap(b.startMin), 0, Math.max(0, period - minutes)),
      };
    },
    [period]
  );

  const addBlock = useCallback(
    (type: ActivityType, at?: number) => {
      setBlocks((blocks) => {
        const start =
          at == null
            ? nextOpenStart(blocks, type.defaultMinutes, period)
            : findFreeStart(blocks, type.defaultMinutes, at, period);
        return [...blocks, newBlock(type.id, start)];
      });
    },
    [period, setBlocks]
  );

  const changeBlock = useCallback(
    (id: string, patch: Partial<PlanBlock>) => {
      setBlocks((blocks) =>
        blocks.map((b) => (b.id === id ? fit({ ...b, ...patch }) : b))
      );
    },
    [fit, setBlocks]
  );

  const removeBlock = useCallback(
    (id: string) => {
      setBlocks((blocks) => blocks.filter((b) => b.id !== id));
      setExpandedId((cur) => (cur === id ? null : cur));
    },
    [setBlocks]
  );

  // ── Resizing ────────────────────────────────────────────────────────
  // The grid reports a raw delta from where the pointer went down, so the
  // original geometry is held for the whole gesture and the delta always
  // applies to the same baseline.
  const resizeBase = useRef<{
    id: string;
    startMin: number;
    minutes: number;
  } | null>(null);

  const onResize = useCallback(
    (id: string, edge: ResizeEdge, deltaMin: number) => {
      setBlocks((blocks) => {
        const block = blocks.find((b) => b.id === id);
        if (!block) return blocks;

        if (!resizeBase.current || resizeBase.current.id !== id) {
          resizeBase.current = {
            id,
            startMin: block.startMin,
            minutes: block.minutes,
          };
        }
        const base = resizeBase.current;
        const end = base.startMin + base.minutes;

        let startMin = base.startMin;
        let minutes = base.minutes;

        if (edge === "top") {
          // Move the start, hold the end still.
          startMin = clamp(snap(base.startMin + deltaMin), 0, end - SLOT_MIN);
          minutes = end - startMin;
        } else {
          minutes = clamp(
            snap(base.minutes + deltaMin),
            SLOT_MIN,
            period - base.startMin
          );
        }

        return blocks.map((b) => (b.id === id ? { ...b, startMin, minutes } : b));
      });
    },
    [period, setBlocks]
  );

  const onResizeEnd = useCallback(() => {
    resizeBase.current = null;
  }, []);

  const tidy = useCallback(() => {
    setBlocks((blocks) => {
      let cursor = 0;
      return blocks
        .slice()
        .sort((a, b) => a.startMin - b.startMin)
        .map((b) => {
          const next = { ...b, startMin: cursor };
          cursor += b.minutes;
          return next;
        });
    });
  }, [setBlocks]);

  // ── Drag and drop ───────────────────────────────────────────────────
  const sensors = useSensors(
    // A few pixels of slop so a palette tile's click still fires, and so
    // clicking a block opens its details instead of nudging it.
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor)
  );

  const handleDragStart = useCallback(
    (e: DragStartEvent) => {
      const id = String(e.active.id);
      setDragging(
        id.startsWith(PALETTE_PREFIX)
          ? activityType(id.slice(PALETTE_PREFIX.length))
          : (lesson.blocks.find((b) => b.id === id) ?? null)
      );
    },
    [lesson.blocks]
  );

  const handleDragEnd = useCallback(
    (e: DragEndEvent) => {
      setDragging(null);
      const { active, over } = e;
      if (!over) return;

      const overId = String(over.id);
      if (!overId.startsWith(SLOT_PREFIX)) return;
      const minute = Number(overId.slice(SLOT_PREFIX.length));
      if (Number.isNaN(minute)) return;

      const activeId = String(active.id);

      if (activeId.startsWith(PALETTE_PREFIX)) {
        addBlock(activityType(activeId.slice(PALETTE_PREFIX.length)), minute);
        return;
      }

      setBlocks((blocks) =>
        blocks.map((b) =>
          b.id === activeId
            ? {
                ...b,
                startMin: findFreeStart(blocks, b.minutes, minute, period, b.id),
              }
            : b
        )
      );
    },
    [addBlock, period, setBlocks]
  );

  const expanded = useMemo(
    () => lesson.blocks.find((b) => b.id === expandedId) ?? null,
    [lesson.blocks, expandedId]
  );

  const used = lessonMinutes(lesson);
  const spare = period - used;

  return (
    <DndContext
      sensors={sensors}
      // A calendar wants the pointer's position to pick the slot, not the
      // centre of whatever is being dragged.
      collisionDetection={pointerWithin}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onDragCancel={() => setDragging(null)}
    >
      <div className="grid gap-4 lg:grid-cols-[220px_minmax(0,1fr)]">
        <aside className="order-1">
          <div className="sticky top-24 max-h-[calc(100vh-8rem)] overflow-y-auto rounded-xl border-2 border-pnp-navy bg-white shadow-[3px_3px_0_var(--pnp-navy)]">
            <ActivityPalette onAdd={(type) => addBlock(type)} />
          </div>
        </aside>

        <div className="order-2 min-w-0">
          <div className="mb-3 rounded-xl border-2 border-pnp-navy bg-white p-4 shadow-[3px_3px_0_var(--pnp-navy)]">
            <div className="mb-2 flex items-center gap-2">
              <button
                type="button"
                onClick={onBack}
                className="rounded px-1.5 py-1 text-xs font-bold text-pnp-accent hover:underline"
              >
                ← {breadcrumb}
              </button>
            </div>

            <input
              value={lesson.title}
              onChange={(e) => onChange({ title: e.target.value })}
              placeholder="Lesson title"
              className="w-full rounded border-2 border-transparent font-heading text-2xl font-extrabold text-pnp-navy hover:border-pnp-gray-200 focus-visible:border-pnp-accent focus-visible:outline-none"
              aria-label="Lesson title"
            />

            <div className="mt-3 grid gap-3 sm:grid-cols-4">
              <Field label="Standard">
                <input
                  value={lesson.standard}
                  onChange={(e) => onChange({ standard: e.target.value })}
                  placeholder="Optional"
                  className={FIELD}
                />
              </Field>
              <Field label="Period (min)">
                <input
                  type="number"
                  min={SLOT_MIN}
                  max={240}
                  step={SLOT_MIN}
                  value={period}
                  onChange={(e) =>
                    onChange({
                      periodMinutes: clamp(
                        snap(Number(e.target.value) || SLOT_MIN),
                        SLOT_MIN,
                        240
                      ),
                    })
                  }
                  className={FIELD}
                />
              </Field>
              <Field label="Objective">
                <input
                  value={lesson.objective}
                  onChange={(e) => onChange({ objective: e.target.value })}
                  placeholder="What students will be able to do"
                  className={FIELD}
                />
              </Field>
              <Field label="Materials">
                <input
                  value={lesson.materials}
                  onChange={(e) => onChange({ materials: e.target.value })}
                  placeholder="What you need on hand"
                  className={FIELD}
                />
              </Field>
            </div>

            <div className="mt-3">
              <Field label="Notes">
                <textarea
                  value={lesson.notes}
                  onChange={(e) => onChange({ notes: e.target.value })}
                  rows={2}
                  placeholder="Anything else that should print on the plan"
                  className={FIELD}
                />
              </Field>
            </div>
          </div>

          <div className="mb-3 flex flex-wrap items-center gap-3 rounded-lg border-2 border-pnp-navy bg-white px-3 py-2 text-sm font-semibold text-pnp-navy">
            <span className="tabular-nums">{used} min scheduled</span>
            <span className="font-medium text-pnp-gray-600">
              of {period}
              {spare > 0 && ` · ${spare} min open`}
              {spare < 0 && (
                <span className="text-pnp-red"> · {-spare} min over</span>
              )}
            </span>
            <button
              type="button"
              onClick={tidy}
              className="ml-auto rounded-lg border-2 border-pnp-navy px-2.5 py-1 text-xs font-bold text-pnp-navy transition-colors hover:bg-pnp-gray-100"
              title="Stack every activity end to end from the start of the period"
            >
              Close the gaps
            </button>
          </div>

          <ScheduleGrid
            blocks={lesson.blocks}
            periodMinutes={period}
            expandedId={expandedId}
            onExpand={setExpandedId}
            onResize={onResize}
            onResizeEnd={onResizeEnd}
          />
        </div>
      </div>

      <DragOverlay>
        {dragging && (
          <div
            className="rounded-lg border-2 border-pnp-navy px-2.5 py-1.5 shadow-[3px_3px_0_var(--pnp-navy)]"
            style={{
              backgroundColor:
                "typeId" in dragging
                  ? activityType(dragging.typeId).fill
                  : dragging.fill,
            }}
          >
            <span
              className={`text-[13px] font-bold ${
                ("typeId" in dragging
                  ? activityType(dragging.typeId).onFill
                  : dragging.onFill) === "white"
                  ? "text-white"
                  : "text-pnp-navy"
              }`}
            >
              {dragging.label}
            </span>
          </div>
        )}
      </DragOverlay>

      {expanded && (
        <BlockDetails
          block={expanded}
          contextLabel={lesson.title || "Lesson"}
          periodMinutes={period}
          onChange={changeBlock}
          onRemove={removeBlock}
          onClose={() => setExpandedId(null)}
        />
      )}
    </DndContext>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-bold uppercase tracking-wide text-pnp-gray-500">
        {label}
      </span>
      {children}
    </label>
  );
}
