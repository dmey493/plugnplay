import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { getAllStrategies, getStrategyById } from "@/lib/library/strategies";
import { getSubjectBySlug, PURPOSES } from "@/lib/core/constants";
import Container from "@/components/layout/Container";
import PageBanner from "@/components/ui/PageBanner";
import Card from "@/components/ui/Card";
import Badge, { type BadgeTone } from "@/components/ui/Badge";
import Tag from "@/components/ui/Tag";
import type { StrategyBody } from "@/lib/core/types";

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

/* --- Icons ------------------------------------------------------------- */
const ICON = {
  when: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.25" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  ),
  how: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.25" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="9 11 12 14 22 4" />
      <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" />
    </svg>
  ),
  moves: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.25" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  ),
  variations: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.25" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="20" x2="18" y2="10" />
      <line x1="12" y1="20" x2="12" y2="4" />
      <line x1="6" y1="20" x2="6" y2="14" />
    </svg>
  ),
  research: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.25" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z" />
      <path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z" />
    </svg>
  ),
} as const;

/**
 * PrimarySection — the "do it now" pair (When to Use, How to Implement).
 * Full comic depth via the shared Card, a coloured accent stripe, and a
 * large heading with a filled icon chip so it reads as the loudest thing
 * on the page.
 */
function PrimarySection({
  eyebrow,
  title,
  content,
  icon,
  accent,
  chip,
}: {
  eyebrow: string;
  title: string;
  content: string;
  icon: React.ReactNode;
  accent: string;
  chip: string;
}) {
  return (
    <Card accent={accent}>
      <div className="p-6 md:p-7">
        <div className="mb-4 flex items-center gap-3">
          <span className={`flex h-11 w-11 flex-none items-center justify-center rounded-lg text-white ${chip}`}>
            {icon}
          </span>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-pnp-gray-500">
              {eyebrow}
            </p>
            <h2 className="font-heading text-xl font-extrabold leading-tight text-pnp-navy md:text-2xl">
              {title}
            </h2>
          </div>
        </div>
        <div className="whitespace-pre-line text-[15px] leading-relaxed text-pnp-gray-700">
          {content}
        </div>
      </div>
    </Card>
  );
}

/**
 * TeacherMovesAside — the "when things go sideways" callout. Orange comic
 * card with a soft orange fill so it reads as a distinct aside, not a peer
 * of the primary steps.
 */
function TeacherMovesAside({ content }: { content: string }) {
  return (
    <div className="overflow-hidden rounded-xl border-2 border-pnp-navy bg-pnp-orange/5 shadow-[4px_4px_0_var(--pnp-navy)]">
      <span className="block h-1.5 bg-pnp-orange" aria-hidden="true" />
      <div className="p-6">
        <div className="mb-3 flex items-center gap-3">
          <span className="flex h-9 w-9 flex-none items-center justify-center rounded-lg bg-pnp-orange text-white">
            {ICON.moves}
          </span>
          <h2 className="font-heading text-lg font-bold text-pnp-navy">
            When things go sideways
          </h2>
        </div>
        <div className="whitespace-pre-line text-sm leading-relaxed text-pnp-gray-700">
          {content}
        </div>
      </div>
    </div>
  );
}

/**
 * ReferenceSection — quieter, collapsed-by-default reference material
 * (Variations, Research Base). Native <details> so it stays
 * reduced-motion-safe with no JS.
 */
function ReferenceSection({
  title,
  content,
  icon,
}: {
  title: string;
  content: string;
  icon: React.ReactNode;
}) {
  return (
    <details className="group rounded-xl border-2 border-pnp-navy bg-white shadow-[2px_2px_0_var(--pnp-navy)]">
      <summary className="flex cursor-pointer list-none items-center gap-3 rounded-xl px-5 py-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2">
        <span className="flex h-8 w-8 flex-none items-center justify-center rounded-lg bg-pnp-navy/5 text-pnp-navy">
          {icon}
        </span>
        <h2 className="flex-1 font-heading text-base font-bold text-pnp-navy">
          {title}
        </h2>
        <svg
          className="h-5 w-5 flex-none text-pnp-gray-400 transition-transform group-open:rotate-180"
          viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.25" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </summary>
      <div className="whitespace-pre-line border-t-2 border-pnp-gray-100 px-5 py-4 text-sm leading-relaxed text-pnp-gray-700">
        {content}
      </div>
    </details>
  );
}

function InfoRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-wider text-pnp-gray-500">
        {label}
      </p>
      <div className="mt-1.5">{children}</div>
    </div>
  );
}

function formatPurpose(value: string): string {
  const found = PURPOSES.find((p) => p.value === value);
  return found?.label ?? value.split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
}

/** Split the summary prose into scannable bullet points on sentence
 *  boundaries (keeps the terminal punctuation with each point). */
function toSummaryPoints(summary: string): string[] {
  return summary
    .split(/(?<=[.!?])\s+/)
    .map((s) => s.trim())
    .filter(Boolean);
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

  const hasStandards =
    strategy.standards.indiana.length > 0 ||
    strategy.standards.commonCore.length > 0 ||
    strategy.standards.ngss.length > 0;

  return (
    <>
      <PageBanner
        back={{ href: "/library", label: "Back to strategies" }}
        title={strategy.title}
        subtitle={strategy.preview}
      />

      <section className="bg-pnp-gray-50 py-10 md:py-14">
        <Container>
          {/* Subject + purpose metadata */}
          <div className="mb-6 flex flex-wrap gap-2">
            {strategy.subjects.map((sub) => (
              <Badge key={sub} tone={SUBJECT_TONE[sub] ?? "neutral"}>
                {getSubjectBySlug(sub)?.label ?? sub}
              </Badge>
            ))}
            {strategy.purposes.map((p) => (
              <Tag key={p}>{formatPurpose(p)}</Tag>
            ))}
          </div>

          {/* Summary as a scannable lead-in — quick bullets, not a wall of text */}
          {body.summary && (
            <div className="mb-10 max-w-3xl">
              <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-pnp-gray-500">
                Summary
              </p>
              <ul className="space-y-1.5">
                {toSummaryPoints(body.summary).map((point, i) => (
                  <li
                    key={i}
                    className="flex gap-2.5 text-[15px] leading-relaxed text-pnp-gray-700"
                  >
                    <span
                      className="mt-2 h-1.5 w-1.5 flex-none rounded-full bg-pnp-accent"
                      aria-hidden="true"
                    />
                    <span>{point}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
            {/* Main column */}
            <div className="space-y-6">
              {/* PRIMARY — the do-it-now pair */}
              <PrimarySection
                eyebrow="Start here"
                title="When to use it"
                content={body.whenToUse}
                icon={ICON.when}
                accent="var(--pnp-blue)"
                chip="bg-pnp-blue"
              />
              <PrimarySection
                eyebrow="Then run it"
                title="How to implement"
                content={body.howToImplement}
                icon={ICON.how}
                accent="var(--pnp-accent)"
                chip="bg-pnp-accent"
              />

              {/* ASIDE — when things go sideways */}
              {body.teacherMoves && <TeacherMovesAside content={body.teacherMoves} />}

              {/* REFERENCE — collapsed by default */}
              <div className="space-y-3 pt-2">
                <p className="text-xs font-semibold uppercase tracking-wider text-pnp-gray-500">
                  Go deeper
                </p>
                <ReferenceSection
                  title="Variations & differentiation"
                  content={body.variations}
                  icon={ICON.variations}
                />
                <ReferenceSection
                  title="Research base"
                  content={body.researchBase}
                  icon={ICON.research}
                />
              </div>
            </div>

            {/* Sidebar — at a glance */}
            <div className="space-y-6">
              <Card>
                <div className="p-6">
                  <h3 className="mb-4 font-heading text-base font-bold text-pnp-navy">
                    At a glance
                  </h3>
                  <div className="space-y-4">
                    <InfoRow label="Time">
                      <p className="text-sm font-semibold text-pnp-navy">
                        {strategy.time.minMinutes}&ndash;{strategy.time.maxMinutes} minutes
                      </p>
                    </InfoRow>

                    <InfoRow label="Grades">
                      <div className="flex flex-wrap gap-1.5">
                        {strategy.grades.map((g) => (
                          <Tag key={g}>{g}th</Tag>
                        ))}
                      </div>
                    </InfoRow>

                    <InfoRow label="MTSS tier">
                      <div className="flex flex-wrap gap-1.5">
                        {strategy.mtssTiers.map((t) => (
                          <Badge key={t} tone={TIER_TONE[t] ?? "neutral"}>
                            Tier {t}
                          </Badge>
                        ))}
                      </div>
                    </InfoRow>

                    <InfoRow label="Scope">
                      <p className="text-sm font-semibold capitalize text-pnp-navy">
                        {strategy.scope}
                      </p>
                    </InfoRow>

                    {hasStandards && (
                      <InfoRow label="Standards">
                        <div className="flex flex-wrap gap-1.5">
                          {strategy.standards.indiana.map((s) => (
                            <Tag key={`in-${s}`} variant="code">IN {s}</Tag>
                          ))}
                          {strategy.standards.commonCore.map((s) => (
                            <Tag key={`cc-${s}`} variant="code">CC {s}</Tag>
                          ))}
                          {strategy.standards.ngss.map((s) => (
                            <Tag key={`ngss-${s}`} variant="code">NGSS {s}</Tag>
                          ))}
                        </div>
                      </InfoRow>
                    )}
                  </div>
                </div>
              </Card>

              {strategy.tags.length > 0 && (
                <Card>
                  <div className="p-6">
                    <h3 className="mb-3 font-heading text-base font-bold text-pnp-navy">
                      Tags
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {strategy.tags.map((tag) => (
                        <Tag key={tag}>{tag}</Tag>
                      ))}
                    </div>
                  </div>
                </Card>
              )}
            </div>
          </div>
        </Container>
      </section>
    </>
  );
}
