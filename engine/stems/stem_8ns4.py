"""
Stem generator for 8.NS.4:
  Solve real-world problems with rational numbers by using multiple
  operations.

Content Limits:
  - Rational numbers
  - Two or more different operations
  - May include: unit conversions, percentages (increase/decrease),
    exponents, use of exponent rules, variables
  - If unit conversion needed, conversion is embedded in item stem
  - Percent increase/decrease at Above Proficiency; per teacher request
    (state item spec), At Proficiency also rotates in percent-increase
    problems built on rational unit-conversion factors
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: positive whole numbers, benchmark percents (25%, 50%, 75%)
  Medium: integers with decimals or positive exponents
  Difficult: integers with decimals, fractions, negative exponents, any percent

5 Stems from the Item Spec:
  Stem 1 (Below-MC, DOK 2, Easy): Identify expression for a real-world problem
  Stem 2 (Approaching-NR, DOK 2, Easy): Solve 2-step real-world problem (whole numbers)
  Stem 3 (Approaching-NR, DOK 2, Medium): Solve 2-step problem with decimals
  Stem 4 (At-NR, DOK 2, Medium): Solve 3-4 step problem with unit conversion
      (rotates: percent increase w/ conversion factor, total after
      conversion, recipe scaling, multi-item purchase)
  Stem 5 (Above-NR, DOK 3, Difficult): Solve complex multi-step with percent/fractions
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
from engine.context_pools import CONTEXTS_8NS4, pick_name


STANDARD_CODE = "8.NS.4"
VARIANTS_PER_STEM = 20


# ============================================================
# HELPERS
# ============================================================

def _fmt_money(val):
    """Format a value as dollars and cents."""
    f = float(val)
    if f == int(f):
        return f"${int(f)}"
    return f"${f:.2f}"


def _fmt_num(val):
    """Format a numeric value cleanly."""
    f = float(val)
    if f == int(f):
        return str(int(f))
    # Up to 2 decimal places
    s = f"{f:.2f}".rstrip('0').rstrip('.')
    return s


class Stem8NS4:
    """Generates ~20 variants for each of 5 stems from the 8.NS.4 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 2, Easy)
    # Identify the algebraic equation for a real-world problem
    # e.g., "40 white flowers at $2.15 each + red flowers at $1.90
    #         each = $158.20 total"
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        name = pick_name(rng)

        # Generate a two-item purchasing scenario
        # Item A: known quantity * known price
        qty_a = rng.randint(10, 50)
        price_a = Fraction(rng.randint(100, 500), 100)  # $1.00-$5.00
        # Item B: unknown quantity * known price
        price_b = Fraction(rng.randint(100, 400), 100)  # $1.00-$4.00
        while price_b == price_a:
            price_b = Fraction(rng.randint(100, 400), 100)
        # Total: we pick a reasonable number of item B
        qty_b = rng.randint(5, 30)
        total = qty_a * price_a + qty_b * price_b

        pa = _fmt_money(price_a)
        pb = _fmt_money(price_b)
        total_str = _fmt_money(total)
        pa_num = _fmt_num(price_a)
        pb_num = _fmt_num(price_b)
        total_num = _fmt_num(total)

        item_a = rng.choice(["white flowers", "cupcakes", "red pens", "large bags", "postcards"])
        item_b = rng.choice(["red flowers", "cookies", "blue pens", "small bags", "greeting cards"])
        event = rng.choice(["a fundraiser", "a bake sale", "a school supply drive", "a craft fair"])

        stem_text = (
            f"A school sold {item_a} and {item_b} for {event}.\n\n"
            f"- {qty_a} {item_a} were sold for {pa} each.\n"
            f"- Each of the {item_b} was sold for {pb}.\n"
            f"- The school earned a total of {total_str}.\n\n"
            f"Which algebraic equation represents one way to calculate "
            f"how many {item_b} were sold?"
        )

        # Correct equation: qty_a * price_a + price_b * x = total
        correct = f"{qty_a}({pa_num}) + {pb_num}x = {total_num}"

        # Distractors
        distractors = []
        # Wrong: forgets multiplication for item A
        distractors.append(f"{qty_a} + {pa_num} + {pb_num}x = {total_num}")
        # Wrong: variable on wrong term
        distractors.append(f"{qty_a}x + {pa_num} + {pb_num} = {total_num}")
        # Wrong: uses addition only
        distractors.append(f"{total_num} - {qty_a}({pa_num}) - {pb_num} = x")

        all_options = [(correct, True)] + [(d, False) for d in distractors[:3]]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"The total earned is the sum of:\n"
            f"- Revenue from {item_a}: {qty_a} x {pa} = "
            f"{_fmt_money(qty_a * price_a)}\n"
            f"- Revenue from {item_b}: {pb} x (unknown quantity)\n\n"
            f"So the equation is: {qty_a}({pa_num}) + {pb_num}x = {total_num}\n"
            f"Answer: {correct}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="identify equation for purchasing problem",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - NR (DOK 2, Easy)
    # Solve 2-step problem with whole numbers
    # e.g., "earns $X per hour for Y hours plus $Z bonus = total?"
    # ================================================================

    def stem2_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        name = pick_name(rng)

        scenario = rng.choice(["earnings", "shopping", "recipe"])

        if scenario == "earnings":
            rate = rng.randint(8, 25)
            hours = rng.randint(4, 10)
            bonus = rng.randint(10, 50)
            total = rate * hours + bonus
            stem_text = (
                f"{name} earns ${rate} per hour at a part-time job. "
                f"This week {name} worked {hours} hours and received "
                f"a ${bonus} bonus.\n\n"
                f"What is {name}'s total earnings for the week?"
            )
            answer_val = total
            worked = (
                f"Hourly earnings: ${rate} x {hours} = ${rate * hours}\n"
                f"Plus bonus: ${rate * hours} + ${bonus} = ${total}\n"
                f"Total earnings: ${total}"
            )
        elif scenario == "shopping":
            n_items = rng.randint(3, 8)
            price = rng.randint(5, 25)
            discount = rng.randint(5, 20)
            subtotal = n_items * price
            total = subtotal - discount
            stem_text = (
                f"{name} buys {n_items} notebooks at ${price} each. "
                f"{name} has a coupon for ${discount} off the total.\n\n"
                f"What is the final cost?"
            )
            answer_val = total
            worked = (
                f"Subtotal: {n_items} x ${price} = ${subtotal}\n"
                f"After coupon: ${subtotal} - ${discount} = ${total}\n"
                f"Final cost: ${total}"
            )
        else:  # recipe
            servings_per = rng.randint(4, 8)
            needed = rng.randint(16, 40)
            # Make needed a multiple of servings_per
            needed = servings_per * (needed // servings_per)
            batches = needed // servings_per
            cups_per = rng.randint(2, 5)
            total_cups = batches * cups_per
            stem_text = (
                f"A recipe makes {servings_per} servings and calls for "
                f"{cups_per} cups of flour. {name} needs to make "
                f"{needed} servings.\n\n"
                f"How many cups of flour does {name} need?"
            )
            answer_val = total_cups
            worked = (
                f"Number of batches: {needed} / {servings_per} = {batches}\n"
                f"Flour needed: {batches} x {cups_per} = {total_cups} cups\n"
                f"Answer: {total_cups}"
            )

        answer_text = str(answer_val)

        stem_text += "\n\nWrite your answer in the box."

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_text, answer_latex=f"${answer_text}$",
            worked_solution=worked,
            context_scenario=f"2-step real-world ({scenario})",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - NR (DOK 2, Medium)
    # Solve 2-step problem with decimals
    # e.g., "earns two different hourly rates"
    # ================================================================

    def stem3_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        name = pick_name(rng)

        scenario = rng.choice(["two_rates", "purchase_tax", "distance"])

        if scenario == "two_rates":
            rate1 = Fraction(rng.randint(800, 2000), 100)  # $8.00-$20.00
            h1 = rng.randint(3, 8)
            rate2 = Fraction(rng.randint(1000, 2500), 100)  # $10.00-$25.00
            h2 = rng.randint(2, 5)
            total = rate1 * h1 + rate2 * h2
            stem_text = (
                f"{name} works two jobs.\n"
                f"- Job A pays {_fmt_money(rate1)} per hour. "
                f"{name} works {h1} hours.\n"
                f"- Job B pays {_fmt_money(rate2)} per hour. "
                f"{name} works {h2} hours.\n\n"
                f"What are {name}'s total earnings?"
            )
            answer_val = total
            worked = (
                f"Job A: {_fmt_money(rate1)} x {h1} = "
                f"{_fmt_money(rate1 * h1)}\n"
                f"Job B: {_fmt_money(rate2)} x {h2} = "
                f"{_fmt_money(rate2 * h2)}\n"
                f"Total: {_fmt_money(rate1 * h1)} + {_fmt_money(rate2 * h2)} "
                f"= {_fmt_money(total)}"
            )
        elif scenario == "purchase_tax":
            n_items = rng.randint(2, 6)
            price = Fraction(rng.randint(250, 1500), 100)  # $2.50-$15.00
            tax_rate = rng.choice([5, 6, 7, 8])
            subtotal = n_items * price
            tax = subtotal * Fraction(tax_rate, 100)
            total = subtotal + tax
            stem_text = (
                f"{name} buys {n_items} items at {_fmt_money(price)} each. "
                f"Sales tax is {tax_rate}%.\n\n"
                f"What is the total cost including tax?"
            )
            answer_val = total
            worked = (
                f"Subtotal: {n_items} x {_fmt_money(price)} = "
                f"{_fmt_money(subtotal)}\n"
                f"Tax: {_fmt_money(subtotal)} x {tax_rate}% = "
                f"{_fmt_money(tax)}\n"
                f"Total: {_fmt_money(subtotal)} + {_fmt_money(tax)} = "
                f"{_fmt_money(total)}"
            )
        else:  # distance
            speed1 = Fraction(rng.randint(30, 65), 1)
            time1 = Fraction(rng.randint(10, 30), 10)  # 1.0-3.0 hours
            speed2 = Fraction(rng.randint(25, 55), 1)
            time2 = Fraction(rng.randint(10, 25), 10)
            d1 = speed1 * time1
            d2 = speed2 * time2
            total = d1 + d2
            stem_text = (
                f"{name} drives at {_fmt_num(speed1)} mph for "
                f"{_fmt_num(time1)} hours, then at "
                f"{_fmt_num(speed2)} mph for {_fmt_num(time2)} hours.\n\n"
                f"What is the total distance {name} traveled?"
            )
            answer_val = total
            worked = (
                f"Distance 1: {_fmt_num(speed1)} x {_fmt_num(time1)} = "
                f"{_fmt_num(d1)} miles\n"
                f"Distance 2: {_fmt_num(speed2)} x {_fmt_num(time2)} = "
                f"{_fmt_num(d2)} miles\n"
                f"Total: {_fmt_num(d1)} + {_fmt_num(d2)} = "
                f"{_fmt_num(total)} miles"
            )

        answer_text = _fmt_num(answer_val)
        stem_text += "\n\nWrite your answer in the box."

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_text, answer_latex=f"${answer_text}$",
            worked_solution=worked,
            context_scenario=f"2-step with decimals ({scenario})",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At Proficiency - NR (DOK 2, Medium)
    # Solve 3-4 step problem, may include unit conversion
    # Rotation (variant_idx % 4):
    #   0: percent increase with a rational unit-conversion factor
    #      (state item spec: 48 gallons in stock, 17 liters delivered,
    #       1 liter ~ 0.26 gallons -> percent increase to nearest whole);
    #      the conversion pair itself cycles across liters/gallons (0.26),
    #      kilometers/miles (0.62), kilograms/pounds (2.2), and
    #      inches/centimeters (2.54)
    #   1: total after unit conversion ("gallons in stock + liters delivered")
    #   2: recipe scaling
    #   3: multi-item purchase with coupon
    # ================================================================

    def stem4_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        name = pick_name(rng)

        scenarios = ["pct_convert", "unit_convert", "recipe_scale",
                     "multi_purchase"]
        scenario = scenarios[variant_idx % 4]

        if scenario == "pct_convert":
            # Percent increase after an addition stated in a different unit.
            # Cycle deterministically through the four conversion pairs.
            conv_idx = (variant_idx // 4) % 4
            if conv_idx == 0:
                stock = rng.randint(30, 80)        # gallons in stock
                added_src = rng.randint(10, 40)    # liters delivered
                factor = Fraction(26, 100)
                factor_str = "0.26"
                bullet = "1 liter ≈ 0.26 gallons"
                intro = f"A store had {stock} gallons of milk in stock."
                event = f"A delivery of {added_src} liters of milk arrived."
                question = (
                    "What is the percent increase, to the nearest whole "
                    "number, in the amount of milk after the delivery?"
                )
                src_units, dst_units = "liters", "gallons"
            elif conv_idx == 1:
                stock = rng.randint(25, 60)        # miles run so far
                added_src = rng.randint(8, 25)     # kilometers added
                factor = Fraction(62, 100)
                factor_str = "0.62"
                bullet = "1 kilometer ≈ 0.62 miles"
                intro = (f"{name} has run {stock} miles in training "
                         f"this season.")
                event = (f"This week {name} adds a {added_src}-kilometer "
                         f"run.")
                question = (
                    f"What is the percent increase, to the nearest whole "
                    f"number, in {name}'s total training distance after "
                    f"the run?"
                )
                src_units, dst_units = "kilometers", "miles"
            elif conv_idx == 2:
                stock = rng.randint(150, 400)      # pounds in stock
                added_src = rng.randint(10, 40)    # kilograms delivered
                factor = Fraction(22, 10)
                factor_str = "2.2"
                bullet = "1 kilogram ≈ 2.2 pounds"
                intro = f"A warehouse had {stock} pounds of rice in stock."
                event = (f"A shipment of {added_src} kilograms of rice "
                         f"arrived.")
                question = (
                    "What is the percent increase, to the nearest whole "
                    "number, in the amount of rice after the shipment?"
                )
                src_units, dst_units = "kilograms", "pounds"
            else:
                stock = rng.randint(150, 400)      # centimeters of ribbon
                added_src = rng.randint(10, 40)    # inches purchased
                factor = Fraction(254, 100)
                factor_str = "2.54"
                bullet = "1 inch ≈ 2.54 centimeters"
                intro = f"{name} had {stock} centimeters of ribbon."
                event = f"{name} buys {added_src} more inches of ribbon."
                question = (
                    "What is the percent increase, to the nearest whole "
                    "number, in the total length of ribbon after the "
                    "purchase?"
                )
                src_units, dst_units = "inches", "centimeters"

            # Compute the answer exactly, then round half-up to the
            # nearest whole percent.
            added = added_src * factor                 # in stock units
            pct = added / Fraction(stock) * 100
            pct_rounded = int(pct + Fraction(1, 2))    # round half up
            # Machine-check: the rounded percent is within 0.5 of exact
            assert abs(pct - pct_rounded) <= Fraction(1, 2), (
                f"8.NS.4 pct_convert rounding check failed: "
                f"{pct} -> {pct_rounded}"
            )
            assert pct_rounded >= 1, (
                f"8.NS.4 pct_convert produced a degenerate percent: {pct}"
            )

            stem_text = (
                f"{intro}\n\n"
                f"- {event}\n"
                f"- {bullet}\n\n"
                f"{question}"
            )
            answer_val = pct_rounded
            worked = (
                f"Convert to {dst_units}: {added_src} {src_units} × "
                f"{factor_str} = {_fmt_num(added)} {dst_units}\n"
                f"Percent increase = (amount added ÷ original amount) "
                f"× 100\n"
                f"= {_fmt_num(added)} ÷ {stock} × 100 = "
                f"{float(pct):.2f}%\n"
                f"Rounded to the nearest whole number: {pct_rounded}%"
            )
        elif scenario == "unit_convert":
            # Milk problem: gallons + liters, find total in gallons
            gallons = rng.randint(20, 80)
            liters = rng.randint(10, 40)
            conversion = Fraction(26, 100)  # 1 liter ~ 0.26 gallons
            converted = liters * conversion
            total = Fraction(gallons) + converted
            # Round to nearest whole number
            total_rounded = round(float(total))

            stem_text = (
                f"A store had {gallons} gallons of milk in stock.\n"
                f"A delivery of {liters} liters of milk arrived.\n\n"
                f"1 liter is approximately 0.26 gallons.\n\n"
                f"How many total gallons of milk does the store have now? "
                f"Round to the nearest whole number."
            )
            answer_val = total_rounded
            worked = (
                f"Convert liters to gallons: {liters} x 0.26 = "
                f"{_fmt_num(converted)} gallons\n"
                f"Total: {gallons} + {_fmt_num(converted)} = "
                f"{_fmt_num(total)} gallons\n"
                f"Rounded: {total_rounded} gallons"
            )
        elif scenario == "recipe_scale":
            # Scale a recipe with mixed number ingredients
            base_serves = rng.choice([4, 6, 8])
            target_serves = base_serves * rng.randint(2, 4)
            scale = target_serves // base_serves
            # Ingredient amounts
            cups_flour = Fraction(rng.randint(1, 4))
            cups_sugar = Fraction(rng.randint(1, 3), rng.choice([2, 4]))
            total_flour = cups_flour * scale
            total_sugar = cups_sugar * scale

            flour_str = _fmt_num(cups_flour)
            sugar_str = _fmt_num(cups_sugar)
            flour_unit = "cup" if cups_flour == 1 else "cups"
            sugar_unit = "cup" if cups_sugar == 1 else "cups"

            stem_text = (
                f"A recipe serves {base_serves} people and uses:\n"
                f"- {flour_str} {flour_unit} of flour\n"
                f"- {sugar_str} {sugar_unit} of sugar\n\n"
                f"{name} needs to serve {target_serves} people.\n\n"
                f"How many total cups of flour and sugar does {name} need?"
            )
            total = total_flour + total_sugar
            answer_val = total
            worked = (
                f"Scale factor: {target_serves} / {base_serves} = {scale}\n"
                f"Flour: {flour_str} x {scale} = {_fmt_num(total_flour)} cups\n"
                f"Sugar: {sugar_str} x {scale} = {_fmt_num(total_sugar)} cups\n"
                f"Total: {_fmt_num(total_flour)} + {_fmt_num(total_sugar)} = "
                f"{_fmt_num(total)} cups"
            )
        else:  # multi_purchase
            # Buy different items at different prices, apply a flat discount
            item_names = rng.sample(
                ["shirts", "hats", "pairs of socks", "scarves", "belts"], 2
            )
            qty1 = rng.randint(2, 5)
            price1 = Fraction(rng.randint(800, 2500), 100)
            qty2 = rng.randint(1, 4)
            price2 = Fraction(rng.randint(500, 1800), 100)
            coupon = Fraction(rng.randint(500, 1500), 100)

            sub1 = qty1 * price1
            sub2 = qty2 * price2
            subtotal = sub1 + sub2
            total = subtotal - coupon
            if total < 0:
                total = Fraction(0)

            stem_text = (
                f"{name} buys:\n"
                f"- {qty1} {item_names[0]} at {_fmt_money(price1)} each\n"
                f"- {qty2} {item_names[1]} at {_fmt_money(price2)} each\n\n"
                f"{name} has a coupon for {_fmt_money(coupon)} off.\n\n"
                f"What is {name}'s total cost?"
            )
            answer_val = total
            worked = (
                f"{item_names[0]}: {qty1} x {_fmt_money(price1)} = "
                f"{_fmt_money(sub1)}\n"
                f"{item_names[1]}: {qty2} x {_fmt_money(price2)} = "
                f"{_fmt_money(sub2)}\n"
                f"Subtotal: {_fmt_money(sub1)} + {_fmt_money(sub2)} = "
                f"{_fmt_money(subtotal)}\n"
                f"After coupon: {_fmt_money(subtotal)} - {_fmt_money(coupon)} = "
                f"{_fmt_money(total)}"
            )

        answer_text = _fmt_num(answer_val)
        stem_text += "\n\nWrite your answer in the box."

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_text, answer_latex=f"${answer_text}$",
            worked_solution=worked,
            context_scenario=f"3-4 step problem ({scenario})",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above Proficiency - NR (DOK 3, Difficult)
    # Complex multi-step with percent and/or fractions
    # e.g., "Make 6 gallons of fruit drink, 37.5% apple juice,
    #         sold in 64oz bottles at $2.29 each"
    # ================================================================

    def stem5_above_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        name = pick_name(rng)

        scenario = rng.choice(["juice_party", "investment", "markup_discount"])

        if scenario == "juice_party":
            # Make N gallons, P% is juice, juice in X-oz bottles at $Y each
            oz_per_gallon = 128
            total_gallons = rng.choice([4, 5, 6, 8, 10])
            pct = rng.choice([25, 30, 37.5, 40, 50, 60, 75])
            pct_frac = Fraction(int(pct * 10), 1000)
            bottle_oz = rng.choice([32, 48, 64])
            bottle_price = Fraction(rng.randint(149, 399), 100)

            total_oz = total_gallons * oz_per_gallon
            juice_oz = Fraction(total_oz) * pct_frac
            bottles_needed_exact = juice_oz / bottle_oz
            # Must buy whole bottles
            import math as _math
            bottles_needed = _math.ceil(float(bottles_needed_exact))
            total_cost = Fraction(bottles_needed) * bottle_price

            pct_display = _fmt_num(pct) + "%"

            stem_text = (
                f"The relationship between fluid ounces and gallons is given.\n\n"
                f"  128 fluid ounces = 1 gallon\n\n"
                f"{name} is making a fruit drink for a party.\n"
                f"- {name} needs to make {total_gallons} gallons of the "
                f"fruit drink.\n"
                f"- {pct_display} of the fruit drink is apple juice.\n"
                f"- Apple juice only comes in {bottle_oz}-fluid ounce bottles. "
                f"Each bottle costs {_fmt_money(bottle_price)}.\n\n"
                f"How much does the apple juice cost for the "
                f"{total_gallons} gallons of fruit drink?"
            )

            answer_val = total_cost
            worked = (
                f"Total fluid ounces: {total_gallons} x 128 = "
                f"{total_oz} oz\n"
                f"Apple juice needed: {total_oz} x {pct_display} = "
                f"{_fmt_num(juice_oz)} oz\n"
                f"Bottles needed: {_fmt_num(juice_oz)} / {bottle_oz} = "
                f"{_fmt_num(bottles_needed_exact)}"
                f" --> {bottles_needed} bottles (round up)\n"
                f"Cost: {bottles_needed} x {_fmt_money(bottle_price)} = "
                f"{_fmt_money(total_cost)}"
            )

        elif scenario == "investment":
            # Simple interest: P dollars at R% for T years
            principal = rng.choice([500, 750, 1000, 1200, 1500, 2000])
            rate = rng.choice([3, 4, 5, 6, 7, 8])
            years = rng.randint(2, 5)

            interest = Fraction(principal * rate * years, 100)
            total = Fraction(principal) + interest

            stem_text = (
                f"{name} invests ${principal} at {rate}% simple interest "
                f"per year for {years} years.\n\n"
                f"What is the total value of the investment after "
                f"{years} years?"
            )
            answer_val = total
            worked = (
                f"Interest = Principal x Rate x Time\n"
                f"Interest = ${principal} x {rate}% x {years}\n"
                f"Interest = ${principal} x {rate/100} x {years} = "
                f"{_fmt_money(interest)}\n"
                f"Total = ${principal} + {_fmt_money(interest)} = "
                f"{_fmt_money(total)}"
            )

        else:  # markup_discount
            # Store marks up by R1%, then gives R2% off
            wholesale = Fraction(rng.choice([20, 25, 30, 40, 50, 60, 75, 80, 100]))
            markup_pct = rng.choice([25, 30, 40, 50, 60, 75, 100])
            discount_pct = rng.choice([10, 15, 20, 25, 30])

            marked_up = wholesale * (Fraction(100 + markup_pct, 100))
            discount_amount = marked_up * Fraction(discount_pct, 100)
            sale_price = marked_up - discount_amount

            stem_text = (
                f"A store buys an item for {_fmt_money(wholesale)} "
                f"(wholesale price).\n"
                f"The store marks up the price by {markup_pct}%.\n"
                f"Then the store offers a {discount_pct}% sale discount.\n\n"
                f"What is the final sale price?"
            )
            answer_val = sale_price
            worked = (
                f"Wholesale: {_fmt_money(wholesale)}\n"
                f"After {markup_pct}% markup: {_fmt_money(wholesale)} x "
                f"{_fmt_num(Fraction(100 + markup_pct, 100))} = "
                f"{_fmt_money(marked_up)}\n"
                f"Discount: {_fmt_money(marked_up)} x {discount_pct}% = "
                f"{_fmt_money(discount_amount)}\n"
                f"Sale price: {_fmt_money(marked_up)} - "
                f"{_fmt_money(discount_amount)} = {_fmt_money(sale_price)}"
            )

        answer_text = _fmt_num(answer_val)
        stem_text += "\n\nWrite your answer in the box."

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.NR,
                               Difficulty.DIFFICULT, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_text, answer_latex=f"${answer_text}$",
            worked_solution=worked,
            context_scenario=f"complex multi-step ({scenario})",
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
            self.stem2_approaching_nr,
            self.stem3_approaching_nr,
            self.stem4_at_nr,
            self.stem5_above_nr,
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
            2: self.stem2_approaching_nr,
            3: self.stem3_approaching_nr,
            4: self.stem4_at_nr,
            5: self.stem5_above_nr,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-5.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 8.NS.4 question variants...")
    gen = Stem8NS4(seed=42)
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
