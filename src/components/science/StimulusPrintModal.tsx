"use client";

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import Button from "@/components/ui/Button";
import PrintSheet from "./PrintSheet";
import type { Stimulus } from "@/lib/science";

/**
 * Print preview for one stimulus. Shows the clean, worksheet-formatted sheet
 * (PrintSheet) inside a modal with an "answer key" toggle; the Print button
 * prints only that sheet. Rendered via a portal to <body> so the print
 * stylesheet can isolate it cleanly.
 */
export default function StimulusPrintModal({
  stimulus,
  pe,
  peText,
  onClose,
}: {
  stimulus: Stimulus;
  pe: string;
  peText: string;
  onClose: () => void;
}) {
  const [showAnswers, setShowAnswers] = useState(false);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const handlePrint = () => {
    document.body.classList.add("printing-sheet");
    const cleanup = () => {
      document.body.classList.remove("printing-sheet");
      window.removeEventListener("afterprint", cleanup);
    };
    window.addEventListener("afterprint", cleanup);
    window.print();
  };

  if (typeof document === "undefined") return null;

  return createPortal(
    <div className="stimulus-print-portal">
      <div
        onClick={(e) => e.target === e.currentTarget && onClose()}
        className="print-overlay fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-3 sm:p-6"
      >
        <div className="print-modal flex max-h-[92vh] w-full max-w-3xl flex-col overflow-hidden rounded-xl bg-white shadow-2xl">
          {/* toolbar */}
          <div
            data-no-print
            className="flex flex-wrap items-center justify-between gap-3 border-b border-pnp-gray-200 px-5 py-3"
          >
            <h2 className="font-heading text-base font-bold text-pnp-navy">
              Print preview
            </h2>
            <div className="flex items-center gap-4">
              <label className="flex cursor-pointer items-center gap-2 text-sm font-medium text-pnp-gray-700">
                <input
                  type="checkbox"
                  checked={showAnswers}
                  onChange={(e) => setShowAnswers(e.target.checked)}
                  className="h-4 w-4 accent-pnp-accent"
                />
                Include answer key
              </label>
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
          </div>

          {/* scrolling preview — the white "paper" */}
          <div className="print-scroll flex-1 overflow-auto bg-pnp-gray-100 p-4 sm:p-8">
            <div className="sheet-frame mx-auto w-full max-w-[7.7in] bg-white p-[0.45in] shadow-[0_1px_8px_rgba(0,0,0,0.15)]">
              <PrintSheet
                stimulus={stimulus}
                pe={pe}
                peText={peText}
                showAnswers={showAnswers}
              />
            </div>
          </div>

          {/* footer */}
          <div
            data-no-print
            className="flex items-center justify-end gap-3 border-t border-pnp-gray-200 px-5 py-3"
          >
            <Button tier="tertiary" onClick={onClose}>
              Close
            </Button>
            <Button tier="primary" onClick={handlePrint}>
              Print
            </Button>
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
}
