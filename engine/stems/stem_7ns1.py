"""
Stem generator for 7.NS.1:
  Show on a number line that a number and its opposite have a sum of 0
  (are additive inverses). Find and interpret sums of rational numbers
  in real-world contexts.

Content Limits:
  - Rational numbers can be integers, fractions, or decimals
  - Both terms 'additive inverse' and 'opposites' can be used
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: only integers
  Medium: decimal numbers
  Difficult: fractions, mixed numbers, or variables

6 Stems from the Item Spec:
  Stem 1 (Below-NR):    Sum of a number and its opposite (DOK 1, medium)
  Stem 2 (Below-MC):    Select expression modeling distance between points (DOK 2, easy)
  Stem 3 (Approaching-NR): Distance between two points on a number line (DOK 2, difficult)
  Stem 4 (At-NR):       Sum of rational numbers with opposite signs (DOK 2, difficult)
  Stem 5 (At-NR):       Real-world sum of rationals — distance on number line (DOK 2, medium)
  Stem 6 (Above-MC):    Additive inverse reasoning with variables (DOK 2, difficult)
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
from engine.context_pools import CONTEXTS_7NS1, pick_name


STANDARD_CODE = "7.NS.1"
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


class Stem7NS1:
    """Generates ~20 variants for each of 6 stems from the 7.NS.1 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - NR (DOK 1, Medium)
    # Sum of a number and its opposite: a + (-a) = 0
    # "Solve: 2.3 + (-2.3)"  Answer: 0
    # ================================================================

    def stem1_below_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        # Medium difficulty: decimals
        val = gen.signed_decimal(min_val=1.1, max_val=9.9, places=1)
        # Make sure it's positive for presentation
        val = abs(val)
        neg_val = -val

        # Present as  val + (-val)
        stem_text = (
            f"Solve.\n\n"
            f"{_fmt(val)} + ({_fmt(neg_val)})"
        )

        correct_str = "0"

        worked = (
            f"A number plus its opposite (additive inverse) always equals 0.\n"
            f"{_fmt(val)} + ({_fmt(neg_val)}) = 0"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.NR,
                               Difficulty.MEDIUM, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_str, answer_latex=correct_str,
            worked_solution=worked,
            context_scenario="additive inverse with decimals",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Below Proficiency - MC (DOK 2, Easy)
    # Select the expression that models the distance between two points
    # on a number line. E.g. points at -4 and 8 -> |-4 + 8|
    # ================================================================

    def stem2_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        # Easy difficulty: integers
        a = gen.signed_integer(min_val=-10, max_val=-1)
        b = gen.signed_integer(min_val=1, max_val=10)

        a_int = int(a)
        b_int = int(b)

        # Correct: |a + b| or |a - b| depending on context
        # Per the item spec, the distance expression is |a - b| or equivalently |b - a|
        # The item spec example uses |-4 + 8| as correct for distance between -4 and 8
        # Distance = |a| + |b| when on opposite sides of zero = |b - a|
        # The correct answer from the spec: |-4 + 8| which equals |b + a|
        correct_text = f"|{_fmt(a)} + {_fmt(b)}|"
        correct_latex = f"|{_fmt(a)} + {_fmt(b)}|"

        # Distractors (common student errors)
        distractors = []
        rationales = []

        # Distractor 1: no absolute value (just a + b) — forgets absolute value
        d1 = f"{_fmt(b)} + ({_fmt(a)})"
        distractors.append(d1)
        rationales.append("Forgot to use absolute value for distance")

        # Distractor 2: |a| + b (absolute value of only one term)
        d2 = f"{_fmt(b)} + |{_fmt(a)}|"
        distractors.append(d2)
        rationales.append("Applied absolute value to only one number")

        # Distractor 3: |a| + |b| (sum of absolute values, not distance expression)
        d3 = f"|{_fmt(b)}| + {_fmt(a)}"
        distractors.append(d3)
        rationales.append("Used absolute value of b but not as a combined expression")

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
            f"A number line is given with point A at {_fmt(a)} and point B at {_fmt(b)}.\n\n"
            f"Select the expression that models the distance between points A and B."
        )

        worked = (
            f"The distance between two points on a number line is the absolute value "
            f"of their sum when they are on opposite sides of zero.\n"
            f"Distance = |{_fmt(a)} + {_fmt(b)}| = |{_fmt(a + b)}| = {_fmt(abs(a + b))}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 2, variant_idx)

        # Number line ticks covering both points
        nl_min = min(int(a) - 1, -8)
        nl_max = max(int(b) + 1, 8)
        ticks = list(range(nl_min, nl_max + 1))

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="distance expression on number line",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx,
            render_data={
                "type": "number_line_point",
                "ticks": ticks,
                "points": [
                    {"value": float(a), "label": "A"},
                    {"value": float(b), "label": "B"},
                ],
            }
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - NR (DOK 2, Difficult)
    # Calculate the distance between two points on opposite sides of
    # zero on a number line. Uses mixed numbers.
    # ================================================================

    def stem3_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        # Difficult: fractions / mixed numbers
        # Generate two points on opposite sides of zero
        # Point a: negative mixed number
        a_whole = rng.randint(1, 5)
        a_numer = rng.randint(1, 3)
        a_denom = rng.choice([2, 4])
        a_frac = Fraction(a_numer, a_denom)
        a_val = -(Fraction(a_whole) + a_frac)

        # Point b: positive mixed number with same denominator for clean answer
        b_whole = rng.randint(1, 5)
        b_numer = rng.randint(1, a_denom - 1)
        b_frac = Fraction(b_numer, a_denom)
        b_val = Fraction(b_whole) + b_frac

        distance = abs(b_val - a_val)  # = |b - a| = b + |a| since opposite sides

        stem_text = (
            f"What is the distance between point A at {_fmt_mixed(a_val)} "
            f"and point B at {_fmt_mixed(b_val)} on a number line?"
        )

        correct_str = _fmt_mixed(distance)

        worked = (
            f"Distance = |B - A| = |{_fmt_mixed(b_val)} - ({_fmt_mixed(a_val)})|\n"
            f"= |{_fmt_mixed(b_val)} + {_fmt_mixed(abs(a_val))}|\n"
            f"= {correct_str}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.DIFFICULT, 3, variant_idx)

        # Number line with half-unit ticks covering both points
        nl_min = int(a_val) - 1
        nl_max = int(b_val) + 2
        half_ticks = [x / 2 for x in range(nl_min * 2, nl_max * 2 + 1)]

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_str, answer_latex=correct_str,
            worked_solution=worked,
            context_scenario="distance between mixed number points",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx,
            render_data={
                "type": "number_line_point",
                "ticks": [t for t in half_ticks if t == int(t)],
                "points": [
                    {"value": float(a_val), "label": "A"},
                    {"value": float(b_val), "label": "B"},
                ],
            }
        )

    # ================================================================
    # STEM 4: At Proficiency - NR (DOK 2, Difficult)
    # Calculate the sum of rational numbers with opposite signs
    # e.g. -5/4 + 1/2 + 3/4
    # ================================================================

    def stem4_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        # Difficult: fractions
        # Generate three fractions that sum to a clean value
        denom = rng.choice([2, 4, 6, 8])

        # Generate a negative fraction, and two positive fractions
        neg_numer = rng.randint(2, denom * 2)
        neg_val = Fraction(-neg_numer, denom)

        # Two positive fractions that combined with neg_val give a clean answer
        # Pick the answer first, then derive the second positive
        answer_options = [Fraction(0), Fraction(1, denom), Fraction(-1, denom),
                          Fraction(1), Fraction(-1), Fraction(1, 2), Fraction(-1, 2)]
        target_sum = rng.choice(answer_options)

        pos1_numer = rng.randint(1, denom)
        pos1 = Fraction(pos1_numer, denom)

        pos2 = target_sum - neg_val - pos1

        terms = [neg_val, pos1, pos2]
        rng.shuffle(terms)

        total = sum(terms)

        terms_str = " + ".join([_fmt_signed(t) if t < 0 else _fmt_frac(t) for t in terms])
        # Clean up display: replace "+ (-" with "- "
        terms_display = _fmt_frac(terms[0])
        for t in terms[1:]:
            if t < 0:
                terms_display += f" + ({_fmt_frac(t)})"
            else:
                terms_display += f" + {_fmt_frac(t)}"

        stem_text = (
            f"Solve.\n\n"
            f"{terms_display}"
        )

        correct_str = _fmt_frac(total)

        worked = (
            f"Combine the fractions:\n"
            f"{terms_display}\n"
            f"= {correct_str}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.DIFFICULT, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_str, answer_latex=correct_str,
            worked_solution=worked,
            context_scenario="sum of rational fractions with opposite signs",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: At Proficiency - NR (DOK 2, Medium)
    # Real-world sum of rationals (distance / number line context)
    # E.g. Megan and Jake on number line, find distance
    # ================================================================

    def stem5_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        ctx = rng.choice(CONTEXTS_7NS1)
        name = pick_name(rng)

        # Medium difficulty: decimals
        a = gen.signed_decimal(min_val=-9.9, max_val=-0.1, places=1)
        b = gen.signed_decimal(min_val=0.1, max_val=9.9, places=1)

        total = a + b

        # Fill in the context template
        a_str = _fmt(a)
        b_str = _fmt(b)
        if b >= 0:
            b_display = f"+{b_str}"
        else:
            b_display = b_str

        stem_text = ctx["template"].format(name=name, a=a_str, b=b_display)
        correct_str = _fmt(total)

        worked = (
            f"Starting value: {a_str}\n"
            f"Change: {b_display}\n"
            f"Result: {a_str} + {_fmt_signed(b)} = {correct_str} {ctx['unit']}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.MEDIUM, 5, variant_idx)

        # Number line with labeled points
        nl_min = min(int(a) - 1, -10)
        nl_max = max(int(b) + 1, 10)
        ticks = list(range(nl_min, nl_max + 1))

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_str, answer_latex=correct_str,
            worked_solution=worked,
            context_scenario=f"real-world sum of rationals ({ctx['unit']})",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx,
            render_data={
                "type": "number_line_point",
                "ticks": ticks,
                "points": [
                    {"value": float(a), "label": "A"},
                    {"value": float(b), "label": "B"},
                ],
            }
        )

    # ================================================================
    # STEM 6: Above Proficiency - MC (DOK 2, Difficult)
    # Additive inverse reasoning with variables
    # "Jack knows that a + b = 0. Which statement is true?"
    # ================================================================

    def stem6_above_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)

        name = pick_name(rng)

        # Pick variable names
        var_pairs = [("a", "b"), ("p", "q"), ("m", "n"), ("x", "y"), ("r", "s")]
        v1, v2 = rng.choice(var_pairs)

        fmt = variant_idx % 4

        render = None  # set per format

        if fmt == 0:
            # Format A: v1 + v2 = 0, which statement is true?
            correct_text = f"{v2} = -{v1}"
            distractors = [
                f"{v2} > {v1}",
                f"{v2} = {v1}",
                f"{v1} = -{v1}",
            ]
            # Place v1 at a positive position on the number line
            v1_pos = rng.randint(2, 6)
            ticks = list(range(-v1_pos - 2, v1_pos + 3))
            render = {
                "type": "number_line_point",
                "ticks": ticks,
                "points": [{"value": v1_pos, "label": v1}],
            }
            stem_text = (
                f"A number line is given showing {v1} to the right of 0. [FIGURE]\n\n"
                f"{name} knows that {v1} + {v2} = 0.\n\n"
                f"Which statement is true?"
            )
            worked = (
                f"Since {v1} + {v2} = 0, the values are additive inverses.\n"
                f"This means {v2} = -{v1}.\n"
                f"Because {v1} is to the right of 0 (positive), {v2} must be "
                f"to the left of 0 (negative) at the same distance from 0."
            )

        elif fmt == 1:
            # Format B: If v1 = -v2, which expression equals 0?
            correct_text = f"{v1} + {v2}"
            distractors = [
                f"{v1} - {v2}",
                f"|{v1}| + |{v2}|",
                f"|{v1}| - {v1}",
            ]
            stem_text = (
                f"{name} knows that {v1} = -{v2}.\n\n"
                f"Which expression is equal to 0?"
            )
            worked = (
                f"If {v1} = -{v2}, then {v1} and {v2} are additive inverses.\n"
                f"By definition, additive inverses sum to 0.\n"
                f"So {v1} + {v2} = 0."
            )

        elif fmt == 2:
            # Format C: Which equation shows additive inverses?
            correct_text = f"{v1} + {v2} = 0"
            distractors = [
                f"{v1} + {v2} = {v1}",
                f"{v1} x {v2} = 0",
                f"{v1} - {v2} = 0",
            ]
            stem_text = (
                f"Two numbers {v1} and {v2} are additive inverses.\n\n"
                f"Which equation must be true?"
            )
            worked = (
                f"Additive inverses are two numbers that add to zero.\n"
                f"The equation {v1} + {v2} = 0 represents this.\n"
                f"{v1} - {v2} = 0 would mean they are equal, not inverses."
            )

        else:
            # Format D: Given v1 + v2 = 0 and v1 = k, what is v2?
            k = rng.randint(2, 12) * rng.choice([-1, 1])
            correct_text = str(-k)
            dist_set = {str(k), str(2 * k), "0"}
            dist_set.discard(correct_text)
            distractors = list(dist_set)[:3]
            while len(distractors) < 3:
                d = str(rng.randint(-15, 15))
                if d != correct_text and d not in distractors:
                    distractors.append(d)
            stem_text = (
                f"{name} knows that {v1} + {v2} = 0.\n\n"
                f"If {v1} = {k}, what is the value of {v2}?"
            )
            worked = (
                f"Since {v1} + {v2} = 0, {v2} = -{v1}.\n"
                f"If {v1} = {k}, then {v2} = -({k}) = {-k}."
            )

        all_options = [(correct_text, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MC,
                               Difficulty.DIFFICULT, 6, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="additive inverse with variables",
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6, variant_index=variant_idx,
            render_data=render,
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_nr,
            self.stem2_below_mc,
            self.stem3_approaching_nr,
            self.stem4_at_nr,
            self.stem5_at_nr,
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
            1: self.stem1_below_nr,
            2: self.stem2_below_mc,
            3: self.stem3_approaching_nr,
            4: self.stem4_at_nr,
            5: self.stem5_at_nr,
            6: self.stem6_above_mc,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-6.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 7.NS.1 question variants...")
    gen = Stem7NS1(seed=42)
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
