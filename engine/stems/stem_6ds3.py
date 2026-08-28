"""
Stem generator for 6.DS.3:
  Summarize numerical data sets in relation to their context in multiple ways:
  number of observations, measures of center (mean, median), measures of spread
  (range, IQR), overall patterns (clusters, peaks, gaps, outliers).

Content Limits:
  - Positive rational numbers
  - One set of data or one graphical representation
  - No mean absolute deviation
  - Box plot Q1/Q3: exclude median
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: 7 or fewer values, whole numbers
  Medium: 8-12 values, simple fracs/decimals (halves/fourths)
  Difficult: 12-15 values, complex fracs/decimals

4 Stems:
  Stem 1 (Below-MC, DOK 1):     Calculate mean, median, range; identify best measure
  Stem 2 (Approaching-NR, DOK 1-2): Calculate IQR; determine observations between intervals
  Stem 3 (At-MC, DOK 2):        Describe patterns; how outliers affect mean/median
  Stem 4 (Above-MP, DOK 2-3):   How measures change when data added; create dataset
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
from engine.svg_helpers import dot_plot_svg, box_plot_svg
from engine.stem_guards import distinct_choices


STANDARD_CODE = "6.DS.3"
VARIANTS_PER_STEM = 20

DATA_CONTEXTS = [
    "quiz scores", "daily high temperatures (F)", "number of pushups",
    "hours spent studying", "ages of club members", "points scored per game",
    "heights of seedlings (cm)", "weights of fish caught (lb)",
    "number of pages read per day", "distances jogged (miles)",
]


def _fmt(val, dec=2):
    f = float(val)
    if f == int(f):
        return str(int(f))
    return f"{f:.{dec}f}".rstrip('0').rstrip('.')


def _mean(data):
    return sum(data) / len(data)


def _median(data):
    s = sorted(data)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2


class Stem6DS3:
    """Generates 20 variants for each of 4 stems from the 6.DS.3 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx, variant_idx):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    def _make_dataset(self, gen, rng, difficulty):
        if difficulty == "easy":
            n = rng.randint(5, 7)
            return gen.generate_dataset(n, 2, 20)
        elif difficulty == "medium":
            n = rng.randint(8, 12)
            return gen.generate_dataset(n, 1, 30)
        else:
            n = rng.randint(12, 15)
            return gen.generate_dataset(n, 1, 40)

    # ----------------------------------------------------------------
    # Stem 1: Below – Calculate mean, median, range (MC, DOK 1)
    # ----------------------------------------------------------------
    @distinct_choices
    def _stem1(self, variant_idx):
        gen, rng = self._make_gen(1, variant_idx)
        context = rng.choice(DATA_CONTEXTS)
        data = self._make_dataset(gen, rng, "easy")

        # Ask for one of: mean, median, or range
        measure = rng.choice(["mean", "median", "range"])

        data_str = ", ".join(str(d) for d in data)

        if measure == "mean":
            answer_val = _mean(data)
            stem = f"Find the mean of the following {context}: {data_str}."
            worked = f"Mean = ({' + '.join(str(d) for d in data)}) / {len(data)} = {_fmt(answer_val)}"
        elif measure == "median":
            answer_val = _median(data)
            stem = f"Find the median of the following {context}: {data_str}."
            worked = f"Sorted: {', '.join(str(d) for d in sorted(data))}. Middle value = {_fmt(answer_val)}"
        else:
            answer_val = max(data) - min(data)
            stem = f"Find the range of the following {context}: {data_str}."
            worked = f"Range = {max(data)} - {min(data)} = {_fmt(answer_val)}"

        answer_str = _fmt(answer_val)

        # Distractors
        mean_v = _mean(data)
        med_v = _median(data)
        range_v = max(data) - min(data)
        all_vals = {_fmt(mean_v), _fmt(med_v), _fmt(range_v)}
        all_vals.add(_fmt(answer_val + rng.choice([1, 2, -1])))
        all_vals.discard(answer_str)
        wrong = list(all_vals)[:3]
        while len(wrong) < 3:
            wrong.append(_fmt(answer_val + rng.randint(2, 5)))

        all_choices = [(answer_str, True)] + [(w, False) for w in wrong[:3]]
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
            worked_solution=worked,
            choices=choices,
            seed=gen.seed, stem_index=1, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 2: Approaching – Calculate IQR (NR, DOK 1-2)
    # ----------------------------------------------------------------
    def _stem2(self, variant_idx):
        gen, rng = self._make_gen(2, variant_idx)
        context = rng.choice(DATA_CONTEXTS)
        data = self._make_dataset(gen, rng, "medium")
        fns = five_number_summary(data)
        mn, q1, med, q3, mx = fns
        iqr = q3 - q1

        # Show as box plot
        svg = box_plot_svg([fns], [context.split('(')[0].strip()],
                           x_min=mn - 2, x_max=mx + 2)

        stem = (f"The box plot below shows {context} for a group of students. "
                f"[FIGURE] What is the interquartile range (IQR) of the data?")

        answer_str = _fmt(iqr)
        worked = f"IQR = Q3 - Q1 = {_fmt(q3)} - {_fmt(q1)} = {answer_str}"

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING,
                                         ItemType.NR, Difficulty.MEDIUM, 2, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_str, answer_latex=answer_str,
            worked_solution=worked,
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=gen.seed, stem_index=2, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 3: At – Describe patterns, outlier effects (MC, DOK 2)
    # ----------------------------------------------------------------
    def _stem3(self, variant_idx):
        gen, rng = self._make_gen(3, variant_idx)
        context = rng.choice(DATA_CONTEXTS)
        data = self._make_dataset(gen, rng, "medium")

        # Add an outlier to some variants
        has_outlier = rng.choice([True, False])
        if has_outlier:
            outlier = max(data) + rng.randint(15, 30)
            data_with_outlier = sorted(data + [outlier])
            mean_before = _mean(data)
            median_before = _median(data)
            mean_after = _mean(data_with_outlier)
            median_after = _median(data_with_outlier)
        else:
            data_with_outlier = data

        svg = dot_plot_svg(data_with_outlier, context.split('(')[0].strip(),
                           min(data_with_outlier), max(data_with_outlier))

        if has_outlier:
            stem = (f"The dot plot shows {context}. [FIGURE] "
                    f"How does the outlier at {outlier} affect the mean compared to the median?")
            correct = (f"The outlier increases the mean more than the median. "
                       f"Mean changes from {_fmt(mean_before)} to {_fmt(mean_after)}, "
                       f"while median changes less.")
            wrong = [
                "The outlier affects the median more than the mean.",
                "The outlier has no effect on either measure.",
                "The outlier decreases both the mean and the median.",
            ]
        else:
            # Ask about distribution shape
            from collections import Counter
            counts = Counter(data)
            mode_val = max(counts, key=counts.get)
            mean_val = _mean(data)
            med_val = _median(data)

            stem = (f"The dot plot shows {context}. [FIGURE] "
                    f"Which statement best describes the distribution?")

            if mean_val > med_val + 1:
                correct = "The data is skewed right (the mean is greater than the median)."
                wrong = [
                    "The data is symmetric.",
                    "The data is skewed left.",
                    "The data has no pattern.",
                ]
            elif mean_val < med_val - 1:
                correct = "The data is skewed left (the mean is less than the median)."
                wrong = [
                    "The data is symmetric.",
                    "The data is skewed right.",
                    "The data has no pattern.",
                ]
            else:
                correct = "The data is approximately symmetric (the mean and median are close)."
                wrong = [
                    "The data is strongly skewed right.",
                    "The data is strongly skewed left.",
                    "The data has multiple peaks with no central tendency.",
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
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.AT,
                                         ItemType.MC, Difficulty.MEDIUM, 3, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_key, answer_latex=answer_key,
            worked_solution=correct,
            choices=choices,
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=gen.seed, stem_index=3, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 4: Above – How measures change with new data point (MP, DOK 2-3)
    # ----------------------------------------------------------------
    def _stem4(self, variant_idx):
        gen, rng = self._make_gen(4, variant_idx)
        context = rng.choice(DATA_CONTEXTS)
        data = self._make_dataset(gen, rng, "medium")

        mean_before = _mean(data)
        median_before = _median(data)
        range_before = max(data) - min(data)

        # Add a new data point
        new_point = rng.choice([
            max(data) + rng.randint(10, 20),  # high outlier
            min(data) - rng.randint(1, min(data) - 1) if min(data) > 2 else 1,  # low value
            round(mean_before),  # near mean
        ])

        new_data = sorted(data + [new_point])
        mean_after = _mean(new_data)
        median_after = _median(new_data)
        range_after = max(new_data) - min(new_data)

        data_str = ", ".join(str(d) for d in data)

        partA_prompt = f"How does the mean change when {new_point} is added?"
        if mean_after > mean_before:
            partA_answer = f"The mean increases from {_fmt(mean_before)} to {_fmt(mean_after)}."
        elif mean_after < mean_before:
            partA_answer = f"The mean decreases from {_fmt(mean_before)} to {_fmt(mean_after)}."
        else:
            partA_answer = f"The mean stays approximately the same at {_fmt(mean_before)}."

        partB_prompt = f"How does the median change when {new_point} is added?"
        if median_after > median_before:
            partB_answer = f"The median increases from {_fmt(median_before)} to {_fmt(median_after)}."
        elif median_after < median_before:
            partB_answer = f"The median decreases from {_fmt(median_before)} to {_fmt(median_after)}."
        else:
            partB_answer = f"The median stays the same at {_fmt(median_before)}."

        stem = (f"A dataset of {context} contains the values: {data_str}. "
                f"A new value of {new_point} is added to the dataset.\n\n"
                f"Part A: {partA_prompt}\n\n"
                f"Part B: {partB_prompt}")

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
                                         ItemType.MP, Difficulty.MEDIUM, 4, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.MEDIUM, dok=3, item_type=ItemType.MP,
            stem_text=stem, stem_latex=stem,
            answer_text=f"A: {partA_answer} B: {partB_answer}",
            answer_latex=f"A: {partA_answer} B: {partB_answer}",
            worked_solution=f"Before: mean={_fmt(mean_before)}, median={_fmt(median_before)}. After adding {new_point}: mean={_fmt(mean_after)}, median={_fmt(median_after)}.",
            parts=parts,
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
