"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Button from "@/components/ui/Button";
import DrawingOverlay from "@/components/intervention/DrawingOverlay";

/**
 * Full-screen digital whiteboard for the Math Tools section.
 *
 * Reuses the projection-mode DrawingOverlay (pen / highlighter / eraser /
 * color picker / undo / clear), pinned in always-active state on top of a
 * blank white canvas. Hides the site header/footer via the existing
 * `project-mode` body class so the whole viewport is a drawing surface.
 *
 * The `wipeKey` is owned here so the Clear button can bump it and wipe the
 * strokes without piping anything into DrawingOverlay's internals.
 */
export default function WhiteboardClient() {
  // active is always true for the standalone tool — there's nothing
  // underneath the canvas to "uncover," so we never let it turn off.
  const [active, setActive] = useState(true);
  // Bumping this number from the Clear button triggers DrawingOverlay's
  // wipe effect via the prop. Strings concatenated so the prop type matches.
  const [wipeBump, setWipeBump] = useState(0);

  // Hide the site header/footer for the duration of this page.
  useEffect(() => {
    document.body.classList.add("project-mode");
    return () => {
      document.body.classList.remove("project-mode");
    };
  }, []);

  // Standalone mode: ignore attempts to deactivate (e.g. the palette's Done
  // button) — the canvas should always be drawable.
  const noopSetActive = () => setActive(true);

  return (
    <div className="fixed inset-0 flex h-screen w-screen flex-col bg-white text-pnp-gray-900">
      {/* Minimal top bar: back link on the left, clear on the right. */}
      <div className="relative z-[260] flex shrink-0 items-center justify-between border-b border-pnp-gray-200 bg-white/95 px-4 py-2 backdrop-blur">
        <Link
          href="/math"
          className="inline-flex items-center gap-1.5 rounded-md px-2 py-1.5 text-sm font-semibold text-pnp-gray-700 transition-colors hover:bg-pnp-gray-100"
        >
          <svg
            width="16" height="16" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          Back to Math
        </Link>

        <div className="flex items-center gap-2 text-sm">
          <span className="hidden text-pnp-gray-500 md:inline">
            Pen • Highlighter • Eraser &middot; <kbd className="rounded border border-pnp-gray-300 bg-pnp-gray-50 px-1 text-[0.7rem] font-mono">Space</kbd>+drag to pan &middot; <kbd className="rounded border border-pnp-gray-300 bg-pnp-gray-50 px-1 text-[0.7rem] font-mono">Ctrl</kbd>+wheel to zoom
          </span>
          <Button
            tier="secondary"
            size="small"
            onClick={() => setWipeBump((n) => n + 1)}
            title="Wipe the board"
          >
            Clear board
          </Button>
        </div>
      </div>

      {/* Empty canvas area. The overlay's fixed SVG covers this region. */}
      <div className="relative flex-1" aria-label="Whiteboard canvas" />

      <DrawingOverlay
        active={active}
        setActive={noopSetActive}
        wipeKey={`whiteboard-${wipeBump}`}
        infinite
      />
    </div>
  );
}
