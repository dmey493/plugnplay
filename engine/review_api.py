"""
CLI entry points for the review flow:
  - review-generate: Returns JSON with selected questions
  - swap-question: Returns a replacement question
  - review-pdf: Generates PDF from specific question IDs

Usage:
  echo '{"action":"review-generate","standard":"6.AF.3","format":"mms",...}' | python engine/review_api.py
"""

import json
import os
import sys
import random
import importlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.models import ProficiencyLevel, Difficulty
from engine.pdf_generator import (
    generate_exit_ticket_pdf,
    generate_mms_pdf,
    generate_proficiency_pdf,
)

PROF_MAP = {
    "below": ProficiencyLevel.BELOW,
    "approaching": ProficiencyLevel.APPROACHING,
    "at": ProficiencyLevel.AT,
    "above": ProficiencyLevel.ABOVE,
}
DIFF_MAP = {
    "easy": Difficulty.EASY,
    "medium": Difficulty.MEDIUM,
    "difficult": Difficulty.DIFFICULT,
}


def get_stem_class(standard_code: str):
    parts = standard_code.lower().replace(".", "")
    module_name = f"engine.stems.stem_{parts}"
    class_name = f"Stem{parts.upper()}"
    try:
        mod = importlib.import_module(module_name)
    except ModuleNotFoundError:
        alt = f"engine.stems.stem_{standard_code.replace('.', '')}"
        mod = importlib.import_module(alt)
    return getattr(mod, class_name)


def get_questions(standard_code, seed=None):
    if seed is None:
        seed = random.randint(1, 100000)
    cls = get_stem_class(standard_code)
    stem = cls(seed=seed)
    return stem.generate_all_variants(), seed


def question_to_dict(q):
    return {
        "question_id": q.question_id,
        "stem_text": q.stem_text,
        "answer_text": q.answer_text,
        "proficiency_level": q.proficiency_level.name.lower(),
        "difficulty": q.difficulty.name.lower(),
        "item_type": q.item_type.name if hasattr(q.item_type, 'name') else str(q.item_type),
        "stem_index": q.stem_index,
        "variant_index": q.variant_index,
    }


def filter_prof(questions, level_str):
    level = PROF_MAP.get(level_str)
    return [q for q in questions if q.proficiency_level == level] if level else questions


def filter_diff(questions, diff_str):
    diff = DIFF_MAP.get(diff_str)
    return [q for q in questions if q.difficulty == diff] if diff else questions


def filter_stems(questions, stems):
    """Narrow to the stems that practise one intervention skill.

    `stems` is the skill's `engine_stems` list from
    web/content/skills/<STD>.json - 1-based indices into this standard's stem
    module. An empty or missing list means "no skill picked", so nothing is
    filtered. An unknown index yields an empty pool, which every caller falls
    back out of rather than returning zero questions.
    """
    if not stems:
        return questions
    wanted = {int(i) for i in stems}
    return [q for q in questions if q.stem_index in wanted]


def handle_review_generate(params):
    standard = params["standard"]
    fmt = params.get("format", "exit_ticket")
    seed = params.get("seed")

    all_questions, used_seed = get_questions(standard, seed)

    result = {
        "format": fmt,
        "standard": standard,
        "seed": used_seed,
        "questions": [],
    }

    if fmt == "exit_ticket":
        prof = params.get("exit_proficiency", "any")
        diff = params.get("exit_difficulty", "any")
        stems = params.get("stems")
        pool = all_questions
        # A picked skill IS the proficiency choice - its stems already sit at
        # one level - so the skill filter supersedes exit_proficiency rather
        # than stacking with it.
        if stems:
            narrowed = filter_stems(pool, stems)
            if narrowed:
                pool = narrowed
        elif prof != "any":
            pool = filter_prof(pool, prof)
        if diff != "any":
            narrowed = filter_diff(pool, diff)
            if narrowed:
                pool = narrowed
        if not pool:
            pool = all_questions
        q = random.choice(pool)
        result["questions"] = [question_to_dict(q)]

    elif fmt == "mms":
        axis = params.get("mms_axis", "difficulty")
        per_tier = int(params.get("questions_per_tier", 1))

        if axis == "difficulty":
            tier_defs = [("Mild", "easy"), ("Medium", "medium"), ("Spicy", "difficult")]
            tiers_data = {}
            questions_list = []
            idx = 0
            for label, level in tier_defs:
                pool = filter_diff(all_questions, level)
                if pool:
                    selected = random.sample(pool, min(per_tier, len(pool)))
                    tier_indices = []
                    for q in selected:
                        questions_list.append(question_to_dict(q))
                        tier_indices.append(idx)
                        idx += 1
                    tiers_data[label] = tier_indices
            result["questions"] = questions_list
            result["tiers"] = tiers_data
            result["mms_axis"] = axis
        else:
            tier_defs = [("Mild", "approaching"), ("Medium", "at"), ("Spicy", "above")]
            tiers_data = {}
            questions_list = []
            idx = 0
            for label, level in tier_defs:
                pool = filter_prof(all_questions, level)
                if pool:
                    selected = random.sample(pool, min(per_tier, len(pool)))
                    tier_indices = []
                    for q in selected:
                        questions_list.append(question_to_dict(q))
                        tier_indices.append(idx)
                        idx += 1
                    tiers_data[label] = tier_indices
            result["questions"] = questions_list
            result["tiers"] = tiers_data
            result["mms_axis"] = axis

    elif fmt == "proficiency":
        level = params.get("proficiency_level", "at")
        count = int(params.get("prof_count", 4))
        stems = params.get("stems")
        # Same rule as the exit ticket: a picked skill replaces the level
        # dropdown, it does not narrow within it.
        pool = filter_stems(all_questions, stems) if stems else filter_prof(all_questions, level)
        if not pool:
            pool = all_questions
        selected = random.sample(pool, min(count, len(pool)))
        result["questions"] = [question_to_dict(q) for q in selected]

    return result


def handle_swap_question(params):
    standard = params["standard"]
    seed = params.get("seed", 42)
    question_id = params["question_id"]
    exclude_ids = set(params.get("exclude_ids", []))
    target_prof = params.get("proficiency_level")
    target_diff = params.get("difficulty")
    stems = params.get("stems")

    all_questions, _ = get_questions(standard, seed)

    # Find candidates matching proficiency + difficulty, excluding current selections
    candidates = [q for q in all_questions if q.question_id not in exclude_ids]
    # When the set was built for one skill, a swap has to stay inside that
    # skill - otherwise "Swap" quietly hands back a problem for a different
    # skill than the worksheet says it is practising.
    if stems:
        narrowed = filter_stems(candidates, stems)
        if narrowed:
            return question_to_dict(random.choice(narrowed))
        return {"error": "No replacement questions available"}
    if target_prof:
        narrowed = filter_prof(candidates, target_prof)
        if target_diff:
            narrowed2 = filter_diff(narrowed, target_diff)
            if narrowed2:
                candidates = narrowed2
            elif narrowed:
                candidates = narrowed

    if not candidates:
        return {"error": "No replacement questions available"}

    replacement = random.choice(candidates)
    return question_to_dict(replacement)


def handle_review_pdf(params):
    standard = params["standard"]
    fmt = params.get("format", "exit_ticket")
    seed = params.get("seed", 42)
    question_ids = set(params.get("question_ids", []))
    include_answer_key = params.get("include_answer_key", True)

    all_questions, _ = get_questions(standard, seed)
    id_to_q = {q.question_id: q for q in all_questions}

    # Rebuild the ordered question list from IDs
    selected = [id_to_q[qid] for qid in params.get("question_ids", []) if qid in id_to_q]
    if not selected:
        return {"error": "No matching questions found"}

    # System temp dir: always writable, including on read-only container
    # filesystems (e.g. Cloud Run, where only /tmp is guaranteed writable).
    import tempfile
    tmp_dir = tempfile.gettempdir()
    os.makedirs(tmp_dir, exist_ok=True)
    safe = standard.replace(".", "_")
    output_path = os.path.join(tmp_dir, f"review_{safe}_{fmt}_{random.randint(1000,9999)}.pdf")

    standard_text = params.get("standard_text", "")

    if fmt == "exit_ticket":
        generate_exit_ticket_pdf(selected[0], output_path, standard_code=standard,
                                 standard_text=standard_text, include_answer_key=include_answer_key)
    elif fmt == "mms":
        axis = params.get("mms_axis", "difficulty")
        # Accept tiers_by_id (question IDs grouped by tier) or fall back to index-based tiers
        tiers_by_id = params.get("tiers_by_id")
        if tiers_by_id:
            questions_by_tier = []
            for tier_name, qids in tiers_by_id.items():
                tier_qs = [id_to_q[qid] for qid in qids if qid in id_to_q]
                if tier_qs:
                    label = tier_name.lower()
                    questions_by_tier.append((label, tier_qs))
        else:
            tiers = params.get("tiers", {})
            questions_by_tier = []
            for tier_name, indices in tiers.items():
                tier_qs = [selected[i] for i in indices if i < len(selected)]
                if tier_qs:
                    label = tier_name.lower()
                    questions_by_tier.append((label, tier_qs))
        if not questions_by_tier:
            questions_by_tier = [("all", selected)]
        generate_mms_pdf(questions_by_tier, output_path, standard_code=standard,
                         standard_text=standard_text, mms_axis=axis, include_answer_key=include_answer_key)
    elif fmt == "proficiency":
        level = params.get("proficiency_level", "at")
        generate_proficiency_pdf(selected, output_path, standard_code=standard,
                                 standard_text=standard_text, proficiency_level=level,
                                 include_answer_key=include_answer_key)

    return {"path": output_path, "size": os.path.getsize(output_path)}


def main():
    raw = sys.stdin.read()
    params = json.loads(raw)
    action = params.get("action", "review-generate")

    if action == "review-generate":
        result = handle_review_generate(params)
    elif action == "swap-question":
        result = handle_swap_question(params)
    elif action == "review-pdf":
        result = handle_review_pdf(params)
    else:
        result = {"error": f"Unknown action: {action}"}

    print(json.dumps(result))


if __name__ == "__main__":
    main()
