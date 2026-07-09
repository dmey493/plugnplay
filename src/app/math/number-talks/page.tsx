import type { Metadata } from "next";
import { Suspense } from "react";
import Container from "@/components/layout/Container";
import PageBanner from "@/components/ui/PageBanner";
import NumberTalksBrowse from "@/components/math/number-talks/NumberTalksBrowse";
import { getAllNumberTalks } from "@/lib/number-talks";

export const metadata: Metadata = {
  title: "Number Talks | Math | Plug N Play",
  description:
    "Short mental-math warm-ups for grades 6-8. Show a problem, ask “How did you solve it in your head?”, then compare strategies. Problems reveal one at a time, with teacher notes and an answer key.",
};

export default function NumberTalksPage() {
  const grades = getAllNumberTalks();
  return (
    <>
      <PageBanner
        tone="navy"
        back={{ href: "/math", label: "Back to math" }}
        title="Number talks"
        subtitle="Short mental-math warm-ups that get every student thinking and talking. Show a problem, ask how they solved it in their head, then compare strategies — no pencils, no calculators. Problems reveal one at a time so the string builds."
      />

      <section className="bg-pnp-gray-50 py-10 md:py-14">
        <Container>
          <Suspense fallback={<div className="min-h-[60vh]" />}>
            <NumberTalksBrowse grades={grades} />
          </Suspense>
        </Container>
      </section>
    </>
  );
}
