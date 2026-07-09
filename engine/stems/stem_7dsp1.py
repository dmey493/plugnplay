"""
Stem generator for 7.DSP.1:
  Understand that statistics can be used to gain information about a population
  by examining a sample. Understand that conclusions and generalizations about
  a population from a sample are valid only if the sample is representative
  and that random sampling tends to produce representative samples.

Content Limits:
  - Use grade-appropriate context
  - Real-world problems at each PLD level
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: No sub-populations mentioned
  Medium: Sub-populations of equal size
  Difficult: Sub-populations based on two categories, unequal size

4 Stems:
  Stem 1 (Below-MC, DOK 1):       Identify appropriate sampling method
  Stem 2 (Approaching-MC, DOK 1-2): Identify if method produces representative sample
  Stem 3 (At-MC, DOK 2):          Determine if conclusion is valid based on sampling
  Stem 4 (Above-MP, DOK 3):       Justify/critique inferences about populations
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
from engine.context_pools import pick_name


STANDARD_CODE = "7.DSP.1"
VARIANTS_PER_STEM = 20


# --- Scenario pools ---

POPULATIONS = [
    ("students at Lincoln Middle School", "students"),
    ("residents of a city", "residents"),
    ("customers at a grocery store", "customers"),
    ("voters in a town", "voters"),
    ("employees at a company", "employees"),
    ("members of a fitness club", "members"),
    ("fans at a basketball game", "fans"),
    ("patients at a dental clinic", "patients"),
    ("families in a neighborhood", "families"),
    ("shoppers at a mall", "shoppers"),
]

TOPICS = [
    ("favorite lunch option", ["pizza", "tacos", "salad", "sandwich"]),
    ("preferred after-school activity", ["sports", "art", "music", "reading"]),
    ("favorite season", ["spring", "summer", "fall", "winter"]),
    ("preferred mode of transportation to school", ["bus", "car", "bike", "walk"]),
    ("favorite subject", ["math", "science", "English", "history"]),
    ("preferred type of movie", ["comedy", "action", "animated", "drama"]),
    ("favorite type of pet", ["dog", "cat", "fish", "bird"]),
    ("preferred weekend activity", ["sports", "gaming", "shopping", "hiking"]),
]

SAMPLING_METHODS = {
    "random": [
        "randomly selects {n} {unit} from a list of all {population}",
        "assigns each {unit_s} a number and uses a random number generator to pick {n}",
        "puts all names in a hat and draws {n} names",
        "uses a computer to randomly select {n} {unit} from the full list",
    ],
    "biased": [
        "surveys only {unit} who are in the cafeteria at lunch",
        "surveys only the first {n} {unit} who arrive in the morning",
        "surveys only {unit} in one classroom",
        "surveys only {unit} who volunteer to participate",
        "surveys only {unit} who are on the soccer team",
        "asks only friends to respond to the survey",
    ],
}


def _fmt(val, decimals=1):
    f = float(val)
    if f == int(f):
        return str(int(f))
    return f"{f:.{decimals}f}".rstrip('0').rstrip('.')


class Stem7DSP1:
    """Generates 20 variants for each of 4 stems from the 7.DSP.1 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx, variant_idx):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ----------------------------------------------------------------
    # Stem 1: Below – Identify appropriate sampling method (MC, DOK 1)
    # ----------------------------------------------------------------
    def _stem1(self, variant_idx):
        gen, rng = self._make_gen(1, variant_idx)
        pop_desc, unit = rng.choice(POPULATIONS)
        topic, options = rng.choice(TOPICS)
        n = rng.choice([20, 25, 30, 40, 50])
        unit_s = unit.rstrip('s')  # singular

        # Correct = random method
        correct_method = rng.choice(SAMPLING_METHODS["random"]).format(
            n=n, unit=unit, unit_s=unit_s, population=pop_desc)
        biased_methods = [m.format(n=n, unit=unit, unit_s=unit_s, population=pop_desc)
                          for m in rng.sample(SAMPLING_METHODS["biased"], 3)]

        stem = (f"A researcher wants to find out the {topic} of {pop_desc}. "
                f"Which sampling method would best represent the entire population?")

        all_choices = [(correct_method, True)] + [(m, False) for m in biased_methods]
        rng.shuffle(all_choices)
        keys = "abcd"
        choices = []
        answer_key = ""
        for i, (text, correct) in enumerate(all_choices):
            c = QuestionChoice(key=keys[i], text=text, text_latex=text, is_correct=correct)
            choices.append(c)
            if correct:
                answer_key = keys[i]

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW,
                                         ItemType.MC, Difficulty.EASY, 1, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY,
            dok=1,
            item_type=ItemType.MC,
            stem_text=stem,
            stem_latex=stem,
            answer_text=f"{answer_key}",
            answer_latex=f"{answer_key}",
            worked_solution=(f"Random sampling gives every member of the population an equal "
                             f"chance of being selected, which produces a representative sample."),
            choices=choices,
            seed=gen.seed, stem_index=1, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 2: Approaching – Identify if method is representative (MC, DOK 1-2)
    # ----------------------------------------------------------------
    def _stem2(self, variant_idx):
        gen, rng = self._make_gen(2, variant_idx)
        pop_desc, unit = rng.choice(POPULATIONS)
        topic, _ = rng.choice(TOPICS)
        n = rng.choice([15, 20, 25, 30, 50])
        unit_s = unit.rstrip('s')

        is_random = rng.choice([True, False])
        if is_random:
            method_desc = rng.choice(SAMPLING_METHODS["random"]).format(
                n=n, unit=unit, unit_s=unit_s, population=pop_desc)
        else:
            method_desc = rng.choice(SAMPLING_METHODS["biased"]).format(
                n=n, unit=unit, unit_s=unit_s, population=pop_desc)

        stem = (f"To find out the {topic} of {pop_desc}, a researcher "
                f"{method_desc}. Is this sample likely to be representative "
                f"of the entire population?")

        if is_random:
            correct = "Yes, because every member had an equal chance of being selected."
            wrong = [
                "No, because the sample is too small.",
                "No, because the researcher should have asked everyone.",
                "Yes, but only if the population is small enough.",
            ]
        else:
            correct = "No, because the sample does not give every member an equal chance of being selected."
            wrong = [
                "Yes, because any sample can represent the population.",
                "Yes, because the researcher collected enough responses.",
                "No, because surveys are never reliable.",
            ]

        all_choices = [(correct, True)] + [(w, False) for w in wrong]
        rng.shuffle(all_choices)
        keys = "abcd"
        choices = []
        answer_key = ""
        for i, (text, is_correct) in enumerate(all_choices):
            choices.append(QuestionChoice(key=keys[i], text=text, text_latex=text, is_correct=is_correct))
            if is_correct:
                answer_key = keys[i]

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING,
                                         ItemType.MC, Difficulty.MEDIUM, 2, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM,
            dok=2,
            item_type=ItemType.MC,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_key, answer_latex=answer_key,
            worked_solution=(f"A representative sample requires random selection so every member "
                             f"has an equal chance. {'This method is random.' if is_random else 'This method is biased.'}"),
            choices=choices,
            seed=gen.seed, stem_index=2, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 3: At – Determine if conclusion is valid (MC, DOK 2)
    # ----------------------------------------------------------------
    def _stem3(self, variant_idx):
        gen, rng = self._make_gen(3, variant_idx)
        pop_desc, unit = rng.choice(POPULATIONS)
        topic, options = rng.choice(TOPICS)
        n = rng.choice([30, 40, 50, 60, 100])

        is_valid = rng.choice([True, False])
        if is_valid:
            method = f"randomly selected {n} {unit}"
        else:
            biased = rng.choice(SAMPLING_METHODS["biased"]).format(
                n=n, unit=unit, unit_s=unit.rstrip('s'), population=pop_desc)
            method = biased

        winner = rng.choice(options)
        pct = rng.randint(30, 55)

        stem = (f"A survey of {pop_desc} found that {pct}% preferred {winner} as "
                f"their {topic}. The researcher {method}. Which conclusion is valid?")

        if is_valid:
            correct = f"About {pct}% of all {unit} likely prefer {winner} because the sample was random."
            wrong = [
                f"Exactly {pct}% of all {unit} prefer {winner}.",
                f"The survey cannot tell us anything about the population.",
                f"The result only applies to the {n} {unit} surveyed.",
            ]
        else:
            correct = f"The conclusion may not apply to all {unit} because the sample was not random."
            wrong = [
                f"About {pct}% of all {unit} likely prefer {winner}.",
                f"The sample size was too small to draw any conclusion.",
                f"The conclusion is valid because {n} {unit} is a large sample.",
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
            difficulty=Difficulty.MEDIUM,
            dok=2,
            item_type=ItemType.MC,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_key, answer_latex=answer_key,
            worked_solution=(f"A valid generalization requires a random sample. "
                             f"{'The sample was random so the conclusion is valid.' if is_valid else 'The sample was biased so the conclusion may not be valid.'}"),
            choices=choices,
            seed=gen.seed, stem_index=3, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 4: Above – Justify/critique inference (MP, DOK 3)
    # ----------------------------------------------------------------
    def _stem4(self, variant_idx):
        gen, rng = self._make_gen(4, variant_idx)
        pop_desc, unit = rng.choice(POPULATIONS)
        topic, options = rng.choice(TOPICS)
        n = rng.choice([40, 50, 75, 100])

        winner = rng.choice(options)
        pct = rng.randint(35, 60)

        # Part A: Was the sampling method appropriate?
        is_random = rng.choice([True, False])
        if is_random:
            method = f"randomly selected {n} {unit} from the full population"
            partA_answer = "Yes, the sample is likely representative because it was randomly selected."
        else:
            bias_desc = rng.choice([
                f"surveyed only {unit} who were in the gym",
                f"asked only {unit} who volunteered",
                f"surveyed the first {n} {unit} to arrive",
            ])
            method = bias_desc
            partA_answer = "No, the sample may not be representative because it was not randomly selected."

        # Part B: What would improve the study?
        if is_random:
            partB_answer = f"Increase the sample size to get more precise results, or repeat the study to confirm."
        else:
            partB_answer = f"Use random sampling to ensure every member has an equal chance of being selected."

        partA_prompt = "Is the researcher's sampling method likely to produce a representative sample? Explain."
        partB_prompt = "What could the researcher do to improve the validity of the study?"

        stem = (f"A researcher wants to determine the {topic} of {pop_desc}. "
                f"The researcher {method} and found that {pct}% preferred {winner}.\n\n"
                f"Part A: {partA_prompt}\n\n"
                f"Part B: {partB_prompt}")

        parts = [
            QuestionPart(
                label="Part A",
                prompt=partA_prompt, prompt_latex=partA_prompt,
                answer=partA_answer, answer_latex=partA_answer,
                item_type=ItemType.ER,
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
                                         ItemType.MP, Difficulty.DIFFICULT, 4, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT,
            dok=3,
            item_type=ItemType.MP,
            stem_text=stem, stem_latex=stem,
            answer_text=f"A: {partA_answer} B: {partB_answer}",
            answer_latex=f"A: {partA_answer} B: {partB_answer}",
            worked_solution=f"Part A: {partA_answer} Part B: {partB_answer}",
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
