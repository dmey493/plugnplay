"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import type { ContentEnvelope, ThinSliceBody } from "@/lib/types";

interface Props {
  slices: ContentEnvelope[];
}

type GradeFilter = "all" | 6 | 7 | 8;

/**
 * Browse page for thin slices: grade chips + a standard dropdown that's
 * filtered by the active grade. Cards below show every slice that matches.
 *
 * Mirrors the ProblemGenerator's input style — grade chips with blue active
 * state and a grouped <select> for the standard dropdown — so the two pages
 * read as part of the same family.
 */
export default function ThinSlicesLibrary({ slices }: Props) {
  const [grade, setGrade] = useState<GradeFilter>("all");
  const [standard, setStandard] = useState<string>("all");

  // When the grade filter changes, we need to clear the standard filter if the
  // currently selected standard isn't in the new grade.
  const slicesForGrade = useMemo(() => {
    if (grade === "all") return slices;
    return slices.filter((s) => s.grades.includes(grade));
  }, [slices, grade]);

  // Build the dropdown's standard list from whatever slices match the grade.
  // Group by domain (NS, AF, RP, GM, DSP) — same pattern the generator uses.
  const standardGroups = useMemo(() => {
    const set = new Set<string>();
    for (const s of slicesForGrade) {
      for (const code of s.standards.indiana ?? []) set.add(code);
    }
    const groups: Record<string, string[]> = {};
    for (const code of set) {
      // Indiana codes look like "7.NS.1", "8.GM.3" — domain is the middle part.
      const parts = code.split(".");
      const domain = parts[1] ?? "Other";
      (groups[domain] ??= []).push(code);
    }
    // Sort each group's codes
    for (const domain of Object.keys(groups)) {
      groups[domain].sort();
    }
    return groups;
  }, [slicesForGrade]);

  // The actual filtered list rendered as cards.
  const filtered = useMemo(() => {
    return slicesForGrade.filter((s) => {
      if (standard === "all") return true;
      return (s.standards.indiana ?? []).includes(standard);
    });
  }, [slicesForGrade, standard]);

  // If the selected standard disappears from the active grade's list (because
  // the teacher just switched grade and the prior standard isn't in the new
  // grade), snap the dropdown back to "all". Run after render to avoid
  // setting state during render.
  const visibleStandards = useMemo(
    () => Object.values(standardGroups).flat(),
    [standardGroups]
  );
  useEffect(() => {
    if (standard !== "all" && !visibleStandards.includes(standard)) {
      setStandard("all");
    }
  }, [standard, visibleStandards]);

  const handleGradeChange = (g: GradeFilter) => {
    setGrade(g);
  };

  return (
    <div className="space-y-8">
      {/* Filters */}
      <div className="rounded-xl border-2 border-pnp-gray-200 bg-white p-5 md:p-6">
        {/* Grade */}
        <div>
          <label className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
            Grade
          </label>
          <div className="mt-2 flex flex-wrap gap-2">
            {(["all", 6, 7, 8] as GradeFilter[]).map((g) => (
              <button
                key={String(g)}
                onClick={() => handleGradeChange(g)}
                className={`rounded-lg border-2 px-5 py-2.5 text-base font-semibold transition-all ${
                  grade === g
                    ? "border-pnp-blue bg-pnp-blue text-white"
                    : "border-pnp-gray-200 bg-white text-pnp-gray-700 hover:border-pnp-gray-300"
                }`}
              >
                {g === "all" ? "All Grades" : `${g}th`}
              </button>
            ))}
          </div>
        </div>

        {/* Standard */}
        <div className="mt-6">
          <label className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
            Standard
          </label>
          <select
            value={standard}
            onChange={(e) => setStandard(e.target.value)}
            className="mt-2 w-full rounded-lg border-2 border-pnp-gray-200 bg-white px-4 py-3 text-sm font-medium text-pnp-navy outline-none transition-colors focus:border-pnp-blue"
          >
            <option value="all">All standards</option>
            {Object.entries(standardGroups)
              .sort(([a], [b]) => a.localeCompare(b))
              .map(([domain, codes]) => (
                <optgroup key={domain} label={domain}>
                  {codes.map((code) => (
                    <option key={code} value={code}>
                      {code}
                    </option>
                  ))}
                </optgroup>
              ))}
          </select>
        </div>

        {/* Result count */}
        <div className="mt-4 text-sm text-pnp-gray-500">
          {filtered.length} thin slice{filtered.length === 1 ? "" : "s"}
          {grade !== "all" && ` for grade ${grade}`}
          {standard !== "all" && ` aligned to ${standard}`}
        </div>
      </div>

      {/* Cards */}
      {filtered.length === 0 ? (
        <div className="rounded-xl border-2 border-dashed border-pnp-gray-200 p-12 text-center text-pnp-gray-500">
          No thin slices match the current filters.
        </div>
      ) : (
        <ul className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((slice) => {
            const body = slice.body as ThinSliceBody;
            const stepCount = body.steps?.length ?? 0;
            const primaryStandard =
              slice.standards.indiana?.[0] ?? slice.standards.commonCore?.[0];
            return (
              <li key={slice.id}>
                <Link
                  href={`/math/thin-slices/${slice.id}/project`}
                  className="group flex h-full flex-col rounded-lg border border-pnp-gray-200 bg-white p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:border-purple-400 hover:shadow-md"
                >
                  <div className="mb-3 flex items-center justify-between gap-2">
                    <span className="rounded-full bg-purple-100 px-3 py-0.5 text-xs font-bold uppercase text-purple-800">
                      {stepCount} steps
                    </span>
                    {primaryStandard && (
                      <span className="rounded border border-pnp-gray-300 bg-pnp-gray-50 px-2 py-0.5 text-xs font-mono text-pnp-gray-700">
                        {primaryStandard}
                      </span>
                    )}
                  </div>
                  <h3 className="font-heading text-lg font-bold leading-snug text-pnp-navy line-clamp-2">
                    {slice.title}
                  </h3>
                  <p className="mt-2 flex-1 text-sm leading-relaxed text-pnp-gray-600 line-clamp-3">
                    {body.goal || slice.preview}
                  </p>
                  <div className="mt-4 flex items-center gap-3 border-t border-pnp-gray-100 pt-3 text-xs text-pnp-gray-500">
                    <div className="flex gap-1">
                      {slice.grades.map((g) => (
                        <span
                          key={g}
                          className="rounded bg-pnp-gray-100 px-2 py-0.5 font-medium"
                        >
                          {g}th
                        </span>
                      ))}
                    </div>
                    <span className="ml-auto font-semibold text-purple-700 group-hover:underline">
                      Project →
                    </span>
                  </div>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
