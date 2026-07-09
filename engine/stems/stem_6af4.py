"""
Stem generator for 6.AF.4:
  Write an inequality of the form x > c, x >= c, x < c, or x <= c,
  where c is a rational number, to represent a constraint or condition
  in a real-world or other mathematical problem. Explain that inequalities
  have infinitely many solutions and how to represent solutions on a number line.

Content Limits:
  - Inequalities must be in forms: x > c, x >= c, x < c, x <= c (or c > x, etc.)
  - Use only one variable
  - Items will NOT require students to compute or solve inequalities
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: whole numbers only
  Medium: integers (positive and negative whole numbers)
  Difficult: positive and negative fractions, mixed numbers, or decimals

5 Stems from the Item Spec:
  Stem 1 (Below-MC): Match inequality to number line representation (DOK 1, difficult)
  Stem 2 (Approaching-EQ): Write inequality from real-world constraint with negative integers (DOK 2, medium)
  Stem 3 (At-MP): Write inequality + identify number line, Part A MC + Part B (DOK 2, easy)
  Stem 4 (Above-MC): Two constraints -> complete pair of inequalities (DOK 2, easy)
  Stem 5 (Above-MP): Two constraints -> Part A: identify inequality pair, Part B: explain (DOK 3, difficult)
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


STANDARD_CODE = "6.AF.4"
VARIANTS_PER_STEM = 20

# Medium-tier contexts that naturally support negative integers
MEDIUM_CONSTRAINT_CONTEXTS = [
    {
        "setup": "A freezer must maintain a temperature below {limit} degrees Celsius to keep food frozen.",
        "question": "Write an inequality to represent {var}, the temperatures at which the freezer keeps food frozen.",
        "answer_op": "<",
        "unit": "degrees",
    },
    {
        "setup": "A weather station reports that the wind chill must be at least {limit} degrees for outdoor recess to be allowed.",
        "question": "Write an inequality to represent {var}, the wind chill temperatures that allow outdoor recess.",
        "answer_op": ">=",
        "unit": "degrees",
    },
    {
        "setup": "{name}'s bank account balance must stay above {limit} dollars to avoid a penalty fee.",
        "question": "Write an inequality to represent {var}, the account balance {name} must maintain.",
        "answer_op": ">",
        "unit": "dollars",
    },
    {
        "setup": "A submarine must not descend below {limit} meters relative to sea level.",
        "question": "Write an inequality to represent {var}, the depth in meters the submarine may reach.",
        "answer_op": ">=",
        "unit": "meters",
    },
    {
        "setup": "The lowest allowable temperature in the science lab is {limit} degrees Celsius.",
        "question": "Write an inequality to represent {var}, the temperatures allowed in the science lab.",
        "answer_op": ">=",
        "unit": "degrees",
    },
    {
        "setup": "A storage unit keeps items at a temperature less than or equal to {limit} degrees Fahrenheit.",
        "question": "Write an inequality to represent {var}, the temperatures maintained in the storage unit.",
        "answer_op": "<=",
        "unit": "degrees",
    },
]

# Real-world inequality contexts for "approaching" and "at" stems
SINGLE_CONSTRAINT_CONTEXTS = [
    {
        "setup": "{name} purchases a cell phone plan. Each month {name} receives {limit} gigabytes of data for free. If {name} exceeds {limit} gigabytes, {name} must pay extra.",
        "question": "Write an inequality to represent {var}, any amount of gigabytes {name} may receive for free each month.",
        "answer_op": "<=",
        "unit": "gigabytes",
    },
    {
        "setup": "A roller coaster requires riders to be at least {limit} inches tall.",
        "question": "Write an inequality to represent {var}, the height in inches of riders allowed on the roller coaster.",
        "answer_op": ">=",
        "unit": "inches",
    },
    {
        "setup": "A swimming pool has a maximum capacity of {limit} people at any time.",
        "question": "Write an inequality to represent {var}, the number of people allowed in the pool at one time.",
        "answer_op": "<=",
        "unit": "people",
    },
    {
        "setup": "{name} needs to save more than ${limit} to buy a new bicycle.",
        "question": "Write an inequality to represent {var}, the amount of money {name} needs to save.",
        "answer_op": ">",
        "unit": "dollars",
    },
    {
        "setup": "A package must weigh less than {limit} pounds to qualify for standard shipping.",
        "question": "Write an inequality to represent {var}, the weight in pounds of packages that qualify for standard shipping.",
        "answer_op": "<",
        "unit": "pounds",
    },
    {
        "setup": "Students must score at least {limit} points on the test to pass.",
        "question": "Write an inequality to represent {var}, the scores of students who pass.",
        "answer_op": ">=",
        "unit": "points",
    },
    {
        "setup": "A parking garage has a height limit of {limit} feet. Vehicles taller than {limit} feet cannot enter.",
        "question": "Write an inequality to represent {var}, the height in feet of vehicles that can enter the garage.",
        "answer_op": "<=",
        "unit": "feet",
    },
    {
        "setup": "{name} wants to buy tickets that cost less than ${limit} each.",
        "question": "Write an inequality to represent {var}, the ticket prices {name} is willing to pay.",
        "answer_op": "<",
        "unit": "dollars",
    },
]

# Contexts for the "at" proficiency (write inequality + graph on number line)
AT_PROFICIENCY_CONTEXTS = [
    {
        "setup": "A landscaper wants to buy a new lawnmower for the business. New lawnmowers cost at least ${limit}.",
        "question_a": "Choose the inequality that represents {var}, the amount of money needed to buy a new lawnmower.",
        "answer_op": ">=",
    },
    {
        "setup": "{name} needs to run more than {limit} miles this week for training.",
        "question_a": "Choose the inequality that represents {var}, the distance {name} needs to run.",
        "answer_op": ">",
    },
    {
        "setup": "A recipe requires the oven temperature to be at most {limit} degrees.",
        "question_a": "Choose the inequality that represents {var}, the allowable oven temperatures.",
        "answer_op": "<=",
    },
    {
        "setup": "A bag of apples must weigh at least {limit} pounds to be sold at the market.",
        "question_a": "Choose the inequality that represents {var}, the weight of bags that can be sold.",
        "answer_op": ">=",
    },
    {
        "setup": "{name}'s doctor said to drink at least {limit} cups of water each day.",
        "question_a": "Choose the inequality that represents {var}, the number of cups {name} should drink.",
        "answer_op": ">=",
    },
]

# Two-constraint contexts for "above" proficiency
TWO_CONSTRAINT_CONTEXTS = [
    {
        "setup": "An architect is planning a new playground. The area of the playground may be {low} square feet or greater but less than or equal to {high} square feet.",
        "var_desc": "{var}, all the possible areas, in square feet, of the playground",
    },
    {
        "setup": "A store's sale requires purchases to be at least ${low} but no more than ${high} to receive a discount.",
        "var_desc": "{var}, all the purchase amounts that qualify for the discount",
    },
    {
        "setup": "The temperature in a greenhouse must be at least {low} degrees but less than {high} degrees for the plants to grow properly.",
        "var_desc": "{var}, all the allowable temperatures in the greenhouse",
    },
    {
        "setup": "A water tank can hold between {low} and {high} gallons, inclusive.",
        "var_desc": "{var}, all the possible amounts of water in the tank",
    },
    {
        "setup": "Students must be between {low} and {high} years old, inclusive, to participate in the program.",
        "var_desc": "{var}, all the possible ages of participants",
    },
]

# Two-constraint contexts with time (for stem 5, like scavenger hunt)
TWO_CONSTRAINT_TIME = [
    {
        "setup": "A group of students participated in a scavenger hunt.\n\n- The first student completed the scavenger hunt in {low} minutes.\n- The last student completed the scavenger hunt in {high} minutes.",
        "question_a": "Which pair of inequalities represents {var}, all the possible times, in minutes, it took all the students to complete the scavenger hunt?",
        "explain": "because the fastest person completed in {low} minutes and the slowest in {high} minutes, all times must be between these values",
    },
    {
        "setup": "A science experiment measures the temperature of a liquid.\n\n- The lowest recorded temperature was {low} degrees.\n- The highest recorded temperature was {high} degrees.",
        "question_a": "Which pair of inequalities represents {var}, all the possible temperatures recorded during the experiment?",
        "explain": "because the lowest temperature was {low} degrees and the highest was {high} degrees, all temperatures must be between these values",
    },
    {
        "setup": "{name} tracked the number of steps taken each day for a week.\n\n- The fewest steps in a day was {low}.\n- The most steps in a day was {high}.",
        "question_a": "Which pair of inequalities represents {var}, all the possible daily step counts during the week?",
        "explain": "because the minimum was {low} steps and the maximum was {high} steps, all daily counts must be between these values",
    },
]


class Stem6AF4:
    """Generates ~20 variants for each of 5 stems from the 6.AF.4 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    @staticmethod
    def _pick_display(val):
        if val.denominator == 1:
            return "whole"
        d = val.denominator
        while d % 2 == 0: d //= 2
        while d % 5 == 0: d //= 5
        if d == 1:
            return "decimal"
        if val >= 1:
            return "mixed"
        return "fraction"

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 1, Difficult)
    # "Select the number line that represents x < -7/4."
    # (Since we can't draw number lines, we describe them textually)
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        # Generate inequality with fraction (difficult)
        # Can use negative values since this is about number line matching
        numer = int(gen.whole_number(1, 11))
        denom = rng.choice([2, 3, 4, 5, 8])
        is_negative = rng.random() < 0.5
        val = Fraction(numer, denom)
        if is_negative:
            val = -val

        op = rng.choice(["<", ">", "<=", ">="])
        var = rng.choice(["x", "n", "t"])

        if val >= 0:
            val_rn = RationalNumber(val, self._pick_display(val))
            val_display = val_rn.display()
        else:
            abs_val = abs(val)
            abs_rn = RationalNumber(abs_val, self._pick_display(abs_val))
            val_display = f"-{abs_rn.display()}"

        op_display = {">=": "\u2265", "<=": "\u2264"}.get(op, op)
        ineq_text = f"{var} {op_display} {val_display}"

        # Describe number line options textually
        # Correct: open/closed circle at val, arrow in correct direction
        circle = "closed" if op in ["<=", ">="] else "open"
        direction = "left" if op in ["<", "<="] else "right"

        correct_desc = f"{circle.title()} circle at {val_display}, arrow pointing {direction}"

        # Distractors: wrong circle type, wrong direction, both wrong
        wrong_circle = "closed" if circle == "open" else "open"
        wrong_direction = "right" if direction == "left" else "left"

        distractors = [
            f"{wrong_circle.title()} circle at {val_display}, arrow pointing {direction}",
            f"{circle.title()} circle at {val_display}, arrow pointing {wrong_direction}",
            f"{wrong_circle.title()} circle at {val_display}, arrow pointing {wrong_direction}",
        ]

        # Number line render data for each option
        float_val = float(val)
        correct_nl = {"type": "number_line", "value": float_val,
                      "circle_type": circle, "direction": direction}
        distractor_nls = [
            {"type": "number_line", "value": float_val,
             "circle_type": wrong_circle, "direction": direction},
            {"type": "number_line", "value": float_val,
             "circle_type": circle, "direction": wrong_direction},
            {"type": "number_line", "value": float_val,
             "circle_type": wrong_circle, "direction": wrong_direction},
        ]

        all_options = [(correct_desc, True, correct_nl)] + [
            (d, False, nl) for d, nl in zip(distractors, distractor_nls)
        ]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct, nl_data) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i),
                text=text,
                text_latex=text,
                is_correct=is_correct,
                render_data=nl_data,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = (
            f"Select the number line that represents {ineq_text}."
        )

        worked = (
            f"For {ineq_text}:\n"
            f"- Use a {'closed' if op in ['<=', '>='] else 'open'} circle because "
            f"{'the value is included (= sign)' if op in ['<=', '>='] else 'the value is NOT included (no = sign)'}.\n"
            f"- Arrow points {'left' if op in ['<', '<='] else 'right'} because "
            f"{'values are less than' if op in ['<', '<='] else 'values are greater than'} {val_display}."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.DIFFICULT, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.DIFFICULT,
            dok=1,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=correct_letter,
            answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices,
            context_scenario="number line matching",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - EQ (DOK 2, Medium)
    # Write inequality from real-world constraint using negative integers
    # ================================================================

    def stem2_approaching_eq(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        ctx = rng.choice(MEDIUM_CONSTRAINT_CONTEXTS)
        name = pick_name(rng)
        var = rng.choice(["x", "n", "t", "p"])

        # Medium tier: negative integers
        limit = -int(gen.whole_number(1, 30))

        setup = ctx["setup"].format(name=name, limit=limit, var=var)
        question = ctx["question"].format(name=name, var=var)
        op = ctx["answer_op"]
        op_display = {">=": "\u2265", "<=": "\u2264"}.get(op, op)

        answer = f"{var} {op_display} {limit}"

        stem_text = f"{setup}\n\n{question}"

        worked = (
            f"The constraint is that {var} must be {op_display} {limit} {ctx['unit']}.\n"
            f"The inequality is: {answer}"
        )

        # Blank number line for students to graph the answer
        circle = "closed" if op in ["<=", ">="] else "open"
        direction = "left" if op in ["<", "<="] else "right"
        nl_render = {
            "type": "number_line",
            "value": float(limit),
            "circle_type": circle,
            "direction": direction,
            "blank": True,
        }

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.EQ,
                               Difficulty.MEDIUM, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM,
            dok=2,
            item_type=ItemType.EQ,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=answer,
            answer_latex=f"${answer}$",
            worked_solution=worked,
            context_scenario=ctx["unit"] + " constraint",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2,
            variant_index=variant_idx,
            render_data=nl_render,
        )

    # ================================================================
    # STEM 3: At Proficiency - MP (DOK 2, Easy)
    # "Landscaper needs at least $325.
    #  Part A: Choose inequality. Part B: Graph on number line."
    # ================================================================

    def stem3_at_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        ctx = rng.choice(AT_PROFICIENCY_CONTEXTS)
        name = pick_name(rng)
        var = rng.choice(["x", "n", "d", "t"])

        # Easy tier: whole numbers
        limit = int(gen.whole_number(50, 500))
        op = ctx["answer_op"]
        op_symbols = {">=": "\u2265", ">": ">", "<=": "\u2264", "<": "<"}
        op_display = op_symbols[op]

        setup = ctx["setup"].format(name=name, limit=limit)
        question_a = ctx["question_a"].format(name=name, var=var)

        correct = f"{var} {op_display} {limit}"

        # Generate distractors with wrong operators
        all_ops = [">=", ">", "<=", "<"]
        wrong_ops = [o for o in all_ops if o != op]
        distractors = [f"{var} {op_symbols[o]} {limit}" for o in wrong_ops]

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

        # Number line description for Part B
        circle = "closed" if op in ["<=", ">="] else "open"
        direction = "left" if op in ["<", "<="] else "right"

        stem_text = (
            f"{setup}\n\n"
            f"{name} writes an inequality to represent {var}, the amount needed.\n\n"
            f"Part A:\n{question_a}\n\n"
            f"Part B:\nDescribe how to graph the solutions on a number line."
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
            prompt="Graph the solutions on a number line.",
            prompt_latex="Graph the solutions on a number line.",
            answer=f"{circle.title()} circle at {limit}, arrow pointing {direction}",
            answer_latex=f"{circle.title()} circle at {limit}, arrow pointing {direction}",
            item_type=ItemType.EQ,
        )

        worked = (
            f"Part A: {correct}\n"
            f"Part B: Place a {circle} circle at {limit} on the number line, "
            f"with an arrow pointing to the {direction}.\n"
            f"The circle is {circle} because the inequality "
            f"{'includes' if op in ['<=', '>='] else 'does not include'} the value {limit}."
        )

        # Blank number line for students to graph the solution
        nl_render = {
            "type": "number_line",
            "value": float(limit),
            "circle_type": circle,
            "direction": direction,
            "blank": True,
        }

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MP,
                               Difficulty.EASY, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.EASY,
            dok=2,
            item_type=ItemType.MP,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"Part A: {correct_letter}; Part B: {circle} circle at {limit}, arrow {direction}",
            answer_latex=f"Part A: {correct_letter}; Part B: {circle} circle at {limit}, arrow {direction}",
            worked_solution=worked,
            choices=choices,
            parts=[part_a, part_b],
            context_scenario="inequality with number line",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3,
            variant_index=variant_idx,
            render_data=nl_render,
        )

    # ================================================================
    # STEM 4: Above Proficiency - MC (DOK 2, Easy)
    # "Playground area: 248 <= a and a <= 328.
    #  Complete the pair of inequalities."
    # ================================================================

    def stem4_above_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        ctx = rng.choice(TWO_CONSTRAINT_CONTEXTS)
        var = rng.choice(["a", "x", "t", "n"])

        low = int(gen.whole_number(50, 500))
        high = low + int(gen.whole_number(20, 200))

        setup = ctx["setup"].format(low=low, high=high, var=var)

        # The answer is: a >= low AND a <= high
        correct = f"{var} \u2265 {low} and {var} \u2264 {high}"

        distractors = [
            f"{var} > {low} and {var} < {high}",
            f"{var} \u2264 {low} and {var} \u2265 {high}",
            f"{var} \u2265 {high} and {var} \u2264 {low}",
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
            f"Select the pair of inequalities that represents "
            f"{ctx['var_desc'].format(var=var)}."
        )

        worked = (
            f"The area must be {low} or greater: {var} \u2265 {low}\n"
            f"The area must be {high} or less: {var} \u2264 {high}\n"
            f"Combined: {correct}"
        )

        # Blank number line for students to graph the solution
        nl_render = {
            "type": "number_line",
            "value": float(low),
            "circle_type": "closed",
            "direction": "right",
            "blank": True,
        }

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MC,
                               Difficulty.EASY, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.EASY,
            dok=2,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=correct_letter,
            answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices,
            context_scenario="two-constraint inequality",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4,
            variant_index=variant_idx,
            render_data=nl_render,
        )

    # ================================================================
    # STEM 5: Above Proficiency - MP (DOK 3, Difficult)
    # "Scavenger hunt: first=23.6 min, last=34.8 min.
    #  Part A: Which pair of inequalities? Part B: Explain."
    # ================================================================

    def stem5_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        ctx = rng.choice(TWO_CONSTRAINT_TIME)
        name = pick_name(rng)
        var = rng.choice(["t", "x", "n"])

        # Difficult tier: decimals
        low = gen.decimal_1place(5.0, 50.0)
        high = low + gen.decimal_1place(5.0, 30.0)

        low_rn = RationalNumber(low, "decimal")
        high_rn = RationalNumber(high, "decimal")

        setup = ctx["setup"].format(name=name, low=low_rn.display(), high=high_rn.display())
        question_a = ctx["question_a"].format(var=var)

        correct = f"{var} \u2265 {low_rn.display()} and {var} \u2264 {high_rn.display()}"

        distractors = [
            f"{var} > {low_rn.display()} and {var} < {high_rn.display()}",
            f"{var} \u2264 {low_rn.display()} and {var} \u2265 {high_rn.display()}",
            f"{var} \u2265 {high_rn.display()} and {var} \u2264 {low_rn.display()}",
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
            f"Part B:\nExplain your answer."
        )

        explain = ctx["explain"].format(low=low_rn.display(), high=high_rn.display())

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
            prompt="Explain your answer.",
            prompt_latex="Explain your answer.",
            answer=f"The correct pair is {correct} {explain}.",
            answer_latex=f"The correct pair is ${correct}$ {explain}.",
            item_type=ItemType.ER,
        )

        worked = (
            f"Part A: {correct}\n"
            f"Part B: {var} \u2265 {low_rn.display()} {explain}.\n"
            f"The \u2265 and \u2264 symbols are used because the boundary values are included."
        )

        # Blank number line for students to graph the solution
        nl_render = {
            "type": "number_line",
            "value": float(low),
            "circle_type": "closed",
            "direction": "right",
            "blank": True,
        }

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.DIFFICULT, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT,
            dok=3,
            item_type=ItemType.MP,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"Part A: {correct_letter}\nPart B: {explain}",
            answer_latex=f"Part A: {correct_letter}\nPart B: {explain}",
            worked_solution=worked,
            choices=choices,
            parts=[part_a, part_b],
            context_scenario="two-constraint with explanation",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5,
            variant_index=variant_idx,
            render_data=nl_render,
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_approaching_eq,
            self.stem3_at_mp,
            self.stem4_above_mc,
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
            2: self.stem2_approaching_eq,
            3: self.stem3_at_mp,
            4: self.stem4_above_mc,
            5: self.stem5_above_mp,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-5.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 6.AF.4 question variants...")
    gen = Stem6AF4(seed=42)
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
