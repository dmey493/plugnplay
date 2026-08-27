"use client";

import { useRef, useState } from "react";
import Button from "@/components/ui/Button";
import GraphOfWeekPrintModal from "./GraphOfWeekPrintModal";
import { worksheetUrl, type GotwEntry } from "@/lib/library/gotw";

/** On-screen worksheet preview (the print-ready front/back sheet, embedded)
 *  + a Print action that opens the clean print-preview modal — the same
 *  shape as the stimulus generator's StimulusView. */
export default function GraphOfWeekView({ entry }: { entry: GotwEntry }) {
  const [printing, setPrinting] = useState(false);
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [height, setHeight] = useState(1100);

  // Auto-size to content so the whole two-page worksheet shows inline and the
  // page (not a nested scrollbar) drives scrolling. Same-origin: readable.
  const fitToContent = () => {
    const doc = iframeRef.current?.contentWindow?.document;
    if (doc) setHeight(doc.documentElement.scrollHeight + 24);
  };

  return (
    <div>
      <div className="mb-3 flex justify-end">
        <Button tier="secondary" onClick={() => setPrinting(true)}>
          <span className="inline-flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
              <polyline points="6 9 6 2 18 2 18 9" />
              <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" />
              <rect x="6" y="14" width="12" height="8" />
            </svg>
            Print this graph
          </span>
        </Button>
      </div>

      <div className="overflow-hidden rounded-xl border-2 border-pnp-navy bg-pnp-gray-100 shadow-[4px_4px_0_var(--pnp-navy)]">
        <iframe
          ref={iframeRef}
          src={worksheetUrl(entry.file)}
          title={`Graph of the Week — Week ${entry.week} — ${entry.standard}`}
          onLoad={fitToContent}
          className="block w-full border-0"
          style={{ height }}
        />
      </div>

      {printing && (
        <GraphOfWeekPrintModal entry={entry} onClose={() => setPrinting(false)} />
      )}
    </div>
  );
}
