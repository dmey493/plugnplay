/**
 * The stems a teacher can choose from, grouped by proficiency level.
 *
 * This is what backs the level columns under a standard: click a level, see
 * what its stems actually address, pick one, and the generator builds from
 * that stem alone.
 *
 * It reads `web/content/generator/stem-index.json`, which pairs every stem in
 * `engine/stems/stem_<std>.py` with the level it emits and the prose from its
 * module docstring. Regenerate with
 *
 *     python engine/build_stem_index.py
 *
 * Deliberately sourced from stems rather than from intervention skills. The
 * stem is what actually gets printed, and its level is the level the question
 * carries, so nothing here can claim a level the worksheet does not deliver.
 */

/* eslint-disable @typescript-eslint/no-require-imports */
const stemIndex = require("../../../content/generator/stem-index.json");
/* eslint-enable @typescript-eslint/no-require-imports */

import {
  PROFICIENCY_LEVELS,
  type ProficiencyLevel,
} from "@/lib/standards/plds";

interface RawStem {
  proficiency: ProficiencyLevel;
  difficulty: string;
  variants: number;
  describes?: string;
  item_type?: string;
}

type StemIndex = Record<string, { stems: Record<string, RawStem> }>;

export interface PickableStem {
  /** 1-based index into the standard's stem module. */
  index: number;
  /** What the stem addresses, in a teacher's words. */
  describes: string;
  level: ProficiencyLevel;
  /** "Multiple choice", "Numeric response", and so on. */
  itemType?: string;
  /** Distinct problems the engine can draw from this stem. */
  variants: number;
}

/** Every stem for a standard, keyed by level, each list in stem order. */
export type StemsByLevel = Record<ProficiencyLevel, PickableStem[]>;

const EMPTY: StemsByLevel = {
  below: [],
  approaching: [],
  at: [],
  above: [],
};

/**
 * The pickable stems for a standard, grouped by the level they sit at.
 * Returns empty lists for a standard with no stem module.
 *
 * A stem with no docstring prose is skipped rather than shown unlabelled: an
 * unnamed row in the picker tells a teacher nothing and cannot be chosen
 * meaningfully. `build_stem_index.py` warns when that happens.
 */
export function getStemsByLevel(standard: string): StemsByLevel {
  const entry = (stemIndex as StemIndex)[standard];
  if (!entry) return EMPTY;

  const grouped: StemsByLevel = {
    below: [],
    approaching: [],
    at: [],
    above: [],
  };

  for (const [key, raw] of Object.entries(entry.stems)) {
    const index = Number(key);
    if (!Number.isFinite(index) || !raw.describes) continue;
    if (!PROFICIENCY_LEVELS.includes(raw.proficiency)) continue;
    grouped[raw.proficiency].push({
      index,
      describes: raw.describes,
      level: raw.proficiency,
      itemType: raw.item_type,
      variants: raw.variants,
    });
  }

  for (const level of PROFICIENCY_LEVELS) {
    grouped[level].sort((a, b) => a.index - b.index);
  }
  return grouped;
}

/** Look up stems by index, for labelling a selection already made. */
export function findStems(standard: string, indices: number[]): PickableStem[] {
  const grouped = getStemsByLevel(standard);
  const all = PROFICIENCY_LEVELS.flatMap((l) => grouped[l]);
  return indices
    .map((i) => all.find((s) => s.index === i))
    .filter((s): s is PickableStem => Boolean(s));
}
