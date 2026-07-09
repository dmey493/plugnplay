"use client";

import { useEffect, useState } from "react";
import QRCode from "qrcode";

/**
 * Modal opened on the projection when the teacher clicks 📱 Connect.
 *
 * Shows the 4-character room code in large monospace, plus a QR code
 * that deep-links to `/remote?code=XXXX` for instant phone pairing.
 * Status flips from "Waiting…" to "Connected" the moment the phone
 * heartbeat reports `phonePaired: true`.
 *
 * ESC and click-outside close the modal — they do NOT disconnect. The
 * room stays alive until the teacher explicitly clicks Disconnect or
 * the projection unmounts. Reopening the modal (click the now-yellow
 * Connect button again) shows the same code.
 */
interface Props {
  code: string;
  phonePaired: boolean;
  isDark: boolean;
  onClose: () => void;
  onDisconnect: () => void;
}

export default function RemoteConnectModal({
  code,
  phonePaired,
  isDark,
  onClose,
  onDisconnect,
}: Props) {
  const [qrSvg, setQrSvg] = useState<string | null>(null);
  const [remoteUrl, setRemoteUrl] = useState<string>("");

  // Detect "phone-unreachable" hosts. A phone on the same WiFi as the
  // laptop can't fetch `http://localhost:3000` or `http://127.0.0.1:3000`
  // — those hostnames mean "this device" on the phone too. When dev
  // happens at `localhost`, the QR encodes an unreachable URL and the
  // teacher's phone shows "site can't be reached". We surface a
  // dedicated warning + the typeable code as the fallback path.
  const isUnreachableHost = /^https?:\/\/(localhost|127\.0\.0\.1)(:|\/|$)/i.test(
    remoteUrl
  );

  // Render QR to inline SVG once per code. Using the OSS `qrcode` lib's
  // Promise API — no extra render loop, no CDN.
  //
  // Hostname strategy: when the teacher's browser is at `localhost` or
  // `127.0.0.1` we ask the server for its own LAN IPv4 address and
  // substitute it. That makes the QR work even in dev when the teacher
  // didn't think to access the projection via the LAN address. In all
  // other cases we use `window.location.host` directly.
  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      if (typeof window === "undefined") return;
      const origin = window.location.origin;
      const port = window.location.port || "3000";
      const protocol = window.location.protocol || "http:";
      const onLoopback = /^https?:\/\/(localhost|127\.0\.0\.1)(:|\/|$)/i.test(origin);
      let url = `${origin}/remote?code=${code}`;
      if (onLoopback) {
        try {
          const res = await fetch("/api/remote/lan-host");
          if (res.ok) {
            const { host } = (await res.json()) as { host: string | null };
            if (host) {
              url = `${protocol}//${host}:${port}/remote?code=${code}`;
            }
          }
        } catch {
          // Best-effort — fall back to the localhost URL with the
          // unreachable-host warning copy in the UI below.
        }
      }
      if (cancelled) return;
      setRemoteUrl(url);
      try {
        const svg = await QRCode.toString(url, {
          type: "svg",
          errorCorrectionLevel: "M",
          margin: 1,
          color: { dark: "#1a1f3d", light: "#ffffff" },
        });
        if (!cancelled) setQrSvg(svg);
      } catch {
        if (!cancelled) setQrSvg(null);
      }
    };
    void run();
    return () => {
      cancelled = true;
    };
  }, [code]);

  // ESC closes the modal (but does NOT disconnect).
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        e.stopPropagation();
        onClose();
      }
    };
    // Capture phase so we beat ProjectionView's own ESC handler that
    // would otherwise exit the whole projection.
    window.addEventListener("keydown", onKey, true);
    return () => window.removeEventListener("keydown", onKey, true);
  }, [onClose]);

  // Format the 4-char code as e.g. "RX 7K" for easy reading at a
  // distance. Pure visual — typing accepts either form.
  const formatted = code.slice(0, 2) + " " + code.slice(2);

  const panelBg = isDark
    ? "bg-pnp-navy text-white"
    : "bg-white text-pnp-navy";

  return (
    <>
      <div
        onClick={onClose}
        className="fixed inset-0 z-[250] bg-black/60"
        aria-hidden="true"
      />
      <div
        role="dialog"
        aria-label="Connect your phone"
        className={`fixed left-1/2 top-1/2 z-[251] w-[min(92vw,420px)] -translate-x-1/2 -translate-y-1/2 rounded-3xl p-7 shadow-2xl ${panelBg}`}
      >
        <div className="flex items-start justify-between">
          <div>
            <h2 className="font-heading text-2xl font-extrabold">
              Run the room from your phone
            </h2>
            <p className={`mt-1 text-sm ${isDark ? "text-white/70" : "text-pnp-gray-500"}`}>
              Scan this code with your phone&rsquo;s camera to use it as a remote.
              No app needed.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className={`rounded-md px-2 py-1 transition-colors ${
              isDark ? "hover:bg-white/10" : "hover:bg-pnp-gray-100"
            }`}
            aria-label="Close"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.25" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* Code in big readable mono. Spaced for legibility from the back
            of the room. */}
        <div className="mt-5 flex flex-col items-center gap-4">
          <div
            className={`rounded-2xl px-6 py-4 font-mono text-5xl font-extrabold tracking-[0.2em] tabular-nums ${
              isDark ? "bg-white/10 text-pnp-yellow" : "bg-pnp-gray-100 text-pnp-navy"
            }`}
            aria-label={`Room code ${code}`}
          >
            {formatted}
          </div>

          {/* QR code — clean white background regardless of theme so phones
              can always parse it. We dim it when the URL it encodes is
              unreachable from a phone (localhost / 127.0.0.1) so the
              teacher doesn't waste time scanning it. */}
          <div
            className={`overflow-hidden rounded-xl bg-white p-2 shadow-inner ${
              isUnreachableHost ? "opacity-40" : ""
            }`}
            style={{ width: 196, height: 196 }}
            aria-label="QR code to /remote with this room code"
          >
            {qrSvg ? (
              <div
                className="h-full w-full [&>svg]:h-full [&>svg]:w-full"
                // eslint-disable-next-line react/no-danger
                dangerouslySetInnerHTML={{ __html: qrSvg }}
              />
            ) : (
              <div className="flex h-full w-full items-center justify-center text-xs text-pnp-gray-500">
                Generating QR…
              </div>
            )}
          </div>

          {/* Pairing-URL line. The QR is the easy path when the
              hostname is reachable — when it isn't, the teacher needs
              the typeable instructions instead. */}
          {isUnreachableHost ? (
            <div className={`w-full rounded-xl px-4 py-3 text-sm ${
              isDark ? "bg-pnp-yellow/15 text-pnp-yellow" : "bg-pnp-yellow/20 text-pnp-navy"
            }`}>
              <div className="font-bold">This phone can&rsquo;t reach the code right now.</div>
              <div className={`mt-1 text-xs leading-relaxed ${
                isDark ? "text-white/70" : "text-pnp-gray-700"
              }`}>
                The projection is open on a private address only this laptop can see. Scanning works once the projection is opened on a shared network address &mdash; ask your IT admin if you&rsquo;re not sure.
              </div>
            </div>
          ) : (
            <div className={`w-full break-all rounded-md px-3 py-2 text-center font-mono text-xs ${
              isDark ? "bg-white/5 text-white/70" : "bg-pnp-gray-100 text-pnp-gray-600"
            }`}>
              {remoteUrl}
            </div>
          )}

          {/* Status */}
          {phonePaired ? (
            <div className="flex w-full items-center justify-between rounded-xl bg-pnp-green/15 px-4 py-3 text-pnp-green">
              <span className="flex items-center gap-2 font-semibold">
                <span className="text-lg">✓</span> Phone connected
              </span>
              <button
                type="button"
                onClick={onDisconnect}
                className="rounded-md px-3 py-1.5 text-sm font-semibold underline hover:no-underline"
              >
                Disconnect
              </button>
            </div>
          ) : (
            <div className={`flex w-full items-center justify-between rounded-xl px-4 py-3 ${
              isDark ? "bg-white/5" : "bg-pnp-gray-100"
            }`}>
              <span className={`flex items-center gap-2 text-sm font-semibold ${
                isDark ? "text-white/70" : "text-pnp-gray-600"
              }`}>
                <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-pnp-yellow" />
                Waiting for phone…
              </span>
              <button
                type="button"
                onClick={onDisconnect}
                className={`rounded-md px-3 py-1.5 text-xs font-semibold underline hover:no-underline ${
                  isDark ? "text-white/60" : "text-pnp-gray-500"
                }`}
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
