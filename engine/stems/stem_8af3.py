"""
Stem generator for 8.AF.3:
  Understand that a function assigns to each x-value exactly one y-value.

Content Limits:
  - Relations as ordered pairs, tables, graphs, equations
  - No function notation
  - Calculator: ALLOWED

5 Stems:
  Stem 1 (Below-MS):         Select all independent (even variants) or dependent
                             (odd variants) variables from ordered pairs (DOK 1, Easy)
  Stem 2 (Approaching-MC):   Which definition describes a function? (DOK 1, Easy)
  Stem 3 (Approaching-MP):   Does this set of ordered pairs represent a function? (DOK 2, Medium)
  Stem 4 (At-MC):            Is this relation a function? Representation rotates by
                             variant_idx % 4: ordered pairs / table / graph / mapping diagram
                             (DOK 2, Medium)
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
from engine.context_pools import pick_name, NAMES
from engine.svg_helpers import mapping_diagram_svg


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
    # Select all independent (even variants) or dependent (odd variants)
    # variables from ordered pairs.
    # ================================================================

    def stem1_below_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        # Alternate the target term so students practice BOTH vocabulary
        # words: even variants ask for independent (x), odd for dependent (y).
        ask_dependent = (variant_idx % 2 == 1)

        # Generate 3-4 ordered pairs. Draw x-values and y-values from
        # disjoint pools so every listed number is unambiguously an x OR a y
        # (the other category's values are the distractors).
        n_pairs = rng.randint(3, 4)
        all_nums = rng.sample(range(-8, 9), n_pairs * 2)
        x_vals = all_nums[:n_pairs]
        y_vals = all_nums[n_pairs:]
        pairs = list(zip(x_vals, y_vals))

        pairs_str = ", ".join(f"({x}, {y})" for x, y in pairs)

        # All values that appear in the pairs
        all_vals = sorted(set(x_vals + y_vals))
        # Correct set: y-values (dependent) or x-values (independent)
        correct_set = set(y_vals) if ask_dependent else set(x_vals)

        choices = []
        keys = "abcdefgh"
        correct_keys = []
        for i, val in enumerate(all_vals[:8]):
            is_correct = val in correct_set
            choices.append(QuestionChoice(
                key=keys[i], text=str(val), text_latex=str(val),
                is_correct=is_correct,
            ))
            if is_correct:
                correct_keys.append(keys[i])

        if ask_dependent:
            prompt = "Select ALL the numbers that are dependent variables (y-values)."
        else:
            prompt = "Select ALL the numbers that are independent variables (x-values)."

        stem_text = (
            f"A set of ordered pairs is given.\n\n"
            f"{{{pairs_str}}}\n\n"
            f"{prompt}"
        )

        correct_str = ", ".join(correct_keys)
        if ask_dependent:
            worked = (f"Dependent variables are the y-values (second number in each pair): "
                      f"{', '.join(str(y) for y in sorted(y_vals))}")
        else:
            worked = (f"Independent variables are the x-values (first number in each pair): "
                      f"{', '.join(str(x) for x in sorted(x_vals))}")

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
    # Is this relation a function? Representation rotates by variant:
    #   variant_idx % 4 == 0 -> set of ordered pairs (text)
    #   variant_idx % 4 == 1 -> table (data_table)
    #   variant_idx % 4 == 2 -> graph (coordinate_grid points)
    #   variant_idx % 4 == 3 -> mapping diagram (SVG)
    # Choices are justification-style; the correct one matches the data.
    # ================================================================

    def stem4_at_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        representation = ("pairs", "table", "graph", "mapping")[variant_idx % 4]
        is_function = rng.random() < 0.5
        n_pairs = rng.randint(4, 5)

        if is_function:
            # Function: unique x-values. Force exactly one REPEATED y-value
            # (two inputs share an output) so the "an output repeats"
            # distractor is concrete — and still wrong.
            xs = rng.sample(range(1, 10), n_pairs)
            y_pool = rng.sample(range(1, 10), n_pairs - 1)
            ys = y_pool + [rng.choice(y_pool)]
            rng.shuffle(ys)
            rep_y = next(v for v in ys if ys.count(v) > 1)
            dup_x = None
        else:
            # Non-function: one x-value repeated with two different y-values.
            # Keep ALL y-values distinct so "an output repeats" stays false.
            base_xs = rng.sample(range(1, 10), n_pairs - 1)
            dup_x = rng.choice(base_xs)
            xs = base_xs + [dup_x]
            ys = rng.sample(range(1, 10), n_pairs)
            rep_y = None

        pairs = list(zip(xs, ys))
        rng.shuffle(pairs)

        # --- Build the representation-specific stem text + figure ---
        pairs_meta = [[x, y] for x, y in pairs]  # ground truth for checkers
        if representation == "pairs":
            pairs_str = ", ".join(f"({x}, {y})" for x, y in pairs)
            stem_text = (
                f"A relation is shown as a set of ordered pairs.\n\n"
                f"{{{pairs_str}}}\n\n"
                f"Is this relation a function?"
            )
            render_data = None
        elif representation == "table":
            stem_text = (
                "A relation is shown in the table below.\n\n[FIGURE]\n\n"
                "Is this relation a function?"
            )
            render_data = {
                "type": "data_table",
                "headers": ["x", "y"],
                "rows": [[str(x), str(y)] for x, y in pairs],
                "orientation": "vertical",
                "relation_pairs": pairs_meta,
            }
        elif representation == "graph":
            stem_text = (
                "A relation is shown as a set of points on the coordinate "
                "grid below.\n\n[FIGURE]\n\n"
                "Is this relation a function?"
            )
            render_data = {
                "type": "coordinate_grid",
                "x_range": [0, 10],
                "y_range": [0, 10],
                "points": [{"x": x, "y": y, "label": ""} for x, y in pairs],
                "lines": [],
                "relation_pairs": pairs_meta,
            }
        else:  # mapping
            unique_inputs = sorted(set(xs))
            unique_outputs = sorted(set(ys))
            arrows = sorted({(unique_inputs.index(x), unique_outputs.index(y))
                             for x, y in pairs})
            svg = mapping_diagram_svg(
                [str(v) for v in unique_inputs],
                [str(v) for v in unique_outputs],
                arrows,
            )
            stem_text = (
                "A relation is shown in the mapping diagram below.\n\n[FIGURE]\n\n"
                "Is this relation a function?"
            )
            render_data = {
                "svg_html": svg,
                "type": "svg_html",
                "relation_pairs": pairs_meta,
            }

        # --- Justification-style choices (exactly one consistent with data) ---
        if is_function:
            correct = "Yes — each input (x-value) is paired with exactly one output (y-value)."
            distractors = [
                f"No — the output {rep_y} is paired with two different inputs.",
                "No — one input has two different outputs.",
                "Yes — every input and output value is different.",
            ]
            worked = (
                "Check whether any input (x-value) repeats. Every input is paired "
                "with exactly one output, so the relation IS a function. "
                f"(The output {rep_y} repeats, but a repeated output does not "
                "break the function rule.)"
            )
        else:
            dup_ys = sorted(y for x, y in pairs if x == dup_x)
            correct = (f"No — the input {dup_x} has two different outputs "
                       f"({dup_ys[0]} and {dup_ys[1]}).")
            distractors = [
                "Yes — each input (x-value) is paired with exactly one output (y-value).",
                "Yes — every input is paired with an output.",
                "No — one output (y-value) is paired with two different inputs.",
            ]
            worked = (
                f"The input {dup_x} is paired with two different outputs "
                f"({dup_ys[0]} and {dup_ys[1]}), so the relation is NOT a function. "
                "A function pairs each input with exactly one output."
            )

        choices = shuffle_choices(correct, correct, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MC,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct}",
            answer_latex=f"{correct_letter}) {correct}",
            worked_solution=worked, choices=choices,
            render_data=render_data,
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

        kind = rng.choice(["temperature", "shirts", "pages", "subjects"])

        # Build a scenario-appropriate table whose data actually matches the
        # is-function verdict and the Part B explanation.
        if kind == "temperature":
            desc = f"{name} records the temperature each hour from noon to 5 PM."
            x_label, y_label = "Hour", "Temperature (F)"
            xs = ["12 PM", "1 PM", "2 PM", "3 PM", "4 PM", "5 PM"]
            ys = [str(rng.randint(58, 92)) for _ in xs]
            is_func = True
            reason = ("Each hour (x-value) has exactly one temperature reading "
                      "(y-value), so the relation is a function.")
        elif kind == "shirts":
            desc = "A store records the price and color of each shirt sold."
            x_label, y_label = "Price ($)", "Color"
            prices = rng.sample([8, 10, 12, 14, 15, 18, 20, 24], 5)
            colors = rng.sample(["Red", "Blue", "Green", "Black",
                                 "White", "Gray", "Yellow", "Purple"], 5)
            is_func = rng.random() < 0.5
            if is_func:
                # Each price appears exactly once -> price maps to one color.
                rows = list(zip(prices, colors))
                reason = ("Each price (x-value) appears exactly once, so every "
                          "price is paired with exactly one color (y-value). "
                          "The relation is a function.")
            else:
                # Duplicate one price with a DIFFERENT color (colors are all
                # distinct, so the two rows sharing a price differ in color).
                base_prices = prices[:4]
                dup_price = rng.choice(base_prices)
                rows = list(zip(base_prices + [dup_price], colors))
                rng.shuffle(rows)
                dup_colors = [c for p, c in rows if p == dup_price]
                reason = (f"The price ${dup_price} appears twice with two "
                          f"different colors ({dup_colors[0]} and {dup_colors[1]}). "
                          "One x-value (price) is paired with two different "
                          "y-values (colors), so the relation is not a function.")
            xs = [str(p) for p, c in rows]
            ys = [c for p, c in rows]
        elif kind == "pages":
            desc = f"{name} tracks the number of pages read each day for a week."
            x_label, y_label = "Day", "Pages Read"
            xs = [str(day) for day in range(1, 8)]
            ys = [str(rng.randint(5, 40)) for _ in range(7)]
            is_func = True
            reason = ("Each day (x-value) has exactly one number of pages read "
                      "(y-value), so the relation is a function.")
        else:  # subjects
            desc = "A classroom records each student's favorite subject."
            x_label, y_label = "Student", "Favorite Subject"
            xs = rng.sample(NAMES["male"] + NAMES["female"], 5)
            subjects = ["Math", "Science", "Reading", "History", "Art", "Music"]
            ys = [rng.choice(subjects) for _ in xs]
            is_func = True
            reason = ("Each student (x-value) has exactly one favorite subject "
                      "(y-value), so the relation is a function. Two students "
                      "may share a subject — repeated y-values are allowed.")

        table_render = {
            "type": "data_table",
            "headers": [x_label, y_label],
            "rows": [[x, y] for x, y in zip(xs, ys)],
            "orientation": "vertical",
        }

        func_word = "is" if is_func else "is not"

        stem_text = (
            f"{desc}\n\n"
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
            answer=reason,
            answer_latex=reason,
            item_type=ItemType.ER,
        )

        worked = f"This relation {func_word} a function. {reason}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.MEDIUM, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.MEDIUM, dok=3, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"This relation {func_word} a function. {reason}",
            answer_latex=f"This relation {func_word} a function. {reason}",
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
