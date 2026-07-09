"""
Stem generator for 7.NS.2:
  Show that the distance between two rational numbers on the number line
  is the absolute value of their difference, and apply this principle in
  real-world contexts.

Content Limits:
  - Rational numbers may be integers, fractions, or decimals
  - Distances may be found without using a number line
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: only integers
  Medium: decimal numbers (must have a negative value or negative solution)
  Difficult: fractions or mixed numbers; calculate distance using absolute value

6 Stems from the Item Spec:
  Stem 1 (Below-MC):    Identify absolute value of a number on number line (DOK 2, difficult)
  Stem 2 (Below-NR):    Write the absolute value of a given number (DOK 1, easy)
  Stem 3 (Approaching-NR): Calculate distance / subtract with negatives (DOK 2, medium)
  Stem 4 (At-NR):       Subtract rational numbers — fractions/decimals (DOK 1, difficult)
  Stem 5 (At-NR):       Real-world subtraction with signed numbers (DOK 2, easy)
  Stem 6 (Above-MS):    Reason about a - b = c using number line with variables (DOK 3, difficult)
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
from engine.context_pools import CONTEXTS_7NS2, pick_name


STANDARD_CODE = "7.NS.2"
VARIANTS_PER_STEM = 20


# ============================================================
# HELPERS
# ============================================================

def _fmt(val):
    """Format a signed rational value for display (plain string, no RationalNumber).

    Handles int, float, and Fraction inputs.
    """
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return str(int(val))
        f = float(val)
        if f == int(f):
            return str(int(f))
        s = f"{f:.4f}".rstrip('0').rstrip('.')
        return s
    if isinstance(val, float):
        if val == int(val):
            return str(int(val))
        s = f"{val:.4f}".rstrip('0').rstrip('.')
        return s
    return str(val)


def _fmt_frac(val):
    """Format a Fraction as a fraction string (e.g. 3/4 or -3/4)."""
    if val.denominator == 1:
        return str(int(val))
    return f"{val.numerator}/{val.denominator}"


def _fmt_mixed(val):
    """Format a Fraction as a mixed number string (e.g. 2 3/4 or -2 3/4)."""
    if val.denominator == 1:
        return str(int(val))
    sign = -1 if val < 0 else 1
    abs_val = abs(val)
    whole = int(abs_val)
    remainder = abs_val - whole
    if remainder == 0:
        prefix = "-" if sign < 0 else ""
        return f"{prefix}{whole}"
    if whole == 0:
        prefix = "-" if sign < 0 else ""
        return f"{prefix}{remainder.numerator}/{remainder.denominator}"
    prefix = "-" if sign < 0 else ""
    return f"{prefix}{whole} {remainder.numerator}/{remainder.denominator}"


def _fmt_signed(val):
    """Format a value with explicit parentheses around negatives for expressions."""
    s = _fmt(val)
    if val < 0:
        return f"({s})"
    return s


class Stem7NS2:
    """Generates ~20 variants for each of 5 stems from the 7.NS.2 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 2, Difficult)
    # A number line with point A is given.
    # Select the number that shows the distance from point A to zero.
    # Uses mixed numbers.
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        # Difficult: mixed numbers
        whole = rng.randint(1, 8)
        denom = rng.choice([2, 4])
        numer = rng.randint(1, denom - 1)
        frac_part = Fraction(numer, denom)
        point_val = -(Fraction(whole) + frac_part)  # negative point

        abs_val = abs(point_val)

        point_str = _fmt_mixed(point_val)
        abs_str = _fmt_mixed(abs_val)

        # Correct answer: |point_val| expressed as |mixed number|
        correct_text = f"|{point_str}|"
        correct_latex = f"|{point_str}|"

        # Distractors
        distractors = []
        rationales = []

        # Distractor 1: the negative value itself (forgot absolute value)
        d1 = point_str
        distractors.append(d1)
        rationales.append("Used the negative value instead of absolute value")

        # Distractor 2: wrong magnitude (only the whole part)
        d2 = str(-whole)
        distractors.append(d2)
        rationales.append("Took only the whole number part, ignoring the fraction")

        # Distractor 3: |whole part| only
        d3 = f"|{-whole}|"
        distractors.append(d3)
        rationales.append("Applied absolute value to only the whole part")

        all_options = [(correct_text, correct_latex, True, None)]
        for i, d in enumerate(distractors):
            all_options.append((d, d, False, rationales[i]))
        rng.shuffle(all_options)

        choices = []
        for i, (text, latex, is_correct, rationale) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=latex,
                is_correct=is_correct, distractor_rationale=rationale,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = (
            f"A number line with point A at {point_str} is given.\n\n"
            f"Select the number that shows the value of the distance from point A to zero."
        )

        worked = (
            f"The distance from any point to zero is its absolute value.\n"
            f"|{point_str}| = {abs_str}\n"
            f"The correct expression is |{point_str}|."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.DIFFICULT, 1, variant_idx)

        # Number line with Point A
        nl_min = int(point_val) - 1
        nl_max = max(1, int(abs(point_val)) + 2)
        ticks = list(range(nl_min, nl_max + 1))

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="absolute value of mixed number on number line",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx,
            render_data={
                "type": "number_line_point",
                "ticks": ticks,
                "points": [{"value": float(point_val), "label": "A"}],
            }
        )

    # ================================================================
    # STEM 2: Below Proficiency - NR (DOK 1, Easy)
    # Write the absolute value of a given integer.
    # "What is the value of |42|?" Answer: 42
    # ================================================================

    def stem2_below_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        # Easy: integers
        val = gen.signed_integer(min_val=-50, max_val=50)

        abs_val = abs(val)
        val_str = _fmt(val)
        abs_str = _fmt(abs_val)

        stem_text = f"What is the value of |{val_str}|?"

        correct_str = abs_str

        worked = (
            f"The absolute value of a number is its distance from 0 on a number line.\n"
            f"|{val_str}| = {abs_str}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.NR,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_str, answer_latex=correct_str,
            worked_solution=worked,
            context_scenario="absolute value of integer",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - NR (DOK 2, Medium)
    # Calculate the distance between two points (subtraction with negatives)
    # "Solve 3.5 - (-2.5)"  Answer: 6
    # ================================================================

    def stem3_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        # Medium: decimals, must involve a negative value
        a = gen.signed_decimal(min_val=0.1, max_val=9.9, places=1)
        a = abs(a)  # ensure positive
        b = gen.signed_decimal(min_val=-9.9, max_val=-0.1, places=1)
        b = -abs(b)  # ensure negative

        result = a - b  # a - (-|b|) = a + |b|

        a_str = _fmt(a)
        b_str = _fmt(b)
        result_str = _fmt(result)

        stem_text = (
            f"Solve.\n\n"
            f"{a_str} - ({b_str})"
        )

        correct_str = result_str

        worked = (
            f"Subtracting a negative is the same as adding the positive.\n"
            f"{a_str} - ({b_str}) = {a_str} + {_fmt(abs(b))}\n"
            f"= {result_str}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_str, answer_latex=correct_str,
            worked_solution=worked,
            context_scenario="subtract negative decimal",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At Proficiency - NR (DOK 1, Difficult)
    # Subtract rational numbers (fractions/mixed numbers)
    # "What is the value of -1 1/4 - 3 3/4?"  Answer: -5
    # ================================================================

    def stem4_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        # Difficult: mixed numbers / fractions
        denom = rng.choice([2, 4])

        # First number: negative mixed number
        a_whole = rng.randint(1, 6)
        a_numer = rng.randint(0, denom - 1)
        a_val = -(Fraction(a_whole) + Fraction(a_numer, denom))

        # Second number: positive mixed number
        b_whole = rng.randint(1, 6)
        b_numer = rng.randint(0, denom - 1)
        b_val = Fraction(b_whole) + Fraction(b_numer, denom)

        result = a_val - b_val

        a_str = _fmt_mixed(a_val)
        b_str = _fmt_mixed(b_val)
        result_str = _fmt_mixed(result)

        stem_text = (
            f"An expression is shown.\n\n"
            f"{a_str} - {b_str}\n\n"
            f"What is the value of the expression?"
        )

        correct_str = result_str

        worked = (
            f"{a_str} - {b_str}\n"
            f"= {a_str} + ({_fmt_mixed(-b_val)})\n"
            f"= {result_str}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.DIFFICULT, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_str, answer_latex=correct_str,
            worked_solution=worked,
            context_scenario="subtract mixed numbers",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: At Proficiency - NR (DOK 2, Easy)
    # Real-world subtraction problem with signed integers
    # "The temperature at 1 am is -7. It drops 5 degrees. What is the
    #  temperature at 3 am?"  Answer: -12
    # ================================================================

    def stem5_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        ctx = rng.choice(CONTEXTS_7NS2)
        name = pick_name(rng)

        # Easy: integers
        a = gen.signed_integer(min_val=-15, max_val=15)
        b = gen.signed_integer(min_val=-15, max_val=15)

        # Ensure the two values are different
        while b == a:
            b = gen.signed_integer(min_val=-15, max_val=15)

        distance = abs(a - b)

        a_str = _fmt(a)
        b_str = _fmt(b)
        distance_str = _fmt(distance)

        stem_text = ctx["template"].format(name=name, a=a_str, b=b_str)
        correct_str = distance_str

        worked = (
            f"Distance = |{a_str} - {_fmt_signed(b)}|\n"
            f"= |{_fmt(a - b)}|\n"
            f"= {distance_str} {ctx['unit']}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.EASY, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_str, answer_latex=correct_str,
            worked_solution=worked,
            context_scenario=f"real-world distance ({ctx['unit']})",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    # STEM 6: Above Proficiency - MS (DOK 3, Difficult)
    # Reason about c = a - b using a number line with variables.
    # Number line shows positions of a and b (no numeric values).
    # Student determines which statements about c are true.
    # "The difference of a - b is c. The number line shows a and b.
    #  Which statements about c are true?"
    # ================================================================

    def stem6_above_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)

        # Generate varied configurations of a and b on a number line
        configs = [
            ("neg_pos", -1, 1),
            ("pos_neg", 1, -1),
            ("both_pos_a_gt", 2, 1),
            ("both_pos_a_lt", 1, 2),
            ("both_neg_a_lt", -2, -1),
            ("both_neg_a_gt", -1, -2),
        ]
        config_name, a_sign, b_sign = rng.choice(configs)

        if a_sign < 0:
            a = -rng.randint(2, 8)
        elif a_sign > 0:
            a = rng.randint(2, 8)
        else:
            a = 0
        if b_sign < 0:
            b = -rng.randint(2, 8)
        elif b_sign > 0:
            b = rng.randint(2, 8)
        else:
            b = 0
        while a == b:
            b = rng.randint(-8, 8)
            if b == 0:
                b = 1

        c = a - b
        dist = abs(a - b)

        nl_min = min(a, b, 0) - 2
        nl_max = max(a, b, 0) + 2
        ticks = list(range(nl_min, nl_max + 1))

        render_data = {
            "type": "number_line_point",
            "ticks": ticks,
            "points": [
                {"value": a, "label": "a"},
                {"value": b, "label": "b"},
            ],
            "show_zero": True,
        }

        var_pairs = [("p", "q"), ("m", "n"), ("r", "s")]
        v1, v2 = rng.choice(var_pairs)

        fmt = variant_idx % 4

        if fmt == 0:
            # Format A: Original — which statements about c are true?
            all_statements = [
                ("|a| < |c|", abs(a) < abs(c)),
                ("|a| = |c|", abs(a) == abs(c)),
                ("|a| > |c|", abs(a) > abs(c)),
                ("c < 0", c < 0),
                ("c = 0", c == 0),
                ("c > 0", c > 0),
            ]
            choices = []
            correct_keys = []
            for i, (text, is_true) in enumerate(all_statements):
                key = chr(ord('a') + i)
                choices.append(QuestionChoice(
                    key=key, text=text, text_latex=text, is_correct=is_true,
                ))
                if is_true:
                    correct_keys.append(key)
            answer_str = ", ".join(correct_keys)
            stem_text = (
                f"The difference of a - b is c. The number line shows a and b.\n\n"
                f"Which statements about c are true?"
            )
            worked_lines = [
                f"From the number line, a is at {a} and b is at {b}.",
                f"c = a - b = {a} - {_fmt_signed(b)} = {c}",
                f"|a| = {abs(a)}, |c| = {abs(c)}",
            ]
            for text, is_true in all_statements:
                worked_lines.append(f"  {text}: {'TRUE' if is_true else 'FALSE'}")
            worked = "\n".join(worked_lines)
            item_type = ItemType.MS

        elif fmt == 1:
            # Format B: Which expression gives the distance between two points?
            correct_text = f"|{v1} - {v2}|"
            wrong = [
                f"{v1} - {v2}",
                f"{v1} + {v2}",
                f"|{v1}| - |{v2}|",
            ]
            all_options = [(correct_text, True)] + [(d, False) for d in wrong]
            rng.shuffle(all_options)
            choices = []
            for i, (text, is_correct) in enumerate(all_options):
                choices.append(QuestionChoice(
                    key=chr(ord('a') + i), text=text, text_latex=text,
                    is_correct=is_correct,
                ))
            answer_str = next(c.key for c in choices if c.is_correct)
            stem_text = (
                f"Points {v1} and {v2} are shown on the number line.\n\n"
                f"Which expression always gives the distance between {v1} and {v2}?"
            )
            render_data["points"] = [
                {"value": a, "label": v1},
                {"value": b, "label": v2},
            ]
            worked = (
                f"Distance between two points is always |{v1} - {v2}|.\n"
                f"The absolute value ensures the result is positive "
                f"regardless of which value is larger.\n"
                f"{v1} - {v2} alone could be negative."
            )
            item_type = ItemType.MC

        elif fmt == 2:
            # Format C: True statements about distance on number line
            all_statements = [
                (f"The distance between a and b is |a - b|.", True),
                (f"|a - b| = |b - a|", True),
                (f"The distance is always positive.", True),
                (f"a - b is always positive.", a > b),
                (f"|a - b| = a + b", abs(a - b) == a + b),
                (f"a - b = b - a", a == b),
            ]
            # Keep first 5 to have mix of true/false
            statements = all_statements[:5]
            choices = []
            correct_keys = []
            for i, (text, is_true) in enumerate(statements):
                key = chr(ord('a') + i)
                choices.append(QuestionChoice(
                    key=key, text=text, text_latex=text, is_correct=is_true,
                ))
                if is_true:
                    correct_keys.append(key)
            answer_str = ", ".join(correct_keys)
            stem_text = (
                f"Points a and b are on a number line.\n\n"
                f"Select all statements that are always true."
            )
            worked = (
                f"The distance between two points is |a - b|, which is "
                f"always non-negative.\n"
                f"|a - b| = |b - a| because absolute value ignores sign.\n"
                f"a - b can be negative if b > a."
            )
            item_type = ItemType.MS

        else:
            # Format D: What is |a - b| given positions?
            correct_text = str(dist)
            dist_set = {str(abs(a)), str(abs(b)), str(abs(a + b))}
            dist_set.discard(correct_text)
            wrong = list(dist_set)[:3]
            while len(wrong) < 3:
                d = str(rng.randint(1, 15))
                if d != correct_text and d not in wrong:
                    wrong.append(d)
            all_options = [(correct_text, True)] + [(d, False) for d in wrong]
            rng.shuffle(all_options)
            choices = []
            for i, (text, is_correct) in enumerate(all_options):
                choices.append(QuestionChoice(
                    key=chr(ord('a') + i), text=text, text_latex=text,
                    is_correct=is_correct,
                ))
            answer_str = next(c.key for c in choices if c.is_correct)
            stem_text = (
                f"The number line shows a at {a} and b at {b}.\n\n"
                f"What is |a - b|?"
            )
            worked = (
                f"|a - b| = |{a} - {_fmt_signed(b)}| = |{c}| = {dist}"
            )
            item_type = ItemType.MC

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, item_type,
                               Difficulty.DIFFICULT, 6, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=item_type,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_str, answer_latex=answer_str,
            worked_solution=worked,
            choices=choices,
            context_scenario="reason about distance with variables",
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6, variant_index=variant_idx,
            render_data=render_data if fmt != 2 else None,
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_below_nr,
            self.stem3_approaching_nr,
            self.stem4_at_nr,
            self.stem5_at_nr,
            self.stem6_above_ms,
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
            2: self.stem2_below_nr,
            3: self.stem3_approaching_nr,
            4: self.stem4_at_nr,
            5: self.stem5_at_nr,
            6: self.stem6_above_ms,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-6.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 7.NS.2 question variants...")
    gen = Stem7NS2(seed=42)
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
