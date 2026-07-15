import type { FractionCircleItem } from "../types";
import { FRACTION_CIRCLE_R, FRACTION_FILLS, NAVY, STROKE_W } from "../constants";

/** Fraction circle sector — 1/n of a circle, pivoting on the circle
 *  centre so sectors dropped at one point assemble into a whole purely by
 *  rotation. Shares the fraction-tile fill ramp so 1/3 the bar and 1/3 the
 *  circle read as the same value. */
export default function FractionCircle({ item }: { item: FractionCircleItem }) {
  const R = FRACTION_CIRCLE_R;
  const d = item.denominator;
  const fill = item.tint ?? FRACTION_FILLS[d] ?? "var(--pnp-gray-200)";
  const label = d === 1 ? "1" : `1/${d}`;

  let path: React.ReactNode;
  if (d === 1) {
    path = <circle r={R} fill={fill} stroke={NAVY} strokeWidth={STROKE_W} />;
  } else {
    // Sector from straight-up, sweeping clockwise by 2π/d.
    const a = (2 * Math.PI) / d;
    const x1 = 0;
    const y1 = -R;
    const x2 = R * Math.sin(a);
    const y2 = -R * Math.cos(a);
    path = (
      <path
        d={`M 0 0 L ${x1} ${y1} A ${R} ${R} 0 ${a > Math.PI ? 1 : 0} 1 ${x2} ${y2} Z`}
        fill={fill}
        stroke={NAVY}
        strokeWidth={STROKE_W}
        strokeLinejoin="round"
      />
    );
  }

  // Label sits along the sector's bisector (or dead centre for a whole).
  const mid = d === 1 ? 0 : Math.PI / d;
  const lr = d === 1 ? 0 : R * 0.62;
  const showLabel = d <= 12;
  return (
    <g>
      {path}
      {showLabel && (
        <text
          x={lr * Math.sin(mid)}
          y={-lr * Math.cos(mid)}
          textAnchor="middle"
          dominantBaseline="central"
          fontSize={d >= 9 ? 13 : 16}
          fontWeight={700}
          fill={NAVY}
          style={{ fontFamily: "var(--font-heading), sans-serif", pointerEvents: "none" }}
        >
          {label}
        </text>
      )}
    </g>
  );
}
