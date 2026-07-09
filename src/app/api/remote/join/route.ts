export const dynamic = "force-dynamic";

import type { JoinResponse } from "@/lib/types";
import { joinRoom } from "@/lib/remote-store";
import { isValidRoomCode, normaliseRoomCode } from "@/lib/remote-codes";

/**
 * Phone-side join. Called once when the user types or QR-scans into a
 * room. Returns the task bundle (parsed prompt + reference fields) and
 * the projection's current state in one shot, so the phone can render
 * its dashboard immediately without a second round-trip.
 *
 * Body: `{ code }`
 * Returns: `JoinResponse` or `{ error, reason }` with 4xx.
 */
export async function POST(request: Request) {
  try {
    const body = (await request.json()) as { code?: unknown };
    const raw = typeof body.code === "string" ? body.code : "";
    const code = normaliseRoomCode(raw);
    if (!isValidRoomCode(code)) {
      return Response.json(
        { error: "Invalid room code", reason: "invalid-format" },
        { status: 400 }
      );
    }

    const result = joinRoom(code);
    if (!result.ok) {
      // Map the store's structured reasons to the right HTTP code so the
      // phone client can show a friendly message ("expired", "not
      // found", etc.) without parsing prose.
      const status =
        result.reason === "not-found"
          ? 404
          : result.reason === "ended"
            ? 410 // Gone
            : 503; // no-state-yet — projection hasn't heartbeated yet
      return Response.json(
        { error: "Cannot join room", reason: result.reason },
        { status }
      );
    }

    const response: JoinResponse = {
      ok: true,
      taskBundle: result.taskBundle,
      state: result.state,
    };
    return Response.json(response);
  } catch (e) {
    return Response.json(
      { error: e instanceof Error ? e.message : "Unknown error" },
      { status: 500 }
    );
  }
}
