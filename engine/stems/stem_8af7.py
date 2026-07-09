"""
Stem generator for 8.AF.7:
  Compare properties of two linear functions given in different forms
  (table, equation, verbal description, graph).

Content Limits:
  - Include only linear functions
  - Exactly two functions (not more)
  - Properties: rate of change, starting point (y-intercept), values at specific inputs
  - Only continuous graphs; discrete graphs may not be used
  - Calculator: ALLOWED

5 Stems:
  Stem 1 (Below-MC):        Match table to equation (DOK 2, Medium)
  Stem 2 (Approaching-MC):  Compare two equations: which statement is true? (DOK 2, Easy)
  Stem 3 (At-MC):           Compare equation vs table: which statement is true? (DOK 3, Medium)
  Stem 4 (At-NR):           Difference in rates of change between two tables (DOK 2, Difficult)
  Stem 5 (Above-ER):        Write function with constraints relative to given one (DOK 3, Difficult)
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
from engine.distractor_engine import shuffle_choices
from engine.context_pools import pick_name


STANDARD_CODE = "8.AF.7"
VARIANTS_PER_STEM = 20


def _fmt(val: Fraction) -> str:
    if val.denominator == 1:
        return str(int(val))
    av = abs(val)
    if val < 0:
        return f"-{av.numerator}/{av.denominator}"
    return f"{val.numerator}/{val.denominator}"


def _fmt_eq(m: Fraction, b: Fraction) -> str:
    parts = ["y = "]
    if m == 1:
        parts.append("x")
    elif m == -1:
        parts.append("-x")
    elif m.denominator == 1:
        parts.append(f"{int(m)}x")
    else:
        parts.append(f"({m.numerator}/{m.denominator})x")
    if b > 0:
        parts.append(f" + {_fmt(b)}")
    elif b < 0:
        parts.append(f" - {_fmt(abs(b))}")
    return "".join(parts)


def _make_table(m: Fraction, b: Fraction, xs: list[Fraction]):
    """Generate a table of (x, y) from y = mx + b."""
    return [(x, m * x + b) for x in xs]


class Stem8AF7:
    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below - MC (DOK 2, Medium)
    # Which table represents the equation y = mx + b?
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        m = Fraction(rng.randint(1, 5)) * rng.choice([1, -1])
        b = Fraction(rng.randint(1, 8)) * rng.choice([1, -1])
        eq_str = _fmt_eq(m, b)

        xs = [Fraction(i) for i in range(5)]

        # Correct table
        correct_rows = _make_table(m, b, xs)

        # Distractors: wrong m, wrong b, swapped m/b
        d1_rows = _make_table(m + 1, b, xs)
        d2_rows = _make_table(m, b + Fraction(rng.randint(2, 5)), xs)
        d3_rows = _make_table(b, m, xs) if b != m else _make_table(-m, b, xs)

        all_tables = [
            (correct_rows, True),
            (d1_rows, False),
            (d2_rows, False),
            (d3_rows, False),
        ]

        keys = "abcd"
        choices = []
        correct_key = None
        order = list(range(4))
        rng.shuffle(order)

        for new_i, old_i in enumerate(order):
            rows, is_correct = all_tables[old_i]
            text = "x | y: " + ", ".join(f"({_fmt(x)},{_fmt(y)})" for x, y in rows)
            choices.append(QuestionChoice(
                key=keys[new_i], text=text, text_latex=text,
                is_correct=is_correct,
                render_data={
                    "type": "data_table",
                    "headers": ["x", "y"],
                    "rows": [[_fmt(x), _fmt(y)] for x, y in rows],
                    "orientation": "vertical",
                },
            ))
            if is_correct:
                correct_key = keys[new_i]

        stem_text = f"Which table of values represents the equation {eq_str}?"

        worked = (
            f"Substitute x values into {eq_str} and check.\n"
            f"When x = 0: y = {_fmt(m * Fraction(0) + b)}\n"
            f"When x = 1: y = {_fmt(m * Fraction(1) + b)}\n"
            f"Table {correct_key}) matches."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.MEDIUM, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{correct_key})",
            answer_latex=f"{correct_key})",
            worked_solution=worked, choices=choices,
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Approaching - MC (DOK 2, Easy)
    # Compare two equations: which statement is true?
    # ================================================================

    def stem2_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        m1 = Fraction(rng.randint(1, 6))
        b1 = Fraction(rng.randint(1, 10))
        m2 = Fraction(rng.randint(1, 6))
        b2 = Fraction(rng.randint(1, 10))
        while m1 == m2 and b1 == b2:
            m2 = Fraction(rng.randint(1, 6))
            b2 = Fraction(rng.randint(1, 10))

        # Build correct and incorrect statements
        statements = []
        if m1 > m2:
            statements.append((f"Function A has a greater rate of change than Function B.", True))
            statements.append((f"Function B has a greater rate of change than Function A.", False))
        elif m1 < m2:
            statements.append((f"Function B has a greater rate of change than Function A.", True))
            statements.append((f"Function A has a greater rate of change than Function B.", False))
        else:
            statements.append((f"Both functions have the same rate of change.", True))
            statements.append((f"Function A has a greater rate of change than Function B.", False))

        if b1 > b2:
            statements.append((f"Function A has a greater y-intercept than Function B.", True))
            statements.append((f"Function B has a greater y-intercept than Function A.", False))
        elif b1 < b2:
            statements.append((f"Function B has a greater y-intercept than Function A.", True))
            statements.append((f"Function A has a greater y-intercept than Function B.", False))
        else:
            statements.append((f"Both functions have the same y-intercept.", True))
            statements.append((f"Function A has a greater y-intercept.", False))

        # Pick one true, three false
        true_stmts = [s for s, correct in statements if correct]
        false_stmts = [s for s, correct in statements if not correct]

        # Add more false if needed
        false_stmts.append("Both functions have the same rate of change and y-intercept." if m1 != m2 or b1 != b2 else "The functions are completely different.")

        correct = rng.choice(true_stmts)
        distractors = rng.sample(false_stmts, min(3, len(false_stmts)))
        while len(distractors) < 3:
            distractors.append("The functions are identical.")
        distractors = distractors[:3]

        # Build coordinate grid showing both lines
        x_lo, x_hi = -2, 8
        grid_render_data = {
            "type": "coordinate_grid",
            "x_range": [x_lo, x_hi],
            "y_range": [min(int(b1), int(b2)) - 2, max(int(m1 * x_hi + b1), int(m2 * x_hi + b2)) + 2],
            "points": [],
            "lines": [
                {"x1": x_lo, "y1": float(m1 * x_lo + b1), "x2": x_hi, "y2": float(m1 * x_hi + b1), "label": "A"},
                {"x1": x_lo, "y1": float(m2 * x_lo + b2), "x2": x_hi, "y2": float(m2 * x_hi + b2), "label": "B"},
            ],
        }

        stem_text = (
            f"Function A and Function B are shown in the graph below.\n\n"
            f"Which statement is true?"
        )

        choices = shuffle_choices(correct, correct, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"Function A: slope = {_fmt(m1)}, y-intercept = {_fmt(b1)}\n"
            f"Function B: slope = {_fmt(m2)}, y-intercept = {_fmt(b2)}\n"
            f"{correct}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct}",
            answer_latex=f"{correct_letter}) {correct}",
            worked_solution=worked, choices=choices,
            render_data=grid_render_data,
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: At - MC (DOK 3, Medium)
    # Compare equation vs table: which statement is true?
    # ================================================================

    def stem3_at_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)
        name1 = pick_name(rng)
        name2 = pick_name(rng)
        while name2 == name1:
            name2 = pick_name(rng)

        # Function A as equation
        m1 = Fraction(rng.randint(2, 8))
        b1 = Fraction(rng.randint(10, 50))
        eq_str = _fmt_eq(m1, b1)

        # Function B as table
        m2 = Fraction(rng.randint(2, 8))
        b2 = Fraction(rng.randint(10, 50))
        xs = [Fraction(i) for i in range(5)]
        table_rows = _make_table(m2, b2, xs)

        table_render = {
            "type": "data_table",
            "headers": ["x", "y"],
            "rows": [[_fmt(x), _fmt(y)] for x, y in table_rows],
            "orientation": "vertical",
        }

        # Build statements
        true_parts = []
        if m1 > m2:
            true_parts.append(f"{name1}'s function has a greater rate of change")
        elif m1 < m2:
            true_parts.append(f"{name2}'s function has a greater rate of change")
        else:
            true_parts.append(f"Both functions have the same rate of change")

        if b1 > b2:
            true_parts.append(f"{name1}'s function has a greater starting value")
        elif b1 < b2:
            true_parts.append(f"{name2}'s function has a greater starting value")
        else:
            true_parts.append(f"Both functions have the same starting value")

        correct = f"{true_parts[0]} and {true_parts[1]}."

        # Distractors: flip the comparisons
        false_parts_m = (f"{name2}'s function has a greater rate of change"
                         if m1 >= m2
                         else f"{name1}'s function has a greater rate of change")
        false_parts_b = (f"{name2}'s function has a greater starting value"
                         if b1 >= b2
                         else f"{name1}'s function has a greater starting value")

        distractors = [
            f"{false_parts_m} and {true_parts[1]}.",
            f"{true_parts[0]} and {false_parts_b}.",
            f"{false_parts_m} and {false_parts_b}.",
        ]
        distractors = [d for d in distractors if d != correct][:3]
        while len(distractors) < 3:
            distractors.append("Both functions are identical.")

        stem_text = (
            f"{name1}'s function: {eq_str}\n\n"
            f"{name2}'s function is shown in the table below.\n\n"
            f"Which statement is true?"
        )

        choices = shuffle_choices(correct, correct, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"{name1}'s function: slope = {_fmt(m1)}, y-intercept = {_fmt(b1)}\n"
            f"{name2}'s function (from table): slope = ({_fmt(table_rows[1][1])} - {_fmt(table_rows[0][1])}) / "
            f"({_fmt(table_rows[1][0])} - {_fmt(table_rows[0][0])}) = {_fmt(m2)}, y-intercept = {_fmt(b2)}\n"
            f"{correct}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MC,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=3, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct}",
            answer_latex=f"{correct_letter}) {correct}",
            worked_solution=worked, choices=choices,
            render_data=table_render,
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At - NR (DOK 2, Difficult)
    # Find the difference in rates of change between two tables.
    # ================================================================

    def stem4_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        # Two tables with different slopes (possibly rational)
        num1 = rng.randint(1, 5)
        den1 = rng.choice([1, 2, 3])
        m1 = Fraction(num1, den1)
        b1 = Fraction(rng.randint(0, 10))

        num2 = rng.randint(1, 5)
        den2 = rng.choice([1, 2, 3])
        m2 = Fraction(num2, den2)
        b2 = Fraction(rng.randint(0, 10))
        while m1 == m2:
            num2 = rng.randint(1, 5)
            m2 = Fraction(num2, den2)

        xs1 = sorted(Fraction(v) for v in rng.sample(range(0, 8), 4))
        xs2 = sorted(Fraction(v) for v in rng.sample(range(0, 8), 4))

        table1 = _make_table(m1, b1, xs1)
        table2 = _make_table(m2, b2, xs2)

        diff = abs(m1 - m2)
        correct = _fmt(diff)

        render1 = {
            "type": "data_table",
            "headers": ["x", "y"],
            "rows": [[_fmt(x), _fmt(y)] for x, y in table1],
            "orientation": "vertical",
        }
        render2 = {
            "type": "data_table",
            "headers": ["x", "y"],
            "rows": [[_fmt(x), _fmt(y)] for x, y in table2],
            "orientation": "vertical",
        }

        stem_text = (
            f"Function J is shown in Table 1.\n"
            f"Function K is shown in Table 2.\n\n"
            f"Enter the absolute difference between the rates of change of Function J and Function K."
        )

        # For NR, no choices - just the answer
        worked = (
            f"Function J: rate of change = {_fmt(m1)}\n"
            f"Function K: rate of change = {_fmt(m2)}\n"
            f"Difference = |{_fmt(m1)} - {_fmt(m2)}| = {correct}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.DIFFICULT, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct, answer_latex=correct,
            worked_solution=worked,
            render_data={"tables": [render1, render2]},
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above - MP (DOK 3, Difficult)
    # Write a function with constraints relative to a given function.
    # ================================================================

    def stem5_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)
        name = pick_name(rng)

        # Given function as table
        m_given = Fraction(rng.randint(2, 6))
        b_given = Fraction(rng.randint(-5, 10))
        xs = [Fraction(i) for i in range(5)]
        given_table = _make_table(m_given, b_given, xs)

        table_render = {
            "type": "data_table",
            "headers": ["x", "y"],
            "rows": [[_fmt(x), _fmt(y)] for x, y in given_table],
            "orientation": "vertical",
        }

        # Constraint: same rate of change + greater y-intercept OR greater rate + same intercept
        constraint_type = rng.choice(["same_slope_greater_b", "greater_slope_same_b"])

        if constraint_type == "same_slope_greater_b":
            required_m = m_given
            required_b_desc = f"greater than {_fmt(b_given)}"
            example_b = b_given + rng.randint(1, 5)
            constraint_text = f"same rate of change as Function G and a greater y-intercept"
            part_a_answer = f"The rate of change of Function G is {_fmt(m_given)} and its y-intercept is {_fmt(b_given)}."
            part_b_answer = f"Any equation y = {_fmt(required_m)}x + b where b > {_fmt(b_given)}. Example: {_fmt_eq(required_m, example_b)}"
        else:
            required_b = b_given
            required_m_desc = f"greater than {_fmt(m_given)}"
            example_m = m_given + rng.randint(1, 3)
            constraint_text = f"a greater rate of change than Function G and the same y-intercept"
            part_a_answer = f"The rate of change of Function G is {_fmt(m_given)} and its y-intercept is {_fmt(b_given)}."
            part_b_answer = f"Any equation y = mx + {_fmt(required_b)} where m > {_fmt(m_given)}. Example: {_fmt_eq(example_m, required_b)}"

        stem_text = (
            f"Function G is shown in the table below.\n\n"
            f"Part A: What is the rate of change and y-intercept of Function G?\n\n"
            f"Part B: Write an equation for a function that has {constraint_text}."
        )

        part_a = QuestionPart(
            label="Part A",
            prompt="What is the rate of change and y-intercept?",
            prompt_latex="What is the rate of change and y-intercept?",
            answer=part_a_answer, answer_latex=part_a_answer,
            item_type=ItemType.NR,
        )
        part_b = QuestionPart(
            label="Part B",
            prompt=f"Write an equation with {constraint_text}.",
            prompt_latex=f"Write an equation with {constraint_text}.",
            answer=part_b_answer, answer_latex=part_b_answer,
            item_type=ItemType.EQ,
        )

        worked = f"Part A: {part_a_answer}\nPart B: {part_b_answer}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.DIFFICULT, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"A: {part_a_answer}\nB: {part_b_answer}",
            answer_latex=f"A: {part_a_answer}\nB: {part_b_answer}",
            worked_solution=worked, parts=[part_a, part_b],
            render_data=table_render,
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        for stem_fn in [self.stem1_below_mc, self.stem2_approaching_mc,
                        self.stem3_at_mc, self.stem4_at_nr, self.stem5_above_mp]:
            for v in range(variants_per_stem):
                all_questions.append(stem_fn(v))
        return all_questions

    def generate_stem_variants(self, stem_index: int,
                               variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        methods = {1: self.stem1_below_mc, 2: self.stem2_approaching_mc,
                   3: self.stem3_at_mc, 4: self.stem4_at_nr, 5: self.stem5_above_mp}
        return [methods[stem_index](v) for v in range(variants_per_stem)]
