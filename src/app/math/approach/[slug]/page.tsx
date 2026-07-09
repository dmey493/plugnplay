import { notFound } from "next/navigation";
import type { Metadata } from "next";
import {
  getAllApproachPages,
  getApproachPage,
  type ApproachSection,
} from "@/lib/approach";
import Container from "@/components/layout/Container";
import PageBanner from "@/components/ui/PageBanner";
import ApproachBlocks from "@/components/approach/ApproachBlocks";

export async function generateStaticParams() {
  return getAllApproachPages().map((p) => ({ slug: p.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const page = getApproachPage(slug);
  if (!page) return { title: "Not found | Plug N Play" };
  return {
    title: `${page.title} | Our approach | Plug N Play`,
    description: page.subtitle,
  };
}

function SectionView({
  section,
  showLabel,
}: {
  section: ApproachSection;
  showLabel: boolean;
}) {
  return (
    <section
      id={showLabel && section.label ? slugify(section.label) : undefined}
      className="scroll-mt-24"
    >
      {showLabel && section.label && (
        <div className="mb-6 flex items-center gap-3">
          <span className="h-2.5 w-2.5 rotate-45 bg-pnp-accent" aria-hidden="true" />
          <h2 className="font-heading text-lg font-extrabold uppercase tracking-wide text-pnp-navy">
            {section.label}
          </h2>
          <span className="h-px flex-1 bg-pnp-gray-200" aria-hidden="true" />
        </div>
      )}

      <ApproachBlocks blocks={section.blocks} />

      {section.sources && (
        <p className="mt-8 border-t border-pnp-gray-200 pt-4 text-xs leading-relaxed text-pnp-gray-500">
          {section.sources}
        </p>
      )}
    </section>
  );
}

function slugify(s: string): string {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

export default async function ApproachDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const page = getApproachPage(slug);
  if (!page) notFound();

  const multi = page.sections.length > 1;

  return (
    <>
      <PageBanner
        back={{ href: "/math/approach", label: "Back to our approach" }}
        title={page.title}
        subtitle={page.subtitle}
      />

      <section className="bg-pnp-gray-50 py-10 md:py-14">
        <Container>
          {/* Eyebrow + metadata chips */}
          <div className="mb-8">
            <p className="text-xs font-bold uppercase tracking-widest text-pnp-accent">
              {page.doctype}
            </p>
            {page.chips && page.chips.length > 0 && (
              <div className="mt-4 flex flex-wrap gap-2">
                {page.chips.map((chip) => (
                  <span
                    key={chip}
                    className="inline-flex select-none items-center rounded-md border-2 border-pnp-navy bg-white px-2.5 py-1 text-xs font-semibold text-pnp-navy shadow-[2px_2px_0_var(--pnp-navy)]"
                  >
                    {chip}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* In-page jump nav for multi-section (tool) pages */}
          {multi && (
            <nav
              aria-label="On this page"
              className="mb-10 flex flex-wrap gap-2 rounded-xl border-2 border-pnp-navy bg-white p-3 shadow-[3px_3px_0_var(--pnp-navy)]"
            >
              {page.sections.map(
                (s) =>
                  s.label && (
                    <a
                      key={s.label}
                      href={`#${slugify(s.label)}`}
                      className="rounded-md px-3 py-1.5 text-sm font-semibold text-pnp-navy transition-colors hover:bg-pnp-accent-soft"
                    >
                      {s.label}
                    </a>
                  )
              )}
            </nav>
          )}

          <div className="mx-auto max-w-3xl space-y-14">
            {page.sections.map((s, i) => (
              <SectionView key={i} section={s} showLabel={multi} />
            ))}
          </div>
        </Container>
      </section>
    </>
  );
}
