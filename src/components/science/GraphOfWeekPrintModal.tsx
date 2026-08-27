"use client";

import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import Button from "@/components/ui/Button";
import { worksheetUrl, type GotwEntry } from "@/lib/library/gotw";

/**
 * Print preview for one Graph of the Week worksheet. Mirrors the stimulus
 * generator's print modal (StimulusPrintModal): a white "paper" on a gray
 * scroll area, with a toolbar and a Print button. The worksheet itself is a
 * self-contained, print-ready document served from /public, embedded in an
 * iframe — so Print prints the worksheet's own two-page (front/back) layout
 * via its built-in print stylesheet, cleanly isolated from the app chrome.
 */
export default function GraphOfWeekPrintModal({
  entry,
  onClose,
}: {
  entry: GotwEntry;
  onClose: () => void;
}) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [sheetHeight, setSheetHeight] = useState(1100);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  // Auto-size the iframe to its content so the modal's own scroll drives the
  // preview (no nested iframe scrollbar). Same-origin, so this is readable.
  const fitToContent = () => {
    const doc = iframeRef.current?.contentWindow?.document;
    if (doc) setSheetHeight(doc.documentElement.scrollHeight + 24);
  };

  const handlePrint = () => {
    const win = iframeRef.current?.contentWindow;
    if (!win) return;
    win.focus();
    win.print();
  };

  if (typeof document === "undefined") return null;

  return createPortal(
    <div
      onClick={(e) => e.target === e.currentTarget && onClose()}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-3 sm:p-6"
    >
      <div className="flex max-h-[92vh] w-full max-w-4xl flex-col overflow-hidden rounded-xl bg-white shadow-2xl">
        {/* toolbar */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-pnp-gray-200 px-5 py-3">
          <div className="min-w-0">
            <h2 className="font-heading text-base font-bold text-pnp-navy">
              Print preview
            </h2>
            <p className="truncate text-xs text-pnp-gray-500">
              Week {entry.week} · {entry.standard} · {entry.topicTitle}
            </p>
          </div>
          <button
            onClick={onClose}
            aria-label="Close"
            className="rounded-md p-1 text-pnp-gray-500 hover:bg-pnp-gray-100 hover:text-pnp-navy"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* scrolling preview — the white "paper" */}
        <div className="flex-1 overflow-auto bg-pnp-gray-100 p-4 sm:p-6">
          <iframe
            ref={iframeRef}
            src={worksheetUrl(entry.file)}
            title={`Graph of the Week — Week ${entry.week} — ${entry.standard}`}
            onLoad={fitToContent}
            className="mx-auto block w-full max-w-[8.5in] border-0 bg-white"
            style={{ height: sheetHeight }}
          />
        </div>

        {/* footer */}
        <div className="flex items-center justify-end gap-3 border-t border-pnp-gray-200 px-5 py-3">
          <Button tier="tertiary" onClick={onClose}>
            Close
          </Button>
          <Button tier="primary" onClick={handlePrint}>
            Print
          </Button>
        </div>
      </div>
    </div>,
    document.body
  );
}
