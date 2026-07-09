"""
Stem generator for 8.GM.3:
  Apply the Pythagorean Theorem to determine unknown side lengths
  in right triangles in real-world and mathematical problems.

Content Limits:
  - No simplified radicals (answers are perfect squares or decimal approximations)
  - Calculator: ALLOWED
  - Answers rounded to the nearest hundredth when not perfect squares

Difficulty Tiers:
  Easy: Pythagorean triples (whole-number answers), model provided
  Medium: Scaled triples or one-step application, model provided
  Difficult: Non-perfect-square answers (round to hundredth), no model

4 Stems from the Item Spec:
  Stem 1 (Below-MC):       Identify the correct Pythagorean equation for a triangle (DOK 1, Easy)
  Stem 2 (Approaching-NR): Find the missing side length (DOK 1, Easy/Medium)
  Stem 3 (At-NR):          Real-world Pythagorean theorem problem (DOK 2, Medium/Difficult)
  Stem 4 (Above-MP):       Two-part compound shape problem (DOK 2, Medium)
"""

import random
import math
from fractions import Fraction

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.models import (
    GeneratedQuestion, QuestionChoice, QuestionPart,
    Difficulty, ProficiencyLevel, ItemType,
    make_question_id
)
from engine.number_generators import NumberGenerator
from engine.context_pools import pick_name
from engine.svg_helpers import right_triangle_svg


STANDARD_CODE = "8.GM.3"
VARIANTS_PER_STEM = 20


# ============================================================
# HELPERS
# ============================================================

# Common Pythagorean triples (a, b, c) where a^2 + b^2 = c^2
PYTHAGOREAN_TRIPLES = [
    (3, 4, 5),
    (5, 12, 13),
    (8, 15, 17),
    (7, 24, 25),
    (6, 8, 10),
    (9, 12, 15),
    (12, 16, 20),
    (15, 20, 25),
    (10, 24, 26),
    (20, 21, 29),
]

# Scale factors for medium difficulty
SCALE_FACTORS = [2, 3, 4, 5]

# Real-world contexts for Stem 3
REAL_WORLD_CONTEXTS = [
    {
        "scenario": "ladder",
        "template": "{name} leans a {c}-foot ladder against a wall. The base of the ladder is {a} feet from the wall.",
        "question": "How high up the wall does the ladder reach?",
        "missing": "b",  # find leg (wall height)
        "unit": "feet",
    },
    {
        "scenario": "walking_path",
        "template": "{name} walks {a} blocks east and then {b} blocks north.",
        "question": "What is the straight-line distance from {name}'s starting point to the ending point?",
        "missing": "c",  # find hypotenuse
        "unit": "blocks",
    },
    {
        "scenario": "tv_screen",
        "template": "A television screen measures {a} inches wide and {c} inches diagonally.",
        "question": "What is the height of the screen, to the nearest hundredth of an inch?",
        "missing": "b",  # find leg (height)
        "unit": "inches",
    },
    {
        "scenario": "kite",
        "template": "{name} is flying a kite. The string is {c} meters long and the kite is directly above a point that is {a} meters away from {name}.",
        "question": "How high is the kite above the ground, to the nearest hundredth of a meter?",
        "missing": "b",  # find leg (height)
        "unit": "meters",
    },
    {
        "scenario": "baseball",
        "template": "A baseball diamond is a square with sides of {a} feet.",
        "question": "What is the distance from home plate to second base, to the nearest hundredth of a foot?",
        "missing": "c",  # find hypotenuse (diagonal)
        "unit": "feet",
    },
    {
        "scenario": "ramp",
        "template": "A ramp is {c} feet long and rises {b} feet vertically.",
        "question": "What is the horizontal distance covered by the ramp?",
        "missing": "a",  # find leg (horizontal)
        "unit": "feet",
    },
    {
        "scenario": "flagpole",
        "template": "A {b}-foot flagpole casts a shadow that is {a} feet long.",
        "question": "What is the distance from the top of the flagpole to the tip of the shadow?",
        "missing": "c",  # find hypotenuse
        "unit": "feet",
    },
    {
        "scenario": "pond",
        "template": "{name} wants to measure the distance across a rectangular pond. The pond is {a} meters wide and {b} meters long.",
        "question": "What is the distance diagonally across the pond, to the nearest hundredth of a meter?",
        "missing": "c",  # find hypotenuse
        "unit": "meters",
    },
]


def _is_perfect_square(n):
    """Check if n is a perfect square (works for ints)."""
    if n < 0:
        return False
    root = int(math.isqrt(n))
    return root * root == n


def _fmt_answer(val):
    """Format a numeric answer: whole if perfect square, else rounded to hundredth."""
    if isinstance(val, float):
        if val == int(val):
            return str(int(val))
        return f"{val:.2f}"
    return str(val)


class Stem8GM3:
    """Generates ~20 variants for each of 4 stems from the 8.GM.3 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 1, Easy)
    # Identify the correct Pythagorean equation for a right triangle
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        # Pick a Pythagorean triple
        triple = rng.choice(PYTHAGOREAN_TRIPLES)
        a, b, c = triple

        # Use variable side labels
        side_names = rng.choice([
            ("a", "b", "c"),
            ("x", "y", "z"),
            ("p", "q", "r"),
        ])
        leg1_name, leg2_name, hyp_name = side_names

        labels = {"a": str(a), "b": str(b), "c": str(c)}

        svg = right_triangle_svg(a, b, c, labels=labels)

        # Correct equation
        correct = f"{a}^2 + {b}^2 = {c}^2"

        # Distractors
        distractors = set()
        distractors.add(f"{a}^2 + {c}^2 = {b}^2")   # swapped leg and hypotenuse
        distractors.add(f"{b}^2 + {c}^2 = {a}^2")   # swapped other way
        distractors.add(f"{a} + {b} = {c}")           # forgot to square
        distractors.add(f"{a}^2 - {b}^2 = {c}^2")   # subtracted instead of added
        distractors.add(f"{a}^2 * {b}^2 = {c}^2")   # multiplied instead of added
        distractors.discard(correct)

        dist_list = list(distractors)
        rng.shuffle(dist_list)
        dist_list = dist_list[:3]

        all_options = [(correct, True)] + [(d, False) for d in dist_list]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text,
                text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = (
            f"A right triangle is shown with side lengths {a}, {b}, and {c}.\n\n"
            f"Which equation represents the Pythagorean theorem for this triangle?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=(
                f"The Pythagorean theorem states: leg^2 + leg^2 = hypotenuse^2\n"
                f"The two legs are {a} and {b}, and the hypotenuse is {c}.\n"
                f"So: {a}^2 + {b}^2 = {c}^2\n"
                f"Check: {a**2} + {b**2} = {c**2} --> {a**2 + b**2} = {c**2}  True"
            ),
            choices=choices,
            context_scenario="Pythagorean equation identification",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx,
            render_data={"svg_html": svg, "type": "svg_html"},
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - NR (DOK 1, Easy/Medium)
    # Find the missing side length
    # Randomly chooses whether the missing side is a leg or hypotenuse
    # ================================================================

    def stem2_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        # Pick a triple (or scaled triple for medium)
        base_triple = rng.choice(PYTHAGOREAN_TRIPLES[:5])
        a_base, b_base, c_base = base_triple

        # ~50% chance of scaling (medium difficulty)
        if rng.random() < 0.5:
            scale = rng.choice(SCALE_FACTORS)
            difficulty = Difficulty.MEDIUM
        else:
            scale = 1
            difficulty = Difficulty.EASY

        a = a_base * scale
        b = b_base * scale
        c = c_base * scale

        # Randomly choose which side is missing (~50/50 leg vs hypotenuse)
        missing_choice = rng.choice(["a", "b", "c"])

        if missing_choice == "a":
            # Missing leg a: given b and c
            missing_val = a
            given_desc = f"The hypotenuse is {c} and one leg is {b}."
            equation = f"{b}^2 + ?^2 = {c}^2"
            solution = (
                f"a^2 + b^2 = c^2\n"
                f"a^2 + {b}^2 = {c}^2\n"
                f"a^2 = {c}^2 - {b}^2\n"
                f"a^2 = {c**2} - {b**2}\n"
                f"a^2 = {c**2 - b**2}\n"
                f"a = sqrt({c**2 - b**2}) = {a}"
            )
            labels = {"a": "?", "b": str(b), "c": str(c)}
        elif missing_choice == "b":
            # Missing leg b: given a and c
            missing_val = b
            given_desc = f"The hypotenuse is {c} and one leg is {a}."
            equation = f"{a}^2 + ?^2 = {c}^2"
            solution = (
                f"a^2 + b^2 = c^2\n"
                f"{a}^2 + b^2 = {c}^2\n"
                f"b^2 = {c}^2 - {a}^2\n"
                f"b^2 = {c**2} - {a**2}\n"
                f"b^2 = {c**2 - a**2}\n"
                f"b = sqrt({c**2 - a**2}) = {b}"
            )
            labels = {"a": str(a), "b": "?", "c": str(c)}
        else:
            # Missing hypotenuse c: given a and b
            missing_val = c
            given_desc = f"The two legs are {a} and {b}."
            equation = f"{a}^2 + {b}^2 = ?^2"
            solution = (
                f"a^2 + b^2 = c^2\n"
                f"{a}^2 + {b}^2 = c^2\n"
                f"{a**2} + {b**2} = c^2\n"
                f"c^2 = {a**2 + b**2}\n"
                f"c = sqrt({a**2 + b**2}) = {c}"
            )
            labels = {"a": str(a), "b": str(b), "c": "?"}

        svg = right_triangle_svg(a, b, c, labels=labels)

        stem_text = (
            f"A right triangle is shown.\n"
            f"{given_desc}\n\n"
            f"Find the length of the missing side."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               difficulty, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=difficulty, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=str(missing_val), answer_latex=str(missing_val),
            worked_solution=solution,
            context_scenario="find missing side",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx,
            render_data={"svg_html": svg, "type": "svg_html"},
        )

    # ================================================================
    # STEM 3: At Proficiency - NR (DOK 2, Medium/Difficult)
    # Real-world Pythagorean theorem problem
    # Randomly varies which side is unknown based on context
    # ================================================================

    def stem3_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        ctx = rng.choice(REAL_WORLD_CONTEXTS)
        name = pick_name(rng)

        # Generate dimensions based on context
        missing = ctx["missing"]

        if ctx["scenario"] == "baseball":
            # Square diamond: both legs equal, find diagonal
            side = rng.choice([60, 70, 80, 90])
            a = side
            b = side
            c_sq = a**2 + b**2
            c = math.sqrt(c_sq)
            answer = c
            difficulty = Difficulty.DIFFICULT if not _is_perfect_square(c_sq) else Difficulty.MEDIUM
        elif missing == "c":
            # Find hypotenuse
            base_triple = rng.choice(PYTHAGOREAN_TRIPLES[:6])
            scale = rng.choice([1, 2, 3])
            a = base_triple[0] * scale
            b = base_triple[1] * scale
            c_sq = a**2 + b**2
            c = base_triple[2] * scale
            answer = c
            difficulty = Difficulty.MEDIUM
        elif missing == "b":
            # Find leg b given a and c
            # Mix of perfect and non-perfect square results
            if rng.random() < 0.5:
                # Use a triple (perfect square result)
                base_triple = rng.choice(PYTHAGOREAN_TRIPLES[:6])
                scale = rng.choice([1, 2, 3])
                a = base_triple[0] * scale
                b = base_triple[1] * scale
                c = base_triple[2] * scale
                answer = b
                difficulty = Difficulty.MEDIUM
            else:
                # Non-perfect square (difficult)
                a = rng.randint(5, 15)
                c = rng.randint(a + 3, a + 20)
                b_sq = c**2 - a**2
                if b_sq <= 0:
                    c = a + rng.randint(3, 10)
                    b_sq = c**2 - a**2
                answer = math.sqrt(b_sq)
                b = answer
                difficulty = Difficulty.DIFFICULT
        else:
            # Find leg a given b and c
            if rng.random() < 0.5:
                base_triple = rng.choice(PYTHAGOREAN_TRIPLES[:6])
                scale = rng.choice([1, 2, 3])
                a = base_triple[0] * scale
                b = base_triple[1] * scale
                c = base_triple[2] * scale
                answer = a
                difficulty = Difficulty.MEDIUM
            else:
                b = rng.randint(5, 15)
                c = rng.randint(b + 3, b + 20)
                a_sq = c**2 - b**2
                answer = math.sqrt(a_sq)
                a = answer
                difficulty = Difficulty.DIFFICULT

        answer_str = _fmt_answer(answer)

        # Build stem text from template
        template_text = ctx["template"].format(name=name, a=int(a) if a == int(a) else f"{a:.2f}",
                                                b=int(b) if b == int(b) else f"{b:.2f}",
                                                c=int(c) if c == int(c) else f"{c:.2f}")
        question_text = ctx["question"].format(name=name)

        stem_text = f"{template_text}\n\n{question_text}"

        # Build worked solution
        if missing == "c":
            solution = (
                f"a^2 + b^2 = c^2\n"
                f"{int(a) if a == int(a) else a}^2 + {int(b) if b == int(b) else b}^2 = c^2\n"
                f"{int(a**2)} + {int(b**2)} = c^2\n"
                f"c^2 = {int(a**2 + b**2)}\n"
                f"c = sqrt({int(a**2 + b**2)}) = {answer_str} {ctx['unit']}"
            )
        elif missing == "b":
            a_int = int(a) if a == int(a) else a
            c_int = int(c) if c == int(c) else c
            solution = (
                f"a^2 + b^2 = c^2\n"
                f"{a_int}^2 + b^2 = {c_int}^2\n"
                f"b^2 = {c_int}^2 - {a_int}^2\n"
                f"b^2 = {int(c**2)} - {int(a**2)}\n"
                f"b^2 = {int(c**2 - a**2)}\n"
                f"b = sqrt({int(c**2 - a**2)}) = {answer_str} {ctx['unit']}"
            )
        else:
            b_int = int(b) if b == int(b) else b
            c_int = int(c) if c == int(c) else c
            solution = (
                f"a^2 + b^2 = c^2\n"
                f"a^2 + {b_int}^2 = {c_int}^2\n"
                f"a^2 = {c_int}^2 - {b_int}^2\n"
                f"a^2 = {int(c**2)} - {int(b**2)}\n"
                f"a^2 = {int(c**2 - b**2)}\n"
                f"a = sqrt({int(c**2 - b**2)}) = {answer_str} {ctx['unit']}"
            )

        # No model for Difficult per item spec
        render = None
        if difficulty != Difficulty.DIFFICULT:
            # Show triangle with known and unknown sides
            if missing == "c":
                labels = {"a": str(int(a)), "b": str(int(b)), "c": "?"}
            elif missing == "b":
                labels = {"a": str(int(a)), "b": "?", "c": str(int(c))}
            else:
                labels = {"a": "?", "b": str(int(b)), "c": str(int(c))}
            svg = right_triangle_svg(a, b, c, labels=labels, unit=ctx["unit"])
            render = {"svg_html": svg, "type": "svg_html"}

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               difficulty, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=difficulty, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_str, answer_latex=answer_str,
            worked_solution=solution,
            context_scenario=ctx["scenario"],
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx,
            render_data=render,
        )

    # ================================================================
    # STEM 4: Above Proficiency - MP (DOK 2, Medium)
    # Two-part with compound shapes
    # ================================================================

    def stem4_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        name = pick_name(rng)

        # Compound shape scenarios
        scenario_type = rng.choice(["sail", "field", "frame"])

        if scenario_type == "sail":
            # Two triangular sails: find the missing side of each
            triple1 = rng.choice(PYTHAGOREAN_TRIPLES[:5])
            triple2 = rng.choice(PYTHAGOREAN_TRIPLES[:5])
            while triple2 == triple1:
                triple2 = rng.choice(PYTHAGOREAN_TRIPLES[:5])

            a1, b1, c1 = triple1
            a2, b2, c2 = triple2

            # Part A: find hypotenuse of sail 1
            part_a_answer = str(c1)
            part_a = QuestionPart(
                label="Part A",
                prompt=f"Sail 1 has legs of {a1} ft and {b1} ft. What is the length of the longest side (the hypotenuse)?",
                prompt_latex=f"Sail 1 has legs of {a1} ft and {b1} ft. What is the length of the longest side (the hypotenuse)?",
                answer=part_a_answer,
                answer_latex=part_a_answer,
                item_type=ItemType.NR,
            )

            # Part B: find leg of sail 2
            part_b_answer = str(b2)
            part_b = QuestionPart(
                label="Part B",
                prompt=f"Sail 2 has a hypotenuse of {c2} ft and one leg of {a2} ft. What is the length of the other leg?",
                prompt_latex=f"Sail 2 has a hypotenuse of {c2} ft and one leg of {a2} ft. What is the length of the other leg?",
                answer=part_b_answer,
                answer_latex=part_b_answer,
                item_type=ItemType.NR,
            )

            stem_text = (
                f"{name} is making two triangular sails for a model boat. "
                f"Both sails are right triangles.\n\n"
                f"Part A\n"
                f"Sail 1 has legs of {a1} ft and {b1} ft. What is the length of the longest side (the hypotenuse)?\n\n"
                f"Part B\n"
                f"Sail 2 has a hypotenuse of {c2} ft and one leg of {a2} ft. What is the length of the other leg?"
            )

            svg1 = right_triangle_svg(a1, b1, c1,
                                       labels={"a": str(a1), "b": str(b1), "c": "?"},
                                       unit="ft")

            answer_text = f"Part A: {part_a_answer} ft | Part B: {part_b_answer} ft"
            solution = (
                f"Part A: {a1}^2 + {b1}^2 = c^2 --> {a1**2} + {b1**2} = c^2 --> c = {c1} ft\n"
                f"Part B: {a2}^2 + b^2 = {c2}^2 --> b^2 = {c2**2} - {a2**2} = {c2**2 - a2**2} --> b = {b2} ft"
            )

        elif scenario_type == "field":
            # Rectangular field: find diagonal, then find perimeter + diagonal total
            triple = rng.choice(PYTHAGOREAN_TRIPLES[:6])
            scale = rng.choice([1, 2, 3])
            a = triple[0] * scale
            b = triple[1] * scale
            c = triple[2] * scale

            part_a_answer = str(c)
            part_a = QuestionPart(
                label="Part A",
                prompt=f"A rectangular field is {a} m wide and {b} m long. What is the length of the diagonal path across the field?",
                prompt_latex=f"A rectangular field is {a} m wide and {b} m long. What is the length of the diagonal path across the field?",
                answer=f"{part_a_answer} m",
                answer_latex=f"{part_a_answer} m",
                item_type=ItemType.NR,
            )

            perimeter = 2 * (a + b)
            total = perimeter + c
            part_b_answer = str(total)
            part_b = QuestionPart(
                label="Part B",
                prompt=f"{name} walks the perimeter of the field and then walks diagonally back to the starting corner. What is the total distance walked?",
                prompt_latex=f"{name} walks the perimeter of the field and then walks diagonally back to the starting corner. What is the total distance walked?",
                answer=f"{part_b_answer} m",
                answer_latex=f"{part_b_answer} m",
                item_type=ItemType.NR,
            )

            stem_text = (
                f"A rectangular field is {a} m wide and {b} m long.\n\n"
                f"Part A\n"
                f"What is the length of the diagonal path across the field?\n\n"
                f"Part B\n"
                f"{name} walks the perimeter of the field and then walks diagonally back to the starting corner. "
                f"What is the total distance walked?"
            )

            svg1 = right_triangle_svg(a, b, c,
                                       labels={"a": str(a), "b": str(b), "c": "?"},
                                       unit="m")

            answer_text = f"Part A: {part_a_answer} m | Part B: {part_b_answer} m"
            solution = (
                f"Part A: {a}^2 + {b}^2 = c^2 --> {a**2} + {b**2} = {a**2+b**2} --> c = {c} m\n"
                f"Part B: Perimeter = 2({a} + {b}) = {perimeter} m\n"
                f"Total = {perimeter} + {c} = {total} m"
            )

        else:  # frame
            # Picture frame with diagonal brace
            triple = rng.choice(PYTHAGOREAN_TRIPLES[:6])
            scale = rng.choice([1, 2])
            a = triple[0] * scale
            b = triple[1] * scale
            c = triple[2] * scale

            part_a_answer = str(c)
            part_a = QuestionPart(
                label="Part A",
                prompt=f"A rectangular frame is {a} in. by {b} in. What is the length of the diagonal brace?",
                prompt_latex=f"A rectangular frame is {a} in. by {b} in. What is the length of the diagonal brace?",
                answer=f"{part_a_answer} in.",
                answer_latex=f"{part_a_answer} in.",
                item_type=ItemType.NR,
            )

            frame_perimeter = 2 * (a + b) + c
            part_b_answer = str(frame_perimeter)
            part_b = QuestionPart(
                label="Part B",
                prompt=f"How much total wood is needed for the frame sides and the diagonal brace?",
                prompt_latex=f"How much total wood is needed for the frame sides and the diagonal brace?",
                answer=f"{part_b_answer} in.",
                answer_latex=f"{part_b_answer} in.",
                item_type=ItemType.NR,
            )

            stem_text = (
                f"{name} is building a rectangular picture frame that is {a} in. by {b} in. "
                f"A diagonal brace will be added for support.\n\n"
                f"Part A\n"
                f"What is the length of the diagonal brace?\n\n"
                f"Part B\n"
                f"How much total wood is needed for the frame sides and the diagonal brace?"
            )

            svg1 = right_triangle_svg(a, b, c,
                                       labels={"a": str(a), "b": str(b), "c": "?"},
                                       unit="in.")

            answer_text = f"Part A: {part_a_answer} in. | Part B: {part_b_answer} in."
            solution = (
                f"Part A: {a}^2 + {b}^2 = c^2 --> {a**2} + {b**2} = {a**2+b**2} --> c = {c} in.\n"
                f"Part B: Frame sides = 2({a} + {b}) = {2*(a+b)} in.\n"
                f"Total = {2*(a+b)} + {c} = {frame_perimeter} in."
            )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_text, answer_latex=answer_text,
            worked_solution=solution,
            parts=[part_a, part_b],
            context_scenario=scenario_type,
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx,
            render_data={"svg_html": svg1, "type": "svg_html"},
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_approaching_nr,
            self.stem3_at_nr,
            self.stem4_above_mp,
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
            1: self.stem1_below_mc,
            2: self.stem2_approaching_nr,
            3: self.stem3_at_nr,
            4: self.stem4_above_mp,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-4.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 8.GM.3 question variants...")
    gen = Stem8GM3(seed=42)
    all_q = gen.generate_all_variants(variants_per_stem=3)
    for q in all_q:
        print(f"\n{'='*60}")
        print(f"ID: {q.question_id}")
        print(f"Stem {q.stem_index} | {q.proficiency_level.value} | {q.difficulty.value} | DOK {q.dok}")
        print(f"\n{q.stem_text}")
        if q.choices:
            for c in q.choices:
                marker = " *" if c.is_correct else ""
                print(f"  {c.key}. {c.text}{marker}")
        print(f"\nAnswer: {q.answer_text}")
        if q.render_data:
            print(f"Visual: {q.render_data.get('type', 'none')}")
    print(f"\nTotal: {len(all_q)}")
