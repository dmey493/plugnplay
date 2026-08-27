import Container from "@/components/layout/Container";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";
import Tag from "@/components/ui/Tag";
import { getTaskById } from "@/lib/library/tasks";

/**
 * ProductPeekSection — "show, don't tell" (redesign direction B).
 *
 * Server Component that loads a real featured task and renders a faithful
 * mini TaskCard on a saturated field, so a first-time visitor sees what
 * they actually get. Falls back to hardcoded "Better Buy" copy if the
 * featured id is ever missing, so the homepage never breaks on content
 * changes. The card mirrors the real TaskCard vocabulary: a format Badge
 * ("Rich Task", blue) — NOT the internal task type — plus a standard
 * code Tag and Project/Print actions.
 */

const FEATURED_ID = "task-math-005";

export default async function ProductPeekSection() {
  const task = await getTaskById(FEATURED_ID);

  const id = task?.id ?? FEATURED_ID;
  const title = task?.title ?? "Better Buy";
  const standard = task?.standards.indiana[0] ?? "7.RP.2";
  const excerpt =
    task?.preview ??
    "Compare two products by unit rate — then wrestle with what “better” even means.";
  const grades = task?.grades ?? [7];
  const minM = task?.time.minMinutes;
  const maxM = task?.time.maxMinutes;
  const duration = minM && maxM ? `${minM}–${maxM} min` : "15–35 min";
  const gradeLabel = grades.map((g) => `${g}th`).join(", ");

  const projectHref = `/math/rich-tasks/${id}/project`;
  const openHref = `/math/rich-tasks/${id}`;

  return (
    <section className="relative overflow-hidden bg-pnp-blue py-16 md:py-24">
      <svg
        className="pointer-events-none absolute left-6 top-8 h-24 w-24 opacity-20"
        viewBox="0 0 80 80"
        fill="none"
        aria-hidden="true"
      >
        <defs>
          <pattern
            id="ppdots"
            width="14"
            height="14"
            patternUnits="userSpaceOnUse"
          >
            <circle cx="2" cy="2" r="2" fill="white" />
          </pattern>
        </defs>
        <rect width="80" height="80" fill="url(#ppdots)" />
      </svg>

      {/* Floating shapes — drift over the blue field, behind the content. */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
        <div className="pnp-drift absolute right-[8%] top-10 h-14 w-14 rounded-full bg-pnp-teal/25" />
        <div className="pnp-sway absolute left-[6%] bottom-10 h-10 w-10 bg-pnp-yellow/25" />
        <div className="pnp-bob-slow absolute right-[22%] bottom-8 h-6 w-6 rounded-full bg-white/15" style={{ animationDelay: "1.2s" }} />
        <div className="pnp-spin-slow absolute left-[42%] top-6 h-8 w-8 bg-pnp-orange/20" />
      </div>

      <Container className="relative">
        <div className="grid items-center gap-12 md:grid-cols-2">
          {/* Copy */}
          <div className="text-white">
            <h2 className="font-heading text-4xl font-extrabold leading-tight md:text-5xl">
              Open a task.
              <br className="hidden sm:block" /> Project it. Teach.
            </h2>
            <p className="mt-5 max-w-md text-lg leading-relaxed text-white/90">
              Every rich task opens clean and classroom-ready. Project it to the
              board in one tap, or print it for students — no reformatting, no
              prep.
            </p>
            <div className="mt-7">
              <Button href="/math/rich-tasks" tier="primary">
                Browse the task library
              </Button>
            </div>
          </div>

          {/* Real task card */}
          <div className="relative flex justify-center md:justify-end">
            <div
              className="pnp-bob absolute -left-1 top-0 h-10 w-10 rounded-full bg-pnp-yellow"
              aria-hidden="true"
            />
            <div
              className="pnp-sway absolute -right-1 bottom-6 h-9 w-9 bg-pnp-orange"
              aria-hidden="true"
            />
            <div className="relative -rotate-2">
              <div
                className="absolute inset-0 translate-x-3 translate-y-3 rounded-2xl bg-pnp-teal"
                aria-hidden="true"
              />
              <div className="relative w-[320px] max-w-full rounded-2xl border-2 border-pnp-navy bg-white p-5">
                <div className="flex items-center justify-between">
                  <Badge tone="blue">Rich Task</Badge>
                  <Tag variant="code">{standard}</Tag>
                </div>
                <h3 className="mt-3 font-heading text-2xl font-extrabold leading-tight text-pnp-navy">
                  {title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-pnp-gray-600">
                  {excerpt}
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  <Tag>{gradeLabel}</Tag>
                  <Tag>{duration}</Tag>
                </div>
                <div className="mt-4 flex gap-2 border-t border-pnp-gray-200 pt-4">
                  <Button href={projectHref} tier="primary" size="small">
                    Project
                  </Button>
                  <Button href={openHref} tier="secondary" size="small">
                    Print
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Container>
    </section>
  );
}
