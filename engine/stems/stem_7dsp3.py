"""
Stem generator for 7.DSP.3:
  Make observations about the degree of visual overlap of two numerical data
  distributions represented in line plots or box plots. Describe how data,
  particularly outliers, added to a data set may affect the mean and/or median.

Content Limits:
  - Data displayed as line plots (dot plots) or box plots
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: Same mean but different variations, 0-5 values, no computation
  Medium: Same variation but different means, 6-15 values
  Difficult: Different means AND variations, 16+ values

4 Stems:
  Stem 1 (Below-MC, DOK 2):     Classify overlap as full, partial, or none
  Stem 2 (Approaching-MC, DOK 2): Analyze overlap using measures on box plots
  Stem 3 (At-MC, DOK 2):        Analyze overlap; describe outlier effects
  Stem 4 (Above-MC, DOK 3):     Justify/critique comparative inferences
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


STANDARD_CODE = "7.DSP.3"
VARIANTS_PER_STEM = 20


CONTEXTS = [
    # (label_a, label_b, topic, higher_is_better) -- the direction makes clear
    # whether a higher or lower value counts as "better" for this metric.
    ("Class A", "Class B", "test scores", True),
    ("Runner A", "Runner B", "race times", False),
    ("Store A", "Store B", "weekly sales", True),
    ("Plant group A", "Plant group B", "plant heights", True),
    ("Golfer A", "Golfer B", "golf scores", False),
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


class Stem7DSP3:
    """Generates 20 variants for each of 4 stems from the 7.DSP.3 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx, variant_idx):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    def _make_overlap_data(self, rng, gen, overlap_type):
        """Generate two datasets with specified overlap.

        overlap_type: 'full', 'partial', or 'none'
        """
        if overlap_type == "full":
            # Same range, different distributions
            center = rng.randint(20, 40)
            spread = rng.randint(5, 10)
            n = rng.randint(6, 10)
            data_a = sorted([center + rng.randint(-spread, spread) for _ in range(n)])
            data_b = sorted([center + rng.randint(-spread, spread) for _ in range(n)])
        elif overlap_type == "partial":
            # Overlapping but shifted ranges. Keep the shift below the combined
            # spread so the whisker ranges genuinely overlap (otherwise the box
            # plots look separate and a "partial overlap" key is wrong), but
            # large enough that the medians are clearly different.
            spread = rng.randint(6, 9)
            n = rng.randint(6, 10)
            center_a = rng.randint(15, 22)
            center_b = center_a + rng.randint(spread, 2 * spread - 2)
            data_a = sorted([center_a + rng.randint(-spread, spread) for _ in range(n)])
            data_b = sorted([center_b + rng.randint(-spread, spread) for _ in range(n)])
            # Guarantee the ranges actually overlap even on an unlucky draw.
            if max(data_a) < min(data_b):
                data_a[-1] = min(data_b) + rng.randint(1, spread)
                data_a.sort()
        else:  # none
            n = rng.randint(5, 8)
            data_a = sorted([rng.randint(5, 15) for _ in range(n)])
            data_b = sorted([rng.randint(25, 40) for _ in range(n)])
        return data_a, data_b

    # ----------------------------------------------------------------
    # Stem 1: Below – Classify overlap (MC, DOK 2)
    # ----------------------------------------------------------------
    def _stem1(self, variant_idx):
        gen, rng = self._make_gen(1, variant_idx)
        label_a, label_b, topic, _hib = rng.choice(CONTEXTS)

        overlap_type = rng.choice(["full", "partial", "none"])
        data_a, data_b = self._make_overlap_data(rng, gen, overlap_type)

        fns_a = five_number_summary(data_a)
        fns_b = five_number_summary(data_b)
        all_min = min(fns_a[0], fns_b[0])
        all_max = max(fns_a[4], fns_b[4])
        svg = box_plot_svg([fns_a, fns_b], [label_a, label_b],
                           x_min=all_min - 2, x_max=all_max + 2)

        overlap_desc = {
            "full": "full overlap (the ranges completely overlap)",
            "partial": "partial overlap (the ranges partially overlap)",
            "none": "no overlap (the ranges do not overlap)",
        }

        stem = (f"The box plots below show {topic} for two groups. [FIGURE] "
                f"How would you describe the degree of visual overlap between the two distributions?")

        correct = overlap_desc[overlap_type]
        wrong_keys = [k for k in overlap_desc if k != overlap_type]
        wrong = [overlap_desc[k] for k in wrong_keys]
        wrong.append("Cannot be determined from box plots.")

        all_choices = [(correct, True)] + [(w, False) for w in wrong[:3]]
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
            worked_solution=(f"{label_a} range: {fns_a[0]}-{fns_a[4]}. "
                             f"{label_b} range: {fns_b[0]}-{fns_b[4]}. This shows {correct}."),
            choices=choices,
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=gen.seed, stem_index=1, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 2: Approaching – Analyze overlap using measures on box plots (MC, DOK 2)
    # ----------------------------------------------------------------
    def _stem2(self, variant_idx):
        gen, rng = self._make_gen(2, variant_idx)
        label_a, label_b, topic, _hib = rng.choice(CONTEXTS)

        data_a, data_b = self._make_overlap_data(rng, gen, "partial")
        fns_a = five_number_summary(data_a)
        fns_b = five_number_summary(data_b)
        med_a, med_b = fns_a[2], fns_b[2]
        iqr_a = fns_a[3] - fns_a[1]
        iqr_b = fns_b[3] - fns_b[1]

        all_min = min(fns_a[0], fns_b[0])
        all_max = max(fns_a[4], fns_b[4])
        svg = box_plot_svg([fns_a, fns_b], [label_a, label_b],
                           x_min=all_min - 2, x_max=all_max + 2)

        stem = (f"The box plots show {topic} for two groups. [FIGURE] "
                f"Which statement accurately compares the two distributions?")

        # Build correct statement
        if med_a > med_b:
            correct = (f"{label_a} has a higher median ({_fmt(med_a)}) than "
                       f"{label_b} ({_fmt(med_b)}), but the distributions partially overlap.")
        else:
            correct = (f"{label_b} has a higher median ({_fmt(med_b)}) than "
                       f"{label_a} ({_fmt(med_a)}), but the distributions partially overlap.")

        wrong = [
            f"The two groups have no overlap so they are completely different.",
            f"Both groups have the same median so they perform equally.",
            f"The IQRs are the same, so the groups have equal variability.",
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
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_key, answer_latex=answer_key,
            worked_solution=correct,
            choices=choices,
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=gen.seed, stem_index=2, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 3: At – Describe outlier effects on mean/median (MC, DOK 2)
    # ----------------------------------------------------------------
    def _stem3(self, variant_idx):
        gen, rng = self._make_gen(3, variant_idx)
        context = rng.choice(CONTEXTS)[2]

        n = rng.randint(7, 12)
        data = gen.generate_dataset(n, 10, 40)
        mean_orig = _mean(data)
        median_orig = _median(data)

        # Add an outlier
        outlier = max(data) + rng.randint(20, 40)
        data_with = sorted(data + [outlier])
        mean_new = _mean(data_with)
        median_new = _median(data_with)

        svg = dot_plot_svg(data_with, context, min(data_with), max(data_with))

        mean_change = abs(mean_new - mean_orig)
        median_change = abs(median_new - median_orig)

        stem = (f"The dot plot shows {context} for a group. [FIGURE] "
                f"The value {outlier} is an outlier. "
                f"How does this outlier affect the mean compared to the median?")

        correct = (f"The outlier affects the mean more than the median. "
                   f"The mean shifts by about {_fmt(mean_change, 1)}, "
                   f"while the median shifts by about {_fmt(median_change, 1)}.")
        wrong = [
            "The outlier affects the median more than the mean.",
            "The outlier affects both the mean and median equally.",
            "The outlier has no effect on either the mean or the median.",
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
            worked_solution=(f"Without outlier: mean={_fmt(mean_orig)}, median={_fmt(median_orig)}. "
                             f"With outlier: mean={_fmt(mean_new)}, median={_fmt(median_new)}."),
            choices=choices,
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=gen.seed, stem_index=3, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 4: Above – Justify/critique comparative inferences (MC, DOK 3)
    # ----------------------------------------------------------------
    def _stem4(self, variant_idx):
        gen, rng = self._make_gen(4, variant_idx)
        label_a, label_b, topic, higher_better = rng.choice(CONTEXTS)

        overlap = rng.choice(["partial", "full"])
        data_a, data_b = self._make_overlap_data(rng, gen, overlap)
        fns_a = five_number_summary(data_a)
        fns_b = five_number_summary(data_b)
        med_a, med_b = fns_a[2], fns_b[2]

        all_min = min(fns_a[0], fns_b[0])
        all_max = max(fns_a[4], fns_b[4])
        svg = box_plot_svg([fns_a, fns_b], [label_a, label_b],
                           x_min=all_min - 2, x_max=all_max + 2)

        # Which group is actually "better" depends on the metric's direction, so
        # state that direction in the prompt (a race time is better when lower; a
        # test score is better when higher). Basing "outperforms" purely on a higher
        # median would be wrong for a lower-is-better metric like race times.
        high_median = label_a if med_a >= med_b else label_b
        low_median = label_b if high_median == label_a else label_a
        better = high_median if higher_better else low_median
        worse = low_median if higher_better else high_median
        direction = "a higher value is better" if higher_better else "a lower value is better"

        claim = f"In {topic}, {better} always outperforms {worse}."
        stem = (f"The box plots show {topic}, where {direction}. [FIGURE] "
                f"A student says: \"{claim}\" "
                f"Which response best evaluates this claim?")

        if overlap == "full":
            correct = (f"The claim is not supported. Even though {better} has a better "
                       f"median, the full overlap means many {worse} values outperform "
                       f"{better} values, so 'always' is wrong.")
        else:
            correct = (f"The claim is too strong. {better} has a better median, but the "
                       f"partial overlap means some {worse} values outperform some "
                       f"{better} values. 'Always' is not justified.")

        wrong = [
            f"The claim is correct because {better} has a better median.",
            f"The claim is correct because box plots show all individual values.",
            f"Neither group is better because the box plots overlap.",
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
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE,
                                         ItemType.MC, Difficulty.DIFFICULT, 4, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=ItemType.MC,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_key, answer_latex=answer_key,
            worked_solution=correct,
            choices=choices,
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
