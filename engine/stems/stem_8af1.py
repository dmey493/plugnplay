"""
Stem generator for 8.AF.1:
  Solve linear equations and inequalities with rational number coefficients
  fluently, including those whose solutions require expanding expressions
  using the distributive property and collecting like terms.

Content Limits:
  - All rational numbers; common fractions; decimals to hundredths
  - Variables on one side only
  - Distributive property may be used one or more times
  - Calculator: ALLOWED

5 Stems:
  Stem 1 (Below-MC):        Is a given value a solution? (DOK 1, Easy)
  Stem 2 (Approaching-MC):  Solve multi-step equation (DOK 2, Easy)
  Stem 3 (Approaching-MC):  Solve inequality with fractions (DOK 2, Medium)
  Stem 4 (At-MP):           Real-world: write equation + solve (DOK 2, Medium)
  Stem 5 (Above-MP):        Real-world: write + solve + explain (DOK 3, Medium)
"""

import random
from fractions import Fraction

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.models import (
    GeneratedQuestion, QuestionPart,
    Difficulty, ProficiencyLevel, ItemType,
    make_question_id
)
from engine.number_generators import NumberGenerator
from engine.distractor_engine import shuffle_choices
from engine.context_pools import pick_name


STANDARD_CODE = "8.AF.1"
VARIANTS_PER_STEM = 20


def _fmt(val: Fraction) -> str:
    """Format a number for display."""
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


def _fmt_eq_term(coeff: Fraction, var: str, first: bool = False) -> str:
    """Format a term like 3x or -2x for equation display."""
    if coeff == 0:
        return ""
    sign = ""
    if coeff > 0 and not first:
        sign = " + "
    elif coeff < 0:
        sign = " - " if not first else "-"
        coeff = abs(coeff)

    if coeff == 1:
        return f"{sign}{var}"
    elif coeff.denominator == 1:
        return f"{sign}{int(coeff)}{var}"
    else:
        return f"{sign}{coeff.numerator}/{coeff.denominator}{var}"


def _fmt_const(val: Fraction, first: bool = False) -> str:
    """Format a constant term."""
    if val == 0:
        return ""
    sign = ""
    if val > 0 and not first:
        sign = " + "
    elif val < 0:
        sign = " - " if not first else "-"
        val = abs(val)
    if val.denominator == 1:
        return f"{sign}{int(val)}"
    return f"{sign}{_fmt(val)}"


class Stem8AF1:
    """Generates 20 variants for each of 5 stems from the 8.AF.1 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 1, Easy)
    # Is a given value a solution to an equation?
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Below - Determine if a given value is a solution to an equation."""
        gen, rng = self._make_gen(1, variant_idx)

        a, b, c, d, e, x = gen.multi_step_equation("easy")

        # The equation: a(bx + c) + dx = e
        # Format it nicely
        inner = f"{_fmt_eq_term(b, 'x', first=True)}{_fmt_const(c)}"
        eq_str = f"{_fmt(a)}({inner}){_fmt_eq_term(d, 'x')} = {_fmt(e)}"

        # 50% chance we test the correct solution, 50% a wrong one
        is_correct_test = rng.random() < 0.5
        if is_correct_test:
            test_val = x
        else:
            test_val = x + rng.choice([-2, -1, 1, 2, 3])

        test_int = int(test_val)
        # Evaluate LHS with test value
        lhs_val = a * (b * test_val + c) + d * test_val
        is_solution = (lhs_val == e)

        if is_solution:
            correct = f"{test_int} is a solution because both sides equal {_fmt(e)}"
            distractors = [
                f"{test_int} is not a solution",
                f"{test_int} is a solution because {_fmt(lhs_val + 1)} = {_fmt(e)}",
                f"Cannot be determined",
            ]
        else:
            correct = f"{test_int} is not a solution because {_fmt(lhs_val)} does not equal {_fmt(e)}"
            distractors = [
                f"{test_int} is a solution",
                f"{test_int} is a solution because {_fmt(e)} = {_fmt(e)}",
                f"Cannot be determined",
            ]

        stem_text = (
            f"An equation is given.\n\n"
            f"{eq_str}\n\n"
            f"Determine if {test_int} is a solution to the equation."
        )

        choices = shuffle_choices(correct, correct, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"Substitute x = {test_int} into the equation:\n"
            f"{_fmt(a)}({_fmt(b)}({test_int}) + {_fmt(c)}) + {_fmt(d)}({test_int})\n"
            f"= {_fmt(a)}({_fmt(b * test_val + c)}) + {_fmt(d * test_val)}\n"
            f"= {_fmt(a * (b * test_val + c))} + {_fmt(d * test_val)}\n"
            f"= {_fmt(lhs_val)}\n"
            f"Since {_fmt(lhs_val)} {'=' if is_solution else '!='} {_fmt(e)}, "
            f"{test_int} {'is' if is_solution else 'is not'} a solution."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct}",
            answer_latex=f"{correct_letter}) {correct}",
            worked_solution=worked, choices=choices,
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - MC (DOK 2, Easy)
    # Solve a multi-step equation with distribution (integers).
    # ================================================================

    def stem2_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Approaching - Solve multi-step equation with distribution."""
        gen, rng = self._make_gen(2, variant_idx)

        a, b, c, d, e, x = gen.multi_step_equation("easy")

        # Format: a(bx + c) + dx = e
        inner = f"{_fmt_eq_term(b, 'x', first=True)}{_fmt_const(c)}"
        eq_str = f"{_fmt(a)}({inner}){_fmt_eq_term(d, 'x')} = {_fmt(e)}"

        correct = _fmt(x)

        # Distractors: common errors
        distractors = []
        # Sign error
        if -x != x:
            distractors.append(_fmt(-x))
        # Forgot to distribute to c
        wrong1 = a * b * x + c + d * x
        if wrong1 != 0:
            wrong_x1 = (e - c) / (a * b + d) if (a * b + d) != 0 else x + 1
        else:
            wrong_x1 = x + 1
        if wrong_x1 != x and wrong_x1.denominator == 1:
            distractors.append(_fmt(wrong_x1))
        # Off by 1
        distractors.append(_fmt(x + 1))
        distractors.append(_fmt(x - 1))

        # Ensure we have exactly 3 unique distractors
        seen = {correct}
        unique = []
        for d_val in distractors:
            if d_val not in seen:
                seen.add(d_val)
                unique.append(d_val)
        while len(unique) < 3:
            offset = rng.choice([-3, -2, 2, 3, 4])
            candidate = _fmt(x + offset)
            if candidate not in seen:
                seen.add(candidate)
                unique.append(candidate)
        distractors = unique[:3]

        stem_text = f"Solve.\n\n{eq_str}"

        choices = shuffle_choices(correct, correct, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        ab = a * b
        ac = a * c
        combined_coeff = ab + d
        combined_const = ac
        rhs_minus_const = e - combined_const

        worked = (
            f"Distribute: {_fmt(ab)}x{_fmt_const(ac)}{_fmt_eq_term(d, 'x')} = {_fmt(e)}\n"
            f"Combine like terms: {_fmt(combined_coeff)}x{_fmt_const(ac)} = {_fmt(e)}\n"
            f"Subtract {_fmt(ac)}: {_fmt(combined_coeff)}x = {_fmt(rhs_minus_const)}\n"
            f"Divide by {_fmt(combined_coeff)}: x = {_fmt(x)}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{correct_letter}) x = {correct}",
            answer_latex=f"{correct_letter}) x = {correct}",
            worked_solution=worked, choices=choices,
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - MC (DOK 2, Medium)
    # Solve inequality with fractions.
    # ================================================================

    def stem3_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Approaching - Solve inequality with fractional coefficients."""
        gen, rng = self._make_gen(3, variant_idx)

        # Generate: (a/b)x + (c/d)x + e < f  or similar
        # Pick two fraction coefficients that sum to a clean fraction
        d1 = rng.choice([2, 3, 4, 6])
        d2 = rng.choice([2, 3, 4, 6])
        n1 = rng.randint(1, d1 - 1)
        n2 = rng.randint(1, d2 - 1)
        coeff1 = Fraction(n1, d1)
        coeff2 = Fraction(n2, d2)
        total_coeff = coeff1 + coeff2

        # Pick a clean boundary for x
        # x_boundary = (rhs - const) / total_coeff should be clean
        const = Fraction(rng.randint(-5, 5))
        x_boundary = Fraction(rng.randint(-8, 8))
        while x_boundary == 0:
            x_boundary = Fraction(rng.randint(-8, 8))
        rhs = total_coeff * x_boundary + const

        op = rng.choice(["<", ">", "<=", ">="])
        eq_str = f"{_fmt(coeff1)}x + {_fmt(coeff2)}x{_fmt_const(const)} {op} {_fmt(rhs)}"

        correct = f"x {op} {_fmt(x_boundary)}"

        # Distractors
        opposite_op = {"<": ">", ">": "<", "<=": ">=", ">=": "<="}[op]
        distractors = [
            f"x {opposite_op} {_fmt(x_boundary)}",
            f"x {op} {_fmt(-x_boundary)}",
        ]
        # Wrong coefficient combination
        wrong_coeff = coeff1 * coeff2
        if wrong_coeff != 0:
            wrong_bound = (rhs - const) / wrong_coeff
            if wrong_bound != x_boundary:
                distractors.append(f"x {op} {_fmt(wrong_bound)}")

        seen = {correct}
        unique = []
        for d_val in distractors:
            if d_val not in seen:
                seen.add(d_val)
                unique.append(d_val)
        while len(unique) < 3:
            offset = rng.choice([-3, -2, 2, 3])
            candidate = f"x {op} {_fmt(x_boundary + offset)}"
            if candidate not in seen:
                seen.add(candidate)
                unique.append(candidate)
        distractors = unique[:3]

        stem_text = f"Solve.\n\n{eq_str}"

        choices = shuffle_choices(correct, correct, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"Combine like terms: ({_fmt(coeff1)} + {_fmt(coeff2)})x{_fmt_const(const)} {op} {_fmt(rhs)}\n"
            f"{_fmt(total_coeff)}x{_fmt_const(const)} {op} {_fmt(rhs)}\n"
            f"{_fmt(total_coeff)}x {op} {_fmt(rhs - const)}\n"
            f"x {op} {_fmt(x_boundary)}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct}",
            answer_latex=f"{correct_letter}) {correct}",
            worked_solution=worked, choices=choices,
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At Proficiency - MP (DOK 2, Medium)
    # Real-world: write equation with like terms + solve.
    # Equation form: ax + bx + c = total (requires combining like terms)
    # ================================================================

    def stem4_at_mp(self, variant_idx: int) -> GeneratedQuestion:
        """At Proficiency - Real-world equation requiring combining like terms."""
        gen, rng = self._make_gen(4, variant_idx)
        name = pick_name(rng)

        # Generate equation of form: coeff1*x + coeff2*x +/- constant = total
        # where x is the unknown monthly fee / hourly rate / unit price
        coeff1 = rng.randint(2, 6)   # e.g. months of membership
        coeff2 = rng.randint(2, 5)   # e.g. enrollment fee multiplier
        constant = rng.randint(5, 30) # e.g. discount or bonus
        x_val = rng.randint(8, 40)    # the unit value (monthly fee, etc.)

        # Randomly choose add or subtract the constant
        is_subtract = rng.random() < 0.5

        combined = coeff1 + coeff2
        if is_subtract:
            total = combined * x_val - constant
            const_sign = "-"
        else:
            total = combined * x_val + constant
            const_sign = "+"

        # Real-world contexts that naturally produce two variable terms
        contexts = [
            (f"{name} joins a gym that charges a one-time enrollment fee "
             f"and a monthly membership fee.\n"
             f"The enrollment fee is {coeff2} times the monthly fee.\n"
             f"{'New members receive a $' + str(constant) + ' discount on enrollment.' if is_subtract else 'There is a $' + str(constant) + ' registration fee.'}\n\n"
             f"{name} pays the enrollment fee plus {coeff1} months of membership "
             f"for a total of ${total}."),
            (f"{name} works two part-time jobs that pay the same hourly rate.\n"
             f"Last week, {name} worked {coeff1} hours at the first job "
             f"and {coeff2} hours at the second job.\n"
             f"{'After deducting $' + str(constant) + ' for transportation, ' + name + ' earned' if is_subtract else name + ' also received a $' + str(constant) + ' bonus, earning'} "
             f"${total} total."),
            (f"A school is ordering supplies. They order {coeff1} boxes of notebooks "
             f"and {coeff2} boxes of folders.\n"
             f"Each box of notebooks costs the same as each box of folders.\n"
             f"{'Shipping is $' + str(constant) + ' and' + ' the' if not is_subtract else 'A $' + str(constant) + ' coupon is applied and the'} "
             f"total {'cost is' if not is_subtract else 'amount paid is'} ${total}."),
        ]
        ctx = rng.choice(contexts)

        stem_text = (
            f"{ctx}\n\n"
            f"Part A: Write an equation to represent the situation. Use x for the unknown.\n\n"
            f"Part B: Solve the equation."
        )

        equation = f"{coeff1}x + {coeff2}x {const_sign} {constant} = {total}"
        answer_str = str(x_val)

        part_a = QuestionPart(
            label="Part A",
            prompt="Write an equation to represent the situation. Use x for the unknown.",
            prompt_latex="Write an equation to represent the situation. Use x for the unknown.",
            answer=equation,
            answer_latex=equation,
            item_type=ItemType.EQ,
        )

        part_b = QuestionPart(
            label="Part B",
            prompt="Solve the equation.",
            prompt_latex="Solve the equation.",
            answer=f"x = {answer_str}",
            answer_latex=f"x = {answer_str}",
            item_type=ItemType.NR,
        )

        if is_subtract:
            rhs_after_const = total + constant
        else:
            rhs_after_const = total - constant

        worked = (
            f"Part A: {equation}\n"
            f"Part B:\n"
            f"Combine like terms: {combined}x {const_sign} {constant} = {total}\n"
            f"{'Add' if is_subtract else 'Subtract'} {constant}: {combined}x = {rhs_after_const}\n"
            f"Divide by {combined}: x = {answer_str}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MP,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"Part A: {equation}; Part B: x = {answer_str}",
            answer_latex=f"Part A: {equation}; Part B: x = {answer_str}",
            worked_solution=worked, parts=[part_a, part_b],
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above Proficiency - MP (DOK 3, Medium)
    # Real-world: write + solve + explain in context.
    # ================================================================

    def stem5_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        """Above - Real-world with distribution: write, solve, explain."""
        gen, rng = self._make_gen(5, variant_idx)

        name = pick_name(rng)

        # Scenario: "{name} buys {n} items at ${price} each. There's a ${discount}
        # off the total. Tax of ${tax_rate} is added. The final cost is ${final}."
        # Equation: n * price - discount + tax_rate * (n * price - discount) = final
        # Simpler: a(x + b) + cx = total, where a is a multiplier

        # Use: enrollment_fee = factor * monthly_fee
        # Equation: factor*x - discount + months*x = total
        # i.e. (factor + months)*x - discount = total
        factor = Fraction(rng.randint(2, 5))
        months = Fraction(rng.randint(3, 8))
        discount = Fraction(rng.randint(5, 25))
        x_val = Fraction(rng.randint(10, 50))  # monthly fee
        total = (factor + months) * x_val - discount

        stem_text = (
            f"{name} joins a fitness center.\n"
            f"The enrollment fee is {int(factor)} times the monthly fee.\n"
            f"New members receive a ${int(discount)} discount on their enrollment fee.\n"
            f"{name} pays the discounted enrollment fee plus {int(months)} months "
            f"of membership for a total of ${int(total)}.\n\n"
            f"Part A: Write an equation to represent the situation. "
            f"Use x to represent the monthly fee.\n\n"
            f"Part B: How much is the monthly fee?\n\n"
            f"Part C: Explain what your answer means in the context of the problem."
        )

        equation = f"{int(factor)}x - {int(discount)} + {int(months)}x = {int(total)}"
        combined = factor + months

        part_a = QuestionPart(
            label="Part A",
            prompt="Write an equation to represent the situation.",
            prompt_latex="Write an equation to represent the situation.",
            answer=equation,
            answer_latex=equation,
            item_type=ItemType.EQ,
        )

        part_b = QuestionPart(
            label="Part B",
            prompt="How much is the monthly fee?",
            prompt_latex="How much is the monthly fee?",
            answer=f"${int(x_val)}",
            answer_latex=f"${int(x_val)}",
            item_type=ItemType.NR,
        )

        part_c = QuestionPart(
            label="Part C",
            prompt="Explain what your answer means.",
            prompt_latex="Explain what your answer means.",
            answer=f"The monthly membership fee is ${int(x_val)} per month.",
            answer_latex=f"The monthly membership fee is ${int(x_val)} per month.",
            item_type=ItemType.ER,
        )

        worked = (
            f"Part A: {equation}\n"
            f"Part B:\n"
            f"Combine like terms: {_fmt(combined)}x - {int(discount)} = {int(total)}\n"
            f"{_fmt(combined)}x = {int(total + discount)}\n"
            f"x = {_fmt(x_val)}\n"
            f"Part C: The monthly fee is ${int(x_val)}."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.MEDIUM, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.MEDIUM, dok=3, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"Part A: {equation}; Part B: ${int(x_val)}; Part C: Monthly fee is ${int(x_val)}",
            answer_latex=f"Part A: {equation}; Part B: ${int(x_val)}; Part C: Monthly fee is ${int(x_val)}",
            worked_solution=worked, parts=[part_a, part_b, part_c],
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    # MAIN GENERATION METHOD
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_approaching_mc,
            self.stem3_approaching_mc,
            self.stem4_at_mp,
            self.stem5_above_mp,
        ]
        for stem_fn in stem_methods:
            for v in range(variants_per_stem):
                all_questions.append(stem_fn(v))
        return all_questions

    def generate_stem_variants(self, stem_index: int,
                               variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        stem_methods = {
            1: self.stem1_below_mc,
            2: self.stem2_approaching_mc,
            3: self.stem3_approaching_mc,
            4: self.stem4_at_mp,
            5: self.stem5_above_mp,
        }
        fn = stem_methods[stem_index]
        return [fn(v) for v in range(variants_per_stem)]
