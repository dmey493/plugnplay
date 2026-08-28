/**
 * ILEARN proficiency level descriptors (PLDs), one set per standard.
 *
 * These are the assessment's own words for what each level demands. The
 * problem generator shows them under the standard a teacher picks, so the
 * choice of format is made against what the level actually asks for rather
 * than against the band name alone.
 *
 * Built from the item-specification docx set, with IDOE's rolling revisions
 * layered on top. Regenerate with
 *
 *     python authoring/extract_plds.py
 *
 * All 69 standards are covered. 16 carry a `revised` date, meaning IDOE has
 * rewritten that standard's descriptors since the docx set was published; the
 * rewrites are substantive, so the date is shown to the teacher rather than
 * kept as build metadata.
 */

/* eslint-disable @typescript-eslint/no-require-imports */
const pldData = require("../../../content/standards/plds.json");
/* eslint-enable @typescript-eslint/no-require-imports */

export type ProficiencyLevel = "below" | "approaching" | "at" | "above";

/** Ascending, which is the order they are shown in. */
export const PROFICIENCY_LEVELS: ProficiencyLevel[] = [
  "below",
  "approaching",
  "at",
  "above",
];

export const PROFICIENCY_LABELS: Record<ProficiencyLevel, string> = {
  below: "Below",
  approaching: "Approaching",
  at: "At",
  above: "Above",
};

export interface StandardPlds extends Partial<Record<ProficiencyLevel, string>> {
  /** ISO date of the IDOE revision these descriptors came from, when they came
   *  from one. Absent means the original published specification still holds. */
  revised?: string;
}

/** The four descriptors for a standard, or null when the spec is missing. */
export function getPlds(standard: string): StandardPlds | null {
  const found = (pldData as Record<string, StandardPlds>)[standard];
  return found && PROFICIENCY_LEVELS.some((l) => found[l]) ? found : null;
}

/** "24 August 2026" from "2026-08-24". Returns null for anything unparseable
 *  so a malformed date never renders as "Invalid Date" on the page. */
export function formatRevised(revised: string | undefined): string | null {
  if (!revised) return null;
  const parts = /^(\d{4})-(\d{2})-(\d{2})$/.exec(revised);
  if (!parts) return null;
  const date = new Date(Number(parts[1]), Number(parts[2]) - 1, Number(parts[3]));
  if (Number.isNaN(date.getTime())) return null;
  return date.toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}
