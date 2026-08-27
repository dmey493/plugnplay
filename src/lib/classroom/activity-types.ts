/**
 * The generic activity types a teacher drags onto the schedule.
 *
 * Deliberately NOT tied to specific content. A block says "Rich task, 25
 * minutes" — which rich task is a later decision, made in the room or in a
 * later phase of this tool. That keeps the planner useful for planning a
 * week before any of the resources are chosen.
 *
 * This is the file to edit when a type should be added, renamed, recoloured
 * or given a different default length. Nothing else hard-codes a type.
 *
 * Colours are brand tokens only (see .claude/rules/design.md). `onFill` says
 * which text colour keeps AA contrast on that fill — the yellow and the
 * light fills need navy text, the saturated ones take white.
 */

export type ActivityGroup = "phase" | "format" | "blank";

export interface ActivityType {
  id: string;
  label: string;
  group: ActivityGroup;
  /** Starting length in minutes; every block is editable afterwards. */
  defaultMinutes: number;
  fill: string;
  onFill: "white" | "navy";
  /** One-line hint shown in the palette. */
  hint: string;
}

export const ACTIVITY_TYPES: ActivityType[] = [
  // ── Lesson phases: the spine of a period ────────────────────────────
  {
    id: "opener",
    label: "Opener",
    group: "phase",
    defaultMinutes: 8,
    fill: "#f97316",
    onFill: "white",
    hint: "Bell work, warm-up, hook",
  },
  {
    id: "core",
    label: "Core",
    group: "phase",
    defaultMinutes: 25,
    fill: "#0d9488",
    onFill: "white",
    hint: "The main event of the lesson",
  },
  {
    id: "practice",
    label: "Practice",
    group: "phase",
    defaultMinutes: 12,
    fill: "#22c55e",
    onFill: "white",
    hint: "Independent or partner work",
  },
  {
    id: "close",
    label: "Close",
    group: "phase",
    defaultMinutes: 5,
    fill: "#1a1f3d",
    onFill: "white",
    hint: "Consolidate, debrief, exit",
  },

  // ── Formats: what the activity actually is ──────────────────────────
  {
    id: "rich-task",
    label: "Rich task",
    group: "format",
    defaultMinutes: 25,
    fill: "#0d9488",
    onFill: "white",
    hint: "Thinking task at the boards",
  },
  {
    id: "wodb",
    label: "Which One Doesn't Belong",
    group: "format",
    defaultMinutes: 8,
    fill: "#3f42d9",
    onFill: "white",
    hint: "Four boxes, every one arguable",
  },
  {
    id: "number-talk",
    label: "Number talk",
    group: "format",
    defaultMinutes: 10,
    fill: "#ea580c",
    onFill: "white",
    hint: "Mental math, compare strategies",
  },
  {
    id: "thin-slice",
    label: "Thin slice",
    group: "format",
    defaultMinutes: 20,
    fill: "#3f42d9",
    onFill: "white",
    hint: "Small-step sequence",
  },
  {
    id: "fluency",
    label: "Fluency practice",
    group: "format",
    defaultMinutes: 10,
    fill: "#22c55e",
    onFill: "white",
    hint: "Timed skill drill",
  },
  {
    id: "mini-lesson",
    label: "Mini-lesson",
    group: "format",
    defaultMinutes: 10,
    fill: "#1a1f3d",
    onFill: "white",
    hint: "Direct instruction, notes",
  },
  {
    id: "discussion",
    label: "Discussion",
    group: "format",
    defaultMinutes: 10,
    fill: "#ffe25a",
    onFill: "navy",
    hint: "Whole-class talk, share out",
  },
  {
    id: "group-work",
    label: "Group work",
    group: "format",
    defaultMinutes: 15,
    fill: "#60a5fa",
    onFill: "navy",
    hint: "Visibly random groups",
  },
  {
    id: "manipulatives",
    label: "Manipulatives / tools",
    group: "format",
    defaultMinutes: 10,
    fill: "#2dd4bf",
    onFill: "navy",
    hint: "Hands-on or the whiteboard",
  },
  {
    id: "exit-ticket",
    label: "Exit ticket",
    group: "format",
    defaultMinutes: 5,
    fill: "#4b5563",
    onFill: "white",
    hint: "Quick check before the bell",
  },
  {
    id: "assessment",
    label: "Assessment",
    group: "format",
    defaultMinutes: 20,
    fill: "#ef4444",
    onFill: "white",
    hint: "Quiz, test, proficiency check",
  },

  // ── Blank ───────────────────────────────────────────────────────────
  {
    id: "activity",
    label: "Activity",
    group: "blank",
    defaultMinutes: 10,
    fill: "#9ca3af",
    onFill: "navy",
    hint: "Anything else — name it yourself",
  },
];

export const GROUP_LABEL: Record<ActivityGroup, string> = {
  phase: "Lesson phases",
  format: "Activity formats",
  blank: "Blank",
};

const BY_ID = new Map(ACTIVITY_TYPES.map((t) => [t.id, t]));

/** Types are looked up by id from stored blocks, so a plan saved before a
 *  type was renamed still resolves. Unknown ids fall back to the blank type
 *  rather than crashing the grid. */
export function activityType(id: string): ActivityType {
  return BY_ID.get(id) ?? BY_ID.get("activity")!;
}
