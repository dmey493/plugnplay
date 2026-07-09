"""
Stem generator for 7.NS.6:
  Apply the inverse relationship between squaring and finding the square root
  of a perfect square whole number. Find square roots of perfect square whole numbers.

Content Limits:
  - Perfect square integers <= 400
  - Use either the square root symbol or the words "square root"
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: perfect squares < 100
  Medium: perfect squares 100-144
  Difficult: perfect squares 144-400

6 Stems from the Item Spec:
  Stem 1 (Below-MS):       Choose all numbers that are perfect squares (DOK 1, easy)
  Stem 2 (Approaching-NR): Calculate the square root of a perfect square (DOK 1, medium/difficult)
  Stem 3 (Approaching-MC): Evaluate sqrt(n) as multiple choice (DOK 1, easy)
  Stem 4 (At-MC):          Which expression has a value of k? (DOK 1, easy)
  Stem 5 (At-NR):          sqrt(x) = k, find x (DOK 1, difficult)
  Stem 6 (Above-MC):       Apply inverse relationship between squaring and square root (DOK 2, easy)
"""

import random
from fractions import Fraction

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.models import (
    GeneratedQuestion, QuestionChoice, QuestionPart,
    Difficulty, ProficiencyLevel, ItemType, RationalNumber,
    make_question_id
)
from engine.number_generators import NumberGenerator
from engine.context_pools import CONTEXTS_7NS6, pick_name


STANDARD_CODE = "7.NS.6"
VARIANTS_PER_STEM = 20


# ============================================================
# HELPERS
# ============================================================

# All perfect squares <= 400
PERFECT_SQUARES = {n * n: n for n in range(1, 21)}
# Roots: 1..20, squares: 1..400

# Non-perfect-square numbers useful for distractors
NON_PERFECT_SQUARES_SMALL = [n for n in range(2, 100) if n not in PERFECT_SQUARES]
NON_PERFECT_SQUARES_MED = [n for n in range(100, 400) if n not in PERFECT_SQUARES]


def _easy_squares():
    """Perfect squares < 100: 4, 9, 16, 25, 36, 49, 64, 81."""
    return [(n * n, n) for n in range(2, 10)]


def _medium_squares():
    """Perfect squares 100-144: 100, 121, 144."""
    return [(n * n, n) for n in range(10, 13)]


def _difficult_squares():
    """Perfect squares 144-400: 144, 169, 196, 225, 256, 289, 324, 361, 400."""
    return [(n * n, n) for n in range(12, 21)]


class Stem7NS6:
    """Generates ~20 variants for each of 6 stems from the 7.NS.6 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MS (DOK 1, Easy)
    # Choose all the numbers that are perfect squares
    # ================================================================

    def stem1_below_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        # Pick 2-3 perfect squares (correct) and 2-3 non-perfect squares (wrong)
        easy_sq = _easy_squares()
        num_correct = rng.choice([2, 3])
        num_wrong = 5 - num_correct

        correct_items = rng.sample(easy_sq, num_correct)
        correct_values = [sq for sq, _ in correct_items]

        # Pick non-perfect squares that are close to perfect squares (common traps)
        wrong_pool = [n for n in NON_PERFECT_SQUARES_SMALL if n <= 100]
        wrong_values = rng.sample(wrong_pool, num_wrong)

        all_values = [(v, True) for v in correct_values] + [(v, False) for v in wrong_values]
        rng.shuffle(all_values)

        choices = []
        for i, (val, is_correct) in enumerate(all_values):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=str(val), text_latex=f"${val}$",
                is_correct=is_correct,
            ))

        correct_letters = ", ".join(c.key for c in choices if c.is_correct)

        stem_text = "Choose all the numbers that are perfect squares."

        correct_explanations = []
        for sq, root in correct_items:
            correct_explanations.append(f"{sq} = {root}^2")

        worked = (
            f"A perfect square is a number that can be written as n^2 for some whole number n.\n"
            + "\n".join(correct_explanations) + "\n"
            + f"The other numbers are not perfect squares."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MS,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MS,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letters, answer_latex=correct_letters,
            worked_solution=worked,
            choices=choices, context_scenario="identify perfect squares",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - NR (DOK 1, Medium/Difficult)
    # Calculate the square root of a perfect square
    # e.g., "Calculate the square root of 256." -> 16
    # ================================================================

    def stem2_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        # Alternate difficulty: even variants medium, odd variants difficult
        if variant_idx % 2 == 0:
            pool = _medium_squares()
            difficulty = Difficulty.MEDIUM
        else:
            pool = _difficult_squares()
            difficulty = Difficulty.DIFFICULT

        sq, root = rng.choice(pool)

        stem_text = f"Calculate the square root of {sq}."
        answer_str = str(root)

        worked = (
            f"We need to find a number n such that n^2 = {sq}.\n"
            f"Since {root} x {root} = {sq}, the square root of {sq} is {root}."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               difficulty, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=difficulty, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_str, answer_latex=f"${answer_str}$",
            worked_solution=worked,
            context_scenario="calculate square root",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - MC (DOK 1, Easy)
    # Evaluate sqrt(n) with multiple choice
    # e.g., "What is the value of sqrt(25)?" -> 5
    # ================================================================

    def stem3_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        pool = _easy_squares()
        sq, root = rng.choice(pool)

        correct_str = str(root)

        # Distractors based on common student errors
        distractors = set()
        distractors.add(str(sq // 2))          # halving instead of square root
        distractors.add(str(root + 1))          # off by one
        distractors.add(str(root - 1))          # off by one
        distractors.add(str(sq // root + 1))    # near miss
        distractors.discard(correct_str)
        distractors.discard("0")

        dist_list = [d for d in distractors if d != correct_str and int(d) > 0]
        rng.shuffle(dist_list)
        dist_list = dist_list[:3]

        # If we need more distractors
        while len(dist_list) < 3:
            extra = root + rng.choice([2, 3, -2])
            if extra > 0 and str(extra) != correct_str and str(extra) not in dist_list:
                dist_list.append(str(extra))

        all_options = [(correct_str, True)] + [(d, False) for d in dist_list[:3]]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = f"What is the value of the square root of {sq}?"
        stem_latex = f"What is the value of $\\sqrt{{{sq}}}$?"

        worked = (
            f"The square root of {sq} is the number that, when multiplied by itself, equals {sq}.\n"
            f"Since {root} x {root} = {sq}, the square root of {sq} is {root}."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.EASY, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_latex,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="evaluate square root MC",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At Proficiency - MC (DOK 1, Easy/Medium)
    # Which expression has a value of k?
    # e.g., "Which expression has a value of 13?" -> sqrt(169)
    # ================================================================

    def stem4_at_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        # Pick a root value, then ask which expression equals it
        if variant_idx % 2 == 0:
            pool = _easy_squares()
            difficulty = Difficulty.EASY
        else:
            pool = _medium_squares() + _difficult_squares()
            difficulty = Difficulty.MEDIUM

        sq, root = rng.choice(pool)

        # Correct answer: sqrt(sq) = root
        correct_text = f"square root of {sq}"
        correct_latex = f"$\\sqrt{{{sq}}}$"

        # Distractors: expressions that do NOT equal root
        wrong_exprs = []

        # Wrong: sqrt of a nearby non-perfect-square
        for offset in [1, -1, 2, -2]:
            candidate = sq + offset
            if candidate > 0 and candidate not in PERFECT_SQUARES:
                wrong_exprs.append((f"square root of {candidate}", f"$\\sqrt{{{candidate}}}$"))
                break

        # Wrong: sqrt of a different perfect square
        other_squares = [(s, r) for s, r in PERFECT_SQUARES.items() if r != root and s <= 400]
        rng.shuffle(other_squares)
        for os_sq, os_root in other_squares[:2]:
            wrong_exprs.append((f"square root of {os_sq}", f"$\\sqrt{{{os_sq}}}$"))

        # Wrong: root^2 (confusing square with square root)
        wrong_exprs.append((f"{root}^2", f"${root}^2$"))

        rng.shuffle(wrong_exprs)
        wrong_exprs = wrong_exprs[:3]

        all_options = [((correct_text, correct_latex), True)]
        for wt, wl in wrong_exprs:
            all_options.append(((wt, wl), False))

        rng.shuffle(all_options)

        choices = []
        for i, ((text, latex), is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=latex,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = f"Which expression has a value of {root}?"
        stem_latex = f"Which expression has a value of ${root}$?"

        worked = (
            f"We need the expression that equals {root}.\n"
            f"The square root of {sq} = {root} because {root} x {root} = {sq}.\n"
            f"{root}^2 = {root * root}, which is {sq}, not {root}."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MC,
                               difficulty, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=difficulty, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_latex,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="identify expression with given value",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: At Proficiency - NR (DOK 1, Difficult)
    # sqrt(x) = k, find x
    # e.g., "An equation is given: sqrt(x) = 13. What is the value of x?"
    # -> 169
    # ================================================================

    def stem5_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        # Use difficult squares (larger values)
        pool = _difficult_squares()
        sq, root = rng.choice(pool)

        # Use a context from CONTEXTS_7NS6 sometimes
        use_context = rng.random() < 0.5 and variant_idx < 15

        if use_context:
            ctx = rng.choice(CONTEXTS_7NS6)
            name = pick_name(rng)
            context_text = ctx["template"].format(name=name, sq=sq)
            unit = ctx["unit"]

            stem_text = (
                f"{context_text}\n\n"
                f"Enter the side length in {unit}."
            )
            answer_str = str(root)

            worked = (
                f"The area of a square is side length squared: A = s^2.\n"
                f"If A = {sq}, then s = square root of {sq}.\n"
                f"Since {root} x {root} = {sq}, the side length is {root} {unit}."
            )
        else:
            stem_text = (
                f"An equation is given.\n\n"
                f"square root of x = {root}\n\n"
                f"What is the value of x?"
            )
            stem_latex = (
                f"An equation is given.\n\n"
                f"$\\sqrt{{x}} = {root}$\n\n"
                f"What is the value of $x$?"
            )
            answer_str = str(sq)

            worked = (
                f"If the square root of x = {root}, then x = {root}^2.\n"
                f"{root} x {root} = {sq}.\n"
                f"Therefore x = {sq}."
            )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.DIFFICULT, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT, dok=1, item_type=ItemType.NR,
            stem_text=stem_text,
            stem_latex=stem_latex if not use_context else stem_text,
            answer_text=answer_str, answer_latex=f"${answer_str}$",
            worked_solution=worked,
            context_scenario="inverse of square root" if not use_context else "square area context",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    # STEM 6: Above Proficiency - MC (DOK 2, Easy)
    # Apply the inverse relationship between squaring and square roots
    # e.g., "What is (sqrt(25))^2?" or "A square has area 64.
    #         The side length is doubled. What is the new area?"
    # ================================================================

    def stem6_above_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)

        name = pick_name(rng)
        pool = _easy_squares()  # Easy difficulty per item spec

        fmt = variant_idx % 4

        if fmt == 0:
            # Format A: What is (sqrt(n))^2?
            sq, root = rng.choice(pool)
            correct_text = str(sq)
            dist_set = {str(root), str(sq * 2), str(root * 2)}
            dist_set.discard(correct_text)
            distractors = list(dist_set)[:3]
            while len(distractors) < 3:
                d = str(rng.randint(2, 100))
                if d != correct_text and d not in distractors:
                    distractors.append(d)
            stem_text = (
                f"What is the value of (square root of {sq})^2?"
            )
            worked = (
                f"square root of {sq} = {root}\n"
                f"({root})^2 = {sq}\n"
                f"Squaring undoes the square root, so (square root of {sq})^2 = {sq}."
            )

        elif fmt == 1:
            # Format B: Area of square doubled side length
            sq, root = rng.choice([(n * n, n) for n in range(2, 8)])
            new_side = root * 2
            new_area = new_side * new_side
            correct_text = str(new_area)
            dist_set = {str(sq * 2), str(sq * 4), str(root * 4)}
            dist_set.discard(correct_text)
            distractors = list(dist_set)[:3]
            while len(distractors) < 3:
                d = str(rng.randint(10, 400))
                if d != correct_text and d not in distractors:
                    distractors.append(d)
            stem_text = (
                f"A square has an area of {sq} square feet.\n\n"
                f"{name} builds a new square with side lengths that are "
                f"double the original. What is the area of the new square "
                f"in square feet?"
            )
            worked = (
                f"Original area = {sq}, so side = square root of {sq} = {root} ft.\n"
                f"New side = 2 x {root} = {new_side} ft.\n"
                f"New area = {new_side}^2 = {new_area} sq ft."
            )

        elif fmt == 2:
            # Format C: Which shows the inverse relationship?
            sq, root = rng.choice(pool)
            correct_text = f"(square root of {sq})^2 = {sq}"
            distractors = [
                f"square root of {sq} = {sq}",
                f"{root}^2 = {root}",
                f"square root of {root} = {sq}",
            ]
            stem_text = (
                f"Squaring and finding the square root are inverse operations.\n\n"
                f"Which equation shows this relationship?"
            )
            worked = (
                f"Inverse operations undo each other.\n"
                f"square root of {sq} = {root}, and {root}^2 = {sq}.\n"
                f"So (square root of {sq})^2 = {sq} demonstrates the inverse relationship."
            )

        else:
            # Format D: sqrt(k^2) = ?
            root = rng.randint(2, 15)
            sq = root * root
            correct_text = str(root)
            dist_set = {str(sq), str(root * 2), str(root + 1)}
            dist_set.discard(correct_text)
            distractors = list(dist_set)[:3]
            while len(distractors) < 3:
                d = str(rng.randint(2, 20))
                if d != correct_text and d not in distractors:
                    distractors.append(d)
            stem_text = (
                f"What is the value of square root of ({root}^2)?"
            )
            worked = (
                f"{root}^2 = {sq}\n"
                f"square root of {sq} = {root}\n"
                f"The square root undoes the squaring, so the answer is {root}."
            )

        all_options = [(correct_text, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MC,
                               Difficulty.EASY, 6, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices,
            context_scenario="inverse relationship squaring and square root",
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6, variant_index=variant_idx,
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_ms,
            self.stem2_approaching_nr,
            self.stem3_approaching_mc,
            self.stem4_at_mc,
            self.stem5_at_nr,
            self.stem6_above_mc,
        ]
        for stem_fn in stem_methods:
            for v in range(variants_per_stem):
                try:
                    all_questions.append(stem_fn(v))
                except Exception as e:
                    print(f"Error generating {stem_fn.__name__} variant {v}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
        return all_questions

    def generate_stem_variants(self, stem_index: int,
                                variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        stem_methods = {
            1: self.stem1_below_ms,
            2: self.stem2_approaching_nr,
            3: self.stem3_approaching_mc,
            4: self.stem4_at_mc,
            5: self.stem5_at_nr,
            6: self.stem6_above_mc,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-6.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 7.NS.6 question variants...")
    print("=" * 60)

    generator = Stem7NS6(seed=42)
    all_questions = generator.generate_all_variants(variants_per_stem=3)

    for q in all_questions:
        print(f"\n{'='*60}")
        print(f"ID: {q.question_id}")
        print(f"Stem {q.stem_index} | {q.proficiency_level.value} | {q.difficulty.value} | DOK {q.dok} | {q.item_type.value}")
        print(f"\n{q.stem_text}")
        if q.choices:
            for c in q.choices:
                marker = " *" if c.is_correct else ""
                print(f"  {c.key}. {c.text}{marker}")
        print(f"\nAnswer: {q.answer_text}")
        print(f"\nWorked Solution:\n{q.worked_solution}")

    print(f"\n{'='*60}")
    print(f"Total questions generated: {len(all_questions)}")
