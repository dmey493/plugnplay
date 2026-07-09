import type { Metadata } from "next";
import Container from "@/components/layout/Container";
import ClassesList from "@/components/classes/ClassesList";

export const metadata: Metadata = {
  title: "Classes | Plug N Play",
  description:
    "Save your class rosters locally so you can randomize groups, take attendance, and run the room without retyping names every period.",
};

export default function ClassesPage() {
  return (
    <>
      {/* Navy banner matches the math hub / library banner pattern so
          the chrome reads as a peer surface, not a detail page. */}
      <section className="bg-pnp-navy py-10 md:py-12">
        <Container>
          <h1
            className="font-heading font-extrabold uppercase tracking-wide text-white"
            style={{ fontSize: "clamp(1.75rem, 3.5vw, 2.5rem)" }}
          >
            Classes
          </h1>
          <p className="mt-2 max-w-2xl text-white/80">
            Save a roster once, reuse it everywhere. Classes are stored in this browser only until accounts ship.
          </p>
        </Container>
      </section>

      <section className="bg-pnp-gray-50 py-8 md:py-10">
        <Container>
          <ClassesList />
        </Container>
      </section>
    </>
  );
}
