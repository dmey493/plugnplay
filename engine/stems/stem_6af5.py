"""
Stem generator for 6.AF.5:
  Solve real-world and other mathematical problems by graphing points with
  rational number coordinates on a coordinate plane. Include the use of
  coordinates and absolute value to find distances between points with
  the same first coordinate or the same second coordinate.

Content Limits:
  - Include rational numbers
  - All four quadrants
  - Distance only between points with same x or same y (horiz/vert only)
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: Ordered pairs within same quadrant, integers only, all visuals
  Medium: One integer and one decimal/fraction, coordinate plane provided
  Difficult: Ordered pairs on opposite sides of axes, decimals/fractions, no visuals

4 Stems:
  Stem 1 (Below-MC, DOK 1):     Identify parts of coordinate plane; plot/identify points
  Stem 2 (Approaching-NR, DOK 1-2): Calculate distance between two points (same x or y)
  Stem 3 (At-NR, DOK 2):        Solve real-world problem using ordered pairs
  Stem 4 (Above-MP, DOK 3):     Find multiple points at given distance from original
"""

import random
from fractions import Fraction

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.models import (
    GeneratedQuestion, QuestionChoice, QuestionPart,
    Difficulty, ProficiencyLevel, ItemType, make_question_id
)
from engine.number_generators import NumberGenerator
from engine.svg_helpers import coord_grid_polygon_svg
from engine.stem_guards import distinct_choices


STANDARD_CODE = "6.AF.5"
VARIANTS_PER_STEM = 20


NAMES = ["Marcus", "Sofia", "Jayden", "Aaliyah", "Wei", "Priya", "Carlos", "Maya",
         "Ethan", "Lin", "Amir", "Emma", "Diego", "Zara", "Leo", "Grace"]


def _fmt(val, dec=1):
    f = float(val)
    if f == int(f):
        return str(int(f))
    return f"{f:.{dec}f}".rstrip('0').rstrip('.')


def _point_svg(points, x_range, y_range, labels=None, width=300, height=300):
    """Create a coordinate grid SVG with just points (no polygon lines)."""
    import drawsvg as draw
    import math

    d = draw.Drawing(width, height)
    margin = 45
    x_min, x_max = x_range
    y_min, y_max = y_range
    gw = width - 2 * margin
    gh = height - 2 * margin

    def to_px(x, y):
        px = margin + (x - x_min) / (x_max - x_min) * gw
        py = margin + (y_max - y) / (y_max - y_min) * gh
        return px, py

    # Grid lines
    for x in range(x_min, x_max + 1):
        px, _ = to_px(x, 0)
        d.append(draw.Line(px, margin, px, margin + gh,
                           stroke='#e5e7eb', stroke_width=0.5))
    for y in range(y_min, y_max + 1):
        _, py = to_px(0, y)
        d.append(draw.Line(margin, py, margin + gw, py,
                           stroke='#e5e7eb', stroke_width=0.5))

    # Axes
    if x_min <= 0 <= x_max:
        ax_px, _ = to_px(0, 0)
        d.append(draw.Line(ax_px, margin, ax_px, margin + gh,
                           stroke='#374151', stroke_width=1.5))
    if y_min <= 0 <= y_max:
        _, ax_py = to_px(0, 0)
        d.append(draw.Line(margin, ax_py, margin + gw, ax_py,
                           stroke='#374151', stroke_width=1.5))

    # Axis labels
    step = 1 if (x_max - x_min) <= 12 else 2
    for x in range(x_min, x_max + 1, step):
        if x == 0:
            continue
        px, py0 = to_px(x, 0)
        ref_py = py0 if y_min <= 0 <= y_max else margin + gh
        d.append(draw.Text(str(x), 10, px, ref_py + 14,
                           text_anchor='middle', fill='#6b7280'))
    for y in range(y_min, y_max + 1, step):
        if y == 0:
            continue
        px0, py = to_px(0, y)
        ref_px = px0 if x_min <= 0 <= x_max else margin
        d.append(draw.Text(str(y), 10, ref_px - 8, py + 4,
                           text_anchor='end', fill='#6b7280'))

    # Axis names
    d.append(draw.Text('x', 13, margin + gw + 8, margin + gh + 14 if y_min <= 0 <= y_max else margin + gh + 14,
                       fill='#374151', font_weight='bold'))
    d.append(draw.Text('y', 13, margin - 14 if x_min <= 0 <= x_max else margin - 14,
                       margin - 8, fill='#374151', font_weight='bold'))

    # Origin
    if x_min <= 0 <= x_max and y_min <= 0 <= y_max:
        opx, opy = to_px(0, 0)
        d.append(draw.Text('O', 10, opx - 10, opy + 14, fill='#6b7280'))

    # Points
    vertex_labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    colors = ['#2563eb', '#dc2626', '#059669', '#d97706', '#7c3aed']
    if labels is None:
        labels = [vertex_labels[i] for i in range(len(points))]

    for i, (x, y) in enumerate(points):
        px, py = to_px(x, y)
        color = colors[i % len(colors)]
        d.append(draw.Circle(px, py, 4.5, fill=color, stroke='white', stroke_width=1))
        ox = 10 if x >= 0 else -10
        oy = -10 if y >= 0 else 12
        anchor = 'start' if x >= 0 else 'end'
        lbl = labels[i]
        d.append(draw.Text(lbl, 10, px + ox, py + oy,
                           text_anchor=anchor, fill=color, font_weight='bold'))

    return d.as_svg()


class Stem6AF5:
    """Generates 20 variants for each of 4 stems from the 6.AF.5 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx, variant_idx):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ----------------------------------------------------------------
    # Stem 1: Below – Identify points on coordinate plane (MC, DOK 1)
    # ----------------------------------------------------------------
    @distinct_choices
    def _stem1(self, variant_idx):
        gen, rng = self._make_gen(1, variant_idx)

        # Generate a point and ask which quadrant / what ordered pair
        x = rng.randint(-6, 6)
        while x == 0:
            x = rng.randint(-6, 6)
        y = rng.randint(-6, 6)
        while y == 0:
            y = rng.randint(-6, 6)

        svg = _point_svg([(x, y)], (-7, 7), (-7, 7), labels=["P"])

        # Determine quadrant
        if x > 0 and y > 0:
            quadrant = "I"
        elif x < 0 and y > 0:
            quadrant = "II"
        elif x < 0 and y < 0:
            quadrant = "III"
        else:
            quadrant = "IV"

        ask_type = rng.choice(["coordinates", "quadrant"])

        if ask_type == "coordinates":
            stem = f"What are the coordinates of point P shown on the grid? [FIGURE]"
            correct = f"({x}, {y})"
            wrong = [
                f"({y}, {x})",
                f"({-x}, {y})",
                f"({x}, {-y})",
            ]
        else:
            stem = f"In which quadrant is point P located? [FIGURE]"
            correct = f"Quadrant {quadrant}"
            wrong = [f"Quadrant {q}" for q in ["I", "II", "III", "IV"] if q != quadrant][:3]

        all_choices = [(correct, True)] + [(w, False) for w in wrong]
        rng.shuffle(all_choices)
        keys = "abcd"
        choices = []
        answer_key = ""
        for i, (text, is_c) in enumerate(all_choices):
            choices.append(QuestionChoice(key=keys[i], text=text, text_latex=text, is_correct=is_c))
            if is_c:
                answer_key = keys[i]

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW,
                                         ItemType.MC, Difficulty.EASY, 1, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_key, answer_latex=answer_key,
            worked_solution=f"Point P is at ({x}, {y}) in Quadrant {quadrant}.",
            choices=choices,
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=gen.seed, stem_index=1, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 2: Approaching – Calculate distance (same x or same y) (NR, DOK 1-2)
    # ----------------------------------------------------------------
    def _stem2(self, variant_idx):
        gen, rng = self._make_gen(2, variant_idx)

        # Generate two points with same x or same y
        direction = rng.choice(["vertical", "horizontal"])

        if direction == "vertical":
            x = rng.randint(-5, 5)
            y1 = rng.randint(-6, -1)
            y2 = rng.randint(1, 6)
            p1 = (x, y1)
            p2 = (x, y2)
            dist = abs(y2 - y1)
            worked = f"|{y2} - ({y1})| = |{y2 - y1}| = {dist}"
        else:
            y = rng.randint(-5, 5)
            x1 = rng.randint(-6, -1)
            x2 = rng.randint(1, 6)
            p1 = (x1, y)
            p2 = (x2, y)
            dist = abs(x2 - x1)
            worked = f"|{x2} - ({x1})| = |{x2 - x1}| = {dist}"

        svg = _point_svg([p1, p2], (-7, 7), (-7, 7), labels=["A", "B"])

        stem = (f"Point A is at {p1} and Point B is at {p2}. [FIGURE] "
                f"What is the distance between Point A and Point B?")

        answer_str = str(dist)

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING,
                                         ItemType.NR, Difficulty.MEDIUM, 2, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_str, answer_latex=answer_str,
            worked_solution=f"Distance = {worked}",
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=gen.seed, stem_index=2, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 3: At – Multi-step real-world problem using coordinates (MP, DOK 2)
    # ----------------------------------------------------------------
    def _stem3(self, variant_idx):
        gen, rng = self._make_gen(3, variant_idx)
        name = rng.choice(NAMES)

        # Three points forming an L-path: A -> B (horiz) then B -> C (vert) or vice versa
        ax = rng.randint(-5, -1)
        ay = rng.randint(-4, 0)
        bx = rng.randint(1, 5)
        by = ay  # same y as A (horizontal segment)
        cx = bx  # same x as B (vertical segment)
        cy = rng.randint(1, 5)

        dist_ab = abs(bx - ax)
        dist_bc = abs(cy - by)
        total = dist_ab + dist_bc

        p_a, p_b, p_c = (ax, ay), (bx, by), (cx, cy)
        svg = _point_svg([p_a, p_b, p_c], (-7, 7), (-7, 7), labels=["A", "B", "C"])

        contexts = [
            {"desc": f"{name} is delivering packages on a city grid. "
                     f"The route goes from location A to location B, then from B to C. "
                     f"Each grid unit represents 1 block.",
             "unit": "blocks"},
            {"desc": f"On a park map, {name} walks from the entrance (A) to the "
                     f"playground (B), then from the playground to the picnic area (C). "
                     f"Each grid unit represents 10 meters.",
             "unit": "meters", "scale": 10},
            {"desc": f"{name} is mapping a garden. Three features are plotted: "
                     f"a fountain (A), a bench (B), and a tree (C). "
                     f"Each grid unit represents 1 yard.",
             "unit": "yards"},
        ]
        ctx = rng.choice(contexts)
        scale = ctx.get("scale", 1)

        stem = (f"{ctx['desc']} [FIGURE]")

        partA_prompt = f"What is the distance from A to B?"
        partA_answer = f"{dist_ab * scale} {ctx['unit']}"

        partB_prompt = f"What is the total distance from A to B to C?"
        partB_answer = f"{total * scale} {ctx['unit']}"

        parts = [
            QuestionPart(
                label="Part A", prompt=partA_prompt, prompt_latex=partA_prompt,
                answer=partA_answer, answer_latex=partA_answer, item_type=ItemType.NR,
            ),
            QuestionPart(
                label="Part B", prompt=partB_prompt, prompt_latex=partB_prompt,
                answer=partB_answer, answer_latex=partB_answer, item_type=ItemType.NR,
            ),
        ]

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.AT,
                                         ItemType.MP, Difficulty.MEDIUM, 3, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MP,
            stem_text=stem, stem_latex=stem,
            answer_text=f"A: {partA_answer} B: {partB_answer}",
            answer_latex=f"A: {partA_answer} B: {partB_answer}",
            worked_solution=(f"A to B: |{bx} - ({ax})| = {dist_ab} units. "
                             f"B to C: |{cy} - ({by})| = {dist_bc} units. "
                             f"Total = {dist_ab} + {dist_bc} = {total} units."
                             + (f" {total} x {scale} = {total * scale} {ctx['unit']}." if scale > 1 else "")),
            parts=parts,
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=gen.seed, stem_index=3, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 4: Above – Find multiple points at given distance (MP, DOK 3)
    # ----------------------------------------------------------------
    def _stem4(self, variant_idx):
        gen, rng = self._make_gen(4, variant_idx)

        # Difficult tier: no visual, use decimals/fractions
        # Use half-integer coordinates for non-integer values
        halves = [-3.5, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 3.5]
        px = rng.choice(halves)
        py = rng.choice(halves)
        d = rng.choice([2.5, 3.5, 4.5, 5.5])

        def _fmt_coord(v):
            if v == int(v):
                return str(int(v))
            return str(v)

        px_s, py_s, d_s = _fmt_coord(px), _fmt_coord(py), _fmt_coord(d)

        # Real-world contexts (no model per Difficult tier)
        contexts = [
            (f"On a park map, a fountain is located at F({px_s}, {py_s}). "
             f"Each grid unit represents 1 meter. A groundskeeper wants to place "
             f"benches exactly {d_s} meters from the fountain."),
            (f"On a garden grid, a sprinkler is at F({px_s}, {py_s}). "
             f"Each unit represents 1 foot. The sprinkler reaches exactly {d_s} feet."),
            (f"On a school campus map, the flagpole is at F({px_s}, {py_s}). "
             f"Each grid unit is 1 yard. Signs must be placed exactly {d_s} yards away."),
        ]
        ctx = rng.choice(contexts)

        stem = (ctx + " Use the coordinate grid below to plot point F and "
                "find the requested locations.\n\n[FIGURE]")

        y_up = py + d
        y_down = py - d
        partA_prompt = (f"Name two locations that are exactly {d_s} units from F "
                        f"and are directly north or south of F (same x-coordinate).")
        partA_answer = f"({px_s}, {_fmt_coord(y_up)}) and ({px_s}, {_fmt_coord(y_down)})"

        x_right = px + d
        x_left = px - d
        partB_prompt = (f"Name two locations that are exactly {d_s} units from F "
                        f"and are directly east or west of F (same y-coordinate).")
        partB_answer = f"({_fmt_coord(x_right)}, {py_s}) and ({_fmt_coord(x_left)}, {py_s})"

        parts = [
            QuestionPart(
                label="Part A", prompt=partA_prompt, prompt_latex=partA_prompt,
                answer=partA_answer, answer_latex=partA_answer, item_type=ItemType.NR,
            ),
            QuestionPart(
                label="Part B", prompt=partB_prompt, prompt_latex=partB_prompt,
                answer=partB_answer, answer_latex=partB_answer, item_type=ItemType.NR,
            ),
        ]

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE,
                                         ItemType.MP, Difficulty.DIFFICULT, 4, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=ItemType.MP,
            stem_text=stem, stem_latex=stem,
            answer_text=f"A: {partA_answer} B: {partB_answer}",
            answer_latex=f"A: {partA_answer} B: {partB_answer}",
            worked_solution=f"Same x: add/subtract {d_s} from y = {partA_answer}. Same y: add/subtract {d_s} from x = {partB_answer}.",
            parts=parts,
            render_data={
                "type": "coordinate_grid",
                "x_range": [-10, 10],
                "y_range": [-10, 10],
                "points": [],
                "lines": [],
                "hide_labels": True,
            },
            seed=gen.seed, stem_index=4, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    def generate_all_variants(self, variants_per_stem=VARIANTS_PER_STEM):
        questions = []
        for v in range(variants_per_stem):
            questions.append(self._stem1(v))
            questions.append(self._stem2(v))
            questions.append(self._stem3(v))
            questions.append(self._stem4(v))
        return questions
