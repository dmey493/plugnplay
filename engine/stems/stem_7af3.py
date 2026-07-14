"""
Stem generator for 7.AF.3:
  Solve equations of the form px + q = r and p(x + q) = r fluently,
  where p, q, and r are specific rational numbers. Represent real-world
  problems using equations of these forms and solve such problems.

Content Limits:
  - Rational numbers only
  - Decimals to the hundredths place
  - Real-world context OR purely mathematical
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: integer values only
  Medium: one fraction or decimal number
  Difficult: more than one fraction or decimal number

6 Stems from the Item Spec:
  Stem 1 (Below-MC):      Solve px + q = r with integers (DOK 2, Easy)
  Stem 2 (Approaching-NR): Solve p(x + q) = r with one decimal (DOK 2, Medium)
  Stem 3 (Approaching-MC): Which equation models a real-world situation? (DOK 2, Easy)
  Stem 4 (At-MP):         Real-world: Part A write equation, Part B solve (DOK 2, Easy)
  Stem 5 (At-MP):         Real-world with decimals: Part A + Part B (DOK 2, Medium)
  Stem 6 (Above-MS):      Select TWO equations modeling a situation (DOK 2, Easy)
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
from engine.context_pools import (
    CONTEXTS_7AF3_PX_PLUS_Q, CONTEXTS_7AF3_PAREN, CONTEXTS_7AF3_SUB, pick_name
)


STANDARD_CODE = "7.AF.3"
VARIANTS_PER_STEM = 20


def _fmt_num(val: Fraction) -> str:
    """Format a number for equation display as a clean decimal.

    7.AF.3 values are always integers or terminating decimals, so render them as
    decimals (0.8, 19.6) rather than reduced improper fractions (4/5, 98/5).
    """
    f = float(val)
    if f == int(f):
        return str(int(f))
    return f"{f:.4f}".rstrip("0").rstrip(".")


def _fmt_money(val: Fraction) -> str:
    """Format as dollar amount."""
    f = float(val)
    if f == int(f):
        return str(int(f))
    return f"{f:.2f}"


class Stem7AF3:
    """Generates ~20 variants for each of 6 stems from the 7.AF.3 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        """Create a seeded NumberGenerator for a specific stem+variant."""
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - Multiple Choice (DOK 2, Easy)
    # "3x - 6 = 27. What is the solution?"
    # Form: px + q = r with integer values.
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Below Proficiency - Solve px + q = r (integers).

        Student solves a two-step equation with integer coefficients.
        Multiple choice with common error distractors.
        Difficulty: easy (integers only)
        """
        gen, rng = self._make_gen(1, variant_idx)

        # Generate clean values: pick p and x, compute q and r
        p, q, r, x = gen.two_step_add_pair("easy")

        # Decide whether to use px + q = r or px - q = r
        if rng.random() < 0.5 and q > 0:
            # px - q = r form (subtract q from both sides of px = r + q)
            actual_r = p * x - q
            eq_text = f"{_fmt_num(p)}x - {_fmt_num(q)} = {_fmt_num(actual_r)}"
            worked = (
                f"{_fmt_num(p)}x - {_fmt_num(q)} = {_fmt_num(actual_r)}\n"
                f"{_fmt_num(p)}x = {_fmt_num(actual_r)} + {_fmt_num(q)}\n"
                f"{_fmt_num(p)}x = {_fmt_num(actual_r + q)}\n"
                f"x = {_fmt_num(actual_r + q)} / {_fmt_num(p)}\n"
                f"x = {_fmt_num(x)}"
            )
        else:
            actual_r = r
            eq_text = f"{_fmt_num(p)}x + {_fmt_num(q)} = {_fmt_num(actual_r)}"
            worked = (
                f"{_fmt_num(p)}x + {_fmt_num(q)} = {_fmt_num(actual_r)}\n"
                f"{_fmt_num(p)}x = {_fmt_num(actual_r)} - {_fmt_num(q)}\n"
                f"{_fmt_num(p)}x = {_fmt_num(actual_r - q)}\n"
                f"x = {_fmt_num(actual_r - q)} / {_fmt_num(p)}\n"
                f"x = {_fmt_num(x)}"
            )

        correct = _fmt_num(x)

        # Distractors: common errors
        distractors = set()
        # Error: forgot to subtract q first (divided r by p)
        if p != 0:
            d1 = actual_r / p
            if d1 != x and d1 >= 0:
                distractors.add(_fmt_num(d1))
        # Error: multiplied instead of divided
        d2 = p * actual_r
        if d2 != x:
            distractors.add(_fmt_num(d2))
        # Error: added q instead of subtracting (or vice versa)
        d3 = (actual_r + q) / p if rng.random() < 0.5 else (actual_r - q) * p
        if d3 != x and d3 >= 0:
            distractors.add(_fmt_num(Fraction(d3).limit_denominator(100)))
        # Error: off by small amount
        d4 = x + rng.choice([Fraction(1), Fraction(-1), Fraction(2)])
        if d4 >= 0 and d4 != x:
            distractors.add(_fmt_num(d4))

        distractors.discard(correct)
        distractor_list = list(distractors)
        rng.shuffle(distractor_list)
        distractor_list = distractor_list[:3]

        # Pad if needed
        while len(distractor_list) < 3:
            offset = rng.choice([1, 2, 3, -1, -2])
            d = x + Fraction(offset)
            if d >= 0 and _fmt_num(d) != correct and _fmt_num(d) not in distractor_list:
                distractor_list.append(_fmt_num(d))

        stem_text = f"An equation is given.\n\n  {eq_text}\n\nWhat is the solution to the equation?"

        choices = shuffle_choices(correct, correct, distractor_list, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY,
            dok=2,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"{correct_letter}) x = {correct}",
            answer_latex=f"{correct_letter}) x = {correct}",
            worked_solution=worked,
            choices=choices,
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - Numeric Response (DOK 2, Medium)
    # "0.5(x - 3) = 7.5. What is the solution?"
    # Form: p(x + q) = r with one decimal.
    # ================================================================

    def stem2_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        """Approaching Proficiency - Solve p(x + q) = r with decimal.

        Student solves a two-step equation in parenthetical form with
        at least one decimal value. Numeric response.
        Difficulty: medium (one decimal)
        """
        gen, rng = self._make_gen(2, variant_idx)

        p, q, r, x = gen.two_step_paren_pair("medium")

        # Format equation: p(x + q) = r or p(x - |q|) = r
        p_str = _fmt_num(p)
        q_str = _fmt_num(q)
        r_str = _fmt_num(r)
        x_str = _fmt_num(x)

        if q >= 0:
            eq_text = f"{p_str}(x + {q_str}) = {r_str}"
            step1 = f"x + {q_str} = {r_str} / {p_str}"
            inner = r / p
            step2 = f"x + {q_str} = {_fmt_num(inner)}"
            step3 = f"x = {_fmt_num(inner)} - {q_str}"
        else:
            eq_text = f"{p_str}(x - {_fmt_num(abs(q))}) = {r_str}"
            step1 = f"x - {_fmt_num(abs(q))} = {r_str} / {p_str}"
            inner = r / p
            step2 = f"x - {_fmt_num(abs(q))} = {_fmt_num(inner)}"
            step3 = f"x = {_fmt_num(inner)} + {_fmt_num(abs(q))}"

        worked = (
            f"{eq_text}\n"
            f"{step1}\n"
            f"{step2}\n"
            f"{step3}\n"
            f"x = {x_str}"
        )

        stem_text = f"An equation is given.\n\n  {eq_text}\n\nWhat is the solution to the equation?"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.MEDIUM, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM,
            dok=2,
            item_type=ItemType.NR,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"x = {x_str}",
            answer_latex=f"x = {x_str}",
            worked_solution=worked,
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - Multiple Choice (DOK 2, Easy)
    # Real-world: "Which equation models this situation?"
    # ================================================================

    def stem3_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Approaching Proficiency - Select equation for real-world context.

        Real-world situation described; student selects the correct
        equation of form px + q = r.
        Difficulty: easy (integers)
        """
        gen, rng = self._make_gen(3, variant_idx)

        ctx = rng.choice(CONTEXTS_7AF3_PX_PLUS_Q)
        name = pick_name(rng)
        var = ctx["var_letter"]

        # Generate integer values
        p, q, r, x = gen.two_step_add_pair("easy")
        p_int = int(p)
        q_int = int(q)
        r_int = int(r)

        # Format the setup with actual numbers
        setup_text = ctx["setup"].format(
            name=name, p=p_int, q=q_int, r=r_int, var=var, q2=q_int
        )

        correct_eq = f"{p_int}{var} + {q_int} = {r_int}"

        # Distractors: common modeling errors
        distractors = []

        # Wrong 1: flipped p and q roles
        d1 = f"{q_int}{var} + {p_int} = {r_int}"
        if d1 != correct_eq:
            distractors.append(d1)

        # Wrong 2: wrong operation (multiplication instead of addition)
        d2 = f"{p_int} * {q_int}{var} = {r_int}"
        if d2 != correct_eq and d2 not in distractors:
            distractors.append(d2)

        # Wrong 3: subtraction instead
        d3 = f"{p_int}{var} - {q_int} = {r_int}"
        if d3 != correct_eq and d3 not in distractors:
            distractors.append(d3)

        # Wrong 4: p + q*var = r
        d4 = f"{p_int} + {q_int}{var} = {r_int}"
        if d4 != correct_eq and d4 not in distractors:
            distractors.append(d4)

        while len(distractors) < 3:
            delta = rng.choice([1, -1, 2])
            d = f"{p_int + delta}{var} + {q_int} = {r_int}"
            if d != correct_eq and d not in distractors:
                distractors.append(d)

        distractors = distractors[:3]

        stem_text = (
            f"{setup_text}\n\n"
            f"Which equation can be used to determine {var}?"
        )

        choices = shuffle_choices(correct_eq, correct_eq, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"The rate is {p_int} per unit, so the variable term is {p_int}{var}.\n"
            f"The fixed amount is {q_int}, added to give {p_int}{var} + {q_int}.\n"
            f"The total is {r_int}, so: {correct_eq}"
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
            answer_text=f"{correct_letter}) {correct_eq}",
            answer_latex=f"{correct_letter}) {correct_eq}",
            worked_solution=worked,
            choices=choices,
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At Proficiency - Multi-Part (DOK 2, Easy)
    # "Part A: Create an equation. Part B: Solve it."
    # Real-world context with integers. p(x + q) = r form.
    # ================================================================

    def stem4_at_mp(self, variant_idx: int) -> GeneratedQuestion:
        """At Proficiency - Multi-part: write and solve equation (integers).

        Real-world context leading to p(x + q) = r.
        Part A: Write the equation. Part B: Solve for x.
        Difficulty: easy (integers)
        """
        gen, rng = self._make_gen(4, variant_idx)

        ctx = rng.choice(CONTEXTS_7AF3_PAREN)
        name = pick_name(rng)
        var = ctx["var_letter"]

        p, q, r, x = gen.two_step_paren_pair("easy")
        p_int = int(p)
        q_int = int(q)
        r_int = int(r)
        x_int = int(x)

        setup_text = ctx["setup"].format(
            name=name, p=p_int, q=q_int, r=r_int, var=var
        )

        correct_eq = f"{p_int}({var} + {q_int}) = {r_int}"
        alt_eq = f"{p_int}{var} + {p_int * q_int} = {r_int}"

        stem_text = (
            f"{setup_text}\n\n"
            f"Part A: Create an equation that models this situation.\n\n"
            f"Part B: Solve the equation. {ctx['question'].format(name=name)}"
        )

        part_a = QuestionPart(
            label="Part A",
            prompt="Create an equation that models this situation.",
            prompt_latex="Create an equation that models this situation.",
            answer=correct_eq,
            answer_latex=correct_eq,
            item_type=ItemType.EQ
        )
        part_b = QuestionPart(
            label="Part B",
            prompt=f"Solve the equation.",
            prompt_latex=f"Solve the equation.",
            answer=f"{var} = {x_int}",
            answer_latex=f"{var} = {x_int}",
            item_type=ItemType.NR
        )

        worked = (
            f"Part A: {correct_eq}  (or equivalently: {alt_eq})\n"
            f"Part B:\n"
            f"  {correct_eq}\n"
            f"  {var} + {q_int} = {r_int} / {p_int}\n"
            f"  {var} + {q_int} = {_fmt_num(Fraction(r_int, p_int))}\n"
            f"  {var} = {_fmt_num(Fraction(r_int, p_int))} - {q_int}\n"
            f"  {var} = {x_int}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MP,
                               Difficulty.EASY, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.EASY,
            dok=2,
            item_type=ItemType.MP,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"Part A: {correct_eq}; Part B: {var} = {x_int}",
            answer_latex=f"Part A: {correct_eq}; Part B: {var} = {x_int}",
            worked_solution=worked,
            parts=[part_a, part_b],
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: At Proficiency - Multi-Part (DOK 2, Medium)
    # "Part A: Create an equation with decimals. Part B: Solve."
    # Real-world context with one decimal. px + q = r form.
    # ================================================================

    def stem5_at_mp_medium(self, variant_idx: int) -> GeneratedQuestion:
        """At Proficiency - Multi-part with decimal values.

        Real-world px + q = r with at least one decimal.
        Part A: Write equation. Part B: Solve.
        Difficulty: medium (one decimal)
        """
        gen, rng = self._make_gen(5, variant_idx)

        name = pick_name(rng)

        # Half the variants use a subtraction scenario (a - bx = c) so the bank is
        # not limited to addition (ax + b = c).
        use_sub = (variant_idx % 2 == 1)
        if use_sub:
            # Build a - bx = c with an integer count x and a realistic per-unit
            # amount, so "how many tickets/reports" always has a whole answer.
            p = gen.decimal_1place(1.0, 9.0)      # amount removed per unit
            x = gen.whole_number(3, 12)           # integer count
            q = gen.decimal_1place(1.0, 20.0)     # amount remaining
            r = q + p * x                         # starting amount
        else:
            p, q, r, x = gen.two_step_add_pair("medium")

        p_str = _fmt_num(p)
        q_str = _fmt_num(q)
        r_str = _fmt_num(r)
        x_str = _fmt_num(x)

        # Use money format for dollar contexts
        p_money = _fmt_money(p)
        q_money = _fmt_money(q)
        r_money = _fmt_money(r)

        if use_sub:
            ctx = rng.choice(CONTEXTS_7AF3_SUB)
            var = ctx["var_letter"]
            setup_text = ctx["setup"].format(
                name=name, p=p_money, q=q_money, r=r_money, var=var
            )
            correct_eq = f"{r_str} - {p_str}{var} = {q_str}"
            worked = (
                f"Part A: {correct_eq}\n"
                f"Part B:\n"
                f"  {r_str} - {p_str}{var} = {q_str}\n"
                f"  {r_str} - {q_str} = {p_str}{var}\n"
                f"  {_fmt_num(r - q)} = {p_str}{var}\n"
                f"  {var} = {_fmt_num(r - q)} / {p_str}\n"
                f"  {var} = {x_str}"
            )
        else:
            ctx = rng.choice(CONTEXTS_7AF3_PX_PLUS_Q)
            var = ctx["var_letter"]
            setup_text = ctx["setup"].format(
                name=name, p=p_money, q=q_money, r=r_money, var=var, q2=q_money
            )
            correct_eq = f"{p_str}{var} + {q_str} = {r_str}"
            worked = (
                f"Part A: {correct_eq}\n"
                f"Part B:\n"
                f"  {p_str}{var} + {q_str} = {r_str}\n"
                f"  {p_str}{var} = {r_str} - {q_str}\n"
                f"  {p_str}{var} = {_fmt_num(r - q)}\n"
                f"  {var} = {_fmt_num(r - q)} / {p_str}\n"
                f"  {var} = {x_str}"
            )

        stem_text = (
            f"{setup_text}\n\n"
            f"Part A: Write an equation that represents this situation.\n\n"
            f"Part B: Solve the equation. {ctx['question'].format(name=name)}"
        )

        part_a = QuestionPart(
            label="Part A",
            prompt="Write an equation that represents this situation.",
            prompt_latex="Write an equation that represents this situation.",
            answer=correct_eq,
            answer_latex=correct_eq,
            item_type=ItemType.EQ
        )
        part_b = QuestionPart(
            label="Part B",
            prompt="Solve the equation.",
            prompt_latex="Solve the equation.",
            answer=f"{var} = {x_str}",
            answer_latex=f"{var} = {x_str}",
            item_type=ItemType.NR
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MP,
                               Difficulty.MEDIUM, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM,
            dok=2,
            item_type=ItemType.MP,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"Part A: {correct_eq}; Part B: {var} = {x_str}",
            answer_latex=f"Part A: {correct_eq}; Part B: {var} = {x_str}",
            worked_solution=worked,
            parts=[part_a, part_b],
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 6: Above Proficiency - Multiple Select (DOK 2, Easy)
    # "Select the TWO equations that model this situation."
    # Both px + q = r and p(x + q') = r forms should be correct.
    # ================================================================

    def stem6_above_ms(self, variant_idx: int) -> GeneratedQuestion:
        """Above Proficiency - Select two equivalent equations.

        Real-world situation where both px + q = r and an equivalent
        rearrangement are valid. Student selects the two correct equations.
        Difficulty: easy (integers)
        """
        gen, rng = self._make_gen(6, variant_idx)

        name = pick_name(rng)

        # Generate: p items of type A + x items of type B at $c each = total
        c = int(gen.small_whole(2, 10))  # cost per item
        a = int(gen.small_whole(2, 8))   # known quantity
        x = int(gen.whole_number(1, 15)) # unknown quantity
        total = c * (a + x)

        var = "x"

        # Two correct equation forms:
        eq1 = f"{c}({var} + {a}) = {total}"          # c(x + a) = total
        eq2 = f"{c}{var} + {c * a} = {total}"        # cx + ca = total

        # Build context
        item_pairs = [
            ("red shirts", "blue shirts", "shirts"),
            ("fiction books", "nonfiction books", "books"),
            ("vanilla cupcakes", "chocolate cupcakes", "cupcakes"),
            ("pepperoni pizzas", "cheese pizzas", "pizzas"),
            ("hardcover books", "paperback books", "books"),
        ]
        item_a, item_b, item_general = rng.choice(item_pairs)

        setup_text = (
            f"{name} purchased {a} {item_a} and {var} {item_b}. "
            f"Each {item_general[:-1] if item_general.endswith('s') else item_general} "
            f"costs ${c}. The total cost is ${total}."
        )

        stem_text = (
            f"{setup_text}\n\n"
            f"Select the TWO equations that could be used to determine {var}, "
            f"the number of {item_b} purchased."
        )

        # Wrong options
        wrong_options = []
        w1 = f"{a}{var} + {c} = {total}"
        if w1 != eq1 and w1 != eq2:
            wrong_options.append(w1)
        w2 = f"{c}{var} - {c * a} = {total}"
        if w2 != eq1 and w2 != eq2 and w2 not in wrong_options:
            wrong_options.append(w2)
        w3 = f"{c}({var} - {a}) = {total}"
        if w3 != eq1 and w3 != eq2 and w3 not in wrong_options:
            wrong_options.append(w3)
        w4 = f"{a}{var} = {total} - {c}"
        if w4 != eq1 and w4 != eq2 and w4 not in wrong_options:
            wrong_options.append(w4)

        while len(wrong_options) < 3:
            delta = rng.choice([1, 2, -1])
            w = f"{c + delta}({var} + {a}) = {total}"
            if w != eq1 and w != eq2 and w not in wrong_options:
                wrong_options.append(w)

        wrong_options = wrong_options[:3]

        # Build choices: 2 correct + 3 wrong
        all_options = [(eq1, True), (eq2, True)]
        for w in wrong_options:
            all_options.append((w, False))
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

        worked = (
            f"Two valid equations:\n"
            f"  {eq1} (parenthetical form)\n"
            f"  {eq2} (distributed form)\n"
            f"Both solve to {var} = {x}."
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
            answer_text=f"{', '.join(correct_letters)}) {eq1}; {eq2}",
            answer_latex=f"{', '.join(correct_letters)}) {eq1}; {eq2}",
            worked_solution=worked,
            choices=choices,
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6,
            variant_index=variant_idx
        )

    # ================================================================
    # MAIN GENERATION METHOD
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        """Generate all variants for all 6 stems.

        Returns ~120 questions (6 stems x 20 variants).
        """
        all_questions = []

        stem_methods = [
            self.stem1_below_mc,
            self.stem2_approaching_nr,
            self.stem3_approaching_mc,
            self.stem4_at_mp,
            self.stem5_at_mp_medium,
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
            1: self.stem1_below_mc,
            2: self.stem2_approaching_nr,
            3: self.stem3_approaching_mc,
            4: self.stem4_at_mp,
            5: self.stem5_at_mp_medium,
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
    print("Generating 7.AF.3 question variants...")
    print("=" * 60)

    generator = Stem7AF3(seed=42)
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
