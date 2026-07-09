"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { renderBox } from "@/lib/wodb-render";
import type { WodbGrade, WodbSet } from "@/lib/wodb";
import Tag from "@/components/ui/Tag";
import Button from "@/components/ui/Button";

/**
 * WodbBrowse — the "Which One Doesn't Belong?" warm-up browser.
 *
 * Pick a grade, filter by strand / concept / search, click a set to project
 * it full-screen, and reveal teacher notes when ready. The four boxes are
 * rendered from specs by `renderBox`; a per-box seed keeps any generated
 * SVG ids deterministic (SSR-safe) and collision-free.
 */

const LETTERS = ["A", "B", "C", "D"];

function boxSeed(setIndex: number, boxIndex: number, modal = false): number {
  return (setIndex * 4 + boxIndex) * 20 + (modal ? 900_000 : 0);
}

function WodbBoxView({
  grade,
  set,
  setIndex,
  boxIndex,
  mini,
  modal,
}: {
  grade: number;
  set: WodbSet;
  setIndex: number;
  boxIndex: number;
  mini?: boolean;
  modal?: boolean;
}) {
  const html = renderBox(grade, set.quads[boxIndex], boxSeed(setIndex, boxIndex, modal));
  return (
    <div
      className={`wodb-box flex items-center justify-center${mini ? " mini" : ""}`}
      style={{ fontSize: mini ? "15px" : "clamp(20px, 4.4vw, 46px)" }}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}

function BoxGrid({
  grade,
  set,
  setIndex,
  color,
  mini,
  modal,
}: {
  grade: number;
  set: WodbSet;
  setIndex: number;
  color: string;
  mini?: boolean;
  modal?: boolean;
}) {
  return (
    <div className={`grid grid-cols-2 ${mini ? "gap-1.5" : "gap-3 md:gap-4"}`}>
      {[0, 1, 2, 3].map((i) => (
        <div
          key={i}
          className={`relative flex items-center justify-center rounded-lg border-2 border-pnp-navy bg-white ${
            mini ? "aspect-square p-1.5" : "min-h-[26vh] p-3 md:p-5"
          }`}
        >
          {!mini && (
            <span
              className="absolute left-2 top-2 flex h-7 w-7 items-center justify-center rounded-md text-sm font-extrabold text-white md:h-9 md:w-9 md:text-base"
              style={{ backgroundColor: color }}
              aria-hidden="true"
            >
              {LETTERS[i]}
            </span>
          )}
          <WodbBoxView
            grade={grade}
            set={set}
            setIndex={setIndex}
            boxIndex={i}
            mini={mini}
            modal={modal}
          />
        </div>
      ))}
    </div>
  );
}

function SetCard({
  grade,
  set,
  setIndex,
  color,
  strandName,
  onOpen,
}: {
  grade: number;
  set: WodbSet;
  setIndex: number;
  color: string;
  strandName: string;
  onOpen: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onOpen}
      className="group flex h-full flex-col rounded-xl border-2 border-pnp-navy bg-white p-4 text-left shadow-[4px_4px_0_var(--pnp-navy)] transition-transform hover:-translate-y-0.5 hover:shadow-[5px_6px_0_var(--pnp-navy)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2"
      style={{ borderTop: `6px solid ${color}` }}
    >
      <div className="mb-3 flex items-center justify-between gap-2">
        <h3 className="font-heading text-base font-extrabold leading-tight text-pnp-navy">
          {set.title}
        </h3>
        <Tag variant="code">{set.std}</Tag>
      </div>
      <BoxGrid grade={grade} set={set} setIndex={setIndex} color={color} mini />
      <div className="mt-3 flex items-center justify-between gap-2">
        <span
          className="inline-flex items-center gap-1.5 text-xs font-semibold"
          style={{ color }}
        >
          <span
            className="h-2.5 w-2.5 rounded-full"
            style={{ backgroundColor: color }}
            aria-hidden="true"
          />
          {strandName}
        </span>
        <span className="text-xs font-semibold text-pnp-accent opacity-0 transition-opacity group-hover:opacity-100">
          Project →
        </span>
      </div>
    </button>
  );
}

function Projection({
  grade,
  set,
  setIndex,
  color,
  strandName,
  onClose,
}: {
  grade: number;
  set: WodbSet;
  setIndex: number;
  color: string;
  strandName: string;
  onClose: () => void;
}) {
  const [showNotes, setShowNotes] = useState(false);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 overflow-y-auto bg-pnp-navy/70 p-3 md:p-6"
      role="dialog"
      aria-modal="true"
      aria-label={`${set.title} — Which One Doesn't Belong`}
      onClick={onClose}
    >
      <div
        className="pnp-reveal mx-auto max-w-6xl rounded-2xl border-2 border-pnp-navy bg-white p-4 shadow-[6px_6px_0_var(--pnp-navy)] md:p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-2.5">
            <span
              className="inline-flex items-center gap-1.5 rounded-md border-2 border-pnp-navy px-2.5 py-1 text-xs font-bold text-white"
              style={{ backgroundColor: color }}
            >
              {strandName}
            </span>
            <Tag variant="code">{set.std}</Tag>
            <h2 className="font-heading text-lg font-extrabold text-pnp-navy md:text-2xl">
              {set.title}
            </h2>
          </div>
          <Button tier="secondary" size="small" onClick={onClose}>
            Close ✕
          </Button>
        </div>

        <p className="mb-3 text-center font-heading text-base font-bold text-pnp-navy md:text-lg">
          Which one doesn&rsquo;t belong — and why?
        </p>

        <BoxGrid grade={grade} set={set} setIndex={setIndex} color={color} modal />

        <div className="mt-5 border-t-2 border-pnp-gray-100 pt-4">
          {!showNotes ? (
            <Button tier="primary" onClick={() => setShowNotes(true)}>
              Show teacher notes
            </Button>
          ) : (
            <div className="pnp-reveal">
              <p className="text-sm italic text-pnp-gray-600">{set.lead}</p>
              <div className="mt-3 space-y-2">
                {set.args.map((a, i) => (
                  <div key={i} className="flex items-start gap-2.5">
                    <span
                      className="mt-0.5 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-md text-xs font-extrabold text-white"
                      style={{ backgroundColor: color }}
                      aria-hidden="true"
                    >
                      {LETTERS[i]}
                    </span>
                    <span
                      className="text-sm leading-relaxed text-pnp-gray-700"
                      dangerouslySetInnerHTML={{ __html: a }}
                    />
                  </div>
                ))}
              </div>
              {set.prompts.length > 0 && (
                <div className="mt-4">
                  <p className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
                    Discussion prompts
                  </p>
                  <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-pnp-gray-700">
                    {set.prompts.map((p, i) => (
                      <li key={i} dangerouslySetInnerHTML={{ __html: p }} />
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function WodbBrowse({ grades }: { grades: WodbGrade[] }) {
  const [grade, setGrade] = useState<number>(6);
  const [strand, setStrand] = useState<string>("all");
  const [concept, setConcept] = useState<string>("all");
  const [search, setSearch] = useState<string>("");
  const [openId, setOpenId] = useState<string | null>(null);

  // Deep-link from a unit lesson's warm-up strip: ?grade=8&set=<id> opens
  // that set. First render only (mirrors the generator's ?standard= prefill).
  const searchParams = useSearchParams();
  useEffect(() => {
    const gp = Number(searchParams?.get("grade"));
    if (gp >= 6 && gp <= 8) setGrade(gp);
    const setId = searchParams?.get("set");
    if (setId) setOpenId(setId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const data = grades.find((g) => g.grade === grade) ?? grades[0];

  const concepts = useMemo(
    () => [...new Set(data.sets.map((s) => s.concept))].sort(),
    [data],
  );

  const q = search.trim().toLowerCase();
  const filtered = data.sets
    .map((s, i) => ({ s, i })) // keep the stable grade index for seeding
    .filter(({ s }) => {
      if (strand !== "all" && s.strand !== strand) return false;
      if (concept !== "all" && s.concept !== concept) return false;
      if (q && !`${s.title} ${s.concept} ${s.std}`.toLowerCase().includes(q))
        return false;
      return true;
    });

  const openEntry = openId
    ? filtered.find(({ s }) => s.id === openId) ??
      data.sets.map((s, i) => ({ s, i })).find(({ s }) => s.id === openId)
    : null;

  const resetFilters = (g: number) => {
    setGrade(g);
    setStrand("all");
    setConcept("all");
    setSearch("");
    setOpenId(null);
  };

  return (
    <div>
      {/* Grade */}
      <div>
        <span className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
          Grade
        </span>
        <div className="mt-2 flex gap-2" role="radiogroup" aria-label="Grade">
          {grades.map((gr) => {
            const active = gr.grade === grade;
            return (
              <button
                key={gr.grade}
                type="button"
                role="radio"
                aria-checked={active}
                onClick={() => resetFilters(gr.grade)}
                className={`rounded-md border-2 px-5 py-2.5 text-base font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 ${
                  active
                    ? "border-pnp-accent bg-pnp-accent text-white"
                    : "border-pnp-gray-200 bg-white text-pnp-gray-700 hover:border-pnp-gray-400"
                }`}
              >
                {gr.grade}th
              </button>
            );
          })}
        </div>
      </div>

      {/* Strand chips */}
      <div className="mt-5 flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={() => setStrand("all")}
          className={`rounded-md border-2 px-3 py-1.5 text-sm font-semibold transition-colors ${
            strand === "all"
              ? "border-pnp-navy bg-pnp-navy text-white"
              : "border-pnp-gray-200 bg-white text-pnp-gray-700 hover:border-pnp-gray-400"
          }`}
        >
          All strands
        </button>
        {Object.entries(data.strands).map(([key, st]) => {
          const active = strand === key;
          return (
            <button
              key={key}
              type="button"
              onClick={() => setStrand(active ? "all" : key)}
              className="inline-flex items-center gap-1.5 rounded-md border-2 px-3 py-1.5 text-sm font-semibold transition-colors"
              style={
                active
                  ? { backgroundColor: st.color, borderColor: st.color, color: "#fff" }
                  : { borderColor: "var(--pnp-gray-200)", color: "var(--pnp-gray-700)" }
              }
            >
              <span
                className="h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: active ? "#fff" : st.color }}
                aria-hidden="true"
              />
              {st.name}
            </button>
          );
        })}
      </div>

      {/* Concept + search */}
      <div className="mt-4 flex flex-wrap items-center gap-3">
        <select
          value={concept}
          onChange={(e) => setConcept(e.target.value)}
          className="rounded-md border-2 border-pnp-gray-200 bg-white px-3 py-2 text-sm font-medium text-pnp-navy outline-none focus:border-pnp-accent"
          aria-label="Filter by concept"
        >
          <option value="all">All concepts</option>
          {concepts.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
        <input
          type="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search title, concept, or standard…"
          className="min-w-[220px] flex-1 rounded-md border-2 border-pnp-gray-200 bg-white px-3 py-2 text-sm text-pnp-navy outline-none focus:border-pnp-accent"
        />
        <span className="text-sm font-semibold text-pnp-gray-500">
          {filtered.length} set{filtered.length === 1 ? "" : "s"}
        </span>
      </div>

      {/* Grid */}
      {filtered.length === 0 ? (
        <p className="mt-8 rounded-md border-2 border-dashed border-pnp-gray-200 px-4 py-10 text-center text-sm text-pnp-gray-500">
          No sets match that filter. Try clearing the search.
        </p>
      ) : (
        <div className="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map(({ s, i }) => (
            <SetCard
              key={s.id}
              grade={grade}
              set={s}
              setIndex={i}
              color={data.strands[s.strand]?.color ?? "#0d9488"}
              strandName={data.strands[s.strand]?.name ?? s.strand}
              onOpen={() => setOpenId(s.id)}
            />
          ))}
        </div>
      )}

      {openEntry && (
        <Projection
          grade={grade}
          set={openEntry.s}
          setIndex={openEntry.i}
          color={data.strands[openEntry.s.strand]?.color ?? "#0d9488"}
          strandName={data.strands[openEntry.s.strand]?.name ?? openEntry.s.strand}
          onClose={() => setOpenId(null)}
        />
      )}
    </div>
  );
}
