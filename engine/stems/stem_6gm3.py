"""
Stem generator for 6.GM.3:
  Find the area of complex shapes composed of polygons by composing or
  decomposing into simple shapes; apply this technique to solve real-world
  and other mathematical problems.

Content Limits:
  - Limit to positive rational numbers
  - Shapes decompose into rectangles, parallelograms, and triangles
  - All complex shapes consist of at least two simple shapes
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: Limit to rectangular shapes or a single right triangle.
        Measurements in whole numbers.
  Medium: Two different simple shapes. Triangles have height labeled inside.
          Measurements are a mixture of whole numbers and decimals or fractions.
  Difficult: Multiple simple shapes. Triangles have height labeled outside.
             Measurements are in decimals or fractions.

4 Stems from the Item Spec:
  Stem 1 (Below-MC):       Area of L-shape (two rectangles) (DOK 2, Easy)
  Stem 2 (Approaching-NR): Area of 3-shape composite (rect+rect+triangle) (DOK 2, Medium)
  Stem 3 (At-NR):          Real-world decomposition problem (DOK 2, Medium)
  Stem 4 (Above-NR):       Negative space: large rect minus cutout (DOK 2, Easy)
"""

import random
import math
from fractions import Fraction
from decimal import Decimal

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


STANDARD_CODE = "6.GM.3"
VARIANTS_PER_STEM = 20


# ============================================================
# HELPERS
# ============================================================

UNITS = ["ft", "m", "cm", "in.", "yd"]

REAL_WORLD_CONTEXTS = [
    ("garden", "a garden", "sq"),
    ("floor", "a floor plan", "sq"),
    ("patio", "a patio", "sq"),
    ("parking", "a parking lot", "sq"),
    ("playground", "a playground", "sq"),
    ("wall", "a wall to be painted", "sq"),
    ("carpet", "an area to be carpeted", "sq"),
    ("pool_deck", "a pool deck", "sq"),
]


def _fmt_dec(val):
    """Format a number for display - whole numbers as ints, decimals to 1-2 places."""
    if isinstance(val, Fraction):
        f_val = float(val)
    else:
        f_val = float(val)
    if f_val == int(f_val):
        return str(int(f_val))
    # Round to avoid floating point artifacts
    rounded = round(f_val, 2)
    if rounded == int(rounded):
        return str(int(rounded))
    return str(rounded)


class Stem6GM3:
    """Generates ~20 variants for each of 4 stems from the 6.GM.3 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 2, Easy)
    # L-shape (two rectangles), whole number dimensions
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        unit = rng.choice(UNITS)

        # L-shape: a big rectangle with a smaller rectangle attached
        # Layout: bottom rectangle (w1 x h1) + right rectangle stacked on top (w2 x h2)
        w1 = rng.randint(8, 20)
        h1 = rng.randint(4, 10)
        w2 = rng.randint(3, w1 - 2)  # narrower than base
        h2 = rng.randint(3, 8)

        area = w1 * h1 + w2 * h2

        # Build composite_shape render_data
        rotated = rng.random() < 0.5  # sometimes horizontal L

        if rotated:
            # Horizontal L: left rect full height, right rect bottom portion
            scale = min(250 / (h1 + h2), 200 / w1)
            scale = min(scale, 15)

            r1_x, r1_y = 0, 0
            r1_w, r1_h = h1 * scale, w1 * scale
            r2_x, r2_y = h1 * scale, (w1 - w2) * scale
            r2_w, r2_h = h2 * scale, w2 * scale

            svg_w = int((h1 + h2) * scale + 60)
            svg_h = int(w1 * scale + 60)

            dimensions = [
                # Bottom width (total)
                {"x1": 0, "y1": r1_h + 15, "x2": r1_w + r2_w, "y2": r1_h + 15,
                 "label": f"{h1 + h2} {unit}"},
                # Left height (full)
                {"x1": -15, "y1": 0, "x2": -15, "y2": r1_h,
                 "label": f"{w1} {unit}"},
                # Top of right rect (width)
                {"x1": r2_x, "y1": r2_y - 10, "x2": r2_x + r2_w, "y2": r2_y - 10,
                 "label": f"{h2} {unit}"},
                # Right height (partial)
                {"x1": r1_w + r2_w + 15, "y1": r2_y, "x2": r1_w + r2_w + 15, "y2": r1_h,
                 "label": f"{w2} {unit}"},
            ]
            dashed_lines = []
        else:
            # Vertical L: bottom rect full width, top rect narrower
            scale = min(250 / max(w1, w2), 200 / (h1 + h2))
            scale = min(scale, 15)

            r1_x, r1_y = 0, h2 * scale
            r1_w, r1_h = w1 * scale, h1 * scale
            r2_x, r2_y = 0, 0
            r2_w, r2_h = w2 * scale, h2 * scale

            svg_w = int(w1 * scale + 60)
            svg_h = int((h1 + h2) * scale + 60)

            dimensions = [
                # Bottom width
                {"x1": r1_x, "y1": r1_y + r1_h + 15, "x2": r1_x + r1_w, "y2": r1_y + r1_h + 15,
                 "label": f"{w1} {unit}"},
                # Left height (full)
                {"x1": r1_x - 15, "y1": r2_y, "x2": r1_x - 15, "y2": r1_y + r1_h,
                 "label": f"{h1 + h2} {unit}"},
                # Top width of upper rect
                {"x1": r2_x, "y1": r2_y - 10, "x2": r2_x + r2_w, "y2": r2_y - 10,
                 "label": f"{w2} {unit}"},
                # Right height of lower rect only
                {"x1": r1_x + r1_w + 15, "y1": r1_y, "x2": r1_x + r1_w + 15, "y2": r1_y + r1_h,
                 "label": f"{h1} {unit}"},
            ]
            dashed_lines = [
                {"x1": r2_w, "y1": r2_h, "x2": r1_w, "y2": r2_h},
            ]

        render = {
            "type": "composite_shape",
            "svg_width": svg_w,
            "svg_height": svg_h,
            "offset_x": 25,
            "offset_y": 30,
            "shapes": [
                {"type": "rect", "x": r1_x, "y": r1_y, "width": r1_w, "height": r1_h,
                 "fill": "#dbeafe"},
                {"type": "rect", "x": r2_x, "y": r2_y, "width": r2_w, "height": r2_h,
                 "fill": "#bfdbfe"},
            ],
            "dimensions": dimensions,
            "dashed_lines": dashed_lines,
        }

        correct_str = f"{area} sq {unit}"

        # Distractors
        d1 = w1 * (h1 + h2)  # treating as full rectangle
        d2 = w1 * h1          # only bottom
        d3 = 2 * (w1 + h1 + h2)  # perimeter-ish
        dist_set = {str(d1), str(d2), str(d3)}
        dist_set.discard(str(area))
        dist_list = list(dist_set)[:3]
        while len(dist_list) < 3:
            d = area + rng.choice([-5, 5, 10, -10])
            if str(d) != str(area) and str(d) not in dist_list and d > 0:
                dist_list.append(str(d))

        all_options = [(correct_str, True)]
        for d in dist_list[:3]:
            all_options.append((f"{d} sq {unit}", False))
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text,
                text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = (
            f"The figure below shows a complex shape.\n\n"
            f"What is the total area of the shape?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=(
                f"Decompose into two rectangles:\n"
                f"Rectangle 1: {w1} x {h1} = {w1 * h1} sq {unit}\n"
                f"Rectangle 2: {w2} x {h2} = {w2 * h2} sq {unit}\n"
                f"Total = {w1 * h1} + {w2 * h2} = {area} sq {unit}"
            ),
            choices=choices, context_scenario="L-shape area",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx,
            render_data=render,
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - NR (DOK 2, Medium)
    # 3-shape composite (rect + rect + triangle)
    # ================================================================

    def stem2_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        unit = rng.choice(UNITS)

        # Rectangle base + triangle on top
        rect_w = rng.randint(6, 14)
        rect_h_dec = rng.randint(6, 18) / 2  # 3.0 to 9.0 in 0.5 steps
        tri_h_dec = rng.randint(4, 12) / 2  # 2.0 to 6.0 in 0.5 steps

        rect_area = rect_w * rect_h_dec
        tri_area = 0.5 * rect_w * tri_h_dec
        total_area = rect_area + tri_area

        scale = min(250 / rect_w, 200 / (rect_h_dec + tri_h_dec))
        scale = min(scale, 14)

        r_x, r_y = 0, tri_h_dec * scale
        r_w, r_h = rect_w * scale, rect_h_dec * scale

        # Triangle on top of rectangle (isoceles, base = rect_w)
        tri_points = (
            f"{r_x},{r_y} "
            f"{r_x + r_w},{r_y} "
            f"{r_x + r_w / 2},{0}"
        )

        render = {
            "type": "composite_shape",
            "svg_width": int(r_w + 60),
            "svg_height": int((rect_h_dec + tri_h_dec) * scale + 50),
            "offset_x": 25,
            "offset_y": 20,
            "shapes": [
                {"type": "rect", "x": r_x, "y": r_y, "width": r_w, "height": r_h,
                 "fill": "#dbeafe"},
                {"type": "triangle", "points": tri_points, "fill": "#fef3c7"},
            ],
            "dimensions": [
                # Bottom width
                {"x1": r_x, "y1": r_y + r_h + 15, "x2": r_x + r_w, "y2": r_y + r_h + 15,
                 "label": f"{rect_w} {unit}"},
                # Right height of rectangle
                {"x1": r_x + r_w + 15, "y1": r_y, "x2": r_x + r_w + 15, "y2": r_y + r_h,
                 "label": f"{_fmt_dec(rect_h_dec)} {unit}"},
                # Triangle height (dashed line from apex to base)
                {"x1": r_x + r_w / 2, "y1": 0, "x2": r_x + r_w / 2, "y2": r_y,
                 "label": f"{_fmt_dec(tri_h_dec)} {unit}", "dashed": True},
            ],
            "dashed_lines": [],
        }

        stem_text = (
            f"The figure below shows a composite shape made of a rectangle and a triangle.\n\n"
            f"What is the total area, in square {unit}, of the shape?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.MEDIUM, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=_fmt_dec(total_area), answer_latex=_fmt_dec(total_area),
            worked_solution=(
                f"Rectangle area = {rect_w} x {_fmt_dec(rect_h_dec)} = {_fmt_dec(rect_area)} sq {unit}\n"
                f"Triangle area = 1/2 x {rect_w} x {_fmt_dec(tri_h_dec)} = {_fmt_dec(tri_area)} sq {unit}\n"
                f"Total = {_fmt_dec(rect_area)} + {_fmt_dec(tri_area)} = {_fmt_dec(total_area)} sq {unit}"
            ),
            context_scenario="composite shape area",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx,
            render_data=render,
        )

    # ================================================================
    # STEM 3: At Proficiency - NR (DOK 2, Medium)
    # Real-world decomposition problem
    # ================================================================

    def stem3_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        ctx = rng.choice(REAL_WORLD_CONTEXTS)
        ctx_key, ctx_desc, sq = ctx
        unit = rng.choice(UNITS)
        name = pick_name(rng)

        # Shape: rectangle + triangle extension (like a house shape)
        rect_w = rng.randint(8, 18)
        rect_h_dec = rng.choice([4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8])
        tri_base = rng.randint(3, rect_w - 2)
        tri_h_dec = rng.choice([3, 3.5, 4, 4.5, 5])

        rect_area = rect_w * rect_h_dec
        tri_area = 0.5 * tri_base * tri_h_dec
        total_area = rect_area + tri_area

        orient_top = rng.random() < 0.5

        if orient_top:
            # Triangle on top of rectangle (house shape)
            scale = min(250 / rect_w, 180 / (rect_h_dec + tri_h_dec))
            scale = min(scale, 13)

            r_x, r_y = 0, tri_h_dec * scale
            r_w, r_h = rect_w * scale, rect_h_dec * scale

            tri_cx = r_x + r_w / 2
            tri_half = tri_base * scale / 2
            tri_points = (
                f"{tri_cx - tri_half},{r_y} "
                f"{tri_cx + tri_half},{r_y} "
                f"{tri_cx},{0}"
            )

            svg_w = int(rect_w * scale + 60)
            svg_h = int((rect_h_dec + tri_h_dec) * scale + 60)

            dimensions = [
                # Bottom width of rectangle
                {"x1": r_x, "y1": r_y + r_h + 15, "x2": r_x + r_w, "y2": r_y + r_h + 15,
                 "label": f"{rect_w} {unit}"},
                # Left height of rectangle
                {"x1": r_x - 15, "y1": r_y, "x2": r_x - 15, "y2": r_y + r_h,
                 "label": f"{_fmt_dec(rect_h_dec)} {unit}"},
                # Triangle base (horizontal on top)
                {"x1": tri_cx - tri_half, "y1": r_y - 5,
                 "x2": tri_cx + tri_half, "y2": r_y - 5,
                 "label": f"{tri_base} {unit}"},
                # Triangle height (vertical)
                {"x1": tri_cx + tri_half + 10, "y1": 0,
                 "x2": tri_cx + tri_half + 10, "y2": r_y,
                 "label": f"{_fmt_dec(tri_h_dec)} {unit}"},
            ]
            dashed_lines = []
        else:
            # Triangle on right side of rectangle
            scale = min(250 / (rect_w + tri_base), 180 / rect_h_dec)
            scale = min(scale, 13)

            r_x, r_y = 0, 0
            r_w, r_h = rect_w * scale, rect_h_dec * scale

            tri_points = (
                f"{r_x + r_w},{r_y} "
                f"{r_x + r_w + tri_base * scale},{r_y + r_h / 2} "
                f"{r_x + r_w},{r_y + r_h}"
            )

            svg_w = int((rect_w + tri_base) * scale + 60)
            svg_h = int(rect_h_dec * scale + 60)

            dimensions = [
                # Bottom width of rectangle
                {"x1": r_x, "y1": r_y + r_h + 15, "x2": r_x + r_w, "y2": r_y + r_h + 15,
                 "label": f"{rect_w} {unit}"},
                # Left height of rectangle
                {"x1": r_x - 15, "y1": r_y, "x2": r_x - 15, "y2": r_y + r_h,
                 "label": f"{_fmt_dec(rect_h_dec)} {unit}"},
                # Triangle height (vertical on right)
                {"x1": r_x + r_w + tri_base * scale + 15, "y1": r_y,
                 "x2": r_x + r_w + tri_base * scale + 15, "y2": r_y + r_h,
                 "label": f"{_fmt_dec(tri_h_dec)} {unit}"},
                # Triangle base (horizontal)
                {"x1": r_x + r_w, "y1": r_y + r_h + 15,
                 "x2": r_x + r_w + tri_base * scale, "y2": r_y + r_h + 15,
                 "label": f"{tri_base} {unit}"},
            ]
            dashed_lines = [
                {"x1": r_w, "y1": r_y, "x2": r_w, "y2": r_y + r_h},
            ]

        render = {
            "type": "composite_shape",
            "svg_width": svg_w,
            "svg_height": svg_h,
            "offset_x": 25,
            "offset_y": 30,
            "shapes": [
                {"type": "rect", "x": r_x, "y": r_y, "width": r_w, "height": r_h,
                 "fill": "#d1fae5"},
                {"type": "triangle", "points": tri_points, "fill": "#fef3c7"},
            ],
            "dimensions": dimensions,
            "dashed_lines": dashed_lines,
        }

        stem_text = (
            f"{name} is designing {ctx_desc} shaped like the figure below.\n\n"
            f"What is the total area, in square {unit}, of the shape?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=_fmt_dec(total_area), answer_latex=_fmt_dec(total_area),
            worked_solution=(
                f"Rectangle area = {rect_w} x {_fmt_dec(rect_h_dec)} = {_fmt_dec(rect_area)} {sq} {unit}\n"
                f"Triangle area = 1/2 x {tri_base} x {_fmt_dec(tri_h_dec)} = {_fmt_dec(tri_area)} {sq} {unit}\n"
                f"Total = {_fmt_dec(rect_area)} + {_fmt_dec(tri_area)} = {_fmt_dec(total_area)} {sq} {unit}"
            ),
            context_scenario=ctx_key,
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx,
            render_data=render,
        )

    # ================================================================
    # STEM 4: Above Proficiency - NR (DOK 2, Easy)
    # Negative space: large rectangle minus cutout
    # ================================================================

    def stem4_above_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        unit = rng.choice(UNITS)
        name = pick_name(rng)

        # Large rectangle with a triangular or rectangular cutout
        outer_w = rng.randint(12, 22)
        outer_h = rng.randint(8, 16)
        outer_area = outer_w * outer_h

        # Choose cutout type
        cutout_type = rng.choice(["rect", "triangle"])

        if cutout_type == "rect":
            cut_w = rng.randint(3, outer_w // 2)
            cut_h = rng.randint(3, outer_h // 2)
            cut_area = cut_w * cut_h
        else:
            cut_base = rng.randint(3, outer_w // 2)
            cut_h = rng.randint(3, outer_h // 2)
            cut_area = cut_base * cut_h / 2

        shaded_area = outer_area - cut_area

        scale = min(250 / outer_w, 200 / outer_h)
        scale = min(scale, 12)

        o_w, o_h = outer_w * scale, outer_h * scale

        # Cutout position: centered or offset
        if cutout_type == "rect":
            c_x = (o_w - cut_w * scale) / 2
            c_y = (o_h - cut_h * scale) / 2
            cut_shape = {"type": "rect", "x": c_x, "y": c_y,
                         "width": cut_w * scale, "height": cut_h * scale,
                         "fill": "white", "stroke": "#6b7280", "stroke_dasharray": "4,3"}
            cut_dims = [
                {"x1": c_x, "y1": c_y + cut_h * scale + 10,
                 "x2": c_x + cut_w * scale, "y2": c_y + cut_h * scale + 10,
                 "label": f"{cut_w} {unit}"},
                {"x1": c_x + cut_w * scale + 10, "y1": c_y,
                 "x2": c_x + cut_w * scale + 10, "y2": c_y + cut_h * scale,
                 "label": f"{cut_h} {unit}"},
            ]
        else:
            # Triangle cutout in center
            cx = o_w / 2
            cy = o_h / 2
            tri_points = (
                f"{cx - cut_base * scale / 2},{cy + cut_h * scale / 2} "
                f"{cx + cut_base * scale / 2},{cy + cut_h * scale / 2} "
                f"{cx},{cy - cut_h * scale / 2}"
            )
            cut_shape = {"type": "triangle", "points": tri_points,
                         "fill": "white", "stroke": "#6b7280", "stroke_dasharray": "4,3"}
            cut_dims = [
                {"x1": cx - cut_base * scale / 2, "y1": cy + cut_h * scale / 2 + 10,
                 "x2": cx + cut_base * scale / 2, "y2": cy + cut_h * scale / 2 + 10,
                 "label": f"{cut_base} {unit}"},
                {"x1": cx + 5, "y1": cy - cut_h * scale / 2,
                 "x2": cx + 5, "y2": cy + cut_h * scale / 2,
                 "label": f"{cut_h} {unit}", "dashed": True},
            ]

        render = {
            "type": "composite_shape",
            "svg_width": int(o_w + 60),
            "svg_height": int(o_h + 50),
            "offset_x": 25,
            "offset_y": 20,
            "shapes": [
                {"type": "rect", "x": 0, "y": 0, "width": o_w, "height": o_h,
                 "fill": "#e0e7ff"},
                cut_shape,
            ],
            "dimensions": [
                {"x1": 0, "y1": o_h + 15, "x2": o_w, "y2": o_h + 15,
                 "label": f"{outer_w} {unit}"},
                {"x1": -15, "y1": 0, "x2": -15, "y2": o_h,
                 "label": f"{outer_h} {unit}"},
            ] + cut_dims,
            "dashed_lines": [],
        }

        if cutout_type == "rect":
            cut_desc = f"rectangular opening ({cut_w} {unit} by {cut_h} {unit})"
            cut_area_str = f"{cut_w} x {cut_h} = {cut_area}"
        else:
            cut_desc = f"triangular opening (base {cut_base} {unit}, height {cut_h} {unit})"
            cut_area_str = f"1/2 x {cut_base} x {cut_h} = {_fmt_dec(cut_area)}"

        stem_text = (
            f"{name} has a rectangular region that is {outer_w} {unit} by {outer_h} {unit}. "
            f"There is a {cut_desc} cut out of the center, as shown in the figure below.\n\n"
            f"What is the area, in square {unit}, of the shaded region?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.NR,
                               Difficulty.EASY, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=_fmt_dec(shaded_area), answer_latex=_fmt_dec(shaded_area),
            worked_solution=(
                f"Outer rectangle area = {outer_w} x {outer_h} = {outer_area} sq {unit}\n"
                f"Cutout area = {cut_area_str} sq {unit}\n"
                f"Shaded area = {outer_area} - {_fmt_dec(cut_area)} = {_fmt_dec(shaded_area)} sq {unit}"
            ),
            context_scenario="negative space area",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx,
            render_data=render,
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
    print("Generating 6.GM.3 question variants...")
    gen = Stem6GM3(seed=42)
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
        if q.render_data:
            print(f"Visual: {q.render_data.get('type', 'none')}")
    print(f"\nTotal: {len(all_q)}")
