"use client";

import type { ThinSliceShape } from "@/lib/core/types";

interface Props {
  shape: ThinSliceShape;
  labels: Record<string, string>;
  /** Pixel width of the rendered shape. Height is derived. */
  width?: number;
}

/**
 * Renders a geometric shape with per-step labels filled in. The shape itself is
 * fixed by the slice; only the labels change per step. Uses currentColor so
 * stroke/text adapt to the bubble's text color (light vs dark theme).
 */
export default function ShapeRenderer({ shape, labels, width = 140 }: Props) {
  if (shape.kind === "cylinder") {
    return <CylinderShape labels={labels} width={width} />;
  }
  if (shape.kind === "right-triangle") {
    return <RightTriangleShape labels={labels} width={width} />;
  }
  return null;
}

// =====================
// CYLINDER
// =====================
// labels: { r, h } — both as authored strings (e.g., "2", "\frac{1}{2}").
// Note: we render the labels as plain text (not via MathExpression) because
// SVG <text> doesn't compose with HTML. For fractional radii we just write
// the string; the bubble's own text shows the formal "r = 1/2".
function CylinderShape({
  labels,
  width,
}: {
  labels: Record<string, string>;
  width: number;
}) {
  const r = labels.r ?? "r";
  const h = labels.h ?? "h";

  // Cylinder geometry. We reserve a generous right gutter for the h label so
  // labels like "h = 1/2" or "h = 100" never spill out of the viewBox.
  const W = width;
  const H = width * 1.1;
  const rightGutter = W * 0.42;
  const cx = (W - rightGutter) / 2 + W * 0.02;
  const ellipseRx = (W - rightGutter) * 0.36;
  const ellipseRy = ellipseRx * 0.28;
  const topY = H * 0.2;
  const botY = H * 0.82;
  const labelFontSize = W * 0.085;

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      width={W}
      height={H}
      stroke="currentColor"
      fill="none"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-label={`Cylinder with radius ${r} and height ${h}`}
    >
      {/* body sides */}
      <line x1={cx - ellipseRx} y1={topY} x2={cx - ellipseRx} y2={botY} />
      <line x1={cx + ellipseRx} y1={topY} x2={cx + ellipseRx} y2={botY} />
      {/* bottom ellipse */}
      <ellipse cx={cx} cy={botY} rx={ellipseRx} ry={ellipseRy} />
      {/* top ellipse — back half dashed, front half solid */}
      <path
        d={`M ${cx - ellipseRx} ${topY}
            a ${ellipseRx} ${ellipseRy} 0 0 0 ${2 * ellipseRx} 0`}
        strokeDasharray="3 3"
      />
      <path
        d={`M ${cx - ellipseRx} ${topY}
            a ${ellipseRx} ${ellipseRy} 0 0 1 ${2 * ellipseRx} 0`}
      />

      {/* radius arrow on top ellipse: from center to right edge */}
      <line x1={cx} y1={topY} x2={cx + ellipseRx} y2={topY} strokeWidth={1.2} />
      <text
        x={cx + ellipseRx / 2}
        y={topY - W * 0.025}
        fill="currentColor"
        stroke="none"
        fontSize={labelFontSize}
        fontFamily="system-ui, sans-serif"
        fontWeight={600}
        textAnchor="middle"
      >
        r = {r}
      </text>

      {/* height arrow on the right side. Sits inside the right gutter. */}
      {(() => {
        const hArrowX = cx + ellipseRx + W * 0.05;
        const tickHalf = W * 0.025;
        return (
          <>
            <line x1={hArrowX} y1={topY} x2={hArrowX} y2={botY} strokeWidth={1.2} />
            <line x1={hArrowX - tickHalf} y1={topY} x2={hArrowX + tickHalf} y2={topY} strokeWidth={1.2} />
            <line x1={hArrowX - tickHalf} y1={botY} x2={hArrowX + tickHalf} y2={botY} strokeWidth={1.2} />
          </>
        );
      })()}
      <text
        x={cx + ellipseRx + W * 0.09}
        y={(topY + botY) / 2}
        fill="currentColor"
        stroke="none"
        fontSize={labelFontSize}
        fontFamily="system-ui, sans-serif"
        fontWeight={600}
        textAnchor="start"
        dominantBaseline="middle"
      >
        h = {h}
      </text>
    </svg>
  );
}

// =====================
// RIGHT TRIANGLE
// =====================
// labels: { a, b, c } — leg a (vertical), leg b (horizontal), hypotenuse c.
// Use "?" to mark the unknown side.
function RightTriangleShape({
  labels,
  width,
}: {
  labels: Record<string, string>;
  width: number;
}) {
  const a = labels.a ?? "a";
  const b = labels.b ?? "b";
  const c = labels.c ?? "c";

  // Reserve generous gutters: left for the `a =` label, bottom for `b =`,
  // right/top for `c =`. Labels can be 5-7 chars (e.g., "c = 169").
  const W = width;
  const H = width * 1.02;
  const leftGutter = W * 0.32;
  const bottomGutter = W * 0.22;
  const rightGutter = W * 0.18;
  const topPad = W * 0.06;
  const x0 = leftGutter; // bottom-left vertex = right angle
  const y0 = H - bottomGutter;
  const x1 = W - rightGutter; // bottom-right
  const y1 = y0;
  const x2 = x0; // top-left
  const y2 = topPad;
  const labelFontSize = W * 0.078;

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      width={W}
      height={H}
      stroke="currentColor"
      fill="none"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-label={`Right triangle with legs ${a} and ${b} and hypotenuse ${c}`}
    >
      {/* triangle */}
      <polygon
        points={`${x0},${y0} ${x1},${y1} ${x2},${y2}`}
        fill="currentColor"
        fillOpacity={0.06}
      />
      {/* right-angle square */}
      {(() => {
        const sq = W * 0.07;
        return (
          <polyline
            points={`${x0 + sq},${y0} ${x0 + sq},${y0 - sq} ${x0},${y0 - sq}`}
            strokeWidth={1.4}
          />
        );
      })()}

      {/* leg a — vertical (left side). Sits inside the left gutter. */}
      <text
        x={x0 - W * 0.025}
        y={(y0 + y2) / 2}
        fill="currentColor"
        stroke="none"
        fontSize={labelFontSize}
        fontFamily="system-ui, sans-serif"
        fontWeight={600}
        textAnchor="end"
        dominantBaseline="middle"
      >
        a = {a}
      </text>

      {/* leg b — horizontal (bottom). Sits inside the bottom gutter. */}
      <text
        x={(x0 + x1) / 2}
        y={y0 + bottomGutter * 0.55}
        fill="currentColor"
        stroke="none"
        fontSize={labelFontSize}
        fontFamily="system-ui, sans-serif"
        fontWeight={600}
        textAnchor="middle"
        dominantBaseline="middle"
      >
        b = {b}
      </text>

      {/* hypotenuse c — label offset perpendicular to the hypotenuse, away
          from the right angle. We center it so it doesn't spill out of the
          right or top edges. */}
      {(() => {
        const mx = (x1 + x2) / 2;
        const my = (y1 + y2) / 2;
        const offset = W * 0.06;
        // Push toward the upper-right where there's free space (we have a
        // right gutter and top pad).
        return (
          <text
            x={Math.min(mx + offset, W - rightGutter * 0.15)}
            y={Math.max(my - offset, topPad + labelFontSize * 0.5)}
            fill="currentColor"
            stroke="none"
            fontSize={labelFontSize}
            fontFamily="system-ui, sans-serif"
            fontWeight={600}
            textAnchor="middle"
            dominantBaseline="middle"
          >
            c = {c}
          </text>
        );
      })()}
    </svg>
  );
}
