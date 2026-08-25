import fs from "fs";
import path from "path";

/**
 * Checkpoint loader — which standards ILEARN assesses on each checkpoint.
 *
 * Mirrors the pattern in `units.ts` and `lessons.ts`: scan a content
 * directory, parse each JSON, return it keyed by grade for a client
 * component to receive as a prop.
 *
 * WHERE THE DATA COMES FROM
 * `Indiana Assessment Framework_ Mathematics.xlsx` (IDOE), one sheet per
 * grade, generated into `content/checkpoints/math/grade-{6,7,8}.json`. Each
 * standard's row marks "Assessed" under the checkpoints it appears on.
 *
 * Two things this is NOT:
 *   - It is not in the ILEARN item specifications. Their "Assessed On" row
 *     is a static header listing all four windows, identical in all 68
 *     documents, with no per-window marking of any kind.
 *   - It is not the teaching order. The district scope and sequence says
 *     when a module is TAUGHT, which is a different (and larger) set per
 *     checkpoint than what the state ASSESSES. `basis` records which
 *     question a given file answers.
 *
 * Server-only. Do not import from client components.
 */

export interface Checkpoint {
  /** "cp1" | "cp2" | "cp3". */
  id: string;
  label: string;
  fullName: string;
  /** Testing window, e.g. "September - November". */
  window: string;
  /** Item count for the window, e.g. "20-25 Items". */
  items: string;
  /** The count the framework's own header claims, used to verify the parse. */
  expectedCount: number | null;
  standards: string[];
}

/** Per-standard detail straight off the framework row. */
export interface FrameworkStandard {
  code: string;
  /** "Essential" | "Standard" — the framework's Level of Priority. */
  priority: string;
  /** "Calculator" | "Non-Calculator". */
  calculator: string;
  subdomain: string;
  /** "All Indiana Students" | "Sample of Indiana Students". */
  summative: string;
  /** Checkpoint ids this standard is assessed on; empty = summative only. */
  checkpoints: string[];
}

export interface GradeCheckpoints {
  grade: number;
  /**
   * Which question the data answers:
   *   "framework" — standards IDOE ASSESSES on each checkpoint.
   *   "teaching-order" — standards TAUGHT before each checkpoint, derived
   *      from a district scope and sequence. A larger, different set.
   */
  basis: "framework" | "teaching-order";
  source: string;
  note: string;
  summativeLabel: string;
  summativeItems: string;
  summativeWindow: string;
  checkpoints: Checkpoint[];
  standards: Record<string, FrameworkStandard>;
}

export type CheckpointNav = Record<number, GradeCheckpoints>;

const DIR = path.join(process.cwd(), "content", "checkpoints", "math");

export async function getCheckpointNav(): Promise<CheckpointNav> {
  const nav: CheckpointNav = {};
  if (!fs.existsSync(DIR)) return nav;

  for (const file of fs.readdirSync(DIR).filter((f) => f.endsWith(".json"))) {
    const raw = fs.readFileSync(path.join(DIR, file), "utf-8");
    const parsed = JSON.parse(raw) as GradeCheckpoints;
    nav[parsed.grade] = parsed;
  }
  return nav;
}

/** The checkpoint a standard is assessed on, or null when it is summative
 *  only (or the grade has no framework data). */
export function checkpointForStandard(
  nav: CheckpointNav,
  grade: number,
  code: string
): Checkpoint | null {
  const g = nav[grade];
  if (!g) return null;
  return g.checkpoints.find((cp) => cp.standards.includes(code)) ?? null;
}

/** Standards the framework assesses only on the summative, never on a
 *  checkpoint. Worth surfacing: they are easy to leave until too late. */
export function summativeOnly(g: GradeCheckpoints): string[] {
  return Object.values(g.standards)
    .filter((s) => s.checkpoints.length === 0)
    .map((s) => s.code);
}
