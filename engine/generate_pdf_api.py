"""
CLI entry point for PDF generation. Called by the Next.js API route via subprocess.
Reads JSON args from stdin, writes PDF to the specified output path, prints the path to stdout.

Usage:
  echo '{"standard":"6.AF.3","format":"exit_ticket"}' | python engine/generate_pdf_api.py
"""

import json
import os
import sys
import random
import importlib

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.models import ProficiencyLevel, Difficulty
from engine.pdf_generator import (
    generate_exit_ticket_pdf,
    generate_mms_pdf,
    generate_proficiency_pdf,
)

# Map standard codes to stem class names
def get_stem_class(standard_code: str):
    """Dynamically import the stem class for a standard code."""
    # "6.AF.3" -> "stem_6af3" -> Stem6AF3
    parts = standard_code.lower().replace(".", "")
    module_name = f"engine.stems.stem_{parts}"
    class_name = f"Stem{parts.upper()}"
    # Handle casing: stem_7GM3 is actually stem_7GM3.py
    try:
        mod = importlib.import_module(module_name)
    except ModuleNotFoundError:
        # Try alternate casings (some files use uppercase like stem_7GM3)
        alt = f"engine.stems.stem_{standard_code.replace('.', '').replace(' ', '')}"
        mod = importlib.import_module(alt)
    return getattr(mod, class_name)


STANDARDS_TEXT = {}  # Lazy-loaded if needed


def get_questions(standard_code: str, seed: int | None = None):
    """Generate all question variants for a standard."""
    if seed is None:
        seed = random.randint(1, 100000)
    cls = get_stem_class(standard_code)
    stem = cls(seed=seed)
    return stem.generate_all_variants()


def filter_by_proficiency(questions, level_str: str):
    level_map = {
        "below": ProficiencyLevel.BELOW,
        "approaching": ProficiencyLevel.APPROACHING,
        "at": ProficiencyLevel.AT,
        "above": ProficiencyLevel.ABOVE,
    }
    level = level_map.get(level_str)
    if level is None:
        return questions
    return [q for q in questions if q.proficiency_level == level]


def filter_by_difficulty(questions, diff_str: str):
    diff_map = {
        "easy": Difficulty.EASY,
        "medium": Difficulty.MEDIUM,
        "difficult": Difficulty.DIFFICULT,
    }
    diff = diff_map.get(diff_str)
    if diff is None:
        return questions
    return [q for q in questions if q.difficulty == diff]


def main():
    raw = sys.stdin.read()
    params = json.loads(raw)

    standard = params["standard"]
    fmt = params.get("format", "exit_ticket")
    seed = params.get("seed")

    # Generate questions
    all_questions = get_questions(standard, seed)

    # Output directory
    tmp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    safe_standard = standard.replace(".", "_")
    output_path = os.path.join(tmp_dir, f"StruggleBus_{safe_standard}_{fmt}_{random.randint(1000,9999)}.pdf")

    standard_text = params.get("standard_text", "")

    if fmt == "exit_ticket":
        prof = params.get("exit_proficiency", "any")
        diff = params.get("exit_difficulty", "any")

        pool = all_questions
        if prof != "any":
            pool = filter_by_proficiency(pool, prof)
        if diff != "any":
            pool = filter_by_difficulty(pool, diff)

        if not pool:
            # Relax filters
            pool = all_questions

        question = random.choice(pool)
        generate_exit_ticket_pdf(question, output_path, standard_code=standard,
                                 standard_text=standard_text, include_answer_key=True)

    elif fmt == "mms":
        axis = params.get("mms_axis", "difficulty")
        per_tier = int(params.get("questions_per_tier", 1))

        if axis == "difficulty":
            tiers = [
                ("easy", filter_by_difficulty(all_questions, "easy")),
                ("medium", filter_by_difficulty(all_questions, "medium")),
                ("difficult", filter_by_difficulty(all_questions, "difficult")),
            ]
        else:
            tiers = [
                ("approaching", filter_by_proficiency(all_questions, "approaching")),
                ("at", filter_by_proficiency(all_questions, "at")),
                ("above", filter_by_proficiency(all_questions, "above")),
            ]

        questions_by_tier = []
        for name, pool in tiers:
            if pool:
                selected = random.sample(pool, min(per_tier, len(pool)))
                questions_by_tier.append((name, selected))

        if not questions_by_tier:
            print(json.dumps({"error": "No questions match the criteria"}), file=sys.stderr)
            sys.exit(1)

        generate_mms_pdf(questions_by_tier, output_path, standard_code=standard,
                         standard_text=standard_text, mms_axis=axis, include_answer_key=True)

    elif fmt == "proficiency":
        level = params.get("proficiency_level", "at")
        count = int(params.get("prof_count", 4))

        pool = filter_by_proficiency(all_questions, level)
        if not pool:
            pool = all_questions

        selected = random.sample(pool, min(count, len(pool)))
        generate_proficiency_pdf(selected, output_path, standard_code=standard,
                                 standard_text=standard_text, proficiency_level=level,
                                 include_answer_key=True)

    else:
        print(json.dumps({"error": f"Unknown format: {fmt}"}), file=sys.stderr)
        sys.exit(1)

    # Print the output path so the caller can find the file
    print(json.dumps({"path": output_path, "size": os.path.getsize(output_path)}))


if __name__ == "__main__":
    main()
