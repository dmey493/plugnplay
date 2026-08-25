import type { Metadata } from "next";
import Container from "@/components/layout/Container";
import PageBanner from "@/components/ui/PageBanner";
import SkillIntervention from "@/components/math/SkillIntervention";
import { getLessonNav } from "@/lib/lessons";
import { getCheckpointNav } from "@/lib/checkpoints";

export const metadata: Metadata = {
  title: "Skill Intervention | Math | Plug N Play",
  description:
    "Tier 2 skill intervention organized as a learning progression per standard — pick a skill to generate its worksheet, plus diagnostics and progress checks.",
};

export default async function InterventionPage() {
  const lessonNav = await getLessonNav();
  const checkpointNav = await getCheckpointNav();
  return (
    <>
      <PageBanner
        tone="light"
        title="Skill intervention"
        subtitle="Pick a standard to see its learning progression — skills organized by Looking Back, On Grade, and Looking Forward. Click any skill to generate its worksheet."
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
