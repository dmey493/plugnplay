"""
Stem generator for 6.RP.4:
  Solve real-world and other mathematical problems involving rates and
  ratios using models and strategies such as reasoning about tables of
  equivalent ratios, tape diagrams, double number line diagrams, or equations.

Content Limits:
  - Limit to whole numbers except when identifying a unit rate
  - Models may be equivalent ratio tables, tape diagrams, double number lines
  - Specific strategies should NOT be tested
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: compatible numbers, both single-digit
  Medium: one single-digit number
  Difficult: both double-digit or include fraction/decimal; reverse order

6 Stems from the Item Spec:
  Stem 1 (Below-MC):  Solve simple ratio problem (DOK 1, easy)
  Stem 2 (Below-NR):  Find missing value in a proportion (DOK 1, easy)
  Stem 3 (Approaching-MC): Set up proportion for real-world problem (DOK 2, medium)
  Stem 4 (At-MP):     Part A: set up; Part B: solve real-world ratio (DOK 2, medium)
  Stem 5 (At-NR):     Solve rate problem in context (DOK 2, medium)
  Stem 6 (Above-NR):  Multi-step ratio/rate comparison (DOK 3, difficult)
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
from engine.context_pools import pick_name, pick_name_pair, CONTEXTS_6RP4


STANDARD_CODE = "6.RP.4"
VARIANTS_PER_STEM = 20


class Stem6RP4:
    """Generates ~20 variants for each of 6 stems from the 6.RP.4 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 1, Easy)
    # Solve a simple ratio problem
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        ctx = rng.choice(CONTEXTS_6RP4)
        name = pick_name(rng)
        a = rng.randint(2, 6)
        b = rng.randint(2, 6)
        mult = rng.randint(2, 5)

        item_a = ctx.get("item_a", "item A")
        item_b = ctx.get("item_b", "item B")
        template = ctx["template"].format(name=name, a=a, b=b)

        given = a * mult
        answer = b * mult

        # Distractors
        distractors = set()
        distractors.add(str(b * (mult + 1)))  # wrong multiplier
        distractors.add(str(given + b))        # added
        distractors.add(str(b * (mult - 1)) if mult > 2 else str(b * (mult + 2)))
        distractors.discard(str(answer))
        distractors = [d for d in distractors if d != str(answer)][:3]
        while len(distractors) < 3:
            d = answer + rng.choice([-3, -2, 2, 3, 5])
            if d > 0 and str(d) != str(answer) and str(d) not in distractors:
                distractors.append(str(d))
        distractors = distractors[:3]

        all_options = [(str(answer), True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = (
            f"{template}\n\n"
            f"If there are {given} {item_a}, how many {item_b} are there?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=f"Ratio {a}:{b}. Given {given} {item_a}, multiplier = {given}/{a} = {mult}. {item_b} = {b} x {mult} = {answer}.",
            choices=choices, context_scenario="ratio word problem",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Below Proficiency - NR (DOK 1, Easy)
    # Find missing value in proportion
    # ================================================================

    def stem2_below_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        name = pick_name(rng)
        rate = rng.randint(2, 10)
        units = rng.randint(3, 8)
        total = rate * units

        contexts = [
            {"setup": f"A babysitter is paid ${rate} per hour.",
             "question": f"How much will the babysitter earn in {units} hours?",
             "answer": f"${total}",
             "col_a": "Hours", "col_b": "Pay ($)"},
            {"setup": f"{name} reads {rate} pages every minute.",
             "question": f"How many pages will {name} read in {units} minutes?",
             "answer": f"{total} pages",
             "col_a": "Minutes", "col_b": "Pages"},
            {"setup": f"A car travels {rate} miles per gallon.",
             "question": f"How many miles can the car travel on {units} gallons?",
             "answer": f"{total} miles",
             "col_a": "Gallons", "col_b": "Miles"},
        ]
        ctx = rng.choice(contexts)

        # Build table rows: show a few known values, ask for the target
        table_rows = []
        for i in range(1, units + 1):
            if i == units:
                table_rows.append([str(i), "?"])
            else:
                table_rows.append([str(i), str(rate * i)])

        stem_text = f"{ctx['setup']}\n\n{ctx['question']}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.NR,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=ctx["answer"], answer_latex=ctx["answer"],
            worked_solution=f"{rate} x {units} = {total}",
            context_scenario="rate application",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx,
            render_data={
                "type": "data_table",
                "headers": [ctx["col_a"], ctx["col_b"]],
                "rows": table_rows,
                "orientation": "vertical",
            }
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - MC (DOK 2, Medium)
    # Ratio word problem with one single-digit number
    # ================================================================

    def stem3_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        ctx = rng.choice(CONTEXTS_6RP4)
        name = pick_name(rng)

        a = rng.randint(2, 6)
        b = rng.randint(8, 20)
        mult = rng.randint(4, 10)
        given = a * mult
        answer = b * mult

        item_a = ctx.get("item_a", "item A")
        item_b = ctx.get("item_b", "item B")
        template = ctx["template"].format(name=name, a=a, b=b)

        # Build table: show a few known rows, then the target row with "?"
        table_rows = []
        for i in range(1, mult + 1):
            if i == mult:
                table_rows.append([str(a * i), "?"])
            elif i <= 3:
                table_rows.append([str(a * i), str(b * i)])
        # Ensure target row is included
        if mult > 4:
            table_rows = table_rows[:3] + [[str(given), "?"]]

        # Distractors
        distractors = set()
        distractors.add(str(a * b))              # multiplied a and b
        distractors.add(str(given + b))           # added
        distractors.add(str(b * (mult + 1)))      # wrong multiplier
        distractors.discard(str(answer))
        distractors = [d for d in distractors if d != str(answer)][:3]
        while len(distractors) < 3:
            d = answer + rng.choice([-10, -5, 5, 10])
            if d > 0 and str(d) != str(answer) and str(d) not in distractors:
                distractors.append(str(d))
        distractors = distractors[:3]

        all_options = [(str(answer), True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = (
            f"{template}\n\n"
            f"The table shows this ratio relationship.\n\n"
            f"If there are {given} {item_a}, how many {item_b} are there?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=f"Ratio {a}:{b}. Given {given} {item_a}, multiplier = {given}/{a} = {mult}. {item_b} = {b} x {mult} = {answer}.",
            choices=choices, context_scenario="ratio word problem",
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
    # STEM 4: At Proficiency - MP (DOK 2, Medium)
    # Part A: identify ratio; Part B: solve
    # ================================================================

    def stem4_at_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        name = pick_name(rng)

        items = rng.choice([
            ("large popcorn", "small popcorn"),
            ("cheese pizzas", "pepperoni pizzas"),
            ("fiction books", "nonfiction books"),
        ])

        a = rng.randint(2, 5)
        b = rng.randint(2, 5)
        while a == b:
            b = rng.randint(2, 5)

        given_b = b * rng.randint(20, 60)
        mult = given_b // b
        answer_a = a * mult

        stem_text = (
            f"A store sells {items[0]} and {items[1]} in a ratio of {a}:{b}.\n\n"
            f"Part A: If the store sold {given_b} {items[1]}, what expression can be used to "
            f"find the number of {items[0]} sold?\n\n"
            f"Part B: How many {items[0]} were sold?"
        )

        expr = f"({given_b} / {b}) x {a}"

        part_a = QuestionPart(
            label="Part A", prompt=f"Expression to find {items[0]}",
            prompt_latex=f"Expression to find {items[0]}",
            answer=expr, answer_latex=f"${expr}$",
            item_type=ItemType.EQ,
        )
        part_b = QuestionPart(
            label="Part B", prompt=f"How many {items[0]}?",
            prompt_latex=f"How many {items[0]}?",
            answer=str(answer_a), answer_latex=str(answer_a),
            item_type=ItemType.NR,
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MP,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"Part A: {expr}; Part B: {answer_a}",
            answer_latex=f"Part A: ${expr}$; Part B: {answer_a}",
            worked_solution=f"Ratio {a}:{b}. Multiplier = {given_b}/{b} = {mult}. {items[0]} = {a} x {mult} = {answer_a}.",
            parts=[part_a, part_b],
            context_scenario="ratio proportion",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: At Proficiency - NR (DOK 2, Medium)
    # Solve rate problem in context
    # ================================================================

    def stem5_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        name = pick_name(rng)

        contexts = [
            {"setup": "{name} makes lemonade using {a} teaspoons of sugar for every {b} lemons.",
             "question": "{name} has {given} lemons. How many teaspoons of sugar does {name} need?",
             "item_a": "teaspoons", "item_b": "lemons"},
            {"setup": "A garden center plants {a} flowers for every {b} feet of garden bed.",
             "question": "How many flowers are needed for {given} feet of garden bed?",
             "item_a": "flowers", "item_b": "feet"},
            {"setup": "{name} uses {a} gallons of paint for every {b} rooms.",
             "question": "How many gallons does {name} need for {given} rooms?",
             "item_a": "gallons", "item_b": "rooms"},
        ]
        ctx = rng.choice(contexts)

        a = rng.randint(2, 6)
        b = rng.randint(2, 6)
        mult = rng.randint(3, 10)
        given = b * mult
        answer = a * mult

        setup = ctx["setup"].format(name=name, a=a, b=b)
        question = ctx["question"].format(name=name, given=given)

        stem_text = f"{setup}\n\n{question}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.MEDIUM, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=str(answer), answer_latex=str(answer),
            worked_solution=f"Ratio {a}:{b}. With {given} {ctx['item_b']}, multiplier = {mult}. Answer = {a} x {mult} = {answer} {ctx['item_a']}.",
            context_scenario="rate in context",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    # STEM 6: Above Proficiency - NR (DOK 3, Difficult)
    # Compare two ratios to solve a multi-step problem
    # ================================================================

    def stem6_above_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)

        name = pick_name(rng)

        # Grocery store context from item spec
        items = rng.choice([
            ("red apples", "green apples"),
            ("chocolate cookies", "vanilla cookies"),
            ("hardcover books", "paperback books"),
        ])

        # Two months with different ratios but same amount of second item
        a1 = rng.randint(3, 8)
        b1 = rng.randint(10, 20)
        a2 = a1 + rng.randint(2, 6)
        b2 = b1  # same

        same_count = b1 * rng.randint(2, 5)
        mult1 = same_count // b1
        mult2 = same_count // b2

        total1 = a1 * mult1
        total2 = a2 * mult2
        diff = total2 - total1

        stem_text = (
            f"A grocery store sold {items[0]} and {items[1]} in two different months.\n\n"
            f"- September: For every {a1} {items[0]}, there were {b1} {items[1]}.\n"
            f"- October: For every {a2} {items[0]}, there were {b2} {items[1]}.\n\n"
            f"Each month, {same_count} {items[1]} were sold.\n"
            f"How many more {items[0]} were sold in October than in September?"
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
                f"September: {a1}:{b1}, with {same_count} {items[1]} -> multiplier = {mult1} -> {total1} {items[0]}\n"
                f"October: {a2}:{b2}, with {same_count} {items[1]} -> multiplier = {mult2} -> {total2} {items[0]}\n"
                f"Difference: {total2} - {total1} = {diff}"
            ),
            context_scenario="compare ratios",
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6, variant_index=variant_idx
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_below_nr,
            self.stem3_approaching_mc,
            self.stem4_at_mp,
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
            2: self.stem2_below_nr,
            3: self.stem3_approaching_mc,
            4: self.stem4_at_mp,
            5: self.stem5_at_nr,
            6: self.stem6_above_nr,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-6.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 6.RP.4 question variants...")
    gen = Stem6RP4(seed=42)
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
