export const dynamic = "force-dynamic";

import type {
  HeartbeatResponse,
  ProjectionState,
} from "@/lib/core/types";
import { heartbeat } from "@/lib/classroom/remote-store";

/**
 * Projection-side heartbeat (~1Hz). Publishes the projection's current
 * state and drains any pending commands that the phone has queued.
 *
 * Body: `{ code, projectionToken, state }`
 * Returns: `{ alive, pendingCommands[], phonePaired }`
 *
 * `alive: false` tells the projection that the room is gone (swept for
 * inactivity, or the user deliberately cleared it server-side) — the
 * projection should stop heartbeating and reset its connect state.
 */
export async function POST(request: Request) {
  try {
    const body = (await request.json()) as {
      code?: unknown;
      projectionToken?: unknown;
      state?: unknown;
    };
    const code = typeof body.code === "string" ? body.code : null;
    const projectionToken =
      typeof body.projectionToken === "string" ? body.projectionToken : null;
    if (!code || !projectionToken) {
      return Response.json({ error: "Missing code or token" }, { status: 400 });
    }
    if (!isProjectionState(body.state)) {
      return Response.json({ error: "Missing/invalid state" }, { status: 400 });
    }

    const result = heartbeat(code, projectionToken, body.state);
    if (!result.ok) {
      // 200 with `alive: false` rather than a 4xx — the projection's
      // heartbeat loop should handle expiry as a soft state, not a
      // network error.
      const out: HeartbeatResponse = {
        alive: false,
        pendingCommands: [],
        phonePaired: false,
      };
      return Response.json(out);
    }
    const out: HeartbeatResponse = {
      alive: true,
      pendingCommands: result.pendingCommands,
      phonePaired: result.phonePaired,
    };
    return Response.json(out);
  } catch (e) {
    return Response.json(
      { error: e instanceof Error ? e.message : "Unknown error" },
      { status: 500 }
    );
  }
}

function isProjectionState(value: unknown): value is ProjectionState {
  if (!value || typeof value !== "object") return false;
  const v = value as Record<string, unknown>;
  return (
    typeof v.taskId === "string" &&
    typeof v.totalQuestions === "number" &&
    typeof v.revealedCount === "number" &&
    typeof v.themeId === "string"
  );
}
