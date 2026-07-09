"""
Stem generator for 8.DSP.4:
  Define the probability of a compound event as the fraction of outcomes in the
  sample space for which the compound event occurs. Use appropriate terminology
  to describe independent, dependent, complementary, and mutually exclusive events.

Content Limits:
  - Fractions only (no percentages)
  - If deck of cards: include total (52) and type counts
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: Identify type of event only
  Medium: Identify type AND probability (3 objects/2 events or 2 objects/3 events)
  Difficult: Identify type AND probability (3+ objects/3 events)

4 Stems:
  Stem 1 (Below-MC, DOK 1):       Identify event type
  Stem 2 (Approaching-MC, DOK 1): Identify fraction expression for compound event
  Stem 3 (At-NR, DOK 2-3):        Calculate probability of compound event
  Stem 4 (Above-MP, DOK 3):       Analyze errors in probability calculations
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


STANDARD_CODE = "8.DSP.4"
VARIANTS_PER_STEM = 20


# Event type scenarios
EVENT_SCENARIOS = {
    "independent": [
        ("Flipping a coin and rolling a number cube",
         "The outcome of the coin does not affect the number cube."),
        ("Drawing a card from a deck, replacing it, and drawing again",
         "Since the card is replaced, the second draw is not affected."),
        ("Spinning a spinner and rolling a die",
         "The spinner result does not affect the die roll."),
        ("Choosing a marble from a bag, replacing it, then choosing again",
         "With replacement, each draw is independent."),
    ],
    "dependent": [
        ("Drawing two cards from a deck without replacement",
         "The first draw changes the remaining cards for the second draw."),
        ("Choosing two marbles from a bag without replacement",
         "Removing the first marble changes the probability for the second."),
        ("Selecting two students from a class without replacement",
         "After the first student is selected, there are fewer students remaining."),
    ],
    "complementary": [
        ("Rolling a 5 on a number cube vs. not rolling a 5",
         "These events account for all outcomes and cannot both occur."),
        ("Drawing a red card vs. drawing a non-red card from a deck",
         "Every card is either red or non-red; the events cover all outcomes."),
        ("It will rain tomorrow vs. it will not rain tomorrow",
         "One event must occur, and they cannot both happen."),
    ],
    "mutually_exclusive": [
        ("Rolling a 2 and rolling a 5 on a single number cube",
         "You cannot roll both a 2 and a 5 on one roll."),
        ("Drawing a king and drawing a queen from a single draw",
         "A single card cannot be both a king and a queen."),
        ("Landing on red and landing on blue on a single spin",
         "The spinner lands on exactly one color per spin."),
    ],
}

# Probability calculation scenarios
PROB_SCENARIOS = [
    {"desc": "A bag contains {r} red, {b} blue, and {g} green marbles",
     "total_fn": lambda r, b, g: r + b + g,
     "items": ["red", "blue", "green"]},
]


def _frac_str(f):
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


class Stem8DSP4:
    """Generates 20 variants for each of 4 stems from the 8.DSP.4 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx, variant_idx):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ----------------------------------------------------------------
    # Stem 1: Below – Identify event type (MC, DOK 1)
    # ----------------------------------------------------------------
    def _stem1(self, variant_idx):
        gen, rng = self._make_gen(1, variant_idx)

        event_type = rng.choice(["independent", "dependent", "complementary", "mutually_exclusive"])
        scenario, explanation = rng.choice(EVENT_SCENARIOS[event_type])

        display_type = event_type.replace("_", " ")
        stem = f"Which type of event is described? {scenario}."

        options = ["independent", "dependent", "complementary", "mutually exclusive"]
        correct = display_type
        wrong = [o for o in options if o != correct]
        rng.shuffle(wrong)

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
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_key, answer_latex=answer_key,
            worked_solution=f"This is {display_type}. {explanation}",
            choices=choices,
            seed=gen.seed, stem_index=1, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 2: Approaching – Identify fraction expression for compound event (MC, DOK 1)
    # ----------------------------------------------------------------
    def _stem2(self, variant_idx):
        gen, rng = self._make_gen(2, variant_idx)

        # Independent: P(A and B) = P(A) * P(B)
        # Use marbles with replacement
        colors = rng.sample(["red", "blue", "green", "yellow", "purple"], 3)
        counts = {c: rng.randint(2, 5) for c in colors}
        total = sum(counts.values())
        target1, target2 = rng.sample(colors, 2)

        p1 = Fraction(counts[target1], total)
        p2 = Fraction(counts[target2], total)

        items_desc = ", ".join(f"{counts[c]} {c}" for c in colors)
        stem = (f"A bag contains {items_desc} marbles ({total} total). "
                f"A marble is drawn, replaced, then another is drawn. "
                f"Which expression represents the probability of drawing "
                f"a {target1} marble then a {target2} marble?")

        correct = f"{_frac_str(p1)} x {_frac_str(p2)}"

        # Distractors
        wrong = []
        wrong.append(f"{_frac_str(p1)} + {_frac_str(p2)}")
        # Without replacement distractor
        p2_dep = Fraction(counts[target2], total - 1)
        wrong.append(f"{_frac_str(p1)} x {_frac_str(p2_dep)}")
        wrong.append(f"{_frac_str(Fraction(counts[target1] + counts[target2], total))}")

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
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING,
                                         ItemType.MC, Difficulty.MEDIUM, 2, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.MC,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_key, answer_latex=answer_key,
            worked_solution=(f"With replacement: P({target1}) = {_frac_str(p1)}, "
                             f"P({target2}) = {_frac_str(p2)}. "
                             f"P(both) = {_frac_str(p1)} x {_frac_str(p2)}."),
            choices=choices,
            seed=gen.seed, stem_index=2, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 3: At – Calculate probability of compound event (NR, DOK 2-3)
    # ----------------------------------------------------------------
    def _stem3(self, variant_idx):
        gen, rng = self._make_gen(3, variant_idx)

        # Dependent event (without replacement)
        colors = rng.sample(["red", "blue", "green", "yellow"], 3)
        counts = {c: rng.randint(3, 6) for c in colors}
        total = sum(counts.values())
        target1 = rng.choice(colors)
        target2 = rng.choice(colors)

        p1 = Fraction(counts[target1], total)
        if target1 == target2:
            p2 = Fraction(counts[target2] - 1, total - 1)
        else:
            p2 = Fraction(counts[target2], total - 1)
        answer = p1 * p2

        items_desc = ", ".join(f"{counts[c]} {c}" for c in colors)
        if target1 == target2:
            stem = (f"A bag contains {items_desc} marbles ({total} total). "
                    f"Two marbles are drawn without replacement. "
                    f"What is the probability that both marbles are {target1}? "
                    f"Express your answer as a fraction.")
        else:
            stem = (f"A bag contains {items_desc} marbles ({total} total). "
                    f"Two marbles are drawn without replacement. "
                    f"What is the probability of drawing a {target1} marble "
                    f"then a {target2} marble? Express your answer as a fraction.")

        answer_str = _frac_str(answer)
        worked = (f"P(1st {target1}) = {_frac_str(p1)}. "
                  f"After removing 1 {'same' if target1 == target2 else target1}: "
                  f"P(2nd {target2}) = {_frac_str(p2)}. "
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
    # Stem 4: Above – Analyze errors in probability calculations (MP, DOK 3)
    # ----------------------------------------------------------------
    def _stem4(self, variant_idx):
        gen, rng = self._make_gen(4, variant_idx)

        # Setup: student makes a common error
        colors = rng.sample(["red", "blue", "green", "yellow", "orange"], 3)
        counts = {c: rng.randint(2, 5) for c in colors}
        total = sum(counts.values())
        target1 = rng.choice(colors)
        target2 = rng.choice(colors)

        # Correct answer (without replacement)
        p1 = Fraction(counts[target1], total)
        if target1 == target2:
            p2_correct = Fraction(counts[target2] - 1, total - 1)
        else:
            p2_correct = Fraction(counts[target2], total - 1)
        correct_answer = p1 * p2_correct

        # Common error: using replacement probability
        p2_wrong = Fraction(counts[target2], total)
        wrong_answer = p1 * p2_wrong

        items_desc = ", ".join(f"{counts[c]} {c}" for c in colors)
        scenario = (f"A bag contains {items_desc} marbles ({total} total). "
                    f"Two marbles are drawn without replacement.")

        stem = (f"{scenario} A student calculates the probability of drawing "
                f"a {target1} then a {target2} marble as {_frac_str(wrong_answer)}. "
                f"Answer the following questions about the student's work.")

        partA_prompt = "Identify the error the student made."
        partA_answer = (f"The student used {_frac_str(p2_wrong)} for the second draw "
                        f"instead of {_frac_str(p2_correct)}. Without replacement, "
                        f"the total changes from {total} to {total - 1}.")

        partB_prompt = "Calculate the correct probability."
        partB_answer = _frac_str(correct_answer)

        parts = [
            QuestionPart(
                label="Part A", prompt=partA_prompt, prompt_latex=partA_prompt,
                answer=partA_answer, answer_latex=partA_answer, item_type=ItemType.MC,
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
            worked_solution=f"Error: used replacement. Correct: P = {_frac_str(p1)} x {_frac_str(p2_correct)} = {_frac_str(correct_answer)}",
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
