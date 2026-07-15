"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import type { NumberTalk, NumberTalkGrade } from "@/lib/number-talks";
import Tag from "@/components/ui/Tag";
import Button from "@/components/ui/Button";
import GroupsButton from "@/components/groups/GroupsButton";

/**
 * NumberTalksBrowse — browse + project short mental-math warm-ups.
 *
 * Pick a grade, filter by strand / concept / search, open a talk to project
 * it. String/estimation talks reveal their problems one at a time (the
 * "string" builds on screen); image talks show a quick image. Teacher notes
 * (target strategy, likely thinking, what to record, talk moves, answer key)
 * are tucked behind a reveal.
 */

function Html({ html, className }: { html: string; className?: string }) {
  return <span className={className} dangerouslySetInnerHTML={{ __html: html }} />;
}

function TalkCard({
  talk,
  color,
  strandName,
  typeLabel,
  onOpen,
}: {
  talk: NumberTalk;
  color: string;
  strandName: string;
  typeLabel: string;
  onOpen: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onOpen}
      className="group flex flex-col rounded-xl border-2 border-pnp-navy bg-white p-4 text-left shadow-[4px_4px_0_var(--pnp-navy)] transition-transform hover:-translate-y-0.5 hover:shadow-[5px_6px_0_var(--pnp-navy)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2"
      style={{ borderTop: `6px solid ${color}` }}
    >
      <div className="mb-2 flex items-start justify-between gap-2">
        <h3 className="line-clamp-2 min-h-[2.5rem] font-heading text-base font-extrabold leading-tight text-pnp-navy">
          {talk.title}
        </h3>
        <Tag variant="code">{talk.std}</Tag>
      </div>

      {/* thumbnail — fixed height so every tile is identical */}
      <div className="flex h-28 items-center justify-center overflow-hidden rounded-lg border-2 border-pnp-navy bg-pnp-gray-50 p-3">
        {talk.svgHtml ? (
          <Html html={talk.svgHtml} className="nt-card-fig block w-full" />
        ) : (
          <div className="text-center">
            <Html
              html={talk.problems[0] ?? ""}
              className="font-heading text-2xl font-extrabold text-pnp-navy"
            />
            {talk.problems.length > 1 && (
              <div className="mt-1.5 text-xs font-semibold text-pnp-gray-500">
                + {talk.problems.length - 1} more, one at a time
              </div>
            )}
          </div>
        )}
      </div>

      <div className="mt-3 flex items-center justify-between gap-2">
        <span className="inline-flex items-center gap-1.5 text-xs font-semibold" style={{ color }}>
          <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: color }} aria-hidden="true" />
          {strandName}
        </span>
        <span className="rounded-md border border-pnp-gray-200 bg-pnp-gray-50 px-2 py-0.5 text-[11px] font-bold uppercase tracking-wide text-pnp-gray-500">
          {typeLabel}
        </span>
      </div>
    </button>
  );
}

function Projection({
  talk,
  color,
  strandName,
  onClose,
}: {
  talk: NumberTalk;
  color: string;
  strandName: string;
  onClose: () => void;
}) {
  const isImage = !!talk.svgHtml;
  const [revealed, setRevealed] = useState(isImage ? 0 : 1); // problems shown
  const [showNotes, setShowNotes] = useState(false);
  // Image talks start hidden — the teacher flashes the picture on demand.
  const [imgShown, setImgShown] = useState(false);
  const flashTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const total = talk.problems.length;

  const flashImage = () => {
    if (flashTimer.current) clearTimeout(flashTimer.current);
    setImgShown(true);
    flashTimer.current = setTimeout(() => setImgShown(false), 3000);
  };
  const holdImage = () => {
    if (flashTimer.current) clearTimeout(flashTimer.current);
    setImgShown(true);
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      else if (!isImage && (e.key === "ArrowRight" || e.key === " "))
        setRevealed((r) => Math.min(total, r + 1));
      else if (!isImage && e.key === "ArrowLeft")
        setRevealed((r) => Math.max(1, r - 1));
    };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
      if (flashTimer.current) clearTimeout(flashTimer.current);
    };
  }, [onClose, isImage, total]);

  return (
    <div
      className="nt-fig fixed inset-0 z-50 overflow-y-auto bg-pnp-navy/70 p-3 md:p-6"
      role="dialog"
      aria-modal="true"
      aria-label={`${talk.title} — Number Talk`}
      onClick={onClose}
    >
      <div
        className="pnp-reveal mx-auto max-w-5xl rounded-2xl border-2 border-pnp-navy bg-white p-4 shadow-[6px_6px_0_var(--pnp-navy)] md:p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-2.5">
            <span
              className="inline-flex items-center rounded-md border-2 border-pnp-navy px-2.5 py-1 text-xs font-bold text-white"
              style={{ backgroundColor: color }}
            >
              {strandName}
            </span>
            <Tag variant="code">{talk.std}</Tag>
            <h2 className="font-heading text-lg font-extrabold text-pnp-navy md:text-2xl">
              {talk.title}
            </h2>
          </div>
          <div className="flex items-center gap-2">
            <GroupsButton
              isDark={false}
              className="inline-flex items-center gap-1.5 rounded-md border-2 border-pnp-navy bg-white px-3 py-1.5 text-xs font-bold text-pnp-navy transition-colors hover:bg-pnp-gray-50"
            />
            <Button tier="secondary" size="small" onClick={onClose}>
              Close ✕
            </Button>
          </div>
        </div>

        {talk.launch && (
          <p className="mb-4 rounded-lg border-2 border-pnp-navy bg-pnp-yellow/30 px-4 py-2.5 text-sm font-semibold text-pnp-navy md:text-base">
            {talk.launch}
          </p>
        )}

        {/* Stage */}
        <div className="flex min-h-[36vh] flex-col items-center justify-center rounded-xl border-2 border-pnp-navy bg-pnp-gray-50 p-5 md:p-8">
          {isImage ? (
            <Html
              html={talk.svgHtml!}
              className={`block w-full max-w-xl transition-opacity duration-150 ${imgShown ? "opacity-100" : "opacity-0"}`}
            />
          ) : (
            <div className="flex w-full flex-col items-center gap-3">
              {talk.problems.slice(0, revealed).map((p, i) => {
                const current = i === revealed - 1;
                return (
                  <div
                    key={i}
                    className={`flex w-full max-w-2xl items-center justify-center gap-4 rounded-lg px-4 py-3 transition-colors ${
                      current ? "bg-white shadow-[3px_3px_0_var(--pnp-navy)] border-2 border-pnp-navy" : ""
                    }`}
                  >
                    <Html
                      html={p}
                      className={`font-heading font-extrabold text-pnp-navy ${current ? "text-3xl md:text-5xl" : "text-xl opacity-55 md:text-2xl"}`}
                    />
                    {showNotes && talk.answers[i] != null && (
                      <Html
                        html={`= ${talk.answers[i]}`}
                        className={`font-heading font-bold ${current ? "text-2xl md:text-3xl" : "text-lg opacity-55"}`}
                      />
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Flash controls (image talks) */}
        {isImage && (
          <div className="mt-4 flex flex-col items-center gap-2">
            <div className="flex flex-wrap items-center justify-center gap-3">
              <Button tier="primary" onClick={flashImage}>
                Flash for 3 seconds
              </Button>
              <Button tier="secondary" onClick={holdImage}>
                Keep it up
              </Button>
            </div>
            <p className="text-xs font-semibold text-pnp-gray-500">
              &ldquo;Flash&rdquo; shows the image briefly, then hides it — pushing students to hold the picture in their minds.
            </p>
          </div>
        )}

        {/* Stepper */}
        {!isImage && (
          <div className="mt-4 flex flex-wrap items-center justify-center gap-3">
            <Button
              tier="secondary"
              onClick={() => setRevealed((r) => Math.max(1, r - 1))}
              disabled={revealed <= 1}
            >
              ← Back
            </Button>
            <span className="text-sm font-semibold text-pnp-gray-500">
              Problem {revealed} of {total}
            </span>
            <Button
              tier="primary"
              onClick={() => setRevealed((r) => Math.min(total, r + 1))}
              disabled={revealed >= total}
            >
              Reveal next →
            </Button>
          </div>
        )}

        {/* Teacher notes */}
        <div className="mt-5 border-t-2 border-pnp-gray-100 pt-4">
          {!showNotes ? (
            <Button tier="secondary" onClick={() => setShowNotes(true)}>
              Show teacher notes {isImage ? "" : "& answers"}
            </Button>
          ) : (
            <div className="pnp-reveal space-y-4">
              <NoteBlock label="Target strategy" html={talk.target} color={color} />
              {talk.anticipated.length > 0 && (
                <NoteList label="Likely student thinking" items={talk.anticipated} color={color} />
              )}
              <NoteBlock label="What to record" html={talk.record} color={color} />
              {talk.moves.length > 0 && (
                <NoteList label="Talk moves" items={talk.moves} color={color} />
              )}
              {talk.answers.length > 0 && (
                <div>
                  <p className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">
                    Answer key
                  </p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {talk.answers.map((a, i) => (
                      <span
                        key={i}
                        className="inline-flex items-center gap-1.5 rounded-md border-2 border-pnp-navy bg-white px-2.5 py-1 text-sm font-bold text-pnp-navy shadow-[2px_2px_0_var(--pnp-navy)]"
                      >
                        <Html html={a} />
                      </span>
                    ))}
                  </div>
                </div>
              )}
              <Button tier="tertiary" onClick={() => setShowNotes(false)}>
                Hide notes
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function NoteBlock({ label, html, color }: { label: string; html: string; color: string }) {
  if (!html) return null;
  return (
    <div className="rounded-lg border-l-4 pl-3" style={{ borderColor: color }}>
      <p className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">{label}</p>
      <Html html={html} className="mt-1 block text-sm leading-relaxed text-pnp-gray-700" />
    </div>
  );
}

function NoteList({ label, items, color }: { label: string; items: string[]; color: string }) {
  return (
    <div className="rounded-lg border-l-4 pl-3" style={{ borderColor: color }}>
      <p className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">{label}</p>
      <ul className="mt-1 list-disc space-y-1 pl-5 text-sm leading-relaxed text-pnp-gray-700">
        {items.map((it, i) => (
          <li key={i}>
            <Html html={it} />
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function NumberTalksBrowse({ grades }: { grades: NumberTalkGrade[] }) {
  const [grade, setGrade] = useState<number>(6);
  const [strand, setStrand] = useState<string>("all");
  const [concept, setConcept] = useState<string>("all");
  const [search, setSearch] = useState<string>("");
  const [openId, setOpenId] = useState<string | null>(null);

  // Deep-link from a unit lesson's warm-up strip: ?grade=8&talk=<id> opens
  // that talk. First render only.
  const searchParams = useSearchParams();
  useEffect(() => {
    const gp = Number(searchParams?.get("grade"));
    if (gp >= 6 && gp <= 8) setGrade(gp);
    const talkId = searchParams?.get("talk");
    if (talkId) setOpenId(talkId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const data = grades.find((g) => g.grade === grade) ?? grades[0];
  const concepts = useMemo(
    () => [...new Set(data.talks.map((t) => t.concept))].sort(),
    [data],
  );

  const q = search.trim().toLowerCase();
  const filtered = data.talks.filter((t) => {
    if (strand !== "all" && t.strand !== strand) return false;
    if (concept !== "all" && t.concept !== concept) return false;
    if (q && !`${t.title} ${t.concept} ${t.std}`.toLowerCase().includes(q)) return false;
    return true;
  });

  const open = openId ? data.talks.find((t) => t.id === openId) : null;

  const reset = (g: number) => {
    setGrade(g);
    setStrand("all");
    setConcept("all");
    setSearch("");
    setOpenId(null);
  };

  return (
    <div className="nt-fig">
      {/* Grade */}
      <div>
        <span className="text-xs font-bold uppercase tracking-widest text-pnp-gray-500">Grade</span>
        <div className="mt-2 flex gap-2" role="radiogroup" aria-label="Grade">
          {grades.map((gr) => {
            const active = gr.grade === grade;
            return (
              <button
                key={gr.grade}
                type="button"
                role="radio"
                aria-checked={active}
                onClick={() => reset(gr.grade)}
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
          {filtered.length} talk{filtered.length === 1 ? "" : "s"}
        </span>
      </div>

      {/* Grid */}
      {filtered.length === 0 ? (
        <p className="mt-8 rounded-md border-2 border-dashed border-pnp-gray-200 px-4 py-10 text-center text-sm text-pnp-gray-500">
          No talks match that filter. Try clearing the search.
        </p>
      ) : (
        <div className="mt-6 grid items-start gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((t) => (
            <TalkCard
              key={t.id}
              talk={t}
              color={data.strands[t.strand]?.color ?? "#0d9488"}
              strandName={data.strands[t.strand]?.name ?? t.strand}
              typeLabel={data.types[t.type] ?? t.type}
              onOpen={() => setOpenId(t.id)}
            />
          ))}
        </div>
      )}

      {open && (
        <Projection
          talk={open}
          color={data.strands[open.strand]?.color ?? "#0d9488"}
          strandName={data.strands[open.strand]?.name ?? open.strand}
          onClose={() => setOpenId(null)}
        />
      )}
    </div>
  );
}
