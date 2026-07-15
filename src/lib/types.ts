export interface ContentEnvelope {
  id: string;
  type: string;
  scope: "lesson" | "component";
  version: number;
  title: string;
  subjects: string[];
  gradeBand: string;
  grades: number[];
  standards: {
    indiana: string[];
    commonCore: string[];
    ngss: string[];
  };
  mtssTiers: number[];
  purposes: string[];
  time: {
    estimatedMinutes: number;
    minMinutes: number;
    maxMinutes: number;
  };
  tags: string[];
  preview: string;
  body: StrategyBody | TaskBody | ThinSliceBody | Record<string, unknown>;
  authoring: {
    generatedBy: string;
    generatedAt: string;
    reviewedBy: string | null;
  };
}

export interface StrategyBody {
  summary: string;
  whenToUse: string;
  howToImplement: string;
  teacherMoves: string;
  variations: string;
  researchBase: string;
}

export interface FilterState {
  subjects: string[];
  grades: number[];
  purposes: string[];
  mtssTiers: number[];
  search: string;
}

// =====================
// Rich Tasks (Phase 1)
// =====================

export type TaskType =
  | "anchor"
  | "investigation"
  | "three-act"
  | "warmup"
  | "performance"
  | "problem-set";

export interface TaskSource {
  name: string;          // e.g. "Illustrative Mathematics 6-8 (Open Up Resources)"
  license: string;       // e.g. "CC BY 4.0"
  url: string;           // canonical link to the original
  attribution: string;   // full attribution string to display on the task page
}

/**
 * Identifiers for built-in interactive image components. When TaskImage.kind
 * is "interactive", `component` selects which one to render.
 */
export type InteractiveImageComponent = "rubiks-cube";

/**
 * An optional task image. Three modes, in order of preference:
 *   - `kind: "interactive"` with a built-in component (e.g. 3D Rubik's cube)
 *   - inline SVG markup (`svg`) — best for static figures
 *   - external URL (`url`) — fallback for hosted images
 * `alt` is required for accessibility.
 * `credit` is shown below external URL images.
 */
export interface TaskImage {
  /** Selects the rendering mode. Defaults to inline SVG / URL. */
  kind?: "svg" | "url" | "interactive";
  /** Used when kind === "interactive" — picks the built-in component. */
  component?: InteractiveImageComponent;
  svg?: string;        // inline SVG markup, e.g. "<svg ...>...</svg>"
  url?: string;        // external image URL (use with credit)
  alt: string;         // alt text describing the image
  credit?: string;     // attribution shown for external URL images
}

export interface TaskBody {
  goal: string;                       // 1-sentence teacher-facing mathematical goal
  studentPrompt: string;              // exact text/instructions for students (print-ready)
  image?: TaskImage;                  // optional visual aid for the task
  launch?: string;                    // teacher's brief intro / setup script
  materials?: string[];               // list (whiteboards, manipulatives, handouts)
  concepts: string[];                 // free-text concept tags
  taskType: TaskType;
  btcFit?: string;                    // BTC fit note (e.g., "Strong day-1 non-curricular task")
  anticipatedApproaches?: string;     // markdown-friendly text
  commonMisconceptions?: string;
  discussionQuestions?: string;
  extensions?: string;
  sampleSolutions?: string;
  source: TaskSource;
  thinSliceSequence?: {
    sequenceId: string;
    position: number;
    prevTaskId?: string;
    nextTaskId?: string;
  };
}

/**
 * The umbrella categorisation surfaced in the unified Lessons library.
 * Every envelope rendered by the library is either a rich task or a thin
 * slice — the underlying body's narrower `taskType` ("anchor",
 * "investigation", etc.) stays in the JSON for authoring history but is
 * no longer surfaced in the UI per Dave's "combine things" direction.
 */
export type LessonFormat = "rich-task" | "thin-slice";

export interface TaskFilterState {
  grades: number[];
  /** Rich-task vs thin-slice filter. Empty array = show both. */
  formats: LessonFormat[];
  durationBuckets: DurationBucket[];
  concepts: string[];
  standards: string[];
  search: string;
}

export type DurationBucket = "short" | "medium" | "long";
// short  = <= 15 min
// medium = 16-30 min
// long   = > 30 min

export type BrowseMode = "unit" | "standard" | "concept";

// =====================
// Units (Fishtank-style Unit → Section → Tasks browse)
// =====================
//
// One JSON file per unit at `web/content/units/<subject>/`. The PPT module
// numbering is the source of truth — Grade 8 has modules 1, 2, 3, 4, 5, 6,
// 7, 9, 10 (no 8). Each module breaks into sections (the in-book sub-units
// like 1-1, 1-2, 1-3). A section owns a list of task IDs, and the SAME task
// can appear in multiple sections / units — the unit JSON is the canonical
// home of the mapping (tasks themselves don't carry unit metadata, so we
// never have to re-author 80+ task files).

/** A warm-up routine (WODB set or Number Talk) assigned to a lesson. */
export interface WarmupRef {
  kind: "wodb" | "talk";
  /** Set/talk id within its grade file. */
  id: string;
  grade: number;
  /** Denormalized title for the lesson chip (link is id-based). */
  title: string;
}

export interface UnitSection {
  /** Stable slug for in-page nav + analytics. e.g. "1-1-multiplication-properties". */
  id: string;
  /** Human display label. e.g. "1-1 Multiplication Properties of Exponents". */
  label: string;
  /** Optional 1-line teacher framing for the section. */
  description?: string;
  /** Ordered list of rich-task IDs that belong to this section. */
  taskIds: string[];
  /** Optional ordered list of thin-slice IDs that fit this section's
   *  objective. Rendered as a secondary strip below the task grid on the
   *  unit detail page. Same ID can appear in multiple sections. */
  thinSliceIds?: string[];
  /** Optional Indiana standard code for this section (e.g. "7.NS.1"). When
   *  present, the unit detail page surfaces a "Generate CFU →" button that
   *  deep-links to the Problem Generator with this standard pre-selected.
   *  Section labels still carry the textbook reference; this is just the
   *  hook for the engine integration. */
  standard?: string;
  /** Optional skill_ids within `standard`'s progression that this lesson's
   *  objective targets. The intervention page highlights these specific
   *  skills when a teacher opens it from this lesson. Every id must exist in
   *  that standard's skill file (e.g. "8NS3-S2"). */
  skillIds?: string[];
  /** Warm-up routine(s) assigned to THIS lesson (one per lesson — each
   *  WODB set / Number Talk belongs to a single lesson, never repeated).
   *  Rendered as the "Warm-up" strip above the lesson's tasks. */
  warmupRefs?: WarmupRef[];
  /** Optional Fluency Practice topic ID (e.g. "add-integers", "eq-two-pos").
   *  When present, the unit detail page surfaces a "Fluency Practice →"
   *  button that deep-links to /math/fluency?topic=<id> with that skill
   *  pre-selected. Only sections with a clean drill match carry this —
   *  conceptual sections (e.g. "Apply rational numbers") are left blank. */
  fluencyTopic?: string;
}

export interface UnitFile {
  /** "grade-8-module-1". Also the URL slug. */
  id: string;
  grade: 6 | 7 | 8;
  /** Matches the source PPT module numbering. May skip (e.g. grade 8 has no 8). */
  moduleNumber: number;
  /** Order this unit is taught within the grade. When present, used by the
   *  landing-page sort so the grid follows the scope-and-sequence calendar
   *  instead of plain module numbering. Modules are not always taught in
   *  numerical order (e.g. grade 7 teaches Module 3 first). When absent,
   *  the loader falls back to `moduleNumber`. */
  teachingOrder?: number;
  /** "Exponents and Scientific Notation" */
  title: string;
  /** Short hook for the unit-tile card on `/math/units`. */
  preview: string;
  /** Optional teacher framing for the unit detail banner — longer than preview. */
  description?: string;
  /** Optional estimated days the unit takes to teach. */
  estimatedDays?: number;
  /** Sections in the order the curriculum teaches them. */
  sections: UnitSection[];
  /** Source attribution for the unit organisation (NOT the tasks). */
  source: {
    name: string;
    license: string;
    attribution: string;
  };
}

// =====================
// Thin Slices (BTC)
// =====================

/**
 * Built-in geometric shapes a thin-slice step can render. The labels object on
 * each step provides the per-step values; the shape itself is fixed for the
 * whole slice (declared on ThinSliceBody.shape).
 */
export type ThinSliceShape =
  | { kind: "cylinder" }       // labels: { r, h }
  | { kind: "right-triangle" } // labels: { a, b, c }  ("?" for the unknown)
  ;

/**
 * One step in a thin-slice sequence. Each step is a tiny, self-contained problem
 * that varies only one detail from the prior step. Teachers reveal them one at a
 * time during a live whiteboard session.
 */
export interface ThinSliceStep {
  /** The problem text, exactly as students see it. Short — usually one line. */
  problem: string;
  /** Optional answer or worked solution, revealed when the teacher hits "show answer". */
  answer?: string;
  /** Optional teacher-only note for the consolidation move tied to this step. */
  teacherNote?: string;
  /** Optional inline SVG illustration for this step (same shape as TaskImage). */
  image?: TaskImage;
  /**
   * Per-step labels for the slice's declared shape. E.g., for a cylinder slice:
   * { r: "2", h: "5" } — r and h are read by the cylinder renderer. Use "?" for
   * the unknown. Strings, not numbers, so authors can write "1/2" or "\frac{1}{2}".
   */
  labels?: Record<string, string>;
}

/**
 * The body of a `type: "thin-slice"` content envelope. A short ordered sequence
 * of micro-problems for live classroom delivery.
 */
export interface ThinSliceBody {
  /** Teacher-facing one-line goal. */
  goal: string;
  /** Brief launch script for the teacher. */
  launch?: string;
  /**
   * Optional fixed scenario shown above every step (e.g., "A pancake recipe
   * uses 3 cups of mix to make 2 servings."). Stays put as steps advance — so
   * the teacher and class don't lose the setup as the sequence progresses.
   */
  stem?: string;
  /**
   * Optional declared shape that every step in this slice illustrates. Each step
   * provides its own `labels` map filled into the shape. Keep `shape` undefined
   * for non-geometry slices (integer products, ratios, equations).
   */
  shape?: ThinSliceShape;
  /** Free-text concept tags (drives Browse-by-Concept on the thin-slice page). */
  concepts: string[];
  /**
   * Optional warm-up steps that run BEFORE the main sequence. Used to "open the
   * file cabinet" — e.g., one-step equations before a two-step thin-slice. The
   * runner shows a quick landing screen, then runs these, then runs `steps`.
   */
  prerequisiteSteps?: ThinSliceStep[];
  /** One-line description of what the prereq is rehearsing (shown on landing). */
  prerequisiteLabel?: string;
  /** Ordered main slice steps. Typically 5-10. */
  steps: ThinSliceStep[];
  /**
   * Optional enrichment steps for early finishers / extension. Treated as a
   * second group in the teacher's step picker. They run after the main steps.
   */
  enrichmentSteps?: ThinSliceStep[];
  /** Notes for whole-group discussion after the sequence. */
  consolidation?: string;
  source: TaskSource;
}

export type SubjectSlug = "math" | "science";

export interface SubjectConfig {
  slug: SubjectSlug;
  label: string;
  color: string;
  bgClass: string;
  textClass: string;
  borderClass: string;
}

// =====================
// Phone-as-remote (polling)
// =====================
//
// Shared types between the projection (`ProjectionView`), the phone
// (`/remote` route), and the in-memory room store. The protocol is
// poll-based — see plan file `validated-waddling-crab.md` for the full
// architecture. These types are pure data (JSON-serialisable) so they pass
// cleanly through the `Response.json()` API handlers.

import type { ThemeId } from "./projection-themes";

/** The projection's broadcastable state. Sent in every heartbeat and
 *  consumed by the phone on every poll. Mirrors a subset of the
 *  `ProjectionView` component state — only the fields the phone needs to
 *  reflect or display. */
export interface ProjectionState {
  /** Current task being projected. */
  taskId: string;
  /** Total questions parsed from the prompt. */
  totalQuestions: number;
  /** 1-based index of the question currently revealed. */
  revealedCount: number;
  /** Sliding-window size (how many cards visible at once). */
  windowSize: 1 | 2 | 3;
  /** Active theme. */
  themeId: ThemeId;
  /** Whether the draw overlay is engaged. */
  drawing: boolean;
  /** Timer state. Mirrors the controlled props on TimerOverlay. */
  timer: {
    visible: boolean;
    durationSec: number;
    remainingSec: number;
    running: boolean;
  };
  /** Random-groups mirror. The projection broadcasts the currently-saved
   *  assignment (or null) plus the list of saved classes, so the phone can
   *  display the groups and offer a class to form from. Optional so older
   *  state builders (and non-groups surfaces) stay valid. */
  groups?: GroupsMirror | null;
  classes?: GroupsClassSummary[];
}

/** A class the phone can form groups from — id + name + roster size. */
export interface GroupsClassSummary {
  id: string;
  name: string;
  count: number;
}

/** The projection's current group assignment, mirrored to the phone. */
export interface GroupsMirror {
  label: string;
  groups: { id: string; name: string }[][];
}

/** Commands the phone can issue. The projection's heartbeat loop drains
 *  pending commands and applies each via the matching state setter. */
export type RemoteCommand =
  | { type: "advance" }
  | { type: "retreat" }
  | { type: "set-theme"; themeId: ThemeId }
  | { type: "set-window-size"; size: 1 | 2 | 3 }
  | { type: "toggle-drawing"; on: boolean }
  | { type: "set-timer-visible"; visible: boolean }
  | { type: "timer-set-duration"; seconds: number }
  | { type: "timer-set-running"; running: boolean }
  | { type: "timer-reset" }
  // Random groups — the phone drives the projection's Groups overlay.
  | { type: "groups-open" }
  | { type: "groups-close" }
  | { type: "groups-form-class"; classId: string }
  | { type: "groups-reshuffle" }
  | { type: "groups-clear" };

/** Reference fields the phone shows in collapsible cards. Pulled from
 *  `TaskBody` and bundled at join time so the phone doesn't fetch the
 *  whole task file. */
export interface RemoteTaskBundle {
  taskId: string;
  title: string;
  intro: string;
  questions: string[];
  discussionQuestions?: string;
  anticipatedApproaches?: string;
  commonMisconceptions?: string;
  sampleSolutions?: string;
  extensions?: string;
}

/** Returned by `/api/remote/connect-projection` to the projection. */
export interface ConnectProjectionResponse {
  code: string;
  projectionToken: string;
}

/** Returned by `/api/remote/heartbeat` to the projection. */
export interface HeartbeatResponse {
  alive: boolean;
  pendingCommands: RemoteCommand[];
  phonePaired: boolean;
}

/** Returned by `/api/remote/join` to the phone. */
export interface JoinResponse {
  ok: true;
  taskBundle: RemoteTaskBundle;
  state: ProjectionState;
}

/** Returned by `/api/remote/poll` to the phone. */
export interface PollResponse {
  alive: boolean;
  state: ProjectionState | null;
  /** True if the projection has explicitly disconnected. Phone treats
   *  this as a terminal state and shows the disconnected screen. */
  ended?: boolean;
}
