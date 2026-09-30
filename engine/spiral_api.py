"""
CLI entry points for spiral review (several standards on one sheet, by week):
  - spiral-generate:        pick every week's problems for a set of standards
  - spiral-regenerate-week: new problems for one week, keeping the other weeks
  - spiral-swap:            replace one problem, optionally at a different level
  - spiral-pdf:             draw the weeks, plus the answer key, to a PDF

Usage:
  echo '{"action":"spiral-generate","grade":7,...}' | python engine/spiral_api.py

A problem is rebuilt from (standard, seed, question_id), as in the single-
standard review flow (review_api.py). A question_id repeats across seeds, so a
problem's identity here is its uid, "standard|seed|question_id". Some pools
also hold the same content under two variants, so "no repeats" also compares
a fingerprint of what the student actually sees.
"""

import contextlib
import hashlib
import json
import os
import random
import sys
import tempfile
import zlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.review_api import PROF_MAP, get_stem_class
from engine.spiral_pdf import (
    LEVEL_LABELS,
    Measurer,
    SpiralItem,
    fit_summary,
    fit_week,
    render_spiral_pdf,
)

LEVELS = ("below", "approaching", "at", "above")
MAX_PER_WEEK = 8
MAX_WEEKS = 8
# When a level runs out of fresh problems, draw from the same stems at these
# extra seeds before repeating any content.
EXTRA_SEED_STEP = 7777
EXTRA_POOLS = 2
# Where to look when a standard has no problems at the requested level.
LEVEL_FALLBACK = {
    "below": ("approaching", "at"),
    "approaching": ("below", "at"),
    "at": ("approaching", "above"),
    "above": ("at",),
}


class BadRequest(Exception):
    pass


def standard_seed(set_seed, code):
    return 1 + (int(set_seed) * 7919 + zlib.crc32(code.encode())) % 99991


def _renderable(q):
    # shaded_grid figures are not drawn by any layout yet; the problem would
    # print without the grid it asks about.
    return (getattr(q, "render_data", None) or {}).get("type") != "shaded_grid"


class Pools:
    """Every (standard, seed) pool is built once per process."""

    def __init__(self):
        self._pools = {}
        self._by_id = {}
        self._fps = {}

    def pool(self, code, seed):
        key = (code, int(seed))
        if key not in self._pools:
            cls = get_stem_class(code)
            qs = [q for q in cls(seed=int(seed)).generate_all_variants() if _renderable(q)]
            self._pools[key] = qs
            self._by_id[key] = {q.question_id: q for q in qs}
        return self._pools[key]

    def at_level(self, code, seed, level):
        want = PROF_MAP[level]
        return [q for q in self.pool(code, seed) if q.proficiency_level == want]

    def lookup(self, code, seed, question_id):
        self.pool(code, seed)
        return self._by_id[(code, int(seed))].get(question_id)

    def fingerprint(self, code, seed, q):
        key = (code, int(seed), q.question_id)
        fp = self._fps.get(key)
        if fp is None:
            payload = "\x1f".join([
                q.stem_text or "",
                "|".join(sorted((c.text or "") for c in (q.choices or []))),
                "|".join((p.prompt or "") for p in (q.parts or [])),
                json.dumps(getattr(q, "render_data", None) or {},
                           sort_keys=True, default=str),
            ])
            fp = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]
            self._fps[key] = fp
        return fp

    def stems_at(self, code, seed, level):
        return sorted({q.stem_index for q in self.at_level(code, seed, level)})


def uid_of(code, seed, question_id):
    return f"{code}|{int(seed)}|{question_id}"


def problem_dict(pools, code, seed, q, position):
    return {
        "uid": uid_of(code, seed, q.question_id),
        "standard": code,
        "seed": int(seed),
        "question_id": q.question_id,
        "position": position,
        "proficiency_level": q.proficiency_level.name.lower(),
        "difficulty": q.difficulty.name.lower(),
        "item_type": q.item_type.name if hasattr(q.item_type, "name") else str(q.item_type),
        "stem_index": q.stem_index,
        "stem_text": q.stem_text,
        "answer_text": q.answer_text,
        "has_figure": bool(getattr(q, "render_data", None)),
        "fingerprint": pools.fingerprint(code, seed, q),
    }


def pick_problem(pools, code, level, base_seed, stem_order, taken_uids,
                 taken_fps, salt):
    """The first problem, in stem preference order, that is new by id and by
    content. Returns (seed, question, note) or None; note is None, or
    "pool_extended" / "content_repeat" when it had to reach further.
    """
    for allow_repeat in (False, True):
        for k in range(EXTRA_POOLS + 1):
            seed = int(base_seed) + EXTRA_SEED_STEP * k
            by_stem = {}
            for q in pools.at_level(code, seed, level):
                by_stem.setdefault(q.stem_index, []).append(q)
            order = [s for s in stem_order if s in by_stem]
            order += [s for s in sorted(by_stem) if s not in order]
            for s in order:
                variants = list(by_stem[s])
                random.Random(f"{salt}|{seed}|{s}").shuffle(variants)
                for q in variants:
                    if uid_of(code, seed, q.question_id) in taken_uids:
                        continue
                    if not allow_repeat and pools.fingerprint(code, seed, q) in taken_fps:
                        continue
                    note = None
                    if allow_repeat:
                        note = "content_repeat"
                    elif k > 0:
                        note = "pool_extended"
                    return seed, q, note
    return None


def _validate_set(params):
    try:
        grade = int(params.get("grade"))
    except (TypeError, ValueError):
        raise BadRequest("Pick a grade.")
    if grade not in (6, 7, 8):
        raise BadRequest("Grade must be 6, 7 or 8.")
    weeks = int(params.get("weeks", 1))
    if not 1 <= weeks <= MAX_WEEKS:
        raise BadRequest(f"Build between 1 and {MAX_WEEKS} weeks.")
    start_week = int(params.get("start_week", 1))
    if not 1 <= start_week <= 99:
        raise BadRequest("The starting week must be between 1 and 99.")
    standards = params.get("standards") or []
    if not standards:
        raise BadRequest("Pick at least one standard.")
    seen, total, cleaned = set(), 0, []
    for s in standards:
        code = str(s.get("code", ""))
        level = str(s.get("level", "at"))
        count = int(s.get("count", 1))
        if not code.startswith(f"{grade}.") or code in seen:
            raise BadRequest(f"{code or 'A standard'} does not belong on this sheet.")
        if level not in LEVELS:
            raise BadRequest(f"Unknown level {level} for {code}.")
        if count not in (1, 2):
            raise BadRequest(f"{code} can have 1 or 2 problems.")
        seen.add(code)
        total += count
        cleaned.append({"code": code, "level": level, "count": count})
    if total > MAX_PER_WEEK:
        raise BadRequest(f"A week holds at most {MAX_PER_WEEK} problems.")
    return grade, weeks, start_week, cleaned


def _week_items(pools, week):
    """SpiralItems for a week sent back by the client, in print order."""
    items, missing = [], []
    for i, ref in enumerate(week.get("questions", []), 1):
        code, seed, qid = ref["standard"], int(ref["seed"]), ref["question_id"]
        q = pools.lookup(code, seed, qid)
        if q is None:
            missing.append(f"{code} {qid}")
            continue
        items.append(SpiralItem(question=q, standard=code,
                                level=q.proficiency_level.name.lower(),
                                uid=uid_of(code, seed, qid), position=i))
    if missing:
        raise BadRequest("These problems could not be rebuilt: " + ", ".join(missing))
    return items


def _fit(pools, measurer, week):
    items = _week_items(pools, week)
    return fit_summary(fit_week(items, measurer)) if items else None


def handle_generate(params, pools, measurer):
    grade, weeks, start_week, standards = _validate_set(params)
    set_seed = int(params.get("set_seed") or random.randint(1, 10**6))
    warnings = []

    # Print order: every standard's first problem, then the second problems.
    # A standard keeps the same spots every week, and its two problems are
    # spaced apart rather than side by side.
    slots = [(si, 0) for si in range(len(standards))]
    slots += [(si, 1) for si, s in enumerate(standards) if s["count"] == 2]

    info = []
    for s in standards:
        code = s["code"]
        seed = standard_seed(set_seed, code)
        try:
            pools.pool(code, seed)
        except Exception as exc:  # a stem module that fails to build
            raise BadRequest(f"{code} could not be generated ({exc}).")
        level_used = next((lv for lv in (s["level"],) + LEVEL_FALLBACK[s["level"]]
                           if pools.at_level(code, seed, lv)), None)
        if level_used is None:
            raise BadRequest(f"{code} has no printable problems yet.")
        if level_used != s["level"]:
            warnings.append({
                "code": "level_fallback", "standard": code,
                "message": f"{code} has no {LEVEL_LABELS[s['level']]} problems, "
                           f"so it uses {LEVEL_LABELS[level_used]}."})
        stems = pools.stems_at(code, seed, level_used)
        offset = random.Random(f"{set_seed}|{code}").randrange(len(stems))
        info.append({**s, "seed": seed, "level_used": level_used,
                     "stems": stems, "offset": offset,
                     "taken_uids": set(), "taken_fps": set()})

    out_weeks = []
    for w in range(weeks):
        questions = []
        for position, (si, slot) in enumerate(slots, 1):
            st = info[si]
            k = len(st["stems"])
            start = (st["offset"] + w * st["count"] + slot) % k
            stem_order = st["stems"][start:] + st["stems"][:start]
            got = pick_problem(pools, st["code"], st["level_used"], st["seed"],
                               stem_order, st["taken_uids"], st["taken_fps"],
                               salt=f"{set_seed}|{st['code']}|w{w}|s{slot}")
            if got is None:
                raise BadRequest(f"Ran out of {st['code']} problems.")
            seed, q, note = got
            st["taken_uids"].add(uid_of(st["code"], seed, q.question_id))
            st["taken_fps"].add(pools.fingerprint(st["code"], seed, q))
            if note:
                warnings.append({"code": note, "standard": st["code"],
                                 "week_number": start_week + w})
            questions.append(problem_dict(pools, st["code"], seed, q, position))
        week = {"week_number": start_week + w, "questions": questions}
        week["fit"] = _fit(pools, measurer, week)
        out_weeks.append(week)

    return {
        "grade": grade,
        "set_seed": set_seed,
        "start_week": start_week,
        "standards": [{
            "code": st["code"], "level": st["level"], "level_used": st["level_used"],
            "count": st["count"], "seed": st["seed"],
            "stem_count": len(st["stems"]),
        } for st in info],
        "weeks": out_weeks,
        "warnings": _dedupe(warnings),
    }


def _dedupe(warnings):
    seen, out = set(), []
    for w in warnings:
        key = (w.get("code"), w.get("standard"), w.get("week_number"))
        if key not in seen:
            seen.add(key)
            out.append(w)
    return out


def _plan_weeks(params):
    weeks = (params.get("plan") or {}).get("weeks") or []
    if not weeks:
        raise BadRequest("There is no sheet to change.")
    return weeks


def _taken(pools, weeks, code):
    """Every uid and fingerprint the plan already uses for one standard."""
    uids, fps = set(), set()
    for wk in weeks:
        for ref in wk.get("questions", []):
            if ref["standard"] != code:
                continue
            seed = int(ref["seed"])
            uids.add(uid_of(code, seed, ref["question_id"]))
            q = pools.lookup(code, seed, ref["question_id"])
            if q is not None:
                fps.add(pools.fingerprint(code, seed, q))
    return uids, fps


def _stem_order(pools, weeks, code, seed, level, this_week, salt):
    """Stems this standard has not used this week first, then the least used."""
    stems = pools.stems_at(code, seed, level)
    used_all, used_here = {}, set()
    for wk in weeks:
        for ref in wk.get("questions", []):
            if ref["standard"] != code:
                continue
            q = pools.lookup(code, int(ref["seed"]), ref["question_id"])
            if q is None:
                continue
            used_all[q.stem_index] = used_all.get(q.stem_index, 0) + 1
            if wk.get("week_number") == this_week:
                used_here.add(q.stem_index)
    rng = random.Random(salt)
    tiebreak = {s: rng.random() for s in stems}
    return sorted(stems, key=lambda s: (s in used_here, used_all.get(s, 0), tiebreak[s]))


def _find_week(weeks, week_number):
    for wk in weeks:
        if int(wk.get("week_number")) == int(week_number):
            return wk
    raise BadRequest(f"Week {week_number} is not on this sheet.")


def handle_regenerate_week(params, pools, measurer):
    weeks = _plan_weeks(params)
    week = _find_week(weeks, params.get("week_number"))
    nonce = params.get("nonce") or random.randint(1, 10**9)
    others = [wk for wk in weeks if wk is not week]

    # Each spot keeps its standard and its current level.
    current = _week_items(pools, week)
    new_refs, questions, warnings = [], [], []
    for it in current:
        code = it.standard
        seed = int(it.uid.split("|")[1])
        # Avoid everything else in the plan and this week's current problems,
        # so every problem really is new.
        uids, fps = _taken(pools, others + [{"questions": new_refs}], code)
        cur_uids, cur_fps = _taken(pools, [week], code)
        order = _stem_order(pools, others + [{"week_number": week["week_number"],
                                                "questions": new_refs}],
                            code, seed, it.level, week["week_number"],
                            salt=f"{nonce}|{code}|{it.position}")
        got = pick_problem(pools, code, it.level, seed, order,
                           uids | cur_uids, fps | cur_fps,
                           salt=f"{nonce}|{code}|{it.position}")
        if got is None:
            # Nothing new is left; keep the problem that is already there.
            got = (seed, it.question, "content_repeat")
        new_seed, q, note = got
        if note:
            warnings.append({"code": note, "standard": code,
                             "week_number": week["week_number"]})
        ref = {"standard": code, "seed": new_seed, "question_id": q.question_id}
        new_refs.append(ref)
        questions.append(problem_dict(pools, code, new_seed, q, it.position))

    out = {"week_number": week["week_number"], "questions": questions}
    out["fit"] = _fit(pools, measurer, out)
    return {"week": out, "warnings": _dedupe(warnings)}


def handle_swap(params, pools, measurer):
    weeks = _plan_weeks(params)
    target = params.get("target") or {}
    week = _find_week(weeks, target.get("week_number"))
    position = int(target.get("position", 0))
    refs = week.get("questions", [])
    if not 1 <= position <= len(refs):
        raise BadRequest("That problem is not on this week's sheet.")
    ref = refs[position - 1]
    code, seed = ref["standard"], int(ref["seed"])
    current = pools.lookup(code, seed, ref["question_id"])
    if current is None:
        raise BadRequest("That problem could not be rebuilt.")
    level = params.get("level") or current.proficiency_level.name.lower()
    if level not in LEVELS:
        raise BadRequest(f"Unknown level {level}.")

    nonce = params.get("nonce") or random.randint(1, 10**9)
    uids, fps = _taken(pools, weeks, code)
    order = _stem_order(pools, weeks, code, seed, level, week["week_number"],
                        salt=f"{nonce}|{code}|{position}")
    # The level is strict: a swap never hands back a different level than asked.
    got = pick_problem(pools, code, level, seed, order, uids, fps,
                       salt=f"{nonce}|{code}|{position}")
    if got is None or got[2] == "content_repeat":
        return {"error": "no_candidates",
                "message": f"No other {LEVEL_LABELS[level]} problems left for {code}."}
    new_seed, q, _ = got
    question = problem_dict(pools, code, new_seed, q, position)

    swapped = dict(week)
    swapped["questions"] = list(refs)
    swapped["questions"][position - 1] = {"standard": code, "seed": new_seed,
                                          "question_id": q.question_id}
    return {"question": question, "level_used": level,
            "fit": _fit(pools, measurer, swapped)}


def handle_pdf(params, pools, measurer):
    try:
        grade = int(params.get("grade"))
    except (TypeError, ValueError):
        raise BadRequest("Pick a grade.")
    weeks_in = params.get("weeks") or []
    if not weeks_in:
        raise BadRequest("There is nothing to print yet.")
    weeks = [{"week_number": int(wk["week_number"]), "items": _week_items(pools, wk)}
             for wk in weeks_in]

    tmp_dir = tempfile.gettempdir()
    os.makedirs(tmp_dir, exist_ok=True)
    output_path = os.path.join(
        tmp_dir, f"spiral_g{grade}_{random.randint(100000, 999999)}.pdf")
    report = render_spiral_pdf(weeks, grade, output_path,
                               include_answer_key=bool(params.get("include_answer_key", True)),
                               measurer=measurer)
    return {"path": output_path, "size": os.path.getsize(output_path), "report": report}


HANDLERS = {
    "spiral-generate": handle_generate,
    "spiral-regenerate-week": handle_regenerate_week,
    "spiral-swap": handle_swap,
    "spiral-pdf": handle_pdf,
}


def main():
    raw = sys.stdin.read()
    out = sys.stdout
    # Stem modules print "Error generating ..." when a variant fails. Anything
    # printed while handling goes to stderr so stdout stays one JSON document.
    with contextlib.redirect_stdout(sys.stderr):
        try:
            params = json.loads(raw)
            handler = HANDLERS.get(params.get("action"))
            if handler is None:
                result = {"error": "bad_request",
                          "message": f"Unknown action: {params.get('action')}"}
            else:
                result = handler(params, Pools(), Measurer())
        except BadRequest as exc:
            result = {"error": "bad_request", "message": str(exc)}
        except Exception as exc:  # report, rather than a bare stack trace
            import traceback
            traceback.print_exc()
            result = {"error": "engine_error", "message": str(exc)}
    out.write(json.dumps(result))
    out.flush()


if __name__ == "__main__":
    main()
