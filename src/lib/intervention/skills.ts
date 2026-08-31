/**
 * Skill-intervention data: types + loader for the per-standard skill JSONs
 * in `web/content/skills/`.
 *
 * Two schema generations coexist:
 *   - v1 (no `schema_version`): skills derived stem-first. Renders in the
 *     legacy column view only.
 *   - v2 (`schema_version: 2`): adds a top-level `progression` (the
 *     standard-first learning arc) and per-skill resource sections
 *     (practice_problems / activities / strategy_links / teacher_moves).
 *     v2 skills get an "Open" detail page.
 *
 * All v2 fields are additive — the Python packet/diagnostic engine reads
 * the same files by key and ignores everything it doesn't know.
 */

/* eslint-disable @typescript-eslint/no-require-imports */
const skillDataAF1 = require("../../../content/skills/6.AF.1.json");
const skillDataAF2 = require("../../../content/skills/6.AF.2.json");
const skillDataAF3 = require("../../../content/skills/6.AF.3.json");
const skillDataAF4 = require("../../../content/skills/6.AF.4.json");
const skillDataAF5 = require("../../../content/skills/6.AF.5.json");
const skillDataRP1 = require("../../../content/skills/6.RP.1.json");
const skillDataRP2 = require("../../../content/skills/6.RP.2.json");
const skillDataRP3 = require("../../../content/skills/6.RP.3.json");
const skillDataRP4 = require("../../../content/skills/6.RP.4.json");
const skillDataRP5 = require("../../../content/skills/6.RP.5.json");
const skillDataNS1 = require("../../../content/skills/6.NS.1.json");
const skillDataNS2 = require("../../../content/skills/6.NS.2.json");
const skillDataNS3 = require("../../../content/skills/6.NS.3.json");
const skillDataNS4 = require("../../../content/skills/6.NS.4.json");
const skillDataNS5 = require("../../../content/skills/6.NS.5.json");
const skillDataNS6 = require("../../../content/skills/6.NS.6.json");
const skillDataNS7 = require("../../../content/skills/6.NS.7.json");
const skillDataNS8 = require("../../../content/skills/6.NS.8.json");
const skillDataGM1 = require("../../../content/skills/6.GM.1.json");
const skillDataGM2 = require("../../../content/skills/6.GM.2.json");
const skillDataGM3 = require("../../../content/skills/6.GM.3.json");
const skillDataGM4 = require("../../../content/skills/6.GM.4.json");
const skillDataDS1 = require("../../../content/skills/6.DS.1.json");
const skillDataDS2 = require("../../../content/skills/6.DS.2.json");
const skillDataDS3 = require("../../../content/skills/6.DS.3.json");
// Grade 7
const skillData7RP1 = require("../../../content/skills/7.RP.1.json");
const skillData7RP2 = require("../../../content/skills/7.RP.2.json");
const skillData7RP3 = require("../../../content/skills/7.RP.3.json");
const skillData7NS1 = require("../../../content/skills/7.NS.1.json");
const skillData7NS2 = require("../../../content/skills/7.NS.2.json");
const skillData7NS3 = require("../../../content/skills/7.NS.3.json");
const skillData7NS4 = require("../../../content/skills/7.NS.4.json");
const skillData7NS5 = require("../../../content/skills/7.NS.5.json");
const skillData7NS6 = require("../../../content/skills/7.NS.6.json");
const skillData7NS7 = require("../../../content/skills/7.NS.7.json");
const skillData7AF1 = require("../../../content/skills/7.AF.1.json");
const skillData7AF2 = require("../../../content/skills/7.AF.2.json");
const skillData7AF3 = require("../../../content/skills/7.AF.3.json");
const skillData7AF4 = require("../../../content/skills/7.AF.4.json");
const skillData7AF5 = require("../../../content/skills/7.AF.5.json");
const skillData7AF6 = require("../../../content/skills/7.AF.6.json");
const skillData7GM1 = require("../../../content/skills/7.GM.1.json");
const skillData7GM2 = require("../../../content/skills/7.GM.2.json");
const skillData7GM3 = require("../../../content/skills/7.GM.3.json");
const skillData7DSP1 = require("../../../content/skills/7.DSP.1.json");
const skillData7DSP2 = require("../../../content/skills/7.DSP.2.json");
const skillData7DSP3 = require("../../../content/skills/7.DSP.3.json");
const skillData7DSP4 = require("../../../content/skills/7.DSP.4.json");
const skillData7DSP5 = require("../../../content/skills/7.DSP.5.json");
// Grade 8
const skillData8AF1 = require("../../../content/skills/8.AF.1.json");
const skillData8AF2 = require("../../../content/skills/8.AF.2.json");
const skillData8AF3 = require("../../../content/skills/8.AF.3.json");
const skillData8AF4 = require("../../../content/skills/8.AF.4.json");
const skillData8AF5 = require("../../../content/skills/8.AF.5.json");
const skillData8AF6 = require("../../../content/skills/8.AF.6.json");
const skillData8AF7 = require("../../../content/skills/8.AF.7.json");
const skillData8AF8 = require("../../../content/skills/8.AF.8.json");
const skillData8NS1 = require("../../../content/skills/8.NS.1.json");
const skillData8NS2 = require("../../../content/skills/8.NS.2.json");
const skillData8NS3 = require("../../../content/skills/8.NS.3.json");
const skillData8NS4 = require("../../../content/skills/8.NS.4.json");
const skillData8GM1 = require("../../../content/skills/8.GM.1.json");
const skillData8GM2 = require("../../../content/skills/8.GM.2.json");
const skillData8GM3 = require("../../../content/skills/8.GM.3.json");
const skillData8DSP1 = require("../../../content/skills/8.DSP.1.json");
const skillData8DSP2 = require("../../../content/skills/8.DSP.2.json");
const skillData8DSP3 = require("../../../content/skills/8.DSP.3.json");
const skillData8DSP4 = require("../../../content/skills/8.DSP.4.json");
const skillData8DSP5 = require("../../../content/skills/8.DSP.5.json");
/* eslint-enable @typescript-eslint/no-require-imports */

export type SkillColumn =
  | "foundation"
  | "looking_back"
  | "on_grade"
  | "looking_forward";

export interface PracticeProblem {
  difficulty: "warm_up" | "core" | "stretch";
  stem: string;
  answer: string;
  notes?: string;
  /** Conceptual item types (v3): "error_analysis" shows flawed work to
   *  find and fix; "number_line" carries render_data for placement. */
  type?: "error_analysis" | "number_line";
  shown_work?: string[];
  render_data?: Record<string, unknown>;
}

export interface ActivityContent {
  categories?: string[];
  cards?: Array<{ text: string; category: string }>;
  pairs?: Array<{ left: string; right: string }>;
  decoys?: string[];
  triples?: Array<{ phrase: string; notation: string; expanded: string }>;
  worked_problem?: string;
  error_step?: string;
  why?: string;
}

export interface Activity {
  type: "card_sort" | "error_analysis" | "matching" | "hands_on" | "game";
  title: string;
  time_minutes: number;
  grouping: "pairs" | "small_group" | "individual" | "whole_class";
  materials: string[];
  instructions: string;
  content?: ActivityContent;
}

export interface StrategyLink {
  strategy_id: string;
  why: string;
}

export interface TeacherMoves {
  questioning_prompts: string[];
  misconception_redirects: Array<{
    if_you_see: string;
    say: string;
    praise: string;
  }>;
  quick_checks: Array<{ prompt: string; look_for: string }>;
}

/** The closed menu of session-sheet micro-check moves (schema v4).
 *  Mirrors THINKING_MOVES in engine/generate_skill_packet.py and the
 *  glossary in authoring/directives/skill_authoring/thinking_moves.md. */
export type ThinkingMove =
  | "spot_signal"
  | "show_it"
  | "call_it"
  | "say_why"
  | "check_it"
  | "name_trap";

export const THINKING_MOVE_LABELS: Record<ThinkingMove, string> = {
  spot_signal: "Spot the Signal",
  show_it: "Show It",
  call_it: "Call It",
  say_why: "Say Why",
  check_it: "Check It",
  name_trap: "Name the Trap",
};

/** A 5-second student action attached to a worked-solution step (v4). */
export interface MicroCheck {
  move: ThinkingMove;
  prompt: string;
  /** Teacher key — prints only in the companion. */
  answer: string;
}

export interface WorkedStep {
  /** null on faded/guided blank steps the student fills in. */
  math: string | null;
  annotation?: string;
  /** faded_example / guided_example only: given steps print, others blank. */
  given?: boolean;
  /** worked_solution only (v4). */
  check?: MicroCheck;
}

export interface WorkedSolution {
  stem: string;
  answer: string;
  steps: WorkedStep[];
  render_data?: Record<string, unknown>;
}

/** The four ILEARN proficiency bands. These are performance levels on the
 *  standard in front of you, NOT lower-grade content: a skill tagged
 *  "below" is grade-level work at its least complex entry point. */
export type PldBand = "below" | "approaching" | "at" | "above";

export const PLD_BAND_LABELS: Record<PldBand, string> = {
  below: "Below Proficiency",
  approaching: "Approaching Proficiency",
  at: "At Proficiency",
  above: "Above Proficiency",
};

/** Ladder order, used to group the On Grade column. */
export const PLD_BAND_ORDER: PldBand[] = ["below", "approaching", "at", "above"];

export interface Skill {
  skill_id: string;
  name: string;
  column: SkillColumn;
  /** Which proficiency band this skill answers. On-grade and
   *  looking-forward skills carry it; foundation and looking-back do not,
   *  because those are below-grade prerequisites rather than bands. */
  pld_band?: PldBand;
  canonical_error?: { pattern: string; example: string; why?: string };
  i_do_script?: string;
  redirect_script?: { stop: string; prompt: string; praise: string };
  sample_items: Array<{ stem: string; answer: string; choices?: string[] | null }>;
  engine_stems?: number[];
  printable_artifact?: { title?: string; kind?: string };
  vocabulary?: Array<{ term: string; definition: string }>;
  next_steps?: { if_pass: string; if_fail: string };
  // v2 resource sections (optional — absent on v1 skills)
  practice_problems?: PracticeProblem[];
  activities?: Activity[];
  strategy_links?: StrategyLink[];
  teacher_moves?: TeacherMoves;
  // v3 session-sheet fields (optional — absent on Foundation skills)
  worked_solution?: WorkedSolution;
  faded_example?: WorkedSolution;
  sentence_starters?: string[];
  fluency_source?: string;
  // v4 backward-fade middle rung ("Let's try together" as a faded problem)
  guided_example?: WorkedSolution;
}

export interface ProgressionStep {
  skill_id: string;
  verb?: string;
  rationale: string;
}

export interface PldDescriptors {
  /** "refreshed" = the 2026-08 spec rewrite; "prior" = not yet rewritten. */
  source: "refreshed" | "prior";
  note: string;
  below: string;
  approaching: string;
  at: string;
  above: string;
}

export interface SkillData {
  standard_code: string;
  standard_text: string;
  schema_version?: number;
  progression?: { narrative: string; steps: ProgressionStep[] };
  skills: Skill[];
  skill_columns: Partial<
    Record<SkillColumn, { label: string; description: string; skills: string[] }>
  >;
  /** The four band statements, verbatim from the item specification. */
  pld_descriptors?: PldDescriptors;
}

export const AVAILABLE_STANDARDS: Record<string, SkillData> = {
  "6.AF.1": skillDataAF1 as unknown as SkillData,
  "6.AF.2": skillDataAF2 as unknown as SkillData,
  "6.AF.3": skillDataAF3 as unknown as SkillData,
  "6.AF.4": skillDataAF4 as unknown as SkillData,
  "6.AF.5": skillDataAF5 as unknown as SkillData,
  "6.RP.1": skillDataRP1 as unknown as SkillData,
  "6.RP.2": skillDataRP2 as unknown as SkillData,
  "6.RP.3": skillDataRP3 as unknown as SkillData,
  "6.RP.4": skillDataRP4 as unknown as SkillData,
  "6.RP.5": skillDataRP5 as unknown as SkillData,
  "6.NS.1": skillDataNS1 as unknown as SkillData,
  "6.NS.2": skillDataNS2 as unknown as SkillData,
  "6.NS.3": skillDataNS3 as unknown as SkillData,
  "6.NS.4": skillDataNS4 as unknown as SkillData,
  "6.NS.5": skillDataNS5 as unknown as SkillData,
  "6.NS.6": skillDataNS6 as unknown as SkillData,
  "6.NS.7": skillDataNS7 as unknown as SkillData,
  "6.NS.8": skillDataNS8 as unknown as SkillData,
  "6.GM.1": skillDataGM1 as unknown as SkillData,
  "6.GM.2": skillDataGM2 as unknown as SkillData,
  "6.GM.3": skillDataGM3 as unknown as SkillData,
  "6.GM.4": skillDataGM4 as unknown as SkillData,
  "6.DS.1": skillDataDS1 as unknown as SkillData,
  "6.DS.2": skillDataDS2 as unknown as SkillData,
  "6.DS.3": skillDataDS3 as unknown as SkillData,
  // Grade 7
  "7.RP.1": skillData7RP1 as unknown as SkillData,
  "7.RP.2": skillData7RP2 as unknown as SkillData,
  "7.RP.3": skillData7RP3 as unknown as SkillData,
  "7.NS.1": skillData7NS1 as unknown as SkillData,
  "7.NS.2": skillData7NS2 as unknown as SkillData,
  "7.NS.3": skillData7NS3 as unknown as SkillData,
  "7.NS.4": skillData7NS4 as unknown as SkillData,
  "7.NS.5": skillData7NS5 as unknown as SkillData,
  "7.NS.6": skillData7NS6 as unknown as SkillData,
  "7.NS.7": skillData7NS7 as unknown as SkillData,
  "7.AF.1": skillData7AF1 as unknown as SkillData,
  "7.AF.2": skillData7AF2 as unknown as SkillData,
  "7.AF.3": skillData7AF3 as unknown as SkillData,
  "7.AF.4": skillData7AF4 as unknown as SkillData,
  "7.AF.5": skillData7AF5 as unknown as SkillData,
  "7.AF.6": skillData7AF6 as unknown as SkillData,
  "7.GM.1": skillData7GM1 as unknown as SkillData,
  "7.GM.2": skillData7GM2 as unknown as SkillData,
  "7.GM.3": skillData7GM3 as unknown as SkillData,
  "7.DSP.1": skillData7DSP1 as unknown as SkillData,
  "7.DSP.2": skillData7DSP2 as unknown as SkillData,
  "7.DSP.3": skillData7DSP3 as unknown as SkillData,
  "7.DSP.4": skillData7DSP4 as unknown as SkillData,
  "7.DSP.5": skillData7DSP5 as unknown as SkillData,
  // Grade 8
  "8.AF.1": skillData8AF1 as unknown as SkillData,
  "8.AF.2": skillData8AF2 as unknown as SkillData,
  "8.AF.3": skillData8AF3 as unknown as SkillData,
  "8.AF.4": skillData8AF4 as unknown as SkillData,
  "8.AF.5": skillData8AF5 as unknown as SkillData,
  "8.AF.6": skillData8AF6 as unknown as SkillData,
  "8.AF.7": skillData8AF7 as unknown as SkillData,
  "8.AF.8": skillData8AF8 as unknown as SkillData,
  "8.NS.1": skillData8NS1 as unknown as SkillData,
  "8.NS.2": skillData8NS2 as unknown as SkillData,
  "8.NS.3": skillData8NS3 as unknown as SkillData,
  "8.NS.4": skillData8NS4 as unknown as SkillData,
  "8.GM.1": skillData8GM1 as unknown as SkillData,
  "8.GM.2": skillData8GM2 as unknown as SkillData,
  "8.GM.3": skillData8GM3 as unknown as SkillData,
  "8.DSP.1": skillData8DSP1 as unknown as SkillData,
  "8.DSP.2": skillData8DSP2 as unknown as SkillData,
  "8.DSP.3": skillData8DSP3 as unknown as SkillData,
  "8.DSP.4": skillData8DSP4 as unknown as SkillData,
  "8.DSP.5": skillData8DSP5 as unknown as SkillData,
};

export function isV2(data: SkillData): boolean {
  return (data.schema_version ?? 1) >= 2;
}

/** Progression order (1-based) for a skill within its standard, or null
 *  for v1 data / foundation skills that aren't progression steps. */
export function progressionIndex(data: SkillData, skillId: string): number | null {
  const idx = data.progression?.steps.findIndex((s) => s.skill_id === skillId) ?? -1;
  return idx >= 0 ? idx + 1 : null;
}

export function progressionStep(
  data: SkillData,
  skillId: string
): ProgressionStep | undefined {
  return data.progression?.steps.find((s) => s.skill_id === skillId);
}

const MIN_AUTHORED_FOR_PACKET = 4;

/** A packet needs enough items to fill Worked Example + Try It + We Do +
 *  You Do + Exit Ticket: either ≥4 authored sample_items or an engine_stems
 *  mapping the Python engine can fill from. */
export function isPacketReady(skill: Skill): boolean {
  return (
    (skill.sample_items?.length ?? 0) >= MIN_AUTHORED_FOR_PACKET ||
    (Array.isArray(skill.engine_stems) && skill.engine_stems.length > 0)
  );
}

/** The part of a skill id that varies within a standard: "6NS1-S3" -> "S3".
 *  Every id in the corpus is exactly "<standard><tag>", one dash, so the tag
 *  is whatever follows it. This is what a card wears so a teacher can find
 *  the skill the teacher companion's NEXT STEPS box names. */
export function shortSkillTag(skillId: string): string {
  const dash = skillId.indexOf("-");
  return dash === -1 ? skillId : skillId.slice(dash + 1);
}

/** Skill ids referenced by a next_steps branch.
 *
 *  Two thirds of the corpus stores a bare id ("6NS1-F2"); the rest stores a
 *  sentence that mentions one or more ids ("Drop to 6NS1-F2 and drill single
 *  direction words"). Both need to become findable tags, so match ids
 *  anywhere in the string rather than testing the whole value. Roughly a
 *  third of prose branches name no skill at all (they say "reteach this" or
 *  describe an off-ladder review) — those correctly yield []. */
const SKILL_ID_RE = /\b\d[A-Z]{1,3}\d+-[A-Z]\d+\b/g;

export function nextStepRefs(branch: string | undefined): string[] {
  if (!branch) return [];
  const seen = new Set<string>(branch.match(SKILL_ID_RE) ?? []);
  return [...seen];
}

export interface FoundSkill {
  skill: Skill;
  data: SkillData;
}

export function findSkillById(skillId: string): FoundSkill | null {
  for (const data of Object.values(AVAILABLE_STANDARDS)) {
    const skill = data.skills.find((s) => s.skill_id === skillId);
    if (skill) return { skill, data };
  }
  return null;
}

// ── Display metadata ────────────────────────────────────────────────────

/** The four buckets in progression order, weakest prerequisite first.
 *  This is the canonical DATA order; the intervention page arranges them
 *  differently on screen (On Grade leads, Foundation closes) because
 *  reading priority and progression order are not the same thing. */
export const BUCKET_ORDER = [
  "foundation",
  "looking_back",
  "on_grade",
  "looking_forward",
] as const;

/** Brand-token accents per column (design.md: no off-palette hex). */
export const COLUMN_META: Record<
  SkillColumn,
  { label: string; accent: string; badgeTone: "yellow" | "blue" | "emerald" | "red" }
> = {
  foundation: { label: "Foundation", accent: "var(--pnp-red)", badgeTone: "red" },
  looking_back: { label: "Looking Back", accent: "var(--pnp-yellow-dark)", badgeTone: "yellow" },
  on_grade: { label: "On Grade", accent: "var(--pnp-blue)", badgeTone: "blue" },
  looking_forward: { label: "Looking Forward", accent: "var(--pnp-green)", badgeTone: "emerald" },
};

export const ACTIVITY_TYPE_LABELS: Record<Activity["type"], string> = {
  card_sort: "Card sort",
  error_analysis: "Error analysis",
  matching: "Matching",
  hands_on: "Hands-on",
  game: "Game",
};

export const GROUPING_LABELS: Record<Activity["grouping"], string> = {
  pairs: "Pairs",
  small_group: "Small group",
  individual: "Individual",
  whole_class: "Whole class",
};

export const DIFFICULTY_META: Record<
  PracticeProblem["difficulty"],
  { label: string; tone: "emerald" | "blue" | "orange" }
> = {
  warm_up: { label: "Warm-up", tone: "emerald" },
  core: { label: "Core", tone: "blue" },
  stretch: { label: "Stretch", tone: "orange" },
};
