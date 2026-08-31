"use client";

import { shortSkillTag, type PldBand } from "@/lib/intervention/skills";
import type { GraphNode } from "@/lib/intervention/skill-graph";
import { BAND_SHORT } from "@/lib/intervention/skill-graph";

/**
 * The one skill card the test bench draws, shared by the linear stem and
 * the map so the two layouts differ only in arrangement.
 *
 * Fixed size: the map positions cards absolutely and draws the wiring
 * between them, which needs the geometry up front.
 */

export const CARD_W = 184;
export const CARD_H = 120;

/** Light-to-dark ramp: the darker the chip, the higher the band. */
export const BAND_CHIP: Record<PldBand, string> = {
  below: "bg-pnp-gray-100 text-pnp-gray-700",
  approaching: "bg-sky-100 text-sky-800",
  at: "bg-sky-200 text-sky-900",
  above: "bg-pnp-navy text-white",
};

export default function SkillNodeCard({
  node,
  accent,
  selected,
  highlighted = false,
  dimmed = false,
  /** Map view only: this card feeds, or is fed by, the selected one. */
  linked = false,
  onSelect,
  cardRef,
}: {
  node: GraphNode;
  accent: string;
  selected: boolean;
  highlighted?: boolean;
  dimmed?: boolean;
  linked?: boolean;
  onSelect: () => void;
  cardRef?: (el: HTMLButtonElement | null) => void;
}) {
  const { skill, step, ready } = node;

  return (
    <button
      ref={cardRef}
      type="button"
      onClick={onSelect}
      aria-current={selected ? "true" : undefined}
      title={skill.name}
      style={{ width: CARD_W, height: CARD_H }}
      className={`relative flex flex-shrink-0 flex-col overflow-hidden rounded-xl border-2 p-3 pt-3.5 text-left transition-[transform,box-shadow,border-color] duration-150 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 ${
        selected
          ? "-translate-x-0.5 -translate-y-0.5 border-pnp-navy shadow-[6px_6px_0_var(--pnp-navy)]"
          : linked
            ? "border-pnp-accent shadow-[3px_3px_0_var(--pnp-navy)] hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[5px_5px_0_var(--pnp-navy)]"
            : "border-pnp-navy shadow-[3px_3px_0_var(--pnp-navy)] hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[5px_5px_0_var(--pnp-navy)]"
      } ${dimmed ? "opacity-40" : ""} ${ready ? "bg-white" : "bg-pnp-gray-50"}`}
    >
      <span
        aria-hidden="true"
        className="absolute inset-x-0 top-0 h-1.5"
        style={{ backgroundColor: accent }}
      />

      <span className="flex items-center gap-2">
        <span
          className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full text-[11px] font-bold text-white"
          style={{ backgroundColor: accent }}
        >
          {step ?? "•"}
        </span>
        <span
          title={skill.skill_id}
          className="rounded border border-pnp-gray-300 bg-pnp-gray-50 px-1 py-px font-mono text-[10px] font-bold leading-tight text-pnp-gray-600"
        >
          {shortSkillTag(skill.skill_id)}
        </span>
        {highlighted && (
          <span
            title="Targeted by the lesson you picked"
            className="ml-auto h-2.5 w-2.5 flex-shrink-0 rounded-full bg-pnp-accent"
          />
        )}
      </span>

      <span className="mt-2 line-clamp-3 font-heading text-[13px] font-bold leading-snug text-pnp-navy">
        {skill.name}
      </span>

      <span className="mt-auto flex items-center justify-between gap-2 pt-1.5">
        {node.band ? (
          <span
            className={`rounded px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wide ${BAND_CHIP[node.band]}`}
          >
            {BAND_SHORT[node.band]}
          </span>
        ) : (
          <span />
        )}
        {!ready && (
          <span className="text-[10px] font-semibold uppercase tracking-wide text-pnp-gray-400">
            Soon
          </span>
        )}
      </span>
    </button>
  );
}
