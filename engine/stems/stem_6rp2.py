"""
Stem generator for 6.RP.2:
  Understand the concept of a unit rate and use terms related to rate
  in the context of a ratio relationship.

Content Limits:
  - Models limited to tape diagrams or double number lines
  - Rates expressed as fractions, colon, or words
  - Units may be same or different
  - Limit to whole numbers except when identifying a unit rate
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: compatible numbers, both single-digit
  Medium: one single-digit number
  Difficult: both double-digit or include fraction/decimal

6 Stems from the Item Spec:
  Stem 1 (Below-MC):  Identify which statement describes a unit rate (DOK 1, easy)
  Stem 2 (Below-NR):  Find the unit rate from a simple ratio (DOK 1, easy)
  Stem 3 (Approaching-MC): Determine unit rate from a ratio table/model (DOK 2, medium)
  Stem 4 (Approaching-NR): Find unit rate given a real-world ratio (DOK 2, medium)
  Stem 5 (At-MP):     Part A: find unit rate; Part B: use it to solve (DOK 2, medium)
  Stem 6 (Above-NR):  Find unit rate with difficult numbers (DOK 3, difficult)
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
from engine.context_pools import pick_name, CONTEXTS_6RP2


STANDARD_CODE = "6.RP.2"
VARIANTS_PER_STEM = 20


def _fmt(val):
    """Format a number for display."""
    if isinstance(val, Fraction):
        f = float(val)
        if f == int(f):
            return str(int(f))
        return f"{f:g}"
    if isinstance(val, float):
        if val == int(val):
            return str(int(val))
        return f"{val:g}"
    return str(val)


class Stem6RP2:
    """Generates ~20 variants for each of 6 stems from the 6.RP.2 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 1, Easy)
    # Identify which statement describes a unit rate
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        # Generate a rate context
        a, b = gen.ratio_pair("easy")
        name = pick_name(rng)

        # The unit rate statement has "1" as one of the quantities
        unit_rate = Fraction(b, a)
        ur_str = _fmt(unit_rate)

        rate_contexts = [
            (f"{name} drove {ur_str} miles in 1 hour", f"{name} drove {b} miles in {a} hours",
             f"{name} drove {a} miles in {b} hours", f"{name} drove {a + b} miles total"),
            (f"{name} earned ${ur_str} for 1 hour of work", f"{name} earned ${b} for {a} hours",
             f"{name} earned ${a} for {b} hours", f"{name} earned ${a + b} total"),
            (f"{name} read {ur_str} pages in 1 minute", f"{name} read {b} pages in {a} minutes",
             f"{name} read {a} pages in {b} minutes", f"{name} read {a + b} pages total"),
        ]
        ctx = rng.choice(rate_contexts)
        correct = ctx[0]
        distractors = list(ctx[1:])

        all_options = [(correct, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = "Which statement describes a unit rate?"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=f"A unit rate compares a quantity to 1 unit. {correct} is a unit rate because it uses '1 hour/minute'.",
            choices=choices, context_scenario="identify unit rate",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Below Proficiency - NR (DOK 1, Easy)
    # Calculate unit rate from a simple ratio
    # ================================================================

    def stem2_below_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        # Spec: "A ratio is given: 9 to 3. Complete the table to show the unit rate."
        # Horizontal table showing multiples of the ratio, ending at unit rate
        a = rng.randint(2, 5)  # unit rate
        b = rng.randint(2, 4)  # multiplier count

        # Build ratio table: e.g., ratio a:1 shown as columns
        # Top row: a, 2a, 3a (the bigger quantity)
        # Bottom row: 1, 2, 3 (the unit quantity)
        top_vals = [str(a * i) for i in range(b, 0, -1)]
        bot_vals = [str(i) for i in range(b, 0, -1)]

        # The table shows the full ratio first, then the unit rate has a "?"
        # e.g., top: [6, 3, ?]  bottom: [2, 1, ?] -- no, spec shows top with blanks
        # Spec image shows: top row [_, _, 9], bottom row [1, 2, 3]
        # Answer: top row [3, 6, 9], bottom [1, 2, 3]
        total = a * b
        top_display = []
        for i in range(1, b + 1):
            if i == b:
                top_display.append(str(a * i))
            else:
                top_display.append("?")
        bot_display = [str(i) for i in range(1, b + 1)]

        stem_text = (
            f"A ratio is given: {total} to {b}.\n\n"
            f"Complete the table to show the unit rate for the given ratio."
        )

        # Answer is the unit rate
        answer = str(a)

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=f"{total} / {b} = {a}. The unit rate is {a} to 1. Table: {', '.join(str(a*i) for i in range(1, b+1))} over {', '.join(str(i) for i in range(1, b+1))}.",
            context_scenario="unit rate table",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx,
            render_data={
                "type": "data_table",
                "headers": top_display,
                "rows": [bot_display],
                "orientation": "horizontal",
            }
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - MC (DOK 2, Medium)
    # Determine unit rate from a ratio (one single-digit number)
    # ================================================================

    def stem3_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        # Spec: "The double number line diagram represents a ratio."
        # Top line shows one quantity, bottom line shows the other
        # Student must determine the unit rate from the diagram
        # Difficult: unit rate may be a decimal not shown on the model

        # Generate ratio where unit rate may be a decimal (difficult)
        b = rng.choice([2, 3, 4, 5])  # bottom line max divisor
        a_per_b = rng.choice([3, 5, 7, 9, 11])  # top value per bottom unit
        # But make it so unit rate = a_per_b / b_step could be non-integer
        # e.g., top: 0, 5, 10, 15, 20  bottom: 0, 2, 4, 6, 8  => unit rate = 2.5:1
        n_ticks = rng.randint(4, 6)
        top_step = rng.randint(3, 8)
        bot_step = rng.randint(2, 4)

        top_ticks = [top_step * i for i in range(n_ticks)]
        bot_ticks = [bot_step * i for i in range(n_ticks)]

        unit_rate = Fraction(top_step, bot_step)
        ur_str = _fmt(unit_rate)

        # Distractors
        distractors = set()
        distractors.add(_fmt(Fraction(bot_step, top_step)))  # inverted
        distractors.add(f"{top_step}:{bot_step}")  # ratio, not unit rate
        distractors.add(str(top_step + bot_step))  # added
        distractors.discard(ur_str)
        distractors = [d for d in distractors if d != ur_str][:3]
        while len(distractors) < 3:
            d = float(unit_rate) + rng.choice([-1.5, -0.5, 0.5, 1.5])
            if d > 0:
                ds = _fmt(Fraction(d).limit_denominator(100))
                if ds != ur_str and ds not in distractors:
                    distractors.append(ds)
        distractors = distractors[:3]

        all_options = [(ur_str, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = (
            f"The double number line diagram represents a ratio.\n\n"
            f"What is the unit rate for this ratio?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.DIFFICULT, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=f"Top line goes by {top_step}s, bottom by {bot_step}s. Unit rate = {top_step}/{bot_step} = {ur_str}:1",
            choices=choices, context_scenario="double number line unit rate",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx,
            render_data={
                "type": "double_number_line",
                "top_ticks": top_ticks,
                "bottom_ticks": bot_ticks,
            }
        )

    # ================================================================
    # STEM 4: Approaching Proficiency - NR (DOK 2, Medium)
    # Find unit rate with one single-digit number in context
    # ================================================================

    def stem4_at_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        # Spec: "1 large pizza feeds 4 people. Choose the two statements that are true."
        # Generate a unit rate context, then build true/false statements
        unit_rate = rng.randint(3, 8)

        contexts = [
            {"setup": f"A pizza restaurant advertises that 1 large pizza will feed {unit_rate} people.",
             "unit_label": "pizzas", "rate_label": "people"},
            {"setup": f"A machine produces {unit_rate} widgets per hour.",
             "unit_label": "hours", "rate_label": "widgets"},
            {"setup": f"A recipe uses {unit_rate} cups of flour per batch.",
             "unit_label": "batches", "rate_label": "cups of flour"},
        ]
        ctx = rng.choice(contexts)

        # Build 5 statements: 2 correct, 3 wrong
        # Correct: multiplier * 1 = multiplier units, multiplier * unit_rate = total
        correct_mults = rng.sample(range(2, 10), 2)
        correct_stmts = []
        for m in correct_mults:
            correct_stmts.append(f"{m} {ctx['unit_label']} will produce {m * unit_rate} {ctx['rate_label']}.")

        # Wrong statements: use wrong multiplication
        wrong_stmts = []
        wrong_mults = [m for m in range(2, 10) if m not in correct_mults]
        rng.shuffle(wrong_mults)
        for m in wrong_mults[:3]:
            wrong_total = m * unit_rate + rng.choice([-unit_rate, unit_rate, m])
            if wrong_total <= 0:
                wrong_total = m + unit_rate
            wrong_stmts.append(f"{m} {ctx['unit_label']} will produce {wrong_total} {ctx['rate_label']}.")

        all_options = [(s, True) for s in correct_stmts] + [(s, False) for s in wrong_stmts]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=text,
                is_correct=is_correct,
            ))

        correct_letters = sorted([c.key for c in choices if c.is_correct])
        answer_str = ", ".join(correct_letters)

        stem_text = f"{ctx['setup']}\n\nChoose the two statements that are true."

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MS,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MS,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_str, answer_latex=answer_str,
            worked_solution=f"Unit rate = {unit_rate} {ctx['rate_label']} per {ctx['unit_label'][:-1]}. Multiply: {correct_mults[0]}x{unit_rate}={correct_mults[0]*unit_rate}, {correct_mults[1]}x{unit_rate}={correct_mults[1]*unit_rate}.",
            choices=choices, context_scenario="unit rate true statements",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: At Proficiency - MP (DOK 2, Medium)
    # Part A: find unit rate; Part B: use it to solve
    # ================================================================

    def stem5_at_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        name = pick_name(rng)

        # Pizza context from item spec
        contexts = [
            {"setup": "A pizza restaurant reports that 1 large pizza feeds {ur} people.",
             "question_b": "How many large pizzas are needed to feed {target} people?",
             "unit": "people per pizza"},
            {"setup": "{name} can type {ur} words per minute.",
             "question_b": "How many words can {name} type in {target} minutes?",
             "unit": "words per minute"},
            {"setup": "A factory produces {ur} widgets per hour.",
             "question_b": "How many widgets will the factory produce in {target} hours?",
             "unit": "widgets per hour"},
        ]
        ctx = rng.choice(contexts)

        # Generate clean unit rate
        ur = rng.randint(3, 12)
        a = rng.randint(3, 8)
        b = ur * a
        target = rng.randint(10, 30)
        answer_b = ur * target

        setup = ctx["setup"].format(name=name, ur=ur)
        q_b = ctx["question_b"].format(name=name, target=target)

        stem_text = (
            f"{name} reports the following:\n"
            f"- {b} items were completed in {a} sessions.\n\n"
            f"Part A:\nWhat is the unit rate, in items per session?\n\n"
            f"Part B:\nHow many items will be completed in {target} sessions?"
        )

        part_a = QuestionPart(
            label="Part A", prompt="What is the unit rate?",
            prompt_latex="What is the unit rate?",
            answer=str(ur), answer_latex=str(ur),
            item_type=ItemType.NR,
        )
        part_b = QuestionPart(
            label="Part B", prompt=f"How many items in {target} sessions?",
            prompt_latex=f"How many items in {target} sessions?",
            answer=str(answer_b), answer_latex=str(answer_b),
            item_type=ItemType.NR,
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MP,
                               Difficulty.MEDIUM, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"Part A: {ur}; Part B: {answer_b}",
            answer_latex=f"Part A: {ur}; Part B: {answer_b}",
            worked_solution=f"Part A: {b} / {a} = {ur} items per session\nPart B: {ur} x {target} = {answer_b} items",
            parts=[part_a, part_b],
            context_scenario="unit rate application",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    # STEM 6: Above Proficiency - NR (DOK 3, Difficult)
    # Error analysis: identify and explain rate calculation error
    # ================================================================

    def stem6_above_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)

        name = pick_name(rng)

        # Both double-digit
        a = rng.randint(10, 30)
        b = rng.randint(40, 200)
        correct_rate = Fraction(b, a)
        wrong_rate = Fraction(a, b)

        correct_str = _fmt(correct_rate)
        wrong_str = _fmt(wrong_rate)

        stem_text = (
            f"{name} solved the following problem:\n\n"
            f"\"{name} ran {b} miles in {a} hours. What is {name}'s speed?\"\n\n"
            f"{name}'s work: speed = {a}/{b} = {wrong_str} miles per hour.\n\n"
            f"Identify and explain the error the student made in solving the problem. Provide the correct solution."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.NR,
                               Difficulty.DIFFICULT, 6, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_str, answer_latex=correct_str,
            worked_solution=(
                f"{name} inverted the rate. Speed = distance / time = {b} / {a} = {correct_str} mph.\n"
                f"{name} calculated time / distance = {a} / {b} = {wrong_str}, which is incorrect."
            ),
            context_scenario="rate error analysis",
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
            self.stem4_at_ms,
            self.stem5_at_mp,
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
            4: self.stem4_at_ms,
            5: self.stem5_at_mp,
            6: self.stem6_above_nr,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-6.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 6.RP.2 question variants...")
    gen = Stem6RP2(seed=42)
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
