"use client";

import CanvasEngine from "./canvas/CanvasEngine";

/**
 * The board — one unified canvas combining the whiteboard and the virtual
 * manipulatives (tray collapsed to a tab by default). Boards saved under
 * the old separate whiteboard / manipulatives keys are folded into the
 * single document on first load.
 */
export default function WhiteboardClient() {
  return <CanvasEngine docKey="pnp.board.v2" />;
}
