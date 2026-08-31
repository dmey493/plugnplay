/**
 * Skill graph layout — turns one standard's skills into a layered DAG.
 *
 * The authored data already contains a graph: every skill's
 * `next_steps.if_pass` names the skill (or skills) a passing student moves
 * to. Read across the corpus that routing is NOT a chain — 68 of 69
 * standards contain at least one skill that two other skills feed into,
 * and every standard has more than one entry point. Two prerequisites run
 * in parallel, carry the same weight, and converge on the bigger skill
 * downstream.
 *
 * This module recovers that shape:
 *   layer (x) = how far along the progression a skill sits
 *   row   (y) = which parallel strand it belongs to
 *
 * Layer is seeded from the skill's rung (Foundation → Looking Back →
 * the four On Grade proficiency bands → Looking Forward) and then pushed
 * right until it clears every predecessor, so an edge always points
 * forward and a column keeps its rung meaning. Across the corpus only 6
 * of 528 columns end up holding more than one rung, which is what lets
 * the header label them.
 *
 * Read by the intervention page's Map view (`SkillMap`); the Line view
 * uses the same layering to order its rail.
 */

import {
  COLUMN_META,
  PLD_BAND_LABELS,
  isPacketReady,
  nextStepRefs,
  progressionIndex,
  type PldBand,
  type Skill,
  type SkillColumn,
  type SkillData,
} from "./skills";

export interface GraphNode {
  skill: Skill;
  column: SkillColumn;
  band?: PldBand;
  /** 1-based progression order, or null when the skill isn't a step. */
  step: number | null;
  ready: boolean;
  layer: number;
  row: number;
}

export interface GraphEdge {
  from: string;
  to: string;
  /** How many layers the edge crosses. 1 = a short hop to the next column. */
  span: number;
}

export interface RungHeader {
  label: string;
  accent: string;
  phase: SkillColumn;
  /** First column this header sits over, and how many columns it spans. */
  startLayer: number;
  span: number;
}

export interface SkillGraph {
  nodes: GraphNode[];
  byId: Map<string, GraphNode>;
  edges: GraphEdge[];
  /** Nodes grouped by layer, left to right. */
  layers: GraphNode[][];
  headers: RungHeader[];
  columns: number;
  rows: number;
  /** Skills with no routing edge either way — drawn, but off the wiring. */
  isolated: string[];
}

/** Where a rung starts before predecessors push it right. */
const BAND_RANK: Record<PldBand, number> = {
  below: 2,
  approaching: 3,
  at: 4,
  above: 5,
};

function baseRank(column: SkillColumn, band?: PldBand): number {
  if (column === "foundation") return 0;
  if (column === "looking_back") return 1;
  if (column === "on_grade") return band ? BAND_RANK[band] : 2;
  return 6;
}

/** Short rung name — the full band label is too wide for a column header. */
const BAND_SHORT: Record<PldBand, string> = {
  below: "Below",
  approaching: "Approaching",
  at: "At",
  above: "Above",
};

export function rungLabel(column: SkillColumn, band?: PldBand): string {
  if (column === "on_grade") return band ? BAND_SHORT[band] : "On Grade";
  return COLUMN_META[column].label;
}

export function bandLabel(band: PldBand): string {
  return PLD_BAND_LABELS[band];
}

export { BAND_SHORT };

export function buildSkillGraph(data: SkillData): SkillGraph {
  const skills = data.skills;
  const ids = new Set(skills.map((s) => s.skill_id));
  const order = new Map(skills.map((s, i) => [s.skill_id, i]));

  // ── Edges: "pass this, go here", kept inside the standard ────────────
  const out = new Map<string, string[]>();
  for (const s of skills) {
    const targets = nextStepRefs(s.next_steps?.if_pass).filter(
      (t) => ids.has(t) && t !== s.skill_id,
    );
    out.set(s.skill_id, targets);
  }

  // Two standards route a pair of skills at each other (6.NS.3 S5↔S7,
  // 7.NS.4 S3↔S4). A cycle has no layering, so drop the back edge —
  // depth-first, keeping the first direction reached.
  const state = new Map<string, 0 | 1 | 2>();
  const dropped = new Set<string>();
  const visit = (id: string) => {
    state.set(id, 1);
    for (const t of out.get(id) ?? []) {
      const st = state.get(t) ?? 0;
      if (st === 1) dropped.add(`${id}->${t}`);
      else if (st === 0) visit(t);
    }
    state.set(id, 2);
  };
  for (const s of skills) if ((state.get(s.skill_id) ?? 0) === 0) visit(s.skill_id);

  const preds = new Map<string, string[]>(skills.map((s) => [s.skill_id, []]));
  const edgePairs: Array<[string, string]> = [];
  for (const s of skills) {
    for (const t of out.get(s.skill_id) ?? []) {
      if (dropped.has(`${s.skill_id}->${t}`)) continue;
      edgePairs.push([s.skill_id, t]);
      preds.get(t)!.push(s.skill_id);
    }
  }

  // ── Layers: rung, then pushed right past every predecessor ───────────
  const layer = new Map<string, number>(
    skills.map((s) => [s.skill_id, baseRank(s.column, s.pld_band)]),
  );
  // The graph is small (about 10 nodes) and now acyclic, so relaxing to a
  // fixed point costs nothing and needs no topological sort.
  for (let pass = 0; pass < skills.length + 1; pass++) {
    let changed = false;
    for (const s of skills) {
      for (const p of preds.get(s.skill_id)!) {
        const want = layer.get(p)! + 1;
        if (layer.get(s.skill_id)! < want) {
          layer.set(s.skill_id, want);
          changed = true;
        }
      }
    }
    if (!changed) break;
  }

  // ── Spill: a rung wraps rather than towers ───────────────────────────
  // Two standards (6.AF.3, 6.RP.4) author most of their on-grade routing
  // as prose with no skill id in it, so half a dozen skills land on the
  // same rung with nothing wiring them. Stacked, that column is a tower
  // nobody can read. Wrapping it into extra columns of the same rung
  // keeps the claim honest (still one rung) and the drawing flat.
  // Renumbering is also what drops empty rungs, so there are no blank
  // columns mid-progression.
  const MAX_ROWS = 3;
  const wired = new Set<string>();
  for (const [from, to] of edgePairs) {
    wired.add(from);
    wired.add(to);
  }
  const byLayer = new Map<number, string[]>();
  for (const s of skills) {
    const l = layer.get(s.skill_id)!;
    byLayer.set(l, [...(byLayer.get(l) ?? []), s.skill_id]);
  }
  let nextLayer = 0;
  for (const l of [...byLayer.keys()].sort((a, b) => a - b)) {
    const here = byLayer.get(l)!;
    // Keep the wired skills in the first column of the rung so the through
    // line stays straight; the loose ones spill after them.
    const arranged = [
      ...here.filter((id) => wired.has(id)),
      ...here.filter((id) => !wired.has(id)),
    ];
    for (let i = 0; i < arranged.length; i += MAX_ROWS) {
      for (const id of arranged.slice(i, i + MAX_ROWS)) layer.set(id, nextLayer);
      nextLayer++;
    }
  }

  const columns = nextLayer;

  // ── Rows: keep a chain on one line, stack parallel strands ───────────
  const row = new Map<string, number>();
  const layers: GraphNode[][] = Array.from({ length: columns }, () => []);
  const nodeFor = (skill: Skill): GraphNode => ({
    skill,
    column: skill.column,
    band: skill.pld_band,
    step: progressionIndex(data, skill.skill_id),
    ready: isPacketReady(skill),
    layer: layer.get(skill.skill_id)!,
    row: row.get(skill.skill_id) ?? 0,
  });

  for (let l = 0; l < columns; l++) {
    const inLayer = skills.filter((s) => layer.get(s.skill_id) === l);

    // A node wants to sit level with whatever feeds it (the barycenter
    // heuristic), so an unbranched chain draws as a straight line.
    const want = new Map<string, number | null>();
    for (const s of inLayer) {
      const placed = preds
        .get(s.skill_id)!
        .map((p) => row.get(p))
        .filter((r): r is number => r !== undefined);
      want.set(
        s.skill_id,
        placed.length ? placed.reduce((a, b) => a + b, 0) / placed.length : null,
      );
    }

    const wantOf = (id: string): number | null => want.get(id) ?? null;
    const sorted = [...inLayer].sort((a, b) => {
      const wa = wantOf(a.skill_id);
      const wb = wantOf(b.skill_id);
      if (wa !== null && wb !== null && wa !== wb) return wa - wb;
      if (wa === null && wb !== null) return 1; // unfed strands settle below
      if (wa !== null && wb === null) return -1;
      return order.get(a.skill_id)! - order.get(b.skill_id)!;
    });

    const taken = new Set<number>();
    for (const s of sorted) {
      const target = Math.round(wantOf(s.skill_id) ?? 0);
      let r = target;
      for (let d = 1; taken.has(r); d++) {
        const candidate = d % 2 === 1 ? target + ((d + 1) >> 1) : target - (d >> 1);
        r = candidate < 0 ? target + ((d + 1) >> 1) : candidate;
      }
      taken.add(r);
      row.set(s.skill_id, r);
    }
  }

  // Rows can end up sparse (a strand pushed to row 3 with row 1 empty);
  // compact them so the drawing has no dead bands.
  const usedRows = [...new Set([...row.values()])].sort((a, b) => a - b);
  const compact = new Map(usedRows.map((r, i) => [r, i]));
  for (const [id, r] of row) row.set(id, compact.get(r)!);

  const nodes = skills.map(nodeFor);
  for (const n of nodes) layers[n.layer].push(n);
  for (const l of layers) l.sort((a, b) => a.row - b.row);

  const byId = new Map(nodes.map((n) => [n.skill.skill_id, n]));
  const edges: GraphEdge[] = edgePairs.map(([from, to]) => ({
    from,
    to,
    span: byId.get(to)!.layer - byId.get(from)!.layer,
  }));

  // ── Column headers: consecutive layers sharing a rung merge into one ──
  const headers: RungHeader[] = [];
  for (let l = 0; l < columns; l++) {
    const here = layers[l];
    if (here.length === 0) continue;
    // 6 columns in the whole corpus hold two rungs; the majority wins.
    const tally = new Map<string, { n: number; node: GraphNode }>();
    for (const n of here) {
      const key = `${n.column}|${n.band ?? ""}`;
      const t = tally.get(key);
      if (t) t.n++;
      else tally.set(key, { n: 1, node: n });
    }
    const win = [...tally.values()].sort((a, b) => b.n - a.n)[0].node;
    const label = rungLabel(win.column, win.band);
    const last = headers[headers.length - 1];
    if (last && last.label === label && last.startLayer + last.span === l) {
      last.span++;
    } else {
      headers.push({
        label,
        accent: COLUMN_META[win.column].accent,
        phase: win.column,
        startLayer: l,
        span: 1,
      });
    }
  }

  return {
    nodes,
    byId,
    edges,
    layers,
    headers,
    columns,
    rows: usedRows.length,
    isolated: skills.map((s) => s.skill_id).filter((id) => !wired.has(id)),
  };
}
