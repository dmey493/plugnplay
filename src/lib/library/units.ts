import fs from "fs";
import path from "path";
import type { UnitFile } from "@/lib/core/types";

/**
 * Filesystem-backed loader for unit definitions. Mirrors the pattern in
 * `tasks.ts` (lines 9-36): scan a content directory, parse each JSON, return
 * the collection sorted into a stable order.
 *
 * Units are owned by `web/content/units/{subject}/<id>.json`. Each JSON is a
 * plain `UnitFile` (NOT a `ContentEnvelope`) — units don't fit the
 * envelope shape and adding a 4th body variant adds friction with no win.
 *
 * Server-only. Do not import from client components.
 */

const UNITS_DIR = path.join(process.cwd(), "content", "units");
const SUBJECT_DIRS = ["math", "science"];

/** Read every unit JSON across subjects. Sorted by grade then module number
 *  so the caller can hand straight to a renderer without re-sorting. */
export async function getAllUnits(): Promise<UnitFile[]> {
  const units: UnitFile[] = [];

  for (const subject of SUBJECT_DIRS) {
    const dir = path.join(UNITS_DIR, subject);
    if (!fs.existsSync(dir)) continue;

    const files = fs.readdirSync(dir).filter((f) => f.endsWith(".json"));
    for (const file of files) {
      const raw = fs.readFileSync(path.join(dir, file), "utf-8");
      const parsed = JSON.parse(raw) as UnitFile;
      units.push(parsed);
    }
  }

  return units.sort((a, b) => {
    if (a.grade !== b.grade) return a.grade - b.grade;
    // Honour explicit teaching order (scope-and-sequence calendar) when set,
    // otherwise fall back to plain module numbering. Falling back to
    // moduleNumber means grade 8 units (which don't carry teachingOrder)
    // still sort the way they always did.
    const oa = a.teachingOrder ?? a.moduleNumber;
    const ob = b.teachingOrder ?? b.moduleNumber;
    return oa - ob;
  });
}

/** Single-unit lookup by ID (e.g. "grade-8-module-1"). Used by the unit
 *  detail page. */
export async function getUnitById(id: string): Promise<UnitFile | undefined> {
  const all = await getAllUnits();
  return all.find((u) => u.id === id);
}

/** Reverse lookup: every unit whose sections reference `taskId`. Used by
 *  the task detail page to render a small "Appears in" backlinks row.
 *  Same task ID can legitimately live in multiple units — this returns
 *  them all. */
export async function getUnitsForTask(taskId: string): Promise<UnitFile[]> {
  const all = await getAllUnits();
  return all.filter((u) =>
    u.sections.some((s) => s.taskIds.includes(taskId))
  );
}
