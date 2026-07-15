"use client";

import { useEffect, useRef } from "react";
import type { Item } from "./types";
import { TINTS } from "./constants";

interface Props {
  /** Position in pixels relative to the canvas container. */
  x: number;
  y: number;
  item: Item;
  onFlip: () => void;
  onTint: (tint: string | undefined) => void;
  onDuplicate: () => void;
  onBringToFront: () => void;
  onDelete: () => void;
  onClose: () => void;
}

/** Right-click menu for a piece: flip (counters/algebra), recolour,
 *  duplicate, bring to front, delete. Closes on outside click or Esc. */
export default function ContextMenu({
  x,
  y,
  item,
  onFlip,
  onTint,
  onDuplicate,
  onBringToFront,
  onDelete,
  onClose,
}: Props) {
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const onDown = (e: PointerEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) onClose();
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("pointerdown", onDown, true);
    window.addEventListener("keydown", onKey, true);
    return () => {
      window.removeEventListener("pointerdown", onDown, true);
      window.removeEventListener("keydown", onKey, true);
    };
  }, [onClose]);

  const canFlip = item.kind === "counter" || item.kind === "algebra";
  const flipLabel = item.kind === "counter" ? "Flip color" : "Flip sign";

  const row =
    "flex w-full items-center gap-2 rounded px-2.5 py-1.5 text-left text-sm font-semibold text-pnp-navy hover:bg-pnp-gray-100";

  return (
    <div
      ref={ref}
      role="menu"
      className="absolute z-30 w-44 rounded-lg border-2 border-pnp-navy bg-white p-1.5 shadow-[3px_3px_0_var(--pnp-navy)]"
      style={{ left: x, top: y }}
      // Keep board pointer handlers from seeing clicks inside the menu.
      onPointerDown={(e) => e.stopPropagation()}
      onContextMenu={(e) => e.preventDefault()}
    >
      {canFlip && (
        <button type="button" role="menuitem" className={row} onClick={onFlip}>
          {flipLabel}
        </button>
      )}

      <div className="px-2.5 py-1.5">
        <p className="mb-1 text-[0.65rem] font-bold uppercase tracking-wide text-pnp-gray-600">Color</p>
        <div className="flex flex-wrap gap-1">
          {TINTS.map((t) => (
            <button
              key={t}
              type="button"
              title="Recolor"
              aria-label={`Set color ${t}`}
              onClick={() => onTint(t)}
              className="h-5 w-5 rounded-full border-2 border-pnp-navy transition-transform hover:scale-110"
              style={{ background: t, boxShadow: item.tint === t ? "0 0 0 2px var(--pnp-accent)" : undefined }}
            />
          ))}
          <button
            type="button"
            title="Reset to default color"
            aria-label="Reset color"
            onClick={() => onTint(undefined)}
            className="flex h-5 w-5 items-center justify-center rounded-full border-2 border-dashed border-pnp-gray-400 text-[0.6rem] font-bold text-pnp-gray-600 hover:border-pnp-navy hover:text-pnp-navy"
          >
            ×
          </button>
        </div>
      </div>

      <div className="my-1 border-t border-pnp-gray-200" />

      <button type="button" role="menuitem" className={row} onClick={onDuplicate}>
        Duplicate
      </button>
      <button type="button" role="menuitem" className={row} onClick={onBringToFront}>
        Bring to front
      </button>
      <button
        type="button"
        role="menuitem"
        className="flex w-full items-center gap-2 rounded px-2.5 py-1.5 text-left text-sm font-semibold text-pnp-red hover:bg-pnp-gray-100"
        onClick={onDelete}
      >
        Delete
      </button>
    </div>
  );
}
