import { memo } from "react";
import type { Item } from "./types";
import { itemSize } from "./constants";
import ItemShape from "./ItemShape";

/** A one-shot visual effect on a piece. `sweep` slides the new colour
 *  across the old one; `flip` squashes the piece like a turning coin.
 *  `n` makes each trigger unique so repeat actions restart the animation. */
export interface ItemFx {
  type: "sweep" | "flip";
  n: number;
  /** The item as it looked before the change (sweep renders it underneath). */
  prev: Item;
}

interface Props {
  item: Item;
  selected: boolean;
  /** Live drag offset in world units, applied to selected items mid-drag. */
  dx: number;
  dy: number;
  /** Stroke width for the selection outline (kept constant on screen by
   *  the caller dividing by zoom). */
  outline: number;
  fx?: ItemFx | null;
}

/** One placed piece: the shape wrapped in a positioned/rotated group with
 *  a `data-item-id` hook the board uses for hit-testing. Memoised so an
 *  unrelated piece never re-renders on camera ticks or selection changes. */
function ItemViewImpl({ item, selected, dx, dy, outline, fx }: Props) {
  const { w, h } = itemSize(item);
  const cx = item.x + dx;
  const cy = item.y + dy;

  let shape: React.ReactNode;
  if (fx?.type === "sweep") {
    // Old colour underneath; new colour on top, revealed by a clip rect
    // sliding left-to-right across the piece.
    const clipId = `pnp-sweep-${item.id}-${fx.n}`;
    shape = (
      <>
        <ItemShape item={fx.prev} />
        <clipPath id={clipId}>
          <rect
            className="pnp-sweep-rect"
            x={-w / 2 - 4}
            y={-h / 2 - 4}
            width={w + 8}
            height={h + 8}
            style={{ ["--sweep-w" as string]: `${w + 8}px` }}
          />
        </clipPath>
        <g clipPath={`url(#${clipId})`}>
          <ItemShape item={item} />
        </g>
      </>
    );
  } else if (fx?.type === "flip") {
    // Keyed on the trigger count so a re-flip restarts the animation.
    shape = (
      <g key={fx.n} className="pnp-flip-anim">
        <ItemShape item={item} />
      </g>
    );
  } else {
    shape = <ItemShape item={item} />;
  }

  return (
    <g
      data-item-id={item.id}
      transform={`translate(${cx} ${cy}) rotate(${item.rot})`}
      style={{ cursor: "grab" }}
    >
      {shape}
      {selected && (
        <rect
          x={-w / 2 - 3}
          y={-h / 2 - 3}
          width={w + 6}
          height={h + 6}
          rx={5}
          fill="none"
          stroke="var(--pnp-accent)"
          strokeWidth={outline}
          strokeDasharray={`${outline * 3} ${outline * 2}`}
          pointerEvents="none"
        />
      )}
    </g>
  );
}

export default memo(ItemViewImpl);
