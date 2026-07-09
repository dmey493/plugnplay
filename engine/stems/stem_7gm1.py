"""
Stem generator for 7.GM.1:
  Solve real-world and other mathematical problems involving scale drawings
  of geometric figures, including computing actual lengths and areas from a
  scale drawing. Create a scale drawing by using proportional reasoning.

Content Limits:
  - Limit to two-dimensional polygons only
  - Unit conversions should be within the same system
  - Most items should have a real-world context
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: Whole-number lengths and scale factor
  Medium: Fractions or decimals for length OR scale factor, but not both
  Difficult: Fractions or decimals for both lengths and scale factor

8 Stems from the Item Spec:
  Stem 1 (Below-NR):       Identify scale factor from Figure A to Figure B (DOK 2, Easy)
  Stem 2 (Approaching-NR): Use scale to find actual length - whole numbers (DOK 2, Easy)
  Stem 3 (Approaching-NR): Use scale to find actual length - decimals (DOK 2, Difficult)
  Stem 4 (Approaching-NR): Two figures with scale, find missing side x (DOK 2, Easy)
  Stem 5 (At-NR):          Compute actual area from scale drawing (DOK 2, Easy)
  Stem 6 (At-MS):          Table with missing scale/actual measurements (DOK 2, Medium)
  Stem 7 (Above-MP):       Multi-part: blueprint scale A -> actual -> new scale B (DOK 3, Medium)
  Stem 8 (Above-MP):       Multi-part: select best scale for paper constraints (DOK 3, Easy)
"""

import random
import math
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
from engine.svg_helpers import scale_pair_svg, rectangle_svg


STANDARD_CODE = "7.GM.1"
VARIANTS_PER_STEM = 20


# ============================================================
# HELPERS
# ============================================================

SCALE_ITEMS = [
    ("boat", "ft"),
    ("building", "ft"),
    ("park", "yd"),
    ("room", "ft"),
    ("car", "ft"),
    ("playground", "m"),
    ("bridge", "ft"),
    ("garden", "m"),
]

# Furniture items for the table question (stem 6)
FURNITURE_ITEMS = [
    ("couch length", "couch width", "coffee table length"),
    ("desk width", "desk depth", "bookshelf height"),
    ("bed length", "bed width", "dresser width"),
    ("table length", "table width", "chair height"),
    ("sofa length", "sofa depth", "end table width"),
]

# Objects with dimensions for the "best scale" question (stem 8)
LARGE_OBJECTS = [
    ("house", 84, 36, "ft"),
    ("warehouse", 120, 60, "ft"),
    ("soccer field", 100, 50, "m"),
    ("parking lot", 90, 45, "ft"),
    ("gymnasium", 80, 40, "ft"),
    ("swimming pool", 50, 25, "m"),
    ("tennis court", 78, 36, "ft"),
    ("basketball court", 94, 50, "ft"),
]


def _fmt_dec(val):
    """Format a float to clean decimal string (strip trailing zeros)."""
    if val == int(val):
        return str(int(val))
    return f"{val:.2f}".rstrip('0').rstrip('.')


class Stem7GM1:
    """Generates ~20 variants for each of 8 stems from the 7.GM.1 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - NR (DOK 2, Easy)
    # "Figure B is a scale image of Figure A, as shown.
    #  Enter the scale factor applied to Figure A to produce Figure B."
    # ================================================================

    def stem1_below_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        shape_type = rng.choice(["rectangle", "triangle"])
        scale_factor = rng.choice([2, 3, 4, 5])

        if shape_type == "rectangle":
            a_w = rng.randint(2, 6)
            a_h = rng.randint(2, 6)
            while a_w == a_h:
                a_h = rng.randint(2, 6)
            b_w = a_w * scale_factor
            b_h = a_h * scale_factor

            svg = scale_pair_svg(
                [a_w, a_h], [b_w, b_h],
                shape_type="rectangle",
                label_a="Figure A", label_b="Figure B"
            )
        else:
            a_w = rng.randint(3, 8)
            a_h = rng.randint(3, 8)
            b_w = a_w * scale_factor
            b_h = a_h * scale_factor

            svg = scale_pair_svg(
                [a_w, a_h], [b_w, b_h],
                shape_type="triangle",
                label_a="Figure A", label_b="Figure B"
            )

        stem_text = (
            f"Figure B is a scale image of Figure A, as shown.\n\n"
            f"[FIGURE]\n\n"
            f"Enter the scale factor applied to Figure A to produce Figure B."
        )

        answer = str(scale_factor)
        solution = (
            f"Scale factor = corresponding side of B / corresponding side of A\n"
            f"Scale factor = {b_w} / {a_w} = {scale_factor}"
        )

        render = {"svg_html": svg, "type": "svg_html"}

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.NR,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=solution,
            context_scenario="scale factor identification",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx,
            render_data=render,
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - NR (DOK 2, Easy)
    # "A student drew a picture of a boat. She used the scale shown.
    #  1 inch : 6 feet. Her picture is 7 inches long.
    #  What is the length of the actual boat? ___ feet"
    # ================================================================

    def stem2_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        item, unit = rng.choice(SCALE_ITEMS)
        name = pick_name(rng)

        # Scale: 1 in : N actual_units (whole numbers only - Easy)
        scale_ratio = rng.randint(3, 12)
        drawing_length = rng.randint(2, 10)
        actual_length = drawing_length * scale_ratio

        stem_text = (
            f"{name} drew a picture of a {item}. "
            f"The scale used is 1 inch : {scale_ratio} {unit}.\n"
            f"The picture is {drawing_length} inches long.\n\n"
            f"What is the length of the actual {item} in {unit}?"
        )

        answer = str(actual_length)
        solution = (
            f"Scale: 1 in. = {scale_ratio} {unit}\n"
            f"Actual = {drawing_length} x {scale_ratio} = {actual_length} {unit}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=solution,
            context_scenario=f"scale drawing {item}",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx,
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - NR (DOK 2, Difficult)
    # Same format as stem 2 but with decimal scale and drawing length.
    # "1.5 inch : 6.5 feet. Her picture is 7.25 inches long."
    # ================================================================

    def stem3_approaching_nr_difficult(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        item, unit = rng.choice(SCALE_ITEMS)
        name = pick_name(rng)

        # Generate decimal scale that produces a clean result
        # scale_draw : scale_actual — both decimals
        # actual = drawing_length * (scale_actual / scale_draw)
        # To get clean 2-decimal results, pick rate = scale_actual / scale_draw
        # as a simple decimal, then pick drawing length accordingly.
        rates = [2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]
        rate = rng.choice(rates)

        # Scale draw component (decimal)
        scale_draw_options = [0.5, 1.0, 1.5, 2.0, 2.5]
        scale_draw = rng.choice(scale_draw_options)
        scale_actual = scale_draw * rate

        # Drawing length (decimal)
        draw_len_options = [2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5]
        drawing_length = rng.choice(draw_len_options)

        actual_length = drawing_length * rate

        # Format cleanly
        scale_draw_str = _fmt_dec(scale_draw)
        scale_actual_str = _fmt_dec(scale_actual)
        draw_str = _fmt_dec(drawing_length)
        actual_str = _fmt_dec(actual_length)

        inch_word = "inch" if scale_draw == 1 else "inches"
        stem_text = (
            f"{name} drew a picture of a {item}. "
            f"The scale used is {scale_draw_str} {inch_word} : {scale_actual_str} {unit}.\n"
            f"The picture is {draw_str} inches long.\n\n"
            f"What is the length of the actual {item} in {unit}?"
        )

        answer = actual_str
        solution = (
            f"Scale: {scale_draw_str} in. = {scale_actual_str} {unit}\n"
            f"Rate = {scale_actual_str} / {scale_draw_str} = {_fmt_dec(rate)} {unit} per inch\n"
            f"Actual = {draw_str} x {_fmt_dec(rate)} = {actual_str} {unit}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.DIFFICULT, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=solution,
            context_scenario=f"decimal scale {item}",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx,
        )

    # ================================================================
    # STEM 4: Approaching Proficiency - NR (DOK 2, Easy)
    # "Two figures are given. Figure B is a scale image of Figure A.
    #  The scale that maps Figure A onto Figure B is 1:2.
    #  Enter the value of x on Figure B. ___ cm"
    # ================================================================

    def stem4_approaching_nr_findx(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        scale_factor = rng.choice([2, 3, 4, 5])
        shape_type = rng.choice(["rectangle", "triangle"])

        a_w = rng.randint(2, 8)
        a_h = rng.randint(2, 8)
        while a_w == a_h:
            a_h = rng.randint(2, 8)

        b_w = a_w * scale_factor
        b_h = a_h * scale_factor

        # Hide one dimension on Figure B as "x"
        hide_width = rng.choice([True, False])

        if hide_width:
            labels_b = ["x", str(b_h)]
            answer = str(b_w)
            hidden_side_a = a_w
        else:
            labels_b = [str(b_w), "x"]
            answer = str(b_h)
            hidden_side_a = a_h

        unit = rng.choice(["cm", "in."])

        svg = scale_pair_svg(
            [a_w, a_h], [b_w, b_h],
            shape_type=shape_type,
            label_a="Figure A", label_b="Figure B",
            unit_a=unit, unit_b=unit,
            dim_labels_b=labels_b,
        )

        stem_text = (
            f"Two figures are given. Figure B is a scale image of Figure A.\n"
            f"The scale that maps Figure A onto Figure B is 1:{scale_factor}.\n\n"
            f"[FIGURE]\n\n"
            f"Enter the value of x on Figure B."
        )

        solution = (
            f"Scale factor = {scale_factor}\n"
            f"The corresponding side on Figure A is {hidden_side_a} {unit}.\n"
            f"x = {hidden_side_a} x {scale_factor} = {answer} {unit}"
        )

        render = {"svg_html": svg, "type": "svg_html"}

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.EASY, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=solution,
            context_scenario="find missing side from scale",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx,
            render_data=render,
        )

    # ================================================================
    # STEM 5: At Proficiency - NR (DOK 2, Easy)
    # "A scale drawing of a room is given. The scale that maps the
    #  drawing to the actual room is 1 in. to 7 ft. Using the scale
    #  given, enter the actual area of the room. ___ square feet"
    # ================================================================

    def stem5_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        name = pick_name(rng)

        # Scale drawing dimensions (whole numbers - Easy difficulty)
        scale_ratio = rng.randint(3, 10)
        draw_w = rng.randint(3, 10)
        draw_h = rng.randint(3, 10)
        while draw_w == draw_h:
            draw_h = rng.randint(3, 10)

        actual_w = draw_w * scale_ratio
        actual_h = draw_h * scale_ratio
        actual_area = actual_w * actual_h

        context = rng.choice(["room", "park", "garden", "patio"])
        unit = "ft" if context in ["room", "patio"] else "m"

        # Show a single scale drawing rectangle with dimensions
        svg = rectangle_svg(
            draw_w, draw_h,
            label_w=f"{draw_w} in.", label_h=f"{draw_h} in.",
            title="Scale Drawing",
        )

        stem_text = (
            f"A scale drawing of a {context} is shown. "
            f"The scale that maps the drawing to the actual {context} is "
            f"1 in. to {scale_ratio} {unit}.\n\n"
            f"[FIGURE]\n\n"
            f"Using the scale given, enter the actual area of the {context} "
            f"in square {unit}."
        )

        answer = str(actual_area)
        solution = (
            f"Actual width = {draw_w} x {scale_ratio} = {actual_w} {unit}\n"
            f"Actual height = {draw_h} x {scale_ratio} = {actual_h} {unit}\n"
            f"Actual area = {actual_w} x {actual_h} = {actual_area} sq {unit}"
        )

        render = {"svg_html": svg, "type": "svg_html"}

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.EASY, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=solution,
            context_scenario=f"scale area {context}",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx,
            render_data=render,
        )

    # ================================================================
    # STEM 6: At Proficiency - MS (DOK 2, Medium)
    # "The table shows some of the scale drawing measurements and
    #  actual dimensions of a couch and a chair.
    #  Choose the TWO measurements that are missing from the table."
    #
    # Scale uses decimals (Medium difficulty: decimals for length
    # but not for scale factor, or vice versa).
    # ================================================================

    def stem6_at_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)

        name = pick_name(rng)

        # Pick furniture group
        items = list(rng.choice(FURNITURE_ITEMS))

        # Scale factor (integer for Medium - only one of scale/length is decimal)
        scale_factor = rng.randint(5, 15)

        # Generate 3 furniture items with drawing and actual measurements
        # Make some measurements decimal (Medium difficulty)
        draw_dims = []
        actual_dims = []
        for i in range(3):
            # Some drawing dimensions are decimal, some whole
            if i == 0:
                d = rng.choice([1.5, 2.0, 2.5, 3.0, 3.5, 4.0])
            elif i == 1:
                d = rng.choice([1.0, 1.2, 1.4, 1.5, 1.8, 2.0, 2.5])
            else:
                d = rng.choice([2.0, 2.5, 3.0, 3.5, 4.0])
            a = d * scale_factor
            draw_dims.append(d)
            actual_dims.append(a)

        # Choose which two cells to hide (one drawing, one actual, on different rows)
        # Row 0: hide actual
        # Row 1: hide drawing
        hide_actual_row = 0
        hide_draw_row = 1
        # Row 2: both shown (anchors the scale factor)

        actual_hidden_val = actual_dims[hide_actual_row]
        draw_hidden_val = draw_dims[hide_draw_row]

        # Build table rows with "?" for hidden values
        rows = []
        for i in range(3):
            d_str = _fmt_dec(draw_dims[i]) + " in." if i != hide_draw_row else "?"
            a_str = _fmt_dec(actual_dims[i]) + " in." if i != hide_actual_row else "?"
            rows.append([items[i].capitalize(), d_str, a_str])

        # Build answer choices (2 correct, 4 wrong)
        correct_actual = f"The actual measurement of the {items[hide_actual_row]} is {_fmt_dec(actual_hidden_val)} inches"
        correct_draw = f"The scale drawing measurement of the {items[hide_draw_row]} is {_fmt_dec(draw_hidden_val)} inches"

        # Wrong options: plausible but incorrect values
        wrong_actual_1 = f"The actual measurement of the {items[hide_actual_row]} is {_fmt_dec(actual_hidden_val + scale_factor)} inches"
        wrong_actual_2 = f"The actual measurement of the {items[hide_actual_row]} is {_fmt_dec(draw_dims[hide_actual_row])} inches"
        wrong_draw_1 = f"The scale drawing measurement of the {items[hide_draw_row]} is {_fmt_dec(draw_hidden_val + 0.5)} inches"
        wrong_draw_2 = f"The scale drawing measurement of the {items[hide_draw_row]} is {_fmt_dec(actual_dims[hide_draw_row] / (scale_factor + 1))} inches"

        all_options = [
            (correct_actual, True),
            (wrong_actual_1, False),
            (wrong_actual_2, False),
            (correct_draw, True),
            (wrong_draw_1, False),
            (wrong_draw_2, False),
        ]
        rng.shuffle(all_options)

        choices = []
        correct_keys = []
        for i, (text, is_correct) in enumerate(all_options):
            key = chr(ord('a') + i)
            choices.append(QuestionChoice(
                key=key, text=text, text_latex=text,
                is_correct=is_correct,
            ))
            if is_correct:
                correct_keys.append(key)

        answer_str = ", ".join(correct_keys)

        stem_text = (
            f"A scale drawing uses a scale factor of 1 inch = {scale_factor} inches "
            f"(actual). The table shows some of the scale drawing measurements "
            f"and actual dimensions of furniture in {name}'s room.\n\n"
            f"[FIGURE]\n\n"
            f"Choose the TWO measurements that correctly fill in the missing "
            f"values in the table."
        )

        render = {
            "type": "data_table",
            "headers": ["Item", "Scale Drawing", "Actual"],
            "rows": rows,
        }

        solution = (
            f"Scale factor: 1 in. (drawing) = {scale_factor} in. (actual)\n"
            f"Missing actual: {_fmt_dec(draw_dims[hide_actual_row])} x {scale_factor} "
            f"= {_fmt_dec(actual_hidden_val)} in.\n"
            f"Missing drawing: {_fmt_dec(actual_dims[hide_draw_row])} / {scale_factor} "
            f"= {_fmt_dec(draw_hidden_val)} in."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MS,
                               Difficulty.MEDIUM, 6, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MS,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_str, answer_latex=answer_str,
            worked_solution=solution,
            choices=choices,
            context_scenario="furniture scale table",
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6, variant_index=variant_idx,
            render_data=render,
        )

    # ================================================================
    # STEM 7: Above Proficiency - MP (DOK 3, Medium)
    # "The original blueprint for an apartment has a scale of
    #  2 inches = 15 feet.
    #  Part A: What is the actual measurement of the width?
    #  Part B: You want to create a new scale drawing with a scale
    #          of 1 inch = 2.5 feet. What is the scale drawing width
    #          on the new blueprint?"
    # ================================================================

    def stem7_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(7, variant_idx)

        name = pick_name(rng)
        context = rng.choice(["apartment", "classroom", "office", "warehouse"])
        article = "an" if context[0] in "aeiou" else "a"
        unit = "ft"

        # Scale A: D_a inches = A_a feet (may use non-1:N format)
        d_a = rng.choice([1, 2, 3])
        a_a = rng.choice([5, 8, 10, 12, 15])

        # Drawing A width (in inches)
        draw_a_w = rng.randint(2, 8)
        actual_w = draw_a_w * a_a // d_a

        # Ensure clean division
        attempts = 0
        while (draw_a_w * a_a) % d_a != 0 and attempts < 20:
            draw_a_w = rng.randint(2, 8)
            attempts += 1
        actual_w = draw_a_w * a_a // d_a

        # Scale B: 1 inch = B_b feet (decimal allowed - Medium)
        b_b_options = [2, 2.5, 3, 4, 5, 6]
        b_b = rng.choice(b_b_options)

        # New drawing width
        draw_b_w = actual_w / b_b

        # Format
        draw_b_w_str = _fmt_dec(draw_b_w)
        b_b_str = _fmt_dec(b_b)

        # Blueprint diagram showing the drawing with its width labeled
        svg = rectangle_svg(
            draw_a_w, rng.randint(3, 6),
            label_w=f"{draw_a_w} in.",
            label_h="",
            title=f"Blueprint (scale: {d_a} in. = {a_a} {unit})",
            width=320, height=180,
        )

        part_a = QuestionPart(
            label="Part A",
            prompt=(
                f"The original blueprint for {article} {context} has a scale of "
                f"{d_a} inches = {a_a} {unit}. The blueprint shows the "
                f"width as {draw_a_w} inches. What is the actual width "
                f"of the {context} in {unit}?"
            ),
            prompt_latex="",
            answer=f"{actual_w} {unit}",
            answer_latex=f"{actual_w} {unit}",
            item_type=ItemType.NR,
        )

        part_b = QuestionPart(
            label="Part B",
            prompt=(
                f"{name} wants to create a new scale drawing of the "
                f"{context} with a scale of 1 inch = {b_b_str} {unit}. "
                f"What is the scale drawing width on the new blueprint "
                f"in inches?"
            ),
            prompt_latex="",
            answer=f"{draw_b_w_str} inches",
            answer_latex=f"{draw_b_w_str} inches",
            item_type=ItemType.NR,
        )

        render = {"svg_html": svg, "type": "svg_html"}

        stem_text = (
            f"This item has two parts.\n\n"
            f"[FIGURE]\n\n"
            f"Part A: The original blueprint for {article} {context} has a scale of "
            f"{d_a} inches = {a_a} {unit}. The blueprint shows the "
            f"width as {draw_a_w} inches. What is the actual width "
            f"of the {context} in {unit}?\n\n"
            f"Part B: {name} wants to create a new scale drawing of the "
            f"{context} with a scale of 1 inch = {b_b_str} {unit}. "
            f"What is the scale drawing width on the new blueprint "
            f"in inches?"
        )

        answer_text = (
            f"Part A: {actual_w} {unit} | "
            f"Part B: {draw_b_w_str} inches"
        )

        solution = (
            f"Part A:\n"
            f"  Scale: {d_a} in. = {a_a} {unit}, so 1 in. = {a_a // d_a if a_a % d_a == 0 else _fmt_dec(a_a / d_a)} {unit}\n"
            f"  Actual width = {draw_a_w} x {a_a // d_a if a_a % d_a == 0 else _fmt_dec(a_a / d_a)} = {actual_w} {unit}\n"
            f"Part B:\n"
            f"  New scale: 1 in. = {b_b_str} {unit}\n"
            f"  Drawing width = {actual_w} / {b_b_str} = {draw_b_w_str} in."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.MEDIUM, 7, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.MEDIUM, dok=3, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_text, answer_latex=answer_text,
            worked_solution=solution,
            parts=[part_a, part_b],
            context_scenario=f"dual scale blueprint {context}",
            seed=self.base_seed * 1000 + 700 + variant_idx,
            stem_index=7, variant_index=variant_idx,
            render_data=render,
        )

    # ================================================================
    # STEM 8: Above Proficiency - MP (DOK 3, Easy)
    # "A student wants to create a scale drawing of the house shown.
    #  The house is 84 ft by 36 ft.
    #  The scale drawing must fit on a paper that is 15 inches long
    #  and 9 inches wide. The drawing should be as large as possible.
    #  Part A: Select the best scale for the drawing.
    #  Part B: What are the dimensions of the scale drawing?"
    # ================================================================

    def stem8_above_mp_best_scale(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(8, variant_idx)

        name = pick_name(rng)

        obj_name, obj_l, obj_w, unit = rng.choice(LARGE_OBJECTS)

        # Paper dimensions (inches)
        paper_options = [(15, 9), (12, 8), (11, 8), (14, 10), (16, 10)]
        paper_l, paper_w = rng.choice(paper_options)

        # Generate 4 scale options — need exactly one "best" (largest that fits)
        # Scale = 1 in : S unit
        # Drawing would be obj_l/S by obj_w/S
        # Must fit: obj_l/S <= paper_l AND obj_w/S <= paper_w
        # Minimum S for length: obj_l / paper_l
        # Minimum S for width: obj_w / paper_w
        min_scale = max(obj_l / paper_l, obj_w / paper_w)

        # Find good scale options (integers) that bracket min_scale
        # We want one that's just at or above min_scale (best), and others
        candidates = sorted(set(range(2, 20)))

        # Scales that fit (>= min_scale)
        fitting = [s for s in candidates if s >= min_scale]
        # Scales that don't fit (< min_scale)
        not_fitting = [s for s in candidates if s < min_scale and s >= 2]

        if len(fitting) < 2 or len(not_fitting) < 1:
            # Fallback: use the predefined object
            obj_l, obj_w = 84, 36
            unit = "ft"
            paper_l, paper_w = 15, 9
            min_scale = max(84 / 15, 36 / 9)  # = 5.6
            fitting = [6, 7, 8, 10]
            not_fitting = [3, 4, 5]

        best_scale = fitting[0]  # smallest fitting = largest drawing

        # Pick 1-2 scales that don't fit, 1-2 larger fitting scales
        too_small = rng.sample(not_fitting, min(1, len(not_fitting)))
        too_big = rng.sample(fitting[1:], min(2, len(fitting) - 1))

        scale_options = sorted(too_small + [best_scale] + too_big)

        # Calculate drawing dimensions for the best scale
        draw_l = obj_l / best_scale
        draw_w = obj_w / best_scale
        draw_l_str = _fmt_dec(draw_l)
        draw_w_str = _fmt_dec(draw_w)

        # Build MC choices for Part A
        mc_choices = []
        correct_key = ""
        for i, s in enumerate(scale_options):
            key = chr(ord('a') + i)
            text = f"1 inch = {s} {unit}"
            is_correct = (s == best_scale)
            mc_choices.append(QuestionChoice(
                key=key, text=text, text_latex=text,
                is_correct=is_correct,
            ))
            if is_correct:
                correct_key = key

        part_a = QuestionPart(
            label="Part A",
            prompt=(
                f"Select the best scale for the drawing."
            ),
            prompt_latex="",
            answer=f"1 inch = {best_scale} {unit}",
            answer_latex=f"1 inch = {best_scale} {unit}",
            item_type=ItemType.MC,
        )

        part_b = QuestionPart(
            label="Part B",
            prompt=(
                f"Using the scale from Part A, what are the dimensions "
                f"of the scale drawing in inches?"
            ),
            prompt_latex="",
            answer=f"{draw_l_str} in. by {draw_w_str} in.",
            answer_latex=f"{draw_l_str} in. by {draw_w_str} in.",
            item_type=ItemType.NR,
        )

        stem_text = (
            f"{name} wants to create a scale drawing of the "
            f"{obj_name} shown. The {obj_name} is {obj_l} {unit} by "
            f"{obj_w} {unit}.\n\n"
            f"The scale drawing must fit on paper that is {paper_l} inches "
            f"long and {paper_w} inches wide. The drawing should be as "
            f"large as possible.\n\n"
            f"Part A: Select the best scale for the drawing.\n\n"
            f"Part B: Using the scale from Part A, what are the dimensions of "
            f"the scale drawing in inches?"
        )

        answer_text = (
            f"Part A: {correct_key} (1 inch = {best_scale} {unit}) | "
            f"Part B: {draw_l_str} in. by {draw_w_str} in."
        )

        # Explain why each scale works or doesn't
        explain_lines = []
        for s in scale_options:
            dl = obj_l / s
            dw = obj_w / s
            fits = dl <= paper_l and dw <= paper_w
            explain_lines.append(
                f"  1 in = {s} {unit}: drawing = {_fmt_dec(dl)} x {_fmt_dec(dw)} in. "
                f"{'- FITS' if fits else '- TOO BIG for paper'}"
            )

        solution = (
            f"Paper: {paper_l} in. x {paper_w} in.\n"
            + "\n".join(explain_lines) + "\n"
            f"Best scale is 1 in. = {best_scale} {unit} (largest drawing that fits).\n"
            f"Drawing: {obj_l}/{best_scale} = {draw_l_str} in., "
            f"{obj_w}/{best_scale} = {draw_w_str} in."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.EASY, 8, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.EASY, dok=3, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_text, answer_latex=answer_text,
            worked_solution=solution,
            choices=mc_choices,
            parts=[part_a, part_b],
            context_scenario=f"best scale for {obj_name}",
            seed=self.base_seed * 1000 + 800 + variant_idx,
            stem_index=8, variant_index=variant_idx,
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_nr,
            self.stem2_approaching_nr,
            self.stem3_approaching_nr_difficult,
            self.stem4_approaching_nr_findx,
            self.stem5_at_nr,
            self.stem6_at_ms,
            self.stem7_above_mp,
            self.stem8_above_mp_best_scale,
        ]
        for stem_fn in stem_methods:
            for v in range(variants_per_stem):
                try:
                    all_questions.append(stem_fn(v))
                except Exception as e:
                    print(f"Error generating {stem_fn.__name__} variant {v}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
        return all_questions

    def generate_stem_variants(self, stem_index: int,
                                variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        stem_methods = {
            1: self.stem1_below_nr,
            2: self.stem2_approaching_nr,
            3: self.stem3_approaching_nr_difficult,
            4: self.stem4_approaching_nr_findx,
            5: self.stem5_at_nr,
            6: self.stem6_at_ms,
            7: self.stem7_above_mp,
            8: self.stem8_above_mp_best_scale,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-8.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 7.GM.1 question variants...")
    gen = Stem7GM1(seed=42)
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
