"""
Stem generator for 8.GM.1:
  Identify, describe, and perform transformations (translations,
  rotations about the origin, reflections over x/y axis, dilations
  about the origin) on figures in a coordinate plane.

Content Limits:
  - Integer coordinates only
  - Rotations and dilations about the origin only
  - Reflections over x-axis or y-axis only
  - Single transformations except Above (which may chain two)
  - Proper notation: A -> A' (preimage -> image)
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: Translation or dilation (preimage and image shown)
  Medium: Rotation or dilation, identifying transformation
  Difficult: Multi-step (two transformations chained)

4 Stems from the Item Spec:
  Stem 1 (Below-MC):       Identify which transformation maps ABC to A'B'C' (DOK 1, Easy)
  Stem 2 (Approaching-MC): Identify specific transformation or find vertex coords (DOK 2, Medium)
  Stem 3 (At-NR):          Perform transformation, give coordinates (DOK 2, Medium)
  Stem 4 (Above-MP):       Two transformations chained (DOK 3, Difficult)
"""

import random
import math

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
from engine.svg_helpers import coord_grid_polygon_svg


STANDARD_CODE = "8.GM.1"
VARIANTS_PER_STEM = 20

VERTEX_LABELS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


# ============================================================
# TRANSFORMATION FUNCTIONS
# ============================================================

def translate(vertices, dx, dy):
    return [(x + dx, y + dy) for x, y in vertices]


def reflect_x(vertices):
    """Reflect over x-axis: (x,y) -> (x,-y)."""
    return [(x, -y) for x, y in vertices]


def reflect_y(vertices):
    """Reflect over y-axis: (x,y) -> (-x,y)."""
    return [(-x, y) for x, y in vertices]


def rotate_90_cw(vertices):
    """Rotate 90 degrees clockwise about origin: (x,y) -> (y,-x)."""
    return [(y, -x) for x, y in vertices]


def rotate_180(vertices):
    """Rotate 180 degrees about origin: (x,y) -> (-x,-y)."""
    return [(-x, -y) for x, y in vertices]


def rotate_270_cw(vertices):
    """Rotate 270 degrees CW (= 90 CCW) about origin: (x,y) -> (-y,x)."""
    return [(-y, x) for x, y in vertices]


def dilate(vertices, k):
    """Dilation about origin by factor k: (x,y) -> (kx,ky)."""
    return [(k * x, k * y) for x, y in vertices]


# All single-transformation options
TRANSFORMATIONS = {
    "translation": {
        "name": "translation",
        "desc_template": "a translation of ({dx}, {dy})",
    },
    "reflect_x": {
        "name": "reflection over the x-axis",
        "func": reflect_x,
    },
    "reflect_y": {
        "name": "reflection over the y-axis",
        "func": reflect_y,
    },
    "rotate_90_cw": {
        "name": "90-degree clockwise rotation about the origin",
        "func": rotate_90_cw,
    },
    "rotate_180": {
        "name": "180-degree rotation about the origin",
        "func": rotate_180,
    },
    "rotate_270_cw": {
        "name": "270-degree clockwise rotation about the origin",
        "func": rotate_270_cw,
    },
}


def _gen_triangle(rng, quadrant=1, max_coord=5):
    """Generate a triangle in a given quadrant with integer coords."""
    if quadrant == 1:
        x_base = rng.randint(1, 3)
        y_base = rng.randint(1, 3)
    elif quadrant == 2:
        x_base = rng.randint(-5, -2)
        y_base = rng.randint(1, 3)
    else:
        x_base = rng.randint(1, 3)
        y_base = rng.randint(1, 3)

    # Simple right triangle or scalene
    v1 = (x_base, y_base)
    v2 = (x_base + rng.randint(2, 4), y_base)
    v3 = (x_base + rng.randint(0, 2), y_base + rng.randint(2, 4))

    return [v1, v2, v3]


def _gen_quadrilateral(rng, quadrant=1):
    """Generate a rectangle or parallelogram with integer coords."""
    if quadrant == 1:
        x_base = rng.randint(1, 3)
        y_base = rng.randint(1, 3)
    elif quadrant == 2:
        x_base = rng.randint(-5, -2)
        y_base = rng.randint(1, 3)
    else:
        x_base = rng.randint(1, 3)
        y_base = rng.randint(1, 3)

    w = rng.randint(2, 4)
    h = rng.randint(2, 4)
    # Rectangle ABCD going clockwise
    v1 = (x_base, y_base)
    v2 = (x_base + w, y_base)
    v3 = (x_base + w, y_base + h)
    v4 = (x_base, y_base + h)
    return [v1, v2, v3, v4]


def _gen_figure(rng, quadrant=1):
    """Generate either a triangle or quadrilateral randomly."""
    if rng.random() < 0.5:
        verts = _gen_triangle(rng, quadrant)
        n = 3
        name = "triangle"
    else:
        verts = _gen_quadrilateral(rng, quadrant)
        n = 4
        name = "quadrilateral"
    labels = VERTEX_LABELS[:n]
    return verts, name, labels


def _apply_transform(vertices, transform_key, rng):
    """Apply a named transformation and return (result, description, params)."""
    if transform_key == "translation":
        dx = rng.choice([-5, -4, -3, -2, 2, 3, 4, 5])
        dy = rng.choice([-5, -4, -3, -2, 2, 3, 4, 5])
        result = translate(vertices, dx, dy)
        desc = f"a translation of ({dx}, {dy})"
        return result, desc, {"dx": dx, "dy": dy}
    elif transform_key == "reflect_x":
        result = reflect_x(vertices)
        desc = "a reflection over the x-axis"
        return result, desc, {}
    elif transform_key == "reflect_y":
        result = reflect_y(vertices)
        desc = "a reflection over the y-axis"
        return result, desc, {}
    elif transform_key == "rotate_90_cw":
        result = rotate_90_cw(vertices)
        desc = "a 90-degree clockwise rotation about the origin"
        return result, desc, {}
    elif transform_key == "rotate_180":
        result = rotate_180(vertices)
        desc = "a 180-degree rotation about the origin"
        return result, desc, {}
    elif transform_key == "rotate_270_cw":
        result = rotate_270_cw(vertices)
        desc = "a 270-degree clockwise rotation about the origin"
        return result, desc, {}
    elif transform_key.startswith("dilation"):
        k = int(transform_key.split("_")[1])
        result = dilate(vertices, k)
        desc = f"a dilation by a scale factor of {k} about the origin"
        return result, desc, {"k": k}
    else:
        raise ValueError(f"Unknown transform: {transform_key}")


def _grid_range(all_vertices):
    """Compute grid range that fits all vertices with padding."""
    all_x = [v[0] for v in all_vertices]
    all_y = [v[1] for v in all_vertices]
    x_min = min(all_x) - 2
    x_max = max(all_x) + 2
    y_min = min(all_y) - 2
    y_max = max(all_y) + 2

    # Ensure origin is visible and range is symmetric-ish
    x_min = min(x_min, -1)
    x_max = max(x_max, 1)
    y_min = min(y_min, -1)
    y_max = max(y_max, 1)

    # Ensure at least 8 units range
    if x_max - x_min < 8:
        mid = (x_max + x_min) / 2
        x_min = int(mid - 4)
        x_max = int(mid + 4)
    if y_max - y_min < 8:
        mid = (y_max + y_min) / 2
        y_min = int(mid - 4)
        y_max = int(mid + 4)

    return (x_min, x_max), (y_min, y_max)


def _fmt_vertex(label, x, y):
    return f"{label}({x}, {y})"


def _fmt_vertices(vertices, suffix=""):
    """Format vertices with labels: A(1,2), B(3,4), C(5,6)."""
    parts = []
    for i, (x, y) in enumerate(vertices):
        lbl = VERTEX_LABELS[i] + suffix
        parts.append(f"{lbl}({x}, {y})")
    return ", ".join(parts)


class Stem8GM1:
    """Generates ~20 variants for each of 4 stems from the 8.GM.1 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 1, Easy)
    # Identify which transformation maps ABC to A'B'C'
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        # Use both triangles and quadrilaterals
        verts, fig_name, labels = _gen_figure(rng)
        label_str = "".join(labels)
        label_prime_str = "".join(l + "'" for l in labels)

        # Easy tier: limited to translations and dilations only
        transform_key = rng.choice(["translation", "dilation_2", "dilation_3"])
        image, correct_desc, params = _apply_transform(verts, transform_key, rng)

        all_verts = verts + image
        x_range, y_range = _grid_range(all_verts)

        svg = coord_grid_polygon_svg(x_range, y_range,
                                      preimage=verts, image=image,
                                      img_label="'")

        # Distractors: the 4 transformation types
        correct_type = "translation" if transform_key == "translation" else "dilation"
        type_options = ["translation", "reflection", "rotation", "dilation"]
        wrong_types = [t for t in type_options if t != correct_type]

        all_options = [(correct_type, True)] + [(w, False) for w in wrong_types]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text,
                text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        pre_str = _fmt_vertices(verts)
        img_str = _fmt_vertices(image, "'")

        stem_text = (
            f"A transformation of {fig_name} {label_str} is given.\n\n"
            f"[FIGURE] Select the transformation that maps "
            f"{label_str} onto {label_prime_str}."
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
                f"The transformation is {correct_desc}.\n"
                f"Pre-image: {pre_str}\n"
                f"Image: {img_str}"
            ),
            choices=choices,
            context_scenario="identify transformation",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx,
            render_data={"svg_html": svg, "type": "svg_html"},
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - MC (DOK 2, Medium)
    # Identify specific transformation or find one vertex's coords
    # ================================================================

    def stem2_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        preimage = _gen_triangle(rng)

        # Use rotations or dilations
        transform_key = rng.choice(["rotate_90_cw", "rotate_180", "rotate_270_cw",
                                     "dilation_2", "dilation_3"])
        image, correct_desc, params = _apply_transform(preimage, transform_key, rng)

        # Ask: what are the coordinates of a specific vertex after transformation?
        ask_idx = rng.randint(0, len(preimage) - 1)
        ask_label = VERTEX_LABELS[ask_idx]
        correct_coord = image[ask_idx]
        correct_str = f"({correct_coord[0]}, {correct_coord[1]})"

        all_verts = preimage + image
        x_range, y_range = _grid_range(all_verts)
        svg = coord_grid_polygon_svg(x_range, y_range,
                                      preimage=preimage, image=image,
                                      img_label="'")

        # Generate distractor coordinates
        dists = set()
        orig = preimage[ask_idx]
        dists.add(f"({orig[0]}, {orig[1]})")  # unchanged
        dists.add(f"({-correct_coord[0]}, {correct_coord[1]})")  # wrong sign
        dists.add(f"({correct_coord[0]}, {-correct_coord[1]})")  # wrong sign
        dists.add(f"({correct_coord[1]}, {correct_coord[0]})")  # swapped
        dists.discard(correct_str)
        dist_list = list(dists)
        rng.shuffle(dist_list)
        dist_list = dist_list[:3]

        all_options = [(correct_str, True)] + [(d, False) for d in dist_list]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text,
                text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        pre_str = _fmt_vertices(preimage)

        stem_text = (
            f"Triangle ABC has vertices {pre_str}.\n"
            f"The triangle undergoes {correct_desc}.\n\n"
            f"What are the coordinates of {ask_label}'?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.MEDIUM, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=(
                f"Apply {correct_desc} to {ask_label}{orig}:\n"
                f"{ask_label}' = {correct_str}"
            ),
            choices=choices,
            context_scenario="find vertex coordinates",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx,
            render_data={"svg_html": svg, "type": "svg_html"},
        )

    # ================================================================
    # STEM 3: At Proficiency - NR (DOK 2, Medium)
    # Perform transformation, give coordinates of resulting vertex
    # ================================================================

    def stem3_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        preimage = _gen_triangle(rng)

        transform_key = rng.choice(["translation", "reflect_x", "reflect_y",
                                     "rotate_90_cw", "rotate_180", "rotate_270_cw"])
        image, correct_desc, params = _apply_transform(preimage, transform_key, rng)

        # Ask for all vertices of the image
        img_str = _fmt_vertices(image, "'")
        pre_str = _fmt_vertices(preimage)

        all_verts = preimage + image
        x_range, y_range = _grid_range(all_verts)
        svg = coord_grid_polygon_svg(x_range, y_range,
                                      preimage=preimage)

        stem_text = (
            f"Triangle ABC has vertices {pre_str}.\n\n"
            f"Perform {correct_desc} on triangle ABC.\n"
            f"What are the coordinates of A', B', and C'?"
        )

        answer = img_str

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=(
                f"Apply {correct_desc}:\n"
                + "\n".join(
                    f"  {VERTEX_LABELS[i]}{preimage[i]} -> {VERTEX_LABELS[i]}'{image[i]}"
                    for i in range(len(preimage))
                )
            ),
            context_scenario="perform transformation",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx,
            render_data={"svg_html": svg, "type": "svg_html"},
        )

    # ================================================================
    # STEM 4: Above Proficiency - MP (DOK 3, Difficult)
    # Two transformations chained
    # ================================================================

    def stem4_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        preimage = _gen_triangle(rng)

        # Pick two different transformations
        all_keys = ["translation", "reflect_x", "reflect_y",
                     "rotate_90_cw", "rotate_180"]
        t1_key = rng.choice(all_keys)
        t2_key = rng.choice(all_keys)
        while t2_key == t1_key:
            t2_key = rng.choice(all_keys)

        image1, desc1, params1 = _apply_transform(preimage, t1_key, rng)
        image2, desc2, params2 = _apply_transform(image1, t2_key, rng)

        pre_str = _fmt_vertices(preimage)
        img1_str = _fmt_vertices(image1, "'")
        img2_str = _fmt_vertices(image2, "''")

        all_verts = preimage + image1 + image2
        x_range, y_range = _grid_range(all_verts)
        svg = coord_grid_polygon_svg(x_range, y_range,
                                      preimage=preimage)

        part_a = QuestionPart(
            label="Part A",
            prompt=f"Perform {desc1} on triangle ABC. What are the coordinates of A', B', and C'?",
            prompt_latex=f"Perform {desc1} on triangle ABC. What are the coordinates of A', B', and C'?",
            answer=img1_str,
            answer_latex=img1_str,
            item_type=ItemType.NR,
        )

        part_b = QuestionPart(
            label="Part B",
            prompt=f"Now perform {desc2} on triangle A'B'C'. What are the coordinates of A'', B'', and C''?",
            prompt_latex=f"Now perform {desc2} on triangle A'B'C'. What are the coordinates of A'', B'', and C''?",
            answer=img2_str,
            answer_latex=img2_str,
            item_type=ItemType.NR,
        )

        stem_text = (
            f"Triangle ABC has vertices {pre_str}.\n\n"
            f"Part A\n"
            f"Perform {desc1} on triangle ABC. "
            f"What are the coordinates of A', B', and C'?\n\n"
            f"Part B\n"
            f"Now perform {desc2} on triangle A'B'C'. "
            f"What are the coordinates of A'', B'', and C''?"
        )

        answer_text = f"Part A: {img1_str} | Part B: {img2_str}"

        solution_lines = [f"Part A: Apply {desc1}:"]
        for i in range(len(preimage)):
            solution_lines.append(
                f"  {VERTEX_LABELS[i]}{preimage[i]} -> {VERTEX_LABELS[i]}'{image1[i]}"
            )
        solution_lines.append(f"\nPart B: Apply {desc2}:")
        for i in range(len(image1)):
            solution_lines.append(
                f"  {VERTEX_LABELS[i]}'{image1[i]} -> {VERTEX_LABELS[i]}''{image2[i]}"
            )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.DIFFICULT, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_text, answer_latex=answer_text,
            worked_solution="\n".join(solution_lines),
            parts=[part_a, part_b],
            context_scenario="two transformations",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx,
            render_data={"svg_html": svg, "type": "svg_html"},
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
                    import traceback
                    traceback.print_exc()
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
    print("Generating 8.GM.1 question variants...")
    gen = Stem8GM1(seed=42)
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
    print(f"\nTotal: {len(all_q)}")
