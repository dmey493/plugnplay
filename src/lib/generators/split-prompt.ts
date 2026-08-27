/**
 * Split a multi-part student prompt into:
 *   - intro: text before the first numbered question (the scenario / setup)
 *   - first: the first numbered question
 *   - rest: the remaining numbered questions, joined back together
 *
 * The split fires on lines that start with "1.", "2.", "3." etc.
 * If the prompt has no numbered parts, intro = "", first = full prompt, rest = "".
 *
 * This is for projection mode: project the intro + first question only,
 * keep the rest as "more questions" revealable on demand.
 */
export interface SplitPrompt {
  intro: string;
  first: string;
  rest: string;
  hasMore: boolean;
}

export function splitPrompt(prompt: unknown): SplitPrompt {
  const text = normalizeToString(prompt);
  if (!text) {
    return { intro: "", first: "", rest: "", hasMore: false };
  }

  const lines = text.split("\n");
  // Match lines that start with "1.", "2.", "10.", " 1." etc.
  const numberedRe = /^\s*(\d+)\.\s/;

  // Find every line that begins a numbered question.
  const starts: number[] = [];
  for (let i = 0; i < lines.length; i++) {
    if (numberedRe.test(lines[i])) starts.push(i);
  }

  if (starts.length < 2) {
    // No numbered split, or only one numbered item. Treat whole prompt as "first".
    return { intro: "", first: text.trim(), rest: "", hasMore: false };
  }

  const introLines = lines.slice(0, starts[0]);
  const firstLines = lines.slice(starts[0], starts[1]);
  const restLines = lines.slice(starts[1]);

  return {
    intro: introLines.join("\n").trim(),
    first: firstLines.join("\n").trim(),
    rest: restLines.join("\n").trim(),
    hasMore: true,
  };
}

/**
 * Normalize a value into a single string. Older task JSONs sometimes encode
 * extensions / discussion blocks as `string[]` instead of one multi-line
 * string — we coerce those into a bulleted text block so the parsers below
 * (which assume strings) don't crash with "x.split is not a function".
 */
function normalizeToString(value: unknown): string {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) {
    return value
      .map((item) => (typeof item === "string" ? item : String(item ?? "")))
      .map((line) => line.trim())
      .filter((line) => line.length > 0)
      .map((line) => (line.startsWith("-") || line.startsWith("•") ? line : `- ${line}`))
      .join("\n");
  }
  if (value == null) return "";
  return String(value);
}

/**
 * Same parser, but returns the full ordered list of numbered questions plus
 * the intro. Used by the rich-task projection to reveal questions one at a
 * time as the teacher presses the arrow.
 *
 * If the prompt has no numbered parts, returns intro = "" and a single-item
 * list containing the whole prompt.
 */
export interface PromptParts {
  intro: string;
  questions: string[];
}

/**
 * Parse a bulleted extension block (lines starting with "- " or "• ") into an
 * ordered array of items. Each item is a single bullet's text. If the block
 * has no bullets, returns the whole block as a single item.
 */
export function parseBulletedList(text: unknown): string[] {
  // If the JSON already encoded a list (string[]), trust it directly so each
  // entry stays as one bullet — even when the entry itself contains newlines.
  if (Array.isArray(text)) {
    return text
      .map((item) => (typeof item === "string" ? item : String(item ?? "")))
      .map((s) => s.trim())
      .filter((s) => s.length > 0);
  }
  const normalized = normalizeToString(text);
  if (!normalized) return [];
  const lines = normalized.split("\n");
  const bulletRe = /^\s*[-•]\s+/;
  const items: string[] = [];
  let cur: string[] = [];
  for (const line of lines) {
    if (bulletRe.test(line)) {
      if (cur.length) items.push(cur.join("\n").trim());
      cur = [line.replace(bulletRe, "")];
    } else {
      cur.push(line);
    }
  }
  if (cur.length) items.push(cur.join("\n").trim());
  return items.filter((s) => s.length > 0);
}

export function parsePrompt(prompt: unknown): PromptParts {
  const text = normalizeToString(prompt);
  if (!text) return { intro: "", questions: [] };

  const lines = text.split("\n");
  const numberedRe = /^\s*(\d+)\.\s/;
  const starts: number[] = [];
  for (let i = 0; i < lines.length; i++) {
    if (numberedRe.test(lines[i])) starts.push(i);
  }

  if (starts.length === 0) {
    return { intro: "", questions: [text.trim()] };
  }

  const intro = lines.slice(0, starts[0]).join("\n").trim();
  const questions: string[] = [];
  for (let i = 0; i < starts.length; i++) {
    const from = starts[i];
    const to = i + 1 < starts.length ? starts[i + 1] : lines.length;
    questions.push(lines.slice(from, to).join("\n").trim());
  }
  return { intro, questions };
}
