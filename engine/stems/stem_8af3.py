"""
Stem generator for 8.AF.3:
  Understand that a function assigns to each x-value exactly one y-value.

Content Limits:
  - Relations as ordered pairs, tables, graphs, equations
  - No function notation
  - Calculator: ALLOWED

5 Stems:
  Stem 1 (Below-MS):         Select all independent variables from ordered pairs (DOK 1, Easy)
  Stem 2 (Approaching-MC):   Which definition describes a function? (DOK 1, Easy)
  Stem 3 (Approaching-MC):   Does this set of ordered pairs represent a function? (DOK 2, Medium)
  Stem 4 (At-MC):            Which table represents a function? (DOK 2, Medium)
  Stem 5 (Above-MP):         Real-world: is this relation a function? Explain (DOK 3, Medium)
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


STANDARD_CODE = "8.AF.3"
VARIANTS_PER_STEM = 20


class Stem8AF3:
    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below - MS (DOK 1, Easy)
    # Select all independent variables from ordered pairs.
    # ================================================================

    def stem1_below_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        # Generate 3-4 ordered pairs with unique x-values
        n_pairs = rng.randint(3, 4)
        x_vals = rng.sample(range(-8, 9), n_pairs)
        y_vals = [rng.randint(-8, 8) for _ in range(n_pairs)]
        pairs = list(zip(x_vals, y_vals))

        pairs_str = ", ".join(f"({x}, {y})" for x, y in pairs)

        # All values that appear in the pairs
        all_vals = sorted(set(x_vals + y_vals))
        # Correct: x-values (independent)
        correct_set = set(x_vals)

        choices = []
        keys = "abcdefgh"
        correct_keys = []
        for i, val in enumerate(all_vals[:7]):
            is_correct = val in correct_set
            choices.append(QuestionChoice(
                key=keys[i], text=str(val), text_latex=str(val),
                is_correct=is_correct,
            ))
            if is_correct:
                correct_keys.append(keys[i])

        stem_text = (
            f"A set of ordered pairs is given.\n\n"
            f"{{{pairs_str}}}\n\n"
            f"Select ALL the numbers that are independent variables (x-values)."
        )

        correct_str = ", ".join(correct_keys)
        worked = f"Independent variables are the x-values (first number in each pair): {', '.join(str(x) for x in sorted(x_vals))}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MS,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MS,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_str, answer_latex=correct_str,
            worked_solution=worked, choices=choices,
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Approaching - MC (DOK 1, Easy)
    # Which definition describes a function?
    # ================================================================

    def stem2_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        correct_defs = [
            "Every x-value has exactly one y-value.",
            "Each input has exactly one output.",
            "Every independent variable has one unique dependent variable.",
        ]
        wrong_defs = [
            "Every y-value has exactly one x-value.",
            "All inputs and outputs must be different numbers.",
            "A function must always be linear.",
            "A set of ordered pairs is always a function.",
            "Every dependent variable has one unique independent variable.",
            "A function must pass through the origin.",
        ]

        correct = rng.choice(correct_defs)
        distractors = rng.sample(wrong_defs, 3)

        stem_text = "Which statement best describes a function?"

        choices = shuffle_choices(correct, correct, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"A function assigns exactly one y-value (output) for each x-value (input). "
            f"The correct answer is: {correct}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct}",
            answer_latex=f"{correct_letter}) {correct}",
            worked_solution=worked, choices=choices,
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching - MC (DOK 2, Medium)
    # Does this set of ordered pairs represent a function?
    # ================================================================

    def stem3_approaching_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        is_function = rng.random() < 0.5
        n_pairs = rng.randint(4, 5)

        if is_function:
            x_vals = rng.sample(range(-6, 7), n_pairs)
            y_vals = [rng.randint(-6, 6) for _ in range(n_pairs)]
        else:
            # Make a non-function: repeat an x-value with different y-values
            x_vals = rng.sample(range(-6, 7), n_pairs - 1)
            repeat_x = rng.choice(x_vals)
            x_vals.append(repeat_x)
            y_vals = [rng.randint(-6, 6) for _ in range(n_pairs)]
            # Ensure the repeated x has different y
            repeat_indices = [i for i, x in enumerate(x_vals) if x == repeat_x]
            while y_vals[repeat_indices[0]] == y_vals[repeat_indices[1]]:
                y_vals[repeat_indices[1]] = rng.randint(-6, 6)

        pairs = list(zip(x_vals, y_vals))
        pairs_str = ", ".join(f"({x}, {y})" for x, y in pairs)

        # Build coordinate grid showing the points
        all_xs = [x for x, y in pairs]
        all_ys = [y for x, y in pairs]
        grid_render_data = {
            "type": "coordinate_grid",
            "x_range": [min(all_xs) - 1, max(all_xs) + 1],
            "y_range": [min(all_ys) - 1, max(all_ys) + 1],
            "points": [{"x": x, "y": y, "label": ""} for x, y in pairs],
            "lines": [],
        }

        func_word = "is" if is_function else "is not"

        if is_function:
            explanation = "Each x-value has exactly one y-value, so this is a function."
        else:
            dup_x = repeat_x
            dup_ys = [y for x, y in pairs if x == dup_x]
            explanation = (f"x = {dup_x} maps to both y = {dup_ys[0]} and y = {dup_ys[1]}. "
                          f"Since one x-value has two different y-values, this is not a function.")

        stem_text = (
            f"A set of ordered pairs is given.\n\n"
            f"{{{pairs_str}}}\n\n"
            f"Part A: Does this set of ordered pairs represent a function?\n\n"
            f"Part B: Explain your reasoning using the definition of a function."
        )

        part_a = QuestionPart(
            label="Part A",
            prompt="Does this set represent a function?",
            prompt_latex="Does this set represent a function?",
            answer=f"This set {func_word} a function.",
            answer_latex=f"This set {func_word} a function.",
            item_type=ItemType.MC,
        )
        part_b = QuestionPart(
            label="Part B",
            prompt="Explain your reasoning.",
            prompt_latex="Explain your reasoning.",
            answer=explanation,
            answer_latex=explanation,
            item_type=ItemType.ER,
        )

        worked = (
            f"Check each x-value for uniqueness.\n"
            + (f"Each x-value appears once, so this IS a function." if is_function
               else f"x = {dup_x} appears with y = {dup_ys[0]} and y = {dup_ys[1]}, so this is NOT a function.")
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MP,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"This set {func_word} a function. {explanation}",
            answer_latex=f"This set {func_word} a function. {explanation}",
            worked_solution=worked, parts=[part_a, part_b],
            render_data=grid_render_data,
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At - MC (DOK 2, Medium)
    # Which table represents a function?
    # ================================================================

    def stem4_at_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        # Generate 4 small tables. One is a function, three are not.
        correct_idx = rng.randint(0, 3)
        tables = []

        for i in range(4):
            n_rows = 4
            if i == correct_idx:
                # Function: unique x-values
                xs = rng.sample(range(1, 10), n_rows)
                ys = [rng.randint(1, 15) for _ in range(n_rows)]
            else:
                # Non-function: at least one repeated x with different y
                xs = rng.sample(range(1, 10), n_rows - 1)
                xs.append(rng.choice(xs))
                ys = [rng.randint(1, 15) for _ in range(n_rows)]
                dup_indices = [j for j in range(n_rows) if xs[j] == xs[-1]]
                while ys[dup_indices[0]] == ys[dup_indices[-1]]:
                    ys[dup_indices[-1]] = rng.randint(1, 15)

            table = list(zip(xs, ys))
            tables.append(table)

        # Build table text for each choice
        keys = "abcd"
        choices = []
        for i, table in enumerate(tables):
            text_lines = "x | y: " + ", ".join(f"({x},{y})" for x, y in table)
            choices.append(QuestionChoice(
                key=keys[i], text=text_lines, text_latex=text_lines,
                is_correct=(i == correct_idx),
                render_data={
                    "type": "data_table",
                    "headers": ["x", "y"],
                    "rows": [[str(x), str(y)] for x, y in table],
                    "orientation": "vertical",
                },
            ))

        correct_letter = keys[correct_idx]

        stem_text = "Which table of values represents a function?"

        worked = (
            f"A function requires each x-value to map to exactly one y-value.\n"
            f"Table {correct_letter}) has all unique x-values, so it represents a function.\n"
            f"The other tables have repeated x-values with different y-values."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MC,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{correct_letter})",
            answer_latex=f"{correct_letter})",
            worked_solution=worked, choices=choices,
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above - MP (DOK 3, Medium)
    # Real-world: is this relation a function? Explain.
    # ================================================================

    def stem5_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        name = pick_name(rng)

        scenarios = [
            {
                "desc": f"{name} records the temperature each hour from noon to 5 PM.",
                "x_label": "Hour", "y_label": "Temperature (F)",
                "is_function": True,
                "reason": "Each hour (x-value) has exactly one temperature reading (y-value).",
            },
            {
                "desc": f"A store records the price and color of each shirt sold.",
                "x_label": "Price ($)", "y_label": "Color",
                "is_function": False,
                "reason": "The same price can correspond to different colors, so one x-value maps to multiple y-values.",
            },
            {
                "desc": f"{name} tracks the number of pages read each day for a week.",
                "x_label": "Day", "y_label": "Pages Read",
                "is_function": True,
                "reason": "Each day (x-value) has exactly one number of pages read (y-value).",
            },
            {
                "desc": f"A classroom records each student's favorite subject.",
                "x_label": "Student", "y_label": "Favorite Subject",
                "is_function": True,
                "reason": "Each student (x-value) has exactly one favorite subject (y-value).",
            },
        ]

        scenario = rng.choice(scenarios)

        # Generate a small table
        n_rows = rng.randint(4, 6)
        if scenario["is_function"]:
            xs = list(range(1, n_rows + 1))
            ys = [rng.randint(1, 30) for _ in range(n_rows)]
        else:
            xs = list(range(1, n_rows + 1))
            ys = [rng.randint(1, 20) for _ in range(n_rows)]
            # Add a duplicate x with different y
            xs.append(rng.choice(xs[:n_rows]))
            ys.append(ys[-1] + rng.randint(1, 5))

        table_render = {
            "type": "data_table",
            "headers": [scenario["x_label"], scenario["y_label"]],
            "rows": [[str(x), str(y)] for x, y in zip(xs, ys)],
            "orientation": "vertical",
        }

        is_func = scenario["is_function"]
        func_word = "is" if is_func else "is not"

        stem_text = (
            f"{scenario['desc']}\n\n"
            f"The table below shows the data.\n\n"
            f"Part A: Is this relation a function?\n\n"
            f"Part B: Explain your reasoning using the definition of a function."
        )

        part_a = QuestionPart(
            label="Part A",
            prompt="Is this relation a function?",
            prompt_latex="Is this relation a function?",
            answer=f"This relation {func_word} a function.",
            answer_latex=f"This relation {func_word} a function.",
            item_type=ItemType.MC,
        )

        part_b = QuestionPart(
            label="Part B",
            prompt="Explain your reasoning.",
            prompt_latex="Explain your reasoning.",
            answer=scenario["reason"],
            answer_latex=scenario["reason"],
            item_type=ItemType.ER,
        )

        worked = f"This relation {func_word} a function. {scenario['reason']}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.MEDIUM, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.MEDIUM, dok=3, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"This relation {func_word} a function. {scenario['reason']}",
            answer_latex=f"This relation {func_word} a function. {scenario['reason']}",
            worked_solution=worked, parts=[part_a, part_b],
            render_data=table_render,
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        for stem_fn in [self.stem1_below_ms, self.stem2_approaching_mc,
                        self.stem3_approaching_mp, self.stem4_at_mc, self.stem5_above_mp]:
            for v in range(variants_per_stem):
                all_questions.append(stem_fn(v))
        return all_questions

    def generate_stem_variants(self, stem_index: int,
                               variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        methods = {1: self.stem1_below_ms, 2: self.stem2_approaching_mc,
                   3: self.stem3_approaching_mp, 4: self.stem4_at_mc, 5: self.stem5_above_mp}
        return [methods[stem_index](v) for v in range(variants_per_stem)]
