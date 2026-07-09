"""
Stem generator for 7.NS.4:
  Explain that if p and q are integers, then -(p/q) = (-p)/q = p/(-q)
  for all nonzero integers. Division of integers holds the same sign
  properties as multiplication.

Content Limits:
  - Rational numbers can be integers, fractions, or decimals
  - Division of integers holds the same properties as multiplication
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: Limit to integers only, one integer is negative
  Medium: Limit to integers and decimals, at least one negative number
  Difficult: Includes fractions

5 Stems from the Item Spec:
  Stem 1 (Below-MS):       Identify equivalent fractions satisfying -(p/q) = (-p)/q = p/(-q) (DOK 1, medium)
  Stem 2 (Approaching-MC): Choose the quotient of two signed integers (DOK 1, easy)
  Stem 3 (At-NR):          Calculate the quotient of two integers as a decimal (DOK 1, easy)
  Stem 4 (At-MC):          Divide with fractions (DOK 1, difficult)
  Stem 5 (Above-NR):       Generate equivalent fractions for -(p/q) (DOK 1, easy)
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


STANDARD_CODE = "7.NS.4"
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


def _fmt_frac_unsigned(p, q):
    """Format p/q as a fraction string preserving original p and q (not reduced)."""
    if q == 1:
        return str(p)
    return f"{p}/{q}"


class Stem7NS4:
    """Generates ~20 variants for each of 5 stems from the 7.NS.4 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MS (DOK 1, Medium)
    # Identify equivalent fractions satisfying -(p/q) = (-p)/q = p/(-q)
    # e.g., "Which expression has a value of -7/10? Select all that apply."
    # ================================================================

    def stem1_below_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        # Pick p and q (both positive), the target is -p/q
        p = rng.randint(1, 9)
        q = rng.randint(2, 10)
        # Ensure they don't reduce to a whole number
        while Fraction(p, q).denominator == 1:
            q = rng.randint(2, 10)

        target = Fraction(-p, q)
        target_str = f"-{p}/{q}"

        # Correct forms: -(p/q), (-p)/q, p/(-q)
        correct_forms = [
            (f"-({p}/{q})", True),
            (f"{-p}/{q}", True),
            (f"{p}/{-q}", True),
        ]

        # Wrong forms
        wrong_forms = [
            (f"{p}/{q}", False),         # Missing negative
            (f"{-p}/{-q}", False),        # Both negative = positive
        ]

        # Add another wrong: wrong values
        wrong_p = p + rng.choice([1, 2])
        wrong_forms.append((f"-{wrong_p}/{q}", False))

        # Combine: 3 correct + 3 wrong = 6 options
        all_options = correct_forms + wrong_forms[:3]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letters = ", ".join(c.key for c in choices if c.is_correct)

        stem_text = f"Select all options that are equivalent to {target_str}."

        worked = (
            f"The rule: -(p/q) = (-p)/q = p/(-q)\n"
            f"For {target_str}:\n"
            f"  -({p}/{q}) = {target_str}  (correct)\n"
            f"  {-p}/{q} = {target_str}  (correct)\n"
            f"  {p}/{-q} = {target_str}  (correct)\n"
            f"  {p}/{q} is positive, not equivalent.\n"
            f"  {-p}/{-q} = {p}/{q} is positive, not equivalent."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MS,
                               Difficulty.MEDIUM, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.MS,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letters, answer_latex=correct_letters,
            worked_solution=worked,
            choices=choices, context_scenario="equivalent fractions -(p/q) rule",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - MC (DOK 1, Easy)
    # Choose the quotient of two signed integers
    # e.g., -45 / 9 = ?
    # ================================================================

    def stem2_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        # Generate dividend and divisor (integers, one negative)
        divisor = rng.choice([2, 3, 4, 5, 6, 7, 8, 9])
        quotient_val = rng.randint(2, 12)

        # Decide sign arrangement: exactly one negative
        sign_config = rng.choice(["neg_div_pos", "pos_div_neg"])
        if sign_config == "neg_div_pos":
            dividend = -(divisor * quotient_val)
            correct = -quotient_val
        else:
            dividend = divisor * quotient_val
            divisor = -divisor
            correct = -quotient_val

        correct_str = _fmt(correct)

        # Distractors
        distractors = set()
        distractors.add(_fmt(-correct))                          # wrong sign
        distractors.add(_fmt(abs(dividend) + abs(divisor)))      # added instead
        unreduced = f"{abs(dividend)}/{abs(divisor)}"
        distractors.add(unreduced)                               # left as fraction string
        distractors.discard(correct_str)
        dist_list = [d for d in distractors if d != correct_str][:3]
        while len(dist_list) < 3:
            offset = rng.choice([1, -1, 2, -2])
            d = _fmt(correct + offset)
            if d != correct_str and d not in dist_list:
                dist_list.append(d)
        dist_list = dist_list[:3]

        all_options = [(correct_str, True)] + [(d, False) for d in dist_list]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = f"Solve.\n\n{_fmt(dividend)} / {_fmt(divisor)}\n\nChoose the quotient of the given expression."

        if dividend < 0 and divisor > 0:
            sign_rule = "negative / positive = negative"
        else:
            sign_rule = "positive / negative = negative"

        worked = (
            f"{_fmt(dividend)} / {_fmt(divisor)}\n"
            f"Rule: {sign_rule}\n"
            f"|{_fmt(dividend)}| / |{_fmt(divisor)}| = {abs(dividend)} / {abs(divisor)} = {abs(correct)}\n"
            f"Apply sign: {correct_str}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="quotient of two signed integers",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: At Proficiency - NR (DOK 1, Easy)
    # Calculate the quotient of two integers as a decimal
    # e.g., -12 / 5 = -2.4
    # ================================================================

    def stem3_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        # Ensure the result is a terminating decimal
        # Use divisors whose multiples produce terminating decimals
        divisor_choices = [2, 4, 5, 8, 10, 20, 25]
        divisor = rng.choice(divisor_choices)

        # Dividend: a multiple of divisor +/- some amount to create a decimal
        quotient_int_part = rng.randint(1, 10)
        # Pick a clean fraction part
        frac_parts = [Fraction(1, divisor)]
        for k in range(1, divisor):
            f = Fraction(k, divisor)
            # Check terminating
            d = f.denominator
            temp = d
            while temp % 2 == 0:
                temp //= 2
            while temp % 5 == 0:
                temp //= 5
            if temp == 1:
                frac_parts.append(f)
        frac_part = rng.choice(frac_parts)
        abs_quotient = Fraction(quotient_int_part) + frac_part
        dividend = abs_quotient * divisor

        # Apply sign: exactly one negative
        sign_config = rng.choice(["neg_num", "neg_den"])
        if sign_config == "neg_num":
            actual_dividend = -int(dividend)
            actual_divisor = int(divisor)
        else:
            actual_dividend = int(dividend)
            actual_divisor = -int(divisor)

        result = Fraction(actual_dividend, actual_divisor)
        result_float = float(result)

        if result_float == int(result_float):
            correct_str = str(int(result_float))
        else:
            correct_str = f"{result_float:.4f}".rstrip('0').rstrip('.')

        stem_text = (
            f"Calculate the quotient of {_fmt(actual_dividend)} / {_fmt(actual_divisor)} "
            f"as a decimal."
        )

        worked = (
            f"{_fmt(actual_dividend)} / {_fmt(actual_divisor)}\n"
            f"|{abs(actual_dividend)}| / |{abs(actual_divisor)}| = {_fmt(abs(result_float))}\n"
            f"One factor is negative, so the result is negative.\n"
            f"Answer: {correct_str}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.EASY, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_str, answer_latex=f"${correct_str}$",
            worked_solution=worked,
            context_scenario="integer quotient as decimal",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At Proficiency - MC (DOK 1, Difficult)
    # Divide with fractions: e.g., (-2/5) / (3/4) = ?
    # ================================================================

    def stem4_at_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        # Generate two signed fractions for division
        denom_a = rng.choice([2, 3, 4, 5, 6])
        numer_a = rng.randint(1, denom_a - 1)
        sign_a = rng.choice([-1, 1])
        a = Fraction(sign_a * numer_a, denom_a)

        denom_b = rng.choice([2, 3, 4, 5, 6])
        numer_b = rng.randint(1, denom_b - 1)
        sign_b = rng.choice([-1, 1])
        b = Fraction(sign_b * numer_b, denom_b)

        result = a / b
        a_str = _fmt_frac(a)
        b_str = _fmt_frac(b)
        result_str = _fmt_frac(result)

        correct_str = result_str

        # Distractors
        distractors = set()
        distractors.add(_fmt_frac(-result))                   # wrong sign
        distractors.add(_fmt_frac(a * b))                     # multiplied instead
        distractors.add(_fmt_frac(abs(result)))                # forgot sign (if negative)
        if result < 0:
            distractors.add(_fmt_frac(abs(result)))
        distractors.discard(correct_str)
        dist_list = [d for d in distractors if d != correct_str][:3]

        # Add more if needed
        while len(dist_list) < 3:
            offset = Fraction(rng.choice([1, -1]), rng.choice([2, 3, 4, 5]))
            d = _fmt_frac(result + offset)
            if d != correct_str and d not in dist_list:
                dist_list.append(d)
        dist_list = dist_list[:3]

        all_options = [(correct_str, True)] + [(d, False) for d in dist_list]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = f"Solve.\n\n({a_str}) / ({b_str})"

        reciprocal = Fraction(b.denominator, b.numerator)
        reciprocal_str = _fmt_frac(reciprocal)

        worked = (
            f"Dividing by a fraction means multiplying by its reciprocal.\n"
            f"({a_str}) / ({b_str}) = ({a_str}) x ({reciprocal_str})\n"
            f"= {result_str}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MC,
                               Difficulty.DIFFICULT, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="division of signed fractions",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above Proficiency - NR (DOK 1, Easy)
    # Write two fractions equivalent to -(p/q)
    # e.g., Write two fractions equivalent to -(7/8).
    # Answer: -7/8 and 7/(-8)
    # ================================================================

    def stem5_above_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        # Pick p and q (positive integers)
        p = rng.randint(1, 11)
        q = rng.randint(2, 12)
        # Ensure not whole
        while Fraction(p, q).denominator == 1:
            q = rng.randint(2, 12)

        # The three equivalent forms
        form1 = f"-({p}/{q})"
        form2 = f"{-p}/{q}"
        form3 = f"{p}/{-q}"

        # Accept any two of: form2 and form3 (form1 is the given)
        correct_str = f"{-p}/{q} and {p}/{-q}"

        stem_text = (
            f"Write two fractions that are equivalent to -({p}/{q}).\n\n"
            f"Write your answers in the boxes."
        )

        worked = (
            f"The rule: -(p/q) = (-p)/q = p/(-q)\n"
            f"-({p}/{q}) = {-p}/{q} = {p}/{-q}\n"
            f"Two equivalent fractions: {-p}/{q} and {p}/{-q}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.NR,
                               Difficulty.EASY, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_str, answer_latex=f"${correct_str}$",
            worked_solution=worked,
            context_scenario="generate equivalent signed fractions",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_ms,
            self.stem2_approaching_mc,
            self.stem3_at_nr,
            self.stem4_at_mc,
            self.stem5_above_nr,
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
            1: self.stem1_below_ms,
            2: self.stem2_approaching_mc,
            3: self.stem3_at_nr,
            4: self.stem4_at_mc,
            5: self.stem5_above_nr,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-5.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 7.NS.4 question variants...")
    gen = Stem7NS4(seed=42)
    all_q = gen.generate_all_variants(variants_per_stem=3)
    for q in all_q:
        print(f"\n{'='*60}")
        print(f"ID: {q.question_id}")
        print(f"Stem {q.stem_index} | {q.proficiency_level.value} | {q.difficulty.value} | DOK {q.dok} | {q.item_type.value}")
        print(f"\n{q.stem_text}")
        if q.choices:
            for c in q.choices:
                marker = " *" if c.is_correct else ""
                print(f"  {c.key}. {c.text}{marker}")
        print(f"\nAnswer: {q.answer_text}")
        print(f"\nWorked Solution:\n{q.worked_solution}")
    print(f"\n{'='*60}")
    print(f"Total: {len(all_q)}")
