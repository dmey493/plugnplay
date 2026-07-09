import type { Metadata } from "next";
import Container from "@/components/layout/Container";
import PageBanner from "@/components/ui/PageBanner";
import Card from "@/components/ui/Card";
import { ArrowRightIcon } from "@/components/ui/icons";
import { stimulusCount } from "@/lib/science";
import { graphCount } from "@/lib/gotw";

export const metadata: Metadata = {
  title: "Science | Plug N Play",
  description:
    "Science tools for grades 6-12: a Graph of the Week analysis routine (MS-PS/LS/ESS/ETS) and an ILEARN biology stimulus generator — ready to print.",
};

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
    title: "Graph of the Week",
    description: `A weekly graph-analysis routine for grades 6-8. Pick a grade and standard, then a phenomenon graph — students read the data, make a first look, then write a claim with evidence and reasoning. ${graphCount()} graphs, print-ready front and back.`,
    href: "/science/graph-of-the-week",
    color: "#22c55e",
    icon: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 3v18h18" />
        <path d="m19 9-5 5-4-4-3 3" />
      </svg>
    ),
  },
  {
    title: "Stimulus generator",
    description: `Pick a biology (HS-LS) standard and one of its phenomenon stimuli — ILEARN End-of-Course style, with a chart or data table and auto-scorable items. ${stimulusCount()} in all, ready to print.`,
    href: "/science/generator",
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
];

export default function SciencePage() {
  return (
    <>
      <PageBanner
        title="Science"
        subtitle="Indiana Science Standards · Grades 6–12"
      />

      <section className="bg-pnp-gray-50 py-10 md:py-14">
        <Container>
          <h2 className="mb-8 font-heading text-2xl font-extrabold text-pnp-navy md:text-3xl">
            Warm-ups &amp; generators
          </h2>
          <TileGrid tiles={RESOURCES.filter((t) => !t.hidden)} />
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
  const lgCols =
    colCap[Math.min(Math.max(tiles.length, 1), 4)] ?? "lg:grid-cols-3";

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
