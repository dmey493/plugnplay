"""
Stem generator for 6.NS.5:
  Apply the order of operations and properties of operations to evaluate
  numerical expressions with nonnegative rational numbers, including
  grouping symbols and whole number exponents.

Content Limits:
  - Nonnegative rational numbers
  - Grouping symbols (parentheses, brackets)
  - Whole number exponents
  - Properties: commutative, associative, distributive
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: whole numbers, one operation inside grouping
  Medium: whole numbers, two operations inside grouping or two sets of grouping
  Difficult: fractions/decimals, two sets of grouping

The 2026-08-17 revision moved 'identify equivalent expressions by a property'
down to Approaching (stem 5) and rewrote Above around complex rational
expressions and placing grouping symbols, neither of which existed, so stems
6 and 7 were written for it. Stems 1 to 4 were left untouched.

7 Stems from the Item Spec:
  Stem 1 (Below-NR):      Evaluate expression like 6 x (42/7) + 100 (DOK 1, easy)
  Stem 2 (Below-MC):      Identify which property is being applied (DOK 2, easy)
  Stem 3 (Approaching-MC): Evaluate expression with brackets like [(54/9 + 14)/4] (DOK 1, medium)
  Stem 4 (At-NR):         Evaluate expression with fractions/decimals and exponents (DOK 1, difficult)
  Stem 5 (Approaching-MS): Identify equivalent expressions by a property (DOK 2, medium)
  Stem 6 (Above-NR):    Complex rational expression, operations above and below the bar (DOK 2, difficult)
  Stem 7 (Above-MC):    Place grouping symbols to make an expression equal a target (DOK 3, difficult)
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


STANDARD_CODE = "6.NS.5"
VARIANTS_PER_STEM = 20


# ============================================================
# PROPERTY DEFINITIONS for Stem 2
# ============================================================

PROPERTIES = [
    {
        "name": "Commutative Property of Addition",
        "pattern": "a + b = b + a",
        "gen": lambda a, b: (f"{a} + {b} = {b} + {a}", "commutative_add"),
    },
    {
        "name": "Commutative Property of Multiplication",
        "pattern": "a x b = b x a",
        "gen": lambda a, b: (f"{a} x {b} = {b} x {a}", "commutative_mult"),
    },
    {
        "name": "Associative Property of Addition",
        "pattern": "(a + b) + c = a + (b + c)",
        "gen": lambda a, b, c=None: (f"({a} + {b}) + {c} = {a} + ({b} + {c})", "associative_add"),
    },
    {
        "name": "Associative Property of Multiplication",
        "pattern": "(a x b) x c = a x (b x c)",
        "gen": lambda a, b, c=None: (f"({a} x {b}) x {c} = {a} x ({b} x {c})", "associative_mult"),
    },
    {
        "name": "Distributive Property",
        "pattern": "a x (b + c) = a x b + a x c",
        "gen": lambda a, b, c=None: (f"{a} x ({b} + {c}) = {a} x {b} + {a} x {c}", "distributive"),
    },
]


class Stem6NS5:
    """Generates ~20 variants for each of 5 stems from the 6.NS.5 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        """Create a seeded NumberGenerator for a specific stem+variant."""
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - NR (DOK 1, Easy)
    # Evaluate expression like: 6 x (42 / 7) + 100
    # Whole numbers, one op inside grouping
    # ================================================================

    def stem1_below_nr(self, variant_idx: int) -> GeneratedQuestion:
        """Below Proficiency - Evaluate a simple order-of-operations expression.

        Expression has one grouping with one operation inside, plus one
        operation outside. Whole numbers only.
        Difficulty: easy
        """
        gen, rng = self._make_gen(1, variant_idx)

        # Build expression from answer backwards to guarantee clean values
        # Pattern variations:
        #   a x (b / c) + d    where b/c is a whole number
        #   a + b x (c - d)    where c > d
        #   (a + b) x c - d    where result > 0
        pattern = rng.choice(["mult_div_add", "add_mult_sub", "group_add_mult_sub"])

        if pattern == "mult_div_add":
            # a x (b / c) + d
            c = int(gen.small_whole(2, 9))
            quotient = int(gen.small_whole(2, 9))
            b = c * quotient
            a = int(gen.small_whole(2, 9))
            d = int(gen.whole_number(10, 200))
            answer = Fraction(a * quotient + d)

            expr_text = f"{a} x ({b} / {c}) + {d}"
            expr_latex = f"${a} \\times ({b} \\div {c}) + {d}$"

            worked = (
                f"{expr_text}\n"
                f"= {a} x {quotient} + {d}   (evaluate {b} / {c} first)\n"
                f"= {a * quotient} + {d}   (multiply)\n"
                f"= {int(answer)}   (add)"
            )

        elif pattern == "add_mult_sub":
            # a + b x (c - d)
            d = int(gen.small_whole(1, 8))
            diff = int(gen.small_whole(2, 8))
            c = d + diff
            b = int(gen.small_whole(2, 9))
            a = int(gen.whole_number(5, 50))
            answer = Fraction(a + b * diff)

            expr_text = f"{a} + {b} x ({c} - {d})"
            expr_latex = f"${a} + {b} \\times ({c} - {d})$"

            worked = (
                f"{expr_text}\n"
                f"= {a} + {b} x {diff}   (evaluate {c} - {d} first)\n"
                f"= {a} + {b * diff}   (multiply)\n"
                f"= {int(answer)}   (add)"
            )

        else:
            # (a + b) x c - d
            a = int(gen.small_whole(2, 9))
            b = int(gen.small_whole(2, 9))
            c = int(gen.small_whole(2, 8))
            product = (a + b) * c
            d = int(gen.whole_number(1, max(1, product - 1)))
            answer = Fraction(product - d)

            expr_text = f"({a} + {b}) x {c} - {d}"
            expr_latex = f"$({a} + {b}) \\times {c} - {d}$"

            worked = (
                f"{expr_text}\n"
                f"= {a + b} x {c} - {d}   (evaluate {a} + {b} first)\n"
                f"= {product} - {d}   (multiply)\n"
                f"= {int(answer)}   (subtract)"
            )

        answer_str = str(int(answer))

        stem_text = f"Evaluate the expression.\n\n{expr_text}"
        stem_latex = f"Evaluate the expression.\n\n{expr_latex}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.NR,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY,
            dok=1,
            item_type=ItemType.NR,
            stem_text=stem_text,
            stem_latex=stem_latex,
            answer_text=answer_str,
            answer_latex=f"${answer_str}$",
            worked_solution=worked,
            context_scenario="order of operations - simple grouping",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Below Proficiency - MC (DOK 2, Easy)
    # Identify which property is being applied
    # ================================================================

    def stem2_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Below Proficiency - Identify the property used in an equation.

        Students see an equation demonstrating a property and select its name.
        Difficulty: easy (whole numbers)
        """
        gen, rng = self._make_gen(2, variant_idx)

        # Pick the correct property
        correct_idx = rng.randint(0, len(PROPERTIES) - 1)
        correct_prop = PROPERTIES[correct_idx]

        # Generate numbers for the property
        a = int(gen.small_whole(2, 12))
        b = int(gen.small_whole(2, 12))
        c = int(gen.small_whole(2, 9))

        # Build the equation showing the property
        prop_key = correct_prop["pattern"]
        if "commutative" in correct_prop["name"].lower() and "add" in correct_prop["name"].lower():
            equation = f"{a} + {b} = {b} + {a}"
        elif "commutative" in correct_prop["name"].lower() and "mult" in correct_prop["name"].lower():
            equation = f"{a} x {b} = {b} x {a}"
        elif "associative" in correct_prop["name"].lower() and "add" in correct_prop["name"].lower():
            equation = f"({a} + {b}) + {c} = {a} + ({b} + {c})"
        elif "associative" in correct_prop["name"].lower() and "mult" in correct_prop["name"].lower():
            equation = f"({a} x {b}) x {c} = {a} x ({b} x {c})"
        else:  # distributive
            equation = f"{a} x ({b} + {c}) = {a} x {b} + {a} x {c}"

        correct_name = correct_prop["name"]

        # Build distractors: other property names
        all_names = [p["name"] for p in PROPERTIES]
        distractors = [n for n in all_names if n != correct_name]
        rng.shuffle(distractors)
        distractors = distractors[:3]

        all_options = [(correct_name, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i),
                text=text,
                text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = (
            f"Which property of operations is shown by the equation below?\n\n"
            f"{equation}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY,
            dok=2,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=correct_letter,
            answer_latex=correct_letter,
            worked_solution=f'The equation "{equation}" demonstrates the {correct_name}.',
            choices=choices,
            context_scenario="identify property of operations",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - MC (DOK 1, Medium)
    # Evaluate expression with brackets: [(54/9 + 14) / 4]
    # Two operations inside grouping or two sets of grouping
    # ================================================================

    def stem3_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Approaching Proficiency - Evaluate nested grouping expression.

        Expression uses brackets/parentheses with two levels of grouping.
        Whole numbers only.
        Difficulty: medium
        """
        gen, rng = self._make_gen(3, variant_idx)

        # Build from the inside out to guarantee clean integer results
        # Pattern: [ (a / b + c) / d ] or [ (a x b - c) x d ]
        pattern = rng.choice(["div_add_div", "mult_sub_mult", "add_mult_sub"])

        if pattern == "div_add_div":
            # [ (a / b + c) / d ]
            b = int(gen.small_whole(2, 9))
            inner_quot = int(gen.small_whole(1, 8))
            a = b * inner_quot
            c = int(gen.small_whole(1, 20))
            inner_sum = inner_quot + c
            # Make sure inner_sum is divisible by d
            d = rng.choice([f for f in [2, 3, 4, 5, 6] if inner_sum % f == 0] or [1])
            if d == 1:
                # Regenerate to get a clean division
                c = int(gen.small_whole(2, 10))
                inner_sum = inner_quot + c
                for candidate in [2, 3, 4, 5, 6]:
                    if inner_sum % candidate == 0:
                        d = candidate
                        break
                else:
                    d = 1
            answer = Fraction(inner_sum, d)

            expr_text = f"[({a} / {b} + {c}) / {d}]"
            expr_latex = f"$\\left[\\left(\\frac{{{a}}}{{{b}}} + {c}\\right) \\div {d}\\right]$"

            worked = (
                f"{expr_text}\n"
                f"= [({inner_quot} + {c}) / {d}]   (evaluate {a} / {b})\n"
                f"= [{inner_sum} / {d}]   (add inside parentheses)\n"
                f"= {int(answer) if answer.denominator == 1 else float(answer)}   (divide)"
            )

        elif pattern == "mult_sub_mult":
            # [ (a x b - c) x d ]
            a = int(gen.small_whole(2, 6))
            b = int(gen.small_whole(2, 6))
            product = a * b
            c = int(gen.whole_number(1, max(1, product - 1)))
            diff = product - c
            d = int(gen.small_whole(2, 5))
            answer = Fraction(diff * d)

            expr_text = f"[({a} x {b} - {c}) x {d}]"
            expr_latex = f"$\\left[\\left({a} \\times {b} - {c}\\right) \\times {d}\\right]$"

            worked = (
                f"{expr_text}\n"
                f"= [({product} - {c}) x {d}]   (multiply {a} x {b})\n"
                f"= [{diff} x {d}]   (subtract inside parentheses)\n"
                f"= {int(answer)}   (multiply)"
            )

        else:
            # [ a + (b x c) ] - d
            b = int(gen.small_whole(2, 8))
            c = int(gen.small_whole(2, 8))
            prod = b * c
            a = int(gen.whole_number(5, 30))
            bracket_val = a + prod
            d = int(gen.whole_number(1, max(1, bracket_val - 1)))
            answer = Fraction(bracket_val - d)

            expr_text = f"[{a} + ({b} x {c})] - {d}"
            expr_latex = f"$\\left[{a} + ({b} \\times {c})\\right] - {d}$"

            worked = (
                f"{expr_text}\n"
                f"= [{a} + {prod}] - {d}   (multiply {b} x {c})\n"
                f"= {bracket_val} - {d}   (add inside brackets)\n"
                f"= {int(answer)}   (subtract)"
            )

        answer_str = str(int(answer)) if answer.denominator == 1 else str(float(answer))
        answer_int = int(answer) if answer.denominator == 1 else float(answer)

        # Generate distractors from common order-of-operations errors
        distractors = set()
        # Left-to-right error (ignoring grouping)
        distractors.add(answer_int + rng.choice([3, 5, -3, -5]))
        distractors.add(answer_int * 2)
        distractors.add(abs(answer_int - rng.choice([4, 8, 12])))
        distractors.add(answer_int + rng.choice([10, -10, 7, -7]))
        distractors.discard(answer_int)
        distractors = [d for d in distractors if d > 0 and d != answer_int]
        rng.shuffle(distractors)
        distractors = distractors[:3]

        while len(distractors) < 3:
            d = answer_int + rng.choice([-15, -8, 8, 15, 20])
            if d > 0 and d != answer_int and d not in distractors:
                distractors.append(d)

        all_options = [(str(int(answer_int)), True)] + [(str(int(d)), False) for d in distractors[:3]]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i),
                text=text,
                text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = f"Evaluate the expression.\n\n{expr_text}"
        stem_latex_full = f"Evaluate the expression.\n\n{expr_latex}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM,
            dok=1,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_latex_full,
            answer_text=correct_letter,
            answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices,
            context_scenario="order of operations - nested grouping",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At Proficiency - NR (DOK 1, Difficult)
    # Evaluate expression with fractions/decimals and exponents
    # ================================================================

    def stem4_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        """At Proficiency - Evaluate expression with fractions/decimals and exponents.

        Expression includes an exponent term, fractions or decimals, and grouping.
        Difficulty: difficult (fractions/decimals, two sets of grouping)
        """
        gen, rng = self._make_gen(4, variant_idx)

        # Build from answer backwards
        # Pattern choices:
        #   a^2 + (b/c) x d        where b/c is a clean fraction
        #   (a.d)^2 - b x c        with decimals
        #   a^2 x (b + c/d)        mixed

        pattern = rng.choice(["exp_frac_mult", "dec_exp_sub", "exp_mixed_add"])

        if pattern == "exp_frac_mult":
            # a^2 + (b/c) x d
            a = int(gen.small_whole(2, 6))
            a_sq = a * a
            c = rng.choice([2, 3, 4, 5, 6, 8])
            b = rng.randint(1, c - 1)
            frac = Fraction(b, c)
            d = c * rng.randint(1, 4)  # make d a multiple of c for clean result
            frac_times_d = frac * d
            answer = Fraction(a_sq) + frac_times_d

            frac_rn = RationalNumber(frac, "fraction")
            answer_rn = RationalNumber(answer, "mixed" if answer.denominator != 1 else "whole")

            expr_text = f"{a}^2 + ({b}/{c}) x {d}"
            expr_latex = f"${a}^2 + \\frac{{{b}}}{{{c}}} \\times {d}$"

            ftd_str = str(int(frac_times_d)) if frac_times_d.denominator == 1 else RationalNumber(frac_times_d, "mixed").display()

            worked = (
                f"{expr_text}\n"
                f"= {a_sq} + ({b}/{c}) x {d}   (evaluate {a}^2 = {a_sq})\n"
                f"= {a_sq} + {ftd_str}   (multiply fraction by {d})\n"
                f"= {answer_rn.display()}"
            )

        elif pattern == "dec_exp_sub":
            # a^2 - b.d x c   (all with decimals)
            a = int(gen.small_whole(2, 5))
            a_sq = a * a
            b = gen.decimal_1place(0.5, 3.0)
            c = int(gen.small_whole(2, 6))
            product = b * c
            # Ensure answer is positive
            while a_sq <= product:
                a = a + 1
                a_sq = a * a
            answer = Fraction(a_sq) - product

            b_str = f"{float(b):.1f}"
            prod_str = f"{float(product):.1f}" if product != int(product) else str(int(product))
            answer_val = float(answer)
            answer_str_raw = f"{answer_val:.1f}" if answer_val != int(answer_val) else str(int(answer_val))

            expr_text = f"{a}^2 - {b_str} x {c}"
            expr_latex = f"${a}^2 - {b_str} \\times {c}$"

            worked = (
                f"{expr_text}\n"
                f"= {a_sq} - {b_str} x {c}   (evaluate {a}^2 = {a_sq})\n"
                f"= {a_sq} - {prod_str}   (multiply)\n"
                f"= {answer_str_raw}"
            )

            answer_rn = RationalNumber(answer, "decimal")

        else:  # exp_mixed_add
            # a^2 x (b + c/d)
            a = int(gen.small_whole(2, 4))
            a_sq = a * a
            b = int(gen.small_whole(1, 5))
            d = rng.choice([2, 4, 5])
            c = rng.randint(1, d - 1)
            frac = Fraction(c, d)
            inner = Fraction(b) + frac
            answer = Fraction(a_sq) * inner

            inner_rn = RationalNumber(inner, "mixed")
            answer_rn = RationalNumber(answer, "mixed" if answer.denominator != 1 else "whole")

            expr_text = f"{a}^2 x ({b} + {c}/{d})"
            expr_latex = f"${a}^2 \\times \\left({b} + \\frac{{{c}}}{{{d}}}\\right)$"

            worked = (
                f"{expr_text}\n"
                f"= {a_sq} x ({b} + {c}/{d})   (evaluate {a}^2 = {a_sq})\n"
                f"= {a_sq} x {inner_rn.display()}   (add inside grouping)\n"
                f"= {answer_rn.display()}"
            )

        answer_display = answer_rn.display()

        stem_text = f"Evaluate the expression.\n\n{expr_text}"
        stem_latex_full = f"Evaluate the expression.\n\n{expr_latex}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.DIFFICULT, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT,
            dok=1,
            item_type=ItemType.NR,
            stem_text=stem_text,
            stem_latex=stem_latex_full,
            answer_text=answer_display,
            answer_latex=f"${answer_rn.latex()}$",
            worked_solution=worked,
            context_scenario="order of operations - exponents with fractions/decimals",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above Proficiency - MS (DOK 2, Easy)
    # Select multiple expressions equivalent to a given expression
    # (using distributive property)
    # ================================================================

    def stem5_approaching_ms(self, variant_idx: int) -> GeneratedQuestion:
        """Above Proficiency - Select equivalent expressions (multi-select).

        Given a(b + c), students select all equivalent expressions from a list.
        Tests understanding of the distributive property.
        Difficulty: easy (whole numbers)
        """
        gen, rng = self._make_gen(5, variant_idx)

        # Generate a distributive expression: a(b + c)
        a = int(gen.small_whole(2, 9))
        b = int(gen.small_whole(1, 12))
        c = int(gen.small_whole(1, 12))

        ab = a * b
        ac = a * c
        total = a * (b + c)
        b_plus_c = b + c

        # The given expression
        given_expr = f"{a} x ({b} + {c})"
        given_latex = f"${a} \\times ({b} + {c})$"

        # Correct equivalent expressions (2-3 correct)
        correct_exprs = []
        correct_exprs.append(f"{ab} + {ac}")                # a*b + a*c (distributive)
        correct_exprs.append(f"{a} x {b_plus_c}")           # a * (b+c) simplified
        # Potentially add commuted forms
        alt_correct = f"{ac} + {ab}"                         # commuted distributive
        if alt_correct not in correct_exprs:
            correct_exprs.append(alt_correct)

        # Wrong expressions (3-4 wrong)
        wrong_exprs = []
        wrong_exprs.append(f"{a} + {b} x {c}")              # common error: a + b*c
        wrong_exprs.append(f"{a} x {b} + {c}")              # forgot to distribute to c
        wrong_exprs.append(f"{a + b} x {c}")                # added a+b then multiplied c
        wrong_exprs.append(f"{ab} x {ac}")                   # multiplied instead of adding

        # Remove any accidental duplicates or collisions
        wrong_exprs = [w for w in wrong_exprs
                       if w not in correct_exprs and eval(w.replace("x", "*")) != total]

        # Ensure we have at least 3 wrong
        while len(wrong_exprs) < 3:
            extra = f"{a * b + c}"
            if extra not in correct_exprs and extra not in wrong_exprs:
                wrong_exprs.append(extra)
            else:
                extra = f"{a} + {b + c}"
                if extra not in correct_exprs and extra not in wrong_exprs:
                    wrong_exprs.append(extra)
                    break

        # Build 5-6 options: 2-3 correct, 3 wrong
        # Limit correct to 2 for cleaner question
        correct_use = correct_exprs[:2]
        wrong_use = wrong_exprs[:3]

        all_options = [(e, True) for e in correct_use] + [(e, False) for e in wrong_use]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i),
                text=text,
                text_latex=f"${text.replace('x', '\\\\times')}$",
                is_correct=is_correct,
            ))

        correct_letters = ", ".join(c.key for c in choices if c.is_correct)

        stem_text = (
            f"Select all expressions that are equivalent to {given_expr}."
        )

        worked = (
            f"Using the distributive property:\n"
            f"{given_expr} = {a} x {b} + {a} x {c} = {ab} + {ac}\n"
            f"Also equivalent: {a} x {b_plus_c} = {total}\n"
            f"Correct answers: {', '.join(correct_use)}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MS,
                               Difficulty.EASY, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY,
            dok=2,
            item_type=ItemType.MS,
            stem_text=stem_text,
            stem_latex=f"Select all expressions that are equivalent to {given_latex}.",
            answer_text=correct_letters,
            answer_latex=correct_letters,
            worked_solution=worked,
            choices=choices,
            context_scenario="equivalent expressions via distributive property",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5,
            variant_index=variant_idx
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    # ================================================================
    # STEM 6: Above Proficiency - NR (DOK 2, Difficult)
    # NEW. Above gained complex rational expressions: operations stacked in
    # BOTH the numerator and the denominator of a fraction, so the student must
    # finish each half before dividing.
    # ================================================================
    def stem6_above_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)

        # Build a denominator that divides the numerator exactly, so the answer
        # stays a whole number and the difficulty sits in the structure rather
        # than in messy division.
        for _ in range(40):
            base = rng.choice([2, 3, 4, 5])
            exp = rng.choice([2, 3])
            add = rng.randint(1, 9)
            mult = rng.randint(2, 4)
            numerator = (add + base ** exp) * mult

            d_a = rng.randint(6, 20)
            d_b = rng.randint(2, 5)
            d_c = rng.choice([2, 3, 4])
            if (d_a - d_b) % d_c:
                continue
            denominator = (d_a - d_b) // d_c
            if denominator <= 1 or numerator % denominator:
                continue
            break
        else:
            base, exp, add, mult = 3, 2, 1, 2
            numerator = (add + base ** exp) * mult
            d_a, d_b, d_c, denominator = 10, 4, 3, 2

        result = numerator // denominator

        stem_text = (
            f"Evaluate the expression.\n\n"
            f"[({add} + {base}^{exp}) x {mult}] / [({d_a} - {d_b}) / {d_c}]"
        )

        worked = (
            f"Work out the numerator and the denominator separately.\n"
            f"Numerator: ({add} + {base}^{exp}) x {mult} = "
            f"({add} + {base ** exp}) x {mult} = {add + base ** exp} x {mult} "
            f"= {numerator}\n"
            f"Denominator: ({d_a} - {d_b}) / {d_c} = {d_a - d_b} / {d_c} = {denominator}\n"
            f"Then divide: {numerator} / {denominator} = {result}"
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE,
                                         ItemType.NR, Difficulty.DIFFICULT, 6, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=str(result), answer_latex=str(result),
            worked_solution=worked,
            context_scenario="complex rational expression",
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6, variant_index=variant_idx,
        )

    # ================================================================
    # STEM 7: Above Proficiency - MC (DOK 3, Difficult)
    # NEW. "Place grouping symbols within a numerical expression to set it
    # equal to a given value." The student works backwards from the target
    # rather than evaluating left to right.
    # ================================================================
    def stem7_above_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(7, variant_idx)

        # 6.NS.5 is a positive-rational-numbers standard, so every placement
        # must stay positive: c > d keeps (c - d) above zero, and the guard
        # below rejects any draw where a placement still lands at or below it.
        def draw():
            a = rng.randint(2, 9)
            b = rng.randint(2, 9)
            d = rng.randint(2, 5)
            c = rng.randint(d + 1, 9)
            return a, b, c, d

        a, b, c, d = draw()
        for _ in range(40):
            vals = [(a + b) * c - d, a + b * (c - d), (a + b) * (c - d), a + (b * c - d)]
            if len(set(vals)) == 4 and all(v > 0 for v in vals):
                break
            a, b, c, d = draw()

        bare = f"{a} + {b} x {c} - {d}"
        # Four placements; each evaluates differently.
        forms = {
            f"({a} + {b}) x {c} - {d}": (a + b) * c - d,
            f"{a} + {b} x ({c} - {d})": a + b * (c - d),
            f"({a} + {b}) x ({c} - {d})": (a + b) * (c - d),
            f"{a} + ({b} x {c} - {d})": a + (b * c - d),
        }
        # Fall back to a known-good set if the search above ran out of tries:
        # four distinct positive values are required or more than one option
        # would be correct.
        if len(set(forms.values())) < 4 or any(v <= 0 for v in forms.values()):
            a, b, c, d = 3, 4, 7, 2
            bare = f"{a} + {b} x {c} - {d}"
            forms = {
                f"({a} + {b}) x {c} - {d}": (a + b) * c - d,
                f"{a} + {b} x ({c} - {d})": a + b * (c - d),
                f"({a} + {b}) x ({c} - {d})": (a + b) * (c - d),
                f"{a} + ({b} x {c} - {d})": a + (b * c - d),
            }

        target_expr = rng.choice(list(forms))
        target = forms[target_expr]

        options = []
        for expr, value in forms.items():
            if expr == target_expr:
                options.append((expr, True, None))
            else:
                options.append((expr, False,
                                f"Evaluates to {value}, not {target}"))
        rng.shuffle(options)
        choices = [QuestionChoice(key=chr(ord("a") + i), text=t, text_latex=t,
                                  is_correct=cr, distractor_rationale=r)
                   for i, (t, cr, r) in enumerate(options)]
        key = next(c.key for c in choices if c.is_correct).upper()

        stem_text = (
            f"An expression is given.\n\n{bare}\n\n"
            f"Where should parentheses be placed so that the expression "
            f"equals {target}?"
        )

        worked = (
            f"Try each placement and evaluate with the order of operations.\n"
            + "\n".join(f"{expr} = {value}" for expr, value in forms.items())
            + f"\nOnly {target_expr} equals {target}."
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE,
                                         ItemType.MC, Difficulty.DIFFICULT, 7, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{key}. {target_expr}", answer_latex=f"{key}. {target_expr}",
            worked_solution=worked, choices=choices,
            context_scenario="place grouping symbols to hit a target value",
            seed=self.base_seed * 1000 + 700 + variant_idx,
            stem_index=7, variant_index=variant_idx,
        )

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        """Generate all variants for all 5 stems.

        Returns ~100 questions (5 stems x 20 variants).
        """
        all_questions = []

        stem_methods = [
            self.stem1_below_nr,
            self.stem2_below_mc,
            self.stem3_approaching_mc,
            self.stem4_at_nr,
            self.stem5_approaching_ms,
            self.stem6_above_nr,
            self.stem7_above_mc,
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
        """Generate variants for a single stem (1-5)."""
        stem_methods = {
            1: self.stem1_below_nr,
            2: self.stem2_below_mc,
            3: self.stem3_approaching_mc,
            4: self.stem4_at_nr,
            5: self.stem5_approaching_ms,
            6: self.stem6_above_nr,
            7: self.stem7_above_mc,
        }

        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-5.")

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
    print("Generating 6.NS.5 question variants...")
    print("=" * 60)

    generator = Stem6NS5(seed=42)
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
