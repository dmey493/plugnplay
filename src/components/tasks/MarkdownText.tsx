"use client";

import React from "react";

/**
 * Lightweight markdown renderer for projection-view content.
 *
 * The student-prompt JSON uses a small markdown subset: bold (`**text**`),
 * italic (`*text*` and `_text_`), bullet lists (lines starting with `- `),
 * and GitHub-flavored tables. We render those as proper HTML so the
 * projection isn't a wall of raw `|` characters.
 *
 * This is intentionally tiny — no external dependency, no HTML sanitization
 * beyond what JSX gives us (we never set innerHTML), and only the constructs
 * we actually use in task prompts.
 */

interface Props {
  /** Markdown source. Some task JSONs store list-shaped fields like
   *  `discussionQuestions` or `extensions` as `string[]` instead of a
   *  newline-joined string, so we defensively accept either shape and
   *  normalise on the way in. */
  text: string | string[] | undefined | null;
  /** Inline class applied to every block (paragraph, list, table). */
  blockClassName?: string;
  /** Font size + colour come from the parent — we don't set them here. */
  style?: React.CSSProperties;
  /** Visual scale knob: shrinks table cell padding when density is tight. */
  density?: number;
  /** Optional override for table text colours. Defaults inherit from parent. */
  isDark?: boolean;
}

/** Normalise an authoring-time field into a single markdown string.
 *  Arrays become bullet-prefixed lines so they render as a list block
 *  (matching what an author writing `- item` would have produced). */
function normaliseToString(raw: string | string[] | undefined | null): string {
  if (!raw) return "";
  if (typeof raw === "string") return raw;
  if (Array.isArray(raw)) {
    // If any entry already begins with `-` or `*`, trust the author.
    // Otherwise prefix each with `- ` so it renders as a bullet list.
    return raw
      .map((entry) => {
        const t = String(entry).trim();
        if (!t) return "";
        return /^[-*•]\s/.test(t) ? t : `- ${t}`;
      })
      .filter(Boolean)
      .join("\n");
  }
  return String(raw);
}

type Block =
  | { kind: "table"; header: string[]; rows: string[][] }
  | { kind: "list"; items: string[] }
  | { kind: "paragraph"; text: string }
  // A "scenario cards" row — one or more `::: card TITLE ... :::` blocks
  // that appeared back-to-back in the source. We render them as a grid so
  // tasks like Sort the Bills can present three pricing situations as
  // distinct visual cards rather than as bulleted text.
  | { kind: "cards"; cards: { title: string; body: string }[] };

export default function MarkdownText({
  text,
  blockClassName,
  style,
  density = 1,
  isDark = false,
}: Props) {
  const blocks = React.useMemo(
    () => parseBlocks(normaliseToString(text)),
    [text]
  );
  if (blocks.length === 0) return null;

  return (
    <>
      {blocks.map((block, i) => {
        if (block.kind === "table") {
          return (
            <MarkdownTable
              key={i}
              header={block.header}
              rows={block.rows}
              density={density}
              isDark={isDark}
              style={style}
            />
          );
        }
        if (block.kind === "list") {
          return (
            <ul
              key={i}
              className={`${blockClassName ?? ""} ml-5 list-disc space-y-1`}
              style={style}
            >
              {block.items.map((item, j) => (
                <li key={j}>{renderInline(item)}</li>
              ))}
            </ul>
          );
        }
        if (block.kind === "cards") {
          return (
            <ScenarioCardsRow
              key={i}
              cards={block.cards}
              density={density}
              isDark={isDark}
              style={style}
            />
          );
        }
        return (
          <p
            key={i}
            className={`${blockClassName ?? ""} whitespace-pre-line`}
            style={style}
          >
            {renderInline(block.text)}
          </p>
        );
      })}
    </>
  );
}

// ───────────────────────────────────────────────────────────
// Scenario cards row — for tasks that present multiple
// labelled situations (Sort the Bills, etc.) as side-by-side
// visual cards instead of bulleted text.
// ───────────────────────────────────────────────────────────

function ScenarioCardsRow({
  cards,
  density,
  isDark,
  style,
}: {
  cards: { title: string; body: string }[];
  density: number;
  isDark: boolean;
  style?: React.CSSProperties;
}) {
  // Padding tightens with density so multi-card rows still fit when the
  // projection is dense with revealed questions stacked below.
  const pad = `${(0.9 * density).toFixed(2)}rem ${(1.1 * density).toFixed(2)}rem`;
  const radius = `${(0.6 * density).toFixed(2)}rem`;
  const accentBg = isDark ? "rgba(255,255,255,0.08)" : "rgba(63,66,217,0.06)";
  const cardBg = isDark ? "rgba(255,255,255,0.05)" : "#ffffff";
  const headerBg = isDark ? "rgba(255,255,255,0.16)" : "rgba(63,66,217,0.12)";
  const headerColor = isDark ? "#fff" : "var(--pnp-navy, #1a1f3d)";
  const border = isDark ? "rgba(255,255,255,0.20)" : "rgba(0,0,0,0.12)";
  // 1 col on phones, 2 cols at sm if 4+ cards, 3 cols at md+ when there's
  // 3 cards (the common shape).
  const cols = cards.length >= 3 ? 3 : cards.length;
  const gridClass =
    cols === 3
      ? "grid grid-cols-1 sm:grid-cols-3 gap-3"
      : cols === 2
        ? "grid grid-cols-1 sm:grid-cols-2 gap-3"
        : "grid grid-cols-1 gap-3";
  return (
    <div className={`my-3 ${gridClass}`} style={{ background: accentBg, borderRadius: radius, padding: `${(0.4 * density).toFixed(2)}rem` }}>
      {cards.map((c, i) => (
        <div
          key={i}
          style={{
            background: cardBg,
            border: `1px solid ${border}`,
            borderRadius: radius,
            overflow: "hidden",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <div
            style={{
              padding: `${(0.5 * density).toFixed(2)}rem ${(1.0 * density).toFixed(2)}rem`,
              background: headerBg,
              color: headerColor,
              fontWeight: 800,
              letterSpacing: "0.02em",
              textTransform: "uppercase",
              fontSize: "0.85em",
              borderBottom: `1px solid ${border}`,
            }}
          >
            {renderInline(c.title)}
          </div>
          <div
            style={{ padding: pad, ...(style ?? {}) }}
            className="leading-snug"
          >
            <MarkdownText
              text={c.body}
              density={density}
              isDark={isDark}
              style={{ fontSize: "inherit" }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

function MarkdownTable({
  header,
  rows,
  density,
  isDark,
  style,
}: {
  header: string[];
  rows: string[][];
  density: number;
  isDark: boolean;
  style?: React.CSSProperties;
}) {
  // Padding tightens as density drops so multi-question projections still fit.
  const pad = `${(0.6 * density).toFixed(2)}rem ${(0.9 * density).toFixed(2)}rem`;
  const headerBg = isDark ? "rgba(255,255,255,0.10)" : "rgba(63,66,217,0.08)";
  const rowAltBg = isDark ? "rgba(255,255,255,0.04)" : "rgba(0,0,0,0.02)";
  const border = isDark ? "rgba(255,255,255,0.25)" : "rgba(0,0,0,0.18)";

  return (
    <div className="my-3 overflow-x-auto">
      <table
        className="w-auto border-collapse"
        style={{ ...style, fontSize: style?.fontSize }}
      >
        {header.length > 0 && (
          <thead>
            <tr>
              {header.map((cell, i) => (
                <th
                  key={i}
                  scope="col"
                  className="text-left font-bold"
                  style={{
                    padding: pad,
                    background: headerBg,
                    borderBottom: `2px solid ${border}`,
                    borderTop: `1px solid ${border}`,
                    borderLeft: i === 0 ? `1px solid ${border}` : undefined,
                    borderRight: `1px solid ${border}`,
                  }}
                >
                  {renderInline(cell)}
                </th>
              ))}
            </tr>
          </thead>
        )}
        <tbody>
          {rows.map((row, r) => (
            <tr key={r} style={r % 2 === 1 ? { background: rowAltBg } : undefined}>
              {row.map((cell, c) => (
                <td
                  key={c}
                  style={{
                    padding: pad,
                    borderBottom: `1px solid ${border}`,
                    borderLeft: c === 0 ? `1px solid ${border}` : undefined,
                    borderRight: `1px solid ${border}`,
                  }}
                >
                  {renderInline(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ───────────────────────────────────────────────────────────
// Block parser
// ───────────────────────────────────────────────────────────

function parseBlocks(text: string): Block[] {
  if (!text) return [];
  const lines = text.split("\n");
  const blocks: Block[] = [];

  let i = 0;
  while (i < lines.length) {
    const line = lines[i];

    // Blank line — skip.
    if (line.trim().length === 0) {
      i += 1;
      continue;
    }

    // Scenario card fence — `::: card TITLE` opens, `:::` closes.
    // Multiple adjacent card blocks are collapsed into a single
    // `cards` row so they render as a grid.
    if (isCardOpen(line)) {
      const cards: { title: string; body: string }[] = [];
      while (i < lines.length && isCardOpen(lines[i])) {
        const title = parseCardOpen(lines[i]);
        let j = i + 1;
        const bodyLines: string[] = [];
        while (j < lines.length && !isCardClose(lines[j])) {
          bodyLines.push(lines[j]);
          j += 1;
        }
        cards.push({ title, body: bodyLines.join("\n").trim() });
        // Step past the closing `:::` (or end-of-input).
        i = j < lines.length ? j + 1 : j;
        // Eat blank lines between adjacent card fences.
        while (i < lines.length && lines[i].trim().length === 0) i += 1;
      }
      blocks.push({ kind: "cards", cards });
      continue;
    }

    // Table: a `|` row followed by a separator row (`|---|---|`).
    if (isTableHeader(lines, i)) {
      const header = parseRow(lines[i]);
      // i+1 is the separator — we know it matches from isTableHeader.
      let j = i + 2;
      const rows: string[][] = [];
      while (j < lines.length && isTableRow(lines[j])) {
        rows.push(parseRow(lines[j]));
        j += 1;
      }
      blocks.push({ kind: "table", header, rows });
      i = j;
      continue;
    }

    // Bullet list: contiguous lines starting with `- `, `* `, or `• `.
    if (isBullet(line)) {
      const items: string[] = [];
      let j = i;
      while (j < lines.length && isBullet(lines[j])) {
        items.push(stripBullet(lines[j]));
        j += 1;
        // Allow soft-wrapped continuation lines that don't start a new bullet.
        while (
          j < lines.length &&
          lines[j].trim().length > 0 &&
          !isBullet(lines[j]) &&
          !isTableRow(lines[j])
        ) {
          items[items.length - 1] += " " + lines[j].trim();
          j += 1;
        }
      }
      blocks.push({ kind: "list", items });
      i = j;
      continue;
    }

    // Paragraph: contiguous non-blank, non-bullet, non-table lines.
    const para: string[] = [];
    while (
      i < lines.length &&
      lines[i].trim().length > 0 &&
      !isBullet(lines[i]) &&
      !isTableHeader(lines, i)
    ) {
      para.push(lines[i]);
      i += 1;
    }
    blocks.push({ kind: "paragraph", text: para.join("\n") });
  }

  return blocks;
}

/** A line that opens a scenario card. Allows two title shapes:
 *    "::: card Card 1"   → title is "Card 1"
 *    "::: card"           → no title (header bar still renders) */
function isCardOpen(line: string): boolean {
  return /^\s*:::\s*card\b/i.test(line);
}
function isCardClose(line: string): boolean {
  return /^\s*:::\s*$/.test(line);
}
function parseCardOpen(line: string): string {
  return line.replace(/^\s*:::\s*card\s*/i, "").trim();
}

function isTableRow(line: string): boolean {
  const t = line.trim();
  return t.startsWith("|") && t.endsWith("|") && t.length > 2;
}

function isTableHeader(lines: string[], i: number): boolean {
  if (!isTableRow(lines[i])) return false;
  const next = lines[i + 1];
  if (!next || !isTableRow(next)) return false;
  // Separator row is all dashes / colons / pipes / spaces.
  return /^[\s|:-]+$/.test(next.trim()) && next.includes("-");
}

function parseRow(line: string): string[] {
  const t = line.trim();
  // Strip leading & trailing pipes, then split on internal pipes.
  const inner = t.replace(/^\|/, "").replace(/\|$/, "");
  return inner.split("|").map((cell) => cell.trim());
}

function isBullet(line: string): boolean {
  return /^\s*[-*•]\s+/.test(line);
}

function stripBullet(line: string): string {
  return line.replace(/^\s*[-*•]\s+/, "").trim();
}

// ───────────────────────────────────────────────────────────
// Inline renderer (bold + italic)
// ───────────────────────────────────────────────────────────

/**
 * Render inline markdown for `**bold**`, `*italic*`, `_italic_`.
 * Returns an array of React children so each match becomes a real element.
 */
function renderInline(text: string): React.ReactNode {
  if (!text) return text;

  // Tokenise left-to-right. We want bold to bind tighter than italic, so
  // we scan for `**...**` first, then `*...*` / `_..._` inside the rest.
  const nodes: React.ReactNode[] = [];
  const BOLD = /\*\*([^*]+)\*\*/g;
  const ITALIC = /(^|[^*])\*([^*]+)\*|_([^_]+)_/g;

  let cursor = 0;
  let key = 0;
  const matches: { start: number; end: number; node: React.ReactNode }[] = [];

  // Bold matches first.
  for (let m = BOLD.exec(text); m !== null; m = BOLD.exec(text)) {
    matches.push({
      start: m.index,
      end: m.index + m[0].length,
      node: <strong key={`b-${key++}`}>{m[1]}</strong>,
    });
  }

  // Italic matches that don't overlap a bold match.
  for (let m = ITALIC.exec(text); m !== null; m = ITALIC.exec(text)) {
    const offset = m[1] ? m[1].length : 0;
    const start = m.index + offset;
    const end = m.index + m[0].length;
    const content = m[2] ?? m[3] ?? "";
    if (matches.some((b) => overlap(b.start, b.end, start, end))) continue;
    matches.push({
      start,
      end,
      node: <em key={`i-${key++}`}>{content}</em>,
    });
  }

  matches.sort((a, b) => a.start - b.start);

  for (const m of matches) {
    if (m.start > cursor) nodes.push(text.slice(cursor, m.start));
    nodes.push(m.node);
    cursor = m.end;
  }
  if (cursor < text.length) nodes.push(text.slice(cursor));

  return nodes.length > 0 ? nodes : text;
}

function overlap(a1: number, a2: number, b1: number, b2: number): boolean {
  return a1 < b2 && b1 < a2;
}
