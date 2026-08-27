/**
 * The printable output.
 *
 * Hidden on screen, revealed by `@media print` (see the `.plan-print-sheet`
 * block in globals.css). Plain black on white: an administrator's copy and
 * a binder page, not a brand artifact.
 *
 * Prints whatever the workspace is showing:
 *   - a lesson open  → that lesson's timeline on one page
 *   - the Weeks tab  → the all-preps week grid, one page
 *   - a course library → its units and lessons as a contents list
 *
 * Deliberately NOT a React-rendered PDF. The browser's own "Save as PDF" in
 * the print dialog produces the file, which is the same zero-dependency
 * approach `tools/canvas/exportPdf.ts` already uses for the whiteboard.
 */

import { activityType } from "@/lib/classroom/activity-types";
import type { Course, Lesson, Library, Week } from "@/lib/classroom/lesson-plans";
import {
  DAY_LABELS,
  GROUPING_LABEL,
  blockEnd,
  cellLesson,
  lessonMinutes,
  periodFor,
  sortedBlocks,
} from "@/lib/classroom/lesson-plans";

/** "2026-08-19" → "Wednesday, August 19, 2026". Parsed as local time
 *  (the `new Date("yyyy-mm-dd")` overload is UTC and shifts the day back
 *  for anyone west of Greenwich, which is everyone using this). */
function formatDate(iso: string): string {
  if (!iso) return "";
  const [y, m, d] = iso.split("-").map(Number);
  if (!y || !m || !d) return iso;
  return new Date(y, m - 1, d).toLocaleDateString(undefined, {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function Field({ label, value }: { label: string; value: string }) {
  if (!value.trim()) return null;
  return (
    <div className="plan-sheet-field">
      <span className="plan-sheet-field-label">{label}</span>
      <span className="plan-sheet-field-value">{value}</span>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// One lesson
// ─────────────────────────────────────────────────────────────────────

function LessonSheet({
  lesson,
  course,
}: {
  lesson: Lesson;
  course: Course | null;
}) {
  const period = course ? periodFor(course, lesson) : (lesson.periodMinutes ?? 60);
  const used = lessonMinutes(lesson);

  // Gaps print as their own rows so the plan reads as a complete timeline
  // rather than a list that quietly skips ten minutes.
  const rows: React.ReactNode[] = [];
  let cursor = 0;
  for (const b of sortedBlocks(lesson.blocks)) {
    if (b.startMin > cursor) {
      rows.push(
        <tr key={`gap-${cursor}`}>
          <td className="plan-sheet-col-time">{cursor}</td>
          <td className="plan-sheet-col-kind" />
          <td className="plan-sheet-empty">
            Unscheduled ({b.startMin - cursor} min)
          </td>
        </tr>
      );
    }
    const type = activityType(b.typeId);
    rows.push(
      <tr key={b.id}>
        <td className="plan-sheet-col-time">
          <strong>
            {b.startMin}–{blockEnd(b)}
          </strong>
          <span className="plan-sheet-start">{b.minutes} min</span>
        </td>
        <td className="plan-sheet-col-kind">{type.label}</td>
        <td>
          <span className="plan-sheet-activity">{b.label || type.label}</span>
          {b.grouping && (
            <span className="plan-sheet-std">{GROUPING_LABEL[b.grouping]}</span>
          )}
          {b.note && <span className="plan-sheet-note">{b.note}</span>}
          {b.details && <span className="plan-sheet-note">{b.details}</span>}
          {b.materials && (
            <span className="plan-sheet-std">Materials: {b.materials}</span>
          )}
        </td>
      </tr>
    );
    cursor = Math.max(cursor, blockEnd(b));
  }
  if (cursor < period) {
    rows.push(
      <tr key="gap-end">
        <td className="plan-sheet-col-time">{cursor}</td>
        <td className="plan-sheet-col-kind" />
        <td className="plan-sheet-empty">Unscheduled ({period - cursor} min)</td>
      </tr>
    );
  }

  const meta = [course?.name ?? "", lesson.standard, `${period} minute period`]
    .filter(Boolean)
    .join("  ·  ");

  return (
    <section className="plan-sheet-day">
      <header className="plan-sheet-head">
        <h1 className="plan-sheet-title">{lesson.title || "Lesson plan"}</h1>
        <p className="plan-sheet-meta">{meta}</p>
      </header>

      <Field label="Objective" value={lesson.objective} />
      <Field label="Materials" value={lesson.materials} />

      <table className="plan-sheet-table">
        <thead>
          <tr>
            <th className="plan-sheet-col-time">Min</th>
            <th className="plan-sheet-col-kind">Type</th>
            <th>Activity</th>
          </tr>
        </thead>
        <tbody>
          {rows}
          {lesson.blocks.length === 0 && (
            <tr>
              <td colSpan={3} className="plan-sheet-empty">
                Nothing scheduled yet.
              </td>
            </tr>
          )}
        </tbody>
        <tfoot>
          <tr>
            <td className="plan-sheet-col-time">
              <strong>{used} min</strong>
            </td>
            <td colSpan={2}>
              Scheduled of {period}
              {used < period && ` · ${period - used} min unscheduled`}
              {used > period && ` · ${used - period} min over`}
            </td>
          </tr>
        </tfoot>
      </table>

      <Field label="Notes" value={lesson.notes} />

      <div className="plan-sheet-reflection">
        <span className="plan-sheet-field-label">Reflection</span>
        <span className="plan-sheet-rule" />
        <span className="plan-sheet-rule" />
        <span className="plan-sheet-rule" />
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────
// A week: every prep across the five days
// ─────────────────────────────────────────────────────────────────────

function WeekSheet({ library, week }: { library: Library; week: Week }) {
  const courses = library.courses.filter((c) => !c.archived);

  return (
    <section>
      <header className="plan-sheet-head">
        <h1 className="plan-sheet-title">{week.label || "Weekly schedule"}</h1>
        {week.startDate && (
          <p className="plan-sheet-meta">Week of {formatDate(week.startDate)}</p>
        )}
      </header>

      <table className="plan-sheet-table plan-sheet-week">
        <thead>
          <tr>
            <th className="plan-sheet-col-course">Course</th>
            {DAY_LABELS.map((d) => (
              <th key={d}>{d}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {courses.map((course) => (
            <tr key={course.id}>
              <th className="plan-sheet-col-course">
                {course.name}
                <span className="plan-sheet-start">
                  {course.periodMinutes} min
                </span>
              </th>
              {DAY_LABELS.map((_, day) => {
                const cell = week.cells.find(
                  (c) => c.courseId === course.id && c.day === day
                );
                const lesson = cell ? cellLesson(library, cell) : null;
                return (
                  <td key={day}>
                    {lesson ? (
                      <>
                        <span className="plan-sheet-activity">
                          {lesson.title || "Untitled lesson"}
                        </span>
                        {lesson.objective && (
                          <span className="plan-sheet-note">
                            {lesson.objective}
                          </span>
                        )}
                        {cell?.note && (
                          <span className="plan-sheet-note">{cell.note}</span>
                        )}
                      </>
                    ) : (
                      <span className="plan-sheet-empty">—</span>
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────
// A course: its units and lessons, as a contents list
// ─────────────────────────────────────────────────────────────────────

function CourseSheet({ course }: { course: Course }) {
  return (
    <section>
      <header className="plan-sheet-head">
        <h1 className="plan-sheet-title">{course.name}</h1>
        <p className="plan-sheet-meta">
          {course.units.length}{" "}
          {course.units.length === 1 ? "unit" : "units"} ·{" "}
          {course.units.reduce((n, u) => n + u.lessons.length, 0)} lessons ·{" "}
          {course.periodMinutes} minute periods
        </p>
      </header>

      {course.units.map((unit) => (
        <div key={unit.id} className="plan-sheet-day">
          <h2 className="plan-sheet-unit">{unit.name}</h2>
          <table className="plan-sheet-table">
            <tbody>
              {unit.lessons.map((l) => (
                <tr key={l.id}>
                  <td className="plan-sheet-col-time">
                    {lessonMinutes(l)} min
                  </td>
                  <td>
                    <span className="plan-sheet-activity">
                      {l.title || "Untitled lesson"}
                    </span>
                    {l.standard && (
                      <span className="plan-sheet-std">{l.standard}</span>
                    )}
                    {l.objective && (
                      <span className="plan-sheet-note">{l.objective}</span>
                    )}
                  </td>
                </tr>
              ))}
              {unit.lessons.length === 0 && (
                <tr>
                  <td className="plan-sheet-empty">No lessons yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      ))}
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────

export default function PlanSheet({
  library,
  course,
  lesson,
  week,
}: {
  library: Library;
  course: Course | null;
  lesson: Lesson | null;
  week: Week | null;
}) {
  return (
    <div className="plan-print-sheet" aria-hidden="true">
      {week ? (
        <WeekSheet library={library} week={week} />
      ) : lesson ? (
        <LessonSheet lesson={lesson} course={course} />
      ) : course ? (
        <CourseSheet course={course} />
      ) : (
        <p className="plan-sheet-empty">Nothing to print yet.</p>
      )}
      <p className="plan-sheet-footer">Plug N Play</p>
    </div>
  );
}
