"""
Stem generator for 7.DSP.2:
  Find, use, and interpret measures of central tendency (mean, median) and
  measures of spread (range, IQR, MAD) for numerical data from random samples
  to draw comparative inferences about two populations.

Content Limits:
  - Must include at least two sets of data
  - Approximately normal distributions
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: 9 or fewer values, whole numbers, list of values
  Medium: 10-20 values, integers, line plot or box plot
  Difficult: 20+ values, rational numbers or multiple data sets

4 Stems:
  Stem 1 (Below-MC, DOK 2):       Calculate mean/median/range from two samples
  Stem 2 (Approaching-NR, DOK 2): Calculate IQR and MAD for two samples
  Stem 3 (At-MP, DOK 2):          Compare two datasets using measures
  Stem 4 (Above-MP, DOK 3):       Justify/critique comparative inferences
"""

import random
from fractions import Fraction

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.models import (
    GeneratedQuestion, QuestionChoice, QuestionPart,
    Difficulty, ProficiencyLevel, ItemType, make_question_id
)
from engine.number_generators import (
    NumberGenerator, five_number_summary, mean_absolute_deviation
)
from engine.svg_helpers import dot_plot_svg, box_plot_svg


STANDARD_CODE = "7.DSP.2"
VARIANTS_PER_STEM = 20


COMPARISON_CONTEXTS = [
    ("Class A test scores", "Class B test scores", "test scores"),
    ("Team 1 points per game", "Team 2 points per game", "points scored"),
    ("Morning shift output", "Evening shift output", "items produced"),
    ("Boys' heights (in)", "Girls' heights (in)", "heights"),
    ("School A reading scores", "School B reading scores", "reading scores"),
    ("Group 1 run times (min)", "Group 2 run times (min)", "run times"),
    ("Store A daily sales", "Store B daily sales", "daily sales"),
    ("Plant A heights (cm)", "Plant B heights (cm)", "plant heights"),
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


class Stem7DSP2:
    """Generates 20 variants for each of 4 stems from the 7.DSP.2 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx, variant_idx):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    def _make_pair(self, gen, rng, n, lo, hi):
        """Generate two datasets for comparison."""
        data_a = gen.generate_dataset(n, lo, hi)
        # Shift second dataset slightly
        shift = rng.randint(-5, 5)
        data_b = [max(lo, min(hi, d + rng.randint(-3, 3) + shift)) for d in
                  gen.generate_dataset(n, lo, hi)]
        data_b.sort()
        return data_a, data_b

    # ----------------------------------------------------------------
    # Stem 1: Below – Calculate mean/median/range from two samples (MC, DOK 2)
    # ----------------------------------------------------------------
    def _stem1(self, variant_idx):
        gen, rng = self._make_gen(1, variant_idx)
        label_a, label_b, topic = rng.choice(COMPARISON_CONTEXTS)

        n = rng.randint(5, 9)
        data_a, data_b = self._make_pair(gen, rng, n, 10, 50)

        measure = rng.choice(["mean", "median"])
        if measure == "mean":
            val_a = _mean(data_a)
            val_b = _mean(data_b)
        else:
            val_a = _median(data_a)
            val_b = _median(data_b)

        if val_a > val_b:
            higher = label_a
        elif val_b > val_a:
            higher = label_b
        else:
            higher = "They are equal"

        data_a_str = ", ".join(str(d) for d in data_a)
        data_b_str = ", ".join(str(d) for d in data_b)

        stem = (f"{label_a}: {data_a_str}\n{label_b}: {data_b_str}\n"
                f"Which group has the higher {measure}?")

        all_choices = [
            (f"{label_a} (the {measure} is {_fmt(val_a)})", val_a >= val_b and val_a != val_b),
            (f"{label_b} (the {measure} is {_fmt(val_b)})", val_b > val_a),
            (f"They have the same {measure}.", val_a == val_b),
            (f"Cannot be determined from the data.", False),
        ]
        # Fix: ensure exactly one is correct
        correct_idx = next(i for i, (_, c) in enumerate(all_choices) if c)
        for i in range(len(all_choices)):
            text, _ = all_choices[i]
            all_choices[i] = (text, i == correct_idx)

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
            worked_solution=f"{label_a} {measure} = {_fmt(val_a)}, {label_b} {measure} = {_fmt(val_b)}.",
            choices=choices,
            seed=gen.seed, stem_index=1, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 2: Approaching – Calculate IQR and MAD (NR, DOK 2)
    # ----------------------------------------------------------------
    def _stem2(self, variant_idx):
        gen, rng = self._make_gen(2, variant_idx)
        label_a, label_b, topic = rng.choice(COMPARISON_CONTEXTS)

        measure = rng.choice(["IQR", "MAD"])
        # MAD is computed by hand from the listed values, so cap it at 10 values to
        # keep it a quick check; IQR is read off a box plot, so it can run larger.
        n = rng.randint(6, 10) if measure == "MAD" else rng.randint(7, 12)
        data_a, data_b = self._make_pair(gen, rng, n, 10, 50)

        if measure == "IQR":
            fns_a = five_number_summary(data_a)
            fns_b = five_number_summary(data_b)
            val_a = fns_a[3] - fns_a[1]  # Q3 - Q1
            val_b = fns_b[3] - fns_b[1]

            # Show box plots
            all_min = min(fns_a[0], fns_b[0])
            all_max = max(fns_a[4], fns_b[4])
            svg = box_plot_svg([fns_a, fns_b], [label_a, label_b],
                               x_min=all_min - 2, x_max=all_max + 2)

            stem = (f"The box plots below show {topic} for two groups. [FIGURE] "
                    f"What is the IQR for {label_a}?")
            answer_str = _fmt(val_a)
            worked = f"IQR({label_a}) = Q3 - Q1 = {_fmt(fns_a[3])} - {_fmt(fns_a[1])} = {answer_str}"
        else:
            val_a = mean_absolute_deviation(data_a)
            data_a_str = ", ".join(str(d) for d in data_a)
            stem = (f"The data below shows {topic} for {label_a}: {data_a_str}. "
                    f"Calculate the mean absolute deviation (MAD). Round to the nearest tenth.")
            svg = None
            answer_str = _fmt(round(val_a, 1), 1)
            worked = f"Mean = {_fmt(_mean(data_a))}. MAD = {answer_str}"

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING,
                                         ItemType.NR, Difficulty.MEDIUM, 2, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_str, answer_latex=answer_str,
            worked_solution=worked,
            render_data={"svg_html": svg, "type": "svg_html"} if svg else None,
            seed=gen.seed, stem_index=2, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 3: At – Compare two datasets using measures (MP, DOK 2)
    # ----------------------------------------------------------------
    def _stem3(self, variant_idx):
        gen, rng = self._make_gen(3, variant_idx)
        label_a, label_b, topic = rng.choice(COMPARISON_CONTEXTS)

        n = rng.randint(8, 15)
        data_a, data_b = self._make_pair(gen, rng, n, 10, 60)

        mean_a, mean_b = _mean(data_a), _mean(data_b)
        med_a, med_b = _median(data_a), _median(data_b)
        fns_a, fns_b = five_number_summary(data_a), five_number_summary(data_b)
        iqr_a = fns_a[3] - fns_a[1]
        iqr_b = fns_b[3] - fns_b[1]

        # Show box plots
        all_min = min(fns_a[0], fns_b[0])
        all_max = max(fns_a[4], fns_b[4])
        svg = box_plot_svg([fns_a, fns_b], [label_a, label_b],
                           x_min=all_min - 2, x_max=all_max + 2)

        partA_prompt = f"Compare the centers (medians) of the two groups."
        if med_a > med_b:
            partA_answer = (f"{label_a} has a higher median ({_fmt(med_a)}) than "
                            f"{label_b} ({_fmt(med_b)}), suggesting {label_a} generally has higher {topic}.")
        elif med_b > med_a:
            partA_answer = (f"{label_b} has a higher median ({_fmt(med_b)}) than "
                            f"{label_a} ({_fmt(med_a)}), suggesting {label_b} generally has higher {topic}.")
        else:
            partA_answer = f"Both groups have the same median ({_fmt(med_a)})."

        partB_prompt = f"Compare the spreads (IQRs) of the two groups. What does this tell you?"
        if iqr_a > iqr_b:
            partB_answer = (f"{label_a} has a larger IQR ({_fmt(iqr_a)}) than {label_b} ({_fmt(iqr_b)}), "
                            f"meaning {label_a}'s {topic} are more spread out.")
        elif iqr_b > iqr_a:
            partB_answer = (f"{label_b} has a larger IQR ({_fmt(iqr_b)}) than {label_a} ({_fmt(iqr_a)}), "
                            f"meaning {label_b}'s {topic} are more spread out.")
        else:
            partB_answer = f"Both groups have similar IQRs (about {_fmt(iqr_a)}), meaning similar variability."

        stem = (f"The box plots below compare {topic} for two groups.\n\n"
                f"[FIGURE]\n\n"
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
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.AT,
                                         ItemType.MP, Difficulty.MEDIUM, 3, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MP,
            stem_text=stem, stem_latex=stem,
            answer_text=f"A: {partA_answer} B: {partB_answer}",
            answer_latex=f"A: {partA_answer} B: {partB_answer}",
            worked_solution=f"Medians: {_fmt(med_a)} vs {_fmt(med_b)}. IQRs: {_fmt(iqr_a)} vs {_fmt(iqr_b)}.",
            parts=parts,
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=gen.seed, stem_index=3, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 4: Above – Justify/critique comparative inferences (MP, DOK 3)
    # ----------------------------------------------------------------
    def _stem4(self, variant_idx):
        gen, rng = self._make_gen(4, variant_idx)
        label_a, label_b, topic = rng.choice(COMPARISON_CONTEXTS)

        n = rng.randint(8, 12)
        data_a, data_b = self._make_pair(gen, rng, n, 10, 50)

        mean_a, mean_b = _mean(data_a), _mean(data_b)
        mad_a = mean_absolute_deviation(data_a)
        mad_b = mean_absolute_deviation(data_b)

        data_a_str = ", ".join(str(d) for d in data_a)
        data_b_str = ", ".join(str(d) for d in data_b)

        # Present a claim for students to evaluate
        if mean_a > mean_b:
            claim = f"Since {label_a} has a higher mean ({_fmt(mean_a)} vs {_fmt(mean_b)}), {label_a} is definitely better."
        else:
            claim = f"Since {label_b} has a higher mean ({_fmt(mean_b)} vs {_fmt(mean_a)}), {label_b} is definitely better."

        partA_prompt = "Is this claim valid? Explain using measures of center and spread."
        diff = abs(mean_a - mean_b)
        avg_mad = (mad_a + mad_b) / 2
        if diff > avg_mad * 2:
            partA_answer = (f"The claim has some support. The difference in means ({_fmt(diff)}) "
                            f"is large compared to the average MAD ({_fmt(avg_mad, 1)}). "
                            f"However, saying 'definitely' is too strong for sample data.")
        else:
            partA_answer = (f"The claim is not well-supported. The difference in means ({_fmt(diff)}) "
                            f"is small compared to the variability (MAD: {_fmt(mad_a, 1)} and {_fmt(mad_b, 1)}). "
                            f"The overlap makes it hard to conclude one is better.")

        partB_prompt = "What additional information would strengthen or weaken the conclusion?"
        partB_answer = "A larger sample size from random sampling would make the conclusion more reliable."

        stem = (f"{label_a}: {data_a_str}\n{label_b}: {data_b_str}\n"
                f"A student claims: \"{claim}\"\n\n"
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
            worked_solution=f"Means: {_fmt(mean_a)} vs {_fmt(mean_b)}, diff={_fmt(diff)}. MADs: {_fmt(mad_a,1)}, {_fmt(mad_b,1)}.",
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
