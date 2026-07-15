import type React from "react";

export interface BBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

interface Props {
  bbox: BBox;
  /** World units per screen pixel (1 / zoom) — keeps chrome a constant
   *  on-screen size at any zoom. */
  scale: number;
  onDelete: () => void;
  onDuplicate: () => void;
  onRotateStart: (e: React.PointerEvent) => void;
}

const HANDLE_PX = 16;
const ROTATE_ARM_PX = 28;

/** Bounding box + transform handles for the current selection. Delete and
 *  duplicate are clicks; rotate is a drag the board interprets. Everything
 *  is sized in world units scaled by `scale` so it looks fixed on screen. */
export default function SelectionOverlay({ bbox, scale, onDelete, onDuplicate, onRotateStart }: Props) {
  const r = (HANDLE_PX / 2) * scale;
  const arm = ROTATE_ARM_PX * scale;
  const cx = (bbox.x1 + bbox.x2) / 2;
  const stop = (e: React.PointerEvent) => e.stopPropagation();

  return (
    <g>
      <rect
        x={bbox.x1}
        y={bbox.y1}
        width={bbox.x2 - bbox.x1}
        height={bbox.y2 - bbox.y1}
        fill="none"
        stroke="var(--pnp-accent)"
        strokeWidth={1.5 * scale}
        strokeDasharray={`${6 * scale} ${4 * scale}`}
        pointerEvents="none"
      />

      {/* Rotate handle — an arm above the top edge. */}
      <line x1={cx} y1={bbox.y1} x2={cx} y2={bbox.y1 - arm} stroke="var(--pnp-accent)" strokeWidth={1.5 * scale} pointerEvents="none" />
      <circle
        cx={cx}
        cy={bbox.y1 - arm}
        r={r}
        fill="white"
        stroke="var(--pnp-accent)"
        strokeWidth={1.5 * scale}
        style={{ cursor: "grab" }}
        onPointerDown={(e) => {
          e.stopPropagation();
          onRotateStart(e);
        }}
      />

      {/* Duplicate (＋) — bottom-left corner. */}
      <g
        transform={`translate(${bbox.x1} ${bbox.y2})`}
        style={{ cursor: "pointer" }}
        onPointerDown={stop}
        onClick={(e) => {
          e.stopPropagation();
          onDuplicate();
        }}
      >
        <circle r={r} fill="white" stroke="var(--pnp-accent)" strokeWidth={1.5 * scale} />
        <line x1={-r * 0.5} y1={0} x2={r * 0.5} y2={0} stroke="var(--pnp-accent)" strokeWidth={1.5 * scale} />
        <line x1={0} y1={-r * 0.5} x2={0} y2={r * 0.5} stroke="var(--pnp-accent)" strokeWidth={1.5 * scale} />
      </g>

      {/* Delete (×) — top-right corner. */}
      <g
        transform={`translate(${bbox.x2} ${bbox.y1})`}
        style={{ cursor: "pointer" }}
        onPointerDown={stop}
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
      >
        <circle r={r} fill="white" stroke="var(--pnp-red)" strokeWidth={1.5 * scale} />
        <line x1={-r * 0.45} y1={-r * 0.45} x2={r * 0.45} y2={r * 0.45} stroke="var(--pnp-red)" strokeWidth={1.5 * scale} />
        <line x1={-r * 0.45} y1={r * 0.45} x2={r * 0.45} y2={-r * 0.45} stroke="var(--pnp-red)" strokeWidth={1.5 * scale} />
      </g>
    </g>
  );
}
