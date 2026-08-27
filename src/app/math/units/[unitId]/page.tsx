import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import Container from "@/components/layout/Container";
import { getUnitById, getAllUnits } from "@/lib/library/units";
import { getAllTasks } from "@/lib/library/tasks";
import { getAllThinSlices } from "@/lib/library/thin-slices";
import UnitDetail from "@/components/units/UnitDetail";

interface PageProps {
  params: Promise<{ unitId: string }>;
}

/** Pre-render every authored unit so the detail pages are static. */
export async function generateStaticParams() {
  const units = await getAllUnits();
  return units.map((u) => ({ unitId: u.id }));
}

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const { unitId } = await params;
  const unit = await getUnitById(unitId);
  if (!unit) return { title: "Unit Not Found | Plug N Play" };
  return {
    title: `${unit.title} | Math Unit | Plug N Play`,
    description: unit.preview,
  };
}

export default async function UnitDetailPage({ params }: PageProps) {
  const { unitId } = await params;
  const unit = await getUnitById(unitId);
  if (!unit) notFound();

  // Resolve task IDs to ContentEnvelopes in one shot. Tasks not found are
  // dropped silently so a stale task ID in a unit JSON doesn't break the
  // whole page — the unit detail just renders without that card.
  const allTasks = await getAllTasks();
  const tasksById = new Map(allTasks.map((t) => [t.id, t]));
  // Same pattern for thin slices — used by the secondary "Thin Slices"
  // strip under each section. Missing IDs are dropped silently.
  const allSlices = await getAllThinSlices();
  const slicesById = new Map(allSlices.map((s) => [s.id, s]));

  return (
    <>
      {/* Banner — matches the rich-tasks pages so navigation feels
          continuous when teachers hop between modes. */}
      <section className="bg-pnp-navy py-8 md:py-12">
        <Container>
          <Link
            href="/math/units"
            className="mb-3 inline-flex items-center gap-2 text-sm font-semibold text-white/70 transition-colors hover:text-white"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 12H5M12 19l-7-7 7-7" />
            </svg>
            All units
          </Link>
          <div className="flex items-baseline gap-3">
            <span className="rounded-md bg-white/10 px-2.5 py-0.5 font-mono text-xs font-bold text-white/80">
              Grade {unit.grade} · Module {unit.moduleNumber}
            </span>
          </div>
          <h1
            className="mt-2 font-heading font-extrabold text-white"
            style={{ fontSize: "clamp(1.75rem, 3.5vw, 2.5rem)" }}
          >
            {unit.title}
          </h1>
          <p className="mt-2 max-w-3xl text-base text-white/75 md:text-lg">
            {unit.description ?? unit.preview}
          </p>
        </Container>
      </section>

      <section className="bg-pnp-gray-50 py-8 md:py-12">
        <Container>
          <UnitDetail
            unit={unit}
            tasksById={tasksById}
            slicesById={slicesById}
          />
        </Container>
      </section>
    </>
  );
}
