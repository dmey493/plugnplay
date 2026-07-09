import type { Metadata } from "next";
import Container from "@/components/layout/Container";
import PageBanner from "@/components/ui/PageBanner";
import GraphOfWeekGenerator from "@/components/science/GraphOfWeekGenerator";
import { graphCount } from "@/lib/gotw";

export const metadata: Metadata = {
  title: "Graph of the Week | Science | Plug N Play",
  description:
    "Pick a grade and Indiana science standard, then a phenomenon graph. Students read the data, make a first look, then write a claim with evidence and reasoning — print-ready front and back.",
};

export default function GraphOfWeekPage() {
  return (
    <>
      <PageBanner
        tone="light"
        back={{ href: "/science", label: "Back to science" }}
        title="Graph of the Week"
        subtitle={`Pick a grade and standard, then a phenomenon graph — ${graphCount()} in all across grades 6–8. Students analyze the data, then write a claim with evidence and reasoning. Print-ready front and back.`}
      />

      <section className="bg-pnp-gray-50 py-10 md:py-14">
        <Container>
          <GraphOfWeekGenerator />
        </Container>
      </section>
    </>
  );
}
