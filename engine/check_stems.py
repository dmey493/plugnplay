# -*- coding: utf-8 -*-
"""Structural checks for generated stems.

Everything here is standard-agnostic: it verifies the invariants a generated
question must satisfy no matter what mathematics it contains. Mathematical
correctness is per standard and belongs in that standard's own check.

These were all found the hard way while rebuilding 6.NS.4:
  - two answer choices that differ as numbers but collide once formatted
  - an f-string that never interpolated, shipping a literal "{name}"
  - a distractor with no rationale, so nobody can say why it is wrong
  - a stem whose declared level disagrees with the level it actually emits

Run:
    python engine/check_stems.py                 # every standard
    python engine/check_stems.py 6.NS.4 7.NS.2   # only these
    python engine/check_stems.py --seeds 30      # widen the sweep

Exits non-zero if any check fails, so it can gate a rebuild.
"""
import argparse
import glob
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import review_api  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "content", "generator", "stem-index.json")

# A stem that never interpolated its context leaves these behind.
UNFORMATTED = re.compile(r"\{[a-z_]+\}|\bNone\b")
# Bare instruction with no context. Not wrong everywhere, but the caller can
# ask for it to be flagged on standards whose descriptors demand context.
BARE = re.compile(r"^\s*(solve|add|subtract|multiply|divide|evaluate|simplify)\.\s*$",
                  re.I | re.M)


def check_question(q, tag, failures, warnings):
    if not (q.stem_text or "").strip():
        failures.append(f"{tag}: empty stem")
    if not (q.answer_text or "").strip():
        failures.append(f"{tag}: empty answer")
    if not (q.worked_solution or "").strip():
        failures.append(f"{tag}: empty worked solution")

    m = UNFORMATTED.search(q.stem_text or "")
    if m:
        failures.append(f"{tag}: unformatted stem near {m.group(0)!r}")

    if q.choices:
        texts = [c.text for c in q.choices]
        if len(set(texts)) != len(texts):
            failures.append(f"{tag}: duplicate choices {texts}")
        if any(not (t or "").strip() for t in texts):
            failures.append(f"{tag}: blank choice text")
        # Multi-select legitimately has several correct options; only single
        # -answer types must have exactly one.
        kind = getattr(q.item_type, "name", str(q.item_type))
        n_correct = sum(1 for c in q.choices if c.is_correct)
        if kind in ("MS", "TM"):
            if n_correct < 2:
                failures.append(f"{tag}: {kind} with {n_correct} correct, expected 2+")
        elif n_correct != 1:
            failures.append(f"{tag}: {kind} with {n_correct} correct, expected 1")
        for c in q.choices:
            if not c.is_correct and not (c.distractor_rationale or "").strip():
                # A warning, not a failure. Most of the library predates the
                # convention; a rationale is what lets a teacher say WHY an
                # option is wrong, so new stems should carry one.
                warnings.append(f"{tag}: distractor {c.key!r} has no rationale")

    if q.parts is not None:
        if len(q.parts) < 2:
            failures.append(f"{tag}: multi-part with {len(q.parts)} part(s)")
        for p in q.parts:
            if not (p.answer or "").strip():
                failures.append(f"{tag}: part {p.label!r} has no answer")


def run(codes, seeds, require_context):
    index = json.load(io.open(INDEX, encoding="utf-8"))
    failures, warnings = [], []
    checked = 0

    for code in codes:
        described = index.get(code, {}).get("stems", {})
        for seed in range(1, seeds + 1):
            try:
                questions, _ = review_api.get_questions(code, seed)
            except Exception as exc:  # noqa: BLE001
                failures.append(f"{code} seed {seed}: generation failed ({exc})")
                break
            if not questions:
                failures.append(f"{code} seed {seed}: generated nothing")
                break

            per_stem = {}
            for q in questions:
                checked += 1
                tag = f"{code} s{seed} stem{q.stem_index} v{q.variant_index}"
                check_question(q, tag, failures, warnings)
                per_stem.setdefault(q.stem_index, set()).add(
                    q.proficiency_level.name.lower())

                if code in require_context and BARE.search(q.stem_text or ""):
                    failures.append(f"{tag}: bare computation on a context standard")

            for idx, levels in per_stem.items():
                if len(levels) > 1:
                    failures.append(f"{code} stem {idx}: emits {sorted(levels)}")
                recorded = described.get(str(idx), {}).get("proficiency")
                if recorded and recorded not in levels:
                    failures.append(
                        f"{code} stem {idx}: index says {recorded}, emits {sorted(levels)}")

            if seed == 1:
                for idx in sorted(per_stem):
                    if not described.get(str(idx), {}).get("describes"):
                        failures.append(f"{code} stem {idx}: no description in the index")

    return checked, failures, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("standards", nargs="*", help="standard codes; default all")
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--show-warnings", action="store_true")
    ap.add_argument("--require-context", default="",
                    help="comma-separated codes that must never emit a bare drill")
    args = ap.parse_args()

    index = json.load(io.open(INDEX, encoding="utf-8"))
    codes = args.standards or sorted(index)
    require = {c.strip() for c in args.require_context.split(",") if c.strip()}

    checked, failures, warnings = run(codes, args.seeds, require)

    print("check_stems: %d standards, %d seeds, %d questions checked"
          % (len(codes), args.seeds, checked))
    if warnings:
        by_std = {}
        for w in warnings:
            by_std[w.split()[0]] = by_std.get(w.split()[0], 0) + 1
        print("check_stems: %d warnings across %d standards (worst: %s)"
              % (len(warnings), len(by_std),
                 ", ".join("%s x%d" % kv for kv in
                           sorted(by_std.items(), key=lambda x: -x[1])[:5])))
        if args.show_warnings:
            for w in warnings[:40]:
                print("   ~ " + w)
    if failures:
        print("check_stems: %d FAILURES" % len(failures))
        for f in failures[:40]:
            print("   " + f)
        if len(failures) > 40:
            print("   ... and %d more" % (len(failures) - 40))
        return 1
    print("check_stems: all structural checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
