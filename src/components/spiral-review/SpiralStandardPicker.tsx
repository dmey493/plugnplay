"use client";

import { getStandardsByDomain } from "@/lib/standards/standards";
import type { GradeCheckpoints } from "@/lib/standards/checkpoints";
import { currentCheckpointId, type SpiralPick } from "@/lib/generators/spiral-review";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Tag from "@/components/ui/Tag";

/**
 * SpiralStandardPicker — choose several standards for a spiral review sheet.
 *
 * Two lenses on the grade's standards:
 *   - By checkpoint: the ILEARN checkpoint windows and the standards each one
 *     assesses, plus the summative-only group. Each window has "Add all",
 *     which adds its standards at 1 problem each until the sheet is full.
 *   - Essential standards: only the standards IDOE marks Essential, grouped
 *     by strand, each tagged with the checkpoint that assesses it.
 *
 * Multi-select: a card toggles its standard on and off. The sheet holds 8
 * problems, so once it is full the unpicked cards are disabled with a note
 * saying how to make room.
 */

export type PickerTab = "checkpoint" | "essential";

const GRADES = [6, 7, 8] as const;

const TABS: { id: PickerTab; label: string }[] = [
  { id: "checkpoint", label: "By checkpoint" },
  { id: "essential", label: "Essential standards" },
];

interface Props {
  grade: number;
  onGradeChange: (grade: number) => void;
  tab: PickerTab;
  onTabChange: (tab: PickerTab) => void;
  checkpoints?: GradeCheckpoints;
  picks: SpiralPick[];
  full: boolean;
  onToggle: (code: string) => void;
  onAddAll: (codes: string[]) => void;
  /** Result of the last "Add all", e.g. "Added 5. The sheet is full." */
  note?: string | null;
}

function CheckIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M20 6 9 17l-5-5" />
    </svg>
  );
}

function StandardCard({
  code,
  text,
  pick,
  disabled,
  essential,
  footnote,
  dashed,
  onToggle,
}: {
  code: string;
  text: string;
  pick?: SpiralPick;
  disabled: boolean;
  essential: boolean;
  footnote?: string;
  dashed?: boolean;
  onToggle: (code: string) => void;
}) {
  const selected = Boolean(pick);
  return (
    <button
      type="button"
      aria-pressed={selected}
      disabled={disabled}
      onClick={() => onToggle(code)}
      className={`flex flex-col rounded-md border-2 p-3 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 ${
        dashed ? "border-dashed" : ""
      } ${
        selected
          ? "border-pnp-accent bg-pnp-accent-soft"
          : disabled
            ? "cursor-not-allowed border-pnp-gray-200 bg-pnp-gray-50 opacity-60"
            : "border-pnp-gray-200 bg-white hover:border-pnp-accent"
      }`}
    >
      <span className="flex items-center justify-between gap-2">
        <span className="font-heading text-sm font-bold text-pnp-navy">{code}</span>
        {pick && (
          <span className="inline-flex items-center gap-1 text-xs font-bold text-pnp-accent-press">
            <CheckIcon />
            {pick.count === 2 ? "2 problems" : "1 problem"}
          </span>
        )}
      </span>
      <span className="mt-0.5 text-xs leading-snug text-pnp-gray-600">{text}</span>
      {(essential || footnote) && (
        <span className="mt-1.5 flex flex-wrap items-center gap-1.5">
          {essential && (
            <span
              className={`rounded px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide text-pnp-accent-press ${
                selected ? "bg-white" : "bg-pnp-accent-soft"
              }`}
            >
              Essential
            </span>
          )}
          {footnote && (
            <span className="text-[10px] font-semibold text-pnp-gray-500">{footnote}</span>
          )}
        </span>
      )}
    </button>
  );
}

export default function SpiralStandardPicker({
  grade,
  onGradeChange,
  tab,
  onTabChange,
  checkpoints,
  picks,
  full,
  onToggle,
  onAddAll,
  note,
}: Props) {
  const domainGroups = getStandardsByDomain(grade);
  const byCode = new Map(
    Object.values(domainGroups).flat().map((st) => [st.code, st])
  );
  const pickByCode = new Map(picks.map((p) => [p.code, p]));
  const isEssential = (code: string) =>
    checkpoints?.standards[code]?.priority === "Essential";
  const nowId = checkpoints ? currentCheckpointId(checkpoints.checkpoints) : null;

  const summativeOnly = checkpoints
    ? Object.values(checkpoints.standards)
        .filter((st) => st.checkpoints.length === 0)
        .map((st) => st.code)
        .sort((a, b) => a.localeCompare(b, undefined, { numeric: true }))
    : [];

  const checkpointLabel = (code: string) => {
    const ids = checkpoints?.standards[code]?.checkpoints ?? [];
    if (ids.length === 0) return "Summative only";
    return ids
      .map((id) => checkpoints?.checkpoints.find((cp) => cp.id === id)?.label ?? id)
      .join(", ");
  };

  const card = (code: string, extra?: { footnote?: string; dashed?: boolean }) => {
    const pick = pickByCode.get(code);
    return (
      <StandardCard
        key={code}
        code={code}
        text={byCode.get(code)?.text ?? ""}
        pick={pick}
        disabled={!pick && full}
        essential={isEssential(code)}
        footnote={extra?.footnote}
        dashed={extra?.dashed}
        onToggle={onToggle}
      />
    );
  };

  const groupHeader = (
    id: string,
    title: string,
    meta: string,
    codes: string[],
    now = false
  ) => {
    const missing = codes.filter((c) => !pickByCode.has(c));
    return (
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <h3 id={id} className="font-heading text-sm font-extrabold text-pnp-navy">
            {title}
          </h3>
          {now && <Badge tone="teal">Now</Badge>}
          <span className="text-xs text-pnp-gray-500">{meta}</span>
        </div>
        <Button
          tier="tertiary"
          size="small"
          disabled={missing.length === 0 || full}
          onClick={() => onAddAll(codes)}
          aria-label={`Add all ${title} standards`}
        >
          Add all
        </Button>
      </div>
    );
  };

  const essentialGroups = Object.entries(domainGroups)
    .map(([domainName, standards]) => ({
      domainName,
      domain: standards[0]?.domain,
      codes: standards.map((s) => s.code).filter(isEssential),
    }))
    .filter((g) => g.codes.length > 0);

  return (
    <div>
      {/* Grade */}
      <div>
        <span className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
          Grade
        </span>
        <div className="mt-2 flex gap-2" role="radiogroup" aria-label="Grade">
          {GRADES.map((g) => {
            const active = grade === g;
            return (
              <button
                key={g}
                type="button"
                role="radio"
                aria-checked={active}
                onClick={() => onGradeChange(g)}
                className={`rounded-md border-2 px-5 py-2.5 text-base font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 ${
                  active
                    ? "border-pnp-accent bg-pnp-accent text-white"
                    : "border-pnp-gray-200 bg-white text-pnp-gray-700 hover:border-pnp-gray-400"
                }`}
              >
                {g}th
              </button>
            );
          })}
        </div>
      </div>

      {/* Standards */}
      <div className="mt-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <span className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
            Standards
          </span>
          <div
            role="tablist"
            aria-label="Choose how to find standards"
            className="inline-flex items-center gap-1 rounded-lg border border-pnp-gray-200 bg-white p-1"
          >
            {TABS.map((t) => {
              const active = tab === t.id;
              return (
                <button
                  key={t.id}
                  id={`spiral-tab-${t.id}`}
                  type="button"
                  role="tab"
                  aria-selected={active}
                  aria-controls="spiral-tabpanel"
                  onClick={() => onTabChange(t.id)}
                  className={`inline-flex h-8 select-none items-center rounded-md px-3 text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 ${
                    active ? "bg-pnp-accent text-white" : "text-pnp-gray-700 hover:bg-pnp-gray-100"
                  }`}
                >
                  {t.label}
                </button>
              );
            })}
          </div>
        </div>

        <div role="status" aria-live="polite" className="mt-3 min-h-[1.25rem] text-sm">
          {full ? (
            <span className="font-semibold text-pnp-navy">
              The sheet is full: 8 of 8 problems. Remove a standard, or set one to
              1 problem, to add another.
            </span>
          ) : note ? (
            <span className="font-semibold text-pnp-accent-press">{note}</span>
          ) : null}
        </div>

        <div
          id="spiral-tabpanel"
          role="tabpanel"
          aria-labelledby={`spiral-tab-${tab}`}
          className="mt-2"
        >
          {!checkpoints ? (
            <p className="rounded-md border-2 border-dashed border-pnp-gray-200 px-4 py-6 text-center text-sm text-pnp-gray-500">
              There is no checkpoint map for grade {grade} yet.
            </p>
          ) : tab === "checkpoint" ? (
            <div className="space-y-6">
              {checkpoints.checkpoints.map((cp) => (
                <section key={cp.id} aria-labelledby={`spiral-${cp.id}`}>
                  {groupHeader(
                    `spiral-${cp.id}`,
                    cp.label,
                    `${cp.window} · ${cp.standards.length} standards`,
                    cp.standards,
                    cp.id === nowId
                  )}
                  <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
                    {cp.standards.map((code) => card(code))}
                  </div>
                </section>
              ))}
              {summativeOnly.length > 0 && (
                <section aria-labelledby="spiral-summative">
                  {groupHeader(
                    "spiral-summative",
                    "Summative only",
                    `${checkpoints.summativeWindow} · on no checkpoint`,
                    summativeOnly
                  )}
                  <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
                    {summativeOnly.map((code) => card(code, { dashed: true }))}
                  </div>
                </section>
              )}
            </div>
          ) : (
            <div className="space-y-6">
              {essentialGroups.map((g) => (
                <section key={g.domainName} aria-label={g.domainName}>
                  <div className="mb-2 flex items-center gap-2">
                    {g.domain && <Tag variant="code">{g.domain}</Tag>}
                    <h3 className="font-heading text-sm font-extrabold text-pnp-navy">
                      {g.domainName}
                    </h3>
                  </div>
                  <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
                    {g.codes.map((code) => card(code, { footnote: checkpointLabel(code) }))}
                  </div>
                </section>
              ))}
              <p className="text-xs leading-snug text-pnp-gray-500">
                Essential standards are the ones IDOE marks Essential in the
                Indiana Assessment Framework.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
