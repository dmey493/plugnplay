import Link from "next/link";
import Container from "@/components/layout/Container";
import { ArrowLeftIcon } from "./icons";

/**
 * PageBanner — the one shared header for every inner page, so the app
 * reads as a single designed product instead of per-page banners.
 *
 * Sentence case (never ALL-CAPS). No decorative eyebrow pill above the
 * title — the title carries it. Two tones:
 *   - "navy"  (default): dark band, white title, a couple of flat
 *     decorative shapes + a short accent rule. For browse/detail pages.
 *   - "light": white/gray-50 with a bottom border, navy title. For
 *     utility/form pages (generator, fluency) where a saturated marketing
 *     band would feel too heavy.
 */
type Props = {
  title: string;
  subtitle?: string;
  back?: { href: string; label: string };
  tone?: "navy" | "light";
};

export default function PageBanner({
  title,
  subtitle,
  back,
  tone = "navy",
}: Props) {
  const navy = tone === "navy";

  return (
    <section
      className={`relative overflow-hidden py-10 md:py-14 ${
        navy ? "bg-pnp-navy" : "border-b border-pnp-gray-200 bg-white"
      }`}
    >
      {navy && (
        <div className="pointer-events-none absolute inset-0" aria-hidden="true">
          <div className="absolute right-[6%] top-7 h-16 w-16 rounded-full bg-pnp-teal/15" />
          <div className="pnp-bob absolute bottom-5 right-[17%] h-9 w-9 rotate-45 bg-pnp-yellow/15" />
        </div>
      )}

      <Container className="relative">
        {back && (
          <Link
            href={back.href}
            className={`mb-3 inline-flex items-center gap-2 rounded text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 ${
              navy
                ? "text-white/70 hover:text-white"
                : "text-pnp-gray-600 hover:text-pnp-navy"
            }`}
          >
            <ArrowLeftIcon size={16} />
            {back.label}
          </Link>
        )}

        <h1
          className={`font-heading font-extrabold leading-[1.05] ${
            navy ? "text-white" : "text-pnp-navy"
          }`}
          style={{ fontSize: "clamp(1.9rem, 4vw, 3rem)" }}
        >
          {title}
        </h1>

        {subtitle && (
          <p
            className={`mt-3 max-w-2xl text-lg leading-relaxed ${
              navy ? "text-white/75" : "text-pnp-gray-600"
            }`}
          >
            {subtitle}
          </p>
        )}

        {navy && (
          <div
            className="mt-5 h-1 w-16 rounded-full bg-pnp-accent"
            aria-hidden="true"
          />
        )}
      </Container>
    </section>
  );
}
