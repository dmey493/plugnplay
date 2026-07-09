"""
Stem generator for 6.GM.4:
  Find the volume of a right rectangular prism with fractional edge lengths
  using unit cubes. Apply V = lwh and V = Bh to solve real-world problems.

Content Limits:
  - No composite rectangular prisms
  - At least one dimension should be a fraction or mixed number
  - Labels in cubic units (may be written out or exponential)
  - A graphic of the prism must be provided for Below and Approaching levels
  - Calculator: ALLOWED (four-function)

Difficulty Tiers:
  Easy: 2 whole number dimensions + 1 unit fraction or mixed number
  Medium: 1 whole number + 2 fractions or mixed numbers
  Difficult: all dimensions are fractions or mixed numbers

4 Stems from the Item Spec:
  Stem 1 (Below-NR):       Calculate volume of rectangular prism (DOK 1, Easy)
  Stem 2 (Approaching-MC): Unit cube packing problem (DOK 2, Medium)
  Stem 3 (At-NR):          Real-world volume problem (DOK 2, Medium)
  Stem 4 (Above-MP):       Multi-part: find volume + find missing edge (DOK 3, Difficult)
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


STANDARD_CODE = "6.GM.4"
VARIANTS_PER_STEM = 20


# ============================================================
# HELPERS
# ============================================================

# Allowed denominators for fractional dimensions
ALLOWED_DENOMS = [2, 3, 4, 5, 6, 8]

VOLUME_CONTEXTS = [
    ("box", "a rectangular box", "cubic inches", "in."),
    ("aquarium", "a rectangular aquarium", "cubic centimeters", "cm"),
    ("storage", "a storage container", "cubic feet", "ft"),
    ("cereal", "a cereal box", "cubic inches", "in."),
    ("gift", "a gift box", "cubic inches", "in."),
    ("planter", "a rectangular planter", "cubic centimeters", "cm"),
    ("drawer", "a desk drawer", "cubic inches", "in."),
]


def _fmt_frac(f):
    """Format a Fraction for display (mixed number if > 1)."""
    if f.denominator == 1:
        return str(int(f))
    if abs(f) >= 1:
        whole = int(f)
        remainder = abs(f) - abs(whole)
        if remainder == 0:
            return str(whole)
        return f"{whole} {remainder.numerator}/{remainder.denominator}"
    return f"{f.numerator}/{f.denominator}"


def _gen_frac_dim(rng, allow_whole=True, max_whole=8):
    """Generate a fractional dimension."""
    denom = rng.choice(ALLOWED_DENOMS)
    if allow_whole and rng.random() < 0.5:
        # Mixed number
        whole = rng.randint(1, max_whole)
        numer = rng.randint(1, denom - 1)
        return Fraction(whole * denom + numer, denom)
    else:
        # Simple fraction
        numer = rng.randint(1, denom - 1)
        return Fraction(numer, denom)


def _gen_whole_dim(rng, lo=2, hi=10):
    """Generate a whole number dimension."""
    return Fraction(rng.randint(lo, hi))


def _isometric_prism(l_val, w_val, h_val, unit_label=""):
    """Compute isometric projection of a rectangular prism for SVG rendering.
    l_val, w_val, h_val are the actual dimension values (Fraction).
    Returns render_data dict with pre-computed polygon point strings.
    """
    # Scale dimensions to pixel space (target ~80-150px for largest dimension)
    max_dim = max(float(l_val), float(w_val), float(h_val))
    scale = 100 / max_dim if max_dim > 0 else 1
    l_px = float(l_val) * scale
    w_px = float(w_val) * scale
    h_px = float(h_val) * scale

    # Ensure minimum visible size
    l_px = max(l_px, 30)
    w_px = max(w_px, 30)
    h_px = max(h_px, 30)

    cos30 = 0.866
    sin30 = 0.5
    cx, cy = 150, 200  # anchor point (front-bottom-center)

    # 8 vertices of the prism in isometric projection
    # Front face (facing viewer)
    fbl = (cx - l_px * cos30 / 2, cy)                          # front-bottom-left
    fbr = (cx + l_px * cos30 / 2, cy)                          # front-bottom-right
    ftl = (cx - l_px * cos30 / 2, cy - h_px)                   # front-top-left
    ftr = (cx + l_px * cos30 / 2, cy - h_px)                   # front-top-right

    # Back face (offset by width along the depth axis - going up-right)
    dx_w = w_px * cos30 / 2
    dy_w = w_px * sin30 / 2
    bbl = (fbl[0] + dx_w, fbl[1] - dy_w)                       # back-bottom-left
    bbr = (fbr[0] + dx_w, fbr[1] - dy_w)                       # back-bottom-right
    btl = (ftl[0] + dx_w, ftl[1] - dy_w)                       # back-top-left
    btr = (ftr[0] + dx_w, ftr[1] - dy_w)                       # back-top-right

    def pts(*vertices):
        return " ".join(f"{v[0]:.1f},{v[1]:.1f}" for v in vertices)

    # Three visible faces
    front_face = pts(fbl, fbr, ftr, ftl)
    top_face = pts(ftl, ftr, btr, btl)
    right_face = pts(fbr, bbr, btr, ftr)

    # Hidden edges (dashed)
    hidden_edges = [
        {"x1": round(fbl[0], 1), "y1": round(fbl[1], 1),
         "x2": round(bbl[0], 1), "y2": round(bbl[1], 1)},
        {"x1": round(bbl[0], 1), "y1": round(bbl[1], 1),
         "x2": round(bbr[0], 1), "y2": round(bbr[1], 1)},
        {"x1": round(bbl[0], 1), "y1": round(bbl[1], 1),
         "x2": round(btl[0], 1), "y2": round(btl[1], 1)},
    ]

    l_label = f"l = {_fmt_frac(l_val)} {unit_label}".strip()
    w_label = f"w = {_fmt_frac(w_val)} {unit_label}".strip()
    h_label = f"h = {_fmt_frac(h_val)} {unit_label}".strip()

    # Label positions
    l_label_pos = {"x": round((fbl[0] + fbr[0]) / 2, 1),
                   "y": round(cy + 18, 1)}
    w_label_pos = {"x": round((fbr[0] + bbr[0]) / 2 + 10, 1),
                   "y": round((fbr[1] + bbr[1]) / 2 + 12, 1)}
    h_label_pos = {"x": round(fbl[0] - 15, 1),
                   "y": round((fbl[1] + ftl[1]) / 2, 1)}

    return {
        "type": "rectangular_prism",
        "front_face": front_face,
        "top_face": top_face,
        "right_face": right_face,
        "hidden_edges": hidden_edges,
        "length_label": l_label,
        "width_label": w_label,
        "height_label": h_label,
        "length_label_pos": l_label_pos,
        "width_label_pos": w_label_pos,
        "height_label_pos": h_label_pos,
    }


class Stem6GM4:
    """Generates ~20 variants for each of 4 stems from the 6.GM.4 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - NR (DOK 1, Easy)
    # Calculate volume of a rectangular prism
    # ================================================================

    def stem1_below_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        # Easy: 2 whole + 1 fraction
        l = _gen_whole_dim(rng, 2, 10)
        w = _gen_whole_dim(rng, 2, 10)
        h = _gen_frac_dim(rng, allow_whole=True, max_whole=5)

        vol = l * w * h
        unit_info = rng.choice(VOLUME_CONTEXTS)
        _, desc, cubic_unit, unit_abbr = unit_info

        prism_render = _isometric_prism(l, w, h, unit_abbr)

        stem_text = (
            f"A rectangular prism is shown below.\n\n"
            f"What is the volume, in {cubic_unit}, of the rectangular prism?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.NR,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=_fmt_frac(vol), answer_latex=_fmt_frac(vol),
            worked_solution=(
                f"V = l x w x h\n"
                f"V = {_fmt_frac(l)} x {_fmt_frac(w)} x {_fmt_frac(h)}\n"
                f"V = {_fmt_frac(vol)} {cubic_unit}"
            ),
            context_scenario="rectangular prism volume",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx,
            render_data=prism_render,
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - MC (DOK 2, Medium)
    # Unit cube packing
    # ================================================================

    def stem2_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        # Choose a unit cube edge that divides nicely
        cube_denom = rng.choice([2, 3, 4])
        cube_edge = Fraction(1, cube_denom)

        # Generate prism dimensions as multiples of cube_edge
        l_mult = rng.randint(2, 6)
        w_mult = rng.randint(2, 6)
        h_mult = rng.randint(2, 5)
        l = cube_edge * l_mult
        w = cube_edge * w_mult
        h = cube_edge * h_mult

        vol_prism = l * w * h
        vol_cube = cube_edge ** 3
        num_cubes = int(vol_prism / vol_cube)

        unit_info = rng.choice(VOLUME_CONTEXTS)
        _, desc, cubic_unit, unit_abbr = unit_info

        prism_render = _isometric_prism(l, w, h, unit_abbr)

        stem_text = (
            f"A rectangular prism with dimensions "
            f"{_fmt_frac(l)} {unit_abbr} x {_fmt_frac(w)} {unit_abbr} x {_fmt_frac(h)} {unit_abbr} "
            f"is packed with cubes that measure {_fmt_frac(cube_edge)} {unit_abbr} on each side.\n\n"
            f"What is the volume, in {cubic_unit}, of the rectangular prism?"
        )

        correct_str = _fmt_frac(vol_prism)

        # Distractors
        distractors = set()
        distractors.add(str(num_cubes))                           # count of cubes, not volume
        distractors.add(_fmt_frac(vol_prism * 2))                 # double
        distractors.add(_fmt_frac(l * w))                         # forgot height
        distractors.add(_fmt_frac(Fraction(2) * (l*w + w*h + l*h)))  # surface area
        distractors.discard(correct_str)
        dist_list = [d for d in distractors if d != correct_str][:3]
        while len(dist_list) < 3:
            offset = rng.choice([1, 2, -1])
            d = _fmt_frac(vol_prism + Fraction(offset))
            if d != correct_str and d not in dist_list:
                dist_list.append(d)

        all_options = [(correct_str, True)] + [(d, False) for d in dist_list[:3]]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=f"{text} {cubic_unit}",
                text_latex=f"${text}$ {cubic_unit}",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.MEDIUM, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=(
                f"V = l x w x h = {_fmt_frac(l)} x {_fmt_frac(w)} x {_fmt_frac(h)} = {correct_str} {cubic_unit}\n"
                f"(The prism fits {l_mult} x {w_mult} x {h_mult} = {num_cubes} unit cubes of edge {_fmt_frac(cube_edge)})"
            ),
            choices=choices, context_scenario="unit cube packing",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx,
            render_data=prism_render,
        )

    # ================================================================
    # STEM 3: At Proficiency - NR (DOK 2, Medium)
    # Real-world volume problem
    # ================================================================

    def stem3_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        # Cube packing problem: how many small cubes fill the box?
        cube_denom = rng.choice([2, 3, 4, 5])
        cube_edge = Fraction(1, cube_denom)

        # Box dimensions as multiples of cube_edge
        l_mult = rng.randint(3, 10)
        w_mult = rng.randint(3, 8)
        h_mult = rng.randint(2, 6)
        l = cube_edge * l_mult
        w = cube_edge * w_mult
        h = cube_edge * h_mult

        num_cubes = l_mult * w_mult * h_mult

        PACKING_ITEMS = [
            ("dice collection", "dice"),
            ("block set", "blocks"),
            ("sugar cube container", "sugar cubes"),
            ("marble set", "cube-shaped beads"),
        ]
        item_desc, item_plural = rng.choice(PACKING_ITEMS)

        unit_info = rng.choice(VOLUME_CONTEXTS)
        _, desc, cubic_unit, unit_abbr = unit_info
        name = pick_name(rng)

        prism_render = _isometric_prism(l, w, h, unit_abbr)

        stem_text = (
            f"{name} has a wooden box that measures "
            f"{_fmt_frac(l)} {unit_abbr} long, {_fmt_frac(w)} {unit_abbr} wide, "
            f"and {_fmt_frac(h)} {unit_abbr} tall. The box is filled with "
            f"{item_plural} that are cubes with side lengths of "
            f"{_fmt_frac(cube_edge)} {unit_abbr}.\n\n"
            f"How many {item_plural} are needed to fill the box?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=str(num_cubes), answer_latex=str(num_cubes),
            worked_solution=(
                f"Cubes along length: {_fmt_frac(l)} / {_fmt_frac(cube_edge)} = {l_mult}\n"
                f"Cubes along width: {_fmt_frac(w)} / {_fmt_frac(cube_edge)} = {w_mult}\n"
                f"Cubes along height: {_fmt_frac(h)} / {_fmt_frac(cube_edge)} = {h_mult}\n"
                f"Total cubes: {l_mult} x {w_mult} x {h_mult} = {num_cubes}"
            ),
            context_scenario="cube packing",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx,
            render_data=prism_render,
        )

    # ================================================================
    # STEM 4: Above Proficiency - MP (DOK 3, Difficult)
    # Part A: find volume. Part B: find missing edge given volume.
    # ================================================================

    def stem4_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        # Cube packing per item spec: worker packs small cubes into a crate
        cube_denom = rng.choice([2, 3, 4, 5, 8])
        cube_edge = Fraction(1, cube_denom)
        cube_vol = cube_edge ** 3

        # Crate dimensions as multiples of cube_edge
        l_mult = rng.randint(3, 8)
        w_mult = rng.randint(3, 8)
        h_mult = rng.randint(2, 6)

        l = cube_edge * l_mult
        w = cube_edge * w_mult
        h = cube_edge * h_mult

        num_cubes = l_mult * w_mult * h_mult
        total_vol = num_cubes * cube_vol  # = l * w * h

        PACKING_ROLES = [
            ("worker", "square boxes"),
            ("student", "wooden blocks"),
            ("baker", "sugar cubes"),
            ("artist", "clay cubes"),
        ]
        role, item_name = rng.choice(PACKING_ROLES)
        name = pick_name(rng)

        unit_info = rng.choice(VOLUME_CONTEXTS)
        _, desc, cubic_unit, unit_abbr = unit_info

        # Figure A: show the small cube
        cube_render = _isometric_prism(cube_edge, cube_edge, cube_edge, unit_abbr)

        edge_str = _fmt_frac(cube_edge)

        # Part A: total volume
        part_a_text = (
            f"What is the total volume, in {cubic_unit}, "
            f"of the {num_cubes} {item_name}?"
        )
        part_a = QuestionPart(
            label="Part A",
            prompt=part_a_text,
            prompt_latex=part_a_text,
            answer=_fmt_frac(total_vol),
            answer_latex=_fmt_frac(total_vol),
            item_type=ItemType.NR,
        )

        # Part B: possible dimensions of the crate
        part_b_text = (
            f"What are possible dimensions, in {unit_abbr}, of the crate? "
            f"Give a set of length, width, and height values."
        )
        part_b = QuestionPart(
            label="Part B",
            prompt=part_b_text,
            prompt_latex=part_b_text,
            answer=(
                f"{_fmt_frac(l)} {unit_abbr} x {_fmt_frac(w)} {unit_abbr} x {_fmt_frac(h)} {unit_abbr}"
            ),
            answer_latex=(
                f"{_fmt_frac(l)} {unit_abbr} x {_fmt_frac(w)} {unit_abbr} x {_fmt_frac(h)} {unit_abbr}"
            ),
            item_type=ItemType.NR,
        )

        stem_text = (
            f"{name} packs {num_cubes} {item_name} (each {edge_str} {unit_abbr} "
            f"per side) into a crate with no gaps. [FIGURE]\n\n"
            f"Part A: {part_a_text}\n\n"
            f"Part B: {part_b_text}"
        )

        answer_text = (
            f"Part A: {_fmt_frac(total_vol)} | "
            f"Part B: {_fmt_frac(l)} x {_fmt_frac(w)} x {_fmt_frac(h)} {unit_abbr}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.DIFFICULT, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_text, answer_latex=answer_text,
            worked_solution=(
                f"Part A:\n"
                f"Volume of each cube = ({edge_str})^3 = {_fmt_frac(cube_vol)} {cubic_unit}\n"
                f"Total volume = {num_cubes} x {_fmt_frac(cube_vol)} = {_fmt_frac(total_vol)} {cubic_unit}\n\n"
                f"Part B:\n"
                f"Need dimensions whose product = {_fmt_frac(total_vol)}\n"
                f"One possible set: {_fmt_frac(l)} x {_fmt_frac(w)} x {_fmt_frac(h)} {unit_abbr}\n"
                f"(each dimension must be a multiple of {edge_str})"
            ),
            parts=[part_a, part_b],
            context_scenario="cube packing dimensions",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx,
            render_data=cube_render,
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_nr,
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
            1: self.stem1_below_nr,
            2: self.stem2_approaching_mc,
            3: self.stem3_at_nr,
            4: self.stem4_above_mp,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-4.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 6.GM.4 question variants...")
    gen = Stem6GM4(seed=42)
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
