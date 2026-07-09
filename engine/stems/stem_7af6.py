"""
Stem generator for 7.AF.6:
  Graph a line given its slope and a point on the line.
  Find the slope of a line given its graph.

Content Limits:
  - Linear graphs only
  - Decimals to tenths only
  - Fraction denominators: 2, 3, 4, 5
  - Slopes can be positive or negative
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: whole number coordinates, positive slope
  Medium: integer coordinates, slope positive or negative
  Difficult: fraction/decimal coordinates, decimal slope

5 Stems from the Item Spec:
  Stem 1 (Below-MC):      Classify slope as positive/negative/zero/undefined (DOK 1, Easy)
  Stem 2 (Approaching-MC): Find slope from two points on a line (DOK 1, Easy)
  Stem 3 (At-MC):         Find slope from two points, may include negatives (DOK 2, Medium)
  Stem 4 (Above-MS):      Given point + slope, select TWO other points on line (DOK 2, Medium)
  Stem 5 (Above-NR):      Real-world slope as a fraction (DOK 3, Easy)
"""

import random
from fractions import Fraction
from typing import Optional

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.models import (
    GeneratedQuestion, QuestionChoice, QuestionPart,
    Difficulty, ProficiencyLevel, ItemType, RationalNumber,
    make_question_id
)
from engine.number_generators import NumberGenerator
from engine.distractor_engine import shuffle_choices
from engine.context_pools import CONTEXTS_7AF6_REAL_WORLD_SLOPE, pick_name


STANDARD_CODE = "7.AF.6"
VARIANTS_PER_STEM = 20


def _fmt(val: Fraction) -> str:
    """Format a number for display."""
    if val.denominator == 1:
        return str(int(val))
    av = abs(val)
    if av > 1:
        whole = int(av)
        remainder = av - whole
        if remainder == 0:
            return ("-" if val < 0 else "") + str(whole)
        sign = "-" if val < 0 else ""
        return f"{sign}{whole} {remainder.numerator}/{remainder.denominator}"
    if val < 0:
        return f"-{av.numerator}/{av.denominator}"
    return f"{val.numerator}/{val.denominator}"


def _fmt_slope(val: Fraction) -> str:
    """Format a slope as a fraction."""
    if val.denominator == 1:
        return str(int(val))
    return f"{val.numerator}/{val.denominator}"


class Stem7AF6:
    """Generates ~20 variants for each of 5 stems from the 7.AF.6 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        """Create a seeded NumberGenerator for a specific stem+variant."""
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - Multiple Choice (DOK 1, Easy)
    # Given a line through two points, classify the slope as
    # positive, negative, zero, or undefined.
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Below Proficiency - Classify slope type.

        A line passes through two points. Student identifies the slope
        as positive, negative, zero, or undefined.
        Difficulty: easy (whole number coordinates)
        """
        gen, rng = self._make_gen(1, variant_idx)

        slope_type = rng.choice(["positive", "negative", "zero", "undefined"])

        if slope_type == "positive":
            x1 = rng.randint(0, 5)
            y1 = rng.randint(0, 5)
            x2 = x1 + rng.randint(1, 4)
            y2 = y1 + rng.randint(1, 4)
            explanation = f"Since y increases as x increases (from {y1} to {y2}), the slope is positive."

        elif slope_type == "negative":
            x1 = rng.randint(0, 5)
            y1 = rng.randint(3, 8)
            x2 = x1 + rng.randint(1, 4)
            y2 = y1 - rng.randint(1, 4)
            explanation = f"Since y decreases as x increases (from {y1} to {y2}), the slope is negative."

        elif slope_type == "zero":
            y_val = rng.randint(0, 8)
            x1 = rng.randint(0, 3)
            x2 = x1 + rng.randint(2, 5)
            y1, y2 = y_val, y_val
            explanation = f"The y-values are the same ({y1}), so there is no vertical change. The slope is zero."

        else:  # undefined
            x_val = rng.randint(0, 8)
            y1 = rng.randint(0, 3)
            y2 = y1 + rng.randint(2, 5)
            x1, x2 = x_val, x_val
            explanation = f"The x-values are the same ({x1}), so there is no horizontal change. The slope is undefined."

        correct = f"The slope is {slope_type}."
        distractors = [f"The slope is {t}." for t in ["positive", "negative", "zero", "undefined"] if t != slope_type]

        # Build coordinate grid showing the line
        ix1, iy1, ix2, iy2 = int(x1), int(y1), int(x2), int(y2)
        x_min = min(ix1, ix2) - 2
        x_max = max(ix1, ix2) + 2
        y_min = min(iy1, iy2) - 2
        y_max = max(iy1, iy2) + 2
        x_min = min(x_min, -1)
        y_min = min(y_min, -1)

        if slope_type == "undefined":
            # Vertical line: extend up and down
            grid_lines = [{"x1": ix1, "y1": iy1 - 2, "x2": ix2, "y2": iy2 + 2}]
        elif slope_type == "zero":
            # Horizontal line: extend left and right
            grid_lines = [{"x1": ix1 - 2, "y1": iy1, "x2": ix2 + 2, "y2": iy2}]
        else:
            dx = ix2 - ix1
            dy = iy2 - iy1
            grid_lines = [{"x1": ix1 - dx, "y1": iy1 - dy, "x2": ix2 + dx, "y2": iy2 + dy}]

        grid_render_data = {
            "type": "coordinate_grid",
            "x_range": [x_min, x_max],
            "y_range": [y_min, y_max],
            "points": [
                {"x": ix1, "y": iy1, "label": f"({ix1}, {iy1})"},
                {"x": ix2, "y": iy2, "label": f"({ix2}, {iy2})"},
            ],
            "lines": grid_lines,
        }

        stem_text = "What type of slope does the line shown in the graph below have?"

        choices = shuffle_choices(correct, correct, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

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
            answer_text=f"{correct_letter}) {correct}",
            answer_latex=f"{correct_letter}) {correct}",
            worked_solution=explanation,
            choices=choices,
            render_data=grid_render_data,
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - Multiple Choice (DOK 1, Easy)
    # Find the slope of a line given two points (positive, whole numbers).
    # ================================================================

    def stem2_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Approaching Proficiency - Find slope from two points.

        Two points with whole-number coordinates, positive slope.
        Student computes rise/run.
        Difficulty: easy (whole numbers, positive slope)
        """
        gen, rng = self._make_gen(2, variant_idx)

        # Generate two points with positive slope
        x1, y1, x2, y2, slope = gen.slope_from_points()

        # Force positive slope for easy difficulty
        while slope <= 0:
            gen.reseed(gen.seed + 100)
            x1, y1, x2, y2, slope = gen.slope_from_points()

        # Force whole-number coordinates for easy
        # Regenerate with constrained values
        num = rng.randint(1, 5)
        den = rng.randint(1, 5)
        slope = Fraction(num, den)
        x1 = Fraction(rng.randint(0, 5))
        y1 = Fraction(rng.randint(0, 5))
        x2 = x1 + Fraction(den)
        y2 = y1 + Fraction(num)

        slope_str = _fmt_slope(slope)

        # Distractors
        distractors = []
        # Reciprocal (run/rise)
        recip = Fraction(den, num) if num != 0 else Fraction(1)
        if recip != slope:
            distractors.append(_fmt_slope(recip))
        # Negative slope
        neg = -slope
        if neg != slope:
            distractors.append(_fmt_slope(neg))
        # Off by 1
        off = slope + Fraction(1)
        distractors.append(_fmt_slope(off))

        while len(distractors) < 3:
            d = Fraction(rng.randint(1, 8), rng.randint(1, 5))
            if d != slope and _fmt_slope(d) not in distractors:
                distractors.append(_fmt_slope(d))

        distractors = distractors[:3]

        # Build coordinate grid render_data
        ix1, iy1, ix2, iy2 = int(x1), int(y1), int(x2), int(y2)
        x_min = min(ix1, ix2) - 2
        x_max = max(ix1, ix2) + 2
        y_min = min(iy1, iy2) - 2
        y_max = max(iy1, iy2) + 2
        x_min = min(x_min, -1)
        y_min = min(y_min, -1)

        # Extend line beyond the two points
        dx = ix2 - ix1
        dy = iy2 - iy1
        grid_render_data = {
            "type": "coordinate_grid",
            "x_range": [x_min, x_max],
            "y_range": [y_min, y_max],
            "points": [
                {"x": ix1, "y": iy1, "label": f"({ix1}, {iy1})"},
                {"x": ix2, "y": iy2, "label": f"({ix2}, {iy2})"},
            ],
            "lines": [{"x1": ix1 - dx, "y1": iy1 - dy, "x2": ix2 + dx, "y2": iy2 + dy}],
        }

        stem_text = "What is the slope of the line shown in the graph below?"

        choices = shuffle_choices(slope_str, slope_str, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"slope = (y2 - y1) / (x2 - x1)\n"
            f"      = ({_fmt(y2)} - {_fmt(y1)}) / ({_fmt(x2)} - {_fmt(x1)})\n"
            f"      = {_fmt(y2 - y1)} / {_fmt(x2 - x1)}\n"
            f"      = {slope_str}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY,
            dok=1,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"{correct_letter}) {slope_str}",
            answer_latex=f"{correct_letter}) {slope_str}",
            worked_solution=worked,
            choices=choices,
            render_data=grid_render_data,
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: At Proficiency - Multiple Choice (DOK 2, Medium)
    # Find slope from two points, may include negatives.
    # ================================================================

    def stem3_at_mc(self, variant_idx: int) -> GeneratedQuestion:
        """At Proficiency - Find slope with negative coordinates.

        Two points that may have negative coordinates or negative slope.
        Difficulty: medium (integers, positive or negative slope)
        """
        gen, rng = self._make_gen(3, variant_idx)

        x1, y1, x2, y2, slope = gen.slope_from_points()

        slope_str = _fmt_slope(slope)

        # Distractors
        distractors = []
        # Reciprocal
        if slope.numerator != 0:
            recip = Fraction(slope.denominator, slope.numerator)
            if recip != slope:
                distractors.append(_fmt_slope(recip))
        # Negated
        neg = -slope
        if neg != slope:
            distractors.append(_fmt_slope(neg))
        # Negated reciprocal
        if slope.numerator != 0:
            neg_recip = -Fraction(slope.denominator, slope.numerator)
            if neg_recip != slope and _fmt_slope(neg_recip) not in distractors:
                distractors.append(_fmt_slope(neg_recip))

        while len(distractors) < 3:
            n = rng.randint(-5, 5)
            d = rng.randint(1, 5)
            if n == 0:
                n = 1
            candidate = Fraction(n, d)
            if candidate != slope and _fmt_slope(candidate) not in distractors:
                distractors.append(_fmt_slope(candidate))

        distractors = distractors[:3]

        # Build coordinate grid render_data
        ix1, iy1, ix2, iy2 = int(x1), int(y1), int(x2), int(y2)
        x_min = min(ix1, ix2) - 2
        x_max = max(ix1, ix2) + 2
        y_min = min(iy1, iy2) - 2
        y_max = max(iy1, iy2) + 2
        x_min = min(x_min, -1)
        y_min = min(y_min, -1)

        dx = ix2 - ix1
        dy = iy2 - iy1
        grid_render_data = {
            "type": "coordinate_grid",
            "x_range": [x_min, x_max],
            "y_range": [y_min, y_max],
            "points": [
                {"x": ix1, "y": iy1, "label": f"({ix1}, {iy1})"},
                {"x": ix2, "y": iy2, "label": f"({ix2}, {iy2})"},
            ],
            "lines": [{"x1": ix1 - dx, "y1": iy1 - dy, "x2": ix2 + dx, "y2": iy2 + dy}],
        }

        stem_text = "What is the slope of the line shown in the graph below?"

        choices = shuffle_choices(slope_str, slope_str, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"slope = (y2 - y1) / (x2 - x1)\n"
            f"      = ({_fmt(y2)} - {_fmt(y1)}) / ({_fmt(x2)} - {_fmt(x1)})\n"
            f"      = {_fmt(y2 - y1)} / {_fmt(x2 - x1)}\n"
            f"      = {slope_str}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MC,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM,
            dok=2,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"{correct_letter}) {slope_str}",
            answer_latex=f"{correct_letter}) {slope_str}",
            worked_solution=worked,
            choices=choices,
            render_data=grid_render_data,
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: Above Proficiency - Multiple Select (DOK 2, Medium)
    # Given a point and slope, select TWO other points on the line.
    # ================================================================

    def stem4_above_ms(self, variant_idx: int) -> GeneratedQuestion:
        """Above Proficiency - Find other points on a line.

        Given a point and slope, student selects two points that lie
        on the same line from a list of 5.
        Difficulty: medium (integers, may be negative)
        """
        gen, rng = self._make_gen(4, variant_idx)

        # Generate slope as fraction
        num = rng.randint(-4, 4)
        while num == 0:
            num = rng.randint(-4, 4)
        den = rng.randint(1, 4)
        slope = Fraction(num, den)

        # Starting point
        px = rng.randint(-5, 5)
        py = rng.randint(-5, 5)

        # Generate correct points: move by multiples of (den, num)
        correct_points = []
        for k in [-2, -1, 1, 2, 3]:
            cx = px + k * den
            cy = py + k * num
            if (cx, cy) != (px, py) and -10 <= cx <= 10 and -10 <= cy <= 10:
                correct_points.append((cx, cy))

        if len(correct_points) < 2:
            # Fallback
            correct_points = [(px + den, py + num), (px + 2*den, py + 2*num)]

        # Pick 2 correct
        correct_two = rng.sample(correct_points, min(2, len(correct_points)))
        while len(correct_two) < 2:
            k = rng.randint(3, 5)
            correct_two.append((px + k * den, py + k * num))

        # Generate 3 wrong points (not on the line)
        wrong_points = []
        attempts = 0
        while len(wrong_points) < 3 and attempts < 50:
            wx = rng.randint(-8, 8)
            wy = rng.randint(-8, 8)
            # Check it's NOT on the line: py + slope * (wx - px) != wy
            expected_y = Fraction(py) + slope * (Fraction(wx) - Fraction(px))
            if expected_y != Fraction(wy) and (wx, wy) != (px, py):
                if (wx, wy) not in wrong_points and (wx, wy) not in correct_two:
                    wrong_points.append((wx, wy))
            attempts += 1

        # Fallback wrong points
        while len(wrong_points) < 3:
            wx = px + den
            wy = py + num + rng.choice([1, -1, 2])
            if (wx, wy) not in correct_two and (wx, wy) not in wrong_points:
                wrong_points.append((wx, wy))

        wrong_points = wrong_points[:3]

        # Build choices
        all_options = [(f"({c[0]}, {c[1]})", True) for c in correct_two]
        all_options += [(f"({w[0]}, {w[1]})", False) for w in wrong_points]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i),
                text=text,
                text_latex=text,
                is_correct=is_correct,
            ))

        correct_letters = [c.key for c in choices if c.is_correct]

        slope_str = _fmt_slope(slope)

        stem_text = (
            f"A line passes through ({px}, {py}) and has a slope of {slope_str}.\n\n"
            f"Select TWO points that also lie on this line."
        )

        worked = (
            f"Using slope {slope_str} from ({px}, {py}):\n"
            f"  Move right {den}, up {num}: ({correct_two[0][0]}, {correct_two[0][1]})\n"
            f"  Another step: ({correct_two[1][0]}, {correct_two[1][1]})\n"
            f"Both points satisfy y - {py} = {slope_str}(x - {px})."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MS,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.MEDIUM,
            dok=2,
            item_type=ItemType.MS,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"{', '.join(correct_letters)}) ({correct_two[0][0]}, {correct_two[0][1]}); ({correct_two[1][0]}, {correct_two[1][1]})",
            answer_latex=f"{', '.join(correct_letters)}) ({correct_two[0][0]}, {correct_two[0][1]}); ({correct_two[1][0]}, {correct_two[1][1]})",
            worked_solution=worked,
            choices=choices,
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above Proficiency - Numeric Response (DOK 3, Easy)
    # Real-world rate as slope (e.g., 20 houses per 15 min = 4/3).
    # ================================================================

    def stem5_above_nr(self, variant_idx: int) -> GeneratedQuestion:
        """Above Proficiency - Real-world slope as a fraction.

        Real-world rate described in words. Student expresses it as
        a reduced fraction (slope).
        Difficulty: easy (whole numbers)
        """
        gen, rng = self._make_gen(5, variant_idx)

        name = pick_name(rng)
        ctx = rng.choice(CONTEXTS_7AF6_REAL_WORLD_SLOPE)

        # Generate rate as num/den -- spec limits denominators to 2, 3, 4, 5
        target_den = rng.choice([2, 3, 4, 5])
        target_num = rng.randint(1, target_den * 2)
        while target_num % target_den == 0:  # avoid reducing to integer
            target_num = rng.randint(1, target_den * 2)
        # Scale up for realistic context numbers
        k = rng.randint(1, 5)
        num = target_num * k
        den = target_den * k

        slope = Fraction(num, den)
        slope_str = _fmt_slope(slope)

        desc = ctx["desc"].format(name=name, num=num, den=den)

        # Determine axis labels from context
        rate_unit = ctx["rate_unit"]

        stem_text = (
            f"{desc} The relationship is graphed on a coordinate grid where "
            f"the x-axis represents the time and the y-axis represents the quantity.\n\n"
            f"What is the slope of the line?"
        )

        worked = (
            f"slope = vertical change / horizontal change\n"
            f"      = {num} / {den}\n"
            f"      = {slope_str}\n"
            f"The rate is {slope_str} {rate_unit}."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.NR,
                               Difficulty.EASY, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.EASY,
            dok=3,
            item_type=ItemType.NR,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=slope_str,
            answer_latex=slope_str,
            worked_solution=worked,
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5,
            variant_index=variant_idx
        )

    # ================================================================
    # MAIN GENERATION METHOD
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        """Generate all variants for all 5 stems.

        Returns ~100 questions (5 stems x 20 variants).
        """
        all_questions = []

        stem_methods = [
            self.stem1_below_mc,
            self.stem2_approaching_mc,
            self.stem3_at_mc,
            self.stem4_above_ms,
            self.stem5_above_nr,
        ]

        for stem_fn in stem_methods:
            for v in range(variants_per_stem):
                try:
                    question = stem_fn(v)
                    all_questions.append(question)
                except Exception as e:
                    print(f"Error generating {stem_fn.__name__} variant {v}: {e}")
                    continue

        return all_questions

    def generate_stem_variants(self, stem_index: int,
                                variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        """Generate variants for a single stem (1-5)."""
        stem_methods = {
            1: self.stem1_below_mc,
            2: self.stem2_approaching_mc,
            3: self.stem3_at_mc,
            4: self.stem4_above_ms,
            5: self.stem5_above_nr,
        }

        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-5.")

        questions = []
        for v in range(variants_per_stem):
            try:
                questions.append(fn(v))
            except Exception as e:
                print(f"Error generating stem {stem_index} variant {v}: {e}")
                continue

        return questions


# ================================================================
# CLI ENTRY POINT FOR TESTING
# ================================================================

if __name__ == "__main__":
    print("Generating 7.AF.6 question variants...")
    print("=" * 60)

    generator = Stem7AF6(seed=42)
    all_questions = generator.generate_all_variants(variants_per_stem=3)

    for q in all_questions:
        print(f"\n{'='*60}")
        print(f"ID: {q.question_id}")
        print(f"Stem {q.stem_index} | {q.proficiency_level.value} | {q.difficulty.value} | DOK {q.dok} | {q.item_type.value}")
        print(f"\n{q.stem_text}")
        if q.choices:
            for c in q.choices:
                marker = " *" if c.is_correct else ""
                print(f"  {c.key}. {c.text}{marker}")
        print(f"\nAnswer: {q.answer_text}")
        print(f"\nWorked Solution:\n{q.worked_solution}")

    print(f"\n{'='*60}")
    print(f"Total questions generated: {len(all_questions)}")
