import type { Metadata } from "next";
import { getAllStrategies } from "@/lib/content";
import Container from "@/components/layout/Container";
import PageBanner from "@/components/ui/PageBanner";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { ArrowRightIcon } from "@/components/ui/icons";
import StrategyLibrary from "@/components/library/StrategyLibrary";

export const metadata: Metadata = {
  title: "Math | Plug N Play",
  description:
    "Math tools and strategies for grades 6-8: problem generator, skill intervention, fluency practice, and teaching strategies.",
};

// `hidden: true` parks an entry without deleting it. Colors are brand
// tokens only (no off-palette hex).
type TileEntry = {
  title: string;
  description: string;
  href: string;
  color: string;
  icon: React.ReactNode;
  hidden?: boolean;
};

const RESOURCES: TileEntry[] = [
  {
    title: "Lesson activities",
    description:
      "Rich tasks and thin slices for thinking classrooms. Browse by unit, standard, or concept; project on screen; print in one click.",
    href: "/math/units",
    color: "#0d9488",
    icon: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2 2 7l10 5 10-5-10-5z" />
        <path d="m2 17 10 5 10-5" />
        <path d="m2 12 10 5 10-5" />
      </svg>
    ),
  },
  {
    title: "Problem generator",
    description:
      "Standards-aligned exit tickets, tiered Mild/Medium/Spicy sets, and proficiency checks. Review and swap each question before printing.",
    href: "/math/generator",
    color: "#3f42d9",
    icon: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="4" y="2" width="16" height="20" rx="2" />
        <line x1="8" y1="6" x2="16" y2="6" />
        <line x1="8" y1="10" x2="16" y2="10" />
        <line x1="8" y1="14" x2="12" y2="14" />
      </svg>
    ),
  },
  {
    title: "Fluency practice",
    description:
      "Printable fluency worksheets across every core 6–8 skill — integers, fractions, percent, equations, geometry, and more. Pick a skill, print in one click.",
    href: "/math/fluency",
    color: "#22c55e",
    icon: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" />
        <polyline points="12 6 12 12 16 14" />
      </svg>
    ),
  },
  {
    title: "Skill intervention",
    description:
      "Tier 2 intervention built as a learning progression per standard — practice, activities, teacher moves, diagnostics, and printable packets.",
    href: "/math/intervention",
    color: "#f97316",
    icon: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 20h9" />
        <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z" />
      </svg>
    ),
  },
];

const ROUTINES: TileEntry[] = [
  {
    title: "Which One Doesn't Belong?",
    description:
      "A 5–10 minute thinking routine. Show four boxes, ask which one doesn't belong — every box can be argued. Filter by strand or concept, project full-screen, reveal teacher notes.",
    href: "/math/wodb",
    color: "#0d9488",
    icon: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="7" height="7" rx="1" />
        <rect x="14" y="3" width="7" height="7" rx="1" />
        <rect x="3" y="14" width="7" height="7" rx="1" />
        <path d="M14 17.5a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z" />
      </svg>
    ),
  },
  {
    title: "Number Talks",
    description:
      "Short mental-math warm-ups. Show a problem, ask “how did you solve it in your head?”, compare strategies. Problems reveal one at a time, with target strategies, talk moves, and an answer key.",
    href: "/math/number-talks",
    color: "#ea580c",
    icon: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        <path d="M8 9h8M8 13h5" />
      </svg>
    ),
  },
];

const TOOLS: TileEntry[] = [
  {
    title: "Whiteboard",
    description:
      "Full-screen digital whiteboard. Draw, sketch, or work through problems with pen, highlighter, and eraser — projector-ready.",
    href: "/math/tools/whiteboard",
    color: "#1a1f3d",
    icon: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="18" height="14" rx="2" />
        <path d="M8 21h8" />
        <path d="M12 17v4" />
        <path d="m7 9 3 3 7-7" />
      </svg>
    ),
  },
  {
    title: "Flash cards",
    description:
      "Voice-powered fact practice. Speak the answer and the app checks it instantly — set the operation, range, and pace.",
    href: "/math/tools/flash-cards",
    color: "#f97316",
    icon: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="6" width="14" height="14" rx="2" />
        <path d="M7 4h14a2 2 0 0 1 2 2v14" />
        <path d="M9 13h5" />
      </svg>
    ),
  },
];

export default async function MathPage() {
  const allStrategies = await getAllStrategies();
  const mathStrategies = allStrategies.filter((s) =>
    s.subjects.includes("math")
  );

  return (
    <>
      <PageBanner
        title="Math"
        subtitle="Indiana Math Standards · Grades 6–8"
      />

      {/* Flagship: the pedagogical framework behind the tools */}
      <section className="bg-white py-10 md:py-14">
        <Container>
          <Card accent="#0d9488">
            <div className="flex flex-col gap-6 p-6 md:flex-row md:items-center md:gap-10 md:p-8">
              <div className="flex-1">
                <p className="text-xs font-bold uppercase tracking-widest text-pnp-accent">
                  Start here
                </p>
                <h2 className="mt-2 font-heading text-2xl font-extrabold text-pnp-navy md:text-3xl">
                  Our teaching approach
                </h2>
                <p className="mt-3 max-w-2xl leading-relaxed text-pnp-gray-600">
                  The framework behind the tools — a shared vision for grades
                  6–8 mathematics, the two frameworks that ground it, how a
                  lesson is built, and a toolbelt of classroom routines each
                  paired with a lesson-design connection.
                </p>
                <div className="mt-5 flex flex-wrap gap-2">
                  {[
                    "Vision & frameworks",
                    "Lesson design",
                    "18 tools",
                    "5 strands · 8 practices",
                  ].map((chip) => (
                    <span
                      key={chip}
                      className="inline-flex items-center rounded-md border-2 border-pnp-navy bg-pnp-gray-50 px-2.5 py-1 text-xs font-semibold text-pnp-navy shadow-[2px_2px_0_var(--pnp-navy)]"
                    >
                      {chip}
                    </span>
                  ))}
                </div>
              </div>
              <div className="shrink-0">
                <Button href="/math/approach" tier="primary">
                  Explore the approach
                </Button>
              </div>
            </div>
          </Card>
        </Container>
      </section>

      <section className="bg-pnp-gray-50 py-10 md:py-14">
        <Container>
          <h2 className="mb-8 font-heading text-2xl font-extrabold text-pnp-navy md:text-3xl">
            Plan a lesson
          </h2>
          <TileGrid tiles={RESOURCES.filter((t) => !t.hidden)} />
        </Container>
      </section>

      <section className="bg-white py-10 md:py-14">
        <Container>
          <h2 className="mb-8 font-heading text-2xl font-extrabold text-pnp-navy md:text-3xl">
            Warm-ups &amp; routines
          </h2>
          <TileGrid tiles={ROUTINES.filter((t) => !t.hidden)} />
        </Container>
      </section>

      <section className="bg-pnp-gray-50 py-10 md:py-14">
        <Container>
          <h2 className="mb-8 font-heading text-2xl font-extrabold text-pnp-navy md:text-3xl">
            Classroom tools
          </h2>
          <TileGrid tiles={TOOLS.filter((t) => !t.hidden)} />
        </Container>
      </section>

      <section className="bg-white py-10 md:py-14">
        <Container>
          <h2 className="mb-8 font-heading text-2xl font-extrabold text-pnp-navy md:text-3xl">
            Teaching strategies
          </h2>
          <StrategyLibrary strategies={mathStrategies} />
        </Container>
      </section>
    </>
  );
}

// Cap grid columns at the tile count so a short row fills edge-to-edge
// instead of leaving white space. Class strings are literal for the JIT.
function TileGrid({ tiles }: { tiles: TileEntry[] }) {
  const colCap: Record<number, string> = {
    1: "lg:grid-cols-1",
    2: "lg:grid-cols-2",
    3: "lg:grid-cols-3",
    4: "lg:grid-cols-4",
  };
  const lgCols = colCap[Math.min(Math.max(tiles.length, 1), 4)] ?? "lg:grid-cols-3";

  return (
    <div className={`grid gap-6 sm:grid-cols-2 ${lgCols}`}>
      {tiles.map((tile) => (
        <Card key={tile.title} href={tile.href} accent={tile.color} className="h-full">
          <div className="flex h-full flex-col p-6">
            <span
              className="mb-4 flex h-14 w-14 items-center justify-center rounded-xl text-white"
              style={{ backgroundColor: tile.color }}
              aria-hidden="true"
            >
              {tile.icon}
            </span>
            <h3 className="font-heading text-xl font-extrabold text-pnp-navy">
              {tile.title}
            </h3>
            <p className="mt-2 flex-1 text-sm leading-relaxed text-pnp-gray-600">
              {tile.description}
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
  );
}
