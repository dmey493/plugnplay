/**
 * In-memory room store for the phone-as-remote pairing flow.
 *
 * Single Map<code, Room> guarded by basic invariants. NOT redis, NOT
 * persistent — pairing sessions are ephemeral by design (see plan
 * `validated-waddling-crab.md` "Known limits"). When the Node process
 * restarts, all rooms vanish; that's fine for an ephemeral pairing layer
 * and is the reason we don't carry it to a database.
 *
 * The store sweeps stale rooms on a 30s interval. "Stale" means the
 * projection hasn't sent a heartbeat in HEARTBEAT_TIMEOUT_MS, which is
 * how we detect a closed projection tab (no explicit disconnect).
 *
 * All public functions are sync. The HTTP layer wraps them in async
 * route handlers; nothing here awaits anything.
 */

import type {
  ProjectionState,
  RemoteCommand,
  RemoteTaskBundle,
} from "@/lib/core/types";
import { generateRoomCode } from "@/lib/classroom/remote-codes";

/** Projection considered dead if no heartbeat in this many ms. Roughly
 *  60s — covers typical browser tab-switching and brief network blips
 *  without keeping abandoned rooms alive forever. */
const HEARTBEAT_TIMEOUT_MS = 60_000;

/** How often the sweep timer runs. Stale rooms get culled here. */
const SWEEP_INTERVAL_MS = 30_000;

/** A single live pairing session. Owned by the server process. */
interface Room {
  code: string;
  /** Secret per-projection token. Projection must present this to
   *  heartbeat/disconnect so a code collision on another tab can't
   *  hijack this room. */
  projectionToken: string;
  /** Task bundle precomputed at room creation (parsed prompt + ref
   *  fields). The phone fetches this on `/join` so it doesn't have to
   *  re-parse anything. */
  taskBundle: RemoteTaskBundle;
  /** Latest state published by the projection's heartbeat. `null` until
   *  the first heartbeat arrives. */
  state: ProjectionState | null;
  /** Wall-clock ms of last successful heartbeat. Drives the stale sweep. */
  lastHeartbeatAt: number;
  /** Queued commands awaiting the next heartbeat to drain. */
  pendingCommands: RemoteCommand[];
  /** True if a phone is currently paired. Flipped to true on `join` and
   *  to false on phone `disconnect` or when the room is recreated. */
  phonePaired: boolean;
  /** Optional secret per-phone token. We don't currently enforce it on
   *  poll/command (it's nice-to-have, not security-critical for an
   *  ephemeral pairing) but the field is reserved so we can tighten
   *  later without changing the wire format. */
  phoneToken?: string;
  /** Marked true when the projection explicitly disconnects. Phone polls
   *  see `ended: true` and show the disconnect screen. The room is also
   *  scheduled for removal on the next sweep. */
  ended: boolean;
}

/** The one global map. Module-level singleton — Next.js reuses the
 *  module across requests within a single Node process. */
const rooms = new Map<string, Room>();

/** Idempotent installer for the stale-room sweeper. Calling it multiple
 *  times is safe; subsequent calls are no-ops. */
let sweepTimerStarted = false;
function ensureSweepTimer(): void {
  if (sweepTimerStarted) return;
  sweepTimerStarted = true;
  // `setInterval` returns a Timeout in Node. We don't keep the handle —
  // the sweeper runs for the lifetime of the process.
  setInterval(() => {
    const now = Date.now();
    for (const [code, room] of rooms) {
      const stale = now - room.lastHeartbeatAt > HEARTBEAT_TIMEOUT_MS;
      if (room.ended || stale) {
        rooms.delete(code);
      }
    }
  }, SWEEP_INTERVAL_MS);
}

// ─────────────────────────────────────────────────────────────────────
// Public API
// ─────────────────────────────────────────────────────────────────────

/** Mint a new room. Called by `/api/remote/connect-projection` when the
 *  teacher clicks Connect. The caller supplies the initial state and the
 *  pre-bundled task data. Returns the room's public code + projection
 *  token (secret). */
export function createRoom(
  taskBundle: RemoteTaskBundle,
  initialState: ProjectionState
): { code: string; projectionToken: string } {
  ensureSweepTimer();
  const code = generateRoomCode((c) => rooms.has(c));
  const projectionToken = crypto.randomUUID();
  const room: Room = {
    code,
    projectionToken,
    taskBundle,
    state: initialState,
    lastHeartbeatAt: Date.now(),
    pendingCommands: [],
    phonePaired: false,
    ended: false,
  };
  rooms.set(code, room);
  return { code, projectionToken };
}

/** Phone-side join. Validates the code, evicts any prior paired phone on
 *  the same room, returns the task bundle + current state. */
export function joinRoom(code: string): {
  ok: true;
  taskBundle: RemoteTaskBundle;
  state: ProjectionState;
} | { ok: false; reason: "not-found" | "no-state-yet" | "ended" } {
  const room = rooms.get(code);
  if (!room) return { ok: false, reason: "not-found" };
  if (room.ended) return { ok: false, reason: "ended" };
  if (!room.state) return { ok: false, reason: "no-state-yet" };
  // Evict any prior phone — one phone per projection (per the plan).
  // We don't actively notify the prior phone; it will see `phonePaired`
  // flip back-and-forth on its next poll and either reclaim or give up.
  room.phonePaired = true;
  room.phoneToken = crypto.randomUUID();
  return { ok: true, taskBundle: room.taskBundle, state: room.state };
}

/** Phone-side disconnect. Marks the room un-paired but leaves it alive
 *  so the projection can be paired by a different phone using the same
 *  code. */
export function leaveRoom(code: string): void {
  const room = rooms.get(code);
  if (!room) return;
  room.phonePaired = false;
  room.phoneToken = undefined;
}

/** Projection-side heartbeat. Validates the token, updates the room's
 *  state, drains and returns any pending commands. */
export function heartbeat(
  code: string,
  projectionToken: string,
  state: ProjectionState
): {
  ok: true;
  pendingCommands: RemoteCommand[];
  phonePaired: boolean;
} | { ok: false; reason: "not-found" | "token-mismatch" | "ended" } {
  const room = rooms.get(code);
  if (!room) return { ok: false, reason: "not-found" };
  if (room.projectionToken !== projectionToken) {
    return { ok: false, reason: "token-mismatch" };
  }
  if (room.ended) return { ok: false, reason: "ended" };
  room.state = state;
  room.lastHeartbeatAt = Date.now();
  const drained = room.pendingCommands;
  room.pendingCommands = [];
  return { ok: true, pendingCommands: drained, phonePaired: room.phonePaired };
}

/** Phone-side poll. Read-only — fetches the projection's latest state
 *  without consuming commands. */
export function getPolledState(code: string):
  | { ok: true; state: ProjectionState; ended: boolean }
  | { ok: false; reason: "not-found" | "no-state-yet" } {
  const room = rooms.get(code);
  if (!room) return { ok: false, reason: "not-found" };
  if (!room.state) return { ok: false, reason: "no-state-yet" };
  return { ok: true, state: room.state, ended: room.ended };
}

/** Phone-side command. Validates the code, appends to the pending queue
 *  which the projection drains on its next heartbeat. */
export function pushCommand(
  code: string,
  command: RemoteCommand
): { ok: true } | { ok: false; reason: "not-found" | "ended" } {
  const room = rooms.get(code);
  if (!room) return { ok: false, reason: "not-found" };
  if (room.ended) return { ok: false, reason: "ended" };
  room.pendingCommands.push(command);
  return { ok: true };
}

/** Projection-side explicit disconnect. Marks the room ended so the
 *  phone's next poll sees `ended: true`, and the sweep removes it. */
export function endRoom(code: string, projectionToken: string): boolean {
  const room = rooms.get(code);
  if (!room) return false;
  if (room.projectionToken !== projectionToken) return false;
  room.ended = true;
  return true;
}

/** Test/diagnostic only. Not used by routes. */
export function debugRoomCount(): number {
  return rooms.size;
}
