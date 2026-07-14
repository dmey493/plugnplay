"""
Stem generator for 7.RP.2:
  Use proportional relationships to solve ratio and percent problems with
  multiple operations (e.g., simple interest, tax, markups, markdowns,
  gratuities, convert across measurement systems, and percent increase
  and decrease). (E)

Content Limits:
  - Limit to rational numbers
  - Allowable contexts: percent increase or decrease
  - Real world contexts more common
  - Tip and tax are both based on the subtotal (no tax on tip or tip on tax)
  - Measurement conversions allowed when embedded in the item
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: percentages multiple of 5 or 10, familiar numbers
  Medium: percentages not multiple of 5 or 10, calculate percent from original/final
  Difficult: work backwards from total, percents with decimals/fractions, >100%

6 Stems from the Item Spec:
  Stem 1 (Below-NR):     Calculate percent of a number (DOK 1, easy)
  Stem 2 (Approaching-NR): Discount/sale price or tax (DOK 2, easy)
  Stem 3 (Approaching-NR): Percent change (increase/decrease) (DOK 2, easy)
  Stem 4 (At-NR):        Simple interest calculation (DOK 2, medium)
  Stem 5 (At-NR):        Multi-step: tip + tax on a meal (DOK 2, difficult)
  Stem 6 (Above-NR):     Work backwards from total to find original (DOK 3, difficult)
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
from engine.context_pools import pick_name, CONTEXTS_7RP2


STANDARD_CODE = "7.RP.2"
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


def _fmt_money(val):
    """Format a value as dollars with 2 decimal places."""
    f = float(val) if isinstance(val, Fraction) else val
    if f == int(f):
        return f"${int(f):.2f}"
    return f"${f:.2f}"


def _round2(val):
    """Round a Fraction to 2 decimal places and return as Fraction."""
    return Fraction(round(float(val), 2)).limit_denominator(10000)


class Stem7RP2:
    """Generates ~20 variants for each of 6 stems from the 7.RP.2 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - NR (DOK 1, Easy)
    # Calculate percent of a number
    # "What is 60% of 240?" or "Fifteen is what percent of 50?"
    # ================================================================

    def stem1_below_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        question_type = rng.choice(["find_amount", "find_percent"])

        if question_type == "find_amount":
            # "What is P% of B?" — include some >100% percents
            rate = rng.choice([10, 20, 25, 30, 40, 50, 60, 75, 125, 150, 200])
            base = rng.choice([40, 50, 60, 80, 100, 120, 150, 200, 240, 300])
            amount = Fraction(base * rate, 100)
            answer = _fmt(amount)

            stem_text = f"What is {rate}% of {base}?"
            worked = f"{rate}% of {base} = {rate}/100 x {base} = {answer}"
        else:
            # "X is what percent of Y?" — include >100% answers
            rate = rng.choice([10, 15, 20, 25, 30, 40, 50, 60, 75, 120, 150])
            base = rng.choice([20, 40, 50, 80, 100, 200])
            amount = Fraction(base * rate, 100)
            answer = str(rate)

            stem_text = f"{_fmt(amount)} is what percent of {base}?"
            worked = f"{_fmt(amount)} / {base} = {_fmt(Fraction(amount, base))} = {rate}%"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.NR,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=worked,
            context_scenario="calculate percent of a number",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - NR (DOK 2, Easy)
    # Discount / sale price or sales tax
    # ================================================================

    def stem2_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)
        name = pick_name(rng)

        problem_type = rng.choice(["discount", "tax"])

        # Easy: percent is multiple of 5
        rate = rng.choice([5, 10, 15, 20, 25, 30, 35, 40, 50])

        if problem_type == "discount":
            prices = [15, 20, 25, 30, 40, 45, 50, 60, 75, 80, 100, 119, 125, 150]
            price = rng.choice(prices)
            discount = Fraction(price * rate, 100)
            sale_price = Fraction(price) - discount
            answer = _fmt_money(sale_price)

            items = ["basketball", "jacket", "pair of shoes", "backpack",
                     "skateboard", "bicycle helmet", "winter coat", "tennis racket"]
            item = rng.choice(items)

            stem_text = (
                f"The original price of a {item} costs ${price}. "
                f"It is on sale for {rate}% off.\n\n"
                f"What is the sale price of the {item}?"
            )
            worked = (
                f"Discount = {rate}% of ${price} = {_fmt_money(discount)}\n"
                f"Sale price = ${price} - {_fmt_money(discount)} = {answer}"
            )
        else:
            prices = [25, 40, 50, 65, 75, 89, 99, 119, 125, 150, 200]
            price = rng.choice(prices)
            tax = _round2(Fraction(price * rate, 100))
            total = Fraction(price) + tax
            answer = _fmt_money(total)

            items = ["winter coat", "pair of jeans", "laptop bag", "desk lamp",
                     "set of headphones", "running shoes", "kitchen appliance"]
            item = rng.choice(items)

            stem_text = (
                f"A store sells a {item}.\n\n"
                f"The original price of the {item} is ${price}.\n"
                f"A {rate}% sales tax is added.\n\n"
                f"What is the total cost of the {item}?"
            )
            worked = (
                f"Tax = {rate}% of ${price} = {_fmt_money(tax)}\n"
                f"Total = ${price} + {_fmt_money(tax)} = {answer}"
            )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=worked,
            context_scenario=f"{problem_type} calculation",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - NR (DOK 2, Easy)
    # Percent change (increase or decrease)
    # ================================================================

    def stem3_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)
        name = pick_name(rng)

        # Use multiples of 5 for easy difficulty
        # Ensure the percent change is reasonable (not >200%)
        for _ in range(50):
            old_val = rng.choice([15, 20, 25, 30, 40, 50, 60, 75, 80, 100])
            new_val_options = [v for v in [15, 20, 25, 30, 40, 50, 60, 75, 80, 100] if v != old_val]
            new_val = rng.choice(new_val_options)
            pct = abs(new_val - old_val) * 100 / old_val
            if pct <= 200:
                break

        change = abs(new_val - old_val)
        percent_change = Fraction(change * 100, old_val)
        percent_str = _fmt(percent_change)

        # Round to nearest whole percent if needed
        pct_float = float(percent_change)
        if pct_float == int(pct_float):
            percent_answer = str(int(pct_float))
        else:
            percent_answer = str(round(pct_float))

        if new_val > old_val:
            direction = "increase"
        else:
            direction = "decrease"

        contexts = [
            (f"An athlete scored {old_val} points last year and {new_val} points this year.",
             f"What is the percent of change in points from last year to this year? Round to the nearest whole percent."),
            (f"A store sold {old_val} items last month and {new_val} items this month.",
             f"What is the percent of change from last month to this month? Round to the nearest whole percent."),
            (f"{name}'s test score went from {old_val} to {new_val}.",
             f"What is the percent of change? Round to the nearest whole percent."),
            (f"The price of an item changed from ${old_val} to ${new_val}.",
             f"What is the percent of change? Round to the nearest whole percent."),
        ]
        ctx = rng.choice(contexts)

        stem_text = f"{ctx[0]}\n\n{ctx[1]}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.EASY, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{percent_answer}%",
            answer_latex=f"{percent_answer}\\%",
            worked_solution=(
                f"Change = |{new_val} - {old_val}| = {change}\n"
                f"Percent change = {change} / {old_val} x 100 = {percent_str}%\n"
                f"This is a {direction} of approximately {percent_answer}%."
            ),
            context_scenario=f"percent {direction}",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At Proficiency - NR (DOK 2, Medium)
    # Simple interest calculation
    # I = P * r * t; Total = P + I
    # ================================================================

    def stem4_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)
        name = pick_name(rng)

        principal = rng.choice([500, 600, 750, 800, 1000, 1200, 1500, 2000, 2500, 5000])
        # Medium: rate not necessarily multiple of 5; include decimal percents
        if rng.random() < 0.4:
            # Decimal percent (Difficult tier element)
            rate_pct_frac = Fraction(rng.choice([35, 45, 55, 65, 75, 85, 95]), 10)
            rate_pct_str = f"{float(rate_pct_frac):g}"
            rate_decimal = rate_pct_frac / 100
        else:
            rate_pct_frac = Fraction(rng.choice([3, 4, 6, 7, 8, 9, 12, 15]))
            rate_pct_str = str(int(rate_pct_frac))
            rate_decimal = rate_pct_frac / 100
        years = rng.randint(1, 10)

        interest = _round2(Fraction(principal) * rate_decimal * years)
        total = Fraction(principal) + interest

        # Question type: find interest or find total
        q_type = rng.choice(["interest_only", "total"])

        if q_type == "interest_only":
            answer = _fmt_money(interest)
            question = f"How much interest is earned in {years} year{'s' if years > 1 else ''}?"
        else:
            answer = _fmt_money(total)
            question = f"What is the total that will be owed after {years} year{'s' if years > 1 else ''}?"

        contexts = [
            f"{name} invests ${principal} in an account that earns {rate_pct_str}% simple interest.",
            f"A business borrows ${principal} at an interest rate of {rate_pct_str}%.",
            f"{name} deposits ${principal} in a savings account earning {rate_pct_str}% simple interest per year.",
        ]
        ctx = rng.choice(contexts)

        stem_text = f"{ctx}\n\n{question}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=(
                f"I = P x r x t = ${principal} x {rate_pct_str}/100 x {years} = {_fmt_money(interest)}\n"
                f"Total = ${principal} + {_fmt_money(interest)} = {_fmt_money(total)}"
            ),
            context_scenario="simple interest",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: At Proficiency - NR (DOK 2, Difficult)
    # Multi-step: tip + tax on a meal (both based on subtotal)
    # ================================================================

    def stem5_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        # Food cost (with cents)
        food_dollars = rng.randint(20, 150)
        food_cents = rng.choice([0, 15, 25, 35, 45, 50, 65, 75, 85, 95])
        food_cost = Fraction(food_dollars * 100 + food_cents, 100)

        # Tip and tax rates (difficult: may include decimals)
        tip_rate = rng.choice([15, 18, 20, 22, 25])
        tax_rate_options = [5, 6, 7, 8, 9]
        # Sometimes use a decimal tax rate for difficulty
        if rng.random() < 0.4:
            tax_rate_str = f"{rng.choice([5, 6, 7, 8])}.5"
            tax_rate = Fraction(tax_rate_str)
        else:
            tax_rate = Fraction(rng.choice(tax_rate_options))
            tax_rate_str = str(int(tax_rate))

        tip = _round2(food_cost * Fraction(tip_rate, 100))
        tax = _round2(food_cost * Fraction(tax_rate, 100))
        total = food_cost + tip + tax
        total = _round2(total)

        # Vary what is asked: the full total, or just the tip, or just the tax --
        # so the bank isn't limited to "find the total after tip and tax."
        q_type = rng.choice(["total", "tip_only", "tax_only"])
        if q_type == "tip_only":
            answer = _fmt_money(tip)
            question = "How much was the tip?"
        elif q_type == "tax_only":
            answer = _fmt_money(tax)
            question = "How much was the sales tax?"
        else:
            answer = _fmt_money(total)
            question = "What is the total cost of the meal?"

        family_sizes = [
            ("A family", "The family"),
            ("A group of friends", "The group"),
            ("A couple", "The couple"),
        ]
        who_intro, who_ref = rng.choice(family_sizes)

        stem_text = (
            f"{who_intro} goes to dinner.\n\n"
            f"The food costs {_fmt_money(food_cost)}.\n"
            f"{who_ref} gave the server a {tip_rate}% tip before tax was applied.\n"
            f"There is a {tax_rate_str}% sales tax on the food only.\n\n"
            f"{question}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.DIFFICULT, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=(
                f"Tip = {tip_rate}% of {_fmt_money(food_cost)} = {_fmt_money(tip)}\n"
                f"Tax = {tax_rate_str}% of {_fmt_money(food_cost)} = {_fmt_money(tax)}\n"
                f"Total = {_fmt_money(food_cost)} + {_fmt_money(tip)} + {_fmt_money(tax)} = {_fmt_money(total)}"
            ),
            context_scenario="meal with tip and tax",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    # STEM 6: Above Proficiency - NR (DOK 3, Difficult)
    # Work backwards from a total to find the original cost
    # "Total is $X after P% tax and Q% tip. What was the original cost?"
    # ================================================================

    def stem6_above_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)
        name = pick_name(rng)

        # Rotate through several above-proficiency percent problem types so the
        # bank isn't limited to "work backwards from a total."
        q_type = variant_idx % 3

        if q_type == 0:
            # Work backwards from a total meal cost to the original price.
            original_cents = rng.randint(10, 50) * 100 + rng.choice([0, 24, 50, 75, 99])
            original = Fraction(original_cents, 100)
            tax_rate = rng.choice([5, 6, 7, 8, 9])
            tip_rate = rng.choice([15, 18, 19, 20, 22])
            multiplier = Fraction(1) + Fraction(tax_rate, 100) + Fraction(tip_rate, 100)
            total = _round2(original * multiplier)
            total_str = _fmt_money(total)
            answer = _fmt_money(original)
            stem_text = (
                f"{name} buys a meal.\n\n"
                f"A {tax_rate}% sales tax was applied to the original cost.\n"
                f"{name} tips {tip_rate}% on the original cost.\n"
                f"{name} pays a total of {total_str}.\n\n"
                f"What was the original cost of the meal?"
            )
            worked = (
                f"Total = original x (1 + {tax_rate}/100 + {tip_rate}/100)\n"
                f"{total_str} = original x {_fmt(multiplier)}\n"
                f"Original = {total_str} / {_fmt(multiplier)} = {answer}"
            )
            scenario = "work backwards from total"

        elif q_type == 1:
            # Commission: total pay = base + commission% of sales; find the sales.
            base = rng.choice([500, 800, 1000, 1200, 1500])
            comm_rate = rng.choice([2, 3, 4, 5])
            sales = rng.choice([10000, 15000, 20000, 25000, 40000, 50000])
            total_pay = Fraction(base) + Fraction(comm_rate, 100) * sales
            answer = _fmt_money(Fraction(sales))
            stem_text = (
                f"{name} earns a base pay of ${base} per month plus a "
                f"{comm_rate}% commission on total sales.\n\n"
                f"Last month {name} was paid {_fmt_money(total_pay)} in all.\n\n"
                f"What were {name}'s total sales last month?"
            )
            worked = (
                f"Total pay = base + {comm_rate}% of sales\n"
                f"{_fmt_money(total_pay)} = ${base} + {comm_rate}/100 x sales\n"
                f"{_fmt_money(total_pay - base)} = {comm_rate}/100 x sales\n"
                f"sales = {_fmt_money(total_pay - base)} / ({comm_rate}/100) = {answer}"
            )
            scenario = "commission (find sales)"

        else:
            # Successive percent change: markup then discount; find the final price.
            cost = rng.choice([40, 50, 60, 80, 100, 120])
            markup = rng.choice([20, 25, 50])
            discount = rng.choice([10, 20, 25])
            marked = Fraction(cost) * (Fraction(1) + Fraction(markup, 100))
            final = _round2(marked * (Fraction(1) - Fraction(discount, 100)))
            answer = _fmt_money(final)
            stem_text = (
                f"A store buys a jacket for ${cost}.\n\n"
                f"The store marks up the price by {markup}%.\n"
                f"Later the jacket is put on sale for {discount}% off the marked-up price.\n\n"
                f"What is the final sale price?"
            )
            worked = (
                f"Marked-up price = ${cost} x (1 + {markup}/100) = {_fmt_money(marked)}\n"
                f"Final price = {_fmt_money(marked)} x (1 - {discount}/100) = {answer}"
            )
            scenario = "successive markup and discount"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.NR,
                               Difficulty.DIFFICULT, 6, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=worked,
            context_scenario=scenario,
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6, variant_index=variant_idx
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_nr,
            self.stem2_approaching_nr,
            self.stem3_approaching_nr,
            self.stem4_at_nr,
            self.stem5_at_nr,
            self.stem6_above_nr,
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
            1: self.stem1_below_nr,
            2: self.stem2_approaching_nr,
            3: self.stem3_approaching_nr,
            4: self.stem4_at_nr,
            5: self.stem5_at_nr,
            6: self.stem6_above_nr,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-6.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 7.RP.2 question variants...")
    gen = Stem7RP2(seed=42)
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
