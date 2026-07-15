import type { ClockItem } from "../types";
import { CLOCK_HOUR_LEN, CLOCK_MINUTE_LEN, CLOCK_R, NAVY, STROKE_W } from "../constants";

/** Analog clock pieces. The face is static; the hour and minute hands are
 *  separate pieces that pivot at their local origin, so dropping a hand on
 *  the face centre and rotating it sets the time with the existing rotate
 *  interaction. */
export default function Clock({ item }: { item: ClockItem }) {
  if (item.part !== "face") {
    const len = item.part === "hour" ? CLOCK_HOUR_LEN : CLOCK_MINUTE_LEN;
    const w = item.part === "hour" ? 10 : 7;
    const fill = item.tint ?? (item.part === "hour" ? "var(--pnp-blue)" : "var(--pnp-red)");
    return (
      <g>
        {/* hand pointing up from the pivot, with a short counterweight tail */}
        <path
          d={`M ${-w / 2} 12 L ${-w / 2} ${-len + w} Q 0 ${-len} ${w / 2} ${-len + w} L ${w / 2} 12 Z`}
          fill={fill}
          stroke={NAVY}
          strokeWidth={1.5}
          strokeLinejoin="round"
        />
        <circle r={6} fill={NAVY} />
      </g>
    );
  }

  const ticks: React.ReactNode[] = [];
  const numbers: React.ReactNode[] = [];
  for (let m = 0; m < 60; m++) {
    const a = (m * Math.PI) / 30;
    const major = m % 5 === 0;
    const r1 = CLOCK_R - (major ? 14 : 8);
    const r2 = CLOCK_R - 4;
    ticks.push(
      <line
        key={m}
        x1={r1 * Math.sin(a)}
        y1={-r1 * Math.cos(a)}
        x2={r2 * Math.sin(a)}
        y2={-r2 * Math.cos(a)}
        stroke={NAVY}
        strokeWidth={major ? 2.5 : 1}
        opacity={major ? 1 : 0.5}
      />
    );
  }
  for (let hnum = 1; hnum <= 12; hnum++) {
    const a = (hnum * Math.PI) / 6;
    const r = CLOCK_R - 30;
    numbers.push(
      <text
        key={hnum}
        x={r * Math.sin(a)}
        y={-r * Math.cos(a)}
        textAnchor="middle"
        dominantBaseline="central"
        fontSize={22}
        fontWeight={800}
        fill={NAVY}
        style={{ fontFamily: "var(--font-heading), sans-serif", pointerEvents: "none" }}
      >
        {hnum}
      </text>
    );
  }
  return (
    <g>
      <circle r={CLOCK_R} fill={item.tint ?? "var(--pnp-yellow)"} stroke={NAVY} strokeWidth={STROKE_W + 1} />
      <circle r={CLOCK_R - 2} fill="#ffffff" stroke="none" opacity={0.85} />
      {ticks}
      {numbers}
      <circle r={7} fill={NAVY} />
    </g>
  );
}
