import type { Metadata } from "next";
import { notFound } from "next/navigation";
import PageBanner from "@/components/ui/PageBanner";
import StimulusView from "@/components/science/StimulusView";
import { STANDARDS, DOMAINS, DOMAIN_ACCENT, getStandard } from "@/lib/library/science";

export function generateStaticParams() {
  return STANDARDS.map((s) => ({ pe: s.pe }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ pe: string }>;
}): Promise<Metadata> {
  const { pe } = await params;
  const std = getStandard(pe);
  if (!std) return { title: "Standard not found | Plug N Play" };
  return {
    title: `${pe} — Biology stimuli | Plug N Play`,
    description: std.pe_text,
  };
}

export default async function StandardPage({
  params,
}: {
  params: Promise<{ pe: string }>;
}) {
  const { pe } = await params;
  const std = getStandard(pe);
  if (!std) notFound();

  const domain = DOMAINS.find((d) => d.code === std.domain);
  const accent = DOMAIN_ACCENT[std.domain] ?? "var(--pnp-accent)";

  return (
    <>
      <PageBanner
        title={pe}
        subtitle={std.pe_text}
        back={{ href: "/science/generator", label: "Stimulus generator" }}
        tone="navy"
      />

      <div className="mx-auto max-w-3xl px-5 py-10 sm:px-8">
        {domain && (
          <p className="mb-6 flex items-center gap-2 text-sm font-semibold text-[var(--pnp-gray-500)]">
            <span
              className="inline-block h-3 w-3 rounded-sm"
              style={{ background: accent }}
              aria-hidden
            />
            {domain.code} · {domain.title}
          </p>
        )}

        <div className="space-y-10">
          {std.stimuli.map((stimulus, i) => (
            <StimulusView
              key={i}
              stimulus={stimulus}
              pe={std.pe}
              peText={std.pe_text}
              index={i + 1}
              accent={accent}
            />
          ))}
        </div>
      </div>
    </>
  );
}
