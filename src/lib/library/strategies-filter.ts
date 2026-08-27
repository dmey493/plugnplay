import type { ContentEnvelope, FilterState } from "@/lib/core/types";

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
