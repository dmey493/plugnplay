import Container from "@/components/layout/Container";

/**
 * ProofSection — trust band on navy. Bright brand colors carry the stat
 * numbers (high contrast on the dark field); labels use white/70, which
 * stays well above AA on navy. No color is the sole carrier of meaning —
 * each number is paired with a text label.
 */
const STATS = [
  { value: "10,000+", color: "#ffe25a", label: "Standards-aligned questions" },
  { value: "6–8", color: "#2dd4bf", label: "Indiana-aligned grade bands" },
  { value: "1–3", color: "#f97316", label: "MTSS tiers supported" },
  { value: "Free", color: "#60a5fa", label: "No sign-in to use" },
];

export default function ProofSection() {
  return (
    <section className="relative overflow-hidden bg-pnp-navy py-16 md:py-24">
      {/* Bright shapes drift across the navy field, behind the stats. */}
      <div className="pointer-events-none absolute inset-0" aria-hidden="true">
        <div className="pnp-drift absolute right-[8%] top-10 h-16 w-16 rounded-full bg-pnp-teal/15" />
        <div className="pnp-sway absolute left-[5%] top-12 h-10 w-10 bg-pnp-yellow/15" />
        <div className="pnp-bob absolute right-[24%] bottom-10 h-6 w-6 rounded-full bg-pnp-orange/25" style={{ animationDelay: "0.8s" }} />
        <div className="pnp-spin-slow absolute left-[38%] bottom-8 h-8 w-8 bg-pnp-blue/25" />
      </div>

      <Container className="relative">
        <div className="max-w-2xl">
          <h2 className="font-heading text-3xl font-extrabold leading-tight text-white md:text-4xl">
            Made by middle-school teachers, aligned to your standards.
          </h2>
          <p className="mt-4 text-lg leading-relaxed text-white/80">
            Everything maps to Indiana Academic Standards and MTSS tiers — so
            what you project today is what you’re accountable for.
          </p>
        </div>

        <div className="mt-12 grid grid-cols-2 gap-8 md:grid-cols-4">
          {STATS.map((s) => (
            <div key={s.label}>
              <div
                className="font-heading text-4xl font-extrabold md:text-5xl"
                style={{ color: s.color }}
              >
                {s.value}
              </div>
              <div className="mt-2 text-sm leading-relaxed text-white/70">
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
}
