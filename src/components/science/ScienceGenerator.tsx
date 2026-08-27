"use client";

import { useState } from "react";
import {
  DOMAINS,
  DOMAIN_ACCENT,
  standardsByDomain,
  getStandard,
  type Figure,
} from "@/lib/library/science";
import StimulusView from "./StimulusView";

function figureLabel(fig?: Figure): string {
  switch (fig?.kind) {
    case "chart":
      return "Chart";
    case "table":
      return "Data table";
    case "image":
      return "Image";
    default:
      return "No figure";
  }
}

export default function ScienceGenerator() {
  const [pe, setPe] = useState("");
  const [stimIdx, setStimIdx] = useState<number | null>(null);

  const std = getStandard(pe);
  const accent = std ? DOMAIN_ACCENT[std.domain] ?? "var(--pnp-accent)" : "var(--pnp-accent)";

  const onStandardChange = (v: string) => {
    setPe(v);
    setStimIdx(null);
  };

  return (
    <div>
      <div
        className="rounded-lg bg-white p-6 shadow-sm md:p-8"
        style={{ borderLeft: "4px solid var(--pnp-accent)" }}
      >
        <p className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
          Build a stimulus
        </p>

        {/* Subject (grade fixed for now — biology only) */}
        <div className="mt-6">
          <label className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
            Subject
          </label>
          <div className="mt-2 flex flex-wrap gap-2">
            <button
              type="button"
              className="rounded-lg border-2 border-pnp-accent bg-pnp-accent px-5 py-2.5 text-base font-semibold text-white"
            >
              Biology
            </button>
            <button
              type="button"
              disabled
              className="cursor-not-allowed rounded-lg border-2 border-dashed border-pnp-gray-200 px-5 py-2.5 text-base font-semibold text-pnp-gray-400"
            >
              6th grade · soon
            </button>
          </div>
        </div>

        {/* Standard */}
        <div className="mt-6">
          <label className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
            Standard
          </label>
          <select
            value={pe}
            onChange={(e) => onStandardChange(e.target.value)}
            className="mt-2 w-full rounded-lg border-2 border-pnp-gray-200 bg-white px-4 py-3 text-sm font-medium text-pnp-navy outline-none transition-colors focus:border-pnp-accent"
          >
            <option value="">Select a standard…</option>
            {DOMAINS.map((d) => (
              <optgroup key={d.code} label={`${d.code} · ${d.title}`}>
                {standardsByDomain(d.code).map((s) => (
                  <option key={s.pe} value={s.pe}>
                    {s.pe} — {s.pe_text.slice(0, 70)}
                    {s.pe_text.length > 70 ? "…" : ""}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </div>

        {/* Choose a stimulus */}
        {std && (
          <div className="mt-6">
            <label className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
              Choose a stimulus
            </label>
            <div className="mt-2 grid gap-3 sm:grid-cols-3">
              {std.stimuli.map((s, i) => {
                const active = stimIdx === i;
                return (
                  <button
                    key={i}
                    type="button"
                    onClick={() => setStimIdx(i)}
                    className={`flex h-full flex-col rounded-lg border-2 p-3.5 text-left transition-all ${
                      active
                        ? "border-pnp-accent bg-pnp-accent/5"
                        : "border-pnp-gray-200 bg-white hover:border-pnp-accent/50"
                    }`}
                  >
                    <div className="mb-1 flex items-center justify-between">
                      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-pnp-navy text-xs font-bold text-white">
                        {i + 1}
                      </span>
                      <span className="text-[11px] font-semibold text-pnp-gray-400">
                        {figureLabel(s.figure)} · {s.questions.length} items
                      </span>
                    </div>
                    <span className="text-sm font-bold text-pnp-navy">{s.title}</span>
                    <span className="mt-1 line-clamp-3 text-xs text-pnp-gray-500">
                      {s.phenomenon}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Selected stimulus */}
      {std && stimIdx !== null && (
        <div className="mt-8">
          <StimulusView
            stimulus={std.stimuli[stimIdx]}
            pe={std.pe}
            peText={std.pe_text}
            index={stimIdx + 1}
            accent={accent}
          />
        </div>
      )}
    </div>
  );
}
