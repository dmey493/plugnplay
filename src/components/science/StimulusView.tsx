"use client";

import { useState } from "react";
import Button from "@/components/ui/Button";
import StimulusCard from "./StimulusCard";
import StimulusPrintModal from "./StimulusPrintModal";
import type { Stimulus } from "@/lib/library/science";

/** On-screen stimulus (interactive card) + a Print action that opens the
 *  clean print-preview modal. */
export default function StimulusView({
  stimulus,
  pe,
  peText,
  index,
  accent,
}: {
  stimulus: Stimulus;
  pe: string;
  peText: string;
  index: number;
  accent: string;
}) {
  const [printing, setPrinting] = useState(false);
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
            Print this stimulus
          </span>
        </Button>
      </div>
      <StimulusCard stimulus={stimulus} index={index} accent={accent} />
      {printing && (
        <StimulusPrintModal
          stimulus={stimulus}
          pe={pe}
          peText={peText}
          onClose={() => setPrinting(false)}
        />
      )}
    </div>
  );
}
