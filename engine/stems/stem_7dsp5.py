"""
Stem generator for 7.DSP.5:
  Develop probability models that include the sample space and probabilities
  of outcomes to represent simple events with equally likely outcomes.
  Predict the approximate relative frequency of the event based on the model.
  Compare probabilities from the model to observed frequencies.

Content Limits:
  - Rational numbers only
  - Probabilities NOT given as percentages
  - Probabilities as whole number, fraction, or decimal rounded to nearest tenth/hundredth
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: Whole numbers or unit fractions with common denominators; uniform model
  Medium: Non-unit fractions with common denominator
  Difficult: Fractions with different denominators

4 Stems:
  Stem 1 (Below-MC, DOK 1):       Find probability of event from given probability model
  Stem 2 (Approaching-NR, DOK 1): Calculate probability as ratio from sample space
  Stem 3 (At-MP, DOK 2):          Create probability model and predict expected frequency
  Stem 4 (Above-MP, DOK 3):       Compare theoretical probability to observed frequency
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


STANDARD_CODE = "7.DSP.5"
VARIANTS_PER_STEM = 20


def _frac_str(f):
    """Format a Fraction as a display string."""
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


COLORS = ["red", "blue", "green", "yellow", "orange", "purple", "white", "black"]
OBJECTS = [
    ("marbles", "marble", "a bag"),
    ("tiles", "tile", "a bag"),
    ("balls", "ball", "a box"),
]


class Stem7DSP5:
    """Generates 20 variants for each of 4 stems from the 7.DSP.5 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx, variant_idx):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ----------------------------------------------------------------
    # Stem 1: Below - Find probability from given model (MC, DOK 1)
    # ----------------------------------------------------------------
    def _stem1(self, variant_idx):
        gen, rng = self._make_gen(1, variant_idx)

        # Uniform probability model (easy)
        n_sections = rng.choice([4, 5, 6])
        colors = rng.sample(COLORS, n_sections)
        prob_each = Fraction(1, n_sections)

        # Pick two colors to combine
        targets = rng.sample(colors, 2)
        correct_prob = prob_each * 2

        # Build probability table description
        table_rows = ", ".join(f"{c}: {_frac_str(prob_each)}" for c in colors)
        stem = (f"A spinner has {n_sections} equal sections. The probability of "
                f"landing on each color is shown: {table_rows}. "
                f"What is the probability of landing on {targets[0]} or {targets[1]}?")

        correct = _frac_str(correct_prob)
        wrong = []
        wrong.append(_frac_str(prob_each))  # only one color
        wrong.append(_frac_str(Fraction(1, n_sections * 2)))  # multiply instead of add
        wrong.append(_frac_str(prob_each * 3))  # three colors

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
            worked_solution=f"P({targets[0]} or {targets[1]}) = {_frac_str(prob_each)} + {_frac_str(prob_each)} = {correct}.",
            choices=choices,
            seed=gen.seed, stem_index=1, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 2: Approaching - Calculate probability from sample space (NR, DOK 1)
    # ----------------------------------------------------------------
    def _stem2(self, variant_idx):
        gen, rng = self._make_gen(2, variant_idx)

        obj_plural, obj_singular, container = rng.choice(OBJECTS)
        n_colors = rng.choice([3, 4])
        colors = rng.sample(COLORS, n_colors)
        counts = {c: rng.randint(2, 6) for c in colors}
        total = sum(counts.values())

        # Pick two colors to combine
        targets = rng.sample(colors, 2)
        p1 = Fraction(counts[targets[0]], total)
        p2 = Fraction(counts[targets[1]], total)
        correct_prob = p1 + p2

        items_desc = ", ".join(f"{counts[c]} {c}" for c in colors)
        stem = (f"{container.capitalize()} contains {items_desc} {obj_plural} "
                f"({total} total). One {obj_singular} is drawn at random. "
                f"What is the probability of drawing a {targets[0]} or {targets[1]} "
                f"{obj_singular}? Write your answer as a fraction.")

        answer_str = _frac_str(correct_prob)
        worked = (f"P({targets[0]}) = {_frac_str(p1)}, P({targets[1]}) = {_frac_str(p2)}. "
                  f"P({targets[0]} or {targets[1]}) = {_frac_str(p1)} + {_frac_str(p2)} = {answer_str}.")

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING,
                                         ItemType.NR, Difficulty.MEDIUM, 2, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.NR,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_str, answer_latex=answer_str,
            worked_solution=worked,
            seed=gen.seed, stem_index=2, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 3: At - Create probability model + predict frequency (MP, DOK 2)
    # ----------------------------------------------------------------
    def _stem3(self, variant_idx):
        gen, rng = self._make_gen(3, variant_idx)

        obj_plural, obj_singular, container = rng.choice(OBJECTS)
        n_colors = rng.choice([3, 4, 5])
        colors = rng.sample(COLORS, n_colors)
        counts = {c: rng.randint(2, 6) for c in colors}
        total = sum(counts.values())

        # Pick a target color for the prediction
        target = rng.choice(colors)
        prob = Fraction(counts[target], total)

        # Number of trials - pick so expected value is a whole number
        possible_trials = []
        for t in [20, 24, 30, 36, 40, 48, 50, 60]:
            expected = prob * t
            if expected.denominator == 1 and expected.numerator > 0:
                possible_trials.append(t)

        if not possible_trials:
            counts[target] = rng.choice([2, 3, 5, 6])
            total = sum(counts.values())
            prob = Fraction(counts[target], total)
            for t in [30, 60, total * 2, total * 3, total * 5]:
                expected = prob * t
                if expected.denominator == 1 and expected.numerator > 0:
                    possible_trials.append(t)

        n_trials = rng.choice(possible_trials) if possible_trials else 30
        expected_count = int(prob * n_trials)

        items_desc = ", ".join(f"{counts[c]} {c}" for c in colors)

        # Part A: Create the probability model (give probability for each color)
        prob_answers = []
        for c in colors:
            p = Fraction(counts[c], total)
            prob_answers.append(f"P({c}) = {_frac_str(p)}")
        partA_answer = "; ".join(prob_answers)

        partA_prompt = (f"Complete the probability model by finding the probability "
                        f"of drawing each color. Write each probability as a fraction.")

        # Part B: Predict expected frequency
        partB_prompt = (f"If this experiment is repeated {n_trials} times, how many "
                        f"times would you expect to draw a {target} {obj_singular}?")
        partB_answer = str(expected_count)

        stem = (f"{container.capitalize()} contains {items_desc} {obj_plural} "
                f"({total} total). A {obj_singular} is drawn at random, "
                f"the color is recorded, and the {obj_singular} is returned to "
                f"{container}.\n\n"
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

        worked = (f"Part A: Total = {total}. "
                  + "; ".join(f"P({c}) = {counts[c]}/{total} = {_frac_str(Fraction(counts[c], total))}" for c in colors)
                  + f"\nPart B: P({target}) = {_frac_str(prob)}. "
                  f"Expected = {_frac_str(prob)} x {n_trials} = {expected_count}.")

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.AT,
                                         ItemType.MP, Difficulty.MEDIUM, 3, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MP,
            stem_text=stem, stem_latex=stem,
            answer_text=f"A: {partA_answer}; B: {partB_answer}",
            answer_latex=f"A: {partA_answer}; B: {partB_answer}",
            worked_solution=worked,
            parts=parts,
            seed=gen.seed, stem_index=3, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 4: Above - Compare theoretical vs observed frequency (MP, DOK 3)
    # ----------------------------------------------------------------
    def _stem4(self, variant_idx):
        gen, rng = self._make_gen(4, variant_idx)

        # Fair number cube scenario
        n_sides = 6
        n_trials = rng.choice([30, 36, 60, 120])
        target_number = rng.randint(1, 6)
        theoretical_prob = Fraction(1, n_sides)
        expected_count = Fraction(n_trials, n_sides)

        # Generate realistic observed frequencies for all 6 sides
        # Start with expected, then add random noise
        observed = {}
        remaining = n_trials
        sides = list(range(1, 7))
        for i, side in enumerate(sides[:-1]):
            exp = n_trials / n_sides
            obs = max(1, int(exp + rng.randint(-3, 3)))
            obs = min(obs, remaining - (n_sides - i - 1))
            observed[side] = obs
            remaining -= obs
        observed[sides[-1]] = remaining

        observed_target = observed[target_number]
        observed_freq = Fraction(observed_target, n_trials)

        # Observed frequencies as a compact table (clearer than a long inline
        # list that ran off the edge of the page).
        freq_table = {
            "type": "data_table",
            "headers": ["Roll", "Frequency"],
            "rows": [[str(s), str(observed[s])] for s in sides],
            "orientation": "horizontal",
        }

        partA_prompt = f"What is the theoretical probability of rolling a {target_number}?"
        partA_answer = _frac_str(theoretical_prob)

        partB_prompt = (f"The observed results are shown in the table. "
                        f"The observed relative frequency of rolling a {target_number} "
                        f"is {observed_target}/{n_trials}. "
                        f"Is the observed frequency close to the theoretical probability? "
                        f"What might explain any difference?")

        diff = abs(theoretical_prob - observed_freq)
        if diff <= Fraction(1, 20):
            closeness = "very close to"
        elif diff <= Fraction(1, 10):
            closeness = "close to"
        else:
            closeness = "not very close to"

        partB_answer = (f"The observed frequency {_frac_str(observed_freq)} is {closeness} "
                        f"the theoretical probability {_frac_str(theoretical_prob)}. "
                        f"Differences are due to random chance in a finite number of trials.")

        stem = (f"A student rolls a fair number cube (sides 1-6) {n_trials} times "
                f"and records the results in the table below.\n\n"
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

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE,
                                         ItemType.MP, Difficulty.DIFFICULT, 4, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=ItemType.MP,
            stem_text=stem, stem_latex=stem,
            answer_text=f"A: {partA_answer} B: {partB_answer}",
            answer_latex=f"A: {partA_answer} B: {partB_answer}",
            worked_solution=f"P(theoretical) = {_frac_str(theoretical_prob)}. Observed = {observed_target}/{n_trials} = {_frac_str(observed_freq)}. Difference due to random variation.",
            parts=parts,
            render_data=freq_table,
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
