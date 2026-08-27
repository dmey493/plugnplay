import React from "react";
import Link from "next/link";
import type { Block } from "@/lib/library/approach";

/**
 * Renderer for the teaching-approach content blocks (see lib/approach.ts).
 * Pure Server Component — no client JS. Every visual choice maps to the
 * Plug N Play design system (brand tokens, navy borders + hard offset
 * shadows on emphasis cards, no purple on interactive surfaces, emojiless).
 *
 * Inline text supports a tiny, safe markdown subset — **bold**, *italic*,
 * `code`, [label](/href) — parsed by renderInline(). No raw HTML is ever
 * injected, so content stays XSS-safe.
 */

// ─── Inline markdown ────────────────────────────────────────────────────

// One combined matcher for the four inline forms. Order matters: code first
// so backticked content isn't re-parsed for * / [ inside it. A fresh instance
// is built per call because renderInline recurses (link labels), and a shared
// global-flag regex would clobber the outer loop's lastIndex.
const INLINE_SRC = "(`[^`]+`)|(\\*\\*[^*]+\\*\\*)|(\\*[^*]+\\*)|(\\[[^\\]]+\\]\\([^)]+\\))";

export function renderInline(text: string, keyPrefix = "i"): React.ReactNode[] {
  const nodes: React.ReactNode[] = [];
  const re = new RegExp(INLINE_SRC, "g");
  let last = 0;
  let m: RegExpExecArray | null;
  let k = 0;

  while ((m = re.exec(text)) !== null) {
    if (m.index > last) nodes.push(text.slice(last, m.index));
    const token = m[0];
    const key = `${keyPrefix}-${k++}`;

    if (token.startsWith("`")) {
      nodes.push(
        <code
          key={key}
          className="rounded bg-pnp-blue/10 px-1.5 py-0.5 font-mono text-[0.92em] font-semibold text-pnp-blue"
        >
          {token.slice(1, -1)}
        </code>
      );
    } else if (token.startsWith("**")) {
      nodes.push(
        <strong key={key} className="font-bold text-pnp-navy">
          {token.slice(2, -2)}
        </strong>
      );
    } else if (token.startsWith("*")) {
      nodes.push(<em key={key}>{token.slice(1, -1)}</em>);
    } else {
      // [label](href) — the label may itself carry **bold** / *italic* / `code`,
      // so render it recursively rather than as a literal string.
      const split = token.indexOf("](");
      const label = token.slice(1, split);
      const href = token.slice(split + 2, -1);
      const external = /^https?:\/\//.test(href);
      const linkClass =
        "font-semibold text-pnp-accent underline decoration-pnp-accent/40 underline-offset-2 hover:decoration-pnp-accent";
      const labelNodes = renderInline(label, key);
      nodes.push(
        external ? (
          <a
            key={key}
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className={linkClass}
          >
            {labelNodes}
          </a>
        ) : (
          <Link key={key} href={href} className={linkClass}>
            {labelNodes}
          </Link>
        )
      );
    }
    last = m.index + token.length;
  }
  if (last < text.length) nodes.push(text.slice(last));
  return nodes;
}

function Inline({ text }: { text: string }) {
  return <>{renderInline(text)}</>;
}

// ─── Callout theming (brand tokens only) ────────────────────────────────
// House-style emphasis cards: navy border + hard offset shadow, a tinted
// fill per variant. No colored edge bars.

const CALLOUT: Record<string, { wrap: string }> = {
  vision: { wrap: "bg-white" },
  equity: { wrap: "bg-pnp-accent-soft/40" },
  tip: { wrap: "bg-pnp-yellow/15" },
  watch: { wrap: "bg-pnp-red/5" },
};

// ─── Single block ───────────────────────────────────────────────────────

function BlockView({ block }: { block: Block }) {
  switch (block.type) {
    case "lead":
      return (
        <p className="text-lg leading-relaxed text-pnp-gray-700">
          <Inline text={block.text} />
        </p>
      );

    case "heading":
      return (
        <h2 className="mt-10 border-b-2 border-pnp-gray-200 pb-2 font-heading text-xl font-extrabold text-pnp-navy md:text-2xl">
          <Inline text={block.text} />
        </h2>
      );

    case "subheading":
      return (
        <h3 className="mt-6 font-heading text-lg font-bold text-pnp-navy">
          <Inline text={block.text} />
        </h3>
      );

    case "paragraph":
      return (
        <p
          className={`leading-relaxed ${
            block.muted ? "text-sm text-pnp-gray-500" : "text-pnp-gray-700"
          }`}
        >
          <Inline text={block.text} />
        </p>
      );

    case "list": {
      const Tag = block.ordered ? "ol" : "ul";
      return (
        <Tag
          className={`space-y-1.5 pl-5 text-pnp-gray-700 ${
            block.ordered ? "list-decimal" : "list-disc"
          } marker:text-pnp-gray-400`}
        >
          {block.items.map((it, i) => (
            <li key={i} className="leading-relaxed">
              <Inline text={it} />
            </li>
          ))}
        </Tag>
      );
    }

    case "steps":
      return (
        <ol className="space-y-3">
          {block.items.map((it, i) => (
            <li
              key={i}
              className="flex gap-4 rounded-xl border-2 border-pnp-navy bg-white p-4 shadow-[3px_3px_0_var(--pnp-navy)]"
            >
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-pnp-navy font-heading text-sm font-bold text-white">
                {i + 1}
              </span>
              <div className="pt-0.5 leading-relaxed text-pnp-gray-700">
                <Inline text={it} />
              </div>
            </li>
          ))}
        </ol>
      );

    case "callout": {
      const c = CALLOUT[block.variant] ?? CALLOUT.vision;
      return (
        <div
          className={`rounded-xl border-2 border-pnp-navy ${c.wrap} p-5 shadow-[3px_3px_0_var(--pnp-navy)]`}
        >
          <p className="mb-2 font-heading text-base font-extrabold text-pnp-navy">
            {block.title}
          </p>
          <div className="space-y-3 text-pnp-gray-700">
            {block.blocks.map((b, i) => (
              <BlockView key={i} block={b} />
            ))}
          </div>
        </div>
      );
    }

    case "doDont":
      return (
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-xl border-2 border-pnp-green/40 bg-pnp-green/5 p-5">
            <h4 className="mb-3 flex items-center gap-2 font-heading text-base font-bold text-pnp-green">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              {block.yes.title}
            </h4>
            <ul className="space-y-1.5 pl-5 list-disc text-sm leading-relaxed text-pnp-gray-700 marker:text-pnp-green/60">
              {block.yes.items.map((it, i) => (
                <li key={i}>
                  <Inline text={it} />
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-xl border-2 border-pnp-red/40 bg-pnp-red/5 p-5">
            <h4 className="mb-3 flex items-center gap-2 font-heading text-base font-bold text-pnp-red">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M18 6 6 18M6 6l12 12" />
              </svg>
              {block.no.title}
            </h4>
            <ul className="space-y-1.5 pl-5 list-disc text-sm leading-relaxed text-pnp-gray-700 marker:text-pnp-red/50">
              {block.no.items.map((it, i) => (
                <li key={i}>
                  <Inline text={it} />
                </li>
              ))}
            </ul>
          </div>
        </div>
      );

    case "table":
      return (
        <div className="overflow-x-auto rounded-xl border-2 border-pnp-navy shadow-[3px_3px_0_var(--pnp-navy)]">
          <table className="w-full border-collapse text-left text-sm">
            <thead>
              <tr className="bg-pnp-navy text-white">
                {block.headers.map((h, i) => (
                  <th key={i} className="px-4 py-3 font-heading font-bold">
                    <Inline text={h} />
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {block.rows.map((row, r) => (
                <tr
                  key={r}
                  className="border-t border-pnp-gray-200 even:bg-pnp-gray-50"
                >
                  {row.map((cell, c) => (
                    <td
                      key={c}
                      className="px-4 py-3 align-top leading-relaxed text-pnp-gray-700"
                    >
                      <Inline text={cell} />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );

    case "tags": {
      const strand = block.variant === "strand";
      return (
        <div>
          {block.label && (
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-pnp-gray-500">
              {block.label}
            </p>
          )}
          <div className="flex flex-wrap gap-2">
            {block.items.map((it, i) => (
              <span
                key={i}
                className={`inline-flex select-none items-center rounded-md border-2 border-pnp-navy px-2.5 py-1 text-xs font-semibold shadow-[2px_2px_0_var(--pnp-navy)] ${
                  strand
                    ? "bg-pnp-accent-soft text-pnp-accent-press"
                    : "bg-pnp-gray-100 text-pnp-navy"
                }`}
              >
                {it}
              </span>
            ))}
          </div>
        </div>
      );
    }

    default:
      return null;
  }
}

// ─── Public: render a list of blocks with vertical rhythm ───────────────

export default function ApproachBlocks({ blocks }: { blocks: Block[] }) {
  return (
    <div className="space-y-4">
      {blocks.map((b, i) => (
        <BlockView key={i} block={b} />
      ))}
    </div>
  );
}
