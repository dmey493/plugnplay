import React from "react";

/**
 * Badge — small categorical label that uses a tinted surface to convey
 * its category (e.g. task type: "Anchor", "Investigation", "Performance").
 *
 * Distinct from Tag (which is neutral/gray) and from Button (which is
 * tappable). Badges are NOT interactive — same shape and size as Tag but
 * coloured to communicate type at a glance. The colour is muted so the
 * badge doesn't look like a primary call-to-action.
 *
 * Approach: each `tone` maps to a low-saturation surface + matching dark
 * text. Surfaces use the brand colours at ~12% tint so multiple badges
 * in a row don't pull the eye away from real CTAs.
 *
 *   IMPORTANT: no purple/indigo tone — that was removed per the design
 *   spec. Anything that used to be purple should now be "neutral".
 */

export type BadgeTone =
  | "neutral"
  | "blue"
  | "teal"
  | "emerald"
  | "orange"
  | "yellow"
  | "red";

interface Props {
  tone?: BadgeTone;
  children: React.ReactNode;
  className?: string;
}

const TONES: Record<BadgeTone, string> = {
  // Muted neutrals first — falls back here whenever a previous purple
  // tone was in use.
  neutral: "bg-pnp-gray-100 text-pnp-gray-700",
  blue:    "bg-pnp-blue/10 text-pnp-blue",
  teal:    "bg-pnp-accent-soft text-pnp-accent",
  emerald: "bg-emerald-100 text-emerald-700",
  orange:  "bg-pnp-orange/10 text-pnp-orange",
  yellow:  "bg-pnp-yellow/30 text-pnp-navy",
  red:     "bg-pnp-red/10 text-pnp-red",
};

export default function Badge({
  tone = "neutral",
  children,
  className = "",
}: Props) {
  return (
    <span
      className={`inline-flex select-none items-center rounded-md border-2 border-pnp-navy px-2 py-0.5 text-xs font-semibold shadow-[2px_2px_0_var(--pnp-navy)] ${TONES[tone]} ${className}`}
    >
      {children}
    </span>
  );
}
