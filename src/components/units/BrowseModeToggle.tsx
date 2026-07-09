"use client";

import Link from "next/link";

/**
 * Canonical browse-mode toggle that appears at the top of `/math/units`,
 * `/math/units/[unitId]`, and `/math/rich-tasks`. Switches between three
 * organisational lenses on the same task library:
 *
 *   - By Unit     → `/math/units` (the Fishtank-style teacher view)
 *   - By Standard → `/math/rich-tasks` (?mode=standard, the existing default)
 *   - By Concept  → `/math/rich-tasks` (?mode=concept)
 *
 * Pure navigation — no internal state. Renders as a segmented control
 * matching the design-system language: active = accent fill + white text,
 * inactive = transparent + neutral text. Uses rounded-md, never full-pill,
 * so it reads as "control" not "metadata."
 */
type Mode = "unit" | "standard" | "concept";

interface Props {
  current: Mode;
}

export default function BrowseModeToggle({ current }: Props) {
  return (
    <div
      role="tablist"
      aria-label="Browse mode"
      className="inline-flex items-center gap-1 rounded-lg border border-pnp-gray-200 bg-white p-1"
    >
      <ModeLink mode="unit" current={current} href="/math/units">
        By Unit
      </ModeLink>
      <ModeLink mode="standard" current={current} href="/math/rich-tasks">
        By Standard
      </ModeLink>
      <ModeLink mode="concept" current={current} href="/math/rich-tasks?mode=concept">
        By Concept
      </ModeLink>
    </div>
  );
}

function ModeLink({
  mode,
  current,
  href,
  children,
}: {
  mode: Mode;
  current: Mode;
  href: string;
  children: React.ReactNode;
}) {
  const active = current === mode;
  return (
    <Link
      href={href}
      role="tab"
      aria-selected={active}
      className={[
        "inline-flex h-9 select-none items-center rounded-md px-3 text-sm font-semibold",
        "transition-[background-color,color,transform] duration-150 ease-out",
        "active:scale-[0.98]",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2",
        active
          ? "bg-pnp-accent text-white"
          : "text-pnp-gray-700 hover:bg-pnp-gray-100",
      ].join(" ")}
    >
      {children}
    </Link>
  );
}
