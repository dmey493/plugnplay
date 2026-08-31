import type { Metadata } from "next";
import Container from "@/components/layout/Container";
import PageBanner from "@/components/ui/PageBanner";
import SkillIntervention from "@/components/intervention/SkillIntervention";
import { getLessonNav } from "@/lib/library/lessons";
import { getCheckpointNav } from "@/lib/standards/checkpoints";

export const metadata: Metadata = {
  title: "Skill Intervention | Math | Plug N Play",
  description:
    "Tier 2 skill intervention mapped as a learning progression per standard — see which skills run in parallel and where they converge, then generate a worksheet, diagnostic, or progress check.",
};

export default async function InterventionPage() {
  const lessonNav = await getLessonNav();
  const checkpointNav = await getCheckpointNav();
  return (
    <>
      <PageBanner
        tone="light"
        title="Skill intervention"
        subtitle="Pick a standard to map its learning progression, from the far-below prerequisites through the grade-level rungs and out to what comes next. Skills that sit side by side carry the same weight; the lines show which ones have to be in place before the next skill. Click any skill to generate its worksheet."
        back={{ href: "/math", label: "Back to Math" }}
      />

      <section className="bg-pnp-gray-50 py-10 md:py-14">
        <Container>
          <SkillIntervention lessonNav={lessonNav} checkpointNav={checkpointNav} />
        </Container>
      </section>
    </>
  );
}
