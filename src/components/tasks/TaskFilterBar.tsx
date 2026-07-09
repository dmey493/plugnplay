"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import type { TaskFilterState, LessonFormat, DurationBucket, BrowseMode } from "@/lib/types";
import type { StandardsSystem } from "@/lib/tasks-filter";
import Button from "@/components/ui/Button";

// The unified library has just two formats. Sub-types (Anchor, Investigation,
// Three-Act, Warm-Up, Performance, Problem Set) were retired in the
// "combine things" pass — Dave wanted one mental model for teachers.
const FORMATS: { value: LessonFormat; label: string }[] = [
  { value: "rich-task", label: "Rich Task" },
  { value: "thin-slice", label: "Thin Slice" },
];

const DURATION_BUCKETS: { value: DurationBucket; label: string }[] = [
  { value: "short", label: "≤ 15 min" },
  { value: "medium", label: "16-30 min" },
  { value: "long", label: "30+ min" },
];

const GRADES = [6, 7, 8] as const;

function SearchIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  );
}

function toggle<T>(arr: T[], item: T): T[] {
  return arr.includes(item) ? arr.filter((x) => x !== item) : [...arr, item];
}

// ─────────────────────────────────────────────────────────────────────
// Filter chip — small interactive toggle in the filter row.
//
// Same shape as the design-system buttons (rounded-md, never full-pill,
// uses accent for the active state). Denser height (h-8) because there
// are 10+ of these in a row and the filter row would dominate the page
// at the standard button height. The chip IS a button, just compact.
// ─────────────────────────────────────────────────────────────────────

function FilterChip({
  active,
  onClick,
  children,
  title,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
  title?: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      title={title}
      className={[
        "inline-flex h-8 select-none items-center rounded-md px-3 text-xs font-semibold",
        "transition-[background-color,color,border-color,transform] duration-150 ease-out",
        "active:scale-[0.98]",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2",
        active
          ? "bg-pnp-accent text-white border border-pnp-accent hover:bg-pnp-accent-hover"
          : "bg-white text-pnp-gray-700 border border-pnp-gray-300 hover:bg-pnp-gray-50 hover:border-pnp-gray-400",
      ].join(" ")}
    >
      {children}
    </button>
  );
}

// ─────────────────────────────────────────────────────────────────────
// Segmented control — for mode toggles where exactly one option is on.
// ─────────────────────────────────────────────────────────────────────

function SegmentedButton({
  active,
  onClick,
  href,
  children,
  title,
}: {
  active: boolean;
  onClick?: () => void;
  href?: string;
  children: React.ReactNode;
  title?: string;
}) {
  const cls = [
    "inline-flex h-9 select-none items-center rounded-md px-3 text-sm font-semibold",
    "transition-[background-color,color,transform] duration-150 ease-out",
    "active:scale-[0.98]",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2",
    active
      ? "bg-pnp-accent text-white"
      : "text-pnp-gray-700 hover:bg-pnp-gray-100",
  ].join(" ");
  if (href) {
    return (
      <Link href={href} className={cls} title={title}>
        {children}
      </Link>
    );
  }
  return (
    <button type="button" onClick={onClick} aria-pressed={active} className={cls} title={title}>
      {children}
    </button>
  );
}

interface Props {
  filters: TaskFilterState;
  onChange: (next: TaskFilterState) => void;
  browseMode: BrowseMode;
  onBrowseModeChange: (mode: BrowseMode) => void;
  system: StandardsSystem;
  onSystemChange: (s: StandardsSystem) => void;
  resultCount: number;
}

export default function TaskFilterBar({
  filters,
  onChange,
  browseMode,
  onBrowseModeChange,
  system,
  onSystemChange,
  resultCount,
}: Props) {
  // Debounced search input
  const [searchInput, setSearchInput] = useState(filters.search);

  useEffect(() => {
    const t = setTimeout(() => {
      if (searchInput !== filters.search) {
        onChange({ ...filters, search: searchInput });
      }
    }, 200);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchInput]);

  const hasFilters =
    filters.grades.length > 0 ||
    filters.formats.length > 0 ||
    filters.durationBuckets.length > 0 ||
    filters.concepts.length > 0 ||
    filters.standards.length > 0 ||
    filters.search.trim().length > 0;

  const clearAll = () => {
    setSearchInput("");
    onChange({
      grades: [],
      formats: [],
      durationBuckets: [],
      concepts: [],
      standards: [],
      search: "",
    });
  };

  return (
    <div className="space-y-4 rounded-lg border border-pnp-gray-200 bg-white p-4">
      {/* Row 1: Browse mode + search */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Browse mode toggle. "By Unit" navigates away; the other two
            flip internal state. All three share the segmented-button
            language so the visual hierarchy is consistent. */}
        <div className="inline-flex items-center gap-1 rounded-lg border border-pnp-gray-200 bg-white p-1">
          <SegmentedButton active={false} href="/math/units">
            By Unit
          </SegmentedButton>
          <SegmentedButton
            active={browseMode === "standard"}
            onClick={() => onBrowseModeChange("standard")}
          >
            By Standard
          </SegmentedButton>
          <SegmentedButton
            active={browseMode === "concept"}
            onClick={() => onBrowseModeChange("concept")}
          >
            By Concept
          </SegmentedButton>
        </div>

        {/* Standards system — second segmented control, same language. */}
        {browseMode === "standard" && (
          <div className="inline-flex items-center gap-1 rounded-lg border border-pnp-gray-200 bg-white p-1">
            <SegmentedButton
              active={system === "indiana"}
              onClick={() => onSystemChange("indiana")}
              title="Indiana 2023 Academic Standards for Mathematics"
            >
              Indiana 2023
            </SegmentedButton>
            <SegmentedButton
              active={system === "commonCore"}
              onClick={() => onSystemChange("commonCore")}
              title="Common Core State Standards — Math"
            >
              Common Core
            </SegmentedButton>
          </div>
        )}

        {/* Search */}
        <div className="relative flex-1 min-w-[200px]">
          <div className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-pnp-gray-500">
            <SearchIcon />
          </div>
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search by title, concept, or standard…"
            className="h-10 w-full rounded-md border border-pnp-gray-300 bg-white pl-10 pr-4 text-sm text-pnp-navy outline-none transition-colors focus:border-pnp-accent focus:ring-2 focus:ring-pnp-accent/30"
          />
        </div>

        {/* Result count + clear */}
        <div className="flex items-center gap-3">
          {hasFilters && (
            <Button tier="tertiary" size="small" onClick={clearAll}>
              Clear all
            </Button>
          )}
          <span className="text-sm text-pnp-gray-500">
            {resultCount} {resultCount === 1 ? "task" : "tasks"}
          </span>
        </div>
      </div>

      {/* Row 2: Grade chips, task type chips, duration chips */}
      <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
        {/* Grades */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-pnp-gray-500">
            Grade
          </span>
          {GRADES.map((g) => (
            <FilterChip
              key={g}
              active={filters.grades.includes(g)}
              onClick={() => onChange({ ...filters, grades: toggle(filters.grades, g) })}
            >
              {g}th
            </FilterChip>
          ))}
        </div>

        {/* Format — Rich Task vs Thin Slice. The two umbrella categories
            in the unified library. */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-pnp-gray-500">
            Type
          </span>
          {FORMATS.map((t) => (
            <FilterChip
              key={t.value}
              active={filters.formats.includes(t.value)}
              onClick={() =>
                onChange({
                  ...filters,
                  formats: toggle(filters.formats, t.value),
                })
              }
            >
              {t.label}
            </FilterChip>
          ))}
        </div>

        {/* Duration */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-pnp-gray-500">
            Time
          </span>
          {DURATION_BUCKETS.map((d) => (
            <FilterChip
              key={d.value}
              active={filters.durationBuckets.includes(d.value)}
              onClick={() =>
                onChange({
                  ...filters,
                  durationBuckets: toggle(filters.durationBuckets, d.value),
                })
              }
            >
              {d.label}
            </FilterChip>
          ))}
        </div>
      </div>
    </div>
  );
}
