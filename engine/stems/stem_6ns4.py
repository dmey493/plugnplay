"""
Stem generator for 6.NS.4:
  Solve real-world problems with positive fractions and decimals by using
  one or two operations.

Content Limits:
  - Positive fractions and mixed numbers
  - Positive decimals to thousandths
  - Maximum of 2 operations
  - Minimize order of operations at Below level
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: add/subtract only, fractions or decimals exclusively
  Medium: any operation, fractions or decimals exclusively
  Difficult: any operation, mix of fractions and decimals

6 Stems from the Item Spec:
  Stem 1 (Below-NR):      Add fractions (DOK 1, easy)
  Stem 2 (Below-NR):      Subtract decimals (DOK 1, easy)
  Stem 3 (Approaching-NR): One-step word problem with fraction multiply/divide (DOK 2, medium)
  Stem 4 (Approaching-MC): One-step decimal word problem, multiply/divide (DOK 2, medium)
  Stem 5 (At-NR):         Two-step problem mixing fractions and decimals (DOK 2, difficult)
  Stem 6 (Above-MP):      Evaluate reasoning about two-step decimal problem (DOK 3, medium)
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
from engine.context_pools import CONTEXTS_6NS4, pick_name


STANDARD_CODE = "6.NS.4"
VARIANTS_PER_STEM = 20


# ============================================================
# HELPERS
# ============================================================

def _fmt_fraction(val: Fraction) -> str:
    """Format a Fraction as a mixed number string (e.g. '4 1/2') or fraction."""
    if val.denominator == 1:
        return str(int(val))
    whole = int(val)
    remainder = val - whole
    if whole == 0:
        return f"{remainder.numerator}/{remainder.denominator}"
    return f"{whole} {remainder.numerator}/{remainder.denominator}"


def _fmt_decimal(val: Fraction, places: int = 2) -> str:
    """Format a Fraction as a decimal string with specified places."""
    f = float(val)
    if f == int(f):
        return str(int(f))
    # Use enough places to show the value cleanly
    formatted = f"{f:.{places}f}"
    # Strip trailing zeros but keep at least one decimal place
    if '.' in formatted:
        formatted = formatted.rstrip('0').rstrip('.')
    return formatted


class Stem6NS4:
    """Generates ~20 variants for each of 6 stems from the 6.NS.4 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        """Create a seeded NumberGenerator for a specific stem+variant."""
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - NR (DOK 1, Easy)
    # Add fractions: e.g., 4 1/2 + 3 2/3 = ?
    # ================================================================

    def stem1_below_nr(self, variant_idx: int) -> GeneratedQuestion:
        """Below Proficiency - Add two mixed numbers (fractions only).

        Students add two positive mixed numbers.
        Difficulty: easy (fractions only, add/subtract only)
        """
        gen, rng = self._make_gen(1, variant_idx)

        # Generate two mixed numbers with manageable denominators
        a = gen.mixed_number(max_whole=9, max_denom=6)
        b = gen.mixed_number(max_whole=9, max_denom=6)
        answer = a + b

        a_str = _fmt_fraction(a)
        b_str = _fmt_fraction(b)
        answer_str = _fmt_fraction(answer)

        a_rn = RationalNumber(a, "mixed")
        b_rn = RationalNumber(b, "mixed")
        answer_rn = RationalNumber(answer, "mixed")

        stem_text = f"Add.\n\n{a_str} + {b_str}"
        stem_latex = f"Add.\n\n${a_rn.latex()} + {b_rn.latex()}$"

        # Worked solution showing common denominator
        from math import gcd
        lcd = (a.denominator * b.denominator) // gcd(a.denominator, b.denominator)
        a_frac_part = a - int(a)
        b_frac_part = b - int(b)
        a_new_num = a_frac_part.numerator * (lcd // a_frac_part.denominator) if a_frac_part != 0 else 0
        b_new_num = b_frac_part.numerator * (lcd // b_frac_part.denominator) if b_frac_part != 0 else 0

        worked = (
            f"Find a common denominator: LCD = {lcd}\n"
            f"{a_str} + {b_str}\n"
            f"= {int(a)} {a_new_num}/{lcd} + {int(b)} {b_new_num}/{lcd}\n"
            f"= {answer_str}"
        )

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
            answer_latex=f"${answer_rn.latex()}$",
            worked_solution=worked,
            context_scenario="fraction addition",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Below Proficiency - NR (DOK 1, Easy)
    # Subtract decimals: e.g., 42.80 - 13.55 = ?
    # ================================================================

    def stem2_below_nr(self, variant_idx: int) -> GeneratedQuestion:
        """Below Proficiency - Subtract two decimals.

        Students subtract two positive decimals.
        Difficulty: easy (decimals only, add/subtract only)
        """
        gen, rng = self._make_gen(2, variant_idx)

        # Generate two 2-place decimals; ensure a > b so result is positive
        a = gen.decimal_2place(20.00, 99.99)
        b = gen.decimal_2place(5.00, 50.00)
        if b >= a:
            a, b = b + gen.decimal_2place(10.00, 30.00), a
        answer = a - b

        a_str = f"{float(a):.2f}"
        b_str = f"{float(b):.2f}"
        answer_str = f"{float(answer):.2f}"

        stem_text = f"Subtract.\n\n{a_str} - {b_str}"
        stem_latex = f"Subtract.\n\n${a_str} - {b_str}$"

        worked = (
            f"  {a_str}\n"
            f"- {b_str}\n"
            f"--------\n"
            f"  {answer_str}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.NR,
                               Difficulty.EASY, 2, variant_idx)

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
            context_scenario="decimal subtraction",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - NR (DOK 2, Medium)
    # One-step word problem with fraction multiplication or division
    # ================================================================

    def stem3_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        """Approaching Proficiency - One-step fraction word problem.

        Real-world context requiring multiplication or division of fractions.
        Difficulty: medium (fractions only, any operation)
        """
        gen, rng = self._make_gen(3, variant_idx)
        name = pick_name(rng)

        # Choose multiply or divide
        operation = rng.choice(["multiply", "divide"])

        if operation == "multiply":
            # E.g., "A recipe calls for 2/3 cup of flour. Name wants to make 4 1/2 batches."
            frac_a = gen.proper_fraction(max_denom=6)
            mixed_b = gen.mixed_number(max_whole=5, max_denom=4)
            answer = frac_a * mixed_b

            a_str = _fmt_fraction(frac_a)
            b_str = _fmt_fraction(mixed_b)
            answer_str = _fmt_fraction(answer)

            a_rn = RationalNumber(frac_a, "fraction")
            b_rn = RationalNumber(mixed_b, "mixed")
            answer_rn = RationalNumber(answer, "mixed")

            contexts = [
                f"A recipe calls for {a_str} cups of sugar per batch. {name} wants to make {b_str} batches. How many cups of sugar does {name} need?",
                f"{name} can walk {a_str} miles in one hour. How far will {name} walk in {b_str} hours?",
                f"Each serving of juice requires {a_str} cups. {name} needs {b_str} servings. How many cups of juice does {name} need in all?",
                f"A garden plot is {a_str} acres wide. The plot is {b_str} acres long. What is the area of the garden in square acres?",
            ]
            stem_text = rng.choice(contexts)

            # Convert mixed to improper for worked solution
            b_imp_num = mixed_b.numerator
            b_imp_den = mixed_b.denominator
            worked = (
                f"Multiply: {a_str} x {b_str}\n"
                f"= {frac_a.numerator}/{frac_a.denominator} x {b_imp_num}/{b_imp_den}\n"
                f"= {answer.numerator}/{answer.denominator}\n"
                f"= {answer_str}"
            )
        else:
            # Division: e.g., "Name has 3 1/4 pounds to divide into bags of 1/2 pound each"
            mixed_a = gen.mixed_number(max_whole=5, max_denom=4)
            frac_b = gen.proper_fraction(max_denom=6)
            # Ensure frac_b is not too tiny
            while frac_b < Fraction(1, 6):
                frac_b = gen.proper_fraction(max_denom=6)
            answer = mixed_a / frac_b

            a_str = _fmt_fraction(mixed_a)
            b_str = _fmt_fraction(frac_b)
            answer_str = _fmt_fraction(answer)

            a_rn = RationalNumber(mixed_a, "mixed")
            b_rn = RationalNumber(frac_b, "fraction")
            answer_rn = RationalNumber(answer, "mixed")

            contexts = [
                f"{name} has {a_str} pounds of trail mix to divide into bags of {b_str} pound each. How many bags can {name} make?",
                f"A ribbon is {a_str} yards long. {name} cuts it into pieces that are {b_str} yard each. How many pieces does {name} get?",
                f"{name} has {a_str} gallons of paint. Each wall needs {b_str} gallon. How many walls can {name} paint?",
            ]
            stem_text = rng.choice(contexts)

            recip = Fraction(frac_b.denominator, frac_b.numerator)
            worked = (
                f"Divide: {a_str} / {b_str}\n"
                f"= {mixed_a.numerator}/{mixed_a.denominator} x {recip.numerator}/{recip.denominator}\n"
                f"= {answer.numerator}/{answer.denominator}\n"
                f"= {answer_str}"
            )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM,
            dok=2,
            item_type=ItemType.NR,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=answer_str,
            answer_latex=f"${answer_rn.latex()}$",
            worked_solution=worked,
            context_scenario=f"fraction {operation} word problem",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: Approaching Proficiency - MC (DOK 2, Medium)
    # One-step decimal word problem (multiply or divide)
    # ================================================================

    def stem4_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Approaching Proficiency - One-step decimal word problem (MC).

        Real-world context requiring multiplication or division of decimals.
        Difficulty: medium (decimals only, any operation)
        """
        gen, rng = self._make_gen(4, variant_idx)
        name = pick_name(rng)

        operation = rng.choice(["multiply", "divide"])

        if operation == "multiply":
            # e.g., "Each shirt costs $12.75. Name buys 4 shirts."
            unit_price = gen.money(3.00, 25.00)
            quantity = int(gen.whole_number(2, 9))
            answer = unit_price * quantity

            price_str = f"{float(unit_price):.2f}"
            answer_str = f"{float(answer):.2f}"

            contexts = [
                f"Each notebook costs ${price_str}. {name} buys {quantity} notebooks. What is the total cost?",
                f"{name} earns ${price_str} per hour. How much does {name} earn in {quantity} hours?",
                f"A bag of apples weighs {price_str} pounds. {name} buys {quantity} bags. What is the total weight in pounds?",
                f"Each bottle holds {price_str} liters. {name} has {quantity} bottles. How many liters does {name} have in all?",
            ]
            stem_text = rng.choice(contexts)

            # Distractors from common errors
            distractors = set()
            distractors.add(float(unit_price) + quantity)                # added instead
            distractors.add(float(unit_price) * (quantity + 1))          # one extra
            distractors.add(float(unit_price) * (quantity - 1))          # one fewer
            distractors.add(round(float(unit_price) * quantity / 10, 2)) # decimal place error
            distractors.discard(float(answer))

            worked = (
                f"Multiply: ${price_str} x {quantity}\n"
                f"= ${answer_str}"
            )

        else:
            # e.g., "Name has $45.60 to buy pens at $3.80 each."
            unit_price = gen.money(2.00, 15.00)
            quantity = int(gen.whole_number(3, 8))
            total = unit_price * quantity

            total_str = f"{float(total):.2f}"
            price_str = f"{float(unit_price):.2f}"
            answer = unit_price  # reframe: total / quantity = unit_price
            # Actually, let's ask "how many items" -> answer = quantity
            answer = Fraction(quantity)
            answer_str = str(quantity)

            contexts = [
                f"{name} has ${total_str} to spend on pencils that cost ${price_str} each. How many pencils can {name} buy?",
                f"A rope that is {total_str} feet long is cut into pieces of {price_str} feet each. How many pieces are there?",
                f"{name} divides ${total_str} equally among friends, giving each friend ${price_str}. How many friends does {name} have?",
            ]
            stem_text = rng.choice(contexts)

            distractors = set()
            distractors.add(quantity + 1)
            distractors.add(quantity - 1)
            distractors.add(quantity * 2)
            distractors.add(round(float(total) + float(unit_price), 2))
            distractors.discard(float(answer))

            worked = (
                f"Divide: {total_str} / {price_str}\n"
                f"= {answer_str}"
            )

        # Build MC choices
        distractors = [d for d in distractors if d > 0 and d != float(answer)][:3]
        while len(distractors) < 3:
            d = float(answer) + rng.choice([-5, -2, 2, 5, 10])
            if d > 0 and d != float(answer) and d not in distractors:
                distractors.append(d)

        def _fmt_choice(v):
            if v == int(v):
                return str(int(v))
            return f"{v:.2f}"

        all_options = [(_fmt_choice(float(answer)), True)]
        for d in distractors[:3]:
            all_options.append((_fmt_choice(d), False))
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

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM,
            dok=2,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=correct_letter,
            answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices,
            context_scenario=f"decimal {operation} word problem",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: At Proficiency - NR (DOK 2, Difficult)
    # Two-step problem mixing fractions and decimals
    # ================================================================

    def stem5_at_mp(self, variant_idx: int) -> GeneratedQuestion:
        """At Proficiency - Multi-part two-step problem mixing fractions and decimals.

        Part A: Calculate the intermediate result.
        Part B: Use the intermediate result to find the final answer.
        Difficulty: difficult (mix of fractions and decimals, any operation)
        """
        gen, rng = self._make_gen(5, variant_idx)
        name = pick_name(rng)

        scenario = rng.choice(["earn_spend", "recipe_leftover", "distance_two_parts"])

        if scenario == "earn_spend":
            rate = gen.money(7.00, 15.00)
            hours = gen.mixed_number(max_whole=4, max_denom=4)
            spending = gen.money(5.00, 20.00)
            earnings = rate * hours
            answer = earnings - spending
            while answer <= 0:
                spending = gen.money(2.00, float(earnings) - 1.00)
                answer = earnings - spending

            rate_str = f"{float(rate):.2f}"
            hours_str = _fmt_fraction(hours)
            spending_str = f"{float(spending):.2f}"
            earnings_str = f"{float(earnings):.2f}"
            answer_str = f"{float(answer):.2f}"

            stem_text = (
                f"{name} earns ${rate_str} per hour and works for "
                f"{hours_str} hours. Then {name} spends ${spending_str} on lunch.\n\n"
                f"Part A: How much does {name} earn before lunch?\n\n"
                f"Part B: How much money does {name} have after buying lunch?"
            )

            part_a = QuestionPart(
                label="Part A",
                prompt=f"How much does {name} earn before lunch?",
                prompt_latex=f"How much does {name} earn before lunch?",
                answer=f"${earnings_str}",
                answer_latex=f"\\${earnings_str}",
                item_type=ItemType.NR,
            )
            part_b = QuestionPart(
                label="Part B",
                prompt=f"How much money does {name} have after buying lunch?",
                prompt_latex=f"How much money does {name} have after buying lunch?",
                answer=f"${answer_str}",
                answer_latex=f"\\${answer_str}",
                item_type=ItemType.NR,
            )

            worked = (
                f"Part A: ${rate_str} x {hours_str} = ${earnings_str}\n"
                f"Part B: ${earnings_str} - ${spending_str} = ${answer_str}"
            )

        elif scenario == "recipe_leftover":
            total = gen.decimal_1place(3.0, 10.0)
            per_serving = gen.proper_fraction(max_denom=4)
            servings = int(gen.whole_number(2, 6))
            used = per_serving * servings
            while total <= used:
                total = total + gen.decimal_1place(2.0, 5.0)
            answer = total - used

            total_str = _fmt_decimal(total)
            per_str = _fmt_fraction(per_serving)
            used_str = _fmt_decimal(used)
            answer_val = float(answer)
            answer_str = f"{answer_val:.2f}" if answer_val != int(answer_val) else str(int(answer_val))

            stem_text = (
                f"{name} has {total_str} cups of sugar. A recipe uses "
                f"{per_str} cup of sugar per serving. {name} makes "
                f"{servings} servings.\n\n"
                f"Part A: How many cups of sugar does {name} use?\n\n"
                f"Part B: How many cups of sugar does {name} have left?"
            )

            part_a = QuestionPart(
                label="Part A",
                prompt=f"How many cups of sugar does {name} use?",
                prompt_latex=f"How many cups of sugar does {name} use?",
                answer=used_str,
                answer_latex=used_str,
                item_type=ItemType.NR,
            )
            part_b = QuestionPart(
                label="Part B",
                prompt=f"How many cups of sugar does {name} have left?",
                prompt_latex=f"How many cups of sugar does {name} have left?",
                answer=answer_str,
                answer_latex=answer_str,
                item_type=ItemType.NR,
            )

            worked = (
                f"Part A: {per_str} x {servings} = {used_str} cups\n"
                f"Part B: {total_str} - {used_str} = {answer_str} cups"
            )

        else:  # distance_two_parts
            part1 = gen.decimal_1place(1.0, 5.0)
            part2 = gen.mixed_number(max_whole=3, max_denom=4)
            walked = part1 + part2
            goal = walked + gen.decimal_1place(1.0, 5.0)
            answer = goal - walked

            part1_str = _fmt_decimal(part1)
            part2_str = _fmt_fraction(part2)
            goal_str = _fmt_decimal(goal)
            walked_str = _fmt_decimal(walked)
            answer_str = _fmt_decimal(answer)

            stem_text = (
                f"{name} wants to walk {goal_str} miles today. "
                f"In the morning, {name} walked {part1_str} miles. "
                f"In the afternoon, {name} walked {part2_str} miles.\n\n"
                f"Part A: How many miles has {name} walked so far?\n\n"
                f"Part B: How many more miles does {name} need to walk?"
            )

            part_a = QuestionPart(
                label="Part A",
                prompt=f"How many miles has {name} walked so far?",
                prompt_latex=f"How many miles has {name} walked so far?",
                answer=f"{walked_str} miles",
                answer_latex=f"{walked_str} miles",
                item_type=ItemType.NR,
            )
            part_b = QuestionPart(
                label="Part B",
                prompt=f"How many more miles does {name} need to walk?",
                prompt_latex=f"How many more miles does {name} need to walk?",
                answer=f"{answer_str} miles",
                answer_latex=f"{answer_str} miles",
                item_type=ItemType.NR,
            )

            worked = (
                f"Part A: {part1_str} + {part2_str} = {walked_str} miles\n"
                f"Part B: {goal_str} - {walked_str} = {answer_str} miles"
            )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MP,
                               Difficulty.DIFFICULT, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT,
            dok=2,
            item_type=ItemType.MP,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"Part A: see solution; Part B: {answer_str}",
            answer_latex=f"Part A: see solution; Part B: {answer_str}",
            worked_solution=worked,
            parts=[part_a, part_b],
            context_scenario=scenario,
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 6: Above Proficiency - MP (DOK 3, Medium)
    # Evaluate reasoning about a two-step decimal problem
    # ================================================================

    def stem6_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        """Above Proficiency - Multi-part: evaluate reasoning about a decimal problem.

        Part A: Identify the error in a student's work on a two-step decimal problem.
        Part B: Solve the problem correctly.
        Difficulty: medium (decimals, any operation)
        """
        gen, rng = self._make_gen(6, variant_idx)
        name = pick_name(rng)
        student_name = pick_name(rng)
        while student_name == name:
            student_name = pick_name(rng)

        # Generate a two-step decimal problem
        # Pattern: buy multiple items at a price, then apply a flat amount change
        unit_price = gen.money(3.00, 12.00)
        quantity = int(gen.whole_number(3, 8))
        extra = gen.money(2.00, 10.00)
        total = unit_price * quantity + extra

        price_str = f"{float(unit_price):.2f}"
        extra_str = f"{float(extra):.2f}"
        total_str = f"{float(total):.2f}"
        subtotal_str = f"{float(unit_price * quantity):.2f}"

        # Choose an error type
        error_type = rng.choice(["added_instead", "wrong_multiply", "forgot_step"])

        if error_type == "added_instead":
            # Student added unit_price + quantity instead of multiplying
            wrong_subtotal = float(unit_price) + quantity
            wrong_answer = wrong_subtotal + float(extra)
            wrong_str = f"{wrong_answer:.2f}"
            error_desc = (
                f"{student_name} added ${price_str} + {quantity} = "
                f"${float(unit_price) + quantity:.2f} instead of multiplying "
                f"${price_str} x {quantity} = ${subtotal_str}."
            )
        elif error_type == "wrong_multiply":
            # Student misplaced decimal in multiplication
            wrong_subtotal = float(unit_price) * quantity * 10
            wrong_answer = wrong_subtotal + float(extra)
            wrong_str = f"{wrong_answer:.2f}"
            error_desc = (
                f"{student_name} got ${wrong_subtotal:.2f} for the multiplication "
                f"instead of ${subtotal_str}. The decimal point was misplaced."
            )
        else:
            # Student forgot to add the extra amount
            wrong_answer = float(unit_price * quantity)
            wrong_str = f"{wrong_answer:.2f}"
            error_desc = (
                f"{student_name} correctly multiplied ${price_str} x {quantity} = "
                f"${subtotal_str} but forgot to add the ${extra_str}."
            )

        stem_text = (
            f"{name} buys {quantity} items at ${price_str} each and pays an "
            f"additional ${extra_str} for shipping.\n\n"
            f"{student_name} says the total cost is ${wrong_str}.\n\n"
            f"Part A: Explain the error in {student_name}'s reasoning.\n\n"
            f"Part B: What is the correct total cost?"
        )

        part_a = QuestionPart(
            label="Part A",
            prompt=f"Explain the error in {student_name}'s reasoning.",
            prompt_latex=f"Explain the error in {student_name}'s reasoning.",
            answer=error_desc,
            answer_latex=error_desc,
            item_type=ItemType.NR,
        )
        part_b = QuestionPart(
            label="Part B",
            prompt=f"What is the correct total cost?",
            prompt_latex=f"What is the correct total cost?",
            answer=f"${total_str}",
            answer_latex=f"\\${total_str}",
            item_type=ItemType.NR,
        )

        worked = (
            f"Part A: {error_desc}\n\n"
            f"Part B:\n"
            f"  Step 1: ${price_str} x {quantity} = ${subtotal_str}\n"
            f"  Step 2: ${subtotal_str} + ${extra_str} = ${total_str}\n"
            f"  Correct total: ${total_str}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.MEDIUM, 6, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.MEDIUM,
            dok=3,
            item_type=ItemType.MP,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"Part A: {error_desc} Part B: ${total_str}",
            answer_latex=f"Part A: {error_desc} Part B: \\${total_str}",
            worked_solution=worked,
            parts=[part_a, part_b],
            context_scenario="evaluate reasoning about decimal computation",
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6,
            variant_index=variant_idx
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        """Generate all variants for all 6 stems.

        Returns ~120 questions (6 stems x 20 variants).
        """
        all_questions = []

        stem_methods = [
            self.stem1_below_nr,
            self.stem2_below_nr,
            self.stem3_approaching_nr,
            self.stem4_approaching_mc,
            self.stem5_at_mp,
            self.stem6_above_mp,
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
            2: self.stem2_below_nr,
            3: self.stem3_approaching_nr,
            4: self.stem4_approaching_mc,
            5: self.stem5_at_mp,
            6: self.stem6_above_mp,
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
    print("Generating 6.NS.4 question variants...")
    print("=" * 60)

    generator = Stem6NS4(seed=42)
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
