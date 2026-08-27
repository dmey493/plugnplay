"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import type {
  JoinResponse,
  PollResponse,
  ProjectionState,
  RemoteCommand,
  RemoteTaskBundle,
} from "@/lib/core/types";
import { isValidRoomCode, normaliseRoomCode } from "@/lib/classroom/remote-codes";
import RemoteCodeEntry from "./RemoteCodeEntry";
import RemoteDashboard from "./RemoteDashboard";

/**
 * Top-level phone-side client. Owns the connection state machine:
 *   entering-code → connecting → connected → disconnected
 *
 * - "entering-code": user types or QR-scans into the form.
 * - "connecting": fetching `/api/remote/join`.
 * - "connected": running the 2Hz poll loop, displaying the dashboard.
 * - "disconnected": room ended on the projection side. User can rejoin.
 */
type Mode =
  | { kind: "entering-code"; error?: string }
  | { kind: "connecting"; code: string }
  | {
      kind: "connected";
      code: string;
      bundle: RemoteTaskBundle;
      state: ProjectionState;
    }
  | { kind: "disconnected"; code: string; reason: string };

export default function RemoteClient() {
  const searchParams = useSearchParams();
  const initialCode = normaliseRoomCode(searchParams?.get("code") ?? "");

  const [mode, setMode] = useState<Mode>({ kind: "entering-code" });

  // ─── Submit code (join) ────────────────────────────────────────────
  const submit = useCallback(async (rawCode: string) => {
    const code = normaliseRoomCode(rawCode);
    if (!isValidRoomCode(code)) {
      setMode({ kind: "entering-code", error: "Code must be 4 letters/digits." });
      return;
    }
    setMode({ kind: "connecting", code });
    try {
      const res = await fetch("/api/remote/join", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
      });
      if (!res.ok) {
        const reason = res.status === 404
          ? "We couldn't find that room. Check the code on the projection."
          : res.status === 410
            ? "That session has ended. Ask the teacher to start a new one."
            : "Couldn't connect. Try again.";
        setMode({ kind: "entering-code", error: reason });
        return;
      }
      const data = (await res.json()) as JoinResponse;
      setMode({
        kind: "connected",
        code,
        bundle: data.taskBundle,
        state: data.state,
      });
    } catch {
      setMode({
        kind: "entering-code",
        error: "Network error. Check your connection and try again.",
      });
    }
  }, []);

  // Auto-join when a code arrives via `?code=` (QR-scan path).
  const autoJoinedRef = useRef(false);
  useEffect(() => {
    if (autoJoinedRef.current) return;
    if (initialCode && isValidRoomCode(initialCode)) {
      autoJoinedRef.current = true;
      void submit(initialCode);
    }
  }, [initialCode, submit]);

  // ─── Poll loop ────────────────────────────────────────────────────
  useEffect(() => {
    if (mode.kind !== "connected") return;
    let cancelled = false;
    const { code } = mode;
    const tick = async () => {
      try {
        const res = await fetch("/api/remote/poll", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code }),
        });
        if (!res.ok || cancelled) return;
        const data = (await res.json()) as PollResponse;
        if (cancelled) return;
        if (!data.alive || data.ended) {
          setMode({
            kind: "disconnected",
            code,
            reason: data.ended
              ? "The teacher ended the session."
              : "The projection went away.",
          });
          return;
        }
        if (data.state) {
          setMode((m) =>
            m.kind === "connected" ? { ...m, state: data.state! } : m
          );
        }
      } catch {
        // Transient — let the next tick try again.
      }
    };
    // Fire one immediately so the dashboard isn't stale for 500ms.
    void tick();
    const id = setInterval(tick, 500);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [mode.kind, mode.kind === "connected" ? mode.code : null]);

  // ─── Command sender ───────────────────────────────────────────────
  const sendCommand = useCallback(
    async (command: RemoteCommand) => {
      if (mode.kind !== "connected") return;
      try {
        await fetch("/api/remote/command", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code: mode.code, command }),
        });
      } catch {
        // Best-effort — the projection will reflect our state on its next
        // heartbeat regardless, and we can rely on the poll loop to
        // confirm. Failing silently is fine for a remote.
      }
    },
    [mode]
  );

  // ─── Disconnect (user-initiated) ──────────────────────────────────
  const disconnect = useCallback(async () => {
    if (mode.kind !== "connected") return;
    try {
      await fetch("/api/remote/leave", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: mode.code }),
      });
    } catch {
      // best-effort
    }
    setMode({ kind: "entering-code" });
  }, [mode]);

  // ─── Render ───────────────────────────────────────────────────────
  if (mode.kind === "entering-code" || mode.kind === "connecting") {
    return (
      <RemoteCodeEntry
        initialCode={initialCode}
        connecting={mode.kind === "connecting"}
        error={mode.kind === "entering-code" ? mode.error : undefined}
        onSubmit={(c) => void submit(c)}
      />
    );
  }
  if (mode.kind === "disconnected") {
    return (
      <DisconnectedScreen
        reason={mode.reason}
        onReconnect={() => void submit(mode.code)}
        onNewCode={() => setMode({ kind: "entering-code" })}
      />
    );
  }
  return (
    <RemoteDashboard
      bundle={mode.bundle}
      state={mode.state}
      onCommand={(c) => void sendCommand(c)}
      onDisconnect={() => void disconnect()}
    />
  );
}

// ─────────────────────────────────────────────────────────────────────
// Disconnected screen
// ─────────────────────────────────────────────────────────────────────

function DisconnectedScreen({
  reason,
  onReconnect,
  onNewCode,
}: {
  reason: string;
  onReconnect: () => void;
  onNewCode: () => void;
}) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-pnp-gray-50 px-6 text-center text-pnp-gray-900">
      <div className="w-full max-w-sm rounded-2xl bg-white p-8 shadow-md">
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-pnp-yellow/40 text-2xl">
          📡
        </div>
        <h1 className="font-heading text-xl font-bold text-pnp-navy">
          Disconnected
        </h1>
        <p className="mt-2 text-sm text-pnp-gray-500">{reason}</p>
        <div className="mt-6 flex flex-col gap-2">
          <button
            type="button"
            onClick={onReconnect}
            className="w-full rounded-lg bg-pnp-blue py-2.5 font-bold text-white hover:bg-pnp-navy"
          >
            Try the same code again
          </button>
          <button
            type="button"
            onClick={onNewCode}
            className="w-full rounded-lg border border-pnp-gray-300 bg-white py-2.5 font-semibold text-pnp-gray-700 hover:bg-pnp-gray-50"
          >
            Enter a different code
          </button>
        </div>
      </div>
    </div>
  );
}
