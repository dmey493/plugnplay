export const dynamic = "force-dynamic";

import type { PollResponse } from "@/lib/core/types";
import { getPolledState } from "@/lib/classroom/remote-store";

/**
 * Phone-side poll (~2Hz). Read-only fetch of the projection's latest
 * broadcast state. Does NOT consume commands.
 *
 * Body: `{ code }`
 * Returns: `PollResponse`.
 *
 * Returns `alive: false` (200 OK, not 4xx) for unknown / expired rooms
 * so the phone's poll loop treats it as state, not a network failure.
 */
export async function POST(request: Request) {
  try {
    const body = (await request.json()) as { code?: unknown };
    const code = typeof body.code === "string" ? body.code : null;
    if (!code) {
      return Response.json({ error: "Missing code" }, { status: 400 });
    }
    const result = getPolledState(code);
    if (!result.ok) {
      const out: PollResponse = { alive: false, state: null };
      return Response.json(out);
    }
    const out: PollResponse = {
      alive: true,
      state: result.state,
      ended: result.ended,
    };
    return Response.json(out);
  } catch (e) {
    return Response.json(
      { error: e instanceof Error ? e.message : "Unknown error" },
      { status: 500 }
    );
  }
}
