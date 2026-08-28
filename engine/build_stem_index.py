# -*- coding: utf-8 -*-
"""Build web/content/generator/stem-index.json.

The generator UI needs to label an intervention skill with the proficiency
level it practises, and it needs that label BEFORE the teacher clicks
"Build my set". That fact lives inside the Python stem modules
(`ProficiencyLevel.AT` on the question each stem emits), which the browser
cannot read. So we precompute it here into a small JSON the front end
imports at build time.

The bridge itself already exists: every skill in web/content/skills/<STD>.json
carries `engine_stems`, a list of 1-based stem indices in
engine/stems/stem_<std>.py. This file just resolves each of those indices to
its proficiency and difficulty.

Run:
    python engine/build_stem_index.py            # rewrite the JSON
    python engine/build_stem_index.py --check    # exit 1 if it is stale

Re-run it after changing which proficiency a stem emits, or after adding a
stem module. `--check` is the guard against silent drift.
"""
import ast
import collections
import glob
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import review_api  # noqa: E402


def _find_root():
    """Walk up until we find the dir holding BOTH web/content/skills and
    web/engine. Mirrors _find_root() in validate_content.py."""
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        if (os.path.isdir(os.path.join(d, "web", "content", "skills"))
                and os.path.isdir(os.path.join(d, "web", "engine"))):
            return d
        d = os.path.dirname(d)
    sys.exit("build_stem_index: could not locate repo root above "
             + os.path.abspath(__file__))


ROOT = _find_root()
SKILLS = os.path.join(ROOT, "web", "content", "skills")
OUT = os.path.join(ROOT, "web", "content", "generator", "stem-index.json")

# Fixed seed: the stem->proficiency mapping is structural, not random, so any
# seed produces the same index. Pinning one keeps the output byte-stable.
SEED = 7

STEMS_DIR = os.path.join(ROOT, "web", "engine", "stems")

# Every stem module documents its stems in the same shape, transcribed from the
# item spec:
#     Stem 3 (Approaching-NR): One-step word problem with fractions (DOK 2, medium)
# We keep the prose, which is what a teacher needs to choose a stem, and drop
# the DOK/difficulty tail, which is internal grading metadata.
STEM_DOC = re.compile(r"^\s*Stem\s+(\d+)\s*\(([^)]*)\)\s*:?\s*(.+?)\s*$", re.I)
DOK_TAIL = re.compile(r"\s*\((?:DOK[^)]*)\)\s*$", re.I)
DOC_LEVELS = {"below", "approaching", "at", "above"}
ITEM_TYPES = {
    "NR": "Numeric response",
    "MC": "Multiple choice",
    "MS": "Multi-select",
    "MP": "Multi-part",
    "TI": "Table input",
    "GR": "Graphing",
    "DD": "Drop-down",
    "EQ": "Equation",
    "ER": "Written response",
    "TM": "Table matching",
}


def stem_descriptions(standard_code):
    """Read the per-stem prose out of a stem module's docstring.

    Returns {stem_index: {"describes": str, "item_type": str|None}}.
    """
    slug = standard_code.lower().replace(".", "")
    path = os.path.join(STEMS_DIR, "stem_%s.py" % slug)
    if not os.path.exists(path):
        # A few modules are cased differently (stem_7GM3.py).
        matches = [p for p in glob.glob(os.path.join(STEMS_DIR, "stem_*.py"))
                   if os.path.basename(p).lower() == "stem_%s.py" % slug]
        if not matches:
            return {}
        path = matches[0]

    doc = ast.get_docstring(ast.parse(io.open(path, encoding="utf-8").read())) or ""
    out = {}
    for line in doc.splitlines():
        m = STEM_DOC.match(line)
        if not m:
            continue
        idx = int(m.group(1))
        meta = m.group(2)
        text = DOK_TAIL.sub("", m.group(3)).strip().rstrip(".")
        # House style: no em dashes in anything a teacher reads.
        text = text.replace(" — ", ", ").replace("—", ", ")
        # meta is "Approaching-NR" or "At-MC, DOK 2, Medium"; only the first
        # comma-separated part carries the level and item type.
        head = meta.split(",")[0].strip()
        code = head.rsplit("-", 1)[-1].strip().upper() if "-" in head else ""
        doc_level = head.rsplit("-", 1)[0].strip().lower() if "-" in head else ""
        out[idx] = {
            "describes": text,
            "item_type": ITEM_TYPES.get(code),
            "doc_level": doc_level if doc_level in DOC_LEVELS else "",
        }
    return out


def build():
    index = {}
    problems = []

    for path in sorted(glob.glob(os.path.join(SKILLS, "*.json"))):
        data = json.load(io.open(path, encoding="utf-8"))
        code = data["standard_code"]

        try:
            questions, _ = review_api.get_questions(code, SEED)
        except Exception as exc:  # noqa: BLE001 - report, don't crash the sweep
            problems.append("%s: stem module failed to generate (%s)" % (code, exc))
            continue

        prof = collections.defaultdict(collections.Counter)
        diff = collections.defaultdict(collections.Counter)
        for q in questions:
            prof[q.stem_index][q.proficiency_level.name.lower()] += 1
            diff[q.stem_index][q.difficulty.name.lower()] += 1

        described = stem_descriptions(code)

        stems = {}
        for idx in sorted(prof):
            if len(prof[idx]) > 1:
                problems.append(
                    "%s stem %d emits more than one proficiency (%s); the "
                    "index records the most common one"
                    % (code, idx, dict(prof[idx]))
                )
            level = prof[idx].most_common(1)[0][0]
            info = described.get(idx)
            if not info:
                problems.append(
                    "%s stem %d has no description in the module docstring; "
                    "the picker would show it unlabelled" % (code, idx)
                )

            # The docstring also names the level ("Stem 3 (Approaching-NR)").
            # If that disagrees with what the stem actually emits, the prose a
            # teacher reads is filed under the wrong level, so say so.
            if info and info.get("doc_level") and info["doc_level"] != level:
                problems.append(
                    "%s stem %d: docstring says %s but the stem emits %s"
                    % (code, idx, info["doc_level"], level)
                )

            entry = {
                "proficiency": level,
                "difficulty": diff[idx].most_common(1)[0][0],
                "variants": sum(prof[idx].values()),
            }
            if info:
                entry["describes"] = info["describes"]
                if info.get("item_type"):
                    entry["item_type"] = info["item_type"]
            stems[str(idx)] = entry

        # Every engine_stems index a skill claims must exist, or the generator
        # would silently return an empty pool for that skill.
        for skill in data["skills"]:
            for claimed in (skill.get("engine_stems") or []):
                if str(claimed) not in stems:
                    problems.append(
                        "%s %s claims engine stem %s, which stem_%s.py does "
                        "not emit (valid: %s)"
                        % (code, skill["skill_id"], claimed,
                           code.lower().replace(".", ""), sorted(stems))
                    )

        index[code] = {"stems": stems}

    return index, problems


def serialize(index):
    return json.dumps(index, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def main():
    check = "--check" in sys.argv
    index, problems = build()
    text = serialize(index)

    # Reported, never fatal. The index always records what a stem actually
    # emits; these lines flag prose that has drifted from the code.
    for p in problems:
        print("build_stem_index: warning: " + p)

    if check:
        if not os.path.exists(OUT):
            print("build_stem_index: %s is missing. Run without --check." % OUT)
            return 1
        current = io.open(OUT, encoding="utf-8").read()
        if current != text:
            print("build_stem_index: %s is stale. Run "
                  "`python engine/build_stem_index.py` and commit the result."
                  % os.path.relpath(OUT, ROOT))
            return 1
        print("build_stem_index: OK (%d standards, index up to date)" % len(index))
        return 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print("build_stem_index: wrote %s (%d standards, %d stems)"
          % (os.path.relpath(OUT, ROOT), len(index),
             sum(len(v["stems"]) for v in index.values())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
