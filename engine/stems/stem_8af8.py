"""
Stem generator for 8.AF.8:
  Approximate the solution of a system of equations by graphing and
  interpreting the reasonableness of the approximation.

Content Limits:
  - Include only rational numbers
  - Solutions should be found by graphing
  - Equations only in slope-intercept form y = mx + b
  - Only continuous graphs
  - Calculator: ALLOWED

5 Stems:
  Stem 1 (Below-MC):        How many solutions? (given graph description) (DOK 1, Easy)
  Stem 2 (Approaching-MC):  What is the solution point? (given graph) (DOK 1, Medium)
  Stem 3 (At-MP):           Graph system, find solution (DOK 2, Medium)
  Stem 4 (At-MC):           Which system matches the given solution? (DOK 2, Medium)
  Stem 5 (Above-MP):        Real-world system interpretation (DOK 3, Easy)
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
from engine.context_pools import CONTEXTS_8AF8_SYSTEM, pick_name


STANDARD_CODE = "8.AF.8"
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
    elif m == 0:
        # y = b
        return f"y = {_fmt(b)}"
    elif m.denominator == 1:
        parts.append(f"{int(m)}x")
    else:
        parts.append(f"({m.numerator}/{m.denominator})x")
    if b > 0:
        parts.append(f" + {_fmt(b)}")
    elif b < 0:
        parts.append(f" - {_fmt(abs(b))}")
    return "".join(parts)


def _make_system_graph(m1, b1, m2, b2, x_range=None, y_range=None,
                       intersection=None):
    """Build render_data for two lines on a coordinate grid.

    If x_range/y_range not given, auto-computes a tight range centered
    around key features (y-intercepts, intersection).
    intersection: (ix, iy) tuple — if given, a dot is placed there.
    """
    # Auto-compute ranges if not provided
    if x_range is None or y_range is None:
        key_x = [0]
        key_y = [float(b1), float(b2)]
        if intersection:
            key_x.append(float(intersection[0]))
            key_y.append(float(intersection[1]))
        x_lo = min(key_x) - 3
        x_hi = max(key_x) + 3
        y_lo = min(key_y) - 3
        y_hi = max(key_y) + 3
        # Ensure at least a -6..6 span and include 0
        x_lo = min(x_lo, -2)
        x_hi = max(x_hi, 2)
        y_lo = min(y_lo, -2)
        y_hi = max(y_hi, 2)
        # Round to integers
        x_lo, x_hi = int(x_lo), int(x_hi)
        y_lo, y_hi = int(y_lo), int(y_hi)
    else:
        x_lo, x_hi = x_range
        y_lo, y_hi = y_range

    # Compute line y-values at grid boundaries for drawing
    y_lo1 = float(m1 * x_lo + b1)
    y_hi1 = float(m1 * x_hi + b1)
    y_lo2 = float(m2 * x_lo + b2)
    y_hi2 = float(m2 * x_hi + b2)

    lines = [
        {"x1": int(x_lo), "y1": y_lo1, "x2": int(x_hi), "y2": y_hi1, "label": "Line 1"},
        {"x1": int(x_lo), "y1": y_lo2, "x2": int(x_hi), "y2": y_hi2, "label": "Line 2"},
    ]

    points = []
    if intersection:
        points.append({"x": float(intersection[0]), "y": float(intersection[1]),
                        "label": f"({_fmt(intersection[0])}, {_fmt(intersection[1])})"})

    # Auto-compute label_step so axes aren't too crowded
    x_span = x_hi - x_lo
    y_span = y_hi - y_lo
    label_step = max(1, max(x_span, y_span) // 10)

    rd = {
        "type": "coordinate_grid",
        "x_range": [x_lo, x_hi],
        "y_range": [y_lo, y_hi],
        "points": points,
        "lines": lines,
        "label_step": label_step,
    }
    return rd


class Stem8AF8:
    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below - MC (DOK 1, Easy)
    # How many solutions does the system have? (graph shown)
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        solution_type = rng.choice(["one", "none", "infinite"])

        intersection = None
        if solution_type == "one":
            m1 = Fraction(rng.randint(1, 4))
            b1 = Fraction(rng.randint(-5, 5))
            m2 = Fraction(rng.randint(-4, -1))
            b2 = Fraction(rng.randint(-5, 5))
            correct = "One solution"
            explanation = "The lines intersect at exactly one point, so there is one solution."
            if m1 != m2:
                ix = (b2 - b1) / (m1 - m2)
                iy = m1 * ix + b1
                intersection = (ix, iy)
        elif solution_type == "none":
            m = Fraction(rng.randint(1, 4))
            b1 = Fraction(rng.randint(1, 6))
            b2 = b1 + rng.randint(2, 5)
            m1 = m
            m2 = m
            correct = "No solution"
            explanation = "The lines are parallel (same slope, different y-intercepts), so there is no solution."
        else:
            m1 = Fraction(rng.randint(1, 4))
            b1 = Fraction(rng.randint(-5, 5))
            m2 = m1
            b2 = b1
            correct = "Infinitely many solutions"
            explanation = "The lines are identical (same slope and y-intercept), so there are infinitely many solutions."

        rd = _make_system_graph(m1, b1, m2, b2, intersection=intersection)

        distractors = ["One solution", "No solution", "Infinitely many solutions"]
        distractors = [d for d in distractors if d != correct]
        distractors.append("Two solutions")
        distractors = distractors[:3]

        eq1_str = _fmt_eq(m1, b1)
        eq2_str = _fmt_eq(m2, b2)

        stem_text = (
            f"A system of equations is graphed below.\n\n"
            f"{eq1_str}\n{eq2_str}\n\n"
            f"How many solutions does the system have?"
        )

        choices = shuffle_choices(correct, correct, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = explanation

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct}",
            answer_latex=f"{correct_letter}) {correct}",
            worked_solution=worked, choices=choices,
            render_data=rd,
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Approaching - MC (DOK 1, Medium)
    # What is the solution (intersection point)? (graph shown)
    # ================================================================

    def stem2_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        # Generate system with integer intersection
        ix = Fraction(rng.randint(-4, 6))
        iy = Fraction(rng.randint(-4, 6))
        m1 = Fraction(rng.randint(1, 4)) * rng.choice([1, -1])
        b1 = iy - m1 * ix
        m2 = Fraction(rng.randint(1, 4)) * rng.choice([1, -1])
        while m2 == m1:
            m2 = Fraction(rng.randint(1, 4)) * rng.choice([1, -1])
        b2 = iy - m2 * ix

        correct = f"({_fmt(ix)}, {_fmt(iy)})"

        # Distractors: swap x/y, nearby points, wrong sign
        distractors = [
            f"({_fmt(iy)}, {_fmt(ix)})",
            f"({_fmt(ix + 1)}, {_fmt(iy - 1)})",
            f"({_fmt(-ix)}, {_fmt(iy)})",
        ]
        distractors = [d for d in distractors if d != correct][:3]
        while len(distractors) < 3:
            dx = Fraction(rng.randint(-2, 2))
            dy = Fraction(rng.randint(-2, 2))
            d = f"({_fmt(ix + dx)}, {_fmt(iy + dy)})"
            if d != correct and d not in distractors:
                distractors.append(d)
        distractors = distractors[:3]

        rd = _make_system_graph(m1, b1, m2, b2, intersection=(ix, iy))

        eq1_str = _fmt_eq(m1, b1)
        eq2_str = _fmt_eq(m2, b2)

        stem_text = (
            f"The graph shows the system of equations:\n\n"
            f"{eq1_str}\n{eq2_str}\n\n"
            f"Which ordered pair best represents the solution?"
        )

        choices = shuffle_choices(correct, correct, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"The lines intersect at {correct}.\n"
            f"Check: {eq1_str}: y = {_fmt(m1)}({_fmt(ix)}) + {_fmt(b1)} = {_fmt(iy)}\n"
            f"Check: {eq2_str}: y = {_fmt(m2)}({_fmt(ix)}) + {_fmt(b2)} = {_fmt(iy)}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.MEDIUM, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct}",
            answer_latex=f"{correct_letter}) {correct}",
            worked_solution=worked, choices=choices,
            render_data=rd,
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: At - MP (DOK 2, Medium)
    # Graph system, find solution. Part A: identify equations, Part B: solution.
    # ================================================================

    def stem3_at_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        # Integer intersection — constrained so lines fit a -5..5 grid
        m1 = Fraction(rng.randint(1, 2))
        m2 = Fraction(rng.randint(-2, -1))
        ix = Fraction(rng.randint(-2, 3))
        iy = Fraction(rng.randint(-2, 3))
        b1 = iy - m1 * ix
        b2 = iy - m2 * ix

        eq1_str = _fmt_eq(m1, b1)
        eq2_str = _fmt_eq(m2, b2)

        # Blank 4-quadrant grid for student to graph on (-5 to 5)
        rd = {
            "type": "coordinate_grid",
            "x_range": [-5, 5],
            "y_range": [-5, 5],
            "points": [],
            "lines": [],
        }

        stem_text = (
            f"Graph the system of equations:\n\n"
            f"{eq1_str}\n{eq2_str}\n\n"
            f"Part A: Graph both equations on the coordinate plane below.\n\n"
            f"Part B: What is the solution to the system?"
        )

        solution_str = f"({_fmt(ix)}, {_fmt(iy)})"

        part_a = QuestionPart(
            label="Part A",
            prompt="Graph both equations.",
            prompt_latex="Graph both equations.",
            answer="See graph.",
            answer_latex="See graph.",
            item_type=ItemType.ER,
        )
        part_b = QuestionPart(
            label="Part B",
            prompt="What is the solution?",
            prompt_latex="What is the solution?",
            answer=solution_str,
            answer_latex=solution_str,
            item_type=ItemType.NR,
        )

        worked = (
            f"Graph {eq1_str}: starts at (0, {_fmt(b1)}), slope {_fmt(m1)}\n"
            f"Graph {eq2_str}: starts at (0, {_fmt(b2)}), slope {_fmt(m2)}\n"
            f"The lines intersect at {solution_str}."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MP,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"A: See graph\nB: {solution_str}",
            answer_latex=f"A: See graph\nB: {solution_str}",
            worked_solution=worked, parts=[part_a, part_b],
            render_data=rd,
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At - MC (DOK 2, Medium)
    # Which coordinate plane represents the system with the correct solution?
    # ================================================================

    def stem4_at_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        # System with integer intersection
        ix = Fraction(rng.randint(-3, 5))
        iy = Fraction(rng.randint(-3, 5))
        m1 = Fraction(rng.randint(1, 3))
        b1 = iy - m1 * ix
        m2 = Fraction(rng.randint(-3, -1))
        b2 = iy - m2 * ix

        eq1_str = _fmt_eq(m1, b1)
        eq2_str = _fmt_eq(m2, b2)

        correct = f"({_fmt(ix)}, {_fmt(iy)})"

        # Distractors: nearby integer points
        dist_points = []
        for dx, dy in [(-1, 1), (1, -1), (2, 0)]:
            pt = f"({_fmt(ix + dx)}, {_fmt(iy + dy)})"
            if pt != correct:
                dist_points.append(pt)
        while len(dist_points) < 3:
            dist_points.append(f"({_fmt(ix + rng.randint(-3, 3))}, {_fmt(iy + rng.randint(-3, 3))})")
        distractors = dist_points[:3]

        rd = _make_system_graph(m1, b1, m2, b2, intersection=(ix, iy))

        stem_text = (
            f"A system of equations is given:\n\n"
            f"{eq1_str}\n{eq2_str}\n\n"
            f"What is the solution to this system of equations?"
        )

        choices = shuffle_choices(correct, correct, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"Set the equations equal: {_fmt(m1)}x + {_fmt(b1)} = {_fmt(m2)}x + {_fmt(b2)}\n"
            f"({_fmt(m1)} - {_fmt(m2)})x = {_fmt(b2)} - {_fmt(b1)}\n"
            f"{_fmt(m1 - m2)}x = {_fmt(b2 - b1)}\n"
            f"x = {_fmt(ix)}\n"
            f"y = {_fmt(m1)}({_fmt(ix)}) + {_fmt(b1)} = {_fmt(iy)}\n"
            f"Solution: {correct}"
        )

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
            render_data=rd,
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above - MP (DOK 3, Easy)
    # Real-world system interpretation.
    # ================================================================

    def stem5_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)
        name = pick_name(rng)

        ctx = CONTEXTS_8AF8_SYSTEM[variant_idx % len(CONTEXTS_8AF8_SYSTEM)]

        # Generate system with integer intersection
        # Ensure m1 > m2 so b2 stays positive in context (higher rate = lower start)
        m1 = Fraction(rng.randint(2, 5))
        m2 = Fraction(rng.randint(1, int(m1) - 1))
        b1 = Fraction(rng.randint(10, 50))
        # Choose b2 so intersection is at a nice x value
        ix = Fraction(rng.randint(5, 15))
        b2 = (m1 - m2) * ix + b1

        iy = m1 * ix + b1

        desc_a = ctx["func_a"].replace("{m1}", str(int(m1))).replace("{b1}", str(int(b1)))
        desc_b = ctx["func_b"].replace("{m2}", str(int(m2))).replace("{b2}", str(int(b2)))
        desc_a = desc_a.replace("{name}", name)
        desc_b = desc_b.replace("{name}", name)

        eq1_str = _fmt_eq(m1, b1)
        eq2_str = _fmt_eq(m2, b2)

        rd = _make_system_graph(m1, b1, m2, b2, intersection=(ix, iy))

        solution_str = f"({_fmt(ix)}, {_fmt(iy)})"

        # Determine which has lower initial cost and which has lower rate
        if b1 < b2:
            lower_initial = "A"
        elif b2 < b1:
            lower_initial = "B"
        else:
            lower_initial = "both (same)"

        stem_text = (
            f"{ctx['desc']}: {desc_a}; {desc_b}. [FIGURE]\n\n"
            f"Part A: Write the system of equations.\n\n"
            f"Part B: At what {ctx['x_label']} value are the {ctx['y_label']}s equal?\n\n"
            f"Part C: Interpret the solution."
        )

        part_a = QuestionPart(
            label="Part A",
            prompt="Write the system of equations.",
            prompt_latex="Write the system of equations.",
            answer=f"{eq1_str} and {eq2_str}",
            answer_latex=f"{eq1_str} and {eq2_str}",
            item_type=ItemType.EQ,
        )
        part_b = QuestionPart(
            label="Part B",
            prompt=f"At what value of {ctx['x_label']} will the {ctx['y_label']} be the same?",
            prompt_latex=f"At what value of {ctx['x_label']} will the {ctx['y_label']} be the same?",
            answer=f"At {_fmt(ix)} {ctx['x_label']}, the {ctx['y_label']} is ${_fmt(iy)} for both.",
            answer_latex=f"At {_fmt(ix)} {ctx['x_label']}, the {ctx['y_label']} is ${_fmt(iy)} for both.",
            item_type=ItemType.NR,
        )
        part_c = QuestionPart(
            label="Part C",
            prompt="Interpret the solution.",
            prompt_latex="Interpret the solution.",
            answer=f"At {_fmt(ix)} {ctx['x_label']}, both options cost ${_fmt(iy)}. "
                   f"Before that point, the option with the lower initial cost is cheaper. "
                   f"After that point, the option with the lower rate is cheaper.",
            answer_latex=f"At {_fmt(ix)} {ctx['x_label']}, both options cost ${_fmt(iy)}. "
                         f"Before that point, the option with the lower initial cost is cheaper. "
                         f"After that point, the option with the lower rate is cheaper.",
            item_type=ItemType.ER,
        )

        worked = (
            f"System: {eq1_str} and {eq2_str}\n"
            f"Set equal: {_fmt(m1)}x + {_fmt(b1)} = {_fmt(m2)}x + {_fmt(b2)}\n"
            f"x = {_fmt(ix)}, y = {_fmt(iy)}\n"
            f"At {_fmt(ix)} {ctx['x_label']}, both cost ${_fmt(iy)}."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.EASY, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.EASY, dok=3, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"A: {eq1_str} and {eq2_str}\nB: x = {_fmt(ix)}, y = {_fmt(iy)}\nC: At {_fmt(ix)} {ctx['x_label']}, both cost ${_fmt(iy)}.",
            answer_latex=f"A: {eq1_str} and {eq2_str}\nB: x = {_fmt(ix)}, y = {_fmt(iy)}\nC: At {_fmt(ix)} {ctx['x_label']}, both cost ${_fmt(iy)}.",
            worked_solution=worked, parts=[part_a, part_b, part_c],
            render_data=rd,
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx,
        )

    # ================================================================
    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        for stem_fn in [self.stem1_below_mc, self.stem2_approaching_mc,
                        self.stem3_at_mp, self.stem4_at_mc, self.stem5_above_mp]:
            for v in range(variants_per_stem):
                all_questions.append(stem_fn(v))
        return all_questions

    def generate_stem_variants(self, stem_index: int,
                               variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        methods = {1: self.stem1_below_mc, 2: self.stem2_approaching_mc,
                   3: self.stem3_at_mp, 4: self.stem4_at_mc, 5: self.stem5_above_mp}
        return [methods[stem_index](v) for v in range(variants_per_stem)]
