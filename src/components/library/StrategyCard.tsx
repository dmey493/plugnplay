import type { ContentEnvelope } from "@/lib/types";
import { getSubjectBySlug } from "@/lib/constants";
import Card from "@/components/ui/Card";
import Badge, { type BadgeTone } from "@/components/ui/Badge";
import Tag from "@/components/ui/Tag";
import { ClockIcon } from "@/components/ui/icons";

// Subject → Badge tone, and MTSS tier → Badge tone. Replaces the old
// pill-shaped, inline-colored spans and the vanilla green/yellow/red tier
// chips with the shared Badge so metadata reads consistently everywhere.
const SUBJECT_TONE: Record<string, BadgeTone> = {
  math: "blue",
  science: "teal",
};
const TIER_TONE: Record<number, BadgeTone> = { 1: "emerald", 2: "yellow", 3: "red" };

function titleCase(s: string) {
  return s
    .split("-")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

export default function StrategyCard({ strategy }: { strategy: ContentEnvelope }) {
  const primarySubject = getSubjectBySlug(strategy.subjects[0]);
  const accent = primarySubject?.color ?? "#1a1f3d";

  return (
    <Card href={`/library/${strategy.id}`} accent={accent} className="h-full">
      <div className="flex h-full flex-col p-5">
        {/* Subject + purpose metadata */}
        <div className="mb-3 flex flex-wrap gap-2">
          {strategy.subjects.map((sub) => (
            <Badge key={sub} tone={SUBJECT_TONE[sub] ?? "neutral"}>
              {getSubjectBySlug(sub)?.label ?? sub}
            </Badge>
          ))}
          {strategy.purposes.slice(0, 2).map((p) => (
            <Tag key={p}>{titleCase(p)}</Tag>
          ))}
        </div>

        <h3 className="font-heading text-lg font-bold leading-snug text-pnp-navy line-clamp-2">
          {strategy.title}
        </h3>

        <p className="mt-2 flex-1 text-sm leading-relaxed text-pnp-gray-600 line-clamp-2">
          {strategy.preview}
        </p>

        <div className="mt-4 flex items-center gap-3 border-t border-pnp-gray-100 pt-3 text-xs text-pnp-gray-500">
          <div className="flex gap-1">
            {strategy.grades.map((g) => (
              <Tag key={g}>{g}th</Tag>
            ))}
          </div>
          <div className="flex items-center gap-1">
            <ClockIcon size={14} />
            <span>
              {strategy.time.minMinutes}-{strategy.time.maxMinutes} min
            </span>
          </div>
          <div className="ml-auto flex gap-1">
            {strategy.mtssTiers.map((t) => (
              <Badge key={t} tone={TIER_TONE[t] ?? "neutral"}>
                Tier {t}
              </Badge>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
}
