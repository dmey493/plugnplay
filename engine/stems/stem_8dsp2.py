"""
Stem generator for 8.DSP.2:
  Write and use equations that model linear relationships to make predictions,
  including interpolation and extrapolation, in real-world situations involving
  bivariate measurement data. Interpret the slope and y-intercept in context.

Content Limits:
  - Rational numbers permitted
  - Linear equation MUST be in slope-intercept form
  - Line of best fit MUST be provided on scatter plots
  - Students NOT required to write the equation
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: Key values on line of best fit provided
  Medium: Key values in context of equation and graph
  Difficult: Key values may be provided for predictions

4 Stems:
  Stem 1 (Below-MC, DOK 2):       Interpret slope and y-intercept of given line
  Stem 2 (Approaching-MC, DOK 2): Interpret slope/intercept of equation in context
  Stem 3 (At-NR, DOK 2):          Use equation for interpolation/extrapolation
  Stem 4 (Above-MP, DOK 3):       Analyze/critique predictions, identify errors
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
from engine.svg_helpers import scatter_plot_svg


STANDARD_CODE = "8.DSP.2"
VARIANTS_PER_STEM = 20


# Contexts with real-world meaning for slope and intercept.
#
# Optional `y_min` and `y_max` clamp the noisy scatter points to a physically
# realistic range. Without these, the noise added to each point can push y
# below zero (e.g. battery at -3%) or above a natural ceiling (battery at
# 105%). Clamps don't affect the underlying line — only the rendered points
# stay in-bounds. Contexts where y can legitimately be any value (test
# scores can be 0-100 in theory, weight loss could be slight gain, etc.)
# omit the bounds.
LINEAR_CONTEXTS = [
    {"x": "hours studied", "y": "test score", "x_unit": "hours", "y_unit": "points",
     "desc": "hours studied vs. test scores",
     "slope_range": (2, 8), "intercept_range": (30, 60), "max_x": 15,
     "y_min": 0, "y_max": 100,
     "slope_meaning": "For each additional hour studied, the score increases by about {m} points.",
     "intercept_meaning": "A student who studies 0 hours would score about {b} points."},
    {"x": "weeks", "y": "savings ($)", "x_unit": "weeks", "y_unit": "dollars",
     "desc": "weeks vs. total savings",
     "slope_range": (5, 25), "intercept_range": (10, 50), "max_x": 30,
     "y_min": 0,
     "slope_meaning": "Each week, savings increase by about ${m}.",
     "intercept_meaning": "The starting amount of savings is about ${b}."},
    {"x": "hours of use", "y": "battery level (%)", "x_unit": "hours", "y_unit": "percent",
     "desc": "hours of use vs. battery level",
     "slope_range": (-8, -3), "intercept_range": (95, 100), "max_x": 12,
     "y_min": 0, "y_max": 100,
     "slope_meaning": "For each hour of use, the battery decreases by about {m_abs}%.",
     "intercept_meaning": "The battery starts at about {b}%."},
    {"x": "number of items", "y": "total cost ($)", "x_unit": "items", "y_unit": "dollars",
     "desc": "number of items vs. total cost",
     "slope_range": (2, 15), "intercept_range": (5, 20), "max_x": 25,
     "y_min": 0,
     "slope_meaning": "Each additional item costs about ${m}.",
     "intercept_meaning": "There is a base fee of about ${b}."},
    {"x": "months of membership", "y": "total weight lost (lb)", "x_unit": "months", "y_unit": "pounds",
     "desc": "months of membership vs. weight lost",
     "slope_range": (2, 6), "intercept_range": (0, 5), "max_x": 18,
     "slope_meaning": "Members lose about {m} pounds per month.",
     "intercept_meaning": "The initial weight loss (or gain) at the start is about {b} pounds."},
    {"x": "temperature (F)", "y": "lemonade sales", "x_unit": "degrees F", "y_unit": "cups",
     "desc": "temperature vs. lemonade sales",
     "slope_range": (1, 5), "intercept_range": (-10, 10), "max_x": 105,
     "y_min": 0,
     "slope_meaning": "For each degree increase in temperature, about {m} more cups are sold.",
     "intercept_meaning": "At 0 degrees, the model predicts {b} cups would be sold."},
]


def _fmt(val, dec=1):
    f = float(val)
    if f == int(f):
        return str(int(f))
    return f"{f:.{dec}f}".rstrip('0').rstrip('.')


class Stem8DSP2:
    """Generates 20 variants for each of 4 stems from the 8.DSP.2 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx, variant_idx):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    def _make_linear_scenario(self, rng, gen):
        """Generate a linear scenario with equation, points, and SVG.

        Care has to be taken so the generated line stays inside the context's
        physical y-bounds across the whole [1, max_x] x-domain. Without that
        guard, scenarios like y = 5x + 52 over hours studied (max_x=15) hit
        the y_max=100 ceiling around x=10 and every later point clamps flat
        to 100 — making the data look like a horizontal stack instead of a
        linear trend. Here we constrain b so the line endpoints fit, then
        the noisy scatter generally sits inside the bounds and the clamp
        only catches outliers.
        """
        ctx = rng.choice(LINEAR_CONTEXTS)
        max_x = ctx.get("max_x", 22)
        y_min = ctx.get("y_min")
        y_max = ctx.get("y_max")

        # Pick (m, b) together so the line y = m*x + b stays inside
        # [y_min, y_max] across x in [1, max_x] with room for the scatter
        # noise. For each slope candidate, compute the feasible b range;
        # collect every slope that admits a non-empty range. Sample one
        # uniformly. If none work, fall back to the smallest-magnitude
        # slope with the original b range — better to clip a few outliers
        # than to dramatically misrepresent the data.
        s_lo, s_hi = ctx["slope_range"]
        b_lo_orig, b_hi_orig = ctx["intercept_range"]

        feasible = []  # list of (m, b_lo, b_hi, noise)
        for cand in range(min(s_lo, s_hi), max(s_lo, s_hi) + 1):
            cand_noise = abs(cand) * 1.5 + 2
            cb_lo = b_lo_orig
            cb_hi = b_hi_orig
            if y_min is not None:
                cb_lo = max(cb_lo,
                            (y_min + cand_noise) - cand * 1,
                            (y_min + cand_noise) - cand * max_x)
            if y_max is not None:
                cb_hi = min(cb_hi,
                            (y_max - cand_noise) - cand * 1,
                            (y_max - cand_noise) - cand * max_x)
            if cb_lo <= cb_hi:
                feasible.append((cand, cb_lo, cb_hi, cand_noise))

        if feasible:
            m, b_lo, b_hi, noise = rng.choice(feasible)
        else:
            # Pathological context — pick smallest-|slope| and the original
            # b range; clamping will catch outliers.
            m = min(range(min(s_lo, s_hi), max(s_lo, s_hi) + 1), key=abs)
            noise = abs(m) * 1.5 + 2
            b_lo, b_hi = b_lo_orig, b_hi_orig

        b = rng.randint(int(round(max(0, b_lo))), int(round(b_hi)))

        # Generate scatter data only in the context's intended x-domain.
        points = gen.generate_bivariate_data(12, m, b, noise=noise,
                                             x_min=1, x_max=max_x)

        # Clamp any remaining noise outliers to the physical bounds.
        if y_min is not None or y_max is not None:
            clamped = []
            for x, y in points:
                if y_min is not None and y < y_min:
                    y = y_min
                if y_max is not None and y > y_max:
                    y = y_max
                clamped.append((x, y))
            points = clamped

        svg = scatter_plot_svg(points, ctx["x"], ctx["y"], line_eq=(m, b))

        slope_desc = ctx["slope_meaning"].format(m=_fmt(abs(m)), m_abs=_fmt(abs(m)))
        intercept_desc = ctx["intercept_meaning"].format(b=_fmt(b))

        return ctx, m, b, points, svg, slope_desc, intercept_desc

    # ----------------------------------------------------------------
    # Stem 1: Below – Interpret slope and y-intercept (MC, DOK 2)
    # ----------------------------------------------------------------
    def _stem1(self, variant_idx):
        gen, rng = self._make_gen(1, variant_idx)
        ctx, m, b, points, svg, slope_desc, intercept_desc = self._make_linear_scenario(rng, gen)

        ask_about = rng.choice(["slope", "intercept"])

        if ask_about == "slope":
            stem = (f"The scatter plot shows {ctx['x']} vs. {ctx['y']}. "
                    f"The line of best fit has the equation y = {_fmt(m)}x + {_fmt(b)}. "
                    f"[FIGURE] What does the slope of {_fmt(m)} mean in this context?")
            correct = slope_desc
            wrong = [
                intercept_desc,
                f"The total {ctx['y']} is {_fmt(m)} {ctx['y_unit']}.",
                f"After {_fmt(abs(m))} {ctx['x_unit']}, the {ctx['y']} reaches 0.",
            ]
        else:
            stem = (f"The scatter plot shows {ctx['x']} vs. {ctx['y']}. "
                    f"The line of best fit has the equation y = {_fmt(m)}x + {_fmt(b)}. "
                    f"[FIGURE] What does the y-intercept of {_fmt(b)} mean in this context?")
            correct = intercept_desc
            wrong = [
                slope_desc,
                f"The {ctx['y']} changes by {_fmt(b)} each {ctx['x_unit']}.",
                f"The maximum {ctx['y']} is {_fmt(b)} {ctx['y_unit']}.",
            ]

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
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_key, answer_latex=answer_key,
            worked_solution=f"Slope = rate of change; y-intercept = starting value. {correct}",
            choices=choices,
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=gen.seed, stem_index=1, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 2: Approaching – Interpret equation in context (MC, DOK 2)
    # ----------------------------------------------------------------
    def _stem2(self, variant_idx):
        gen, rng = self._make_gen(2, variant_idx)
        ctx, m, b, points, svg, slope_desc, intercept_desc = self._make_linear_scenario(rng, gen)

        eq_str = f"y = {_fmt(m)}x + {_fmt(b)}"

        stem = (f"The equation {eq_str} models the relationship between "
                f"{ctx['x']} (x) and {ctx['y']} (y). [FIGURE] "
                f"Which statement correctly interprets this equation?")

        correct = f"The slope {_fmt(m)} means: {slope_desc} The intercept {_fmt(b)} means: {intercept_desc}"

        # Truncate for MC option length
        correct_short = f"{slope_desc}"

        wrong = [
            f"The slope means the {ctx['y']} starts at {_fmt(m)} {ctx['y_unit']}.",
            f"The y-intercept means {ctx['y']} increases by {_fmt(b)} per {ctx['x_unit']}.",
            f"The equation means {ctx['x']} and {ctx['y']} are always equal.",
        ]

        all_choices = [(correct_short, True)] + [(w, False) for w in wrong]
        rng.shuffle(all_choices)
        keys = "abcd"
        choices = []
        answer_key = ""
        for i, (text, is_c) in enumerate(all_choices):
            choices.append(QuestionChoice(key=keys[i], text=text, text_latex=text, is_correct=is_c))
            if is_c:
                answer_key = keys[i]

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING,
                                         ItemType.MC, Difficulty.MEDIUM, 2, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_key, answer_latex=answer_key,
            worked_solution=f"{eq_str}: slope = {slope_desc}, intercept = {intercept_desc}",
            choices=choices,
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=gen.seed, stem_index=2, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 3: At – Interpolation/extrapolation prediction (MP, DOK 2)
    # Part A: Use the equation to predict y for a given x
    # Part B: Identify whether it's interpolation or extrapolation
    # ----------------------------------------------------------------
    def _stem3(self, variant_idx):
        gen, rng = self._make_gen(3, variant_idx)
        ctx, m, b, points, svg, _, _ = self._make_linear_scenario(rng, gen)

        eq_str = f"y = {_fmt(m)}x + {_fmt(b)}"
        x_vals = [p[0] for p in points]

        # Choose interpolation or extrapolation
        max_x = ctx.get("max_x", max(x_vals) + 10)
        is_interp = rng.random() < 0.5
        if is_interp:
            x_val = rng.randint(min(x_vals) + 1, max(x_vals) - 1)
            pred_type = "interpolation"
            pred_reason = (f"This is interpolation because x = {x_val} is within "
                          f"the data range ({min(x_vals)} to {max(x_vals)}).")
        else:
            x_val = min(max(x_vals) + rng.randint(2, 5), max_x)
            pred_type = "extrapolation"
            pred_reason = (f"This is extrapolation because x = {x_val} is beyond "
                          f"the data range ({min(x_vals)} to {max(x_vals)}).")

        y_pred = m * x_val + b
        answer_str = _fmt(round(y_pred, 1), 1)

        partA_prompt = (f"Using the equation, predict the {ctx['y']} when "
                       f"{ctx['x']} = {x_val}. Round to the nearest tenth.")
        partA_answer = answer_str

        partB_prompt = "Is this prediction an example of interpolation or extrapolation? Explain."
        partB_answer = pred_reason

        stem = (f"The equation {eq_str} models {ctx['desc']} for data between "
                f"x = {min(x_vals)} and x = {max(x_vals)}.\n\n"
                f"[FIGURE]\n\n"
                f"Part A: {partA_prompt}\n\n"
                f"Part B: {partB_prompt}")

        parts = [
            QuestionPart(
                label="Part A", prompt=partA_prompt, prompt_latex=partA_prompt,
                answer=partA_answer, answer_latex=partA_answer, item_type=ItemType.NR,
            ),
            QuestionPart(
                label="Part B", prompt=partB_prompt, prompt_latex=partB_prompt,
                answer=partB_answer, answer_latex=partB_answer, item_type=ItemType.ER,
            ),
        ]

        worked = (f"Part A: y = {_fmt(m)} * {x_val} + {_fmt(b)} = "
                  f"{_fmt(m * x_val)} + {_fmt(b)} = {answer_str}\n"
                  f"Part B: {pred_reason}")

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.AT,
                                         ItemType.MP, Difficulty.MEDIUM, 3, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MP,
            stem_text=stem, stem_latex=stem,
            answer_text=f"A: {answer_str}; B: {pred_reason}",
            answer_latex=f"A: {answer_str}; B: {pred_reason}",
            worked_solution=worked,
            parts=parts,
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=gen.seed, stem_index=3, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 4: Above – Analyze/critique predictions (MP, DOK 3)
    # ----------------------------------------------------------------
    def _stem4(self, variant_idx):
        gen, rng = self._make_gen(4, variant_idx)
        ctx, m, b, points, svg, slope_desc, intercept_desc = self._make_linear_scenario(rng, gen)

        eq_str = f"y = {_fmt(m)}x + {_fmt(b)}"
        x_vals = [p[0] for p in points]
        max_x = ctx.get("max_x", max(x_vals) + 30)

        # Extrapolation prediction (far enough to be unreliable, but not absurd)
        x_far = min(max(x_vals) + rng.randint(10, 20), max_x + 10)
        y_pred = m * x_far + b

        partA_prompt = "Is this prediction reliable? Explain why or why not."
        partA_answer = (f"This prediction uses extrapolation far beyond the data range "
                        f"(data goes up to {max(x_vals)}, but prediction is at {x_far}). "
                        f"Extrapolation is less reliable because the linear trend "
                        f"may not continue.")

        partB_prompt = f"Would a prediction at {ctx['x']} = {rng.randint(min(x_vals)+1, max(x_vals)-1)} be more reliable? Explain."
        partB_answer = (f"Yes, interpolation (predicting within the data range) is more "
                        f"reliable because we have evidence the linear pattern holds there.")

        stem = (f"The equation {eq_str} models {ctx['desc']} for data between "
                f"x = {min(x_vals)} and x = {max(x_vals)}.\n\n"
                f"[FIGURE]\n\n"
                f"A student predicts that when {ctx['x']} = {x_far}, "
                f"{ctx['y']} will be {_fmt(round(y_pred, 1), 1)}.\n\n"
                f"Part A: {partA_prompt}\n\n"
                f"Part B: {partB_prompt}")

        parts = [
            QuestionPart(
                label="Part A", prompt=partA_prompt, prompt_latex=partA_prompt,
                answer=partA_answer, answer_latex=partA_answer, item_type=ItemType.ER,
            ),
            QuestionPart(
                label="Part B", prompt=partB_prompt, prompt_latex=partB_prompt,
                answer=partB_answer, answer_latex=partB_answer, item_type=ItemType.ER,
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
            worked_solution="Extrapolation far beyond data is unreliable. Interpolation is more reliable.",
            parts=parts,
            render_data={"svg_html": svg, "type": "svg_html"},
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
