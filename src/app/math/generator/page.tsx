import type { Metadata } from "next";
import { Suspense } from "react";
import Container from "@/components/layout/Container";
import PageBanner from "@/components/ui/PageBanner";
import ProblemGenerator from "@/components/math/ProblemGenerator";
import { getLessonNav } from "@/lib/lessons";

export const metadata: Metadata = {
  title: "Problem Generator | Math | Plug N Play",
  description:
    "Generate math practice problems aligned to Indiana Math Standards for grades 6-8.",
};

export default async function GeneratorPage() {
  const lessonNav = await getLessonNav();
  return (
    <>
      <PageBanner
        tone="light"
        back={{ href: "/math", label: "Back to math" }}
        title="Problem generator"
        subtitle="Make an exit ticket, a tiered practice set, or a proficiency check — aligned to any Indiana standard, ready to print."
      />

      {/* Suspense wraps the client component because it reads
          useSearchParams() for the ?standard= pre-fill, which Next 16
          requires be bounded so static prerender works. */}
      <section className="bg-pnp-gray-50 py-10 md:py-14">
        <Container>
          <Suspense fallback={<div className="min-h-[60vh]" />}>
            <ProblemGenerator lessonNav={lessonNav} />
          </Suspense>
        </Container>
      </section>
    </>
  );
}
