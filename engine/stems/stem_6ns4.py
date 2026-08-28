"""
Stem generator for 6.NS.4:
  Solve real-world problems with positive fractions and decimals by using
  one or two operations. (E)

REBUILT for the 2026-08-24 specification revision. Indiana deleted the entire
"Solve." computation-drill family from this standard: bare arithmetic no longer
appears at any level, and the Below descriptor changed from "Compute fluently
with positive fractions and decimals" to "Solve simple real-world problems...".
The old stems 1 and 2 (Add fractions / Subtract decimals) were retired with it.

Difficulty is no longer set by the old easy/medium/difficult context table. The
ladder is now number precision and form conversion:
  Below        decimals to hundredths, benchmark fractions, one or two operations
  Approaching  same numbers, but the problem forces converting between forms
  At           decimals to thousandths, several operations, precise computation
  Above        non-routine structure, or critique of someone else's reasoning

Content Limits:
  - Positive fractions and mixed numbers
  - Positive decimals to the thousandths place
  - Maximum of 2 operations at Below and Approaching
  - Calculator: NOT ALLOWED

7 Stems from the revised Item Spec:
  Stem 1 (Below-MC): Number-of-groups-unknown with a benchmark mixed number
  Stem 2 (Below-MC): Two-operation part-part-whole with money
  Stem 3 (Approaching-MC): Add across number forms, fractions plus a decimal
  Stem 4 (Approaching-MC): Decimal divided by a non-benchmark fraction
  Stem 5 (At-MP): Multi-operation problem carrying thousandths precision
  Stem 6 (Above-ER): Critique a division-remainder misconception
  Stem 7 (Above-MP): Non-routine comparison of different discount structures

The four items the specification prints are captured verbatim in
authoring/data/spec_items_2026-08.json and are reproducible here: 1 1/2 cups at
0.25 -> 6 jars (stem 1); 2.4 m at 3/10 -> 8 bookmarks (stem 4); 0.35 gal/mi over
120.5 mi -> 42.175 gal (stem 5); 12.75 lb at 0.4 -> 31 full, 0.35 left (stem 6).
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
from engine.context_pools import pick_name


STANDARD_CODE = "6.NS.4"
VARIANTS_PER_STEM = 20

# Benchmark container sizes. Restricted to quarters and halves so a whole number
# of them always lands on a benchmark mixed number, which is what Below allows.
BENCHMARK_SIZES = [Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)]

# Fractions that are deliberately NOT benchmarks. Approaching is defined by
# having to convert between forms, and a benchmark converts by sight.
#
# Fifths and tenths only. Eighths were tried and removed: 3/8 of a whole number
# lands on thousandths (3.375), which breaks the Approaching content limit of
# "decimals to the hundredths" AND makes the printed total a rounded value, so
# the division in the stem would no longer come out even.
NON_BENCHMARK = [Fraction(1, 5), Fraction(2, 5), Fraction(3, 5), Fraction(4, 5),
                 Fraction(3, 10), Fraction(7, 10), Fraction(9, 10)]


def _fmt_fraction(val: Fraction) -> str:
    """Mixed-number display: 7/2 -> '3 1/2', 3/4 -> '3/4', 4 -> '4'."""
    if val.denominator == 1:
        return str(val.numerator)
    whole = val.numerator // val.denominator
    rem = val - whole
    if whole == 0:
        return f"{rem.numerator}/{rem.denominator}"
    return f"{whole} {rem.numerator}/{rem.denominator}"


def _fmt_decimal(val, places: int = 2) -> str:
    """Trim trailing zeros but never show fewer than one decimal place."""
    text = f"{float(val):.{places}f}".rstrip("0")
    return text + "0" if text.endswith(".") else text


def _money(val) -> str:
    return f"${float(val):.2f}"


def _round_half_up(value: Fraction, places: int = 2) -> Fraction:
    """Round exactly, half away from zero, the way students are taught.

    Python's round() is banker's rounding, so round(424.575, 2) can land on
    424.57. Money answers are graded half-up, and the arithmetic here is exact
    Fractions anyway, so we round on the Fraction rather than on a float.
    """
    scale = 10 ** places
    scaled = value * scale
    floor = scaled.numerator // scaled.denominator
    if scaled - floor >= Fraction(1, 2):
        floor += 1
    return Fraction(floor, scale)


def _build_mc(rng, correct, candidates, fmt, fallback_step):
    """Build four shuffled choices; return them plus the key of the correct one.

    Distractors are deduplicated on their FORMATTED text, not their numeric
    value. Two different quantities can render identically once rounded for
    display (8.67 and 9 both print as "9"), and a question that ships the same
    string twice has no defensible answer. When an error model collides or lands
    on the correct value it is dropped, and we step away from the correct answer
    instead so the item still has four distinct options.
    """
    correct_text = fmt(correct)
    seen = {correct_text}
    picked = []

    for value, rationale in candidates:
        if float(value) <= 0:
            continue
        text = fmt(value)
        if text in seen:
            continue
        seen.add(text)
        picked.append((text, rationale))
        if len(picked) == 3:
            break

    step = 1
    while len(picked) < 3 and step <= 60:
        value = correct + fallback_step * step
        if float(value) > 0:
            text = fmt(value)
            if text not in seen:
                seen.add(text)
                picked.append((text, "Arithmetic slip"))
        step += 1

    rows = [(correct_text, True, None)] + [(t, False, r) for t, r in picked]
    rng.shuffle(rows)

    letters = "ABCD"
    choices = []
    correct_key = "A"
    for i, (text, is_correct, rationale) in enumerate(rows):
        key = letters[i]
        if is_correct:
            correct_key = key
        choices.append(QuestionChoice(
            key=key.lower(), text=text, text_latex=text,
            is_correct=is_correct, distractor_rationale=rationale,
        ))
    return choices, correct_key


class Stem6NS4:
    """Generates ~20 variants for each of 7 stems from the revised 6.NS.4 spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 2, Easy)
    # Number-of-groups-unknown. One operation, benchmark mixed number.
    # Spec anchor: 1 1/2 cups of glitter into 0.25-cup jars -> 6 jars.
    # ================================================================
    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)
        name = pick_name(rng)

        size = rng.choice(BENCHMARK_SIZES)
        groups = rng.randint(5, 12)
        total = size * groups
        # The total must carry a fraction, or this stops being a benchmark
        # mixed-number task and becomes whole-number division.
        tries = 0
        while total.denominator == 1 and tries < 12:
            groups = rng.randint(5, 12)
            total = size * groups
            tries += 1
        if total.denominator == 1:
            size, groups = Fraction(1, 4), 7
            total = size * groups

        what, singular, plural, unit = rng.choice([
            ("small craft jars with glitter", "jar", "jars", "cups"),
            ("palettes with paint", "palette", "palettes", "cups"),
            ("bags with birdseed", "bag", "bags", "pounds"),
            ("bottles with syrup", "bottle", "bottles", "liters"),
            ("containers with rice", "container", "containers", "pounds"),
            ("tins with candle wax", "tin", "tins", "pounds"),
            ("jars with honey", "jar", "jars", "cups"),
            ("bins with laundry detergent", "bin", "bins", "cups"),
            ("flasks with apple juice", "flask", "flasks", "liters"),
            ("boxes with play sand", "box", "boxes", "pounds"),
        ])

        size_str = _fmt_decimal(size)
        total_str = _fmt_fraction(total)

        stem_text = (
            f"{name} fills {what}.\n\n"
            f"- Each {singular} holds {size_str} {unit}.\n"
            f"- {name} has {total_str} {unit} available.\n\n"
            f"How many {plural} can {name} fill completely?"
        )

        whole_only = int(total) / float(size)
        rounded_up = (int(total) + 1) / float(size)
        choices, correct_key = _build_mc(rng, groups, [
            (whole_only, "Uses only the whole-number part and ignores the fraction"),
            (groups - 1, "Off by one; drops the final full group"),
            (rounded_up, "Rounds the total up to the next whole number first"),
        ], lambda v: str(int(round(float(v)))), fallback_step=2)

        worked = (
            f"Divide the amount available by the size of one {singular}.\n"
            f"{total_str} / {size_str} = {groups}\n"
            f"{name} can fill {groups} {plural} completely."
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW,
                                         ItemType.MC, Difficulty.EASY, 1, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY,
            dok=2,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"{correct_key}. {groups}",
            answer_latex=f"{correct_key}. {groups}",
            worked_solution=worked,
            choices=choices,
            context_scenario="number-of-groups-unknown division",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1,
            variant_index=variant_idx,
        )

    # ================================================================
    # STEM 2: Below Proficiency - MC (DOK 2, Easy)
    # Two operations, part-part-whole with money. Two operations count as
    # Below now, provided the numbers stay simple.
    # ================================================================
    def stem2_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)
        name = pick_name(rng)

        weight = Fraction(rng.randint(15, 65), 10)          # tenths, 1.5 to 6.5
        unit_price = Fraction(rng.choice([100, 150, 200, 250, 300]), 100)
        part_cost = weight * unit_price                      # lands on hundredths
        other_cost = Fraction(rng.randint(120, 899), 100)
        total = part_cost + other_cost

        produce, other = rng.choice([
            ("bananas", "a carton of milk"),
            ("apples", "a loaf of bread"),
            ("grapes", "a box of cereal"),
            ("potatoes", "a bag of flour"),
            ("tomatoes", "a jar of sauce"),
            ("carrots", "a block of cheese"),
            ("oranges", "a bottle of juice"),
            ("onions", "a bag of rice"),
            ("peppers", "a dozen eggs"),
            ("mushrooms", "a tub of yogurt"),
        ])

        stem_text = (
            f"{name} buys {produce} and {other} at the grocery store.\n\n"
            f"- {name} buys {_fmt_decimal(weight, 1)} pounds of {produce} "
            f"for {_money(unit_price)} per pound.\n"
            f"- {name} spends a total of {_money(total)}.\n\n"
            f"How much did {name} pay for {other}?"
        )

        choices, correct_key = _build_mc(rng, other_cost, [
            (total - unit_price, "Subtracts the price per pound instead of the total cost"),
            (total - part_cost / 10, "Misplaces the decimal point when multiplying"),
            (total + unit_price, "Adds instead of subtracting"),
        ], _money, fallback_step=Fraction(1, 1))

        worked = (
            f"Cost of the {produce}: {_fmt_decimal(weight, 1)} x "
            f"{_money(unit_price)} = {_money(part_cost)}\n"
            f"Cost of {other}: {_money(total)} - {_money(part_cost)} = {_money(other_cost)}"
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW,
                                         ItemType.MC, Difficulty.EASY, 2, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY,
            dok=2,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"{correct_key}. {_money(other_cost)}",
            answer_latex=f"{correct_key}. {_money(other_cost)}",
            worked_solution=worked,
            choices=choices,
            context_scenario="part-part-whole with money",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2,
            variant_index=variant_idx,
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - MC (DOK 2, Medium)
    # Fractions and a decimal in one problem, so a form conversion is forced.
    # ================================================================
    def stem3_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)
        name = pick_name(rng)

        f1 = rng.choice([Fraction(1, 2), Fraction(1, 4), Fraction(3, 4)])
        f2 = rng.choice([Fraction(1, 2), Fraction(1, 4), Fraction(3, 4)])
        dec = Fraction(rng.randint(25, 250), 100)
        total = f1 + f2 + dec

        dish, a_name, b_name, c_name, unit, single = rng.choice([
            ("a smoothie", "orange juice", "apple juice", "strawberries", "cups", "cup"),
            ("a fruit salad", "diced melon", "sliced banana", "blueberries", "cups", "cup"),
            ("trail mix", "raisins", "almonds", "granola", "cups", "cup"),
            ("a punch", "lemonade", "pineapple juice", "sparkling water", "liters", "liter"),
            ("a soup", "chopped carrots", "diced celery", "broth", "cups", "cup"),
            ("a pancake batter", "milk", "water", "oil", "cups", "cup"),
            ("a yogurt bowl", "plain yogurt", "honey", "frozen berries", "cups", "cup"),
            ("a marinade", "olive oil", "vinegar", "soy sauce", "cups", "cup"),
            ("iced tea", "brewed tea", "lemon juice", "cold water", "liters", "liter"),
            ("a paint mix", "blue paint", "white paint", "clear medium", "liters", "liter"),
        ])

        stem_text = (
            f"{name} makes {dish}.\n\n"
            f"- {name} uses {_fmt_fraction(f1)} {single} of {a_name}.\n"
            f"- {name} uses {_fmt_fraction(f2)} {single} of {b_name}.\n"
            f"- {name} uses {_fmt_decimal(dec)} {unit} of {c_name}.\n\n"
            f"How many {unit} of {a_name}, {b_name}, and {c_name} "
            f"does {name} use in total?"
        )

        # Error models a form conversion actually produces.
        digits_error = (Fraction(f1.numerator * 10 + f1.denominator, 100)
                        + f2 + dec)                              # 3/4 read as 0.34
        denom_tenths = f1 + Fraction(f2.denominator, 10) + dec   # 1/4 read as 0.4
        fractions_only = f1 + f2                                 # drops the decimal

        def fmt(v):
            return f"{_fmt_decimal(v)} {unit}"

        choices, correct_key = _build_mc(rng, total, [
            (digits_error, "Reads the fraction's digits as decimal digits"),
            (denom_tenths, "Uses the denominator as a tenths value"),
            (fractions_only, "Adds only the two fractions and drops the decimal"),
        ], fmt, fallback_step=Fraction(5, 100))

        worked = (
            f"Write every amount in the same form.\n"
            f"{_fmt_fraction(f1)} = {_fmt_decimal(f1)}, "
            f"{_fmt_fraction(f2)} = {_fmt_decimal(f2)}\n"
            f"{_fmt_decimal(f1)} + {_fmt_decimal(f2)} + {_fmt_decimal(dec)} "
            f"= {_fmt_decimal(total)} {unit}"
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING,
                                         ItemType.MC, Difficulty.MEDIUM, 3, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM,
            dok=2,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"{correct_key}. {fmt(total)}",
            answer_latex=f"{correct_key}. {fmt(total)}",
            worked_solution=worked,
            choices=choices,
            context_scenario="adding across number forms",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3,
            variant_index=variant_idx,
        )

    # ================================================================
    # STEM 4: Approaching Proficiency - MC (DOK 2, Medium)
    # Decimal divided by a NON-benchmark fraction.
    # Spec anchor: 2.4 m of ribbon at 3/10 m each -> 8 bookmarks.
    # ================================================================
    def stem4_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)
        name = pick_name(rng)

        piece = rng.choice(NON_BENCHMARK)
        count = rng.randint(5, 12)
        total = piece * count

        material, noun, product, single, unit, unit_single = rng.choice([
            ("a ribbon", "ribbon", "bookmarks", "bookmark", "meters", "meter"),
            ("a board", "board", "shelves", "shelf", "feet", "foot"),
            ("a rope", "rope", "jump ropes", "jump rope", "meters", "meter"),
            ("a roll of tape", "roll", "labels", "label", "meters", "meter"),
            ("a length of wire", "wire", "hooks", "hook", "feet", "foot"),
            ("a chain", "chain", "keyrings", "keyring", "meters", "meter"),
            ("a strip of felt", "strip", "patches", "patch", "meters", "meter"),
            ("a plank", "plank", "birdhouses", "birdhouse", "feet", "foot"),
            ("a length of trim", "trim", "picture frames", "picture frame", "feet", "foot"),
            ("a spool of cord", "cord", "bracelets", "bracelet", "meters", "meter"),
        ])

        stem_text = (
            f"{name} makes {product} from {material}.\n\n"
            f"- The {noun} is {_fmt_decimal(total)} {unit} long.\n"
            f"- Each {single} uses {_fmt_fraction(piece)} {unit_single} of it.\n\n"
            f"How many {product} can {name} make?"
        )

        choices, correct_key = _build_mc(rng, count, [
            (count - 2, "Miscounts by two when sharing out the length"),
            (count - 1, "Off by one; drops the final full piece"),
            (count + 2, "Uses a smaller piece size than the one given"),
        ], lambda v: str(int(round(float(v)))), fallback_step=3)

        worked = (
            f"Divide the total length by the length of one {single}.\n"
            f"{_fmt_decimal(total)} / {_fmt_fraction(piece)} = "
            f"{_fmt_decimal(total)} / {_fmt_decimal(piece)} = {count}\n"
            f"{name} can make {count} {product}."
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING,
                                         ItemType.MC, Difficulty.MEDIUM, 4, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM,
            dok=2,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"{correct_key}. {count}",
            answer_latex=f"{correct_key}. {count}",
            worked_solution=worked,
            choices=choices,
            context_scenario="dividing a decimal by a non-benchmark fraction",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4,
            variant_index=variant_idx,
        )

    # ================================================================
    # STEM 5: At Proficiency - MP (DOK 2, Difficult)
    # Several operations, and the intermediate value runs to thousandths.
    # Spec anchor: 0.35 gal/mile over 120.5 miles -> 42.175 gallons.
    # ================================================================
    def stem5_at_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)
        name = pick_name(rng)

        rate = Fraction(rng.randint(15, 85), 100)        # hundredths
        amount = Fraction(rng.randint(805, 1995), 10)    # tenths
        used = rate * amount                             # thousandths
        price = Fraction(rng.choice([225, 275, 325, 375, 425]), 100)
        cost = used * price
        cost_rounded = _round_half_up(cost, 2)

        (doing, device, rate_unit, dist_lead, dist_unit,
         price_lead, price_unit, quantity_name, thing) = rng.choice([
            ("plans a road trip", "car uses", "gallons of gas per mile",
             "The total distance for the trip is", "miles", "Gas costs",
             "per gallon", "gallons of gas", "gas"),
            ("plans a large paint job", "sprayer uses", "gallons of paint per square foot",
             "The total area to cover is", "square feet", "Paint costs",
             "per gallon", "gallons of paint", "paint"),
            ("plans a lawn treatment", "spreader uses", "gallons of fertilizer per square foot",
             "The total area to treat is", "square feet", "Fertilizer costs",
             "per gallon", "gallons of fertilizer", "fertilizer"),
            ("plans a boat trip", "boat uses", "gallons of fuel per mile",
             "The total distance on the water is", "miles", "Fuel costs",
             "per gallon", "gallons of fuel", "fuel"),
            ("plans a sealing job", "roller uses", "gallons of sealant per square foot",
             "The total area to seal is", "square feet", "Sealant costs",
             "per gallon", "gallons of sealant", "sealant"),
            ("plans a delivery route", "van uses", "gallons of gas per mile",
             "The total route is", "miles", "Gas costs",
             "per gallon", "gallons of gas", "gas"),
            ("plans a wall mural", "airbrush uses", "gallons of primer per square foot",
             "The total area to prime is", "square feet", "Primer costs",
             "per gallon", "gallons of primer", "primer"),
            ("plans a moving trip", "truck uses", "gallons of gas per mile",
             "The total distance to the new house is", "miles", "Gas costs",
             "per gallon", "gallons of gas", "gas"),
        ])

        stem_text = (
            f"This item has two parts.\n\n"
            f"{name} {doing}.\n\n"
            f"- {name}'s {device} {_fmt_decimal(rate)} {rate_unit}.\n"
            f"- {dist_lead} {_fmt_decimal(amount, 1)} {dist_unit}.\n"
            f"- {price_lead} {_money(price)} {price_unit}.\n\n"
            f"Part A: How many {quantity_name} will {name} need in total?\n\n"
            f"Part B: How much will {name} spend on {thing}? "
            f"Round your answer to the nearest hundredth."
        )

        used_str = _fmt_decimal(used, 3)
        part_a = QuestionPart(
            label="Part A",
            prompt=f"How many {quantity_name} will {name} need in total?",
            prompt_latex=f"How many {quantity_name} will {name} need in total?",
            answer=used_str,
            answer_latex=used_str,
            item_type=ItemType.NR,
        )
        part_b = QuestionPart(
            label="Part B",
            prompt=f"How much will {name} spend on {thing}?",
            prompt_latex=f"How much will {name} spend on {thing}?",
            answer=_money(cost_rounded),
            answer_latex=_money(cost_rounded),
            item_type=ItemType.NR,
        )

        worked = (
            f"Part A: {_fmt_decimal(rate)} x {_fmt_decimal(amount, 1)} = {used_str}\n"
            f"  Keep all three decimal places; rounding here changes Part B.\n"
            f"Part B: {used_str} x {_money(price)} = {_fmt_decimal(cost, 5)}\n"
            f"  Rounded to the nearest hundredth: {_money(cost_rounded)}"
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.AT,
                                         ItemType.MP, Difficulty.DIFFICULT, 5, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT,
            dok=2,
            item_type=ItemType.MP,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"Part A: {used_str}; Part B: {_money(cost_rounded)}",
            answer_latex=f"Part A: {used_str}; Part B: {_money(cost_rounded)}",
            worked_solution=worked,
            parts=[part_a, part_b],
            context_scenario="multi-operation with thousandths precision",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5,
            variant_index=variant_idx,
        )

    # ================================================================
    # STEM 6: Above Proficiency - ER (DOK 3, Difficult)
    # Critique a solution. The misconception is reading the decimal part of a
    # quotient as the physical amount left over.
    # Spec anchor: 12.75 lb of clay into 0.4 lb containers -> 31, 0.35 left.
    # ================================================================
    def stem6_above_er(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)
        student = pick_name(rng)

        size = Fraction(rng.choice([20, 25, 40, 50, 60, 75]), 100)
        total = Fraction(rng.randint(505, 1995), 100)
        quotient = total / size
        filled = int(quotient)
        leftover = total - filled * size
        tries = 0
        # A zero remainder removes the misconception the item is built on.
        while leftover == 0 and tries < 12:
            total = Fraction(rng.randint(505, 1995), 100)
            quotient = total / size
            filled = int(quotient)
            leftover = total - filled * size
            tries += 1
        claimed = quotient - filled   # the decimal tail the student misreads

        material, holder, single, unit = rng.choice([
            ("modeling clay", "containers", "container", "pounds"),
            ("potting soil", "planters", "planter", "pounds"),
            ("apple cider", "bottles", "bottle", "liters"),
            ("floor sealant", "trays", "tray", "gallons"),
            ("wildflower seed", "packets", "packet", "pounds"),
            ("maple syrup", "jars", "jar", "liters"),
            ("sidewalk chalk powder", "tubs", "tub", "pounds"),
            ("hand sanitizer", "pump bottles", "pump bottle", "liters"),
            ("birdseed", "feeders", "feeder", "pounds"),
        ])

        stem_text = (
            f"{student} is packing {material} for a school event.\n\n"
            f"- {student} has {_fmt_decimal(total)} {unit} of {material}.\n"
            f"- {student} packs it into {holder} that hold "
            f"{_fmt_decimal(size)} {unit} each.\n\n"
            f"{student} calculates that {filled} {holder} can be filled with "
            f"{_fmt_decimal(claimed, 3)} {unit} of {material} left over.\n\n"
            f"Is {student}'s conclusion correct? Evaluate {student}'s answer and "
            f"use words and equations to explain your answer."
        )

        answer = (
            f"{student}'s solution is partially correct. The number of full "
            f"{holder} is right: {filled}. The amount left over is not.\n"
            f"{_fmt_decimal(total)} / {_fmt_decimal(size)} = "
            f"{_fmt_decimal(quotient, 3)}, so {filled} {holder} can be filled. "
            f"{student} read the {_fmt_decimal(claimed, 3)} after the decimal "
            f"point as the amount left over, but that is a part of one "
            f"{single}, not a measure of {material}.\n"
            f"Left over = {_fmt_decimal(total)} - {filled} x "
            f"{_fmt_decimal(size)} = {_fmt_decimal(leftover)} {unit}."
        )

        worked = (
            f"Divide: {_fmt_decimal(total)} / {_fmt_decimal(size)} = "
            f"{_fmt_decimal(quotient, 3)}\n"
            f"Full {holder}: {filled}\n"
            f"Used: {filled} x {_fmt_decimal(size)} = {_fmt_decimal(filled * size)}\n"
            f"Left over: {_fmt_decimal(total)} - {_fmt_decimal(filled * size)} "
            f"= {_fmt_decimal(leftover)}\n"
            f"The student's {_fmt_decimal(claimed, 3)} is the fractional part of "
            f"the quotient, not the leftover amount."
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE,
                                         ItemType.ER, Difficulty.DIFFICULT, 6, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT,
            dok=3,
            item_type=ItemType.ER,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=answer,
            answer_latex=answer,
            worked_solution=worked,
            context_scenario="critique of a division remainder",
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6,
            variant_index=variant_idx,
        )

    # ================================================================
    # STEM 7: Above Proficiency - MP (DOK 3, Difficult)
    # Non-routine: each option carries a DIFFERENT discount structure, so the
    # steps have to be inferred rather than executed.
    # ================================================================
    def stem7_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(7, variant_idx)
        name = pick_name(rng)

        qty = rng.choice([8, 10, 12, 14, 16])
        p_half = Fraction(rng.randint(3200, 4400), 100)    # buy one, second half off
        p_plain = Fraction(rng.randint(2600, 3200), 100)   # no sale
        p_off = Fraction(rng.randint(3000, 3800), 100)     # flat amount off each
        off = Fraction(rng.choice([500, 650, 750, 900]), 100)

        def totals():
            return (qty * p_half * Fraction(3, 4),
                    qty * p_plain,
                    qty * (p_off - off))

        # The flat-discount option has to win by a clear margin, but NOT by a
        # runaway one. If it is far cheaper per item, a student can pick it off
        # by eye and never compute a total, which is exactly the reasoning this
        # non-routine item exists to require. Target: cheapest by more than $5
        # but by less than a fifth of its own total.
        def spread_ok(half, plain, off_total):
            second = min(half, plain)
            gap = second - off_total
            return gap > 5 and gap < off_total * Fraction(1, 5)

        t_half, t_plain, t_off = totals()
        tries = 0
        while not spread_ok(t_half, t_plain, t_off) and tries < 40:
            off = Fraction(rng.choice([400, 500, 650, 750]), 100)
            p_off = Fraction(rng.randint(3000, 3600), 100)
            p_plain = Fraction(rng.randint(2800, 3300), 100)
            p_half = Fraction(rng.randint(3400, 4200), 100)
            t_half, t_plain, t_off = totals()
            tries += 1

        kind, item = rng.choice([
            ("costumes", "costume"), ("jerseys", "jersey"),
            ("aprons", "apron"), ("jackets", "jacket"),
        ])
        a, b, c = rng.sample(["Mermaid", "Cowgirl", "Dragon", "Falcon", "Comet"], 3)

        stem_text = (
            f"This item has two parts.\n\n"
            f"{name} must choose new {kind} for a class of {qty} students.\n\n"
            f"- The {a} {item} costs {_money(p_half)}. For each {a} {item} "
            f"bought, the second one is half off.\n"
            f"- The {b} {item} costs {_money(p_plain)}. It is not on sale.\n"
            f"- The {c} {item} costs {_money(p_off)}, on sale for {_money(off)} "
            f"off each {item}.\n\n"
            f"{name} buys the same {item} for every student.\n\n"
            f"Part A: Which {item} costs the least in total?\n\n"
            f"Part B: What is that total for {qty} {kind}?"
        )

        part_a = QuestionPart(
            label="Part A",
            prompt=f"Which {item} costs the least in total?",
            prompt_latex=f"Which {item} costs the least in total?",
            answer=c, answer_latex=c, item_type=ItemType.MC,
        )
        part_b = QuestionPart(
            label="Part B",
            prompt=f"What is that total for {qty} {kind}?",
            prompt_latex=f"What is that total for {qty} {kind}?",
            answer=_money(t_off),
            answer_latex=_money(t_off),
            item_type=ItemType.NR,
        )

        worked = (
            f"Each option is priced a different way, so each needs its own steps.\n"
            f"{a}: a pair costs {_money(p_half)} + {_money(p_half / 2)} = "
            f"{_money(p_half * Fraction(3, 2))}. "
            f"{qty // 2} pairs x {_money(p_half * Fraction(3, 2))} = {_money(t_half)}\n"
            f"{b}: {qty} x {_money(p_plain)} = {_money(t_plain)}\n"
            f"{c}: {_money(p_off)} - {_money(off)} = {_money(p_off - off)} each, "
            f"so {qty} x {_money(p_off - off)} = {_money(t_off)}\n"
            f"The {c} {item} costs the least, at {_money(t_off)}."
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE,
                                         ItemType.MP, Difficulty.DIFFICULT, 7, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT,
            dok=3,
            item_type=ItemType.MP,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"Part A: {c}; Part B: {_money(t_off)}",
            answer_latex=f"Part A: {c}; Part B: {_money(t_off)}",
            worked_solution=worked,
            parts=[part_a, part_b],
            context_scenario="non-routine comparison of discount structures",
            seed=self.base_seed * 1000 + 700 + variant_idx,
            stem_index=7,
            variant_index=variant_idx,
        )

    # ================================================================
    def _stem_methods(self):
        return {
            1: self.stem1_below_mc,
            2: self.stem2_below_mc,
            3: self.stem3_approaching_mc,
            4: self.stem4_approaching_mc,
            5: self.stem5_at_mp,
            6: self.stem6_above_er,
            7: self.stem7_above_mp,
        }

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM):
        all_questions = []
        for _, fn in sorted(self._stem_methods().items()):
            for v in range(variants_per_stem):
                try:
                    all_questions.append(fn(v))
                except Exception as e:
                    print(f"Error generating {fn.__name__} variant {v}: {e}")
                    continue
        return all_questions

    def generate_stem_variants(self, stem_index: int,
                               variants_per_stem: int = VARIANTS_PER_STEM):
        fn = self._stem_methods().get(stem_index)
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


if __name__ == "__main__":
    generator = Stem6NS4(seed=42)
    for q in generator.generate_all_variants(variants_per_stem=2):
        print("=" * 66)
        print(f"Stem {q.stem_index} | {q.proficiency_level.value} | {q.item_type.value}")
        print(q.stem_text)
        if q.choices:
            for c in q.choices:
                print(f"  {c.key}. {c.text}{' *' if c.is_correct else ''}")
        print(f"Answer: {q.answer_text}")
