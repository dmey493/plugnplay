"use client";

import { useState } from "react";
import Button from "@/components/ui/Button";

interface Props {
  taskId: string;
}

type PrintMode = "student" | "teacher" | "both";

/**
 * The action bar at the top of every task detail page.
 *
 * Tier hierarchy (one primary, per design-system spec):
 *   - PRIMARY:   Project    — the in-class moment is the reason to
 *                              open a task. This is the action.
 *   - SECONDARY: Print Both, Student Handout, Teacher Notes — peer
 *                              planning actions.
 *   - TERTIARY:  Copy Link  — low-emphasis utility.
 *
 * Icons are real (lucide-style 16px, stroke 2, currentColor) — no
 * decorative arrows inside filled buttons.
 */
export default function TaskActionBar({ taskId }: Props) {
  const [copied, setCopied] = useState(false);

  const triggerPrint = (mode: PrintMode) => {
    document.body.setAttribute("data-print-mode", mode);
    requestAnimationFrame(() => {
      window.print();
      setTimeout(() => {
        document.body.removeAttribute("data-print-mode");
      }, 100);
    });
  };

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // ignore
    }
  };

  return (
    <div className="no-print sticky top-2 z-30 mb-6 flex flex-wrap items-center gap-2 rounded-xl border border-pnp-gray-200 bg-white/95 p-2 shadow-sm backdrop-blur">
      {/* PRIMARY — the single accent-filled action on this view. */}
      <Button
        tier="primary"
        size="small"
        href={`/math/rich-tasks/${taskId}/project`}
        icon={<ProjectIcon />}
        title="Open in full-screen presentation mode for in-class display"
      >
        Project
      </Button>

      {/* SECONDARY — print actions, peers. Print Both leads the print
          group but stays secondary so it doesn't compete with Project. */}
      <Button
        tier="secondary"
        size="small"
        onClick={() => triggerPrint("both")}
        icon={<PrinterIcon />}
        title="Print everything (student + teacher notes)"
      >
        Print Both
      </Button>
      <Button
        tier="secondary"
        size="small"
        onClick={() => triggerPrint("student")}
        icon={<PrinterIcon />}
        title="Print just the student handout (title, materials, the task)"
      >
        Student Handout
      </Button>
      <Button
        tier="secondary"
        size="small"
        onClick={() => triggerPrint("teacher")}
        icon={<PrinterIcon />}
        title="Print just the teacher notes"
      >
        Teacher Notes
      </Button>

      <div className="ml-auto">
        {/* TERTIARY — quiet utility. */}
        <Button
          tier="tertiary"
          size="small"
          onClick={copyLink}
          icon={<LinkIcon />}
        >
          {copied ? "Copied!" : "Copy link"}
        </Button>
      </div>
    </div>
  );
}

function PrinterIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <polyline points="6 9 6 2 18 2 18 9" />
      <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" />
      <rect x="6" y="14" width="12" height="8" />
    </svg>
  );
}

function ProjectIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="3" y="3" width="18" height="14" rx="2" />
      <line x1="8" y1="21" x2="16" y2="21" />
      <line x1="12" y1="17" x2="12" y2="21" />
    </svg>
  );
}

function LinkIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
      <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
    </svg>
  );
}
