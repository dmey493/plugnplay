import { getAllNumberTalks } from "@/lib/library/number-talks";
import { getAllWodb } from "@/lib/library/wodb";

/**
 * Library warm-ups (Number Talks + Which One Doesn't Belong) matched to a
 * standard. Both decks tag every item with its `std`, so the skill pages can
 * surface ready-made conceptual warm-ups with zero per-skill authoring —
 * the Ground layer's five-minute opener, pulled from content that already
 * ships. Links deep-link into the tools' existing ?grade&talk / ?grade&set
 * handling.
 */
export interface WarmupLink {
  kind: "talk" | "wodb";
  id: string;
  title: string;
  concept: string;
  grade: number;
  href: string;
}

export function getWarmupsForStandard(standardCode: string): WarmupLink[] {
  const out: WarmupLink[] = [];
  for (const g of getAllNumberTalks()) {
    for (const t of g.talks) {
      if (t.std === standardCode) {
        out.push({
          kind: "talk",
          id: t.id,
          title: t.title,
          concept: t.concept,
          grade: g.grade,
          href: `/math/number-talks?grade=${g.grade}&talk=${encodeURIComponent(t.id)}`,
        });
      }
    }
  }
  for (const g of getAllWodb()) {
    for (const s of g.sets) {
      if (s.std === standardCode) {
        out.push({
          kind: "wodb",
          id: s.id,
          title: s.title,
          concept: s.concept,
          grade: g.grade,
          href: `/math/wodb?grade=${g.grade}&set=${encodeURIComponent(s.id)}`,
        });
      }
    }
  }
  return out;
}
