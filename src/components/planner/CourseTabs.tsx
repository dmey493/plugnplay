"use client";

/**
 * One tab per course, plus a Weeks tab and an actions menu.
 *
 * A course is whatever the teacher names it — this planner is not tied to a
 * subject — so the tab label is an editable field, not a fixed string. A
 * freshly created course opens straight into its rename input, and carries
 * its typical period length beside the name so the length of a period is
 * visible from the moment the course exists.
 */

import { useEffect, useRef, useState } from "react";
import type { Course } from "@/lib/lesson-plans";

export const WEEKS_TAB = "__weeks__";

interface Props {
  courses: Course[];
  activeId: string;
  /** Set right after creating a course so its tab opens in rename mode. */
  autoEditId: string | null;
  onAutoEditDone: () => void;
  onSelect: (id: string) => void;
  onRename: (courseId: string, name: string) => void;
  onAddCourse: () => void;
  actions: { label: string; onSelect: () => void; danger?: boolean }[];
}

function CourseTab({
  course,
  active,
  autoEdit,
  onAutoEditDone,
  onSelect,
  onRename,
}: {
  course: Course;
  active: boolean;
  autoEdit: boolean;
  onAutoEditDone: () => void;
  onSelect: () => void;
  onRename: (name: string) => void;
}) {
  const [editing, setEditing] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (autoEdit) setEditing(true);
  }, [autoEdit]);

  useEffect(() => {
    if (editing) inputRef.current?.select();
  }, [editing]);

  const stopEditing = () => {
    setEditing(false);
    onAutoEditDone();
  };

  if (editing) {
    return (
      <span className="inline-flex items-center rounded-t-lg border-2 border-b-0 border-pnp-navy bg-white px-2 py-1.5">
        <span
          className="mr-1.5 h-3 w-3 shrink-0 rounded-full border-2 border-pnp-navy"
          style={{ backgroundColor: course.color }}
          aria-hidden="true"
        />
        <input
          ref={inputRef}
          value={course.name}
          onChange={(e) => onRename(e.target.value)}
          onBlur={stopEditing}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === "Escape") stopEditing();
          }}
          className="w-36 bg-transparent text-sm font-bold text-pnp-navy focus-visible:outline-none"
          aria-label="Course name"
        />
        <span className="ml-1 shrink-0 text-[11px] font-semibold text-pnp-gray-400">
          {course.periodMinutes}m
        </span>
      </span>
    );
  }

  return (
    <span
      className={`inline-flex items-center rounded-t-lg border-2 border-b-0 px-3 py-1.5 ${
        active
          ? "border-pnp-navy bg-white"
          : "border-transparent bg-pnp-gray-100 hover:bg-pnp-gray-200"
      }`}
    >
      <span
        className="mr-1.5 h-3 w-3 shrink-0 rounded-full border-2 border-pnp-navy"
        style={{ backgroundColor: course.color }}
        aria-hidden="true"
      />
      <button
        type="button"
        onClick={onSelect}
        onDoubleClick={() => setEditing(true)}
        aria-current={active ? "page" : undefined}
        className={`text-sm font-bold ${
          active ? "text-pnp-navy" : "text-pnp-gray-600"
        }`}
        title={active ? "Double-click to rename" : course.name}
      >
        {course.name || "Untitled course"}
        <span
          className={`ml-1.5 text-[11px] font-semibold ${
            active ? "text-pnp-gray-500" : "text-pnp-gray-400"
          }`}
        >
          {course.periodMinutes}m
        </span>
      </button>
      {active && (
        <button
          type="button"
          onClick={() => setEditing(true)}
          className="ml-1.5 rounded p-0.5 text-pnp-gray-400 hover:text-pnp-navy"
          aria-label={`Rename ${course.name}`}
          title="Rename"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M12 20h9" />
            <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z" />
          </svg>
        </button>
      )}
    </span>
  );
}

/** Export / import / delete / print, folded into one menu so the toolbar
 *  above the grid stays a single line. Mirrors the header's dropdown. */
function ActionsMenu({ actions }: { actions: Props["actions"] }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function onClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        aria-haspopup="menu"
        className="flex items-center gap-1 rounded-t-lg border-2 border-b-0 border-transparent bg-pnp-gray-100 px-3 py-1.5 text-sm font-bold text-pnp-gray-600 hover:bg-pnp-gray-200 hover:text-pnp-navy"
      >
        Actions
        <svg
          width="10"
          height="7"
          viewBox="0 0 12 8"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
          className={open ? "rotate-180" : ""}
        >
          <path d="M1 1.5l5 5 5-5" />
        </svg>
      </button>

      {open && (
        <div
          role="menu"
          className="absolute right-0 top-full z-50 mt-1 min-w-[180px] overflow-hidden rounded-lg border-2 border-pnp-navy bg-white py-1 shadow-[3px_3px_0_var(--pnp-navy)]"
        >
          {actions.map((a) => (
            <button
              key={a.label}
              type="button"
              role="menuitem"
              onClick={() => {
                setOpen(false);
                a.onSelect();
              }}
              className={`block w-full px-4 py-2 text-left text-sm font-semibold hover:bg-pnp-gray-50 ${
                a.danger ? "text-pnp-red" : "text-pnp-navy"
              }`}
            >
              {a.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default function CourseTabs({
  courses,
  activeId,
  autoEditId,
  onAutoEditDone,
  onSelect,
  onRename,
  onAddCourse,
  actions,
}: Props) {
  return (
    <div className="flex flex-wrap items-end gap-1 border-b-2 border-pnp-navy">
      {courses.map((c) => (
        <CourseTab
          key={c.id}
          course={c}
          active={c.id === activeId}
          autoEdit={c.id === autoEditId}
          onAutoEditDone={onAutoEditDone}
          onSelect={() => onSelect(c.id)}
          onRename={(name) => onRename(c.id, name)}
        />
      ))}

      <button
        type="button"
        onClick={onAddCourse}
        className="rounded-t-lg px-2.5 py-1.5 text-sm font-bold text-pnp-gray-500 hover:bg-pnp-gray-100 hover:text-pnp-navy"
        title="Add a course"
      >
        +
      </button>

      <span className="ml-auto flex items-end gap-1">
        <button
          type="button"
          onClick={() => onSelect(WEEKS_TAB)}
          aria-current={activeId === WEEKS_TAB ? "page" : undefined}
          className={`rounded-t-lg border-2 border-b-0 px-3 py-1.5 text-sm font-bold ${
            activeId === WEEKS_TAB
              ? "border-pnp-navy bg-white text-pnp-navy"
              : "border-transparent bg-pnp-gray-100 text-pnp-gray-600 hover:bg-pnp-gray-200"
          }`}
        >
          Weeks
        </button>
        <ActionsMenu actions={actions} />
      </span>
    </div>
  );
}
