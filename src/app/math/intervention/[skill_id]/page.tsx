import { notFound } from "next/navigation";
import type { Metadata } from "next";
import Container from "@/components/layout/Container";
import PageBanner from "@/components/ui/PageBanner";
import SkillDetail from "@/components/math/SkillDetail";
import { getStrategyById } from "@/lib/content";
import {
  AVAILABLE_STANDARDS,
  findSkillById,
  isV2,
  progressionStep,
} from "@/lib/skills";
import type { ContentEnvelope } from "@/lib/types";

/**
 * Skill detail page — the drill-in for one skill of a standard's learning
 * progression: Practice · Activities · Strategies · Teacher Moves.
 * Only v2 skills (with authored resource sections) get this page; v1
 * skills 404 here and keep their legacy card on the progression view.
 */

function findV2Skill(skillId: string) {
  const found = findSkillById(skillId);
  if (!found) return null;
  if (!isV2(found.data) || !found.skill.practice_problems) return null;
  return found;
}

export function generateStaticParams() {
  return Object.values(AVAILABLE_STANDARDS)
    .filter((data) => isV2(data))
    .flatMap((data) =>
      data.skills
        .filter((s) => s.practice_problems)
        .map((s) => ({ skill_id: s.skill_id }))
    );
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ skill_id: string }>;
}): Promise<Metadata> {
  const { skill_id } = await params;
  const found = findV2Skill(skill_id);
  if (!found) return { title: "Skill Not Found | Plug N Play" };
  return {
    title: `${found.skill.name} | Skill Intervention | Plug N Play`,
    description: `Practice, activities, strategies, and teacher moves for ${found.skill.name} (${found.data.standard_code}).`,
  };
}

export default async function SkillDetailPage({
  params,
}: {
  params: Promise<{ skill_id: string }>;
}) {
  const { skill_id } = await params;
  const found = findV2Skill(skill_id);
  if (!found) notFound();
  const { skill, data } = found;

  // Resolve linked strategies to full envelopes so the client renders the
  // canonical StrategyCard. Dangling ids are dropped with a dev-time warn.
  const strategies: Array<{ envelope: ContentEnvelope; why: string }> = [];
  for (const link of skill.strategy_links ?? []) {
    const envelope = await getStrategyById(link.strategy_id);
    if (envelope) {
      strategies.push({ envelope, why: link.why });
    } else if (process.env.NODE_ENV !== "production") {
      console.warn(
        `[skill-detail] ${skill.skill_id} links unknown strategy id "${link.strategy_id}"`
      );
    }
  }

  const step = progressionStep(data, skill.skill_id);

  return (
    <>
      <PageBanner
        tone="light"
        title={skill.name}
        subtitle={data.standard_text}
        back={{ href: "/math/intervention", label: "Back to skill intervention" }}
      />

      <section className="bg-pnp-gray-50 py-10 md:py-14">
        <Container>
          <SkillDetail
            skill={skill}
            standardCode={data.standard_code}
            standardText={data.standard_text}
            rationale={step?.rationale}
            strategies={strategies}
          />
        </Container>
      </section>
    </>
  );
}
