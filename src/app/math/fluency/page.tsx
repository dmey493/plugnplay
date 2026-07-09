import type { Metadata } from "next";
import { Suspense } from "react";
import Container from "@/components/layout/Container";
import PageBanner from "@/components/ui/PageBanner";
import FluencyGenerator from "@/components/fluency/FluencyGenerator";

export const metadata: Metadata = {
  title: "Fluency Practice | Math | Plug N Play",
  description:
    "Printable fluency practice worksheets for grades 6–8 — integers, fractions, decimals, percent, equations, inequalities, geometry, graphing, and Algebra 1 essentials, with answer keys.",
};

export default function FluencyPage() {
  return (
    <>
      {/* Banner hidden on print so the worksheet prints clean. */}
      <div className="print:hidden">
        <PageBanner
          tone="light"
          back={{ href: "/math", label: "Back to math" }}
          title="Fluency practice"
          subtitle="Build a printable fluency worksheet for any grades 6–8 skill — integers, fractions, percent, equations, geometry, graphing, and Algebra 1 essentials. Pick the skill, tune the difficulty, print."
        />
      </div>

      {/* Suspense wraps the client component because it reads
          useSearchParams() for the ?topic= pre-fill. */}
      <section className="bg-pnp-gray-50 py-8 print:bg-white print:py-0">
        <Container>
          <Suspense fallback={<div className="min-h-[60vh]" />}>
            <FluencyGenerator />
          </Suspense>
        </Container>
      </section>
    </>
  );
}
