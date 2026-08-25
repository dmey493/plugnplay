/**
 * Planner data layer — localStorage-backed, no login required.
 *
 * Same bet as `classes.ts`: a teacher can build a plan the moment the page
 * loads, with no account and no backend. The stored shape is the shape a
 * database row would hold, so adding accounts later is a migration rather
 * than a rewrite:
 *
 *   planner_libraries (
 *     user_id   uuid primary key references auth.users,
 *     doc       jsonb not null,   -- the whole Library, verbatim
 *     updated_at timestamptz
 *   )
 *
 * Every read/write goes through `loadLibrary` / `saveLibrary` and nowhere
 * else, so swapping localStorage for Supabase touches only those two.
 *
 * ── THE MODEL ────────────────────────────────────────────────────────
 * Two axes, deliberately kept apart:
 *
 *   CURRICULUM (reusable, undated)   Course → Unit → Lesson
 *   CALENDAR   (dated, disposable)   Week → cells that POINT at lessons
 *
 * Lessons live in the curriculum. A week only holds references, so wiping
 * last year's weeks leaves every lesson intact and a course can be carried
 * into a new year by duplicating it. A cell can be "detached" into its own
 * copy when one day needs to differ without forking the source lesson.
 *
 * Nothing here is subject-specific. A course is whatever the teacher names
 * it — "Grade 7 Math", "AP Biology", "English 9".
 *
 * ── SCHEMA HISTORY ───────────────────────────────────────────────────
 *   v1  ordered list of blocks, duration only.
 *   v2  blocks positioned in time (`startMin`), one period per plan.
 *   v3  a plan held a week of days.
 *   v4  a library of courses, units, lessons and weeks (this file).
 */

import { activityType } from "./activity-types";

// ─────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────

export const SCHEMA_VERSION = 4;

/** The schedule snaps to this grid, in minutes. Also the shortest block. */
export const SLOT_MIN = 5;

export const DAY_LABELS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

export type Grouping = "" | "whole" | "pairs" | "small-groups" | "individual";

export const GROUPING_LABEL: Record<Exclude<Grouping, "">, string> = {
  whole: "Whole class",
  pairs: "Pairs",
  "small-groups": "Small groups",
  individual: "Individual",
};

export interface PlanBlock {
  id: string;
  /** References ACTIVITY_TYPES in `activity-types.ts`. */
  typeId: string;
  /** Editable name; defaults to the type's label. */
  label: string;
  /** Minutes elapsed from the start of the period. Multiple of SLOT_MIN. */
  startMin: number;
  /** Duration in minutes. Multiple of SLOT_MIN. */
  minutes: number;
  /** One-line summary, shown on the block when it is tall enough. */
  note?: string;
  /** The long version, shown when the block is expanded. */
  details?: string;
  grouping?: Grouping;
  materials?: string;
}

export interface Lesson {
  id: string;
  title: string;
  standard: string;
  objective: string;
  materials: string;
  notes: string;
  /** Overrides the course's period length when set. */
  periodMinutes: number | null;
  blocks: PlanBlock[];
  createdAt: string;
  updatedAt: string;
}

/** A folder inside a course. Units sort newest first, so a new one lands on
 *  top and pushes the year's earlier work down. */
export interface Unit {
  id: string;
  name: string;
  collapsed?: boolean;
  lessons: Lesson[];
  createdAt: string;
}

/** One prep. */
export interface Course {
  id: string;
  name: string;
  /** Brand token; colours the tab and the week row. */
  color: string;
  periodMinutes: number;
  units: Unit[];
  archived?: boolean;
  createdAt: string;
}

/** One slot in the weekly schedule: a course on a day. */
export interface WeekCell {
  id: string;
  courseId: string;
  /** 0 = Monday … 4 = Friday. */
  day: number;
  /** Live link into the curriculum. */
  lessonId?: string;
  /** Set when this cell was detached: its own copy, no longer linked. */
  detached?: Lesson;
  /** Free text for the cell, e.g. "assembly schedule, 30 min periods". */
  note?: string;
}

export interface Week {
  id: string;
  label: string;
  /** ISO yyyy-mm-dd for the Monday, or "" when undated. */
  startDate: string;
  cells: WeekCell[];
  /**
   * Per-day override of the period length, one entry per weekday. A
   * shortened schedule (assembly, two-hour delay, pep rally) shortens every
   * course that day, so this lives on the day and not on the cell. `null`
   * means "use each course's typical length".
   */
  dayMinutes?: (number | null)[];
  createdAt: string;
}

export interface Library {
  schemaVersion: number;
  courses: Course[];
  /** Newest first. */
  weeks: Week[];
  createdAt: string;
  updatedAt: string;
}

/** Brand tokens only (see .claude/rules/design.md). Cycled for new courses. */
export const COURSE_COLORS = [
  "#0d9488",
  "#3f42d9",
  "#f97316",
  "#22c55e",
  "#1a1f3d",
  "#ea580c",
];

// ─────────────────────────────────────────────────────────────────────
// Time helpers
// ─────────────────────────────────────────────────────────────────────

export function snap(min: number): number {
  return Math.round(min / SLOT_MIN) * SLOT_MIN;
}

export function clamp(v: number, lo: number, hi: number): number {
  return Math.min(hi, Math.max(lo, v));
}

export function blockEnd(b: PlanBlock): number {
  return b.startMin + b.minutes;
}

export function overlaps(a: PlanBlock, b: PlanBlock): boolean {
  return a.startMin < blockEnd(b) && b.startMin < blockEnd(a);
}

export function sortedBlocks(blocks: PlanBlock[]): PlanBlock[] {
  return blocks.slice().sort((a, b) => a.startMin - b.startMin);
}

export function lessonMinutes(lesson: Lesson): number {
  return lesson.blocks.reduce((sum, b) => sum + (Number(b.minutes) || 0), 0);
}

/** The period a lesson runs in: its own override, else its course's. */
export function periodFor(course: Course, lesson: Lesson): number {
  return lesson.periodMinutes ?? course.periodMinutes;
}

/**
 * How long the period actually is for a course on one day of a week.
 * A day override beats everything else, because a shortened schedule is a
 * fact about the day rather than a preference on the lesson.
 */
export function weekDayPeriod(
  week: Week,
  course: Course,
  day: number
): number {
  return week.dayMinutes?.[day] ?? course.periodMinutes;
}

export function findFreeStart(
  blocks: PlanBlock[],
  minutes: number,
  preferred: number,
  periodMinutes: number,
  ignoreId?: string
): number {
  const others = blocks.filter((b) => b.id !== ignoreId);
  const fits = (start: number) =>
    start >= 0 &&
    start + minutes <= periodMinutes &&
    !others.some((o) => start < blockEnd(o) && o.startMin < start + minutes);

  const want = clamp(snap(preferred), 0, Math.max(0, periodMinutes - minutes));
  if (fits(want)) return want;

  for (let step = SLOT_MIN; step <= periodMinutes; step += SLOT_MIN) {
    if (fits(want + step)) return want + step;
    if (fits(want - step)) return want - step;
  }
  return want;
}

export function nextOpenStart(
  blocks: PlanBlock[],
  minutes: number,
  periodMinutes: number
): number {
  let cursor = 0;
  for (const b of sortedBlocks(blocks)) {
    if (b.startMin - cursor >= minutes) break;
    cursor = Math.max(cursor, blockEnd(b));
  }
  return clamp(snap(cursor), 0, Math.max(0, periodMinutes - minutes));
}

// ─────────────────────────────────────────────────────────────────────
// Tree lookups
// ─────────────────────────────────────────────────────────────────────

export function findLesson(
  lib: Library,
  lessonId: string
): { course: Course; unit: Unit; lesson: Lesson } | null {
  for (const course of lib.courses) {
    for (const unit of course.units) {
      const lesson = unit.lessons.find((l) => l.id === lessonId);
      if (lesson) return { course, unit, lesson };
    }
  }
  return null;
}

/** What a week cell actually resolves to: its own copy, or the linked
 *  lesson. Returns null when the link points at a deleted lesson. */
export function cellLesson(lib: Library, cell: WeekCell): Lesson | null {
  if (cell.detached) return cell.detached;
  if (!cell.lessonId) return null;
  return findLesson(lib, cell.lessonId)?.lesson ?? null;
}

export function courseById(lib: Library, id: string): Course | null {
  return lib.courses.find((c) => c.id === id) ?? null;
}

// ─────────────────────────────────────────────────────────────────────
// Low-level storage
// ─────────────────────────────────────────────────────────────────────

const LIBRARY_KEY = "pnp:planner-library";
/** v3 and earlier lived here as an array of week-shaped plans. */
const LEGACY_PLANS_KEY = "pnp:lesson-plans";

function readJSON<T>(key: string): T | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(key);
    if (!raw) return null;
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

function writeJSON(key: string, value: unknown): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(key, JSON.stringify(value));
}

export function newId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `id-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

function nowISO(): string {
  return new Date().toISOString();
}

// ─────────────────────────────────────────────────────────────────────
// Factories
// ─────────────────────────────────────────────────────────────────────

export function emptyLesson(title = "Untitled lesson"): Lesson {
  const ts = nowISO();
  return {
    id: newId(),
    title,
    standard: "",
    objective: "",
    materials: "",
    notes: "",
    periodMinutes: null,
    blocks: [],
    createdAt: ts,
    updatedAt: ts,
  };
}

export function emptyUnit(name = "New unit"): Unit {
  return { id: newId(), name, lessons: [], createdAt: nowISO() };
}

export function emptyCourse(name = "New course", colorIndex = 0): Course {
  return {
    id: newId(),
    name,
    color: COURSE_COLORS[colorIndex % COURSE_COLORS.length],
    periodMinutes: 60,
    units: [emptyUnit("Unit 1")],
    createdAt: nowISO(),
  };
}

export function emptyWeek(label = "New week"): Week {
  return {
    id: newId(),
    label,
    startDate: "",
    cells: [],
    dayMinutes: DAY_LABELS.map(() => null),
    createdAt: nowISO(),
  };
}

export function emptyLibrary(): Library {
  const ts = nowISO();
  return {
    schemaVersion: SCHEMA_VERSION,
    courses: [emptyCourse("New course", 0)],
    weeks: [],
    createdAt: ts,
    updatedAt: ts,
  };
}

export function newBlock(
  typeId: string,
  startMin: number,
  overrides: Partial<PlanBlock> = {}
): PlanBlock {
  const type = activityType(typeId);
  return {
    id: newId(),
    typeId: type.id,
    label: type.label,
    startMin,
    minutes: type.defaultMinutes,
    ...overrides,
  };
}

// ─────────────────────────────────────────────────────────────────────
// Migration from the pre-library schemas
// ─────────────────────────────────────────────────────────────────────

interface LegacyBlockV1 {
  id?: string;
  kind?: string;
  title?: string;
  minutes?: number;
  note?: string;
}

const LEGACY_KIND_MAP: Record<string, string> = {
  warmup: "opener",
  fluency: "fluency",
  task: "rich-task",
  "thin-slice": "thin-slice",
  intervention: "practice",
  tool: "manipulatives",
  note: "activity",
};

interface LegacyDay {
  label?: string;
  title?: string;
  date?: string;
  standard?: string;
  objective?: string;
  materials?: string;
  notes?: string;
  blocks?: unknown[];
}

interface LegacyPlan {
  id?: string;
  schemaVersion?: number;
  title?: string;
  grade?: number | null;
  periodMinutes?: number;
  days?: LegacyDay[];
  blocks?: unknown[];
  objective?: string;
  materials?: string;
  notes?: string;
  standard?: string;
}

function blocksFromLegacy(raw: unknown[], version: number): PlanBlock[] {
  if (version >= 2) return raw as PlanBlock[];
  let cursor = 0;
  return (raw as LegacyBlockV1[]).map((b) => {
    const typeId = LEGACY_KIND_MAP[b.kind ?? ""] ?? "activity";
    const minutes = Math.max(SLOT_MIN, snap(Number(b.minutes) || SLOT_MIN));
    const block: PlanBlock = {
      id: b.id ?? newId(),
      typeId,
      label: b.title || activityType(typeId).label,
      startMin: cursor,
      minutes,
      note: b.note,
    };
    cursor += minutes;
    return block;
  });
}

/**
 * Fold the old array of week-shaped plans into one course per plan. Each
 * day that had any content becomes a lesson in an "Imported" unit, so
 * nothing a teacher already built is lost when the schema moved on.
 */
function migrateLegacy(plans: LegacyPlan[]): Library | null {
  if (plans.length === 0) return null;
  const ts = nowISO();

  const courses: Course[] = plans.map((plan, i) => {
    const version = plan.schemaVersion ?? 1;
    const unit = emptyUnit("Imported");

    const days: LegacyDay[] =
      plan.days ??
      // v1 and v2 had no days: the whole plan was a single period.
      [
        {
          title: plan.title,
          standard: plan.standard,
          objective: plan.objective,
          materials: plan.materials,
          notes: plan.notes,
          blocks: plan.blocks ?? [],
        },
      ];

    unit.lessons = days
      .filter((d) => (d.blocks?.length ?? 0) > 0 || (d.title ?? "").trim())
      .map((d) => ({
        ...emptyLesson(d.title || d.label || "Imported lesson"),
        standard: d.standard ?? "",
        objective: d.objective ?? "",
        materials: d.materials ?? "",
        notes: d.notes ?? "",
        blocks: blocksFromLegacy(d.blocks ?? [], version),
      }));

    return {
      ...emptyCourse(plan.title || `Course ${i + 1}`, i),
      periodMinutes: plan.periodMinutes || 60,
      units: [unit],
    };
  });

  return {
    schemaVersion: SCHEMA_VERSION,
    courses,
    weeks: [],
    createdAt: ts,
    updatedAt: ts,
  };
}

// ─────────────────────────────────────────────────────────────────────
// Storage adapter — the ONLY surface callers may use
// ─────────────────────────────────────────────────────────────────────

export function loadLibrary(): Library {
  const stored = readJSON<Library>(LIBRARY_KEY);
  if (stored?.courses) return stored;

  // First run on this browser: adopt anything from the older schema.
  const legacy = readJSON<LegacyPlan[]>(LEGACY_PLANS_KEY);
  if (legacy?.length) {
    const migrated = migrateLegacy(legacy);
    if (migrated) {
      writeJSON(LIBRARY_KEY, migrated);
      return migrated;
    }
  }

  return emptyLibrary();
}

export function saveLibrary(lib: Library): Library {
  const saved: Library = {
    ...lib,
    schemaVersion: SCHEMA_VERSION,
    updatedAt: nowISO(),
  };
  writeJSON(LIBRARY_KEY, saved);
  return saved;
}

// ─────────────────────────────────────────────────────────────────────
// Export / import — how a unit or course leaves this browser
//
// No backend needed: a course serialises to a JSON file a teacher can
// hand to a colleague, keep for next year, or send to an administrator.
// ─────────────────────────────────────────────────────────────────────

export interface CourseExport {
  kind: "pnp-course";
  schemaVersion: number;
  exportedAt: string;
  course: Course;
}

export function exportCourse(course: Course): string {
  const payload: CourseExport = {
    kind: "pnp-course",
    schemaVersion: SCHEMA_VERSION,
    exportedAt: nowISO(),
    course,
  };
  return JSON.stringify(payload, null, 2);
}

/** Parse an exported course, re-issuing every id so importing your own
 *  file back never collides with what is already in the library. */
export function parseCourseExport(text: string): Course | null {
  try {
    const parsed = JSON.parse(text) as CourseExport;
    if (parsed.kind !== "pnp-course" || !parsed.course) return null;
    const c = parsed.course;
    return {
      ...c,
      id: newId(),
      createdAt: nowISO(),
      units: (c.units ?? []).map((u) => ({
        ...u,
        id: newId(),
        lessons: (u.lessons ?? []).map((l) => ({ ...l, id: newId() })),
      })),
    };
  } catch {
    return null;
  }
}
