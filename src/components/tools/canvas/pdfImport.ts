"use client";

/**
 * Import helpers for placing PDFs and images on a world-coordinate canvas.
 *
 * Extracted from WhiteboardClient so any canvas tool can rasterise a PDF or
 * measure an image before laying it out as a BackgroundImage. PDF rendering
 * uses pdf.js, dynamically imported on first use so it stays out of the
 * initial bundle.
 */

// Every imported page is laid out this many world units wide; height follows
// the page aspect ratio. Pages stack down the world with GAP between them.
export const WORLD_PAGE_WIDTH = 1000;
export const WORLD_PAGE_GAP = 48;
// Target on-screen crispness for rasterised PDF pages, clamped so huge
// documents don't blow up memory. 1500px wide reads sharp even zoomed in.
const PDF_TARGET_PX = 1500;
const PDF_MIN_SCALE = 1;
const PDF_MAX_SCALE = 3;

export type Raster = { href: string; px: { w: number; h: number } };

/** Read an image file into a data URL and measure its natural size. */
export async function renderImage(file: File): Promise<Raster> {
  const href = await fileToDataURL(file);
  const size = await new Promise<{ w: number; h: number }>((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve({ w: img.naturalWidth, h: img.naturalHeight });
    img.onerror = () => reject(new Error("image decode failed"));
    img.src = href;
  });
  return { href, px: size };
}

/** Rasterise every page of a PDF to a PNG data URL via pdf.js. The library
 *  is imported lazily so it never lands in the initial page bundle. */
export async function renderPdf(file: File): Promise<Raster[]> {
  const pdfjs = await import("pdfjs-dist");
  // Point the worker at the bundled asset. `new URL(..., import.meta.url)`
  // is the bundler-friendly form that Next resolves to a hashed URL.
  pdfjs.GlobalWorkerOptions.workerSrc = new URL(
    "pdfjs-dist/build/pdf.worker.min.mjs",
    import.meta.url
  ).toString();

  const data = await file.arrayBuffer();
  const doc = await pdfjs.getDocument({ data }).promise;
  const out: Raster[] = [];
  try {
    for (let i = 1; i <= doc.numPages; i++) {
      const page = await doc.getPage(i);
      const base = page.getViewport({ scale: 1 });
      const scale = Math.min(
        PDF_MAX_SCALE,
        Math.max(PDF_MIN_SCALE, PDF_TARGET_PX / base.width)
      );
      const viewport = page.getViewport({ scale });
      const canvas = document.createElement("canvas");
      canvas.width = Math.ceil(viewport.width);
      canvas.height = Math.ceil(viewport.height);
      const ctx = canvas.getContext("2d");
      if (!ctx) throw new Error("no 2d context");
      await page.render({ canvasContext: ctx, viewport }).promise;
      out.push({
        href: canvas.toDataURL("image/png"),
        px: { w: canvas.width, h: canvas.height },
      });
      page.cleanup();
    }
  } finally {
    doc.destroy();
  }
  return out;
}

export function fileToDataURL(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = () => reject(reader.error ?? new Error("read failed"));
    reader.readAsDataURL(file);
  });
}
