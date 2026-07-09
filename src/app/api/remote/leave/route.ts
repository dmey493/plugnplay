export const dynamic = "force-dynamic";

import { leaveRoom } from "@/lib/remote-store";

/**
 * Phone-side disconnect. Marks the room un-paired but leaves it alive
 * so the projection can be re-paired by a different phone (or the same
 * phone reconnecting from a fresh tab) using the same code.
 *
 * Body: `{ code }`
 * Returns: `{ ok: true }` always (idempotent — unknown room is a no-op).
 */
export async function POST(request: Request) {
  try {
    const body = (await request.json()) as { code?: unknown };
    const code = typeof body.code === "string" ? body.code : null;
    if (!code) {
      return Response.json({ error: "Missing code" }, { status: 400 });
    }
    leaveRoom(code);
    return Response.json({ ok: true });
  } catch (e) {
    return Response.json(
      { error: e instanceof Error ? e.message : "Unknown error" },
      { status: 500 }
    );
  }
}
