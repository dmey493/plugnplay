"use client";

import { useState, useEffect } from "react";
import type { FilterState } from "@/lib/types";
import { SUBJECTS, GRADES, PURPOSES, MTSS_TIERS } from "@/lib/constants";

function SearchIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-pnp-gray-500">
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  );
}

function toggle<T>(arr: T[], item: T): T[] {
  return arr.includes(item) ? arr.filter((x) => x !== item) : [...arr, item];
}

export default function FilterBar({
  filters,
  onChange,
  resultCount,
}: {
  filters: FilterState;
  onChange: (f: FilterState) => void;
  resultCount: number;
}) {
  const [searchLocal, setSearchLocal] = useState(filters.search);

  // Debounce search
  useEffect(() => {
    const t = setTimeout(() => {
      if (searchLocal !== filters.search) {
        onChange({ ...filters, search: searchLocal });
      }
    }, 200);
    return () => clearTimeout(t);
  }, [searchLocal, filters, onChange]);

  const hasFilters =
    filters.subjects.length > 0 ||
    filters.grades.length > 0 ||
    filters.purposes.length > 0 ||
    filters.mtssTiers.length > 0 ||
    filters.search.trim().length > 0;

  const clearAll = () => {
    setSearchLocal("");
    onChange({ subjects: [], grades: [], purposes: [], mtssTiers: [], search: "" });
  };

  return (
    <div className="space-y-4">
      {/* Search */}
      <div className="relative">
        <div className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2">
          <SearchIcon />
        </div>
        <input
          type="text"
          value={searchLocal}
          onChange={(e) => setSearchLocal(e.target.value)}
          placeholder="Search strategies..."
          className="w-full rounded-lg border-2 border-pnp-gray-200 bg-white py-3 pl-12 pr-4 text-base text-pnp-navy outline-none transition-colors focus:border-pnp-blue"
        />
      </div>

      {/* Filter chips row */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Subject chips */}
        <div className="flex gap-2">
          {SUBJECTS.map((sub) => {
            const active = filters.subjects.includes(sub.slug);
            return (
              <button
                key={sub.slug}
                onClick={() =>
                  onChange({ ...filters, subjects: toggle(filters.subjects, sub.slug) })
                }
                className={`rounded-lg border-2 px-4 py-2 text-sm font-semibold transition-all ${
                  active
                    ? "text-white"
                    : "border-pnp-gray-200 bg-white text-pnp-gray-700 hover:border-pnp-gray-300"
                }`}
                style={
                  active
                    ? { borderColor: sub.color, backgroundColor: sub.color }
                    : undefined
                }
              >
                {sub.label}
              </button>
            );
          })}
        </div>

        <div className="h-6 w-px bg-pnp-gray-200" />

        {/* Grade chips */}
        <div className="flex gap-2">
          {GRADES.map((g) => {
            const active = filters.grades.includes(g);
            return (
              <button
                key={g}
                onClick={() =>
                  onChange({ ...filters, grades: toggle(filters.grades, g) })
                }
                className={`rounded-lg border-2 px-3 py-2 text-sm font-semibold transition-all ${
                  active
                    ? "border-pnp-navy bg-pnp-navy text-white"
                    : "border-pnp-gray-200 bg-white text-pnp-gray-700 hover:border-pnp-gray-300"
                }`}
              >
                {g}th
              </button>
            );
          })}
        </div>

        <div className="h-6 w-px bg-pnp-gray-200" />

        {/* Purpose dropdown */}
        <select
          value=""
          onChange={(e) => {
            if (e.target.value) {
              onChange({ ...filters, purposes: toggle(filters.purposes, e.target.value) });
            }
          }}
          className="rounded-lg border-2 border-pnp-gray-200 bg-white px-3 py-2 text-sm font-semibold text-pnp-gray-700 outline-none transition-colors hover:border-pnp-gray-300 focus:border-pnp-blue"
        >
          <option value="">Purpose</option>
          {PURPOSES.map((p) => (
            <option key={p.value} value={p.value}>
              {filters.purposes.includes(p.value) ? "✓ " : ""}{p.label}
            </option>
          ))}
        </select>

        {/* Tier dropdown */}
        <select
          value=""
          onChange={(e) => {
            if (e.target.value) {
              onChange({
                ...filters,
                mtssTiers: toggle(filters.mtssTiers, Number(e.target.value)),
              });
            }
          }}
          className="rounded-lg border-2 border-pnp-gray-200 bg-white px-3 py-2 text-sm font-semibold text-pnp-gray-700 outline-none transition-colors hover:border-pnp-gray-300 focus:border-pnp-blue"
        >
          <option value="">Tier</option>
          {MTSS_TIERS.map((t) => (
            <option key={t} value={t}>
              {filters.mtssTiers.includes(t) ? "✓ " : ""}Tier {t}
            </option>
          ))}
        </select>

        {/* Clear + count */}
        <div className="ml-auto flex items-center gap-4">
          {hasFilters && (
            <button
              onClick={clearAll}
              className="text-sm font-semibold text-pnp-blue hover:underline"
            >
              Clear All
            </button>
          )}
          <span className="text-sm text-pnp-gray-500">
            {resultCount} {resultCount === 1 ? "strategy" : "strategies"}
          </span>
        </div>
      </div>

      {/* Active purpose/tier chips */}
      {(filters.purposes.length > 0 || filters.mtssTiers.length > 0) && (
        <div className="flex flex-wrap gap-2">
          {filters.purposes.map((p) => {
            const label = PURPOSES.find((x) => x.value === p)?.label ?? p;
            return (
              <button
                key={p}
                onClick={() =>
                  onChange({ ...filters, purposes: filters.purposes.filter((x) => x !== p) })
                }
                className="flex items-center gap-1 rounded-full bg-pnp-navy/10 px-3 py-1 text-xs font-semibold text-pnp-navy"
              >
                {label}
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              </button>
            );
          })}
          {filters.mtssTiers.map((t) => (
            <button
              key={t}
              onClick={() =>
                onChange({ ...filters, mtssTiers: filters.mtssTiers.filter((x) => x !== t) })
              }
              className="flex items-center gap-1 rounded-full bg-pnp-navy/10 px-3 py-1 text-xs font-semibold text-pnp-navy"
            >
              Tier {t}
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
