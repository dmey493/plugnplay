import { BRAND_CYCLE } from "@/lib/core/constants";
import type { Figure } from "@/lib/library/science";

/**
 * Lightweight SVG chart for the ILEARN stimulus figures: bar, grouped_bar,
 * line, scatter. Pure/static (no client JS), responsive via viewBox, styled
 * with the brand palette. Data comes straight from the cluster's `figure`.
 */

const W = 580;
const H = 320;
const M = { top: 30, right: 18, bottom: 52, left: 56 };
const PX0 = M.left;
const PX1 = W - M.right;
const PY0 = M.top;
const PY1 = H - M.bottom;

function niceMax(raw: number): number {
  if (raw <= 0) return 1;
  const pow = Math.pow(10, Math.floor(Math.log10(raw)));
  const n = raw / pow;
  const step = n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10;
  return step * pow;
}

export default function Chart({ figure }: { figure: Figure }) {
  const series = figure.series ?? [];
  const xs = figure.x ?? [];
  if (series.length === 0 || xs.length === 0) return null;

  const numericX = xs.every((v) => v !== "" && Number.isFinite(Number(v)));
  const isXY = figure.chart_type === "line" || figure.chart_type === "scatter";
  const allVals = series.flatMap((s) => s.values);
  const dataMax = Math.max(0, ...allVals);
  const yMax = figure.ymax ?? niceMax(dataMax * 1.1);

  const yTo = (v: number) => PY1 - (v / yMax) * (PY1 - PY0);

  // X positioning: numeric axis for xy charts with numeric x, else category slots.
  const useNumericAxis = isXY && numericX;
  const xNums = xs.map((v) => Number(v));
  const xMin = useNumericAxis ? Math.min(...xNums) : 0;
  const xMax = useNumericAxis ? Math.max(...xNums) : 0;
  const xToNum = (v: number) =>
    PX0 + ((v - xMin) / (xMax - xMin || 1)) * (PX1 - PX0);
  const slotW = (PX1 - PX0) / xs.length;
  const xToCat = (i: number) => PX0 + slotW * (i + 0.5);

  const yTicks = 5;
  const gridY = Array.from({ length: yTicks + 1 }, (_, i) => (yMax / yTicks) * i);
  const fmt = (n: number) =>
    Number.isInteger(n) ? String(n) : n.toFixed(n < 1 ? 2 : 1);

  const color = (i: number) => BRAND_CYCLE[i % BRAND_CYCLE.length];
  const showLegend = series.length > 1;

  return (
    <figure className="my-4">
      {figure.title && (
        <p className="mb-1 text-center text-sm font-semibold text-[var(--pnp-navy)]">
          {figure.title}
        </p>
      )}
      <div className="overflow-x-auto">
        <svg
          viewBox={`0 0 ${W} ${H}`}
          role="img"
          aria-label={figure.caption ?? figure.title ?? "Chart"}
          className="mx-auto h-auto w-full max-w-[640px] min-w-[420px]"
        >
          {/* y gridlines + labels */}
          {gridY.map((v, i) => (
            <g key={i}>
              <line
                x1={PX0} x2={PX1} y1={yTo(v)} y2={yTo(v)}
                stroke="var(--pnp-gray-200)" strokeWidth={1}
              />
              <text
                x={PX0 - 8} y={yTo(v) + 3} textAnchor="end"
                className="fill-[var(--pnp-gray-500)]" fontSize={11}
              >
                {fmt(v)}
              </text>
            </g>
          ))}
          {/* axes */}
          <line x1={PX0} x2={PX1} y1={PY1} y2={PY1} stroke="var(--pnp-gray-400)" strokeWidth={1.5} />
          <line x1={PX0} x2={PX0} y1={PY0} y2={PY1} stroke="var(--pnp-gray-400)" strokeWidth={1.5} />

          {/* bars */}
          {figure.chart_type === "bar" &&
            xs.map((_, i) => {
              const v = series[0].values[i] ?? 0;
              const bw = slotW * 0.56;
              return (
                <rect
                  key={i}
                  x={xToCat(i) - bw / 2} y={yTo(v)}
                  width={bw} height={PY1 - yTo(v)}
                  fill={color(0)} rx={2}
                />
              );
            })}

          {/* grouped bars */}
          {figure.chart_type === "grouped_bar" &&
            xs.map((_, i) => {
              const gw = slotW * 0.72;
              const bw = gw / series.length;
              const x0 = xToCat(i) - gw / 2;
              return series.map((s, si) => {
                const v = s.values[i] ?? 0;
                return (
                  <rect
                    key={`${i}-${si}`}
                    x={x0 + si * bw + 1} y={yTo(v)}
                    width={Math.max(1, bw - 2)} height={PY1 - yTo(v)}
                    fill={color(si)} rx={1.5}
                  />
                );
              });
            })}

          {/* lines */}
          {figure.chart_type === "line" &&
            series.map((s, si) => {
              const pts = s.values.map((v, i) => {
                const x = useNumericAxis ? xToNum(xNums[i]) : xToCat(i);
                return `${x},${yTo(v)}`;
              });
              return (
                <g key={si}>
                  <polyline
                    points={pts.join(" ")} fill="none"
                    stroke={color(si)} strokeWidth={2.5}
                    strokeLinejoin="round" strokeLinecap="round"
                  />
                  {s.values.map((v, i) => {
                    const x = useNumericAxis ? xToNum(xNums[i]) : xToCat(i);
                    return <circle key={i} cx={x} cy={yTo(v)} r={3} fill={color(si)} />;
                  })}
                </g>
              );
            })}

          {/* scatter */}
          {figure.chart_type === "scatter" &&
            series.map((s, si) =>
              s.values.map((v, i) => {
                const x = useNumericAxis ? xToNum(xNums[i]) : xToCat(i);
                return (
                  <circle
                    key={`${si}-${i}`} cx={x} cy={yTo(v)} r={4}
                    fill={color(si)} fillOpacity={0.85}
                  />
                );
              })
            )}

          {/* x labels */}
          {xs.map((v, i) => {
            const x = useNumericAxis ? xToNum(xNums[i]) : xToCat(i);
            // thin out numeric labels if crowded
            if (useNumericAxis && xs.length > 8 && i % 2 === 1) return null;
            return (
              <text
                key={i} x={x} y={PY1 + 16} textAnchor="middle"
                className="fill-[var(--pnp-gray-600)]" fontSize={11}
              >
                {String(v)}
              </text>
            );
          })}

          {/* axis titles */}
          {figure.xlabel && (
            <text x={(PX0 + PX1) / 2} y={H - 8} textAnchor="middle"
              className="fill-[var(--pnp-gray-700)]" fontSize={12} fontWeight={600}>
              {figure.xlabel}
            </text>
          )}
          {figure.ylabel && (
            <text
              transform={`translate(14 ${(PY0 + PY1) / 2}) rotate(-90)`}
              textAnchor="middle" className="fill-[var(--pnp-gray-700)]"
              fontSize={12} fontWeight={600}
            >
              {figure.ylabel}
            </text>
          )}
        </svg>
      </div>

      {showLegend && (
        <ul className="mt-1 flex flex-wrap justify-center gap-x-4 gap-y-1">
          {series.map((s, i) => (
            <li key={i} className="flex items-center gap-1.5 text-xs text-[var(--pnp-gray-700)]">
              <span className="inline-block h-2.5 w-2.5 rounded-sm" style={{ background: color(i) }} />
              {s.name}
            </li>
          ))}
        </ul>
      )}

      {(figure.caption || figure.source) && (
        <figcaption className="mt-1.5 text-center text-xs text-[var(--pnp-gray-500)]">
          {figure.caption}
          {figure.source ? ` ${figure.source}` : ""}
        </figcaption>
      )}
    </figure>
  );
}
