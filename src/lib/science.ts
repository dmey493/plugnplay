/**
 * Biology stimulus bank: types + loader for the ILEARN HS-LS phenomenon
 * clusters in `web/content/science/biology.json` (3 stimuli per standard,
 * grouped into the four HS-LS domains).
 */

/* eslint-disable @typescript-eslint/no-require-imports */
const biologyData = require("../../content/science/biology.json");
/* eslint-enable @typescript-eslint/no-require-imports */

export interface ChartSeries {
  name: string;
  values: number[];
}

export interface Figure {
  kind: "chart" | "table" | "image" | "none";
  caption?: string;
  // chart
  chart_type?: "bar" | "grouped_bar" | "line" | "scatter";
  title?: string;
  xlabel?: string;
  ylabel?: string;
  x?: Array<string | number>;
  series?: ChartSeries[];
  ymax?: number;
  source?: string;
  // table
  columns?: string[];
  rows?: string[][];
  // image
  file?: string;
}

export type QuestionKind =
  | "mc" | "ms" | "seq" | "dropdown" | "match" | "hottext" | "tf";

export interface Question {
  kind: QuestionKind;
  stem: string;
  rationale?: string;
  td?: number;
  // mc / ms
  options?: string[];
  correct?: number | number[] | string[] | string;
  // seq
  items?: string[];
  order?: number[];
  // dropdown
  dd?: Array<[string, string]>;
  // match
  left?: string;
  right?: string;
  rows?: string[];
  optset?: string;
}

export interface Stimulus {
  title: string;
  phenomenon: string;
  figure?: Figure;
  questions: Question[];
}

export interface ScienceStandard {
  pe: string;
  domain: string;
  pe_text: string;
  stimuli: Stimulus[];
}

export interface Domain {
  code: string;
  title: string;
  blurb: string;
}

interface BiologyData {
  domains: Domain[];
  standards: ScienceStandard[];
}

const DATA = biologyData as unknown as BiologyData;

export const DOMAINS: Domain[] = DATA.domains;
export const STANDARDS: ScienceStandard[] = DATA.standards;

/** Per-domain accent from the brand cycle (no off-palette hex per design.md). */
export const DOMAIN_ACCENT: Record<string, string> = {
  "HS-LS1": "var(--pnp-blue)",
  "HS-LS2": "var(--pnp-green)",
  "HS-LS3": "var(--pnp-orange)",
  "HS-LS4": "var(--pnp-accent)",
};

export function standardsByDomain(code: string): ScienceStandard[] {
  return STANDARDS.filter((s) => s.domain === code);
}

export function getStandard(pe: string): ScienceStandard | undefined {
  return STANDARDS.find((s) => s.pe === pe);
}

/** Total stimulus count (used for the header count). */
export function stimulusCount(): number {
  return STANDARDS.reduce((n, s) => n + s.stimuli.length, 0);
}

const QUESTION_LABELS: Record<QuestionKind, string> = {
  mc: "Multiple choice",
  ms: "Select all",
  seq: "Sequencing",
  dropdown: "Drop-down",
  match: "Matching",
  hottext: "Hot text",
  tf: "True / False",
};

export function questionLabel(kind: QuestionKind): string {
  return QUESTION_LABELS[kind] ?? kind;
}
