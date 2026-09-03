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

Session Sheet v4 gate (thinking moves + full backward fade). Applies only to
skills that carry the new fields (guided_example / worked_solution checks), so
legacy v3 content is untouched:
  Gate 6  a) every `check` uses a move from the closed menu, with a
             non-empty prompt (<=110 chars) and answer; at most one check
             per step; a skill with guided_example has >=1 check.
          b) (strict-warn) no name_trap check on the worked solution, or a
             name_trap that shares no content words with canonical_error.
          b2) (strict-warn) no blank-step hint in faded/guided cues a move
             by name — the through-line fade needs the cue.
          c) `given` flags form a true-prefix in faded_example and
             guided_example; faded has >=1 given and >=1 blank. guided may
             give nothing -- it hands over every step with a clue per line.
          d) fade ladder — guided gives strictly fewer steps than faded;
             faded fades ONLY the last step; step counts match the
             worked_solution.
          e) a Find the Mistake source exists: >=1 practice problem of
             type error_analysis with shown_work.

Item-spec alignment gate:
  Gate 7  PLD coverage — a standard that carries `pld_descriptors` (the
          proficiency-level descriptors lifted from the ILEARN item
          specification) must have at least one skill tagged with each band
          the spec actually describes. A band the spec defines but no skill
          teaches is an intervention that cannot move a student across that
          proficiency line. Reports as a warning; hard-fails under --strict.

Run:  python engine/validate_content.py [--strict]
Wire into CI as a gate before shipping content; authoring runs --strict.
"""
import json, io, glob, os, re, sys


def _find_root():
    """Walk up from this file until we find the repo root (the dir holding
    BOTH skill mirrors). The old dirname(dirname(__file__)) broke for the
    web/engine copy — it globbed web/web/content/skills, matched nothing,
    and 'passed' vacuously."""
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        if (os.path.isdir(os.path.join(d, "web", "content", "skills"))
                and os.path.isdir(os.path.join(d, "authoring", "data", "skills"))):
            return d
        d = os.path.dirname(d)
    sys.exit("validate_content: could not locate repo root (web/content/skills "
             "+ authoring/data/skills) above " + os.path.abspath(__file__))


ROOT = _find_root()
WEB = os.path.join(ROOT, "web", "content", "skills")
AUTH = os.path.join(ROOT, "authoring", "data", "skills")
STRATS = os.path.join(ROOT, "web", "content", "strategies", "math")

# Gate 7: the ILEARN proficiency bands, low to high. Mirrors PLD_BAND_ORDER
# in web/src/lib/intervention/skills.ts.
PLD_BANDS = ("below", "approaching", "at", "above")

# Gate 8: stems that point at a specific object printed on the page. Kept
# deliberately narrow — a definite article or an explicit "shows"/"below".
# "Name a number between 1/2 and 1 on the number line" describes the task
# rather than referring to a drawing, and owes no render_data.
# Gate 9: a stem that tells the student to choose must give them something to
# choose from. Options can live in a `choices` list or be listed inline.
# "Which expression does it model?" implies a set to pick from just as much as
# "Select the expression", so the pattern covers both. The first version only
# matched select/choose/circle/pick and missed eight shipped stems.
ASKS_TO_CHOOSE = re.compile(
    r"\b(select|choose|circle the|pick the|identify which"
    r"|which (?:of|expression|equation|statement"
    r"|explanation|answer|product|model|form))\b", re.I)
# Deliberately NOT matched: "which one is farther left", "say which one is the
# distance". Those point back at values the student just produced in an earlier
# step, so the options are in their own work and no list is owed.
# Inline options look like a comma-separated run, an "A or B" pair, or a
# "from the set ..." preamble.
LISTS_OPTIONS = re.compile(
    r"(?:[:,]\s*[^,:]+,\s*[^,:]+)"     # at least two comma-separated options
    r"|\bor\b"                          # "... : A or B?"
    r"|\bfrom the set\b"
    r"|\bwhich of\s+[^,]+,", re.I)

PROMISES_FIGURE = re.compile(
    r"\b(the number ?line|the model|the grid|the table|the figure|the diagram"
    r"|number ?line (shows|below)|model shows|listed in the table|shown below"
    r"|the point shown|shows only the point)", re.I)

# Gate 6a: the closed thinking-moves menu (mirror of THINKING_MOVES in
# generate_skill_packet.py and the glossary in
# authoring/directives/skill_authoring/thinking_moves.md).
THINKING_MOVES = {
    "spot_signal": "Spot the Signal",
    "show_it":     "Show It",
    "call_it":     "Call It",
    "say_why":     "Say Why",
    "check_it":    "Check It",
    "name_trap":   "Name the Trap",
}
# Words too generic to count as shared content between a name_trap check and
# the canonical error (Gate 6b overlap test).
_STOPWORDS = {
    "the", "a", "an", "is", "are", "of", "to", "in", "on", "and", "or", "not",
    "it", "its", "that", "this", "with", "for", "as", "at", "by", "be", "was",
    "student", "students", "answer", "number", "value", "problem", "wrong",
}

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


def _content_words(text):
    """Lowercased word set minus stopwords, for the Gate 6b overlap test."""
    words = "".join(ch if ch.isalnum() else " " for ch in text.lower()).split()
    return {w for w in words if len(w) > 2 and w not in _STOPWORDS}


def lesson_text(s):
    """All teacher/student-facing lesson prose for one skill, lowercased."""
    parts = [s.get("i_do_script") or ""]
    for st in s.get("worked_example_script") or []:
        parts.append(st.get("text") or "")
    # Session Sheet v4 moved the modelling into the ladder, so a skill can
    # enact a representation there and still read as model debt to Gate 1.
    # Count the ladder's own prose, its micro-check prompts, and the TYPE of
    # any figure it draws ("number_line_point" contains "number line").
    for blk in ("worked_solution", "faded_example", "guided_example"):
        b = s.get(blk) or {}
        parts.append(b.get("stem") or "")
        rd = b.get("render_data") or {}
        parts.append(str(rd.get("type") or "").replace("_", " "))
        for st in b.get("steps") or []:
            parts.append(st.get("math") or "")
            parts.append(st.get("annotation") or "")
            ck = st.get("check") or {}
            parts.append(ck.get("prompt") or "")
            parts.append(ck.get("answer") or "")
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

    skill_files = sorted(glob.glob(os.path.join(WEB, "*.json")))
    if not skill_files:
        sys.exit(f"validate_content: no skill files found in {WEB} -- "
                 "refusing to pass vacuously")

    for wf in skill_files:
        base = os.path.basename(wf)
        wj = json.load(io.open(wf, encoding="utf-8"))
        cf = os.path.join(AUTH, base)
        if not os.path.exists(cf):
            failures.append(f"{base}: missing authoring mirror")
            continue
        cj = json.load(io.open(cf, encoding="utf-8"))
        if wj != cj:
            failures.append(f"{base}: web/authoring mirrors differ")

        # -- Gate 7: item-spec PLD coverage ---------------------------
        # Bands are only checked when the spec describes them, so standards
        # without pld_descriptors (not yet mapped to an item spec) are silent
        # rather than noisy.
        pld_desc = wj.get("pld_descriptors") or {}
        described = [b for b in PLD_BANDS if (pld_desc.get(b) or "").strip()]
        if described:
            tagged = {s.get("pld_band") for s in wj.get("skills", [])}
            for band in described:
                if band not in tagged:
                    gate.append(
                        f"{base}: item spec describes the '{band}' proficiency "
                        f"level but no skill is tagged pld_band '{band}' (Gate 7)")

        for s in wj.get("skills", []):
            sid = s.get("skill_id", "?")
            where = f"{sid} ({base})"
            is_foundation = s.get("column") == "foundation"
            text = lesson_text(s)

            # -- Gate 9: a select-type stem must present its options ------
            # "Select the expressions equivalent to (-4/9)(3/4)" printed no
            # expressions, so the student was asked to choose from nothing.
            # Options may be a `choices` list OR listed inline in the stem
            # ("From the set 3, 33, 41, 57, 89, select all the primes").
            for blk in ("worked_solution", "faded_example", "guided_example"):
                b = s.get(blk) or {}
                stem = b.get("stem") or ""
                if not ASKS_TO_CHOOSE.search(stem):
                    continue
                if b.get("choices") or LISTS_OPTIONS.search(stem):
                    continue
                gate.append(
                    f"{where}: {blk} asks the student to select but prints no "
                    f"options (Gate 9)")

            # -- Gate 8: promised figures must exist ----------------------
            # A stem that points at a specific printed object ("the number
            # line shows only the point -4", "the model shows 65% shaded",
            # "listed in the table") is unanswerable when nothing is drawn,
            # and it silently turns a scaffolded below-grade item into a
            # from-scratch one. Only DEFINITE references count: "name a
            # number between 1/2 and 1 on the number line" describes the
            # task and owes no drawing.
            for blk in ("worked_solution", "faded_example", "guided_example"):
                b = s.get(blk) or {}
                if PROMISES_FIGURE.search(b.get("stem") or "") and not b.get("render_data"):
                    gate.append(
                        f"{where}: {blk} stem names a printed figure but has "
                        f"no render_data (Gate 8)")
            for pool in ("sample_items", "practice_problems"):
                for i, it in enumerate(s.get(pool) or []):
                    if PROMISES_FIGURE.search(it.get("stem") or "") and not it.get("render_data"):
                        gate.append(
                            f"{where}: {pool}[{i}] stem names a printed figure "
                            f"but has no render_data (Gate 8)")

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

            # -- Gate 6: Session Sheet v4 (micro-checks + backward fade) ---
            ws = s.get("worked_solution") or {}
            ws_steps = ws.get("steps") or []
            checks = [st.get("check") for st in ws_steps if st.get("check")]
            guided = s.get("guided_example")
            faded = s.get("faded_example")
            if guided or checks:
                # 6a — checks are well-formed and on-menu.
                for n, st in enumerate(ws_steps, start=1):
                    c = st.get("check")
                    if not c:
                        continue
                    if c.get("move") not in THINKING_MOVES:
                        failures.append(
                            f"{where}: step {n} check move '{c.get('move')}' not in the thinking-moves menu (Gate 6a)")
                    prompt = (c.get("prompt") or "").strip()
                    if not prompt:
                        failures.append(f"{where}: step {n} check has an empty prompt (Gate 6a)")
                    elif len(prompt) > 110:
                        failures.append(
                            f"{where}: step {n} check prompt is {len(prompt)} chars (max 110) (Gate 6a)")
                    if not str(c.get("answer") or "").strip():
                        failures.append(f"{where}: step {n} check has an empty answer (Gate 6a)")
                if guided and not checks:
                    failures.append(
                        f"{where}: has guided_example but no micro-checks on the worked solution (Gate 6a)")

                # 6b (strict-warn) — a name_trap should exist and echo the
                # canonical error.
                err = s.get("canonical_error") or {}
                traps = [c for c in checks if c and c.get("move") == "name_trap"]
                if not traps:
                    gate.append(
                        f"{where}: no Name the Trap check on the worked solution (Gate 6b)")
                elif not (err.get("pattern") or "").strip():
                    gate.append(
                        f"{where}: name_trap check but empty canonical_error.pattern (Gate 6b)")
                else:
                    err_words = _content_words(
                        (err.get("pattern") or "") + " " + (err.get("example") or ""))
                    for c in traps:
                        trap_words = _content_words(
                            (c.get("prompt") or "") + " " + str(c.get("answer") or ""))
                        if err_words and not (trap_words & err_words):
                            gate.append(
                                f"{where}: name_trap check shares no content words with the canonical error (Gate 6b)")

                # 6b2 (strict-warn) — blank-step hints cue a move by name.
                for bname, block in (("faded_example", faded),
                                     ("guided_example", guided)):
                    if not block:
                        continue
                    hints = " ".join(
                        (st.get("annotation") or "")
                        for st in block.get("steps") or [] if not st.get("given")).lower()
                    if hints and not any(mv.lower() in hints
                                         for mv in THINKING_MOVES.values()):
                        gate.append(
                            f"{where}: no {bname} blank-step hint cues a thinking move by name (Gate 6b2)")

                # 6c — fade shape: givens are a true-prefix, >=1 given.
                def _givens(block):
                    return [bool(st.get("given"))
                            for st in (block.get("steps") or [])]
                for bname, block in (("faded_example", faded),
                                     ("guided_example", guided)):
                    if not block:
                        continue
                    g = _givens(block)
                    first_blank = g.index(False) if False in g else len(g)
                    if any(g[first_blank:]):
                        failures.append(
                            f"{where}: {bname} gives a step after a blank -- fade from the bottom (Gate 6c)")
                    # guided_example may give nothing at all: "Let's try
                    # together" hands the student every step with a clue under
                    # each line. faded_example still needs its given prefix.
                    if bname == "faded_example" and not any(g):
                        failures.append(f"{where}: {bname} has no given step (Gate 6c)")
                if faded and all(_givens(faded)):
                    failures.append(f"{where}: faded_example has no blank step (Gate 6c)")

                # 6d — the ladder itself.
                if guided:
                    if not faded:
                        failures.append(f"{where}: guided_example without a faded_example (Gate 6d)")
                    else:
                        fg, gg = _givens(faded), _givens(guided)
                        if sum(gg) >= sum(fg):
                            failures.append(
                                f"{where}: guided_example gives {sum(gg)} steps, faded gives {sum(fg)} -- guided must give strictly fewer (Gate 6d)")
                        if fg.count(False) != 1:
                            failures.append(
                                f"{where}: faded_example has {fg.count(False)} blanks -- must fade exactly the last step (Gate 6d)")
                        if ws_steps and not (len(ws_steps) == len(fg) == len(gg)):
                            failures.append(
                                f"{where}: step counts differ (worked {len(ws_steps)} / faded {len(fg)} / guided {len(gg)}) (Gate 6d)")

                # 6e — the Find the Mistake source.
                if guided and not any(
                        p.get("type") == "error_analysis" and p.get("shown_work")
                        for p in s.get("practice_problems") or []):
                    failures.append(
                        f"{where}: no error_analysis practice problem with shown_work (Find the Mistake source) (Gate 6e)")

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
