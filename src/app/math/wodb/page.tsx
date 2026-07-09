import type { Metadata } from "next";
import { Suspense } from "react";
import Container from "@/components/layout/Container";
import PageBanner from "@/components/ui/PageBanner";
import WodbBrowse from "@/components/math/wodb/WodbBrowse";
import { getAllWodb } from "@/lib/wodb";

export const metadata: Metadata = {
  title: "Which One Doesn't Belong? | Math | Plug N Play",
  description:
    "A quick, low-floor / high-ceiling math warm-up for grades 6-8. Show four boxes, ask which one doesn't belong — and let the reasoning fly. Filter by strand or concept and project full-screen.",
};

export default function WodbPage() {
  const grades = getAllWodb();
  return (
    <>
      <PageBanner
        tone="navy"
        back={{ href: "/math", label: "Back to math" }}
        title="Which one doesn't belong?"
        subtitle="A 5–10 minute thinking routine. Every set has four boxes, and each one can be argued as the odd one out — so the point is justification, vocabulary, and math talk. Pick a set to project it, then reveal teacher notes."
      />

      <section className="bg-pnp-gray-50 py-10 md:py-14">
        <Container>
          <Suspense fallback={<div className="min-h-[60vh]" />}>
            <WodbBrowse grades={grades} />
          </Suspense>
        </Container>
      </section>
    </>
  );
}
