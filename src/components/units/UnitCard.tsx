import type { UnitFile } from "@/lib/core/types";
import Card from "@/components/ui/Card";
import { brandAccent } from "@/lib/core/constants";
import { ArrowRightIcon } from "@/components/ui/icons";

/**
 * One unit tile on the `/math/units` grid. Shares the Card vocabulary with
 * the rest of the app (navy border + hard offset shadow). The top stripe
 * cycles through the brand palette by teaching order so a teacher can
 * eyeball units by color — no off-palette hex, no misleading number label.
 */
interface Props {
  unit: UnitFile;
}

export default function UnitCard({ unit }: Props) {
  const orderForColor = unit.teachingOrder ?? unit.moduleNumber;
  const color = brandAccent(orderForColor - 1);
  const taskCount = unit.sections.reduce((n, s) => n + s.taskIds.length, 0);

  return (
    <Card href={`/math/units/${unit.id}`} accent={color} className="h-full">
      <div className="flex h-full flex-col p-6">
        <div className="flex items-start justify-end">
          <div className="text-right text-xs tracking-wider text-pnp-gray-500">
            Grade {unit.grade}
            {unit.estimatedDays && (
              <div className="font-mono text-pnp-gray-500">
                ~{unit.estimatedDays} days
              </div>
            )}
          </div>
        </div>

        <h3 className="mt-3 font-heading text-xl font-bold text-pnp-navy">
          {unit.title}
        </h3>
        <p className="mt-2 flex-1 text-sm leading-relaxed text-pnp-gray-600">
          {unit.preview}
        </p>

        <div className="mt-4 flex items-center justify-between text-sm font-semibold">
          <span className="inline-flex items-center gap-1.5 text-pnp-accent">
            Open
            <ArrowRightIcon
              size={15}
              className="transition-transform group-hover:translate-x-1"
            />
          </span>
          <span className="text-xs font-medium text-pnp-gray-500">
            {taskCount} task{taskCount === 1 ? "" : "s"} ·{" "}
            {unit.sections.length} section{unit.sections.length === 1 ? "" : "s"}
          </span>
        </div>
      </div>
    </Card>
  );
}
