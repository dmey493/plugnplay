"""
Stem generator for 6.GM.2:
  Apply the sums of interior angles of triangles and quadrilaterals
  to solve real-world and mathematical problems.

Content Limits:
  - Exclude complementary, adjacent, or supplementary angles
  - Label 90-degree angles with degree notation or a small square symbol
  - Limit angle measures to whole numbers or decimals (no fractions)
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: No computation required
  Medium: Computation with whole numbers
  Difficult: Computation with decimals

4 Stems from the Item Spec:
  Stem 1 (Below-MC):       Sum of interior angles of triangle/quadrilateral (DOK 1, Easy)
  Stem 2 (Approaching-MC): Find missing angle given other angles in diagram (DOK 1, Medium)
  Stem 3 (At-NR):          Real-world missing angle problem (DOK 2, Medium)
  Stem 4 (Above-MP):       Agree/disagree with a claim about a triangle angle (DOK 2, Medium)
"""

import random
import math
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
from engine.context_pools import pick_name


STANDARD_CODE = "6.GM.2"
VARIANTS_PER_STEM = 20


# ============================================================
# HELPERS
# ============================================================

def _triangle_vertices(angles, size=120):
    """Compute SVG vertices for a triangle given 3 angle measures.
    Returns list of {x, y} dicts and label offsets.
    Places bottom-left vertex at origin, bottom side horizontal.
    """
    a, b, c = [float(x) for x in angles]
    # Bottom-left angle = a, bottom-right angle = b, top angle = c
    # Bottom side length
    base = size
    # Using sine rule: side_a/sin(A) = side_b/sin(B) = side_c/sin(C)
    # side opposite angle a = BC, opposite b = AC, opposite c = AB (base)
    sin_a = math.sin(math.radians(a))
    sin_b = math.sin(math.radians(b))
    sin_c = math.sin(math.radians(c))

    # base (AB) is opposite angle c
    # side AC (left) opposite angle b
    # side BC (right) opposite angle a
    side_ac = base * sin_b / sin_c if sin_c > 0 else base
    side_bc = base * sin_a / sin_c if sin_c > 0 else base

    # Vertices
    ax, ay = 60, 180  # bottom-left (angle a)
    bx, by = 60 + base, 180  # bottom-right (angle b)
    # Top vertex from angle a
    cx_val = ax + side_ac * math.cos(math.radians(a))
    cy_val = ay - side_ac * math.sin(math.radians(a))

    vertices = [
        {"x": round(ax, 1), "y": round(ay, 1)},
        {"x": round(bx, 1), "y": round(by, 1)},
        {"x": round(cx_val, 1), "y": round(cy_val, 1)},
    ]

    # Label offsets: push labels away from center
    center_x = (ax + bx + cx_val) / 3
    center_y = (ay + by + cy_val) / 3
    label_offsets = []
    for v in vertices:
        dx = v["x"] - center_x
        dy = v["y"] - center_y
        dist = math.sqrt(dx*dx + dy*dy) or 1
        label_offsets.append({
            "dx": round(dx / dist * 35, 1),
            "dy": round(dy / dist * 35, 1),
        })

    return vertices, label_offsets


def _quad_vertices(angles, size=120):
    """Compute SVG vertices for a quadrilateral given 4 angle measures.
    Creates a roughly rectangular shape with the given angles.
    """
    # Simple approach: create a trapezoid-like shape
    # Bottom-left at (30, 180), bottom-right at (30+size, 180)
    # Top vertices offset inward
    w = size
    h = size * 0.7
    inset = size * 0.15

    vertices = [
        {"x": 60, "y": 180},               # bottom-left
        {"x": 60 + w, "y": 180},            # bottom-right
        {"x": 60 + w - inset, "y": 180 - h},  # top-right
        {"x": 60 + inset, "y": 180 - h},    # top-left
    ]

    center_x = sum(v["x"] for v in vertices) / 4
    center_y = sum(v["y"] for v in vertices) / 4
    label_offsets = []
    for v in vertices:
        dx = v["x"] - center_x
        dy = v["y"] - center_y
        dist = math.sqrt(dx*dx + dy*dy) or 1
        label_offsets.append({
            "dx": round(dx / dist * 35, 1),
            "dy": round(dy / dist * 35, 1),
        })

    return vertices, label_offsets


def _make_polygon_render(shape, vertices, angles_info, label_offsets, right_angle_indices=None):
    """Build polygon_angles render_data dict."""
    return {
        "type": "polygon_angles",
        "shape": shape,
        "vertices": vertices,
        "angles": angles_info,
        "right_angle_indices": right_angle_indices or [],
        "label_offsets": label_offsets,
    }


# Real-world contexts for Stem 3
ANGLE_CONTEXTS = [
    ("ramp", "A carpenter designs a ramp in the shape of a right triangle"),
    ("roof", "A roof truss is shaped like a triangle"),
    ("garden", "A garden bed is shaped like a triangle"),
    ("sail", "A sail on a boat is shaped like a triangle"),
    ("sign", "A yield sign is shaped like a triangle"),
    ("window", "A decorative window frame is shaped like a quadrilateral"),
    ("tile", "A floor tile is shaped like a quadrilateral"),
    ("kite", "A kite is shaped like a quadrilateral"),
    ("frame", "A picture frame is shaped like a quadrilateral"),
    ("table", "A tabletop is shaped like a quadrilateral"),
]


CLAIM_CONTEXTS = [
    ("ramp", "a ramp shaped like a triangle", "the ramp"),
    ("roof", "a roof truss shaped like a triangle", "the truss"),
    ("sail", "a sail shaped like a triangle", "the sail"),
    ("garden", "a garden bed shaped like a triangle", "the garden bed"),
    ("sign", "a triangular road sign", "the sign"),
]


class Stem6GM2:
    """Generates ~20 variants for each of 4 stems from the 6.GM.2 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 1, Easy)
    # "What is the sum of interior angles of a triangle/quadrilateral?"
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        shape = rng.choice(["triangle", "quadrilateral"])
        correct = 180 if shape == "triangle" else 360

        if shape == "triangle":
            stem_text = "What is the sum of the interior angles of any triangle?"
            distractors = [90, 270, 360]
        else:
            stem_text = "What is the sum of the interior angles of any quadrilateral?"
            distractors = [180, 270, 540]

        all_options = [(f"{correct} degrees", True)]
        for d in distractors:
            all_options.append((f"{d} degrees", False))
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text,
                text_latex=f"${text.replace('degrees', '^{\\\\circ}')}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=f"The sum of interior angles of a {shape} is {correct} degrees.",
            choices=choices, context_scenario="angle sum fact",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx,
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - MC (DOK 1, Medium)
    # Find missing angle in triangle or quadrilateral with diagram
    # ================================================================

    def stem2_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        shape = rng.choice(["triangle", "quadrilateral"])

        if shape == "triangle":
            total = 180
            # Generate 2 known angles, compute missing
            has_right = rng.random() < 0.3
            if has_right:
                a1 = 90
                a2 = rng.randint(15, 75)
                missing = total - a1 - a2
            else:
                a1 = rng.randint(25, 80)
                a2 = rng.randint(25, 80)
                missing = total - a1 - a2
                if missing < 10:
                    a1 = rng.randint(30, 60)
                    a2 = rng.randint(30, 60)
                    missing = total - a1 - a2

            known_angles = [a1, a2]
            all_angles = [a1, a2, missing]
            missing_idx = 2  # top vertex

            right_indices = [0] if has_right else []
            vertices, offsets = _triangle_vertices(all_angles)

            angles_info = [
                {"value": str(a1), "label": f"{a1}" + ("" if a1 == 90 else "\u00b0")},
                {"value": str(a2), "label": f"{a2}\u00b0"},
                {"value": "?", "label": "?"},
            ]
        else:
            total = 360
            a1 = rng.randint(60, 120)
            a2 = rng.randint(60, 120)
            a3 = rng.randint(60, 120)
            missing = total - a1 - a2 - a3
            # Ensure valid (positive and reasonable)
            while missing < 20 or missing > 170:
                a1 = rng.randint(70, 110)
                a2 = rng.randint(70, 110)
                a3 = rng.randint(70, 110)
                missing = total - a1 - a2 - a3

            known_angles = [a1, a2, a3]
            all_angles = [a1, a2, a3, missing]
            missing_idx = 3  # top-left vertex

            has_right = 90 in known_angles
            right_indices = [i for i, a in enumerate(all_angles) if a == 90]
            vertices, offsets = _quad_vertices(all_angles)

            angles_info = [
                {"value": str(a1), "label": f"{a1}" + ("" if a1 == 90 else "\u00b0")},
                {"value": str(a2), "label": f"{a2}" + ("" if a2 == 90 else "\u00b0")},
                {"value": str(a3), "label": f"{a3}" + ("" if a3 == 90 else "\u00b0")},
                {"value": "?", "label": "x"},
            ]

        render = _make_polygon_render(shape, vertices, angles_info, offsets, right_indices)

        stem_text = (
            f"The figure below shows a {shape} with the given angle measurements.\n\n"
            f"What is the measurement of angle x?"
        )

        correct_str = str(missing)

        # Distractors
        dist_set = set()
        dist_set.add(str(total - missing))  # common: confuse with complement to total
        dist_set.add(str(missing + 10))
        dist_set.add(str(abs(missing - 10)))
        if total - sum(known_angles[:2]) != missing:
            dist_set.add(str(total - sum(known_angles[:2])))
        dist_set.discard(correct_str)
        dist_set.discard("0")
        dist_list = sorted(dist_set)[:3]
        while len(dist_list) < 3:
            d = str(missing + rng.choice([-15, 15, 20, -20]))
            if d != correct_str and d not in dist_list and int(d) > 0:
                dist_list.append(d)

        all_options = [(f"{correct_str} degrees", True)]
        for d in dist_list[:3]:
            all_options.append((f"{d} degrees", False))
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text,
                text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.MEDIUM, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=(
                f"Sum of interior angles of a {shape} = {total} degrees\n"
                f"Known angles: {', '.join(str(a) for a in known_angles)}\n"
                f"Missing angle = {total} - {' - '.join(str(a) for a in known_angles)} = {missing} degrees"
            ),
            choices=choices, context_scenario="missing angle",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx,
            render_data=render,
        )

    # ================================================================
    # STEM 3: At Proficiency - NR (DOK 2, Medium)
    # Real-world missing angle problem
    # ================================================================

    def stem3_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        ctx = rng.choice(ANGLE_CONTEXTS)
        ctx_key, ctx_text = ctx

        is_triangle = "triangle" in ctx_text
        if is_triangle:
            total = 180
            # Real-world: often has a right angle
            has_right = rng.random() < 0.4
            if has_right:
                a1 = 90
                a2 = rng.randint(15, 75)
            else:
                a1 = rng.randint(25, 80)
                a2 = rng.randint(25, 80)
            missing = total - a1 - a2
            if missing < 10:
                a1 = rng.randint(30, 60)
                a2 = rng.randint(30, 60)
                missing = total - a1 - a2

            known_angles = [a1, a2]
            all_angles = [a1, a2, missing]
            right_indices = [0] if has_right else []
            vertices, offsets = _triangle_vertices(all_angles)
            angles_info = [
                {"value": str(a1), "label": f"{a1}" + ("" if a1 == 90 else "\u00b0")},
                {"value": str(a2), "label": f"{a2}\u00b0"},
                {"value": "?", "label": "x"},
            ]
            shape = "triangle"
        else:
            total = 360
            has_right = rng.random() < 0.3
            if has_right:
                a1 = 90
                a2 = rng.randint(60, 120)
                a3 = rng.randint(60, 120)
            else:
                a1 = rng.randint(60, 120)
                a2 = rng.randint(60, 120)
                a3 = rng.randint(60, 120)
            missing = total - a1 - a2 - a3
            while missing < 20 or missing > 170:
                a1 = rng.randint(70, 110)
                a2 = rng.randint(70, 110)
                a3 = rng.randint(70, 110)
                missing = total - a1 - a2 - a3

            known_angles = [a1, a2, a3]
            all_angles = [a1, a2, a3, missing]
            right_indices = [i for i, a in enumerate(all_angles) if a == 90]
            vertices, offsets = _quad_vertices(all_angles)
            angles_info = [
                {"value": str(a1), "label": f"{a1}" + ("" if a1 == 90 else "\u00b0")},
                {"value": str(a2), "label": f"{a2}" + ("" if a2 == 90 else "\u00b0")},
                {"value": str(a3), "label": f"{a3}" + ("" if a3 == 90 else "\u00b0")},
                {"value": "?", "label": "x"},
            ]
            shape = "quadrilateral"

        render = _make_polygon_render(shape, vertices, angles_info, offsets, right_indices)

        name = pick_name(rng)
        known_str = " degrees and ".join(str(a) for a in known_angles)
        stem_text = (
            f"{ctx_text}. The figure below shows the shape with the given angle measurements.\n\n"
            f"Enter the measure, in degrees, of the missing angle x."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=str(missing), answer_latex=str(missing),
            worked_solution=(
                f"Sum of interior angles of a {shape} = {total} degrees\n"
                f"Known angles: {', '.join(str(a) for a in known_angles)}\n"
                f"x = {total} - {' - '.join(str(a) for a in known_angles)} = {missing} degrees"
            ),
            context_scenario=ctx_key,
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx,
            render_data=render,
        )

    # ================================================================
    # STEM 4: Above Proficiency - MP (DOK 2, Medium)
    # Triangle: a student claims a missing angle value, prove right or wrong
    # ================================================================

    def stem4_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        # Pick real-world context
        ctx_key, ctx_desc, ctx_ref = CLAIM_CONTEXTS[variant_idx % len(CLAIM_CONTEXTS)]
        student_name = pick_name(rng)
        claimer_name = pick_name(rng)
        while claimer_name == student_name:
            claimer_name = pick_name(rng)

        # Generate a triangle with 3 whole-number angles summing to 180
        has_right = rng.random() < 0.3
        if has_right:
            a1 = 90
            a2 = rng.randint(15, 75)
        else:
            a1 = rng.randint(25, 80)
            a2 = rng.randint(25, 80)
        a3 = 180 - a1 - a2
        if a3 < 15:
            a1 = rng.randint(35, 65)
            a2 = rng.randint(35, 65)
            a3 = 180 - a1 - a2

        all_angles = [a1, a2, a3]
        right_indices = [0] if has_right else []

        # The student claims a value for the missing angle (a3).
        # Half the time the claim is correct, half wrong.
        is_correct = (variant_idx % 2 == 0)
        if is_correct:
            claimed = a3
        else:
            # Generate a wrong claim from common student errors
            error_type = rng.choice(["forgot_right", "subtracted_wrong", "used_360", "added"])
            if error_type == "forgot_right" and has_right:
                # Student forgot the right angle, subtracted only a2 from 180
                claimed = 180 - a2
            elif error_type == "used_360":
                # Student used 360 instead of 180
                claimed = 360 - a1 - a2
            elif error_type == "added":
                # Student added instead of subtracted
                claimed = a1 + a2
            else:
                # Simple arithmetic error
                claimed = a3 + rng.choice([-10, 10, -15, 15, -5, 5])
            # Make sure claim is positive and not accidentally correct
            if claimed <= 0 or claimed == a3:
                claimed = a3 + rng.choice([10, -10, 20])
            if claimed <= 0:
                claimed = a3 + 15

        # Build triangle diagram showing a1 and a2, with a3 as "?"
        vertices, offsets = _triangle_vertices(all_angles, size=140)
        angles_info = [
            {"value": str(a1), "label": f"{a1}" + ("" if a1 == 90 else "\u00b0")},
            {"value": str(a2), "label": f"{a2}\u00b0"},
            {"value": "?", "label": "x"},
        ]
        render = _make_polygon_render("triangle", vertices, angles_info, offsets, right_indices)

        # Build stem text
        agree_or_disagree = "agree" if is_correct else "disagree"
        correct_answer = a3

        stem_text = (
            f"{student_name} is designing {ctx_desc}. "
            f"Two of the angles in {ctx_ref} measure {a1} degrees and {a2} degrees.\n\n"
            f"[FIGURE]\n\n"
            f"{claimer_name} says the third angle measures {claimed} degrees.\n\n"
            f"Part A\n"
            f"Do you agree or disagree with {claimer_name}? "
            f"What is the correct measure of the third angle?\n\n"
            f"Part B\n"
            f"Explain how you know."
        )

        if is_correct:
            explanation = (
                f"{claimer_name} is correct. The sum of interior angles of a triangle is 180 degrees.\n"
                f"{a1} + {a2} + x = 180\n"
                f"x = 180 - {a1} - {a2} = {a3} degrees.\n"
                f"{claimer_name} said {claimed} degrees, which is correct."
            )
        else:
            explanation = (
                f"{claimer_name} is incorrect. The sum of interior angles of a triangle is 180 degrees.\n"
                f"{a1} + {a2} + x = 180\n"
                f"x = 180 - {a1} - {a2} = {a3} degrees.\n"
                f"{claimer_name} said {claimed} degrees, but the correct answer is {a3} degrees."
            )

        part_a = QuestionPart(
            label="Part A",
            prompt=f"Do you agree or disagree with {claimer_name}? What is the correct measure of the third angle?",
            prompt_latex=f"Do you agree or disagree with {claimer_name}? What is the correct measure of the third angle?",
            answer=f"I {agree_or_disagree}. The third angle is {correct_answer} degrees.",
            answer_latex=f"I {agree_or_disagree}. The third angle is {correct_answer} degrees.",
            item_type=ItemType.ER,
        )
        part_b = QuestionPart(
            label="Part B",
            prompt="Explain how you know.",
            prompt_latex="Explain how you know.",
            answer=explanation,
            answer_latex=explanation,
            item_type=ItemType.ER,
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"Part A: I {agree_or_disagree}. The third angle is {correct_answer} degrees. | Part B: {explanation}",
            answer_latex=f"Part A: I {agree_or_disagree}. The third angle is {correct_answer} degrees. | Part B: {explanation}",
            worked_solution=explanation,
            parts=[part_a, part_b],
            context_scenario=ctx_key,
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx,
            render_data=render,
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_approaching_mc,
            self.stem3_at_nr,
            self.stem4_above_mp,
        ]
        for stem_fn in stem_methods:
            for v in range(variants_per_stem):
                try:
                    all_questions.append(stem_fn(v))
                except Exception as e:
                    print(f"Error generating {stem_fn.__name__} variant {v}: {e}")
                    continue
        return all_questions

    def generate_stem_variants(self, stem_index: int,
                                variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        stem_methods = {
            1: self.stem1_below_mc,
            2: self.stem2_approaching_mc,
            3: self.stem3_at_nr,
            4: self.stem4_above_mp,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-4.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 6.GM.2 question variants...")
    gen = Stem6GM2(seed=42)
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
