"""
Stem generator for 6.AF.1:
  Define and use multiple variables when writing expressions to represent
  real-world and other mathematical problems, and evaluate them for given values.

Content Limits:
  - Limit expressions to three or fewer unique variables
  - Exponents must be whole numbers
  - Items should be limited to whole numbers with common fractions and decimals used sparingly
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: whole numbers only
  Medium: mixture of whole numbers and decimals; exponents may be used
  Difficult: only decimals are used; exponents may be used

6 Stems from the Item Spec:
  Stem 1 (Below-MC): Choose expression matching a verbal description, 1 var, 1 op (DOK 1, easy)
  Stem 2 (Below-EQ): Write expression from verbal description with exponent (DOK 2, medium)
  Stem 3 (Approaching-MC): Choose expression for a real-world situation, 1 var (DOK 2, medium)
  Stem 4 (Approaching-MC): Evaluate an expression for a given value (DOK 1, easy)
  Stem 5 (At-MP): Two-variable real-world expression: Part A select, Part B evaluate (DOK 2, medium)
  Stem 6 (Above-NR): Substitute 3 variable values into expression and compute (DOK 2, difficult)
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
from engine.context_pools import pick_name, pick_name_pair


STANDARD_CODE = "6.AF.1"
VARIANTS_PER_STEM = 20


# ============================================================
# VERBAL DESCRIPTION TEMPLATES for expression writing
# ============================================================

# Template: (description_template, expression_template, distractor_templates)
# {a}, {b} are whole numbers; {var} is the variable

VERBAL_DESCRIPTIONS = [
    # "N less than the product of M and a number"
    {
        "desc": "{a} less than the product of {b} and a number",
        "expr": "{b}{var} - {a}",
        "distractors": [
            "{a} - {b}{var}",
            "{a}{var} - {b}",
            "{b}{var} + {a}",
        ],
    },
    # "N more than the quotient of a number and M"
    {
        "desc": "{a} more than the quotient of a number and {b}",
        "expr": "{var}/{b} + {a}",
        "distractors": [
            "{var}/{b} - {a}",
            "{a}/{var} + {b}",
            "{b}{var} + {a}",
        ],
    },
    # "the sum of N and the product of M and a number"
    {
        "desc": "the sum of {a} and the product of {b} and a number",
        "expr": "{a} + {b}{var}",
        "distractors": [
            "{a} - {b}{var}",
            "{a}{var} + {b}",
            "{a} + {b} + {var}",
        ],
    },
    # "the difference of a number and N, multiplied by M"
    {
        "desc": "the difference of a number and {a}, multiplied by {b}",
        "expr": "{b}({var} - {a})",
        "distractors": [
            "{b}{var} - {a}",
            "{a}({var} - {b})",
            "({var} + {a}) * {b}",
        ],
    },
    # "twice a number, decreased by N"
    {
        "desc": "twice a number, decreased by {a}",
        "expr": "2{var} - {a}",
        "distractors": [
            "2{var} + {a}",
            "2 - {a}{var}",
            "{a}{var} - 2",
        ],
    },
    # "N times the sum of a number and M"
    {
        "desc": "{a} times the sum of a number and {b}",
        "expr": "{a}({var} + {b})",
        "distractors": [
            "{a}{var} + {b}",
            "{a} + {b}{var}",
            "({var} + {a}) * {b}",
        ],
    },
    # "the quotient of N and a number, increased by M"
    {
        "desc": "the quotient of {a} and a number, increased by {b}",
        "expr": "{a}/{var} + {b}",
        "distractors": [
            "{var}/{a} + {b}",
            "{a}/{var} - {b}",
            "{a} + {b}/{var}",
        ],
    },
    # "M less than half a number"
    {
        "desc": "{a} less than half a number",
        "expr": "{var}/2 - {a}",
        "distractors": [
            "{a} - {var}/2",
            "{var}/2 + {a}",
            "2{var} - {a}",
        ],
    },
]

# Verbal descriptions involving exponents (for stem 2)
EXPONENT_DESCRIPTIONS = [
    {
        "desc": "the product of {var} raised to the second power and the difference of {var} and {a}",
        "expr": "{var}^2 * ({var} - {a})",
        "expr_latex": "{var}^2({var} - {a})",
    },
    {
        "desc": "{a} more than {var} raised to the third power",
        "expr": "{var}^3 + {a}",
        "expr_latex": "{var}^3 + {a}",
    },
    {
        "desc": "the sum of {var} raised to the second power and {a} times {var}",
        "expr": "{var}^2 + {a}{var}",
        "expr_latex": "{var}^2 + {a}{var}",
    },
    {
        "desc": "{a} less than the square of a number",
        "expr": "{var}^2 - {a}",
        "expr_latex": "{var}^2 - {a}",
    },
    {
        "desc": "the product of {a} and a number raised to the second power",
        "expr": "{a}{var}^2",
        "expr_latex": "{a}{var}^2",
    },
    {
        "desc": "the cube of a number, decreased by {a}",
        "expr": "{var}^3 - {a}",
        "expr_latex": "{var}^3 - {a}",
    },
]

# Real-world expression contexts (1 variable, for approaching proficiency)
REAL_WORLD_SINGLE_VAR = [
    {
        "setup": "A book of postage stamps costs ${total}. Each stamp costs ${unit_cost}.",
        "question": "Which expression can be used to determine how many stamps, {var}, are in one book of stamps?",
        "correct": "{total}/{var}",
        "correct_latex": "\\frac{{{total}}}{{{var}}}",
        "distractors": [
            "{total} - {var}",
            "{unit_cost} + {var}",
            "{unit_cost}{var}",
        ],
        "gen_fn": "stamps",
    },
    {
        "setup": "A movie theater charges ${fixed} to rent a party room and ${per_unit} per person.",
        "question": "Which expression represents the total cost for {var} people?",
        "correct": "{fixed} + {per_unit}{var}",
        "correct_latex": "{fixed} + {per_unit}{var}",
        "distractors": [
            "{fixed} * {per_unit}{var}",
            "{per_unit}{var} - {fixed}",
            "{fixed}{var} + {per_unit}",
        ],
        "gen_fn": "party",
    },
    {
        "setup": "{name} earns ${per_unit} per hour at a part-time job. {name} also receives a one-time bonus of ${fixed}.",
        "question": "Which expression represents the total earnings for {var} hours of work?",
        "correct": "{per_unit}{var} + {fixed}",
        "correct_latex": "{per_unit}{var} + {fixed}",
        "distractors": [
            "{per_unit} + {fixed}{var}",
            "({per_unit} + {fixed}){var}",
            "{per_unit}{var} - {fixed}",
        ],
        "gen_fn": "earnings",
    },
    {
        "setup": "A gym charges a ${fixed} registration fee plus ${per_unit} per month.",
        "question": "Which expression represents the total cost for {var} months of membership?",
        "correct": "{fixed} + {per_unit}{var}",
        "correct_latex": "{fixed} + {per_unit}{var}",
        "distractors": [
            "{per_unit}{var} - {fixed}",
            "{fixed}{var} + {per_unit}",
            "({fixed} + {per_unit}){var}",
        ],
        "gen_fn": "gym",
    },
    {
        "setup": "A parking garage charges ${fixed} for the first hour and ${per_unit} for each additional hour.",
        "question": "Which expression represents the total cost for {var} additional hours after the first?",
        "correct": "{fixed} + {per_unit}{var}",
        "correct_latex": "{fixed} + {per_unit}{var}",
        "distractors": [
            "{per_unit}{var} - {fixed}",
            "({fixed} + {per_unit}){var}",
            "{fixed}{var}",
        ],
        "gen_fn": "parking",
    },
    {
        "setup": "A cell phone plan costs ${fixed} per month plus ${per_unit} per text message sent.",
        "question": "Which expression represents the monthly cost for {var} text messages?",
        "correct": "{fixed} + {per_unit}{var}",
        "correct_latex": "{fixed} + {per_unit}{var}",
        "distractors": [
            "{per_unit}{var} - {fixed}",
            "{fixed}{var}",
            "({fixed} - {per_unit}){var}",
        ],
        "gen_fn": "phone",
    },
]

# Two-variable real-world contexts (for At Proficiency)
REAL_WORLD_TWO_VAR = [
    {
        "setup": "{name} sets up a booth at a carnival to sell {item1} and {item2}.\n\n- The booth rental costs ${rental}.\n- Each {item1_s}, {var1}, sells for ${price1}.\n- Each {item2_s}, {var2}, sells for ${price2}.",
        "question": "Identify the expression that models the total amount, in dollars, {name} will earn at the carnival.",
        "correct": "({price1}{var1} + {price2}{var2}) - {rental}",
        "distractors": [
            "{price1}{var1} + {price2}{var2}",
            "{price1}{var1} - {price2}{var2}",
            "{rental} - ({price1}{var1} + {price2}{var2})",
        ],
        "eval_prompt": "What is the total amount, in dollars, {name} will earn if {var1} = {val1} and {var2} = {val2}?",
        "items": [
            ("muffins", "muffin", "cookies", "cookie"),
            ("cupcakes", "cupcake", "brownies", "brownie"),
            ("lemonades", "lemonade", "popcorn bags", "popcorn bag"),
            ("bracelets", "bracelet", "keychains", "keychain"),
            ("bookmarks", "bookmark", "stickers", "sticker pack"),
        ],
    },
    {
        "setup": "{name} runs a small business selling {item1} and {item2} online.\n\n- Shipping costs a flat ${rental}.\n- Each {item1_s}, {var1}, is sold for ${price1}.\n- Each {item2_s}, {var2}, is sold for ${price2}.",
        "question": "Identify the expression that models the total profit, in dollars, after shipping.",
        "correct": "({price1}{var1} + {price2}{var2}) - {rental}",
        "distractors": [
            "{price1}{var1} + {price2}{var2}",
            "{price1}{var1} - {price2}{var2}",
            "{rental} - ({price1}{var1} + {price2}{var2})",
        ],
        "eval_prompt": "What is the total profit, in dollars, if {var1} = {val1} and {var2} = {val2}?",
        "items": [
            ("t-shirts", "t-shirt", "hats", "hat"),
            ("paintings", "painting", "sketches", "sketch"),
            ("candles", "candle", "soaps", "soap"),
        ],
    },
]

# Three-variable expression contexts (for Above Proficiency)
THREE_VAR_CONTEXTS = [
    {
        "setup": "A zoo is building an enclosure. The total area is {var1}^2 square units. Two sections of area {var2} * {var3} are removed.",
        "expr": "{var1}^2 - 2 * {var2} * {var3}",
        "expr_display": "{var1}^2 - 2{var2}{var3}",
        "eval_desc": "What is the remaining area, in square units, if {var1} = {val1}, {var2} = {val2}, and {var3} = {val3}?",
    },
    {
        "setup": "A farmer has a rectangular field that is {var1} feet long and {var2} feet wide. A path of width {var3} feet runs along one side.",
        "expr": "{var1} * {var2} - {var1} * {var3}",
        "expr_display": "{var1}{var2} - {var1}{var3}",
        "eval_desc": "What is the remaining area, in square feet, if {var1} = {val1}, {var2} = {val2}, and {var3} = {val3}?",
    },
    {
        "setup": "A store sells {var1} boxes of large items at ${price1} each and {var2} boxes of small items at ${price2} each. Delivery costs ${var3} per trip.",
        "expr": "{price1} * {var1} + {price2} * {var2} - {var3}",
        "expr_display": "{price1}{var1} + {price2}{var2} - {var3}",
        "eval_desc": "What is the total, in dollars, if {var1} = {val1}, {var2} = {val2}, and {var3} = {val3}?",
    },
]


class Stem6AF1:
    """Generates ~20 variants for each of 6 stems from the 6.AF.1 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 1, Easy)
    # "7 less than the product of 2 and a number" → choose expression
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        a = int(gen.whole_number(2, 15))
        b = int(gen.whole_number(2, 12))
        var = rng.choice(["x", "n", "y", "p"])

        template = rng.choice(VERBAL_DESCRIPTIONS)
        desc = template["desc"].format(a=a, b=b, var=var)
        correct = template["expr"].format(a=a, b=b, var=var)
        distractors = [d.format(a=a, b=b, var=var) for d in template["distractors"]]

        all_options = [(correct, True)] + [(d, False) for d in distractors[:3]]
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

        stem_text = (
            f"A description of an expression is given.\n\n"
            f"\"{desc}\"\n\n"
            f"Choose the expression that represents the description."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY,
            dok=1,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=correct_letter,
            answer_latex=correct_letter,
            worked_solution=f'"{desc}" translates to {correct}.',
            choices=choices,
            context_scenario="verbal description to expression",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Below Proficiency - EQ (DOK 2, Medium)
    # "the product of x raised to the second power and the difference
    #  of x and 14" → write expression
    # ================================================================

    def stem2_below_eq(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        a = int(gen.whole_number(2, 20))
        var = rng.choice(["x", "n", "y", "t"])

        template = rng.choice(EXPONENT_DESCRIPTIONS)
        desc = template["desc"].format(a=a, var=var)
        expr = template["expr"].format(a=a, var=var)
        expr_latex = template["expr_latex"].format(a=a, var=var)

        stem_text = (
            f"A description of an expression is given.\n\n"
            f"\"{desc}\"\n\n"
            f"Write the expression that is described."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.EQ,
                               Difficulty.MEDIUM, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.MEDIUM,
            dok=2,
            item_type=ItemType.EQ,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=expr,
            answer_latex=f"${expr_latex}$",
            worked_solution=f'"{desc}" translates to the expression {expr}.',
            context_scenario="verbal description with exponents",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - MC (DOK 2, Medium)
    # "A book of postage stamps costs $14.60. Each stamp costs $0.73.
    #  Which expression determines how many stamps, s, are in one book?"
    # ================================================================

    def stem3_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        ctx = rng.choice(REAL_WORLD_SINGLE_VAR)
        name = pick_name(rng)
        var = rng.choice(["s", "n", "p", "x"])

        # Generate context-appropriate numbers
        if ctx["gen_fn"] == "stamps":
            unit_cost = gen.decimal_2place(0.25, 2.50)
            count = int(gen.whole_number(10, 30))
            total = unit_cost * count
            params = {"total": RationalNumber(total, "decimal").display(),
                      "unit_cost": RationalNumber(unit_cost, "decimal").display(),
                      "var": var, "name": name}
        else:
            fixed = int(gen.whole_number(10, 300))
            per_unit = gen.decimal_2place(1.00, 25.00)
            params = {"fixed": str(fixed),
                      "per_unit": RationalNumber(per_unit, "decimal").display(),
                      "var": var, "name": name}

        setup = ctx["setup"].format(**params)
        question = ctx["question"].format(**params)
        correct = ctx["correct"].format(**params)
        distractors = [d.format(**params) for d in ctx["distractors"]]

        all_options = [(correct, True)] + [(d, False) for d in distractors[:3]]
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

        stem_text = f"{setup}\n\n{question}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.MEDIUM, 3, variant_idx)

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
            worked_solution=f"The correct expression is {correct} because it models the given situation.",
            choices=choices,
            context_scenario=ctx["gen_fn"],
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: Approaching Proficiency - MC (DOK 1, Easy)
    # "A movie theater charges $200 to rent a party room and $7 per person.
    #  Total cost = 200 + 7p. What is the total cost if p = 18?"
    # ================================================================

    def stem4_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        fixed = int(gen.whole_number(50, 500))
        per_unit = int(gen.whole_number(3, 25))
        var = rng.choice(["p", "n", "x", "t"])
        val = int(gen.whole_number(5, 30))

        correct_answer = fixed + per_unit * val

        # Context scenarios
        contexts = [
            f"A movie theater charges ${fixed} to rent a party room and ${per_unit} per person.",
            f"A catering company charges ${fixed} for setup and ${per_unit} per guest.",
            f"A bus rental costs ${fixed} plus ${per_unit} per mile traveled.",
            f"A printing shop charges ${fixed} for design and ${per_unit} per copy.",
            f"A party venue charges ${fixed} for the space and ${per_unit} per hour.",
        ]
        context = rng.choice(contexts)

        expr_text = f"{fixed} + {per_unit}{var}"

        stem_text = (
            f"{context}\n\n"
            f"The total cost can be modeled by the expression {expr_text}, "
            f"where {var} represents the number of units.\n\n"
            f"What is the total cost if {var} = {val}?"
        )

        # Generate distractors using common errors
        distractors = set()
        distractors.add(per_unit * val)                # forgot the fixed cost
        distractors.add(fixed * per_unit * val)        # multiplied everything
        distractors.add(fixed + per_unit + val)        # added all three
        distractors.discard(correct_answer)
        # Pad if needed
        while len(distractors) < 3:
            d = correct_answer + rng.choice([-50, -20, 20, 50, 100])
            if d > 0 and d != correct_answer:
                distractors.add(d)

        distractors = list(distractors)[:3]

        all_options = [(f"${correct_answer}", True)] + [(f"${d}", False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i),
                text=text,
                text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"{expr_text} where {var} = {val}\n"
            f"= {fixed} + {per_unit}({val})\n"
            f"= {fixed} + {per_unit * val}\n"
            f"= {correct_answer}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.EASY, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY,
            dok=1,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=correct_letter,
            answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices,
            context_scenario="evaluate expression",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: At Proficiency - Multi-Part (DOK 2, Medium)
    # "Baker booth: muffins at $3.50, cookies at $2.00, rental $55
    #  Part A: choose expression for earnings
    #  Part B: evaluate if m=60, c=42"
    # ================================================================

    def stem5_at_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        ctx_template = rng.choice(REAL_WORLD_TWO_VAR)
        name = pick_name(rng)

        # Pick items
        items = rng.choice(ctx_template["items"])
        item1, item1_s, item2, item2_s = items

        var1 = item1_s[0]  # first letter
        var2 = item2_s[0]
        if var1 == var2:
            var2 = chr(ord(var2) + 1)

        # Generate prices and rental
        price1 = gen.decimal_1place(1.5, 8.0)
        price2 = gen.decimal_1place(1.0, 5.0)
        rental = int(gen.whole_number(20, 100))

        p1_rn = RationalNumber(price1, "decimal")
        p2_rn = RationalNumber(price2, "decimal")

        # Values for Part B
        val1 = int(gen.whole_number(20, 80))
        val2 = int(gen.whole_number(20, 80))
        earnings = price1 * val1 + price2 * val2 - rental
        earnings_rn = RationalNumber(earnings, "decimal")

        params = {
            "name": name, "item1": item1, "item1_s": item1_s,
            "item2": item2, "item2_s": item2_s,
            "var1": var1, "var2": var2,
            "price1": p1_rn.display(), "price2": p2_rn.display(),
            "rental": str(rental),
        }

        setup = ctx_template["setup"].format(**params)
        question_a = ctx_template["question"].format(**params)

        correct = f"({p1_rn.display()}{var1} + {p2_rn.display()}{var2}) - {rental}"

        distractors = [
            f"{p1_rn.display()}{var1} + {p2_rn.display()}{var2}",
            f"{p1_rn.display()}{var1} - {p2_rn.display()}{var2}",
            f"{rental} - ({p1_rn.display()}{var1} + {p2_rn.display()}{var2})",
        ]

        all_options = [(correct, True)] + [(d, False) for d in distractors]
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

        stem_text = (
            f"{setup}\n\n"
            f"Part A:\n{question_a}\n\n"
            f"Part B:\nWhat is the total amount, in dollars, "
            f"{name} will earn if {var1} = {val1} and {var2} = {val2}?"
        )

        part_a = QuestionPart(
            label="Part A",
            prompt=question_a,
            prompt_latex=question_a,
            answer=f"{correct_letter}. {correct}",
            answer_latex=f"{correct_letter}. ${correct}$",
            item_type=ItemType.MC,
        )
        part_b = QuestionPart(
            label="Part B",
            prompt=f"Evaluate for {var1} = {val1} and {var2} = {val2}.",
            prompt_latex=f"Evaluate for ${var1} = {val1}$ and ${var2} = {val2}$.",
            answer=f"${earnings_rn.display()}",
            answer_latex=f"\\${earnings_rn.display()}",
            item_type=ItemType.NR,
        )

        worked = (
            f"Part A: {correct}\n"
            f"Part B: ({p1_rn.display()}*{val1} + {p2_rn.display()}*{val2}) - {rental}\n"
            f"      = ({float(price1*val1):.2f} + {float(price2*val2):.2f}) - {rental}\n"
            f"      = {float(price1*val1 + price2*val2):.2f} - {rental}\n"
            f"      = {earnings_rn.display()}"
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
            answer_text=f"Part A: {correct_letter}; Part B: ${earnings_rn.display()}",
            answer_latex=f"Part A: {correct_letter}; Part B: \\${earnings_rn.display()}",
            worked_solution=worked,
            choices=choices,
            parts=[part_a, part_b],
            context_scenario=f"booth selling {item1} and {item2}",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 6: Above Proficiency - NR (DOK 2, Difficult)
    # "Zoo enclosure: area = x^2 - 2lw. Find area if x=30.5, l=5.25, w=6.5"
    # Answer: 862 square units
    # ================================================================

    def stem6_above_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)

        var1, var2, var3 = "x", "l", "w"

        # Generate decimal values for difficult tier
        val1 = gen.decimal_1place(15.0, 50.0)  # main dimension
        val2 = gen.decimal_2place(2.00, 10.00)  # length of removed section
        val3 = gen.decimal_1place(3.0, 12.0)    # width of removed section

        # Expression: x^2 - 2*l*w
        answer = val1 * val1 - 2 * val2 * val3

        v1_rn = RationalNumber(val1, "decimal")
        v2_rn = RationalNumber(val2, "decimal")
        v3_rn = RationalNumber(val3, "decimal")
        ans_rn = RationalNumber(answer, "decimal")

        contexts = [
            f"A zoo is building an enclosure for animals. The total area is {var1}^2 square units. Two identical areas of {var2} by {var3} are removed for walkways.",
            f"An architect designs a square courtyard with side length {var1}. Two rectangular gardens, each {var2} by {var3}, are placed inside.",
            f"A park has a square field with side {var1} meters. Two maintenance strips, each {var2} meters by {var3} meters, are excluded from the play area.",
        ]
        context = rng.choice(contexts)

        stem_text = (
            f"{context}\n\n"
            f"The remaining area can be found using the expression "
            f"{var1}^2 - 2{var2}{var3}, in square units.\n\n"
            f"What is the remaining area, in square units, "
            f"if {var1} = {v1_rn.display()}, {var2} = {v2_rn.display()}, "
            f"and {var3} = {v3_rn.display()}?"
        )

        v1_sq = val1 * val1
        two_lw = 2 * val2 * val3

        worked = (
            f"{var1}^2 - 2{var2}{var3}\n"
            f"= ({v1_rn.display()})^2 - 2({v2_rn.display()})({v3_rn.display()})\n"
            f"= {RationalNumber(v1_sq, 'decimal').display()} - {RationalNumber(two_lw, 'decimal').display()}\n"
            f"= {ans_rn.display()} square units"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.NR,
                               Difficulty.DIFFICULT, 6, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT,
            dok=2,
            item_type=ItemType.NR,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"{ans_rn.display()} square units",
            answer_latex=f"${ans_rn.display()}$ square units",
            worked_solution=worked,
            context_scenario="multi-variable area calculation",
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6,
            variant_index=variant_idx,
            render_data={
                "type": "rectangle_diagram",
                "side": v1_rn.display(),
                "cut_l": v2_rn.display(),
                "cut_w": v3_rn.display(),
            }
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_below_eq,
            self.stem3_approaching_mc,
            self.stem4_approaching_mc,
            self.stem5_at_mp,
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
            1: self.stem1_below_mc,
            2: self.stem2_below_eq,
            3: self.stem3_approaching_mc,
            4: self.stem4_approaching_mc,
            5: self.stem5_at_mp,
            6: self.stem6_above_nr,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-6.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 6.AF.1 question variants...")
    gen = Stem6AF1(seed=42)
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
