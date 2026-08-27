export const dynamic = "force-dynamic";

import type { RemoteCommand } from "@/lib/core/types";
import { pushCommand } from "@/lib/classroom/remote-store";

/**
 * Phone-side command. Fired immediately on every user action
 * (next/back, theme switch, timer adjust). Queued on the server; the
 * projection drains the queue on its next heartbeat (~1s later) and
 * applies the commands via its existing setters.
 *
 * Body: `{ code, command: RemoteCommand }`
 * Returns: `{ ok: true }` or `{ error, reason }` 4xx.
 */
export async function POST(request: Request) {
  try {
    const body = (await request.json()) as {
      code?: unknown;
      command?: unknown;
    };
    const code = typeof body.code === "string" ? body.code : null;
    if (!code) {
      return Response.json({ error: "Missing code" }, { status: 400 });
    }
    if (!isRemoteCommand(body.command)) {
      return Response.json(
        { error: "Invalid command" },
        { status: 400 }
      );
    }
    const result = pushCommand(code, body.command);
    if (!result.ok) {
      const status = result.reason === "not-found" ? 404 : 410;
      return Response.json(
        { error: "Cannot send command", reason: result.reason },
        { status }
      );
    }
    return Response.json({ ok: true });
  } catch (e) {
    return Response.json(
      { error: e instanceof Error ? e.message : "Unknown error" },
      { status: 500 }
    );
  }
}

/** Structural guard for the wire form. We only check `type` since the
 *  rest of each variant's payload is small and type-tight enough that
 *  the projection's apply step rejects garbage gracefully. */
function isRemoteCommand(value: unknown): value is RemoteCommand {
  if (!value || typeof value !== "object") return false;
  const v = value as Record<string, unknown>;
  if (typeof v.type !== "string") return false;
  switch (v.type) {
    case "advance":
    case "retreat":
    case "timer-reset":
      return true;
    case "set-theme":
      return typeof v.themeId === "string";
    case "set-window-size":
      return v.size === 1 || v.size === 2 || v.size === 3;
    case "toggle-drawing":
      return typeof v.on === "boolean";
    case "set-timer-visible":
      return typeof v.visible === "boolean";
    case "timer-set-duration":
      return typeof v.seconds === "number" && v.seconds >= 0;
    case "timer-set-running":
      return typeof v.running === "boolean";
    default:
      return false;
  }
}
