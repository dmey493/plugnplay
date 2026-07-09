export const dynamic = "force-dynamic";

import { endRoom } from "@/lib/remote-store";

/**
 * Projection-side explicit disconnect. Called when the teacher hits
 * Disconnect or closes the projection tab cleanly (the unload-hook
 * variant uses `navigator.sendBeacon` against the same route, hence the
 * simple body shape).
 *
 * Body: `{ code, projectionToken }`
 * Returns: `{ ok: true }`
 *
 * Idempotent — calling on an unknown room is treated as a no-op so the
 * teardown path stays simple.
 */
export async function POST(request: Request) {
  try {
    const body = (await request.json()) as {
      code?: unknown;
      projectionToken?: unknown;
    };
    const code = typeof body.code === "string" ? body.code : null;
    const projectionToken =
      typeof body.projectionToken === "string" ? body.projectionToken : null;
    if (!code || !projectionToken) {
      return Response.json({ error: "Missing code or token" }, { status: 400 });
    }
    endRoom(code, projectionToken);
    return Response.json({ ok: true });
  } catch (e) {
    return Response.json(
      { error: e instanceof Error ? e.message : "Unknown error" },
      { status: 500 }
    );
  }
}
