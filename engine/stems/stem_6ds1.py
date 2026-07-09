"""
Stem generator for 6.DS.1:
  Select, create, and interpret graphical representations of numerical data,
  including line plots (dot plots), histograms, and box plots.

Content Limits:
  - Positive rational numbers only
  - Line plots: decimals to hundredths, grade-level fractions
  - Box plot Q1/Q3: exclude median when calculating
  - No commas in multi-digit numbers
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: 7 or less data values, whole numbers
  Medium: 8-12 data values, simple fracs/mixed/decimals (halves/fourths)
  Difficult: 12-15 data values, complex fracs/mixed/decimals

4 Stems:
  Stem 1 (Below-MC, DOK 1):     Identify appropriate display type for given data
  Stem 2 (Approaching-NR, DOK 1): Read values from a dot plot/histogram/box plot
  Stem 3 (At-MC, DOK 2):        Interpret data displays - identify true statements
  Stem 4 (Above-MP, DOK 3):     Draw conclusions/claims supported by data evidence
"""

import random
from fractions import Fraction

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.models import (
    GeneratedQuestion, QuestionChoice, QuestionPart,
    Difficulty, ProficiencyLevel, ItemType, make_question_id
)
from engine.number_generators import NumberGenerator, five_number_summary
from engine.svg_helpers import dot_plot_svg, histogram_svg, box_plot_svg


STANDARD_CODE = "6.DS.1"
VARIANTS_PER_STEM = 20

DATA_CONTEXTS = [
    "heights of plants (inches)", "test scores", "daily temperatures (F)",
    "number of books read", "shoe sizes", "ages of students",
    "points scored per game", "hours of sleep", "distance walked (miles)",
    "weight of apples (ounces)",
]


def _fmt(val, dec=2):
    f = float(val)
    if f == int(f):
        return str(int(f))
    return f"{f:.{dec}f}".rstrip('0').rstrip('.')


class Stem6DS1:
    """Generates 20 variants for each of 4 stems from the 6.DS.1 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx, variant_idx):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    def _make_dataset(self, rng, gen, difficulty):
        """Generate a dataset appropriate for the difficulty tier."""
        if difficulty == "easy":
            n = rng.randint(5, 7)
            data = gen.generate_dataset(n, 1, 15)
        elif difficulty == "medium":
            n = rng.randint(8, 12)
            data = gen.generate_dataset(n, 1, 25)
        else:
            n = rng.randint(12, 15)
            data = gen.generate_dataset(n, 1, 30)
        return data

    # ----------------------------------------------------------------
    # Stem 1: Below – Identify appropriate display type (MC, DOK 1)
    # ----------------------------------------------------------------
    def _stem1(self, variant_idx):
        gen, rng = self._make_gen(1, variant_idx)
        context = rng.choice(DATA_CONTEXTS)
        data = self._make_dataset(rng, gen, "easy")

        # Randomly pick what the correct display should be
        display_type = rng.choice(["dot plot", "histogram", "box plot"])

        if display_type == "dot plot":
            rationale = "A dot plot shows individual data values and is best for small datasets."
        elif display_type == "histogram":
            rationale = "A histogram groups data into intervals and shows frequency distribution."
        else:
            rationale = "A box plot summarizes data using the five-number summary."

        data_str = ", ".join(str(d) for d in data)
        stem = (f"The following data represents {context}: {data_str}. "
                f"A student wants to see the shape of the distribution. "
                f"Which type of display would be most appropriate for this data?")

        if display_type == "dot plot":
            correct = "Dot plot (line plot)"
            wrong = ["Bar graph", "Circle graph", "Stem-and-leaf plot"]
        elif display_type == "histogram":
            correct = "Histogram"
            wrong = ["Circle graph", "Bar graph", "Stem-and-leaf plot"]
        else:
            correct = "Box plot"
            wrong = ["Circle graph", "Bar graph", "Stem-and-leaf plot"]

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
            worked_solution=rationale,
            choices=choices,
            seed=gen.seed, stem_index=1, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 2: Approaching – Read values from a display (NR, DOK 1)
    # ----------------------------------------------------------------
    def _stem2(self, variant_idx):
        gen, rng = self._make_gen(2, variant_idx)
        context = rng.choice(DATA_CONTEXTS)
        data = self._make_dataset(rng, gen, "easy")

        # Choose display type and question
        display_choice = rng.choice(["dot_plot", "histogram", "box_plot"])

        if display_choice == "dot_plot":
            svg = dot_plot_svg(data, context.split('(')[0].strip(),
                               min(data), max(data))
            from collections import Counter
            counts = Counter(data)
            # Ask: how many data points have value X?
            target = rng.choice(list(counts.keys()))
            answer = counts[target]
            question = f"How many data points have a value of {target}?"
            worked = f"Count the dots above {target}: there are {answer}."

        elif display_choice == "histogram":
            # Create bins
            lo, hi = min(data), max(data)
            bin_width = max(1, (hi - lo) // 4)
            bins = list(range(lo, hi + bin_width + 1, bin_width))
            freqs = []
            for i in range(len(bins) - 1):
                count = sum(1 for d in data if bins[i] <= d < bins[i + 1])
                if i == len(bins) - 2:
                    count = sum(1 for d in data if bins[i] <= d <= bins[i + 1])
                freqs.append(count)
            svg = histogram_svg(bins, freqs, context.split('(')[0].strip(), "Frequency")
            # Ask: how many values in a specific bin?
            bin_idx = rng.randint(0, len(freqs) - 1)
            answer = freqs[bin_idx]
            question = f"How many values are in the interval {bins[bin_idx]} to {bins[bin_idx+1]}?"
            worked = f"The bar for {bins[bin_idx]}-{bins[bin_idx+1]} shows a frequency of {answer}."

        else:
            fns = five_number_summary(data)
            svg = box_plot_svg([fns], [context.split('(')[0].strip()],
                               x_min=fns[0] - 1, x_max=fns[4] + 1)
            # Ask: what is the median?
            answer = fns[2]
            question = "What is the median of the data shown in the box plot?"
            worked = f"The line inside the box represents the median: {_fmt(answer)}."

        stem = (f"The {display_choice.replace('_', ' ')} below shows {context}. "
                f"[FIGURE] {question}")

        answer_str = _fmt(answer)

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING,
                                         ItemType.NR, Difficulty.EASY, 2, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.NR,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_str, answer_latex=answer_str,
            worked_solution=worked,
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=gen.seed, stem_index=2, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 3: At – Interpret data display, identify true statements (MC, DOK 2)
    # ----------------------------------------------------------------
    def _stem3(self, variant_idx):
        gen, rng = self._make_gen(3, variant_idx)
        context = rng.choice(DATA_CONTEXTS)
        data = self._make_dataset(rng, gen, "medium")
        fns = five_number_summary(data)
        mn, q1, med, q3, mx = fns
        iqr = q3 - q1
        data_range = mx - mn
        mean_val = sum(data) / len(data)

        svg = box_plot_svg([fns], [context.split('(')[0].strip()],
                           x_min=mn - 2, x_max=mx + 2)

        # Generate true/false statements
        true_statements = [
            f"The median is {_fmt(med)}.",
            f"The range of the data is {_fmt(data_range)}.",
            f"The interquartile range (IQR) is {_fmt(iqr)}.",
            f"About 50% of the data is between {_fmt(q1)} and {_fmt(q3)}.",
            f"The minimum value is {_fmt(mn)}.",
        ]
        false_statements = [
            f"The median is {_fmt(mean_val)}." if abs(mean_val - med) > 0.5 else f"The median is {_fmt(med + 3)}.",
            f"The range of the data is {_fmt(iqr)}.",
            f"The interquartile range (IQR) is {_fmt(data_range)}.",
            f"About 75% of the data is below {_fmt(q1)}.",
        ]

        correct = rng.choice(true_statements)
        wrong = rng.sample(false_statements, min(3, len(false_statements)))
        while len(wrong) < 3:
            wrong.append(f"The maximum value is {_fmt(mx + rng.randint(2, 5))}.")

        all_choices = [(correct, True)] + [(w, False) for w in wrong[:3]]
        rng.shuffle(all_choices)
        keys = "abcd"
        choices = []
        answer_key = ""
        for i, (text, is_c) in enumerate(all_choices):
            choices.append(QuestionChoice(key=keys[i], text=text, text_latex=text, is_correct=is_c))
            if is_c:
                answer_key = keys[i]

        stem = (f"The box plot below shows data for {context}. "
                f"[FIGURE] Which statement about the data is true?")

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.AT,
                                         ItemType.MC, Difficulty.MEDIUM, 3, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_key, answer_latex=answer_key,
            worked_solution=f"The correct statement is: {correct}",
            choices=choices,
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=gen.seed, stem_index=3, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 4: Above – Draw conclusions from data (MP, DOK 3)
    # ----------------------------------------------------------------
    def _stem4(self, variant_idx):
        gen, rng = self._make_gen(4, variant_idx)
        context = rng.choice(DATA_CONTEXTS)
        data = self._make_dataset(rng, gen, "medium")
        fns = five_number_summary(data)
        mn, q1, med, q3, mx = fns
        iqr = q3 - q1
        mean_val = sum(data) / len(data)

        svg = dot_plot_svg(data, context.split('(')[0].strip(),
                           min(data), max(data))

        partA_prompt = "What is the range and median of this dataset?"
        partB_prompt = "Describe what the data tells you about the spread of values. Use evidence from the display."
        data_range = mx - mn
        partA_answer = f"Range = {_fmt(data_range)}, Median = {_fmt(med)}"

        # Part B: interpretation
        if iqr > data_range * 0.5:
            partB_answer = (f"The data is spread out since the IQR ({_fmt(iqr)}) is more than "
                            f"half the range ({_fmt(data_range)}). The data values vary considerably.")
        else:
            partB_answer = (f"The middle 50% of data is relatively clustered between "
                            f"{_fmt(q1)} and {_fmt(q3)} (IQR = {_fmt(iqr)}), suggesting "
                            f"moderate consistency in the data.")

        stem = (f"The dot plot below shows data for {context} collected from "
                f"{len(data)} observations.\n\n"
                f"[FIGURE]\n\n"
                f"Part A: {partA_prompt}\n\n"
                f"Part B: {partB_prompt}")

        parts = [
            QuestionPart(
                label="Part A",
                prompt=partA_prompt, prompt_latex=partA_prompt,
                answer=partA_answer, answer_latex=partA_answer,
                item_type=ItemType.NR,
            ),
            QuestionPart(
                label="Part B",
                prompt=partB_prompt, prompt_latex=partB_prompt,
                answer=partB_answer, answer_latex=partB_answer,
                item_type=ItemType.ER,
            ),
        ]

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE,
                                         ItemType.MP, Difficulty.MEDIUM, 4, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.MEDIUM, dok=3, item_type=ItemType.MP,
            stem_text=stem, stem_latex=stem,
            answer_text=f"A: {partA_answer} B: {partB_answer}",
            answer_latex=f"A: {partA_answer} B: {partB_answer}",
            worked_solution=f"Range = {_fmt(mx)} - {_fmt(mn)} = {_fmt(data_range)}. Median = {_fmt(med)}. IQR = {_fmt(iqr)}.",
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
