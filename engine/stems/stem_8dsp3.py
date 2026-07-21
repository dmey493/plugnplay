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


# Compound events over a coin flip + number cube sample space,
# shared by the list and table representations of Stem 1.
_COIN_CUBE_EVENTS = [
    ("flipping heads and rolling an even number",
     lambda c, n: c == "H" and n % 2 == 0),
    ("flipping tails and rolling a number greater than 4",
     lambda c, n: c == "T" and n > 4),
    ("flipping heads and rolling a 3",
     lambda c, n: c == "H" and n == 3),
    ("flipping tails and rolling a number less than 3",
     lambda c, n: c == "T" and n < 3),
]


class Stem8DSP3:
    """Generates 20 variants for each of 4 stems from the 8.DSP.3 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx, variant_idx):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ----------------------------------------------------------------
    # Stem 1: Below – Sample spaces (MC, DOK 2)
    # Representation rotates across variants per the standard
    # ("organized lists, tables, and tree diagrams"):
    #   variant % 3 == 0 -> tree diagram
    #   variant % 3 == 1 -> organized list in the stem text
    #   variant % 3 == 2 -> table (data_table render)
    # ----------------------------------------------------------------
    @staticmethod
    def _build_mc(correct, candidates, rng, fallback):
        """Build 4 unique MC choices (1 correct + 3 unique distractors)."""
        seen = {correct}
        wrong = []
        for c in candidates:
            if len(wrong) == 3:
                break
            if c not in seen:
                seen.add(c)
                wrong.append(c)
        while len(wrong) < 3:
            c = fallback()
            if c not in seen:
                seen.add(c)
                wrong.append(c)
        all_choices = [(correct, True)] + [(w, False) for w in wrong]
        rng.shuffle(all_choices)
        keys = "abcd"
        choices = []
        answer_key = ""
        for i, (text, is_c) in enumerate(all_choices):
            choices.append(QuestionChoice(key=keys[i], text=text, text_latex=text, is_correct=is_c))
            if is_c:
                answer_key = keys[i]
        return choices, answer_key

    def _stem1(self, variant_idx):
        gen, rng = self._make_gen(1, variant_idx)
        rep = variant_idx % 3
        if rep == 1:
            return self._stem1_list(gen, rng, variant_idx)
        if rep == 2:
            return self._stem1_table(gen, rng, variant_idx)
        return self._stem1_tree(gen, rng, variant_idx)

    def _stem1_tree(self, gen, rng, variant_idx):
        """Tree-diagram representation: count outcomes in the sample space."""
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

        stem = (f"{desc}. The tree diagram shows the sample space. [FIGURE] "
                f"How many outcomes are in the sample space?")

        correct = str(total)
        candidates = [
            str(len(stage1) + len(stage2)),
            str(total + len(stage1)),
            str(total - 1),
        ]
        choices, answer_key = self._build_mc(
            correct, candidates, rng,
            lambda: str(rng.randint(2, total + 8)))

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

    def _stem1_list(self, gen, rng, variant_idx):
        """Organized-list representation: sample space enumerated in the stem."""
        scenario = rng.choice(["coin_cube", "spinner_coin"])

        if scenario == "coin_cube":
            outcomes = [(c, n) for c in ("H", "T") for n in range(1, 7)]
            labels = [f"{c}{n}" for c, n in outcomes]
            desc = ("A coin is flipped and a number cube (1-6) is rolled. "
                    "The organized list shows the sample space")
            events = _COIN_CUBE_EVENTS
            n1, n2 = 2, 6
        else:
            colors = rng.sample(["Red", "Blue", "Green", "Yellow"], 3)
            outcomes = [(col, f) for col in colors for f in ("H", "T")]
            labels = [f"{col}-{f}" for col, f in outcomes]
            target = rng.choice(colors)
            desc = (f"A spinner with equal sections {', '.join(colors)} is spun "
                    f"and a coin is flipped. The organized list shows the sample space")
            events = [
                (f"the spinner landing on {target} and the coin showing heads",
                 lambda col, f, t=target: col == t and f == "H"),
                (f"the spinner landing on {target} and the coin showing tails",
                 lambda col, f, t=target: col == t and f == "T"),
            ]
            n1, n2 = len(colors), 2

        total = len(outcomes)
        list_str = ", ".join(labels)
        q_type = rng.choice(["count", "prob"])

        if q_type == "count":
            question = "How many outcomes are in the sample space?"
            correct = str(total)
            candidates = [str(n1 + n2), str(total - 1), str(total + 2)]
            fallback = lambda: str(rng.randint(2, total + 8))
            worked = f"Count the outcomes in the list: {n1} x {n2} = {total} outcomes."
        else:
            event_desc, pred = rng.choice(events)
            fav = sum(1 for o in outcomes if pred(*o))
            prob = Fraction(fav, total)
            correct = _frac_str(prob)
            question = f"What is the probability of {event_desc}?"
            wrong_fracs = [Fraction(fav + 1, total), Fraction(1, total),
                           Fraction(fav, n1 + n2)]
            candidates = [_frac_str(f) for f in wrong_fracs if f != prob]
            fallback = lambda: _frac_str(Fraction(rng.randint(1, total - 1), total))
            worked = (f"{fav} of the {total} equally likely outcomes in the list "
                      f"match the event, so P = {fav}/{total}"
                      + (f" = {correct}." if correct != f"{fav}/{total}" else "."))

        choices, answer_key = self._build_mc(correct, candidates, rng, fallback)

        stem = f"{desc}: {list_str}. {question}"

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW,
                                         ItemType.MC, Difficulty.EASY, 1, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_key, answer_latex=answer_key,
            worked_solution=worked,
            choices=choices,
            seed=gen.seed, stem_index=1, variant_index=variant_idx,
        )

    def _stem1_table(self, gen, rng, variant_idx):
        """Table representation: outcome grid or sum table as a data_table."""
        scenario = rng.choice(["sum_table", "coin_cube_grid"])

        if scenario == "sum_table":
            headers = ["+", "1", "2", "3", "4", "5", "6"]
            rows = [[str(r)] + [str(r + c) for c in range(1, 7)] for r in range(1, 7)]
            desc = ("Two number cubes are rolled. The table shows the sum of the "
                    "two cubes for every outcome in the sample space.")
            q_type = rng.choice(["count", "count_event", "prob"])
            s = rng.randint(3, 11)
            fav = 6 - abs(7 - s)
            if q_type == "count":
                question = "How many outcomes are in the sample space?"
                correct = "36"
                candidates = ["12", "11", "21"]
                fallback = lambda: str(rng.randint(6, 48))
                worked = "The table has 6 rows x 6 columns = 36 outcomes."
            elif q_type == "count_event":
                question = f"How many outcomes have a sum of {s}?"
                correct = str(fav)
                candidates = [str(fav + 1), str(fav - 1), str(s)]
                fallback = lambda: str(rng.randint(1, 12))
                worked = f"Count the cells in the table equal to {s}: there are {fav}."
            else:
                prob = Fraction(fav, 36)
                correct = _frac_str(prob)
                question = f"What is the probability that the sum is {s}?"
                wrong_fracs = [Fraction(fav + 1, 36), Fraction(s, 36),
                               Fraction(fav, 12)]
                candidates = [_frac_str(f) for f in wrong_fracs if f != prob]
                fallback = lambda: _frac_str(Fraction(rng.randint(1, 35), 36))
                worked = (f"{fav} of the 36 cells in the table show a sum of {s}, "
                          f"so P(sum = {s}) = {fav}/36 = {correct}.")
        else:
            headers = ["", "1", "2", "3", "4", "5", "6"]
            rows = [["H"] + [f"H{n}" for n in range(1, 7)],
                    ["T"] + [f"T{n}" for n in range(1, 7)]]
            desc = ("A coin is flipped and a number cube (1-6) is rolled. "
                    "The table shows every outcome in the sample space.")
            outcomes = [(c, n) for c in ("H", "T") for n in range(1, 7)]
            q_type = rng.choice(["count", "prob"])
            if q_type == "count":
                question = "How many outcomes are in the sample space?"
                correct = "12"
                candidates = ["8", "6", "11"]
                fallback = lambda: str(rng.randint(2, 18))
                worked = "The table has 2 rows x 6 columns = 12 outcomes."
            else:
                event_desc, pred = rng.choice(_COIN_CUBE_EVENTS)
                fav = sum(1 for o in outcomes if pred(*o))
                prob = Fraction(fav, 12)
                correct = _frac_str(prob)
                question = f"What is the probability of {event_desc}?"
                wrong_fracs = [Fraction(fav + 1, 12), Fraction(1, 12),
                               Fraction(fav, 8)]
                candidates = [_frac_str(f) for f in wrong_fracs if f != prob]
                fallback = lambda: _frac_str(Fraction(rng.randint(1, 11), 12))
                worked = (f"{fav} of the 12 outcomes in the table match the event, "
                          f"so P = {fav}/12 = {correct}.")

        choices, answer_key = self._build_mc(correct, candidates, rng, fallback)

        stem = f"{desc} [FIGURE] {question}"

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW,
                                         ItemType.MC, Difficulty.EASY, 1, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_key, answer_latex=answer_key,
            worked_solution=worked,
            choices=choices,
            render_data={"type": "data_table", "headers": headers, "rows": rows},
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
