import { primaryStandard as primaryStandardOf, formatOf } from "@/lib/library/tasks-filter";
import { getStandardLabel } from "@/lib/standards/standards-labels";
import type { ContentEnvelope, TaskBody } from "@/lib/core/types";
import Badge, { type BadgeTone } from "@/components/ui/Badge";
import Tag from "@/components/ui/Tag";
import Card from "@/components/ui/Card";

// Unified umbrella: every card in the library is either a Rich Task or a
// Thin Slice. The narrower sub-types (Anchor / Investigation / Three-Act /
// Warm-Up / Performance / Problem Set) are no longer surfaced — Dave's
// "combine things" pass. The underlying `body.taskType` stays in the JSON
// for authoring history but isn't shown to teachers.
const FORMAT_LABEL: Record<"rich-task" | "thin-slice", string> = {
  "rich-task": "Rich Task",
  "thin-slice": "Thin Slice",
};
const FORMAT_TONE: Record<"rich-task" | "thin-slice", BadgeTone> = {
  "rich-task": "blue",
  "thin-slice": "teal",
};
// Top-stripe accent matching the format Badge (brand tokens only).
const FORMAT_ACCENT: Record<"rich-task" | "thin-slice", string> = {
  "rich-task": "#3f42d9",
  "thin-slice": "#0d9488",
};

function ClockIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0">
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  );
}

export default function TaskCard({ task }: { task: ContentEnvelope }) {
  // Cast as TaskBody for convenience; thin-slice bodies share the same
  // common fields (goal, concepts, source) we read here.
  const body = task.body as TaskBody;
  const format = formatOf(task);
  const formatTone = FORMAT_TONE[format];
  const formatLabel = FORMAT_LABEL[format];
  const sourceShort = body.source?.name?.split(" ")[0] ?? "";
  const primaryStandard = primaryStandardOf(task);
  const primaryStandardLabel = primaryStandard
    ? getStandardLabel(primaryStandard, "indiana")
    : "";
  const concepts = (body.concepts ?? []).slice(0, 3);
  // Thin slices land on `/math/thin-slices/[id]/project` (their projection
  // runner). Rich tasks land on their detail page. The card is the affordance
  // either way — same hover, same card shape.
  const href =
    format === "thin-slice"
      ? `/math/thin-slices/${task.id}/project`
      : `/math/rich-tasks/${task.id}`;

  return (
    <Card href={href} accent={FORMAT_ACCENT[format]} className="h-full">
      <div className="flex h-full flex-col p-5">
        {/* Top row: type Badge on left, standard code Tag on right.
            Both are muted metadata — they communicate categorisation, not
            tappability. The whole card IS the action. */}
        <div className="mb-3 flex items-start justify-between gap-2">
          <Badge tone={formatTone}>{formatLabel}</Badge>
          {primaryStandard && (
            <Tag variant="code" title={primaryStandardLabel || primaryStandard}>
              {primaryStandard}
            </Tag>
          )}
        </div>

        {/* Title */}
        <h3 className="font-heading text-lg font-bold leading-snug text-pnp-navy line-clamp-2">
          {task.title}
        </h3>

        {/* Concept chips — muted Tags so they don't compete with real
            actions on the page. Capped at 3 to keep the card compact. */}
        {concepts.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {concepts.map((c) => (
              <Tag key={c}>{c}</Tag>
            ))}
          </div>
        )}

        {/* Goal (replaces preview for tasks — student-facing focus) */}
        <p className="mt-2 flex-1 text-sm leading-relaxed text-pnp-gray-600 line-clamp-3">
          {body.goal || task.preview}
        </p>

        {/* Bottom metadata */}
        <div className="mt-4 flex items-center gap-3 border-t border-pnp-gray-100 pt-3 text-xs text-pnp-gray-500">
          <div className="flex gap-1">
            {task.grades.map((g) => (
              <Tag key={g}>{g}th</Tag>
            ))}
          </div>

          <div className="flex items-center gap-1">
            <ClockIcon />
            <span>{task.time.minMinutes}-{task.time.maxMinutes} min</span>
          </div>

          <div className="ml-auto text-xs italic text-pnp-gray-500">
            {sourceShort}
          </div>
        </div>
      </div>
    </Card>
  );
}
