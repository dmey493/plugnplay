"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Optional external controller. When provided, the timer is fully
 * controlled by the parent — `duration` / `remaining` / `running` come
 * from props and every mutation goes through `set()`. When absent, the
 * timer uses its own internal state (the original standalone behaviour).
 *
 * This is what lets the phone-as-remote work: `ProjectionView` lifts
 * timer state into itself, broadcasts it via heartbeat, and applies
 * phone commands by writing back through `set()`.
 */
export interface TimerController {
  duration: number;
  remaining: number;
  running: boolean;
  set: (
    patch: Partial<{ duration: number; remaining: number; running: boolean }>
  ) => void;
}

interface Props {
  visible: boolean;
  /** Kept for parity with old callers; no longer surfaced as a button in
   *  the header — teachers toggle the timer via the chrome "Timer" button. */
  onClose?: () => void;
  isDark: boolean;
  /** Optional external controller. See `TimerController` above. */
  controller?: TimerController;
}

/**
 * A draggable classroom countdown timer overlay for the projection view.
 * Click the time to type a new duration (MM:SS or HH:MM:SS). Start/Pause +
 * Reset. Plays a short beep at 0. Position is preserved between toggles.
 *
 * The chrome header is the drag handle; clicks on inputs or buttons don't
 * start a drag.
 */
export default function TimerOverlay({ visible, isDark, controller }: Props) {
  // Position is a `{x, y}` offset from the viewport origin. Survives toggle.
  const [position, setPosition] = useState({ x: 32, y: 96 });
  // Internal-state fallback. Unused when `controller` is supplied.
  const [internalDuration, setInternalDuration] = useState(300);
  const [internalRemaining, setInternalRemaining] = useState(300);
  const [internalRunning, setInternalRunning] = useState(false);
  const [editing, setEditing] = useState(false);

  // Bridge: read effective state from controller-or-internal, write via
  // a single `apply()` helper so the rest of the component is uniform.
  const duration = controller ? controller.duration : internalDuration;
  const remaining = controller ? controller.remaining : internalRemaining;
  const running = controller ? controller.running : internalRunning;
  const apply = (
    patch: Partial<{ duration: number; remaining: number; running: boolean }>
  ) => {
    if (controller) {
      controller.set(patch);
      return;
    }
    if (patch.duration !== undefined) setInternalDuration(patch.duration);
    if (patch.remaining !== undefined) setInternalRemaining(patch.remaining);
    if (patch.running !== undefined) setInternalRunning(patch.running);
  };
  const setDuration = (n: number) => apply({ duration: n });
  const setRemaining = (
    updater: number | ((prev: number) => number)
  ) => {
    const next = typeof updater === "function" ? updater(remaining) : updater;
    apply({ remaining: next });
  };
  const setRunning = (
    updater: boolean | ((prev: boolean) => boolean)
  ) => {
    const next = typeof updater === "function" ? updater(running) : updater;
    apply({ running: next });
  };
  const dragOffset = useRef<{ x: number; y: number } | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const beepedRef = useRef(false);

  // Countdown tick.
  useEffect(() => {
    if (!running) return;
    intervalRef.current = setInterval(() => {
      setRemaining((r) => Math.max(0, r - 1));
    }, 1000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [running]);

  // Beep + auto-stop at zero. Three soft dings spaced ~450ms apart so the
  // teacher hears it from across the classroom without being startling.
  useEffect(() => {
    if (remaining === 0 && running) {
      setRunning(false);
      if (!beepedRef.current) {
        beepedRef.current = true;
        try {
          const AudioCtor =
            window.AudioContext ||
            (window as unknown as { webkitAudioContext: typeof AudioContext })
              .webkitAudioContext;
          const ctx = new AudioCtor();
          const startAt = ctx.currentTime;
          // Three identical short dings — schedule them on a single context
          // so timing stays even if React re-renders happen between them.
          for (let i = 0; i < 3; i += 1) {
            const t0 = startAt + i * 0.45;
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.frequency.value = 880;
            // Soft volume (0.12) and quick decay (0.3s) — three of these
            // together read as "ding-ding-ding" not "BEEEEP".
            gain.gain.setValueAtTime(0.12, t0);
            gain.gain.exponentialRampToValueAtTime(0.001, t0 + 0.3);
            osc.start(t0);
            osc.stop(t0 + 0.32);
          }
        } catch {
          // Audio context blocked (e.g., user hasn't interacted yet) —
          // silent timer is still fine.
        }
      }
    }
    if (remaining > 0) beepedRef.current = false;
  }, [remaining, running]);

  // Drag handlers — only on the header strip.
  const onHeaderPointerDown = (e: React.PointerEvent) => {
    dragOffset.current = {
      x: e.clientX - position.x,
      y: e.clientY - position.y,
    };
    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
  };
  const onHeaderPointerMove = (e: React.PointerEvent) => {
    if (!dragOffset.current) return;
    const nx = e.clientX - dragOffset.current.x;
    const ny = e.clientY - dragOffset.current.y;
    // Clamp to viewport so it can't be dragged off-screen.
    const w = 240, h = 160;
    setPosition({
      x: Math.max(4, Math.min(window.innerWidth - w, nx)),
      y: Math.max(4, Math.min(window.innerHeight - h, ny)),
    });
  };
  const onHeaderPointerUp = (e: React.PointerEvent) => {
    dragOffset.current = null;
    (e.currentTarget as HTMLElement).releasePointerCapture(e.pointerId);
  };

  if (!visible) return null;

  // Format remaining as MM:SS (or HH:MM:SS over an hour).
  const hours = Math.floor(remaining / 3600);
  const mins = Math.floor((remaining % 3600) / 60);
  const secs = remaining % 60;
  const display =
    hours > 0
      ? `${hours}:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
      : `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;

  const parseTime = (s: string): number | null => {
    const m = /^(\d+):(\d{1,2})(?::(\d{1,2}))?$/.exec(s.trim());
    if (!m) {
      // Bare minutes ("5" → 5:00).
      const bare = /^(\d+)$/.exec(s.trim());
      if (bare) return parseInt(bare[1], 10) * 60;
      return null;
    }
    if (m[3]) return parseInt(m[1]) * 3600 + parseInt(m[2]) * 60 + parseInt(m[3]);
    return parseInt(m[1]) * 60 + parseInt(m[2]);
  };

  const commitEdit = (raw: string) => {
    const total = parseTime(raw);
    if (total !== null && total >= 0) {
      setDuration(total);
      setRemaining(total);
    }
    setEditing(false);
  };

  const reset = () => {
    setRemaining(duration);
    setRunning(false);
  };

  return (
    <div
      className={`fixed z-[220] select-none rounded-2xl border-2 shadow-2xl ${
        isDark
          ? "border-pnp-yellow bg-pnp-navy/95 text-white"
          : "border-pnp-yellow bg-white text-pnp-navy"
      }`}
      style={{ left: position.x, top: position.y, width: 240 }}
      role="region"
      aria-label="Classroom timer"
    >
      {/* Header — drag handle */}
      <div
        onPointerDown={onHeaderPointerDown}
        onPointerMove={onHeaderPointerMove}
        onPointerUp={onHeaderPointerUp}
        onPointerCancel={onHeaderPointerUp}
        className={`flex cursor-move items-center justify-between rounded-t-xl px-3 py-1.5 ${
          isDark ? "bg-white/10" : "bg-pnp-gray-100"
        }`}
        title="Drag to move"
      >
        <span className="text-xs font-bold uppercase tracking-wider">Timer</span>
        {/* No close (×) button — the chrome bar's "Timer" toggle hides
            this overlay, same pattern as the Draw button. */}
      </div>

      {/* Time display / editor */}
      <div className="px-4 pb-4 pt-3">
        {editing ? (
          <input
            type="text"
            defaultValue={display}
            autoFocus
            onBlur={(e) => commitEdit(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") (e.target as HTMLInputElement).blur();
              if (e.key === "Escape") setEditing(false);
            }}
            placeholder="MM:SS"
            className={`w-full rounded-md border px-2 py-1 text-center font-mono text-4xl font-bold tabular-nums ${
              isDark
                ? "border-white/30 bg-white/5 text-white"
                : "border-pnp-gray-300 bg-white text-pnp-navy"
            }`}
          />
        ) : (
          <button
            type="button"
            onClick={() => !running && setEditing(true)}
            disabled={running}
            className={`w-full text-center font-mono text-5xl font-bold tabular-nums ${
              remaining === 0
                ? "text-red-500"
                : running
                  ? ""
                  : "cursor-text hover:opacity-70"
            }`}
            title={running ? "Pause to edit the time" : "Click to set time"}
            aria-label={`${display} remaining; click to edit`}
          >
            {display}
          </button>
        )}

        {/* Controls */}
        <div className="mt-3 flex items-center justify-center gap-2">
          <button
            onClick={() => {
              if (remaining === 0) {
                setRemaining(duration);
                setRunning(true);
              } else {
                setRunning((r) => !r);
              }
            }}
            className={`flex-1 rounded-md px-3 py-1.5 text-sm font-semibold transition-colors ${
              running
                ? "bg-pnp-yellow text-pnp-navy hover:opacity-80"
                : "bg-pnp-navy text-white hover:opacity-90"
            }`}
          >
            {running ? "Pause" : remaining === 0 ? "Restart" : "Start"}
          </button>
          <button
            onClick={reset}
            className={`rounded-md px-3 py-1.5 text-sm font-semibold transition-colors ${
              isDark
                ? "bg-white/10 text-white hover:bg-white/20"
                : "bg-pnp-gray-200 text-pnp-gray-800 hover:bg-pnp-gray-300"
            }`}
          >
            Reset
          </button>
        </div>
      </div>
    </div>
  );
}
