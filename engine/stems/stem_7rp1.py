"""
Stem generator for 7.RP.1:
  Identify the unit rate or constant of proportionality in tables, graphs,
  equations, and verbal descriptions of proportional relationships.

Content Limits:
  - Rational numbers
  - Ratios can be expressed as fractions, colon, or words
  - Limit to same units within the item
  - Equations in form y = kx where k is a positive rational number
  - Items should not require creating a table/graph/equation, only interpreting
  - Unit rate labels not required, only numerical answers
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: whole numbers resulting in whole-number unit rate
  Medium: whole numbers resulting in non-whole-number unit rate
  Difficult: more than one proportional relationship or non-whole numbers

5 Stems from the Item Spec:
  Stem 1 (Below-MC):  Identify which table/description is proportional (DOK 2, easy)
  Stem 2 (Approaching-MC): Identify a unit rate statement (DOK 1, easy)
  Stem 3 (At-NR):     Calculate unit rate from a verbal description (DOK 1, medium)
  Stem 4 (At-NR):     Calculate unit rate involving fractions (DOK 1, difficult)
  Stem 5 (Above-MP):  Identify equation y=kx and apply to find a value (DOK 3, medium)
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
from engine.context_pools import pick_name, CONTEXTS_7RP1


STANDARD_CODE = "7.RP.1"
VARIANTS_PER_STEM = 20


def _fmt(val):
    """Format a Fraction or number for display."""
    if isinstance(val, Fraction):
        f = float(val)
        if f == int(f):
            return str(int(f))
        return f"{f:g}"
    if isinstance(val, float):
        if val == int(val):
            return str(int(val))
        return f"{val:g}"
    return str(val)


def _fmt_frac(val):
    """Format a Fraction as a fraction string like '1/14' or a whole number."""
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return str(int(val))
        return f"{val.numerator}/{val.denominator}"
    return str(val)


def _fmt_money(val):
    """Format a value as dollars with 2 decimal places."""
    f = float(val) if isinstance(val, Fraction) else val
    if f == int(f):
        return f"${int(f)}"
    return f"${f:.2f}"


class Stem7RP1:
    """Generates ~20 variants for each of 5 stems from the 7.RP.1 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 2, Easy)
    # Identify which description represents a proportional relationship
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)
        name = pick_name(rng)

        # One proportional, three non-proportional descriptions
        rate = rng.randint(3, 15)
        proportional_options = [
            f"A gym membership costs ${rate} per month.",
            f"{name} earns ${rate} per hour at a part-time job.",
            f"A printer prints {rate} pages per minute.",
            f"A car uses {rate} gallons of gas per 100 miles.",
            f"{name} reads {rate} pages every day.",
            f"A store charges ${rate} per pound of fruit.",
        ]

        flat = rng.randint(5, 30)
        per = rng.randint(2, 10)
        deposit = rng.randint(20, 100)
        non_proportional_options = [
            f"A cleaning company charges ${per} per hour plus a ${flat} service fee.",
            f"{name} pays a ${deposit} deposit and ${per} per hour to rent a car.",
            f"A student orders two pizzas and pays a delivery fee.",
            f"A phone plan costs ${flat} per month plus ${per} per gigabyte of data.",
            f"{name} pays ${flat} for a base fare plus ${per} per mile in a taxi.",
            f"A video streaming service costs ${flat} monthly plus ${per} per movie rented.",
        ]

        correct = rng.choice(proportional_options)
        distractors = rng.sample(non_proportional_options, 3)

        all_options = [(correct, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = "Choose the description that represents a proportional relationship."

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=(
                f"A proportional relationship has a constant rate with no added fee or starting value. "
                f"'{correct}' is proportional because the total depends only on multiplying by the rate."
            ),
            choices=choices, context_scenario="identify proportional relationship",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - MC (DOK 1, Easy)
    # Identify which statement represents a unit rate
    # ================================================================

    def stem2_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)
        name = pick_name(rng)

        # Generate numbers for the ratio
        unit_rate = rng.randint(2, 12)
        multiplier = rng.randint(2, 5)
        total_qty = unit_rate * multiplier

        rate_contexts = [
            {
                "unit_stmt": f"${unit_rate} for 1 apple",
                "distractors": [
                    f"${total_qty} for {multiplier} apples",
                    f"${multiplier} for {total_qty} apples",
                    f"${unit_rate + multiplier} for 2 apples",
                ]
            },
            {
                "unit_stmt": f"${unit_rate} for 1 pound",
                "distractors": [
                    f"${total_qty} for {multiplier} pounds",
                    f"${multiplier} for {unit_rate} pounds",
                    f"${unit_rate * 2} for 3 pounds",
                ]
            },
            {
                "unit_stmt": f"{unit_rate} miles in 1 hour",
                "distractors": [
                    f"{total_qty} miles in {multiplier} hours",
                    f"{multiplier} miles in {unit_rate} hours",
                    f"{total_qty + unit_rate} miles total",
                ]
            },
            {
                "unit_stmt": f"{unit_rate} pages in 1 minute",
                "distractors": [
                    f"{total_qty} pages in {multiplier} minutes",
                    f"{multiplier} pages in {unit_rate} minutes",
                    f"{total_qty} pages total",
                ]
            },
        ]

        ctx = rng.choice(rate_contexts)
        correct = ctx["unit_stmt"]
        distractors = ctx["distractors"]

        all_options = [(correct, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = "Which statement represents a unit rate?"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=(
                f"A unit rate compares a quantity to exactly 1 unit. "
                f"'{correct}' is the unit rate because it uses '1' as the denominator of the comparison."
            ),
            choices=choices, context_scenario="identify unit rate statement",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: At Proficiency - NR (DOK 1, Medium)
    # Calculate the unit rate from a verbal description
    # (whole numbers that result in a non-whole unit rate)
    # ================================================================

    def stem3_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)
        name = pick_name(rng)

        # Pick context
        ctx = rng.choice(CONTEXTS_7RP1)

        # Generate numbers: whole numbers that do NOT divide evenly
        # to make the unit rate a non-whole number (medium difficulty)
        for _ in range(50):
            divisor = rng.randint(3, 8)
            total = rng.randint(divisor + 1, divisor * 15)
            if total % divisor != 0:
                break

        unit_rate = Fraction(total, divisor)
        ur_str = _fmt(unit_rate)

        # Build the verbal description from context
        desc = ctx["desc"].format(
            name=name, total=total, hours=divisor,
            months=divisor, items=total, pages=divisor
        )

        stem_text = (
            f"{desc}\n\n"
            f"What is the unit rate, in {ctx['unit']}?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=ur_str, answer_latex=ur_str,
            worked_solution=f"Unit rate = {total} / {divisor} = {ur_str} {ctx['unit']}",
            context_scenario="calculate unit rate from verbal description",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At Proficiency - NR (DOK 1, Difficult)
    # Calculate unit rate involving fractions
    # (e.g., "A bus travels 1/2 mile in 7 minutes")
    # ================================================================

    def stem4_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)
        name = pick_name(rng)

        # Generate a fractional distance/amount and a whole-number time
        numerators = [1, 1, 2, 3, 1, 3]
        denominators = [2, 3, 3, 4, 4, 5]
        idx = rng.randint(0, len(numerators) - 1)
        frac_num = numerators[idx]
        frac_den = denominators[idx]
        frac_val = Fraction(frac_num, frac_den)

        time_val = rng.randint(3, 12)
        unit_rate = frac_val / time_val
        ur_frac_str = _fmt_frac(unit_rate)

        contexts = [
            {
                "desc": f"A city bus travels {frac_num}/{frac_den} of a mile in {time_val} minutes.",
                "question": "What is the unit rate, in miles per minute?",
                "unit": "miles per minute",
            },
            {
                "desc": f"{name} uses {frac_num}/{frac_den} of a gallon of paint in {time_val} minutes.",
                "question": "What is the unit rate, in gallons per minute?",
                "unit": "gallons per minute",
            },
            {
                "desc": f"A snail crawls {frac_num}/{frac_den} of a foot in {time_val} seconds.",
                "question": "What is the unit rate, in feet per second?",
                "unit": "feet per second",
            },
            {
                "desc": f"{name} reads {frac_num}/{frac_den} of a chapter in {time_val} minutes.",
                "question": "What is the unit rate, in chapters per minute?",
                "unit": "chapters per minute",
            },
        ]

        ctx = rng.choice(contexts)

        stem_text = f"{ctx['desc']}\n\n{ctx['question']}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.DIFFICULT, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=ur_frac_str, answer_latex=ur_frac_str,
            worked_solution=(
                f"Unit rate = ({frac_num}/{frac_den}) / {time_val} "
                f"= {frac_num}/{frac_den} x 1/{time_val} "
                f"= {ur_frac_str} {ctx['unit']}"
            ),
            context_scenario="unit rate with fractions",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above Proficiency - MP (DOK 3, Medium)
    # Part A: Identify the equation y = kx from a verbal description
    # Part B: Use the equation to find the cost/value for a given amount
    # ================================================================

    def stem5_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)
        name = pick_name(rng)

        # Generate a unit rate that is a decimal (medium difficulty)
        # e.g., granola costs $2.80 for 7 ounces -> k = 0.40
        denominators = [4, 5, 6, 8]
        denom = rng.choice(denominators)
        total_price_cents = rng.randint(2, 6) * denom * 10  # ensures clean division
        total_price = Fraction(total_price_cents, 100)
        quantity = denom
        k = total_price / quantity
        k_str = _fmt(k)

        # Target for Part B
        target_qty = rng.randint(10, 30)
        answer_b = k * target_qty
        answer_b_str = _fmt(answer_b)

        # (item_name, unit, cost_desc, indep_desc, variable, measure_word)
        items = [
            ("granola", "ounces", "the cost, c", "the weight, w", "w", "weight"),
            ("ribbon", "feet", "the cost, c", "the length, f", "f", "length"),
            ("fabric", "yards", "the cost, c", "the number of yards, y", "y", "length"),
            ("trail mix", "ounces", "the cost, c", "the weight, w", "w", "weight"),
        ]
        item = rng.choice(items)
        var = item[4]  # equation variable matches item description

        # Build wrong equations for Part A MC using correct variable
        correct_eq = f"c = {k_str}{var}"
        inv_rate = quantity / total_price
        inv_str = f"{float(inv_rate):.2f}".rstrip('0').rstrip('.')
        wrong_eqs = [
            f"c = {inv_str}{var}",
            f"c = {_fmt(k + Fraction(1, 10))}{var}",
            f"c = {_fmt(total_price)}{var}",
        ]

        all_eq_options = [(correct_eq, True)] + [(w, False) for w in wrong_eqs]
        rng.shuffle(all_eq_options)

        choices_a = []
        for i, (text, is_correct) in enumerate(all_eq_options):
            choices_a.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter_a = next(c.key for c in choices_a if c.is_correct)

        # Build data table showing proportional relationship (max 5 rows)
        max_rows = min(quantity, 5)
        table_xs = list(range(1, max_rows + 1))
        table_ys = [k * x for x in table_xs]
        table_render = {
            "type": "data_table",
            "headers": [f"{item[1].capitalize()} ({var})", "Cost (c)"],
            "rows": [[str(x), _fmt_money(y)] for x, y in zip(table_xs, table_ys)],
        }

        stem_text = (
            f"The cost of {item[0]} is proportional to its {item[5]}. "
            f"{item[0].capitalize()} costs {_fmt_money(total_price)} for {quantity} {item[1]}.\n\n"
            f"The table shows the relationship.\n\n"
            f"Part A\n"
            f"Identify the equation that represents the relationship between "
            f"{item[2]} and {item[3]}.\n\n"
            f"Part B\n"
            f"What is the cost of {target_qty} {item[1]} of {item[0]}?"
        )

        part_a = QuestionPart(
            label="Part A",
            prompt=f"Identify the equation representing the relationship.",
            prompt_latex=f"Identify the equation representing the relationship.",
            answer=correct_letter_a, answer_latex=correct_letter_a,
            item_type=ItemType.MC,
        )
        part_b = QuestionPart(
            label="Part B",
            prompt=f"What is the cost of {target_qty} {item[1]}?",
            prompt_latex=f"What is the cost of {target_qty} {item[1]}?",
            answer=_fmt_money(answer_b), answer_latex=_fmt_money(answer_b),
            item_type=ItemType.NR,
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.MEDIUM, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.MEDIUM, dok=3, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"Part A: {correct_letter_a}; Part B: {_fmt_money(answer_b)}",
            answer_latex=f"Part A: {correct_letter_a}; Part B: {_fmt_money(answer_b)}",
            worked_solution=(
                f"Part A: Unit rate = {_fmt_money(total_price)} / {quantity} = {_fmt_money(k)} per {item[1][:-1] if item[1].endswith('s') else item[1]}. "
                f"So c = {k_str}{var}.\n"
                f"Part B: c = {k_str} x {target_qty} = {_fmt_money(answer_b)}"
            ),
            choices=choices_a, parts=[part_a, part_b],
            render_data=table_render,
            context_scenario="proportional equation and prediction",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_approaching_mc,
            self.stem3_at_nr,
            self.stem4_at_nr,
            self.stem5_above_mp,
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
            3: self.stem3_at_nr,
            4: self.stem4_at_nr,
            5: self.stem5_above_mp,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-5.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 7.RP.1 question variants...")
    gen = Stem7RP1(seed=42)
    all_q = gen.generate_all_variants(variants_per_stem=3)
    for q in all_q:
        print(f"\n{'='*60}")
        print(f"ID: {q.question_id}")
        print(f"Stem {q.stem_index} | {q.proficiency_level.value} | {q.difficulty.value} | DOK {q.dok}")
        print(f"\n{q.stem_text}")
        if q.choices:
            for c in q.choices:
                marker = " *" if c.is_correct else ""
                print(f"  {c.key}. {c.text}{marker}")
        print(f"\nAnswer: {q.answer_text}")
    print(f"\nTotal: {len(all_q)}")
