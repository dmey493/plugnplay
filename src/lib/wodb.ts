import fs from "fs";
import path from "path";
import type { WodbBox } from "./wodb-render";

/**
 * Loader for the "Which One Doesn't Belong?" warm-up sets. One JSON file
 * per grade at `web/content/wodb/grade-{6,7,8}.json`, generated from the
 * original standalone activity (see scratchpad/extract_wodb.js). Each set's
 * four boxes are render specs consumed by `renderBox` in `wodb-render.ts`.
 *
 * Server-only (reads the filesystem). Pass the result into the client
 * browse component as a prop.
 */

export interface WodbSet {
  /** Slug id, unique within the grade. */
  id: string;
  title: string;
  /** Strand key (ns / rp / af / gm / ds). */
  strand: string;
  /** Indiana standard code, e.g. "6.RP.3". */
  std: string;
  concept: string;
  /** The four boxes (top-left, top-right, bottom-left, bottom-right). */
  quads: WodbBox[];
  /** One-line framing shown above the teacher notes. */
  lead: string;
  /** Why each of A/B/C/D can be argued as the odd one out. */
  args: string[];
  /** Discussion prompts. */
  prompts: string[];
}

export interface WodbStrand {
  name: string;
  color: string;
}

export interface WodbGrade {
  grade: number;
  strands: Record<string, WodbStrand>;
  sets: WodbSet[];
}

export function getWodbGrade(grade: number): WodbGrade {
  const p = path.join(process.cwd(), "content", "wodb", `grade-${grade}.json`);
  return JSON.parse(fs.readFileSync(p, "utf-8")) as WodbGrade;
}

/** All grades (6, 7, 8) in order. */
export function getAllWodb(): WodbGrade[] {
  return [6, 7, 8].map(getWodbGrade);
}
