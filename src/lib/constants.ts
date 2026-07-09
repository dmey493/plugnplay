import type { SubjectConfig } from "./types";

export const SUBJECTS: SubjectConfig[] = [
  {
    slug: "math",
    label: "Math",
    color: "#3f42d9",
    bgClass: "bg-pnp-blue",
    textClass: "text-pnp-blue",
    borderClass: "border-pnp-blue",
  },
  {
    slug: "science",
    label: "Science",
    color: "#2dd4bf",
    bgClass: "bg-pnp-teal",
    textClass: "text-pnp-teal",
    borderClass: "border-pnp-teal",
  },
];

export const GRADES = [6, 7, 8] as const;

export const PURPOSES = [
  { value: "warm-up", label: "Warm-Up" },
  { value: "direct-instruction", label: "Direct Instruction" },
  { value: "guided-practice", label: "Guided Practice" },
  { value: "independent-practice", label: "Independent Practice" },
  { value: "check-for-understanding", label: "Check for Understanding" },
  { value: "intervention", label: "Intervention" },
  { value: "closing", label: "Closing" },
] as const;

export const MTSS_TIERS = [1, 2, 3] as const;

export const NAV_ITEMS: { label: string; href: string; soon?: boolean }[] = [
  { label: "Math", href: "/math" },
  { label: "Science", href: "/science" },
];

// ─── Homepage "jump-in" board ─────────────────────────────────────────
// Powers the playground hero — the live subjects and tools teachers jump
// straight into. `icon` is a key into ICONS in components/ui/icons.tsx;
// `accent` is the icon-chip fill.
export type JumpInIcon =
  | "calculator"
  | "fileplus"
  | "cards"
  | "library"
  | "book"
  | "flask"
  | "layers";

export type JumpInTile = {
  label: string;
  href: string;
  blurb: string;
  icon: JumpInIcon;
  accent: string;
  /** Icon color on the chip; defaults to white. Set dark on light chips. */
  accentText?: string;
  status: "live" | "soon";
};

export const JUMP_IN: JumpInTile[] = [
  { label: "Math", href: "/math", blurb: "Tasks, units & practice", icon: "calculator", accent: "#0d9488", status: "live" },
  { label: "Science", href: "/science", blurb: "Graph of the Week & stimuli", icon: "flask", accent: "#22c55e", status: "live" },
  { label: "Exit Tickets", href: "/math/generator", blurb: "Generate & print in seconds", icon: "fileplus", accent: "#1a1f3d", status: "live" },
  { label: "Lesson activities", href: "/math/units", blurb: "Rich tasks & thin slices", icon: "layers", accent: "#3f42d9", status: "live" },
];

// Brand-only accent cycle for per-item card stripes (units by module, hub
// tiles, strategies by subject). Replaces the off-palette MODULE_COLORS /
// tile colors so nothing uses non-token hex. Every value is a defined
// brand token (see globals.css). Use brandAccent(i) to pick by index.
export const BRAND_CYCLE = [
  "#0d9488", // teal-600 (accent)
  "#3f42d9", // blue
  "#f97316", // orange
  "#f5d000", // yellow-dark
  "#22c55e", // green
  "#60a5fa", // light-blue
  "#1a1f3d", // navy
] as const;

export function brandAccent(i: number): string {
  const n = BRAND_CYCLE.length;
  return BRAND_CYCLE[((i % n) + n) % n];
}

export const TOOLS = [
  {
    title: "Strategies Library",
    description:
      "Browse teaching strategies by subject, purpose, and MTSS tier.",
    href: "/library",
    active: true,
    icon: "book",
  },
] as const;

export function getSubjectBySlug(slug: string): SubjectConfig | undefined {
  return SUBJECTS.find((s) => s.slug === slug);
}
