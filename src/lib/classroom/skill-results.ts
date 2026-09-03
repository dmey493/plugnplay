/**
 * Tier 2 session results — localStorage-backed, no login required.
 *
 * Why this exists: the intervention could generate a sheet but nothing kept
 * what happened after it. Indiana's Individual Mathematics Plan asks for a
 * dated outcome per progress check (template p.8) and a goal cycle needs a
 * trend, not a pile of loose paper. One record per (student, skill, date) is
 * the smallest thing that makes both possible.
 *
 * Same storage conventions as `classes.ts`: a single anonymous key in this
 * browser, shaped like a real database row so a future account system can
 * migrate by writing the same JSON to a per-user table.
 *
 * Deliberately NOT stored here: anything identifying beyond the student id
 * already held in the roster. Nothing leaves the browser.
 */

/** What the two-item exit ticket produced.
 *  `mastered` mirrors the printed criterion: BOTH items correct AND a sound
 *  written explanation. `partial` is one correct, or two correct with a shaky
 *  explanation — the case the printed sheet's two branches could not express. */
export type SkillOutcome = "mastered" | "partial" | "not_yet";

/** How the evidence was collected. A session exit ticket and a dedicated
 *  progress check are not the same instrument and should not share a trend
 *  line without being distinguishable. */
export type ResultSource = "exit_ticket" | "progress_check" | "diagnostic" | "observation";

export interface SkillResult {
  id: string;
  studentId: string;
  classId?: string;
  /** e.g. "6NS4-B2" */
  skillId: string;
  /** e.g. "6.NS.4" — denormalised so a caseload view can group by standard
   *  without loading every skill file. */
  standard: string;
  outcome: SkillOutcome;
  source: ResultSource;
  /** Items correct out of items given, when the adult recorded it. Optional:
   *  a teacher who only ticks an outcome should not be blocked. */
  correct?: number;
  outOf?: number;
  /** Free text the teacher typed — what to watch next session. */
  note?: string;
  /** ISO date of the session this measures (not of data entry). */
  onDate: string;
  createdAt: string;
}

/** A goal cycle: the 3-4 week planning unit Indiana's guidance uses. Skills
 *  are named up front so the same small set can be measured more than once,
 *  which is what produces a trend. */
export interface GoalCycle {
  id: string;
  classId?: string;
  studentIds: string[];
  standard: string;
  /** The 4-6 skills this cycle drives toward. */
  skillIds: string[];
  /** e.g. "at" — the PLD band the goal targets. */
  pldBand?: string;
  goalText?: string;
  startDate: string;
  endDate: string;
  createdAt: string;
}

const RESULTS_KEY = "pnp:skill-results";
const CYCLES_KEY = "pnp:goal-cycles";

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

function newId(): string {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

function todayISO(): string {
  return new Date().toISOString().slice(0, 10);
}

// ─────────────────────────────────────────────────────────────────────
// Results
// ─────────────────────────────────────────────────────────────────────

export function getResults(): SkillResult[] {
  const list = readJSON<SkillResult[]>(RESULTS_KEY);
  if (!list) return [];
  // Oldest-first: every consumer here is building a trend, and a trend reads
  // forward in time.
  return [...list].sort((a, b) => a.onDate.localeCompare(b.onDate));
}

export function recordResult(
  input: Omit<SkillResult, "id" | "createdAt" | "onDate"> & { onDate?: string }
): SkillResult {
  const row: SkillResult = {
    ...input,
    onDate: input.onDate ?? todayISO(),
    id: newId(),
    createdAt: new Date().toISOString(),
  };
  writeJSON(RESULTS_KEY, [...getResults(), row]);
  return row;
}

export function deleteResult(id: string): void {
  writeJSON(RESULTS_KEY, getResults().filter((r) => r.id !== id));
}

export function getResultsForStudent(studentId: string): SkillResult[] {
  return getResults().filter((r) => r.studentId === studentId);
}

/** Every attempt at one skill by one student, oldest first. More than one
 *  entry here is the point: a single measurement cannot show growth. */
export function getSkillHistory(studentId: string, skillId: string): SkillResult[] {
  return getResults().filter(
    (r) => r.studentId === studentId && r.skillId === skillId
  );
}

/** The most recent outcome per skill for one student. */
export function getLatestBySkill(studentId: string): Record<string, SkillResult> {
  const out: Record<string, SkillResult> = {};
  for (const r of getResultsForStudent(studentId)) out[r.skillId] = r;
  return out;
}

// ─────────────────────────────────────────────────────────────────────
// Goal cycles
// ─────────────────────────────────────────────────────────────────────

export function getCycles(): GoalCycle[] {
  const list = readJSON<GoalCycle[]>(CYCLES_KEY);
  if (!list) return [];
  return [...list].sort((a, b) => b.startDate.localeCompare(a.startDate));
}

export function createCycle(
  input: Omit<GoalCycle, "id" | "createdAt">
): GoalCycle {
  const row: GoalCycle = { ...input, id: newId(), createdAt: new Date().toISOString() };
  writeJSON(CYCLES_KEY, [...getCycles(), row]);
  return row;
}

export function deleteCycle(id: string): void {
  writeJSON(CYCLES_KEY, getCycles().filter((c) => c.id !== id));
}

/** Progress for one student against one cycle: how many of the cycle's named
 *  skills they have mastered, and whether the cycle has enough repeated
 *  measurement to show a trend at all.
 *
 * `monitoringPoints` counts DISTINCT dates on which any cycle skill was
 * measured. Indiana asks for monitoring every 2-4 weeks inside a 3-4 week
 * cycle, so a cycle with fewer than two points has produced a snapshot, not
 * a trend, however many skills it covered. */
export function summariseCycle(cycle: GoalCycle, studentId: string) {
  const inCycle = getResultsForStudent(studentId).filter((r) =>
    cycle.skillIds.includes(r.skillId) &&
    r.onDate >= cycle.startDate && r.onDate <= cycle.endDate
  );
  const latest: Record<string, SkillResult> = {};
  for (const r of inCycle) latest[r.skillId] = r;
  const mastered = Object.values(latest).filter((r) => r.outcome === "mastered").length;
  const monitoringPoints = new Set(inCycle.map((r) => r.onDate)).size;
  return {
    skillsTargeted: cycle.skillIds.length,
    skillsMeasured: Object.keys(latest).length,
    skillsMastered: mastered,
    monitoringPoints,
    /** True once the cycle can support a trend line rather than a snapshot. */
    hasTrend: monitoringPoints >= 2,
    results: inCycle,
  };
}
