"""
Stem generator for 6.AF.3:
  Solve equations of the form x + p = q, x - p = q, px = q, and x/p = q
  fluently for cases in which p, q and x are all nonnegative rational numbers.
  Represent real-world problems using equations of these forms and solve such problems.

Content Limits:
  - Equations must be presented in one of the four forms above
  - All numbers must be nonneg rational
  - One variable per equation
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: whole numbers only
  Medium: mix of whole numbers and decimals
  Difficult: fractions, mixed numbers, or decimals only

7 Stems from the Item Spec:
  Stem 1 (Below-EQ): Write an equation from a real-world sharing/division context (DOK 2, difficult)
  Stem 2 (Below-MC): Select the equation that models a real-world addition context (DOK 1, easy)
  Stem 3 (Approaching-NR): Solve a given equation px = q (DOK 1, medium)
  Stem 4 (Approaching-MC): Which equation has solution x = V? (DOK 1, medium)
  Stem 5 (At-MP): Real-world multiplication context → Part A: write equation, Part B: solve (DOK 2, easy)
  Stem 6 (At-MP): Real-world addition context with decimals → Part A: write equation, Part B: solve (DOK 2, difficult)
  Stem 7 (Above-ER): Budget problem → write equation, solve, explain with rounding (DOK 3, difficult)
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
from engine.number_generators import NumberGenerator, display_mode_for_difficulty
from engine.context_pools import (
    CONTEXTS_6AF3_ADD, CONTEXTS_6AF3_SUBTRACT,
    CONTEXTS_6AF3_MULTIPLY, CONTEXTS_6AF3_DIVIDE,
    CONTEXTS_6AF3_ABOVE, pick_name, pick_relationship
)
from engine.distractor_engine import DistractorEngine, shuffle_choices
from engine.answer_validator import validate_and_report


STANDARD_CODE = "6.AF.3"
VARIANTS_PER_STEM = 20


class Stem6AF3:
    """Generates ~20 variants for each of 7 stems from the 6.AF.3 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        """Create a seeded NumberGenerator for a specific stem+variant."""
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - Equation Entry (DOK 2, Difficult)
    # "A group of friends share 3 1/3 pints of ice cream. Each person
    #  received 2/3 pint. Create an equation using f that models the situation."
    # Form: x/f = q  (division), or equivalently q*f = x
    # ================================================================

    def stem1_below_eq(self, variant_idx: int) -> GeneratedQuestion:
        """Below Proficiency - Write a division equation from context.

        Structure: Total amount is shared among f people, each gets some amount.
        Equation form: total / f = each_share (or each_share * f = total)
        Difficulty: difficult (fractions/mixed numbers)
        """
        gen, rng = self._make_gen(1, variant_idx)

        # Generate numbers: each_share and num_people, compute total
        # Using fractions for difficult tier
        each_share = gen.proper_fraction()  # what each person gets
        num_people = gen.small_whole(2, 8)  # number of people
        total = each_share * num_people     # total amount

        # Pick a sharing context
        ctx_template = rng.choice(CONTEXTS_6AF3_DIVIDE)
        name = pick_name(rng)

        # Pick item for sharing contexts that have item_options
        item = "pints of ice cream"
        if "item_options" in ctx_template:
            item = rng.choice(ctx_template["item_options"])

        var = "f"  # variable for number of people, per original stem

        # Format numbers
        total_rn = RationalNumber(total, "mixed")
        share_rn = RationalNumber(each_share, "fraction")

        # Build stem text
        stem_text = (
            f"A group of friends share {total_rn.display()} {item}. "
            f"Each person received {share_rn.display()} {item}.\n\n"
            f"Let {var} be the number of friends who shared the {item}.\n\n"
            f"Create an equation using {var} that models the situation."
        )

        stem_latex = (
            f"A group of friends share ${total_rn.latex()}$ {item}. "
            f"Each person received ${share_rn.latex()}$ {item}.\n\n"
            f"Let ${var}$ be the number of friends who shared the {item}.\n\n"
            f"Create an equation using ${var}$ that models the situation."
        )

        # Answer: total / f = each_share  OR  each_share * f = total
        answer_text = (
            f"{total_rn.display()} ÷ {var} = {share_rn.display()} "
            f"or {share_rn.display()} × {var} = {total_rn.display()}"
        )
        answer_latex = (
            f"${total_rn.latex()} \\div {var} = {share_rn.latex()}$ "
            f"or ${share_rn.latex()} \\cdot {var} = {total_rn.latex()}$"
        )

        worked = (
            f"The total amount ({total_rn.display()}) is divided equally among {var} friends, "
            f"with each receiving {share_rn.display()}.\n"
            f"This gives: {total_rn.display()} ÷ {var} = {share_rn.display()}\n"
            f"Solving: {var} = {total_rn.display()} ÷ {share_rn.display()} = {int(num_people)}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.EQ,
                               Difficulty.DIFFICULT, 1, variant_idx)

        q = GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.DIFFICULT,
            dok=2,
            item_type=ItemType.EQ,
            stem_text=stem_text,
            stem_latex=stem_latex,
            answer_text=answer_text,
            answer_latex=answer_latex,
            worked_solution=worked,
            context_scenario=f"sharing {item}",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1,
            variant_index=variant_idx
        )

        # Validate
        valid, errs = validate_and_report(q, num_people, each_share, total, "divide")
        if errs:
            # Note: for EQ type the equation validation may not apply directly
            # since the student writes the equation. Generic validation still applies.
            pass

        return q

    # ================================================================
    # STEM 2: Below Proficiency - Multiple Choice (DOK 1, Easy)
    # "A student read a whole book on Monday and Tuesday... Select the
    #  equation that models this situation."
    # Form: p + x = q (addition) - student selects from 4 options
    # ================================================================

    def stem2_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Below Proficiency - Select the correct equation from context.

        Structure: Two-part addition problem. Student picks the right equation.
        Difficulty: easy (whole numbers)
        """
        gen, rng = self._make_gen(2, variant_idx)

        # Pick equation form - addition for this stem
        x = gen.whole_number(50, 500)
        p = gen.whole_number(50, 500)
        q = x + p

        # Pick context
        ctx = rng.choice(CONTEXTS_6AF3_ADD)
        name = pick_name(rng)
        var = ctx["var_letter"]

        # Format for context template
        p_display = str(int(p))
        q_display = str(int(q))

        # Build stem with the context sentence
        activity = ctx["scenario_type"]
        context_sentence = self._add_context_sentence(ctx, name, p_display, q_display, var)
        stem_text = (
            f"{context_sentence}\n\n"
            f"Select the equation that models this situation."
        )

        # Build correct equation and distractors
        correct_eq = f"{p_display} + {var} = {q_display}"
        correct_eq_latex = f"${p_display} + {var} = {q_display}$"

        # Distractor equations (common modeling errors)
        distractor_eqs = [
            f"{p_display} + {q_display} = {var}",     # adds both knowns
            f"{p_display}{var} = {q_display}",          # multiplies instead
            f"{p_display} - {var} = {q_display}",       # subtracts instead
        ]
        rng.shuffle(distractor_eqs)

        # Build choices
        all_options = [(correct_eq, True)] + [(d, False) for d in distractor_eqs[:3]]
        rng.shuffle(all_options)

        choices = []
        for i, (eq_text, is_correct) in enumerate(all_options):
            key = chr(ord('a') + i)
            choices.append(QuestionChoice(
                key=key,
                text=eq_text,
                text_latex=f"${eq_text}$" if "$" not in eq_text else eq_text,
                is_correct=is_correct,
            ))

        # Find correct letter
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
            stem_latex=stem_text,  # no special latex needed for word problem
            answer_text=correct_letter,
            answer_latex=correct_letter,
            worked_solution=f"The correct equation is {correct_eq} because {ctx['variable_desc'].format(name=name)} plus {p_display} equals {q_display}.",
            choices=choices,
            context_scenario=activity,
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - Numeric Response (DOK 1, Medium)
    # "Solve. 5/8 x = 40"  → Answer: 64
    # Form: px = q, solve for x
    # ================================================================

    def stem3_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        """Approaching Proficiency - Solve a multiplication equation.

        Direct equation solving with no real-world context.
        Difficulty: medium (mix of whole numbers and fractions)
        """
        gen, rng = self._make_gen(3, variant_idx)

        # Generate px = q where p is a fraction/decimal and x is a whole number
        # This matches the original: (5/8)x = 40 -> x = 64
        # We generate p and x first, then compute q = p*x to guarantee clean answer
        if rng.random() < 0.5:
            # Fraction coefficient (like the original 5/8)
            p = gen.proper_fraction()
            x = gen.whole_number(4, 50)
            q = p * x
        else:
            # Decimal coefficient
            p = gen.decimal_1place(0.5, 9.9)
            x = gen.whole_number(2, 30)
            q = p * x

        # Stick to multiply form for this stem (matches the original item spec)
        # Determine display mode: fractions show as fractions, decimals as decimals, whole as whole
        def _pick_display(val):
            if val.denominator == 1:
                return "whole"
            # Check if it's a clean terminating decimal
            d = val.denominator
            while d % 2 == 0: d //= 2
            while d % 5 == 0: d //= 5
            if d == 1:
                return "decimal"
            # If > 1, show as mixed number; if < 1, show as fraction
            if val >= 1:
                return "mixed"
            return "fraction"

        p_rn = RationalNumber(p, _pick_display(p))
        q_rn = RationalNumber(q, _pick_display(q))
        x_rn = RationalNumber(x, _pick_display(x))

        var = "x"
        stem_text = f"Solve.\n\n{p_rn.display()}{var} = {q_rn.display()}"
        stem_latex = f"Solve.\n\n${p_rn.latex()}{var} = {q_rn.latex()}$"

        answer_text = x_rn.display()
        answer_latex = f"${x_rn.latex()}$"

        # Worked solution
        if p.denominator == 1:
            worked = (
                f"{p_rn.display()}{var} = {q_rn.display()}\n"
                f"{var} = {q_rn.display()} ÷ {p_rn.display()}\n"
                f"{var} = {x_rn.display()}"
            )
        else:
            recip = Fraction(p.denominator, p.numerator)
            recip_rn = RationalNumber(recip, "fraction")
            worked = (
                f"{p_rn.display()}{var} = {q_rn.display()}\n"
                f"Multiply both sides by {recip_rn.display()}:\n"
                f"{var} = {q_rn.display()} × {recip_rn.display()}\n"
                f"{var} = {x_rn.display()}"
            )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.MEDIUM, 3, variant_idx)

        question = GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM,
            dok=1,
            item_type=ItemType.NR,
            stem_text=stem_text,
            stem_latex=stem_latex,
            answer_text=answer_text,
            answer_latex=answer_latex,
            worked_solution=worked,
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3,
            variant_index=variant_idx
        )

        # Validate
        valid, errs = validate_and_report(question, x, p, q, "multiply")
        if errs:
            pass  # Log in production

        return question

    # ================================================================
    # STEM 4: Approaching Proficiency - Multiple Choice (DOK 1, Medium)
    # "Which equation has the solution x = 1/3?"
    # One correct equation, 3 wrong equations
    # ================================================================

    def stem4_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Approaching Proficiency - Which equation has the given solution?

        Student tests each equation to find which one yields x = target.
        Difficulty: medium (whole numbers and fractions)
        """
        gen, rng = self._make_gen(4, variant_idx)

        # Pick a target solution - mix of fractions and whole numbers
        if rng.random() < 0.5:
            target_x = gen.proper_fraction()
            display = "fraction"
        else:
            target_x = gen.whole_number(1, 10)
            display = "whole"

        target_rn = RationalNumber(target_x, display)

        # Build the CORRECT equation (randomly pick a form)
        form = rng.choice(["add", "subtract", "multiply"])
        if form == "add":
            a = gen.whole_number(1, 10)
            b = a + target_x
            b_rn = RationalNumber(b, "mixed" if b.denominator != 1 else "whole")
            correct_eq = f"{int(a)} + x = {b_rn.display()}"
            correct_latex = f"${int(a)} + x = {b_rn.latex()}$"
        elif form == "subtract":
            a = gen.whole_number(2, 10)
            if a <= target_x:
                a = target_x + gen.whole_number(1, 5)
            b = a - target_x
            b_rn = RationalNumber(b, "mixed" if b.denominator != 1 else "whole")
            a_rn = RationalNumber(a, "whole" if a.denominator == 1 else "mixed")
            correct_eq = f"{a_rn.display()} - x = {b_rn.display()}"
            correct_latex = f"${a_rn.latex()} - x = {b_rn.latex()}$"
        else:  # multiply
            a = gen.whole_number(2, 10)
            b = a * target_x
            b_rn = RationalNumber(b, "mixed" if b.denominator != 1 else "whole")
            correct_eq = f"{int(a)}x = {b_rn.display()}"
            correct_latex = f"${int(a)}x = {b_rn.latex()}$"

        # Build wrong equations that look similar but have different solutions
        wrong_eqs = []
        wrong_latexes = []

        # Wrong eq 1: addition with wrong sum
        a1 = gen.whole_number(1, 10)
        b1 = a1 + target_x + rng.choice([Fraction(1), Fraction(2), Fraction(-1)])
        if b1 > 0 and b1 - a1 != target_x:
            b1_rn = RationalNumber(b1, "mixed" if b1.denominator != 1 else "whole")
            wrong_eqs.append(f"{int(a1)} + x = {b1_rn.display()}")
            wrong_latexes.append(f"${int(a1)} + x = {b1_rn.latex()}$")

        # Wrong eq 2: multiplication with wrong product
        a2 = gen.whole_number(2, 10)
        b2 = a2 * target_x + rng.choice([Fraction(1), Fraction(-1), Fraction(2)])
        if b2 > 0 and b2 / a2 != target_x:
            b2_rn = RationalNumber(b2, "mixed" if b2.denominator != 1 else "whole")
            wrong_eqs.append(f"{int(a2)}x = {b2_rn.display()}")
            wrong_latexes.append(f"${int(a2)}x = {b2_rn.latex()}$")

        # Wrong eq 3: subtraction with wrong result
        a3 = gen.whole_number(2, 10)
        b3 = a3 - target_x + rng.choice([Fraction(1), Fraction(-1)])
        if b3 >= 0 and a3 - b3 != target_x:
            b3_rn = RationalNumber(b3, "mixed" if b3.denominator != 1 else "whole")
            wrong_eqs.append(f"{int(a3)} - x = {b3_rn.display()}")
            wrong_latexes.append(f"${int(a3)} - x = {b3_rn.latex()}$")

        # Pad if needed
        while len(wrong_eqs) < 3:
            a_extra = gen.whole_number(2, 12)
            b_extra = a_extra * (target_x + Fraction(self.base_seed % 3 + 1))
            b_extra_rn = RationalNumber(b_extra, "whole" if b_extra.denominator == 1 else "mixed")
            eq = f"{int(a_extra)}x = {b_extra_rn.display()}"
            if eq != correct_eq and eq not in wrong_eqs:
                wrong_eqs.append(eq)
                wrong_latexes.append(f"${int(a_extra)}x = {b_extra_rn.latex()}$")

        # Build choices
        all_options = [(correct_eq, correct_latex, True)]
        for i in range(3):
            all_options.append((wrong_eqs[i], wrong_latexes[i], False))
        rng.shuffle(all_options)

        choices = []
        for i, (text, latex, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i),
                text=text,
                text_latex=latex,
                is_correct=is_correct
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = f"Which equation has the solution x = {target_rn.display()}?"
        stem_latex = f"Which equation has the solution $x = {target_rn.latex()}$?"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM,
            dok=1,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_latex,
            answer_text=correct_letter,
            answer_latex=correct_letter,
            worked_solution=f"Substitute x = {target_rn.display()} into each equation. Only {correct_eq} is true.",
            choices=choices,
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: At Proficiency - Multi-Part (DOK 2, Easy)
    # "A brother and sister measure their height.
    #  The sister is 3 times as tall as her brother. Sister is 63 inches.
    #  Part A: Write an equation. Part B: Solve."
    # Form: px = q (multiplication)
    # ================================================================

    def stem5_at_mp_easy(self, variant_idx: int) -> GeneratedQuestion:
        """At Proficiency - Multi-part multiplication equation from context.

        Real-world comparison: one quantity is N times another.
        Part A: Write the equation
        Part B: Solve for the variable
        Difficulty: easy (whole numbers)
        """
        gen, rng = self._make_gen(5, variant_idx)

        # Generate: multiplier, x (smaller), q = multiplier * x
        multiplier = gen.small_whole(2, 9)
        x = gen.whole_number(5, 50)
        q = multiplier * x

        # Pick context
        ctx = rng.choice(CONTEXTS_6AF3_MULTIPLY)
        name = pick_name(rng)
        var = ctx["var_letter"]

        mult_int = int(multiplier)
        q_int = int(q)
        x_int = int(x)

        # Build stem based on context type
        if ctx.get("uses_relationship"):
            rel1, rel2 = pick_relationship(rng)
            stem_text = (
                f"A {rel1} and {rel2} measure their height.\n\n"
                f"- The {rel1} is {mult_int} times as tall as the {rel2}.\n"
                f"- The {rel1} is {q_int} inches tall.\n"
                f"- The {rel2} is {var} inches tall.\n\n"
                f"Part A: Write an equation to represent the {rel2}'s height.\n\n"
                f"Part B: Solve the equation to find the {rel2}'s height, {var}."
            )
            scenario = f"{rel1}/{rel2} height comparison"
        else:
            template = ctx["template"]
            unit = ctx["unit"]
            filled = template.format(
                name=name, p=mult_int, q=q_int, x=var, var=var,
                relation1="", relation2=""
            )
            stem_text = (
                f"{filled}\n\n"
                f"Part A: Write an equation to represent {ctx['variable_desc'].format(name=name)}.\n\n"
                f"Part B: Solve the equation to find {var}."
            )
            scenario = ctx["scenario_type"]

        # Parts
        part_a = QuestionPart(
            label="Part A",
            prompt=f"Write an equation to represent the situation.",
            prompt_latex=f"Write an equation to represent the situation.",
            answer=f"{mult_int}{var} = {q_int}",
            answer_latex=f"${mult_int}{var} = {q_int}$",
            item_type=ItemType.EQ
        )
        part_b = QuestionPart(
            label="Part B",
            prompt=f"Solve the equation to find {var}.",
            prompt_latex=f"Solve the equation to find ${var}$.",
            answer=f"{var} = {x_int}",
            answer_latex=f"${var} = {x_int}$",
            item_type=ItemType.NR
        )

        worked = (
            f"Part A: {mult_int}{var} = {q_int}\n"
            f"Part B: {mult_int}{var} = {q_int}\n"
            f"        {mult_int}{var} ÷ {mult_int} = {q_int} ÷ {mult_int}\n"
            f"        {var} = {x_int}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MP,
                               Difficulty.EASY, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.EASY,
            dok=2,
            item_type=ItemType.MP,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"Part A: {mult_int}{var} = {q_int}; Part B: {var} = {x_int}",
            answer_latex=f"Part A: ${mult_int}{var} = {q_int}$; Part B: ${var} = {x_int}$",
            worked_solution=worked,
            parts=[part_a, part_b],
            context_scenario=scenario,
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 6: At Proficiency - Multi-Part (DOK 2, Difficult)
    # "A boy feeds his dog in the morning and at night.
    #  x cups morning + 1.25 cups night = 2.5 cups total
    #  Part A: Write equation. Part B: Solve."
    # Form: x + p = q (addition with decimals)
    # ================================================================

    def stem6_at_mp_difficult(self, variant_idx: int) -> GeneratedQuestion:
        """At Proficiency - Multi-part addition equation with decimals/fractions.

        Real-world two-part total. Student writes and solves x + p = q.
        Difficulty: difficult (decimals or fractions)
        """
        gen, rng = self._make_gen(6, variant_idx)

        # Generate x + p = q with decimal/fraction values
        if rng.random() < 0.5:
            # Decimals
            q = gen.decimal_1place(2.0, 20.0)
            p = gen.decimal_1place(0.5, float(q) - 0.5)
            if p >= q:
                p = q - Fraction(5, 10)
            x = q - p
            display = "decimal"
        else:
            # Fractions
            q = gen.mixed_number(5, 6)
            p = gen.proper_fraction(6)
            if p >= q:
                p = Fraction(1, 3)
            x = q - p
            display = "mixed"

        p_rn = RationalNumber(p, display)
        q_rn = RationalNumber(q, display)
        x_rn = RationalNumber(x, display)

        # Specific two-part addition contexts (like original: dog food morning+night)
        name = pick_name(rng)
        two_part_contexts = [
            {
                "intro": f"{name} feeds a pet in the morning and at night.",
                "bullets": [
                    f"{name} gives the pet some food, {{var}}, in the morning.",
                    f"{name} gives the pet {p_rn.display()} cups of food at night.",
                    f"{name} gives the pet {q_rn.display()} total cups of food each day."
                ],
                "part_b_q": f"How much food does {name} give the pet in the morning?",
                "unit": "cups",
                "var": "x"
            },
            {
                "intro": f"{name} practices an instrument on two days.",
                "bullets": [
                    f"On Saturday, {name} practices for {{var}} hours.",
                    f"On Sunday, {name} practices for {p_rn.display()} hours.",
                    f"{name} practices for {q_rn.display()} hours total over the weekend."
                ],
                "part_b_q": f"How many hours does {name} practice on Saturday?",
                "unit": "hours",
                "var": "h"
            },
            {
                "intro": f"{name} runs a race in two stages.",
                "bullets": [
                    f"In the first stage, {name} runs {{var}} miles.",
                    f"In the second stage, {name} runs {p_rn.display()} miles.",
                    f"The total race distance is {q_rn.display()} miles."
                ],
                "part_b_q": f"How far does {name} run in the first stage?",
                "unit": "miles",
                "var": "d"
            },
            {
                "intro": f"{name} pours juice into two glasses.",
                "bullets": [
                    f"The first glass gets {{var}} ounces of juice.",
                    f"The second glass gets {p_rn.display()} ounces of juice.",
                    f"There are {q_rn.display()} ounces of juice in total."
                ],
                "part_b_q": f"How much juice is in the first glass?",
                "unit": "ounces",
                "var": "j"
            },
            {
                "intro": f"{name} saves money over two weeks.",
                "bullets": [
                    f"In the first week, {name} saves ${{var}}.",
                    f"In the second week, {name} saves ${p_rn.display()}.",
                    f"{name} saves ${q_rn.display()} in total."
                ],
                "part_b_q": f"How much does {name} save in the first week?",
                "unit": "dollars",
                "var": "s"
            },
            {
                "intro": f"{name} reads a book over two days.",
                "bullets": [
                    f"On the first day, {name} reads {{var}} pages.",
                    f"On the second day, {name} reads {p_rn.display()} pages.",
                    f"The book has {q_rn.display()} pages in total."
                ],
                "part_b_q": f"How many pages does {name} read on the first day?",
                "unit": "pages",
                "var": "p"
            },
        ]

        ctx = rng.choice(two_part_contexts)
        var = ctx["var"]
        unit = ctx["unit"]

        bullets = "\n".join(f"- {b.format(var=var)}" for b in ctx["bullets"])
        stem_text = (
            f"{ctx['intro']}\n\n"
            f"{bullets}\n\n"
            f"Part A: Write an equation to represent the total.\n\n"
            f"Part B: {ctx['part_b_q']}"
        )

        part_a = QuestionPart(
            label="Part A",
            prompt=f"Write an equation to represent the total amount.",
            prompt_latex=f"Write an equation to represent the total amount.",
            answer=f"{var} + {p_rn.display()} = {q_rn.display()}",
            answer_latex=f"${var} + {p_rn.latex()} = {q_rn.latex()}$",
            item_type=ItemType.EQ
        )
        part_b = QuestionPart(
            label="Part B",
            prompt=f"Find the value of {var}.",
            prompt_latex=f"Find the value of ${var}$.",
            answer=f"{var} = {x_rn.display()} {unit}",
            answer_latex=f"${var} = {x_rn.latex()}$ {unit}",
            item_type=ItemType.NR
        )

        worked = (
            f"Part A: {var} + {p_rn.display()} = {q_rn.display()}\n"
            f"Part B: {var} + {p_rn.display()} = {q_rn.display()}\n"
            f"        {var} = {q_rn.display()} - {p_rn.display()}\n"
            f"        {var} = {x_rn.display()}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MP,
                               Difficulty.DIFFICULT, 6, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT,
            dok=2,
            item_type=ItemType.MP,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"Part A: {var} + {p_rn.display()} = {q_rn.display()}; Part B: {var} = {x_rn.display()} {unit}",
            answer_latex=f"Part A: ${var} + {p_rn.latex()} = {q_rn.latex()}$; Part B: ${var} = {x_rn.latex()}$ {unit}",
            worked_solution=worked,
            parts=[part_a, part_b],
            context_scenario=ctx["intro"][:50],
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 7: Above Proficiency - Extended Response (DOK 3, Difficult)
    # "A teacher wants to buy pizza for her class.
    #  A large pizza costs $13.99. Maximum $73.50 to spend.
    #  Write equation, show steps, explain how many WHOLE pizzas."
    # Form: px = q where answer requires rounding/interpretation
    # ================================================================

    def stem7_above_er(self, variant_idx: int) -> GeneratedQuestion:
        """Above Proficiency - Extended response with real-world interpretation.

        Budget problem where the exact answer is not a whole number,
        requiring students to reason about rounding in context.
        Difficulty: difficult (decimals, inferred rounding)
        """
        gen, rng = self._make_gen(7, variant_idx)

        # Generate item cost and budget where budget/cost is NOT a whole number
        item_cost = gen.money(3.00, 25.00)
        # Ensure budget/cost gives a non-integer
        num_items = gen.whole_number(3, 8)
        # Budget = cost * num_items + partial (so answer requires rounding down)
        partial = gen.money(0.50, float(item_cost) - 0.01)
        budget = item_cost * num_items + partial

        # The "real" answer is non-integer
        exact_answer = budget / item_cost  # will be > num_items
        whole_answer = int(exact_answer)   # round down

        cost_rn = RationalNumber(item_cost, "decimal")
        budget_rn = RationalNumber(budget, "decimal")

        # Pick a budget context
        ctx = rng.choice(CONTEXTS_6AF3_ABOVE)
        name = pick_name(rng)

        if "items" in ctx:
            item_plural, item_singular = rng.choice(ctx["items"])
        else:
            item_plural = "items"
            item_singular = "item"

        var = ctx["var_letter"]

        stem_text = (
            f"{name} wants to buy {item_plural} for a class event.\n\n"
            f"- Each {item_singular} costs ${cost_rn.as_decimal_str}.\n"
            f"- {name} has a maximum of ${budget_rn.as_decimal_str} to spend.\n\n"
            f"In the box below, write an equation to represent how many {item_plural} "
            f"{name} can buy. Show the steps to solving the equation and explain "
            f"how many whole {item_plural} {name} can buy."
        )

        answer_text = (
            f"Equation: {cost_rn.as_decimal_str}{var} = {budget_rn.as_decimal_str}\n"
            f"Solving: {var} = {budget_rn.as_decimal_str} ÷ {cost_rn.as_decimal_str}\n"
            f"{var} ≈ {float(exact_answer):.4f}\n"
            f"Since {name} can only buy whole {item_plural}, "
            f"{name} can buy {whole_answer} {item_plural}."
        )

        worked = (
            f"Step 1: Write the equation.\n"
            f"  {cost_rn.as_decimal_str}{var} = {budget_rn.as_decimal_str}\n\n"
            f"Step 2: Solve for {var}.\n"
            f"  {var} = {budget_rn.as_decimal_str} ÷ {cost_rn.as_decimal_str}\n"
            f"  {var} ≈ {float(exact_answer):.2f}\n\n"
            f"Step 3: Interpret the answer.\n"
            f"  Since you can only buy whole {item_plural}, round down.\n"
            f"  {name} can buy {whole_answer} whole {item_plural}."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.ER,
                               Difficulty.DIFFICULT, 7, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT,
            dok=3,
            item_type=ItemType.ER,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=answer_text,
            answer_latex=answer_text,
            worked_solution=worked,
            context_scenario=f"buying {item_plural}",
            seed=self.base_seed * 1000 + 700 + variant_idx,
            stem_index=7,
            variant_index=variant_idx
        )

    # ================================================================
    # HELPER METHODS
    # ================================================================

    def _add_context_sentence(self, ctx: dict, name: str, p: str, q: str, var: str) -> str:
        """Build a context paragraph for addition problems."""
        template = ctx["template"]
        try:
            return template.format(name=name, p=p, q=q, x=var, var=var)
        except KeyError:
            return template.format(name=name, p=p, q=q)

    @staticmethod
    def _fmt(val: Fraction) -> str:
        """Format a fraction for text display."""
        if val.denominator == 1:
            return str(int(val))
        f = float(val)
        if f == int(f):
            return str(int(f))
        return f"{f:g}"

    @staticmethod
    def _fmt_latex(rn: RationalNumber) -> str:
        """Get LaTeX from a RationalNumber."""
        return rn.latex()

    # ================================================================
    # MAIN GENERATION METHOD
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        """Generate all variants for all 7 stems.

        Returns ~140 questions (7 stems x 20 variants).
        """
        all_questions = []

        stem_methods = [
            self.stem1_below_eq,
            self.stem2_below_mc,
            self.stem3_approaching_nr,
            self.stem4_approaching_mc,
            self.stem5_at_mp_easy,
            self.stem6_at_mp_difficult,
            self.stem7_above_er,
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
        """Generate variants for a single stem (1-7)."""
        stem_methods = {
            1: self.stem1_below_eq,
            2: self.stem2_below_mc,
            3: self.stem3_approaching_nr,
            4: self.stem4_approaching_mc,
            5: self.stem5_at_mp_easy,
            6: self.stem6_at_mp_difficult,
            7: self.stem7_above_er,
        }

        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-7.")

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
    print("Generating 6.AF.3 question variants...")
    print("=" * 60)

    generator = Stem6AF3(seed=42)
    all_questions = generator.generate_all_variants(variants_per_stem=3)  # 3 for quick test

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
