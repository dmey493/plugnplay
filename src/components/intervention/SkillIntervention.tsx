"use client";

import { useState, useRef, useEffect, useMemo, useCallback } from "react";
import {
  AVAILABLE_STANDARDS,
  BUCKET_ORDER,
  COLUMN_META,
  isV2,
  progressionStep,
  shortSkillTag,
  nextStepRefs,
  PLD_BAND_LABELS,
  PLD_BAND_ORDER,
  type PldBand,
  type Skill,
  type SkillColumn,
  type SkillData,
} from "@/lib/intervention/skills";
import {
  buildSkillGraph,
  BAND_SHORT,
  type GraphNode,
  type SkillGraph,
} from "@/lib/intervention/skill-graph";
import type { LessonNav } from "@/lib/library/lessons";
import type { CheckpointNav } from "@/lib/standards/checkpoints";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import Tag from "@/components/ui/Tag";
import DiagnosticModal from "./DiagnosticModal";
import SkillPacketModal from "./SkillPacketModal";
import SkillMap from "./SkillMap";
import SkillNodeCard, { BAND_CHIP } from "./SkillNodeCard";
import StandardPicker from "@/components/standards/StandardPicker";

/**
 * SkillIntervention — the Tier 2 progression view (route: /math/intervention).
 *
 * A standard's skills are not a list and not a chain. The authored
 * `next_steps.if_pass` routing is a graph: 68 of 69 standards contain a
 * skill that two others feed into, and every standard has more than one
 * entry point. Two prerequisites run in parallel, carry the same weight,
 * and converge on the bigger skill downstream.
 *
 * So the page draws that, in two arrangements:
 *
 *   Map  — columns are rungs (Foundation out to Looking Forward), rows are
 *          the parallel strands, lines are the pass routing. Convergence
 *          shows as convergence.
 *   Line — every skill on one left-to-right rail, no wiring. Easier to
 *          scan, but it flattens two parallel skills into a sequence.
 *
 * Either way the board carries only what a teacher needs in order to
 * choose: rung, step number, skill id, name. Rationale, routing and the
 * worksheet button live in one detail panel underneath, so the eye scans
 * a single board instead of ten competing cards.
 *
 * Layout math (layering, cycle breaking, row packing) is in
 * `@/lib/intervention/skill-graph`.
 */

type View = "map" | "line";

interface BandCluster {
  band: PldBand | null;
  nodes: GraphNode[];
}

interface PhaseGroup {
  column: SkillColumn;
  label: string;
  description: string;
  accent: string;
  clusters: BandCluster[];
  count: number;
}

/** The Line view: buckets in progression order, On Grade split by rung.
 *  Within a cluster the routing order (layer, then row) wins over file
 *  order, so the two views tell the same story. */
function buildPhases(data: SkillData, graph: SkillGraph): PhaseGroup[] {
  const phases: PhaseGroup[] = [];
  const byReading = (a: GraphNode, b: GraphNode) =>
    a.layer - b.layer || a.row - b.row;

  for (const column of BUCKET_ORDER) {
    const config = data.skill_columns[column];
    const nodes = graph.nodes.filter((n) => n.column === column).sort(byReading);
    if (!config || nodes.length === 0) continue;

    const clusters: BandCluster[] =
      column === "on_grade"
        ? [
            ...PLD_BAND_ORDER.map((band) => ({
              band: band as PldBand | null,
              nodes: nodes.filter((n) => n.band === band),
            })),
            { band: null, nodes: nodes.filter((n) => !n.band) },
          ].filter((c) => c.nodes.length > 0)
        : [{ band: null, nodes }];

    phases.push({
      column,
      label: config.label,
      description: config.description,
      accent: COLUMN_META[column].accent,
      clusters,
      count: nodes.length,
    });
  }

  return phases;
}

/** The line between two nodes on the rail. Decorative: the stem itself. */
function Segment({ wide = false }: { wide?: boolean }) {
  return (
    <span
      aria-hidden="true"
      className={`h-0.5 flex-shrink-0 self-center bg-pnp-gray-300 ${wide ? "w-8" : "w-4"}`}
    />
  );
}

/** The joint between two phases on the rail. */
function PhaseJoin() {
  return (
    <span
      aria-hidden="true"
      className="flex flex-shrink-0 items-center self-center px-1 text-pnp-gray-400"
    >
      <span className="h-0.5 w-5 bg-pnp-gray-300" />
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M9 6l6 6-6 6" />
      </svg>
      <span className="h-0.5 w-5 bg-pnp-gray-300" />
    </span>
  );
}

/** One branch of next_steps, rendered as the tags a teacher can go find. */
function RouteChips({
  label,
  tone,
  refs,
}: {
  label: string;
  tone: "pass" | "fail";
  refs: string[];
}) {
  if (refs.length === 0) return null;
  return (
    <span className="inline-flex items-center gap-1">
      <span
        className={`font-semibold ${tone === "pass" ? "text-emerald-700" : "text-rose-700"}`}
      >
        {label}
      </span>
      <span aria-hidden="true" className="text-pnp-gray-400">
        &rarr;
      </span>
      {refs.map((id) => (
        <span
          key={id}
          title={id}
          className={`rounded px-1 py-px font-mono text-[10px] font-bold ${
            tone === "pass"
              ? "bg-emerald-50 text-emerald-800"
              : "bg-rose-50 text-rose-800"
          }`}
        >
          {shortSkillTag(id)}
        </span>
      ))}
    </span>
  );
}

/** Everything the rail leaves off, for one skill at a time. */
function SkillDetailPanel({
  node,
  data,
  graph,
  onGenerate,
  onJump,
}: {
  node: GraphNode;
  data: SkillData;
  graph: SkillGraph;
  onGenerate: () => void;
  onJump: (id: string) => void;
}) {
  const { skill, step, ready } = node;
  const rationale = progressionStep(data, skill.skill_id)?.rationale;
  const preview = skill.sample_items?.[1] ?? skill.sample_items?.[0];
  const passRefs = nextStepRefs(skill.next_steps?.if_pass);
  const failRefs = nextStepRefs(skill.next_steps?.if_fail);
  const accent = COLUMN_META[node.column].accent;

  // What has to be in place before this skill, straight off the graph.
  const feeders = graph.edges
    .filter((e) => e.to === skill.skill_id)
    .map((e) => graph.byId.get(e.from))
    .filter((n): n is GraphNode => !!n);

  return (
    <Card accent={accent} className="p-6 pt-7">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span
              className="flex h-6 w-6 items-center justify-center rounded-full text-[11px] font-bold text-white"
              style={{ backgroundColor: accent }}
            >
              {step ?? "•"}
            </span>
            <span className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
              {COLUMN_META[node.column].label}
            </span>
            {node.band && (
              <span
                className={`rounded px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide ${BAND_CHIP[node.band]}`}
              >
                {PLD_BAND_LABELS[node.band]}
              </span>
            )}
            <span
              title={skill.skill_id}
              className="rounded border border-pnp-gray-300 bg-pnp-gray-50 px-1.5 py-px font-mono text-[10px] font-bold text-pnp-gray-600"
            >
              {skill.skill_id}
            </span>
          </div>
          <h3 className="mt-2 font-heading text-lg font-extrabold leading-snug text-pnp-navy">
            {skill.name}
          </h3>
        </div>

        <Button tier="primary" onClick={onGenerate} disabled={!ready}>
          {ready ? "Generate worksheet" : "Coming soon"}
        </Button>
      </div>

      {feeders.length > 0 && (
        <p className="mt-3 flex flex-wrap items-center gap-2 text-xs text-pnp-gray-500">
          <span className="font-semibold uppercase tracking-wide">
            {feeders.length > 1 ? "Both of these feed it" : "Comes after"}
          </span>
          {feeders.map((f) => (
            <button
              key={f.skill.skill_id}
              type="button"
              onClick={() => onJump(f.skill.skill_id)}
              className="rounded border border-pnp-gray-300 bg-white px-1.5 py-px font-mono text-[10px] font-bold text-pnp-gray-700 transition-colors hover:border-pnp-accent hover:text-pnp-accent"
            >
              {shortSkillTag(f.skill.skill_id)}
            </button>
          ))}
        </p>
      )}

      {(rationale || preview) && (
        <div className="mt-4 border-t border-pnp-gray-100 pt-4">
          {rationale && (
            <p className="text-sm leading-relaxed text-pnp-gray-600">{rationale}</p>
          )}
          {preview && (
            <p className="mt-3 whitespace-pre-wrap break-words rounded-lg bg-pnp-gray-50 px-4 py-3 text-sm italic text-pnp-gray-600">
              {preview.stem}
            </p>
          )}
        </div>
      )}

      {skill.canonical_error && (
        <p className="mt-3 text-sm text-pnp-gray-600">
          <span className="font-bold text-pnp-navy">Watch for: </span>
          {skill.canonical_error.pattern}
        </p>
      )}

      {(passRefs.length > 0 || failRefs.length > 0) && (
        <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-1 border-t border-pnp-gray-100 pt-3 text-xs text-pnp-gray-500">
          <RouteChips label="Pass" tone="pass" refs={passRefs} />
          <RouteChips label="Miss" tone="fail" refs={failRefs} />
        </div>
      )}
    </Card>
  );
}

/** All textbook lessons (across the grade's modules) that map to a standard. */
interface LessonRef {
  label: string;
  moduleNumber: number;
  moduleTitle: string;
  skillIds: string[];
}

function lessonsForStandard(
  lessonNav: LessonNav,
  grade: number,
  code: string,
): LessonRef[] {
  const out: LessonRef[] = [];
  for (const mod of lessonNav[grade] ?? []) {
    for (const lesson of mod.lessons) {
      if (lesson.standard === code) {
        out.push({
          label: lesson.label,
          moduleNumber: mod.moduleNumber,
          moduleTitle: mod.title,
          skillIds: lesson.skillIds,
        });
      }
    }
  }
  return out;
}

const VIEWS: Array<{ id: View; label: string; hint: string }> = [
  { id: "map", label: "Map", hint: "Parallel strands and where they converge" },
  { id: "line", label: "Line", hint: "One rail, left to right" },
];

export default function SkillIntervention({
  lessonNav,
  checkpointNav,
}: {
  lessonNav: LessonNav;
  checkpointNav?: CheckpointNav;
}) {
  const [grade, setGrade] = useState<number>(6);
  const [standard, setStandard] = useState<string>("");
  const [view, setView] = useState<View>("map");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [packetFor, setPacketFor] = useState<Skill | null>(null);
  const [diagnosticOpen, setDiagnosticOpen] = useState(false);
  const [progressOpen, setProgressOpen] = useState(false);
  const [selectedLesson, setSelectedLesson] = useState<string | undefined>(undefined);

  const data = standard ? AVAILABLE_STANDARDS[standard] : null;
  const graph = useMemo(() => (data ? buildSkillGraph(data) : null), [data]);
  const phases = useMemo(
    () => (data && graph ? buildPhases(data, graph) : []),
    [data, graph],
  );

  /** Reading order, shared by both views: column first, then row. */
  const ordered = useMemo(
    () =>
      graph
        ? [...graph.nodes].sort((a, b) => a.layer - b.layer || a.row - b.row)
        : [],
    [graph],
  );

  const lessons = standard ? lessonsForStandard(lessonNav, grade, standard) : [];
  const highlightedSkillIds = useMemo(
    () =>
      new Set(
        (selectedLesson && lessons.find((l) => l.label === selectedLesson)?.skillIds) ||
          [],
      ),
    // `lessons` is derived fresh each render; the pick is what changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [standard, selectedLesson],
  );
  const lessonActive = highlightedSkillIds.size > 0;

  const boardRef = useRef<HTMLDivElement>(null);
  const cardRefs = useRef(new Map<string, HTMLButtonElement>());
  const stemRef = useRef<HTMLDivElement>(null);
  const scrollPending = useRef(false);

  // Open on the lesson's first skill if one was picked, else on the first
  // On Grade skill: that's the grade-level entry point, and it parks the
  // view in the middle of the story rather than at the far-below end.
  useEffect(() => {
    if (!graph) {
      setSelectedId(null);
      return;
    }
    const lessonFirst = ordered.find((n) => highlightedSkillIds.has(n.skill.skill_id));
    const onGradeFirst = ordered.find((n) => n.column === "on_grade");
    setSelectedId((lessonFirst ?? onGradeFirst ?? ordered[0])?.skill.skill_id ?? null);
  }, [graph, ordered, highlightedSkillIds]);

  // Keep the selected card on screen as selection moves.
  useEffect(() => {
    if (!selectedId) return;
    cardRefs.current
      .get(selectedId)
      ?.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
  }, [selectedId, view]);

  useEffect(() => {
    if (standard && scrollPending.current) {
      scrollPending.current = false;
      stemRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [standard]);

  /** Left/right walk the reading order; up/down move between the strands
   *  stacked in the same column. */
  const move = useCallback(
    (dx: number, dy: number) => {
      if (ordered.length === 0) return;
      const current = ordered.find((n) => n.skill.skill_id === selectedId) ?? ordered[0];
      if (dy !== 0) {
        const sameCol = ordered
          .filter((n) => n.layer === current.layer)
          .sort((a, b) => a.row - b.row);
        const i = sameCol.indexOf(current);
        const next = sameCol[i + dy];
        if (next) setSelectedId(next.skill.skill_id);
        return;
      }
      const i = ordered.indexOf(current);
      const next = ordered[Math.min(ordered.length - 1, Math.max(0, i + dx))];
      if (next) setSelectedId(next.skill.skill_id);
    },
    [ordered, selectedId],
  );

  const nudge = (direction: -1 | 1) => {
    boardRef.current?.scrollBy({ left: direction * 420, behavior: "smooth" });
  };

  const selected = ordered.find((n) => n.skill.skill_id === selectedId) ?? null;

  return (
    <div>
      <Card className="p-6">
        <StandardPicker
          grade={grade}
          standard={standard}
          onGradeChange={(g) => {
            setGrade(g);
            setStandard("");
            setSelectedLesson(undefined);
          }}
          onStandardChange={(code, lessonLabel) => {
            setStandard(code);
            setSelectedLesson(lessonLabel);
            scrollPending.current = true;
          }}
          lessonNav={lessonNav}
          checkpointNav={checkpointNav}
          isEnabled={(code) => code in AVAILABLE_STANDARDS}
        />
      </Card>

      {data && graph && (
        <div key={standard} ref={stemRef} className="pnp-reveal mt-8 scroll-mt-24">
          {/* Standard header */}
          <Card accent="var(--pnp-accent)" className="mb-6 p-6">
            <div className="flex flex-wrap items-center gap-3">
              <Tag variant="code">{data.standard_code}</Tag>
              <h2 className="font-heading text-xl font-extrabold text-pnp-navy">
                Skill progression
              </h2>
            </div>
            <p className="mt-2 text-sm font-medium text-pnp-gray-700">
              {data.standard_text}
            </p>
            {isV2(data) && data.progression && (
              <p className="mt-3 border-t border-pnp-gray-100 pt-3 text-sm leading-relaxed text-pnp-gray-600">
                {data.progression.narrative}
              </p>
            )}
            {lessons.length > 0 && (
              <div className="mt-4 border-t border-pnp-gray-100 pt-3">
                <span className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
                  Lessons for this standard
                </span>
                <div className="mt-2 flex flex-wrap gap-2">
                  {lessons.map((l) => {
                    const active = l.label === selectedLesson;
                    return (
                      <span
                        key={l.label}
                        title={`Module ${l.moduleNumber}: ${l.moduleTitle}`}
                        className={`inline-flex items-center rounded-md border-2 px-2.5 py-1 text-xs font-semibold ${
                          active
                            ? "border-pnp-accent bg-pnp-accent text-white pnp-lesson-flash"
                            : "border-pnp-gray-200 bg-white text-pnp-gray-700"
                        }`}
                      >
                        {l.label}
                      </span>
                    );
                  })}
                </div>
              </div>
            )}
          </Card>

          {/* The board */}
          <div className="mb-6 rounded-xl border-2 border-pnp-navy bg-white p-4 shadow-[4px_4px_0_var(--pnp-navy)] sm:p-5">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-1 rounded-lg border-2 border-pnp-navy p-0.5">
                {VIEWS.map((v) => (
                  <button
                    key={v.id}
                    type="button"
                    onClick={() => setView(v.id)}
                    aria-pressed={view === v.id}
                    title={v.hint}
                    className={`rounded px-3 py-1 text-xs font-bold transition-colors ${
                      view === v.id
                        ? "bg-pnp-navy text-white"
                        : "text-pnp-gray-600 hover:text-pnp-navy"
                    }`}
                  >
                    {v.label}
                  </button>
                ))}
              </div>

              <p className="text-xs font-semibold text-pnp-gray-500">
                {view === "map"
                  ? "Lines follow the pass route. Where two lines meet, both skills feed the next one."
                  : "Read left to right."}{" "}
                Click a skill to open it below, or use the arrow keys.
              </p>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => nudge(-1)}
                  aria-label="Scroll left"
                  className="flex h-8 w-8 items-center justify-center rounded-md border-2 border-pnp-navy bg-white text-pnp-navy shadow-[2px_2px_0_var(--pnp-navy)] transition-transform active:translate-x-0.5 active:translate-y-0.5 active:shadow-none"
                >
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <path d="M15 6l-6 6 6 6" />
                  </svg>
                </button>
                <button
                  type="button"
                  onClick={() => nudge(1)}
                  aria-label="Scroll right"
                  className="flex h-8 w-8 items-center justify-center rounded-md border-2 border-pnp-navy bg-white text-pnp-navy shadow-[2px_2px_0_var(--pnp-navy)] transition-transform active:translate-x-0.5 active:translate-y-0.5 active:shadow-none"
                >
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <path d="M9 6l6 6-6 6" />
                  </svg>
                </button>
              </div>
            </div>

            <div
              role="group"
              aria-label={`${data.standard_code} skill progression`}
              tabIndex={0}
              onKeyDown={(e) => {
                const map: Record<string, [number, number]> = {
                  ArrowRight: [1, 0],
                  ArrowLeft: [-1, 0],
                  ArrowDown: [0, 1],
                  ArrowUp: [0, -1],
                };
                const delta = map[e.key];
                if (!delta) return;
                e.preventDefault();
                move(delta[0], delta[1]);
              }}
              className="focus-visible:outline-none"
            >
              {view === "map" ? (
                <SkillMap
                  graph={graph}
                  selectedId={selectedId}
                  onSelect={setSelectedId}
                  highlightedSkillIds={highlightedSkillIds}
                  lessonActive={lessonActive}
                  boardRef={boardRef}
                  cardRefs={cardRefs}
                />
              ) : (
                <div ref={boardRef} className="overflow-x-auto pb-2">
                  <div className="flex min-w-max items-stretch">
                    {phases.map((phase, pi) => (
                      <div key={phase.column} className="flex items-stretch">
                        {pi > 0 && <PhaseJoin />}
                        <div className="flex flex-col">
                          <span
                            aria-hidden="true"
                            className="h-1.5 rounded-full"
                            style={{ backgroundColor: phase.accent }}
                          />
                          <div
                            className="mb-2 mt-1.5 flex items-baseline gap-2 px-0.5"
                            title={phase.description}
                          >
                            <span className="font-heading text-xs font-extrabold uppercase tracking-wide text-pnp-navy">
                              {phase.label}
                            </span>
                            <span className="text-[11px] text-pnp-gray-500">
                              {phase.count}
                            </span>
                          </div>

                          <div className="flex items-stretch">
                            {phase.clusters.map((cluster, ci) => (
                              <div
                                key={cluster.band ?? "all"}
                                className="flex items-stretch"
                              >
                                {ci > 0 && <Segment wide />}
                                <div className="flex flex-col">
                                  {cluster.band ? (
                                    <span className="mb-1 px-0.5 text-[10px] font-bold uppercase tracking-wide text-pnp-gray-500">
                                      {BAND_SHORT[cluster.band]}
                                    </span>
                                  ) : (
                                    <span
                                      aria-hidden="true"
                                      className="mb-1 block h-[15px]"
                                    />
                                  )}
                                  <div className="flex items-stretch">
                                    {cluster.nodes.map((node, ni) => (
                                      <div
                                        key={node.skill.skill_id}
                                        className="flex items-stretch"
                                      >
                                        {ni > 0 && <Segment />}
                                        <SkillNodeCard
                                          node={node}
                                          accent={phase.accent}
                                          selected={node.skill.skill_id === selectedId}
                                          highlighted={highlightedSkillIds.has(
                                            node.skill.skill_id,
                                          )}
                                          dimmed={
                                            lessonActive &&
                                            !highlightedSkillIds.has(node.skill.skill_id)
                                          }
                                          onSelect={() =>
                                            setSelectedId(node.skill.skill_id)
                                          }
                                          cardRef={(el) => {
                                            if (el)
                                              cardRefs.current.set(
                                                node.skill.skill_id,
                                                el,
                                              );
                                            else
                                              cardRefs.current.delete(
                                                node.skill.skill_id,
                                              );
                                          }}
                                        />
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {view === "map" && graph.isolated.length > 0 && (
              <p className="mt-3 border-t border-pnp-gray-100 pt-3 text-xs text-pnp-gray-500">
                {graph.isolated.length} skill
                {graph.isolated.length === 1 ? " has" : "s have"} no pass route
                authored, so nothing wires to{" "}
                {graph.isolated.length === 1 ? "it" : "them"} yet:{" "}
                {graph.isolated.map(shortSkillTag).join(", ")}.
              </p>
            )}
          </div>

          {/* The selected skill, in full */}
          {selected && (
            <SkillDetailPanel
              key={selected.skill.skill_id}
              node={selected}
              data={data}
              graph={graph}
              onGenerate={() => setPacketFor(selected.skill)}
              onJump={setSelectedId}
            />
          )}

          {/* Assessment actions */}
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <Button tier="secondary" onClick={() => setDiagnosticOpen(true)}>
              Generate diagnostic
            </Button>
            <Button tier="secondary" onClick={() => setProgressOpen(true)}>
              Progress monitoring
            </Button>
            <p className="text-sm text-pnp-gray-500">
              Diagnose gaps across every skill, or re-assess specific skills after
              intervention.
            </p>
          </div>
        </div>
      )}

      {packetFor && data && (
        <SkillPacketModal
          skillName={packetFor.name}
          skillId={packetFor.skill_id}
          standardCode={data.standard_code}
          hasArtifact={!!packetFor.printable_artifact}
          artifactTitle={packetFor.printable_artifact?.title}
          onClose={() => setPacketFor(null)}
        />
      )}

      {diagnosticOpen && data && (
        <DiagnosticModal
          standardCode={data.standard_code}
          mode="diagnostic"
          skills={data.skills.map((s) => ({
            skill_id: s.skill_id,
            name: s.name,
            column: s.column,
          }))}
          onClose={() => setDiagnosticOpen(false)}
        />
      )}

      {progressOpen && data && (
        <DiagnosticModal
          standardCode={data.standard_code}
          mode="progress"
          skills={data.skills.map((s) => ({
            skill_id: s.skill_id,
            name: s.name,
            column: s.column,
          }))}
          onClose={() => setProgressOpen(false)}
        />
      )}
    </div>
  );
}
