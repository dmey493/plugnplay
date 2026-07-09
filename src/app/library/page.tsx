import type { Metadata } from "next";
import { getAllStrategies } from "@/lib/content";
import Container from "@/components/layout/Container";
import PageBanner from "@/components/ui/PageBanner";
import StrategyLibrary from "@/components/library/StrategyLibrary";

export const metadata: Metadata = {
  title: "Strategies Library | Plug N Play",
  description:
    "Browse teaching strategies by subject, purpose, and MTSS tier for grades 6-8.",
};

export default async function LibraryPage() {
  const strategies = await getAllStrategies();

  return (
    <>
      <PageBanner
        title="Strategies library"
        subtitle="Filter by subject, grade, and purpose to find the right strategy for your classroom."
      />

      <section className="bg-pnp-gray-50 py-10 md:py-14">
        <Container>
          <StrategyLibrary strategies={strategies} />
        </Container>
      </section>
    </>
  );
}
