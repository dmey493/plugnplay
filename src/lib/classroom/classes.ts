/**
 * Class roster data layer — localStorage-backed, no login required.
 *
 * Classes live under a single anonymous key in this browser. There's no
 * account and no sign-in: a teacher can build classes and form groups
 * immediately. The shape still mirrors what a real database row would
 * hold, so if a real account system ever lands we can migrate by writing
 * the same JSON to a per-user table without reworking callers.
 *
 * No constraints (lock-with, lock-apart, fixed-board) in this draft per
 * Dave's instructions — students are just `{ id, name }` for now. The
 * type leaves room for those fields to slot in later without breaking
 * existing rosters (they'll be undefined for old records, which is
 * fine: the randomizer treats undefined as "no constraint").
 */

export interface Student {
  id: string;
  name: string;
  // Reserved for the next phase — undefined for now.
  fixedBoard?: number;
  lockWith?: string[];   // student ids
  lockApart?: string[];  // student ids
}

export interface Class {
  id: string;
  name: string;
  students: Student[];
  createdAt: string;
  updatedAt: string;
}

// ─────────────────────────────────────────────────────────────────────
// Storage keys + low-level helpers
// ─────────────────────────────────────────────────────────────────────

const CLASSES_KEY = "pnp:classes";
// Legacy per-user key prefix from the old fake-login draft. Kept only so
// migrateLegacy() can adopt classes saved before sign-in was removed.
const LEGACY_CLASSES_PREFIX = "pnp:classes:";

/** Read JSON from localStorage; return null on miss or parse error.
 *  SSR-safe — returns null when `window` is undefined. */
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

/** URL-safe random id. Good enough for localStorage records — when
 *  real auth lands and these become DB rows, the DB issues real ids. */
function newId(): string {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

function nowISO(): string {
  return new Date().toISOString();
}

// ─────────────────────────────────────────────────────────────────────
// One-time migration off the old fake-login store
// ─────────────────────────────────────────────────────────────────────

/** If classes were saved under the old per-user key (`pnp:classes:<id>`)
 *  before sign-in was removed, adopt them into the new anonymous key so
 *  the teacher doesn't lose their rosters. Runs lazily on first read and
 *  is a no-op once the new key exists. Picks the largest legacy roster
 *  set if more than one name was ever used in this browser. */
function migrateLegacy(): void {
  if (typeof window === "undefined") return;
  // Already migrated (or already has data) — nothing to do.
  if (window.localStorage.getItem(CLASSES_KEY) !== null) return;

  let best: Class[] | null = null;
  let bestKey: string | null = null;
  for (let i = 0; i < window.localStorage.length; i++) {
    const key = window.localStorage.key(i);
    // Match `pnp:classes:<id>` but not the new bare `pnp:classes`.
    if (!key || !key.startsWith(LEGACY_CLASSES_PREFIX)) continue;
    const list = readJSON<Class[]>(key);
    if (list && list.length > (best?.length ?? 0)) {
      best = list;
      bestKey = key;
    }
  }

  // Write something to CLASSES_KEY either way so this migration doesn't
  // re-scan on every read. An empty array is a valid "no classes" state.
  writeJSON(CLASSES_KEY, best ?? []);
  // Clean up the adopted legacy key so it can't shadow future edits.
  if (bestKey) window.localStorage.removeItem(bestKey);
}

// ─────────────────────────────────────────────────────────────────────
// Classes CRUD
// ─────────────────────────────────────────────────────────────────────

export function getClasses(): Class[] {
  migrateLegacy();
  const list = readJSON<Class[]>(CLASSES_KEY);
  if (!list) return [];
  // Sort newest-first so the most recently edited class is at the top.
  return [...list].sort((a, b) =>
    (b.updatedAt ?? b.createdAt).localeCompare(a.updatedAt ?? a.createdAt)
  );
}

export function getClass(classId: string): Class | null {
  return getClasses().find((c) => c.id === classId) ?? null;
}

export function createClass(name: string): Class {
  const cls: Class = {
    id: newId(),
    name: name.trim() || "Untitled class",
    students: [],
    createdAt: nowISO(),
    updatedAt: nowISO(),
  };
  const all = getClasses();
  writeJSON(CLASSES_KEY, [cls, ...all]);
  return cls;
}

export function updateClass(
  classId: string,
  patch: Partial<Pick<Class, "name" | "students">>
): Class | null {
  const all = getClasses();
  const idx = all.findIndex((c) => c.id === classId);
  if (idx === -1) return null;
  const updated: Class = {
    ...all[idx],
    ...patch,
    updatedAt: nowISO(),
  };
  const next = [...all];
  next[idx] = updated;
  writeJSON(CLASSES_KEY, next);
  return updated;
}

export function deleteClass(classId: string): void {
  const all = getClasses();
  writeJSON(
    CLASSES_KEY,
    all.filter((c) => c.id !== classId)
  );
}

// ─────────────────────────────────────────────────────────────────────
// Roster helpers
// ─────────────────────────────────────────────────────────────────────

/** Parse a free-form roster paste into Student records. Accepts one
 *  name per line (Excel column copy, hand-typed list, etc.); commas
 *  and tabs are also supported for compact pastes. Trims and de-dupes
 *  blanks. Each new student gets a fresh id — callers can merge with
 *  existing students afterwards if they want to preserve ids. */
export function parseRosterPaste(text: string): Student[] {
  const parts = text
    .split(/[\n,\t]/g)
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
  return parts.map((name) => ({ id: newId(), name }));
}

/** Add a single student to a class. Returns the updated class, or null
 *  if the class doesn't exist. */
export function addStudent(classId: string, name: string): Class | null {
  const cls = getClass(classId);
  if (!cls) return null;
  const student: Student = { id: newId(), name: name.trim() };
  return updateClass(classId, {
    students: [...cls.students, student],
  });
}

// ─────────────────────────────────────────────────────────────────────
// Grouping algorithm — locked to "threes with twos on the remainder"
// per Dave's draft spec. Lifted into the lib now so the future
// animation code consumes a single source of truth.
//
//   n % 3 === 0 → all groups of 3
//   n % 3 === 1 → (n−4)/3 threes + two twos       (e.g. 13 → 3,3,3,2,2)
//   n % 3 === 2 → (n−2)/3 threes + one  two       (e.g. 14 → 3,3,3,3,2)
//
// Edge cases:
//   n = 0 → []      (no students, no groups)
//   n = 1 → [[only]] (one solo group — better than dropping the student)
//   n = 2 → [[two]]  (one pair)
//   n = 4 → [[2],[2]] (two pairs — can't make a 3+1)
// ─────────────────────────────────────────────────────────────────────

/** Compute the desired group sizes (largest-first) for n students. */
export function planGroupSizes(n: number): number[] {
  if (n <= 0) return [];
  if (n === 1) return [1];
  if (n === 2) return [2];
  if (n === 4) return [2, 2];
  const r = n % 3;
  if (r === 0) return Array.from({ length: n / 3 }, () => 3);
  if (r === 1) {
    const threes = (n - 4) / 3;
    return [...Array.from({ length: threes }, () => 3), 2, 2];
  }
  // r === 2
  const threes = (n - 2) / 3;
  return [...Array.from({ length: threes }, () => 3), 2];
}

/** Shuffle a copy of `items` using Fisher–Yates. Pure, side-effect-free.
 *  Used both for the actual randomization and for the visual animation
 *  layer (so the animation reflects the real assignment). */
export function shuffle<T>(items: readonly T[]): T[] {
  const arr = [...items];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

// ─────────────────────────────────────────────────────────────────────
// Last-formed groups — persisted so closing the projection overlay
// doesn't lose the assignment. A student who forgot their board can
// reopen Groups and see exactly where they were placed. One slot,
// latest-wins; "Clear" / "New groups" reset it.
// ─────────────────────────────────────────────────────────────────────

const LAST_GROUPS_KEY = "pnp:groups:last";

export interface SavedGroups {
  /** Class name or "Quick group" — shown so the teacher knows whose
   *  groups these are. */
  label: string;
  groups: Student[][];
  /** ISO timestamp of when they were formed. */
  formedAt: string;
}

export function getLastGroups(): SavedGroups | null {
  const saved = readJSON<SavedGroups>(LAST_GROUPS_KEY);
  // Guard against a malformed/empty payload from an older shape.
  if (!saved || !Array.isArray(saved.groups) || saved.groups.length === 0) {
    return null;
  }
  return saved;
}

export function saveLastGroups(label: string, groups: Student[][]): void {
  writeJSON(LAST_GROUPS_KEY, { label, groups, formedAt: nowISO() });
}

export function clearLastGroups(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(LAST_GROUPS_KEY);
}

/** Form groups from a flat list of students.  v1 logic: shuffle, then
 *  slice into the sizes returned by planGroupSizes(). Returns groups
 *  in deal order — the animation can use the order directly. */
export function formGroups(students: readonly Student[]): Student[][] {
  const sizes = planGroupSizes(students.length);
  const shuffled = shuffle(students);
  const groups: Student[][] = [];
  let cursor = 0;
  for (const size of sizes) {
    groups.push(shuffled.slice(cursor, cursor + size));
    cursor += size;
  }
  return groups;
}
