"""
Stem generator for 6.RP.5:
  Use variables to represent two quantities in a proportional relationship
  in a real-world problem; write an equation to express one quantity, the
  dependent variable, in terms of the other quantity, the independent variable.
  Analyze the relationship between the dependent and independent variables
  using graphs and tables, and relate these to the equation.

Content Limits:
  - Equations must be in the form y = px
  - Identifying or writing equations FROM A GRAPH is NOT part of this standard
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: calculations not required
  Medium: whole numbers only
  Difficult: decimals or fractions

5 Stems from the Item Spec:
  Stem 1 (Below-MC):  Identify independent and dependent variables (DOK 1, easy)
  Stem 2 (Approaching-MC): Identify equation y=px from a table (DOK 2, medium)
  Stem 3 (Approaching-NR): Complete a table for a proportional relationship (DOK 2, medium)
  Stem 4 (At-NR):     Solve using proportional relationship (DOK 2, medium)
  Stem 5 (Above-MC):  Critique statements about proportional relationship (DOK 3, easy)
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
from engine.context_pools import pick_name, CONTEXTS_6RP5


STANDARD_CODE = "6.RP.5"
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


class Stem6RP5:
    """Generates ~20 variants for each of 5 stems from the 6.RP.5 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 1, Easy)
    # Identify independent and dependent variables
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        scenarios = [
            {"desc": "The number of miles biked and the number of calories burned",
             "independent": "miles biked", "dependent": "calories burned"},
            {"desc": "The number of lemonade cups sold and the amount of money earned",
             "independent": "cups sold", "dependent": "money earned"},
            {"desc": "The number of hours worked and the total pay",
             "independent": "hours worked", "dependent": "total pay"},
            {"desc": "The number of items purchased and the total cost",
             "independent": "items purchased", "dependent": "total cost"},
            {"desc": "The number of days and the total food a pet eats",
             "independent": "number of days", "dependent": "total food eaten"},
            {"desc": "The number of gallons of gas used and the total miles driven",
             "independent": "gallons of gas", "dependent": "miles driven"},
        ]
        scenario = rng.choice(scenarios)

        correct = scenario["dependent"]
        distractors = [
            scenario["independent"],
            "both variables",
            "neither variable",
        ]

        all_options = [(correct, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = (
            f"{scenario['desc']}.\n\n"
            f"What is the dependent variable?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=f"The dependent variable changes based on the independent variable. {correct} depends on {scenario['independent']}.",
            choices=choices, context_scenario="identify variables",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - MC (DOK 2, Medium)
    # Identify the equation y=px from a table
    # ================================================================

    def stem2_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        ctx = rng.choice(CONTEXTS_6RP5)
        name = pick_name(rng)

        rate = rng.randint(2, 12)
        x_vals = [1, 2, 3, 4, 5]
        y_vals = [rate * x for x in x_vals]

        correct = f"y = {rate}x"
        distractors = [
            f"y = {rate} + x",
            f"y = x/{rate}",
            f"y = {rate + 1}x",
        ]

        all_options = [(correct, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        desc = ctx["desc"].format(name=name, rate=rate)

        stem_text = (
            f"{desc}\n\n"
            f"The table shows the relationship.\n\n"
            f"Which equation represents this relationship?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.MEDIUM, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=f"Each y-value is {rate} times the x-value. So y = {rate}x.",
            choices=choices, context_scenario="table to equation",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx,
            render_data={
                "type": "data_table",
                "headers": ["x", "y"],
                "rows": [[str(x), str(y)] for x, y in zip(x_vals, y_vals)],
            }
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - NR (DOK 2, Medium)
    # Complete a table for proportional relationship
    # ================================================================

    def stem3_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        name = pick_name(rng)
        rate = rng.randint(2, 15)

        x_vals = list(range(1, 6))
        y_vals = [rate * x for x in x_vals]

        # Hide one y-value
        hide_idx = rng.randint(2, 4)
        answer = y_vals[hide_idx]

        contexts = [
            f"{name} sells lemonade for ${rate} per cup.",
            f"{name} earns ${rate} per hour.",
            f"A cat eats {rate} ounces of food per day.",
        ]
        ctx = rng.choice(contexts)

        # Build table rows with "?" for the hidden value
        tbl_rows = []
        for i, (x, y) in enumerate(zip(x_vals, y_vals)):
            tbl_rows.append([str(x), "?" if i == hide_idx else str(y)])

        stem_text = (
            f"{ctx}\n\n"
            f"The table shows this relationship.\n\n"
            f"What is the missing value?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=str(answer), answer_latex=str(answer),
            worked_solution=f"y = {rate}x. When x = {x_vals[hide_idx]}, y = {rate} x {x_vals[hide_idx]} = {answer}.",
            context_scenario="complete proportional table",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx,
            render_data={
                "type": "data_table",
                "headers": ["x", "y"],
                "rows": tbl_rows,
            }
        )

    # ================================================================
    # STEM 4: At Proficiency - NR (DOK 2, Medium)
    # Solve using proportional relationship
    # ================================================================

    def stem4_at_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        name = pick_name(rng)
        rate = rng.randint(3, 15)
        target_x = rng.randint(6, 20)
        answer = rate * target_x

        contexts = [
            {"setup": f"{name} walks dogs and earns ${rate} per walk.",
             "x_var": "walks", "y_var": "dollars earned", "unit": "dollars"},
            {"setup": f"A machine produces {rate} parts per hour.",
             "x_var": "hours", "y_var": "parts produced", "unit": "parts"},
            {"setup": f"{name}'s cat eats {rate} ounces of food per day.",
             "x_var": "days", "y_var": "ounces of food", "unit": "ounces"},
        ]
        ctx = rng.choice(contexts)

        stem_text = (
            f"{ctx['setup']}\n\n"
            f"Part A: Write an equation in the form y = px that represents "
            f"the relationship between {ctx['x_var']} (x) and {ctx['y_var']} (y).\n\n"
            f"Part B: Use your equation to find y when x = {target_x}."
        )

        part_a = QuestionPart(
            label="Part A",
            prompt=f"Write the equation.",
            prompt_latex=f"Write the equation.",
            answer=f"y = {rate}x",
            answer_latex=f"$y = {rate}x$",
            item_type=ItemType.EQ,
        )
        part_b = QuestionPart(
            label="Part B",
            prompt=f"Find y when x = {target_x}.",
            prompt_latex=f"Find $y$ when $x = {target_x}$.",
            answer=str(answer),
            answer_latex=str(answer),
            item_type=ItemType.NR,
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MP,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"Part A: y = {rate}x; Part B: {answer}",
            answer_latex=f"Part A: $y = {rate}x$; Part B: {answer}",
            worked_solution=f"Part A: y = {rate}x\nPart B: y = {rate} x {target_x} = {answer} {ctx['unit']}.",
            parts=[part_a, part_b],
            context_scenario="proportional relationship application",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above Proficiency - MP (DOK 3, Medium)
    # Critique + apply a proportional relationship equation
    # ================================================================

    def stem5_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        name1 = pick_name(rng)
        name2 = pick_name(rng)
        while name2 == name1:
            name2 = pick_name(rng)

        rate = rng.randint(5, 50)
        test_x = rng.randint(6, 20)
        correct_y = rate * test_x

        contexts = [
            (f"A train travels at a constant speed of {rate} miles per hour.", "miles", "hours"),
            (f"A factory produces {rate} widgets per hour.", "widgets", "hours"),
            (f"Water flows at a rate of {rate} gallons per minute.", "gallons", "minutes"),
        ]
        ctx, y_unit, x_unit = rng.choice(contexts)

        correct_eq = f"y = {rate}x"
        wrong_eq = f"y = {rate} + x"

        stem_text = (
            f"{ctx}\n\n"
            f"{name1} says the relationship can be modeled by {correct_eq}.\n"
            f"{name2} says the relationship can be modeled by {wrong_eq}.\n\n"
            f"Part A: Which student's equation correctly represents "
            f"this proportional relationship? Explain why the other "
            f"equation is incorrect.\n\n"
            f"Part B: Using the correct equation, find the value of y "
            f"when x = {test_x}."
        )

        part_a = QuestionPart(
            label="Part A",
            prompt=f"Which student is correct and why?",
            prompt_latex=f"Which student is correct and why?",
            answer=f"{name1} is correct. {correct_eq} multiplies the rate by x (proportional). {wrong_eq} only adds {rate} once (not proportional).",
            answer_latex=f"{name1} is correct.",
            item_type=ItemType.ER,
        )
        part_b = QuestionPart(
            label="Part B",
            prompt=f"y when x = {test_x}",
            prompt_latex=f"$y$ when $x = {test_x}$",
            answer=str(correct_y),
            answer_latex=str(correct_y),
            item_type=ItemType.NR,
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.MEDIUM, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.MEDIUM, dok=3, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"Part A: {name1} is correct; Part B: {correct_y}",
            answer_latex=f"Part A: {name1}; Part B: {correct_y}",
            worked_solution=(
                f"{name1} is correct. A proportional relationship is y = px, not y = p + x.\n"
                f"{correct_eq} means the quantity is multiplied by {rate} for each unit.\n"
                f"{wrong_eq} adds {rate} once, which is not proportional.\n"
                f"Using {correct_eq}: y = {rate} x {test_x} = {correct_y} {y_unit}."
            ),
            parts=[part_a, part_b],
            context_scenario="critique proportional equation",
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
            self.stem3_approaching_nr,
            self.stem4_at_mp,
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
            3: self.stem3_approaching_nr,
            4: self.stem4_at_mp,
            5: self.stem5_above_mp,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-5.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 6.RP.5 question variants...")
    gen = Stem6RP5(seed=42)
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
