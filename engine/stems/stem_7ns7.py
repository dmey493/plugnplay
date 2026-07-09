"""
Stem generator for 7.NS.7:
  Compute fluently with rational numbers using an algorithmic approach.

Content Limits:
  - Rational numbers: integers, fractions, or decimals
  - Decimals limited to hundredths
  - May mix integers, fractions, and/or decimals
  - Order of operations and properties of operations may be included
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: one operation, decimals limited to tenths, no fractions
  Medium: two operations, decimals to hundredths, fractions with common denominators
  Difficult: three or more operations

6 Stems from the Item Spec:
  Stem 1 (Below-NR):       Simplify integer expression with 2 operations (DOK 1, medium)
  Stem 2 (Below-NR):       Evaluate integer expression with parentheses (DOK 1, medium)
  Stem 3 (Approaching-NR): Simplify expression with decimals (DOK 1, easy/medium)
  Stem 4 (At-NR):          Simplify expression with mixed rationals, 2 ops (DOK 1, medium)
  Stem 5 (At-NR):          Simplify expression with mixed rationals, 3 ops (DOK 1, difficult)
  Stem 6 (Above-MS):       Select all equivalent expressions (DOK 1, difficult)
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


STANDARD_CODE = "7.NS.7"
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


def _fmt_signed(val):
    """Format a signed value, wrapping negatives in parentheses for expressions."""
    s = _fmt(val)
    if isinstance(val, Fraction) and val < 0:
        return f"({s})"
    if isinstance(val, (int, float)) and val < 0:
        return f"({s})"
    return s


def _fmt_decimal_2(val):
    """Format a Fraction as a decimal to at most 2 places."""
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return str(int(val))
        f = float(val)
        if f == int(f):
            return str(int(f))
        # Show up to 2 decimal places
        s = f"{f:.2f}".rstrip('0').rstrip('.')
        return s
    return _fmt(val)


class Stem7NS7:
    """Generates ~20 variants for each of 5 stems from the 7.NS.7 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - NR (DOK 1, Medium)
    # Simplify a signed integer expression with 2 operations
    # e.g., -6 x 7 + 3 x (-4) = -42 + (-12) = -54 ... item spec says answer -42
    # Pattern: a x b + c  or  a x b - c  with signed integers
    # ================================================================

    def stem1_below_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        # Generate a 2-operation integer expression
        pattern = rng.choice(["mult_add", "mult_sub", "add_mult"])

        if pattern == "mult_add":
            # a x b + c
            a = gen.signed_integer(-9, 9)
            b = gen.signed_integer(-9, 9)
            c = gen.signed_integer(-20, 20)
            product = a * b
            answer = product + c

            a_s = _fmt(a)
            b_s = _fmt_signed(b)
            c_s = _fmt(c)

            # Build expression text
            if c >= 0:
                expr_text = f"{a_s} x {b_s} + {_fmt(c)}"
            else:
                expr_text = f"{a_s} x {b_s} - {_fmt(abs(c))}"

            worked = (
                f"{expr_text}\n"
                f"= {_fmt(product)} + {_fmt(c)}   (multiply first: {a_s} x {b_s} = {_fmt(product)})\n"
                f"= {_fmt(answer)}"
            )

        elif pattern == "mult_sub":
            # a x b - c
            a = gen.signed_integer(-9, 9)
            b = gen.signed_integer(-9, 9)
            c = gen.signed_integer(1, 20)
            product = a * b
            answer = product - c

            a_s = _fmt(a)
            b_s = _fmt_signed(b)

            expr_text = f"{a_s} x {b_s} - {_fmt(c)}"

            worked = (
                f"{expr_text}\n"
                f"= {_fmt(product)} - {_fmt(c)}   (multiply first: {a_s} x {b_s} = {_fmt(product)})\n"
                f"= {_fmt(answer)}"
            )

        else:  # add_mult
            # a + b x c
            a = gen.signed_integer(-20, 20)
            b = gen.signed_integer(-9, 9)
            c = gen.signed_integer(-9, 9)
            product = b * c
            answer = a + product

            a_s = _fmt(a)
            b_s = _fmt(b)
            c_s = _fmt_signed(c)

            expr_text = f"{a_s} + {b_s} x {c_s}"

            worked = (
                f"{expr_text}\n"
                f"= {_fmt(a)} + {_fmt(product)}   (multiply first: {b_s} x {c_s} = {_fmt(product)})\n"
                f"= {_fmt(answer)}"
            )

        answer_str = _fmt(answer)

        stem_text = f"Simplify the expression.\n\n{expr_text}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.NR,
                               Difficulty.MEDIUM, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_str, answer_latex=f"${answer_str}$",
            worked_solution=worked,
            context_scenario="signed integer expression, 2 operations",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Below Proficiency - NR (DOK 1, Medium)
    # Evaluate integer expression with parentheses
    # e.g., -17 + 12(6 - 2) = -17 + 48 = 31
    # ================================================================

    def stem2_below_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        # Pattern: a + b(c - d) or a - b(c + d) with integers
        pattern = rng.choice(["add_mult_paren", "sub_mult_paren"])

        if pattern == "add_mult_paren":
            # a + b(c - d)  where c > d for clean subtraction
            a = gen.signed_integer(-20, 20)
            b = gen.signed_integer(2, 12)
            d = int(gen.whole_number(1, 8))
            diff = int(gen.whole_number(1, 8))
            c = d + diff
            paren_val = Fraction(c - d)
            product = b * paren_val
            answer = a + product

            a_s = _fmt(a)
            b_s = _fmt(b)

            expr_text = f"{a_s} + {b_s}({c} - {d})"

            worked = (
                f"{expr_text}\n"
                f"= {a_s} + {b_s}({_fmt(paren_val)})   (evaluate {c} - {d} = {_fmt(paren_val)})\n"
                f"= {a_s} + {_fmt(product)}   (multiply: {b_s} x {_fmt(paren_val)} = {_fmt(product)})\n"
                f"= {_fmt(answer)}"
            )

        else:
            # a - b(c + d) with integers
            a = gen.signed_integer(-5, 30)
            b = gen.signed_integer(2, 8)
            c = int(gen.whole_number(1, 6))
            d = int(gen.whole_number(1, 6))
            paren_val = Fraction(c + d)
            product = b * paren_val
            answer = a - product

            a_s = _fmt(a)
            b_s = _fmt(b)

            expr_text = f"{a_s} - {b_s}({c} + {d})"

            worked = (
                f"{expr_text}\n"
                f"= {a_s} - {b_s}({_fmt(paren_val)})   (evaluate {c} + {d} = {_fmt(paren_val)})\n"
                f"= {a_s} - {_fmt(product)}   (multiply: {b_s} x {_fmt(paren_val)} = {_fmt(product)})\n"
                f"= {_fmt(answer)}"
            )

        answer_str = _fmt(answer)

        stem_text = f"Enter the value of the expression.\n\n{expr_text}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.NR,
                               Difficulty.MEDIUM, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_str, answer_latex=f"${answer_str}$",
            worked_solution=worked,
            context_scenario="integer expression with parentheses",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - NR (DOK 1, Easy/Medium)
    # Simplify expression with decimals
    # e.g., -3.4 x 2.5 + 1.2 = -7.3  (item spec: -13.72 etc.)
    # Easy: one op, tenths. Medium: two ops, hundredths.
    # ================================================================

    def stem3_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        if variant_idx % 2 == 0:
            # Easy: one operation with tenths
            difficulty = Difficulty.EASY
            a = gen.signed_decimal(-9.9, 9.9, places=1)
            b = gen.signed_decimal(-9.9, 9.9, places=1)
            op = rng.choice(["add", "sub", "mult"])

            a_s = _fmt_decimal_2(a)
            b_s = _fmt_decimal_2(b)

            if op == "add":
                answer = a + b
                if b >= 0:
                    expr_text = f"{a_s} + {b_s}"
                else:
                    expr_text = f"{a_s} + ({b_s})"
                worked = f"{expr_text}\n= {_fmt_decimal_2(answer)}"
            elif op == "sub":
                answer = a - b
                if b >= 0:
                    expr_text = f"{a_s} - {b_s}"
                else:
                    expr_text = f"{a_s} - ({b_s})"
                worked = f"{expr_text}\n= {_fmt_decimal_2(answer)}"
            else:  # mult
                answer = a * b
                b_display = f"({b_s})" if b < 0 else b_s
                expr_text = f"{a_s} x {b_display}"
                worked = f"{expr_text}\n= {_fmt_decimal_2(answer)}"
        else:
            # Medium: two operations with decimals to hundredths
            difficulty = Difficulty.MEDIUM
            a = gen.signed_decimal(-9.9, 9.9, places=1)
            b = gen.signed_integer(-9, 9)
            c = gen.signed_decimal(-9.9, 9.9, places=1)

            # a x b + c  (multiply first, then add)
            product = a * b
            answer = product + c

            a_s = _fmt_decimal_2(a)
            b_s = _fmt(b)
            b_display = f"({b_s})" if b < 0 else b_s
            c_s = _fmt_decimal_2(c)

            if c >= 0:
                expr_text = f"{a_s} x {b_display} + {c_s}"
            else:
                expr_text = f"{a_s} x {b_display} + ({c_s})"

            worked = (
                f"{expr_text}\n"
                f"= {_fmt_decimal_2(product)} + {c_s}   (multiply: {a_s} x {b_display} = {_fmt_decimal_2(product)})\n"
                f"= {_fmt_decimal_2(answer)}"
            )

        answer_str = _fmt_decimal_2(answer)

        stem_text = f"Simplify the expression.\n\n{expr_text}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               difficulty, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=difficulty, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_str, answer_latex=f"${answer_str}$",
            worked_solution=worked,
            context_scenario="decimal expression",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At Proficiency - NR (DOK 1, Medium)
    # Simplify expression with mixed rationals, 2 operations
    # e.g., -3/4 x 8 + 5.25 = -6 + 5.25 = -0.75
    # Fractions with common denominators or clean decimal results
    # ================================================================

    def stem4_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        # Build expressions mixing fractions, decimals, and integers
        pattern = rng.choice(["frac_mult_add", "dec_add_frac", "int_sub_frac_mult"])

        if pattern == "frac_mult_add":
            # (a/b) x c + d  where (a/b) x c is clean
            denom = rng.choice([2, 4, 5, 8])
            numer = rng.choice([n for n in range(-denom + 1, denom) if n != 0])
            frac = Fraction(numer, denom)
            c = Fraction(rng.choice([d for d in [denom, denom * 2, denom * 3] if d <= 20]))
            product = frac * c
            d = gen.signed_decimal(-9.9, 9.9, places=1)
            answer = product + d

            frac_s = _fmt_frac(frac)
            c_s = _fmt(c)
            d_s = _fmt_decimal_2(d)

            if d >= 0:
                expr_text = f"{frac_s} x {c_s} + {d_s}"
            else:
                expr_text = f"{frac_s} x {c_s} + ({d_s})"

            worked = (
                f"{expr_text}\n"
                f"= {_fmt_decimal_2(product)} + {d_s}   (multiply: {frac_s} x {c_s} = {_fmt_decimal_2(product)})\n"
                f"= {_fmt_decimal_2(answer)}"
            )

        elif pattern == "dec_add_frac":
            # a + b/c  where b/c has a clean decimal form
            a = gen.signed_decimal(-9.9, 9.9, places=1)
            denom = rng.choice([2, 4, 5])
            numer = rng.choice([n for n in range(-denom + 1, denom) if n != 0])
            frac = Fraction(numer, denom)
            answer = a + frac

            a_s = _fmt_decimal_2(a)
            frac_s = _fmt_frac(frac)

            if frac >= 0:
                expr_text = f"{a_s} + {frac_s}"
            else:
                expr_text = f"{a_s} + ({frac_s})"

            worked = (
                f"{expr_text}\n"
                f"= {a_s} + {_fmt_decimal_2(frac)}   (convert {frac_s} = {_fmt_decimal_2(frac)})\n"
                f"= {_fmt_decimal_2(answer)}"
            )

        else:  # int_sub_frac_mult
            # a - (b/c) x d  where result is clean
            a = gen.signed_integer(-15, 15)
            denom = rng.choice([2, 4, 5])
            numer = rng.choice([n for n in range(1, denom) if n != 0])
            frac = Fraction(numer, denom)
            d = Fraction(rng.choice([denom, denom * 2]))
            product = frac * d
            answer = a - product

            a_s = _fmt(a)
            frac_s = _fmt_frac(frac)
            d_s = _fmt(d)

            expr_text = f"{a_s} - {frac_s} x {d_s}"

            worked = (
                f"{expr_text}\n"
                f"= {a_s} - {_fmt_decimal_2(product)}   (multiply: {frac_s} x {d_s} = {_fmt_decimal_2(product)})\n"
                f"= {_fmt_decimal_2(answer)}"
            )

        answer_str = _fmt_decimal_2(answer)

        stem_text = f"Simplify the expression.\n\n{expr_text}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_str, answer_latex=f"${answer_str}$",
            worked_solution=worked,
            context_scenario="mixed rational expression, 2 operations",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: At Proficiency - NR (DOK 1, Difficult)
    # Simplify expression with mixed rationals, 3+ operations
    # e.g., -2 x (3/4 + 1.5) - 6 = -2 x 2.25 - 6 = -4.5 - 6 = -10.5
    # ================================================================

    def stem5_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        # Multiple patterns for 3-operation expressions
        pattern = rng.choice(["mult_paren_sub", "add_mult_sub", "paren_mult_add"])

        if pattern == "mult_paren_sub":
            # a x (b + c) - d  where b and c are mixed types
            a = gen.signed_integer(-6, 6)
            while a == 0:
                a = gen.signed_integer(-6, 6)

            # b is a fraction, c is a decimal
            denom = rng.choice([2, 4, 5])
            numer = rng.choice([n for n in range(1, denom) if n != 0])
            b = Fraction(numer, denom)
            c = gen.signed_decimal(-4.9, 4.9, places=1)

            paren_val = b + c
            product = a * paren_val
            d = gen.signed_integer(-10, 10)
            answer = product - d

            a_s = _fmt(a)
            b_s = _fmt_frac(b)
            c_s = _fmt_decimal_2(c)
            d_s = _fmt(d)

            if c >= 0:
                paren_text = f"{b_s} + {c_s}"
            else:
                paren_text = f"{b_s} + ({c_s})"

            expr_text = f"{a_s} x ({paren_text}) - {d_s}"

            worked = (
                f"{expr_text}\n"
                f"= {a_s} x ({_fmt_decimal_2(paren_val)}) - {d_s}   "
                f"(evaluate inside parentheses: {b_s} + {c_s} = {_fmt_decimal_2(paren_val)})\n"
                f"= {_fmt_decimal_2(product)} - {d_s}   "
                f"(multiply: {a_s} x {_fmt_decimal_2(paren_val)} = {_fmt_decimal_2(product)})\n"
                f"= {_fmt_decimal_2(answer)}"
            )

        elif pattern == "add_mult_sub":
            # a + b x c - d  where order of operations matters
            a = gen.signed_decimal(-9.9, 9.9, places=1)
            b = gen.signed_integer(-6, 6)
            while b == 0:
                b = gen.signed_integer(-6, 6)
            c = gen.signed_integer(-6, 6)
            while c == 0:
                c = gen.signed_integer(-6, 6)
            d = gen.signed_decimal(-9.9, 9.9, places=1)

            product = b * c
            sum_part = a + product
            answer = sum_part - d

            a_s = _fmt_decimal_2(a)
            b_s = _fmt(b)
            c_s = _fmt_signed(c)
            d_s = _fmt_decimal_2(d)

            if d >= 0:
                expr_text = f"{a_s} + {b_s} x {c_s} - {d_s}"
            else:
                expr_text = f"{a_s} + {b_s} x {c_s} - ({d_s})"

            worked = (
                f"{expr_text}\n"
                f"= {a_s} + {_fmt(product)} - {d_s}   "
                f"(multiply first: {b_s} x {c_s} = {_fmt(product)})\n"
                f"= {_fmt_decimal_2(sum_part)} - {d_s}   (add: {a_s} + {_fmt(product)} = {_fmt_decimal_2(sum_part)})\n"
                f"= {_fmt_decimal_2(answer)}"
            )

        else:  # paren_mult_add
            # (a + b) x c + d
            a = gen.signed_integer(-8, 8)
            # b is a fraction with clean decimal
            denom = rng.choice([2, 4, 5])
            numer = rng.choice([n for n in range(-denom + 1, denom) if n != 0])
            b = Fraction(numer, denom)
            c = gen.signed_integer(-6, 6)
            while c == 0:
                c = gen.signed_integer(-6, 6)
            d = gen.signed_decimal(-9.9, 9.9, places=1)

            paren_val = Fraction(a) + b
            product = paren_val * c
            answer = product + d

            a_s = _fmt(a)
            b_s = _fmt_frac(b)
            c_s = _fmt(c)
            d_s = _fmt_decimal_2(d)

            if b >= 0:
                paren_text = f"{a_s} + {b_s}"
            else:
                paren_text = f"{a_s} + ({b_s})"

            c_display = _fmt_signed(c) if c < 0 else c_s

            if d >= 0:
                expr_text = f"({paren_text}) x {c_display} + {d_s}"
            else:
                expr_text = f"({paren_text}) x {c_display} + ({d_s})"

            worked = (
                f"{expr_text}\n"
                f"= ({_fmt_decimal_2(paren_val)}) x {c_display} + {d_s}   "
                f"(evaluate inside parentheses: {a_s} + {b_s} = {_fmt_decimal_2(paren_val)})\n"
                f"= {_fmt_decimal_2(product)} + {d_s}   "
                f"(multiply: {_fmt_decimal_2(paren_val)} x {c_display} = {_fmt_decimal_2(product)})\n"
                f"= {_fmt_decimal_2(answer)}"
            )

        answer_str = _fmt_decimal_2(answer)

        stem_text = f"Simplify the expression.\n\n{expr_text}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.DIFFICULT, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_str, answer_latex=f"${answer_str}$",
            worked_solution=worked,
            context_scenario="mixed rational expression, 3 operations",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    # STEM 6: Above Proficiency - MS (DOK 1, Difficult)
    # Select ALL expressions equivalent to a given expression.
    # Uses 3+ operations and properties of operations.
    # Spec: "Identify one or more equivalent expressions when one
    #        expression is given."
    # ================================================================

    def stem6_above_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)

        # Generate a base expression: a(b + c) - d  (distributive property)
        a = gen.signed_integer(-6, 6)
        while a == 0 or a == 1:
            a = gen.signed_integer(-6, 6)

        denom = rng.choice([2, 4])
        numer = rng.choice([n for n in range(1, denom) if n != 0])
        b = Fraction(numer, denom)
        c = gen.signed_integer(-8, 8)
        while c == 0:
            c = gen.signed_integer(-8, 8)
        d = gen.signed_integer(-10, 10)
        while d == 0:
            d = gen.signed_integer(-10, 10)

        # Compute the value
        paren_val = b + c
        product = a * paren_val
        answer_val = product - d

        # Build the original expression text
        b_s = _fmt_frac(b)
        c_s = _fmt(c)
        if c >= 0:
            paren_text = f"{b_s} + {c_s}"
        else:
            paren_text = f"{b_s} - {_fmt(abs(c))}"

        a_s = _fmt(a)
        d_s = _fmt(d)
        if d >= 0:
            orig_expr = f"{a_s}({paren_text}) - {d_s}"
        else:
            orig_expr = f"{a_s}({paren_text}) + {_fmt(abs(d))}"

        # Build equivalent and non-equivalent expressions
        ab = a * b
        ac = a * c

        options = []

        # Equivalent 1: Distributive property applied: ab + ac - d
        ab_s = _fmt_frac(ab) if isinstance(ab, Fraction) and ab.denominator != 1 else _fmt(ab)
        ac_s = _fmt(ac)
        if ac >= 0 and d >= 0:
            eq1 = f"{ab_s} + {ac_s} - {d_s}"
        elif ac >= 0 and d < 0:
            eq1 = f"{ab_s} + {ac_s} + {_fmt(abs(d))}"
        elif ac < 0 and d >= 0:
            eq1 = f"{ab_s} - {_fmt(abs(ac))} - {d_s}"
        else:
            eq1 = f"{ab_s} - {_fmt(abs(ac))} + {_fmt(abs(d))}"
        options.append((eq1, True, "Distributive property"))

        # Equivalent 2: Computed value as a single number
        eq2 = _fmt_decimal_2(answer_val)
        options.append((eq2, True, "Fully simplified"))

        # Non-equivalent 1: Forgot to distribute to b (only multiplied c)
        wrong1_val = a * c - d  # forgot to multiply b
        w1 = _fmt_decimal_2(Fraction(a * c) - d)
        if w1 != eq2:
            options.append((w1, False, "Forgot to distribute a to the fraction"))

        # Non-equivalent 2: Wrong sign on d (added instead of subtracted)
        wrong2_val = product + d
        w2 = _fmt_decimal_2(wrong2_val)
        if w2 != eq2:
            options.append((w2, False, "Added d instead of subtracting"))

        # Non-equivalent 3: Distributed but wrong sign on ac
        wrong_ac = a * (-c)  # negated c
        wrong3_ab_s = ab_s
        wrong3_ac_s = _fmt(wrong_ac)
        if wrong_ac >= 0 and d >= 0:
            w3 = f"{wrong3_ab_s} + {wrong3_ac_s} - {d_s}"
        elif wrong_ac >= 0 and d < 0:
            w3 = f"{wrong3_ab_s} + {wrong3_ac_s} + {_fmt(abs(d))}"
        elif wrong_ac < 0 and d >= 0:
            w3 = f"{wrong3_ab_s} - {_fmt(abs(wrong_ac))} - {d_s}"
        else:
            w3 = f"{wrong3_ab_s} - {_fmt(abs(wrong_ac))} + {_fmt(abs(d))}"
        if w3 != eq1:
            options.append((w3, False, "Wrong sign when distributing"))

        # Ensure we have at least 5 options (2 correct + 3 wrong)
        # Add another wrong if needed
        if len(options) < 5:
            # Commutative error: swap order but wrong operation
            wrong4_val = d - product
            w4 = _fmt_decimal_2(wrong4_val)
            if w4 != eq2:
                options.append((w4, False, "Subtracted in wrong order"))

        # Deduplicate and take 5
        seen = set()
        unique_options = []
        for text, is_correct, rationale in options:
            if text not in seen:
                seen.add(text)
                unique_options.append((text, is_correct, rationale))
        options = unique_options[:5]

        # Ensure at least 2 correct and 2 wrong
        n_correct = sum(1 for _, c, _ in options if c)
        n_wrong = sum(1 for _, c, _ in options if not c)
        if n_correct < 2 or n_wrong < 2:
            # Fallback: add commutative version as correct
            comm_expr = f"{_fmt(ac)} + {ab_s} - {d_s}" if ac >= 0 else f"{ab_s} + ({_fmt(ac)}) - {d_s}"
            if comm_expr not in seen:
                options.insert(1, (comm_expr, True, "Commutative property"))

        rng.shuffle(options)
        options = options[:5]

        choices = []
        correct_keys = []
        for i, (text, is_correct, rationale) in enumerate(options):
            key = chr(ord('a') + i)
            choices.append(QuestionChoice(
                key=key, text=text, text_latex=text,
                is_correct=is_correct, distractor_rationale=rationale if not is_correct else None,
            ))
            if is_correct:
                correct_keys.append(key)

        answer_str = ", ".join(correct_keys)

        stem_text = f"Select all expressions equal to {orig_expr}."

        worked = (
            f"Original: {orig_expr}\n"
            f"Distribute: {a_s} x {b_s} = {_fmt_decimal_2(ab)}, "
            f"{a_s} x {c_s} = {_fmt(ac)}\n"
            f"Simplified: {_fmt_decimal_2(answer_val)}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MS,
                               Difficulty.DIFFICULT, 6, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=1, item_type=ItemType.MS,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_str, answer_latex=answer_str,
            worked_solution=worked,
            choices=choices,
            context_scenario="identify equivalent expressions",
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6, variant_index=variant_idx,
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_nr,
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
                    import traceback
                    traceback.print_exc()
                    continue
        return all_questions

    def generate_stem_variants(self, stem_index: int,
                                variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        stem_methods = {
            1: self.stem1_below_nr,
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
    print("Generating 7.NS.7 question variants...")
    print("=" * 60)

    generator = Stem7NS7(seed=42)
    all_questions = generator.generate_all_variants(variants_per_stem=3)

    for q in all_questions:
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
    print(f"Total questions generated: {len(all_questions)}")
