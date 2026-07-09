import Container from "@/components/layout/Container";
import Button from "@/components/ui/Button";

/**
 * FinalCtaSection — bold yellow closing band that bookends the hero's
 * "Plug In. Play On." Navy text on yellow is high-contrast; the primary
 * teal button and white secondary both read cleanly on the field.
 */
export default function FinalCtaSection() {
  return (
    <section className="relative overflow-hidden bg-pnp-yellow py-16 md:py-20">
      <div
        className="pnp-drift absolute -right-6 -top-6 h-28 w-28 rounded-full bg-pnp-orange/30"
        aria-hidden="true"
      />
      <div
        className="pnp-sway absolute bottom-4 left-[8%] h-10 w-10 bg-pnp-teal/40"
        aria-hidden="true"
      />
      <div
        className="pnp-bob-slow absolute left-[22%] top-8 h-8 w-8 rounded-full bg-pnp-navy/10"
        aria-hidden="true"
      />
      <div
        className="pnp-sway absolute right-[12%] bottom-8 h-9 w-9 bg-pnp-navy/10"
        style={{ animationDelay: "1s" }}
        aria-hidden="true"
      />
      <div
        className="pnp-drift absolute right-[30%] top-6 h-5 w-5 rounded-full bg-pnp-orange/40"
        style={{ animationDelay: "1.6s" }}
        aria-hidden="true"
      />

      <Container className="relative text-center">
        <h2 className="font-heading text-4xl font-extrabold leading-tight text-pnp-navy md:text-5xl">
          Plug in. Play on.
        </h2>
        <p className="mx-auto mt-4 max-w-md text-lg leading-relaxed text-pnp-navy/80">
          Free for teachers — no sign-in required to browse, generate, or
          project.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Button href="/math/units" tier="primary">
            Browse math units
          </Button>
          <Button href="/math/generator" tier="secondary">
            Make exit tickets
          </Button>
        </div>
      </Container>
    </section>
  );
}
