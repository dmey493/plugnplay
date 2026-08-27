"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  getClass,
  parseRosterPaste,
  planGroupSizes,
  updateClass,
  type Class,
  type Student,
} from "@/lib/classroom/classes";

/**
 * Class detail — roster editor for one class.
 *
 * Two ways to add students:
 *   1) Paste-many: a textarea that accepts one name per line (also
 *      tolerates commas / tabs). Single click, dozens of students at
 *      a time. Designed for the first-load case.
 *   2) Add-one: an inline form for "oh, we have a new student today."
 *
 * Per-student rename + delete are inline. No drag-to-reorder yet —
 * order in the list doesn't affect the future randomizer, and a real
 * d&d implementation isn't worth it for v1.
 *
 * Per-student constraints (lock-with, lock-apart, fixed-board) live
 * in the data model but no UI yet — Dave's draft intentionally leaves
 * them out. They slot back in here when ready.
 */
export default function ClassDetail({ classId }: { classId: string }) {
  const [cls, setCls] = useState<Class | null | undefined>(undefined);
  const [name, setName] = useState("");
  const [paste, setPaste] = useState("");
  const [addingOne, setAddingOne] = useState("");

  // Read the class from localStorage on mount + when classId changes.
  useEffect(() => {
    const found = getClass(classId);
    setCls(found);
    if (found) setName(found.name);
  }, [classId]);

  if (cls === undefined) {
    return <div className="py-12 text-center text-sm text-pnp-gray-500">Loading…</div>;
  }

  if (cls === null) {
    return (
      <EmptyChrome
        title="Class not found"
        body="It may have been deleted, or this link is from a different browser. Head back to the class list to pick another."
        cta={{ href: "/classes", label: "Back to Classes" }}
      />
    );
  }

  const save = (patch: Partial<Pick<Class, "name" | "students">>) => {
    const next = updateClass(cls.id, patch);
    if (next) setCls(next);
  };

  const handleNameBlur = () => {
    const trimmed = name.trim();
    if (!trimmed || trimmed === cls.name) {
      setName(cls.name);
      return;
    }
    save({ name: trimmed });
  };

  const handlePasteImport = (mode: "append" | "replace") => {
    const parsed = parseRosterPaste(paste);
    if (parsed.length === 0) return;
    const nextRoster = mode === "replace" ? parsed : [...cls.students, ...parsed];
    save({ students: nextRoster });
    setPaste("");
  };

  const handleAddOne = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = addingOne.trim();
    if (!trimmed) return;
    save({ students: [...cls.students, ...parseRosterPaste(trimmed)] });
    setAddingOne("");
  };

  const handleRename = (id: string, newName: string) => {
    const trimmed = newName.trim();
    if (!trimmed) return;
    save({
      students: cls.students.map((s) => (s.id === id ? { ...s, name: trimmed } : s)),
    });
  };

  const handleRemove = (s: Student) => {
    if (!window.confirm(`Remove ${s.name} from ${cls.name}?`)) return;
    save({ students: cls.students.filter((x) => x.id !== s.id) });
  };

  // Preview of how this class would group up under the v1 rule.
  const sizes = planGroupSizes(cls.students.length);
  const sizesText =
    sizes.length === 0
      ? "Add some students to see a group preview."
      : sizes.length === 1
        ? `One group of ${sizes[0]}.`
        : `${sizes.length} groups — ${sizes.join(" + ")}.`;

  return (
    <div className="space-y-8">
      <div>
        <Link
          href="/classes"
          className="inline-flex items-center gap-1.5 text-sm font-semibold text-pnp-gray-600 transition-colors hover:text-pnp-navy"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          Back to Classes
        </Link>
        <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div className="flex-1">
            <label>
              <span className="sr-only">Class name</span>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                onBlur={handleNameBlur}
                onKeyDown={(e) => {
                  if (e.key === "Enter") (e.target as HTMLInputElement).blur();
                }}
                className="w-full max-w-xl rounded-md border border-transparent bg-transparent px-1 py-0.5 font-heading text-2xl font-bold text-pnp-navy outline-none transition-colors hover:border-pnp-gray-200 focus:border-pnp-accent focus:bg-white focus:ring-2 focus:ring-pnp-accent/30"
              />
            </label>
            <p className="mt-1 text-xs text-pnp-gray-500">
              {cls.students.length} student{cls.students.length === 1 ? "" : "s"} &middot; {sizesText}
            </p>
          </div>
          {cls.students.length >= 2 && (
            <Link
              href={`/groups/${cls.id}`}
              className="inline-flex shrink-0 items-center gap-1.5 rounded-md bg-pnp-accent px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-pnp-accent-hover"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M23 21v-2a4 4 0 00-3-3.87" />
                <path d="M16 3.13a4 4 0 010 7.75" />
              </svg>
              Form groups
            </Link>
          )}
        </div>
      </div>

      {/* Two ways to add: paste-many on the left, add-one on the right. */}
      <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
        <section className="rounded-lg border border-pnp-gray-200 bg-white p-4">
          <h2 className="font-heading text-sm font-bold uppercase tracking-wider text-pnp-gray-500">
            Paste a roster
          </h2>
          <p className="mt-1 text-xs text-pnp-gray-500">
            One name per line works best. Commas and tabs are OK too — paste from a spreadsheet column without reformatting.
          </p>
          <textarea
            value={paste}
            onChange={(e) => setPaste(e.target.value)}
            rows={6}
            placeholder={"Amy Chen\nBen Rodriguez\nCarmen Ng\n…"}
            className="mt-3 w-full rounded-md border border-pnp-gray-300 bg-white px-3 py-2 text-sm text-pnp-navy outline-none transition-colors placeholder:text-pnp-gray-500 focus:border-pnp-accent focus:ring-2 focus:ring-pnp-accent/30"
          />
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => handlePasteImport("append")}
              disabled={!paste.trim()}
              className="rounded-md bg-pnp-accent px-3 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-pnp-accent-hover disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Add to roster
            </button>
            <button
              type="button"
              onClick={() => {
                if (cls.students.length === 0 || window.confirm(`Replace the current ${cls.students.length} students?`)) {
                  handlePasteImport("replace");
                }
              }}
              disabled={!paste.trim()}
              className="rounded-md border border-pnp-gray-300 bg-white px-3 py-1.5 text-sm font-semibold text-pnp-navy transition-colors hover:bg-pnp-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Replace roster
            </button>
          </div>
        </section>

        <section className="rounded-lg border border-pnp-gray-200 bg-white p-4">
          <h2 className="font-heading text-sm font-bold uppercase tracking-wider text-pnp-gray-500">
            Add a single student
          </h2>
          <p className="mt-1 text-xs text-pnp-gray-500">
            For "we have a new student today" moments.
          </p>
          <form onSubmit={handleAddOne} className="mt-3 flex flex-col gap-2">
            <input
              type="text"
              value={addingOne}
              onChange={(e) => setAddingOne(e.target.value)}
              placeholder="Name"
              className="w-full rounded-md border border-pnp-gray-300 bg-white px-3 py-2 text-sm text-pnp-navy outline-none transition-colors placeholder:text-pnp-gray-500 focus:border-pnp-accent focus:ring-2 focus:ring-pnp-accent/30"
            />
            <button
              type="submit"
              disabled={!addingOne.trim()}
              className="rounded-md bg-pnp-accent px-3 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-pnp-accent-hover disabled:opacity-50 disabled:cursor-not-allowed"
            >
              + Add student
            </button>
          </form>
        </section>
      </div>

      {/* Roster table. Inline rename via click-to-edit. */}
      <section>
        <h2 className="mb-3 font-heading text-sm font-bold uppercase tracking-wider text-pnp-gray-500">
          Roster
        </h2>
        {cls.students.length === 0 ? (
          <div className="rounded-lg border-2 border-dashed border-pnp-gray-300 bg-white p-8 text-center text-sm text-pnp-gray-500">
            No students yet. Paste a roster or add one above.
          </div>
        ) : (
          <ul className="divide-y divide-pnp-gray-100 rounded-lg border border-pnp-gray-200 bg-white">
            {cls.students.map((s, i) => (
              <RosterRow
                key={s.id}
                index={i + 1}
                student={s}
                onRename={(name) => handleRename(s.id, name)}
                onRemove={() => handleRemove(s)}
              />
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function RosterRow({
  index,
  student,
  onRename,
  onRemove,
}: {
  index: number;
  student: Student;
  onRename: (name: string) => void;
  onRemove: () => void;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(student.name);

  return (
    <li className="flex items-center gap-3 px-4 py-2 text-sm">
      <span className="w-8 text-right text-xs font-semibold tabular-nums text-pnp-gray-500">
        {index}
      </span>
      {editing ? (
        <input
          type="text"
          autoFocus
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onBlur={() => {
            setEditing(false);
            if (draft.trim() && draft.trim() !== student.name) onRename(draft);
            else setDraft(student.name);
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter") (e.target as HTMLInputElement).blur();
            if (e.key === "Escape") {
              setDraft(student.name);
              setEditing(false);
            }
          }}
          className="flex-1 rounded-md border border-pnp-accent bg-white px-2 py-1 text-pnp-navy outline-none ring-2 ring-pnp-accent/30"
        />
      ) : (
        <button
          type="button"
          onClick={() => {
            setDraft(student.name);
            setEditing(true);
          }}
          className="flex-1 rounded-md px-2 py-1 text-left text-pnp-navy transition-colors hover:bg-pnp-gray-50"
        >
          {student.name}
        </button>
      )}
      <button
        type="button"
        onClick={onRemove}
        className="rounded p-1 text-pnp-gray-300 transition-colors hover:bg-pnp-red/10 hover:text-pnp-red"
        aria-label={`Remove ${student.name}`}
        title="Remove"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M18 6L6 18M6 6l12 12" />
        </svg>
      </button>
    </li>
  );
}

function EmptyChrome({
  title,
  body,
  cta,
}: {
  title: string;
  body: string;
  cta?: { href: string; label: string };
}) {
  return (
    <div className="rounded-lg border-2 border-dashed border-pnp-gray-300 bg-white p-10 text-center">
      <h2 className="font-heading text-lg font-bold text-pnp-navy">{title}</h2>
      <p className="mx-auto mt-2 max-w-md text-sm text-pnp-gray-500">{body}</p>
      {cta && (
        <Link
          href={cta.href}
          className="mt-4 inline-flex items-center rounded-md bg-pnp-accent px-3 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-pnp-accent-hover"
        >
          {cta.label}
        </Link>
      )}
    </div>
  );
}
