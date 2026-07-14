"""
Stem generator for 7.AF.5:
  Define slope as vertical change for each unit of horizontal change.
  Apply that a constant rate of change describes a linear function.
  Identify and describe situations with constant or varying rates of change.

Content Limits:
  - Slope may be whole numbers, decimals, or fractions
  - Zero/undefined slope may be included sparingly
  - Items must be in real-world context
  - Non-linear examples: percent increases/decreases, multiplicative changes
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: whole numbers only
  Medium: integers or decimals to tenths
  Difficult: rational numbers (fractions)

5 Stems from the Item Spec:
  Stem 1 (Below-MC):      Table of values — constant or varying rate? (DOK 2, Easy)
  Stem 2 (Approaching-MC): Which real-world situation is linear (constant rate)? (DOK 2, Easy)
  Stem 3 (Approaching-MC): Which situation has a varying rate of change? (DOK 2, Easy)
  Stem 4 (At-MC):         Interpret slope value in context (DOK 2, Easy)
  Stem 5 (Above-MP):      Part A: Find rate from table. Part B: Explain (DOK 3, Easy)
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
from engine.context_pools import (
    CONTEXTS_7AF5_LINEAR, CONTEXTS_7AF5_NONLINEAR,
    CONTEXTS_7AF5_SLOPE_INTERP, pick_name
)


STANDARD_CODE = "7.AF.5"
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


def _build_table_text(headers: list[str], rows: list[list], col_width: int = 10) -> str:
    """Build a simple text table for display."""
    lines = []
    header_line = " | ".join(h.ljust(col_width) for h in headers)
    lines.append(f"  {header_line}")
    lines.append(f"  {'-' * len(header_line)}")
    for row in rows:
        row_line = " | ".join(str(v).ljust(col_width) for v in row)
        lines.append(f"  {row_line}")
    return "\n".join(lines)


class Stem7AF5:
    """Generates ~20 variants for each of 5 stems from the 7.AF.5 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        """Create a seeded NumberGenerator for a specific stem+variant."""
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - Multiple Choice (DOK 2, Easy)
    # Table of x/y values — is the rate constant or varying?
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Below Proficiency - Constant or varying rate from a table.

        Table shows x/y values. Student determines if the rate of change
        is constant (linear) or varying (nonlinear).
        Difficulty: easy (whole numbers)
        """
        gen, rng = self._make_gen(1, variant_idx)

        # 50/50 linear vs nonlinear
        is_linear = rng.random() < 0.5

        if is_linear:
            ctx = rng.choice(CONTEXTS_7AF5_LINEAR)
            slope, intercept, points = gen.linear_table(
                n_points=5, x_start=rng.choice([0, 1]), x_step=1
            )
            x_label = ctx["x_label"]
            y_label = ctx["y_label"]
        else:
            ctx = rng.choice(CONTEXTS_7AF5_NONLINEAR)
            points = gen.nonlinear_table(n_points=5, x_start=rng.choice([0, 1]))
            x_label = ctx["x_label"]
            y_label = ctx["y_label"]

        # Build render_data table with random orientation
        orientation = rng.choice(["horizontal", "vertical"])
        # Build coordinate grid for the data points
        all_xs = [int(x) for x, y in points]
        all_ys = [int(y) for x, y in points]
        grid_data = {
            "type": "coordinate_grid",
            "x_range": [min(all_xs) - 1, max(all_xs) + 1],
            "y_range": [min(min(all_ys), 0) - 1, max(all_ys) + 1],
            "points": [{"x": int(x), "y": int(y), "label": ""} for x, y in points],
            "lines": [{"x1": int(points[i][0]), "y1": int(points[i][1]),
                        "x2": int(points[i+1][0]), "y2": int(points[i+1][1])}
                       for i in range(len(points) - 1)],
        }
        table_render_data = {
            "type": "data_table",
            "headers": [x_label, y_label],
            "rows": [[_fmt(x), _fmt(y)] for x, y in points],
            "orientation": orientation,
            "grid": grid_data,
        }

        # Compute differences for worked solution
        diffs = []
        for i in range(1, len(points)):
            dy = points[i][1] - points[i-1][1]
            dx = points[i][0] - points[i-1][0]
            diffs.append((dy, dx))

        diff_strs = [f"{_fmt(dy)}/{_fmt(dx)}" for dy, dx in diffs]

        if is_linear:
            correct = "The rate of change is constant."
            explanation = (
                f"The differences in {y_label} are all the same: "
                f"{', '.join(_fmt(d[0]) for d in diffs)}.\n"
                f"This means the rate of change is constant at {_fmt(slope)} "
                f"{y_label.lower()} per {x_label.lower()[:-1] if x_label.endswith('s') else x_label.lower()}."
            )
        else:
            correct = "The rate of change is varying."
            explanation = (
                f"The differences in {y_label} are NOT the same: "
                f"{', '.join(_fmt(d[0]) for d in diffs)}.\n"
                f"Since the rate changes, this is not a linear function."
            )

        distractors = []
        if is_linear:
            distractors.append("The rate of change is varying.")
            distractors.append("The rate of change cannot be determined from the table.")
            distractors.append("The rate of change is zero.")
        else:
            distractors.append("The rate of change is constant.")
            distractors.append("The rate of change cannot be determined from the table.")
            distractors.append("The rate of change is zero.")

        stem_text = (
            f"The table below shows data for a real-world situation.\n\n"
            f"[FIGURE]\n\n"
            f"Which statement best describes the rate of change?"
        )

        choices = shuffle_choices(correct, correct, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY,
            dok=2,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct}",
            answer_latex=f"{correct_letter}) {correct}",
            worked_solution=explanation,
            choices=choices,
            render_data=table_render_data,
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - Multiple Choice (DOK 2, Easy)
    # Which real-world situation represents a constant rate (linear)?
    # ================================================================

    def stem2_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Approaching Proficiency - Identify the linear situation.

        Four real-world situations described. Student selects the one
        with a constant rate of change.
        Difficulty: easy (whole numbers)
        """
        gen, rng = self._make_gen(2, variant_idx)

        name = pick_name(rng)

        # Pick one linear context (correct)
        linear_ctx = rng.choice(CONTEXTS_7AF5_LINEAR)
        rate = int(gen.small_whole(2, 20))
        correct_desc = linear_ctx["desc"].format(name=name, rate=rate)

        # Pick 3 nonlinear contexts (wrong)
        nonlinear_ctxs = rng.sample(CONTEXTS_7AF5_NONLINEAR, min(3, len(CONTEXTS_7AF5_NONLINEAR)))
        wrong_descs = [ctx["desc"].format(name=name, rate=rate) for ctx in nonlinear_ctxs]

        # Pad if needed
        extra_nonlinear = [
            f"The number of likes on {name}'s post doubles every day",
            f"A bouncing ball loses 20% of its height with each bounce",
            f"A savings account earns 3% interest compounded annually",
        ]
        while len(wrong_descs) < 3:
            wrong_descs.append(rng.choice(extra_nonlinear))

        wrong_descs = wrong_descs[:3]

        stem_text = (
            f"Which situation represents a constant rate of change?"
        )

        choices = shuffle_choices(correct_desc, correct_desc, wrong_descs, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"'{correct_desc}' has a constant rate because "
            f"the same amount is added for each unit of time.\n"
            f"The other situations involve percentages or varying changes."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY,
            dok=2,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct_desc}",
            answer_latex=f"{correct_letter}) {correct_desc}",
            worked_solution=worked,
            choices=choices,
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - Multiple Choice (DOK 2, Easy)
    # Which situation has a VARYING rate of change?
    # ================================================================

    def stem3_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Approaching Proficiency - Identify the varying-rate situation.

        Four situations; student selects the one with varying rate.
        Difficulty: easy (whole numbers)
        """
        gen, rng = self._make_gen(3, variant_idx)

        name = pick_name(rng)

        # Pick one nonlinear (correct)
        nonlinear_ctx = rng.choice(CONTEXTS_7AF5_NONLINEAR)
        rate = int(gen.small_whole(2, 15))
        correct_desc = nonlinear_ctx["desc"].format(name=name, rate=rate)

        # Pick 3 linear (wrong)
        linear_ctxs = rng.sample(CONTEXTS_7AF5_LINEAR, min(3, len(CONTEXTS_7AF5_LINEAR)))
        wrong_descs = []
        for ctx in linear_ctxs:
            r = int(gen.small_whole(2, 20))
            wrong_descs.append(ctx["desc"].format(name=name, rate=r))

        while len(wrong_descs) < 3:
            r = int(gen.small_whole(3, 25))
            wrong_descs.append(f"{name} saves ${r} every week")

        wrong_descs = wrong_descs[:3]

        stem_text = (
            f"Which situation represents a varying rate of change?"
        )

        choices = shuffle_choices(correct_desc, correct_desc, wrong_descs, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"'{correct_desc}' has a varying rate because "
            f"the change is not the same from one period to the next.\n"
            f"The other situations add the same amount each time (constant rate)."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.EASY, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY,
            dok=2,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct_desc}",
            answer_latex=f"{correct_letter}) {correct_desc}",
            worked_solution=worked,
            choices=choices,
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At Proficiency - Multiple Choice (DOK 2, Easy)
    # Interpret slope value in context (e.g., ramp slope 1/12).
    # ================================================================

    def stem4_at_mc(self, variant_idx: int) -> GeneratedQuestion:
        """At Proficiency - Interpret slope in context.

        Given a slope value (fraction), student selects the correct
        interpretation of what it means in context.
        Difficulty: easy (whole numbers in fraction)
        """
        gen, rng = self._make_gen(4, variant_idx)

        ctx = rng.choice(CONTEXTS_7AF5_SLOPE_INTERP)

        # Generate a clean slope fraction (common denominators only)
        num = rng.randint(1, 5)
        allowed = [d for d in [2, 3, 4, 5, 6, 8, 10, 12] if d > num]
        den = rng.choice(allowed)
        slope = Fraction(num, den)

        slope_str = f"{slope.numerator}/{slope.denominator}"

        context_text = ctx["context"].format(slope=slope_str)
        correct_interp = ctx["interp"].format(
            num=slope.numerator, den=slope.denominator
        )

        # Distractors: swap num/den, wrong interpretation
        distractors = []

        # Error 1: swapped — horizontal for vertical
        d1 = ctx["interp"].format(num=slope.denominator, den=slope.numerator)
        if d1 != correct_interp:
            distractors.append(d1)

        # Error 2: both as same (misunderstand ratio)
        d2 = f"For every {slope.numerator} feet of horizontal distance, it rises {slope.numerator} feet."
        if d2 != correct_interp and d2 not in distractors:
            distractors.append(d2)

        # Error 3: wrong numbers entirely
        d3 = ctx["interp"].format(num=slope.numerator + 1, den=slope.denominator)
        if d3 != correct_interp and d3 not in distractors:
            distractors.append(d3)

        # Error 4: inverted meaning
        d4 = f"For every 1 foot of vertical rise, it goes {slope.denominator} feet horizontally."
        if d4 != correct_interp and d4 not in distractors:
            distractors.append(d4)

        while len(distractors) < 3:
            dn = rng.randint(1, 10)
            dd = rng.randint(2, 15)
            d = ctx["interp"].format(num=dn, den=dd)
            if d != correct_interp and d not in distractors:
                distractors.append(d)

        distractors = distractors[:3]

        stem_text = (
            f"{context_text}\n\n"
            f"What does the slope of {slope_str} mean in this context?"
        )

        choices = shuffle_choices(correct_interp, correct_interp, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"Slope = vertical change / horizontal change = {slope_str}.\n"
            f"This means: {correct_interp}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MC,
                               Difficulty.EASY, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.EASY,
            dok=2,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct_interp}",
            answer_latex=f"{correct_letter}) {correct_interp}",
            worked_solution=worked,
            choices=choices,
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above Proficiency - Multi-Part (DOK 3, Easy)
    # Table with two different rate segments.
    # Part A: Find the rate of change for a segment.
    # Part B: Explain why it can't be modeled by one linear function.
    # ================================================================

    def stem5_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        """Above Proficiency - Analyze piecewise rates from a table.

        Table shows data with two different constant rates (piecewise linear).
        Part A: Find rate for one segment.
        Part B: Explain why it's not one linear function.
        Difficulty: easy (whole numbers)
        """
        gen, rng = self._make_gen(5, variant_idx)

        name = pick_name(rng)

        # Half the variants are a single linear function (one constant rate) and
        # half are piecewise (two different rates). The bank needs both so the
        # "can this be modeled by a single linear function?" answer is sometimes
        # yes -- previously every table was piecewise.
        is_linear = (variant_idx % 2 == 0)

        rate1 = int(gen.small_whole(2, 10))
        intercept = int(gen.whole_number(0, 20))
        breakpoint_x = rng.choice([2, 3])

        if is_linear:
            # One constant rate across the whole table.
            rate2 = rate1
            points = [(Fraction(i), Fraction(intercept + rate1 * i))
                      for i in range(breakpoint_x + 4)]
        else:
            # Two segments with different slopes (piecewise, not one linear fn).
            rate2 = int(gen.small_whole(2, 10))
            while rate2 == rate1:
                rate2 = int(gen.small_whole(2, 10))
            points = []
            y = Fraction(intercept)
            for i in range(breakpoint_x + 1):
                points.append((Fraction(i), y))
                if i < breakpoint_x:
                    y += Fraction(rate1)
            for i in range(1, 4):
                y += Fraction(rate2)
                points.append((Fraction(breakpoint_x + i), y))

        # Pick a context
        contexts = [
            {"scenario": f"{name}'s bank account balance over months",
             "x_label": "Month", "y_label": "Balance ($)",
             "rate_unit": "per month"},
            {"scenario": f"Distance {name} has traveled over hours",
             "x_label": "Hour", "y_label": "Distance (miles)",
             "rate_unit": "per hour"},
            {"scenario": f"Number of items {name} has produced over days",
             "x_label": "Day", "y_label": "Items",
             "rate_unit": "per day"},
        ]
        ctx = rng.choice(contexts)

        # Build render_data table with random orientation
        orientation = rng.choice(["horizontal", "vertical"])
        # Build coordinate grid for piecewise data
        s5_xs = [int(x) for x, y in points]
        s5_ys = [int(y) for x, y in points]
        grid_data_5 = {
            "type": "coordinate_grid",
            "x_range": [min(s5_xs) - 1, max(s5_xs) + 1],
            "y_range": [min(min(s5_ys), 0) - 1, max(s5_ys) + 1],
            "points": [{"x": int(x), "y": int(y), "label": ""} for x, y in points],
            "lines": [{"x1": int(points[i][0]), "y1": int(points[i][1]),
                        "x2": int(points[i+1][0]), "y2": int(points[i+1][1])}
                       for i in range(len(points) - 1)],
        }
        table_render_data = {
            "type": "data_table",
            "headers": [ctx["x_label"], ctx["y_label"]],
            "rows": [[_fmt(x), _fmt(y)] for x, y in points],
            "orientation": orientation,
            "grid": grid_data_5,
        }

        # Rate for first segment
        rate1_text = f"${rate1}" if "Balance" in ctx["y_label"] else str(rate1)
        rate2_text = f"${rate2}" if "Balance" in ctx["y_label"] else str(rate2)

        stem_text = (
            f"The table shows {ctx['scenario']}.\n\n"
            f"[FIGURE]\n\n"
            f"Part A: What is the rate of change from {ctx['x_label']} 0 to "
            f"{ctx['x_label']} {breakpoint_x}?\n\n"
            f"Part B: Can the data in the table be modeled by a single linear function? "
            f"Explain your reasoning."
        )

        part_a = QuestionPart(
            label="Part A",
            prompt=f"Rate of change from {ctx['x_label']} 0 to {breakpoint_x}?",
            prompt_latex=f"Rate of change from {ctx['x_label']} 0 to {breakpoint_x}?",
            answer=f"{rate1_text} {ctx['rate_unit']}",
            answer_latex=f"{rate1_text} {ctx['rate_unit']}",
            item_type=ItemType.NR
        )
        if is_linear:
            part_b_answer = (
                f"Yes. The rate of change is constant at {rate1_text} {ctx['rate_unit']} "
                f"across the whole table, so it can be modeled by a single linear function."
            )
            worked_b = (
                f"Part B:\n"
                f"  The rate of change is {rate1_text} {ctx['rate_unit']} for every step "
                f"in the table.\n"
                f"  Because the rate of change is constant, a single linear function "
                f"models this data."
            )
        else:
            part_b_answer = (
                f"No. From {ctx['x_label']} 0 to {breakpoint_x}, the rate is {rate1_text} "
                f"{ctx['rate_unit']}. From {ctx['x_label']} {breakpoint_x} to "
                f"{breakpoint_x + 3}, the rate is {rate2_text} {ctx['rate_unit']}. "
                f"Since the rates differ, it cannot be one linear function."
            )
            worked_b = (
                f"Part B:\n"
                f"  Rate from 0 to {breakpoint_x}: {rate1_text} {ctx['rate_unit']}\n"
                f"  Rate from {breakpoint_x} to {breakpoint_x + 3}: {rate2_text} {ctx['rate_unit']}\n"
                f"  The rates are different, so a single linear function cannot model this data."
            )

        part_b = QuestionPart(
            label="Part B",
            prompt="Can this be modeled by a single linear function?",
            prompt_latex="Can this be modeled by a single linear function?",
            answer=part_b_answer,
            answer_latex="",
            item_type=ItemType.ER
        )

        worked = (
            f"Part A:\n"
            f"  From {ctx['x_label']} 0 to {breakpoint_x}:\n"
            f"  Change in {ctx['y_label']}: {_fmt(points[breakpoint_x][1])} - {_fmt(points[0][1])} = {rate1 * breakpoint_x}\n"
            f"  Change in {ctx['x_label']}: {breakpoint_x} - 0 = {breakpoint_x}\n"
            f"  Rate = {rate1 * breakpoint_x} / {breakpoint_x} = {rate1_text} {ctx['rate_unit']}\n\n"
            f"{worked_b}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.EASY, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.EASY,
            dok=3,
            item_type=ItemType.MP,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"Part A: {rate1_text} {ctx['rate_unit']}; Part B: {'Yes, constant rate.' if is_linear else 'No, rates differ.'}",
            answer_latex=f"Part A: {rate1_text} {ctx['rate_unit']}; Part B: {'Yes, constant rate.' if is_linear else 'No, rates differ.'}",
            worked_solution=worked,
            parts=[part_a, part_b],
            render_data=table_render_data,
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
            self.stem3_approaching_mc,
            self.stem4_at_mc,
            self.stem5_above_mp,
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
            3: self.stem3_approaching_mc,
            4: self.stem4_at_mc,
            5: self.stem5_above_mp,
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
    print("Generating 7.AF.5 question variants...")
    print("=" * 60)

    generator = Stem7AF5(seed=42)
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
