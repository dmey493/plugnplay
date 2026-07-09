import type { Metadata } from "next";
import Link from "next/link";
import Container from "@/components/layout/Container";
import PageBanner from "@/components/ui/PageBanner";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { ArrowRightIcon } from "@/components/ui/icons";
import { ApproachIcon } from "@/components/approach/icons";
import {
  TOOLS,
  TOOL_GROUPS,
  STRANDS,
  PRACTICES,
  toolAccent,
} from "@/lib/approach";

export const metadata: Metadata = {
  title: "Our teaching approach | Math | Plug N Play",
  description:
    "The framework behind the tools: a shared vision for grades 6–8 mathematics, the two frameworks that ground it, how a lesson is built, and a toolbelt of classroom routines.",
};

export default function ApproachHubPage() {
  return (
    <>
      <PageBanner
        back={{ href: "/math", label: "Back to Math" }}
        title="Our teaching approach"
        subtitle="The framework behind the tools — a shared vision for grades 6–8 mathematics, the two frameworks that ground it, and how a lesson is built."
      />

      {/* ── Vision ── */}
      <section className="bg-pnp-navy py-12 md:py-16">
        <Container>
          <p className="text-xs font-bold uppercase tracking-widest text-pnp-yellow">
            Our vision for mathematics
          </p>
          <h2 className="mt-3 max-w-4xl font-heading text-2xl font-extrabold leading-tight text-white md:text-3xl">
            Every student reasons, talks, and makes sense of mathematics.
          </h2>
          <div className="mt-6 max-w-4xl rounded-xl border-2 border-white/15 border-l-[6px] border-l-pnp-yellow bg-white/5 p-6 text-lg leading-relaxed text-white/85">
            In grades 6–8, every math classroom develops all five strands of
            mathematical proficiency by engaging students in reasoning,
            productive struggle, and discourse around goal-focused tasks and
            number routines — while teachers pose purposeful questions, surface
            and connect student thinking, and build procedural fluency from the
            conceptual understanding students develop.
          </div>
        </Container>
      </section>

      {/* ── Two frameworks ── */}
      <section className="bg-white py-12 md:py-16">
        <Container>
          <div className="max-w-3xl">
            <h2 className="font-heading text-2xl font-extrabold text-pnp-navy md:text-3xl">
              Two frameworks, working together
            </h2>
            <p className="mt-3 leading-relaxed text-pnp-gray-600">
              Every tool connects to both. The{" "}
              <strong className="text-pnp-navy">
                Effective Teaching Practices
              </strong>{" "}
              describe what teachers do. The{" "}
              <strong className="text-pnp-navy">
                Strands of Mathematical Proficiency
              </strong>{" "}
              describe what we want for students. Coach the practices; the
              strands are the result. Select any practice or strand for details.
            </p>
          </div>

          <div className="mt-8 grid gap-6 lg:grid-cols-2">
            {/* Teaching practices */}
            <Card accent="#3f42d9" className="h-full">
              <div className="p-6">
                <h3 className="font-heading text-lg font-extrabold text-pnp-navy">
                  8 Effective Teaching Practices
                </h3>
                <p className="mt-1 text-sm text-pnp-gray-500">
                  NCTM, <em>Principles to Actions</em> (2014) · what teachers do
                </p>
                <ol className="mt-4 space-y-1">
                  {PRACTICES.map((p) => (
                    <li key={p.slug}>
                      <Link
                        href={`/math/approach/${p.slug}`}
                        className="group flex gap-3 rounded-lg px-2 py-1.5 transition-colors hover:bg-pnp-gray-50"
                      >
                        <span className="font-heading text-sm font-bold text-pnp-blue">
                          {p.n}
                        </span>
                        <span className="text-sm leading-snug text-pnp-gray-700 group-hover:text-pnp-navy">
                          {p.title}
                        </span>
                      </Link>
                    </li>
                  ))}
                </ol>
              </div>
            </Card>

            {/* Strands */}
            <Card accent="#0d9488" className="h-full">
              <div className="p-6">
                <h3 className="font-heading text-lg font-extrabold text-pnp-navy">
                  5 Strands of Mathematical Proficiency
                </h3>
                <p className="mt-1 text-sm text-pnp-gray-500">
                  <em>Adding It Up</em> (2001) · what we want for students
                </p>
                <ul className="mt-4 space-y-1">
                  {STRANDS.map((s) => (
                    <li key={s.slug}>
                      <Link
                        href={`/math/approach/${s.slug}`}
                        className="group flex flex-wrap items-baseline gap-x-2 rounded-lg px-2 py-1.5 transition-colors hover:bg-pnp-gray-50"
                      >
                        <span className="text-sm font-bold text-pnp-navy group-hover:text-pnp-accent">
                          {s.title}
                        </span>
                        <span className="text-sm text-pnp-gray-500">
                          — {s.gist}
                        </span>
                      </Link>
                    </li>
                  ))}
                </ul>
                <p className="mt-4 px-2 text-sm text-pnp-gray-500">
                  The strands are <em>interwoven</em>, not sequential. A single
                  number routine can develop four at once.
                </p>
              </div>
            </Card>
          </div>
        </Container>
      </section>

      {/* ── How a lesson is built ── */}
      <section className="bg-pnp-gray-50 py-12 md:py-16">
        <Container>
          <div className="max-w-3xl">
            <h2 className="font-heading text-2xl font-extrabold text-pnp-navy md:text-3xl">
              A lesson is fluid, not a script
            </h2>
            <p className="mt-3 leading-relaxed text-pnp-gray-600">
              Lessons are built from a few <strong>components</strong>, and
              teachers choose what each one looks like based on the day&rsquo;s
              purpose. Not every lesson uses every component — some open with a
              number routine, some launch straight into a task. What stays
              constant is that <strong>student thinking is the engine</strong>.
            </p>
          </div>

          <div className="mt-8 grid gap-5 md:grid-cols-3">
            {LESSON_COMPONENTS.map((c) => (
              <div
                key={c.title}
                className="flex flex-col rounded-xl border-2 border-pnp-navy bg-white p-6 shadow-[4px_4px_0_var(--pnp-navy)]"
              >
                <h3 className="font-heading text-lg font-extrabold text-pnp-navy">
                  {c.title}
                </h3>
                <p className="mt-2 flex-1 text-sm leading-relaxed text-pnp-gray-600">
                  {c.body}
                </p>
                <ul className="mt-4 space-y-1.5 border-t border-pnp-gray-200 pt-4 text-sm text-pnp-gray-700">
                  {c.items.map((it) => (
                    <li key={it} className="flex gap-2">
                      <span className="font-bold text-pnp-accent">›</span>
                      <span>{it}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {/* Note on direct instruction */}
          <div className="mt-6 rounded-xl border-2 border-pnp-blue/30 border-l-[6px] border-l-pnp-blue bg-pnp-blue/5 p-6">
            <p className="text-xs font-bold uppercase tracking-wide text-pnp-blue">
              A note on direct instruction — we are not anti-telling
            </p>
            <p className="mt-2 leading-relaxed text-pnp-gray-700">
              Clear, well-timed direct instruction is one of the highest-impact
              things a teacher does, and it has a permanent home in core
              instruction. This framework changes the <em>timing and length</em>{" "}
              of the tell, not whether it happens: we re-time it to land when
              students are primed for it (above all during consolidation), and
              keep it brief and broken up with student thinking — not a 30–40
              minute monologue.
            </p>
            <p className="mt-3 leading-relaxed text-pnp-gray-700">
              <strong className="text-pnp-navy">Rule of thumb:</strong> don&rsquo;t
              tell students what they can productively figure out; <em>do</em>{" "}
              tell them what they can&rsquo;t reasonably derive — conventions,
              notation, vocabulary — or what they&rsquo;ve struggled enough to be
              ready to receive.
            </p>
          </div>

          <div className="mt-4 rounded-xl border border-pnp-gray-200 bg-white p-5 text-sm leading-relaxed text-pnp-gray-700">
            <strong className="text-pnp-navy">
              Embedded moves — the how, not the what.
            </strong>{" "}
            You don&rsquo;t choose between these; you layer them onto whatever
            activity you run: Talk Moves, the &ldquo;When to Tell&rdquo; decision,
            an Access &amp; Equity lens, vertical surfaces &amp; random groups, the
            5 Practices, and connecting representations.
          </div>
        </Container>
      </section>

      {/* ── The toolbelt ── */}
      <section className="bg-white py-12 md:py-16">
        <Container>
          <div className="max-w-3xl">
            <h2 className="font-heading text-2xl font-extrabold text-pnp-navy md:text-3xl">
              The toolbelt
            </h2>
            <p className="mt-3 leading-relaxed text-pnp-gray-600">
              The component groups (Opener, Core, Practice &amp; Closure) are{" "}
              <strong>activities you choose from</strong> — pick one to run. The{" "}
              <strong>Embedded Moves</strong> are the <em>how</em>: you layer them
              onto whatever activity you run. Each tool page pairs a{" "}
              <strong>What It Is</strong> explainer with a{" "}
              <strong>Lesson Design Connection</strong>.
            </p>
          </div>

          <div className="mt-10 space-y-12">
            {TOOL_GROUPS.map((group) => {
              const tools = TOOLS.filter((t) => t.group === group.id);
              if (tools.length === 0) return null;
              return (
                <div key={group.id}>
                  <div className="mb-5 flex flex-wrap items-baseline gap-x-4 gap-y-1 border-b-2 border-pnp-gray-200 pb-3">
                    <h3 className="font-heading text-xl font-extrabold text-pnp-navy">
                      {group.title}
                    </h3>
                    <p className="text-sm text-pnp-gray-500">{group.note}</p>
                  </div>
                  <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                    {tools.map((t) => (
                      <Card
                        key={t.slug}
                        href={`/math/approach/${t.slug}`}
                        accent={toolAccent(t.group)}
                        className="h-full"
                      >
                        <div className="flex h-full flex-col p-6">
                          <span
                            className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl text-white"
                            style={{ backgroundColor: toolAccent(t.group) }}
                            aria-hidden="true"
                          >
                            <ApproachIcon name={t.icon} size={26} />
                          </span>
                          <h4 className="font-heading text-base font-extrabold text-pnp-navy">
                            {t.title}
                          </h4>
                          <p className="mt-2 flex-1 text-sm leading-relaxed text-pnp-gray-600">
                            {t.blurb}
                          </p>
                          <span className="mt-4 inline-flex items-center gap-1.5 text-sm font-semibold text-pnp-accent">
                            Open
                            <ArrowRightIcon
                              size={15}
                              className="transition-transform group-hover:translate-x-1"
                            />
                          </span>
                        </div>
                      </Card>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </Container>
      </section>

      {/* ── Leaders CTA ── */}
      <section className="bg-pnp-yellow py-12 md:py-16">
        <Container>
          <div className="flex flex-col items-start justify-between gap-6 md:flex-row md:items-center">
            <div className="max-w-2xl">
              <h2 className="font-heading text-2xl font-extrabold text-pnp-navy">
                Coaches &amp; leaders
              </h2>
              <p className="mt-2 leading-relaxed text-pnp-navy/80">
                A year-one rollout and coaching plan for turning this framework
                from a website into changed instruction — the starter sequence,
                the coaching cycle, and a 30/60/90 arc.
              </p>
            </div>
            <Button href="/math/approach/rollout" tier="primary">
              Coaching &amp; implementation plan
            </Button>
          </div>
        </Container>
      </section>
    </>
  );
}

const LESSON_COMPONENTS = [
  {
    title: "Opener / Warm-up",
    body: "One flexible slot you fill by purpose — about 10–15 minutes of reasoning and discourse. Whatever goes here is discourse-rich, not a silent worksheet.",
    items: ["Number Talks & strings", "Same But Different / WODB", "Quick Images, estimation"],
  },
  {
    title: "Core instruction",
    body: "Built around rich tasks / three-act math — students reason and struggle through a goal-focused task, then the teacher consolidates to formalize the math. Direct instruction lives here too, timed to land when students are ready.",
    items: ["Rich Tasks / Three-Act Math", "Thin-Slicing", "Responsive direct instruction"],
  },
  {
    title: "Practice & closure",
    body: "Where students build fluency and we find out if it landed — monitored fluency practice, spaced review, and a short close that surfaces evidence of thinking.",
    items: ["Fluency practice (monitored)", "Check-for-understanding", "Exit tickets & spaced review"],
  },
];
