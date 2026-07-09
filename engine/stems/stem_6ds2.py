"""
Stem generator for 6.DS.2:
  Formulate statistical questions; collect and organize the data,
  and display and interpret the data with graphical representations.

Content Limits:
  - Positive rational numbers only
  - Focus on line plots, histograms, box plots
  - Questions about data should be basic interpretation
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: Data not included in item
  Medium: One set of data used
  Difficult: Two sets of data used

4 Stems:
  Stem 1 (Below-MC, DOK 1):       Distinguish statistical vs non-statistical questions
  Stem 2 (Approaching-MC, DOK 1-2): Identify data collection method; complete frequency table
  Stem 3 (At-MC, DOK 1-2):        Match statistical question to appropriate display
  Stem 4 (Above-MP, DOK 2):       Analyze display, draw conclusions with reasoning
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


STANDARD_CODE = "6.DS.2"
VARIANTS_PER_STEM = 20


# Statistical vs non-statistical question pools
STATISTICAL_QUESTIONS = [
    "How many hours per week do sixth graders spend reading?",
    "What are the heights of students in our class?",
    "How far do students travel to get to school?",
    "How many pets do families in our school have?",
    "What scores did students get on the last math test?",
    "How many minutes do students spend on homework each night?",
    "What are the shoe sizes of students in 6th grade?",
    "How many siblings do students in our grade have?",
    "What are the high temperatures for each day this month?",
    "How many words per minute can students in our class type?",
]

NON_STATISTICAL_QUESTIONS = [
    "What is the school mascot?",
    "How many days are in February 2025?",
    "What time does school start?",
    "How many students are in our class?",
    "What is the capital of Indiana?",
    "How tall is the school building?",
    "What color is the principal's car?",
    "How many pages are in the math textbook?",
    "What day of the week is it?",
    "How many letters are in the word 'mathematics'?",
]

DATA_COLLECTION_METHODS = [
    ("survey", "Ask each student in the grade to fill out a questionnaire."),
    ("observation", "Observe and record each student's choice during lunch for a week."),
    ("measurement", "Measure and record each student's height using a measuring tape."),
    ("experiment", "Have each student complete a timed typing test and record the results."),
]

DATA_CONTEXTS = [
    "hours of sleep per night", "number of books read this month",
    "test scores", "daily step counts (hundreds)",
    "time spent on homework (minutes)", "distance from home to school (miles)",
]


def _fmt(val, dec=1):
    f = float(val)
    if f == int(f):
        return str(int(f))
    return f"{f:.{dec}f}".rstrip('0').rstrip('.')


class Stem6DS2:
    """Generates 20 variants for each of 4 stems from the 6.DS.2 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx, variant_idx):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ----------------------------------------------------------------
    # Stem 1: Below – Statistical vs non-statistical questions (MC, DOK 1)
    # ----------------------------------------------------------------
    def _stem1(self, variant_idx):
        gen, rng = self._make_gen(1, variant_idx)

        # Pick one correct (statistical) and three wrong (non-statistical)
        correct = rng.choice(STATISTICAL_QUESTIONS)
        wrong = rng.sample(NON_STATISTICAL_QUESTIONS, 3)

        stem = "Which of the following is a statistical question?"

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
            worked_solution=(f"A statistical question anticipates variability in the answers. "
                             f"'{correct}' expects different answers from different people."),
            choices=choices,
            seed=gen.seed, stem_index=1, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 2: Approaching – Identify data collection method (MC, DOK 1-2)
    # ----------------------------------------------------------------
    def _stem2(self, variant_idx):
        gen, rng = self._make_gen(2, variant_idx)

        stat_q = rng.choice(STATISTICAL_QUESTIONS)
        correct_method_name, correct_desc = rng.choice(DATA_COLLECTION_METHODS)

        stem = (f"A student wants to answer the question: \"{stat_q}\" "
                f"Which method would be most appropriate for collecting this data?")

        # Make 3 wrong options
        wrong_descs = [
            "Look up the answer in a textbook.",
            "Ask one friend and use their answer for everyone.",
            "Guess the answer based on personal experience.",
        ]

        all_choices = [(correct_desc, True)] + [(w, False) for w in wrong_descs]
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
                                         ItemType.MC, Difficulty.EASY, 2, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_key, answer_latex=answer_key,
            worked_solution=f"To collect data with variability, you need to gather responses from multiple individuals.",
            choices=choices,
            seed=gen.seed, stem_index=2, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 3: At – Match statistical question to display (MC, DOK 1-2)
    # ----------------------------------------------------------------
    def _stem3(self, variant_idx):
        gen, rng = self._make_gen(3, variant_idx)
        context = rng.choice(DATA_CONTEXTS)
        data = gen.generate_dataset(rng.randint(8, 12), 1, 20)

        # Show a display and ask what question it answers
        display_type = rng.choice(["dot_plot", "box_plot"])

        if display_type == "dot_plot":
            svg = dot_plot_svg(data, context, min(data), max(data))
            correct = f"What are the individual values of {context} for these students?"
            wrong = [
                f"What is the total {context}?",
                f"Which student has the highest {context}?",
                f"What is the average {context} for all students in the school?",
            ]
        else:
            fns = five_number_summary(data)
            svg = box_plot_svg([fns], [context], x_min=fns[0] - 1, x_max=fns[4] + 1)
            correct = f"How are the values of {context} distributed across the dataset?"
            wrong = [
                f"What is the exact value for each student?",
                f"How many students were surveyed?",
                f"Which specific value occurred most often?",
            ]

        stem = (f"The {display_type.replace('_', ' ')} below shows data about {context}. "
                f"[FIGURE] Which statistical question could this display help answer?")

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
            worked_solution=f"The display shows how data is distributed, which answers: {correct}",
            choices=choices,
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=gen.seed, stem_index=3, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 4: Above – Analyze display, draw conclusions (MP, DOK 2)
    # ----------------------------------------------------------------
    def _stem4(self, variant_idx):
        gen, rng = self._make_gen(4, variant_idx)
        context = rng.choice(DATA_CONTEXTS)
        data = gen.generate_dataset(rng.randint(10, 15), 1, 25)
        fns = five_number_summary(data)
        mn, q1, med, q3, mx = fns
        mean_val = sum(data) / len(data)

        # Create a histogram
        lo, hi = min(data), max(data)
        bin_width = max(1, (hi - lo) // 4)
        bins = list(range(lo, hi + bin_width + 1, bin_width))
        freqs = []
        for i in range(len(bins) - 1):
            if i == len(bins) - 2:
                count = sum(1 for d in data if bins[i] <= d <= bins[i + 1])
            else:
                count = sum(1 for d in data if bins[i] <= d < bins[i + 1])
            freqs.append(count)

        svg = histogram_svg(bins, freqs, context, "Frequency")

        # Find the tallest bin
        max_freq_idx = freqs.index(max(freqs))
        tallest_bin = f"{bins[max_freq_idx]}-{bins[max_freq_idx + 1]}"

        partA_prompt = "Which interval contains the most data values? How many values are in that interval?"
        partA_answer = f"The interval {tallest_bin} contains {max(freqs)} values."

        partB_prompt = "Based on the histogram, write one conclusion about the data. Support it with evidence."
        if max_freq_idx == 0:
            partB_answer = (f"Most values cluster in the lower range ({tallest_bin}), "
                            f"with {max(freqs)} of {len(data)} values in that interval. "
                            f"The distribution is skewed right.")
        elif max_freq_idx == len(freqs) - 1:
            partB_answer = (f"Most values cluster in the upper range ({tallest_bin}), "
                            f"with {max(freqs)} of {len(data)} values. "
                            f"The distribution is skewed left.")
        else:
            partB_answer = (f"The data peaks in the middle interval ({tallest_bin}) "
                            f"with {max(freqs)} values, suggesting a roughly symmetric distribution.")

        stem = (f"The histogram below shows {context} for {len(data)} observations.\n\n"
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
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MP,
            stem_text=stem, stem_latex=stem,
            answer_text=f"A: {partA_answer} B: {partB_answer}",
            answer_latex=f"A: {partA_answer} B: {partB_answer}",
            worked_solution=f"Tallest bar: {tallest_bin} with {max(freqs)} values.",
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
