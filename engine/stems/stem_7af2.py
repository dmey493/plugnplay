"""
Stem generator for 7.AF.2:
  Solve real-world problems with rational numbers by using one or two operations.

Content Limits:
  - Rational numbers only
  - One or two operations
  - No percents
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: addition/subtraction with integers, one operation
  Medium: add/sub with fractions/decimals, or mult with integers, up to 2 operations
  Difficult: mult/div with fractions or decimals, multiple operations

5 Stems from the Item Spec:
  Stem 1 (Below-MC):     Select expression for price change over time (DOK 3, Medium)
  Stem 2 (Approaching-NR): Unit price multiplication with mixed number (DOK 2, Medium)
  Stem 3 (At-NR):        Multi-step price tracking with table (DOK 2, Medium)
  Stem 4 (At-NR):        Multi-step fraction work problem (DOK 3, Difficult)
  Stem 5 (Above-NR):     Counterexample to disprove a claim (DOK 2, Easy)
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
    CONTEXTS_7AF2_PRICE_CHANGE, CONTEXTS_7AF2_UNIT_PRICE,
    CONTEXTS_7AF2_FRACTION_WORK, pick_name
)


STANDARD_CODE = "7.AF.2"
VARIANTS_PER_STEM = 20


def _money(val: Fraction) -> str:
    """Format a Fraction as a dollar amount."""
    f = float(val)
    if f < 0:
        return f"-${abs(f):.2f}"
    return f"${f:.2f}"


def _change_str(val: Fraction) -> str:
    """Format a price change as +$X.XX or -$X.XX."""
    f = float(val)
    if f >= 0:
        return f"+${f:.2f}"
    return f"-${abs(f):.2f}"


class Stem7AF2:
    """Generates ~20 variants for each of 5 stems from the 7.AF.2 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        """Create a seeded NumberGenerator for a specific stem+variant."""
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - Multiple Choice (DOK 3, Medium)
    # Price changes over months shown in a table. Student selects the
    # expression that finds the starting price given the ending price.
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Below Proficiency - Select expression for price change reversal.

        Table shows price changes over 3 months. Given end price, student
        selects the expression to find the starting price.
        Difficulty: medium (decimals, two operations)
        """
        gen, rng = self._make_gen(1, variant_idx)

        ctx = rng.choice(CONTEXTS_7AF2_PRICE_CHANGE)
        item_name = ctx["item"]

        # Generate 3 monthly changes (positive = increase, negative = decrease)
        months = ["January", "February", "March"]
        if rng.random() < 0.5:
            months = ["August", "September", "October"]

        changes = []
        for i in range(3):
            # Generate change amount (decimals, 0.10 to 0.50)
            amt = gen.money(Fraction(10, 100), Fraction(50, 100))
            direction = rng.choice([1, -1])
            changes.append(direction * amt)

        # Compute start -> end price
        base = Fraction(ctx["base_price"]).limit_denominator(100)
        # Randomize base a bit
        base = base + gen.money(Fraction(0), Fraction(100, 100))
        end_price = base + sum(changes)

        # Build table rows
        table_lines = []
        for i, month in enumerate(months):
            c = changes[i]
            if c >= 0:
                desc = f"+${float(c):.2f}"
            else:
                desc = f"-${float(abs(c)):.2f}"
            table_lines.append(f"  {month}: {desc}")

        table_text = "\n".join(table_lines)

        # Correct expression: end_price - change3 - change2 - change1
        # (undo each change in reverse order)
        correct_parts = [_money(end_price)]
        for c in reversed(changes):
            if c >= 0:
                correct_parts.append(f"- ${float(c):.2f}")
            else:
                correct_parts.append(f"+ ${float(abs(c)):.2f}")

        correct_expr = " ".join(correct_parts)

        # Verify
        start_check = end_price - sum(changes)
        assert start_check == base, f"Math error: {start_check} != {base}"

        # Distractors
        distractors = []

        # Wrong 1: add all changes instead of reversing
        d1_parts = [_money(end_price)]
        for c in changes:
            if c >= 0:
                d1_parts.append(f"+ ${float(c):.2f}")
            else:
                d1_parts.append(f"- ${float(abs(c)):.2f}")
        d1 = " ".join(d1_parts)
        if d1 != correct_expr:
            distractors.append(d1)

        # Wrong 2: just sum the changes (no end price)
        d2_parts = []
        for i, c in enumerate(changes):
            if i == 0:
                d2_parts.append(f"${float(abs(c)):.2f}" if c >= 0 else f"-${float(abs(c)):.2f}")
            else:
                if c >= 0:
                    d2_parts.append(f"+ ${float(c):.2f}")
                else:
                    d2_parts.append(f"- ${float(abs(c)):.2f}")
        d2 = " ".join(d2_parts)
        if d2 != correct_expr and d2 not in distractors:
            distractors.append(d2)

        # Wrong 3: reverse sign only on some changes
        d3_parts = [_money(end_price)]
        for i, c in enumerate(reversed(changes)):
            if i == 0:
                # Correctly reverse first
                if c >= 0:
                    d3_parts.append(f"- ${float(c):.2f}")
                else:
                    d3_parts.append(f"+ ${float(abs(c)):.2f}")
            else:
                # Don't reverse rest (wrong)
                if c >= 0:
                    d3_parts.append(f"+ ${float(c):.2f}")
                else:
                    d3_parts.append(f"- ${float(abs(c)):.2f}")
        d3 = " ".join(d3_parts)
        if d3 != correct_expr and d3 not in distractors:
            distractors.append(d3)

        # Pad if needed
        while len(distractors) < 3:
            delta = gen.money(Fraction(1, 100), Fraction(20, 100))
            wrong_end = end_price + delta
            d_parts = [_money(wrong_end)]
            for c in reversed(changes):
                if c >= 0:
                    d_parts.append(f"- ${float(c):.2f}")
                else:
                    d_parts.append(f"+ ${float(abs(c)):.2f}")
            d = " ".join(d_parts)
            if d != correct_expr and d not in distractors:
                distractors.append(d)

        distractors = distractors[:3]

        stem_text = (
            f"The change in the price of {item_name} over three months "
            f"is recorded in the table below.\n\n"
            f"{table_text}\n\n"
            f"The price at the end of {months[2]} was {_money(end_price)}.\n\n"
            f"Which expression could be used to find the price at the beginning of {months[0]}?"
        )

        choices = shuffle_choices(correct_expr, correct_expr, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"To find the starting price, reverse each change:\n"
            f"  Start with end price: {_money(end_price)}\n"
        )
        running = end_price
        for i, month in enumerate(reversed(months)):
            c = changes[2 - i]
            if c >= 0:
                running -= c
                worked += f"  Undo {month} (+${float(c):.2f}): subtract -> {_money(running)}\n"
            else:
                running -= c
                worked += f"  Undo {month} (-${float(abs(c)):.2f}): add -> {_money(running)}\n"
        worked += f"  Starting price = {_money(base)}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.MEDIUM, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.MEDIUM,
            dok=3,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct_expr}",
            answer_latex=f"{correct_letter}) {correct_expr}",
            worked_solution=worked,
            choices=choices,
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - Numeric Response (DOK 2, Medium)
    # Unit price multiplication with mixed number quantity.
    # "1 3/4 pounds of tomatoes at $2.35/lb = ?"
    # ================================================================

    def stem2_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        """Approaching Proficiency - Unit price multiplication.

        Mixed number quantity times decimal unit price.
        Student computes the total cost.
        Difficulty: medium (mixed number x decimal)
        """
        gen, rng = self._make_gen(2, variant_idx)

        ctx = rng.choice(CONTEXTS_7AF2_UNIT_PRICE)
        name = pick_name(rng)

        # Generate quantity as mixed number: whole + fraction. Use a terminating
        # fraction (halves or quarters) so the money product has no repeating
        # decimal -- 7.AF.2 is a non-calculator standard, so 4 2/3 x a price
        # (which forces repeating decimals) is exactly what we want to avoid.
        whole_part = gen.small_whole(1, 4)
        frac_part = rng.choice([Fraction(1, 2), Fraction(1, 4), Fraction(3, 4)])
        quantity = whole_part + frac_part

        # Unit price in cents, divisible by the fraction's denominator so the
        # total is exact to the cent (e.g. 2 1/4 lb x $3.40 = $7.65).
        den = frac_part.denominator
        cents = rng.randint(100, 500)
        cents -= cents % den
        unit_price = Fraction(cents, 100)

        # Ensure clean multiplication
        total = quantity * unit_price

        # Format display
        qty_rn = RationalNumber(quantity, "mixed")
        price_str = _money(unit_price)

        # Format answer as money
        answer_val = float(total)
        # Round to 2 decimal places for money
        answer_str = f"${answer_val:.2f}"

        stem_text = (
            f"{name} has a recipe that uses {qty_rn.display()} {ctx['unit_plural']} of "
            f"{ctx['item']}. Each {ctx['unit']} of {ctx['item']} costs {price_str}.\n\n"
            f"What is the total cost of the {ctx['item']} {name} needs?"
        )

        # Worked solution
        worked = (
            f"Multiply quantity by unit price:\n"
            f"  {qty_rn.display()} x {price_str}\n"
            f"  = {float(quantity):g} x ${float(unit_price):.2f}\n"
            f"  = {answer_str}"
        )

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
            answer_text=answer_str,
            answer_latex=answer_str,
            worked_solution=worked,
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: At Proficiency - Numeric Response (DOK 2, Medium)
    # Price changes over years in a table. Given starting price,
    # compute ending price by adding all changes.
    # ================================================================

    def stem3_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        """At Proficiency - Multi-step price tracking.

        Table of year-over-year price changes. Given starting price,
        student adds all changes to find ending price.
        Difficulty: medium (decimals, multiple additions)
        """
        gen, rng = self._make_gen(3, variant_idx)

        ctx = rng.choice(CONTEXTS_7AF2_PRICE_CHANGE)
        item_name = ctx["item"]

        # Generate 3-4 yearly changes
        n_years = rng.choice([3, 4])
        start_year = rng.choice([2018, 2019, 2020])
        years = [start_year + i for i in range(n_years)]

        changes = []
        for _ in range(n_years):
            amt = gen.money(Fraction(5, 100), Fraction(45, 100))
            direction = rng.choice([1, -1])
            changes.append(direction * amt)

        # Starting price
        base = Fraction(ctx["base_price"]).limit_denominator(100)
        base = base + gen.money(Fraction(0), Fraction(80, 100))

        end_price = base + sum(changes)

        # Build table
        table_lines = []
        for i, year in enumerate(years):
            c = changes[i]
            table_lines.append(f"  {year}: {_change_str(c)}")

        table_text = "\n".join(table_lines)

        answer_str = _money(end_price)

        stem_text = (
            f"The change in the price of {item_name} from "
            f"{years[0]} to {years[-1]} is shown in the table.\n\n"
            f"{table_text}\n\n"
            f"In {years[0] - 1}, the price of {item_name} was {_money(base)}.\n\n"
            f"What was the price of {item_name} at the end of {years[-1]}?"
        )

        # Worked solution
        worked = f"Start: {_money(base)}\n"
        running = base
        for i, year in enumerate(years):
            c = changes[i]
            running += c
            worked += f"  After {year} ({_change_str(c)}): {_money(running)}\n"
        worked += f"Final price: {answer_str}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.MEDIUM, 3, variant_idx)

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
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At Proficiency - Numeric Response (DOK 3, Difficult)
    # Multi-step fraction word problem: "Mow 2/3 of a 12-acre field
    # at 1/2 acre per 15 minutes."
    # ================================================================

    def stem4_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        """At Proficiency - Multi-step fraction word problem.

        Student computes a fractional part of a total, then divides by
        a fractional rate to find time.
        Difficulty: difficult (fractions throughout)
        """
        gen, rng = self._make_gen(4, variant_idx)

        ctx = rng.choice(CONTEXTS_7AF2_FRACTION_WORK)
        name = pick_name(rng)

        # Generate the fraction of total to work on
        frac_of_choices = [Fraction(1, 3), Fraction(2, 3), Fraction(1, 2),
                           Fraction(3, 4), Fraction(1, 4), Fraction(2, 5)]
        frac_of = rng.choice(frac_of_choices)

        # Generate total (multiple of denominator for clean math)
        denom = frac_of.denominator
        mult = rng.randint(2, 6)
        total = denom * mult  # guaranteed that frac_of * total is whole or clean

        # Generate rate fraction
        rate_choices = [Fraction(1, 2), Fraction(1, 3), Fraction(1, 4),
                        Fraction(2, 3), Fraction(3, 4)]
        rate_frac = rng.choice(rate_choices)

        # Time per unit of rate
        time_per_choices = [10, 15, 20, 30]
        time_per = rng.choice(time_per_choices)

        # Compute answer
        amount_to_work = frac_of * total  # how much to do
        units_of_work = amount_to_work / rate_frac  # how many rate-periods
        total_time = units_of_work * time_per  # total time in minutes

        # Format fractions
        frac_of_rn = RationalNumber(frac_of, "fraction")
        rate_rn = RationalNumber(rate_frac, "fraction")

        answer_val = int(total_time) if total_time.denominator == 1 else float(total_time)
        answer_str = str(answer_val)

        stem_text = ctx["setup"].format(
            name=name, frac_of=frac_of_rn.display(),
            total=total, rate_frac=rate_rn.display(), time_per=time_per
        ) + "\n\n" + ctx["question"].format(name=name)

        worked = (
            f"Step 1: Find how much to work on.\n"
            f"  {frac_of_rn.display()} x {total} = {float(amount_to_work):g}\n\n"
            f"Step 2: Find how many {time_per}-minute periods.\n"
            f"  {float(amount_to_work):g} / {rate_rn.display()} = {float(units_of_work):g} periods\n\n"
            f"Step 3: Find total time.\n"
            f"  {float(units_of_work):g} x {time_per} = {answer_str} minutes"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.DIFFICULT, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT,
            dok=3,
            item_type=ItemType.NR,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=answer_str,
            answer_latex=answer_str,
            worked_solution=worked,
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above Proficiency - Numeric Response (DOK 2, Easy)
    # "The expression -2x - 4. Student claims it's always negative.
    #  Find a counterexample."
    # ================================================================

    def stem5_above_nr(self, variant_idx: int) -> GeneratedQuestion:
        """Above Proficiency - Find counterexample to disprove claim.

        Given an expression like -ax - b, student claims it's always negative.
        Find a value of x that makes it non-negative (>= 0).
        Difficulty: easy (integers)
        """
        gen, rng = self._make_gen(5, variant_idx)

        var = "x"

        # Generate expression: -a*x - b where a > 0, b > 0
        a = int(gen.small_whole(2, 6))
        b = int(gen.small_whole(1, 10))

        # Expression: -ax - b
        # This is >= 0 when x <= -b/a
        # So any x <= floor(-b/a) works as counterexample
        boundary = Fraction(-b, a)

        # Range for x: integers from -5 to 5 (or larger)
        lower = -a - b  # guaranteed to give negative x values
        upper = a + b
        # Ensure range is reasonable
        lower = max(lower, -10)
        upper = min(upper, 10)

        # Valid counterexamples: integers where -a*x - b >= 0
        valid_x = []
        for test_x in range(lower, upper + 1):
            val = -a * test_x - b
            if val >= 0:
                valid_x.append(test_x)

        # There should always be at least one (negative x values)
        if not valid_x:
            # Fallback: x = -(b+a)//a will always work
            valid_x = [-(b + a) // a]

        # Pick one as the "sample answer" and list others
        sample_answer = valid_x[0]
        answer_str = str(sample_answer)
        all_answers = ", ".join(str(v) for v in valid_x)

        stem_text = (
            f"An expression is given:\n\n"
            f"  -{a}{var} - {b}\n\n"
            f"The value of {var} can be any integer from {lower} to {upper}.\n\n"
            f"A student states that because both terms, -{a}{var} and -{b}, "
            f"are negative, the expression will always have a negative value.\n\n"
            f"Enter a value of {var} that proves the student's statement is false."
        )

        worked = (
            f"The expression -{a}{var} - {b} is non-negative when {var} <= {float(boundary):g}.\n"
            f"For example, if {var} = {sample_answer}:\n"
            f"  -{a}({sample_answer}) - {b} = {-a * sample_answer} - {b} = {-a * sample_answer - b}\n"
            f"This value is not negative, so the student is wrong.\n"
            f"Valid answers include: {all_answers}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.NR,
                               Difficulty.EASY, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.EASY,
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
    # MAIN GENERATION METHOD
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        """Generate all variants for all 5 stems.

        Returns ~100 questions (5 stems x 20 variants).
        """
        all_questions = []

        stem_methods = [
            self.stem1_below_mc,
            self.stem2_approaching_nr,
            self.stem3_at_nr,
            self.stem4_at_nr,
            self.stem5_above_nr,
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
            1: self.stem1_below_mc,
            2: self.stem2_approaching_nr,
            3: self.stem3_at_nr,
            4: self.stem4_at_nr,
            5: self.stem5_above_nr,
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
    print("Generating 7.AF.2 question variants...")
    print("=" * 60)

    generator = Stem7AF2(seed=42)
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
