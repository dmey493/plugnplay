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

The 2026-08-17 revision moved the equivalence multi-select down from Above
to Approaching (stem 5), and added sign reasoning at Below (stem 6) and at
Above (stems 8 and 9), plus a coefficient-on-a-mixed-sum item at At (stem 7).
Stems 1 to 4 already match their descriptors and were left untouched.

9 Stems from the Item Spec:
  Stem 1 (Below-MC):       Identify the expression modeled by a number line (DOK 2, easy)
  Stem 2 (Approaching-NR): Compute the product of signed integers (DOK 1, easy)
  Stem 3 (At-MC):          Apply distributive property to simplify (DOK 2, medium)
  Stem 4 (At-NR):          Multiply mixed signed numbers including fractions/decimals (DOK 1, difficult)
  Stem 5 (Approaching-MS): Identify equivalent expressions using sign rules (DOK 2, medium)
  Stem 6 (Below-MS):    Judge the sign of a product without computing (DOK 2, easy)
  Stem 7 (At-NR):       Rational coefficient on a fraction-plus-decimal sum (DOK 2, difficult)
  Stem 8 (Above-MS):    Which statements hold given sign conditions on three variables (DOK 3, difficult)
  Stem 9 (Above-MC):    Sign of a product of two variables (DOK 3, difficult)
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

    def stem5_approaching_ms(self, variant_idx: int) -> GeneratedQuestion:
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

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MS,
                               Difficulty.MEDIUM, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MS,
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

    # ================================================================
    # STEM 6: Below Proficiency - MS (DOK 2, Easy)
    # NEW. Below gained "determine whether a multiplication expression with
    # two or three rational numbers will result in a positive or negative
    # product". The point is to judge by counting negative factors, not to
    # multiply, so the numbers stay small and the options stay unevaluated.
    # ================================================================
    def stem6_below_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)

        def make(n_factors, n_negative):
            vals = []
            for k in range(n_factors):
                mag = rng.choice([2, 3, 4, 5, 6, 8])
                if rng.random() < 0.3:
                    mag = Fraction(1, rng.choice([2, 3, 4]))
                vals.append(-mag if k < n_negative else mag)
            rng.shuffle(vals)
            text = "".join(f"({_fmt(v) if not isinstance(v, Fraction) else _fmt_frac(v)})"
                           for v in vals)
            positive = (n_negative % 2 == 0)
            return text, positive

        options, seen = [], set()
        want_pos, want_neg = 2, 4
        tries = 0
        while (want_pos or want_neg) and tries < 80:
            tries += 1
            n_factors = rng.choice([2, 3])
            n_negative = rng.randint(0, n_factors)
            text, positive = make(n_factors, n_negative)
            if text in seen:
                continue
            if positive and want_pos:
                seen.add(text); options.append((text, True, None)); want_pos -= 1
            elif not positive and want_neg:
                seen.add(text)
                options.append((text, False,
                                "An odd number of negative factors makes the product negative"))
                want_neg -= 1

        rng.shuffle(options)
        choices = [QuestionChoice(key=chr(ord("a") + i), text=t, text_latex=t,
                                  is_correct=c, distractor_rationale=r)
                   for i, (t, c, r) in enumerate(options)]
        keys = [c.key.upper() for c in choices if c.is_correct]

        stem_text = "Which two expressions have a positive value?"
        worked = (
            "Count the negative factors in each expression.\n"
            "An even number of negative factors gives a positive product; "
            "an odd number gives a negative product.\n"
            "No multiplication is needed."
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW,
                                         ItemType.MS, Difficulty.EASY, 6, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MS,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=", ".join(keys), answer_latex=", ".join(keys),
            worked_solution=worked, choices=choices,
            context_scenario="sign of a product without computing",
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6, variant_index=variant_idx,
        )

    # ================================================================
    # STEM 7: At Proficiency - NR (DOK 2, Difficult)
    # NEW. "Evaluate numerical expressions written as a coefficient multiplied
    # by a sum or difference", with a decimal and a fraction inside the
    # parentheses so the student must convert before adding. Mirrors the
    # specification's own At item.
    # ================================================================
    def stem7_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(7, variant_idx)

        # Every value is a power-of-two-and-five denominator, so the answer
        # always terminates rather than repeating.
        coeff = Fraction(rng.choice([-30, -25, -20, -15, -12, 12, 15, 20, 25, 30]), 10)
        # Proper fractions only: 4/4 or 4/2 would reduce to a whole number and
        # the item would stop being a mixed-form conversion.
        frac = rng.choice([Fraction(1, 2), Fraction(1, 4), Fraction(3, 4),
                           Fraction(1, 5), Fraction(2, 5), Fraction(3, 5),
                           Fraction(4, 5)])
        dec = Fraction(rng.choice([-75, -50, -25, 25, 50, 75]), 100)
        inner = frac + dec
        while inner == 0:
            dec = Fraction(rng.choice([-75, -50, -25, 25, 50, 75]), 100)
            inner = frac + dec
        result = coeff * inner

        # A negative addend is parenthesised so the expression never reads as
        # two operators in a row.
        dec_str = f"+ {_fmt(dec)}" if dec > 0 else f"+ ({_fmt(dec)})"
        stem_text = (
            f"What is the value of {_fmt(coeff)}({_fmt_frac(frac)} {dec_str})?"
        )

        worked = (
            f"Write both numbers inside the parentheses in the same form.\n"
            f"{_fmt_frac(frac)} = {_fmt(frac)}\n"
            f"{_fmt(frac)} + ({_fmt(dec)}) = {_fmt(inner)}\n"
            f"{_fmt(coeff)} x {_fmt(inner)} = {_fmt(result)}"
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.AT,
                                         ItemType.NR, Difficulty.DIFFICULT, 7, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=_fmt(result), answer_latex=_fmt(result),
            worked_solution=worked,
            context_scenario="rational coefficient on a mixed-form sum",
            seed=self.base_seed * 1000 + 700 + variant_idx,
            stem_index=7, variant_index=variant_idx,
        )

    # ================================================================
    # STEM 8: Above Proficiency - MS (DOK 3, Difficult)
    # NEW. Reproduces the specification's item 05: given sign conditions on
    # three variables, decide which statements about their products and sums
    # must be true. Nothing is computed; the reasoning is entirely about sign.
    # ================================================================
    def stem8_above_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(8, variant_idx)

        neg, pos1, pos2 = rng.sample(["r", "s", "t", "m", "n", "p"], 3)
        conditions = f"{neg} < 0, {pos1} > 0, {pos2} > 0"

        statements = [
            (f"{neg}{pos1} < 0", True),
            (f"{neg}{pos2} < 0", True),
            (f"{neg}({pos1}{pos2}) > 0", False),
            (f"{neg}({pos1} + {pos2}) < 0", True),
            (f"{neg}({pos1} + {pos2}) > 0", False),
            (f"{neg}{pos1}{pos2} = 0", False),
        ]
        rng.shuffle(statements)
        why = {
            f"{neg}({pos1}{pos2}) > 0": "A negative times a positive product is negative",
            f"{neg}({pos1} + {pos2}) > 0": "The sum of two positives is positive, so the product is negative",
            f"{neg}{pos1}{pos2} = 0": "A product is zero only when a factor is zero, and none is",
        }
        choices = [QuestionChoice(key=chr(ord("a") + i), text=t, text_latex=t,
                                  is_correct=c,
                                  distractor_rationale=None if c else why.get(t))
                   for i, (t, c) in enumerate(statements)]
        keys = [c.key.upper() for c in choices if c.is_correct]

        stem_text = f"If {conditions}, select three true statements."
        worked = (
            f"{neg} is negative; {pos1} and {pos2} are positive.\n"
            f"Negative times positive is negative, so {neg}{pos1} < 0 and {neg}{pos2} < 0.\n"
            f"{pos1}{pos2} > 0, so {neg}({pos1}{pos2}) < 0, not greater than 0.\n"
            f"{pos1} + {pos2} > 0, so {neg}({pos1} + {pos2}) < 0.\n"
            f"No factor is zero, so the product cannot be 0."
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE,
                                         ItemType.MS, Difficulty.DIFFICULT, 8, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=ItemType.MS,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=", ".join(keys), answer_latex=", ".join(keys),
            worked_solution=worked, choices=choices,
            context_scenario="sign reasoning over three variables",
            seed=self.base_seed * 1000 + 800 + variant_idx,
            stem_index=8, variant_index=variant_idx,
        )

    # ================================================================
    # STEM 9: Above Proficiency - MC (DOK 3, Difficult)
    # NEW. "Determine whether a product is greater than, less than, or equal
    # to zero" for two variables with given signs - the simplest form of the
    # generalisation the revised Above descriptor asks for.
    # ================================================================
    def stem9_above_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(9, variant_idx)

        x, y = rng.sample(["x", "y", "a", "b", "m", "n"], 2)
        x_neg = rng.random() < 0.5
        y_neg = rng.random() < 0.5
        cond = f"{x} {'<' if x_neg else '>'} 0 and {y} {'<' if y_neg else '>'} 0"
        product_negative = x_neg != y_neg

        correct = f"{x}{y} < 0" if product_negative else f"{x}{y} > 0"
        options = [
            (correct, True, None),
            (f"{x}{y} > 0" if product_negative else f"{x}{y} < 0", False,
             "Miscounts the negative factors"),
            (f"{x}{y} = 0", False,
             "A product is zero only when a factor is zero"),
            (f"{x}{y} < {x}", False,
             "Compares the product to a factor, which the signs alone do not decide"),
        ]
        rng.shuffle(options)
        choices = [QuestionChoice(key=chr(ord("a") + i), text=t, text_latex=t,
                                  is_correct=c, distractor_rationale=r)
                   for i, (t, c, r) in enumerate(options)]
        key = next(c.key for c in choices if c.is_correct).upper()

        stem_text = f"Suppose {cond}. Which statement is true about the product {x}{y}?"
        n_neg = int(x_neg) + int(y_neg)
        worked = (
            f"There {'is' if n_neg == 1 else 'are'} {n_neg} negative "
            f"factor{'' if n_neg == 1 else 's'}.\n"
            f"An {'odd' if n_neg % 2 else 'even'} number of negative factors gives a "
            f"{'negative' if product_negative else 'positive'} product.\n"
            f"So {correct}."
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE,
                                         ItemType.MC, Difficulty.DIFFICULT, 9, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{key}. {correct}", answer_latex=f"{key}. {correct}",
            worked_solution=worked, choices=choices,
            context_scenario="sign of a product of two variables",
            seed=self.base_seed * 1000 + 900 + variant_idx,
            stem_index=9, variant_index=variant_idx,
        )

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_approaching_nr,
            self.stem3_at_mc,
            self.stem4_at_nr,
            self.stem5_approaching_ms,
            self.stem6_below_ms,
            self.stem7_at_nr,
            self.stem8_above_ms,
            self.stem9_above_mc,
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
            5: self.stem5_approaching_ms,
            6: self.stem6_below_ms,
            7: self.stem7_at_nr,
            8: self.stem8_above_ms,
            9: self.stem9_above_mc,
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
