"""
Stem generator for 7.AF.1:
  Apply the properties of operations (identity, inverse, commutative,
  associative, distributive) to create equivalent linear expressions,
  including factoring. Justify each step.

Content Limits:
  - Only rational numbers
  - Linear expressions in one or two variables
  - Factoring: p(qx + r) or p(qx - r) where p, q, r are rational
  - No nested parentheses beyond ()
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: integer coefficients only
  Medium: mix of integer and non-integer rational coefficients
  Difficult: only non-integer rational coefficients

6 Stems from the Item Spec:
  Stem 1 (Below-NR):  Find missing coefficient by combining like terms (DOK 2, Easy)
  Stem 2 (Below-MC):  Identify property demonstrated (DOK 1, Easy)
  Stem 3 (Approaching-MC): Factor expression — select equivalent factored form (DOK 2, Easy)
  Stem 4 (Approaching-MC): Error analysis — find mistake in distribution (DOK 3, Medium)
  Stem 5 (At-NR):     Distribute and combine like terms (DOK 2, Medium)
  Stem 6 (Above-MS):  Select ALL equivalent expressions (DOK 2, Easy)
"""

import random
from fractions import Fraction
from typing import Optional

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.models import (
    GeneratedQuestion, QuestionChoice, QuestionPart,
    Difficulty, ProficiencyLevel, ItemType, RationalNumber,
    make_question_id
)
from engine.number_generators import NumberGenerator
from engine.distractor_engine import shuffle_choices


STANDARD_CODE = "7.AF.1"
VARIANTS_PER_STEM = 20


def _fmt_coeff(c: Fraction, var: str, first: bool = False) -> str:
    """Format a coefficient*variable term for display.

    first=True means this is the first term (no leading +).
    Handles: 1x -> x, -1x -> -x, 0x -> omitted (caller handles).
    """
    if c == 0:
        return ""
    sign = ""
    if c > 0 and not first:
        sign = " + "
    elif c < 0:
        sign = " - " if not first else "-"
        c = abs(c)

    if c == 1:
        return f"{sign}{var}"
    elif c.denominator == 1:
        return f"{sign}{int(c)}{var}"
    else:
        return f"{sign}{c.numerator}/{c.denominator}{var}"


def _fmt_const(c: Fraction, first: bool = False) -> str:
    """Format a constant term for display."""
    if c == 0:
        return ""
    sign = ""
    if c > 0 and not first:
        sign = " + "
    elif c < 0:
        sign = " - " if not first else "-"
        c = abs(c)

    if c.denominator == 1:
        return f"{sign}{int(c)}"
    return f"{sign}{c.numerator}/{c.denominator}"


def _fmt_fraction_coeff(c: Fraction, var: str, first: bool = False) -> str:
    """Format a coefficient as a fraction (not decimal) for display."""
    if c == 0:
        return ""
    sign = ""
    if c > 0 and not first:
        sign = " + "
    elif c < 0:
        sign = " - " if not first else "-"
        c = abs(c)

    if c == 1:
        return f"{sign}{var}"
    elif c.denominator == 1:
        return f"{sign}{int(c)}{var}"
    else:
        return f"{sign}{c.numerator}/{c.denominator}{var}"


def _fmt_fraction_const(c: Fraction, first: bool = False) -> str:
    """Format a constant as a fraction for display."""
    if c == 0:
        return ""
    sign = ""
    if c > 0 and not first:
        sign = " + "
    elif c < 0:
        sign = " - " if not first else "-"
        c = abs(c)

    if c.denominator == 1:
        return f"{sign}{int(c)}"
    return f"{sign}{c.numerator}/{c.denominator}"


def _format_expression(coeff_x: Fraction, const: Fraction, var: str = "x") -> str:
    """Format ax + b expression, handling edge cases."""
    parts = []
    cx = _fmt_coeff(coeff_x, var, first=True)
    if cx:
        parts.append(cx)
    cc = _fmt_const(const, first=(len(parts) == 0))
    if cc:
        parts.append(cc)
    if not parts:
        return "0"
    return "".join(parts)


class Stem7AF1:
    """Generates ~20 variants for each of 6 stems from the 7.AF.1 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        """Create a seeded NumberGenerator for a specific stem+variant."""
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - Numeric Response (DOK 2, Easy)
    # "(-y + 5) + (7y - 9) = (ny - 4)  Find n."
    # Combine like terms on LHS, match to RHS to find missing coeff.
    # ================================================================

    def stem1_below_nr(self, variant_idx: int) -> GeneratedQuestion:
        """Below Proficiency - Find the missing coefficient.

        Two expressions added on LHS, result on RHS with one unknown coeff.
        Student combines like terms to find the missing value.
        Difficulty: easy (integer coefficients)
        """
        gen, rng = self._make_gen(1, variant_idx)

        var = rng.choice(["x", "y", "n", "m"])

        # Generate two binomials: (a1*var + b1) + (a2*var + b2)
        a1 = int(gen.integer_coefficient(-8, 8))
        b1 = int(gen.integer_coefficient(-12, 12))
        a2 = int(gen.integer_coefficient(-8, 8))
        b2 = int(gen.integer_coefficient(-12, 12))

        # Combined: (a1+a2)var + (b1+b2)
        sum_a = a1 + a2
        sum_b = b1 + b2

        # RHS: missing*var + sum_b  (student finds missing = sum_a)
        # Use a different letter for the missing value
        missing_var = "n" if var != "n" else "k"
        answer = sum_a

        # Format LHS terms
        def _term(coeff, v, const, paren=True):
            """Build a binomial like (-y + 5)."""
            parts = _fmt_coeff(Fraction(coeff), v, first=True) + _fmt_const(Fraction(const))
            if paren:
                return f"({parts})"
            return parts

        lhs_1 = _term(a1, var, b1)
        lhs_2 = _term(a2, var, b2)

        rhs = f"({missing_var}{var}{_fmt_const(Fraction(sum_b))})"

        stem_text = (
            f"{lhs_1} + {lhs_2} = {rhs}\n\n"
            f"Find the value of {missing_var}."
        )

        worked = (
            f"Combine like terms on the left side:\n"
            f"  {var} terms: {a1} + {a2} = {sum_a}\n"
            f"  Constants: {b1} + {b2} = {sum_b}\n"
            f"  Left side = {_format_expression(Fraction(sum_a), Fraction(sum_b), var)}\n"
            f"  Right side = {missing_var}{var}{_fmt_const(Fraction(sum_b))}\n"
            f"  So {missing_var} = {answer}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.NR,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY,
            dok=2,
            item_type=ItemType.NR,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=str(answer),
            answer_latex=str(answer),
            worked_solution=worked,
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Below Proficiency - Multiple Choice (DOK 1, Easy)
    # "Which property is demonstrated?"
    # Show a step (e.g., 3(x+2) = 3x + 6) and identify as distributive.
    # ================================================================

    def stem2_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Below Proficiency - Identify the property demonstrated.

        Show a mathematical step and ask which property justifies it.
        Properties: commutative, associative, distributive, identity.
        Difficulty: easy (integer coefficients)
        """
        gen, rng = self._make_gen(2, variant_idx)

        var = rng.choice(["x", "y", "a", "b"])

        # Pick which property to demonstrate
        property_type = rng.choice(["distributive", "commutative", "associative"])

        if property_type == "distributive":
            p = int(gen.integer_coefficient(2, 9))
            q = int(gen.integer_coefficient(1, 10))
            r = int(gen.integer_coefficient(1, 10))
            # Show: p(qx + r) = pqx + pr
            pq = p * q
            pr = p * r
            step_text = (
                f"{p}({q}{var} + {r}) = "
                f"{_format_expression(Fraction(pq), Fraction(pr), var)}"
            )
            correct_answer = "Distributive Property"
            explanation = f"Multiplying {p} by each term inside the parentheses uses the distributive property."

        elif property_type == "commutative":
            a = int(gen.integer_coefficient(1, 12))
            b = int(gen.integer_coefficient(1, 12))
            op = rng.choice(["add", "mult"])
            if op == "add":
                step_text = f"{a}{var} + {b} = {b} + {a}{var}"
                explanation = "Changing the order of addition uses the commutative property of addition."
            else:
                step_text = f"{a} * {b}{var} = {b}{var} * {a}"
                explanation = "Changing the order of multiplication uses the commutative property of multiplication."
            correct_answer = "Commutative Property"

        else:  # associative
            a = int(gen.integer_coefficient(2, 8))
            b = int(gen.integer_coefficient(2, 8))
            c = int(gen.integer_coefficient(2, 8))
            op = rng.choice(["add", "mult"])
            if op == "add":
                step_text = f"({a} + {b}) + {c}{var} = {a} + ({b} + {c}{var})"
                explanation = "Regrouping terms in addition uses the associative property of addition."
            else:
                step_text = f"({a} * {b}) * {c}{var} = {a} * ({b} * {c}{var})"
                explanation = "Regrouping factors in multiplication uses the associative property of multiplication."
            correct_answer = "Associative Property"

        stem_text = (
            f"Which property of operations is demonstrated below?\n\n"
            f"  {step_text}"
        )

        # Build choices
        all_properties = [
            "Distributive Property",
            "Commutative Property",
            "Associative Property",
            "Identity Property"
        ]
        distractors = [p for p in all_properties if p != correct_answer]
        rng.shuffle(distractors)
        distractors = distractors[:3]

        choices = shuffle_choices(correct_answer, correct_answer,
                                  distractors, rng)

        correct_letter = next(c.key for c in choices if c.is_correct)

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY,
            dok=1,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct_answer}",
            answer_latex=f"{correct_letter}) {correct_answer}",
            worked_solution=explanation,
            choices=choices,
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - Multiple Choice (DOK 2, Easy)
    # "Which expression is equivalent to 36x + 9?"
    # Student must factor out the GCF.
    # ================================================================

    def stem3_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Approaching Proficiency - Factor an expression.

        Given an expanded expression, select the correctly factored form.
        Difficulty: easy (integer coefficients)
        """
        gen, rng = self._make_gen(3, variant_idx)

        var = rng.choice(["x", "y", "p", "m"])

        # Generate factored form: factor * (inner_coeff * var + inner_const)
        factor = int(gen.small_whole(2, 9))
        inner_coeff = int(gen.small_whole(1, 8))
        inner_const = int(gen.integer_coefficient(-10, 10))
        # Avoid inner_const == 0
        while inner_const == 0:
            inner_const = int(gen.integer_coefficient(-10, 10))

        # Expanded form
        expanded_coeff = factor * inner_coeff
        expanded_const = factor * inner_const

        expanded_str = _format_expression(Fraction(expanded_coeff), Fraction(expanded_const), var)

        # Correct factored form
        inner_str = _format_expression(Fraction(inner_coeff), Fraction(inner_const), var)
        correct = f"{factor}({inner_str})"

        # Distractors: common factoring errors
        distractors = []

        # Error 1: Wrong factor (off by 1)
        wrong_f = factor + rng.choice([1, -1]) if factor > 2 else factor + 1
        if wrong_f != 0:
            wc = expanded_coeff // wrong_f if expanded_coeff % wrong_f == 0 else inner_coeff
            wk = expanded_const // wrong_f if expanded_const % wrong_f == 0 else inner_const
            d1 = f"{wrong_f}({_format_expression(Fraction(wc), Fraction(wk), var)})"
            if d1 != correct:
                distractors.append(d1)

        # Error 2: Forgot to factor one term
        d2 = f"{factor}({_format_expression(Fraction(inner_coeff), Fraction(expanded_const), var)})"
        if d2 != correct and d2 not in distractors:
            distractors.append(d2)

        # Error 3: Sign error in factored constant
        d3 = f"{factor}({_format_expression(Fraction(inner_coeff), Fraction(-inner_const), var)})"
        if d3 != correct and d3 not in distractors:
            distractors.append(d3)

        # Error 4: Swapped factor
        d4 = f"{inner_coeff}({_format_expression(Fraction(factor), Fraction(inner_const), var)})"
        if d4 != correct and d4 not in distractors:
            distractors.append(d4)

        # Ensure we have at least 3 distractors
        while len(distractors) < 3:
            alt_f = rng.randint(2, 10)
            alt_inner = rng.randint(1, 8)
            alt_const = rng.choice([-1, 1]) * rng.randint(1, 10)
            d = f"{alt_f}({_format_expression(Fraction(alt_inner), Fraction(alt_const), var)})"
            if d != correct and d not in distractors:
                distractors.append(d)

        distractors = distractors[:3]

        stem_text = f"Which expression is equivalent to {expanded_str}?"

        choices = shuffle_choices(correct, correct, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"Factor out {factor} from {expanded_str}:\n"
            f"  {expanded_coeff}{var} / {factor} = {inner_coeff}{var}\n"
            f"  {expanded_const} / {factor} = {inner_const}\n"
            f"  = {correct}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.EASY, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY,
            dok=2,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct}",
            answer_latex=f"{correct_letter}) {correct}",
            worked_solution=worked,
            choices=choices,
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: Approaching Proficiency - Multiple Choice (DOK 3, Medium)
    # Error analysis: student shows distribution steps, one has an error.
    # Student must identify which step is wrong.
    # ================================================================

    def stem4_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Approaching Proficiency - Error analysis in distribution.

        Shows a student's step-by-step simplification with one error.
        Student identifies the first incorrect step.
        Difficulty: medium (includes decimals)
        """
        gen, rng = self._make_gen(4, variant_idx)

        var = rng.choice(["x", "y"])

        # Generate: a(bx + c + dx) where student must distribute a to all terms
        # Use decimals for medium difficulty
        a = gen.decimal_coefficient(1.0, 5.0)
        while a == 0:
            a = gen.decimal_coefficient(1.0, 5.0)
        b = gen.decimal_coefficient(1.0, 9.0)
        while b == 0:
            b = gen.decimal_coefficient(1.0, 9.0)
        c_val = gen.decimal_coefficient(-9.0, 9.0)
        while c_val == 0:
            c_val = gen.decimal_coefficient(-9.0, 9.0)
        d = gen.decimal_coefficient(1.0, 5.0)
        while d == 0:
            d = gen.decimal_coefficient(1.0, 5.0)

        # Correct steps:
        # Step 1: a(bx + c + dx)  (given)
        # Step 2: abx + ac + adx  (distribute)
        # Step 3: (ab + ad)x + ac  (combine like terms)
        ab = a * b
        ac = a * c_val
        ad = a * d

        correct_combined_coeff = ab + ad
        correct_const = ac

        # Format step 1
        inner = _format_expression(Fraction(b), Fraction(0), var)
        inner += _fmt_const(c_val)
        inner += _fmt_coeff(d, var)
        step1 = f"{float(a):g}({inner})"

        # Pick an error type
        error_type = rng.choice(["sign_error", "forgot_term", "wrong_combine"])

        if error_type == "sign_error":
            # Student flips sign on one distributed term
            wrong_ac = -ac  # sign error on constant
            step2_wrong = (
                f"{_format_expression(ab, Fraction(0), var)}"
                f"{_fmt_const(wrong_ac)}"
                f"{_fmt_coeff(ad, var)}"
            )
            step3_correct_for_wrong = _format_expression(ab + ad, wrong_ac, var)
            error_step = "Step 2"
            error_desc = f"The sign of {float(ac):g} is wrong. {float(a):g} * ({float(c_val):g}) = {float(ac):g}, not {float(wrong_ac):g}."
            # Steps for display
            steps = [
                ("Step 1", step1, True),
                ("Step 2", step2_wrong, False),  # ERROR here
                ("Step 3", step3_correct_for_wrong, True),  # Consistent with wrong step 2
            ]

        elif error_type == "forgot_term":
            # Student forgets to distribute to one term
            step2_wrong = (
                f"{_format_expression(ab, Fraction(0), var)}"
                f"{_fmt_const(c_val)}"  # forgot to multiply c by a
                f"{_fmt_coeff(ad, var)}"
            )
            wrong_combined = _format_expression(ab + ad, c_val, var)
            error_step = "Step 2"
            error_desc = f"The student forgot to multiply {float(c_val):g} by {float(a):g}. It should be {float(ac):g}."
            steps = [
                ("Step 1", step1, True),
                ("Step 2", step2_wrong, False),  # ERROR
                ("Step 3", wrong_combined, True),
            ]

        else:  # wrong_combine
            # Distribution is correct, but combining like terms is wrong
            step2_correct = (
                f"{_format_expression(ab, Fraction(0), var)}"
                f"{_fmt_const(ac)}"
                f"{_fmt_coeff(ad, var)}"
            )
            wrong_combined_coeff = ab - ad  # subtracted instead of added
            step3_wrong = _format_expression(wrong_combined_coeff, ac, var)
            error_step = "Step 3"
            error_desc = (
                f"When combining {float(ab):g}{var} and {float(ad):g}{var}, "
                f"the result should be {float(correct_combined_coeff):g}{var}, "
                f"not {float(wrong_combined_coeff):g}{var}."
            )
            steps = [
                ("Step 1", step1, True),
                ("Step 2", step2_correct, True),
                ("Step 3", step3_wrong, False),  # ERROR
            ]

        # Build stem text showing student's work
        student_name = rng.choice(["Alex", "Jordan", "Morgan", "Taylor", "Riley", "Casey"])
        step_lines = "\n".join(f"  {label}: {expr}" for label, expr, _ in steps)
        stem_text = (
            f"{student_name} simplified the expression below. Identify the step "
            f"where the first error occurs.\n\n"
            f"  Given: {step1}\n\n"
            f"{student_name}'s work:\n"
            f"{step_lines}"
        )

        # Choices: Step 1, Step 2, Step 3, No error
        correct_answer = error_step
        all_options = ["Step 1", "Step 2", "Step 3", "There is no error"]
        distractors = [opt for opt in all_options if opt != correct_answer]

        choices = shuffle_choices(correct_answer, correct_answer, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        correct_result = _format_expression(correct_combined_coeff, correct_const, var)
        worked = (
            f"The error is in {error_step}.\n"
            f"{error_desc}\n"
            f"Correct simplification: {step1} = {correct_result}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM,
            dok=3,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct_answer}",
            answer_latex=f"{correct_letter}) {correct_answer}",
            worked_solution=worked,
            choices=choices,
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: At Proficiency - Numeric Response (DOK 2, Medium)
    # "Simplify: -0.8(10.8x - 20 + 3.2x)"
    # Distribute and combine like terms. Answer as simplified expression.
    # ================================================================

    def stem5_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        """At Proficiency - Distribute and combine like terms.

        Student distributes a coefficient across a multi-term expression
        then combines like terms to produce a simplified expression.
        Difficulty: medium (decimal coefficients)
        """
        gen, rng = self._make_gen(5, variant_idx)

        var = rng.choice(["x", "y"])

        # Pick expression form: either a(bx + c) or (ax + b) + (cx + d)
        form = rng.choice(["distribute", "combine_two"])

        if form == "distribute":
            # a(bx + c) — distribute then combine
            use_fraction = (variant_idx % 3 == 0)
            if use_fraction:
                # Fraction distribution: e.g., 1/2(4x - 8) per spec example
                frac_choices = [Fraction(1, 2), Fraction(1, 4), Fraction(3, 4), Fraction(2, 3)]
                a = rng.choice(frac_choices) * rng.choice([1, -1])
                # Integer inner terms divisible by denominator for clean results
                d = a.denominator
                b = Fraction(rng.choice([i for i in range(2, 10) if i % d == 0]))
                c = Fraction(rng.choice([i * s for i in range(2, 13) if i % d == 0
                                         for s in [1, -1]]))
                while c == 0:
                    c = Fraction(rng.choice([i * s for i in range(2, 13) if i % d == 0
                                             for s in [1, -1]]))
            else:
                a = gen.decimal_coefficient(-5.0, 5.0)
                while a == 0 or a == Fraction(1) or a == Fraction(-1):
                    a = gen.decimal_coefficient(-5.0, 5.0)
                b = gen.decimal_coefficient(1.0, 9.0)
                while b == 0:
                    b = gen.decimal_coefficient(1.0, 9.0)
                c = gen.decimal_coefficient(-9.0, 9.0)
                while c == 0:
                    c = gen.decimal_coefficient(-9.0, 9.0)

            # Correct answer
            result_coeff = a * b
            result_const = a * c

            # Format the expression
            inner = _format_expression(b, c, var)
            if use_fraction:
                a_str = f"{a.numerator}/{a.denominator}" if a > 0 else f"-{abs(a).numerator}/{abs(a).denominator}"
                expr_text = f"{a_str}({inner})"
            else:
                expr_text = f"{float(a):g}({inner})"

        else:
            # (ax + b) + (cx + d) OR (ax + b) - (cx + d)
            a = gen.decimal_coefficient(-5.0, 5.0)
            while a == 0:
                a = gen.decimal_coefficient(-5.0, 5.0)
            b = gen.decimal_coefficient(-9.0, 9.0)
            c = gen.decimal_coefficient(-5.0, 5.0)
            while c == 0:
                c = gen.decimal_coefficient(-5.0, 5.0)
            d = gen.decimal_coefficient(-9.0, 9.0)

            op = rng.choice(["+", "-"])
            if op == "+":
                result_coeff = a + c
                result_const = b + d
                expr1 = _format_expression(a, b, var)
                expr2 = _format_expression(c, d, var)
                expr_text = f"({expr1}) + ({expr2})"
            else:
                result_coeff = a - c
                result_const = b - d
                expr1 = _format_expression(a, b, var)
                expr2 = _format_expression(c, d, var)
                expr_text = f"({expr1}) - ({expr2})"

        answer_str = _format_expression(result_coeff, result_const, var)

        stem_text = f"Simplify the expression:\n\n  {expr_text}"

        if form == "distribute":
            def _n(v):
                return f"{v.numerator}/{v.denominator}" if v.denominator != 1 else f"{float(v):g}"
            worked = (
                f"Distribute {_n(a)} to each term:\n"
                f"  {_n(a)} * {_n(b)}{var} = {_n(result_coeff)}{var}\n"
                f"  {_n(a)} * ({_n(c)}) = {_n(result_const)}\n"
                f"  = {answer_str}"
            )
        else:
            worked = (
                f"Combine like terms:\n"
                f"  {var} terms: {float(a):g} {op} {float(c):g} = {float(result_coeff):g}\n"
                f"  Constants: {float(b):g} {op} {float(d):g} = {float(result_const):g}\n"
                f"  = {answer_str}"
            )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.MEDIUM, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM,
            dok=2,
            item_type=ItemType.NR,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=answer_str,
            answer_latex=answer_str,
            worked_solution=worked,
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 6: Above Proficiency - Multiple Select (DOK 2, Easy)
    # "Select ALL expressions that are equivalent to 3x + 5(-4x + 12) - (x - 3)"
    # Multiple correct answers from a list of 5-6 options.
    # ================================================================

    def stem6_above_ms(self, variant_idx: int) -> GeneratedQuestion:
        """Above Proficiency - Select all equivalent expressions.

        Given a complex expression, student identifies all equivalent forms
        from a list including expanded, partially simplified, and factored forms.
        Difficulty: easy (integer coefficients)
        """
        gen, rng = self._make_gen(6, variant_idx)

        var = rng.choice(["x", "y"])

        # Generate: ax + b(cx + d) + (ex + f)
        a = int(gen.integer_coefficient(-6, 6))
        b = int(gen.small_whole(2, 6)) * rng.choice([-1, 1])
        c = int(gen.integer_coefficient(-5, 5))
        while c == 0:
            c = int(gen.integer_coefficient(-5, 5))
        d = int(gen.integer_coefficient(-10, 10))
        while d == 0:
            d = int(gen.integer_coefficient(-10, 10))
        e = int(gen.integer_coefficient(-5, 5))
        f = int(gen.integer_coefficient(-10, 10))

        # Fully simplified
        total_coeff = a + b * c + e
        total_const = b * d + f

        # Build the original expression
        term1 = _fmt_coeff(Fraction(a), var, first=True)
        inner_bc = _format_expression(Fraction(c), Fraction(d), var)
        term2 = f" + {b}({inner_bc})" if b > 0 else f" - {abs(b)}({inner_bc})"
        if e != 0 or f != 0:
            sub_expr = _format_expression(Fraction(e), Fraction(f), var)
            term3 = f" + ({sub_expr})" if (e > 0 or (e == 0 and f > 0)) else f" - ({_format_expression(Fraction(-e), Fraction(-f), var)})"
        else:
            term3 = ""

        original = term1 + term2 + term3

        simplified = _format_expression(Fraction(total_coeff), Fraction(total_const), var)

        # Generate correct equivalent expressions
        correct_exprs = set()
        correct_exprs.add(simplified)

        # Partially simplified: distribute b but don't combine with a
        bc = b * c
        bd = b * d
        partial = _format_expression(Fraction(a + bc), Fraction(bd), var)
        if e != 0 or f != 0:
            partial += f" + ({_format_expression(Fraction(e), Fraction(f), var)})"
        if partial != simplified:
            correct_exprs.add(partial)

        # Rearranged
        rearranged = _format_expression(Fraction(total_coeff), Fraction(0), var)
        if total_const > 0:
            rearranged += f" + {total_const}"
        elif total_const < 0:
            rearranged += f" - {abs(total_const)}"
        if rearranged != simplified:
            correct_exprs.add(rearranged)

        # Generate wrong expressions (look similar but wrong)
        wrong_exprs = set()

        # Wrong 1: sign error on b*d
        w1 = _format_expression(Fraction(total_coeff), Fraction(-total_const), var)
        if w1 not in correct_exprs:
            wrong_exprs.add(w1)

        # Wrong 2: forgot to distribute b to d
        w2_coeff = a + b * c + e
        w2_const = d + f  # forgot to multiply d by b
        w2 = _format_expression(Fraction(w2_coeff), Fraction(w2_const), var)
        if w2 not in correct_exprs:
            wrong_exprs.add(w2)

        # Wrong 3: wrong sign when subtracting
        w3_coeff = a + b * c - e  # subtracted e instead of adding
        w3_const = b * d - f
        w3 = _format_expression(Fraction(w3_coeff), Fraction(w3_const), var)
        if w3 not in correct_exprs:
            wrong_exprs.add(w3)

        # Wrong 4: coefficient error
        w4 = _format_expression(Fraction(total_coeff + rng.choice([1, -1, 2])),
                                 Fraction(total_const), var)
        if w4 not in correct_exprs:
            wrong_exprs.add(w4)

        # Ensure at least 3 wrong options
        while len(wrong_exprs) < 3:
            delta_c = rng.choice([1, -1, 2, -2])
            delta_k = rng.choice([1, -1, 2, -2])
            w = _format_expression(Fraction(total_coeff + delta_c),
                                    Fraction(total_const + delta_k), var)
            if w not in correct_exprs:
                wrong_exprs.add(w)

        # Build choices: 2-3 correct + 3 wrong
        correct_list = list(correct_exprs)[:3]
        wrong_list = list(wrong_exprs)[:3]

        all_options = [(expr, True) for expr in correct_list] + [(expr, False) for expr in wrong_list]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i),
                text=text,
                text_latex=text,
                is_correct=is_correct,
            ))

        correct_letters = [c.key for c in choices if c.is_correct]

        stem_text = (
            f"Select ALL expressions that are equivalent to:\n\n"
            f"  {original}"
        )

        worked = (
            f"Simplify the original expression:\n"
            f"  {original}\n"
            f"  Distribute: {a}{var} + {b*c}{var} + {b*d} + {e}{var} + {f}\n"
            f"  Combine like terms: ({a} + {b*c} + {e}){var} + ({b*d} + {f})\n"
            f"  = {simplified}\n"
            f"Equivalent expressions: {', '.join(correct_list)}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MS,
                               Difficulty.EASY, 6, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.EASY,
            dok=2,
            item_type=ItemType.MS,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"{', '.join(correct_letters)}) {'; '.join(correct_list)}",
            answer_latex=f"{', '.join(correct_letters)}) {'; '.join(correct_list)}",
            worked_solution=worked,
            choices=choices,
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6,
            variant_index=variant_idx
        )

    # ================================================================
    # HELPER METHODS
    # ================================================================

    @staticmethod
    def _fmt(val: Fraction) -> str:
        """Format a fraction for text display."""
        if val.denominator == 1:
            return str(int(val))
        av = abs(val)
        if av > 1:
            whole = int(av)
            remainder = av - whole
            if remainder == 0:
                return ("-" if val < 0 else "") + str(whole)
            sign = "-" if val < 0 else ""
            return f"{sign}{whole} {remainder.numerator}/{remainder.denominator}"
        if val < 0:
            return f"-{av.numerator}/{av.denominator}"
        return f"{val.numerator}/{val.denominator}"

    # ================================================================
    # MAIN GENERATION METHOD
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        """Generate all variants for all 6 stems.

        Returns ~120 questions (6 stems x 20 variants).
        """
        all_questions = []

        stem_methods = [
            self.stem1_below_nr,
            self.stem2_below_mc,
            self.stem3_approaching_mc,
            self.stem4_approaching_mc,
            self.stem5_at_nr,
            self.stem6_above_ms,
        ]

        for stem_fn in stem_methods:
            for v in range(variants_per_stem):
                try:
                    question = stem_fn(v)
                    all_questions.append(question)
                except Exception as e:
                    print(f"Error generating {stem_fn.__name__} variant {v}: {e}")
                    continue

        return all_questions

    def generate_stem_variants(self, stem_index: int,
                                variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        """Generate variants for a single stem (1-6)."""
        stem_methods = {
            1: self.stem1_below_nr,
            2: self.stem2_below_mc,
            3: self.stem3_approaching_mc,
            4: self.stem4_approaching_mc,
            5: self.stem5_at_nr,
            6: self.stem6_above_ms,
        }

        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-6.")

        questions = []
        for v in range(variants_per_stem):
            try:
                questions.append(fn(v))
            except Exception as e:
                print(f"Error generating stem {stem_index} variant {v}: {e}")
                continue

        return questions


# ================================================================
# CLI ENTRY POINT FOR TESTING
# ================================================================

if __name__ == "__main__":
    print("Generating 7.AF.1 question variants...")
    print("=" * 60)

    generator = Stem7AF1(seed=42)
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
