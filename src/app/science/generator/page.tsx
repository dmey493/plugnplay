import type { Metadata } from "next";
import Container from "@/components/layout/Container";
import PageBanner from "@/components/ui/PageBanner";
import ScienceGenerator from "@/components/science/ScienceGenerator";
import { stimulusCount } from "@/lib/library/science";

export const metadata: Metadata = {
  title: "Stimulus Generator | Science | Plug N Play",
  description:
    "Pick a biology (HS-LS) standard and a phenomenon stimulus — ILEARN End-of-Course style, with a chart or data table and auto-scorable items, ready to print.",
};

export default function ScienceGeneratorPage() {
  return (
    <>
      <PageBanner
        tone="light"
        back={{ href: "/science", label: "Back to science" }}
        title="Stimulus generator"
        subtitle={`Choose a biology standard and pick one of its three phenomenon stimuli — ${stimulusCount()} in all, ILEARN End-of-Course style, ready to print.`}
      />

      <section className="bg-pnp-gray-50 py-10 md:py-14">
        <Container>
          <ScienceGenerator />
        </Container>
      </section>
    </>
  );
}
