import fs from "fs";
import path from "path";
import type { ContentEnvelope, FilterState } from "@/lib/core/types";

const CONTENT_DIR = path.join(process.cwd(), "content", "strategies");
const SUBJECT_DIRS = ["math", "science"];

export async function getAllStrategies(): Promise<ContentEnvelope[]> {
  const strategies: ContentEnvelope[] = [];

  for (const subject of SUBJECT_DIRS) {
    const dir = path.join(CONTENT_DIR, subject);
    if (!fs.existsSync(dir)) continue;

    const files = fs.readdirSync(dir).filter((f) => f.endsWith(".json"));
    for (const file of files) {
      const raw = fs.readFileSync(path.join(dir, file), "utf-8");
      strategies.push(JSON.parse(raw) as ContentEnvelope);
    }
  }

  return strategies.sort((a, b) => a.title.localeCompare(b.title));
}

export async function getStrategyById(
  id: string
): Promise<ContentEnvelope | undefined> {
  const all = await getAllStrategies();
  return all.find((s) => s.id === id);
}

export function filterStrategies(
  strategies: ContentEnvelope[],
  filters: FilterState
): ContentEnvelope[] {
  return strategies.filter((s) => {
    if (
      filters.subjects.length > 0 &&
      !filters.subjects.some((sub) => s.subjects.includes(sub))
    )
      return false;

    if (
      filters.grades.length > 0 &&
      !filters.grades.some((g) => s.grades.includes(g))
    )
      return false;

    if (
      filters.purposes.length > 0 &&
      !filters.purposes.some((p) => s.purposes.includes(p))
    )
      return false;

    if (
      filters.mtssTiers.length > 0 &&
      !filters.mtssTiers.some((t) => s.mtssTiers.includes(t))
    )
      return false;

    if (filters.search.trim()) {
      const q = filters.search.toLowerCase();
      const haystack = `${s.title} ${s.preview} ${s.tags.join(" ")}`.toLowerCase();
      if (!haystack.includes(q)) return false;
    }

    return true;
  });
}
