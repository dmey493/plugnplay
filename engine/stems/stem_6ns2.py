"""
Stem generator for 6.NS.2:
  Explain how opposite signs of numbers indicate locations on opposite sides
  of 0 on the number line; identify the opposite of the opposite of a number.

Content Limits:
  - Limit to rational numbers
  - Items should not require the student to perform an operation
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: integers only
  Medium: positive/negative decimals OR fractions
  Difficult: variables

6 Stems from the Item Spec:
  Stem 1 (Below-MC):       Which pair of points represent opposite values? (DOK 1, easy)
  Stem 2 (Below-MC):       What is the opposite of the number at Point M? (DOK 1, easy)
  Stem 3 (Approaching-NR): A number is N units from 0 - write it and its opposite (DOK 1, easy)
  Stem 4 (At-NR):          What is the opposite of a decimal/fraction? (DOK 1, medium)
  Stem 5 (At-MS):          Select statements about locations of opposites on number line (DOK 2, easy)
  Stem 6 (Above-MC):       Opposite of the opposite of -b (DOK 2, difficult)
"""

import random
from fractions import Fraction

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.models import (
    GeneratedQuestion, QuestionChoice, QuestionPart,
    Difficulty, ProficiencyLevel, ItemType, RationalNumber,
    make_question_id
)
from engine.number_generators import NumberGenerator
from engine.context_pools import pick_name


STANDARD_CODE = "6.NS.2"
VARIANTS_PER_STEM = 20


# ============================================================
# HELPERS
# ============================================================

def _fmt(val):
    """Format a signed rational value for display."""
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return str(val.numerator)
        if abs(val) > 1:
            whole = int(val)
            part = abs(val) - abs(whole)
            sign = "-" if val < 0 else ""
            return f"{sign}{abs(whole)} {part.numerator}/{part.denominator}"
        return f"{val.numerator}/{val.denominator}"
    if isinstance(val, float):
        if val == int(val):
            return str(int(val))
        return f"{val:g}"
    return str(val)


def _fmt_opposite(val):
    """Return the formatted opposite of val."""
    if isinstance(val, Fraction):
        return _fmt(-val)
    if isinstance(val, float):
        return _fmt(-val)
    return _fmt(-val)


class Stem6NS2:
    """Generates ~20 variants for each of 6 stems from the 6.NS.2 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 1, Easy)
    # Which pair of points represent opposite values?
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        # Pick a value and its opposite - the correct opposite pair
        val = rng.randint(2, 7)
        # Pick other values for non-opposite points (all distinct positions)
        used = {val, -val}
        others = []
        while len(others) < 3:
            v = rng.randint(-7, 7)
            if v not in used and v != 0:
                used.add(v)
                others.append(v)

        # Build labeled points on the number line (like spec: J, K, L, M, N)
        labels = ['J', 'K', 'L', 'M', 'N']
        all_vals = [-val, val] + others
        all_vals.sort()
        point_data = [{"value": v, "label": labels[i]} for i, v in enumerate(all_vals)]

        # Find the labels for val and -val
        label_neg = next(p["label"] for p in point_data if p["value"] == -val)
        label_pos = next(p["label"] for p in point_data if p["value"] == val)

        # Number line ticks from -8 to 8
        ticks = list(range(-8, 9))

        correct_pair = f"{label_neg} and {label_pos}"
        # Build wrong pairs
        other_labels = [p["label"] for p in point_data if p["value"] not in (val, -val)]
        distractors = [
            f"{label_neg} and {other_labels[0]}",
            f"{other_labels[0]} and {label_pos}",
            f"{other_labels[1]} and {label_pos}" if len(other_labels) > 1 else f"{label_neg} and {other_labels[0]}",
        ]
        # Deduplicate
        distractors = list(dict.fromkeys(d for d in distractors if d != correct_pair))[:3]
        while len(distractors) < 3:
            pair = f"{other_labels[0]} and {other_labels[-1]}"
            if pair not in distractors and pair != correct_pair:
                distractors.append(pair)
            else:
                break

        all_options = [(correct_pair, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = (
            f"A number line is given. Each point represents a value.\n\n"
            f"Which pair of points represent opposite values?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=f"Opposite numbers are the same distance from 0 but on opposite sides. {-val} and {val} are opposites ({label_neg} and {label_pos}).",
            choices=choices, context_scenario="identify opposite pair",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx,
            render_data={
                "type": "number_line_point",
                "ticks": ticks,
                "points": point_data,
            }
        )

    # ================================================================
    # STEM 2: Below Proficiency - MC (DOK 1, Easy)
    # What is the opposite of the number at Point M?
    # ================================================================

    def stem2_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        val = rng.choice([-8, -6, -5, -4, -3, -2, 2, 3, 4, 5, 6, 8])
        opposite = -val

        # Number line with Point M shown visually
        ticks = list(range(-8, 9))

        stem_text = (
            f"A number line is given. Point M represents a value.\n\n"
            f"What is the opposite of the number located at Point M?"
        )

        correct = str(opposite)
        distractors = [
            str(val),
            "0",
            str(abs(val) * 2) if val > 0 else str(-abs(val) * 2),
        ]

        all_options = [(correct, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=f"Point M is at {val}. The opposite of {val} is {opposite}. Opposites are the same distance from 0 but on opposite sides.",
            choices=choices, context_scenario="opposite from number line",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx,
            render_data={
                "type": "number_line_point",
                "ticks": ticks,
                "points": [{"value": val, "label": "M"}],
            }
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - NR (DOK 1, Easy)
    # A number is N units from 0 - write it and its opposite
    # ================================================================

    def stem3_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        distance = rng.randint(1, 15)
        # Ask for the pair: the positive and negative version
        # Randomly ask for the negative one
        ask_negative = rng.choice([True, False])

        if ask_negative:
            stem_text = (
                f"A number is {distance} units to the left of 0 on a number line.\n\n"
                f"What number is it?"
            )
            answer = -distance
        else:
            stem_text = (
                f"A number is {distance} units to the right of 0 on a number line.\n\n"
                f"What is the opposite of this number?"
            )
            answer = -distance

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.EASY, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=str(answer), answer_latex=str(answer),
            worked_solution=f"A number {distance} units to the right of 0 is {distance}. Its opposite is {-distance}.",
            context_scenario="distance from zero",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At Proficiency - NR (DOK 1, Medium)
    # What is the opposite of a decimal/fraction?
    # ================================================================

    def stem4_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        use_decimal = rng.choice([True, False])

        if use_decimal:
            # Generate a decimal
            whole = rng.randint(0, 20)
            tenths = rng.randint(1, 99)
            val = whole + tenths / 100
            sign = rng.choice([-1, 1])
            val = sign * val
            display = _fmt(val)
            answer = _fmt(-val)
        else:
            # Generate a fraction
            num = rng.randint(1, 11)
            den = rng.choice([2, 3, 4, 5, 6, 8])
            while num >= den:
                num = rng.randint(1, den - 1)
            sign = rng.choice([-1, 1])
            frac = Fraction(sign * num, den)
            display = _fmt(frac)
            answer = _fmt(-frac)

        stem_text = f"What is the opposite of {display}?"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=f"The opposite of {display} is {answer}. Opposite numbers are on opposite sides of 0 at the same distance.",
            context_scenario="opposite of decimal/fraction",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: At Proficiency - MS (DOK 2, Easy)
    # Select statements about locations of opposites on number line
    # ================================================================

    def stem5_at_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        val = rng.randint(3, 50)

        # Correct statements (3 of these)
        correct_stmts = [
            f"{val} is located {val} units to the right of 0.",
            f"-{val} is located {val} units to the left of 0.",
            f"Both numbers are {val} units away from 0 in opposite directions.",
        ]

        # Wrong statements
        wrong_stmts = [
            f"{val} is located {val} units to the left of 0.",
            f"-{val} is located {val} units to the right of 0.",
            f"Both numbers are {val * 2} units away from 0 in the same direction.",
        ]

        # Build 6 options: 3 correct, 3 wrong
        all_options = [(s, True) for s in correct_stmts] + [(s, False) for s in wrong_stmts]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=text,
                is_correct=is_correct,
            ))

        correct_letters = sorted([c.key for c in choices if c.is_correct])
        answer_str = ", ".join(correct_letters)

        stem_text = (
            f"Select three statements that correctly explain the locations of "
            f"-{val} and {val} on a number line."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MS,
                               Difficulty.EASY, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MS,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_str, answer_latex=answer_str,
            worked_solution=f"{val} and -{val} are opposites. {val} is {val} units right of 0, -{val} is {val} units left of 0, and they are equidistant from 0 in opposite directions.",
            choices=choices, context_scenario="number line opposite statements",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    # STEM 6: Above Proficiency - MC (DOK 2, Difficult)
    # Opposite reasoning with variables — diverse question types
    # ================================================================

    def stem6_above_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)

        var = rng.choice(['a', 'b', 'n', 'p', 'x', 'y'])

        # Cycle through 6 distinct patterns so variants differ
        pattern_idx = variant_idx % 6

        if pattern_idx == 0:
            # Nested opposites with variable
            question = f"If {var} is a positive number, what is the opposite of the opposite of -{var}?"
            correct = f"-{var}"
            distractors = [f"{var}", "0", f"2{var}"]
            explanation = (f"Start with -{var}. The opposite of -{var} is {var}. "
                          f"The opposite of {var} is -{var}. "
                          f"So the opposite of the opposite of -{var} is -{var}.")

        elif pattern_idx == 1:
            # Evaluate with a specific value
            val = rng.randint(2, 15)
            question = (f"If {var} = {val}, what is the value of "
                       f"the opposite of the opposite of {var}?")
            correct = str(val)
            distractors = [str(-val), "0", str(val * 2)]
            explanation = (f"The opposite of the opposite of any number is "
                          f"the number itself. So the answer is {var} = {val}.")

        elif pattern_idx == 2:
            # Real-world context
            depth = rng.randint(50, 500)
            question = (f"A submarine is at -{depth} feet (below sea level). "
                       f"It rises to the opposite depth. What is its "
                       f"new position?")
            correct = f"{depth} feet above sea level"
            distractors = [
                f"{depth * 2} feet below sea level",
                "0 feet (sea level)",
                f"{depth} feet below sea level",
            ]
            explanation = (f"The opposite of -{depth} is {depth}. "
                          f"The submarine rises to {depth} feet above sea level.")

        elif pattern_idx == 3:
            # Two students, one correct reasoning
            name1 = pick_name(rng)
            name2 = pick_name(rng)
            while name2 == name1:
                name2 = pick_name(rng)
            val = rng.randint(3, 20)
            question = (f"{name1} says the opposite of -{val} is {val}.\n"
                       f"{name2} says the opposite of -{val} is -{val}.\n\n"
                       f"Who is correct?")
            correct = f"{name1} is correct"
            distractors = [
                f"{name2} is correct",
                "Both are correct",
                "Neither is correct",
            ]
            explanation = (f"The opposite of -{val} is {val} because they are "
                          f"the same distance from 0 on opposite sides. "
                          f"{name1} is correct.")

        elif pattern_idx == 4:
            # Expression evaluation: -(-var)
            val = rng.randint(2, 20)
            question = f"What is the value of -(-{val})?"
            correct = str(val)
            distractors = [str(-val), "0", str(val * 2)]
            explanation = (f"-(-{val}) means the opposite of -{val}, "
                          f"which is {val}.")

        else:  # pattern_idx == 5
            # Which number line shows the opposite
            val = rng.randint(2, 7)
            sign = rng.choice([-1, 1])
            given = sign * val
            question = (f"Point P is at {given} on a number line. "
                       f"Where is the point that represents the "
                       f"opposite of Point P?")
            correct = str(-given)
            distractors = [str(given), "0", str(abs(given) * 2)]
            explanation = (f"The opposite of {given} is {-given}. "
                          f"Both are {abs(given)} units from 0 but "
                          f"on opposite sides.")

        all_options = [(correct, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MC,
                               Difficulty.DIFFICULT, 6, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.MC,
            stem_text=question, stem_latex=question,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=explanation,
            choices=choices, context_scenario="opposite with variables",
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6, variant_index=variant_idx,
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_below_mc,
            self.stem3_approaching_nr,
            self.stem4_at_nr,
            self.stem5_at_ms,
            self.stem6_above_mc,
        ]
        for stem_fn in stem_methods:
            for v in range(variants_per_stem):
                try:
                    all_questions.append(stem_fn(v))
                except Exception as e:
                    print(f"Error generating {stem_fn.__name__} variant {v}: {e}")
                    continue
        return all_questions

    def generate_stem_variants(self, stem_index: int,
                                variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        stem_methods = {
            1: self.stem1_below_mc,
            2: self.stem2_below_mc,
            3: self.stem3_approaching_nr,
            4: self.stem4_at_nr,
            5: self.stem5_at_ms,
            6: self.stem6_above_mc,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-6.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 6.NS.2 question variants...")
    gen = Stem6NS2(seed=42)
    all_q = gen.generate_all_variants(variants_per_stem=3)
    for q in all_q:
        print(f"\n{'='*60}")
        print(f"ID: {q.question_id}")
        print(f"Stem {q.stem_index} | {q.proficiency_level.value} | {q.difficulty.value} | DOK {q.dok}")
        print(f"\n{q.stem_text}")
        if q.choices:
            for c in q.choices:
                marker = " *" if c.is_correct else ""
                print(f"  {c.key}. {c.text}{marker}")
        print(f"\nAnswer: {q.answer_text}")
    print(f"\nTotal: {len(all_q)}")
