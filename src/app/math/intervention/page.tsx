import type { Metadata } from "next";
import Container from "@/components/layout/Container";
import PageBanner from "@/components/ui/PageBanner";
import SkillIntervention from "@/components/math/SkillIntervention";
import { getLessonNav } from "@/lib/lessons";

export const metadata: Metadata = {
  title: "Skill Intervention | Math | Plug N Play",
  description:
    "Tier 2 skill intervention organized as a learning progression per standard — targeted practice, activities, teacher moves, and printable packets.",
};

export default async function InterventionPage() {
  const lessonNav = await getLessonNav();
  return (
    <>
      <PageBanner
        tone="light"
        title="Skill intervention"
        subtitle="Pick a standard to see its learning progression — skills organized by Looking Back, On Grade, and Looking Forward, each with practice, activities, and teacher moves."
        back={{ href: "/math", label: "Back to Math" }}
      />

      <section className="bg-pnp-gray-50 py-10 md:py-14">
        <Container>
          <SkillIntervention lessonNav={lessonNav} />
        </Container>
      </section>
    </>
  );
}
