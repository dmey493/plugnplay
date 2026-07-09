import Container from "@/components/layout/Container";

/**
 * HowItWorksSection — three plain steps that turn the playful promise
 * into a concrete workflow. Cards reuse the bold border + hard-shadow
 * vocabulary from the hero tiles for consistency. Number-chip text color
 * is set per step so it stays AA on light chips (navy on yellow).
 */
const STEPS = [
  {
    n: 1,
    color: "#0d9488",
    numText: "#ffffff",
    title: "Pick a unit or task",
    blurb:
      "Browse by unit or standard, or generate exit tickets from 10,000+ standards-aligned questions.",
  },
  {
    n: 2,
    color: "#3f42d9",
    numText: "#ffffff",
    title: "Project or print",
    blurb:
      "Send it to the board in one tap, or print clean, student-ready exit tickets.",
  },
  {
    n: 3,
    color: "#ffe25a",
    numText: "#1a1f3d",
    title: "Teach",
    blurb:
      "Built-in prompts, timers, and answer keys keep the whole lesson moving.",
  },
];

export default function HowItWorksSection() {
  return (
    <section className="relative overflow-hidden bg-white py-16 md:py-24">
      {/* Ambient drifting shapes behind the steps. */}
      <div className="pointer-events-none absolute inset-0" aria-hidden="true">
        <div className="pnp-bob-slow absolute right-[6%] top-10 h-16 w-16 rounded-full bg-pnp-teal/10" />
        <div className="pnp-sway absolute left-[4%] bottom-12 h-10 w-10 bg-pnp-yellow/20" />
        <div className="pnp-drift absolute right-[16%] bottom-10 h-6 w-6 rounded-full bg-pnp-orange/20" style={{ animationDelay: "1s" }} />
        <div className="pnp-spin-slow absolute left-[44%] top-8 h-8 w-8 bg-pnp-blue/10" />
      </div>

      <Container className="relative">
        <div className="max-w-2xl">
          <h2 className="font-heading text-3xl font-extrabold leading-tight text-pnp-navy md:text-4xl">
            From “what do I teach?” to teaching — in three steps.
          </h2>
        </div>

        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {STEPS.map((s) => (
            <div
              key={s.n}
              className="rounded-2xl border-2 border-pnp-navy bg-white p-6 shadow-[4px_4px_0_var(--pnp-navy)]"
            >
              <span
                className="flex h-12 w-12 items-center justify-center rounded-full font-heading text-xl font-extrabold"
                style={{ backgroundColor: s.color, color: s.numText }}
                aria-hidden="true"
              >
                {s.n}
              </span>
              <h3 className="mt-4 font-heading text-xl font-extrabold text-pnp-navy">
                {s.title}
              </h3>
              <p className="mt-2 text-base leading-relaxed text-pnp-gray-600">
                {s.blurb}
              </p>
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
}
