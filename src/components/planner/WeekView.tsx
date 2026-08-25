"use client";

/**
 * The weekly schedule: every prep at a glance.
 *
 * Rows are courses, columns are days, and each cell names the lesson that
 * course is running that day. This is the view a teacher with three preps
 * actually needs, and the one you would hand to an administrator.
 *
 * A cell holds a LIVE LINK to a lesson in the curriculum, not a copy — fix
 * a typo in the lesson and every week using it updates. "Make a copy"
 * detaches a single cell when one day has to deviate, which leaves the
 * source lesson alone.
 */

import { useState } from "react";
import Button from "@/components/ui/Button";
import type { Course, Library, Week, WeekCell } from "@/lib/lesson-plans";
import {
  DAY_LABELS,
  cellLesson,
  lessonMinutes,
  weekDayPeriod,
} from "@/lib/lesson-plans";

interface Props {
  library: Library;
  week: Week | null;
  weeks: Week[];
  onSelectWeek: (id: string) => void;
  onAddWeek: () => void;
  onRenameWeek: (label: string) => void;
  onDateWeek: (startDate: string) => void;
  onDeleteWeek: () => void;
  onSetCell: (courseId: string, day: number, lessonId: string) => void;
  onClearCell: (cellId: string) => void;
  onDetachCell: (cellId: string) => void;
  onReattachCell: (cellId: string) => void;
  onNoteCell: (cellId: string, note: string) => void;
  onOpenLesson: (courseId: string, lessonId: string) => void;
  /** null clears the override and returns the day to each course's usual. */
  onSetDayMinutes: (day: number, minutes: number | null) => void;
}

/**
 * The length of one day. Normally blank (every course runs its usual
 * period); on an assembly or a two-hour delay the teacher sets it here once
 * and every course on that day is measured against it.
 */
function DayLengthButton({
  minutes,
  onSet,
}: {
  minutes: number | null;
  onSet: (m: number | null) => void;
}) {
  const [editing, setEditing] = useState(false);

  if (editing) {
    return (
      <span className="flex items-center gap-1">
        <input
          type="number"
          min={5}
          max={240}
          step={5}
          autoFocus
          defaultValue={minutes ?? ""}
          placeholder="usual"
          onBlur={(e) => {
            const v = e.target.value.trim();
            onSet(v === "" ? null : Math.max(5, Number(v) || 5));
            setEditing(false);
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter") (e.target as HTMLInputElement).blur();
            if (e.key === "Escape") setEditing(false);
          }}
          className="w-16 rounded border-2 border-pnp-accent px-1 py-0.5 text-[11px] text-pnp-navy focus-visible:outline-none"
          aria-label="Minutes for this day"
        />
      </span>
    );
  }

  return (
    <button
      type="button"
      onClick={() => setEditing(true)}
      className={`rounded border px-1.5 py-0.5 text-[10px] font-bold ${
        minutes == null
          ? "border-pnp-gray-300 text-pnp-gray-500 hover:border-pnp-navy hover:text-pnp-navy"
          : "border-pnp-orange bg-pnp-orange/10 text-pnp-orange"
      }`}
      title={
        minutes == null
          ? "This day runs each course's usual period. Click to shorten or lengthen it."
          : `This day is ${minutes} minutes for every course. Click to change or clear.`
      }
    >
      {minutes == null ? "Usual length" : `${minutes} min`}
    </button>
  );
}

function Cell({
  library,
  course,
  day,
  period,
  cell,
  onSet,
  onClear,
  onDetach,
  onReattach,
  onNote,
  onOpen,
}: {
  library: Library;
  course: Course;
  day: number;
  period: number;
  cell: WeekCell | undefined;
  onSet: (lessonId: string) => void;
  onClear: () => void;
  onDetach: () => void;
  onReattach: () => void;
  onNote: (note: string) => void;
  onOpen: (lessonId: string) => void;
}) {
  const lesson = cell ? cellLesson(library, cell) : null;
  const detached = Boolean(cell?.detached);

  return (
    <td className="w-1/5 border-l-2 border-pnp-navy p-1.5 align-top">
      {lesson ? (
        <div
          className="rounded-lg border-2 border-pnp-navy bg-white p-2 shadow-[2px_2px_0_var(--pnp-navy)]"
          style={{ borderTopColor: course.color, borderTopWidth: 5 }}
        >
          <button
            type="button"
            onClick={() => cell?.lessonId && onOpen(cell.lessonId)}
            disabled={detached}
            className="block w-full text-left text-[13px] font-bold leading-tight text-pnp-navy disabled:cursor-default"
            title={detached ? "This cell is its own copy" : "Open this lesson"}
          >
            <span className={detached ? "" : "hover:underline"}>
              {lesson.title || "Untitled lesson"}
            </span>
          </button>

          <p className="mt-0.5 text-[11px] text-pnp-gray-500">
            {lesson.blocks.length}{" "}
            {lesson.blocks.length === 1 ? "activity" : "activities"} ·{" "}
            <span
              className={
                lessonMinutes(lesson) > period ? "font-bold text-pnp-red" : ""
              }
            >
              {lessonMinutes(lesson)}/{period} min
            </span>
          </p>

          {lesson.objective && (
            <p className="mt-1 line-clamp-2 text-[11px] leading-snug text-pnp-gray-600">
              {lesson.objective}
            </p>
          )}

          <input
            value={cell?.note ?? ""}
            onChange={(e) => onNote(e.target.value)}
            placeholder="Note for this day"
            className="mt-1 w-full rounded border border-transparent bg-transparent text-[11px] italic text-pnp-gray-600 placeholder:text-pnp-gray-400 hover:border-pnp-gray-200 focus-visible:border-pnp-accent focus-visible:outline-none"
            aria-label="Note for this day"
          />

          <div className="mt-1 flex flex-wrap items-center gap-1">
            {detached ? (
              <>
                <span
                  className="rounded bg-pnp-gray-100 px-1 py-0.5 text-[10px] font-bold uppercase text-pnp-gray-600"
                  title="Edits here do not touch the lesson in the unit"
                >
                  Copy
                </span>
                <button
                  type="button"
                  onClick={onReattach}
                  className="text-[10px] font-bold text-pnp-accent hover:underline"
                  title="Discard this copy and link back to the lesson"
                >
                  Relink
                </button>
              </>
            ) : (
              <button
                type="button"
                onClick={onDetach}
                className="text-[10px] font-bold text-pnp-accent hover:underline"
                title="Make this day its own copy so edits here stay here"
              >
                Make a copy
              </button>
            )}
            <button
              type="button"
              onClick={onClear}
              className="ml-auto text-[10px] font-bold text-pnp-gray-500 hover:text-pnp-red"
            >
              Clear
            </button>
          </div>
        </div>
      ) : (
        <label className="block">
          <span className="sr-only">
            Lesson for {course.name} on {DAY_LABELS[day]}
          </span>
          <select
            value=""
            onChange={(e) => e.target.value && onSet(e.target.value)}
            className="w-full rounded-lg border-2 border-dashed border-pnp-gray-300 bg-white px-1.5 py-2 text-[11px] text-pnp-gray-500 hover:border-pnp-navy focus-visible:border-pnp-accent focus-visible:outline-none"
          >
            <option value="">+ Add lesson…</option>
            {course.units.map((u) => (
              <optgroup key={u.id} label={u.name}>
                {u.lessons.map((l) => (
                  <option key={l.id} value={l.id}>
                    {l.title || "Untitled lesson"}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </label>
      )}
    </td>
  );
}

export default function WeekView({
  library,
  week,
  weeks,
  onSelectWeek,
  onAddWeek,
  onRenameWeek,
  onDateWeek,
  onDeleteWeek,
  onSetCell,
  onClearCell,
  onDetachCell,
  onReattachCell,
  onNoteCell,
  onOpenLesson,
  onSetDayMinutes,
}: Props) {
  if (!week) {
    return (
      <div className="rounded-xl border-2 border-dashed border-pnp-gray-300 px-4 py-16 text-center">
        <p className="font-heading text-lg font-extrabold text-pnp-navy">
          No weeks yet
        </p>
        <p className="mx-auto mt-2 max-w-md text-sm text-pnp-gray-600">
          A week schedules lessons you have already built. Create one, then
          pick a lesson for each course and day. Your lessons stay in their
          units, so next year you keep them and drop the weeks.
        </p>
        <div className="mt-4">
          <Button tier="primary" onClick={onAddWeek}>
            + New week
          </Button>
        </div>
      </div>
    );
  }

  const cellFor = (courseId: string, day: number) =>
    week.cells.find((c) => c.courseId === courseId && c.day === day);

  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center gap-2 rounded-xl border-2 border-pnp-navy bg-white p-3 shadow-[3px_3px_0_var(--pnp-navy)]">
        <label className="flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wide text-pnp-gray-500">
            Week
          </span>
          <select
            value={week.id}
            onChange={(e) => onSelectWeek(e.target.value)}
            className="max-w-[220px] rounded-lg border-2 border-pnp-navy px-2 py-1.5 text-sm font-semibold text-pnp-navy"
          >
            {weeks.map((w) => (
              <option key={w.id} value={w.id}>
                {w.label}
              </option>
            ))}
          </select>
        </label>

        <input
          value={week.label}
          onChange={(e) => onRenameWeek(e.target.value)}
          placeholder="Week name"
          className="min-w-[160px] flex-1 rounded-lg border-2 border-pnp-gray-300 px-2 py-1.5 text-sm text-pnp-navy focus-visible:border-pnp-accent focus-visible:outline-none"
          aria-label="Week name"
        />

        <label className="flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wide text-pnp-gray-500">
            Monday
          </span>
          <input
            type="date"
            value={week.startDate}
            onChange={(e) => onDateWeek(e.target.value)}
            className="rounded-lg border-2 border-pnp-gray-300 px-2 py-1.5 text-sm text-pnp-navy focus-visible:border-pnp-accent focus-visible:outline-none"
          />
        </label>

        <Button tier="secondary" size="small" onClick={onAddWeek}>
          + New week
        </Button>
        <Button tier="tertiary" size="small" onClick={onDeleteWeek}>
          Delete week
        </Button>
      </div>

      <div className="overflow-x-auto rounded-xl border-2 border-pnp-navy bg-white">
        <table className="w-full min-w-[900px] border-collapse">
          <thead>
            <tr className="border-b-2 border-pnp-navy bg-pnp-gray-50">
              <th className="w-40 px-2 py-2 text-left text-[11px] font-bold uppercase tracking-wide text-pnp-gray-500">
                Course
              </th>
              {DAY_LABELS.map((d, day) => (
                <th
                  key={d}
                  className="border-l-2 border-pnp-navy px-2 py-2 text-left"
                >
                  <span className="block text-[11px] font-bold uppercase tracking-wide text-pnp-gray-500">
                    {d}
                  </span>
                  <span className="mt-1 block">
                    <DayLengthButton
                      minutes={week.dayMinutes?.[day] ?? null}
                      onSet={(m) => onSetDayMinutes(day, m)}
                    />
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {library.courses
              .filter((c) => !c.archived)
              .map((course) => (
                <tr key={course.id} className="border-b-2 border-pnp-navy last:border-b-0">
                  <th className="px-2 py-2 text-left align-top">
                    <span className="flex items-center gap-1.5">
                      <span
                        className="h-3 w-3 shrink-0 rounded border-2 border-pnp-navy"
                        style={{ backgroundColor: course.color }}
                        aria-hidden="true"
                      />
                      <span className="text-sm font-extrabold text-pnp-navy">
                        {course.name}
                      </span>
                    </span>
                    <span className="mt-0.5 block text-[11px] font-medium text-pnp-gray-500">
                      {course.periodMinutes} min
                    </span>
                  </th>

                  {DAY_LABELS.map((_, day) => {
                    const cell = cellFor(course.id, day);
                    return (
                      <Cell
                        key={day}
                        library={library}
                        course={course}
                        day={day}
                        period={weekDayPeriod(week, course, day)}
                        cell={cell}
                        onSet={(lessonId) => onSetCell(course.id, day, lessonId)}
                        onClear={() => cell && onClearCell(cell.id)}
                        onDetach={() => cell && onDetachCell(cell.id)}
                        onReattach={() => cell && onReattachCell(cell.id)}
                        onNote={(note) => cell && onNoteCell(cell.id, note)}
                        onOpen={(lessonId) => onOpenLesson(course.id, lessonId)}
                      />
                    );
                  })}
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
