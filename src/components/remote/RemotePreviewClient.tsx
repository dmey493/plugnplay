"use client";

import { useEffect, useState } from "react";
import type {
  ProjectionState,
  RemoteCommand,
  RemoteTaskBundle,
} from "@/lib/types";
import { formGroups } from "@/lib/classes";
import RemoteDashboard from "./RemoteDashboard";

/**
 * Local sandbox for the remote dashboard. Holds a piece of fake
 * `ProjectionState` in plain React state and applies every `RemoteCommand`
 * the dashboard issues by calling the same setters the real projection
 * would use. Result: every button on the phone screen does the thing
 * it would do live, without any network round-trip.
 *
 * Includes a tiny preview-only banner across the top so it's obvious
 * this isn't the real pairing flow.
 */
export default function RemotePreviewClient() {
  const [state, setState] = useState<ProjectionState>(INITIAL_STATE);

  // Tick the timer locally when running so the preview behaves like the
  // real projection's timer (which ticks server-side and broadcasts).
  useEffect(() => {
    if (!state.timer.running) return;
    if (state.timer.remainingSec <= 0) return;
    const id = setInterval(() => {
      setState((s) => ({
        ...s,
        timer: {
          ...s.timer,
          remainingSec: Math.max(0, s.timer.remainingSec - 1),
          // Auto-pause at zero so the dashboard's "Start" pill flips back.
          running: s.timer.remainingSec - 1 > 0 ? s.timer.running : false,
        },
      }));
    }, 1000);
    return () => clearInterval(id);
  }, [state.timer.running, state.timer.remainingSec]);

  // Apply a command — mirrors `applyCommand` in ProjectionView.
  const onCommand = (cmd: RemoteCommand) => {
    setState((s) => {
      switch (cmd.type) {
        case "advance":
          return {
            ...s,
            revealedCount: Math.min(s.totalQuestions, s.revealedCount + 1),
          };
        case "retreat":
          return { ...s, revealedCount: Math.max(1, s.revealedCount - 1) };
        case "set-theme":
          return { ...s, themeId: cmd.themeId };
        case "set-window-size":
          return { ...s, windowSize: cmd.size };
        case "toggle-drawing":
          return { ...s, drawing: cmd.on };
        case "set-timer-visible":
          return { ...s, timer: { ...s.timer, visible: cmd.visible } };
        case "timer-set-duration":
          return {
            ...s,
            timer: {
              ...s.timer,
              durationSec: cmd.seconds,
              remainingSec: cmd.seconds,
            },
          };
        case "timer-set-running":
          return { ...s, timer: { ...s.timer, running: cmd.running } };
        case "timer-reset":
          return {
            ...s,
            timer: {
              ...s.timer,
              remainingSec: s.timer.durationSec,
              running: false,
            },
          };
        case "groups-form-class": {
          const roster = SAMPLE_ROSTERS[cmd.classId] ?? [];
          if (roster.length < 2) return s;
          const cls = (s.classes ?? []).find((c) => c.id === cmd.classId);
          return {
            ...s,
            groups: {
              label: cls?.name ?? "Groups",
              groups: formGroups(roster).map((g) =>
                g.map((x) => ({ id: x.id, name: x.name }))
              ),
            },
          };
        }
        case "groups-reshuffle": {
          if (!s.groups) return s;
          const flat = s.groups.groups.flat();
          return {
            ...s,
            groups: {
              ...s.groups,
              groups: formGroups(flat).map((g) =>
                g.map((x) => ({ id: x.id, name: x.name }))
              ),
            },
          };
        }
        case "groups-clear":
          return { ...s, groups: null };
        case "groups-open":
        case "groups-close":
          // No overlay in the sandbox — these are projection-side only.
          return s;
      }
    });
  };

  return (
    <div className="relative">
      {/* Preview banner — sticky-ish "you're in the sandbox" label. */}
      <div className="sticky top-0 z-30 bg-pnp-yellow px-4 py-1.5 text-center text-xs font-bold uppercase tracking-wider text-pnp-navy">
        Preview — no pairing, no projection
      </div>
      <RemoteDashboard
        bundle={SAMPLE_BUNDLE}
        state={state}
        onCommand={onCommand}
        onDisconnect={() => {
          // No-op in preview. Reset state so "Disconnect" still does
          // something visible — back to question 1.
          setState(INITIAL_STATE);
        }}
      />
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// Sample data
// ─────────────────────────────────────────────────────────────────────

const SAMPLE_BUNDLE: RemoteTaskBundle = {
  taskId: "task-math-040",
  title: "Lightning Distance Estimator",
  intro:
    "Sound travels through air at roughly **1129 feet per second**. Light is essentially instant. So when you see lightning and then hear the thunder, the gap tells you how far away the strike was.",
  questions: [
    "1. Write a linear function **d = f(t)** that gives the distance to a lightning strike (in feet) given the time gap **t** (in seconds).",
    "2. Use your function to find how many feet away each of three lightning strikes was (5s, 12s, and 27s gaps).",
    "3. There are 5280 feet in a mile. Convert each distance to miles (round to the nearest tenth).",
    "4. There's an old rule: \"divide the count by 5 to get the distance in miles.\" Check that rule against your model. Is it close? When does it work well, and when does it fail?",
    "5. The National Weather Service says you should seek shelter when thunder follows lightning within 30 seconds. Use your function to find the danger distance in miles. Why do you think 30 seconds is the cutoff?",
  ],
  discussionQuestions:
    "- Why is it OK to ignore the time it takes light to reach you?\n- What does the slope of d = 1129t mean in words?\n- The 'divide by 5' rule is a different linear model. What slope does *it* represent?\n- For Q5, is 30 seconds a safe cutoff in *every* situation?",
  anticipatedApproaches:
    "- Q1: d = 1129t (in feet).\n- Q2: A → 5645 ft; B → 13,548 ft; C → 30,483 ft.\n- Q3: A → 1.1 mi; B → 2.6 mi; C → 5.8 mi.\n- Q4: The 'divide-by-5' rule implies 1 mile per 5 seconds, or 1056 ft/s — about 6.5% slower than 1129 ft/s.\n- Q5: t = 30 → d = 33,870 ft ≈ 6.4 mi.",
  commonMisconceptions:
    "- Writing d = 1129/t (inverse) instead of d = 1129t.\n- Dropping units and reporting '5645' without specifying feet.\n- For Q4, just *applying* the rule rather than *checking* it.\n- Skipping the unit conversion in Q5.",
  sampleSolutions:
    "1. **d = 1129t** (t in seconds, d in feet).\n2. A: 5645 ft. B: 13,548 ft. C: 30,483 ft.\n3. A: 1.1 mi. B: 2.6 mi. C: 5.8 mi.\n4. Rule predicts 1.0, 2.4, 5.4 mi — slightly less than the model. Rule implies 1056 ft/s vs the true 1129 ft/s.\n5. d(30) ≈ 6.4 mi. The 30s cutoff = ~6 mile safety radius.",
  extensions:
    "- Sound speed depends on air temperature. At 50°F it's ~1100 ft/s; at 90°F it's ~1158 ft/s. Build a temperature-adjusted model.\n- Convert the function to give distance in kilometers. Sound is 343 m/s at 20°C.",
};

// Sample rosters so the preview's Groups card actually forms groups.
const SAMPLE_ROSTERS: Record<string, { id: string; name: string }[]> = {
  "sample-p3": [
    "Amy Chen", "Ben Rodriguez", "Carmen Ng", "Deshawn Ford",
    "Elena Petrov", "Frank Liu", "Grace Osei", "Hugo Martín",
  ].map((name, i) => ({ id: `p3-${i}`, name })),
  "sample-p5": [
    "Ivy Park", "Jamal Reed", "Kira Volkov", "Leo Santos", "Mona Haddad",
  ].map((name, i) => ({ id: `p5-${i}`, name })),
};

const INITIAL_STATE: ProjectionState = {
  taskId: "task-math-040",
  totalQuestions: SAMPLE_BUNDLE.questions.length,
  revealedCount: 1,
  windowSize: 2,
  themeId: "underwater",
  drawing: false,
  timer: {
    visible: false,
    durationSec: 300,
    remainingSec: 300,
    running: false,
  },
  groups: null,
  classes: [
    { id: "sample-p3", name: "Period 3 — Grade 7", count: SAMPLE_ROSTERS["sample-p3"].length },
    { id: "sample-p5", name: "Period 5 — Grade 7", count: SAMPLE_ROSTERS["sample-p5"].length },
  ],
};
