/**
 * Shared visual themes for projection-mode UIs (rich-task ProjectionView and
 * thin-slice runner). Defines a small palette of "scenes" — Light, Dark,
 * Polka, Underwater, Chalkboard — each with its own background, decorative
 * pattern, and accent colors.
 *
 * The theme configs use Tailwind class strings for class-based properties
 * (border, bg, text, ring) plus raw CSS for the page background. This lets
 * each consumer apply the theme with a mix of `style={{ background: ... }}`
 * for the page and `className={theme.textClass}` etc for content.
 */

export type ThemeId = "light" | "dark" | "polka" | "underwater" | "chalkboard";

export interface ThemeConfig {
  id: ThemeId;
  label: string;
  /** Whether the theme is dark — drives controls, text, dimmed states. */
  isDark: boolean;
  /** Background applied to the whole runner. CSS background shorthand. */
  background: string;
  /** Optional decorative pattern as an SVG data URL or layered gradient.
   *  Renders as a fixed full-screen layer behind the stage at low opacity. */
  pattern?: string;
  /** Tailwind classes for primary text color. */
  textClass: string;
  /** Card / bubble border + background classes. */
  bubbleBorder: string;
  bubbleBg: string;
  bubbleText: string;
  /** Accent color for the "newest bubble" ring + answer highlight. Tailwind. */
  accentRing: string;
  accentText: string;
}

// Decorative SVG patterns as data URLs. Kept inline because they're small and
// drawn with currentColor-friendly fills so they pick up the theme's accent.
const POLKA_PATTERN = `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 80 80'><circle cx='20' cy='20' r='5' fill='%23ffe25a' opacity='0.45'/><circle cx='60' cy='60' r='5' fill='%232dd4bf' opacity='0.35'/><circle cx='60' cy='20' r='3' fill='%23f97316' opacity='0.3'/><circle cx='20' cy='60' r='3' fill='%233f42d9' opacity='0.3'/></svg>")`;
const UNDERWATER_PATTERN = `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 160 160'><circle cx='30' cy='40' r='14' fill='none' stroke='white' stroke-width='1.2' opacity='0.18'/><circle cx='110' cy='90' r='22' fill='none' stroke='white' stroke-width='1.2' opacity='0.13'/><circle cx='75' cy='130' r='9' fill='none' stroke='white' stroke-width='1.2' opacity='0.2'/><circle cx='140' cy='30' r='6' fill='none' stroke='white' stroke-width='1.2' opacity='0.22'/><circle cx='25' cy='105' r='4' fill='white' opacity='0.18'/></svg>")`;
const CHALKBOARD_PATTERN = `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240' viewBox='0 0 240 240'><g fill='white' opacity='0.04'><circle cx='30' cy='40' r='1'/><circle cx='80' cy='90' r='0.8'/><circle cx='130' cy='30' r='1.2'/><circle cx='180' cy='110' r='0.9'/><circle cx='60' cy='180' r='1'/><circle cx='200' cy='200' r='1.1'/><circle cx='100' cy='220' r='0.7'/><circle cx='10' cy='150' r='0.9'/><circle cx='220' cy='60' r='1'/></g></svg>")`;

export const PROJECTION_THEMES: Record<ThemeId, ThemeConfig> = {
  light: {
    id: "light",
    label: "Light",
    isDark: false,
    background: "#ffffff",
    textClass: "text-pnp-gray-900",
    bubbleBorder: "border-pnp-navy",
    bubbleBg: "bg-white",
    bubbleText: "text-pnp-navy",
    accentRing: "ring-pnp-yellow/40",
    accentText: "text-pnp-blue",
  },
  dark: {
    id: "dark",
    label: "Dark",
    isDark: true,
    background: "#1a1f3d", // pnp-navy
    textClass: "text-white",
    bubbleBorder: "border-pnp-yellow/70",
    bubbleBg: "bg-white/5",
    bubbleText: "text-white",
    accentRing: "ring-pnp-yellow/40",
    accentText: "text-pnp-yellow",
  },
  polka: {
    id: "polka",
    label: "Polka",
    isDark: false,
    background: "#fff8e7", // soft cream
    pattern: POLKA_PATTERN,
    textClass: "text-pnp-navy",
    bubbleBorder: "border-pnp-orange",
    bubbleBg: "bg-white",
    bubbleText: "text-pnp-navy",
    accentRing: "ring-pnp-orange/40",
    accentText: "text-pnp-orange",
  },
  underwater: {
    id: "underwater",
    label: "Underwater",
    isDark: true,
    background: "linear-gradient(180deg, #0c4a6e 0%, #075985 50%, #0e7490 100%)",
    pattern: UNDERWATER_PATTERN,
    textClass: "text-white",
    bubbleBorder: "border-cyan-200",
    bubbleBg: "bg-white/10",
    bubbleText: "text-white",
    accentRing: "ring-cyan-200/50",
    accentText: "text-cyan-200",
  },
  chalkboard: {
    id: "chalkboard",
    label: "Chalkboard",
    isDark: true,
    background: "#1f3a2d", // dark chalkboard green
    pattern: CHALKBOARD_PATTERN,
    textClass: "text-white",
    bubbleBorder: "border-white/70",
    bubbleBg: "bg-white/5",
    bubbleText: "text-white",
    accentRing: "ring-yellow-200/40",
    accentText: "text-yellow-100",
  },
};

export const THEME_ORDER: ThemeId[] = [
  "light",
  "dark",
  "polka",
  "underwater",
  "chalkboard",
];
