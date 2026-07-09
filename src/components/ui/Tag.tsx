import React from "react";

/**
 * Tag — small, muted, NON-interactive metadata label.
 *
 * Tags are NOT buttons. They display facts: a topic ("ratios"), a
 * standard code ("7.NS.1"), a duration label ("25 min"). The visual is
 * deliberately quieter than any Button tier so users don't expect a tap
 * to do something.
 *
 *   - Small text (xs)
 *   - Muted neutral background (gray-100), neutral text (gray-700)
 *   - Rounded-md, NOT pill (full-pill is reserved for Buttons/Badges)
 *   - No hover state, no cursor change
 *
 * Variants:
 *   - "default" : gray-100 bg, gray-700 text
 *   - "code"    : same as default but uses tabular mono font, for
 *                 standard codes like "7.NS.1"
 */

type Variant = "default" | "code";

interface Props {
  variant?: Variant;
  children: React.ReactNode;
  className?: string;
  /** Optional title attribute for hover tooltip context (e.g. expanding
   *  a standard code into its description). */
  title?: string;
}

const VARIANT: Record<Variant, string> = {
  default:
    "bg-pnp-gray-100 text-pnp-navy",
  // Codes use the same surface but force tabular numerals so digits
  // line up. The mono face also subtly signals "system identifier".
  code:
    "bg-pnp-gray-100 text-pnp-navy font-mono tabular-nums",
};

export default function Tag({
  variant = "default",
  children,
  className = "",
  title,
}: Props) {
  return (
    <span
      title={title}
      className={`inline-flex select-none items-center rounded-md border-2 border-pnp-navy px-2 py-0.5 text-xs font-semibold shadow-[2px_2px_0_var(--pnp-navy)] ${VARIANT[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
