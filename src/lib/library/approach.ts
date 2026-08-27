import fs from "fs";
import path from "path";

/**
 * "Our teaching approach" — the pedagogical framework hub under /math/approach.
 *
 * Every detail page (a tool, a strand, a practice) is stored
 * as a JSON file of typed content blocks under content/approach/pages, and
 * rendered by a shared block renderer (components/approach). The hub landing
 * page and its cross-links are driven by the manifests at the bottom of this
 * file. Icons are inline SVG only (emojiless) — see components/approach/icons.
 */

// ─── Content block model ────────────────────────────────────────────────
// Inline text in any `text` / `items[]` / table cell supports a tiny, safe
// markdown subset parsed by renderInline(): **bold**, *italic*, `code`, and
// [label](/href) links. No raw HTML.

export type Block =
  | { type: "lead"; text: string }
  | { type: "heading"; text: string }
  | { type: "subheading"; text: string }
  | { type: "paragraph"; text: string; muted?: boolean }
  | { type: "list"; ordered?: boolean; items: string[] }
  | { type: "steps"; items: string[] }
  | {
      type: "callout";
      variant: "vision" | "equity" | "watch" | "tip";
      title: string;
      blocks: Block[];
    }
  | {
      type: "doDont";
      yes: { title: string; items: string[] };
      no: { title: string; items: string[] };
    }
  | { type: "table"; headers: string[]; rows: string[][] }
  | {
      type: "tags";
      label?: string;
      variant?: "strand" | "practice";
      items: string[];
    };

export type ApproachSection = {
  /** Big divider label — tools carry two ("What it is" / "Lesson design
   *  connection"); strands and practices omit it. */
  label?: string;
  /** Source attribution shown at the foot of the section. */
  sources?: string;
  blocks: Block[];
};

export type ApproachKind = "tool" | "strand" | "practice";

export type ApproachPage = {
  slug: string;
  kind: ApproachKind;
  /** Small eyebrow above the title, e.g. "Mathematics toolbelt". */
  doctype: string;
  title: string;
  subtitle: string;
  /** Metadata chips (grade band, time, focus). */
  chips?: string[];
  sections: ApproachSection[];
};

// ─── Loader ─────────────────────────────────────────────────────────────

const PAGES_DIR = path.join(process.cwd(), "content", "approach", "pages");

export function getAllApproachPages(): ApproachPage[] {
  if (!fs.existsSync(PAGES_DIR)) return [];
  return fs
    .readdirSync(PAGES_DIR)
    .filter((f) => f.endsWith(".json"))
    .map(
      (f) =>
        JSON.parse(fs.readFileSync(path.join(PAGES_DIR, f), "utf-8")) as ApproachPage
    );
}

export function getApproachPage(slug: string): ApproachPage | undefined {
  const file = path.join(PAGES_DIR, `${slug}.json`);
  if (!fs.existsSync(file)) return undefined;
  return JSON.parse(fs.readFileSync(file, "utf-8")) as ApproachPage;
}

// ─── Hub manifest ───────────────────────────────────────────────────────
// Presentation concerns (grouping, ordering, card blurbs, icon + accent)
// live here so the JSON content files stay pure content. Accents are brand
// tokens only (see globals.css / BRAND_CYCLE).

export type ToolGroupId =
  | "opener"
  | "core"
  | "practice"
  | "embedded";

export const TOOL_GROUPS: {
  id: ToolGroupId;
  title: string;
  note: string;
  accent: string;
}[] = [
  {
    id: "opener",
    title: "Opener routines",
    note: "Choose by purpose. The discourse-rich way to use your opener, not a silent worksheet.",
    accent: "#0d9488", // teal-600
  },
  {
    id: "core",
    title: "Core instruction",
    note: "“Task before tell”: students reason through a task before we formalize it.",
    accent: "#3f42d9", // blue
  },
  {
    id: "practice",
    title: "Practice & closure",
    note: "Consolidating learning and knowing it landed.",
    accent: "#22c55e", // green
  },
  {
    id: "embedded",
    title: "Embedded moves",
    note: "The how, not the what. You don’t choose between these; you layer them onto whatever activity you run.",
    accent: "#f97316", // orange
  },
];

export type ToolCard = {
  slug: string;
  title: string;
  blurb: string;
  group: ToolGroupId;
  /** Icon key — see components/approach/icons.tsx (emojiless inline SVG). */
  icon: string;
};

export const TOOLS: ToolCard[] = [
  // ── Opener routines ──
  {
    slug: "number-talks",
    title: "Number Talks & Number Strings",
    blurb:
      "A short, daily mental-math discussion where students share and defend strategies: one rich problem, or a sequenced string that nudges toward a target strategy. The anchor routine for fluency from understanding.",
    group: "opener",
    icon: "talk",
  },
  {
    slug: "number-strings",
    title: "Number Strings",
    blurb:
      "A tightly sequenced set of related problems, posed one at a time, where each helper gives a foothold for the next and drives students toward one target strategy.",
    group: "opener",
    icon: "string",
  },
  {
    slug: "same-but-different",
    title: "Same But Different & WODB",
    blurb:
      "Two comparison routines: compare a pair (“same / different”) or a set of four (“which doesn’t belong?”). Both build precise language and mathematical argument.",
    group: "opener",
    icon: "compare",
  },
  {
    slug: "quick-images",
    title: "Quick Images",
    blurb:
      "Flash a visual for a few seconds, then ask “how many, and how did you see it?” Builds subitizing, structure, and multiple ways of seeing a quantity.",
    group: "opener",
    icon: "image",
  },
  {
    slug: "would-you-rather",
    title: "Would You Rather / Estimation",
    blurb:
      "A low-floor reasoning hook: two options, pick one, and justify with mathematics. Every student has an entry point and an opinion to defend.",
    group: "opener",
    icon: "branch",
  },
  {
    slug: "spiral-review",
    title: "Spiral / Retrieval Review",
    blurb:
      "Distributed practice that revisits older content on purpose, so learning sticks. The opener when your goal is to keep prior skills alive.",
    group: "opener",
    icon: "refresh",
  },
  {
    slug: "error-analysis",
    title: "Error Analysis",
    blurb:
      "Students analyze a wrong (or partly right) solution to find and fix the reasoning, turning misconceptions into the object of study.",
    group: "opener",
    icon: "search",
  },
  // ── Core instruction ──
  {
    slug: "rich-tasks",
    title: "Rich Tasks / Three-Act Math",
    blurb:
      "The centerpiece of core instruction: a compelling, low-floor/high-ceiling task students reason through, then consolidate into formal mathematics.",
    group: "core",
    icon: "task",
  },
  {
    slug: "thin-slicing",
    title: "Thin-Slicing",
    blurb:
      "A sequence of tasks that vary in small increments so students notice patterns and extend their own thinking at the whiteboards. A core “task before tell” move.",
    group: "core",
    icon: "slice",
  },
  {
    slug: "responsive-di",
    title: "Responsive Direct Instruction & Teacher Clarity",
    blurb:
      "Brief, well-timed explicit teaching embedded in core: modeling, naming, and formalizing. The consolidation is the key “tell,” landing when students are primed.",
    group: "core",
    icon: "teach",
  },
  // ── Practice & closure ──
  {
    slug: "fluency-practice",
    title: "Fluency Practice (with monitoring)",
    blurb:
      "Volume reps that build fluency. Every student shows work on paper while the teacher circulates, sees where reasoning breaks, and responds in the moment.",
    group: "practice",
    icon: "pencil",
  },
  {
    slug: "cfu-exit-tickets",
    title: "Check-for-Understanding & Exit Tickets",
    blurb:
      "Short, purposeful practice and a closing prompt that surfaces evidence of student thinking to inform the next lesson.",
    group: "practice",
    icon: "check",
  },
  // ── Embedded moves ──
  {
    slug: "talk-moves",
    title: "Talk Moves",
    blurb:
      "The discourse glue: revoicing, turn-and-talk, “who can add on,” and wait time that make every routine a real conversation.",
    group: "embedded",
    icon: "chat",
  },
  {
    slug: "when-to-tell",
    title: "When to Tell: Decision Guide",
    blurb:
      "The teacher’s judgment for inquiry vs. explicit teaching: don’t tell what students can figure out; do tell conventions and notation, or formalize once they’ve struggled enough.",
    group: "embedded",
    icon: "compass",
  },
  {
    slug: "access-equity",
    title: "Access & Equity Lens",
    blurb:
      "How every tool supports multilingual learners, students with IEPs/504s, and culturally responsive practice. Woven into each tool page, gathered here too.",
    group: "embedded",
    icon: "hands",
  },
  {
    slug: "vnps",
    title: "Vertical Surfaces & Random Groups",
    blurb:
      "Students think at whiteboards in visibly random groups: more starts, more mobility of ideas, less hiding. The structure that powers task work.",
    group: "embedded",
    icon: "board",
  },
  {
    slug: "five-practices",
    title: "The 5 Practices",
    blurb:
      "Anticipate, monitor, select, sequence, connect: how the teacher orchestrates any task discussion so student thinking adds up to the mathematics.",
    group: "embedded",
    icon: "target",
  },
  {
    slug: "connecting-representations",
    title: "Connecting Representations",
    blurb:
      "Linking tables, graphs, equations, and diagrams so students see one idea in many forms. The habit that makes any consolidation deep.",
    group: "embedded",
    icon: "chart",
  },
];

export const STRANDS: { slug: string; title: string; gist: string }[] = [
  {
    slug: "strand-conceptual-understanding",
    title: "Conceptual understanding",
    gist: "knowing why",
  },
  {
    slug: "strand-procedural-fluency",
    title: "Procedural fluency",
    gist: "flexible, accurate, efficient",
  },
  {
    slug: "strand-strategic-competence",
    title: "Strategic competence",
    gist: "formulating & solving problems",
  },
  {
    slug: "strand-adaptive-reasoning",
    title: "Adaptive reasoning",
    gist: "justifying & explaining",
  },
  {
    slug: "strand-productive-disposition",
    title: "Productive disposition",
    gist: "seeing math as sensible & oneself as capable",
  },
];

export const PRACTICES: { slug: string; n: number; title: string }[] = [
  { slug: "practice-1-establish-goals", n: 1, title: "Establish mathematics goals to focus learning" },
  { slug: "practice-2-reasoning-tasks", n: 2, title: "Implement tasks that promote reasoning & problem solving" },
  { slug: "practice-3-representations", n: 3, title: "Use and connect mathematical representations" },
  { slug: "practice-4-discourse", n: 4, title: "Facilitate meaningful mathematical discourse" },
  { slug: "practice-5-purposeful-questions", n: 5, title: "Pose purposeful questions" },
  { slug: "practice-6-fluency-from-understanding", n: 6, title: "Build procedural fluency from conceptual understanding" },
  { slug: "practice-7-productive-struggle", n: 7, title: "Support productive struggle in learning mathematics" },
  { slug: "practice-8-evidence-of-thinking", n: 8, title: "Elicit and use evidence of student thinking" },
];

export function toolAccent(group: ToolGroupId): string {
  return TOOL_GROUPS.find((g) => g.id === group)?.accent ?? "#0d9488";
}
