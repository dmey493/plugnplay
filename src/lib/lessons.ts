import { getAllUnits } from "./units";

/**
 * Client-serializable "browse by lesson" navigation, derived from the
 * filesystem unit files. A teacher who thinks in textbook lessons
 * ("1-3 Scientific Notation") can pick a module → lesson and land on the
 * standard that lesson teaches — the same standard the by-strand view
 * selects directly.
 *
 * Server-only loader (reads unit JSON via `getAllUnits`). The RETURN SHAPE
 * is plain data, so a server component can pass it straight into a client
 * component as a prop. Client components may `import type` the types below
 * (type-only imports are erased and never pull the fs loader into the
 * bundle).
 */

/** One textbook lesson (unit section) that maps to a standard. */
export interface LessonItem {
  /** Display label, e.g. "1-3 Scientific Notation". */
  label: string;
  /** Indiana standard code the lesson teaches, e.g. "8.NS.3". */
  standard: string;
  /** skill_ids within the standard's progression this lesson targets. */
  skillIds: string[];
}

/** One module/unit grouping a run of lessons. */
export interface LessonModule {
  /** Unit id / URL slug, e.g. "grade-8-module-1". */
  id: string;
  /** Textbook module number (may skip within a grade). */
  moduleNumber: number;
  /** Unit title, e.g. "Exponents & Scientific Notation". */
  title: string;
  lessons: LessonItem[];
}

/** grade → ordered modules, each with its standard-mapped lessons. */
export type LessonNav = Record<number, LessonModule[]>;

/**
 * Build the lesson navigation for grades 6–8. Modules keep the teaching
 * order `getAllUnits` already sorts by; only lessons that carry a standard
 * are included (a lesson with no standard can't select one). Modules that
 * end up with zero standard-mapped lessons are dropped.
 */
export async function getLessonNav(): Promise<LessonNav> {
  const units = await getAllUnits();
  const nav: LessonNav = {};

  for (const unit of units) {
    if (unit.grade < 6 || unit.grade > 8) continue;

    const lessons: LessonItem[] = unit.sections
      .filter((s) => !!s.standard)
      .map((s) => ({
        label: s.label,
        standard: s.standard as string,
        skillIds: s.skillIds ?? [],
      }));

    if (lessons.length === 0) continue;

    (nav[unit.grade] ??= []).push({
      id: unit.id,
      moduleNumber: unit.moduleNumber,
      title: unit.title,
      lessons,
    });
  }

  return nav;
}
