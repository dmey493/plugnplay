/**
 * Print-to-PDF export for the canvas board.
 *
 * Zero-dependency: clones the live world <g> (same document, so CSS
 * variables, fonts and KaTeX styles all still resolve) into a hidden
 * print-only container — one standalone <svg> per output page — then opens
 * the browser print dialog, where "Save as PDF" is built into Chrome/Edge.
 * Vector all the way down: ink, shapes and text stay crisp at any size.
 *
 * Page selection: with imported PDF/image pages on the board, each page
 * rect becomes its own print page (annotations included, neighbours
 * clipped by the viewBox); board content outside every imported page gets
 * one extra trailing page. With no imports, the whole board's content
 * bounds go on a single page, landscape or portrait by aspect.
 */

import type { Item } from "../manipulatives/types";
import type { Stroke } from "./ink";
import type { BackgroundImage } from "./types";
import { pointsToList, TEXT_FONT_WORLD } from "./ink";
import { itemSize, rotatedHalfExtent } from "../manipulatives/constants";

export interface WorldRect {
  x: number;
  y: number;
  width: number;
  height: number;
}

const PAD = 24; // world-unit margin around fitted content

type Extent = { x1: number; y1: number; x2: number; y2: number };

function itemExtent(i: Item): Extent {
  const { w, h } = rotatedHalfExtent(itemSize(i), i.rot);
  return { x1: i.x - w, y1: i.y - h, x2: i.x + w, y2: i.y + h };
}

function strokeExtent(s: Stroke): Extent | null {
  const pts = pointsToList(s.points);
  if (pts.length === 0) return null;
  if (s.kind === "text") {
    // Mirror the on-canvas hit-rect approximation from font metrics.
    const [pt] = pts;
    const fs = s.fontSize ?? TEXT_FONT_WORLD;
    const w = Math.max(fs, (s.text?.length ?? 1) * fs * 0.6);
    return { x1: pt[0], y1: pt[1], x2: pt[0] + w, y2: pt[1] + fs * 1.3 };
  }
  let x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity;
  for (const [x, y] of pts) {
    x1 = Math.min(x1, x);
    y1 = Math.min(y1, y);
    x2 = Math.max(x2, x);
    y2 = Math.max(y2, y);
  }
  const r = s.width / 2;
  return { x1: x1 - r, y1: y1 - r, x2: x2 + r, y2: y2 + r };
}

function boundsOf(extents: Extent[], pad: number): WorldRect | null {
  if (extents.length === 0) return null;
  let x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity;
  for (const e of extents) {
    x1 = Math.min(x1, e.x1);
    y1 = Math.min(y1, e.y1);
    x2 = Math.max(x2, e.x2);
    y2 = Math.max(y2, e.y2);
  }
  return { x: x1 - pad, y: y1 - pad, width: x2 - x1 + 2 * pad, height: y2 - y1 + 2 * pad };
}

/** The world rects to print, in page order. Empty array = nothing to export. */
export function exportRects(items: Item[], strokes: Stroke[], pages: BackgroundImage[]): WorldRect[] {
  const extents: Extent[] = [
    ...items.map(itemExtent),
    ...strokes.map(strokeExtent).filter((e): e is Extent => e !== null),
  ];

  if (pages.length === 0) {
    const b = boundsOf(extents, PAD);
    return b ? [b] : [];
  }

  // One print page per imported page; anything whose centre lies outside
  // every imported page (side work, parking-lot notes) gets a final page.
  const rects: WorldRect[] = pages.map((p) => ({ x: p.x, y: p.y, width: p.width, height: p.height }));
  const onAPage = (e: Extent) => {
    const cx = (e.x1 + e.x2) / 2;
    const cy = (e.y1 + e.y2) / 2;
    return rects.some((r) => cx >= r.x && cx <= r.x + r.width && cy >= r.y && cy <= r.y + r.height);
  };
  const overflow = boundsOf(extents.filter((e) => !onAPage(e)), PAD);
  if (overflow) rects.push(overflow);
  return rects;
}

// US letter with 0.4in margins → printable area in inches.
const PRINT_LONG = 10.2;
const PRINT_SHORT = 7.7;

/**
 * Build the hidden print pages from the live scene group and open the
 * print dialog. The container removes itself after printing.
 */
export function printBoardToPdf(sceneEl: SVGGElement, rects: WorldRect[]): void {
  if (rects.length === 0) return;

  // Orientation from the first page's aspect; one orientation per document
  // (mixed @page orientations are unreliable across browsers).
  const landscape = rects[0].width >= rects[0].height;
  const availW = landscape ? PRINT_LONG : PRINT_SHORT;
  const availH = landscape ? PRINT_SHORT : PRINT_LONG;

  const root = document.createElement("div");
  root.className = "pnp-print-root";

  const style = document.createElement("style");
  style.textContent = `
    .pnp-print-root { display: none; }
    @media print {
      body > *:not(.pnp-print-root) { display: none !important; }
      .pnp-print-root { display: block !important; }
      .pnp-print-page { break-after: page; text-align: center; }
      .pnp-print-page:last-child { break-after: auto; }
      @page { size: letter ${landscape ? "landscape" : "portrait"}; margin: 0.4in; }
    }
  `;
  root.appendChild(style);

  const SVG_NS = "http://www.w3.org/2000/svg";
  for (const r of rects) {
    const scale = Math.min(availW / r.width, availH / r.height);
    const svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("viewBox", `${r.x} ${r.y} ${r.width} ${r.height}`);
    svg.setAttribute("width", `${(r.width * scale).toFixed(3)}in`);
    svg.setAttribute("height", `${(r.height * scale).toFixed(3)}in`);
    const clone = sceneEl.cloneNode(true) as SVGGElement;
    clone.removeAttribute("transform"); // drop the camera; viewBox frames the page
    svg.appendChild(clone);
    const page = document.createElement("div");
    page.className = "pnp-print-page";
    page.appendChild(svg);
    root.appendChild(page);
  }

  document.body.appendChild(root);

  let done = false;
  const cleanup = () => {
    if (done) return;
    done = true;
    root.remove();
  };
  window.addEventListener("afterprint", cleanup, { once: true });
  window.print();
  // Fallback for browsers where print() returns without firing afterprint.
  setTimeout(cleanup, 2000);
}
