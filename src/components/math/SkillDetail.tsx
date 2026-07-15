"use client";

import { useState } from "react";
import { useSearchParams } from "next/navigation";
import type { ContentEnvelope } from "@/lib/types";
import {
  ACTIVITY_TYPE_LABELS,
  COLUMN_META,
  DIFFICULTY_META,
  GROUPING_LABELS,
  isPacketReady,
  type Activity,
  type PracticeProblem,
  type Skill,
} from "@/lib/skills";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Tag from "@/components/ui/Tag";
import StrategyCard from "@/components/library/StrategyCard";
import SkillPacketModal from "./SkillPacketModal";
import type { WarmupLink } from "@/lib/warmups";
import { InlineDiagram, type RenderData } from "@/components/intervention/InlineMath";

/**
 * SkillDetail — the drill-in view for one v2 skill: everything a teacher
 * needs to run an intervention session on it, organized as four tabs:
 * Practice · Activities · Strategies · Teacher Moves.
 */

const TABS = ["Practice", "Activities", "Strategies", "Teacher Moves"] as const;
type TabName = (typeof TABS)[number];

interface Props {
  skill: Skill;
  standardCode: string;
  standardText: string;
  rationale?: string;
  /** Strategy envelopes resolved server-side from skill.strategy_links. */
  strategies: Array<{ envelope: ContentEnvelope; why: string }>;
  /** Library warm-ups (Number Talks / WODB) matched to this standard,
   *  resolved server-side from the decks' std tags. */
  warmups?: WarmupLink[];
}

export default function SkillDetail({
  skill,
  standardCode,
  standardText,
  rationale,
  strategies,
  warmups,
}: Props) {
  // ?tab=Activities deep-links a tab (the progression view's per-skill
  // "Activities" chip lands here) — invalid values fall back to Practice.
  const searchParams = useSearchParams();
  const requestedTab = searchParams?.get("tab");
  const [tab, setTab] = useState<TabName>(
    TABS.includes(requestedTab as TabName) ? (requestedTab as TabName) : "Practice"
  );
  const [showModal, setShowModal] = useState(false);
  const ready = isPacketReady(skill);
  const meta = COLUMN_META[skill.column];

  return (
    <div>
      {/* Context + actions */}
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone={meta.badgeTone}>{meta.label}</Badge>
        <Tag variant="code" title={standardText}>{standardCode}</Tag>
        <div className="ml-auto flex flex-wrap items-center gap-2">
          {ready && (
            <>
              <Button tier="primary" onClick={() => setShowModal(true)}>
                Generate packet
              </Button>
              <Button
                tier="secondary"
                href={`/math/intervention/${skill.skill_id}/project`}
                target="_blank"
                rel="noopener noreferrer"
                title="Project problems and digital activity for whole-class display"
              >
                Project
              </Button>
            </>
          )}
        </div>
      </div>

      {rationale && (
        <p className="mt-4 max-w-3xl text-sm leading-relaxed text-pnp-gray-600">
          <span className="font-semibold text-pnp-navy">Why this step: </span>
          {rationale}
        </p>
      )}

      {/* Library warm-ups — five-minute conceptual openers matched to this
          standard. Deep-links into the Number Talks / WODB tools. */}
      {warmups && warmups.length > 0 && (
        <div className="mt-5 max-w-3xl rounded-lg border border-pnp-gray-200 bg-white px-4 py-3">
          <p className="text-xs font-bold uppercase tracking-wide text-pnp-gray-500">
            Warm-ups from the library
          </p>
          <ul className="mt-2 flex flex-wrap gap-2">
            {warmups.map((w) => (
              <li key={`${w.kind}-${w.id}`}>
                <a
                  href={w.href}
                  className="inline-flex items-center gap-1.5 rounded-md border border-pnp-gray-200 bg-pnp-gray-50 px-2.5 py-1.5 text-sm font-semibold text-pnp-navy transition-colors hover:border-pnp-accent hover:bg-pnp-accent-soft focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent"
                >
                  <span className="text-[10px] font-bold uppercase tracking-wide text-pnp-accent">
                    {w.kind === "talk" ? "Number talk" : "WODB"}
                  </span>
                  {w.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Tabs */}
      <div
        role="tablist"
        aria-label="Skill resources"
        className="mt-6 inline-flex max-w-full flex-wrap items-center gap-1 rounded-lg border border-pnp-gray-200 bg-white p-1"
      >
        {TABS.map((t) => {
          const active = tab === t;
          return (
            <button
              key={t}
              role="tab"
              aria-selected={active}
              onClick={() => setTab(t)}
              className={[
                "inline-flex h-9 select-none items-center rounded-md px-3 text-sm font-semibold",
                "transition-[background-color,color,transform] duration-150 ease-out",
                "active:scale-[0.98]",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2",
                active ? "bg-pnp-accent text-white" : "text-pnp-gray-700 hover:bg-pnp-gray-100",
              ].join(" ")}
            >
              {t}
            </button>
          );
        })}
      </div>

      <div className="mt-6" role="tabpanel">
        {tab === "Practice" && <PracticeTab problems={skill.practice_problems ?? []} />}
        {tab === "Activities" && (
          <ActivitiesTab
            activities={skill.activities ?? []}
            skillId={skill.skill_id}
            standardCode={standardCode}
          />
        )}
        {tab === "Strategies" && <StrategiesTab strategies={strategies} />}
        {tab === "Teacher Moves" && <TeacherMovesTab skill={skill} />}
      </div>

      {showModal && (
        <SkillPacketModal
          skillName={skill.name}
          skillId={skill.skill_id}
          standardCode={standardCode}
          hasArtifact={!!skill.printable_artifact}
          artifactTitle={skill.printable_artifact?.title}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
}

// ── Practice ────────────────────────────────────────────────────────────

const DIFFICULTY_ORDER: PracticeProblem["difficulty"][] = ["warm_up", "core", "stretch"];

function PracticeTab({ problems }: { problems: PracticeProblem[] }) {
  if (problems.length === 0) return <EmptyState label="No practice problems authored yet." />;

  return (
    <div className="space-y-8">
      {DIFFICULTY_ORDER.map((level) => {
        const group = problems.filter((p) => p.difficulty === level);
        if (group.length === 0) return null;
        const d = DIFFICULTY_META[level];
        return (
          <section key={level}>
            <div className="mb-3 flex items-center gap-2">
              <h3 className="font-heading text-lg font-extrabold text-pnp-navy">{d.label}</h3>
              <Badge tone={d.tone}>{group.length}</Badge>
            </div>
            <ol className="space-y-3">
              {group.map((p, i) => (
                <li key={i} className="rounded-lg border border-pnp-gray-200 bg-white p-4">
                  {p.type === "error_analysis" && (
                    <Badge tone="red" className="mb-2">Find &amp; fix the mistake</Badge>
                  )}
                  {p.type === "number_line" && (
                    <Badge tone="blue" className="mb-2">Number line</Badge>
                  )}
                  <p className="text-sm leading-relaxed text-pnp-navy">{p.stem}</p>
                  {p.render_data && (
                    <div className="mt-2 text-pnp-navy [&_svg]:h-auto [&_svg]:max-w-full">
                      <InlineDiagram data={p.render_data as RenderData} />
                    </div>
                  )}
                  {p.shown_work && p.shown_work.length > 0 && (
                    <div className="mt-2 rounded border border-pnp-red/30 bg-pnp-red/5 px-3 py-2">
                      {p.shown_work.map((line, j) => (
                        <p key={j} className="font-mono text-sm font-semibold text-pnp-navy">{line}</p>
                      ))}
                    </div>
                  )}
                  {p.notes && (
                    <p className="mt-2 text-xs italic text-pnp-gray-500">{p.notes}</p>
                  )}
                  <details className="mt-2 group/answer">
                    <summary className="inline-flex cursor-pointer select-none items-center rounded text-xs font-semibold text-pnp-accent hover:text-pnp-accent-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2">
                      Show answer
                    </summary>
                    <p className="mt-2 rounded bg-pnp-accent-soft px-3 py-2 text-sm font-semibold text-pnp-navy">
                      {p.answer}
                    </p>
                  </details>
                </li>
              ))}
            </ol>
          </section>
        );
      })}
    </div>
  );
}

// ── Activities ──────────────────────────────────────────────────────────

const ACTIVITY_TONE: Record<Activity["type"], "blue" | "red" | "teal" | "orange" | "yellow"> = {
  card_sort: "blue",
  error_analysis: "red",
  matching: "teal",
  hands_on: "orange",
  game: "yellow",
};

function ActivitiesTab({
  activities,
  skillId,
  standardCode,
}: {
  activities: Activity[];
  skillId: string;
  standardCode: string;
}) {
  if (activities.length === 0) return <EmptyState label="No activities authored yet." />;

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
      {activities.map((a, i) => (
        <Card key={i} className="p-5">
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone={ACTIVITY_TONE[a.type]}>{ACTIVITY_TYPE_LABELS[a.type]}</Badge>
            <Tag>{a.time_minutes} min</Tag>
            <Tag>{GROUPING_LABELS[a.grouping]}</Tag>
            <div className="ml-auto">
              <PrintMaterialsButton
                skillId={skillId}
                standardCode={standardCode}
                activityIndex={i}
              />
            </div>
          </div>
          <h3 className="mt-3 font-heading text-lg font-bold text-pnp-navy">{a.title}</h3>

          {a.materials.length > 0 && (
            <p className="mt-2 text-xs text-pnp-gray-500">
              <span className="font-semibold text-pnp-gray-700">Materials: </span>
              {a.materials.join(" · ")}
            </p>
          )}

          <ol className="mt-3 space-y-1.5">
            {a.instructions.split("\n").map((line, j) => (
              <li key={j} className="text-sm leading-relaxed text-pnp-gray-700">
                {line}
              </li>
            ))}
          </ol>

          {a.content && <ActivityContentBlock activity={a} />}
        </Card>
      ))}
    </div>
  );
}

/**
 * One-click hand-outs: run sheet + cut-apart decks / student slips / any
 * referenced blackline masters, generated by the packet engine's
 * activity_materials mode and opened in a new tab for printing.
 */
function PrintMaterialsButton({
  skillId,
  standardCode,
  activityIndex,
}: {
  skillId: string;
  standardCode: string;
  activityIndex: number;
}) {
  const [loading, setLoading] = useState(false);

  const print = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/generate-skill-packet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          standard: standardCode,
          skill_id: skillId,
          mode: "activity_materials",
          activity_index: activityIndex,
        }),
      });
      if (!res.ok) return;
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      window.open(url, "_blank", "noopener");
      // Give the new tab time to load the blob before revoking.
      setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch {
      // ignore — the button simply re-enables
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button tier="secondary" size="small" onClick={print} disabled={loading}>
      {loading ? "Building…" : "Print materials"}
    </Button>
  );
}

function ActivityContentBlock({ activity }: { activity: Activity }) {
  const c = activity.content!;

  // Error analysis: the worked problem + where it breaks + why.
  if (c.worked_problem) {
    return (
      <div className="mt-4 space-y-2 border-t border-pnp-gray-100 pt-3 text-sm">
        <p className="rounded bg-pnp-gray-50 px-3 py-2 font-medium text-pnp-navy">{c.worked_problem}</p>
        {c.error_step && (
          <p className="text-pnp-gray-700">
            <span className="font-semibold text-pnp-red">The error: </span>
            {c.error_step}
          </p>
        )}
        {c.why && (
          <p className="text-pnp-gray-700">
            <span className="font-semibold text-pnp-accent">Why it&apos;s wrong: </span>
            {c.why}
          </p>
        )}
      </div>
    );
  }

  // Card sort: render the actual cards grouped by category (projectable).
  if (c.categories && c.cards) {
    return (
      <div className="mt-4 grid grid-cols-1 gap-3 border-t border-pnp-gray-100 pt-3 sm:grid-cols-2">
        {c.categories.map((cat) => (
          <div key={cat} className="rounded-lg bg-pnp-gray-50 p-3">
            <p className="mb-2 text-xs font-bold uppercase tracking-wide text-pnp-gray-500">{cat}</p>
            <div className="flex flex-wrap gap-1.5">
              {c.cards!
                .filter((card) => card.category === cat)
                .map((card) => (
                  <span key={card.text} className="rounded-md border border-pnp-gray-200 bg-white px-2 py-1 text-xs font-medium text-pnp-navy">
                    {card.text}
                  </span>
                ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  // Matching pairs (+ decoys).
  if (c.pairs) {
    return (
      <div className="mt-4 border-t border-pnp-gray-100 pt-3">
        <div className="space-y-1.5">
          {c.pairs.map((p, i) => (
            <div key={i} className="flex items-center gap-2 text-sm">
              <span className="flex-1 rounded bg-pnp-gray-50 px-2 py-1 text-pnp-gray-700">{p.left}</span>
              <span aria-hidden="true" className="text-pnp-gray-400">→</span>
              <span className="rounded bg-pnp-accent-soft px-2 py-1 font-mono font-semibold text-pnp-navy">{p.right}</span>
            </div>
          ))}
        </div>
        {c.decoys && c.decoys.length > 0 && (
          <p className="mt-2 text-xs text-pnp-gray-500">
            <span className="font-semibold">Decoys (match nothing): </span>
            {c.decoys.join(", ")}
          </p>
        )}
      </div>
    );
  }

  // Three-way notation triples.
  if (c.triples) {
    return (
      <div className="mt-4 overflow-x-auto border-t border-pnp-gray-100 pt-3">
        <table className="w-full min-w-[420px] text-sm">
          <thead>
            <tr className="text-left text-xs font-bold uppercase tracking-wide text-pnp-gray-500">
              <th className="pb-2 pr-3">Phrase</th>
              <th className="pb-2 pr-3">Notation</th>
              <th className="pb-2">Expanded</th>
            </tr>
          </thead>
          <tbody>
            {c.triples.map((t, i) => (
              <tr key={i} className="border-t border-pnp-gray-100">
                <td className="py-1.5 pr-3 text-pnp-gray-700">{t.phrase}</td>
                <td className="py-1.5 pr-3 font-mono font-semibold text-pnp-navy">{t.notation}</td>
                <td className="py-1.5 font-mono text-pnp-gray-700">{t.expanded}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  return null;
}

// ── Strategies ──────────────────────────────────────────────────────────

function StrategiesTab({
  strategies,
}: {
  strategies: Array<{ envelope: ContentEnvelope; why: string }>;
}) {
  if (strategies.length === 0) return <EmptyState label="No linked strategies yet." />;

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
      {strategies.map(({ envelope, why }) => (
        <div key={envelope.id} className="flex flex-col gap-2">
          <StrategyCard strategy={envelope} />
          <p className="px-1 text-xs leading-relaxed text-pnp-gray-600">
            <span className="font-semibold text-pnp-navy">Why it fits: </span>
            {why}
          </p>
        </div>
      ))}
    </div>
  );
}

// ── Teacher Moves ───────────────────────────────────────────────────────

function TeacherMovesTab({ skill }: { skill: Skill }) {
  const moves = skill.teacher_moves;
  if (!moves) return <EmptyState label="No teacher moves authored yet." />;

  return (
    <div className="space-y-8">
      <section>
        <h3 className="mb-3 font-heading text-lg font-extrabold text-pnp-navy">
          Questioning prompts
        </h3>
        <ul className="space-y-2">
          {moves.questioning_prompts.map((q, i) => (
            <li key={i} className="rounded-lg border border-pnp-gray-200 bg-white px-4 py-3 text-sm leading-relaxed text-pnp-gray-700">
              &ldquo;{q}&rdquo;
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h3 className="mb-3 font-heading text-lg font-extrabold text-pnp-navy">
          Misconception redirects
        </h3>
        <div className="space-y-4">
          {moves.misconception_redirects.map((r, i) => (
            <div key={i} className="overflow-hidden rounded-lg border border-pnp-gray-200 bg-white">
              <div className="border-l-4 border-pnp-red px-4 py-3">
                <p className="text-xs font-bold uppercase tracking-wide text-pnp-red">If you see</p>
                <p className="mt-1 text-sm leading-relaxed text-pnp-gray-700">{r.if_you_see}</p>
              </div>
              <div className="border-l-4 border-pnp-blue px-4 py-3">
                <p className="text-xs font-bold uppercase tracking-wide text-pnp-blue">Say</p>
                <p className="mt-1 text-sm leading-relaxed text-pnp-gray-700">&ldquo;{r.say}&rdquo;</p>
              </div>
              <div className="border-l-4 border-pnp-green px-4 py-3">
                <p className="text-xs font-bold uppercase tracking-wide text-[#15803d]">Then praise</p>
                <p className="mt-1 text-sm leading-relaxed text-pnp-gray-700">&ldquo;{r.praise}&rdquo;</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h3 className="mb-3 font-heading text-lg font-extrabold text-pnp-navy">
          Quick checks
        </h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {moves.quick_checks.map((qc, i) => (
            <div key={i} className="rounded-lg border border-pnp-gray-200 bg-white p-4">
              <p className="text-sm font-semibold leading-relaxed text-pnp-navy">{qc.prompt}</p>
              <p className="mt-2 text-xs leading-relaxed text-pnp-gray-600">
                <span className="font-semibold text-pnp-gray-700">Look for: </span>
                {qc.look_for}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

// ── Shared ──────────────────────────────────────────────────────────────

function EmptyState({ label }: { label: string }) {
  return (
    <div className="rounded-xl border-2 border-dashed border-pnp-gray-300 bg-white py-14 text-center text-sm text-pnp-gray-500">
      {label}
    </div>
  );
}
