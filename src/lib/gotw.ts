/**
 * Graph of the Week: types + loader for the middle-school science weekly
 * graph worksheets in `web/content/science/graph-of-the-week.json`. Each
 * entry maps to a print-ready two-page worksheet in
 * `public/science/gotw/<file>` (front: question + chart + "first look";
 * back: Analyze / Claim-Evidence-Reasoning). Grades 6-8, grouped by NGSS
 * strand (PS / LS / ESS / ETS).
 */

/* eslint-disable @typescript-eslint/no-require-imports */
const gotwData = require("../../content/science/graph-of-the-week.json");
/* eslint-enable @typescript-eslint/no-require-imports */

export interface GotwEntry {
  grade: number;
  week: number;
  standard: string;
  strand: string;
  topicTitle: string;
  concept: string;
  question: string;
  chartType: string;
  file: string;
}

export interface GotwStrand {
  code: string;
  title: string;
}

interface GotwData {
  strands: GotwStrand[];
  entries: GotwEntry[];
}

const DATA = gotwData as unknown as GotwData;

export const STRANDS: GotwStrand[] = DATA.strands;
export const ENTRIES: GotwEntry[] = DATA.entries;

export const GRADES = [6, 7, 8] as const;

/** Per-strand accent from the brand palette (tokens only, per design.md). */
export const STRAND_ACCENT: Record<string, string> = {
  PS: "var(--pnp-blue)",
  LS: "var(--pnp-green)",
  ESS: "var(--pnp-orange)",
  ETS: "var(--pnp-accent)",
};

/** A standard as shown in the picker — one row per unique code in a grade. */
export interface GotwStandard {
  standard: string;
  strand: string;
  topicTitle: string;
  /** How many weekly graphs exist for this standard in this grade. */
  count: number;
}

/** Unique standards for a grade, in first-appearance (week) order. */
export function standardsForGrade(grade: number): GotwStandard[] {
  const out: GotwStandard[] = [];
  const seen = new Map<string, GotwStandard>();
  for (const e of ENTRIES.filter((x) => x.grade === grade)) {
    const hit = seen.get(e.standard);
    if (hit) {
      hit.count += 1;
      continue;
    }
    const row: GotwStandard = {
      standard: e.standard,
      strand: e.strand,
      topicTitle: e.topicTitle,
      count: 1,
    };
    seen.set(e.standard, row);
    out.push(row);
  }
  return out;
}

/** Standards for a grade grouped by strand (in canonical strand order). */
export function strandsForGrade(
  grade: number
): { strand: GotwStrand; standards: GotwStandard[] }[] {
  const standards = standardsForGrade(grade);
  return STRANDS.map((strand) => ({
    strand,
    standards: standards.filter((s) => s.strand === strand.code),
  })).filter((g) => g.standards.length > 0);
}

/** The weekly graphs for one grade + standard, in week order. */
export function entriesForStandard(
  grade: number,
  standard: string
): GotwEntry[] {
  return ENTRIES.filter(
    (e) => e.grade === grade && e.standard === standard
  ).sort((a, b) => a.week - b.week);
}

/** Public URL of a worksheet file. */
export function worksheetUrl(file: string): string {
  return `/science/gotw/${file}`;
}

/** Total weekly-graph count (used for the header count). */
export function graphCount(): number {
  return ENTRIES.length;
}
