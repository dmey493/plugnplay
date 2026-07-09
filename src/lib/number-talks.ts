import fs from "fs";
import path from "path";

/**
 * Loader for Number Talks — short mental-math warm-ups. One JSON file per
 * grade at `web/content/number-talks/grade-{6,7,8}.json`, generated from the
 * original standalone activity (scratchpad/extract_nt.js). All visuals are
 * pre-baked to static SVG strings, so this is pure serializable data.
 *
 * Server-only. Pass the result into the client browse component.
 */

export type NumberTalkType = "string" | "image" | "estimation";

export interface NumberTalk {
  id: string;
  title: string;
  strand: string;
  std: string;
  concept: string;
  type: NumberTalkType;
  /** Student-facing launch prompt. */
  launch: string;
  /** Problems revealed one at a time (HTML; may contain fraction markup). */
  problems: string[];
  /** Pre-rendered SVG for image (quick-image) talks. */
  svgHtml?: string;
  /** Teacher notes. */
  target: string;
  anticipated: string[];
  record: string;
  moves: string[];
  answers: string[];
}

export interface NumberTalkStrand {
  name: string;
  color: string;
}

export interface NumberTalkGrade {
  grade: number;
  strands: Record<string, NumberTalkStrand>;
  types: Record<string, string>;
  talks: NumberTalk[];
}

export function getNumberTalkGrade(grade: number): NumberTalkGrade {
  const p = path.join(process.cwd(), "content", "number-talks", `grade-${grade}.json`);
  return JSON.parse(fs.readFileSync(p, "utf-8")) as NumberTalkGrade;
}

export function getAllNumberTalks(): NumberTalkGrade[] {
  return [6, 7, 8].map(getNumberTalkGrade);
}
