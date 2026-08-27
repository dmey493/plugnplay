"use client";

import { useState, useEffect, useLayoutEffect, useCallback, useMemo, useRef } from "react";
import { useRouter } from "next/navigation";
import { parsePrompt, parseBulletedList } from "@/lib/generators/split-prompt";
import MarkdownText from "./MarkdownText";
import RemoteConnectModal from "./RemoteConnectModal";
import type {
  ConnectProjectionResponse,
  HeartbeatResponse,
  ProjectionState,
  RemoteCommand,
} from "@/lib/core/types";
import type { TimerController } from "./TimerOverlay";
import {
  PROJECTION_THEMES,
  THEME_ORDER,
  type ThemeId,
} from "@/lib/classroom/projection-themes";
import type { TaskImage } from "@/lib/core/types";
import InteractiveImage from "./interactive/InteractiveImage";
import DrawingOverlay from "@/components/projection/DrawingOverlay";
import TimerOverlay from "./TimerOverlay";
import GroupsButton, { type GroupsRemoteAction } from "@/components/groups/GroupsButton";
import { getClasses, getLastGroups } from "@/lib/classroom/classes";

/** Read the current groups mirror + class list from localStorage for the
 *  heartbeat broadcast. Called on the client only (connect + each tick),
 *  so it always reflects the latest saved assignment / rosters. */
function groupsBroadcast(): Pick<ProjectionState, "groups" | "classes"> {
  const saved = getLastGroups();
  return {
    groups: saved
      ? {
          label: saved.label,
          groups: saved.groups.map((g) => g.map((s) => ({ id: s.id, name: s.name }))),
        }
      : null,
    classes: getClasses().map((c) => ({
      id: c.id,
      name: c.name,
      count: c.students.length,
    })),
  };
}

interface Props {
  taskId: string;
  title: string;
  studentPrompt: string;
  primaryStandard?: string;
  extensions?: string;
  image?: TaskImage;
}

// A keyed question — main or extension — used by the drawer + the reveal stack.
interface KeyedQ {
  key: string;
  group: "main" | "extension";
  /** 1-based index within its group, used for drawer labels. */
  groupIndex: number;
  /** Display number students see (renumbered when filtered). */
  displayLabel: string;
  text: string;
}

export default function ProjectionView({
  taskId,
  title,
  studentPrompt,
  primaryStandard,
  extensions,
  image,
}: Props) {
  const router = useRouter();
  // Default to underwater per request — projection feels like the bubbles are
  // floating, especially with the question reveal stack.
  const [themeId, setThemeId] = useState<ThemeId>("underwater");
  const theme = PROJECTION_THEMES[themeId];
  const isDark = theme.isDark;
  const [revealedCount, setRevealedCount] = useState(1);
  const [excludedKeys, setExcludedKeys] = useState<Set<string>>(new Set());
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [controlsVisible, setControlsVisible] = useState(true);
  // Whiteboard drawing toggle. Wipes whenever the visible question
  // changes (revealedCount) or the picker filter changes.
  const [drawing, setDrawing] = useState(false);
  // Sliding-window size: how many of the most-recently-revealed questions
  // are visible at once. Show=1 → only the current question. Show=2 → the
  // current + the one before. Show=3 → the current + the two before.
  // Advance still moves one question at a time; the window just clamps how
  // many trail behind.
  const [windowSize, setWindowSize] = useState<1 | 2 | 3>(2);
  // Draggable countdown timer overlay — defaults to off.
  const [timerOpen, setTimerOpen] = useState(false);
  // Timer state — lifted out of TimerOverlay so we can both broadcast it
  // via the heartbeat (so the phone reflects the same countdown) and
  // mutate it from the phone's commands.
  const [timerDuration, setTimerDuration] = useState(300);
  const [timerRemaining, setTimerRemaining] = useState(300);
  const [timerRunning, setTimerRunning] = useState(false);
  // Wrap them up as the controller TimerOverlay expects. Memoised so we
  // don't recreate the object on every render and trigger needless work
  // inside the overlay.
  const timerController: TimerController = useMemo(
    () => ({
      duration: timerDuration,
      remaining: timerRemaining,
      running: timerRunning,
      set: (patch) => {
        if (patch.duration !== undefined) setTimerDuration(patch.duration);
        if (patch.remaining !== undefined) setTimerRemaining(patch.remaining);
        if (patch.running !== undefined) setTimerRunning(patch.running);
      },
    }),
    [timerDuration, timerRemaining, timerRunning]
  );

  // ─── Phone-as-remote pairing ───────────────────────────────────────
  // `roomCode` is null until the teacher clicks Connect. Once minted,
  // the heartbeat effect below kicks in and runs until the projection
  // unmounts or the teacher explicitly disconnects. `phonePaired`
  // flips true on the first heartbeat response after a phone joins.
  const [roomCode, setRoomCode] = useState<string | null>(null);
  const [projectionToken, setProjectionToken] = useState<string | null>(null);
  const [phonePaired, setPhonePaired] = useState(false);
  const [connectModalOpen, setConnectModalOpen] = useState(false);
  // `connectInFlight` blocks double-clicks while we're still minting.
  const [connectInFlight, setConnectInFlight] = useState(false);

  // Relay for phone → Groups overlay. Each drained groups command bumps
  // the nonce so GroupsButton applies it exactly once.
  const groupsNonce = useRef(0);
  const [groupsAction, setGroupsAction] = useState<GroupsRemoteAction | undefined>();
  const bumpGroups = useCallback((a: Omit<GroupsRemoteAction, "nonce">) => {
    groupsNonce.current += 1;
    setGroupsAction({ ...a, nonce: groupsNonce.current });
  }, []);

  // Parse prompt into intro + ordered questions, plus extensions as a group.
  const parts = useMemo(() => parsePrompt(studentPrompt), [studentPrompt]);
  const extensionItems = useMemo(() => parseBulletedList(extensions), [extensions]);

  // Build keyed lists. Main questions render with their original numbering
  // (1., 2., ...). Extensions show as "Ext 1", "Ext 2".
  const mainKeyed: KeyedQ[] = useMemo(() => {
    return parts.questions.map((text, i) => {
      // Strip a leading "1." prefix so we can re-prefix consistently.
      const stripped = text.replace(/^\s*\d+\.\s*/, "");
      return {
        key: `m-${i}`,
        group: "main",
        groupIndex: i + 1,
        displayLabel: `${i + 1}.`,
        text: stripped,
      };
    });
  }, [parts.questions]);

  const extKeyed: KeyedQ[] = useMemo(() => {
    return extensionItems.map((text, i) => ({
      key: `e-${i}`,
      group: "extension",
      groupIndex: i + 1,
      displayLabel: `Ext ${i + 1}.`,
      text,
    }));
  }, [extensionItems]);

  // The full ordered list, minus excluded keys. Drives the reveal stack.
  const visibleAll: KeyedQ[] = useMemo(
    () => [...mainKeyed, ...extKeyed].filter((q) => !excludedKeys.has(q.key)),
    [mainKeyed, extKeyed, excludedKeys]
  );
  const total = visibleAll.length;
  const canAdvance = revealedCount < total;
  const canRetreat = revealedCount > 1;
  // Snap revealedCount back if filtering reduced visible below current pointer.
  useEffect(() => {
    if (revealedCount > total && total > 0) setRevealedCount(total);
    if (total === 0) setRevealedCount(1);
  }, [revealedCount, total]);

  // Sliding window: show the `windowSize` most-recent questions ending at
  // `revealedCount`. Earlier ones fall off so the projection stays focused.
  const revealEnd = Math.max(1, revealedCount);
  const revealStart = Math.max(0, revealEnd - windowSize);
  const revealed = visibleAll.slice(revealStart, revealEnd);

  const exit = useCallback(() => {
    router.push(`/math/rich-tasks/${taskId}`);
  }, [router, taskId]);

  const advance = useCallback(() => {
    setRevealedCount((n) => Math.min(total, n + 1));
  }, [total]);

  const retreat = useCallback(() => {
    setRevealedCount((n) => Math.max(1, n - 1));
  }, []);

  // ─── Apply a phone command ────────────────────────────────────────
  // Each `RemoteCommand` maps onto one of the existing setters. Drained
  // from the heartbeat response and dispatched here.
  const applyCommand = useCallback(
    (cmd: RemoteCommand) => {
      switch (cmd.type) {
        case "advance":
          advance();
          break;
        case "retreat":
          retreat();
          break;
        case "set-theme":
          setThemeId(cmd.themeId);
          break;
        case "set-window-size":
          setWindowSize(cmd.size);
          break;
        case "toggle-drawing":
          setDrawing(cmd.on);
          break;
        case "set-timer-visible":
          setTimerOpen(cmd.visible);
          break;
        case "timer-set-duration":
          setTimerDuration(cmd.seconds);
          setTimerRemaining(cmd.seconds);
          break;
        case "timer-set-running":
          setTimerRunning(cmd.running);
          break;
        case "timer-reset":
          setTimerRemaining(timerDuration);
          setTimerRunning(false);
          break;
        case "groups-open":
          bumpGroups({ type: "open" });
          break;
        case "groups-close":
          bumpGroups({ type: "close" });
          break;
        case "groups-form-class":
          bumpGroups({ type: "form-class", classId: cmd.classId });
          break;
        case "groups-reshuffle":
          bumpGroups({ type: "reshuffle" });
          break;
        case "groups-clear":
          bumpGroups({ type: "clear" });
          break;
      }
    },
    [advance, retreat, timerDuration, bumpGroups]
  );

  // ─── Connect / disconnect from phone ───────────────────────────────
  const startConnect = useCallback(async () => {
    if (connectInFlight || roomCode) {
      // Already connected — re-open the modal so the code is visible.
      setConnectModalOpen(true);
      return;
    }
    setConnectInFlight(true);
    try {
      const initialState: ProjectionState = {
        taskId,
        totalQuestions: parts.questions.length,
        revealedCount,
        windowSize,
        themeId,
        drawing,
        timer: {
          visible: timerOpen,
          durationSec: timerDuration,
          remainingSec: timerRemaining,
          running: timerRunning,
        },
        ...groupsBroadcast(),
      };
      const res = await fetch("/api/remote/connect-projection", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ taskId, initialState }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = (await res.json()) as ConnectProjectionResponse;
      setRoomCode(data.code);
      setProjectionToken(data.projectionToken);
      setConnectModalOpen(true);
    } catch (e) {
      console.error("Failed to mint room", e);
    } finally {
      setConnectInFlight(false);
    }
  }, [
    connectInFlight,
    roomCode,
    taskId,
    parts.questions.length,
    revealedCount,
    windowSize,
    themeId,
    drawing,
    timerOpen,
    timerDuration,
    timerRemaining,
    timerRunning,
  ]);

  const endConnect = useCallback(async () => {
    if (!roomCode || !projectionToken) return;
    try {
      await fetch("/api/remote/disconnect-projection", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: roomCode, projectionToken }),
      });
    } catch {
      // best-effort; the server-side sweeper will also expire stale rooms
    }
    setRoomCode(null);
    setProjectionToken(null);
    setPhonePaired(false);
    setConnectModalOpen(false);
  }, [roomCode, projectionToken]);

  // ─── Heartbeat refs ────────────────────────────────────────────────
  // The heartbeat interval needs to read the LATEST state every tick,
  // not the values captured when the effect was set up. We mirror the
  // state-builder and the command applier into refs that we update on
  // every render; the interval reads from them.
  const buildState = useCallback(
    (): ProjectionState => ({
      taskId,
      totalQuestions: parts.questions.length,
      revealedCount,
      windowSize,
      themeId,
      drawing,
      timer: {
        visible: timerOpen,
        durationSec: timerDuration,
        remainingSec: timerRemaining,
        running: timerRunning,
      },
      ...groupsBroadcast(),
    }),
    [
      taskId,
      parts.questions.length,
      revealedCount,
      windowSize,
      themeId,
      drawing,
      timerOpen,
      timerDuration,
      timerRemaining,
      timerRunning,
    ]
  );
  const buildStateRef = useRef(buildState);
  const applyCommandRef = useRef(applyCommand);
  useEffect(() => { buildStateRef.current = buildState; }, [buildState]);
  useEffect(() => { applyCommandRef.current = applyCommand; }, [applyCommand]);

  // ─── Heartbeat effect ──────────────────────────────────────────────
  // Lives for the duration that a room is open. Posts ~1Hz; applies any
  // pending commands; updates `phonePaired` from the response.
  useEffect(() => {
    if (!roomCode || !projectionToken) return;
    let cancelled = false;
    const tick = async () => {
      try {
        const state = buildStateRef.current();
        const res = await fetch("/api/remote/heartbeat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code: roomCode, projectionToken, state }),
        });
        if (!res.ok || cancelled) return;
        const data = (await res.json()) as HeartbeatResponse;
        if (cancelled) return;
        if (!data.alive) {
          // Server says the room is gone. Clean up local state so the
          // teacher can connect again.
          setRoomCode(null);
          setProjectionToken(null);
          setPhonePaired(false);
          setConnectModalOpen(false);
          return;
        }
        setPhonePaired(data.phonePaired);
        for (const cmd of data.pendingCommands) applyCommandRef.current(cmd);
      } catch {
        // Network blip — ignore, next tick will retry.
      }
    };
    // Fire one immediately so the room's first state lands without waiting
    // a full second after Connect.
    void tick();
    const id = setInterval(tick, 1000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [roomCode, projectionToken]);

  // Idle-fade controls
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | null = null;
    const reset = () => {
      setControlsVisible(true);
      if (timer) clearTimeout(timer);
      timer = setTimeout(() => setControlsVisible(false), 3000);
    };
    reset();
    window.addEventListener("mousemove", reset);
    window.addEventListener("keydown", reset);
    return () => {
      window.removeEventListener("mousemove", reset);
      window.removeEventListener("keydown", reset);
      if (timer) clearTimeout(timer);
    };
  }, []);

  // Keyboard: ESC exit, ←/→ step, D toggle whiteboard.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      // While drawing, the overlay owns Esc (to exit drawing, not the page).
      if (drawing) return;
      if (e.key === "Escape") exit();
      else if (e.key === "ArrowRight" || e.key === " ") {
        e.preventDefault();
        advance();
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        retreat();
      } else if (e.key.toLowerCase() === "d") {
        setDrawing(true);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [advance, retreat, exit, drawing]);

  // Hide site header/footer
  useEffect(() => {
    document.body.classList.add("project-mode");
    return () => {
      document.body.classList.remove("project-mode");
    };
  }, []);

  // Sizing strategy: scale every text size by `density` so that as more
  // content accumulates (long intros, tables, multiple revealed questions)
  // the layout still fits without clipping the title or the bottom question.
  //
  // We combine two signals:
  //   1) revealedN — how many question cards are stacked
  //   2) introWeight — a rough measure of how much vertical space the intro
  //      eats (long prose + tables are the main offenders, as in
  //      Lightning Distance which pairs a multi-sentence intro with a 4-row
  //      table). Tables consume far more vertical space per character than
  //      prose, so each table row is weighted heavily.
  // Measured fit-to-height. The density heuristic below is a first guess;
  // this correction measures the ACTUAL rendered column and shrinks (or
  // restores) the scale so content never clips at 100% zoom, no matter how
  // heavy the intro/table/question stack is.
  const colRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const [fitScale, setFitScale] = useState(1);

  const revealedN = revealed.length;
  const introWeight = useMemo(() => {
    const intro = parts.intro ?? "";
    if (!intro) return 0;
    let weight = intro.length; // ~1 unit per char of prose
    const lines = intro.split("\n");
    // Each markdown-table data row eats roughly an additional 40-char line of
    // vertical space when rendered (header, separator, plus its own row).
    for (const ln of lines) {
      const t = ln.trim();
      if (t.startsWith("|") && t.endsWith("|")) weight += 40;
    }
    // Long titles wrap to two lines on most projection widths; give those
    // tasks a bit more breathing room by treating the title like extra intro.
    if (title.length > 28) weight += 80;
    return weight;
  }, [parts.intro, title]);

  // Map revealedN → base density. This is the floor that the QUESTION
  // text always renders at — students need the question they're solving
  // at a TV-readable size regardless of how much context the intro
  // carries. The intro absorbs the intro-length penalty separately.
  const baseDensity =
    revealedN <= 1 ? 1.0 :
    revealedN === 2 ? 0.82 :
    revealedN === 3 ? 0.62 :
    revealedN === 4 ? 0.52 :
    revealedN === 5 ? 0.45 :
    0.4;
  // Intro-length penalty. Only applies to the intro itself (and a small
  // share to the title). Decoupling this from the question density is
  // the fix for "the question feels tiny on tasks like mini-golf
  // blueprint / hotel night / Mira's drone" — those tasks have a heavy
  // intro but short questions, and the old combined penalty was making
  // the QUESTION text shrink to ~16-18px on a 1080p TV. Now the intro
  // shrinks; the question stays readable.
  const introPenalty =
    introWeight <= 180 ? 1.0 :
    introWeight <= 320 ? 0.88 :
    introWeight <= 500 ? 0.78 :
    introWeight <= 800 ? 0.68 :
    0.58;
  // Three separate density values: the question stays at baseDensity, the
  // intro shrinks with intro weight, the title takes a mild share of the
  // intro penalty (so it doesn't dominate when the intro is long).
  // fitScale (measured below) folds into every density so the whole column
  // shrinks to fit when the heuristic underestimates the real height.
  const questionDensity = baseDensity * fitScale;
  const introDensity = Math.max(0.5, baseDensity * introPenalty) * fitScale;
  const titleDensity = baseDensity * Math.max(0.85, introPenalty) * fitScale;
  // Anchor the column to the top ONLY when several question cards are
  // stacked. Heavy-intro tasks (mini-golf blueprint, hotel night) stay
  // centered at revealedN ≤ 2 so the layout feels consistent with the
  // light-intro tasks. The column will naturally drift toward the top
  // as more cards reveal — that's expected.
  const anchorTop = revealedN >= 3;

  const scaleAt = (d: number) => (lo: number, vw: number, hi: number) =>
    `clamp(${(lo * d).toFixed(2)}rem, ${(vw * d).toFixed(2)}vw, ${(hi * d).toFixed(2)}rem)`;

  // Title scales a touch more aggressively at the high end so long titles
  // ("Lightning Distance Estimator", "Equation from Two Bus Stops") don't
  // dominate the viewport.
  const titleScale = title.length > 28 ? 0.85 : 1.0;
  const titleFs = scaleAt(titleDensity)(2.0 * titleScale, 4.4 * titleScale, 4.0 * titleScale);
  const introFs = scaleAt(introDensity)(1.25, 2.4, 2);
  const questionFs = scaleAt(questionDensity)(1.5, 2.6, 2.25);
  const labelFs = "0.7em";

  // Measure the rendered content column against its available height and nudge
  // fitScale so the whole task always fits without clipping — the guarantee the
  // character-count heuristic alone can't make. Runs after layout (pre-paint)
  // and re-measures on viewport/theme resize; converges in a couple passes via
  // the 0.02 tolerance. SSR-safe: fitScale defaults to 1 (current behaviour).
  useLayoutEffect(() => {
    const col = colRef.current;
    const content = contentRef.current;
    if (!col || !content) return;
    const measure = () => {
      const avail = col.clientHeight;
      const natural = content.getBoundingClientRect().height;
      if (avail <= 0 || natural <= 0) return;
      const ratio = avail / natural;
      setFitScale((prev) => {
        let next = prev;
        if (ratio < 1) next = prev * ratio * 0.98; // overflowing → shrink to fit
        else if (ratio > 1.06 && prev < 1) next = prev * ratio * 0.98; // room freed → grow back
        next = Math.max(0.35, Math.min(1, next));
        return Math.abs(next - prev) > 0.02 ? next : prev;
      });
    };
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(col);
    return () => ro.disconnect();
  }, [revealedN, parts.intro, title, baseDensity, introPenalty, image, fitScale]);

  return (
    <div
      className={`fixed inset-0 flex h-screen w-screen flex-col overflow-hidden transition-colors ${theme.textClass}`}
      style={{ background: theme.background }}
    >
      {theme.pattern && (
        <div
          className="pointer-events-none absolute inset-0 z-0"
          style={{ backgroundImage: theme.pattern, backgroundRepeat: "repeat" }}
        />
      )}
      {/* Top control bar. z is intentionally above the DrawingOverlay SVG
          (z-200) so when drawing is active, hovering the chrome controls
          shows the normal pointer cursor instead of the draw crosshair. */}
      <div
        className={`relative z-[220] flex shrink-0 items-center justify-between gap-4 px-6 py-2 transition-opacity duration-500 ${
          controlsVisible ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
      >
        <div className={`flex items-center gap-3 text-sm ${isDark ? "text-white/70" : "text-pnp-gray-600"}`}>
          {/* Title is the drawer trigger */}
          <button
            onClick={() => setDrawerOpen(true)}
            className={`group flex items-center gap-1.5 rounded-md px-2 py-1 font-heading text-base font-bold transition-colors ${
              isDark ? "hover:bg-white/10" : "hover:bg-pnp-gray-100"
            }`}
            title="Choose which questions to show"
          >
            {title}
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="opacity-50 group-hover:opacity-100"
              aria-hidden="true"
            >
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
            </svg>
          </button>

        </div>

        <div className="flex items-center gap-2">
          {/* Theme: Light / Dark / Polka / Underwater / Chalkboard */}
          <div
            className={`flex rounded-lg border ${
              isDark ? "border-white/20 bg-white/5" : "border-pnp-gray-300 bg-white"
            }`}
            role="radiogroup"
            aria-label="Theme"
          >
            {THEME_ORDER.map((id, i) => (
              <button
                key={id}
                role="radio"
                aria-checked={themeId === id}
                onClick={() => setThemeId(id)}
                className={`px-2.5 py-1.5 text-sm font-semibold transition-colors ${
                  i === 0 ? "rounded-l-lg" : ""
                } ${i === THEME_ORDER.length - 1 ? "rounded-r-lg" : ""} ${
                  themeId === id
                    ? isDark ? "bg-white/20 text-white" : "bg-pnp-navy text-white"
                    : isDark ? "text-white/70 hover:bg-white/10" : "text-pnp-gray-700 hover:bg-pnp-gray-100"
                }`}
                title={PROJECTION_THEMES[id].label}
              >
                {PROJECTION_THEMES[id].label}
              </button>
            ))}
          </div>
          <button
            onClick={() => {
              if (roomCode) {
                // Already minted — re-open modal so the code is visible.
                setConnectModalOpen(true);
              } else {
                void startConnect();
              }
            }}
            aria-pressed={!!roomCode}
            disabled={connectInFlight}
            className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-semibold transition-colors ${
              phonePaired
                ? "bg-pnp-green text-white"
                : roomCode
                  ? "bg-pnp-yellow text-pnp-navy"
                  : isDark
                    ? "bg-white/10 text-white hover:bg-white/20"
                    : "bg-pnp-gray-100 text-pnp-gray-700 hover:bg-pnp-gray-200"
            } ${connectInFlight ? "opacity-50" : ""}`}
            title={
              phonePaired
                ? "Phone connected — click to view code"
                : roomCode
                  ? "Waiting for phone — click to view code"
                  : "Connect your phone as a remote"
            }
          >
            <PhoneIcon />
            <span>
              {phonePaired ? "Connected" : roomCode ? "Waiting…" : "Connect"}
            </span>
          </button>

          <button
            onClick={() => setTimerOpen((t) => !t)}
            aria-pressed={timerOpen}
            className={`rounded-lg px-3 py-1.5 text-sm font-semibold transition-colors ${
              timerOpen
                ? "bg-pnp-yellow text-pnp-navy"
                : isDark
                  ? "bg-white/10 text-white hover:bg-white/20"
                  : "bg-pnp-gray-100 text-pnp-gray-700 hover:bg-pnp-gray-200"
            }`}
            title="Toggle classroom timer"
          >
            Timer
          </button>

          <button
            onClick={() => setDrawing((d) => !d)}
            aria-pressed={drawing}
            className={`rounded-lg px-3 py-1.5 text-sm font-semibold transition-colors ${
              drawing
                ? "bg-pnp-yellow text-pnp-navy"
                : isDark
                  ? "bg-white/10 text-white hover:bg-white/20"
                  : "bg-pnp-gray-100 text-pnp-gray-700 hover:bg-pnp-gray-200"
            }`}
            title="Draw on the projection (D)"
          >
            {drawing ? "Drawing…" : "Draw"}
          </button>

          <GroupsButton isDark={isDark} remoteAction={groupsAction} />

          <button
            onClick={exit}
            className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-semibold transition-colors ${
              isDark
                ? "bg-white/10 text-white hover:bg-white/20"
                : "bg-pnp-gray-100 text-pnp-gray-700 hover:bg-pnp-gray-200"
            }`}
            title="Exit (ESC)"
          >
            <XIcon />
            <span>Exit</span>
          </button>
        </div>
      </div>

      {/* Main content area */}
      <div className="relative z-10 flex min-h-0 flex-1 flex-col px-8 pb-20 md:px-12">
        <div className={`flex min-h-0 flex-1 gap-8 ${image ? "lg:gap-12" : ""}`}>
          {/* LEFT: title + intro + accumulating questions. Centered vertically
              when content is light; anchored to top when intro is heavy or
              several questions are revealed (otherwise the flex centering
              would push the title above the chrome bar). */}
          <div
            ref={colRef}
            className={`flex min-h-0 flex-col overflow-hidden ${
              anchorTop ? "justify-start pt-1" : "justify-center"
            } ${image ? "lg:w-[64%]" : "w-full"}`}
          >
            <div ref={contentRef}>
            <h1
              className="font-heading font-extrabold leading-tight"
              style={{ fontSize: titleFs }}
            >
              {title}
            </h1>

            {parts.intro && (
              <div
                className={`mt-3 font-sans leading-snug ${
                  isDark ? "text-white/90" : "text-pnp-gray-800"
                }`}
                style={{ fontSize: introFs }}
              >
                <MarkdownText
                  text={parts.intro}
                  density={introDensity}
                  isDark={isDark}
                  style={{ fontSize: introFs }}
                />
              </div>
            )}

            {/* Stack of revealed questions. Newest gets accent ring; older
                ones dim slightly (rolodex-style). Display labels are
                renumbered from the visible (filtered) list, so students see
                clean sequential numbering even when the teacher has hidden
                some questions. Vertical gap shrinks with density so 4+
                questions still fit cleanly in the viewport. */}
            <div
              className="mt-3 flex flex-col"
              style={{ gap: `${(0.75 * questionDensity).toFixed(2)}rem` }}
            >
              {(() => {
                // Renumber: walk the FULL visibleAll list so labels reflect
                // each question's true position (1., 2., 3., Ext 1., …), then
                // slice the labels down to the sliding window. Without this
                // pass, Q2 would mislabel as "1." when Q1 falls off the window.
                const labels: string[] = [];
                let mainCount = 0;
                let extCount = 0;
                for (const q of visibleAll) {
                  if (q.group === "main") {
                    mainCount += 1;
                    labels.push(`${mainCount}.`);
                  } else {
                    extCount += 1;
                    labels.push(`Ext ${extCount}.`);
                  }
                }
                const windowLabels = labels.slice(revealStart, revealEnd);
                return revealed.map((q, idx) => {
                  const isNewest = idx === revealed.length - 1;
                  const isExtension = q.group === "extension";
                  return { q, idx, label: windowLabels[idx] ?? "", isNewest, isExtension };
                });
              })().map(({ q, idx, label, isNewest, isExtension }) => {
                // Older entries dim a bit — keeps the newest as the focal point
                // while everything stays the same size and readable.
                const opacity = isNewest ? 1 : Math.max(0.6, 1 - 0.08 * (revealed.length - 1 - idx));

                // Extension styling: gentle yellow accent. Main: blue accent
                // when newest. Both use a left border for the rolodex feel.
                const borderColor = isExtension
                  ? isDark ? "border-yellow-400" : "border-yellow-500"
                  : isDark ? "border-pnp-yellow/70" : "border-pnp-blue";
                const ringClass = isNewest
                  ? isExtension
                    ? "ring-2 ring-yellow-400/40"
                    : isDark ? "ring-2 ring-pnp-yellow/40" : "ring-2 ring-pnp-blue/30"
                  : "";

                return (
                  <div
                    key={q.key}
                    className={`thin-task-question rounded-xl border-l-8 transition-all ${borderColor} ${
                      isExtension
                        ? isDark ? "bg-white/5" : "bg-yellow-50"
                        : isDark ? "bg-white/5" : "bg-pnp-gray-50"
                    } ${ringClass}`}
                    style={{
                      opacity,
                      // Padding shrinks with density so 4+ stacked cards
                      // don't run off the viewport.
                      paddingLeft: `${(1.25 * questionDensity).toFixed(2)}rem`,
                      paddingRight: `${(1.25 * questionDensity).toFixed(2)}rem`,
                      paddingTop: `${(0.75 * questionDensity).toFixed(2)}rem`,
                      paddingBottom: `${(0.75 * questionDensity).toFixed(2)}rem`,
                    }}
                  >
                    <div className="flex items-baseline gap-2">
                      <span
                        className={`shrink-0 font-mono font-bold ${
                          isExtension
                            ? isDark ? "text-yellow-300" : "text-yellow-700"
                            : isDark ? "text-pnp-yellow" : "text-pnp-blue"
                        }`}
                        style={{ fontSize: labelFs }}
                      >
                        {label}
                      </span>
                      <div
                        className={`min-w-0 flex-1 font-sans font-medium leading-snug ${
                          isDark ? "text-white" : "text-pnp-gray-900"
                        }`}
                        style={{ fontSize: questionFs }}
                      >
                        <MarkdownText
                          text={q.text}
                          density={questionDensity}
                          isDark={isDark}
                          style={{ fontSize: questionFs }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
            </div>
          </div>

          {/* RIGHT: image (SVG, URL, or interactive 3D) */}
          {image && (
            <div className="hidden min-h-0 shrink-0 items-center justify-center lg:flex lg:w-[36%]">
              <div className="flex h-full w-full items-center justify-center">
                {image.kind === "interactive" && image.component ? (
                  // Slightly taller than wide (4:5) so the cube has extra
                  // vertical headroom for diagonal-vertex rotations without
                  // making the canvas spill outside the right column.
                  <div className="aspect-[4/5] w-full max-w-[95%]">
                    <InteractiveImage component={image.component} />
                  </div>
                ) : image.svg ? (
                  <div
                    data-task-image-svg
                    data-theme={isDark ? "dark" : "light"}
                    className="task-image-svg flex h-full w-full items-center justify-center [&>svg]:h-auto [&>svg]:max-h-full [&>svg]:w-auto [&>svg]:max-w-full"
                    aria-label={image.alt}
                    role="img"
                    dangerouslySetInnerHTML={{ __html: image.svg }}
                  />
                ) : image.url ? (
                  // Photo frame: 3px brand-yellow border + rounded corners +
                  // soft drop shadow. Reads as "intentional artifact" on every
                  // theme without overpowering the photo itself.
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={image.url}
                    alt={image.alt}
                    className="max-h-full max-w-full rounded-2xl border-[3px] border-pnp-yellow object-contain shadow-2xl"
                  />
                ) : null}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Bottom step controls. Above the SVG (z-200) so the cursor is
          pointer over Back/Next even when drawing is on. */}
      {total > 0 && (
        <div className="absolute inset-x-0 bottom-0 z-[220] flex items-center justify-center gap-4 pb-5">
          {/* Slide number + standard live down here, off the busy top bar
              (the word "Investigation" and the time estimate were dropped
              entirely — they were teacher-facing noise for students). */}
          <div
            className={`pointer-events-none absolute left-6 bottom-5 hidden items-center gap-2 text-sm font-semibold sm:flex ${
              isDark ? "text-white/60" : "text-pnp-gray-500"
            }`}
          >
            {primaryStandard && <span>{primaryStandard}</span>}
            {primaryStandard && <span className="opacity-40">•</span>}
            <span className="font-mono">
              {Math.min(revealedCount, total)} / {total}
            </span>
          </div>
          <button
            onClick={retreat}
            disabled={!canRetreat}
            className={`rounded-full px-5 py-2.5 text-base font-semibold transition-all ${
              canRetreat
                ? isDark ? "bg-white/10 text-white hover:bg-white/20" : "bg-pnp-gray-200 text-pnp-gray-800 hover:bg-pnp-gray-300"
                : "cursor-not-allowed opacity-30"
            }`}
            title="Previous question (←)"
          >
            ← Back
          </button>

          <div className="flex items-center gap-1.5">
            {visibleAll.map((_, i) => (
              <span
                key={i}
                className={`h-2.5 w-2.5 rounded-full transition-all ${
                  i < revealedCount
                    ? isDark ? "bg-white" : "bg-pnp-navy"
                    : isDark ? "bg-white/20" : "bg-pnp-gray-300"
                }`}
              />
            ))}
          </div>

          <button
            onClick={advance}
            disabled={!canAdvance}
            className={`rounded-full px-6 py-2.5 text-base font-bold transition-all ${
              canAdvance
                ? isDark ? "bg-pnp-yellow text-pnp-navy hover:bg-pnp-yellow-dark" : "bg-pnp-navy text-white hover:bg-pnp-blue"
                : "cursor-not-allowed bg-pnp-gray-200 text-pnp-gray-500"
            }`}
            title="Next question (→ or space)"
          >
            {canAdvance ? "Next →" : "Done"}
          </button>
        </div>
      )}

      <div
        className={`pointer-events-none absolute right-6 top-14 z-10 text-xs transition-opacity duration-500 ${
          controlsVisible ? "opacity-50" : "opacity-0"
        } ${isDark ? "text-white/60" : "text-pnp-gray-500"}`}
      >
        ← / → step • ESC exit
      </div>

      {/* Drawer */}
      {drawerOpen && (
        <QuestionDrawer
          mainQ={mainKeyed}
          extQ={extKeyed}
          excludedKeys={excludedKeys}
          setExcludedKeys={setExcludedKeys}
          windowSize={windowSize}
          setWindowSize={setWindowSize}
          isDark={isDark}
          onClose={() => setDrawerOpen(false)}
        />
      )}

      {/* Whiteboard overlay. wipeKey changes whenever the visible question
          set changes (revealedCount, picker filter, task id), so each
          fresh question starts with a clean board. */}
      <DrawingOverlay
        active={drawing}
        setActive={setDrawing}
        wipeKey={`${taskId}-${revealedCount}-${excludedKeys.size}`}
      />

      {/* Draggable classroom timer. Toggle via the "Timer" button in the
          chrome bar. Shared component with the thin-slice projection so any
          behavior change applies in both places. The controller props lift
          its state up into ProjectionView so the phone-as-remote can both
          read it via heartbeat and drive it via commands. */}
      <TimerOverlay
        visible={timerOpen}
        onClose={() => setTimerOpen(false)}
        isDark={isDark}
        controller={timerController}
      />

      {/* Phone-as-remote pairing modal. Opens when teacher clicks
          📱 Connect in the chrome bar. */}
      {connectModalOpen && roomCode && (
        <RemoteConnectModal
          code={roomCode}
          phonePaired={phonePaired}
          isDark={isDark}
          onClose={() => setConnectModalOpen(false)}
          onDisconnect={() => void endConnect()}
        />
      )}
    </div>
  );
}

// =====================
// QUESTION PICKER DRAWER
// =====================
function QuestionDrawer({
  mainQ,
  extQ,
  excludedKeys,
  setExcludedKeys,
  windowSize,
  setWindowSize,
  isDark,
  onClose,
}: {
  mainQ: KeyedQ[];
  extQ: KeyedQ[];
  excludedKeys: Set<string>;
  setExcludedKeys: (s: Set<string>) => void;
  windowSize: 1 | 2 | 3;
  setWindowSize: (n: 1 | 2 | 3) => void;
  isDark: boolean;
  onClose: () => void;
}) {
  const toggle = (key: string) => {
    const next = new Set(excludedKeys);
    if (next.has(key)) next.delete(key);
    else next.add(key);
    setExcludedKeys(next);
  };
  const allKeys = [...mainQ, ...extQ].map((q) => q.key);
  const allChecked = allKeys.every((k) => !excludedKeys.has(k));
  const reset = () => setExcludedKeys(new Set());
  const noneAll = () => setExcludedKeys(new Set(allKeys));

  // ESC closes the drawer
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const visibleCount = allKeys.filter((k) => !excludedKeys.has(k)).length;

  const panelBg = isDark ? "bg-pnp-navy text-white" : "bg-white text-pnp-gray-900";
  const dividerColor = isDark ? "border-white/10" : "border-pnp-gray-200";
  const subtle = isDark ? "text-white/60" : "text-pnp-gray-500";
  const stepBorder = isDark ? "border-white/10" : "border-pnp-gray-200";
  const stepHover = isDark ? "hover:bg-white/5" : "hover:bg-pnp-gray-50";

  return (
    <>
      <div
        onClick={onClose}
        className="fixed inset-0 z-[230] bg-black/40"
        aria-hidden="true"
      />
      <aside
        role="dialog"
        aria-label="Choose questions"
        className={`fixed left-0 top-0 z-[240] flex h-full w-[360px] flex-col shadow-2xl ${panelBg} animate-rich-task-drawer`}
      >
        <div className={`flex shrink-0 items-center justify-between border-b ${dividerColor} px-5 py-4`}>
          <div>
            <div className="font-heading text-lg font-bold">Choose Questions</div>
            <div className={`text-xs ${subtle}`}>
              {visibleCount} of {allKeys.length} will show
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Close"
            className={`inline-flex items-center rounded-lg px-3 py-1.5 text-sm font-semibold transition-colors ${
              isDark ? "bg-white/10 text-white hover:bg-white/20" : "bg-pnp-gray-100 text-pnp-gray-700 hover:bg-pnp-gray-200"
            }`}
            title="Close (ESC)"
          >
            <XIcon />
          </button>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto px-5 py-4">
          {/* SHOW window size — how many of the most-recently revealed
              questions stay on the projection at once. Defaults to 2 so the
              teacher sees a question + the previous one for context. */}
          <div className="mb-5">
            <div className={`text-xs font-bold uppercase tracking-wider ${subtle}`}>Show at a time</div>
            <div
              className={`mt-2 inline-flex rounded-lg border ${stepBorder}`}
              role="radiogroup"
              aria-label="Show at a time"
            >
              {[1, 2, 3].map((n, i) => (
                <button
                  key={n}
                  role="radio"
                  aria-checked={windowSize === n}
                  onClick={() => setWindowSize(n as 1 | 2 | 3)}
                  className={`px-4 py-1.5 text-sm font-semibold transition-colors ${
                    i === 0 ? "rounded-l-lg" : ""
                  } ${i === 2 ? "rounded-r-lg" : ""} ${
                    windowSize === n
                      ? isDark ? "bg-white/20 text-white" : "bg-pnp-navy text-white"
                      : isDark ? "text-white/70 hover:bg-white/10" : "text-pnp-gray-700 hover:bg-pnp-gray-100"
                  }`}
                  title={`Show ${n} at a time`}
                >
                  {n}
                </button>
              ))}
            </div>
            <div className={`mt-1.5 text-xs ${subtle}`}>
              The window slides as you advance — only the {windowSize} most
              recent stay on screen.
            </div>
          </div>

          {mainQ.length > 0 && (
            <>
              <div className={`text-xs font-bold uppercase tracking-wider ${subtle}`}>Main Questions</div>
              <ul className={`mt-2 space-y-1 rounded-lg border ${stepBorder} p-1`}>
                {mainQ.map((q) => (
                  <QuestionRow
                    key={q.key}
                    q={q}
                    checked={!excludedKeys.has(q.key)}
                    onToggle={() => toggle(q.key)}
                    hoverClass={stepHover}
                    isDark={isDark}
                  />
                ))}
              </ul>
            </>
          )}

          {extQ.length > 0 && (
            <>
              <div className="mt-5">
                <div className={`text-xs font-bold uppercase tracking-wider ${subtle}`}>Extensions</div>
              </div>
              <ul className={`mt-2 space-y-1 rounded-lg border ${stepBorder} p-1`}>
                {extQ.map((q) => (
                  <QuestionRow
                    key={q.key}
                    q={q}
                    checked={!excludedKeys.has(q.key)}
                    onToggle={() => toggle(q.key)}
                    hoverClass={stepHover}
                    isDark={isDark}
                  />
                ))}
              </ul>
            </>
          )}
        </div>

        <div className={`flex shrink-0 items-center justify-between gap-2 border-t ${dividerColor} px-5 py-3`}>
          <button
            onClick={reset}
            disabled={allChecked}
            className={`text-sm font-semibold transition-colors ${
              allChecked
                ? "cursor-not-allowed opacity-30"
                : isDark ? "text-pnp-yellow hover:underline" : "text-pnp-blue hover:underline"
            }`}
          >
            Reset to all
          </button>
          <button
            onClick={noneAll}
            className={`text-sm font-semibold transition-colors ${
              isDark ? "text-white/60 hover:text-white" : "text-pnp-gray-500 hover:text-pnp-gray-700"
            }`}
          >
            Uncheck all
          </button>
        </div>
      </aside>

      <style>{`
        @keyframes rich-task-drawer-in {
          from { transform: translateX(-100%); }
          to   { transform: translateX(0); }
        }
        .animate-rich-task-drawer {
          animation: rich-task-drawer-in 220ms cubic-bezier(0.22, 1, 0.36, 1) both;
        }
      `}</style>
    </>
  );
}

function QuestionRow({
  q,
  checked,
  onToggle,
  hoverClass,
  isDark,
}: {
  q: KeyedQ;
  checked: boolean;
  onToggle: () => void;
  hoverClass: string;
  isDark: boolean;
}) {
  return (
    <li>
      <label
        className={`flex cursor-pointer items-start gap-3 rounded-md px-2 py-1.5 transition-colors ${hoverClass}`}
      >
        <input
          type="checkbox"
          checked={checked}
          onChange={onToggle}
          className="mt-0.5 h-4 w-4 shrink-0 cursor-pointer accent-pnp-blue"
        />
        <span
          className={`shrink-0 font-mono text-xs ${isDark ? "text-white/40" : "text-pnp-gray-500"}`}
          aria-hidden="true"
        >
          {q.displayLabel}
        </span>
        <span className="flex-1 text-sm line-clamp-2">{q.text}</span>
      </label>
    </li>
  );
}

// ─────────────────────────────────────────────────────────────────────
// Inline Lucide-style icons used by the chrome bar. Replaced the 📱 and
// ✕ emojis that were sitting in user-facing chrome.
// ─────────────────────────────────────────────────────────────────────

function PhoneIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="5" y="2" width="14" height="20" rx="2" ry="2" />
      <line x1="12" y1="18" x2="12.01" y2="18" />
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
