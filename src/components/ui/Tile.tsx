import Link from "next/link";
import React from "react";
import { ArrowRightIcon } from "./icons";

/**
 * Tile — the "jump-in" card used on the homepage playground board.
 *
 * Bold & playful: thick navy border + hard offset shadow (no blur), a
 * colored icon chip, an Epilogue label and a muted blurb.
 *
 * Two states:
 *   - "live" → renders as a <Link>. Hover lifts the card up-left and
 *     deepens the offset shadow; a trailing arrow fades in. Keyboard
 *     focusable with a visible accent focus ring.
 *   - "soon" → non-interactive <div>: dashed border, muted surface, a
 *     small "Soon" chip. Not a link, so nothing 404s mid-build.
 *
 * The icon chip's background is data-driven (`accent`) so it's set
 * inline; everything else uses design-system tokens. This is a
 * navigational card, not a Button — buttons still route through Button.
 */

type Props = {
  href: string;
  label: string;
  blurb: string;
  icon: React.ReactNode;
  /** Icon-chip background (brand hex from JUMP_IN config). */
  accent: string;
  /** Icon color on the chip; defaults to white. */
  accentText?: string;
  status?: "live" | "soon";
};

export default function Tile({
  href,
  label,
  blurb,
  icon,
  accent,
  accentText = "#ffffff",
  status = "live",
}: Props) {
  const soon = status === "soon";

  const body = (
    <>
      <span
        className="inline-flex h-11 w-11 items-center justify-center rounded-xl"
        style={{ backgroundColor: accent, color: accentText }}
        aria-hidden="true"
      >
        {icon}
      </span>
      <span className="mt-3 flex items-center gap-2">
        <span className="font-heading text-lg font-extrabold leading-none text-pnp-navy">
          {label}
        </span>
        {soon && (
          <span className="rounded-md bg-pnp-gray-100 px-1.5 py-0.5 text-[11px] font-bold uppercase tracking-wide text-pnp-gray-600">
            Soon
          </span>
        )}
      </span>
      <span className="mt-1 block text-sm text-pnp-gray-600">{blurb}</span>
    </>
  );

  if (soon) {
    return (
      <div
        aria-disabled="true"
        className="relative rounded-xl border-2 border-dashed border-pnp-gray-300 bg-pnp-gray-50 p-4"
      >
        {body}
      </div>
    );
  }

  return (
    <Link
      href={href}
      className="group relative block rounded-xl border-2 border-pnp-navy bg-white p-4 shadow-[4px_4px_0_var(--pnp-navy)] transition-[transform,box-shadow] duration-150 ease-out hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[6px_6px_0_var(--pnp-navy)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2"
    >
      {body}
      <ArrowRightIcon
        size={18}
        className="absolute right-3 top-4 text-pnp-navy opacity-0 transition-opacity group-hover:opacity-100"
      />
    </Link>
  );
}
