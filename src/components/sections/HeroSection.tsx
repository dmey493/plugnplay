import Container from "@/components/layout/Container";
import Button from "@/components/ui/Button";
import Tile from "@/components/ui/Tile";
import { ICONS, ArrowRightIcon } from "@/components/ui/icons";
import { JUMP_IN } from "@/lib/core/constants";

/**
 * HeroSection — the "playground" hero (redesign direction C).
 *
 * Server Component: the content is static and present on first paint
 * (no JS typewriter gating the LCP text, unlike the previous hero).
 * Left = the promise + one primary CTA; right = the jump-in board of
 * live subject and tool Tiles. Motion is
 * one CSS-only ambient bob, neutralized by the global reduced-motion
 * guard in globals.css.
 */
export default function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-background pt-10 pb-16 md:pt-16 md:pb-24">
      {/* Flat decorative shapes — no meaning, just energy. They float and
          drift; the reduced-motion guard in globals.css stills them. */}
      <div
        className="pointer-events-none absolute inset-0 overflow-hidden"
        aria-hidden="true"
      >
        <div className="pnp-bob-slow absolute left-[4%] top-12 h-16 w-16 rounded-full bg-pnp-yellow/30" />
        <div className="pnp-sway absolute right-[7%] top-16 h-12 w-12 bg-pnp-orange/25" />
        <div className="pnp-drift absolute bottom-8 left-[12%] h-24 w-24 rounded-full bg-pnp-teal/15" />
        <div className="pnp-bob absolute right-[14%] bottom-14 h-10 w-10 rounded-full bg-pnp-blue/20" style={{ animationDelay: "0.7s" }} />
        <div className="pnp-spin-slow absolute left-[48%] top-6 h-8 w-8 bg-pnp-green/20" />
        <div className="pnp-drift absolute right-[32%] top-[38%] h-5 w-5 rounded-full bg-pnp-orange/30" style={{ animationDelay: "1.4s" }} />
        <div className="pnp-bob-slow absolute left-[28%] bottom-6 h-6 w-6 rounded-full bg-pnp-yellow/25" style={{ animationDelay: "2s" }} />
        <div className="pnp-sway absolute left-[2%] top-1/2 h-7 w-7 bg-pnp-teal/20" style={{ animationDelay: "1s" }} />
        <div className="pnp-bob absolute right-[4%] top-1/2 h-4 w-4 rounded-full bg-pnp-green/30" style={{ animationDelay: "0.3s" }} />
      </div>

      <Container className="relative">
        <div className="grid items-center gap-10 md:grid-cols-2 md:gap-12">
          {/* Left: promise + primary CTA */}
          <div>
            <h1
              className="font-heading font-extrabold leading-[0.95] text-pnp-navy"
              style={{ fontSize: "clamp(3rem, 6vw, 4.75rem)" }}
            >
              Plug In.
              <br />
              <span className="text-pnp-accent">Play On.</span>
            </h1>
            <p className="mt-5 max-w-md text-lg leading-relaxed text-pnp-gray-600">
              Plan less, teach more. Pick a subject or a tool and jump straight
              into standards-aligned tasks, exit tickets, and strategies for
              grades 6–8.
            </p>
            <div className="mt-7 flex flex-wrap items-center gap-2">
              <Button href="/math/units" tier="primary">
                Browse math units
              </Button>
              <Button
                href="/math/generator"
                tier="tertiary"
                trailingIcon={<ArrowRightIcon size={16} />}
              >
                or make exit tickets
              </Button>
            </div>
            <p className="mt-5 text-sm text-pnp-gray-500">
              Free. No sign-in to browse, generate, or project.
            </p>
          </div>

          {/* Right: the jump-in playground board */}
          <div className="grid grid-cols-2 gap-3 sm:gap-4">
            {JUMP_IN.map((t) => {
              const Icon = ICONS[t.icon];
              return (
                <Tile
                  key={t.label}
                  href={t.href}
                  label={t.label}
                  blurb={t.blurb}
                  accent={t.accent}
                  accentText={t.accentText}
                  status={t.status}
                  icon={<Icon />}
                />
              );
            })}
          </div>
        </div>
      </Container>
    </section>
  );
}
