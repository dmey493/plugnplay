import type { Metadata } from "next";
import Container from "@/components/layout/Container";
import PageBanner from "@/components/ui/PageBanner";
import SpiralReviewBuilder from "@/components/spiral-review/SpiralReviewBuilder";
import { getCheckpointNav } from "@/lib/standards/checkpoints";

export const metadata: Metadata = {
  title: "Spiral Review | Math | Plug N Play",
  description:
    "Build weekly spiral review sheets for grades 6-8 from the standards you pick, at the proficiency level you choose. Swap any problem, then print.",
};

export default async function SpiralReviewPage() {
  const checkpointNav = await getCheckpointNav();
  return (
    <>
      <PageBanner
        tone="light"
        back={{ href: "/math", label: "Back to math" }}
        title="Spiral review"
        subtitle="Pick the standards to keep coming back to. Each week gets new problems at the level you set, ready to print."
      />
      <section className="bg-pnp-gray-50 py-10 md:py-14">
        <Container>
          <SpiralReviewBuilder checkpointNav={checkpointNav} />
        </Container>
      </section>
    </>
  );
}
