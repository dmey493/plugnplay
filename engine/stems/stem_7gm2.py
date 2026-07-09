"""
Stem generator for 7.GM.2:
  Identify and use the formulas for the area and circumference of a circle
  to solve problems. Give an informal derivation of the relationship between
  the circumference and area of a circle.

Content Limits:
  - Solutions may be in terms of \u03c0 or rounded to a specified place value
  - A reference sheet with circle formulas should be provided
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: Whole-number radius/diameter, answers in terms of \u03c0
  Medium: Whole-number radius/diameter, answers rounded to nearest tenth/hundredth
  Difficult: Decimal radius/diameter, multi-step problems

4 Stems from the Item Spec:
  Stem 1 (Below-MC):       Calculate area or circumference given r or d (DOK 1, Easy/Medium)
  Stem 2 (Approaching-NR): Find r or d from circumference or area (DOK 2, Easy)
  Stem 3 (At-NR):          Real-world circle problem (DOK 2, Easy/Medium)
  Stem 4 (Above-MP):       Multi-step investigation (DOK 3, Easy)
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
from engine.svg_helpers import circle_svg, annulus_svg


STANDARD_CODE = "7.GM.2"
VARIANTS_PER_STEM = 20

PI = math.pi


# ============================================================
# HELPERS
# ============================================================

def _fmt_pi(coeff):
    """Format a coefficient of pi for display, e.g. '25\u03c0'."""
    if coeff == int(coeff):
        coeff = int(coeff)
    return f"{coeff}\u03c0"


def _fmt_rounded(val, places=2):
    """Format a decimal value rounded to given places."""
    if places == 1:
        return f"{val:.1f}"
    return f"{val:.2f}"


class Stem7GM2:
    """Generates ~20 variants for each of 4 stems from the 7.GM.2 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 1, Easy/Medium)
    # Calculate area or circumference given r or d
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        r = rng.randint(2, 15)
        d = 2 * r

        # Alternate between area and circumference, given r vs given d
        calc_type = rng.choice(["area_r", "area_d", "circ_r", "circ_d"])
        # Alternate between pi-form and decimal
        use_pi = rng.choice([True, False])

        if use_pi:
            difficulty = Difficulty.EASY
        else:
            difficulty = Difficulty.MEDIUM

        if calc_type == "area_r":
            given = f"radius = {r}"
            show_radius = True
            show_diameter = False
            label = f"r = {r}"
            correct_pi = r * r  # coefficient of pi
            correct_dec = PI * r * r
            what = "area"
            unit_label = "square units"
            formula = f"A = \u03c0r\u00b2 = \u03c0({r})\u00b2 = {_fmt_pi(correct_pi)}"
        elif calc_type == "area_d":
            given = f"diameter = {d}"
            show_radius = False
            show_diameter = True
            label = f"d = {d}"
            correct_pi = r * r
            correct_dec = PI * r * r
            what = "area"
            unit_label = "square units"
            formula = f"A = \u03c0r\u00b2 = \u03c0({r})\u00b2 = {_fmt_pi(correct_pi)} (r = {d}/2 = {r})"
        elif calc_type == "circ_r":
            given = f"radius = {r}"
            show_radius = True
            show_diameter = False
            label = f"r = {r}"
            correct_pi = 2 * r
            correct_dec = 2 * PI * r
            what = "circumference"
            unit_label = "units"
            formula = f"C = 2\u03c0r = 2\u03c0({r}) = {_fmt_pi(correct_pi)}"
        else:  # circ_d
            given = f"diameter = {d}"
            show_radius = False
            show_diameter = True
            label = f"d = {d}"
            correct_pi = d
            correct_dec = PI * d
            what = "circumference"
            unit_label = "units"
            formula = f"C = \u03c0d = \u03c0({d}) = {_fmt_pi(correct_pi)}"

        if use_pi:
            correct_str = _fmt_pi(correct_pi)
            # Distractors in pi form
            dists = set()
            if "area" in calc_type:
                dists.add(_fmt_pi(2 * r))       # used circumference formula
                dists.add(_fmt_pi(r * r * 2))   # doubled
                dists.add(_fmt_pi(d * d))        # used diameter instead of radius
            else:
                dists.add(_fmt_pi(r * r))        # used area formula
                dists.add(_fmt_pi(r))            # forgot the 2
                dists.add(_fmt_pi(d * 2))        # doubled diameter
            dists.discard(correct_str)
        else:
            correct_str = _fmt_rounded(correct_dec)
            dists = set()
            if "area" in calc_type:
                dists.add(_fmt_rounded(2 * PI * r))
                dists.add(_fmt_rounded(PI * d * d))
                dists.add(_fmt_rounded(PI * r * r * 2))
            else:
                dists.add(_fmt_rounded(PI * r * r))
                dists.add(_fmt_rounded(PI * r))
                dists.add(_fmt_rounded(2 * PI * d))
            dists.discard(correct_str)

        dist_list = list(dists)
        rng.shuffle(dist_list)
        dist_list = dist_list[:3]
        while len(dist_list) < 3:
            offset = rng.choice([1, 2, 3])
            d_val = correct_pi + offset if use_pi else correct_dec + offset
            d_str = _fmt_pi(d_val) if use_pi else _fmt_rounded(d_val)
            if d_str != correct_str and d_str not in dist_list:
                dist_list.append(d_str)

        all_options = [(correct_str, True)] + [(d_s, False) for d_s in dist_list[:3]]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=f"{text} {unit_label}",
                text_latex=f"${text}$ {unit_label}",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        svg = circle_svg(r if show_radius else d,
                         label_text=label,
                         show_radius=show_radius,
                         show_diameter=show_diameter)

        answer_format = "in terms of \u03c0" if use_pi else "rounded to the nearest hundredth"
        stem_text = (
            f"A circle is shown with {given}.\n\n"
            f"What is the {what} of the circle, {answer_format}?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               difficulty, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=difficulty, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=formula,
            choices=choices,
            context_scenario=f"circle {what}",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx,
            render_data={"svg_html": svg, "type": "svg_html"},
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - NR (DOK 2, Easy)
    # Find r or d from circumference or area (given in terms of \u03c0)
    # ================================================================

    def stem2_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        r = rng.randint(2, 20)
        d = 2 * r

        calc_type = rng.choice(["r_from_C", "d_from_C", "r_from_A", "d_from_A"])

        if calc_type == "r_from_C":
            c_coeff = 2 * r  # C = 2πr => coeff = 2r
            given = f"circumference = {_fmt_pi(c_coeff)}"
            answer = str(r)
            find = "radius"
            solution = f"C = 2\u03c0r\n{_fmt_pi(c_coeff)} = 2\u03c0r\nr = {c_coeff}/2 = {r}"
        elif calc_type == "d_from_C":
            c_coeff = d  # C = πd => coeff = d
            given = f"circumference = {_fmt_pi(c_coeff)}"
            answer = str(d)
            find = "diameter"
            solution = f"C = \u03c0d\n{_fmt_pi(c_coeff)} = \u03c0d\nd = {d}"
        elif calc_type == "r_from_A":
            a_coeff = r * r  # A = πr² => coeff = r²
            given = f"area = {_fmt_pi(a_coeff)} square units"
            answer = str(r)
            find = "radius"
            solution = f"A = \u03c0r\u00b2\n{_fmt_pi(a_coeff)} = \u03c0r\u00b2\nr\u00b2 = {a_coeff}\nr = sqrt({a_coeff}) = {r}"
        else:  # d_from_A
            a_coeff = r * r
            given = f"area = {_fmt_pi(a_coeff)} square units"
            answer = str(d)
            find = "diameter"
            solution = f"A = \u03c0r\u00b2\n{_fmt_pi(a_coeff)} = \u03c0r\u00b2\nr\u00b2 = {a_coeff}\nr = {r}\nd = 2r = {d}"

        stem_text = (
            f"A circle has a {given}.\n\n"
            f"What is the {find} of the circle?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=solution,
            context_scenario=f"find {find}",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx,
        )

    # ================================================================
    # STEM 3: At Proficiency - NR (DOK 2, Easy/Medium)
    # Real-world circle problem
    # ================================================================

    def stem3_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        name = pick_name(rng)

        context_type = rng.choice([
            "garden_fence", "pool_cover", "pizza", "wheel_distance", "sprinkler"
        ])

        if context_type == "garden_fence":
            # Circumference: fence around circular garden
            r = rng.randint(3, 12)
            d = 2 * r
            circumference = round(PI * d, 2)
            given_what = rng.choice(["radius", "diameter"])
            if given_what == "radius":
                given_val = r
                given_str = f"radius of {r} feet"
            else:
                given_val = d
                given_str = f"diameter of {d} feet"

            stem_text = (
                f"{name} wants to put a fence around a circular garden with a {given_str}.\n\n"
                f"How many feet of fencing does {name} need? Round to the nearest hundredth."
            )
            answer = f"{circumference}"
            solution = f"C = \u03c0d = \u03c0({d}) = {circumference} feet"
            difficulty = Difficulty.MEDIUM
            svg = circle_svg(r, label_text=f"{given_what[0]} = {given_val} ft",
                             show_radius=(given_what == "radius"),
                             show_diameter=(given_what == "diameter"))

        elif context_type == "pool_cover":
            # Area: circular pool cover
            r = rng.randint(3, 10)
            area = round(PI * r * r, 2)

            stem_text = (
                f"{name} needs to buy a cover for a circular pool with a radius of {r} meters.\n\n"
                f"What is the area of the pool cover? Round to the nearest hundredth."
            )
            answer = f"{area}"
            solution = f"A = \u03c0r\u00b2 = \u03c0({r})\u00b2 = \u03c0({r*r}) = {area} square meters"
            difficulty = Difficulty.MEDIUM
            svg = circle_svg(r, label_text=f"r = {r} m", show_radius=True)

        elif context_type == "pizza":
            # Area: pizza comparison
            r = rng.randint(4, 9)
            area_pi = r * r
            area_dec = round(PI * r * r, 2)
            use_pi = rng.choice([True, False])

            stem_text = (
                f"A pizza has a diameter of {2*r} inches.\n\n"
                f"What is the area of the pizza" +
                (f", in terms of \u03c0?" if use_pi else f"? Round to the nearest hundredth.")
            )
            if use_pi:
                answer = f"{_fmt_pi(area_pi)}"
                difficulty = Difficulty.EASY
            else:
                answer = f"{area_dec}"
                difficulty = Difficulty.MEDIUM
            solution = f"r = {2*r}/2 = {r}\nA = \u03c0r\u00b2 = \u03c0({r})\u00b2 = {_fmt_pi(area_pi)} = {area_dec} sq in."
            svg = circle_svg(r, label_text=f"d = {2*r} in.",
                             show_radius=False, show_diameter=True)

        elif context_type == "wheel_distance":
            # Circumference * rotations = distance
            r = rng.randint(1, 4)
            d = 2 * r
            rotations = rng.randint(5, 20)
            circumference = round(PI * d, 2)
            total_distance = round(circumference * rotations, 2)

            stem_text = (
                f"A wheel has a radius of {r} feet. The wheel makes {rotations} complete rotations.\n\n"
                f"How far does the wheel travel? Round to the nearest hundredth."
            )
            answer = f"{total_distance}"
            solution = (
                f"C = 2\u03c0r = 2\u03c0({r}) = {circumference} ft\n"
                f"Distance = {rotations} * {circumference} = {total_distance} ft"
            )
            difficulty = Difficulty.MEDIUM
            svg = circle_svg(r, label_text=f"r = {r} ft", show_radius=True)

        else:  # sprinkler
            # Area: circular coverage
            r = rng.randint(5, 15)
            area_pi = r * r
            area_dec = round(PI * r * r, 2)
            use_pi = rng.choice([True, False])

            stem_text = (
                f"A sprinkler waters a circular area with a radius of {r} yards.\n\n"
                f"What is the total area watered by the sprinkler" +
                (f", in terms of \u03c0?" if use_pi else f"? Round to the nearest hundredth.")
            )
            if use_pi:
                answer = f"{_fmt_pi(area_pi)}"
                difficulty = Difficulty.EASY
            else:
                answer = f"{area_dec}"
                difficulty = Difficulty.MEDIUM
            solution = f"A = \u03c0r\u00b2 = \u03c0({r})\u00b2 = {_fmt_pi(area_pi)} = {area_dec} sq yd"
            svg = circle_svg(r, label_text=f"r = {r} yd", show_radius=True)

        render = {"svg_html": svg, "type": "svg_html"}

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               difficulty, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=difficulty, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=solution,
            context_scenario=context_type,
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx,
            render_data=render,
        )

    # ================================================================
    # STEM 4: Above Proficiency - MP (DOK 3, Easy)
    # Multi-step investigation
    # ================================================================

    def stem4_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        name = pick_name(rng)

        scenario_type = rng.choice(["bike_tire", "radius_doubling", "ring_area"])

        if scenario_type == "bike_tire":
            # Part A: find circumference. Part B: how many rotations for a distance
            r = rng.randint(1, 3)
            d = 2 * r
            distance = rng.choice([100, 200, 300, 500, 1000])
            circumference = round(PI * d, 2)
            rotations = round(distance / circumference, 2)

            part_a = QuestionPart(
                label="Part A",
                prompt=f"A bicycle tire has a diameter of {d} feet. What is the circumference of the tire? Round to the nearest hundredth.",
                prompt_latex=f"A bicycle tire has a diameter of {d} feet. What is the circumference of the tire? Round to the nearest hundredth.",
                answer=f"{circumference} ft",
                answer_latex=f"{circumference} ft",
                item_type=ItemType.NR,
            )

            part_b = QuestionPart(
                label="Part B",
                prompt=f"How many complete rotations does the tire make to travel {distance} feet? Round to the nearest hundredth.",
                prompt_latex=f"How many complete rotations does the tire make to travel {distance} feet? Round to the nearest hundredth.",
                answer=f"{rotations}",
                answer_latex=f"{rotations}",
                item_type=ItemType.NR,
            )

            stem_text = (
                f"{name} is riding a bicycle. The tire has a diameter of {d} feet.\n\n"
                f"Part A\n"
                f"What is the circumference of the tire? Round to the nearest hundredth.\n\n"
                f"Part B\n"
                f"How many complete rotations does the tire make to travel {distance} feet? Round to the nearest hundredth."
            )

            answer_text = f"Part A: {circumference} ft | Part B: {rotations}"
            solution = (
                f"Part A: C = \u03c0d = \u03c0({d}) = {circumference} ft\n"
                f"Part B: rotations = {distance} / {circumference} = {rotations}"
            )
            svg = circle_svg(r, label_text=f"d = {d} ft",
                             show_radius=False, show_diameter=True)

        elif scenario_type == "radius_doubling":
            # Part A: area with radius r. Part B: area with radius 2r. Compare.
            r = rng.randint(3, 8)
            area1 = r * r  # coefficient of pi
            area2 = (2 * r) * (2 * r)  # coefficient of pi

            part_a = QuestionPart(
                label="Part A",
                prompt=f"A circle has a radius of {r} cm. What is the area in terms of \u03c0?",
                prompt_latex=f"A circle has a radius of {r} cm. What is the area in terms of \u03c0?",
                answer=f"{_fmt_pi(area1)} sq cm",
                answer_latex=f"${area1}\\pi$ sq cm",
                item_type=ItemType.NR,
            )

            part_b = QuestionPart(
                label="Part B",
                prompt=f"If the radius is doubled to {2*r} cm, what is the new area in terms of \u03c0? How many times larger is the new area compared to the original?",
                prompt_latex=f"If the radius is doubled to {2*r} cm, what is the new area in terms of \u03c0? How many times larger is the new area compared to the original?",
                answer=f"{_fmt_pi(area2)} sq cm; 4 times larger",
                answer_latex=f"${area2}\\pi$ sq cm; 4 times larger",
                item_type=ItemType.NR,
            )

            stem_text = (
                f"{name} is investigating how the area of a circle changes when the radius changes.\n\n"
                f"Part A\n"
                f"A circle has a radius of {r} cm. What is the area in terms of \u03c0?\n\n"
                f"Part B\n"
                f"If the radius is doubled to {2*r} cm, what is the new area in terms of \u03c0? "
                f"How many times larger is the new area compared to the original?"
            )

            answer_text = f"Part A: {_fmt_pi(area1)} sq cm | Part B: {_fmt_pi(area2)} sq cm, 4 times larger"
            solution = (
                f"Part A: A = \u03c0({r})\u00b2 = {_fmt_pi(area1)} sq cm\n"
                f"Part B: A = \u03c0({2*r})\u00b2 = {_fmt_pi(area2)} sq cm\n"
                f"Ratio: {area2}/{area1} = 4 times larger"
            )
            svg = circle_svg(r, label_text=f"r = {r} cm", show_radius=True)

        else:  # ring_area
            # Part A: area of outer circle. Part B: area of ring (outer - inner)
            r_inner = rng.randint(3, 7)
            r_outer = r_inner + rng.randint(2, 5)
            area_outer_pi = r_outer * r_outer
            area_inner_pi = r_inner * r_inner
            ring_pi = area_outer_pi - area_inner_pi

            part_a = QuestionPart(
                label="Part A",
                prompt=f"A circular ring has an outer radius of {r_outer} in. and an inner radius of {r_inner} in. What is the area of the outer circle in terms of \u03c0?",
                prompt_latex=f"A circular ring has an outer radius of {r_outer} in. and an inner radius of {r_inner} in. What is the area of the outer circle in terms of \u03c0?",
                answer=f"{_fmt_pi(area_outer_pi)} sq in.",
                answer_latex=f"${area_outer_pi}\\pi$ sq in.",
                item_type=ItemType.NR,
            )

            part_b = QuestionPart(
                label="Part B",
                prompt=f"What is the area of the ring (the shaded region between the two circles) in terms of \u03c0?",
                prompt_latex=f"What is the area of the ring (the shaded region between the two circles) in terms of \u03c0?",
                answer=f"{_fmt_pi(ring_pi)} sq in.",
                answer_latex=f"${ring_pi}\\pi$ sq in.",
                item_type=ItemType.NR,
            )

            stem_text = (
                f"A circular ring has an outer radius of {r_outer} in. and an inner radius of {r_inner} in.\n\n"
                f"Part A\n"
                f"What is the area of the outer circle in terms of \u03c0?\n\n"
                f"Part B\n"
                f"What is the area of the ring (the shaded region between the two circles) in terms of \u03c0?"
            )

            answer_text = f"Part A: {_fmt_pi(area_outer_pi)} sq in. | Part B: {_fmt_pi(ring_pi)} sq in."
            solution = (
                f"Part A: A_outer = \u03c0({r_outer})\u00b2 = {_fmt_pi(area_outer_pi)} sq in.\n"
                f"Part B: A_ring = A_outer - A_inner = {_fmt_pi(area_outer_pi)} - {_fmt_pi(area_inner_pi)} = {_fmt_pi(ring_pi)} sq in."
            )
            svg = annulus_svg(r_outer, r_inner,
                             label_outer=f"R = {r_outer} in.",
                             label_inner=f"r = {r_inner} in.")

        render = {"svg_html": svg, "type": "svg_html"}

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.EASY, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.EASY, dok=3, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_text, answer_latex=answer_text,
            worked_solution=solution,
            parts=[part_a, part_b],
            context_scenario=scenario_type,
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
    print("Generating 7.GM.2 question variants...")
    gen = Stem7GM2(seed=42)
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
