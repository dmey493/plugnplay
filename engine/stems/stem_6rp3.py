"""
Stem generator for 6.RP.3:
  Make tables of equivalent ratios relating quantities with whole-number
  measurements, find missing values in the tables, and plot the pairs
  of values on the coordinate plane.

Content Limits:
  - Limit to whole numbers except when identifying a unit rate
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: compatible numbers, both single-digit
  Medium: one single-digit number
  Difficult: both double- or triple-digit, or include fraction/decimal

6 Stems from the Item Spec:
  Stem 1 (Below-MC):  Identify part-to-part vs part-to-whole ratio (DOK 1, easy)
  Stem 2 (Below-MS):  Select all ratios equivalent to a given ratio (DOK 1, medium)
  Stem 3 (Approaching-NR): Find missing value in a ratio table (DOK 2, medium)
  Stem 4 (Approaching-MC): Which table shows the same ratio relationship? (DOK 2, medium)
  Stem 5 (At-NR):     Complete ratio table and find relationship (DOK 2, medium)
  Stem 6 (Above-NR):  Compare two ratio tables (DOK 2, difficult)
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
from engine.context_pools import pick_name, CONTEXTS_6RP4
from engine.stem_guards import distinct_choices


STANDARD_CODE = "6.RP.3"
VARIANTS_PER_STEM = 20


class Stem6RP3:
    """Generates ~20 variants for each of 6 stems from the 6.RP.3 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 1, Easy)
    # Identify part-to-part vs part-to-whole ratio
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        a = rng.randint(3, 12)
        b = rng.randint(3, 12)
        total = a + b

        items = rng.choice([
            ("red marbles", "blue marbles", "marbles"),
            ("boys", "girls", "students"),
            ("cats", "dogs", "pets"),
            ("roses", "daisies", "flowers"),
            ("apples", "oranges", "fruits"),
        ])
        item_a, item_b, whole = items

        # Correct: part-to-part
        correct = f"{a} {item_a} to {b} {item_b}"
        ptp_label = "part-to-part"

        # Distractors
        d1 = f"{a} {item_a} to {total} {whole}"  # part-to-whole
        d2 = f"{b} {item_b} to {total} {whole}"  # part-to-whole
        d3 = f"{total} {whole} to {a} {item_a}"  # whole-to-part

        all_options = [(correct, True), (d1, False), (d2, False), (d3, False)]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = (
            f"A bag contains {a} {item_a} and {b} {item_b}.\n\n"
            f"Which ratio represents a part-to-part relationship?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=f"Part-to-part compares two parts: {a} {item_a} to {b} {item_b}. Part-to-whole compares a part to the total ({total}).",
            choices=choices, context_scenario="part-to-part ratio",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Below Proficiency - MS (DOK 1, Medium)
    # Select all ratios equivalent to a given ratio
    # ================================================================

    @distinct_choices
    def stem2_below_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        a = rng.randint(2, 8)
        b = rng.randint(2, 8)
        # Simplify
        g = Fraction(a, b)
        a, b = g.numerator, g.denominator

        # Equivalent ratios (correct)
        mult1 = rng.randint(2, 5)
        mult2 = rng.randint(6, 10)
        correct1 = f"{a * mult1}:{b * mult1}"
        correct2 = f"{a * mult2}:{b * mult2}"

        # Non-equivalent (wrong)
        wrong1 = f"{a + 1}:{b + 1}"  # additive error
        wrong2 = f"{b}:{a}"          # flipped
        wrong3 = f"{a * 2}:{b * 3}"  # different multipliers

        all_options = [
            (correct1, True), (correct2, True),
            (wrong1, False), (wrong2, False), (wrong3, False),
        ]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letters = ", ".join(c.key for c in choices if c.is_correct)

        stem_text = f"Select all ratios that are equivalent to {a}:{b}."

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MS,
                               Difficulty.MEDIUM, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.MS,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letters, answer_latex=correct_letters,
            worked_solution=f"Equivalent ratios are found by multiplying both parts by the same number.\n{a}:{b} x {mult1} = {correct1}\n{a}:{b} x {mult2} = {correct2}",
            choices=choices, context_scenario="equivalent ratios",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - NR (DOK 2, Medium)
    # Find missing value in a ratio table
    # ================================================================

    def stem3_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        ctx = rng.choice(CONTEXTS_6RP4)
        name = pick_name(rng)

        a = rng.randint(2, 6)
        b = rng.randint(2, 8)
        # Build table of 4 rows
        rows = [(a * i, b * i) for i in range(1, 5)]
        # Hide one value in row 3 or 4
        hide_row = rng.choice([2, 3])
        hide_col = rng.choice([0, 1])
        answer = rows[hide_row][hide_col]

        # Build table render_data
        item_a = ctx.get("item_a", "x")
        item_b = ctx.get("item_b", "y")

        table_rows = []
        for i, (va, vb) in enumerate(rows):
            if i == hide_row:
                if hide_col == 0:
                    table_rows.append(["?", str(vb)])
                else:
                    table_rows.append([str(va), "?"])
            else:
                table_rows.append([str(va), str(vb)])

        template = ctx["template"].format(name=name, a=a, b=b)

        stem_text = (
            f"{template}\n\n"
            f"The table shows equivalent ratios.\n\n"
            f"What is the missing value?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=str(answer), answer_latex=str(answer),
            worked_solution=f"The ratio is {a}:{b}. Row {hide_row + 1} uses multiplier {hide_row + 1}, so the missing value = {answer}.",
            context_scenario="ratio table missing value",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx,
            render_data={
                "type": "data_table",
                "headers": [item_a, item_b],
                "rows": table_rows,
                "orientation": "vertical",
            }
        )

    # ================================================================
    # STEM 4: Approaching Proficiency - MC (DOK 2, Medium)
    # Which table shows the same ratio relationship?
    # ================================================================

    def stem4_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        a = rng.randint(2, 6)
        b = rng.randint(2, 8)

        # Correct table: same ratio, different multipliers
        correct_mult = rng.randint(2, 5)
        correct_rows = [(a * correct_mult * i, b * correct_mult * i) for i in range(1, 4)]
        correct_label = f"{correct_rows[0][0]}:{correct_rows[0][1]}, {correct_rows[1][0]}:{correct_rows[1][1]}, {correct_rows[2][0]}:{correct_rows[2][1]}"

        # Wrong tables
        def make_wrong():
            wa = a + rng.randint(1, 3)
            wb = b + rng.randint(1, 3)
            wrows = [(wa * i, wb * i) for i in range(1, 4)]
            return f"{wrows[0][0]}:{wrows[0][1]}, {wrows[1][0]}:{wrows[1][1]}, {wrows[2][0]}:{wrows[2][1]}"

        distractors = set()
        for _ in range(10):
            distractors.add(make_wrong())
            if len(distractors) >= 3:
                break
        distractors.discard(correct_label)
        distractors = list(distractors)[:3]
        while len(distractors) < 3:
            distractors.append(make_wrong())

        all_options = [(correct_label, True)] + [(d, False) for d in distractors[:3]]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        # Reference table
        ref_rows = [(a * i, b * i) for i in range(1, 4)]
        ref_table = {
            "type": "data_table",
            "headers": ["x", "y"],
            "rows": [[str(va), str(vb)] for va, vb in ref_rows],
        }

        stem_text = (
            f"The table below shows a ratio relationship.\n\n"
            f"Which set of values has the same ratio relationship?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=f"The base ratio is {a}:{b}. The correct table multiplies both values by {correct_mult}: {correct_label}.",
            choices=choices, context_scenario="equivalent ratio tables",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx,
            render_data=ref_table,
        )

    # ================================================================
    # STEM 5: At Proficiency - NR (DOK 2, Medium)
    # Use ratio table to find a specific value
    # ================================================================

    def stem5_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        ctx = rng.choice(CONTEXTS_6RP4)
        name = pick_name(rng)

        a = rng.randint(2, 6)
        b = rng.randint(2, 8)
        target_mult = rng.randint(5, 12)
        answer = b * target_mult

        item_a = ctx.get("item_a", "x")
        item_b = ctx.get("item_b", "y")
        template = ctx["template"].format(name=name, a=a, b=b)

        # Build ratio table with missing value
        table_rows = [[str(a * i), str(b * i)] for i in range(1, 4)]
        table_rows.append([str(a * target_mult), "?"])
        table_render = {
            "type": "data_table",
            "headers": [item_a.capitalize(), item_b.capitalize()],
            "rows": table_rows,
        }

        stem_text = (
            f"{template}\n\n"
            f"Use the table below. If there are {a * target_mult} {item_a}, how many {item_b} are there?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.MEDIUM, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=str(answer), answer_latex=str(answer),
            worked_solution=f"Ratio is {a}:{b}. With {a * target_mult} {item_a}, multiplier = {target_mult}. So {item_b} = {b} x {target_mult} = {answer}.",
            context_scenario="ratio table application",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx,
            render_data=table_render,
        )

    # ================================================================
    # STEM 6: Above Proficiency - NR (DOK 3, Difficult)
    # Compare two ratio tables
    # ================================================================

    def stem6_above_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)

        name1, name2 = pick_name(rng), pick_name(rng)
        while name2 == name1:
            name2 = pick_name(rng)

        items = rng.choice([
            ("flour", "sugar", "cups"),
            ("red paint", "blue paint", "parts"),
            ("vinegar", "oil", "tablespoons"),
        ])
        item_a, item_b, unit = items

        # Two different ratios
        a1 = rng.randint(2, 5)
        b1 = rng.randint(2, 5)
        a2 = a1 + rng.randint(1, 3)
        b2 = b1

        # Same amount of item_b, different item_a
        mult = rng.randint(3, 8)
        total_b = b1 * mult

        total_a1 = a1 * mult
        total_a2 = a2 * mult
        diff = total_a2 - total_a1

        # Build ratio tables for both recipes (show 4 rows each)
        table1_rows = [[str(a1 * i), str(b1 * i)] for i in range(1, 5)]
        table2_rows = [[str(a2 * i), str(b2 * i)] for i in range(1, 5)]
        tables_render = {
            "tables": [
                {"headers": [f"{item_a} ({unit})", f"{item_b} ({unit})"],
                 "rows": table1_rows, "title": f"{name1}'s Recipe"},
                {"headers": [f"{item_a} ({unit})", f"{item_b} ({unit})"],
                 "rows": table2_rows, "title": f"{name2}'s Recipe"},
            ]
        }

        stem_text = (
            f"{name1}'s recipe uses {a1} {unit} of {item_a} for every {b1} {unit} of {item_b}.\n"
            f"{name2}'s recipe uses {a2} {unit} of {item_a} for every {b2} {unit} of {item_b}.\n\n"
            f"The tables below show equivalent ratios for each recipe.\n\n"
            f"If both use {total_b} {unit} of {item_b}, how many more {unit} of {item_a} does {name2} use than {name1}?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.NR,
                               Difficulty.DIFFICULT, 6, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=str(diff), answer_latex=str(diff),
            worked_solution=(
                f"{name1}: {a1}:{b1} ratio, with {total_b} {item_b} -> multiplier = {mult} -> {total_a1} {item_a}\n"
                f"{name2}: {a2}:{b2} ratio, with {total_b} {item_b} -> multiplier = {mult} -> {total_a2} {item_a}\n"
                f"Difference: {total_a2} - {total_a1} = {diff}"
            ),
            context_scenario="compare ratio tables",
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6, variant_index=variant_idx,
            render_data=tables_render,
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_below_ms,
            self.stem3_approaching_nr,
            self.stem4_approaching_mc,
            self.stem5_at_nr,
            self.stem6_above_nr,
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
            2: self.stem2_below_ms,
            3: self.stem3_approaching_nr,
            4: self.stem4_approaching_mc,
            5: self.stem5_at_nr,
            6: self.stem6_above_nr,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-6.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 6.RP.3 question variants...")
    gen = Stem6RP3(seed=42)
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
