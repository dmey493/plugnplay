"""
Stem generator for 8.GM.2:
  Know and use the formulas for the volumes of cones, spheres, and pyramids
  to solve real-world and mathematical problems. Know and use the formula
  for the surface area of spheres.

Content Limits:
  - Right square pyramids only (no triangular, hexagonal, etc.)
  - No cubic roots required (so don't ask "find r from sphere volume")
  - Calculator: ALLOWED
  - Some items have no model (Difficult)

Difficulty Tiers:
  Easy: Whole-number dimensions, model provided
  Medium: One decimal or find missing dimension from volume, model provided
  Difficult: Multi-step or real-world, no model

4 Stems from the Item Spec:
  Stem 1 (Below-NR):       Calculate V or SA with model (DOK 1, Easy)
  Stem 2 (Approaching-NR): Find missing dimension given volume (DOK 1, Medium)
  Stem 3 (At-NR):          Real-world problem (DOK 2, Difficult)
  Stem 4 (Above-MP):       Cross-shape or multi-step (DOK 2, Difficult)
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
from engine.svg_helpers import (
    cone_3d_svg, sphere_svg, pyramid_3d_svg,
    cone_in_cylinder_svg, pyramid_and_cube_svg,
)


STANDARD_CODE = "8.GM.2"
VARIANTS_PER_STEM = 20

PI = math.pi


# ============================================================
# HELPERS
# ============================================================

def _fmt_rounded(val, places=2):
    """Format a decimal value rounded to given places."""
    rounded = round(val, places)
    if rounded == int(rounded):
        return str(int(rounded))
    if places == 1:
        return f"{rounded:.1f}"
    return f"{rounded:.2f}"


def _fmt_pi(coeff):
    """Format coefficient of pi."""
    if coeff == int(coeff):
        coeff = int(coeff)
    return f"{coeff}\u03C0"


class Stem8GM2:
    """Generates ~20 variants for each of 4 stems from the 8.GM.2 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - NR (DOK 1, Easy)
    # Calculate V or SA with model
    # ================================================================

    def stem1_below_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        shape_type = rng.choice(["cone", "sphere", "pyramid"])
        # For cone/sphere: alternate between "in terms of \u03C0" and rounded
        use_pi = (variant_idx % 2 == 1) and shape_type != "pyramid"

        if shape_type == "cone":
            r = rng.randint(2, 10)
            h = rng.randint(3, 15)
            svg = cone_3d_svg(r, h, label_r=f"r = {r}", label_h=f"h = {h}")

            if use_pi:
                # Answer in terms of \u03C0: V = (1/3)*r²*h * pi
                coeff = Fraction(r * r * h, 3)
                answer = _fmt_pi(coeff)
                rounding_note = "Give your answer in terms of \u03C0."
            else:
                volume = round((1/3) * PI * r * r * h, 2)
                answer = _fmt_rounded(volume)
                rounding_note = "Round to the nearest hundredth."

            stem_text = (
                f"A cone is shown with radius {r} and height {h}.\n\n"
                f"What is the volume of the cone? {rounding_note}\n"
                f"(V = (1/3) * \u03C0 * r² * h)"
            )
            solution = (
                f"V = (1/3) * \u03C0 * r² * h\n"
                f"V = (1/3) * \u03C0 * {r}² * {h}\n"
                f"V = (1/3) * \u03C0 * {r*r} * {h}\n"
                f"V = (1/3) * {r*r*h} * \u03C0\n"
                f"V = {answer}"
            )

        elif shape_type == "sphere":
            r = rng.randint(2, 10)
            calc = rng.choice(["volume", "surface_area"])
            svg = sphere_svg(r, label_text=f"r = {r}")

            if calc == "volume":
                if use_pi:
                    coeff = Fraction(4 * r**3, 3)
                    answer = _fmt_pi(coeff)
                    rounding_note = "Give your answer in terms of \u03C0."
                else:
                    volume = round((4/3) * PI * r**3, 2)
                    answer = _fmt_rounded(volume)
                    rounding_note = "Round to the nearest hundredth."

                stem_text = (
                    f"A sphere is shown with radius {r}.\n\n"
                    f"What is the volume of the sphere? {rounding_note}\n"
                    f"(V = (4/3) * \u03C0 * r³)"
                )
                solution = (
                    f"V = (4/3) * \u03C0 * r³\n"
                    f"V = (4/3) * \u03C0 * {r}³\n"
                    f"V = (4/3) * \u03C0 * {r**3}\n"
                    f"V = {answer}"
                )
            else:
                if use_pi:
                    coeff = 4 * r**2
                    answer = _fmt_pi(coeff)
                    rounding_note = "Give your answer in terms of \u03C0."
                else:
                    sa = round(4 * PI * r**2, 2)
                    answer = _fmt_rounded(sa)
                    rounding_note = "Round to the nearest hundredth."

                stem_text = (
                    f"A sphere is shown with radius {r}.\n\n"
                    f"What is the surface area of the sphere? {rounding_note}\n"
                    f"(SA = 4 * \u03C0 * r²)"
                )
                solution = (
                    f"SA = 4 * \u03C0 * r²\n"
                    f"SA = 4 * \u03C0 * {r}²\n"
                    f"SA = 4 * \u03C0 * {r**2}\n"
                    f"SA = {answer}"
                )

        else:  # pyramid (no pi involved)
            s = rng.randint(3, 12)
            h = rng.randint(3, 15)
            base_area = s * s
            volume = round((1/3) * base_area * h, 2)
            svg = pyramid_3d_svg(s, h, label_base=f"s = {s}", label_h=f"h = {h}")
            stem_text = (
                f"A square pyramid is shown with base side length {s} and height {h}.\n\n"
                f"What is the volume of the pyramid? Round to the nearest hundredth.\n"
                f"(V = (1/3) * B * h, where B = s²)"
            )
            answer = _fmt_rounded(volume)
            solution = (
                f"B = s² = {s}² = {base_area}\n"
                f"V = (1/3) * B * h\n"
                f"V = (1/3) * {base_area} * {h}\n"
                f"V = {answer}"
            )

        render = {"svg_html": svg, "type": "svg_html"}

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.NR,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=solution,
            context_scenario=f"{shape_type} volume/SA",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx,
            render_data=render,
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - NR (DOK 1, Medium)
    # Find missing dimension given volume
    # No cubic roots per spec: so find h from cone/pyramid volume, or r from SA
    # ================================================================

    def stem2_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        find_type = rng.choice(["cone_h", "pyramid_h", "sphere_r_from_sa"])

        if find_type == "cone_h":
            r = rng.randint(2, 8)
            h = rng.randint(3, 12)
            volume = round((1/3) * PI * r * r * h, 2)
            svg = cone_3d_svg(r, h, label_r=f"r = {r}", label_h="h = ?")
            stem_text = (
                f"A cone has a radius of {r} and a volume of {_fmt_rounded(volume)}.\n\n"
                f"What is the height of the cone? Round to the nearest hundredth.\n"
                f"(V = (1/3) * \u03C0 * r² * h)"
            )
            answer = str(h)
            solution = (
                f"V = (1/3) * \u03C0 * r² * h\n"
                f"{_fmt_rounded(volume)} = (1/3) * \u03C0 * {r}² * h\n"
                f"{_fmt_rounded(volume)} = (1/3) * \u03C0 * {r*r} * h\n"
                f"h = {_fmt_rounded(volume)} / ((1/3) * \u03C0 * {r*r})\n"
                f"h = {_fmt_rounded(volume)} / {_fmt_rounded((1/3) * PI * r*r)}\n"
                f"h = {h}"
            )

        elif find_type == "pyramid_h":
            s = rng.randint(3, 10)
            h = rng.randint(3, 12)
            base_area = s * s
            volume = round((1/3) * base_area * h, 2)
            svg = pyramid_3d_svg(s, h, label_base=f"s = {s}", label_h="h = ?")
            stem_text = (
                f"A square pyramid has a base side length of {s} and a volume of {_fmt_rounded(volume)}.\n\n"
                f"What is the height of the pyramid?\n"
                f"(V = (1/3) * B * h, where B = s²)"
            )
            answer = str(h)
            solution = (
                f"B = {s}² = {base_area}\n"
                f"V = (1/3) * B * h\n"
                f"{_fmt_rounded(volume)} = (1/3) * {base_area} * h\n"
                f"h = 3 * {_fmt_rounded(volume)} / {base_area}\n"
                f"h = {_fmt_rounded(3 * volume / base_area)} = {h}"
            )

        else:  # sphere_r_from_sa
            r = rng.randint(2, 10)
            sa = round(4 * PI * r**2, 2)
            svg = sphere_svg(r, label_text="r = ?")
            stem_text = (
                f"A sphere has a surface area of {_fmt_rounded(sa)}.\n\n"
                f"What is the radius of the sphere? Round to the nearest hundredth.\n"
                f"(SA = 4 * \u03C0 * r²)"
            )
            answer = str(r)
            solution = (
                f"SA = 4 * \u03C0 * r²\n"
                f"{_fmt_rounded(sa)} = 4 * \u03C0 * r²\n"
                f"r² = {_fmt_rounded(sa)} / (4 * \u03C0)\n"
                f"r² = {_fmt_rounded(sa / (4 * PI))}\n"
                f"r = sqrt({_fmt_rounded(sa / (4 * PI))}) = {r}"
            )

        render = {"svg_html": svg, "type": "svg_html"}

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.MEDIUM, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=solution,
            context_scenario=f"find missing {find_type}",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx,
            render_data=render,
        )

    # ================================================================
    # STEM 3: At Proficiency - NR (DOK 2, Difficult)
    # Real-world problem (no model per spec at Difficult)
    # ================================================================

    def stem3_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        name = pick_name(rng)
        context = rng.choice(["paper_cup", "museum_pyramid", "ball", "ice_cream"])

        if context == "paper_cup":
            # Cone-shaped paper cup: find volume
            r = rng.randint(2, 5)
            h = rng.randint(6, 12)
            volume = round((1/3) * PI * r * r * h, 2)
            stem_text = (
                f"{name} has a cone-shaped paper cup with a radius of {r} cm "
                f"and a height of {h} cm.\n\n"
                f"What is the volume of the cup? Round to the nearest hundredth.\n"
                f"(V = (1/3) * \u03C0 * r² * h)"
            )
            answer = _fmt_rounded(volume)
            solution = (
                f"V = (1/3) * \u03C0 * r² * h\n"
                f"V = (1/3) * \u03C0 * {r}² * {h}\n"
                f"V = (1/3) * \u03C0 * {r*r} * {h}\n"
                f"V = {answer} cubic cm"
            )

        elif context == "museum_pyramid":
            # Square pyramid building
            s = rng.choice([10, 15, 20, 25, 30])
            h = rng.choice([8, 10, 12, 15, 20])
            base_area = s * s
            volume = round((1/3) * base_area * h, 2)
            stem_text = (
                f"A museum has a pyramid-shaped entrance with a square base "
                f"that measures {s} ft on each side and a height of {h} ft.\n\n"
                f"What is the volume of the pyramid entrance?\n"
                f"(V = (1/3) * B * h)"
            )
            answer = _fmt_rounded(volume)
            solution = (
                f"B = {s}² = {base_area} sq ft\n"
                f"V = (1/3) * {base_area} * {h}\n"
                f"V = {answer} cubic ft"
            )

        elif context == "ball":
            # Sphere: basketball/soccer ball volume
            r = rng.choice([4, 5, 6, 7])
            ball_type = rng.choice(["basketball", "soccer ball", "bowling ball"])
            volume = round((4/3) * PI * r**3, 2)
            stem_text = (
                f"A {ball_type} has a radius of approximately {r} inches.\n\n"
                f"What is the volume of the {ball_type}? Round to the nearest hundredth.\n"
                f"(V = (4/3) * \u03C0 * r³)"
            )
            answer = _fmt_rounded(volume)
            solution = (
                f"V = (4/3) * \u03C0 * r³\n"
                f"V = (4/3) * \u03C0 * {r}³\n"
                f"V = (4/3) * \u03C0 * {r**3}\n"
                f"V = {answer} cubic in."
            )

        else:  # ice_cream
            # Cone + half-sphere: ice cream cone volume
            r = rng.randint(2, 4)
            h = rng.randint(8, 14)
            v_cone = round((1/3) * PI * r * r * h, 2)
            v_half_sphere = round((2/3) * PI * r**3, 2)
            total = round(v_cone + v_half_sphere, 2)
            stem_text = (
                f"{name} has an ice cream cone with a cone radius of {r} cm "
                f"and a cone height of {h} cm. The ice cream forms a perfect "
                f"half-sphere on top with the same radius.\n\n"
                f"What is the total volume of the cone and the ice cream? "
                f"Round to the nearest hundredth.\n"
                f"(V_cone = (1/3) * \u03C0 * r² * h; V_sphere = (4/3) * \u03C0 * r³)"
            )
            answer = _fmt_rounded(total)
            solution = (
                f"V_cone = (1/3) * \u03C0 * {r}² * {h} = {_fmt_rounded(v_cone)}\n"
                f"V_half_sphere = (1/2) * (4/3) * \u03C0 * {r}³ = {_fmt_rounded(v_half_sphere)}\n"
                f"Total = {_fmt_rounded(v_cone)} + {_fmt_rounded(v_half_sphere)} = {answer}"
            )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.DIFFICULT, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=solution,
            context_scenario=context,
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx,
            render_data=None,  # No model at Difficult per spec
        )

    # ================================================================
    # STEM 4: Above Proficiency - MP (DOK 2, Difficult)
    # Cross-shape or multi-step
    # ================================================================

    def stem4_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        name = pick_name(rng)
        scenario = rng.choice(["sa_to_volume", "cone_in_cylinder", "compare_shapes"])

        if scenario == "sa_to_volume":
            # Part A: find radius from SA. Part B: find volume.
            r = rng.randint(3, 8)
            sa = round(4 * PI * r**2, 2)
            volume = round((4/3) * PI * r**3, 2)
            svg = sphere_svg(r, label_text=f"SA = {_fmt_rounded(sa)}")

            part_a = QuestionPart(
                label="Part A",
                prompt=f"A sphere has a surface area of {_fmt_rounded(sa)}. What is the radius? Round to the nearest hundredth.",
                prompt_latex=f"A sphere has a surface area of {_fmt_rounded(sa)}. What is the radius? Round to the nearest hundredth.",
                answer=str(r),
                answer_latex=str(r),
                item_type=ItemType.NR,
            )
            part_b = QuestionPart(
                label="Part B",
                prompt=f"Using the radius from Part A, what is the volume of the sphere? Round to the nearest hundredth.",
                prompt_latex=f"Using the radius from Part A, what is the volume of the sphere? Round to the nearest hundredth.",
                answer=_fmt_rounded(volume),
                answer_latex=_fmt_rounded(volume),
                item_type=ItemType.NR,
            )

            stem_text = (
                f"A sphere has a surface area of {_fmt_rounded(sa)} square units.\n\n"
                f"[FIGURE]\n\n"
                f"Part A\n"
                f"What is the radius of the sphere? Round to the nearest hundredth.\n"
                f"(SA = 4 * \u03C0 * r²)\n\n"
                f"Part B\n"
                f"Using the radius from Part A, what is the volume of the sphere? "
                f"Round to the nearest hundredth.\n"
                f"(V = (4/3) * \u03C0 * r³)"
            )
            answer_text = f"Part A: {r} | Part B: {_fmt_rounded(volume)}"
            solution = (
                f"Part A: SA = 4*\u03C0*r²\n"
                f"{_fmt_rounded(sa)} = 4*\u03C0*r²\n"
                f"r² = {_fmt_rounded(sa/(4*PI))}\n"
                f"r = {r}\n\n"
                f"Part B: V = (4/3)*\u03C0*{r}³ = {_fmt_rounded(volume)}"
            )
            render = {"svg_html": svg, "type": "svg_html"}

        elif scenario == "cone_in_cylinder":
            # Cone inscribed in cylinder: Part A = V_cylinder, Part B = V_empty (cylinder - cone)
            r = rng.randint(3, 8)
            h = rng.randint(5, 12)
            v_cyl = round(PI * r * r * h, 2)
            v_cone = round((1/3) * PI * r * r * h, 2)
            v_empty = round(v_cyl - v_cone, 2)
            svg = cone_in_cylinder_svg(r, h, label_r=f"r = {r}", label_h=f"h = {h}")

            part_a = QuestionPart(
                label="Part A",
                prompt=f"A cone with radius {r} and height {h} fits exactly inside a cylinder with the same radius and height. What is the volume of the cylinder? Round to the nearest hundredth.",
                prompt_latex=f"A cone with radius {r} and height {h} fits exactly inside a cylinder with the same radius and height. What is the volume of the cylinder? Round to the nearest hundredth.",
                answer=_fmt_rounded(v_cyl),
                answer_latex=_fmt_rounded(v_cyl),
                item_type=ItemType.NR,
            )
            part_b = QuestionPart(
                label="Part B",
                prompt=f"What is the volume of the empty space between the cone and the cylinder? Round to the nearest hundredth.",
                prompt_latex=f"What is the volume of the empty space between the cone and the cylinder? Round to the nearest hundredth.",
                answer=_fmt_rounded(v_empty),
                answer_latex=_fmt_rounded(v_empty),
                item_type=ItemType.NR,
            )

            stem_text = (
                f"A cone with radius {r} and height {h} fits exactly inside a cylinder "
                f"with the same radius and height.\n\n"
                f"[FIGURE]\n\n"
                f"Part A\n"
                f"What is the volume of the cylinder? Round to the nearest hundredth.\n"
                f"(V = \u03C0 * r² * h)\n\n"
                f"Part B\n"
                f"What is the volume of the empty space between the cone and the cylinder? "
                f"Round to the nearest hundredth."
            )
            answer_text = f"Part A: {_fmt_rounded(v_cyl)} | Part B: {_fmt_rounded(v_empty)}"
            solution = (
                f"Part A: V_cyl = \u03C0*{r}²*{h} = {_fmt_rounded(v_cyl)}\n"
                f"Part B: V_cone = (1/3)*\u03C0*{r}²*{h} = {_fmt_rounded(v_cone)}\n"
                f"V_empty = {_fmt_rounded(v_cyl)} - {_fmt_rounded(v_cone)} = {_fmt_rounded(v_empty)}"
            )
            render = {"svg_html": svg, "type": "svg_html"}

        else:  # compare_shapes
            # Compare volumes: Part A = volume of pyramid, Part B = how many pyramids fit in a cube
            s = rng.randint(4, 10)
            h = s  # pyramid height = cube side for clean comparison
            v_cube = s ** 3
            v_pyramid = round((1/3) * s * s * h, 2)
            n_pyramids = round(v_cube / v_pyramid, 2)
            svg = pyramid_and_cube_svg(s, h, label_base=f"s = {s}",
                                      label_h=f"h = {h}", label_cube=f"s = {s}")

            part_a = QuestionPart(
                label="Part A",
                prompt=f"A square pyramid has a base side length of {s} and a height of {h}. What is the volume of the pyramid?",
                prompt_latex=f"A square pyramid has a base side length of {s} and a height of {h}. What is the volume of the pyramid?",
                answer=_fmt_rounded(v_pyramid),
                answer_latex=_fmt_rounded(v_pyramid),
                item_type=ItemType.NR,
            )
            part_b = QuestionPart(
                label="Part B",
                prompt=f"A cube has side length {s}. How many pyramids from Part A would have the same total volume as the cube?",
                prompt_latex=f"A cube has side length {s}. How many pyramids from Part A would have the same total volume as the cube?",
                answer=str(int(n_pyramids)),
                answer_latex=str(int(n_pyramids)),
                item_type=ItemType.NR,
            )

            stem_text = (
                f"[FIGURE]\n\n"
                f"Part A\n"
                f"A square pyramid has a base side length of {s} and a height of {h}. "
                f"What is the volume of the pyramid?\n"
                f"(V = (1/3) * B * h)\n\n"
                f"Part B\n"
                f"A cube has side length {s}. How many pyramids from Part A would have "
                f"the same total volume as the cube?"
            )
            answer_text = f"Part A: {_fmt_rounded(v_pyramid)} | Part B: {int(n_pyramids)}"
            solution = (
                f"Part A: B = {s}² = {s*s}, V = (1/3)*{s*s}*{h} = {_fmt_rounded(v_pyramid)}\n"
                f"Part B: V_cube = {s}³ = {v_cube}\n"
                f"Number = {v_cube} / {_fmt_rounded(v_pyramid)} = {int(n_pyramids)}"
            )
            # Wide side-by-side figure: render larger in the PDF so the
            # dimension labels stay above the minimum font floor.
            render = {"svg_html": svg, "type": "svg_html",
                      "fig_max_w": 120, "fig_max_h": 80}

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.DIFFICULT, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_text, answer_latex=answer_text,
            worked_solution=solution,
            parts=[part_a, part_b],
            context_scenario=scenario,
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
            self.stem1_below_nr,
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
            1: self.stem1_below_nr,
            2: self.stem2_approaching_nr,
            3: self.stem3_at_nr,
            4: self.stem4_above_mp,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-4.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 8.GM.2 question variants...")
    gen = Stem8GM2(seed=42)
    all_q = gen.generate_all_variants(variants_per_stem=3)
    for q in all_q:
        print(f"\n{'='*60}")
        print(f"ID: {q.question_id}")
        print(f"Stem {q.stem_index} | {q.proficiency_level.value} | {q.difficulty.value} | DOK {q.dok}")
        print(f"\n{q.stem_text}")
        print(f"\nAnswer: {q.answer_text}")
    print(f"\nTotal: {len(all_q)}")
