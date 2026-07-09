import type { Metadata } from "next";
import RemotePreviewClient from "@/components/remote/RemotePreviewClient";

export const metadata: Metadata = {
  title: "Remote Preview | Plug N Play",
  description:
    "Local preview of the phone-as-remote dashboard. No pairing required — uses sample task data so you can see and click the UI.",
};

/**
 * Static-data preview of the phone-as-remote dashboard. Renders the
 * same `RemoteDashboard` component the live pairing flow uses, but
 * wired against a local state simulator instead of a real projection.
 *
 * Open this on your phone (or desktop with mobile viewport) to see and
 * interact with the UI: tap Next/Back and the question count updates,
 * tap a theme and the active one switches, expand reference cards, etc.
 * No `/api/remote/*` requests are made.
 */
export default function RemotePreviewPage() {
  return <RemotePreviewClient />;
}
