"use client";

import type { Student } from "@/lib/classes";

/**
 * Final groups view — what the teacher leaves with.
 *
 * Each group is a coloured circle/card listing its members. Below the
 * grid there are three actions: Re-randomize (loop back to the
 * animation with a fresh shuffle), Back to setup (change presence /
 * animation style), Print (browser print of just this view, via the
 * print CSS that hides chrome elsewhere in the app).
 *
 * Group colours match the animation so the carry-over from the deal
 * is unmistakable.
 */

const GROUP_COLORS = [
  "#0d9488",
  "#f97316",
  "#0ea5e9",
  "#16a34a",
  "#dc2626",
  "#475569",
  "#facc15",
  "#3f42d9",
  "#ec4899",
];
const COL_FOR = (i: number) => GROUP_COLORS[i % GROUP_COLORS.length];

interface Props {
  groups: Student[][];
  onReshuffle: () => void;
  onBack: () => void;
}

export default function GroupsResult({ groups, onReshuffle, onBack }: Props) {
  return (
    <section className="bg-pnp-navy py-10 md:py-14">
      <div className="mx-auto max-w-[1200px] px-4 md:px-6">
        <p className="text-center text-xs font-bold uppercase tracking-[0.3em] text-white/50">
          Today's groups
        </p>
        <h1 className="mt-2 text-center font-heading text-3xl font-extrabold uppercase tracking-wide text-white md:text-4xl">
          {groups.length} group{groups.length === 1 ? "" : "s"}
        </h1>

        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {groups.map((g, gi) => (
            <article
              key={gi}
              className="overflow-hidden rounded-xl bg-white shadow-2xl"
            >
              {/* Coloured header strip matches the animation card. */}
              <div
                className="flex items-center justify-between px-5 py-3 text-white"
                style={{ backgroundColor: COL_FOR(gi) }}
              >
                <p className="font-heading text-sm font-bold uppercase tracking-widest">
                  Group / Board {gi + 1}
                </p>
                <span className="text-xs font-semibold opacity-80">
                  {g.length} student{g.length === 1 ? "" : "s"}
                </span>
              </div>
              <ul className="divide-y divide-pnp-gray-100 px-5 py-3 text-base">
                {g.map((s) => (
                  <li
                    key={s.id}
                    className="flex items-center gap-3 py-2 font-heading text-pnp-navy"
                  >
                    <span
                      aria-hidden="true"
                      className="flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold text-white"
                      style={{ backgroundColor: COL_FOR(gi) }}
                    >
                      {s.name.charAt(0).toUpperCase()}
                    </span>
                    <span className="font-bold">{s.name}</span>
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </div>

        {/* Action row — sits below the groups so it doesn't interrupt
            the at-a-glance scan students will do when they hit their
            seat. */}
        <div className="mt-10 flex flex-col items-center gap-3 print:hidden sm:flex-row sm:justify-center">
          <button
            type="button"
            onClick={onReshuffle}
            className="rounded-md bg-pnp-accent px-5 py-2.5 text-sm font-bold text-white transition-colors hover:bg-pnp-accent-hover"
          >
            Re-randomize
          </button>
          <button
            type="button"
            onClick={onBack}
            className="rounded-md border border-white/30 bg-white/10 px-5 py-2.5 text-sm font-bold text-white transition-colors hover:bg-white/20"
          >
            Change attendance
          </button>
          <button
            type="button"
            onClick={() => window.print()}
            className="rounded-md border border-white/30 bg-white/10 px-5 py-2.5 text-sm font-bold text-white transition-colors hover:bg-white/20"
          >
            Print
          </button>
        </div>
      </div>
    </section>
  );
}
