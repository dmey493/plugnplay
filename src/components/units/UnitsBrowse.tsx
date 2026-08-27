"use client";

import { useMemo, useState } from "react";
import Button from "@/components/ui/Button";
import { ArrowRightIcon } from "@/components/ui/icons";
import type { UnitFile } from "@/lib/core/types";
import UnitCard from "./UnitCard";
import BrowseModeToggle from "./BrowseModeToggle";

/**
 * Client browser for the Units landing.
 *
 * Owns: grade tab state (6 / 7 / 8). Receives the full set of units from
 * the server page and filters in-memory — we never have more than a few
 * dozen units, so client-side filtering is the simpler path.
 *
 * The browse-mode toggle (Unit / Standard / Concept) is rendered above
 * the grade tabs so the teacher can hop back to standards browse without
 * scrolling. Routing-only — no internal mode state.
 */
interface Props {
  units: UnitFile[];
}

export default function UnitsBrowse({ units }: Props) {
  // Default to whichever grade has the most units. Falls back to 8 if
  // nothing's authored yet so the empty state is consistent.
  const defaultGrade = useMemo(() => {
    const counts = new Map<6 | 7 | 8, number>();
    for (const u of units) counts.set(u.grade, (counts.get(u.grade) ?? 0) + 1);
    let best: 6 | 7 | 8 = 8;
    let bestN = -1;
    for (const [g, n] of counts) {
      if (n > bestN) {
        best = g;
        bestN = n;
      }
    }
    return best;
  }, [units]);

  const [grade, setGrade] = useState<6 | 7 | 8>(defaultGrade);

  const grades: (6 | 7 | 8)[] = [6, 7, 8];
  const visible = units.filter((u) => u.grade === grade);

  return (
    <div className="space-y-6">
      {/* Top row: browse-mode toggle (routing-only) + grade tabs */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <BrowseModeToggle current="unit" />
        <div
          role="tablist"
          aria-label="Grade"
          className="inline-flex items-center gap-1 rounded-lg border border-pnp-gray-200 bg-white p-1"
        >
          {grades.map((g) => {
            const active = grade === g;
            return (
              <button
                key={g}
                type="button"
                role="tab"
                aria-selected={active}
                onClick={() => setGrade(g)}
                className={[
                  "inline-flex h-9 select-none items-center rounded-md px-3 text-sm font-semibold",
                  "transition-[background-color,color,transform] duration-150 ease-out",
                  "active:scale-[0.98]",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2",
                  active
                    ? "bg-pnp-accent text-white"
                    : "text-pnp-gray-700 hover:bg-pnp-gray-100",
                ].join(" ")}
              >
                Grade {g}
              </button>
            );
          })}
        </div>
      </div>

      {visible.length === 0 ? (
        <div className="rounded-xl border-2 border-dashed border-pnp-gray-300 bg-white py-14 text-center">
          <p className="text-base font-semibold text-pnp-gray-700">
            No Grade {grade} units yet
          </p>
          <p className="mt-1 text-sm text-pnp-gray-600">
            Other grades may have content — try the tabs above.
          </p>
          <div className="mt-3 flex justify-center">
            <Button
              href="/math/rich-tasks"
              tier="tertiary"
              trailingIcon={<ArrowRightIcon size={15} />}
            >
              Browse all tasks
            </Button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
          {visible.map((unit) => (
            <UnitCard key={unit.id} unit={unit} />
          ))}
        </div>
      )}
    </div>
  );
}
