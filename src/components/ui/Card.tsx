import Link from "next/link";
import React from "react";

/**
 * Card — the shared content-card envelope (strategies, tasks, units, hub
 * tiles). The bold & playful vocabulary from the homepage: white surface,
 * 2px navy border, hard offset shadow (no blur). When given an `href` it
 * renders as a Link that lifts up-left and deepens its shadow on hover,
 * with a visible accent focus ring.
 *
 * `accent` (a brand-token hex from BRAND_CYCLE) paints a thin top stripe
 * for per-item color coding without tinting the whole border. Padding is
 * left to the caller so each card type controls its own internals.
 *
 * Distinct from Tile, which keeps its fixed homepage jump-in layout.
 */
type Props = {
  href?: string;
  /** Brand-token hex for the top stripe (omit for no stripe). */
  accent?: string;
  className?: string;
  children: React.ReactNode;
};

const BASE =
  "group relative block overflow-hidden rounded-xl border-2 border-pnp-navy bg-white shadow-[4px_4px_0_var(--pnp-navy)]";

const INTERACTIVE =
  "transition-[transform,box-shadow] duration-150 ease-out hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[6px_6px_0_var(--pnp-navy)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2";

export default function Card({ href, accent, className = "", children }: Props) {
  const cls = [BASE, href ? INTERACTIVE : "", className]
    .filter(Boolean)
    .join(" ");

  const stripe = accent ? (
    <span
      className="absolute inset-x-0 top-0 h-1.5"
      style={{ backgroundColor: accent }}
      aria-hidden="true"
    />
  ) : null;

  if (href) {
    return (
      <Link href={href} className={cls}>
        {stripe}
        {children}
      </Link>
    );
  }

  return (
    <div className={cls}>
      {stripe}
      {children}
    </div>
  );
}
