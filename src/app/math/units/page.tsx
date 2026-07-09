import type { Metadata } from "next";
import Link from "next/link";
import Container from "@/components/layout/Container";
import { getAllUnits } from "@/lib/units";
import UnitsBrowse from "@/components/units/UnitsBrowse";

export const metadata: Metadata = {
  title: "Units | Math | Plug N Play",
  description:
    "Browse math rich tasks by unit and learning objective. The teacher-planning view of the same task library.",
};

/**
 * Units landing. Server component — fetches every unit JSON and hands the
 * collection to the client browser, which owns the grade-tab state.
 */
export default async function MathUnitsPage() {
  const all = await getAllUnits();
  // Math-only here. Other subjects get their own routes later.
  const units = all.filter((u) => u.id.includes("module") || true);
  return (
    <>
      {/* Banner — same shape as `/math/rich-tasks` so the user feels at home
          when toggling between modes. */}
      <section className="bg-pnp-navy py-8 md:py-12">
        <Container>
          <Link
            href="/math"
            className="mb-3 inline-flex items-center gap-2 text-sm font-semibold text-white/70 transition-colors hover:text-white"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 12H5M12 19l-7-7 7-7" />
            </svg>
            Back to Math
          </Link>
          <h1
            className="font-heading font-extrabold uppercase tracking-wide text-white"
            style={{ fontSize: "clamp(1.75rem, 3.5vw, 2.5rem)" }}
          >
            Rich Tasks · By Unit
          </h1>
          <p className="mt-2 max-w-2xl text-base text-white/75 md:text-lg">
            Pick a grade, then a unit. Each unit lists its learning objectives and the tasks that fit them.
          </p>
        </Container>
      </section>

      <section className="bg-pnp-gray-50 py-8 md:py-12">
        <Container>
          {units.length === 0 ? (
            <div className="rounded-lg border-2 border-dashed border-pnp-gray-200 bg-white py-16 text-center">
              <p className="text-lg font-semibold text-pnp-gray-700">
                Units are on the way
              </p>
              <p className="mt-1 text-sm text-pnp-gray-500">
                We&rsquo;re building out grades 6&ndash;8. Check back soon &mdash; or open the Problem Generator to build a set for any standard you teach.
              </p>
              <Link
                href="/math/generator"
                className="mt-4 inline-flex h-11 items-center rounded-md border border-pnp-gray-300 bg-white px-5 text-sm font-semibold text-pnp-navy transition-colors hover:bg-pnp-gray-50"
              >
                Open the generator
              </Link>
            </div>
          ) : (
            <UnitsBrowse units={units} />
          )}
        </Container>
      </section>
    </>
  );
}
