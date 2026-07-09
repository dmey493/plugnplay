"""
Stem generator for 8.DSP.1:
  Construct and interpret scatter plots for bivariate measurement data to
  investigate patterns of association. Describe patterns such as clustering,
  outliers, positive/negative association, linear/nonlinear association.

Content Limits:
  - Associations must be visually obvious
  - One dataset per graph
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: Only shape of data considered
  Medium: Shape AND quantitative variables considered
  Difficult: Shape, variables, AND value of data points considered

4 Stems:
  Stem 1 (Below-MC, DOK 1):       Identify positive/negative/no association
  Stem 2 (Approaching-MC, DOK 1): Identify multiple characteristics
  Stem 3 (At-MC, DOK 2):          Interpret scatter plot in context
  Stem 4 (Above-MP, DOK 3):       Justify/critique inferences about associations
"""

import random
import math

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.models import (
    GeneratedQuestion, QuestionChoice, QuestionPart,
    Difficulty, ProficiencyLevel, ItemType, make_question_id
)
from engine.number_generators import NumberGenerator
from engine.svg_helpers import scatter_plot_svg


STANDARD_CODE = "8.DSP.1"
VARIANTS_PER_STEM = 20


SCATTER_CONTEXTS = [
    {"x_label": "Hours Studied", "y_label": "Test Score",
     "assoc": "positive", "linear": True,
     "desc": "hours studied vs. test scores for students"},
    {"x_label": "Temperature (F)", "y_label": "Hot Chocolate Sales",
     "assoc": "negative", "linear": True,
     "desc": "daily temperature vs. hot chocolate sales"},
    {"x_label": "Age (years)", "y_label": "Height (inches)",
     "assoc": "positive", "linear": True,
     "desc": "age vs. height for teenagers"},
    {"x_label": "Miles Driven", "y_label": "Gas Remaining (gal)",
     "assoc": "negative", "linear": True,
     "desc": "miles driven vs. gallons of gas remaining"},
    {"x_label": "Study Time (min)", "y_label": "Number of Errors",
     "assoc": "negative", "linear": True,
     "desc": "study time vs. number of errors on a quiz"},
    {"x_label": "Practice Hours", "y_label": "Free Throw %",
     "assoc": "positive", "linear": True,
     "desc": "practice hours vs. free throw percentage"},
    {"x_label": "Shoe Size", "y_label": "Math Score",
     "assoc": "none", "linear": False,
     "desc": "shoe size vs. math test score"},
    {"x_label": "Number of Pets", "y_label": "Favorite Color (code)",
     "assoc": "none", "linear": False,
     "desc": "number of pets vs. favorite color code"},
]


def _generate_scatter_data(rng, assoc, linear, n=15):
    """Generate scatter plot data with specified association pattern."""
    points = []
    if assoc == "positive" and linear:
        slope = rng.uniform(1.5, 4.0)
        intercept = rng.uniform(10, 30)
        for _ in range(n):
            x = rng.randint(1, 20)
            noise = rng.uniform(-5, 5)
            y = max(1, round(slope * x + intercept + noise))
            points.append((x, y))
    elif assoc == "negative" and linear:
        slope = rng.uniform(-4.0, -1.5)
        intercept = rng.uniform(50, 80)
        for _ in range(n):
            x = rng.randint(1, 20)
            noise = rng.uniform(-5, 5)
            y = max(1, round(slope * x + intercept + noise))
            points.append((x, y))
    else:  # no association
        for _ in range(n):
            x = rng.randint(1, 20)
            y = rng.randint(10, 50)
            points.append((x, y))
    return sorted(points, key=lambda p: p[0])


class Stem8DSP1:
    """Generates 20 variants for each of 4 stems from the 8.DSP.1 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx, variant_idx):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ----------------------------------------------------------------
    # Stem 1: Below – Identify association type (MC, DOK 1)
    # ----------------------------------------------------------------
    def _stem1(self, variant_idx):
        gen, rng = self._make_gen(1, variant_idx)
        ctx = rng.choice(SCATTER_CONTEXTS)
        points = _generate_scatter_data(rng, ctx["assoc"], ctx["linear"])
        svg = scatter_plot_svg(points, ctx["x_label"], ctx["y_label"])

        stem = (f"The scatter plot below shows {ctx['desc']}. [FIGURE] "
                f"What type of association does the scatter plot show?")

        assoc = ctx["assoc"]
        if assoc == "positive":
            correct = "Positive association - as one variable increases, the other also increases."
        elif assoc == "negative":
            correct = "Negative association - as one variable increases, the other decreases."
        else:
            correct = "No association - there is no clear pattern between the variables."

        options = [
            "Positive association - as one variable increases, the other also increases.",
            "Negative association - as one variable increases, the other decreases.",
            "No association - there is no clear pattern between the variables.",
            "Nonlinear association - the data follows a curved pattern.",
        ]
        wrong = [o for o in options if o != correct][:3]

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
            worked_solution=f"The scatter plot shows a {assoc} association.",
            choices=choices,
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=gen.seed, stem_index=1, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 2: Approaching – Identify multiple characteristics (MC, DOK 1)
    # ----------------------------------------------------------------
    def _stem2(self, variant_idx):
        gen, rng = self._make_gen(2, variant_idx)

        # Use a context with clear linear association + add an outlier
        ctx_pool = [c for c in SCATTER_CONTEXTS if c["linear"]]
        ctx = rng.choice(ctx_pool)
        points = _generate_scatter_data(rng, ctx["assoc"], True, n=12)

        # Add an outlier
        if ctx["assoc"] == "positive":
            outlier = (rng.randint(15, 20), rng.randint(5, 15))  # low y for high x
        else:
            outlier = (rng.randint(1, 5), rng.randint(5, 15))  # low y for low x
        points.append(outlier)
        points.sort(key=lambda p: p[0])

        svg = scatter_plot_svg(points, ctx["x_label"], ctx["y_label"])

        stem = (f"The scatter plot shows {ctx['desc']}. [FIGURE] "
                f"Which TWO characteristics best describe this scatter plot?")

        assoc_word = ctx["assoc"]
        correct = f"The data shows a {assoc_word}, linear association with an outlier."
        wrong = [
            f"The data shows a {'negative' if assoc_word == 'positive' else 'positive'}, linear association with no outliers.",
            f"The data shows no association with several outliers.",
            f"The data shows a nonlinear association with clustering.",
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
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING,
                                         ItemType.MC, Difficulty.MEDIUM, 2, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.MC,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_key, answer_latex=answer_key,
            worked_solution=f"The data trends {'upward' if assoc_word == 'positive' else 'downward'} linearly with one outlier at {outlier}.",
            choices=choices,
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=gen.seed, stem_index=2, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 3: At – Describe patterns in context (MP, DOK 2)
    # Part A: Identify the type of association
    # Part B: Describe the pattern in context and note any outliers
    # ----------------------------------------------------------------
    def _stem3(self, variant_idx):
        gen, rng = self._make_gen(3, variant_idx)
        ctx_pool = [c for c in SCATTER_CONTEXTS if c["assoc"] != "none"]
        ctx = rng.choice(ctx_pool)
        points = _generate_scatter_data(rng, ctx["assoc"], ctx["linear"], n=12)

        assoc = ctx["assoc"]
        x_lab = ctx["x_label"].lower()
        y_lab = ctx["y_label"].lower()

        # Add an outlier to make the question richer
        if assoc == "positive":
            outlier = (rng.randint(15, 20), rng.randint(5, 15))
        else:
            outlier = (rng.randint(1, 5), rng.randint(5, 15))
        points.append(outlier)
        points.sort(key=lambda p: p[0])

        svg = scatter_plot_svg(points, ctx["x_label"], ctx["y_label"])

        partA_prompt = "What type of association does the scatter plot show (positive, negative, or none)?"
        partA_answer = f"The scatter plot shows a {assoc} association."

        if assoc == "positive":
            partB_answer = (f"As {x_lab} increases, {y_lab} also increases. "
                           f"The association is linear with one outlier near {outlier}.")
        else:
            partB_answer = (f"As {x_lab} increases, {y_lab} decreases. "
                           f"The association is linear with one outlier near {outlier}.")
        partB_prompt = "Describe the pattern in context and identify any outliers."

        # Stem text includes only the figure — the Part A / Part B prompts
        # live in the `parts` array below and the PDF renderer expands them
        # under the figure. Including them inline too made the prompts
        # appear twice (once above the figure, once below).
        stem = f"The scatter plot shows {ctx['desc']}.\n\n[FIGURE]"

        parts = [
            QuestionPart(
                label="Part A", prompt=partA_prompt, prompt_latex=partA_prompt,
                answer=partA_answer, answer_latex=partA_answer, item_type=ItemType.MC,
            ),
            QuestionPart(
                label="Part B", prompt=partB_prompt, prompt_latex=partB_prompt,
                answer=partB_answer, answer_latex=partB_answer, item_type=ItemType.ER,
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
            worked_solution=(f"The data trends {'upward' if assoc == 'positive' else 'downward'} "
                             f"linearly ({assoc} association) with one outlier near {outlier}."),
            parts=parts,
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=gen.seed, stem_index=3, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 4: Above – Justify/critique inferences (MP, DOK 3)
    # ----------------------------------------------------------------
    def _stem4(self, variant_idx):
        gen, rng = self._make_gen(4, variant_idx)
        ctx_pool = [c for c in SCATTER_CONTEXTS if c["assoc"] != "none"]
        ctx = rng.choice(ctx_pool)
        points = _generate_scatter_data(rng, ctx["assoc"], ctx["linear"])
        svg = scatter_plot_svg(points, ctx["x_label"], ctx["y_label"])

        x_lab = ctx["x_label"].lower()
        y_lab = ctx["y_label"].lower()
        assoc = ctx["assoc"]

        # Present a causal claim to critique
        if assoc == "positive":
            claim = f"Increasing {x_lab} causes {y_lab} to increase."
        else:
            claim = f"Increasing {x_lab} causes {y_lab} to decrease."

        partA_prompt = "Does the scatter plot support a causal relationship? Explain."
        partA_answer = (f"No. The scatter plot shows a {assoc} association (correlation), "
                        f"but correlation does not prove causation. There may be other "
                        f"factors (confounding variables) that influence both variables.")

        partB_prompt = "What type of association does the data show? Describe the pattern."
        if assoc == "positive":
            partB_answer = (f"The data shows a positive, linear association. "
                            f"As {x_lab} increases, {y_lab} generally increases too.")
        else:
            partB_answer = (f"The data shows a negative, linear association. "
                            f"As {x_lab} increases, {y_lab} generally decreases.")

        # The student claim stays in the stem (it's setup that both parts
        # respond to), but the Part A / Part B prompts are dropped from the
        # stem text — they're already in the `parts` array, and including
        # them inline causes them to render twice.
        stem = (f"The scatter plot shows {ctx['desc']}.\n\n"
                f"[FIGURE]\n\n"
                f"A student claims: \"{claim}\"")

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
            worked_solution="Correlation does not imply causation.",
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
