"use client";

import Link from "next/link";
import type { ContentEnvelope, UnitFile, WarmupRef } from "@/lib/types";
import TaskCard from "@/components/tasks/TaskCard";
import BrowseModeToggle from "./BrowseModeToggle";
import Button from "@/components/ui/Button";
import Tag from "@/components/ui/Tag";

/**
 * Unit detail view. Renders the browse-mode toggle (routing back to
 * standards/concepts), a sticky sub-nav of section anchors, then each
 * section as a heading + a grid of `TaskCard`s.
 *
 * The same task can appear in multiple sections within the same unit —
 * we render the duplicate without dedupe because that's the curatorial
 * intent (some tasks teach two related sub-objectives).
 */
interface Props {
  unit: UnitFile;
  /** Pre-resolved task lookup by ID. The server page does the
   *  `getAllTasks()` call once and passes us the map. */
  tasksById: Map<string, ContentEnvelope>;
  /** Pre-resolved thin-slice lookup by ID. Same shape as tasksById. */
  slicesById: Map<string, ContentEnvelope>;
}

export default function UnitDetail({ unit, tasksById, slicesById }: Props) {
  // Rich tasks and thin slices now render in the same card grid (Dave's
  // "combine things" pass). We concat tasks-then-slices into a single
  // `items` array so rich tasks come first within a section, then thin
  // slices follow. Both render as TaskCards; the badge on each card
  // distinguishes "Rich Task" from "Thin Slice".
  const sectionsWithContent = unit.sections
    .map((section) => {
      const tasks = section.taskIds
        .map((id) => tasksById.get(id))
        .filter((t): t is ContentEnvelope => Boolean(t));
      const slices = (section.thinSliceIds ?? [])
        .map((id) => slicesById.get(id))
        .filter((s): s is ContentEnvelope => Boolean(s));
      return {
        section,
        items: [...tasks, ...slices],
        taskCount: tasks.length,
        sliceCount: slices.length,
      };
    })
    .filter(
      (entry) =>
        entry.items.length > 0 || !!entry.section.standard
    );

  return (
    <div className="space-y-8">
      {/* Top row: mode toggle. Always present so the teacher can jump
          back to standards/concepts without scrolling. */}
      <div className="flex justify-start">
        <BrowseModeToggle current="unit" />
      </div>

      {/* Section jump-nav. Sticky so it stays available while scrolling. */}
      {sectionsWithContent.length > 1 && (
        <nav
          aria-label="Section navigation"
          className="sticky top-0 z-10 -mx-4 flex gap-2 overflow-x-auto border-y border-pnp-gray-200 bg-pnp-gray-50/95 px-4 py-2 backdrop-blur"
        >
          {sectionsWithContent.map(({ section }) => (
            <a
              key={section.id}
              href={`#${section.id}`}
              className="shrink-0 rounded-md bg-white px-3 py-1.5 text-xs font-semibold text-pnp-gray-700 ring-1 ring-pnp-gray-200 transition-colors hover:bg-pnp-accent-soft hover:text-pnp-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2"
            >
              {section.label}
            </a>
          ))}
        </nav>
      )}

      {sectionsWithContent.length === 0 ? (
        <div className="rounded-xl border-2 border-dashed border-pnp-gray-300 bg-white py-14 text-center">
          <p className="text-base font-semibold text-pnp-gray-700">
            We&rsquo;re still mapping activities to this unit
          </p>
          <p className="mt-1 text-sm text-pnp-gray-600">
            Browse all Grade {unit.grade} activities or jump to another unit.
          </p>
          <div className="mt-4 flex justify-center">
            <Button href="/math/units" tier="secondary">
              All units
            </Button>
          </div>
        </div>
      ) : (
        sectionsWithContent.map(({ section, items, taskCount, sliceCount }) => {
          const summary = [
            taskCount > 0 && `${taskCount} rich task${taskCount === 1 ? "" : "s"}`,
            sliceCount > 0 && `${sliceCount} thin slice${sliceCount === 1 ? "" : "s"}`,
          ]
            .filter(Boolean)
            .join(" · ");
          return (
            <section
              key={section.id}
              id={section.id}
              className="scroll-mt-20"
            >
              <div className="mb-3 flex flex-wrap items-baseline justify-between gap-3 border-b border-pnp-gray-200 pb-2">
                <h2 className="font-heading text-xl font-bold text-pnp-navy md:text-2xl">
                  {section.label}
                </h2>
                <div className="flex items-center gap-2 text-xs">
                  {section.standard && (
                    <Tag variant="code">{section.standard}</Tag>
                  )}
                  {summary && (
                    <span className="font-mono text-pnp-gray-500">
                      {summary}
                    </span>
                  )}
                </div>
              </div>
              {section.description && (
                <p className="mb-4 text-sm text-pnp-gray-600">
                  {section.description}
                </p>
              )}

              {/* Warm-up strip — the routine(s) assigned to THIS lesson,
                  above the rich tasks and thin slices. */}
              <WarmupStrip warmups={section.warmupRefs ?? []} />

              {items.length > 0 && (
                <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
                  {items.map((item, i) => (
                    // Same TaskCard for both formats — the badge on the
                    // card (Rich Task / Thin Slice) does the disambiguation.
                    // `i` handles the legal case of the same ID appearing
                    // twice in one section.
                    <TaskCard key={`${item.id}-${i}`} task={item} />
                  ))}
                </div>
              )}

              {/* Skill action row — CFU button (always) plus Fluency
                  Practice button (only on sections whose JSON declares a
                  matching fluencyTopic). */}
              {section.standard && (
                <SectionActionRow
                  standard={section.standard}
                  fluencyTopic={section.fluencyTopic}
                />
              )}
            </section>
          );
        })
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// SectionActionRow — the standard-level Action Bar that anchors under
// the task grid for a single section.
//
// Layout: a full-width strip with a 1px top border + faint accent tint,
// a small left label ("Build for 7.NS.2:"), and the action buttons
// aligned right. The strip gives the actions presence without
// oversizing the buttons themselves; size + radius stay at the standard
// 40px / rounded-md from the design system.
//
// Hierarchy (per Dave's design direction):
//   PRIMARY   — Generate CFU (the main "what should I build for this
//               standard?" action). Solid accent fill.
//   SECONDARY — Fluency Practice. Transparent + neutral border.
//
// Note: this primary is section-scoped, not view-scoped. Each section
// is its own mini-view with its own action bar; the unit page as a
// whole will render several primaries, one per section.
//
// Not every section has a clean fluency match (e.g. "Apply rational
// numbers" is multi-step word-problem reasoning). In those cases only
// the CFU button renders inside the strip.
// ─────────────────────────────────────────────────────────────────────

function SectionActionRow({
  standard,
  fluencyTopic,
}: {
  standard: string;
  fluencyTopic?: string;
}) {
  return (
    <div className="mt-6 flex flex-wrap items-center gap-2.5 rounded-md border-2 border-pnp-navy bg-pnp-accent-soft/50 px-3 py-2.5 shadow-[2px_2px_0_var(--pnp-navy)]">
      <span className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-widest text-pnp-navy">
        <TargetIcon />
        Practice &amp; Closure
      </span>
      <Button
        tier="primary"
        size="small"
        href={`/math/generator?standard=${encodeURIComponent(standard)}&mode=exit_ticket`}
        icon={<ClipboardCheckIcon />}
      >
        Generate CFU
      </Button>
      {fluencyTopic && (
        <Button
          tier="secondary"
          size="small"
          href={`/math/fluency?topic=${encodeURIComponent(fluencyTopic)}`}
          icon={<DumbbellIcon />}
          title="Open the Fluency Practice tool with this skill pre-selected."
        >
          Fluency Practice
        </Button>
      )}
      <span className="ml-auto text-[11px] font-semibold uppercase tracking-wide text-pnp-gray-500">
        for <span className="font-mono normal-case tracking-normal text-pnp-gray-700">{standard}</span>
      </span>
    </div>
  );
}

// Small "target" mark for the Practice & Closure label — signals the
// aim/assess phase, mirroring the warm-up's spark label.
function TargetIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="9" />
      <circle cx="12" cy="12" r="4.5" />
      <circle cx="12" cy="12" r="0.5" fill="currentColor" />
    </svg>
  );
}

// WarmupStrip — the classroom-routine warm-ups (WODB / Number Talks) that
// match this lesson's standard, shown as a compact band ABOVE the rich
// tasks and thin slices. Each chip deep-links to the routine with that
// exact set/talk opened for projection.
function WarmupStrip({ warmups }: { warmups: WarmupRef[] }) {
  if (warmups.length === 0) return null;
  return (
    <div className="mb-4 rounded-md border-2 border-pnp-navy bg-pnp-yellow/25 px-3 py-2.5 shadow-[2px_2px_0_var(--pnp-navy)]">
      <div className="flex flex-wrap items-center gap-2">
        <span className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-widest text-pnp-navy">
          <SparkIcon />
          Warm-up
        </span>
        {warmups.map((w) => {
          const href =
            w.kind === "wodb"
              ? `/math/wodb?grade=${w.grade}&set=${encodeURIComponent(w.id)}`
              : `/math/number-talks?grade=${w.grade}&talk=${encodeURIComponent(w.id)}`;
          const label = w.kind === "wodb" ? "Which One Doesn't Belong" : "Number Talk";
          return (
            <Link
              key={`${w.kind}-${w.id}`}
              href={href}
              className="group inline-flex items-center gap-2 rounded-md border-2 border-pnp-navy bg-white px-2.5 py-1 text-xs font-semibold text-pnp-navy shadow-[2px_2px_0_var(--pnp-navy)] transition-transform hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2"
              title={`${label}: ${w.title}`}
            >
              <span
                className="inline-block h-2 w-2 rounded-full"
                style={{ backgroundColor: w.kind === "wodb" ? "#0d9488" : "#ea580c" }}
                aria-hidden="true"
              />
              <span className="text-[10px] uppercase tracking-wide text-pnp-gray-500">
                {w.kind === "wodb" ? "WODB" : "Talk"}
              </span>
              <span className="max-w-[16rem] truncate">{w.title}</span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

function SparkIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1" />
    </svg>
  );
}

function ClipboardCheckIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
      <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
      <path d="M9 14l2 2 4-4" />
    </svg>
  );
}

// Lucide-style "dumbbell" — a familiar visual shorthand for "drill /
// strength training." Keeps icon set consistent with the other section
// buttons (16px, stroke 2, currentColor).
function DumbbellIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M6 4v16" />
      <path d="M18 4v16" />
      <path d="M3 8v8" />
      <path d="M21 8v8" />
      <path d="M6 12h12" />
    </svg>
  );
}
