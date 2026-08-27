"use client";

import { useState } from "react";
import type { ContentEnvelope, TaskBody } from "@/lib/core/types";
import { displayStandardsFor, type StandardsSystem } from "@/lib/library/tasks-filter";
import { getStandardLabel } from "@/lib/standards/standards-labels";

/**
 * Toggleable standards display for the task detail page header.
 * Default system is Indiana 2023. The Common Core button switches the
 * visible chips to the CCSS-M cross-references. Codes are filtered to
 * match the task's grades so a 7th-grade task doesn't surface 8.x codes
 * just because the agent tagged an extension reach standard.
 */
export default function StandardsBadges({ task }: { task: ContentEnvelope }) {
  const [system, setSystem] = useState<StandardsSystem>("indiana");
  const codes = displayStandardsFor(task, system);
  const body = task.body as TaskBody;
  const concepts = body.concepts ?? [];

  return (
    <div className="flex flex-col gap-2">
      {/* Concepts row. Tag-style chips: rounded-md (not pill, since these
          aren't interactive), small, muted. On the dark banner so we use
          white/transparent surfaces rather than the light-mode Tag tone. */}
      {concepts.length > 0 && (
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-xs font-semibold uppercase tracking-wider text-white/60">
            Concepts:
          </span>
          {concepts.map((c) => (
            <span
              key={c}
              className="inline-flex select-none items-center rounded-md bg-white/15 px-2 py-0.5 text-xs font-semibold text-white"
            >
              {c}
            </span>
          ))}
        </div>
      )}

      {/* Standards row — system toggle + codes with descriptions. */}
      <div className="flex flex-wrap items-center gap-2">
        <div
          className="inline-flex overflow-hidden rounded-md border border-white/30"
          role="radiogroup"
          aria-label="Standards system"
        >
          <button
            role="radio"
            aria-checked={system === "indiana"}
            onClick={() => setSystem("indiana")}
            className={`px-2.5 py-0.5 text-xs font-semibold transition-colors ${
              system === "indiana"
                ? "bg-white text-pnp-navy"
                : "text-white/80 hover:bg-white/10"
            }`}
            title="Indiana 2023 Academic Standards for Mathematics"
          >
            Indiana 2023
          </button>
          <button
            role="radio"
            aria-checked={system === "commonCore"}
            onClick={() => setSystem("commonCore")}
            className={`px-2.5 py-0.5 text-xs font-semibold transition-colors ${
              system === "commonCore"
                ? "bg-white text-pnp-navy"
                : "text-white/80 hover:bg-white/10"
            }`}
            title="Common Core State Standards — Math"
          >
            Common Core
          </button>
        </div>
        {codes.length === 0 ? (
          <span className="text-xs italic text-white/60">no codes for this system</span>
        ) : (
          codes.map((s) => {
            const label = getStandardLabel(s, system);
            return (
              <span
                key={s}
                className="inline-flex items-center gap-1.5 rounded border border-white/30 bg-white/10 px-2 py-0.5 text-xs text-white/90"
                title={label || s}
              >
                <span className="font-mono font-semibold">{s}</span>
                {label && (
                  <span className="hidden text-white/70 sm:inline">— {label}</span>
                )}
              </span>
            );
          })
        )}
      </div>
    </div>
  );
}
