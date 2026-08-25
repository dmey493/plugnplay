"use client";

/**
 * Planner — the whole workspace.
 *
 * Course tabs across the top (renameable, since a course is whatever the
 * teacher teaches), a unit/lesson file system inside each course, a lesson
 * editor when one is open, and a Weeks tab holding the all-preps schedule.
 *
 * Nothing here is subject-specific and nothing reads site content.
 *
 * Storage goes through `loadLibrary` / `saveLibrary` and nowhere else, so
 * the day this moves behind a login only that file changes. Saving is
 * debounced and automatic.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import Container from "@/components/layout/Container";
import CourseTabs, { WEEKS_TAB } from "./CourseTabs";
import LessonEditor from "./LessonEditor";
import LibraryView from "./LibraryView";
import PlanSheet from "./PlanSheet";
import WeekView from "./WeekView";

import type { Course, Lesson, Library, Unit, Week } from "@/lib/lesson-plans";
import {
  COURSE_COLORS,
  DAY_LABELS,
  emptyCourse,
  emptyLesson,
  emptyLibrary,
  emptyUnit,
  emptyWeek,
  exportCourse,
  findLesson,
  loadLibrary,
  newId,
  parseCourseExport,
  saveLibrary,
} from "@/lib/lesson-plans";

const UI_KEY = "pnp:planner-ui";
const SAVE_DEBOUNCE_MS = 500;

interface UiState {
  activeTab: string;
  openLessonId: string | null;
  activeWeekId: string | null;
}

export default function PlannerApp() {
  // `mounted` gates every localStorage read so the server and the first
  // client render agree (nothing personal exists on the server).
  const [mounted, setMounted] = useState(false);
  const [lib, setLib] = useState<Library>(() => emptyLibrary());
  const [ui, setUi] = useState<UiState>({
    activeTab: "",
    openLessonId: null,
    activeWeekId: null,
  });
  /** A brand-new course opens straight into its rename input. */
  const [autoEditId, setAutoEditId] = useState<string | null>(null);

  // ── Load ────────────────────────────────────────────────────────────
  useEffect(() => {
    const loaded = loadLibrary();
    setLib(loaded);
    let saved: Partial<UiState> = {};
    try {
      saved = JSON.parse(window.localStorage.getItem(UI_KEY) ?? "{}");
    } catch {
      saved = {};
    }
    setUi({
      activeTab: saved.activeTab || loaded.courses[0]?.id || "",
      openLessonId: saved.openLessonId ?? null,
      activeWeekId: saved.activeWeekId ?? loaded.weeks[0]?.id ?? null,
    });
    setMounted(true);
  }, []);

  // ── Autosave ────────────────────────────────────────────────────────
  const skipFirst = useRef(true);
  useEffect(() => {
    if (!mounted) return;
    if (skipFirst.current) {
      skipFirst.current = false;
      return;
    }
    const t = setTimeout(() => saveLibrary(lib), SAVE_DEBOUNCE_MS);
    return () => clearTimeout(t);
  }, [lib, mounted]);

  useEffect(() => {
    if (!mounted) return;
    window.localStorage.setItem(UI_KEY, JSON.stringify(ui));
  }, [ui, mounted]);

  // ── Course mutations ────────────────────────────────────────────────
  const patchCourse = useCallback((courseId: string, patch: Partial<Course>) => {
    setLib((l) => ({
      ...l,
      courses: l.courses.map((c) => (c.id === courseId ? { ...c, ...patch } : c)),
    }));
  }, []);

  const addCourse = useCallback(() => {
    setLib((l) => {
      const course = emptyCourse("New course", l.courses.length);
      setUi((u) => ({ ...u, activeTab: course.id, openLessonId: null }));
      setAutoEditId(course.id);
      return { ...l, courses: [...l.courses, course] };
    });
  }, []);

  const deleteCourse = useCallback(
    (courseId: string) => {
      const course = lib.courses.find((c) => c.id === courseId);
      if (!course) return;
      const lessons = course.units.reduce((n, u) => n + u.lessons.length, 0);
      if (
        !window.confirm(
          `Delete "${course.name}" and its ${lessons} ${
            lessons === 1 ? "lesson" : "lessons"
          }? This cannot be undone.`
        )
      ) {
        return;
      }
      setLib((l) => {
        const courses = l.courses.filter((c) => c.id !== courseId);
        setUi((u) => ({
          ...u,
          activeTab: courses[0]?.id ?? WEEKS_TAB,
          openLessonId: null,
        }));
        return {
          ...l,
          courses,
          // Drop any week cells that pointed at the deleted course.
          weeks: l.weeks.map((w) => ({
            ...w,
            cells: w.cells.filter((c) => c.courseId !== courseId),
          })),
        };
      });
    },
    [lib.courses]
  );

  // ── Unit + lesson mutations ─────────────────────────────────────────
  const patchUnits = useCallback(
    (courseId: string, fn: (units: Unit[]) => Unit[]) => {
      setLib((l) => ({
        ...l,
        courses: l.courses.map((c) =>
          c.id === courseId ? { ...c, units: fn(c.units) } : c
        ),
      }));
    },
    []
  );

  const addUnit = useCallback(
    (courseId: string) => {
      // Newest on top: a new folder pushes the year's earlier work down,
      // and the older ones fold shut so the list stays navigable in May.
      patchUnits(courseId, (units) => [
        emptyUnit(`Unit ${units.length + 1}`),
        ...units.map((u) => ({ ...u, collapsed: true })),
      ]);
    },
    [patchUnits]
  );

  const patchLesson = useCallback(
    (courseId: string, lessonId: string, patch: Partial<Lesson>) => {
      patchUnits(courseId, (units) =>
        units.map((u) => ({
          ...u,
          lessons: u.lessons.map((l) =>
            l.id === lessonId
              ? { ...l, ...patch, updatedAt: new Date().toISOString() }
              : l
          ),
        }))
      );
    },
    [patchUnits]
  );

  // ── Week mutations ──────────────────────────────────────────────────
  const patchWeek = useCallback((weekId: string, fn: (w: Week) => Week) => {
    setLib((l) => ({
      ...l,
      weeks: l.weeks.map((w) => (w.id === weekId ? fn(w) : w)),
    }));
  }, []);

  const addWeek = useCallback(() => {
    setLib((l) => {
      const week = emptyWeek(`Week ${l.weeks.length + 1}`);
      setUi((u) => ({ ...u, activeTab: WEEKS_TAB, activeWeekId: week.id }));
      // Newest first, same as units.
      return { ...l, weeks: [week, ...l.weeks] };
    });
  }, []);

  // ── Export / import ─────────────────────────────────────────────────
  const downloadCourse = useCallback((course: Course) => {
    const blob = new Blob([exportCourse(course)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${course.name.replace(/[^\w\- ]+/g, "").trim() || "course"}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, []);

  const importCourse = useCallback((file: File) => {
    const reader = new FileReader();
    reader.onload = () => {
      const course = parseCourseExport(String(reader.result));
      if (!course) {
        window.alert("That file is not a Plug N Play course export.");
        return;
      }
      setLib((l) => {
        const withColor = {
          ...course,
          color: course.color || COURSE_COLORS[l.courses.length % COURSE_COLORS.length],
        };
        setUi((u) => ({ ...u, activeTab: withColor.id, openLessonId: null }));
        return { ...l, courses: [...l.courses, withColor] };
      });
    };
    reader.readAsText(file);
  }, []);

  const fileInput = useRef<HTMLInputElement>(null);

  // ── Derived ─────────────────────────────────────────────────────────
  const activeCourse = useMemo(
    () => lib.courses.find((c) => c.id === ui.activeTab) ?? null,
    [lib.courses, ui.activeTab]
  );

  const open = useMemo(
    () => (ui.openLessonId ? findLesson(lib, ui.openLessonId) : null),
    [lib, ui.openLessonId]
  );

  const activeWeek = useMemo(
    () => lib.weeks.find((w) => w.id === ui.activeWeekId) ?? lib.weeks[0] ?? null,
    [lib.weeks, ui.activeWeekId]
  );

  if (!mounted) {
    return (
      <Container className="py-16">
        <p className="text-sm text-pnp-gray-500">Loading your planner…</p>
      </Container>
    );
  }

  const onWeeks = ui.activeTab === WEEKS_TAB;

  return (
    <>
      <Container className="no-print py-4">
        <CourseTabs
          courses={lib.courses}
          activeId={ui.activeTab}
          autoEditId={autoEditId}
          onAutoEditDone={() => setAutoEditId(null)}
          onSelect={(id) =>
            setUi((u) => ({ ...u, activeTab: id, openLessonId: null }))
          }
          onRename={(id, name) => patchCourse(id, { name })}
          onAddCourse={addCourse}
          actions={[
            { label: "Print / Save as PDF", onSelect: () => window.print() },
            ...(activeCourse
              ? [
                  {
                    label: "Export course",
                    onSelect: () => downloadCourse(activeCourse),
                  },
                ]
              : []),
            { label: "Import course", onSelect: () => fileInput.current?.click() },
            ...(activeCourse
              ? [
                  {
                    label: "Delete course",
                    onSelect: () => deleteCourse(activeCourse.id),
                    danger: true,
                  },
                ]
              : []),
          ]}
        />

        {/* ── Course toolbar ──────────────────────────────────────── */}
        {activeCourse && !onWeeks && (
          <div className="mt-3 flex flex-wrap items-center gap-3 rounded-xl border-2 border-pnp-navy bg-white px-3 py-2 shadow-[3px_3px_0_var(--pnp-navy)]">
            <label className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wide text-pnp-gray-500">
                Typical period
              </span>
              <input
                type="number"
                min={5}
                max={240}
                step={5}
                value={activeCourse.periodMinutes}
                onChange={(e) =>
                  patchCourse(activeCourse.id, {
                    periodMinutes: Math.max(5, Number(e.target.value) || 5),
                  })
                }
                className="w-20 rounded-lg border-2 border-pnp-gray-300 px-2 py-1 text-sm text-pnp-navy focus-visible:border-pnp-accent focus-visible:outline-none"
              />
              <span className="text-xs text-pnp-gray-500">minutes</span>
            </label>

            <span className="text-xs text-pnp-gray-500">
              Every new lesson in this course starts at this length. Shorten or
              lengthen a single day from the Weeks tab.
            </span>

            <input
              ref={fileInput}
              type="file"
              accept="application/json,.json"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) importCourse(f);
                e.target.value = "";
              }}
            />
          </div>
        )}

        {/* Import needs a file input even when no course tab is active. */}
        {onWeeks && (
          <input
            ref={fileInput}
            type="file"
            accept="application/json,.json"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) importCourse(f);
              e.target.value = "";
            }}
          />
        )}

        <div className="mt-4">
          {onWeeks ? (
            <WeekView
              library={lib}
              week={activeWeek}
              weeks={lib.weeks}
              onSelectWeek={(id) => setUi((u) => ({ ...u, activeWeekId: id }))}
              onAddWeek={addWeek}
              onRenameWeek={(label) =>
                activeWeek && patchWeek(activeWeek.id, (w) => ({ ...w, label }))
              }
              onDateWeek={(startDate) =>
                activeWeek &&
                patchWeek(activeWeek.id, (w) => ({ ...w, startDate }))
              }
              onDeleteWeek={() => {
                if (!activeWeek) return;
                if (!window.confirm(`Delete "${activeWeek.label}"? Your lessons are not affected.`))
                  return;
                setLib((l) => {
                  const weeks = l.weeks.filter((w) => w.id !== activeWeek.id);
                  setUi((u) => ({ ...u, activeWeekId: weeks[0]?.id ?? null }));
                  return { ...l, weeks };
                });
              }}
              onSetCell={(courseId, day, lessonId) =>
                activeWeek &&
                patchWeek(activeWeek.id, (w) => ({
                  ...w,
                  cells: [
                    ...w.cells.filter(
                      (c) => !(c.courseId === courseId && c.day === day)
                    ),
                    { id: newId(), courseId, day, lessonId },
                  ],
                }))
              }
              onClearCell={(cellId) =>
                activeWeek &&
                patchWeek(activeWeek.id, (w) => ({
                  ...w,
                  cells: w.cells.filter((c) => c.id !== cellId),
                }))
              }
              onDetachCell={(cellId) =>
                activeWeek &&
                patchWeek(activeWeek.id, (w) => ({
                  ...w,
                  cells: w.cells.map((c) => {
                    if (c.id !== cellId || !c.lessonId) return c;
                    const found = findLesson(lib, c.lessonId);
                    if (!found) return c;
                    // Snapshot the lesson under a fresh id: edits to this
                    // cell now stay here and never reach the unit.
                    return {
                      ...c,
                      detached: { ...found.lesson, id: newId() },
                    };
                  }),
                }))
              }
              onReattachCell={(cellId) =>
                activeWeek &&
                patchWeek(activeWeek.id, (w) => ({
                  ...w,
                  cells: w.cells.map((c) =>
                    c.id === cellId ? { ...c, detached: undefined } : c
                  ),
                }))
              }
              onNoteCell={(cellId, note) =>
                activeWeek &&
                patchWeek(activeWeek.id, (w) => ({
                  ...w,
                  cells: w.cells.map((c) =>
                    c.id === cellId ? { ...c, note } : c
                  ),
                }))
              }
              onOpenLesson={(courseId, lessonId) =>
                setUi((u) => ({
                  ...u,
                  activeTab: courseId,
                  openLessonId: lessonId,
                }))
              }
              onSetDayMinutes={(day, minutes) =>
                activeWeek &&
                patchWeek(activeWeek.id, (w) => {
                  const dayMinutes = (
                    w.dayMinutes ?? DAY_LABELS.map(() => null)
                  ).slice();
                  dayMinutes[day] = minutes;
                  return { ...w, dayMinutes };
                })
              }
            />
          ) : !activeCourse ? (
            <p className="rounded-xl border-2 border-dashed border-pnp-gray-300 px-4 py-16 text-center text-sm text-pnp-gray-500">
              No courses yet. Use the + tab to add your first one.
            </p>
          ) : open ? (
            <LessonEditor
              lesson={open.lesson}
              coursePeriod={open.course.periodMinutes}
              breadcrumb={`${open.course.name} · ${open.unit.name}`}
              onBack={() => setUi((u) => ({ ...u, openLessonId: null }))}
              onChange={(patch) =>
                patchLesson(open.course.id, open.lesson.id, patch)
              }
            />
          ) : (
            <LibraryView
              course={activeCourse}
              onOpenLesson={(_unitId, lessonId) =>
                setUi((u) => ({ ...u, openLessonId: lessonId }))
              }
              onAddUnit={() => addUnit(activeCourse.id)}
              onRenameUnit={(unitId, name) =>
                patchUnits(activeCourse.id, (units) =>
                  units.map((u) => (u.id === unitId ? { ...u, name } : u))
                )
              }
              onDeleteUnit={(unitId) => {
                const unit = activeCourse.units.find((u) => u.id === unitId);
                if (
                  unit &&
                  unit.lessons.length > 0 &&
                  !window.confirm(
                    `Delete "${unit.name}" and its ${unit.lessons.length} ${
                      unit.lessons.length === 1 ? "lesson" : "lessons"
                    }?`
                  )
                ) {
                  return;
                }
                patchUnits(activeCourse.id, (units) =>
                  units.filter((u) => u.id !== unitId)
                );
              }}
              onToggleUnit={(unitId, collapsed) =>
                patchUnits(activeCourse.id, (units) =>
                  units.map((u) => (u.id === unitId ? { ...u, collapsed } : u))
                )
              }
              onAddLesson={(unitId) => {
                const lesson = emptyLesson();
                patchUnits(activeCourse.id, (units) =>
                  units.map((u) =>
                    u.id === unitId ? { ...u, lessons: [...u.lessons, lesson] } : u
                  )
                );
                setUi((u) => ({ ...u, openLessonId: lesson.id }));
              }}
              onDuplicateLesson={(unitId, lessonId) =>
                patchUnits(activeCourse.id, (units) =>
                  units.map((u) => {
                    if (u.id !== unitId) return u;
                    const src = u.lessons.find((l) => l.id === lessonId);
                    if (!src) return u;
                    const copy: Lesson = {
                      ...src,
                      id: newId(),
                      title: `${src.title} (copy)`,
                      blocks: src.blocks.map((b) => ({ ...b, id: newId() })),
                    };
                    const at = u.lessons.findIndex((l) => l.id === lessonId);
                    const lessons = u.lessons.slice();
                    lessons.splice(at + 1, 0, copy);
                    return { ...u, lessons };
                  })
                )
              }
              onDeleteLesson={(unitId, lessonId) => {
                patchUnits(activeCourse.id, (units) =>
                  units.map((u) =>
                    u.id === unitId
                      ? { ...u, lessons: u.lessons.filter((l) => l.id !== lessonId) }
                      : u
                  )
                );
                // Any week pointing at it becomes an empty cell rather than
                // a dangling reference.
                setLib((l) => ({
                  ...l,
                  weeks: l.weeks.map((w) => ({
                    ...w,
                    cells: w.cells.filter(
                      (c) => c.detached || c.lessonId !== lessonId
                    ),
                  })),
                }));
              }}
              onMoveLesson={(fromUnitId, lessonId, toUnitId) =>
                patchUnits(activeCourse.id, (units) => {
                  const from = units.find((u) => u.id === fromUnitId);
                  const lesson = from?.lessons.find((l) => l.id === lessonId);
                  if (!lesson) return units;
                  return units.map((u) => {
                    if (u.id === fromUnitId) {
                      return {
                        ...u,
                        lessons: u.lessons.filter((l) => l.id !== lessonId),
                      };
                    }
                    if (u.id === toUnitId) {
                      return { ...u, lessons: [...u.lessons, lesson] };
                    }
                    return u;
                  });
                })
              }
            />
          )}
        </div>
      </Container>

      {/* Screen-hidden, print-only. */}
      <PlanSheet
        library={lib}
        course={activeCourse}
        lesson={open?.lesson ?? null}
        week={onWeeks ? activeWeek : null}
      />
    </>
  );
}
