import React from "react";

/**
 * Emojiless, lucide-style inline SVG icons for the teaching-approach tools.
 * The source toolbelt used emoji marks; the Plug N Play design system mandates
 * real icons only. 24×24, currentColor stroke, width 2, round caps/joins.
 * Keyed by the `icon` string on each ToolCard in lib/approach.ts.
 */

type IconProps = { className?: string; size?: number };

function Svg({
  size = 24,
  className,
  children,
}: IconProps & { children: React.ReactNode }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

export const APPROACH_ICONS: Record<string, React.FC<IconProps>> = {
  // Number Talks — speech bubble
  talk: (p) => (
    <Svg {...p}>
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      <path d="M8 9h8M8 13h5" />
    </Svg>
  ),
  // Number Strings — linked sequence
  string: (p) => (
    <Svg {...p}>
      <circle cx="5" cy="12" r="2" />
      <circle cx="12" cy="12" r="2" />
      <circle cx="19" cy="12" r="2" />
      <path d="M7 12h3M14 12h3" />
    </Svg>
  ),
  // Same But Different / WODB — four-box compare
  compare: (p) => (
    <Svg {...p}>
      <rect x="3" y="3" width="7" height="7" rx="1" />
      <rect x="14" y="3" width="7" height="7" rx="1" />
      <rect x="3" y="14" width="7" height="7" rx="1" />
      <path d="M14 17.5a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z" />
    </Svg>
  ),
  // Quick Images — flashed picture
  image: (p) => (
    <Svg {...p}>
      <rect x="3" y="3" width="18" height="18" rx="2" />
      <circle cx="9" cy="9" r="1.5" />
      <path d="m21 15-5-5L5 21" />
    </Svg>
  ),
  // Would You Rather — branching choice
  branch: (p) => (
    <Svg {...p}>
      <circle cx="6" cy="6" r="2.5" />
      <circle cx="18" cy="6" r="2.5" />
      <circle cx="12" cy="19" r="2.5" />
      <path d="M6 8.5V11a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V8.5M12 13v3.5" />
    </Svg>
  ),
  // Spiral / Retrieval Review — refresh loop
  refresh: (p) => (
    <Svg {...p}>
      <path d="M21 12a9 9 0 1 1-2.64-6.36" />
      <path d="M21 3v6h-6" />
    </Svg>
  ),
  // Rich Tasks — lightbulb / big idea
  task: (p) => (
    <Svg {...p}>
      <path d="M9 18h6" />
      <path d="M10 22h4" />
      <path d="M8.5 14a5 5 0 1 1 7 0c-.7.7-1.5 1.3-1.5 2.5h-4c0-1.2-.8-1.8-1.5-2.5z" />
    </Svg>
  ),
  // Thin-Slicing — incremental steps
  slice: (p) => (
    <Svg {...p}>
      <path d="M4 20h4v-4" />
      <path d="M10 16h4v-4" />
      <path d="M16 12h4V8" />
      <path d="M4 20 20 4" opacity="0" />
    </Svg>
  ),
  // Responsive DI — teacher at board
  teach: (p) => (
    <Svg {...p}>
      <rect x="3" y="3" width="18" height="12" rx="2" />
      <path d="M7 8h7M7 11h4" />
      <path d="M12 15v6M8 21h8" />
    </Svg>
  ),
  // Error Analysis — magnifier
  search: (p) => (
    <Svg {...p}>
      <circle cx="11" cy="11" r="7" />
      <path d="m21 21-4.3-4.3" />
      <path d="M9 11h4M11 9v4" />
    </Svg>
  ),
  // Fluency Practice — pencil
  pencil: (p) => (
    <Svg {...p}>
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z" />
    </Svg>
  ),
  // CFU / Exit Tickets — checked clipboard
  check: (p) => (
    <Svg {...p}>
      <rect x="5" y="4" width="14" height="17" rx="2" />
      <path d="M9 4V3a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1" />
      <path d="m9 13 2 2 4-4" />
    </Svg>
  ),
  // Talk Moves — conversation
  chat: (p) => (
    <Svg {...p}>
      <path d="M8 10h8M8 14h5" />
      <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
    </Svg>
  ),
  // When to Tell — compass / judgment
  compass: (p) => (
    <Svg {...p}>
      <circle cx="12" cy="12" r="10" />
      <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
    </Svg>
  ),
  // Access & Equity — supporting hands
  hands: (p) => (
    <Svg {...p}>
      <path d="M12 3v6" />
      <path d="M8 21a4 4 0 0 1-4-4V9a1.5 1.5 0 0 1 3 0v4" />
      <path d="M16 21a4 4 0 0 0 4-4V9a1.5 1.5 0 0 0-3 0v4" />
      <path d="M9 13V6.5a1.5 1.5 0 0 1 3 0V12M12 12V7a1.5 1.5 0 0 1 3 0v6" />
    </Svg>
  ),
  // Vertical surfaces — whiteboard
  board: (p) => (
    <Svg {...p}>
      <rect x="3" y="3" width="18" height="14" rx="2" />
      <path d="M12 17v4M8 21h8" />
      <path d="m7 10 2.5 2.5L15 7" />
    </Svg>
  ),
  // 5 Practices — target
  target: (p) => (
    <Svg {...p}>
      <circle cx="12" cy="12" r="9" />
      <circle cx="12" cy="12" r="5" />
      <circle cx="12" cy="12" r="1" />
    </Svg>
  ),
  // Connecting Representations — linked chart
  chart: (p) => (
    <Svg {...p}>
      <path d="M3 3v18h18" />
      <path d="m7 15 3-3 3 2 5-6" />
    </Svg>
  ),
  // fallbacks used by strands / practices tiles
  strand: (p) => (
    <Svg {...p}>
      <path d="M4 4c4 0 4 4 8 4s4-4 8-4M4 12c4 0 4 4 8 4s4-4 8-4M4 20c4 0 4-4 8-4s4 4 8 4" />
    </Svg>
  ),
  practice: (p) => (
    <Svg {...p}>
      <path d="M12 2 2 7l10 5 10-5-10-5z" />
      <path d="m2 17 10 5 10-5M2 12l10 5 10-5" />
    </Svg>
  ),
};

export function ApproachIcon({
  name,
  size = 32,
  className,
}: {
  name: string;
  size?: number;
  className?: string;
}) {
  const Cmp = APPROACH_ICONS[name] ?? APPROACH_ICONS.task;
  return <Cmp size={size} className={className} />;
}
