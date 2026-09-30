"use client";

import { useCallback, useEffect, useState } from "react";
import type { CheckpointNav } from "@/lib/standards/checkpoints";
import type { ProficiencyLevel } from "@/lib/standards/plds";
import {
  DEFAULT_LEVEL,
  EMPTY_SETUP,
  MAX_PROBLEMS,
  MAX_START_WEEK,
  MAX_WEEKS,
  decodeSetParams,
  encodeSetParams,
  isEngineError,
  loadSaved,
  problemCount,
  saveSaved,
  setupSignature,
  type GradeSetup,
  type SpiralPlan,
} from "@/lib/generators/spiral-review";
import Button from "@/components/ui/Button";
import SheetPanel from "./SheetPanel";
import SpiralReviewPanel from "./SpiralReviewPanel";
import SpiralStandardPicker, { type PickerTab } from "./SpiralStandardPicker";

/**
 * SpiralReviewBuilder — the /math/spiral-review page body.
 *
 * Left: the standard picker (grade, By checkpoint / Essential standards).
 * Right: "Your sheet", sticky on wide screens, with the one Build button.
 * Build opens the review panel, where the teacher swaps problems and prints.
 *
 * Each grade keeps its own set, so switching grades never loses work. The
 * sets are remembered in this browser, and the next visit starts at the week
 * after the last download, which makes the weekly routine: open, Build,
 * Download. A shared link (?grade=&set=) loads someone else's set instead.
 */

type LinkState = "idle" | "copied" | "failed";

const BUILD_FAILED = "The sheet could not be built. Check your connection and try again.";

export default function SpiralReviewBuilder({
  checkpointNav,
}: {
  checkpointNav: CheckpointNav;
}) {
  const [mounted, setMounted] = useState(false);
  const [grade, setGrade] = useState(6);
  const [byGrade, setByGrade] = useState<Record<string, GradeSetup>>({});
  const [lastDownloaded, setLastDownloaded] = useState<Record<string, number>>({});
  const [tab, setTab] = useState<PickerTab>("checkpoint");
  const [restoredNote, setRestoredNote] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);
  const [linkState, setLinkState] = useState<LinkState>("idle");

  const [plan, setPlan] = useState<SpiralPlan | null>(null);
  const [planSig, setPlanSig] = useState<string | null>(null);
  const [reviewOpen, setReviewOpen] = useState(false);
  const [building, setBuilding] = useState(false);
  const [newSetBusy, setNewSetBusy] = useState(false);
  const [buildError, setBuildError] = useState<string | null>(null);

  const setup = byGrade[grade] ?? EMPTY_SETUP;
  const total = problemCount(setup.picks);
  const full = total >= MAX_PROBLEMS;
  const resumable = plan !== null && planSig === setupSignature(grade, setup);

  // ── Restore: a shared link wins over this browser's saved sets ──────────
  useEffect(() => {
    const saved = loadSaved();
    const fromLink = decodeSetParams(new URLSearchParams(window.location.search));
    const last = saved?.lastDownloadedWeek ?? {};
    let nextGrade = saved?.grade ?? 6;
    let nextByGrade: Record<string, GradeSetup> = { ...(saved?.byGrade ?? {}) };
    let message: string | null = null;

    // Pick up the week after the last download.
    for (const [g, s] of Object.entries(nextByGrade)) {
      const after = (last[g] ?? 0) + 1;
      if (s.picks.length && after > s.startWeek && after <= MAX_START_WEEK) {
        nextByGrade[g] = { ...s, startWeek: after };
        if (Number(g) === nextGrade) {
          message = `Restored your last set, starting at Week ${after}, after your last download.`;
        }
      }
    }
    if (fromLink) {
      nextGrade = fromLink.grade;
      nextByGrade = { ...nextByGrade, [fromLink.grade]: fromLink.setup };
      message = "Loaded the set from your link.";
      window.history.replaceState(null, "", window.location.pathname);
    } else if (!message && nextByGrade[nextGrade]?.picks.length) {
      message = "Restored your last set.";
    }

    // localStorage and the URL exist only in the browser, so the saved set is
    // read after hydration (reading it during render would mismatch the
    // server HTML). This runs once, on mount.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setGrade(nextGrade);
    setByGrade(nextByGrade);
    setLastDownloaded(last);
    setRestoredNote(message);
    setMounted(true);
  }, []);

  // ── Autosave ────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!mounted) return;
    saveSaved({ grade, byGrade, lastDownloadedWeek: lastDownloaded });
  }, [mounted, grade, byGrade, lastDownloaded]);

  // ── Set edits (always the current grade) ────────────────────────────────
  const update = (fn: (s: GradeSetup) => GradeSetup) =>
    setByGrade((prev) => ({ ...prev, [grade]: fn(prev[grade] ?? EMPTY_SETUP) }));

  const toggle = (code: string) => {
    setNote(null);
    update((s) => {
      if (s.picks.some((p) => p.code === code)) {
        return { ...s, picks: s.picks.filter((p) => p.code !== code) };
      }
      if (problemCount(s.picks) >= MAX_PROBLEMS) return s;
      return { ...s, picks: [...s.picks, { code, count: 1, level: DEFAULT_LEVEL }] };
    });
  };

  const addAll = (codes: string[]) => {
    const picked = new Set(setup.picks.map((p) => p.code));
    const missing = codes.filter((c) => !picked.has(c));
    const room = MAX_PROBLEMS - total;
    const adding = missing.slice(0, room);
    if (adding.length === 0) return;
    update((s) => ({
      ...s,
      picks: [
        ...s.picks,
        ...adding.map((code) => ({ code, count: 1 as const, level: DEFAULT_LEVEL })),
      ],
    }));
    const left = missing.length - adding.length;
    setNote(
      left > 0
        ? `Added ${adding.length}. The sheet is full, so ${left} more did not fit.`
        : `Added ${adding.length} ${adding.length === 1 ? "standard" : "standards"} at 1 problem each.`
    );
  };

  const setCount = (code: string, count: 1 | 2) =>
    update((s) => {
      const others = problemCount(s.picks.filter((p) => p.code !== code));
      if (others + count > MAX_PROBLEMS) return s;
      return { ...s, picks: s.picks.map((p) => (p.code === code ? { ...p, count } : p)) };
    });

  const setLevel = (code: string, level: ProficiencyLevel) =>
    update((s) => ({
      ...s,
      picks: s.picks.map((p) => (p.code === code ? { ...p, level } : p)),
    }));

  const remove = (code: string) => {
    setNote(null);
    update((s) => ({ ...s, picks: s.picks.filter((p) => p.code !== code) }));
  };

  const startOver = () => {
    update(() => EMPTY_SETUP);
    setRestoredNote(null);
    setNote(null);
  };

  const changeGrade = (g: number) => {
    setGrade(g);
    setNote(null);
    setRestoredNote(null);
  };

  // ── Build ───────────────────────────────────────────────────────────────
  const requestPlan = async (): Promise<SpiralPlan | string> => {
    try {
      const res = await fetch("/api/spiral-generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          grade,
          weeks: setup.weeks,
          start_week: setup.startWeek,
          standards: setup.picks.map((p) => ({ code: p.code, level: p.level, count: p.count })),
        }),
      });
      const data = await res.json();
      if (!res.ok || isEngineError(data)) return data?.message ?? BUILD_FAILED;
      return data as SpiralPlan;
    } catch {
      return BUILD_FAILED;
    }
  };

  const build = async () => {
    setBuilding(true);
    setBuildError(null);
    const result = await requestPlan();
    setBuilding(false);
    if (typeof result === "string") {
      setBuildError(result);
      return;
    }
    setPlan(result);
    setPlanSig(setupSignature(grade, setup));
    setReviewOpen(true);
  };

  const newSet = async () => {
    setNewSetBusy(true);
    const result = await requestPlan();
    setNewSetBusy(false);
    if (typeof result === "string") return result;
    setPlan(result);
    setPlanSig(setupSignature(grade, setup));
    return null;
  };

  const updatePlan = useCallback(
    (fn: (p: SpiralPlan) => SpiralPlan) => setPlan((p) => (p ? fn(p) : p)),
    []
  );
  const closeReview = useCallback(() => setReviewOpen(false), []);

  const downloaded = useCallback(
    (weeks: number[]) => {
      if (!plan || weeks.length === 0) return;
      const g = String(plan.grade);
      const top = Math.max(...weeks);
      setLastDownloaded((prev) => ({ ...prev, [g]: Math.max(prev[g] ?? 0, top) }));
    },
    [plan]
  );

  const copyLink = async () => {
    const url = `${window.location.origin}${window.location.pathname}?${encodeSetParams(grade, setup)}`;
    try {
      await navigator.clipboard.writeText(url);
      setLinkState("copied");
    } catch {
      setLinkState("failed");
    }
    setTimeout(() => setLinkState("idle"), 2500);
  };

  return (
    <div className="pb-24 lg:pb-0">
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_400px] lg:items-start">
        <div className="rounded-xl border-2 border-pnp-navy bg-white p-6 shadow-[4px_4px_0_var(--pnp-navy)] md:p-8">
          <SpiralStandardPicker
            grade={grade}
            onGradeChange={changeGrade}
            tab={tab}
            onTabChange={setTab}
            checkpoints={checkpointNav[grade]}
            picks={setup.picks}
            full={full}
            onToggle={toggle}
            onAddAll={addAll}
            note={note}
          />
        </div>

        <aside
          id="spiral-sheet"
          aria-label="Your sheet"
          className="scroll-mt-6 lg:sticky lg:top-6 lg:max-h-[calc(100vh-3rem)] lg:overflow-y-auto lg:pb-2 lg:pr-2"
        >
          <SheetPanel
            grade={grade}
            setup={setup}
            onCount={setCount}
            onLevel={setLevel}
            onRemove={remove}
            onWeeks={(n) => update((s) => ({ ...s, weeks: Math.min(MAX_WEEKS, Math.max(1, n)) }))}
            onStartWeek={(n) => update((s) => ({ ...s, startWeek: n }))}
            onBuild={build}
            building={building}
            buildError={buildError}
            onResume={resumable ? () => setReviewOpen(true) : undefined}
            onCopyLink={copyLink}
            linkState={linkState}
            restoredNote={restoredNote}
            onStartOver={restoredNote ? startOver : undefined}
          />
        </aside>
      </div>

      {/* Small screens: the sheet panel sits below a long list, so keep its
          count and a way to reach it in view. */}
      <div className="fixed inset-x-0 bottom-0 z-40 flex items-center justify-between gap-3 border-t-2 border-pnp-navy bg-white px-4 py-3 lg:hidden">
        <span className="text-sm font-semibold text-pnp-navy">
          {total} of {MAX_PROBLEMS} problems
        </span>
        <Button
          tier="secondary"
          size="small"
          onClick={() =>
            document.getElementById("spiral-sheet")?.scrollIntoView({ behavior: "smooth" })
          }
        >
          Go to your sheet
        </Button>
      </div>

      {plan && reviewOpen && (
        <SpiralReviewPanel
          plan={plan}
          onPlanChange={updatePlan}
          onClose={closeReview}
          onNewSet={newSet}
          newSetBusy={newSetBusy}
          onDownloaded={downloaded}
        />
      )}
    </div>
  );
}
