"""
Stem generator for 6.NS.6:
  Find the greatest common factor (GCF) of two whole numbers less than or equal
  to 100 and the least common multiple (LCM) of two whole numbers less than or
  equal to 12. Use the distributive property to express a sum of two whole numbers
  1-100 with a common factor as a multiple of a sum of two whole numbers with no
  common factor.

Content Limits:
  - GCF: two whole numbers <= 100
  - LCM: two whole numbers <= 12
  - Distributive property: sum of two whole numbers 1-100 with a common factor
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: LCM pairs from {2,5,10,11}; GCF pairs <= 25
  Medium: LCM pairs from {3,4,6,9}; GCF pairs <= 50
  Difficult: LCM pairs from {7,8,12}; GCF pairs <= 100

6 Stems from the Item Spec:
  Stem 1 (Below-MC, DOK 1, easy): Find GCF from a list of factors
  Stem 2 (Below-MC, DOK 1, medium): Find LCM from a list of multiples
  Stem 3 (Approaching-NR, DOK 1, medium): Find GCF of two numbers
  Stem 4 (Approaching-NR, DOK 2, medium): Distributive property equivalent expression
  Stem 5 (At-NR, DOK 1, difficult): Find LCM of two numbers (includes 7, 8, or 12)
  Stem 6 (Above-NR, DOK 2, easy): Solve real-world GCF or LCM problem
"""

import random
from fractions import Fraction
from math import gcd

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


STANDARD_CODE = "6.NS.6"
VARIANTS_PER_STEM = 20


# ============================================================
# REAL-WORLD CONTEXTS FOR GCF/LCM WORD PROBLEMS (Stem 6)
# ============================================================

LCM_CONTEXTS = [
    {
        "template": "{name1} goes to the beach every {a} days. {name2} goes to the beach every {b} days. They both went to the beach today. In how many days will they both go to the beach on the same day again?",
        "answer_template": "The LCM of {a} and {b} is {lcm}. They will both go to the beach again in {lcm} days.",
        "unit": "days",
    },
    {
        "template": "{name1} waters plants every {a} days. {name2} waters plants every {b} days. Both watered their plants today. In how many days will they both water their plants on the same day again?",
        "answer_template": "The LCM of {a} and {b} is {lcm}. They will both water plants again in {lcm} days.",
        "unit": "days",
    },
    {
        "template": "Bus A arrives at a stop every {a} minutes. Bus B arrives every {b} minutes. Both buses just arrived. In how many minutes will both buses arrive at the stop at the same time again?",
        "answer_template": "The LCM of {a} and {b} is {lcm}. Both buses will arrive together again in {lcm} minutes.",
        "unit": "minutes",
    },
    {
        "template": "{name1} gets a haircut every {a} weeks. {name2} gets a haircut every {b} weeks. They both got haircuts this week. In how many weeks will they both get haircuts in the same week again?",
        "answer_template": "The LCM of {a} and {b} is {lcm}. They will both get haircuts again in {lcm} weeks.",
        "unit": "weeks",
    },
    {
        "template": "Two lighthouses flash their lights at different intervals. One flashes every {a} seconds and the other flashes every {b} seconds. They just flashed at the same time. In how many seconds will they flash at the same time again?",
        "answer_template": "The LCM of {a} and {b} is {lcm}. They will flash together again in {lcm} seconds.",
        "unit": "seconds",
    },
]

GCF_CONTEXTS = [
    {
        "template": "{name1} has {a} red balloons and {b} blue balloons for a party. {name1} wants to make identical groups with no balloons left over. What is the greatest number of groups {name1} can make?",
        "answer_template": "The GCF of {a} and {b} is {gcf}. {name1} can make {gcf} groups.",
        "unit": "groups",
    },
    {
        "template": "A florist has {a} roses and {b} daisies. The florist wants to make identical bouquets using all of the flowers with none left over. What is the greatest number of bouquets the florist can make?",
        "answer_template": "The GCF of {a} and {b} is {gcf}. The florist can make {gcf} bouquets.",
        "unit": "bouquets",
    },
    {
        "template": "{name1} is making snack bags for a field trip. {name1} has {a} granola bars and {b} fruit snacks. Each bag must have the same number of each item with none left over. What is the greatest number of bags {name1} can make?",
        "answer_template": "The GCF of {a} and {b} is {gcf}. {name1} can make {gcf} bags.",
        "unit": "bags",
    },
    {
        "template": "A carpenter has a board that is {a} inches long and another that is {b} inches long. The carpenter wants to cut them into equal-length pieces with no waste. What is the longest possible length of each piece?",
        "answer_template": "The GCF of {a} and {b} is {gcf}. Each piece can be {gcf} inches long.",
        "unit": "inches",
    },
]


class Stem6NS6:
    """Generates ~20 variants for each of 6 stems from the 6.NS.6 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 1, Easy)
    # Find the GCF of two numbers from a list of factors
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        a, b, gcf_val = gen.gcf_pair("easy")

        # List the factors of both numbers
        factors_a = sorted([i for i in range(1, a + 1) if a % i == 0])
        factors_b = sorted([i for i in range(1, b + 1) if b % i == 0])
        common_factors = sorted(set(factors_a) & set(factors_b))

        stem_text = (
            f"The factors of {a} are: {', '.join(str(f) for f in factors_a)}\n"
            f"The factors of {b} are: {', '.join(str(f) for f in factors_b)}\n\n"
            f"What is the greatest common factor (GCF) of {a} and {b}?"
        )

        correct = str(gcf_val)

        # Distractors: other common factors and nearby values
        distractors = set()
        for cf in common_factors:
            if cf != gcf_val:
                distractors.add(str(cf))
        # LCM as common error
        lcm_val = (a * b) // gcd(a, b)
        distractors.add(str(lcm_val))
        # Product as common error
        distractors.add(str(a * b))
        distractors.discard(correct)
        distractors = [d for d in distractors if d != correct][:3]
        while len(distractors) < 3:
            d = gcf_val + rng.choice([-2, -1, 1, 2, 3])
            if d > 0 and str(d) != correct and str(d) not in distractors:
                distractors.append(str(d))
        distractors = distractors[:3]

        all_options = [(correct, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY,
            dok=1,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=correct_letter,
            answer_latex=correct_letter,
            worked_solution=(
                f"Common factors of {a} and {b}: {', '.join(str(f) for f in common_factors)}\n"
                f"The greatest common factor is {gcf_val}."
            ),
            choices=choices,
            context_scenario="GCF from factor lists",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1,
            variant_index=variant_idx,
            render_data={
                "type": "data_table",
                "headers": [str(a), str(b)],
                "rows": [
                    [", ".join(str(f) for f in factors_a),
                     ", ".join(str(f) for f in factors_b)],
                ],
                "title": "Factors",
            }
        )

    # ================================================================
    # STEM 2: Below Proficiency - MC (DOK 1, Medium)
    # Find the LCM of two numbers from a list of multiples
    # ================================================================

    def stem2_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        a, b, lcm_val = gen.lcm_pair("medium")

        # List first several multiples of each number
        num_multiples = max(8, lcm_val // min(a, b) + 3)
        multiples_a = [a * i for i in range(1, num_multiples + 1)]
        multiples_b = [b * i for i in range(1, num_multiples + 1)]

        stem_text = (
            f"The first several multiples of {a} are: {', '.join(str(m) for m in multiples_a[:8])}, ...\n"
            f"The first several multiples of {b} are: {', '.join(str(m) for m in multiples_b[:8])}, ...\n\n"
            f"What is the least common multiple (LCM) of {a} and {b}?"
        )

        correct = str(lcm_val)

        # Distractors: product, GCF, and other common multiples
        distractors = set()
        distractors.add(str(a * b))  # product (common error)
        gcf_ab = gcd(a, b)
        distractors.add(str(gcf_ab))  # GCF (confuses GCF/LCM)
        # A common multiple that isn't the least
        if lcm_val * 2 != a * b:
            distractors.add(str(lcm_val * 2))
        distractors.discard(correct)
        distractors = [d for d in distractors if d != correct][:3]
        while len(distractors) < 3:
            d = lcm_val + rng.choice([-3, -2, -1, 1, 2, 3])
            if d > 0 and str(d) != correct and str(d) not in distractors:
                distractors.append(str(d))
        distractors = distractors[:3]

        all_options = [(correct, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.MEDIUM, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.MEDIUM,
            dok=1,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=correct_letter,
            answer_latex=correct_letter,
            worked_solution=(
                f"List multiples of {a} and {b} until a common one appears.\n"
                f"Multiples of {a}: {', '.join(str(m) for m in multiples_a[:6])}, ...\n"
                f"Multiples of {b}: {', '.join(str(m) for m in multiples_b[:6])}, ...\n"
                f"The least common multiple is {lcm_val}."
            ),
            choices=choices,
            context_scenario="LCM from multiple lists",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2,
            variant_index=variant_idx,
            render_data={
                "type": "data_table",
                "orientation": "horizontal",
                "headers": ["Multiples"],
                "rows": [
                    [str(a)] + [str(m) for m in multiples_a[:8]],
                    [str(b)] + [str(m) for m in multiples_b[:8]],
                ],
                "title": "Multiples",
            }
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - NR (DOK 1, Medium)
    # Find the GCF of two numbers directly
    # ================================================================

    def stem3_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        a, b, gcf_val = gen.gcf_pair("medium")

        stem_text = f"What is the greatest common factor (GCF) of {a} and {b}?"

        answer_text = str(gcf_val)

        # Build worked solution using factor lists
        factors_a = sorted([i for i in range(1, a + 1) if a % i == 0])
        factors_b = sorted([i for i in range(1, b + 1) if b % i == 0])
        common = sorted(set(factors_a) & set(factors_b))

        worked = (
            f"Factors of {a}: {', '.join(str(f) for f in factors_a)}\n"
            f"Factors of {b}: {', '.join(str(f) for f in factors_b)}\n"
            f"Common factors: {', '.join(str(f) for f in common)}\n"
            f"GCF = {gcf_val}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM,
            dok=1,
            item_type=ItemType.NR,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=answer_text,
            answer_latex=f"${answer_text}$",
            worked_solution=worked,
            context_scenario="GCF computation",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: Approaching Proficiency - NR (DOK 2, Medium)
    # Use distributive property: e.g., 8 + 20 = 4(2 + 5)
    # ================================================================

    def stem4_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        # Generate two numbers with a common factor
        a, b, gcf_val = gen.gcf_pair("medium")

        # The reduced terms
        reduced_a = a // gcf_val
        reduced_b = b // gcf_val

        # Present the sum and ask to rewrite using distributive property
        # Answer form: gcf(a + b) = gcf * (reduced_a + reduced_b)
        stem_text = (
            f"Use the distributive property to write an equivalent expression "
            f"for {a} + {b}.\n\n"
            f"Write your answer in the form: GCF(__ + __)\n\n"
            f"What is the GCF used in the equivalent expression?"
        )

        answer_text = str(gcf_val)

        worked = (
            f"{a} + {b}\n"
            f"GCF of {a} and {b} = {gcf_val}\n"
            f"{a} = {gcf_val} x {reduced_a}\n"
            f"{b} = {gcf_val} x {reduced_b}\n"
            f"{a} + {b} = {gcf_val}({reduced_a} + {reduced_b})\n"
            f"The GCF is {gcf_val}."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM,
            dok=2,
            item_type=ItemType.NR,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=answer_text,
            answer_latex=f"${answer_text}$",
            worked_solution=worked,
            context_scenario="distributive property with GCF",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: At Proficiency - NR (DOK 1, Difficult)
    # Find the LCM of two numbers (includes 7, 8, or 12)
    # ================================================================

    def stem5_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        a, b, lcm_val = gen.lcm_pair("difficult")

        stem_text = f"What is the least common multiple (LCM) of {a} and {b}?"

        answer_text = str(lcm_val)

        # List multiples
        num_mult = max(8, lcm_val // min(a, b) + 3)
        multiples_a = [a * i for i in range(1, num_mult + 1)]
        multiples_b = [b * i for i in range(1, num_mult + 1)]

        worked = (
            f"Multiples of {a}: {', '.join(str(m) for m in multiples_a[:8])}, ...\n"
            f"Multiples of {b}: {', '.join(str(m) for m in multiples_b[:8])}, ...\n"
            f"The first common multiple is {lcm_val}.\n"
            f"LCM = {lcm_val}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.DIFFICULT, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT,
            dok=1,
            item_type=ItemType.NR,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=answer_text,
            answer_latex=f"${answer_text}$",
            worked_solution=worked,
            context_scenario="LCM computation",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 6: Above Proficiency - NR (DOK 2, Easy)
    # Real-world GCF or LCM problem
    # ================================================================

    def stem6_above_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)

        name1 = pick_name(rng)
        name2 = pick_name(rng)
        while name2 == name1:
            name2 = pick_name(rng)

        # Alternate between LCM and GCF word problems
        if rng.random() < 0.5:
            # LCM problem
            a, b, lcm_val = gen.lcm_pair("easy")
            ctx = rng.choice(LCM_CONTEXTS)
            stem_text = ctx["template"].format(name1=name1, name2=name2, a=a, b=b)
            answer_text = str(lcm_val)
            worked = ctx["answer_template"].format(a=a, b=b, lcm=lcm_val)
            scenario = "real-world LCM"
        else:
            # GCF problem
            a, b, gcf_val = gen.gcf_pair("easy")
            ctx = rng.choice(GCF_CONTEXTS)
            stem_text = ctx["template"].format(name1=name1, name2=name2, a=a, b=b)
            answer_text = str(gcf_val)
            worked = ctx["answer_template"].format(
                a=a, b=b, gcf=gcf_val, name1=name1
            )
            scenario = "real-world GCF"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.NR,
                               Difficulty.EASY, 6, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.EASY,
            dok=2,
            item_type=ItemType.NR,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=answer_text,
            answer_latex=f"${answer_text}$",
            worked_solution=worked,
            context_scenario=scenario,
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6,
            variant_index=variant_idx
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_below_mc,
            self.stem3_approaching_nr,
            self.stem4_approaching_nr,
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
            2: self.stem2_below_mc,
            3: self.stem3_approaching_nr,
            4: self.stem4_approaching_nr,
            5: self.stem5_at_nr,
            6: self.stem6_above_nr,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-6.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 6.NS.6 question variants...")
    gen = Stem6NS6(seed=42)
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
