"use client";

import Link from "next/link";
import React from "react";

/**
 * The single Button component for the Plug N Play app.
 *
 * Three tiers, as documented in the design-system spec:
 *
 *   PRIMARY    — solid teal-600 fill, white text. One per view.
 *   SECONDARY  — transparent / white background, neutral border, dark text.
 *   TERTIARY   — no fill, no border, accent-colored text. Optional small
 *                trailing icon (and only here).
 *
 * The component renders as a `<button>` by default. Pass an `href` to get
 * a Next.js `<Link>` styled identically — middle-click and right-click
 * keep working for navigational actions.
 *
 * Shape, height, and motion are fixed across all tiers so the visual
 * vocabulary is identical everywhere:
 *
 *   - Radius 8px (rounded-md). Never full-pill — that's reserved for the
 *     Tag/Badge components so users don't confuse metadata with actions.
 *   - Height 40px (small) / 44px (default). Generous horizontal padding.
 *   - Hover darkens fill ~8%. Pressed applies scale(0.98) over 150ms ease
 *     so press feels physical without bouncing.
 *   - Disabled lowers opacity and disables hover/press transforms.
 *
 * IMPORTANT: the previous Button (lime fill + pink hover wipe) was a
 * legacy one-off used in HeroSection only. The new tiers replace it
 * everywhere. HeroSection's usage falls back to the new default
 * (`tier="secondary"` if omitted) and renders correctly with no migration.
 */

type Tier = "primary" | "secondary" | "tertiary";
type Size = "default" | "small";

interface CommonProps {
  /** "primary" | "secondary" | "tertiary". Default secondary so accidental
   *  omission doesn't paint the page teal. */
  tier?: Tier;
  size?: Size;
  /** Real icon (one set, lucide-style 16px stroke). Placed before label. */
  icon?: React.ReactNode;
  /** Tertiary tier only — small trailing icon for "View →" affordances. */
  trailingIcon?: React.ReactNode;
  fullWidth?: boolean;
  disabled?: boolean;
  children: React.ReactNode;
  className?: string;
}

type ButtonAsButton = CommonProps & {
  href?: undefined;
  type?: "button" | "submit" | "reset";
  onClick?: React.MouseEventHandler<HTMLButtonElement>;
  "aria-pressed"?: boolean;
  "aria-label"?: string;
  title?: string;
};

type ButtonAsLink = CommonProps & {
  href: string;
  target?: string;
  rel?: string;
  /** Optional side-effect on click (e.g. closing a mobile menu). The
   *  navigation itself is handled by the Link. */
  onClick?: React.MouseEventHandler<HTMLAnchorElement>;
  "aria-label"?: string;
  title?: string;
};

type Props = ButtonAsButton | ButtonAsLink;

// ─────────────────────────────────────────────────────────────────────
// Style tokens — single source of truth for every button render.
// ─────────────────────────────────────────────────────────────────────

const BASE =
  "inline-flex items-center justify-center gap-2 font-semibold rounded-md " +
  "transition-[background-color,color,transform,border-color,box-shadow] duration-150 ease-out " +
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 " +
  // disabled
  "disabled:cursor-not-allowed disabled:opacity-50";

// Comic-book depth: a thick navy border + hard offset shadow (no blur),
// matching the Tile/Card language. Hover lifts up-left and the shadow
// grows; pressing shifts the button down-right INTO its shadow so the
// click feels physical. Only filled tiers (primary/secondary) carry it —
// tertiary stays a flat inline "View →" affordance.
const DEPTH =
  "border-2 border-pnp-navy shadow-[3px_3px_0_var(--pnp-navy)] " +
  "hover:-translate-y-0.5 hover:shadow-[4px_5px_0_var(--pnp-navy)] " +
  "active:translate-x-[3px] active:translate-y-[3px] active:shadow-none " +
  "disabled:hover:translate-y-0 disabled:hover:shadow-[3px_3px_0_var(--pnp-navy)]";

const TIER_CLASSES: Record<Tier, string> = {
  primary:
    `bg-pnp-accent text-white hover:bg-pnp-accent-hover active:bg-pnp-accent-press disabled:hover:bg-pnp-accent ${DEPTH}`,
  secondary:
    `bg-white text-pnp-navy hover:bg-pnp-gray-50 disabled:hover:bg-white ${DEPTH}`,
  tertiary:
    "bg-transparent text-pnp-accent hover:bg-pnp-accent-soft active:bg-pnp-accent-soft disabled:hover:bg-transparent",
};

const SIZE_CLASSES: Record<Size, string> = {
  // 44px tall, comfortable touch target. Used for top-level CTAs.
  default: "h-11 px-5 text-sm",
  // 40px tall, denser. Used in filter rows / toolbar contexts.
  small: "h-10 px-4 text-sm",
};

export default function Button(props: Props) {
  const {
    tier = "secondary",
    size = "default",
    icon,
    trailingIcon,
    fullWidth,
    children,
    className = "",
  } = props;

  const composed = [
    BASE,
    TIER_CLASSES[tier],
    SIZE_CLASSES[size],
    fullWidth ? "w-full" : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  const content = (
    <>
      {icon && <span className="-ml-0.5 shrink-0">{icon}</span>}
      <span>{children}</span>
      {trailingIcon && tier === "tertiary" && (
        <span className="-mr-0.5 shrink-0">{trailingIcon}</span>
      )}
    </>
  );

  if ("href" in props && props.href) {
    // <Link> has no native `disabled`. Render an aria-disabled span so
    // the click is truly a no-op rather than navigating.
    if (props.disabled) {
      return (
        <span aria-disabled="true" className={composed}>
          {content}
        </span>
      );
    }
    return (
      <Link
        href={props.href}
        target={props.target}
        rel={props.rel}
        onClick={props.onClick}
        aria-label={props["aria-label"]}
        title={props.title}
        className={composed}
      >
        {content}
      </Link>
    );
  }

  const buttonProps = props as ButtonAsButton;
  return (
    <button
      type={buttonProps.type ?? "button"}
      onClick={buttonProps.onClick}
      disabled={buttonProps.disabled}
      aria-pressed={buttonProps["aria-pressed"]}
      aria-label={buttonProps["aria-label"]}
      title={buttonProps.title}
      className={composed}
    >
      {content}
    </button>
  );
}
