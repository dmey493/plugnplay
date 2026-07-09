"""
Stem generator for 8.AF.6:
  Construct a function to model a linear relationship between two quantities
  given a verbal description, table of values, or graph. Describe the meaning
  of m (rate of change) and b (y-intercept) in y = mx + b.

Content Limits:
  - Include linear functions only
  - Equations always in y = mx + b form
  - y-intercept must be included in context (or as (0,b) without context)
  - Only continuous graphs
  - Calculator: ALLOWED

5 Stems:
  Stem 1 (Below-MC):        Find rate of change from a table (DOK 2, Medium)
  Stem 2 (Below-MC):        Find y-intercept from equation (DOK 1, Easy)
  Stem 3 (Approaching-MC):  Match real-world scenario to equation (DOK 1, Easy)
  Stem 4 (At-MP):           Construct function from context, interpret (DOK 2, Medium)
  Stem 5 (Above-MP):        Write equation + interpret m and b in context (DOK 2, Medium)
"""

import random
from fractions import Fraction

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.models import (
    GeneratedQuestion, QuestionPart,
    Difficulty, ProficiencyLevel, ItemType,
    make_question_id
)
from engine.number_generators import NumberGenerator
from engine.distractor_engine import shuffle_choices
from engine.context_pools import CONTEXTS_8AF6_LINEAR, pick_name


STANDARD_CODE = "8.AF.6"
VARIANTS_PER_STEM = 20


def _fmt(val: Fraction) -> str:
    if val.denominator == 1:
        return str(int(val))
    av = abs(val)
    if val < 0:
        return f"-{av.numerator}/{av.denominator}"
    return f"{val.numerator}/{val.denominator}"


def _fmt_eq(m: Fraction, b: Fraction) -> str:
    """Format y = mx + b."""
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


class Stem8AF6:
    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below - MC (DOK 2, Medium)
    # Find the rate of change from a table of values.
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        # Generate y = mx + b table
        m = Fraction(rng.randint(1, 6)) * rng.choice([1, -1])
        b = Fraction(rng.randint(0, 10))
        # Non-consecutive x values for medium difficulty
        xs = sorted(rng.sample(range(0, 10), 5))
        rows = [(Fraction(x), m * Fraction(x) + b) for x in xs]

        correct = _fmt(m)

        # Distractors
        distractors = []
        if m != 0:
            distractors.append(_fmt(Fraction(1) / m if m.numerator != 0 else Fraction(1)))
        distractors.append(_fmt(abs(m)))
        distractors.append(_fmt(-m))
        distractors.append(_fmt(b))
        # De-dup
        distractors = [d for d in distractors if d != correct]
        while len(distractors) < 3:
            v = Fraction(rng.randint(1, 10)) * rng.choice([1, -1])
            s = _fmt(v)
            if s != correct and s not in distractors:
                distractors.append(s)
        distractors = distractors[:3]

        # Build coordinate grid showing the line
        x_vals_int = [int(x) for x, y in rows]
        y_vals_int = [int(y) for x, y in rows]
        grid_x_min = min(x_vals_int) - 1
        grid_x_max = max(x_vals_int) + 1
        grid_y_min = min(min(y_vals_int), 0) - 1
        grid_y_max = max(y_vals_int) + 1

        table_render = {
            "type": "data_table",
            "headers": ["x", "y"],
            "rows": [[_fmt(x), _fmt(y)] for x, y in rows],
            "orientation": "vertical",
            "grid": {
                "type": "coordinate_grid",
                "x_range": [grid_x_min, grid_x_max],
                "y_range": [grid_y_min, grid_y_max],
                "points": [{"x": int(x), "y": int(y), "label": ""} for x, y in rows],
                "lines": [{"x1": grid_x_min, "y1": float(m * grid_x_min + b),
                            "x2": grid_x_max, "y2": float(m * grid_x_max + b)}],
            },
        }

        stem_text = "A table of values is given.\n\nWhat is the rate of change (slope)?"

        choices = shuffle_choices(correct, correct, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        dx = rows[1][0] - rows[0][0]
        dy = rows[1][1] - rows[0][1]
        worked = (
            f"Rate of change = (change in y) / (change in x)\n"
            f"= ({_fmt(rows[1][1])} - {_fmt(rows[0][1])}) / ({_fmt(rows[1][0])} - {_fmt(rows[0][0])})\n"
            f"= {_fmt(dy)} / {_fmt(dx)} = {_fmt(m)}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.MEDIUM, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct}",
            answer_latex=f"{correct_letter}) {correct}",
            worked_solution=worked, choices=choices,
            render_data=table_render,
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Below - MC (DOK 1, Easy)
    # Identify the rate of change from an equation y = mx + b.
    # ================================================================

    def stem2_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        # Use fractions for medium difficulty
        num = rng.randint(1, 7)
        den = rng.choice([2, 3, 4, 5])
        while num % den == 0:
            num = rng.randint(1, 7)
        m = Fraction(num, den) * rng.choice([1, -1])
        b = Fraction(rng.randint(1, 12))

        eq_str = _fmt_eq(m, b)
        correct = _fmt(m)

        distractors = [_fmt(b), _fmt(abs(m)), _fmt(Fraction(den, num))]
        distractors = [d for d in distractors if d != correct]
        while len(distractors) < 3:
            v = Fraction(rng.randint(1, 8)) * rng.choice([1, -1])
            s = _fmt(v)
            if s != correct and s not in distractors:
                distractors.append(s)
        distractors = distractors[:3]

        stem_text = f"What is the rate of change of the function {eq_str}?"

        choices = shuffle_choices(correct, correct, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = f"In y = mx + b, the rate of change (slope) is m. Here m = {_fmt(m)}."

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct}",
            answer_latex=f"{correct_letter}) {correct}",
            worked_solution=worked, choices=choices,
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching - MC (DOK 1, Easy)
    # Real-world scenario: which equation matches?
    # ================================================================

    def stem3_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)
        name = pick_name(rng)

        ctx = CONTEXTS_8AF6_LINEAR[variant_idx % len(CONTEXTS_8AF6_LINEAR)]
        m = Fraction(rng.randint(2, 10))
        b = Fraction(rng.randint(5, 50))

        desc = ctx["desc"].format(name=name, m=int(m), b=int(b))
        correct_eq = _fmt_eq(m, b)

        # Distractors: swap m/b, wrong signs, wrong values
        distractors = [
            _fmt_eq(b, m),                    # swapped
            _fmt_eq(m, -b),                   # wrong sign on b
            _fmt_eq(m + Fraction(rng.randint(1, 3)), b),  # wrong m
        ]
        distractors = [d for d in distractors if d != correct_eq][:3]
        while len(distractors) < 3:
            distractors.append(_fmt_eq(Fraction(rng.randint(1, 10)), Fraction(rng.randint(1, 20))))
        distractors = distractors[:3]

        stem_text = f"{desc}\n\nWhich equation represents this relationship?"

        choices = shuffle_choices(correct_eq, correct_eq, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"The rate of change (m) is {_fmt(m)} ({ctx['m_meaning']}).\n"
            f"The initial value (b) is {_fmt(b)} ({ctx['b_meaning']}).\n"
            f"Equation: {correct_eq}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.EASY, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct_eq}",
            answer_latex=f"{correct_letter}) {correct_eq}",
            worked_solution=worked, choices=choices,
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At - MP (DOK 2, Medium)
    # Construct function from context + table. Part A: equation, Part B: interpret.
    # ================================================================

    def stem4_at_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)
        name = pick_name(rng)

        ctx = CONTEXTS_8AF6_LINEAR[(variant_idx + 3) % len(CONTEXTS_8AF6_LINEAR)]
        m = Fraction(rng.randint(2, 8))
        b = Fraction(rng.randint(5, 30))

        desc = ctx["desc"].format(name=name, m=int(m), b=int(b))
        correct_eq = _fmt_eq(m, b)

        # Build a small table
        xs = [Fraction(x) for x in range(5)]
        rows = [(x, m * x + b) for x in xs]

        table_render = {
            "type": "data_table",
            "headers": [ctx["x_label"], ctx["y_label"]],
            "rows": [[_fmt(x), _fmt(y)] for x, y in rows],
            "orientation": "vertical",
        }

        stem_text = (
            f"{desc}\n\n"
            f"The table shows the data.\n\n"
            f"Part A: Write the equation that represents this relationship in the form y = mx + b.\n\n"
            f"Part B: What does the rate of change represent in this situation?"
        )

        part_a = QuestionPart(
            label="Part A",
            prompt="Write the equation.",
            prompt_latex="Write the equation.",
            answer=correct_eq,
            answer_latex=correct_eq,
            item_type=ItemType.EQ,
        )
        part_b = QuestionPart(
            label="Part B",
            prompt="What does the rate of change represent?",
            prompt_latex="What does the rate of change represent?",
            answer=f"The rate of change ({_fmt(m)}) represents the {ctx['m_meaning']}.",
            answer_latex=f"The rate of change ({_fmt(m)}) represents the {ctx['m_meaning']}.",
            item_type=ItemType.ER,
        )

        worked = (
            f"From the table, the rate of change is ({_fmt(rows[1][1])} - {_fmt(rows[0][1])}) / "
            f"({_fmt(rows[1][0])} - {_fmt(rows[0][0])}) = {_fmt(m)}.\n"
            f"The y-intercept (when x = 0) is {_fmt(b)}.\n"
            f"Equation: {correct_eq}\n"
            f"The rate of change represents the {ctx['m_meaning']}."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MP,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"A: {correct_eq}\nB: The rate of change represents the {ctx['m_meaning']}.",
            answer_latex=f"A: {correct_eq}\nB: The rate of change represents the {ctx['m_meaning']}.",
            worked_solution=worked, parts=[part_a, part_b],
            render_data=table_render,
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above - MP (DOK 2, Medium)
    # Write equation from context, interpret m and b fully.
    # ================================================================

    def stem5_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)
        name = pick_name(rng)

        ctx = CONTEXTS_8AF6_LINEAR[(variant_idx + 5) % len(CONTEXTS_8AF6_LINEAR)]
        m = Fraction(rng.randint(2, 10))
        b = Fraction(rng.randint(5, 40))

        desc = ctx["desc"].format(name=name, m=int(m), b=int(b))
        correct_eq = _fmt_eq(m, b)

        stem_text = (
            f"{desc}\n\n"
            f"Part A: Write the equation in the form y = mx + b.\n\n"
            f"Part B: What does the slope (m) represent in this context?\n\n"
            f"Part C: What does the y-intercept (b) represent in this context?"
        )

        part_a = QuestionPart(
            label="Part A",
            prompt="Write the equation.",
            prompt_latex="Write the equation.",
            answer=correct_eq, answer_latex=correct_eq,
            item_type=ItemType.EQ,
        )
        part_b = QuestionPart(
            label="Part B",
            prompt="What does m represent?",
            prompt_latex="What does m represent?",
            answer=f"m = {_fmt(m)} represents the {ctx['m_meaning']}.",
            answer_latex=f"m = {_fmt(m)} represents the {ctx['m_meaning']}.",
            item_type=ItemType.ER,
        )
        part_c = QuestionPart(
            label="Part C",
            prompt="What does b represent?",
            prompt_latex="What does b represent?",
            answer=f"b = {_fmt(b)} represents the {ctx['b_meaning']}.",
            answer_latex=f"b = {_fmt(b)} represents the {ctx['b_meaning']}.",
            item_type=ItemType.ER,
        )

        worked = (
            f"Equation: {correct_eq}\n"
            f"m = {_fmt(m)}: {ctx['m_meaning']}\n"
            f"b = {_fmt(b)}: {ctx['b_meaning']}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.MEDIUM, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"A: {correct_eq}\nB: m = {_fmt(m)} ({ctx['m_meaning']})\nC: b = {_fmt(b)} ({ctx['b_meaning']})",
            answer_latex=f"A: {correct_eq}\nB: m = {_fmt(m)} ({ctx['m_meaning']})\nC: b = {_fmt(b)} ({ctx['b_meaning']})",
            worked_solution=worked, parts=[part_a, part_b, part_c],
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        for stem_fn in [self.stem1_below_mc, self.stem2_below_mc,
                        self.stem3_approaching_mc, self.stem4_at_mp, self.stem5_above_mp]:
            for v in range(variants_per_stem):
                all_questions.append(stem_fn(v))
        return all_questions

    def generate_stem_variants(self, stem_index: int,
                               variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        methods = {1: self.stem1_below_mc, 2: self.stem2_below_mc,
                   3: self.stem3_approaching_mc, 4: self.stem4_at_mp, 5: self.stem5_above_mp}
        return [methods[stem_index](v) for v in range(variants_per_stem)]
