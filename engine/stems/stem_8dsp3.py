"""
Stem generator for 8.DSP.3:
  Represent sample spaces and find probabilities of compound events
  (independent and dependent) using organized lists, tables, and tree diagrams.

Content Limits:
  - Rational numbers only
  - If using deck of cards, include total (52) and specific type count
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: Two different objects and two different independent events
  Medium: Three objects and two events OR two objects and three events
  Difficult: Compound probability with dependent AND independent events

4 Stems:
  Stem 1 (Below-MC, DOK 2):       Identify correct sample space for compound event
  Stem 2 (Approaching-MP, DOK 2): Calculate probability of independent compound event
  Stem 3 (At-NR, DOK 2):          Calculate probability of dependent compound event
  Stem 4 (Above-MP, DOK 3):       Compound event with multiple dependencies
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
from engine.svg_helpers import tree_diagram_svg


STANDARD_CODE = "8.DSP.3"
VARIANTS_PER_STEM = 20


def _frac_str(f):
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


class Stem8DSP3:
    """Generates 20 variants for each of 4 stems from the 8.DSP.3 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx, variant_idx):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ----------------------------------------------------------------
    # Stem 1: Below – Identify correct sample space (MC, DOK 2)
    # ----------------------------------------------------------------
    def _stem1(self, variant_idx):
        gen, rng = self._make_gen(1, variant_idx)

        scenario_type = rng.choice(["coin_die", "spinner_coin", "two_dice"])

        if scenario_type == "coin_die":
            stage1 = ["H", "T"]
            stage2 = ["1", "2", "3", "4", "5", "6"]
            desc = "A coin is flipped and a number cube is rolled"
            total = 12
        elif scenario_type == "spinner_coin":
            colors = rng.sample(["Red", "Blue", "Green", "Yellow"], 3)
            stage1 = colors
            stage2 = ["H", "T"]
            desc = f"A spinner with sections {', '.join(colors)} is spun and a coin is flipped"
            total = len(colors) * 2
        else:
            stage1 = ["1", "2", "3"]
            stage2 = ["1", "2", "3"]
            desc = "Two spinners, each with sections 1, 2, and 3, are spun"
            total = 9

        svg = tree_diagram_svg([stage1, stage2])

        stem = (f"{desc}. [FIGURE] How many outcomes are in the sample space?")

        correct = str(total)
        wrong = [
            str(len(stage1) + len(stage2)),
            str(total + len(stage1)),
            str(total - 1),
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
            worked_solution=f"Sample space = {len(stage1)} x {len(stage2)} = {total} outcomes.",
            choices=choices,
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=gen.seed, stem_index=1, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 2: Approaching – Probability of independent compound event (MP, DOK 2)
    # ----------------------------------------------------------------
    def _stem2(self, variant_idx):
        gen, rng = self._make_gen(2, variant_idx)

        scenario = rng.choice(["coin_die", "two_spinners", "bag_coin"])

        if scenario == "coin_die":
            desc = "A fair coin is flipped and a fair number cube (1-6) is rolled."
            target = rng.choice([
                ("heads and an even number", Fraction(1, 2) * Fraction(3, 6)),
                ("tails and a number greater than 4", Fraction(1, 2) * Fraction(2, 6)),
                ("heads and a 3", Fraction(1, 2) * Fraction(1, 6)),
            ])
            event_desc, prob = target
        elif scenario == "two_spinners":
            n1 = rng.choice([3, 4])
            n2 = rng.choice([3, 4])
            desc = f"Spinner A has {n1} equal sections numbered 1-{n1}. Spinner B has {n2} equal sections numbered 1-{n2}. Both are spun."
            t1 = rng.randint(1, n1)
            t2 = rng.randint(1, n2)
            prob = Fraction(1, n1) * Fraction(1, n2)
            event_desc = f"Spinner A lands on {t1} and Spinner B lands on {t2}"
        else:
            colors = rng.sample(["red", "blue", "green", "yellow"], 3)
            counts = {c: rng.randint(2, 5) for c in colors}
            total = sum(counts.values())
            target_color = rng.choice(colors)
            desc = (f"A bag contains {', '.join(f'{counts[c]} {c}' for c in colors)} "
                    f"marbles ({total} total). A marble is drawn, replaced, "
                    f"then another is drawn. A fair coin is also flipped.")
            p_marble = Fraction(counts[target_color], total)
            prob = p_marble * Fraction(1, 2)
            event_desc = f"drawing a {target_color} marble and flipping heads"

        stem = f"{desc}"

        partA_prompt = f"How many total outcomes are in the sample space?"
        if scenario == "coin_die":
            total_outcomes = 12
            partA_answer = "12"
        elif scenario == "two_spinners":
            total_outcomes = n1 * n2
            partA_answer = str(total_outcomes)
        else:
            total_outcomes = total * 2
            partA_answer = str(total_outcomes)

        partB_prompt = f"What is the probability of {event_desc}?"
        partB_answer = _frac_str(prob)

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
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING,
                                         ItemType.MP, Difficulty.MEDIUM, 2, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MP,
            stem_text=stem, stem_latex=stem,
            answer_text=f"A: {partA_answer} B: {partB_answer}",
            answer_latex=f"A: {partA_answer} B: {partB_answer}",
            worked_solution=f"Independent: P = product of individual probabilities = {partB_answer}.",
            parts=parts,
            seed=gen.seed, stem_index=2, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 3: At – Dependent compound event (NR, DOK 2)
    # ----------------------------------------------------------------
    def _stem3(self, variant_idx):
        gen, rng = self._make_gen(3, variant_idx)

        # Without replacement
        colors = rng.sample(["red", "blue", "green", "yellow", "purple"], 3)
        counts = {c: rng.randint(3, 6) for c in colors}
        total = sum(counts.values())

        target1 = rng.choice(colors)
        target2 = rng.choice(colors)

        p1 = Fraction(counts[target1], total)
        if target1 == target2:
            p2 = Fraction(counts[target2] - 1, total - 1)
        else:
            p2 = Fraction(counts[target2], total - 1)
        prob = p1 * p2

        items_desc = ", ".join(f"{counts[c]} {c}" for c in colors)

        if target1 == target2:
            stem = (f"A bag contains {items_desc} marbles ({total} total). "
                    f"Two marbles are drawn without replacement. "
                    f"What is the probability that both are {target1}? "
                    f"Write your answer as a fraction.")
        else:
            stem = (f"A bag contains {items_desc} marbles ({total} total). "
                    f"Two marbles are drawn without replacement. "
                    f"What is the probability of drawing a {target1} then "
                    f"a {target2}? Write your answer as a fraction.")

        answer_str = _frac_str(prob)
        worked = (f"P(1st {target1}) = {_frac_str(p1)}. "
                  f"P(2nd {target2} | 1st {target1}) = {_frac_str(p2)}. "
                  f"P(both) = {_frac_str(p1)} x {_frac_str(p2)} = {answer_str}.")

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.AT,
                                         ItemType.NR, Difficulty.MEDIUM, 3, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_str, answer_latex=answer_str,
            worked_solution=worked,
            seed=gen.seed, stem_index=3, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 4: Above – Multiple dependencies (MP, DOK 3)
    # ----------------------------------------------------------------
    def _stem4(self, variant_idx):
        gen, rng = self._make_gen(4, variant_idx)

        # Three draws without replacement
        colors = rng.sample(["red", "blue", "green", "yellow"], 3)
        counts = {c: rng.randint(3, 5) for c in colors}
        total = sum(counts.values())

        # Draw 2 without replacement, then roll a die
        t1 = rng.choice(colors)
        t2 = rng.choice(colors)
        die_target = rng.randint(1, 6)

        p1 = Fraction(counts[t1], total)
        if t1 == t2:
            p2 = Fraction(counts[t2] - 1, total - 1)
        else:
            p2 = Fraction(counts[t2], total - 1)
        p_die = Fraction(1, 6)
        prob = p1 * p2 * p_die

        items_desc = ", ".join(f"{counts[c]} {c}" for c in colors)

        stem = (f"A bag contains {items_desc} marbles ({total} total). "
                f"Two marbles are drawn without replacement, and then "
                f"a fair number cube (1-6) is rolled.")

        partA_prompt = (f"What is the probability of drawing a {t1} marble, "
                        f"then a {t2} marble (without replacement)?")
        partA_answer = _frac_str(p1 * p2)

        partB_prompt = (f"What is the probability of drawing a {t1} then "
                        f"a {t2} (without replacement) AND rolling a {die_target}?")
        partB_answer = _frac_str(prob)

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
                                         ItemType.MP, Difficulty.DIFFICULT, 4, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=ItemType.MP,
            stem_text=stem, stem_latex=stem,
            answer_text=f"A: {partA_answer} B: {partB_answer}",
            answer_latex=f"A: {partA_answer} B: {partB_answer}",
            worked_solution=f"Dependent draws then independent die: {_frac_str(p1)} x {_frac_str(p2)} x {_frac_str(p_die)} = {_frac_str(prob)}",
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
