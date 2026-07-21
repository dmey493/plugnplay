"""
Stem generator for 8.AF.5:
  Interpret y = mx + b as defining a linear function. Give examples of
  nonlinear functions. Describe similarities/differences between linear
  and nonlinear functions from tables, graphs, verbal descriptions, equations.

Content Limits:
  - No function notation
  - Linear functions in slope-intercept form y = mx + b (b != 0)
  - Functions may be presented in tables, graphs, verbal descriptions,
    ordered pairs, and equations
  - Only continuous graphs; discrete graphs may not be used
  - Calculator: ALLOWED

5 Stems:
  Stem 1 (Below-MC):        Identify slope and y-intercept from y = mx + b (DOK 1, Easy)
  Stem 2 (Approaching-MC):  Which function is nonlinear? (DOK 1, Medium)
  Stem 3 (At-MC):           Table: is the function linear or nonlinear? (DOK 2, Medium)
  Stem 4 (At-MS):           Classify multiple functions as linear/nonlinear (DOK 2, Medium)
  Stem 5 (Above-MP):        Real-world: linear or nonlinear? Explain (DOK 3, Easy)
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


STANDARD_CODE = "8.AF.5"
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
        # Bare fraction hugging the variable — the renderer stacks "a/b"
        # and handles a leading minus; no parentheses ("y = 5/3x + 5").
        parts.append(f"{m.numerator}/{m.denominator}x")
    if b > 0:
        parts.append(f" + {_fmt(b)}")
    elif b < 0:
        parts.append(f" - {_fmt(abs(b))}")
    return "".join(parts)


# Nonlinear equation templates
_NONLINEAR_TEMPLATES = [
    ("y = {a}x^2 + {b}", "quadratic"),
    ("y = {a}x^2 - {b}", "quadratic"),
    ("y = {a}x^3", "cubic"),
    ("y = {a}/x + {b}", "rational"),
    ("y = {a}/x", "rational"),
    ("y = {a} * 2^x", "exponential"),
]


def _make_nonlinear_eq(rng) -> str:
    """Generate a random nonlinear equation string."""
    tmpl, _ = rng.choice(_NONLINEAR_TEMPLATES)
    a = rng.randint(1, 5)
    b = rng.randint(1, 8)
    return tmpl.format(a=a, b=b)


def _make_linear_table(rng, m: Fraction, b: Fraction, consecutive: bool = True):
    """Generate a table of (x, y) values for y = mx + b."""
    if consecutive:
        x0 = rng.randint(0, 3)
        xs = [Fraction(x0 + i) for i in range(5)]
    else:
        xs = sorted(Fraction(v) for v in rng.sample(range(0, 10), 5))
    rows = [(x, m * x + b) for x in xs]
    return rows


def _make_nonlinear_table(rng, kind: str = "quadratic"):
    """Generate a nonlinear table of (x, y) values."""
    a = Fraction(rng.randint(1, 3))
    b = Fraction(rng.randint(0, 4))
    xs = [Fraction(i) for i in range(1, 6)]
    if kind == "quadratic":
        rows = [(x, a * x * x + b) for x in xs]
    elif kind == "doubling":
        rows = [(x, a * Fraction(2) ** int(x) + b) for x in xs]
    else:
        rows = [(x, a * x * x + b) for x in xs]
    return rows


def _check_constant_rate(rows) -> bool:
    """Check if a table has a constant rate of change."""
    if len(rows) < 2:
        return True
    rates = []
    for i in range(1, len(rows)):
        dx = rows[i][0] - rows[i - 1][0]
        dy = rows[i][1] - rows[i - 1][1]
        if dx == 0:
            return False
        rates.append(dy / dx)
    return all(r == rates[0] for r in rates)


class Stem8AF5:
    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below - MC (DOK 1, Easy)
    # Identify slope and y-intercept from y = mx + b.
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        m = Fraction(rng.randint(1, 8)) * rng.choice([1, -1])
        b = Fraction(rng.randint(1, 10)) * rng.choice([1, -1])

        eq_str = _fmt_eq(m, b)

        # Ask about slope or y-intercept
        ask_slope = rng.random() < 0.5
        if ask_slope:
            correct = _fmt(m)
            question = f"What is the slope of the equation {eq_str}?"
            distractors = [_fmt(b), _fmt(abs(m)), _fmt(-m)]
        else:
            correct = _fmt(b)
            question = f"What is the y-intercept of the equation {eq_str}?"
            distractors = [_fmt(m), _fmt(abs(b)), _fmt(-b)]

        # De-duplicate distractors against the correct answer AND each other.
        # (e.g. y = 3x - 3: slope distractors [b, |m|, -m] = [-3, 3, -3]
        #  collapse; y = -5x - 9: [b, |m|, -m] = [-9, 5, 5] collapse.)
        seen = {correct}
        unique = []
        for d in distractors:
            if d not in seen:
                seen.add(d)
                unique.append(d)
        # Substitute structured alternates for any removed collisions
        if ask_slope:
            alternates = [_fmt(Fraction(m.denominator, m.numerator)),  # reciprocal
                          _fmt(-b), _fmt(m + 1)]
        else:
            alternates = [_fmt(Fraction(b.denominator, b.numerator)),  # reciprocal
                          _fmt(-m), _fmt(b + 1)]
        for a in alternates:
            if len(unique) >= 3:
                break
            if a not in seen:
                seen.add(a)
                unique.append(a)
        while len(unique) < 3:
            v = Fraction(rng.randint(1, 12)) * rng.choice([1, -1])
            s = _fmt(v)
            if s not in seen:
                seen.add(s)
                unique.append(s)
        distractors = unique[:3]

        stem_text = question

        choices = shuffle_choices(correct, correct, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        if ask_slope:
            worked = f"In y = mx + b, m is the slope. Here m = {_fmt(m)}."
        else:
            worked = f"In y = mx + b, b is the y-intercept. Here b = {_fmt(b)}."

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
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Approaching - MC (DOK 1, Medium)
    # Which function is nonlinear?
    # ================================================================

    def stem2_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        # Generate 1 nonlinear and 3 UNIQUE linear equations
        nonlinear_eq = _make_nonlinear_eq(rng)

        linear_eqs = []
        seen = {nonlinear_eq}
        while len(linear_eqs) < 3:
            m = Fraction(rng.randint(1, 6)) * rng.choice([1, -1])
            b = Fraction(rng.randint(1, 10)) * rng.choice([1, -1])
            eq = _fmt_eq(m, b)
            if eq not in seen:
                seen.add(eq)
                linear_eqs.append(eq)

        stem_text = "Which function is nonlinear?"

        choices = shuffle_choices(nonlinear_eq, nonlinear_eq, linear_eqs, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"Linear functions have the form y = mx + b with no exponents on x.\n"
            f"{nonlinear_eq} is nonlinear because it contains x^2, x^3, 1/x, or 2^x."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.MEDIUM, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{correct_letter}) {nonlinear_eq}",
            answer_latex=f"{correct_letter}) {nonlinear_eq}",
            worked_solution=worked, choices=choices,
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: At - MC (DOK 2, Medium)
    # Table: is the function linear or nonlinear?
    # ================================================================

    def stem3_at_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        is_linear = rng.random() < 0.5

        if is_linear:
            m = Fraction(rng.randint(1, 5)) * rng.choice([1, -1])
            b = Fraction(rng.randint(0, 8))
            rows = _make_linear_table(rng, m, b, consecutive=True)
            correct = "Linear"
            explanation = f"The rate of change is constant: {_fmt(m)} for every unit increase in x."
        else:
            kind = rng.choice(["quadratic", "doubling"])
            rows = _make_nonlinear_table(rng, kind)
            correct = "Nonlinear"
            # Compute first differences to show they vary
            diffs = [rows[i][1] - rows[i - 1][1] for i in range(1, len(rows))]
            explanation = f"The rate of change is not constant. Consecutive y-differences: {', '.join(_fmt(d) for d in diffs)}."

        distractors = ["Nonlinear" if correct == "Linear" else "Linear",
                       "Cannot be determined from the table",
                       "Neither linear nor nonlinear"]

        table_render = {
            "type": "data_table",
            "headers": ["x", "y"],
            "rows": [[_fmt(x), _fmt(y)] for x, y in rows],
            "orientation": "vertical",
        }

        stem_text = "A table of values is given.\n\nIs the function represented by the table linear or nonlinear?"

        choices = shuffle_choices(correct, correct, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = f"Check the rate of change between consecutive points.\n{explanation}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MC,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct}",
            answer_latex=f"{correct_letter}) {correct}",
            worked_solution=worked, choices=choices,
            render_data=table_render,
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At - MS (DOK 2, Medium)
    # Classify multiple functions as linear or nonlinear.
    # ================================================================

    def stem4_at_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        # Generate 5 UNIQUE functions: mix of linear and nonlinear
        functions = []
        seen = set()
        # 2-3 linear
        n_linear = rng.randint(2, 3)
        while len(functions) < n_linear:
            m = Fraction(rng.randint(1, 6)) * rng.choice([1, -1])
            b = Fraction(rng.randint(1, 10)) * rng.choice([1, -1])
            eq = _fmt_eq(m, b)
            if eq not in seen:
                seen.add(eq)
                functions.append((eq, True))

        # Rest nonlinear
        while len(functions) < 5:
            eq = _make_nonlinear_eq(rng)
            if eq not in seen:
                seen.add(eq)
                functions.append((eq, False))

        rng.shuffle(functions)

        keys = "abcde"
        choices = []
        correct_keys = []
        for i, (eq_str, is_lin) in enumerate(functions):
            choices.append(QuestionChoice(
                key=keys[i], text=eq_str, text_latex=eq_str,
                is_correct=is_lin,
            ))
            if is_lin:
                correct_keys.append(keys[i])

        correct_str = ", ".join(correct_keys)

        stem_text = "Select ALL the functions that are linear."

        worked_parts = []
        for eq_str, is_lin in functions:
            label = "linear" if is_lin else "nonlinear"
            worked_parts.append(f"{eq_str} -> {label}")
        worked = "\n".join(worked_parts)

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MS,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MS,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_str, answer_latex=correct_str,
            worked_solution=worked, choices=choices,
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above - MP (DOK 3, Easy)
    # Real-world: linear or nonlinear? Explain.
    # ================================================================

    def stem5_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)
        name = pick_name(rng)

        scenarios = [
            {
                "desc": f"A regular polygon has a side length of {{s}} cm. The table shows the perimeter for polygons with different numbers of sides.",
                "is_linear": True,
                "make_rows": lambda s, rng: [(Fraction(n), Fraction(n * s)) for n in range(3, 8)],
                "reason": "The perimeter increases by a constant amount ({s} cm) for each additional side, so the relationship is linear.",
            },
            {
                "desc": f"A population of bacteria doubles every hour. The table shows the population over time.",
                "is_linear": False,
                "make_rows": lambda s, rng: [(Fraction(t), Fraction(s * (2 ** t))) for t in range(5)],
                "reason": "The population doubles each hour, so the rate of change is not constant. The relationship is nonlinear (exponential).",
            },
            {
                "desc": f"A square has side length s. The table shows the area for different side lengths.",
                "is_linear": False,
                "make_rows": lambda s, rng: [(Fraction(n), Fraction(n * n)) for n in range(1, 6)],
                "reason": "Area = s^2. The rate of change increases as s increases, so the relationship is nonlinear (quadratic).",
            },
            {
                "desc": f"{name} earns ${{s}} per hour. The table shows total earnings for different hours worked.",
                "is_linear": True,
                "make_rows": lambda s, rng: [(Fraction(h), Fraction(h * s)) for h in range(1, 6)],
                "reason": "Earnings increase by a constant ${s} for each additional hour, so the relationship is linear.",
            },
        ]

        s_val = rng.randint(3, 10)
        scenario = scenarios[variant_idx % len(scenarios)]
        desc = scenario["desc"].format(s=s_val, name=name)
        rows = scenario["make_rows"](s_val, rng)
        is_lin = scenario["is_linear"]
        reason = scenario["reason"].format(s=s_val)

        func_word = "linear" if is_lin else "nonlinear"

        table_render = {
            "type": "data_table",
            "headers": ["x", "y"],
            "rows": [[_fmt(x), _fmt(y)] for x, y in rows],
            "orientation": "vertical",
        }

        stem_text = (
            f"{desc}\n\n"
            f"Part A: Is the relationship linear or nonlinear?\n\n"
            f"Part B: Explain your reasoning using the table values."
        )

        part_a = QuestionPart(
            label="Part A",
            prompt="Is the relationship linear or nonlinear?",
            prompt_latex="Is the relationship linear or nonlinear?",
            answer=func_word.capitalize(),
            answer_latex=func_word.capitalize(),
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

        worked = f"The relationship is {func_word}. {reason}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.EASY, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.EASY, dok=3, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{func_word.capitalize()}. {reason}",
            answer_latex=f"{func_word.capitalize()}. {reason}",
            worked_solution=worked, parts=[part_a, part_b],
            render_data=table_render,
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        for stem_fn in [self.stem1_below_mc, self.stem2_approaching_mc,
                        self.stem3_at_mc, self.stem4_at_ms, self.stem5_above_mp]:
            for v in range(variants_per_stem):
                all_questions.append(stem_fn(v))
        return all_questions

    def generate_stem_variants(self, stem_index: int,
                               variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        methods = {1: self.stem1_below_mc, 2: self.stem2_approaching_mc,
                   3: self.stem3_at_mc, 4: self.stem4_at_ms, 5: self.stem5_above_mp}
        return [methods[stem_index](v) for v in range(variants_per_stem)]
