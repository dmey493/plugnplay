"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  createClass,
  deleteClass,
  getClasses,
  type Class,
} from "@/lib/classes";

/**
 * Classes index — list every class saved locally in this browser, plus
 * a "+ New class" inline create row.
 *
 * No login: classes save to this browser immediately. Two states:
 *   - hydrating (before the mount effect reads localStorage): quiet
 *     placeholder so SSR + CSR markup match.
 *   - hydrated: the create row + either the empty nudge or the grid.
 *
 * Deliberately client-side — localStorage is browser-only. When real
 * auth + a DB land we'll refactor this into a server component reading
 * from Supabase, but the JSON shape is already aligned.
 */
export default function ClassesList() {
  const [classes, setClasses] = useState<Class[]>([]);
  const [newName, setNewName] = useState("");
  const [hydrated, setHydrated] = useState(false);

  // Read from localStorage once on mount. localStorage is browser-only,
  // so this can't run during SSR.
  useEffect(() => {
    setClasses(getClasses());
    setHydrated(true);
  }, []);

  if (!hydrated) {
    return <div className="py-12 text-center text-sm text-pnp-gray-500">Loading…</div>;
  }

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = newName.trim();
    if (!trimmed) return;
    createClass(trimmed);
    setClasses(getClasses());
    setNewName("");
  };

  const handleDelete = (cls: Class) => {
    if (
      !window.confirm(
        `Delete "${cls.name}"? This removes the roster of ${cls.students.length} student${cls.students.length === 1 ? "" : "s"} from this browser. Can't be undone.`
      )
    ) {
      return;
    }
    deleteClass(cls.id);
    setClasses(getClasses());
  };

  return (
    <div className="space-y-6">
      {/* Inline create row. Quick because every teacher will want to
          create their first class within seconds of landing here. */}
      <form
        onSubmit={handleCreate}
        className="flex flex-col gap-2 rounded-lg border border-pnp-gray-200 bg-white p-4 sm:flex-row sm:items-center"
      >
        <label className="flex-1">
          <span className="sr-only">New class name</span>
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="e.g. Period 3 — Grade 7 Math"
            className="w-full rounded-md border border-pnp-gray-300 bg-white px-3 py-2 text-sm text-pnp-navy outline-none transition-colors placeholder:text-pnp-gray-500 focus:border-pnp-accent focus:ring-2 focus:ring-pnp-accent/30"
          />
        </label>
        <button
          type="submit"
          disabled={!newName.trim()}
          className="rounded-md bg-pnp-accent px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-pnp-accent-hover disabled:opacity-50 disabled:cursor-not-allowed"
        >
          + New class
        </button>
      </form>

      {classes.length === 0 ? (
        <div className="rounded-lg border-2 border-dashed border-pnp-gray-300 bg-white p-10 text-center">
          <h2 className="font-heading text-lg font-bold text-pnp-navy">
            No classes yet
          </h2>
          <p className="mx-auto mt-2 max-w-md text-sm text-pnp-gray-500">
            Create your first class above, then paste in a student roster on the next screen.
          </p>
        </div>
      ) : (
        <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {classes.map((cls) => (
            <li
              key={cls.id}
              className="group relative flex flex-col rounded-lg border border-pnp-gray-200 bg-white p-4 transition-shadow hover:shadow-md"
            >
              <Link href={`/classes/${cls.id}`} className="absolute inset-0 z-0" aria-label={`Open ${cls.name}`} />
              <div className="relative z-10 flex items-start justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <h3 className="truncate font-heading text-base font-bold text-pnp-navy">
                    {cls.name}
                  </h3>
                  <p className="mt-0.5 text-xs text-pnp-gray-500">
                    {cls.students.length} student{cls.students.length === 1 ? "" : "s"}
                  </p>
                </div>
                {/* Delete handle — pointer-events:auto so it sits above
                    the full-card link anchor. */}
                <button
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    handleDelete(cls);
                  }}
                  className="pointer-events-auto rounded p-1 text-pnp-gray-300 transition-colors hover:bg-pnp-red/10 hover:text-pnp-red"
                  aria-label={`Delete ${cls.name}`}
                  title="Delete class"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6" />
                  </svg>
                </button>
              </div>
              {cls.students.length >= 2 && (
                <Link
                  href={`/groups/${cls.id}`}
                  onClick={(e) => e.stopPropagation()}
                  className="pointer-events-auto relative z-10 mt-3 inline-flex items-center justify-center gap-1.5 rounded-md bg-pnp-accent px-3 py-1.5 text-xs font-semibold text-white transition-colors hover:bg-pnp-accent-hover"
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
                    <circle cx="9" cy="7" r="4" />
                    <path d="M23 21v-2a4 4 0 00-3-3.87" />
                    <path d="M16 3.13a4 4 0 010 7.75" />
                  </svg>
                  Form groups
                </Link>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
