"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  clearLastGroups,
  createClass,
  formGroups,
  getClasses,
  getLastGroups,
  parseRosterPaste,
  planGroupSizes,
  saveLastGroups,
  updateClass,
  type Class,
  type Student,
} from "@/lib/classes";
import MagnetSnapAnimation from "./MagnetSnapAnimation";
import SlotReelsAnimation from "./SlotReelsAnimation";
import GroupsResult from "./GroupsResult";

/**
 * Self-contained "Groups" control for the projection chrome bars.
 *
 * Drop `<GroupsButton isDark={...} />` into any projection surface's
 * control row and it carries its own full-screen overlay + all state.
 * No props beyond the host theme flag; nothing to wire up.
 *
 * The trigger button adapts to the host chrome (dark/light) so it sits
 * beside the surface's other tool buttons (Timer, Draw, …). Surfaces
 * whose chrome uses a different button treatment (e.g. the intervention
 * runner's rounded-full pills) pass `className` to match exactly. The
 * overlay itself is always dark-navy, matching the group animations +
 * result so it reads as one projected surface regardless of the task.
 *
 * Flow (a small state machine in GroupsOverlay):
 *   pick     → choose a saved class OR paste a one-time roster
 *   setup    → who's here today + animation style
 *   animating→ the chosen reveal animation (shuffle frozen up front)
 *   result   → group cards; reshuffle / change attendance / close
 *
 * Class data comes from localStorage — no login. A pasted roster is
 * ephemeral by default; "Save as a class" persists it for next time.
 */
/**
 * A command from the phone remote, relayed by the host projection. The
 * `nonce` makes each distinct command apply exactly once (the host bumps
 * it per command drained from the heartbeat). `form-class`/`reshuffle`
 * play the reveal on the projection so the class sees it; the phone
 * mirrors the result via the projection's broadcast state.
 */
export interface GroupsRemoteAction {
  nonce: number;
  type: "open" | "close" | "form-class" | "reshuffle" | "clear";
  classId?: string;
}

export default function GroupsButton({
  isDark = true,
  className,
  remoteAction,
}: {
  isDark?: boolean;
  /** Overrides the default chrome-button classes so the trigger matches
   *  a host whose control bar uses a different button treatment. */
  className?: string;
  /** Command relayed from the phone remote. Only the rich-task projection
   *  wires this; other hosts leave it undefined and Groups stays local. */
  remoteAction?: GroupsRemoteAction;
}) {
  const [open, setOpen] = useState(false);
  // True when there's a saved assignment to reopen — drives the little
  // dot so a teacher knows this period's groups are still here.
  const [hasSaved, setHasSaved] = useState(false);
  useEffect(() => setHasSaved(!!getLastGroups()), []);

  // The action currently handed to the overlay. Bumped from the remote
  // relay below; the overlay applies each new nonce once.
  const [pendingAction, setPendingAction] = useState<GroupsRemoteAction | null>(null);

  // Relay phone commands. `open`/`form-class`/`reshuffle` open the overlay
  // (which plays on the projection); `close`/`clear` tear it down.
  const lastNonce = useRef<number | null>(null);
  useEffect(() => {
    if (!remoteAction || remoteAction.nonce === lastNonce.current) return;
    lastNonce.current = remoteAction.nonce;
    if (remoteAction.type === "close") {
      setOpen(false);
    } else if (remoteAction.type === "clear") {
      clearLastGroups();
      setHasSaved(false);
      setOpen(false);
    } else {
      setPendingAction(remoteAction);
      setOpen(true);
    }
  }, [remoteAction]);

  const triggerClass =
    className ??
    `inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-semibold transition-colors ${
      isDark
        ? "bg-white/10 text-white hover:bg-white/20"
        : "bg-pnp-gray-100 text-pnp-gray-700 hover:bg-pnp-gray-200"
    }`;

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className={`relative ${triggerClass}`}
        title={hasSaved ? "Groups saved — click to view" : "Form random groups"}
      >
        <GroupsIcon />
        <span>Groups</span>
        {hasSaved && (
          <span
            aria-hidden="true"
            className="absolute -right-1 -top-1 h-2.5 w-2.5 rounded-full bg-pnp-green ring-2 ring-pnp-navy"
          />
        )}
      </button>
      {open && (
        <GroupsOverlay
          pendingAction={pendingAction}
          onClose={() => {
            setOpen(false);
            setPendingAction(null);
            // Re-read so the dot reflects any save/clear from this session.
            setHasSaved(!!getLastGroups());
          }}
        />
      )}
    </>
  );
}

// ─────────────────────────────────────────────────────────────────────
// Overlay + state machine
// ─────────────────────────────────────────────────────────────────────

type Phase = "pick" | "setup" | "animating" | "result";
type AnimationStyle = "magnet-snap" | "slot-reels";
const ALL_STYLES: AnimationStyle[] = ["magnet-snap", "slot-reels"];
// Shared with the standalone /groups flow so the teacher's last-picked
// animation carries across both entry points.
const STYLE_STORAGE_KEY = "pnp:groups:lastStyle";

function GroupsOverlay({
  pendingAction,
  onClose,
}: {
  pendingAction?: GroupsRemoteAction | null;
  onClose: () => void;
}) {
  const [phase, setPhase] = useState<Phase>("pick");
  const [classes, setClasses] = useState<Class[]>([]);
  // The roster we're grouping (from a saved class or a one-time paste),
  // plus a label for the header. Null until the teacher picks a source.
  const [roster, setRoster] = useState<Student[]>([]);
  const [label, setLabel] = useState<string>("");
  const [present, setPresent] = useState<Set<string>>(new Set());
  const [style, setStyle] = useState<AnimationStyle>("magnet-snap");
  const [groups, setGroups] = useState<Student[][]>([]);
  const [animationRun, setAnimationRun] = useState(0);

  // Form + animate a roster immediately (used by both the local flow and
  // the phone remote). Freezes the shuffle up front like the standalone
  // flow; finishAnimation persists it.
  const formNow = (students: Student[], name: string) => {
    setRoster(students);
    setPresent(new Set(students.map((s) => s.id)));
    setLabel(name);
    setGroups(formGroups(students));
    setAnimationRun((n) => n + 1);
    setPhase("animating");
  };

  // On open: load saved classes + last-picked animation. If the phone
  // relayed an action (form a class / reshuffle), act on it so the reveal
  // plays here on the projection. Otherwise, if there's a previously-
  // formed assignment still saved, jump straight to it so a student who
  // forgot their board can see it again — the roster is reconstructed
  // from the saved groups so Change attendance / Reshuffle keep working.
  useEffect(() => {
    setClasses(getClasses());
    if (typeof window !== "undefined") {
      const lastStyle = window.localStorage.getItem(STYLE_STORAGE_KEY) as AnimationStyle | null;
      if (lastStyle && ALL_STYLES.includes(lastStyle)) setStyle(lastStyle);
    }
    if (pendingAction && pendingAction.type !== "open") {
      applyAction(pendingAction);
      return;
    }
    const saved = getLastGroups();
    if (saved) {
      const flat = saved.groups.flat();
      setRoster(flat);
      setPresent(new Set(flat.map((s) => s.id)));
      setGroups(saved.groups);
      setLabel(saved.label);
      setPhase("result");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Later remote actions (arriving while the overlay is already open):
  // apply each new nonce once. The mount effect handles the first one.
  const appliedNonce = useRef<number | null>(pendingAction?.nonce ?? null);
  useEffect(() => {
    if (!pendingAction || pendingAction.nonce === appliedNonce.current) return;
    appliedNonce.current = pendingAction.nonce;
    applyAction(pendingAction);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pendingAction?.nonce]);

  // Translate a remote action into a state change.
  function applyAction(a: GroupsRemoteAction) {
    if (a.type === "form-class") {
      const cls = getClasses().find((c) => c.id === a.classId);
      if (cls && cls.students.length >= 2) formNow(cls.students, cls.name);
    } else if (a.type === "reshuffle") {
      const saved = getLastGroups();
      const base = roster.length
        ? roster.filter((s) => present.has(s.id))
        : saved?.groups.flat() ?? [];
      if (base.length >= 2) formNow(base, label || saved?.label || "Groups");
    }
    // "open" just shows the overlay; the mount effect's saved-restore or
    // the pick screen already covers it.
  }

  // Isolate keyboard while open: Escape closes the overlay (not the task
  // underneath), and arrows/space/d must not leak to the projection's
  // own key handlers. Capture phase + stopImmediatePropagation beats the
  // window-level listeners in ProjectionView / the thin-slice runner.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const k = e.key;
      if (
        k === "Escape" ||
        k === "ArrowRight" ||
        k === "ArrowLeft" ||
        k === " " ||
        k.toLowerCase() === "d"
      ) {
        e.stopImmediatePropagation();
        if (k === "Escape") {
          e.preventDefault();
          onClose();
        }
      }
    };
    window.addEventListener("keydown", onKey, true);
    return () => window.removeEventListener("keydown", onKey, true);
  }, [onClose]);

  const presentStudents = useMemo(
    () => roster.filter((s) => present.has(s.id)),
    [roster, present]
  );
  const sizes = planGroupSizes(presentStudents.length);

  // ── Source selection ──
  const chooseClass = (cls: Class) => {
    setRoster(cls.students);
    setLabel(cls.name);
    setPresent(new Set(cls.students.map((s) => s.id)));
    setPhase("setup");
  };
  const choosePaste = (students: Student[], name: string) => {
    setRoster(students);
    setLabel(name);
    setPresent(new Set(students.map((s) => s.id)));
    setPhase("setup");
  };

  // ── Phase transitions ──
  const start = () => {
    if (presentStudents.length < 2) return;
    setGroups(formGroups(presentStudents));
    setAnimationRun((n) => n + 1);
    setPhase("animating");
  };
  // Persist the frozen assignment as soon as the reveal lands, so it
  // survives Close / an accidental Exit.
  const finishAnimation = () => {
    saveLastGroups(label, groups);
    setPhase("result");
  };
  const reshuffle = () => {
    setGroups(formGroups(presentStudents));
    setAnimationRun((n) => n + 1);
    setPhase("animating");
  };
  // Start over from a different class/roster — keeps the saved groups
  // until a new set is formed.
  const newGroups = () => setPhase("pick");
  // Forget the saved assignment entirely.
  const clearGroups = () => {
    clearLastGroups();
    setGroups([]);
    setLabel("");
    setPhase("pick");
  };

  const pickStyle = (s: AnimationStyle) => {
    setStyle(s);
    if (typeof window !== "undefined") {
      window.localStorage.setItem(STYLE_STORAGE_KEY, s);
    }
  };

  return (
    <div className="fixed inset-0 z-[300] overflow-y-auto bg-pnp-navy">
      {/* Persistent close — returns to the task exactly where it was. */}
      <button
        type="button"
        onClick={onClose}
        className="fixed right-5 top-4 z-[310] inline-flex items-center gap-1.5 rounded-lg border border-white/20 bg-white/10 px-3 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-white/20"
        title="Close groups (Esc)"
      >
        <XIcon />
        <span>Close</span>
      </button>

      {phase === "pick" && (
        <PickScreen
          classes={classes}
          onChooseClass={chooseClass}
          onChoosePaste={choosePaste}
          onSaveClass={(students, name) => {
            const cls = createClass(name);
            const saved = updateClass(cls.id, { students });
            setClasses(getClasses());
            if (saved) chooseClass(saved);
          }}
        />
      )}

      {phase === "setup" && (
        <SetupScreen
          label={label}
          roster={roster}
          present={present}
          sizes={sizes}
          onToggle={(id) =>
            setPresent((prev) => {
              const next = new Set(prev);
              if (next.has(id)) next.delete(id);
              else next.add(id);
              return next;
            })
          }
          onAllPresent={() => setPresent(new Set(roster.map((s) => s.id)))}
          onAllAbsent={() => setPresent(new Set())}
          style={style}
          onChangeStyle={pickStyle}
          onBack={() => setPhase("pick")}
          onStart={start}
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
          label={label}
          onReshuffle={reshuffle}
          onBack={() => setPhase("setup")}
          onNew={newGroups}
          onClear={clearGroups}
        />
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// Pick screen — choose a saved class or paste a one-time roster
// ─────────────────────────────────────────────────────────────────────

function PickScreen({
  classes,
  onChooseClass,
  onChoosePaste,
  onSaveClass,
}: {
  classes: Class[];
  onChooseClass: (cls: Class) => void;
  onChoosePaste: (students: Student[], name: string) => void;
  onSaveClass: (students: Student[], name: string) => void;
}) {
  const [paste, setPaste] = useState("");
  const parsed = useMemo(() => parseRosterPaste(paste), [paste]);
  const canGroup = parsed.length >= 2;

  return (
    <div className="mx-auto flex min-h-screen max-w-[900px] flex-col justify-center px-6 py-16">
      <p className="text-center text-xs font-bold uppercase tracking-[0.3em] text-white/50">
        Random groups
      </p>
      <h1 className="mt-2 text-center font-heading text-3xl font-extrabold text-white md:text-4xl">
        Who's grouping up?
      </h1>

      <div className="mt-10 grid gap-6 md:grid-cols-2">
        {/* Saved classes */}
        <div className="rounded-xl border border-white/15 bg-white/5 p-5">
          <h2 className="font-heading text-sm font-bold uppercase tracking-wider text-white/60">
            Your classes
          </h2>
          {classes.length === 0 ? (
            <p className="mt-3 text-sm text-white/60">
              No saved classes yet. Paste a roster on the right — or build one
              on the Classes page for next time.
            </p>
          ) : (
            <ul className="mt-3 space-y-2">
              {classes.map((cls) => {
                const groupable = cls.students.length >= 2;
                return (
                  <li key={cls.id}>
                    <button
                      type="button"
                      onClick={() => groupable && onChooseClass(cls)}
                      disabled={!groupable}
                      className={`flex w-full items-center justify-between gap-3 rounded-lg border px-4 py-3 text-left transition-colors ${
                        groupable
                          ? "border-white/15 bg-white/5 hover:border-pnp-accent hover:bg-white/10"
                          : "cursor-not-allowed border-white/10 bg-white/5 opacity-50"
                      }`}
                    >
                      <span className="min-w-0 flex-1 truncate font-heading font-bold text-white">
                        {cls.name}
                      </span>
                      <span className="shrink-0 text-xs font-semibold text-white/60">
                        {cls.students.length} student
                        {cls.students.length === 1 ? "" : "s"}
                      </span>
                    </button>
                  </li>
                );
              })}
            </ul>
          )}
        </div>

        {/* Quick paste */}
        <div className="rounded-xl border border-white/15 bg-white/5 p-5">
          <h2 className="font-heading text-sm font-bold uppercase tracking-wider text-white/60">
            Quick group
          </h2>
          <p className="mt-1 text-xs text-white/50">
            Paste names — one per line. Groups now, nothing saved unless you
            want it.
          </p>
          <textarea
            value={paste}
            onChange={(e) => setPaste(e.target.value)}
            rows={6}
            placeholder={"Amy Chen\nBen Rodriguez\nCarmen Ng\n…"}
            className="mt-3 w-full rounded-md border border-white/20 bg-pnp-navy/60 px-3 py-2 text-sm text-white outline-none transition-colors placeholder:text-white/30 focus:border-pnp-accent focus:ring-2 focus:ring-pnp-accent/40"
          />
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => canGroup && onChoosePaste(parsed, "Quick group")}
              disabled={!canGroup}
              className="rounded-md bg-pnp-accent px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-pnp-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
            >
              Make groups
            </button>
            <button
              type="button"
              onClick={() => {
                if (!canGroup) return;
                const name =
                  window.prompt("Save these names as a class called:", "New class")?.trim();
                if (name) onSaveClass(parsed, name);
              }}
              disabled={!canGroup}
              className="rounded-md border border-white/25 bg-white/5 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-white/15 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Save as a class
            </button>
          </div>
          {paste.trim() && !canGroup && (
            <p className="mt-2 text-xs text-white/50">
              Add at least two names to form a group.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// Setup screen — who's here + animation style
// ─────────────────────────────────────────────────────────────────────

function SetupScreen({
  label,
  roster,
  present,
  sizes,
  onToggle,
  onAllPresent,
  onAllAbsent,
  style,
  onChangeStyle,
  onBack,
  onStart,
  canStart,
}: {
  label: string;
  roster: Student[];
  present: Set<string>;
  sizes: number[];
  onToggle: (id: string) => void;
  onAllPresent: () => void;
  onAllAbsent: () => void;
  style: AnimationStyle;
  onChangeStyle: (s: AnimationStyle) => void;
  onBack: () => void;
  onStart: () => void;
  canStart: boolean;
}) {
  const presentCount = roster.filter((s) => present.has(s.id)).length;

  return (
    <div className="mx-auto max-w-[1100px] px-6 py-12">
      <button
        type="button"
        onClick={onBack}
        className="inline-flex items-center gap-1.5 text-sm font-semibold text-white/60 transition-colors hover:text-white"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7" />
        </svg>
        Pick a different class
      </button>

      <div className="mt-3 flex flex-wrap items-end justify-between gap-3">
        <h1 className="font-heading text-2xl font-bold text-white md:text-3xl">{label}</h1>
        <p className="text-sm text-white/60">
          {presentCount} of {roster.length} present
          {sizes.length > 0 && (
            <>
              {" "}
              &middot; {sizes.length} group{sizes.length === 1 ? "" : "s"} (
              {sizes.join(" + ")})
            </>
          )}
        </p>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-[2fr_1fr]">
        {/* Presence checklist */}
        <div className="rounded-xl border border-white/15 bg-white/5">
          <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
            <h2 className="font-heading text-sm font-bold uppercase tracking-wider text-white/60">
              Who's here today?
            </h2>
            <div className="flex items-center gap-2 text-xs">
              <button
                type="button"
                onClick={onAllPresent}
                className="rounded px-2 py-1 font-semibold text-white/70 transition-colors hover:bg-white/10 hover:text-white"
              >
                Mark all present
              </button>
              <span className="text-white/25">·</span>
              <button
                type="button"
                onClick={onAllAbsent}
                className="rounded px-2 py-1 font-semibold text-white/70 transition-colors hover:bg-white/10 hover:text-white"
              >
                Clear
              </button>
            </div>
          </div>
          <ul className="grid gap-1 p-2 sm:grid-cols-2">
            {roster.map((s) => {
              const here = present.has(s.id);
              return (
                <li key={s.id}>
                  <button
                    type="button"
                    onClick={() => onToggle(s.id)}
                    className={`flex w-full items-center gap-3 rounded-md px-3 py-2 text-left text-sm transition-colors hover:bg-white/10 ${
                      here ? "text-white" : "text-white/40"
                    }`}
                  >
                    <span
                      aria-hidden="true"
                      className={`flex h-5 w-5 items-center justify-center rounded-md border-2 transition-colors ${
                        here
                          ? "border-pnp-accent bg-pnp-accent text-white"
                          : "border-white/30 bg-transparent"
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
        </div>

        {/* Animation picker + start */}
        <aside className="space-y-4">
          <div className="rounded-xl border border-white/15 bg-white/5 p-4">
            <h2 className="font-heading text-sm font-bold uppercase tracking-wider text-white/60">
              Reveal
            </h2>
            <div className="mt-3 space-y-2">
              <StyleOption
                value="magnet-snap"
                active={style === "magnet-snap"}
                onChange={onChangeStyle}
                title="Magnet Snap"
                blurb="Names scatter, then fly to their group like magnets. ~3s."
              />
              <StyleOption
                value="slot-reels"
                active={style === "slot-reels"}
                onChange={onChangeStyle}
                title="Slot Reels"
                blurb="Each group is a slot machine that stops to reveal its members. ~4–5s."
              />
            </div>
          </div>

          <button
            type="button"
            onClick={onStart}
            disabled={!canStart}
            className="w-full rounded-md bg-pnp-accent px-4 py-3 text-base font-bold text-white transition-colors hover:bg-pnp-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
          >
            Form groups
          </button>
          {!canStart && (
            <p className="text-xs text-white/50">
              Mark at least two students present to form a group.
            </p>
          )}
        </aside>
      </div>
    </div>
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
          ? "border-pnp-accent bg-pnp-accent/15"
          : "border-white/15 bg-transparent hover:border-pnp-accent/50"
      }`}
    >
      <div className="flex items-center gap-2">
        <span
          aria-hidden="true"
          className={`h-3 w-3 rounded-full border-2 ${
            active ? "border-pnp-accent bg-pnp-accent" : "border-white/30 bg-transparent"
          }`}
        />
        <span className="font-heading text-sm font-bold text-white">{title}</span>
      </div>
      <p className="mt-1 pl-5 text-xs text-white/50">{blurb}</p>
    </button>
  );
}

// ─────────────────────────────────────────────────────────────────────
// Icons
// ─────────────────────────────────────────────────────────────────────

function GroupsIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  );
}

function XIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.25" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}
