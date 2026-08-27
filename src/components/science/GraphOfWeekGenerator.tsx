"use client";

import { useState } from "react";
import Button from "@/components/ui/Button";
import Tag from "@/components/ui/Tag";
import {
  GRADES,
  strandsForGrade,
  standardsForGrade,
  entriesForStandard,
  type GotwEntry,
} from "@/lib/library/gotw";
import GraphOfWeekView from "./GraphOfWeekView";

const CHART_LABELS: Record<string, string> = {
  bar: "Bar graph",
  grouped_bar: "Grouped bars",
  line: "Line graph",
  scatter: "Scatter plot",
  dotplot: "Dot plot",
  pie: "Pie chart",
  radar: "Radar chart",
  histogram: "Histogram",
  pictograph: "Pictograph",
  climograph: "Climograph",
  box: "Box plot",
  bubble: "Bubble chart",
};

function chartLabel(t: string): string {
  return CHART_LABELS[t] ?? "Graph";
}

/**
 * Graph of the Week generator — the Grade → Standard workflow (mirrors the
 * math Problem Generator): pick a grade, then a standard from a strand board
 * that collapses to a summary once chosen; if the standard has more than one
 * weekly graph, pick which one. The selected worksheet renders inline with a
 * Print action styled like the stimulus generator's print modal.
 */
export default function GraphOfWeekGenerator() {
  const [grade, setGrade] = useState<number>(6);
  const [standard, setStandard] = useState("");
  const [expanded, setExpanded] = useState(false);
  const [entry, setEntry] = useState<GotwEntry | null>(null);

  const strandGroups = strandsForGrade(grade);
  const selected = standardsForGrade(grade).find((s) => s.standard === standard);
  const weeks = standard ? entriesForStandard(grade, standard) : [];
  const showBoard = expanded || !standard;

  const handleGrade = (g: number) => {
    setGrade(g);
    setStandard("");
    setEntry(null);
    setExpanded(false);
  };

  // Picking a standard collapses the board. If it has a single weekly graph,
  // select it straight away so there's no redundant one-option step.
  const handleStandard = (code: string) => {
    setStandard(code);
    setExpanded(false);
    const list = entriesForStandard(grade, code);
    setEntry(list.length === 1 ? list[0] : null);
  };

  return (
    <div>
      <div
        className="rounded-lg bg-white p-6 shadow-sm md:p-8"
        style={{ borderLeft: "4px solid var(--pnp-accent)" }}
      >
        <p className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
          Build a graph of the week
        </p>

        {/* Grade */}
        <div className="mt-6">
          <span className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
            Grade
          </span>
          <div className="mt-2 flex gap-2" role="radiogroup" aria-label="Grade">
            {GRADES.map((g) => {
              const active = grade === g;
              return (
                <button
                  key={g}
                  type="button"
                  role="radio"
                  aria-checked={active}
                  onClick={() => handleGrade(g)}
                  className={`rounded-md border-2 px-5 py-2.5 text-base font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 ${
                    active
                      ? "border-pnp-accent bg-pnp-accent text-white"
                      : "border-pnp-gray-200 bg-white text-pnp-gray-700 hover:border-pnp-gray-400"
                  }`}
                >
                  {g}th
                </button>
              );
            })}
          </div>
        </div>

        {/* Standard */}
        <div className="mt-6">
          {showBoard ? (
            <>
              <span className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
                Standard
              </span>
              <div className="mt-3 space-y-6">
                {strandGroups.map(({ strand, standards }) => (
                  <div key={strand.code}>
                    <div className="mb-2 flex items-center gap-2">
                      <Tag variant="code">{strand.code}</Tag>
                      <h3 className="font-heading text-sm font-extrabold text-pnp-navy">
                        {strand.title}
                      </h3>
                    </div>
                    <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
                      {standards.map((s) => {
                        const isSel = s.standard === standard;
                        return (
                          <button
                            key={s.standard}
                            type="button"
                            aria-pressed={isSel}
                            onClick={() => handleStandard(s.standard)}
                            className={`flex flex-col rounded-md border-2 p-3 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 ${
                              isSel
                                ? "border-pnp-accent bg-pnp-accent-soft"
                                : "border-pnp-gray-200 bg-white hover:border-pnp-accent"
                            }`}
                          >
                            <span className="flex items-center justify-between gap-2">
                              <span className="font-heading text-sm font-bold text-pnp-navy">
                                {s.standard}
                              </span>
                              <span className="text-[11px] font-semibold text-pnp-gray-400">
                                {s.count} {s.count === 1 ? "graph" : "graphs"}
                              </span>
                            </span>
                            <span className="mt-0.5 text-xs leading-snug text-pnp-gray-600">
                              {s.topicTitle}
                            </span>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            // Collapsed summary once a standard is chosen.
            <div className="flex flex-wrap items-center justify-between gap-3 rounded-md border-2 border-pnp-accent bg-pnp-accent-soft px-4 py-3">
              <div className="min-w-0">
                <span className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
                  Standard
                </span>
                <div className="mt-1 flex flex-wrap items-center gap-2">
                  <Tag variant="code">{standard}</Tag>
                  {selected && (
                    <span className="text-sm font-medium text-pnp-navy">
                      {selected.topicTitle}
                    </span>
                  )}
                </div>
              </div>
              <Button tier="secondary" size="small" onClick={() => setExpanded(true)}>
                Change
              </Button>
            </div>
          )}
        </div>

        {/* Choose a graph — only when the standard has more than one week */}
        {standard && weeks.length > 1 && (
          <div className="mt-6">
            <span className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
              Choose a graph
            </span>
            <div className="mt-2 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {weeks.map((w) => {
                const active = entry?.file === w.file;
                return (
                  <button
                    key={w.file}
                    type="button"
                    onClick={() => setEntry(w)}
                    className={`flex h-full flex-col rounded-lg border-2 p-3.5 text-left transition-all ${
                      active
                        ? "border-pnp-accent bg-pnp-accent/5"
                        : "border-pnp-gray-200 bg-white hover:border-pnp-accent/50"
                    }`}
                  >
                    <div className="mb-1 flex items-center justify-between">
                      <span className="flex h-6 items-center justify-center rounded-full bg-pnp-navy px-2 text-xs font-bold text-white">
                        Wk {w.week}
                      </span>
                      <span className="text-[11px] font-semibold text-pnp-gray-400">
                        {chartLabel(w.chartType)}
                      </span>
                    </div>
                    <span className="text-sm font-bold text-pnp-navy">{w.concept}</span>
                    <span className="mt-1 line-clamp-3 text-xs text-pnp-gray-500">
                      {w.question}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Selected worksheet */}
      {entry && (
        <div className="mt-8">
          <GraphOfWeekView entry={entry} />
        </div>
      )}
    </div>
  );
}
