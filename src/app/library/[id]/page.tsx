import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { getAllStrategies, getStrategyById } from "@/lib/content";
import { getSubjectBySlug, PURPOSES } from "@/lib/constants";
import Container from "@/components/layout/Container";
import PageBanner from "@/components/ui/PageBanner";
import Badge, { type BadgeTone } from "@/components/ui/Badge";
import Tag from "@/components/ui/Tag";
import type { StrategyBody } from "@/lib/types";

const SUBJECT_TONE: Record<string, BadgeTone> = {
  math: "blue",
  science: "teal",
};
const TIER_TONE: Record<number, BadgeTone> = { 1: "emerald", 2: "yellow", 3: "red" };

export async function generateStaticParams() {
  const strategies = await getAllStrategies();
  return strategies.map((s) => ({ id: s.id }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const strategy = await getStrategyById(id);
  if (!strategy) return { title: "Strategy Not Found | Plug N Play" };
  return {
    title: `${strategy.title} | Plug N Play`,
    description: strategy.preview,
  };
}

function SectionBlock({
  title,
  content,
  icon,
  highlight,
}: {
  title: string;
  content: string;
  icon: React.ReactNode;
  highlight?: boolean;
}) {
  return (
    <div
      className={`rounded-lg border p-6 ${
        highlight
          ? "border-pnp-orange/30 bg-pnp-orange/5"
          : "border-pnp-gray-200 bg-white"
      }`}
    >
      <div className="mb-3 flex items-center gap-3">
        <div
          className={`flex h-9 w-9 items-center justify-center rounded-lg ${
            highlight
              ? "bg-pnp-orange/15 text-pnp-orange"
              : "bg-pnp-navy/5 text-pnp-navy"
          }`}
        >
          {icon}
        </div>
        <h2 className={`font-heading text-lg font-bold ${highlight ? "text-pnp-orange" : "text-pnp-navy"}`}>
          {title}
        </h2>
      </div>
      <div className="whitespace-pre-line text-sm leading-relaxed text-pnp-gray-700">
        {content}
      </div>
    </div>
  );
}

function formatPurpose(value: string): string {
  const found = PURPOSES.find((p) => p.value === value);
  return found?.label ?? value.split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
}

export default async function StrategyDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const strategy = await getStrategyById(id);
  if (!strategy) notFound();

  const body = strategy.body as StrategyBody;

  return (
    <>
      <PageBanner
        back={{ href: "/library", label: "Back to strategies" }}
        title={strategy.title}
        subtitle={strategy.preview}
      />

      {/* Content area */}
      <section className="bg-pnp-gray-50 py-10 md:py-14">
        <Container>
          {/* Subject + purpose metadata */}
          <div className="mb-8 flex flex-wrap gap-2">
            {strategy.subjects.map((sub) => (
              <Badge key={sub} tone={SUBJECT_TONE[sub] ?? "neutral"}>
                {getSubjectBySlug(sub)?.label ?? sub}
              </Badge>
            ))}
            {strategy.purposes.map((p) => (
              <Tag key={p}>{formatPurpose(p)}</Tag>
            ))}
          </div>

          <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
            {/* Main content - body sections */}
            <div className="space-y-6">
              <SectionBlock
                title="Summary"
                content={body.summary}
                icon={
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                    <line x1="16" y1="13" x2="8" y2="13" />
                    <line x1="16" y1="17" x2="8" y2="17" />
                  </svg>
                }
              />

              <SectionBlock
                title="When to Use"
                content={body.whenToUse}
                icon={
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10" />
                    <polyline points="12 6 12 12 16 14" />
                  </svg>
                }
              />

              <SectionBlock
                title="How to Implement"
                content={body.howToImplement}
                icon={
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="9 11 12 14 22 4" />
                    <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" />
                  </svg>
                }
              />

              {body.teacherMoves && (
                <SectionBlock
                  title="Teacher Moves — When Things Go Sideways"
                  content={body.teacherMoves}
                  icon={
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                      <line x1="12" y1="9" x2="12" y2="13" />
                      <line x1="12" y1="17" x2="12.01" y2="17" />
                    </svg>
                  }
                  highlight
                />
              )}

              <SectionBlock
                title="Variations & Differentiation"
                content={body.variations}
                icon={
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="18" y1="20" x2="18" y2="10" />
                    <line x1="12" y1="20" x2="12" y2="4" />
                    <line x1="6" y1="20" x2="6" y2="14" />
                  </svg>
                }
              />

              <SectionBlock
                title="Research Base"
                content={body.researchBase}
                icon={
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z" />
                    <path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z" />
                  </svg>
                }
              />
            </div>

            {/* Sidebar - quick info */}
            <div className="space-y-6">
              {/* At a Glance card */}
              <div className="rounded-lg border border-pnp-gray-200 bg-white p-6">
                <h3 className="mb-4 font-heading text-base font-bold text-pnp-navy">
                  At a glance
                </h3>

                <div className="space-y-4">
                  {/* Time */}
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wider text-pnp-gray-500">
                      Time
                    </p>
                    <p className="mt-1 text-sm font-semibold text-pnp-navy">
                      {strategy.time.minMinutes}&ndash;{strategy.time.maxMinutes} minutes
                    </p>
                  </div>

                  {/* Grades */}
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wider text-pnp-gray-500">
                      Grades
                    </p>
                    <div className="mt-1 flex gap-2">
                      {strategy.grades.map((g) => (
                        <span
                          key={g}
                          className="rounded bg-pnp-gray-100 px-2.5 py-1 text-sm font-semibold text-pnp-navy"
                        >
                          {g}th
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* MTSS Tiers */}
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wider text-pnp-gray-500">
                      MTSS Tier
                    </p>
                    <div className="mt-1 flex gap-2">
                      {strategy.mtssTiers.map((t) => (
                        <Badge key={t} tone={TIER_TONE[t] ?? "neutral"}>
                          Tier {t}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* Scope */}
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wider text-pnp-gray-500">
                      Scope
                    </p>
                    <p className="mt-1 text-sm font-semibold capitalize text-pnp-navy">
                      {strategy.scope}
                    </p>
                  </div>

                  {/* Standards */}
                  {(strategy.standards.indiana.length > 0 ||
                    strategy.standards.commonCore.length > 0 ||
                    strategy.standards.ngss.length > 0) && (
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-wider text-pnp-gray-500">
                        Standards
                      </p>
                      <div className="mt-1 flex flex-wrap gap-1.5">
                        {strategy.standards.indiana.map((s) => (
                          <span key={s} className="rounded bg-pnp-blue/10 px-2 py-0.5 text-xs font-medium text-pnp-blue">
                            IN: {s}
                          </span>
                        ))}
                        {strategy.standards.commonCore.map((s) => (
                          <span key={s} className="rounded bg-pnp-orange/10 px-2 py-0.5 text-xs font-medium text-pnp-orange">
                            CC: {s}
                          </span>
                        ))}
                        {strategy.standards.ngss.map((s) => (
                          <span key={s} className="rounded bg-pnp-teal/10 px-2 py-0.5 text-xs font-medium text-pnp-teal">
                            NGSS: {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Tags */}
              <div className="rounded-lg border border-pnp-gray-200 bg-white p-6">
                <h3 className="mb-3 font-heading text-base font-bold text-pnp-navy">
                  Tags
                </h3>
                <div className="flex flex-wrap gap-2">
                  {strategy.tags.map((tag) => (
                    <Tag key={tag}>{tag}</Tag>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </Container>
      </section>
    </>
  );
}
