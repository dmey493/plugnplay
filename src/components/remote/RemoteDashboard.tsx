"use client";

import { useState } from "react";
import type {
  GroupsClassSummary,
  GroupsMirror,
  ProjectionState,
  RemoteCommand,
  RemoteTaskBundle,
} from "@/lib/core/types";
import {
  PROJECTION_THEMES,
  THEME_ORDER,
  type ThemeId,
} from "@/lib/classroom/projection-themes";
import MarkdownText from "@/components/tasks/MarkdownText";

/**
 * Paired-state phone dashboard. Reads the latest projection state from
 * `state` (polled by the parent) and emits commands via `onCommand`.
 *
 * Layout: a single vertically-scrolling column so a teacher can thumb
 * through the whole facilitation context without zooming. Slide
 * controls live near the top so they're reachable without scrolling.
 */
interface Props {
  bundle: RemoteTaskBundle;
  state: ProjectionState;
  onCommand: (command: RemoteCommand) => void;
  onDisconnect: () => void;
}

export default function RemoteDashboard({
  bundle,
  state,
  onCommand,
  onDisconnect,
}: Props) {
  const currentQuestionIdx = Math.max(
    0,
    Math.min(bundle.questions.length - 1, state.revealedCount - 1)
  );
  const currentQuestionText =
    bundle.questions[currentQuestionIdx]?.replace(/^\s*\d+\.\s*/, "") ?? "";

  return (
    <div className="flex min-h-screen flex-col bg-pnp-gray-50 text-pnp-gray-900">
      {/* Header */}
      <header className="sticky top-0 z-10 flex items-center justify-between border-b border-pnp-gray-200 bg-white px-4 py-3">
        <div className="min-w-0 flex-1">
          <div className="truncate font-heading text-base font-bold text-pnp-navy">
            {bundle.title}
          </div>
          <div className="font-mono text-xs text-pnp-gray-500">
            Question {state.revealedCount} / {state.totalQuestions}
          </div>
        </div>
        <button
          type="button"
          onClick={onDisconnect}
          className="ml-3 rounded-md px-3 py-1.5 text-sm font-semibold text-pnp-gray-500 hover:bg-pnp-gray-100 hover:text-pnp-gray-800"
          title="Disconnect"
          aria-label="Disconnect"
        >
          ✕
        </button>
      </header>

      <main className="flex-1 px-4 py-4">
        {/* Current question card */}
        <section className="rounded-2xl bg-white p-5 shadow-sm">
          <div className="text-xs font-bold uppercase tracking-wider text-pnp-gray-500">
            Showing
          </div>
          <div className="mt-2 text-lg font-medium leading-snug text-pnp-navy">
            <span className="mr-1.5 font-mono font-bold text-pnp-blue">
              {state.revealedCount}.
            </span>
            <MarkdownText text={currentQuestionText} />
          </div>
        </section>

        {/* Slide controls — biggest buttons on the page. */}
        <section className="mt-4 grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => onCommand({ type: "retreat" })}
            disabled={state.revealedCount <= 1}
            className={`rounded-2xl py-5 text-lg font-bold shadow-sm transition-colors ${
              state.revealedCount <= 1
                ? "cursor-not-allowed bg-pnp-gray-200 text-pnp-gray-500"
                : "bg-white text-pnp-navy hover:bg-pnp-gray-100"
            }`}
          >
            ← Back
          </button>
          <button
            type="button"
            onClick={() => onCommand({ type: "advance" })}
            disabled={state.revealedCount >= state.totalQuestions}
            className={`rounded-2xl py-5 text-lg font-bold shadow-sm transition-colors ${
              state.revealedCount >= state.totalQuestions
                ? "cursor-not-allowed bg-pnp-gray-200 text-pnp-gray-500"
                : "bg-pnp-blue text-white hover:bg-pnp-navy"
            }`}
          >
            Next →
          </button>
        </section>

        {/* Timer card */}
        <TimerCard state={state.timer} onCommand={onCommand} />

        {/* Random groups — view the current assignment + form from a class */}
        <GroupsCard
          groups={state.groups ?? null}
          classes={state.classes ?? []}
          onCommand={onCommand}
        />

        {/* Theme picker */}
        <ThemeCard activeId={state.themeId} onCommand={onCommand} />

        {/* Reference cards */}
        <div className="mt-4 space-y-2">
          {bundle.discussionQuestions && (
            <ReferenceCard
              label="Discussion Questions"
              markdown={bundle.discussionQuestions}
            />
          )}
          {bundle.anticipatedApproaches && (
            <ReferenceCard
              label="Anticipated Approaches"
              markdown={bundle.anticipatedApproaches}
            />
          )}
          {bundle.commonMisconceptions && (
            <ReferenceCard
              label="Common Misconceptions"
              markdown={bundle.commonMisconceptions}
            />
          )}
          {bundle.sampleSolutions && (
            <ReferenceCard
              label="Sample Solutions"
              markdown={bundle.sampleSolutions}
            />
          )}
          {bundle.extensions && (
            <ReferenceCard label="Extensions" markdown={bundle.extensions} />
          )}
        </div>
      </main>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// Groups card — mirror the projection's assignment + drive it
// ─────────────────────────────────────────────────────────────────────

// Matches the group colours on the projection (GroupsResult) so a board
// reads the same on the phone and the big screen.
const GROUP_COLORS = [
  "#0d9488", "#f97316", "#0ea5e9", "#16a34a", "#dc2626",
  "#475569", "#facc15", "#3f42d9", "#ec4899",
];
const groupColor = (i: number) => GROUP_COLORS[i % GROUP_COLORS.length];

function GroupsCard({
  groups,
  classes,
  onCommand,
}: {
  groups: GroupsMirror | null;
  classes: GroupsClassSummary[];
  onCommand: (c: RemoteCommand) => void;
}) {
  return (
    <section className="mt-4 rounded-2xl bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="text-xs font-bold uppercase tracking-wider text-pnp-gray-500">
          Groups
        </div>
        {groups && (
          <button
            type="button"
            onClick={() => onCommand({ type: "groups-clear" })}
            className="text-xs font-semibold text-pnp-gray-400 hover:text-pnp-gray-700"
          >
            Clear
          </button>
        )}
      </div>

      {groups ? (
        <>
          <div className="mt-1 text-xs font-semibold text-pnp-gray-500">
            {groups.label}
          </div>
          <div className="mt-3 grid grid-cols-2 gap-2">
            {groups.groups.map((g, i) => (
              <div
                key={i}
                className="rounded-xl border border-pnp-gray-200 p-2.5"
              >
                <div
                  className="text-[11px] font-bold uppercase tracking-wide"
                  style={{ color: groupColor(i) }}
                >
                  Group {i + 1}
                </div>
                <ul className="mt-1 space-y-0.5">
                  {g.map((s) => (
                    <li
                      key={s.id}
                      className="text-sm font-semibold leading-snug text-pnp-navy"
                    >
                      {s.name}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <button
            type="button"
            onClick={() => onCommand({ type: "groups-reshuffle" })}
            className="mt-3 w-full rounded-md bg-pnp-blue py-2.5 text-sm font-bold text-white hover:bg-pnp-navy"
          >
            Reshuffle
          </button>
        </>
      ) : (
        <p className="mt-2 text-sm text-pnp-gray-500">
          No groups formed yet. Pick a class below to form them on the
          projection.
        </p>
      )}

      {classes.length > 0 ? (
        <div className="mt-4">
          <div className="text-xs font-bold uppercase tracking-wider text-pnp-gray-400">
            {groups ? "Form from another class" : "Form from a class"}
          </div>
          <div className="mt-2 space-y-1.5">
            {classes.map((c) => {
              const groupable = c.count >= 2;
              return (
                <button
                  key={c.id}
                  type="button"
                  disabled={!groupable}
                  onClick={() =>
                    onCommand({ type: "groups-form-class", classId: c.id })
                  }
                  className={`flex w-full items-center justify-between gap-3 rounded-lg border px-4 py-3 text-left transition-colors ${
                    groupable
                      ? "border-pnp-gray-200 hover:border-pnp-accent hover:bg-pnp-accent-soft/40"
                      : "cursor-not-allowed border-pnp-gray-100 opacity-50"
                  }`}
                >
                  <span className="min-w-0 flex-1 truncate font-heading font-bold text-pnp-navy">
                    {c.name}
                  </span>
                  <span className="shrink-0 text-xs font-semibold text-pnp-gray-500">
                    {c.count}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      ) : (
        !groups && (
          <p className="mt-3 text-xs text-pnp-gray-400">
            No saved classes on the projection's device. Build one on the
            Classes page first.
          </p>
        )
      )}
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────
// Timer card
// ─────────────────────────────────────────────────────────────────────

function TimerCard({
  state,
  onCommand,
}: {
  state: ProjectionState["timer"];
  onCommand: (c: RemoteCommand) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState("");

  const display = formatMmSs(state.remainingSec);
  const startDraftFromCurrent = () => {
    setDraft(formatMmSs(state.durationSec));
    setEditing(true);
  };
  const commitDraft = () => {
    const seconds = parseMmSs(draft);
    if (seconds !== null) onCommand({ type: "timer-set-duration", seconds });
    setEditing(false);
  };

  return (
    <section className="mt-4 rounded-2xl bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="text-xs font-bold uppercase tracking-wider text-pnp-gray-500">
          Timer
        </div>
        <button
          type="button"
          onClick={() => onCommand({ type: "set-timer-visible", visible: !state.visible })}
          className={`rounded-md px-2.5 py-1 text-xs font-semibold ${
            state.visible
              ? "bg-pnp-yellow text-pnp-navy"
              : "bg-pnp-gray-100 text-pnp-gray-700"
          }`}
        >
          {state.visible ? "On projection" : "Hidden"}
        </button>
      </div>

      <div className="mt-3 flex items-center justify-between gap-3">
        {editing ? (
          <input
            type="text"
            inputMode="numeric"
            autoFocus
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onBlur={commitDraft}
            onKeyDown={(e) => {
              if (e.key === "Enter") (e.target as HTMLInputElement).blur();
              if (e.key === "Escape") setEditing(false);
            }}
            placeholder="MM:SS"
            className="flex-1 rounded-md border border-pnp-gray-300 px-3 py-2 text-center font-mono text-3xl font-bold tabular-nums focus:border-pnp-blue focus:outline-none"
          />
        ) : (
          <button
            type="button"
            onClick={startDraftFromCurrent}
            className="flex-1 text-center font-mono text-4xl font-bold tabular-nums text-pnp-navy hover:opacity-70"
            title="Tap to set duration"
          >
            {display}
          </button>
        )}
      </div>

      <div className="mt-3 grid grid-cols-3 gap-2">
        <button
          type="button"
          onClick={() => onCommand({ type: "timer-set-running", running: !state.running })}
          className={`rounded-md py-2 text-sm font-semibold ${
            state.running
              ? "bg-pnp-yellow text-pnp-navy"
              : "bg-pnp-blue text-white"
          }`}
        >
          {state.running ? "Pause" : "Start"}
        </button>
        <button
          type="button"
          onClick={() => onCommand({ type: "timer-reset" })}
          className="rounded-md bg-pnp-gray-100 py-2 text-sm font-semibold text-pnp-gray-700 hover:bg-pnp-gray-200"
        >
          Reset
        </button>
        <button
          type="button"
          onClick={() => onCommand({ type: "timer-set-duration", seconds: 300 })}
          className="rounded-md bg-pnp-gray-100 py-2 text-sm font-semibold text-pnp-gray-700 hover:bg-pnp-gray-200"
        >
          5:00
        </button>
      </div>
    </section>
  );
}

function formatMmSs(totalSec: number): string {
  const s = Math.max(0, Math.floor(totalSec));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${m}:${r.toString().padStart(2, "0")}`;
}

function parseMmSs(raw: string): number | null {
  const t = raw.trim();
  const mmss = /^(\d+):(\d{1,2})$/.exec(t);
  if (mmss) return parseInt(mmss[1], 10) * 60 + parseInt(mmss[2], 10);
  const bare = /^(\d+)$/.exec(t);
  if (bare) return parseInt(bare[1], 10) * 60;
  return null;
}

// ─────────────────────────────────────────────────────────────────────
// Theme picker
// ─────────────────────────────────────────────────────────────────────

function ThemeCard({
  activeId,
  onCommand,
}: {
  activeId: ThemeId;
  onCommand: (c: RemoteCommand) => void;
}) {
  return (
    <section className="mt-4 rounded-2xl bg-white p-4 shadow-sm">
      <div className="text-xs font-bold uppercase tracking-wider text-pnp-gray-500">
        Theme
      </div>
      <div className="mt-3 grid grid-cols-5 gap-1.5">
        {THEME_ORDER.map((id) => (
          <button
            key={id}
            type="button"
            onClick={() => onCommand({ type: "set-theme", themeId: id })}
            className={`rounded-md py-1.5 text-xs font-semibold transition-colors ${
              activeId === id
                ? "bg-pnp-navy text-white"
                : "bg-pnp-gray-100 text-pnp-gray-700 hover:bg-pnp-gray-200"
            }`}
          >
            {PROJECTION_THEMES[id].label}
          </button>
        ))}
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────
// Reference card (collapsible)
// ─────────────────────────────────────────────────────────────────────

function ReferenceCard({
  label,
  markdown,
}: {
  label: string;
  markdown: string;
}) {
  const [open, setOpen] = useState(false);
  return (
    <details
      open={open}
      onToggle={(e) => setOpen((e.target as HTMLDetailsElement).open)}
      className="rounded-2xl bg-white shadow-sm"
    >
      <summary className="flex cursor-pointer items-center justify-between rounded-2xl px-5 py-3 text-sm font-bold uppercase tracking-wider text-pnp-gray-700">
        <span>{label}</span>
        <span
          className={`text-pnp-gray-500 transition-transform ${
            open ? "rotate-90" : ""
          }`}
          aria-hidden="true"
        >
          ▸
        </span>
      </summary>
      <div className="border-t border-pnp-gray-100 px-5 py-4 text-sm leading-relaxed text-pnp-gray-800">
        <MarkdownText text={markdown} />
      </div>
    </details>
  );
}
