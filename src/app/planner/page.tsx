import type { Metadata } from "next";
import PlannerApp from "@/components/planner/PlannerApp";

export const metadata: Metadata = {
  title: "Planner | Plug N Play",
  description:
    "Build a course, break it into units, and block out each period minute by minute. Schedule every prep across the week, then print it on one page.",
};

/**
 * Top-level, not under /math: the planner is subject-neutral. A course is
 * whatever the teacher names it, and nothing here reads subject content.
 *
 * Entirely client-side (library lives in localStorage), so there is nothing
 * to load on the server. No PageBanner either — this is a workspace, and
 * the banner cost ~200px above the grid.
 */
export default function PlannerPage() {
  return <PlannerApp />;
}
