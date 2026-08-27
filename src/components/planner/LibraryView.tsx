"use client";

/**
 * The file system for one course: units as folders, lessons inside them.
 *
 * Units sort newest first, so creating one puts it on top and pushes the
 * year's earlier work down. Older units collapse by default — after eight
 * months a teacher wants this week's folder open and September's shut.
 *
 * Nothing here is subject-specific. A unit is whatever the teacher names
 * it: "Unit 3 · Fractions", "Week of Oct 6", "Romeo and Juliet".
 */

import { useState } from "react";
import Button from "@/components/ui/Button";
import type { Course, Lesson, Unit } from "@/lib/classroom/lesson-plans";
import { lessonMinutes, periodFor } from "@/lib/classroom/lesson-plans";

interface Props {
  course: Course;
  onOpenLesson: (unitId: string, lessonId: string) => void;
  onAddUnit: () => void;
  onRenameUnit: (unitId: string, name: string) => void;
  onDeleteUnit: (unitId: string) => void;
  onToggleUnit: (unitId: string, collapsed: boolean) => void;
  onAddLesson: (unitId: string) => void;
  onDuplicateLesson: (unitId: string, lessonId: string) => void;
  onDeleteLesson: (unitId: string, lessonId: string) => void;
  onMoveLesson: (
    fromUnitId: string,
    lessonId: string,
    toUnitId: string
  ) => void;
}

function LessonRow({
  course,
  unit,
  lesson,
  units,
  onOpen,
  onDuplicate,
  onDelete,
  onMove,
}: {
  course: Course;
  unit: Unit;
  lesson: Lesson;
  units: Unit[];
  onOpen: () => void;
  onDuplicate: () => void;
  onDelete: () => void;
  onMove: (toUnitId: string) => void;
}) {
  const used = lessonMinutes(lesson);
  const period = periodFor(course, lesson);

  return (
    <li className="flex items-center gap-2 border-t border-pnp-gray-200 py-1.5 pl-6 pr-2 first:border-t-0">
      <button
        type="button"
        onClick={onOpen}
        className="min-w-0 flex-1 text-left"
      >
        <span className="block truncate text-sm font-semibold text-pnp-navy hover:underline">
          {lesson.title || "Untitled lesson"}
        </span>
        <span className="mt-0.5 flex flex-wrap items-center gap-x-2 text-[11px] text-pnp-gray-500">
          <span className="tabular-nums">
            {lesson.blocks.length}{" "}
            {lesson.blocks.length === 1 ? "activity" : "activities"}
          </span>
          <span className="tabular-nums">
            {used}/{period} min
          </span>
          {lesson.standard && (
            <span className="font-mono">{lesson.standard}</span>
          )}
          {lesson.objective && (
            <span className="truncate">{lesson.objective}</span>
          )}
        </span>
      </button>

      {units.length > 1 && (
        <select
          value=""
          onChange={(e) => e.target.value && onMove(e.target.value)}
          className="rounded border border-pnp-gray-300 bg-white px-1 py-0.5 text-[10px] text-pnp-gray-600"
          aria-label={`Move ${lesson.title} to another unit`}
          title="Move to another unit"
        >
          <option value="">Move…</option>
          {units
            .filter((u) => u.id !== unit.id)
            .map((u) => (
              <option key={u.id} value={u.id}>
                {u.name}
              </option>
            ))}
        </select>
      )}

      <button
        type="button"
        onClick={onDuplicate}
        className="rounded p-1 text-pnp-gray-500 hover:bg-pnp-gray-100 hover:text-pnp-navy"
        aria-label={`Duplicate ${lesson.title}`}
        title="Duplicate"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <rect x="9" y="9" width="12" height="12" rx="2" />
          <path d="M5 15V5a2 2 0 0 1 2-2h10" />
        </svg>
      </button>
      <button
        type="button"
        onClick={onDelete}
        className="rounded p-1 text-pnp-gray-500 hover:bg-pnp-red/10 hover:text-pnp-red"
        aria-label={`Delete ${lesson.title}`}
        title="Delete"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6" />
        </svg>
      </button>
    </li>
  );
}

function UnitFolder({
  course,
  unit,
  units,
  onOpenLesson,
  onRenameUnit,
  onDeleteUnit,
  onToggleUnit,
  onAddLesson,
  onDuplicateLesson,
  onDeleteLesson,
  onMoveLesson,
}: Props & { unit: Unit; units: Unit[] }) {
  const collapsed = unit.collapsed ?? false;

  return (
    <li className="overflow-hidden rounded-xl border-2 border-pnp-navy bg-white shadow-[3px_3px_0_var(--pnp-navy)]">
      <div className="flex items-center gap-2 border-b-2 border-pnp-navy bg-pnp-gray-50 px-2 py-2">
        <button
          type="button"
          onClick={() => onToggleUnit(unit.id, !collapsed)}
          className="rounded p-1 text-pnp-gray-600 hover:bg-pnp-gray-200 hover:text-pnp-navy"
          aria-expanded={!collapsed}
          aria-label={collapsed ? `Expand ${unit.name}` : `Collapse ${unit.name}`}
        >
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
            className={collapsed ? "" : "rotate-90"}
          >
            <path d="m9 18 6-6-6-6" />
          </svg>
        </button>

        <input
          value={unit.name}
          onChange={(e) => onRenameUnit(unit.id, e.target.value)}
          className="min-w-0 flex-1 rounded border-2 border-transparent bg-transparent font-heading text-base font-extrabold text-pnp-navy hover:border-pnp-gray-300 focus-visible:border-pnp-accent focus-visible:outline-none"
          aria-label="Unit name"
        />

        <span className="shrink-0 text-[11px] font-semibold text-pnp-gray-500">
          {unit.lessons.length}{" "}
          {unit.lessons.length === 1 ? "lesson" : "lessons"}
        </span>

        <button
          type="button"
          onClick={() => onAddLesson(unit.id)}
          className="shrink-0 rounded-lg border-2 border-pnp-navy bg-pnp-accent px-2 py-1 text-xs font-bold text-white shadow-[2px_2px_0_var(--pnp-navy)] hover:-translate-x-px hover:-translate-y-px active:translate-x-0.5 active:translate-y-0.5 active:shadow-none"
        >
          + Lesson
        </button>
        <button
          type="button"
          onClick={() => onDeleteUnit(unit.id)}
          className="shrink-0 rounded p-1 text-pnp-gray-500 hover:bg-pnp-red/10 hover:text-pnp-red"
          aria-label={`Delete ${unit.name}`}
          title="Delete unit"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6" />
          </svg>
        </button>
      </div>

      {!collapsed && (
        <ul>
          {unit.lessons.map((lesson) => (
            <LessonRow
              key={lesson.id}
              course={course}
              unit={unit}
              lesson={lesson}
              units={units}
              onOpen={() => onOpenLesson(unit.id, lesson.id)}
              onDuplicate={() => onDuplicateLesson(unit.id, lesson.id)}
              onDelete={() => onDeleteLesson(unit.id, lesson.id)}
              onMove={(toUnitId) => onMoveLesson(unit.id, lesson.id, toUnitId)}
            />
          ))}
          {unit.lessons.length === 0 && (
            <li className="px-6 py-4 text-sm text-pnp-gray-500">
              No lessons yet. Add one to start blocking out the period.
            </li>
          )}
        </ul>
      )}
    </li>
  );
}

export default function LibraryView(props: Props) {
  const { course, onAddUnit } = props;
  const [search, setSearch] = useState("");

  const q = search.trim().toLowerCase();
  const units = q
    ? course.units
        .map((u) => ({
          ...u,
          collapsed: false,
          lessons: u.lessons.filter(
            (l) =>
              l.title.toLowerCase().includes(q) ||
              l.standard.toLowerCase().includes(q) ||
              l.objective.toLowerCase().includes(q)
          ),
        }))
        .filter((u) => u.lessons.length > 0 || u.name.toLowerCase().includes(q))
    : course.units;

  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <Button tier="primary" size="small" onClick={onAddUnit}>
          + New unit
        </Button>
        <input
          type="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search lessons in this course…"
          className="min-w-[220px] flex-1 rounded-lg border-2 border-pnp-gray-300 px-3 py-1.5 text-sm text-pnp-navy placeholder:text-pnp-gray-400 focus-visible:border-pnp-accent focus-visible:outline-none"
        />
      </div>

      <ul className="flex flex-col gap-3">
        {units.map((unit) => (
          <UnitFolder
            key={unit.id}
            {...props}
            unit={unit}
            units={course.units}
          />
        ))}
      </ul>

      {units.length === 0 && (
        <p className="rounded-xl border-2 border-dashed border-pnp-gray-300 px-4 py-10 text-center text-sm text-pnp-gray-500">
          {q
            ? "Nothing matches that search."
            : "No units yet. Create one to start the year."}
        </p>
      )}
    </div>
  );
}
