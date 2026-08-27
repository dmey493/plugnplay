"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  formGroups,
  getClass,
  planGroupSizes,
  type Class,
  type Student,
} from "@/lib/classroom/classes";
import MagnetSnapAnimation from "./MagnetSnapAnimation";
import SlotReelsAnimation from "./SlotReelsAnimation";
import GroupsResult from "./GroupsResult";

/**
 * Top-level orchestrator for the Form Groups flow.
 *
 * Three phases, owned by a single state machine:
 *   1) "setup" — class header + presence checklist + animation picker
 *      + Form groups button.
 *   2) "animating" — chosen animation plays. The shuffle is computed
 *      ONCE at phase transition and frozen in state; the animation
 *      just unveils it. A Skip button jumps straight to result.
 *   3) "result" — final group cards on screen. Re-randomize loops back
 *      to "animating" with a fresh shuffle.
 *
 * Class data is read from localStorage via the same getClass() the
 * roster editor uses. The whole experience is keyed off the URL's
 * classId — bookmarkable per class.
 */
type Phase = "setup" | "animating" | "result";
type AnimationStyle = "magnet-snap" | "slot-reels";
const ALL_STYLES: AnimationStyle[] = ["magnet-snap", "slot-reels"];

const STYLE_STORAGE_KEY = "pnp:groups:lastStyle";

export default function FormGroupsView({ classId }: { classId: string }) {
  const [cls, setCls] = useState<Class | null | undefined>(undefined);
  // Set of student ids marked PRESENT (default = everyone). Stored as a
  // Set for O(1) toggle; converted to a filtered array at draw time.
  const [present, setPresent] = useState<Set<string>>(new Set());
  const [phase, setPhase] = useState<Phase>("setup");
  const [style, setStyle] = useState<AnimationStyle>("magnet-snap");
  // The locked assignment for the current animation. Computed at the
  // start of each "animating" phase and frozen so the result page can
  // render exactly what the animation unveiled.
  const [groups, setGroups] = useState<Student[][]>([]);
  // Bump key passed into the animation so each re-randomize remounts
  // it from scratch (cleanest way to reset all the per-card timers).
  const [animationRun, setAnimationRun] = useState(0);

  // Load the class from localStorage on mount + when classId changes.
  useEffect(() => {
    const found = getClass(classId);
    setCls(found);
    if (found) setPresent(new Set(found.students.map((s) => s.id)));
  }, [classId]);

  // Restore the last-picked animation style.
  useEffect(() => {
    if (typeof window === "undefined") return;
    const last = window.localStorage.getItem(STYLE_STORAGE_KEY) as AnimationStyle | null;
    if (last && ALL_STYLES.includes(last)) setStyle(last);
  }, []);

  const presentStudents = useMemo(
    () => cls?.students.filter((s) => present.has(s.id)) ?? [],
    [cls, present]
  );
  const sizes = planGroupSizes(presentStudents.length);

  // ── Empty / error states ──
  if (cls === undefined) {
    return <CenteredMessage title="Loading…" />;
  }
  if (cls === null) {
    return (
      <CenteredMessage
        title="Class not found"
        body="It may have been deleted, or this link is from a different browser."
        cta={{ href: "/classes", label: "Back to Classes" }}
      />
    );
  }

  // ── Phase transitions ──
  const startAnimation = () => {
    if (presentStudents.length < 2) return;
    setGroups(formGroups(presentStudents));
    setAnimationRun((n) => n + 1);
    setPhase("animating");
  };
  const finishAnimation = () => setPhase("result");
  const reshuffle = () => {
    setGroups(formGroups(presentStudents));
    setAnimationRun((n) => n + 1);
    setPhase("animating");
  };
  const backToSetup = () => setPhase("setup");

  return (
    <div className="bg-pnp-gray-50">
      {/* Page chrome — back link + class name. Hidden during the animation
          so the full viewport reads as the projection surface. */}
      {phase === "setup" && (
        <section className="border-b border-pnp-gray-200 bg-white py-6">
          <div className="mx-auto max-w-[1200px] px-4 md:px-6">
            <Link
              href="/classes"
              className="inline-flex items-center gap-1.5 text-sm font-semibold text-pnp-gray-600 transition-colors hover:text-pnp-navy"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M19 12H5M12 19l-7-7 7-7" />
              </svg>
              Back to Classes
            </Link>
            <div className="mt-2 flex flex-wrap items-end justify-between gap-3">
              <div>
                <p className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
                  Form groups
                </p>
                <h1 className="mt-1 font-heading text-2xl font-bold text-pnp-navy md:text-3xl">
                  {cls.name}
                </h1>
              </div>
              <p className="text-sm text-pnp-gray-500">
                {presentStudents.length} of {cls.students.length} present
                {sizes.length > 0 && (
                  <> &middot; {sizes.length} group{sizes.length === 1 ? "" : "s"} ({sizes.join(" + ")})</>
                )}
              </p>
            </div>
          </div>
        </section>
      )}

      {/* Phase-specific body. */}
      {phase === "setup" && (
        <SetupScreen
          students={cls.students}
          present={present}
          onToggle={(id) =>
            setPresent((prev) => {
              const next = new Set(prev);
              if (next.has(id)) next.delete(id);
              else next.add(id);
              return next;
            })
          }
          onAllPresent={() =>
            setPresent(new Set(cls.students.map((s) => s.id)))
          }
          onAllAbsent={() => setPresent(new Set())}
          style={style}
          onChangeStyle={(s) => {
            setStyle(s);
            if (typeof window !== "undefined") {
              window.localStorage.setItem(STYLE_STORAGE_KEY, s);
            }
          }}
          onStart={startAnimation}
          canStart={presentStudents.length >= 2}
        />
      )}

      {phase === "animating" &&
        (style === "slot-reels" ? (
          <SlotReelsAnimation
            key={animationRun}
            groups={groups}
            onFinish={finishAnimation}
            onSkip={finishAnimation}
          />
        ) : (
          <MagnetSnapAnimation
            key={animationRun}
            groups={groups}
            onFinish={finishAnimation}
            onSkip={finishAnimation}
          />
        ))}

      {phase === "result" && (
        <GroupsResult
          groups={groups}
          onReshuffle={reshuffle}
          onBack={backToSetup}
        />
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// Setup screen
// ─────────────────────────────────────────────────────────────────────

function SetupScreen({
  students,
  present,
  onToggle,
  onAllPresent,
  onAllAbsent,
  style,
  onChangeStyle,
  onStart,
  canStart,
}: {
  students: Student[];
  present: Set<string>;
  onToggle: (id: string) => void;
  onAllPresent: () => void;
  onAllAbsent: () => void;
  style: AnimationStyle;
  onChangeStyle: (s: AnimationStyle) => void;
  onStart: () => void;
  canStart: boolean;
}) {
  return (
    <section className="py-8 md:py-10">
      <div className="mx-auto grid max-w-[1200px] gap-6 px-4 md:px-6 lg:grid-cols-[2fr_1fr]">
        {/* Presence checklist — primary content. */}
        <div className="rounded-lg border border-pnp-gray-200 bg-white">
          <div className="flex items-center justify-between border-b border-pnp-gray-200 px-4 py-3">
            <h2 className="font-heading text-sm font-bold uppercase tracking-wider text-pnp-gray-500">
              Who's here today?
            </h2>
            <div className="flex items-center gap-2 text-xs">
              <button
                type="button"
                onClick={onAllPresent}
                className="rounded px-2 py-1 font-semibold text-pnp-gray-600 transition-colors hover:bg-pnp-gray-100 hover:text-pnp-navy"
              >
                Mark all present
              </button>
              <span className="text-pnp-gray-300">·</span>
              <button
                type="button"
                onClick={onAllAbsent}
                className="rounded px-2 py-1 font-semibold text-pnp-gray-600 transition-colors hover:bg-pnp-gray-100 hover:text-pnp-navy"
              >
                Clear
              </button>
            </div>
          </div>
          {students.length === 0 ? (
            <div className="p-6 text-center text-sm text-pnp-gray-500">
              No students on this roster yet.
              <br />
              <Link
                href="/classes"
                className="mt-2 inline-block text-pnp-accent underline-offset-2 hover:underline"
              >
                Back to Classes to add some.
              </Link>
            </div>
          ) : (
            <ul className="divide-y divide-pnp-gray-100">
              {students.map((s) => {
                const here = present.has(s.id);
                return (
                  <li key={s.id}>
                    <button
                      type="button"
                      onClick={() => onToggle(s.id)}
                      className={`flex w-full items-center gap-3 px-4 py-2.5 text-left text-sm transition-colors hover:bg-pnp-gray-50 ${
                        here ? "text-pnp-navy" : "text-pnp-gray-500"
                      }`}
                    >
                      <span
                        aria-hidden="true"
                        className={`flex h-5 w-5 items-center justify-center rounded-md border-2 transition-colors ${
                          here
                            ? "border-pnp-accent bg-pnp-accent text-white"
                            : "border-pnp-gray-300 bg-white"
                        }`}
                      >
                        {here && (
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M5 12l5 5L20 7" />
                          </svg>
                        )}
                      </span>
                      <span className={here ? "" : "line-through"}>{s.name}</span>
                    </button>
                  </li>
                );
              })}
            </ul>
          )}
        </div>

        {/* Right rail: animation picker + start button. */}
        <aside className="space-y-4">
          <div className="rounded-lg border border-pnp-gray-200 bg-white p-4">
            <h2 className="font-heading text-sm font-bold uppercase tracking-wider text-pnp-gray-500">
              Animation
            </h2>
            <div className="mt-3 space-y-2">
              <StyleOption
                value="magnet-snap"
                active={style === "magnet-snap"}
                onChange={onChangeStyle}
                title="Magnet Snap"
                blurb="Names scatter across the screen, group cards fade in below, then each name flies to its assigned group like a magnet. ~3 seconds."
              />
              <StyleOption
                value="slot-reels"
                active={style === "slot-reels"}
                onChange={onChangeStyle}
                title="Slot Reels"
                blurb="Each group is a mini slot machine. All reels spin fast, then stop one at a time to reveal each assigned student — like a casino reveal. ~4–5 seconds."
              />
            </div>
          </div>

          <button
            type="button"
            onClick={onStart}
            disabled={!canStart}
            className="w-full rounded-md bg-pnp-accent px-4 py-3 text-base font-bold text-white transition-colors hover:bg-pnp-accent-hover disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Form groups
          </button>
          {!canStart && (
            <p className="text-xs text-pnp-gray-500">
              Mark at least two students present to form a group.
            </p>
          )}
        </aside>
      </div>
    </section>
  );
}

function StyleOption({
  value,
  active,
  onChange,
  title,
  blurb,
}: {
  value: AnimationStyle;
  active: boolean;
  onChange: (s: AnimationStyle) => void;
  title: string;
  blurb: string;
}) {
  return (
    <button
      type="button"
      onClick={() => onChange(value)}
      className={`block w-full rounded-md border-2 p-3 text-left transition-colors ${
        active
          ? "border-pnp-accent bg-pnp-accent-soft/30"
          : "border-pnp-gray-200 bg-white hover:border-pnp-accent/40"
      }`}
    >
      <div className="flex items-center gap-2">
        <span
          aria-hidden="true"
          className={`h-3 w-3 rounded-full border-2 ${
            active ? "border-pnp-accent bg-pnp-accent" : "border-pnp-gray-300 bg-white"
          }`}
        />
        <span className="font-heading text-sm font-bold text-pnp-navy">{title}</span>
      </div>
      <p className="mt-1 pl-5 text-xs text-pnp-gray-500">{blurb}</p>
    </button>
  );
}

// ─────────────────────────────────────────────────────────────────────
// Centred-message shell for loading / error states
// ─────────────────────────────────────────────────────────────────────

function CenteredMessage({
  title,
  body,
  cta,
}: {
  title: string;
  body?: string;
  cta?: { href: string; label: string };
}) {
  return (
    <div className="flex min-h-[60vh] items-center justify-center px-4">
      <div className="rounded-lg border-2 border-dashed border-pnp-gray-300 bg-white p-10 text-center">
        <h2 className="font-heading text-lg font-bold text-pnp-navy">{title}</h2>
        {body && <p className="mx-auto mt-2 max-w-md text-sm text-pnp-gray-500">{body}</p>}
        {cta && (
          <Link
            href={cta.href}
            className="mt-4 inline-flex items-center rounded-md bg-pnp-accent px-3 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-pnp-accent-hover"
          >
            {cta.label}
          </Link>
        )}
      </div>
    </div>
  );
}
