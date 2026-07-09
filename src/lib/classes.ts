/**
 * Class roster data layer — localStorage-backed for the no-auth draft.
 *
 * Shape mirrors what a real database row will eventually hold, so when
 * Supabase / NextAuth lands we can migrate by writing the same JSON to
 * a table without reworking callers. Everything is keyed off a fake
 * "user" stored in localStorage; the moment real auth ships, swap
 * getUser() for the session reader.
 *
 * No constraints (lock-with, lock-apart, fixed-board) in this draft per
 * Dave's instructions — students are just `{ id, name }` for now. The
 * type leaves room for those fields to slot in later without breaking
 * existing rosters (they'll be undefined for old records, which is
 * fine: the randomizer treats undefined as "no constraint").
 */

export interface User {
  id: string;
  name: string;
  createdAt: string;
}

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

const USER_KEY = "pnp:user";
const classesKey = (userId: string) => `pnp:classes:${userId}`;

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
// User (fake login)
// ─────────────────────────────────────────────────────────────────────

export function getUser(): User | null {
  return readJSON<User>(USER_KEY);
}

export function setUser(name: string): User {
  const trimmed = name.trim();
  const existing = getUser();
  if (existing) {
    const updated: User = { ...existing, name: trimmed };
    writeJSON(USER_KEY, updated);
    return updated;
  }
  const user: User = { id: newId(), name: trimmed, createdAt: nowISO() };
  writeJSON(USER_KEY, user);
  return user;
}

export function clearUser(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(USER_KEY);
}

// ─────────────────────────────────────────────────────────────────────
// Classes CRUD
// ─────────────────────────────────────────────────────────────────────

export function getClasses(userId: string): Class[] {
  const list = readJSON<Class[]>(classesKey(userId));
  if (!list) return [];
  // Sort newest-first so the most recently edited class is at the top.
  return [...list].sort((a, b) =>
    (b.updatedAt ?? b.createdAt).localeCompare(a.updatedAt ?? a.createdAt)
  );
}

export function getClass(userId: string, classId: string): Class | null {
  return getClasses(userId).find((c) => c.id === classId) ?? null;
}

export function createClass(userId: string, name: string): Class {
  const cls: Class = {
    id: newId(),
    name: name.trim() || "Untitled class",
    students: [],
    createdAt: nowISO(),
    updatedAt: nowISO(),
  };
  const all = getClasses(userId);
  writeJSON(classesKey(userId), [cls, ...all]);
  return cls;
}

export function updateClass(
  userId: string,
  classId: string,
  patch: Partial<Pick<Class, "name" | "students">>
): Class | null {
  const all = getClasses(userId);
  const idx = all.findIndex((c) => c.id === classId);
  if (idx === -1) return null;
  const updated: Class = {
    ...all[idx],
    ...patch,
    updatedAt: nowISO(),
  };
  const next = [...all];
  next[idx] = updated;
  writeJSON(classesKey(userId), next);
  return updated;
}

export function deleteClass(userId: string, classId: string): void {
  const all = getClasses(userId);
  writeJSON(
    classesKey(userId),
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
export function addStudent(
  userId: string,
  classId: string,
  name: string
): Class | null {
  const cls = getClass(userId, classId);
  if (!cls) return null;
  const student: Student = { id: newId(), name: name.trim() };
  return updateClass(userId, classId, {
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
