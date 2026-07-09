import { notFound } from "next/navigation";
import Link from "next/link";
import type { Metadata } from "next";
import { getAllTasks, getTaskById } from "@/lib/tasks";
import type { TaskBody, TaskType } from "@/lib/types";
import Container from "@/components/layout/Container";
import TaskActionBar from "@/components/tasks/TaskActionBar";
import TaskImageView from "@/components/tasks/TaskImageView";
import StandardsBadges from "@/components/tasks/StandardsBadges";
import MarkdownText from "@/components/tasks/MarkdownText";
import Badge, { type BadgeTone } from "@/components/ui/Badge";
import Tag from "@/components/ui/Tag";

const TASK_TYPE_LABELS: Record<TaskType, string> = {
  anchor: "Anchor Task",
  investigation: "Investigation",
  "three-act": "Three-Act",
  warmup: "Warm-Up",
  performance: "Performance",
  "problem-set": "Problem Set",
};

// Task type → muted Badge tone. NO purple — three-act used to be purple
// and is now orange per the design system spec.
const TASK_TYPE_TONES: Record<TaskType, BadgeTone> = {
  anchor: "emerald",
  investigation: "blue",
  "three-act": "orange",
  warmup: "yellow",
  performance: "red",
  "problem-set": "neutral",
};

export async function generateStaticParams() {
  const tasks = await getAllTasks();
  return tasks.map((t) => ({ id: t.id }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const task = await getTaskById(id);
  if (!task) return { title: "Task Not Found | Plug N Play" };
  return {
    title: `${task.title} | Lesson Activities | Plug N Play`,
    description: task.preview,
  };
}

const ANCHOR_LINKS = [
  { id: "launch", label: "Launch" },
  { id: "the-task", label: "The Task" },
  { id: "approaches", label: "Approaches" },
  { id: "misconceptions", label: "Misconceptions" },
  { id: "discussion", label: "Discussion" },
  { id: "solutions", label: "Solutions" },
  { id: "extensions", label: "Extensions" },
];

export default async function TaskDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const task = await getTaskById(id);
  if (!task) notFound();

  const body = task.body as TaskBody;
  const typeTone = TASK_TYPE_TONES[body.taskType] ?? "neutral";
  const typeLabel = TASK_TYPE_LABELS[body.taskType] ?? body.taskType;

  return (
    <>
      {/* Banner */}
      <section className="no-print bg-pnp-navy py-6 md:py-8">
        <Container>
          <Link
            href="/math/rich-tasks"
            className="mb-2 inline-flex items-center gap-2 text-sm font-semibold text-white/70 transition-colors hover:text-white"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 12H5M12 19l-7-7 7-7" />
            </svg>
            Back to Lesson Activities
          </Link>
          <div className="flex flex-wrap items-start justify-between gap-3">
            <h1
              className="font-heading font-extrabold text-white"
              style={{ fontSize: "clamp(1.5rem, 3vw, 2.25rem)" }}
            >
              {task.title}
            </h1>
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone={typeTone}>{typeLabel}</Badge>
              <StandardsBadges task={task} />
              {/* Time pill — on a dark banner so we override colours to
                  white/transparent rather than using the muted Tag tone. */}
              <span className="inline-flex select-none items-center rounded-md border border-white/30 bg-white/10 px-2 py-0.5 text-xs font-semibold text-white/90">
                {task.time.minMinutes}-{task.time.maxMinutes} min
              </span>
            </div>
          </div>
        </Container>
      </section>

      {/* Body */}
      <section className="bg-white py-6 md:py-10">
        <Container>
          <TaskActionBar taskId={task.id} />

          {/* Anchor jump links. Tertiary-button styling: no fill, no
              border, accent-coloured text on hover. Looks like links
              (because they ARE jump links) but with the consistent
              hover/focus treatment of the rest of the system. */}
          <nav className="no-print mb-8 flex flex-wrap gap-1 rounded-lg border border-pnp-gray-200 bg-pnp-gray-50 p-2 text-xs">
            {ANCHOR_LINKS.map((a) => (
              <a
                key={a.id}
                href={`#${a.id}`}
                className="rounded-md px-3 py-1.5 text-xs font-semibold text-pnp-gray-700 transition-colors hover:bg-pnp-accent-soft hover:text-pnp-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2"
              >
                {a.label}
              </a>
            ))}
          </nav>

          <article className="task-article mx-auto max-w-4xl space-y-10 text-lg leading-relaxed">

            {/* GOAL, MATERIALS, BTC FIT — intentionally not rendered. The
                fields remain in the schema so authoring isn't disrupted,
                but they're noise on the detail page (goal paraphrases the
                prompt; btcFit is meta-commentary; materials are usually a
                single short list that doesn't earn its own h2). */}

            {/* LAUNCH — teacher only. Rendered via MarkdownText so any
                tables / bullets / bold in the JSON show up properly
                instead of as a wall of raw `|` characters. */}
            {body.launch && (
              <section id="launch" data-print-section="teacher">
                <SectionHeader>Launch</SectionHeader>
                <div className="space-y-3 text-lg text-pnp-gray-700">
                  <MarkdownText text={body.launch} />
                </div>
              </section>
            )}

            {/* THE TASK — student handout */}
            <section id="the-task" data-print-section="both">
              <SectionHeader>The Task</SectionHeader>
              <div className="rounded-xl border-2 border-pnp-navy bg-pnp-yellow/10 p-8 text-pnp-gray-900">
                {body.image && (
                  <div className="mb-6">
                    <TaskImageView image={body.image} size="detail" />
                  </div>
                )}
                <div className="space-y-3 text-xl leading-relaxed md:text-2xl">
                  <MarkdownText text={body.studentPrompt} />
                </div>
              </div>
            </section>

            {/* APPROACHES — teacher only */}
            {body.anticipatedApproaches && (
              <section id="approaches" data-print-section="teacher">
                <SectionHeader>Approaches</SectionHeader>
                <div className="space-y-3 text-lg text-pnp-gray-700">
                  <MarkdownText text={body.anticipatedApproaches} />
                </div>
              </section>
            )}

            {/* MISCONCEPTIONS — teacher only */}
            {body.commonMisconceptions && (
              <section id="misconceptions" data-print-section="teacher">
                <SectionHeader>Common Misconceptions</SectionHeader>
                <div className="space-y-3 text-lg text-pnp-gray-700">
                  <MarkdownText text={body.commonMisconceptions} />
                </div>
              </section>
            )}

            {/* DISCUSSION — teacher only */}
            {body.discussionQuestions && (
              <section id="discussion" data-print-section="teacher">
                <SectionHeader>Discussion Questions</SectionHeader>
                <div className="space-y-3 text-lg text-pnp-gray-700">
                  <MarkdownText text={body.discussionQuestions} />
                </div>
              </section>
            )}

            {/* SOLUTIONS — teacher only */}
            {body.sampleSolutions && (
              <section id="solutions" data-print-section="teacher">
                <SectionHeader>Sample Solutions</SectionHeader>
                <div className="space-y-3 text-lg text-pnp-gray-700">
                  <MarkdownText text={body.sampleSolutions} />
                </div>
              </section>
            )}

            {/* EXTENSIONS — teacher only */}
            {body.extensions && (
              <section id="extensions" data-print-section="teacher">
                <SectionHeader>Extensions</SectionHeader>
                <div className="space-y-3 text-lg text-pnp-gray-700">
                  <MarkdownText text={body.extensions} />
                </div>
              </section>
            )}

            {/* CONCEPTS chip cloud and SOURCE/LICENSE h3 — removed from
                the detail page. Source data is still on the JSON for
                attribution provenance; we just don't render an h3 for it
                since it's pedagogically irrelevant on this page. */}

          </article>
        </Container>
      </section>
    </>
  );
}

function SectionHeader({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="mb-4 font-heading text-2xl font-bold text-pnp-navy md:text-3xl">
      {children}
    </h2>
  );
}
