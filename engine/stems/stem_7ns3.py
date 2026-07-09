"""
Stem generator for 7.NS.3:
  Use the properties of operations, particularly the distributive property,
  leading to products such as (-1)(-1) = 1 and the rules for multiplying
  signed numbers.

Content Limits:
  - Rational numbers can be integers, fractions, or decimals
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: Only integers are used
  Medium: Multiplication with one non-integer rational number
  Difficult: Multiplication of 2 or more non-integer rational numbers

5 Stems from the Item Spec:
  Stem 1 (Below-MC):       Identify the expression modeled by a number line (DOK 2, easy)
  Stem 2 (Approaching-NR): Compute the product of signed integers (DOK 1, easy)
  Stem 3 (At-MC):          Apply distributive property to simplify (DOK 2, medium)
  Stem 4 (At-NR):          Multiply mixed signed numbers including fractions/decimals (DOK 1, difficult)
  Stem 5 (Above-MS):       Identify equivalent expressions using sign rules (DOK 2, difficult)
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
from engine.svg_helpers import multiplication_jumps_svg


STANDARD_CODE = "7.NS.3"
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
    """Format a Fraction as a mixed number string (e.g. -1 1/2 or 2 3/4)."""
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


def _fmt_product_parens(val):
    """Format a signed value in parentheses for product notation, e.g. (-3) or (4)."""
    return f"({_fmt(val)})"


class Stem7NS3:
    """Generates ~20 variants for each of 5 stems from the 7.NS.3 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 2, Easy)
    # Identify which expression is modeled by a number line with
    # repeated jumps. E.g., 3 jumps of -2 from 0 to -6  ->  -2 x 3
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        # Generate two signed integers with opposite signs for the model
        # jump_size is the value of each jump, num_jumps is how many
        configs = [
            # (jump_size, num_jumps) — must have opposite signs so product is negative
            (-2, 3), (-3, 2), (-2, 4), (-3, 3), (-4, 2),
            (-1, 5), (-2, 5), (-5, 2), (-3, 4), (-4, 3),
            (2, -3), (3, -2), (4, -2), (5, -2), (2, -4),
            (-2, 2), (-3, 5), (-5, 3), (-4, 4), (-1, 6),
        ]
        jump_size, num_jumps = configs[variant_idx % len(configs)]
        product = jump_size * num_jumps

        # The correct expression: jump_size x num_jumps
        correct_expr = f"{_fmt(jump_size)} x {_fmt(num_jumps)}"

        # Generate distractors (common errors)
        distractors = set()
        # Wrong sign on jump_size
        distractors.add(f"{_fmt(-jump_size)} x {_fmt(num_jumps)}")
        # Wrong sign on num_jumps
        distractors.add(f"{_fmt(jump_size)} x {_fmt(-num_jumps)}")
        # Both signs flipped (same product, different expression)
        distractors.add(f"{_fmt(-jump_size)} x {_fmt(-num_jumps)}")
        # Confused with addition: 0 x product
        distractors.add(f"0 x {_fmt(product)}")
        # Swapped factors with wrong sign
        distractors.add(f"{_fmt(num_jumps)} x {_fmt(-jump_size)}")

        distractors.discard(correct_expr)
        dist_list = list(distractors)[:3]

        all_options = [(correct_expr, True)] + [(d, False) for d in dist_list]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        # Generate number line SVG
        svg = multiplication_jumps_svg(jump_size, num_jumps)

        stem_text = "Which expression is modeled by the number line? [FIGURE]"

        worked = (
            f"The number line shows {abs(num_jumps)} jumps of {abs(jump_size)} "
            f"{'to the left' if product < 0 else 'to the right'}, "
            f"starting from 0 and landing on {product}.\n"
            f"This models: {correct_expr} = {_fmt(product)}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="number line model of multiplication",
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - NR (DOK 1, Easy)
    # Compute the product of three signed integers
    # e.g., (-2)(5)(-3) = 30
    # ================================================================

    def stem2_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        # Three signed integers, at least one negative
        a = gen.signed_integer(-9, 9)
        b = gen.signed_integer(-9, 9)
        c = gen.signed_integer(-9, 9)
        # Ensure at least one is negative
        if a > 0 and b > 0 and c > 0:
            a = -a

        product = a * b * c
        correct_str = _fmt(product)

        stem_text = f"Solve.\n\n({_fmt(a)})({_fmt(b)})({_fmt(c)})"

        # Step by step
        partial = a * b
        worked = (
            f"Step 1: ({_fmt(a)})({_fmt(b)}) = {_fmt(partial)}\n"
            f"Step 2: ({_fmt(partial)})({_fmt(c)}) = {_fmt(product)}\n"
            f"Answer: {correct_str}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_str, answer_latex=f"${correct_str}$",
            worked_solution=worked,
            context_scenario="product of three signed integers",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: At Proficiency - MC (DOK 2, Medium)
    # Apply the distributive property to simplify an expression
    # e.g., Which equation correctly simplifies -1/2(9 + 3)?
    # ================================================================

    def stem3_at_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        # Generate a(b + c) where a is a signed fraction or decimal, b and c are integers
        # Medium: one non-integer rational number
        denom = rng.choice([2, 4, 5])
        numer = rng.choice([i for i in range(1, denom) if i != 0])
        sign = rng.choice([-1, 1])
        a = Fraction(sign * numer, denom)

        b = int(gen.signed_integer(-12, 12))
        c = int(gen.signed_integer(-12, 12))
        # Ensure b and c are not both zero
        while b == 0 and c == 0:
            b = int(gen.signed_integer(-12, 12))
            c = int(gen.signed_integer(-12, 12))

        # Correct application: a*b + a*c
        ab = a * b
        ac = a * c
        result = ab + ac

        a_str = _fmt_frac(a)
        ab_str = _fmt(ab)
        ac_str = _fmt(ac)
        result_str = _fmt(result)

        # Format the inner operation
        if c >= 0:
            inner = f"{b} + {c}"
        else:
            inner = f"{b} - {abs(c)}"

        # Build correct equation string
        if ac >= 0:
            correct_eq = f"{a_str}({inner}) = {ab_str} + {ac_str} = {result_str}"
        else:
            correct_eq = f"{a_str}({inner}) = {ab_str} - {_fmt(abs(ac))} = {result_str}"

        # Distractors: common errors
        dist_eqs = []

        # Error 1: distribute to first term only (a*b + c)
        err1_result = ab + c
        if c >= 0:
            err1 = f"{a_str}({inner}) = {ab_str} + {c} = {_fmt(err1_result)}"
        else:
            err1 = f"{a_str}({inner}) = {ab_str} - {abs(c)} = {_fmt(err1_result)}"
        if _fmt(err1_result) != result_str:
            dist_eqs.append(err1)

        # Error 2: wrong sign on distribution
        wrong_ab = -a * b
        wrong_ac = -a * c
        err2_result = wrong_ab + wrong_ac
        if wrong_ac >= 0:
            err2 = f"{a_str}({inner}) = {_fmt(wrong_ab)} + {_fmt(wrong_ac)} = {_fmt(err2_result)}"
        else:
            err2 = f"{a_str}({inner}) = {_fmt(wrong_ab)} - {_fmt(abs(wrong_ac))} = {_fmt(err2_result)}"
        if _fmt(err2_result) != result_str:
            dist_eqs.append(err2)

        # Error 3: added a + b + c instead of distributing
        err3_result = a + b + c
        err3 = f"{a_str}({inner}) = {a_str} + {b} + {c} = {_fmt(err3_result)}"
        if _fmt(err3_result) != result_str:
            dist_eqs.append(err3)

        # Ensure we have at least 3 distractors
        while len(dist_eqs) < 3:
            offset = rng.choice([1, -1, 2, -2])
            fake_result = result + offset
            if ac >= 0:
                fake = f"{a_str}({inner}) = {ab_str} + {ac_str} = {_fmt(fake_result)}"
            else:
                fake = f"{a_str}({inner}) = {ab_str} - {_fmt(abs(ac))} = {_fmt(fake_result)}"
            if fake not in dist_eqs and _fmt(fake_result) != result_str:
                dist_eqs.append(fake)
        dist_eqs = dist_eqs[:3]

        all_options = [(correct_eq, True)] + [(d, False) for d in dist_eqs]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = f"Which equation correctly simplifies {a_str}({inner})?"

        worked = (
            f"Use the distributive property: a(b + c) = ab + ac\n"
            f"{a_str}({inner})\n"
            f"= {a_str} x {b} + {a_str} x ({c})\n"
            f"= {ab_str} + {ac_str}\n"
            f"= {result_str}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MC,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="distributive property with signed numbers",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At Proficiency - NR (DOK 1, Difficult)
    # Multiply mixed signed numbers including fractions/decimals
    # e.g., (-1 1/2)(0.25)(-3) = 1.125
    # ================================================================

    def stem4_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        # Difficult: two or more non-integer rational numbers
        # Generate three factors: a mixed number, a decimal, and an integer
        # All signed
        whole_part = rng.randint(1, 3)
        frac_denom = rng.choice([2, 4])
        frac_numer = rng.randint(1, frac_denom - 1)
        sign_a = rng.choice([-1, 1])
        a = Fraction(sign_a * (whole_part * frac_denom + frac_numer), frac_denom)

        # Decimal factor (1 decimal place)
        dec_choices = [Fraction(1, 4), Fraction(1, 2), Fraction(3, 4),
                       Fraction(1, 5), Fraction(2, 5), Fraction(3, 5)]
        b = rng.choice(dec_choices) * rng.choice([-1, 1])

        # Integer factor
        c = Fraction(rng.choice([-1, 1]) * rng.randint(2, 6))

        product = a * b * c

        a_str = _fmt_mixed(a)
        b_str = _fmt(float(b))
        c_str = _fmt(c)

        # Display as decimal
        product_float = float(product)
        if product_float == int(product_float):
            correct_str = str(int(product_float))
        else:
            correct_str = f"{product_float:.4f}".rstrip('0').rstrip('.')

        stem_text = f"Solve.\n\n({a_str})({b_str})({c_str})"

        partial = a * b
        worked = (
            f"Step 1: ({a_str})({b_str}) = {_fmt(float(partial))}\n"
            f"Step 2: ({_fmt(float(partial))})({c_str}) = {correct_str}\n"
            f"Answer: {correct_str}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.DIFFICULT, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_str, answer_latex=f"${correct_str}$",
            worked_solution=worked,
            context_scenario="product of signed rationals (mixed types)",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above Proficiency - MS (DOK 2, Difficult)
    # Select two expressions equivalent to a given product of fractions
    # e.g., Select two expressions equivalent to (-4/9)(3/4)
    # ================================================================

    def stem5_above_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        # Generate two signed fractions
        denom_a = rng.choice([3, 4, 5, 6, 7, 8, 9])
        numer_a = rng.randint(1, denom_a - 1)
        sign_a = rng.choice([-1, 1])

        denom_b = rng.choice([d for d in [3, 4, 5, 6, 7, 8, 9] if d != denom_a])
        numer_b = rng.randint(1, denom_b - 1)
        sign_b = rng.choice([-1, 1])

        a = Fraction(sign_a * numer_a, denom_a)
        b = Fraction(sign_b * numer_b, denom_b)
        product = a * b

        a_str = _fmt_frac(a)
        b_str = _fmt_frac(b)
        product_str = _fmt_frac(product)

        # Build options:
        # The original expression: (a)(b)
        # Correct equivalents:
        # 1. The simplified product value
        # 2. Moving the negative sign: e.g., (-a/b)(c/d) = (a/b)(-c/d)
        # 3. Both negatives removed if both negative: (-a/b)(-c/d) = (a/b)(c/d)

        options = []

        # Always correct: the simplified product
        options.append((_fmt_frac(product), True))

        # Correct: move the negative sign to the other factor
        # If a is negative: (-|a|)(b) == (|a|)(-b)
        if sign_a < 0:
            equiv = f"({_fmt_frac(abs(a))})({_fmt_frac(-b)})"
            options.append((equiv, True))
        elif sign_b < 0:
            equiv = f"({_fmt_frac(-a)})({_fmt_frac(abs(b))})"
            options.append((equiv, True))
        else:
            # Both positive -- equivalent: (-|a|)(-|b|)
            equiv = f"({_fmt_frac(-a)})({_fmt_frac(-b)})"
            options.append((equiv, True))

        # Distractors (wrong):
        # Wrong sign on product
        options.append((_fmt_frac(-product), False))

        # Both absolute values (ignoring signs)
        abs_product = abs(product)
        if _fmt_frac(abs_product) != product_str and _fmt_frac(abs_product) != _fmt_frac(-product):
            options.append((_fmt_frac(abs_product), False))

        # Same factors but with same sign (wrong equivalence)
        if sign_a * sign_b < 0:
            # Product is negative; both positive factors would be wrong
            wrong = f"({_fmt_frac(abs(a))})({_fmt_frac(abs(b))})"
            options.append((wrong, False))
        else:
            # Product is positive; one-negative pairing is wrong
            wrong = f"({_fmt_frac(-abs(a))})({_fmt_frac(abs(b))})"
            options.append((wrong, False))

        # Ensure we have at least 5 options total (2 correct, 3+ wrong)
        # Add another wrong one if needed
        wrong_product2 = product + Fraction(1, product.denominator if product.denominator > 1 else 2)
        if _fmt_frac(wrong_product2) not in [o[0] for o in options]:
            options.append((_fmt_frac(wrong_product2), False))

        # Deduplicate by text
        seen = set()
        unique_options = []
        for text, correct in options:
            if text not in seen:
                seen.add(text)
                unique_options.append((text, correct))
        options = unique_options

        # Ensure at least 2 correct and 3 wrong
        correct_count = sum(1 for _, c in options if c)
        wrong_count = sum(1 for _, c in options if not c)

        while wrong_count < 3:
            offset = Fraction(rng.choice([1, -1]), rng.choice([2, 3, 4, 5]))
            fake = _fmt_frac(product + offset)
            if fake not in seen:
                seen.add(fake)
                options.append((fake, False))
                wrong_count += 1

        # Take 2 correct + 3 wrong = 5 options
        correct_opts = [o for o in options if o[1]][:2]
        wrong_opts = [o for o in options if not o[1]][:3]
        final_options = correct_opts + wrong_opts
        rng.shuffle(final_options)

        choices = []
        for i, (text, is_correct) in enumerate(final_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letters = ", ".join(c.key for c in choices if c.is_correct)

        stem_text = f"Select two expressions that are equivalent to ({a_str})({b_str})."

        worked = (
            f"({a_str})({b_str}) = {product_str}\n"
            f"Sign rules: a negative times a positive is negative; "
            f"a negative times a negative is positive.\n"
            f"Moving the negative: -(p/q) = (-p)/q = p/(-q)\n"
            f"Correct answers: {correct_letters}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MS,
                               Difficulty.DIFFICULT, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.MS,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letters, answer_latex=correct_letters,
            worked_solution=worked,
            choices=choices, context_scenario="equivalent signed fraction products",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_approaching_nr,
            self.stem3_at_mc,
            self.stem4_at_nr,
            self.stem5_above_ms,
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
            2: self.stem2_approaching_nr,
            3: self.stem3_at_mc,
            4: self.stem4_at_nr,
            5: self.stem5_above_ms,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-5.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 7.NS.3 question variants...")
    gen = Stem7NS3(seed=42)
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
