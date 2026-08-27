# -*- coding: utf-8 -*-
"""Build-time content validator for the skill-intervention JSONs.

Fails (exit 1) if any shipped skill would silently degrade the teacher's
close-the-loop experience. Checks, for every standard:
  1. web/content/skills and authoring/data/skills mirrors parse-equal.
  2. Every non-foundation skill has non-empty next_steps.if_pass AND if_fail
     (an empty route collapses the packet to a generic "repeat this skill",
     which contradicts the authored diagnostic_flow — review priority #4).

Grounded-rote gates (July 2026 remediation plan). Gate 5 always hard-fails;
gates 1-4 report as WARNINGS by default and hard-fail under --strict (the
authoring pipeline runs --strict so re-authored content can't regress; legacy
content is grandfathered until the Tier 1/2 sweeps land):
  Gate 1  Model debt — a representation named in a strategy_links.why must
          actually appear in the lesson (worked example, activities, or
          printable_artifact). Kills the "strategy-link IOU".
  Gate 2  Ground first — worked_example_script must open with a show/ask
          (model/prediction) step, not a say (rule statement) step.
  Gate 3  Activity slotting — game-type activities only in the final slot;
          the drill caps the lesson, it doesn't lead it.
  Gate 4  Foundation anchor — foundation skills must reference at least one
          concrete representation somewhere in their lesson text.
  Gate 5  Dedup + link validity — no activity duplicated verbatim across
          standards; every strategy_links.strategy_id exists in
          web/content/strategies/math.

Run:  python engine/validate_content.py [--strict]
Wire into CI as a gate before shipping content; authoring runs --strict.
"""
import json, io, glob, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web", "content", "skills")
AUTH = os.path.join(ROOT, "authoring", "data", "skills")
STRATS = os.path.join(ROOT, "web", "content", "strategies", "math")

# Representations a strategy-link rationale can promise. If the why-text
# names one, the lesson itself must contain it (Gate 1). Keep terms specific
# enough that a match means a real model, not incidental prose.
MODEL_TERMS = [
    "area model", "box model", "algebra tiles", "tile", "double number line",
    "tape diagram", "bar model", "percent bar", "hundredths grid", "hundred grid",
    "number line", "counters", "fraction bar", "fraction strip", "grid paper",
    "pan balance", "balance scale", "dot plot", "array",
]

# Gate 4: a foundation skill counts as anchored if any of these appear in its
# lesson text (i_do + worked example + activities).
ANCHOR_TERMS = MODEL_TERMS + [
    "grid", "pattern", "picture", "diagram", "model", "draw", "shade", "build",
]


def lesson_text(s):
    """All teacher/student-facing lesson prose for one skill, lowercased."""
    parts = [s.get("i_do_script") or ""]
    for st in s.get("worked_example_script") or []:
        parts.append(st.get("text") or "")
    for a in s.get("activities") or []:
        parts.append(a.get("title") or "")
        parts.append(a.get("instructions") or "")
        parts.extend(a.get("materials") or [])
        parts.append(json.dumps(a.get("content") or {}))
    pa = s.get("printable_artifact")
    if pa:
        parts.append(json.dumps(pa))
    return " ".join(parts).lower()


def main():
    strict = "--strict" in sys.argv[1:]
    failures, warnings = [], []
    gate = failures if strict else warnings

    valid_strategy_ids = set()
    for sf in glob.glob(os.path.join(STRATS, "*.json")):
        sj = json.load(io.open(sf, encoding="utf-8"))
        sid = sj.get("strategy_id") or sj.get("id")
        if sid:
            valid_strategy_ids.add(sid)

    seen_activities = {}  # (title, instructions) -> "skill_id (file)"

    for wf in sorted(glob.glob(os.path.join(WEB, "*.json"))):
        base = os.path.basename(wf)
        wj = json.load(io.open(wf, encoding="utf-8"))
        cf = os.path.join(AUTH, base)
        if not os.path.exists(cf):
            failures.append(f"{base}: missing authoring mirror")
            continue
        cj = json.load(io.open(cf, encoding="utf-8"))
        if wj != cj:
            failures.append(f"{base}: web/authoring mirrors differ")

        for s in wj.get("skills", []):
            sid = s.get("skill_id", "?")
            where = f"{sid} ({base})"
            is_foundation = s.get("column") == "foundation"
            text = lesson_text(s)

            # -- original hard checks -------------------------------------
            if not is_foundation:
                ns = s.get("next_steps") or {}
                if not (ns.get("if_pass") or "").strip():
                    failures.append(f"{where}: empty next_steps.if_pass")
                if not (ns.get("if_fail") or "").strip():
                    failures.append(f"{where}: empty next_steps.if_fail")

            # -- Gate 5a: strategy ids must exist (hard) ------------------
            for sl in s.get("strategy_links") or []:
                lid = sl.get("strategy_id")
                if lid and valid_strategy_ids and lid not in valid_strategy_ids:
                    failures.append(f"{where}: unknown strategy_id {lid}")

            # -- Gate 5b: verbatim activity duplication (hard) ------------
            for a in s.get("activities") or []:
                key = (a.get("title") or "", a.get("instructions") or "")
                if key[0]:
                    prev = seen_activities.get(key)
                    if prev and prev.split(" (")[1] != where.split(" (")[1]:
                        failures.append(
                            f"{where}: activity '{key[0]}' duplicated verbatim from {prev}")
                    else:
                        seen_activities.setdefault(key, where)

            # -- Gate 1: model debt ---------------------------------------
            for sl in s.get("strategy_links") or []:
                why = (sl.get("why") or "").lower()
                for term in MODEL_TERMS:
                    if term in why and term not in text:
                        gate.append(
                            f"{where}: strategy link promises '{term}' but the lesson never uses it (Gate 1)")

            # -- Gate 2: ground-first worked example ----------------------
            steps = s.get("worked_example_script") or []
            if steps:
                first = (steps[0].get("kind") or "").lower()
                if first not in ("show", "ask"):
                    gate.append(
                        f"{where}: worked example opens with '{first}' — must open on a show/ask model step (Gate 2)")

            # -- Gate 3: games cap, never lead -----------------------------
            acts = s.get("activities") or []
            for i, a in enumerate(acts):
                if (a.get("type") == "game") and i < len(acts) - 1:
                    gate.append(
                        f"{where}: game '{a.get('title')}' in slot {i + 1} of {len(acts)} — games belong in the final slot (Gate 3)")

            # -- Gate 4: foundation anchor ---------------------------------
            if is_foundation and not any(t in text for t in ANCHOR_TERMS):
                gate.append(
                    f"{where}: foundation skill has no concrete representation anywhere in its lesson (Gate 4)")

    if warnings:
        print(f"GATE WARNINGS ({len(warnings)}) — will fail under --strict:")
        for w in warnings:
            print("  ~", w)
    if failures:
        print(f"CONTENT VALIDATION FAILED ({len(failures)} issue(s)):")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    print("CONTENT VALIDATION PASSED" + (" (strict)" if strict else ""))


if __name__ == "__main__":
    main()
