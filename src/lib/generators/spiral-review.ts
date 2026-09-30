/**
 * Spiral review: types and client-side helpers for /math/spiral-review.
 *
 * A teacher picks standards (1 or 2 problems each, at most 8 a week), a level
 * per standard and a number of weeks. The engine (engine/spiral_api.py) picks
 * every week's problems, with the same standards each week and no repeats,
 * and draws them as one PDF. This module holds the shapes that pass between
 * the page and the API, plus the small pieces of logic the page needs:
 * capacity math, print order, the saved set, and the shareable link.
 *
 * Client-safe: no server imports.
 */

import type { ProficiencyLevel } from "@/lib/standards/plds";

export const MAX_PROBLEMS = 8;
export const MAX_WEEKS = 8;
export const MAX_START_WEEK = 99;
export const DEFAULT_LEVEL: ProficiencyLevel = "at";

export interface SpiralPick {
  code: string;
  count: 1 | 2;
  level: ProficiencyLevel;
}

/** What a teacher has set up for one grade. */
export interface GradeSetup {
  picks: SpiralPick[];
  weeks: number;
  startWeek: number;
}

export const EMPTY_SETUP: GradeSetup = { picks: [], weeks: 1, startWeek: 1 };

// ── API shapes (engine/spiral_api.py) ─────────────────────────────────────

export interface SpiralProblem {
  uid: string;
  standard: string;
  seed: number;
  question_id: string;
  position: number;
  proficiency_level: ProficiencyLevel;
  difficulty: string;
  item_type: string;
  stem_index: number;
  stem_text: string;
  answer_text: string;
  has_figure: boolean;
  fingerprint: string;
}

export interface FitWarning {
  code: "too_tall" | "too_wide";
  position: number;
  standard: string;
  uid: string;
  week_number?: number;
}

/** How a week sits on paper: 1 page when it fits, else split between rows. */
export interface WeekFit {
  pages: number;
  problems_per_page: number[];
  scale: number;
  warnings: FitWarning[];
}

export interface SpiralWeek {
  week_number: number;
  questions: SpiralProblem[];
  fit: WeekFit | null;
}

export interface PlanWarning {
  code: string;
  standard?: string;
  week_number?: number;
  message?: string;
}

export interface PlanStandard {
  code: string;
  level: ProficiencyLevel;
  level_used: ProficiencyLevel;
  count: 1 | 2;
  seed: number;
  /** Problem types at this level. With one, every week is the same type. */
  stem_count: number;
}

export interface SpiralPlan {
  grade: number;
  set_seed: number;
  start_week: number;
  standards: PlanStandard[];
  weeks: SpiralWeek[];
  warnings: PlanWarning[];
}

export interface PdfReport {
  weeks: (WeekFit & { week_number: number })[];
  warnings: FitWarning[];
}

/** The engine's error shape: {error, message}. */
export interface EngineError {
  error: string;
  message?: string;
}

export function isEngineError(x: unknown): x is EngineError {
  return typeof x === "object" && x !== null && "error" in x;
}

// ── Sheet math ────────────────────────────────────────────────────────────

export function problemCount(picks: SpiralPick[]): number {
  return picks.reduce((n, p) => n + p.count, 0);
}

/**
 * The order problems print in: every standard's first problem, then the
 * second problems. It mirrors the engine, which spaces a standard's two
 * problems apart and keeps each standard in the same spot every week.
 */
export function printOrder(picks: SpiralPick[]): { code: string; slot: 0 | 1 }[] {
  return [
    ...picks.map((p) => ({ code: p.code, slot: 0 as const })),
    ...picks.filter((p) => p.count === 2).map((p) => ({ code: p.code, slot: 1 as const })),
  ];
}

/** The request body the engine needs to rebuild one week. */
export function weekRefs(week: SpiralWeek) {
  return {
    week_number: week.week_number,
    questions: week.questions.map((q) => ({
      standard: q.standard,
      seed: q.seed,
      question_id: q.question_id,
    })),
  };
}

export function planRefs(plan: SpiralPlan) {
  return { weeks: plan.weeks.map(weekRefs) };
}

/** A key for "is this plan still what the sheet panel shows?". */
export function setupSignature(grade: number, setup: GradeSetup): string {
  const picks = setup.picks.map((p) => `${p.code}:${p.count}:${p.level}`).join(",");
  return `${grade}|${picks}|${setup.weeks}|${setup.startWeek}`;
}

export function weeksLabel(numbers: number[]): string {
  if (numbers.length === 0) return "";
  const lo = Math.min(...numbers);
  const hi = Math.max(...numbers);
  return lo === hi ? `Week ${lo}` : `Weeks ${lo}-${hi}`;
}

// ── Saved set (per browser) ───────────────────────────────────────────────

const STORAGE_KEY = "pnp.spiral.v1";

export interface SpiralSaved {
  grade: number;
  byGrade: Record<string, GradeSetup>;
  /** Highest week number downloaded, per grade. The next visit starts after it. */
  lastDownloadedWeek: Record<string, number>;
}

const LEVELS: readonly ProficiencyLevel[] = ["below", "approaching", "at", "above"];

function clampInt(v: unknown, lo: number, hi: number, fallback: number): number {
  const n = Math.round(Number(v));
  return Number.isFinite(n) ? Math.min(hi, Math.max(lo, n)) : fallback;
}

/** Keep only what the page can use; storage and links are user-editable. */
export function sanitizeSetup(grade: number, raw: unknown): GradeSetup {
  const src = (raw ?? {}) as Partial<GradeSetup>;
  const picks: SpiralPick[] = [];
  let total = 0;
  for (const p of Array.isArray(src.picks) ? src.picks : []) {
    const code = String((p as SpiralPick)?.code ?? "");
    if (!code.startsWith(`${grade}.`) || picks.some((x) => x.code === code)) continue;
    const count = (p as SpiralPick).count === 2 ? 2 : 1;
    const level = LEVELS.includes((p as SpiralPick).level)
      ? (p as SpiralPick).level
      : DEFAULT_LEVEL;
    if (total + count > MAX_PROBLEMS) break;
    picks.push({ code, count, level });
    total += count;
  }
  return {
    picks,
    weeks: clampInt(src.weeks, 1, MAX_WEEKS, 1),
    startWeek: clampInt(src.startWeek, 1, MAX_START_WEEK, 1),
  };
}

export function loadSaved(): SpiralSaved | null {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const data = JSON.parse(raw) as Partial<SpiralSaved>;
    const grade = [6, 7, 8].includes(Number(data.grade)) ? Number(data.grade) : 6;
    const byGrade: Record<string, GradeSetup> = {};
    for (const g of [6, 7, 8]) {
      if (data.byGrade?.[g]) byGrade[g] = sanitizeSetup(g, data.byGrade[g]);
    }
    const lastDownloadedWeek: Record<string, number> = {};
    for (const [g, w] of Object.entries(data.lastDownloadedWeek ?? {})) {
      lastDownloadedWeek[g] = clampInt(w, 0, MAX_START_WEEK, 0);
    }
    return { grade, byGrade, lastDownloadedWeek };
  } catch {
    return null;
  }
}

export function saveSaved(saved: SpiralSaved): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(saved));
  } catch {
    // Private windows and blocked storage: the page still works, it just
    // won't remember the set next time.
  }
}

// ── Shareable link ────────────────────────────────────────────────────────
// ?grade=7&set=7.RP.2:2:at,7.NS.3:1:approaching&weeks=4&start=5

export function encodeSetParams(grade: number, setup: GradeSetup): string {
  const params = new URLSearchParams();
  params.set("grade", String(grade));
  params.set("set", setup.picks.map((p) => `${p.code}:${p.count}:${p.level}`).join(","));
  params.set("weeks", String(setup.weeks));
  params.set("start", String(setup.startWeek));
  return params.toString();
}

export function decodeSetParams(
  params: URLSearchParams
): { grade: number; setup: GradeSetup } | null {
  const set = params.get("set");
  const grade = Number(params.get("grade"));
  if (!set || ![6, 7, 8].includes(grade)) return null;
  const picks = set.split(",").map((chunk) => {
    const [code, count, level] = chunk.split(":");
    return { code, count: Number(count), level };
  });
  const setup = sanitizeSetup(grade, {
    picks,
    weeks: params.get("weeks"),
    startWeek: params.get("start"),
  });
  return setup.picks.length ? { grade, setup } : null;
}

// ── Checkpoint windows ────────────────────────────────────────────────────

const MONTHS = [
  "january", "february", "march", "april", "may", "june",
  "july", "august", "september", "october", "november", "december",
];

/**
 * The id of the checkpoint whose window ("September - November") includes
 * today's month, or null in the summer. Windows share their edge months, so
 * the earlier window wins.
 */
export function currentCheckpointId(
  checkpoints: { id: string; window: string }[],
  today: Date = new Date()
): string | null {
  const m = today.getMonth();
  for (const cp of checkpoints) {
    const [a, b] = cp.window.toLowerCase().split("-").map((s) => MONTHS.indexOf(s.trim()));
    if (a < 0 || b < 0) continue;
    const inside = a <= b ? m >= a && m <= b : m >= a || m <= b;
    if (inside) return cp.id;
  }
  return null;
}

// ── Labels ────────────────────────────────────────────────────────────────

export const ITEM_TYPE_LABELS: Record<string, string> = {
  MC: "Multiple choice",
  MS: "Select all that apply",
  NR: "Number answer",
  EQ: "Equation",
  MP: "Multi-part",
  ER: "Written response",
  TI: "Fill in",
  DD: "Drop-down",
  TM: "Table",
};
