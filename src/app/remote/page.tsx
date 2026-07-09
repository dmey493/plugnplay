import type { Metadata } from "next";
import { Suspense } from "react";
import RemoteClient from "@/components/remote/RemoteClient";

export const metadata: Metadata = {
  title: "Remote | Plug N Play",
  description:
    "Pair your phone to a Plug N Play projection. Drive slides, timer, and reference cards from your hand.",
};

/**
 * Phone entry page for the projection remote. Server component — all
 * the live behaviour lives inside `RemoteClient`. The `?code=XXXX`
 * query param is read on the client so the QR-scan path auto-fills
 * the code box.
 *
 * `useSearchParams` in Next 16 needs a Suspense boundary so the
 * client-only param read doesn't poison the static prerender.
 */
export default function RemotePage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-pnp-gray-50" />}>
      <RemoteClient />
    </Suspense>
  );
}
