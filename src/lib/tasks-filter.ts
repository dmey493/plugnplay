import type {
  ContentEnvelope,
  TaskBody,
  TaskFilterState,
  DurationBucket,
  LessonFormat,
} from "./types";

/** Map an envelope's `type` field onto the umbrella LessonFormat shown
 *  in the unified library. Anything that isn't tagged as a thin slice
 *  falls through to "rich-task" so future content types default to the
 *  primary surface rather than a separate one. */
export function formatOf(envelope: ContentEnvelope): LessonFormat {
  return envelope.type === "thin-slice" ? "thin-slice" : "rich-task";
}

/**
 * Pure client-safe helpers for the Rich Tasks library.
 * No filesystem access — safe to import from client components.
 * Server-only loaders (getAllTasks, getTaskById) live in tasks.ts.
 */

export function durationBucketFor(estimatedMinutes: number): DurationBucket {
  if (estimatedMinutes <= 15) return "short";
  if (estimatedMinutes <= 30) return "medium";
  return "long";
}

/**
 * Returns the primary standard code for display: Indiana first (we're an
 * Indiana-tagged platform), then Common Core as a cross-reference fallback.
 * Returns undefined if neither framework has any standards.
 */
export function primaryStandard(task: ContentEnvelope): string | undefined {
  return task.standards.indiana?.[0] ?? task.standards.commonCore?.[0];
}

export function filterTasks(
  tasks: ContentEnvelope[],
  filters: TaskFilterState
): ContentEnvelope[] {
  return tasks.filter((task) => {
    const body = task.body as TaskBody;

    if (
      filters.grades.length > 0 &&
      !filters.grades.some((g) => task.grades.includes(g))
    ) {
      return false;
    }

    if (
      filters.formats.length > 0 &&
      !filters.formats.includes(formatOf(task))
    ) {
      return false;
    }

    if (filters.durationBuckets.length > 0) {
      const bucket = durationBucketFor(task.time.estimatedMinutes);
      if (!filters.durationBuckets.includes(bucket)) return false;
    }

    if (filters.concepts.length > 0) {
      const taskConcepts = body.concepts ?? [];
      if (!filters.concepts.some((c) => taskConcepts.includes(c))) {
        return false;
      }
    }

    if (filters.standards.length > 0) {
      const all = [
        ...(task.standards.commonCore ?? []),
        ...(task.standards.indiana ?? []),
        ...(task.standards.ngss ?? []),
      ];
      if (!filters.standards.some((s) => all.includes(s))) return false;
    }

    if (filters.search.trim()) {
      const q = filters.search.toLowerCase();
      const haystack = [
        task.title,
        task.preview,
        body.goal,
        body.studentPrompt,
        (body.concepts ?? []).join(" "),
        (task.tags ?? []).join(" "),
      ]
        .join(" ")
        .toLowerCase();
      if (!haystack.includes(q)) return false;
    }

    return true;
  });
}

export function collectConcepts(tasks: ContentEnvelope[]): string[] {
  const set = new Set<string>();
  for (const task of tasks) {
    const body = task.body as TaskBody;
    for (const c of body.concepts ?? []) {
      set.add(c);
    }
  }
  return Array.from(set).sort();
}

export function collectStandards(
  tasks: ContentEnvelope[],
  framework: "commonCore" | "indiana" | "ngss" = "indiana"
): string[] {
  const set = new Set<string>();
  for (const task of tasks) {
    for (const s of task.standards[framework] ?? []) {
      set.add(s);
    }
  }
  return Array.from(set).sort();
}

/** Which standards system to display. Default is "indiana" (2023 IAS-M). */
export type StandardsSystem = "indiana" | "commonCore";

/**
 * Return the standards a task should DISPLAY for a given system + grade
 * context. Hides cross-graded codes (e.g., 8.NS.1 on a 7th-grade task) so
 * a teacher filtering for grade 7 doesn't see 6.x / 8.x noise.
 *
 * Effective grade context = `gradeFilter` if non-empty, else `task.grades`.
 * A code like "7.AF.1" matches grade 7 by its leading digit. Codes without a
 * leading-digit prefix (e.g., "MP.1") are always shown.
 */
export function displayStandardsFor(
  task: ContentEnvelope,
  system: StandardsSystem,
  gradeFilter: number[] = []
): string[] {
  const codes = task.standards[system] ?? [];
  const effective =
    gradeFilter.length > 0 ? gradeFilter : (task.grades ?? []);
  if (effective.length === 0) return codes;
  return codes.filter((code) => {
    const m = /^(\d+)\./.exec(code);
    if (!m) return true;
    return effective.includes(parseInt(m[1], 10));
  });
}
