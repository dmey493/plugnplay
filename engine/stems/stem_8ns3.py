"""
Stem generator for 8.NS.3:
  Given a numeric expression with common rational number bases and integer
  exponents, apply the properties of exponents to generate equivalent
  expressions.

Content Limits:
  - Integer exponents and rational number bases
  - Variables may represent a missing base or exponent
  - Expressions must have common rational number bases
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: simple fraction or stand-alone rational number
  Medium: expression uses one operation
  Difficult: expression uses more than one operation

Properties of Exponents (all covered across the bank):
  - Product of Powers: a^m * a^n = a^(m+n)          (stems 1, 2, 3)
  - Quotient of Powers: a^m / a^n = a^(m-n)         (stems 3, 4, 5)
  - Power of a Power: (a^m)^n = a^(m*n)             (stems 1, 2, 4)
  - Negative Exponent: a^(-n) = 1/a^n               (stems 2, 4, 5)
  - Zero Exponent: a^0 = 1                          (stem 5)

5 Stems, each rotating item styles across variants (variant_idx % 3):
  Stem 1 (Below-MC, DOK 2, Easy): Match a power expression to its expanded or simplified equivalent
      0: power-of-a-power expanded notation, e.g. (3^2)^4
      1: product-of-powers expanded notation (state-spec style), e.g.
         3^2 x 3^5 -> "(3*3)*(3*3*3*3*3) = 3^7"
      2: simple product rule, e.g. 4^2 x 4^3 -> 4^5
  Stem 2 (Approaching-MC, DOK 2, Easy): Identify an equivalent expression using product, power, or negative exponent rules
      0: product of powers
      1: negative-exponent recognition, e.g. "equivalent to 1/27?" -> 3^-3
      2: power of a power, e.g. (6^3)^4 -> 6^12
  Stem 3 (Approaching-NR, DOK 2, Medium): Simplify a product or quotient of powers
      0: product of powers
      1: quotient of powers, e.g. 4^5 / 4^3 -> 4^2
      2: expanded quotient, e.g. (8x8x8x8x8x8)/(8x8x8) -> 8^3
  Stem 4 (At-MC, DOK 2, Medium): Simplify an expression with negative exponents
      0: multi-property simplify with a negative power inside,
         e.g. 5^4 x (5^-2)^3
      1: quotient producing a negative exponent, e.g. 4^2 / 4^5 -> 4^-3
      2: rewrite a negative-exponent product with a positive exponent,
         e.g. 5^-4 x 5^1 -> 1/(5^3)
  Stem 5 (Above-NR, DOK 2, Difficult): Solve for a missing exponent or base
  Stem 6 (Below-NR):    Missing exponent in a single-property equality (DOK 1, easy)
  Stem 7 (Approaching-NR): Missing exponent where two properties combine (DOK 2, medium)
  Stem 8 (At-MC):       Product of powers with a fractional base (DOK 2, medium)
  Stem 9 (Above-ER):    Find and explain the error in a worked simplification (DOK 3, difficult)
      0: zero-power solve, e.g. 5^a = 1 -> a = 0
      1: solve-for-exponents, e.g. 3^5 x a^5 / 12^2 = 12^b -> a=4, b=3
      2: open-ended pair, e.g. 6^a x 6^b / 6^3 = 1/6^4 -> a+b = -1

Every generated answer is machine-verified with exact Fraction arithmetic
before the question is returned (see _assert_eq calls).

Rendering notes (pdf_generator):
  - "^N" renders as a superscript (supports ^-3 and ^a).
  - "N/D" with digits on both sides renders as a stacked fraction, so
    quotients of powers use the ÷ sign and reciprocals are written
    "1/(b^k)" (the parenthesis prevents accidental fraction stacking).
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
from engine.stem_guards import distinct_choices


STANDARD_CODE = "8.NS.3"
VARIANTS_PER_STEM = 20

MULT = "×"   # multiplication sign
DOT = "·"    # middle dot (compact expanded notation)
DIV = "÷"    # division sign


# ============================================================
# HELPERS
# ============================================================

def _exp(base, exp):
    """Format base^exp using caret notation for PDF renderer.

    The PDF renderer converts ^N to superscript automatically.
    """
    return f"{base}^{exp}"


def _exp_latex(base, exp):
    """LaTeX format for base^exp."""
    return f"{base}^{{{exp}}}"


def _pow(base, exp) -> Fraction:
    """Exact value of base**exp (handles negative and zero exponents)."""
    return Fraction(base) ** exp


def _assert_eq(lhs, rhs, context: str):
    """Machine-verify an equality before shipping the question."""
    assert lhs == rhs, (
        f"8.NS.3 self-check FAILED ({context}): {lhs} != {rhs}"
    )


def _assert_ne(lhs, rhs, context: str):
    """Machine-verify a distractor is NOT equal to the true value."""
    assert lhs != rhs, (
        f"8.NS.3 distractor-check FAILED ({context}): {lhs} == {rhs}"
    )


class Stem8NS3:
    """Generates ~20 variants for each of 5 stems from the 8.NS.3 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ----------------------------------------------------------------
    # Shared MC assembly: dedupe distractors, shuffle, build choices.
    # Guarantees 4 unique choice texts with exactly 1 correct.
    # ----------------------------------------------------------------

    def _build_mc(self, rng, stem_index, variant_idx, proficiency, difficulty,
                  dok, stem_text, correct, distractor_candidates, worked,
                  scenario, fallback=None, stem_latex=None):
        seen = {correct}
        dist = []
        for d in distractor_candidates:
            if d not in seen:
                seen.add(d)
                dist.append(d)
            if len(dist) == 3:
                break
        tries = 0
        while len(dist) < 3 and fallback is not None and tries < 100:
            d = fallback()
            if d not in seen:
                seen.add(d)
                dist.append(d)
            tries += 1
        assert len(dist) == 3, (
            f"8.NS.3 stem {stem_index} v{variant_idx}: could not build 3 "
            f"unique distractors (got {dist})"
        )

        all_options = [(correct, True)] + [(d, False) for d in dist]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))
        correct_letter = next(c.key for c in choices if c.is_correct)

        qid = make_question_id(STANDARD_CODE, proficiency, ItemType.MC,
                               difficulty, stem_index, variant_idx)
        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=proficiency,
            difficulty=difficulty, dok=dok, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_latex or stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario=scenario,
            seed=self.base_seed * 1000 + stem_index * 100 + variant_idx,
            stem_index=stem_index, variant_index=variant_idx,
        )

    def _build_nr(self, stem_index, variant_idx, proficiency, difficulty,
                  dok, stem_text, answer_text, worked, scenario,
                  answer_latex=None):
        qid = make_question_id(STANDARD_CODE, proficiency, ItemType.NR,
                               difficulty, stem_index, variant_idx)
        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=proficiency,
            difficulty=difficulty, dok=dok, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_text,
            answer_latex=answer_latex or f"${answer_text}$",
            worked_solution=worked,
            context_scenario=scenario,
            seed=self.base_seed * 1000 + stem_index * 100 + variant_idx,
            stem_index=stem_index, variant_index=variant_idx,
        )

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 2, Easy)
    # Rotation (variant_idx % 3):
    #   0: power-of-a-power expanded notation
    #   1: product-of-powers expanded notation (state-spec style)
    #   2: simple product rule
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)
        # Style 3 is new for the 2026-08-17 revision, which added the negative
        # exponent property to the Below descriptor.
        style = variant_idx % 4
        if style == 0:
            return self._below_power_of_power_expanded(rng, variant_idx)
        elif style == 1:
            return self._below_product_expanded(rng, variant_idx)
        elif style == 2:
            return self._below_product_rule(rng, variant_idx)
        return self._below_negative_exponent(rng, variant_idx)

    def _below_negative_exponent(self, rng, variant_idx):
        """Below style 3: negative exponents, new in the 2026-08-17 revision.

        Reproduces the specification's own item shape, (5^-3 x 5^4)^2 = 5^2:
        a product of powers whose exponents partly cancel, then raised to a
        power. The distractors are the two ways the sign can go wrong and the
        two ways the exponents can be combined wrongly.
        """
        base = rng.randint(2, 7)
        neg = rng.randint(2, 5)
        pos = rng.randint(neg + 1, neg + 4)     # keep the inner result positive
        outer = 2
        inner_exp = pos - neg
        result_exp = inner_exp * outer

        _assert_eq(_pow(base, -neg) * _pow(base, pos), _pow(base, inner_exp),
                   f"stem1 neg-exp {base}^-{neg} x {base}^{pos}")
        _assert_eq(_pow(base, inner_exp) ** outer, _pow(base, result_exp),
                   f"stem1 neg-exp outer ({base}^{inner_exp})^{outer}")

        expr_text = f"({_exp(base, -neg)} x {_exp(base, pos)})^{outer}"
        correct = _exp(base, result_exp)

        options = [
            (correct, True, None),
            (f"1/{_exp(base, result_exp)}", False,
             "Carries the negative sign through to the result"),
            (f"1/{_exp(base, (pos + neg) * outer)}", False,
             "Adds the exponents as if both were positive, then negates"),
            (_exp(base, (pos + neg) * outer), False,
             "Adds the exponents instead of subtracting for the negative one"),
        ]
        rng.shuffle(options)
        choices = [QuestionChoice(key=chr(ord("a") + i), text=t, text_latex=t,
                                  is_correct=c, distractor_rationale=r)
                   for i, (t, c, r) in enumerate(options)]
        key = next(c.key for c in choices if c.is_correct).upper()

        stem_text = (
            f"An expression is given.\n\n  {expr_text}\n\n"
            f"Select an equivalent expression."
        )
        worked = (
            f"Product of powers: add the exponents, keeping the negative.\n"
            f"{_exp(base, -neg)} x {_exp(base, pos)} = "
            f"{_exp(base, -neg + pos)} = {_exp(base, inner_exp)}\n"
            f"Power of a power: multiply the exponents.\n"
            f"({_exp(base, inner_exp)})^{outer} = {_exp(base, result_exp)}"
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW,
                                         ItemType.MC, Difficulty.EASY, 1, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{key}. {correct}", answer_latex=f"{key}. {correct}",
            worked_solution=worked, choices=choices,
            context_scenario="negative exponent with product and power rules",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx,
        )

    def _below_power_of_power_expanded(self, rng, variant_idx):
        base = rng.randint(2, 7)
        inner_exp = rng.randint(2, 3)
        outer_exp = rng.randint(2, 4)
        result_exp = inner_exp * outer_exp

        # Verify: (base^inner)^outer == base^(inner*outer)
        _assert_eq(_pow(base, inner_exp) ** outer_exp,
                   _pow(base, result_exp),
                   f"stem1 pow-of-pow ({base}^{inner_exp})^{outer_exp}")

        inner_str = f"({_exp(base, inner_exp)})"
        expr_text = f"{inner_str}^{outer_exp}"
        expr_latex = f"$({base}^{{{inner_exp}}})^{{{outer_exp}}}$"

        # Correct: (base^inner) repeated outer times = base^(inner*outer)
        correct_expanded = f" {MULT} ".join([inner_str] * outer_exp)
        correct = f"{correct_expanded} = {_exp(base, result_exp)}"

        distractors = []
        # Common error 1: wrong number of repetitions (inner instead of
        # outer). When inner == outer this collides with the correct string
        # and is dropped by the dedupe in _build_mc.
        d1_expanded = f" {MULT} ".join([inner_str] * inner_exp)
        distractors.append(f"{d1_expanded} = {_exp(base, inner_exp * inner_exp)}")
        # Common error 2: add exponents instead of multiply
        wrong2 = (f"{inner_str} {MULT} ({_exp(base, outer_exp)}) = "
                  f"{_exp(base, inner_exp + outer_exp)}")
        distractors.append(wrong2)
        # Common error 3: one extra repetition
        wrong3_count = outer_exp + 1
        wrong3_expanded = f" {MULT} ".join([inner_str] * wrong3_count)
        distractors.append(
            f"{wrong3_expanded} = {_exp(base, inner_exp * wrong3_count)}")

        def fallback():
            # Wrong repetition count paired with a wrong exponent claim, so
            # both sides of the fallback distractor are numerically wrong.
            reps = outer_exp + rng.choice([1, 2])
            fe = result_exp + rng.choice([1, -1, 2])
            expansion = f" {MULT} ".join([inner_str] * reps)
            return f"{expansion} = {_exp(base, fe)}"

        stem_text = (
            f"An expression is given.\n\n"
            f"  {expr_text}\n\n"
            f"Select the equivalent expanded notation."
        )
        stem_latex = (
            f"An expression is given.\n\n"
            f"  {expr_latex}\n\n"
            f"Select the equivalent expanded notation."
        )
        worked = (
            f"{expr_text} means {inner_str} multiplied by itself "
            f"{outer_exp} times.\n"
            f"Using the power of a power rule: {expr_text} "
            f"= {_exp(base, result_exp)}.\n"
            f"Expanded: {correct}"
        )
        return self._build_mc(
            rng, 1, variant_idx, ProficiencyLevel.BELOW, Difficulty.EASY, 2,
            stem_text, correct, distractors, worked,
            "expanded notation (power of a power)",
            fallback=fallback, stem_latex=stem_latex)

    def _below_product_expanded(self, rng, variant_idx):
        # State-spec style: "3^2 x 3^5 -> (3*3)*(3*3*3*3*3) = 3^7"
        b = rng.randint(2, 7)
        m = rng.randint(2, 3)
        n = rng.randint(3, 5)

        true_val = _pow(b, m) * _pow(b, n)
        _assert_eq(true_val, _pow(b, m + n),
                   f"stem1 product expanded {b}^{m} x {b}^{n}")

        def grp(k):
            return "(" + DOT.join([str(b)] * k) + ")"

        expr_text = f"{_exp(b, m)} {MULT} {_exp(b, n)}"
        correct = f"{grp(m)}{DOT}{grp(n)} = {_exp(b, m + n)}"

        # Distractor 1 (state-spec style): repeat b^m m times and b^n n
        # times -> claims exponent m*m + n*n
        d1 = ("(" + DOT.join([_exp(b, m)] * m) + f"){DOT}(" +
              DOT.join([_exp(b, n)] * n) + f") = {_exp(b, m * m + n * n)}")
        _assert_ne(_pow(b, m * m + n * n), true_val, "stem1 exp-squared dist")

        # Distractor 2 (state-spec style): multiply base by exponent
        d2_val = (b * m) * (b * n)
        d2 = f"({b}{DOT}{m}){DOT}({b}{DOT}{n}) = {d2_val}"
        _assert_ne(Fraction(d2_val), true_val, "stem1 base-times-exp dist")

        # Distractor 3: multiply the exponents (m groups of n factors)
        d3 = DOT.join([grp(n)] * m) + f" = {_exp(b, m * n)}"
        _assert_ne(_pow(b, m * n), true_val, "stem1 exp-multiplied dist")

        def fallback():
            fe = m + n + rng.choice([1, -1, 2])
            return f"{grp(m)}{DOT}{grp(m)} = {_exp(b, fe)}"

        stem_text = (
            f"An expression is given.\n\n"
            f"  {expr_text}\n\n"
            f"Select the equivalent expanded notation."
        )
        worked = (
            f"{_exp(b, m)} means {m} factors of {b}; "
            f"{_exp(b, n)} means {n} factors of {b}.\n"
            f"So {expr_text} = {grp(m)}{DOT}{grp(n)}, which is "
            f"{m} + {n} = {m + n} factors of {b} in all: {_exp(b, m + n)}."
        )
        return self._build_mc(
            rng, 1, variant_idx, ProficiencyLevel.BELOW, Difficulty.EASY, 2,
            stem_text, correct, [d1, d2, d3], worked,
            "expanded notation (product of powers)",
            fallback=fallback)

    def _below_product_rule(self, rng, variant_idx):
        b = rng.randint(2, 9)
        m = rng.randint(2, 4)
        n = rng.randint(2, 4)

        _assert_eq(_pow(b, m) * _pow(b, n), _pow(b, m + n),
                   f"stem1 product rule {b}^{m} x {b}^{n}")

        expr_text = f"{_exp(b, m)} {MULT} {_exp(b, n)}"
        correct = _exp(b, m + n)

        distractors = [
            _exp(b, m * n),          # multiplied exponents
            _exp(b * b, m + n),      # multiplied bases too
            _exp(b, max(m, n)),      # kept larger exponent
            _exp(b, abs(m - n)),     # subtracted exponents
        ]

        def fallback():
            return _exp(b, m + n + rng.choice([1, -1, 2, 3]))

        stem_text = (
            f"An expression is given.\n\n"
            f"  {expr_text}\n\n"
            f"Select an equivalent expression."
        )
        worked = (
            f"Using the product of powers rule, keep the base and add "
            f"the exponents:\n"
            f"{expr_text} = {_exp(b, f'{m}+{n}')} = {correct}"
        )
        return self._build_mc(
            rng, 1, variant_idx, ProficiencyLevel.BELOW, Difficulty.EASY, 2,
            stem_text, correct, distractors, worked,
            "simple product rule",
            fallback=fallback)

    # ================================================================
    # STEM 2: Approaching Proficiency - MC (DOK 2, Easy)
    # Rotation (variant_idx % 3):
    #   0: product of powers
    #   1: negative-exponent recognition ("equivalent to 1/27?" -> 3^-3)
    #   2: power of a power ((6^3)^4 -> 6^12)
    # ================================================================

    def stem2_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)
        style = variant_idx % 3
        if style == 0:
            return self._approaching_product_mc(gen, rng, variant_idx)
        elif style == 1:
            return self._approaching_negative_exponent_mc(rng, variant_idx)
        return self._approaching_power_of_power_mc(rng, variant_idx)

    def _approaching_product_mc(self, gen, rng, variant_idx):
        base, exp1, exp2, op, result_exp = gen.exponent_simplify("easy")
        # op is always "multiply" for easy
        _assert_eq(_pow(base, exp1) * _pow(base, exp2), _pow(base, result_exp),
                   f"stem2 product {base}^{exp1} x {base}^{exp2}")

        expr_text = f"{_exp(base, exp1)} {MULT} {_exp(base, exp2)}"
        correct = _exp(base, result_exp)

        distractors = [
            _exp(base, exp1 * exp2),        # multiplied exponents
            _exp(base * base, exp1 + exp2), # multiplied base too
            _exp(base, abs(exp1 - exp2)),   # subtracted exponents
            _exp(base, max(exp1, exp2)),    # kept larger exponent
        ]

        def fallback():
            return _exp(base, result_exp + rng.choice([1, -1, 2]))

        stem_text = (
            f"An expression is given.\n\n"
            f"  {expr_text}\n\n"
            f"Select an equivalent expression."
        )
        worked = (
            f"Using the product of powers rule: a^m {MULT} a^n = a^(m+n).\n"
            f"{expr_text} = {_exp(base, result_exp)}"
        )
        return self._build_mc(
            rng, 2, variant_idx, ProficiencyLevel.APPROACHING,
            Difficulty.EASY, 2, stem_text, correct, distractors, worked,
            "product of powers", fallback=fallback)

    def _approaching_negative_exponent_mc(self, rng, variant_idx):
        # "Which expression is equivalent to 1/27?" -> 3^-3
        b, k = rng.choice([(2, 2), (2, 3), (2, 4), (2, 5), (3, 2), (3, 3),
                           (3, 4), (4, 2), (4, 3), (5, 2), (5, 3), (6, 2),
                           (10, 2), (10, 3)])
        val = b ** k
        _assert_eq(_pow(b, -k), Fraction(1, val),
                   f"stem2 neg exponent {b}^-{k} = 1/{val}")

        correct = _exp(b, -k)
        distractors = [
            _exp(b, k),          # dropped the negative
            f"-{_exp(b, k)}",    # negative number instead of reciprocal
            f"-{_exp(b, -k)}",   # negative of the reciprocal
        ]
        # Verify every distractor is numerically wrong
        _assert_ne(_pow(b, k), Fraction(1, val), "stem2 neg dist1")
        _assert_ne(-_pow(b, k), Fraction(1, val), "stem2 neg dist2")
        _assert_ne(-_pow(b, -k), Fraction(1, val), "stem2 neg dist3")

        stem_text = (
            f"An expression is given.\n\n"
            f"  1/{val}\n\n"
            f"Select an equivalent expression."
        )
        worked = (
            f"A negative exponent means a reciprocal: {_exp(b, -k)} = "
            f"1/({_exp(b, k)}).\n"
            f"Since {_exp(b, k)} = {val}, the expression 1/{val} is "
            f"equivalent to {_exp(b, -k)}."
        )
        return self._build_mc(
            rng, 2, variant_idx, ProficiencyLevel.APPROACHING,
            Difficulty.EASY, 2, stem_text, correct, distractors, worked,
            "negative exponent recognition")

    def _approaching_power_of_power_mc(self, rng, variant_idx):
        b = rng.randint(2, 7)
        m = rng.randint(2, 4)
        n = rng.randint(2, 4)
        result_exp = m * n
        _assert_eq(_pow(b, m) ** n, _pow(b, result_exp),
                   f"stem2 pow-of-pow ({b}^{m})^{n}")

        expr_text = f"({_exp(b, m)})^{n}"
        correct = _exp(b, result_exp)

        distractors = [
            _exp(b, m + n),                 # added exponents
            _exp(b, int(f"{m}{n}")),        # concatenated exponents
            _exp(b, m ** n),                # raised exponent to exponent
            _exp(b * n, m),                 # multiplied base by outer exp
        ]

        def fallback():
            return _exp(b, result_exp + rng.choice([1, -1, 2, 3]))

        stem_text = (
            f"An expression is given.\n\n"
            f"  {expr_text}\n\n"
            f"Select an equivalent expression."
        )
        worked = (
            f"Using the power of a power rule, multiply the exponents:\n"
            f"{expr_text} = {_exp(b, f'{m}{MULT}{n}')} = {correct}"
        )
        return self._build_mc(
            rng, 2, variant_idx, ProficiencyLevel.APPROACHING,
            Difficulty.EASY, 2, stem_text, correct, distractors, worked,
            "power of a power", fallback=fallback)

    # ================================================================
    # STEM 3: Approaching Proficiency - NR (DOK 2, Medium)
    # Rotation (variant_idx % 3):
    #   0: product of powers
    #   1: quotient of powers (4^5 / 4^3 -> 4^2)
    #   2: expanded quotient ((8x8x8x8x8x8)/(8x8x8) -> 8^3)
    # ================================================================

    def stem3_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)
        style = variant_idx % 3
        b = rng.randint(2, 9)

        if style == 0:
            e1 = rng.randint(4, 8)
            e2 = rng.randint(2, 4)
            result_exp = e1 + e2
            _assert_eq(_pow(b, e1) * _pow(b, e2), _pow(b, result_exp),
                       f"stem3 product {b}^{e1} x {b}^{e2}")
            expr_text = f"{_exp(b, e1)} {MULT} {_exp(b, e2)}"
            stem_text = (
                f"An expression is given.\n\n"
                f"  {expr_text}\n\n"
                f"Simplify the expression. Write your answer as a "
                f"single base with an exponent."
            )
            worked = (
                f"Using the product of powers rule (add the exponents):\n"
                f"{expr_text} = {_exp(b, f'{e1}+{e2}')} = {_exp(b, result_exp)}"
            )
            scenario = "product of powers (NR)"
        elif style == 1:
            e1 = rng.randint(4, 9)
            e2 = rng.randint(2, e1 - 2)
            result_exp = e1 - e2
            _assert_eq(_pow(b, e1) / _pow(b, e2), _pow(b, result_exp),
                       f"stem3 quotient {b}^{e1} / {b}^{e2}")
            expr_text = f"{_exp(b, e1)} {DIV} {_exp(b, e2)}"
            stem_text = (
                f"An expression is given.\n\n"
                f"  {expr_text}\n\n"
                f"Simplify the expression. Write your answer as a "
                f"single base with an exponent."
            )
            worked = (
                f"Using the quotient of powers rule (subtract the exponents):\n"
                f"{expr_text} = {_exp(b, f'{e1}-{e2}')} = {_exp(b, result_exp)}"
            )
            scenario = "quotient of powers (NR)"
        else:
            e1 = rng.randint(5, 7)
            e2 = rng.randint(2, e1 - 2)
            result_exp = e1 - e2
            _assert_eq(_pow(b, e1) / _pow(b, e2), _pow(b, result_exp),
                       f"stem3 expanded quotient {b}^{e1} / {b}^{e2}")
            num = MULT.join([str(b)] * e1)
            den = MULT.join([str(b)] * e2)
            expr_text = f"({num})/({den})"
            stem_text = (
                f"An expression is given.\n\n"
                f"  {expr_text}\n\n"
                f"Simplify the expression. Write your answer in the "
                f"form x^y."
            )
            worked = (
                f"The numerator is {e1} factors of {b} ({_exp(b, e1)}). "
                f"The denominator is {e2} factors of {b} ({_exp(b, e2)}).\n"
                f"Each factor of {b} in the denominator cancels one in the "
                f"numerator, leaving {e1} - {e2} = {result_exp} factors:\n"
                f"{expr_text} = {_exp(b, result_exp)}"
            )
            scenario = "expanded quotient (NR)"

        answer_text = _exp(b, result_exp)
        return self._build_nr(
            3, variant_idx, ProficiencyLevel.APPROACHING, Difficulty.MEDIUM,
            2, stem_text, answer_text, worked, scenario)

    # ================================================================
    # STEM 4: At Proficiency - MC (DOK 2, Medium)
    # Negative exponents woven through every style.
    # Rotation (variant_idx % 3):
    #   0: multi-property simplify with a negative power inside:
    #      base^a x (base^-b)^c
    #   1: quotient producing a negative exponent: b^2 / b^5 -> b^-3
    #   2: rewrite negative-exponent product with a positive exponent:
    #      b^-m x b^n -> 1/(b^k)
    # ================================================================

    def stem4_at_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)
        style = variant_idx % 3
        base = rng.randint(2, 7)

        if style == 0:
            return self._at_multi_property_mc(rng, variant_idx, base)
        elif style == 1:
            return self._at_quotient_negative_mc(rng, variant_idx, base)
        return self._at_rewrite_positive_mc(rng, variant_idx, base)

    def _at_multi_property_mc(self, rng, variant_idx, base):
        # base^a x (base^b)^c with b negative, so the expression carries a
        # negative exponent and the result may be negative too. Redraw until
        # the final exponent is not 0 or 1 (avoids "b^0"/"b^1" answers).
        for _ in range(50):
            a = rng.randint(2, 5)
            b = rng.randint(-3, -1)
            c = rng.randint(2, 3)
            if a + b * c not in (0, 1):
                break

        inner_result = b * c
        final_exp = a + inner_result
        _assert_eq(_pow(base, a) * (_pow(base, b) ** c), _pow(base, final_exp),
                   f"stem4 multi {base}^{a} x ({base}^{b})^{c}")

        expr_text = f"{_exp(base, a)} {MULT} ({_exp(base, b)})^{c}"
        correct = _exp(base, final_exp)

        distractors = [
            _exp(base, a + b + c),          # added all exponents
            _exp(base, a * b * c),          # multiplied all exponents
            _exp(base, inner_result),       # forgot the leading factor
            _exp(base, (a + b) * c),        # grouped wrong
            _exp(base, a + abs(b) * c),     # dropped the negative sign
        ]

        def fallback():
            return _exp(base, final_exp + rng.choice([1, -1, 2, -2]))

        stem_text = (
            f"An expression is given.\n\n"
            f"  {expr_text}\n\n"
            f"Select an equivalent expression."
        )
        worked = (
            f"Step 1: Apply power of a power rule to ({_exp(base, b)})^{c}:\n"
            f"  ({_exp(base, b)})^{c} = {_exp(base, inner_result)}\n\n"
            f"Step 2: Apply product of powers rule:\n"
            f"  {_exp(base, a)} {MULT} {_exp(base, inner_result)} = "
            f"{_exp(base, final_exp)}\n\n"
            f"Answer: {correct}"
        )
        return self._build_mc(
            rng, 4, variant_idx, ProficiencyLevel.AT, Difficulty.MEDIUM, 2,
            stem_text, correct, distractors, worked,
            "multi-property with negative exponent", fallback=fallback)

    def _at_quotient_negative_mc(self, rng, variant_idx, base):
        # b^e1 / b^e2 with e1 < e2 -> negative exponent result
        # (k >= 2 so the answer never displays as b^-1)
        e1 = rng.randint(2, 4)
        k = rng.randint(2, 4)
        e2 = e1 + k

        _assert_eq(_pow(base, e1) / _pow(base, e2), _pow(base, -k),
                   f"stem4 quotient-neg {base}^{e1} / {base}^{e2}")

        expr_text = f"{_exp(base, e1)} {DIV} {_exp(base, e2)}"
        correct = _exp(base, -k)

        distractors = [
            _exp(base, k),           # sign error
            f"-{_exp(base, k)}",     # negative number instead of exponent
            _exp(base, e1 + e2),     # added instead of subtracting
        ]
        _assert_ne(_pow(base, k), _pow(base, -k), "stem4 qneg dist1")
        _assert_ne(-_pow(base, k), _pow(base, -k), "stem4 qneg dist2")
        _assert_ne(_pow(base, e1 + e2), _pow(base, -k), "stem4 qneg dist3")

        def fallback():
            return _exp(base, -k + rng.choice([-1, -2, 2]))

        stem_text = (
            f"An expression is given.\n\n"
            f"  {expr_text}\n\n"
            f"Select an equivalent expression."
        )
        worked = (
            f"Using the quotient of powers rule (subtract the exponents):\n"
            f"{expr_text} = {_exp(base, f'{e1}-{e2}')} = {correct}\n"
            f"The exponent is negative because the denominator has more "
            f"factors of {base} than the numerator."
        )
        return self._build_mc(
            rng, 4, variant_idx, ProficiencyLevel.AT, Difficulty.MEDIUM, 2,
            stem_text, correct, distractors, worked,
            "quotient producing negative exponent", fallback=fallback)

    def _at_rewrite_positive_mc(self, rng, variant_idx, base):
        # b^-m x b^n (n < m - 1) -> b^-(m-n); rewrite with a positive
        # exponent (k >= 2 so the answer never displays as 1/(b^1))
        m = rng.randint(3, 6)
        n = rng.randint(1, m - 2)
        k = m - n

        _assert_eq(_pow(base, -m) * _pow(base, n), Fraction(1, base ** k),
                   f"stem4 rewrite-pos {base}^-{m} x {base}^{n}")

        expr_text = f"{_exp(base, -m)} {MULT} {_exp(base, n)}"
        correct = f"1/({_exp(base, k)})"

        distractors = [
            _exp(base, k),                    # dropped the reciprocal
            f"-{_exp(base, k)}",              # made the value negative
            f"1/({_exp(base, m + n)})",       # added magnitudes instead
        ]
        true_val = Fraction(1, base ** k)
        _assert_ne(_pow(base, k), true_val, "stem4 rewrite dist1")
        _assert_ne(-_pow(base, k), true_val, "stem4 rewrite dist2")
        _assert_ne(Fraction(1, base ** (m + n)), true_val, "stem4 rewrite dist3")

        def fallback():
            return f"1/({_exp(base, k + rng.choice([1, 2, 3]))})"

        stem_text = (
            f"An expression is given.\n\n"
            f"  {expr_text}\n\n"
            f"Select the equivalent expression written with a "
            f"positive exponent."
        )
        worked = (
            f"Product of powers: {expr_text} = {_exp(base, f'{-m}+{n}')} = "
            f"{_exp(base, -k)}\n"
            f"A negative exponent means a reciprocal: {_exp(base, -k)} = "
            f"1/({_exp(base, k)})"
        )
        return self._build_mc(
            rng, 4, variant_idx, ProficiencyLevel.AT, Difficulty.MEDIUM, 2,
            stem_text, correct, distractors, worked,
            "negative to positive exponent", fallback=fallback)

    # ================================================================
    # STEM 5: Above Proficiency - NR (DOK 2, Difficult)
    # Rotation (variant_idx % 3):
    #   0: zero-power solve (b^a = 1 -> a = 0)
    #   1: solve-for-exponents (c^n x a^n / d^m = d^b with c*a = d)
    #   2: open-ended pair (b^a x b^b / b^k = 1/(b^m) -> a + b = k - m)
    # All answers verified with exact Fraction arithmetic.
    # ================================================================

    def stem5_above_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)
        style = variant_idx % 3
        if style == 0:
            return self._above_zero_power(rng, variant_idx)
        elif style == 1:
            return self._above_solve_common_base(rng, variant_idx)
        return self._above_open_pair(rng, variant_idx)

    def _above_zero_power(self, rng, variant_idx):
        b = rng.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 12])
        # Verify the zero-power identity for this base
        _assert_eq(_pow(b, 0), Fraction(1), f"stem5 zero power {b}^0")

        expr_text = f"{b}^a = 1"
        stem_text = (
            f"An equation is given.\n\n"
            f"  {expr_text}\n\n"
            f"What is the value of a?"
        )
        worked = (
            f"Any nonzero base raised to the power 0 equals 1 "
            f"(zero exponent property).\n"
            f"{_exp(b, 0)} = 1, so a = 0."
        )
        return self._build_nr(
            5, variant_idx, ProficiencyLevel.ABOVE, Difficulty.DIFFICULT, 2,
            stem_text, "0", worked, "zero power solve")

    def _above_solve_common_base(self, rng, variant_idx):
        # c^n x a^n / d^m = d^b where c * a = d  ->  a = d/c, b = n - m
        # (state-spec style: 3^5 x a^5 / 12^2 = 12^b -> a = 4, b = 3)
        c, a_val = rng.choice([(2, 2), (2, 3), (2, 4), (2, 5), (2, 6),
                               (3, 2), (3, 3), (3, 4), (4, 2), (4, 3),
                               (5, 2), (6, 2)])
        d = c * a_val
        n = rng.randint(3, 5)
        m = rng.randint(1, n - 1)
        b_val = n - m

        # Machine-verify: substitute the answers and evaluate both sides
        lhs = _pow(c, n) * _pow(a_val, n) / _pow(d, m)
        rhs = _pow(d, b_val)
        _assert_eq(lhs, rhs,
                   f"stem5 solve {c}^{n} x {a_val}^{n} / {d}^{m} = {d}^{b_val}")

        expr_text = (f"{_exp(c, n)} {MULT} a^{n} {DIV} {_exp(d, m)} "
                     f"= {d}^b")
        stem_text = (
            f"An equation is given.\n\n"
            f"  {expr_text}\n\n"
            f"The equation is true for certain values of a and b. "
            f"What is one possible set of values for a and b?"
        )
        answer_text = f"a = {a_val}, b = {b_val}"
        check_val = (c ** n) * (a_val ** n) // (d ** m)
        worked = (
            f"Rewrite {_exp(c, n)} {MULT} a^{n} as ({c}a)^{n}.\n"
            f"If a = {a_val}, then {c} {MULT} {a_val} = {d}, so the left "
            f"side becomes {_exp(d, n)} {DIV} {_exp(d, m)} = "
            f"{_exp(d, f'{n}-{m}')} = {_exp(d, b_val)}.\n"
            f"So one possible set of values is a = {a_val} and b = {b_val}.\n"
            f"Check: {c ** n} {MULT} {a_val ** n} {DIV} {d ** m} = "
            f"{check_val} and {_exp(d, b_val)} = {d ** b_val}."
        )
        return self._build_nr(
            5, variant_idx, ProficiencyLevel.ABOVE, Difficulty.DIFFICULT, 2,
            stem_text, answer_text, worked,
            "solve for exponents (common base)",
            answer_latex=answer_text)

    def _above_open_pair(self, rng, variant_idx):
        # b^a x b^b / b^k = 1/(b^m)  ->  a + b - k = -m  ->  a + b = k - m
        # (state-spec style: 6^a x 6^b / 6^3 = 1/6^4 -> a + b = -1)
        base = rng.randint(2, 7)
        k = rng.randint(2, 5)
        m = rng.randint(2, 6)
        s = k - m  # required a + b

        a0 = rng.randint(-3, 4)
        b0 = s - a0

        # Machine-verify: substitute the answers and evaluate both sides
        lhs = _pow(base, a0) * _pow(base, b0) / _pow(base, k)
        rhs = Fraction(1, base ** m)
        _assert_eq(lhs, rhs,
                   f"stem5 open pair {base}^{a0} x {base}^{b0} / {base}^{k} "
                   f"= 1/{base}^{m}")

        expr_text = (f"{base}^a {MULT} {base}^b {DIV} {_exp(base, k)} "
                     f"= 1/({_exp(base, m)})")
        stem_text = (
            f"An equation is given.\n\n"
            f"  {expr_text}\n\n"
            f"The equation is true for many pairs of values. "
            f"What is one possible set of values for a and b?"
        )
        answer_text = f"a = {a0}, b = {b0} (any pair with a + b = {s})"
        worked = (
            f"The right side 1/({_exp(base, m)}) equals {_exp(base, -m)}.\n"
            f"On the left side, product and quotient rules give the "
            f"exponent a + b - {k}.\n"
            f"So a + b - {k} = -{m}, which means a + b = {s}.\n"
            f"One possible answer: a = {a0}, b = {b0} "
            f"(any pair with a + b = {s} works)."
        )
        return self._build_nr(
            5, variant_idx, ProficiencyLevel.ABOVE, Difficulty.DIFFICULT, 2,
            stem_text, answer_text, worked,
            "solve for exponents (open pair)",
            answer_latex=answer_text)

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    # ================================================================
    # STEM 6: Below Proficiency - NR (DOK 1, Easy)
    # NEW. "Identify unknown exponents in simple equality statements involving
    # a SINGLE exponent property."
    # ================================================================
    def stem6_below_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)

        base = rng.randint(2, 9)
        prop = rng.choice(["product", "power"])
        if prop == "product":
            a = rng.randint(2, 6)
            b = rng.randint(2, 6)
            total = a + b
            _assert_eq(_pow(base, a) * _pow(base, b), _pow(base, total),
                       "stem6 product")
            equation = f"{_exp(base, a)} x {_exp(base, '?')} = {_exp(base, total)}"
            answer = b
            worked = (
                f"Product of powers: the exponents add.\n"
                f"{a} + ? = {total}, so ? = {answer}."
            )
        else:
            a = rng.randint(2, 4)
            b = rng.randint(2, 4)
            total = a * b
            _assert_eq(_pow(base, a) ** b, _pow(base, total), "stem6 power")
            equation = f"({_exp(base, a)})^? = {_exp(base, total)}"
            answer = b
            worked = (
                f"Power of a power: the exponents multiply.\n"
                f"{a} x ? = {total}, so ? = {answer}."
            )

        stem_text = (
            f"An equation is given.\n\n  {equation}\n\n"
            f"What is the value of the missing exponent?"
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW,
                                         ItemType.NR, Difficulty.EASY, 6, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=str(answer), answer_latex=str(answer),
            worked_solution=worked,
            context_scenario="missing exponent, one property",
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6, variant_index=variant_idx,
        )

    # ================================================================
    # STEM 7: Approaching Proficiency - NR (DOK 2, Medium)
    # NEW. "Determine missing exponents in simple equality statements involving
    # TWO properties" - here a power of a power feeding a product or quotient,
    # so the student cannot get there with one rule.
    # ================================================================
    def stem7_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(7, variant_idx)

        base = rng.randint(2, 7)
        inner = rng.randint(2, 4)
        outer = rng.randint(2, 3)
        extra = rng.randint(2, 5)

        if rng.random() < 0.5:
            total = inner * outer + extra
            _assert_eq(_pow(base, inner) ** outer * _pow(base, extra),
                       _pow(base, total), "stem7 power-then-product")
            equation = (f"({_exp(base, inner)})^{outer} x {_exp(base, '?')} "
                        f"= {_exp(base, total)}")
            answer = extra
            worked = (
                f"Power of a power first: ({_exp(base, inner)})^{outer} = "
                f"{_exp(base, inner * outer)}\n"
                f"Then product of powers: {inner * outer} + ? = {total}, "
                f"so ? = {answer}."
            )
        else:
            total = inner * outer - extra
            while total < 1:
                extra = rng.randint(1, max(1, inner * outer - 1))
                total = inner * outer - extra
            _assert_eq(_pow(base, inner) ** outer / _pow(base, extra),
                       _pow(base, total), "stem7 power-then-quotient")
            equation = (f"({_exp(base, inner)})^{outer} / {_exp(base, '?')} "
                        f"= {_exp(base, total)}")
            answer = extra
            worked = (
                f"Power of a power first: ({_exp(base, inner)})^{outer} = "
                f"{_exp(base, inner * outer)}\n"
                f"Then quotient of powers: {inner * outer} - ? = {total}, "
                f"so ? = {answer}."
            )

        stem_text = (
            f"An equation is given.\n\n  {equation}\n\n"
            f"What is the value of the missing exponent?"
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING,
                                         ItemType.NR, Difficulty.MEDIUM, 7, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=str(answer), answer_latex=str(answer),
            worked_solution=worked,
            context_scenario="missing exponent, two properties",
            seed=self.base_seed * 1000 + 700 + variant_idx,
            stem_index=7, variant_index=variant_idx,
        )

    # ================================================================
    # STEM 8: At Proficiency - MC (DOK 2, Medium)
    # NEW. "...including those with FRACTIONAL BASES", which did not appear in
    # the old item set at all.
    # ================================================================
    @distinct_choices
    def stem8_at_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(8, variant_idx)

        # A base like 2/6 would print unreduced, which is not how a fractional
        # base is ever written in the specification.
        from math import gcd
        num = rng.randint(1, 4)
        den = rng.randint(num + 1, 6)
        while gcd(num, den) != 1:
            num = rng.randint(1, 4)
            den = rng.randint(num + 1, 6)
        a = rng.randint(2, 5)
        b = rng.randint(2, 4)
        # When a + b == a * b (2 and 2), the "multiplied the exponents"
        # distractor becomes the correct answer.
        while a + b == a * b:
            a = rng.randint(2, 5)
            b = rng.randint(2, 4)
        total = a + b
        frac = f"({num}/{den})"

        _assert_eq(Fraction(num, den) ** a * Fraction(num, den) ** b,
                   Fraction(num, den) ** total, "stem8 fractional base")

        correct = f"{frac}^{total}"
        options = [
            (correct, True, None),
            (f"{frac}^{a * b}", False, "Multiplies the exponents instead of adding"),
            (f"({num ** 2}/{den ** 2})^{total}", False,
             "Squares the base as well as combining the exponents"),
            # den * 2 collides with den ** 2 when den is 2, so the altered base
            # moves the numerator instead.
            (f"({num + 1}/{den})^{total}", False,
             "Changes the base instead of leaving it alone"),
        ]
        rng.shuffle(options)
        choices = [QuestionChoice(key=chr(ord("a") + i), text=t, text_latex=t,
                                  is_correct=c, distractor_rationale=r)
                   for i, (t, c, r) in enumerate(options)]
        key = next(c.key for c in choices if c.is_correct).upper()

        stem_text = (
            f"An expression is given.\n\n  {frac}^{a} x {frac}^{b}\n\n"
            f"Select an equivalent expression."
        )
        worked = (
            f"The product of powers rule works the same for a fractional base.\n"
            f"The base {frac} does not change; the exponents add.\n"
            f"{a} + {b} = {total}, so the expression equals {correct}."
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.AT,
                                         ItemType.MC, Difficulty.MEDIUM, 8, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{key}. {correct}", answer_latex=f"{key}. {correct}",
            worked_solution=worked, choices=choices,
            context_scenario="product of powers with a fractional base",
            seed=self.base_seed * 1000 + 800 + variant_idx,
            stem_index=8, variant_index=variant_idx,
        )

    # ================================================================
    # STEM 9: Above Proficiency - ER (DOK 3, Difficult)
    # NEW. The revision's added Above item shows a student's work in a table,
    # asks where it goes wrong, and asks for the correct simplification. The
    # planted error is the classic one: multiplying exponents where the product
    # rule calls for adding them.
    # ================================================================
    def stem9_above_er(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(9, variant_idx)
        student = pick_name(rng)

        base = rng.randint(2, 6)
        a = rng.randint(2, 5)
        b = rng.randint(2, 4)
        c = rng.randint(2, 3)
        # a + b == a * b (as with 2 and 2) makes the planted mistake give the
        # right answer, leaving nothing to find.
        while a + b == a * b:
            a = rng.randint(2, 5)
            b = rng.randint(2, 4)

        # (base^a x base^b)^c  ->  base^((a+b)*c)
        correct_exp = (a + b) * c
        wrong_exp = (a * b) * c
        _assert_eq(_pow(base, a) * _pow(base, b), _pow(base, a + b), "stem9 product")
        _assert_ne(_pow(base, correct_exp), _pow(base, wrong_exp), "stem9 error is real")

        expr = f"({_exp(base, a)} x {_exp(base, b)})^{c}"
        steps = (
            f"Step 1: {_exp(base, a)} x {_exp(base, b)} = {_exp(base, a * b)}\n"
            f"Step 2: ({_exp(base, a * b)})^{c} = {_exp(base, wrong_exp)}"
        )

        stem_text = (
            f"An expression is given.\n\n  {expr}\n\n"
            f"{student} simplifies the expression incorrectly. "
            f"{student}'s work is shown.\n\n{steps}\n\n"
            f"Identify where {student} made an error and explain how to "
            f"simplify the expression correctly."
        )

        answer = (
            f"The error is in Step 1. {student} multiplied the exponents, but "
            f"the product of powers rule adds them: "
            f"{_exp(base, a)} x {_exp(base, b)} = {_exp(base, a + b)}, "
            f"not {_exp(base, a * b)}.\n"
            f"Step 2 applies the power of a power rule correctly, so once "
            f"Step 1 is fixed the work finishes as "
            f"({_exp(base, a + b)})^{c} = {_exp(base, correct_exp)}.\n"
            f"Exponents add when powers of the same base are multiplied, and "
            f"multiply only when a power is raised to another power."
        )

        worked = (
            f"Correct simplification:\n"
            f"{_exp(base, a)} x {_exp(base, b)} = {_exp(base, a + b)}  "
            f"(add the exponents)\n"
            f"({_exp(base, a + b)})^{c} = {_exp(base, correct_exp)}  "
            f"(multiply the exponents)\n"
            f"{student} got {_exp(base, wrong_exp)} by adding and multiplying "
            f"the wrong way round in Step 1."
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE,
                                         ItemType.ER, Difficulty.DIFFICULT, 9, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=ItemType.ER,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=worked,
            context_scenario="error analysis of an exponent simplification",
            seed=self.base_seed * 1000 + 900 + variant_idx,
            stem_index=9, variant_index=variant_idx,
        )

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_approaching_mc,
            self.stem3_approaching_nr,
            self.stem4_at_mc,
            self.stem5_above_nr,
            self.stem6_below_nr,
            self.stem7_approaching_nr,
            self.stem8_at_mc,
            self.stem9_above_er,
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
            2: self.stem2_approaching_mc,
            3: self.stem3_approaching_nr,
            4: self.stem4_at_mc,
            5: self.stem5_above_nr,
            6: self.stem6_below_nr,
            7: self.stem7_approaching_nr,
            8: self.stem8_at_mc,
            9: self.stem9_above_er,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-5.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 8.NS.3 question variants...")
    gen = Stem8NS3(seed=42)
    all_q = gen.generate_all_variants(variants_per_stem=6)
    for q in all_q:
        print(f"\n{'='*60}")
        print(f"ID: {q.question_id}")
        print(f"Stem {q.stem_index} | {q.proficiency_level.value} | {q.difficulty.value} | DOK {q.dok}")
        print(f"Style: {q.context_scenario}")
        print(f"\n{q.stem_text}")
        if q.choices:
            for c in q.choices:
                marker = " *" if c.is_correct else ""
                print(f"  {c.key}. {c.text}{marker}")
        print(f"\nAnswer: {q.answer_text}")
    print(f"\nTotal: {len(all_q)}")
