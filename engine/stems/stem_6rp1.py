"""
Stem generator for 6.RP.1:
  Convert between any two representations (fractions, decimals, percents)
  of positive rational numbers without the use of a calculator.

Content Limits:
  - Positive rational numbers
  - May include terminating or repeating decimals
  - Models may include tenths and hundredths grids or area models
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: terminating decimals; fractions with denom 10/100; percents multiples of 10
  Medium: 1-digit repeating decimals; denom 2,4,5; percents 10%-99%
  Difficult: multi-digit repeating (1/11, 1/7); values <10% or >100%

6 Stems from the Item Spec:
  Stem 1 (Below-MC):  Given a model of a percent, choose the equivalent decimal (DOK 1, easy)
  Stem 2 (Below-MC):  Given a decimal with model, choose the equivalent fraction (DOK 1, medium)
  Stem 3 (Approaching-MC): Choose the fraction equivalent to a given percent (DOK 1, easy)
  Stem 4 (Approaching-NR): Write a decimal as a percent (DOK 1, medium)
  Stem 5 (At-MS):     Select TWO values equivalent to a given percent (DOK 2, medium)
  Stem 6 (Above-NR):  Convert a multi-digit repeating decimal fraction to decimal (DOK 2, difficult)
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
from engine.context_pools import pick_name


STANDARD_CODE = "6.RP.1"
VARIANTS_PER_STEM = 20


# ============================================================
# HELPERS
# ============================================================

# Known fraction -> repeating decimal mappings
REPEATING_DECIMALS = {
    Fraction(1, 3): "0.333...",
    Fraction(2, 3): "0.666...",
    Fraction(1, 6): "0.1666...",
    Fraction(5, 6): "0.8333...",
    Fraction(1, 9): "0.111...",
    Fraction(2, 9): "0.222...",
    Fraction(4, 9): "0.444...",
    Fraction(5, 9): "0.555...",
    Fraction(7, 9): "0.777...",
    Fraction(8, 9): "0.888...",
    Fraction(1, 11): "0.0909...",
    Fraction(2, 11): "0.1818...",
    Fraction(3, 11): "0.2727...",
    Fraction(1, 7): "0.142857...",
    Fraction(2, 7): "0.285714...",
    Fraction(3, 7): "0.428571...",
    Fraction(7, 12): "0.5833...",
    Fraction(11, 12): "0.9166...",
}


def frac_to_decimal_str(frac):
    """Convert fraction to decimal string, handling repeating decimals."""
    if frac in REPEATING_DECIMALS:
        return REPEATING_DECIMALS[frac]
    f = float(frac)
    if f == int(f):
        return str(int(f))
    # Terminating decimal
    s = f"{f:.6f}".rstrip('0').rstrip('.')
    return s


def frac_to_percent_str(frac):
    """Convert fraction to percent string."""
    pct = float(frac) * 100
    if pct == int(pct):
        return f"{int(pct)}%"
    s = f"{pct:.4f}".rstrip('0').rstrip('.')
    return f"{s}%"


def frac_to_fraction_str(frac):
    """Display fraction as a/b or whole number."""
    if frac.denominator == 1:
        return str(int(frac))
    return f"{frac.numerator}/{frac.denominator}"


# Easy fractions: terminating decimals with denom 10, 100, or simple like 1/4, 1/2, 3/4
EASY_FRACS = [
    Fraction(1, 10), Fraction(2, 10), Fraction(3, 10), Fraction(4, 10),
    Fraction(6, 10), Fraction(7, 10), Fraction(8, 10), Fraction(9, 10),
    Fraction(1, 4), Fraction(3, 4), Fraction(1, 5), Fraction(2, 5),
    Fraction(3, 5), Fraction(4, 5), Fraction(1, 2),
    Fraction(1, 20), Fraction(3, 20), Fraction(7, 20), Fraction(9, 20),
    Fraction(1, 25), Fraction(3, 25), Fraction(7, 25),
    Fraction(1, 50), Fraction(3, 50), Fraction(7, 50),
]

# Medium fractions: 1-digit repeating or denom 2, 4, 5, 8
MEDIUM_FRACS = [
    Fraction(1, 3), Fraction(2, 3),
    Fraction(1, 8), Fraction(3, 8), Fraction(5, 8), Fraction(7, 8),
    Fraction(1, 6), Fraction(5, 6),
    Fraction(1, 9), Fraction(2, 9), Fraction(4, 9),
]

# Difficult fractions: multi-digit repeating, values >100% or <10%
DIFFICULT_FRACS = [
    Fraction(1, 11), Fraction(2, 11), Fraction(3, 11),
    Fraction(1, 7), Fraction(2, 7), Fraction(3, 7),
    Fraction(7, 12), Fraction(11, 12),
]


class Stem6RP1:
    """Generates ~20 variants for each of 6 stems from the 6.RP.1 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 1, Easy)
    # Given a percent, choose the equivalent decimal
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        frac = rng.choice(EASY_FRACS)
        pct_str = frac_to_percent_str(frac)
        dec_str = frac_to_decimal_str(frac)
        dec_val = float(frac)

        # Distractors: common errors
        distractors = set()
        # Move decimal wrong way (percent as decimal, e.g., 30% -> 30.0)
        distractors.add(f"{float(frac) * 1000:.6f}".rstrip('0').rstrip('.'))
        # Off by factor of 10
        distractors.add(f"{dec_val * 10:.6f}".rstrip('0').rstrip('.'))
        # Reversed digits
        distractors.add(f"{dec_val / 10:.6f}".rstrip('0').rstrip('.'))
        distractors.discard(dec_str)
        distractors = [d for d in distractors if d != dec_str and float(d) > 0]
        while len(distractors) < 3:
            offset = rng.choice([0.01, 0.05, 0.1, -0.01, -0.05])
            d = dec_val + offset
            if d > 0:
                ds = f"{d:.6f}".rstrip('0').rstrip('.')
                if ds != dec_str and ds not in distractors:
                    distractors.append(ds)
        distractors = distractors[:3]

        all_options = [(dec_str, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        shaded_count = int(float(frac) * 100)
        grid_render = {
            "type": "shaded_grid",
            "grid_type": "hundredths",
            "shaded": shaded_count,
            "total": 100,
        }

        stem_text = f"The model below represents {pct_str}. Which decimal is equivalent?"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=f"{pct_str} = {pct_str.replace('%', '')} / 100 = {dec_str}",
            choices=choices, context_scenario="percent to decimal",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx,
            render_data=grid_render,
        )

    # ================================================================
    # STEM 2: Below Proficiency - MC (DOK 1, Medium)
    # Given a fraction, choose the equivalent decimal
    # ================================================================

    def stem2_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        frac = rng.choice(MEDIUM_FRACS)
        frac_str = frac_to_fraction_str(frac)
        dec_str = frac_to_decimal_str(frac)
        dec_val = float(frac)

        # Distractors
        distractors = set()
        # Inverted fraction
        inv = Fraction(frac.denominator, frac.numerator)
        distractors.add(frac_to_decimal_str(inv) if float(inv) < 10 else f"{float(inv):.2f}")
        # Multiply instead of divide
        distractors.add(f"{frac.numerator * frac.denominator}")
        # Nearby values
        distractors.add(f"{dec_val + 0.1:.4f}".rstrip('0').rstrip('.'))
        distractors.discard(dec_str)
        distractors = [d for d in distractors if d != dec_str][:3]
        while len(distractors) < 3:
            offset = rng.choice([0.05, 0.15, -0.05, 0.25])
            d = abs(dec_val + offset)
            ds = f"{d:.4f}".rstrip('0').rstrip('.')
            if ds != dec_str and ds not in distractors:
                distractors.append(ds)
        distractors = distractors[:3]

        all_options = [(dec_str, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        grid_render = {
            "type": "shaded_grid",
            "grid_type": "bar",
            "shaded": frac.numerator,
            "total": frac.denominator,
        }

        stem_text = f"The model below represents a fraction. Which decimal is equivalent to {frac_str}?"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.MEDIUM, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=f"{frac_str} = {frac.numerator} / {frac.denominator} = {dec_str}",
            choices=choices, context_scenario="fraction to decimal",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx,
            render_data=grid_render,
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - MC (DOK 1, Easy)
    # Choose the fraction equivalent to a given percent
    # ================================================================

    def stem3_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        frac = rng.choice(EASY_FRACS)
        pct_str = frac_to_percent_str(frac)
        frac_str = frac_to_fraction_str(frac)

        # Distractors: common fraction errors
        distractors = set()
        # Percent over 10 instead of 100
        pct_val = float(frac) * 100
        if pct_val == int(pct_val):
            wrong_frac = Fraction(int(pct_val), 10)
            distractors.add(frac_to_fraction_str(wrong_frac))
        # Inverted
        distractors.add(f"{frac.denominator}/{frac.numerator}" if frac.numerator != 0 else "1/1")
        # Non-simplified version or nearby
        distractors.add(frac_to_fraction_str(Fraction(frac.numerator + 1, frac.denominator)))
        distractors.discard(frac_str)
        distractors = [d for d in distractors if d != frac_str][:3]
        while len(distractors) < 3:
            n = rng.randint(1, 9)
            d = rng.choice([5, 8, 10, 20])
            ds = frac_to_fraction_str(Fraction(n, d))
            if ds != frac_str and ds not in distractors:
                distractors.append(ds)
        distractors = distractors[:3]

        all_options = [(frac_str, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = f"Which fraction is equivalent to {pct_str}?"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.EASY, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=f"{pct_str} = {pct_str.replace('%', '')}/100 = {frac_str}",
            choices=choices, context_scenario="percent to fraction",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: Approaching Proficiency - NR (DOK 1, Medium)
    # Write a decimal as a percent
    # ================================================================

    def stem4_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        frac = rng.choice(MEDIUM_FRACS + EASY_FRACS)
        dec_str = frac_to_decimal_str(frac)
        pct_str = frac_to_percent_str(frac)

        stem_text = f"What is {dec_str} written as a percent?"

        pct_val = float(frac) * 100
        worked = f"{dec_str} x 100 = {pct_str}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=pct_str, answer_latex=pct_str,
            worked_solution=worked,
            context_scenario="decimal to percent",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: At Proficiency - MS (DOK 2, Medium)
    # Select TWO values equivalent to a given percent
    # ================================================================

    def stem5_at_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        frac = rng.choice(MEDIUM_FRACS)
        pct_str = frac_to_percent_str(frac)
        dec_str = frac_to_decimal_str(frac)
        frac_str = frac_to_fraction_str(frac)

        # Two correct options: the decimal and the fraction
        correct_options = [dec_str, frac_str]

        # Three wrong options
        wrong = set()
        # Wrong decimal (off by factor of 10)
        wrong.add(f"{float(frac) * 10:.4f}".rstrip('0').rstrip('.'))
        # Wrong fraction (inverted)
        wrong.add(f"{frac.denominator}/{frac.numerator}")
        # Wrong percent form as decimal
        wrong.add(f"{float(frac) * 1000:.4f}".rstrip('0').rstrip('.'))
        # Wrong nearby fraction
        wrong.add(frac_to_fraction_str(Fraction(frac.numerator + 1, frac.denominator + 1)))
        wrong -= set(correct_options)
        wrong_list = [w for w in wrong if w not in correct_options][:3]
        while len(wrong_list) < 3:
            n = rng.randint(1, 9)
            d = rng.choice([3, 5, 7, 11])
            ws = frac_to_fraction_str(Fraction(n, d))
            if ws not in correct_options and ws not in wrong_list:
                wrong_list.append(ws)
        wrong_list = wrong_list[:3]

        all_options = [(o, True) for o in correct_options] + [(o, False) for o in wrong_list]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letters = ", ".join(c.key for c in choices if c.is_correct)

        stem_text = f"Select the two values that are equivalent to {pct_str}."

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MS,
                               Difficulty.MEDIUM, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MS,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letters, answer_latex=correct_letters,
            worked_solution=f"{pct_str} = {dec_str} (decimal) = {frac_str} (fraction)",
            choices=choices, context_scenario="percent equivalence multi-select",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    # STEM 6: Above Proficiency - NR (DOK 2, Difficult)
    # Convert a difficult fraction to its decimal equivalent
    # ================================================================

    def stem6_above_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)

        frac = rng.choice(DIFFICULT_FRACS)
        frac_str = frac_to_fraction_str(frac)
        dec_str = frac_to_decimal_str(frac)
        pct_str = frac_to_percent_str(frac)

        stem_text = (
            f"What is the decimal equivalent of {frac_str}?\n\n"
            f"If the decimal repeats, write the first 4 decimal places followed by \"...\""
        )

        worked = (
            f"{frac_str} = {frac.numerator} / {frac.denominator} = {dec_str}\n"
            f"As a percent: {pct_str}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.NR,
                               Difficulty.DIFFICULT, 6, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=dec_str, answer_latex=dec_str,
            worked_solution=worked,
            context_scenario="fraction to repeating decimal",
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
            self.stem2_below_mc,
            self.stem3_approaching_mc,
            self.stem4_approaching_nr,
            self.stem5_at_ms,
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
            3: self.stem3_approaching_mc,
            4: self.stem4_approaching_nr,
            5: self.stem5_at_ms,
            6: self.stem6_above_nr,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-6.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 6.RP.1 question variants...")
    gen = Stem6RP1(seed=42)
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
