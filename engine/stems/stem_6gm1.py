"""
Stem generator for 6.GM.1:
  Convert between measurement systems (customary to metric and metric to
  customary) given the conversion factors, and use these conversions in
  solving real-world problems.

Content Limits:
  - Conversion factors are provided on a grade-level reference sheet
  - Items should not require calculation of a unit rate to solve
  - Scoring allows use of either direction's conversion rate
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: limited to whole numbers; rounding not necessary
  Medium: mixture of whole numbers and decimals; rounding may be needed
  Difficult: limited to decimals; rounding required

4 Stems from the Item Spec:
  Stem 1 (Below-MC):       Identify the expression to convert between systems (DOK 1, Easy)
  Stem 2 (Approaching-NR): Convert between systems in a math context (DOK 1, Easy)
  Stem 3 (At-NR):          Real-world conversion problem (DOK 2, Medium)
  Stem 4 (Above-NR):       Multi-step real-world conversion (DOK 2, Difficult)
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
from engine.context_pools import pick_name


STANDARD_CODE = "6.GM.1"
VARIANTS_PER_STEM = 20


# Pre-computed (cust_unit, met_unit, factor_display, input_val, from_u, to_u, result)
# tuples where both input and result are whole numbers (Easy tier).
EASY_PAIRS = [
    # inches → centimeters (factor 2.54, multiples of 50)
    ("inches", "centimeters", "1 in. = 2.54 cm", 50, "inches", "centimeters", 127),
    ("inches", "centimeters", "1 in. = 2.54 cm", 100, "inches", "centimeters", 254),
    ("inches", "centimeters", "1 in. = 2.54 cm", 150, "inches", "centimeters", 381),
    ("inches", "centimeters", "1 in. = 2.54 cm", 200, "inches", "centimeters", 508),
    ("inches", "centimeters", "1 in. = 2.54 cm", 250, "inches", "centimeters", 635),
    ("inches", "centimeters", "1 in. = 2.54 cm", 300, "inches", "centimeters", 762),
    # centimeters → inches (reverse)
    ("inches", "centimeters", "1 in. = 2.54 cm", 127, "centimeters", "inches", 50),
    ("inches", "centimeters", "1 in. = 2.54 cm", 254, "centimeters", "inches", 100),
    ("inches", "centimeters", "1 in. = 2.54 cm", 381, "centimeters", "inches", 150),
    ("inches", "centimeters", "1 in. = 2.54 cm", 508, "centimeters", "inches", 200),
    # ounces → grams (factor 28.35, multiples of 20)
    ("ounces", "grams", "1 oz = 28.35 g", 20, "ounces", "grams", 567),
    ("ounces", "grams", "1 oz = 28.35 g", 40, "ounces", "grams", 1134),
    ("ounces", "grams", "1 oz = 28.35 g", 60, "ounces", "grams", 1701),
    ("ounces", "grams", "1 oz = 28.35 g", 80, "ounces", "grams", 2268),
    ("ounces", "grams", "1 oz = 28.35 g", 100, "ounces", "grams", 2835),
    # grams → ounces (reverse)
    ("ounces", "grams", "1 oz = 28.35 g", 567, "grams", "ounces", 20),
    ("ounces", "grams", "1 oz = 28.35 g", 1134, "grams", "ounces", 40),
    ("ounces", "grams", "1 oz = 28.35 g", 1701, "grams", "ounces", 60),
    # gallons → liters (factor 3.785, multiples of 200)
    ("gallons", "liters", "1 gal = 3.785 L", 200, "gallons", "liters", 757),
    ("gallons", "liters", "1 gal = 3.785 L", 400, "gallons", "liters", 1514),
]


# ============================================================
# CONVERSION FACTORS
# Each entry: (customary_unit, metric_unit, factor, display)
# factor means: 1 customary_unit = factor metric_units
# ============================================================

# Each entry: (customary_unit, metric_unit, factor, display, category)
CONVERSIONS = [
    ("inches",       "centimeters",  Fraction(254, 100),    "1 in. = 2.54 cm",     "length"),
    ("feet",         "meters",       Fraction(3048, 10000), "1 ft = 0.305 m",      "length"),
    ("yards",        "meters",       Fraction(9144, 10000), "1 yd = 0.914 m",      "length"),
    ("miles",        "kilometers",   Fraction(1609, 1000),  "1 mi = 1.609 km",     "length"),
    ("ounces",       "grams",        Fraction(2835, 100),   "1 oz = 28.35 g",      "weight"),
    ("pounds",       "kilograms",    Fraction(4536, 10000), "1 lb = 0.454 kg",     "weight"),
    ("fluid ounces", "milliliters",  Fraction(2957, 100),   "1 fl oz = 29.57 mL",  "volume"),
    ("quarts",       "liters",       Fraction(946, 1000),   "1 qt = 0.946 L",      "volume"),
    ("gallons",      "liters",       Fraction(3785, 1000),  "1 gal = 3.785 L",     "volume"),
]

# Real-world contexts for Stem 3, keyed by category
CONTEXTS_STEM3 = {
    "length": [
        "{name} is traveling to Canada. The distance is {val} {from_u}. How many {to_u} is that?",
        "{name}'s height is {val} {from_u}. What is {name}'s height in {to_u}?",
        "The classroom is {val} {from_u} long. What is the length in {to_u}?",
        "A swimming pool is {val} {from_u} long. How many {to_u} is that?",
        "A hiking trail is {val} {from_u}. How many {to_u} is the trail?",
    ],
    "weight": [
        "A package weighs {val} {from_u}. What is the weight in {to_u}?",
        "{name} bought {val} {from_u} of flour. How many {to_u} is that?",
        "A newborn baby weighs {val} {from_u}. What is the weight in {to_u}?",
        "{name} needs {val} {from_u} of sugar for a recipe. How many {to_u} is that?",
    ],
    "volume": [
        "{name} bought a container holding {val} {from_u}. How many {to_u} is that?",
        "A recipe calls for {val} {from_u} of milk. How many {to_u} is that?",
        "{name} needs {val} {from_u} of water for a science experiment. How many {to_u} is that?",
        "A fish tank holds {val} {from_u} of water. How many {to_u} is that?",
    ],
}

# Multi-step contexts for Stem 4, keyed by category
CONTEXTS_STEM4 = {
    "length": [
        "{name} ran {v1} {from_u} on Monday and {v2} {from_u} on Tuesday. How many total {to_u} did {name} run?",
        "{name} has {v1} {from_u} of ribbon and uses {v2} {from_u}. How many {to_u} of ribbon are left?",
        "A road has two sections: {v1} {from_u} and {v2} {from_u}. What is the total length in {to_u}?",
    ],
    "weight": [
        "{name} bought {v1} {from_u} of chicken and {v2} {from_u} of beef. How many total {to_u} of meat is that?",
        "A box contains {v1} {from_u} of apples and {v2} {from_u} of oranges. What is the total weight in {to_u}?",
    ],
    "volume": [
        "A recipe needs {v1} {from_u} of juice and {v2} {from_u} of water. How many total {to_u} of liquid is needed?",
        "{name} poured {v1} {from_u} of milk and {v2} {from_u} of cream into a bowl. How many total {to_u} is that?",
    ],
}


def _fmt(val, decimals=2):
    """Format a Fraction as a rounded decimal string."""
    f = float(val)
    if f == int(f):
        return str(int(f))
    s = f"{f:.{decimals}f}".rstrip('0').rstrip('.')
    return s


class Stem6GM1:
    """Generates ~20 variants for each of 4 stems from the 6.GM.1 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 1, Easy)
    # Identify the expression that converts between measurement systems
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        conv = rng.choice(CONVERSIONS)
        cust_unit, met_unit, factor, ref_display, category = conv

        # Pick a whole number input value
        input_val = rng.randint(3, 50)

        # Randomly choose direction
        if rng.random() < 0.5:
            from_u, to_u = cust_unit, met_unit
            correct_expr = f"{input_val} x {_fmt(factor)}"
            wrong_div = f"{input_val} / {_fmt(factor)}"
            wrong_add = f"{input_val} + {_fmt(factor)}"
            wrong_sub = f"{input_val} - {_fmt(factor)}"
        else:
            from_u, to_u = met_unit, cust_unit
            correct_expr = f"{input_val} / {_fmt(factor)}"
            wrong_div = f"{input_val} x {_fmt(factor)}"
            wrong_add = f"{input_val} + {_fmt(factor)}"
            wrong_sub = f"{input_val} - {_fmt(factor)}"

        all_options = [
            (correct_expr, True),
            (wrong_div, False),
            (wrong_add, False),
            (wrong_sub, False),
        ]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = (
            f"Reference: {ref_display}\n\n"
            f"Which expression can be used to convert "
            f"{input_val} {from_u} to {to_u}?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=(
                f"To convert {from_u} to {to_u}, use: {ref_display}.\n"
                f"The correct expression is {correct_expr}."
            ),
            choices=choices, context_scenario="unit conversion expression",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - NR (DOK 1, Easy)
    # Convert between measurement systems (whole-number results)
    # ================================================================

    def stem2_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        # Easy tier: use pre-computed pairs with whole-number results
        pair = EASY_PAIRS[variant_idx % len(EASY_PAIRS)]
        cust_unit, met_unit, ref_display, input_val, from_u, to_u, result = pair

        result_str = str(result)
        input_str = str(input_val)

        stem_text = (
            f"Reference: {ref_display}\n\n"
            f"Convert. How many {to_u} are equivalent to {input_str} {from_u}?"
        )

        # Determine direction for worked solution
        if from_u == cust_unit:
            factor_str = ref_display.split("= ")[1].split(" ")[0]
            worked = (f"Using {ref_display}:\n"
                      f"{input_str} {from_u} x {factor_str} = {result_str} {to_u}")
        else:
            factor_str = ref_display.split("= ")[1].split(" ")[0]
            worked = (f"Using {ref_display}:\n"
                      f"{input_str} {from_u} / {factor_str} = {result_str} {to_u}")

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=result_str, answer_latex=result_str,
            worked_solution=worked,
            context_scenario="unit conversion",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: At Proficiency - NR (DOK 2, Medium)
    # Solve real-world conversion problems
    # ================================================================

    def stem3_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        conv = rng.choice(CONVERSIONS)
        cust_unit, met_unit, factor, ref_display, category = conv
        name = pick_name(rng)

        # Medium tier values
        if rng.random() < 0.4:
            input_val = Fraction(rng.randint(3, 100))
        else:
            input_val = Fraction(rng.randint(10, 999), 10)

        # Direction
        if rng.random() < 0.5:
            from_u, to_u = cust_unit, met_unit
            result = input_val * factor
        else:
            from_u, to_u = met_unit, cust_unit
            result = input_val / factor

        result_str = _fmt(result)
        input_str = _fmt(input_val)

        template = rng.choice(CONTEXTS_STEM3[category])
        context = template.format(
            name=name, val=input_str, from_u=from_u, to_u=to_u
        )

        stem_text = (
            f"Reference: {ref_display}\n\n"
            f"{context}\n\n"
            f"Round to the nearest hundredth if necessary."
        )

        if from_u == cust_unit:
            worked = f"{input_str} {from_u} x {_fmt(factor)} = {result_str} {to_u}"
        else:
            worked = f"{input_str} {from_u} / {_fmt(factor)} = {result_str} {to_u}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=result_str, answer_latex=result_str,
            worked_solution=worked,
            context_scenario="real-world unit conversion",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: Above Proficiency - NR (DOK 2, Difficult)
    # Multi-step real-world conversion
    # ================================================================

    def stem4_above_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        conv = rng.choice(CONVERSIONS)
        cust_unit, met_unit, factor, ref_display, category = conv
        name = pick_name(rng)

        # Difficult tier: decimal inputs
        v1 = Fraction(rng.randint(10, 999), 10)
        v2 = Fraction(rng.randint(10, 999), 10)

        template = rng.choice(CONTEXTS_STEM4[category])

        # Determine if adding or subtracting
        is_subtraction = "uses" in template or "left" in template
        if is_subtraction and v2 > v1:
            v1, v2 = v2, v1  # ensure positive result

        if is_subtraction:
            combined = v1 - v2
        else:
            combined = v1 + v2

        # Direction: customary input -> metric output
        from_u, to_u = cust_unit, met_unit
        result = combined * factor
        result_str = _fmt(result)

        context = template.format(
            name=name, v1=_fmt(v1), v2=_fmt(v2),
            from_u=from_u, to_u=to_u
        )

        stem_text = (
            f"Reference: {ref_display}\n\n"
            f"{context}\n\n"
            f"Round to the nearest hundredth if necessary."
        )

        if is_subtraction:
            worked = (
                f"Step 1: {_fmt(v1)} - {_fmt(v2)} = {_fmt(combined)} {from_u}\n"
                f"Step 2: {_fmt(combined)} x {_fmt(factor)} = {result_str} {to_u}"
            )
        else:
            worked = (
                f"Step 1: {_fmt(v1)} + {_fmt(v2)} = {_fmt(combined)} {from_u}\n"
                f"Step 2: {_fmt(combined)} x {_fmt(factor)} = {result_str} {to_u}"
            )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.NR,
                               Difficulty.DIFFICULT, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=result_str, answer_latex=result_str,
            worked_solution=worked,
            context_scenario="multi-step unit conversion",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_approaching_nr,
            self.stem3_at_nr,
            self.stem4_above_nr,
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
            3: self.stem3_at_nr,
            4: self.stem4_above_nr,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-4.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 6.GM.1 question variants...")
    gen = Stem6GM1(seed=42)
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
