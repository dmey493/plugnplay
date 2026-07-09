export const dynamic = "force-dynamic";

import { networkInterfaces } from "os";

/**
 * Returns the server's best-guess LAN IPv4 address so the QR-code
 * generator on the projection can encode a URL the phone can actually
 * reach. Without this, dev sessions accessed at `localhost` produce a
 * QR that takes the phone to its own loopback — which doesn't work.
 *
 * Picks the first non-internal IPv4 from the OS network interface list.
 * Prefers RFC1918 ranges (192.168.*, 10.*, 172.16-31.*) so VPN
 * addresses don't outrank the actual WiFi address.
 *
 * Returns `{ host: null }` if no suitable interface is found — in that
 * case the modal falls back to whatever the browser sees in
 * `window.location.host`.
 */
export async function GET() {
  try {
    const interfaces = networkInterfaces();
    const candidates: string[] = [];
    for (const name of Object.keys(interfaces)) {
      const list = interfaces[name];
      if (!list) continue;
      for (const entry of list) {
        if (entry.family !== "IPv4") continue;
        if (entry.internal) continue;
        candidates.push(entry.address);
      }
    }
    const preferred = candidates.find(isPrivateLan) ?? candidates[0] ?? null;
    return Response.json({ host: preferred });
  } catch {
    return Response.json({ host: null });
  }
}

/** True if the IPv4 address is in an RFC1918 private range. */
function isPrivateLan(ip: string): boolean {
  if (ip.startsWith("192.168.")) return true;
  if (ip.startsWith("10.")) return true;
  // 172.16.0.0 – 172.31.255.255
  const m = /^172\.(\d{1,3})\./.exec(ip);
  if (m) {
    const n = parseInt(m[1], 10);
    return n >= 16 && n <= 31;
  }
  return false;
}
