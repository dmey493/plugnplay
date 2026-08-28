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
  Stem 6 (Below-MP):    Evaluate both sides, then decide if a value is a solution (DOK 2, medium)
  Stem 7 (Approaching-MC): Solution set of an inequality, including the direction (DOK 2, medium)
"""

import random
from fractions import Fraction

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.models import (
    GeneratedQuestion, QuestionChoice, QuestionPart,
    Difficulty, ProficiencyLevel, ItemType,
    make_question_id
)
from engine.number_generators import NumberGenerator
from engine.stem_guards import distinct_choices
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

        # Real-world contexts that naturally produce two like terms in x
        # plus (add case) or minus (subtract case) a one-time constant.
        # Every context keeps the same roles:
        #   coeff1*x + coeff2*x +/- constant = total
        contexts = [
            # 1. Gym membership
            (f"{name} joins a gym that charges a one-time enrollment fee "
             f"and a monthly membership fee.\n"
             f"The enrollment fee is {coeff2} times the monthly fee.\n"
             f"{'New members receive a $' + str(constant) + ' discount on enrollment.' if is_subtract else 'There is a $' + str(constant) + ' registration fee.'}\n\n"
             f"{name} pays the enrollment fee plus {coeff1} months of membership "
             f"for a total of ${total}."),
            # 2. Two part-time jobs
            (f"{name} works two part-time jobs that pay the same hourly rate.\n"
             f"Last week, {name} worked {coeff1} hours at the first job "
             f"and {coeff2} hours at the second job.\n"
             f"{'After deducting $' + str(constant) + ' for transportation, ' + name + ' earned' if is_subtract else name + ' also received a $' + str(constant) + ' bonus, earning'} "
             f"${total} total."),
            # 3. School supply order
            (f"A school is ordering supplies. They order {coeff1} boxes of notebooks "
             f"and {coeff2} boxes of folders.\n"
             f"Each box of notebooks costs the same as each box of folders.\n"
             f"{'Shipping is $' + str(constant) + ' and' + ' the' if not is_subtract else 'A $' + str(constant) + ' coupon is applied and the'} "
             f"total {'cost is' if not is_subtract else 'amount paid is'} ${total}."),
            # 4. Streaming subscriptions
            (f"{name}'s family pays for a video streaming service for {coeff1} months "
             f"and a music streaming service for {coeff2} months.\n"
             f"Both services cost the same amount per month.\n"
             f"{'A promo code takes $' + str(constant) + ' off the bill.' if is_subtract else 'A one-time signup fee of $' + str(constant) + ' is added to the bill.'}\n\n"
             f"The family pays ${total} in all."),
            # 5. Car wash fundraiser
            (f"The student council holds a car wash fundraiser.\n"
             f"They wash {coeff1} cars in the morning and {coeff2} cars in the "
             f"afternoon, charging the same price for each car.\n"
             f"{'After paying $' + str(constant) + ' for soap and supplies, they have' if is_subtract else 'A local business donates an extra $' + str(constant) + ', bringing the total to'} "
             f"${total}."),
            # 6. Ticket sales
            (f"The drama club sells tickets to its spring play. "
             f"All tickets are the same price.\n"
             f"The club sells {coeff1} tickets on Friday and {coeff2} tickets "
             f"on Saturday.\n"
             f"{'After paying $' + str(constant) + ' to print programs, the club has' if is_subtract else 'The club also receives a $' + str(constant) + ' donation, collecting'} "
             f"${total} in all."),
            # 7. Lawn mowing earnings
            (f"{name} mows lawns and charges the same amount for each lawn.\n"
             f"{name} mowed {coeff1} lawns last week and {coeff2} lawns this week.\n"
             f"{'After spending $' + str(constant) + ' on gas, ' + name + ' has' if is_subtract else 'One customer also gave a $' + str(constant) + ' tip, so ' + name + ' earned'} "
             f"${total}."),
            # 8. T-shirt order
            (f"A coach orders {coeff1} T-shirts for the soccer team and "
             f"{coeff2} T-shirts for the track team.\n"
             f"Every shirt costs the same.\n"
             f"{'The coach uses a $' + str(constant) + ' coupon, paying' if is_subtract else 'The shop adds a one-time $' + str(constant) + ' printing fee, making the total'} "
             f"${total}."),
            # 9. Book fair
            (f"At the book fair, {name} buys {coeff1} mystery books and "
             f"{coeff2} graphic novels.\n"
             f"Every book costs the same.\n"
             f"{name} {'uses a $' + str(constant) + ' gift card and pays' if is_subtract else 'also buys a poster for $' + str(constant) + ', spending'} "
             f"${total} in all."),
            # 10. Field trip admission
            (f"A museum charges the same admission price for each student.\n"
             f"A field trip includes {coeff1} students from one class and "
             f"{coeff2} students from another class.\n"
             f"{'The museum takes $' + str(constant) + ' off the bill as a school discount, so the school pays' if is_subtract else 'The school also pays a $' + str(constant) + ' parking fee, for a total of'} "
             f"${total}."),
        ]
        # Spread scenarios evenly across the variant bank: each consecutive
        # block of len(contexts) variants covers every context exactly once,
        # in a seed-dependent shuffled order.
        n_ctx = len(contexts)
        block, pos = divmod(variant_idx, n_ctx)
        order = random.Random(f"{self.base_seed}-4-{block}").sample(range(n_ctx), n_ctx)
        ctx = contexts[order[pos]]

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

        # Every scenario keeps the same equation form:
        #   factor*x - discount + months*x = total
        # i.e. an upfront fee worth `factor` units of x, minus a one-time
        # discount on that fee, plus `months` more units of x.
        factor = Fraction(rng.randint(2, 5))
        months = Fraction(rng.randint(3, 8))
        x_val = Fraction(rng.randint(10, 50))  # the per-unit price/rate
        # Keep the discount smaller than the upfront fee so the story is sensible.
        discount = Fraction(rng.randint(5, min(25, int(factor * x_val) - 5)))
        total = (factor + months) * x_val - discount

        f_i, m_i, d_i = int(factor), int(months), int(discount)
        t_i, x_i = int(total), int(x_val)

        # Varied real-world scenarios; each maps the same roles onto the
        # equation (upfront fee = factor*x, discount, months more units).
        contexts = [
            {
                "intro": (f"{name} joins a fitness center.\n"
                          f"The enrollment fee is {f_i} times the monthly fee.\n"
                          f"New members receive a ${d_i} discount on their enrollment fee.\n"
                          f"{name} pays the discounted enrollment fee plus {m_i} months "
                          f"of membership for a total of ${t_i}."),
                "x_desc": "the monthly fee",
                "part_b": "How much is the monthly fee?",
                "meaning": f"The monthly membership fee is ${x_i} per month.",
            },
            {
                "intro": (f"{name} signs up for a new cell phone plan.\n"
                          f"The activation fee is {f_i} times the monthly plan price.\n"
                          f"New customers get a ${d_i} credit toward the activation fee.\n"
                          f"{name} pays the discounted activation fee plus {m_i} months "
                          f"of service for a total of ${t_i}."),
                "x_desc": "the monthly plan price",
                "part_b": "How much does the phone plan cost per month?",
                "meaning": f"The phone plan costs ${x_i} per month.",
            },
            {
                "intro": (f"{name} enrolls at a karate studio.\n"
                          f"The registration fee is {f_i} times the monthly tuition.\n"
                          f"New students receive a ${d_i} discount on registration.\n"
                          f"{name} pays the discounted registration fee plus {m_i} months "
                          f"of classes for a total of ${t_i}."),
                "x_desc": "the monthly tuition",
                "part_b": "How much is the monthly tuition?",
                "meaning": f"The karate tuition is ${x_i} per month.",
            },
            {
                "intro": (f"{name} signs up for guitar lessons.\n"
                          f"The sign-up fee is {f_i} times the price of one lesson.\n"
                          f"{name} has a coupon for ${d_i} off the sign-up fee.\n"
                          f"{name} pays the discounted sign-up fee plus {m_i} lessons "
                          f"for a total of ${t_i}."),
                "x_desc": "the price of one lesson",
                "part_b": "How much does one lesson cost?",
                "meaning": f"Each guitar lesson costs ${x_i}.",
            },
            {
                "intro": (f"A club orders custom T-shirts from a print shop.\n"
                          f"The one-time design fee is {f_i} times the price of one shirt.\n"
                          f"The shop takes ${d_i} off the design fee for school clubs.\n"
                          f"The club pays the discounted design fee plus {m_i} shirts "
                          f"for a total of ${t_i}."),
                "x_desc": "the price of one shirt",
                "part_b": "How much does one shirt cost?",
                "meaning": f"Each T-shirt costs ${x_i}.",
            },
            {
                "intro": (f"{name} rents a kayak at a lake.\n"
                          f"The equipment deposit is {f_i} times the hourly rental rate.\n"
                          f"{name} uses a ${d_i} coupon on the deposit.\n"
                          f"{name} pays the discounted deposit plus {m_i} hours of "
                          f"rental time for a total of ${t_i}."),
                "x_desc": "the hourly rental rate",
                "part_b": "How much does the kayak rental cost per hour?",
                "meaning": f"The kayak rental costs ${x_i} per hour.",
            },
            {
                "intro": (f"{name} signs up for a summer coding camp.\n"
                          f"The registration fee is {f_i} times the weekly fee.\n"
                          f"Campers who sign up early get ${d_i} off registration.\n"
                          f"{name} pays the discounted registration fee plus {m_i} weeks "
                          f"of camp for a total of ${t_i}."),
                "x_desc": "the weekly fee",
                "part_b": "How much does the camp cost per week?",
                "meaning": f"The camp costs ${x_i} per week.",
            },
            {
                "intro": (f"{name}'s family joins a community pool.\n"
                          f"The joining fee is {f_i} times the price of a monthly pass.\n"
                          f"Families with students get ${d_i} off the joining fee.\n"
                          f"The family pays the discounted joining fee plus {m_i} months "
                          f"of passes for a total of ${t_i}."),
                "x_desc": "the price of a monthly pass",
                "part_b": "How much does a monthly pool pass cost?",
                "meaning": f"A monthly pool pass costs ${x_i}.",
            },
        ]
        # Spread scenarios evenly across the variant bank: each consecutive
        # block of len(contexts) variants covers every context exactly once,
        # in a seed-dependent shuffled order.
        n_ctx = len(contexts)
        block, pos = divmod(variant_idx, n_ctx)
        order = random.Random(f"{self.base_seed}-5-{block}").sample(range(n_ctx), n_ctx)
        ctx = contexts[order[pos]]

        stem_text = (
            f"{ctx['intro']}\n\n"
            f"Part A: Write an equation to represent the situation. "
            f"Use x to represent {ctx['x_desc']}.\n\n"
            f"Part B: {ctx['part_b']}\n\n"
            f"Part C: Explain what your answer means in the context of the problem."
        )

        equation = f"{f_i}x - {d_i} + {m_i}x = {t_i}"
        combined = factor + months

        part_a = QuestionPart(
            label="Part A",
            prompt=f"Write an equation to represent the situation. Use x to represent {ctx['x_desc']}.",
            prompt_latex=f"Write an equation to represent the situation. Use x to represent {ctx['x_desc']}.",
            answer=equation,
            answer_latex=equation,
            item_type=ItemType.EQ,
        )

        part_b = QuestionPart(
            label="Part B",
            prompt=ctx["part_b"],
            prompt_latex=ctx["part_b"],
            answer=f"${x_i}",
            answer_latex=f"${x_i}",
            item_type=ItemType.NR,
        )

        part_c = QuestionPart(
            label="Part C",
            prompt="Explain what your answer means.",
            prompt_latex="Explain what your answer means.",
            answer=ctx["meaning"],
            answer_latex=ctx["meaning"],
            item_type=ItemType.ER,
        )

        worked = (
            f"Part A: {equation}\n"
            f"Part B:\n"
            f"Combine like terms: {_fmt(combined)}x - {d_i} = {t_i}\n"
            f"{_fmt(combined)}x = {int(total + discount)}\n"
            f"x = {_fmt(x_val)}\n"
            f"Part C: {ctx['meaning']}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.MEDIUM, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.MEDIUM, dok=3, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"Part A: {equation}; Part B: ${x_i}; Part C: {ctx['meaning']}",
            answer_latex=f"Part A: {equation}; Part B: ${x_i}; Part C: {ctx['meaning']}",
            worked_solution=worked, parts=[part_a, part_b, part_c],
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    # MAIN GENERATION METHOD
    # ================================================================

    # ================================================================
    # STEM 6: Below Proficiency - MP (DOK 2, Medium)
    # NEW. The revision's Below item asks for the value of each side before the
    # conclusion, so a student cannot guess from the shape of the equation.
    # ================================================================
    def stem6_below_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)

        # Left side is a constant expression; right side is linear in x.
        p = rng.randint(2, 9)
        q = rng.randint(2, 9)
        left_value = p * q

        coeff = rng.choice([2, 4, 5, 10])
        test_value = rng.randint(2, 12)
        # Half the time the value really is a solution.
        is_solution = rng.random() < 0.5
        if is_solution:
            constant = left_value - coeff * test_value
        else:
            offset = rng.choice([-12, -8, -6, 6, 8, 12])
            constant = left_value - coeff * test_value + offset
        right_value = coeff * test_value + constant

        scale = rng.choice([Fraction(1, 2), Fraction(1, 1)])
        if scale == Fraction(1, 2) and (coeff % 2 or constant % 2):
            scale = Fraction(1, 1)

        if scale == Fraction(1, 2):
            right_text = f"0.5({coeff * 2}x + {constant * 2})"
        else:
            right_text = f"{coeff}x + {constant}" if constant >= 0 else \
                         f"{coeff}x - {abs(constant)}"

        equation = f"{p}({q * 1}) = {right_text}" if False else \
                   f"{p} x {q} = {right_text}"

        stem_text = (
            f"An equation is given.\n\n  {equation}\n\n"
            f"Complete the sentences to explain whether {test_value} is a "
            f"solution to the equation.\n\n"
            f"Part A: The value of the left side is ______.\n\n"
            f"Part B: The value of the right side when x = {test_value} is ______."
        )

        verdict = "is" if is_solution else "is not"
        part_a = QuestionPart(
            label="Part A", prompt="The value of the left side is",
            prompt_latex="The value of the left side is",
            answer=str(left_value), answer_latex=str(left_value),
            item_type=ItemType.NR,
        )
        part_b = QuestionPart(
            label="Part B",
            prompt=f"The value of the right side when x = {test_value} is",
            prompt_latex=f"The value of the right side when x = {test_value} is",
            answer=str(right_value), answer_latex=str(right_value),
            item_type=ItemType.NR,
        )

        worked = (
            f"Left side: {p} x {q} = {left_value}\n"
            f"Right side at x = {test_value}: {coeff} x {test_value} "
            f"{'+' if constant >= 0 else '-'} {abs(constant)} = {right_value}\n"
            f"The two sides are {'equal' if is_solution else 'not equal'}, so "
            f"{test_value} {verdict} a solution."
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW,
                                         ItemType.MP, Difficulty.MEDIUM, 6, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=(f"Part A: {left_value}; Part B: {right_value}; "
                         f"{test_value} {verdict} a solution"),
            answer_latex=(f"Part A: {left_value}; Part B: {right_value}; "
                          f"{test_value} {verdict} a solution"),
            worked_solution=worked, parts=[part_a, part_b],
            context_scenario="evaluate both sides then conclude",
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6, variant_index=variant_idx,
        )

    # ================================================================
    # STEM 7: Approaching Proficiency - MC (DOK 2, Medium)
    # NEW. Replaces the retired free-response fraction inequality with the
    # dropdown format the revision introduced. Dividing by a negative reverses
    # the symbol, so the direction is what the item is really testing and the
    # distractors are the three other symbol-and-value pairings.
    # ================================================================
    @distinct_choices
    def stem7_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(7, variant_idx)

        coeff = rng.choice([-6, -5, -4, -3, -2, 2, 3, 4, 5, 6])
        solution = rng.randint(-8, 8)
        constant = rng.randint(-12, 12)
        rhs = coeff * solution + constant
        # When the solution equals the right-hand side, the "forgot to divide"
        # distractor becomes the correct answer and the item ships duplicates.
        tries = 0
        while solution == rhs and tries < 30:
            tries += 1
            solution = rng.randint(-8, 8)
            constant = rng.randint(-12, 12)
            rhs = coeff * solution + constant
        symbol = rng.choice([">", "<"])

        # Dividing by a negative coefficient flips the symbol.
        result_symbol = symbol
        if coeff < 0:
            result_symbol = "<" if symbol == ">" else ">"

        const_text = f"+ {constant}" if constant >= 0 else f"- {abs(constant)}"
        inequality = f"{coeff}x {const_text} {symbol} {rhs}"
        correct = f"x {result_symbol} {solution}"

        flipped = "<" if result_symbol == ">" else ">"
        options = [
            (correct, True, None),
            (f"x {flipped} {solution}", False,
             "Keeps the symbol the same after dividing by a negative"
             if coeff < 0 else "Reverses the symbol when the coefficient is positive"),
            (f"x {result_symbol} {rhs}", False,
             "Uses the right-hand side without dividing by the coefficient"),
            (f"x {flipped} {rhs}", False,
             "Both errors together: no division and the wrong direction"),
        ]
        rng.shuffle(options)
        choices = [QuestionChoice(key=chr(ord("a") + i), text=t, text_latex=t,
                                  is_correct=c, distractor_rationale=r)
                   for i, (t, c, r) in enumerate(options)]
        key = next(c.key for c in choices if c.is_correct).upper()

        stem_text = (
            f"An inequality is given.\n\n  {inequality}\n\n"
            f"Which statement shows the solution set?"
        )
        worked = (
            f"Subtract {constant} from both sides: {coeff}x {symbol} "
            f"{rhs - constant}\n"
            f"Divide both sides by {coeff}"
            + (f". Dividing by a negative reverses the symbol.\n"
               if coeff < 0 else ".\n")
            + f"{correct}"
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING,
                                         ItemType.MC, Difficulty.MEDIUM, 7, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{key}. {correct}", answer_latex=f"{key}. {correct}",
            worked_solution=worked, choices=choices,
            context_scenario="solution set with the inequality direction",
            seed=self.base_seed * 1000 + 700 + variant_idx,
            stem_index=7, variant_index=variant_idx,
        )

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_approaching_mc,
            self.stem3_approaching_mc,
            self.stem4_at_mp,
            self.stem5_above_mp,
            self.stem6_below_mp,
            self.stem7_approaching_mc,
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
            6: self.stem6_below_mp,
            7: self.stem7_approaching_mc,
        }
        fn = stem_methods[stem_index]
        return [fn(v) for v in range(variants_per_stem)]
