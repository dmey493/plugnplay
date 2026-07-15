import type { NumberLineItem } from "../types";
import { GRID, NAVY } from "../constants";

/** Number line — one GRID unit per integer, arrowheads on both ends,
 *  whole-number tick labels (every 1, thinning to every 5 on long lines).
 *  Centred on the local origin so rotation/snapping behave like tiles. */
export default function NumberLine({ item }: { item: NumberLineItem }) {
  const span = item.max - item.min;
  const w = span * GRID;
  const x0 = -w / 2;
  const color = item.tint ?? NAVY;
  const labelEvery = span > 24 ? 5 : 1;

  const ticks: React.ReactNode[] = [];
  for (let v = item.min; v <= item.max; v++) {
    const x = x0 + (v - item.min) * GRID;
    const major = v % labelEvery === 0;
    ticks.push(
      <g key={v}>
        <line x1={x} y1={major ? -10 : -6} x2={x} y2={major ? 10 : 6} stroke={color} strokeWidth={major ? 2 : 1.5} />
        {major && (
          <text
            x={x}
            y={26}
            textAnchor="middle"
            fontSize={13}
            fontWeight={700}
            fill={color}
            style={{ fontFamily: "var(--font-heading), sans-serif", pointerEvents: "none" }}
          >
            {v}
          </text>
        )}
      </g>
    );
  }

  return (
    <g>
      {/* Invisible hit area so the whole strip is grabbable, not just the 2px line. */}
      <rect x={x0 - 12} y={-36} width={w + 24} height={72} fill="transparent" />
      <line x1={x0 - 8} y1={0} x2={x0 + w + 8} y2={0} stroke={color} strokeWidth={2.5} />
      {/* Arrowheads */}
      <path d={`M ${x0 - 12} 0 l 8 -5 v 10 z`} fill={color} />
      <path d={`M ${x0 + w + 12} 0 l -8 -5 v 10 z`} fill={color} />
      {ticks}
    </g>
  );
}
