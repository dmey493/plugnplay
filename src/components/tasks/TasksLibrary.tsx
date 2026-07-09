"use client";

import { useState, useMemo } from "react";
import type { ContentEnvelope, TaskBody, TaskFilterState, BrowseMode } from "@/lib/types";
import { filterTasks, displayStandardsFor, type StandardsSystem } from "@/lib/tasks-filter";
import { getStandardLabel } from "@/lib/standards-labels";
import TaskCard from "./TaskCard";
import TaskFilterBar from "./TaskFilterBar";

const INITIAL_FILTERS: TaskFilterState = {
  grades: [],
  formats: [],
  durationBuckets: [],
  concepts: [],
  standards: [],
  search: "",
};

interface Props {
  tasks: ContentEnvelope[];
}

interface Group {
  key: string;            // standard code or concept name
  label: string;          // primary header text (the code itself, or concept name)
  description?: string;   // short teacher-friendly phrase shown after the label
  tasks: ContentEnvelope[];
}

export default function TasksLibrary({ tasks }: Props) {
  const [filters, setFilters] = useState<TaskFilterState>(INITIAL_FILTERS);
  const [browseMode, setBrowseMode] = useState<BrowseMode>("standard");
  // Standards system used for both grouping and any display chips. Defaults
  // to "indiana" (2023 IAS-M) per the platform's primary alignment.
  const [system, setSystem] = useState<StandardsSystem>("indiana");

  const filtered = useMemo(() => filterTasks(tasks, filters), [tasks, filters]);

  // Group filtered tasks for display
  const groups: Group[] = useMemo(() => {
    if (browseMode === "standard") {
      const byStandard = new Map<string, ContentEnvelope[]>();
      const noStandard: ContentEnvelope[] = [];

      for (const task of filtered) {
        // Only group by codes that match the effective grade context. A
        // 7th-grade task tagged with 8.NS.1 for an extension reach standard
        // will NOT appear under 8.NS.1 when grade=7 is the filter (or when
        // the task itself is grades:[7]).
        const standards = displayStandardsFor(task, system, filters.grades);
        if (standards.length === 0) {
          noStandard.push(task);
        } else {
          for (const s of standards) {
            const arr = byStandard.get(s) ?? [];
            arr.push(task);
            byStandard.set(s, arr);
          }
        }
      }

      const sorted: Group[] = Array.from(byStandard.entries())
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([key, t]) => ({
          key,
          label: key,
          description: getStandardLabel(key, system),
          tasks: t,
        }));

      if (noStandard.length > 0) {
        sorted.push({
          key: "_no_standard",
          label: "Not aligned to a single standard",
          tasks: noStandard,
        });
      }
      return sorted;
    }

    // browseMode === "concept"
    const byConcept = new Map<string, ContentEnvelope[]>();
    for (const task of filtered) {
      const body = task.body as TaskBody;
      const concepts = body.concepts ?? [];
      if (concepts.length === 0) {
        const arr = byConcept.get("_uncategorized") ?? [];
        arr.push(task);
        byConcept.set("_uncategorized", arr);
        continue;
      }
      for (const c of concepts) {
        const arr = byConcept.get(c) ?? [];
        arr.push(task);
        byConcept.set(c, arr);
      }
    }

    return Array.from(byConcept.entries())
      .sort(([a], [b]) => {
        if (a === "_uncategorized") return 1;
        if (b === "_uncategorized") return -1;
        return a.localeCompare(b);
      })
      .map(([key, t]) => ({
        key,
        label: key === "_uncategorized" ? "Other" : prettifyConcept(key),
        tasks: t,
      }));
  }, [filtered, browseMode]);

  const handleReset = () => setFilters(INITIAL_FILTERS);

  return (
    <div>
      <TaskFilterBar
        filters={filters}
        onChange={setFilters}
        browseMode={browseMode}
        onBrowseModeChange={setBrowseMode}
        system={system}
        onSystemChange={setSystem}
        resultCount={filtered.length}
      />

      <div className="mt-8 space-y-10">
        {groups.length === 0 ? (
          <EmptyState onReset={handleReset} />
        ) : (
          groups.map((group) => (
            <div key={group.key}>
              <h2 className="mb-4 flex flex-wrap items-baseline gap-x-3 gap-y-1 border-b border-pnp-gray-200 pb-2">
                <span className="font-heading text-xl font-bold text-pnp-navy">
                  {group.label}
                </span>
                {group.description && (
                  <span className="text-base font-medium text-pnp-gray-700">
                    — {group.description}
                  </span>
                )}
                <span className="text-sm text-pnp-gray-500">
                  {group.tasks.length} {group.tasks.length === 1 ? "task" : "tasks"}
                </span>
              </h2>
              <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
                {group.tasks.map((task) => (
                  <TaskCard key={task.id} task={task} />
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function prettifyConcept(slug: string): string {
  return slug
    .split("-")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

function EmptyState({ onReset }: { onReset: () => void }) {
  return (
    <div className="rounded-lg border-2 border-dashed border-pnp-gray-200 bg-white py-16 text-center">
      <p className="text-lg font-semibold text-pnp-gray-700">
        No tasks fit these filters
      </p>
      <p className="mt-1 text-sm text-pnp-gray-500">
        Widen your grade or duration &mdash; or clear them all to see everything.
      </p>
      <button
        type="button"
        onClick={onReset}
        className="mt-4 inline-flex h-10 items-center rounded-md border border-pnp-gray-300 bg-white px-4 text-sm font-semibold text-pnp-navy transition-colors hover:bg-pnp-gray-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2"
      >
        Clear all filters
      </button>
    </div>
  );
}
