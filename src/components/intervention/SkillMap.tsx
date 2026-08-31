"use client";

import { useMemo } from "react";
import { COLUMN_META } from "@/lib/intervention/skills";
import type { SkillGraph, GraphNode } from "@/lib/intervention/skill-graph";
import SkillNodeCard, { CARD_W, CARD_H } from "./SkillNodeCard";

/**
 * SkillMap — the progression drawn as the graph the data actually is.
 *
 * Columns run left to right (the rungs, Foundation out to Looking
 * Forward); rows stack the strands that run in parallel and carry the
 * same weight. The lines are the authored pass routing, so where two
 * skills converge on a third, you see it converge.
 *
 * Test bench only. See `@/lib/intervention/skill-graph` for the layout.
 */

const HGAP = 56;
const VGAP = 26;

/** Column centre for a layer index. */
const colX = (layer: number) => layer * (CARD_W + HGAP);
const rowY = (row: number) => row * (CARD_H + VGAP);

/** The wiring between two cards: out of the right edge, into the left. */
function edgePath(from: GraphNode, to: GraphNode): string {
  const x1 = colX(from.layer) + CARD_W;
  const y1 = rowY(from.row) + CARD_H / 2;
  const x2 = colX(to.layer);
  const y2 = rowY(to.row) + CARD_H / 2;
  const reach = Math.max(HGAP * 0.55, (x2 - x1) * 0.35);

  // A long hop would otherwise cut straight through the cards between it,
  // so bow it away from the rows it passes.
  const bow = to.layer - from.layer > 1 ? (from.row <= to.row ? -22 : 22) : 0;
  return `M ${x1} ${y1} C ${x1 + reach} ${y1 + bow}, ${x2 - reach} ${y2 + bow}, ${x2} ${y2}`;
}

export default function SkillMap({
  graph,
  selectedId,
  onSelect,
  highlightedSkillIds,
  lessonActive,
  boardRef,
  cardRefs,
}: {
  graph: SkillGraph;
  selectedId: string | null;
  onSelect: (id: string) => void;
  highlightedSkillIds: Set<string>;
  lessonActive: boolean;
  boardRef?: React.Ref<HTMLDivElement>;
  cardRefs?: React.RefObject<Map<string, HTMLButtonElement>>;
}) {
  const width = graph.columns * CARD_W + (graph.columns - 1) * HGAP;
  const height = graph.rows * CARD_H + (graph.rows - 1) * VGAP;

  // Which skills sit either side of the selected one on the routing.
  const linked = useMemo(() => {
    const set = new Set<string>();
    if (!selectedId) return set;
    for (const e of graph.edges) {
      if (e.from === selectedId) set.add(e.to);
      if (e.to === selectedId) set.add(e.from);
    }
    return set;
  }, [graph.edges, selectedId]);

  return (
    <div ref={boardRef} className="overflow-x-auto pb-2">
      <div className="min-w-max">
        {/* Rung ruler: one block per run of columns sharing a rung. */}
        <div className="relative mb-3" style={{ width, height: 30 }}>
          {graph.headers.map((h) => {
            const w = h.span * CARD_W + (h.span - 1) * HGAP;
            return (
              <div
                key={`${h.label}-${h.startLayer}`}
                className="absolute top-0"
                style={{ left: colX(h.startLayer), width: w }}
              >
                <span
                  aria-hidden="true"
                  className="block h-1.5 rounded-full"
                  style={{ backgroundColor: h.accent }}
                />
                <div className="mt-1.5 flex items-baseline gap-1.5 px-0.5">
                  <span className="font-heading text-xs font-extrabold uppercase tracking-wide text-pnp-navy">
                    {h.label}
                  </span>
                  {h.phase === "on_grade" && (
                    <span className="text-[10px] font-semibold uppercase tracking-wide text-pnp-gray-400">
                      on grade
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        <div className="relative" style={{ width, height }}>
          {/* Wiring sits under the cards. */}
          <svg
            className="absolute inset-0"
            width={width}
            height={height}
            aria-hidden="true"
          >
            <defs>
              <marker
                id="stem-arrow"
                markerWidth="7"
                markerHeight="7"
                refX="6"
                refY="3.5"
                orient="auto"
              >
                <path d="M0,0 L7,3.5 L0,7 z" fill="var(--pnp-gray-400)" />
              </marker>
              <marker
                id="stem-arrow-live"
                markerWidth="7"
                markerHeight="7"
                refX="6"
                refY="3.5"
                orient="auto"
              >
                <path d="M0,0 L7,3.5 L0,7 z" fill="var(--pnp-accent)" />
              </marker>
            </defs>
            {graph.edges.map((e) => {
              const from = graph.byId.get(e.from);
              const to = graph.byId.get(e.to);
              if (!from || !to) return null;
              const live = selectedId === e.from || selectedId === e.to;
              return (
                <path
                  key={`${e.from}->${e.to}`}
                  d={edgePath(from, to)}
                  fill="none"
                  stroke={live ? "var(--pnp-accent)" : "var(--pnp-gray-300)"}
                  strokeWidth={live ? 3 : 2}
                  markerEnd={live ? "url(#stem-arrow-live)" : "url(#stem-arrow)"}
                  opacity={selectedId && !live ? 0.45 : 1}
                />
              );
            })}
          </svg>

          {graph.nodes.map((node) => (
            <div
              key={node.skill.skill_id}
              className="absolute"
              style={{ left: colX(node.layer), top: rowY(node.row) }}
            >
              <SkillNodeCard
                node={node}
                accent={COLUMN_META[node.column].accent}
                selected={node.skill.skill_id === selectedId}
                highlighted={highlightedSkillIds.has(node.skill.skill_id)}
                dimmed={lessonActive && !highlightedSkillIds.has(node.skill.skill_id)}
                linked={linked.has(node.skill.skill_id)}
                onSelect={() => onSelect(node.skill.skill_id)}
                cardRef={(el) => {
                  if (!cardRefs) return;
                  if (el) cardRefs.current.set(node.skill.skill_id, el);
                  else cardRefs.current.delete(node.skill.skill_id);
                }}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
