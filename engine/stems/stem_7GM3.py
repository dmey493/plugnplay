"""
Stem generator for 7.GM.3:
  Know and use the formulas for the volume of cylinders and
  right rectangular prisms (composites of at least 2 prisms).

Content Limits:
  - Composite prisms: at least 2 right rectangular prisms
  - Cylinder formula NOT on reference sheet for this grade
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: Whole-number dimensions, model provided
  Medium: One dimension may be a decimal, multi-step
  Difficult: Complex composite or real-world multi-step

4 Stems from the Item Spec:
  Stem 1 (Below-NR):       V = pi*r^2*h for cylinder OR sum of prism volumes (DOK 1, Easy)
  Stem 2 (Approaching-NR): Find missing dimension from volume (DOK 2, Medium)
  Stem 3 (At-NR):          Real-world multi-step (DOK 3, Medium)
  Stem 4 (Above-MP):       Complex composite (DOK 3, Medium)
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
from engine.svg_helpers import cylinder_3d_svg, composite_prism_svg, isometric_composite_prism_svg, brick_with_holes_svg


STANDARD_CODE = "7.GM.3"
VARIANTS_PER_STEM = 20

PI = math.pi


# ============================================================
# HELPERS
# ============================================================

def _fmt_rounded(val, places=2):
    rounded = round(val, places)
    if rounded == int(rounded):
        return str(int(rounded))
    if places == 1:
        return f"{rounded:.1f}"
    return f"{rounded:.2f}"


def _make_L_shape(rng):
    """Generate an L-shaped composite of 2 rectangular prisms with labels."""
    # Horizontal base
    w1 = rng.randint(4, 10)
    h1 = rng.randint(2, 5)
    d1 = rng.randint(3, 8)

    # Vertical part (sits on one end)
    w2 = rng.randint(2, min(w1 - 1, 5))
    h2 = rng.randint(3, 8)
    d2 = d1  # same depth for clean L-shape

    v1 = w1 * h1 * d1
    v2 = w2 * h2 * d2
    total = v1 + v2

    prisms = [
        {"x": 0, "y": 0, "w": w1, "h": h1},
        {"x": 0, "y": h1, "w": w2, "h": h2},
    ]
    labels = [
        {"text": f"{w1}", "x": w1 / 2, "y": -0.5},
        {"text": f"{h1}", "x": w1 + 0.8, "y": h1 / 2},
        {"text": f"{w2}", "x": w2 / 2, "y": h1 + h2 + 0.5},
        {"text": f"{h2}", "x": -0.8, "y": h1 + h2 / 2},
    ]

    dims = {
        "w1": w1, "h1": h1, "d1": d1,
        "w2": w2, "h2": h2, "d2": d2,
        "v1": v1, "v2": v2, "total": total,
    }

    return prisms, labels, dims


class Stem7GM3:
    """Generates ~20 variants for each of 4 stems from the 7.GM.3 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - NR (DOK 1, Easy)
    # V = pi*r^2*h for cylinder OR sum of prism volumes
    # ================================================================

    def stem1_below_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        shape_type = rng.choice(["cylinder", "composite_prism"])

        if shape_type == "cylinder":
            r = rng.randint(2, 8)
            h = rng.randint(3, 12)
            volume = round(PI * r * r * h, 2)

            svg = cylinder_3d_svg(r, h, label_r=f"r = {r}", label_h=f"h = {h}")

            stem_text = (
                f"A cylinder is shown with radius {r} and height {h}.\n\n"
                f"What is the volume of the cylinder? Round to the nearest hundredth.\n"
                f"(V = \u03c0r\u00b2h)"
            )
            answer = _fmt_rounded(volume)
            solution = (
                f"V = \u03c0r\u00b2h\n"
                f"V = \u03c0({r})\u00b2({h})\n"
                f"V = \u03c0({r*r})({h})\n"
                f"V = \u03c0({r*r*h})\n"
                f"V = {answer}"
            )
            render = {"svg_html": svg, "type": "svg_html"}

        else:
            # Composite of 2 rectangular prisms (L-shape)
            prisms, labels, dims = _make_L_shape(rng)
            svg = isometric_composite_prism_svg(prisms, labels, depth=dims['d1'])

            depth_note = f" (depth = {dims['d1']} for both parts)" if dims['d1'] == dims['d2'] else ""

            stem_text = (
                f"A composite solid is made of two rectangular prisms as shown{depth_note}.\n\n"
                f"What is the total volume of the composite solid?"
            )
            answer = str(dims["total"])
            solution = (
                f"Prism 1: {dims['w1']} x {dims['h1']} x {dims['d1']} = {dims['v1']}\n"
                f"Prism 2: {dims['w2']} x {dims['h2']} x {dims['d2']} = {dims['v2']}\n"
                f"Total = {dims['v1']} + {dims['v2']} = {dims['total']}"
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
            context_scenario=shape_type,
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx,
            render_data=render,
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - NR (DOK 2, Medium)
    # Find missing dimension from volume
    # ================================================================

    def stem2_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        find_type = rng.choice(["cylinder_h", "cylinder_r"])

        if find_type == "cylinder_h":
            r = rng.randint(2, 8)
            h = rng.randint(3, 12)
            volume = round(PI * r * r * h, 2)
            svg = cylinder_3d_svg(r, h, label_r=f"r = {r}", label_h="h = ?")

            stem_text = (
                f"A cylinder has a radius of {r} and a volume of {_fmt_rounded(volume)}.\n\n"
                f"What is the height of the cylinder? Round to the nearest hundredth.\n"
                f"(V = \u03c0r\u00b2h)"
            )
            answer = str(h)
            solution = (
                f"V = \u03c0r\u00b2h\n"
                f"{_fmt_rounded(volume)} = \u03c0({r})\u00b2h\n"
                f"h = {_fmt_rounded(volume)} / (\u03c0 \u00b7 {r*r})\n"
                f"h = {_fmt_rounded(volume)} / {_fmt_rounded(PI * r*r)}\n"
                f"h = {h}"
            )

        else:  # cylinder_r
            r = rng.randint(2, 8)
            h = rng.randint(3, 12)
            volume = round(PI * r * r * h, 2)
            svg = cylinder_3d_svg(r, h, label_r="r = ?", label_h=f"h = {h}")

            stem_text = (
                f"A cylinder has a height of {h} and a volume of {_fmt_rounded(volume)}.\n\n"
                f"What is the radius of the cylinder? Round to the nearest hundredth.\n"
                f"(V = \u03c0r\u00b2h)"
            )
            answer = str(r)
            solution = (
                f"V = \u03c0r\u00b2h\n"
                f"{_fmt_rounded(volume)} = \u03c0r\u00b2({h})\n"
                f"r\u00b2 = {_fmt_rounded(volume)} / (\u03c0 \u00b7 {h})\n"
                f"r\u00b2 = {_fmt_rounded(volume / (PI * h))}\n"
                f"r = sqrt({_fmt_rounded(volume / (PI * h))}) = {r}"
            )

        render = {"svg_html": svg, "type": "svg_html"}

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.MEDIUM, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=solution,
            context_scenario=find_type,
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx,
            render_data=render,
        )

    # ================================================================
    # STEM 3: At Proficiency - NR (DOK 3, Medium)
    # Real-world multi-step
    # ================================================================

    def stem3_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        name = pick_name(rng)
        context = rng.choice(["dog_food", "candle_box", "water_tank", "paint_can"])

        if context == "dog_food":
            # Cylindrical container: how many days of food
            r = rng.randint(3, 6)
            h = rng.randint(10, 20)
            volume = round(PI * r * r * h, 2)
            daily_amount = rng.choice([20, 25, 30, 40, 50])
            days = round(volume / daily_amount, 2)

            stem_text = (
                f"{name} stores dog food in a cylindrical container with "
                f"a radius of {r} inches and a height of {h} inches. "
                f"The dog eats {daily_amount} cubic inches of food per day.\n\n"
                f"How many full days will the food last?"
            )
            answer = str(int(days))  # full days = floor
            solution = (
                f"V = \u03c0({r})\u00b2({h}) = {_fmt_rounded(volume)} cubic in.\n"
                f"Days = {_fmt_rounded(volume)} / {daily_amount} = {_fmt_rounded(days)}\n"
                f"Full days = {int(days)}"
            )
            svg = cylinder_3d_svg(r, h, label_r=f"r = {r} in.", label_h=f"h = {h} in.")

        elif context == "candle_box":
            # Cylindrical candle in rectangular box: leftover space
            r = rng.randint(2, 4)
            h = rng.randint(6, 12)
            box_w = 2 * r + rng.randint(1, 3)
            box_l = 2 * r + rng.randint(1, 3)
            box_h = h

            v_candle = round(PI * r * r * h, 2)
            v_box = box_w * box_l * box_h
            v_leftover = round(v_box - v_candle, 2)

            stem_text = (
                f"{name} places a cylindrical candle with radius {r} cm and "
                f"height {h} cm inside a rectangular box that is "
                f"{box_w} cm x {box_l} cm x {box_h} cm.\n\n"
                f"What is the volume of the empty space in the box? "
                f"Round to the nearest hundredth."
            )
            answer = _fmt_rounded(v_leftover)
            solution = (
                f"V_candle = \u03c0({r})\u00b2({h}) = {_fmt_rounded(v_candle)} cubic cm\n"
                f"V_box = {box_w} * {box_l} * {box_h} = {v_box} cubic cm\n"
                f"V_empty = {v_box} - {_fmt_rounded(v_candle)} = {answer} cubic cm"
            )
            svg = cylinder_3d_svg(r, h, label_r=f"r = {r} cm", label_h=f"h = {h} cm")

        elif context == "water_tank":
            # Cylindrical tank: gallons (1 gal = 231 cubic inches)
            r = rng.randint(5, 10)
            h = rng.randint(12, 24)
            volume = round(PI * r * r * h, 2)
            gallons = round(volume / 231, 2)

            stem_text = (
                f"A cylindrical water tank has a radius of {r} inches and "
                f"a height of {h} inches. One gallon equals 231 cubic inches.\n\n"
                f"How many gallons of water can the tank hold? "
                f"Round to the nearest hundredth."
            )
            answer = _fmt_rounded(gallons)
            solution = (
                f"V = \u03c0({r})\u00b2({h}) = {_fmt_rounded(volume)} cubic in.\n"
                f"Gallons = {_fmt_rounded(volume)} / 231 = {answer}"
            )
            svg = cylinder_3d_svg(r, h, label_r=f"r = {r} in.", label_h=f"h = {h} in.")

        else:  # paint_can
            # Cylindrical paint can: how many cans to fill a volume
            r = rng.randint(2, 5)
            h = rng.randint(8, 15)
            can_vol = round(PI * r * r * h, 2)
            target_vol = rng.choice([500, 1000, 1500, 2000, 3000])
            cans = math.ceil(target_vol / can_vol)

            stem_text = (
                f"A cylindrical paint can has a radius of {r} inches and "
                f"a height of {h} inches. {name} needs {target_vol} cubic inches "
                f"of paint.\n\n"
                f"How many full cans of paint does {name} need to buy?"
            )
            answer = str(cans)
            solution = (
                f"V_can = \u03c0({r})\u00b2({h}) = {_fmt_rounded(can_vol)} cubic in.\n"
                f"Cans needed = {target_vol} / {_fmt_rounded(can_vol)} = "
                f"{_fmt_rounded(target_vol / can_vol)}\n"
                f"Round up: {cans} cans"
            )
            svg = cylinder_3d_svg(r, h, label_r=f"r = {r} in.", label_h=f"h = {h} in.")

        render = {"svg_html": svg, "type": "svg_html"}

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=3, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=solution,
            context_scenario=context,
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx,
            render_data=render,
        )

    # ================================================================
    # STEM 4: Above Proficiency - MP (DOK 3, Medium)
    # Complex composite: brick with cylindrical holes
    # ================================================================

    def stem4_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        name = pick_name(rng)
        scenario = rng.choice(["brick_holes", "pool_steps"])

        if scenario == "brick_holes":
            # Rectangular brick with N cylindrical holes on the front face (l x h)
            # Holes go through the depth (w)
            l = rng.randint(10, 18)
            w = rng.randint(6, 14)
            h = rng.randint(6, 12)
            n_holes = rng.choice([2, 3, 4])
            # Radius must fit: diameter < height AND all holes fit across length
            max_r_height = h // 2 - 1       # leave margin so circles don't touch edges
            max_r_width = l // (2 * n_holes) # circles fit side by side
            max_r = min(max_r_height, max_r_width, 3)
            r = rng.randint(1, max(1, max_r))

            v_brick = l * w * h
            # Holes go through the depth (w), visible on the front face
            v_hole = round(PI * r * r * w, 2)
            v_holes = round(n_holes * v_hole, 2)
            v_remaining = round(v_brick - v_holes, 2)

            part_a = QuestionPart(
                label="Part A",
                prompt=f"A rectangular brick is {l} cm x {w} cm x {h} cm. What is the volume of the brick?",
                prompt_latex=f"A rectangular brick is {l} cm x {w} cm x {h} cm. What is the volume of the brick?",
                answer=f"{v_brick} cubic cm",
                answer_latex=f"{v_brick} cubic cm",
                item_type=ItemType.NR,
            )

            part_b = QuestionPart(
                label="Part B",
                prompt=f"The brick has {n_holes} cylindrical holes, each with radius {r} cm, drilled through its full depth ({w} cm). What is the remaining volume? Round to the nearest hundredth.",
                prompt_latex=f"The brick has {n_holes} cylindrical holes, each with radius {r} cm, drilled through its full depth ({w} cm). What is the remaining volume? Round to the nearest hundredth.",
                answer=_fmt_rounded(v_remaining),
                answer_latex=_fmt_rounded(v_remaining),
                item_type=ItemType.NR,
            )

            svg = brick_with_holes_svg(l, w, h, n_holes, r)

            stem_text = (
                f"A brick ({l} x {w} x {h} cm) has {n_holes} cylindrical holes "
                f"(radius {r} cm) drilled through its full depth. [FIGURE]\n\n"
                f"Part A: What is the volume of the solid brick before drilling?\n\n"
                f"Part B: What is the remaining volume after drilling? Round to the nearest hundredth."
            )
            answer_text = f"Part A: {v_brick} | Part B: {_fmt_rounded(v_remaining)}"
            solution = (
                f"Part A: V_brick = {l} x {w} x {h} = {v_brick} cubic cm\n"
                f"Part B: V_hole = \u03c0({r})\u00b2({w}) = {_fmt_rounded(v_hole)}\n"
                f"V_{n_holes}_holes = {n_holes} \u00b7 {_fmt_rounded(v_hole)} = {_fmt_rounded(v_holes)}\n"
                f"V_remaining = {v_brick} - {_fmt_rounded(v_holes)} = {_fmt_rounded(v_remaining)}"
            )
            render = {"svg_html": svg, "type": "svg_html"}

        else:  # pool_steps
            # L-shaped pool (composite prisms): volume of water
            w_shallow = rng.randint(3, 6)
            l_total = rng.randint(10, 20)
            l_shallow = rng.randint(4, l_total - 4)
            l_deep = l_total - l_shallow
            h_shallow = rng.randint(2, 4)
            h_deep = h_shallow + rng.randint(2, 5)
            width = rng.randint(5, 10)

            v_shallow = l_shallow * width * h_shallow
            v_deep = l_deep * width * h_deep
            v_total = v_shallow + v_deep

            part_a = QuestionPart(
                label="Part A",
                prompt=f"The pool has a shallow section ({l_shallow} ft long, {width} ft wide, {h_shallow} ft deep) and a deep section ({l_deep} ft long, {width} ft wide, {h_deep} ft deep). What is the volume of the shallow section?",
                prompt_latex=f"The pool has a shallow section ({l_shallow} ft long, {width} ft wide, {h_shallow} ft deep) and a deep section ({l_deep} ft long, {width} ft wide, {h_deep} ft deep). What is the volume of the shallow section?",
                answer=f"{v_shallow} cubic ft",
                answer_latex=f"{v_shallow} cubic ft",
                item_type=ItemType.NR,
            )

            part_b = QuestionPart(
                label="Part B",
                prompt=f"What is the total volume of water the pool can hold?",
                prompt_latex=f"What is the total volume of water the pool can hold?",
                answer=f"{v_total} cubic ft",
                answer_latex=f"{v_total} cubic ft",
                item_type=ItemType.NR,
            )

            stem_text = (
                f"{name}'s swimming pool has two rectangular sections.\n"
                f"- Shallow section: {l_shallow} ft long, {width} ft wide, {h_shallow} ft deep\n"
                f"- Deep section: {l_deep} ft long, {width} ft wide, {h_deep} ft deep\n\n"
                f"Part A\n"
                f"What is the volume of the shallow section?\n\n"
                f"Part B\n"
                f"What is the total volume of water the pool can hold?"
            )
            answer_text = f"Part A: {v_shallow} cubic ft | Part B: {v_total} cubic ft"
            solution = (
                f"Part A: V_shallow = {l_shallow} x {width} x {h_shallow} = {v_shallow} cubic ft\n"
                f"Part B: V_deep = {l_deep} x {width} x {h_deep} = {v_deep} cubic ft\n"
                f"V_total = {v_shallow} + {v_deep} = {v_total} cubic ft"
            )
            render = None

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.MEDIUM, dok=3, item_type=ItemType.MP,
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
    print("Generating 7.GM.3 question variants...")
    gen = Stem7GM3(seed=42)
    all_q = gen.generate_all_variants(variants_per_stem=3)
    for q in all_q:
        print(f"\n{'='*60}")
        print(f"ID: {q.question_id}")
        print(f"Stem {q.stem_index} | {q.proficiency_level.value} | {q.difficulty.value} | DOK {q.dok}")
        print(f"\n{q.stem_text}")
        print(f"\nAnswer: {q.answer_text}")
    print(f"\nTotal: {len(all_q)}")
