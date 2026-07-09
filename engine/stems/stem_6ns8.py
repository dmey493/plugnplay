"""
Stem generator for 6.NS.8:
  Evaluate positive rational numbers with whole number exponents.

Content Limits:
  - Positive rational bases
  - Whole number exponents
  - No multi-term expressions
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: whole number base
  Medium: fraction base
  Difficult: decimal base

5 Stems from the Item Spec:
  Stem 1 (Below-MC, DOK 1, easy): Identify relationship between base and exponent
         (e.g., 5^3 = 5 x 5 x 5)
  Stem 2 (Below-NR, DOK 1, easy): Evaluate whole number base (e.g., 8^5 = 32768)
  Stem 3 (Approaching-MC, DOK 1, difficult): Select expression equivalent to
         a decimal power (e.g., 2.3^6)
  Stem 4 (At-NR, DOK 1, medium): Evaluate fraction base (e.g., (2/3)^3 = 8/27)
  Stem 5 (Above-MC, DOK 2, medium): Analyze error in evaluating fraction exponent
         (student multiplied base x exp instead of base^exp)
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


STANDARD_CODE = "6.NS.8"
VARIANTS_PER_STEM = 20


def _expanded_form(base_str, exp):
    """Return 'base x base x base' for a given exponent."""
    return " x ".join([base_str] * exp)


def _frac_display(frac):
    """Display a fraction as a/b or whole number."""
    if frac.denominator == 1:
        return str(int(frac))
    return f"{frac.numerator}/{frac.denominator}"


def _frac_latex(frac):
    """LaTeX display for a fraction."""
    if frac.denominator == 1:
        return str(int(frac))
    return f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"


class Stem6NS8:
    """Generates ~20 variants for each of 5 stems from the 6.NS.8 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 1, Easy)
    # Identify relationship: e.g., 5^3 = 5 x 5 x 5
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        base, exp, result = gen.exponent_pair("easy")
        base_int = int(base)

        stem_text = (
            f"Which expression is equivalent to {base_int}^{exp}?"
        )
        stem_latex = (
            f"Which expression is equivalent to ${base_int}^{{{exp}}}$?"
        )

        # Correct: base x base x base (exp times)
        correct = _expanded_form(str(base_int), exp)

        # Distractors
        distractors = set()
        # base * exp (common error: multiply instead of repeat)
        distractors.add(f"{base_int} x {exp}")
        # Wrong number of repetitions
        if exp > 2:
            distractors.add(_expanded_form(str(base_int), exp - 1))
        distractors.add(_expanded_form(str(base_int), exp + 1))
        # exp x exp x ... (swapped base and exponent)
        distractors.add(_expanded_form(str(exp), base_int) if base_int <= 5 else f"{exp} x {exp} x {exp}")
        distractors.discard(correct)
        distractors = [d for d in distractors if d != correct][:3]
        while len(distractors) < 3:
            wrong_exp = exp + rng.choice([-2, 2, 3])
            if wrong_exp >= 2:
                d = _expanded_form(str(base_int), wrong_exp)
                if d != correct and d not in distractors:
                    distractors.append(d)
                    continue
            d = f"{base_int} + {exp}"
            if d != correct and d not in distractors:
                distractors.append(d)
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
            stem_latex=stem_latex,
            answer_text=correct_letter,
            answer_latex=correct_letter,
            worked_solution=(
                f"{base_int}^{exp} means {base_int} multiplied by itself {exp} times.\n"
                f"{base_int}^{exp} = {correct}"
            ),
            choices=choices,
            context_scenario="exponent expanded form",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Below Proficiency - NR (DOK 1, Easy)
    # Evaluate whole number base: e.g., 8^5 = 32768
    # ================================================================

    def stem2_below_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        base, exp, result = gen.exponent_pair("easy")
        base_int = int(base)
        result_int = int(result)

        stem_text = f"What is the value of {base_int}^{exp}? Show your work or explain your reasoning."
        stem_latex = f"What is the value of ${base_int}^{{{exp}}}$? Show your work or explain your reasoning."

        answer_text = str(result_int)

        # Build step-by-step worked solution
        steps = []
        running = 1
        for i in range(exp):
            running *= base_int
            if i == 0:
                steps.append(f"{base_int}")
            else:
                factors = " x ".join([str(base_int)] * (i + 1))
                steps.append(f"{factors} = {running}")

        worked = (
            f"{base_int}^{exp} = {_expanded_form(str(base_int), exp)}\n"
            f"= {result_int}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.NR,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY,
            dok=1,
            item_type=ItemType.NR,
            stem_text=stem_text,
            stem_latex=stem_latex,
            answer_text=answer_text,
            answer_latex=f"${answer_text}$",
            worked_solution=worked,
            context_scenario="evaluate whole number exponent",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - MC (DOK 1, Difficult)
    # Select expression equivalent to a decimal power: e.g., 2.3^6
    # ================================================================

    def stem3_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        base, exp, result = gen.exponent_pair("difficult")
        base_dec = float(base)
        base_str = f"{base_dec:g}"

        stem_text = (
            f"Which expression is equivalent to {base_str}^{exp}?"
        )
        stem_latex = (
            f"Which expression is equivalent to ${base_str}^{{{exp}}}$?"
        )

        # Correct: base x base x base (exp times)
        correct = _expanded_form(base_str, exp)

        # Distractors
        distractors = set()
        # base * exp (common error)
        product = base_dec * exp
        distractors.add(f"{base_str} x {exp}")
        # Wrong repetitions
        if exp > 2:
            distractors.add(_expanded_form(base_str, exp - 1))
        distractors.add(_expanded_form(base_str, exp + 1))
        # base + base + ... (added instead of multiplied)
        add_form = " + ".join([base_str] * exp)
        distractors.add(add_form)
        distractors.discard(correct)
        distractors = [d for d in distractors if d != correct][:3]
        while len(distractors) < 3:
            d = f"{base_str} x {base_str} + {exp}"
            if d != correct and d not in distractors:
                distractors.append(d)
                continue
            d = f"{exp} x {base_str}"
            if d != correct and d not in distractors:
                distractors.append(d)
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

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.DIFFICULT, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.DIFFICULT,
            dok=1,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_latex,
            answer_text=correct_letter,
            answer_latex=correct_letter,
            worked_solution=(
                f"{base_str}^{exp} means {base_str} multiplied by itself {exp} times.\n"
                f"{base_str}^{exp} = {correct}"
            ),
            choices=choices,
            context_scenario="decimal exponent expanded form",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At Proficiency - NR (DOK 1, Medium)
    # Evaluate fraction base: e.g., (2/3)^3 = 8/27
    # ================================================================

    def stem4_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        base, exp, result = gen.exponent_pair("medium")

        base_str = _frac_display(base)
        base_latex = _frac_latex(base)
        result_str = _frac_display(result)
        result_latex = _frac_latex(result)

        stem_text = f"Evaluate ({base_str})^{exp}."
        stem_latex_text = f"Evaluate $\\left({base_latex}\\right)^{{{exp}}}$."

        answer_text = result_str

        # Worked solution showing numerator and denominator raised separately
        num = base.numerator
        den = base.denominator
        num_result = num ** exp
        den_result = den ** exp

        worked = (
            f"({base_str})^{exp}\n"
            f"= {num}^{exp} / {den}^{exp}\n"
            f"= {num_result} / {den_result}\n"
            f"= {result_str}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM,
            dok=1,
            item_type=ItemType.NR,
            stem_text=stem_text,
            stem_latex=stem_latex_text,
            answer_text=answer_text,
            answer_latex=f"${result_latex}$",
            worked_solution=worked,
            context_scenario="evaluate fraction exponent",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above Proficiency - MC (DOK 2, Medium)
    # Analyze error: student multiplied base x exp instead of base^exp
    # ================================================================

    def stem5_above_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        base, exp, result = gen.exponent_pair("medium")

        base_str = _frac_display(base)
        base_latex = _frac_latex(base)
        result_str = _frac_display(result)

        # The student's wrong answer: base * exp instead of base^exp
        wrong_answer = base * exp
        wrong_str = _frac_display(wrong_answer)

        name = pick_name(rng)

        stem_text = (
            f"{name} evaluated ({base_str})^{exp} and got {wrong_str}.\n\n"
            f"What mistake did {name} most likely make?"
        )
        stem_latex_text = (
            f"{name} evaluated $\\left({base_latex}\\right)^{{{exp}}}$ and got ${_frac_latex(wrong_answer)}$.\n\n"
            f"What mistake did {name} most likely make?"
        )

        # Correct explanation
        correct = (
            f"{name} multiplied {base_str} by {exp} instead of "
            f"multiplying {base_str} by itself {exp} times."
        )

        # Distractors: other plausible explanations
        distractors = []
        distractors.append(
            f"{name} added {base_str} and {exp} instead of multiplying."
        )
        distractors.append(
            f"{name} raised only the numerator to the power of {exp} "
            f"and forgot to raise the denominator."
        )
        distractors.append(
            f"{name} divided {base_str} by {exp} instead of "
            f"multiplying {base_str} by itself {exp} times."
        )

        all_options = [(correct, True)] + [(d, False) for d in distractors[:3]]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"{name} got {wrong_str} because {base_str} x {exp} = {wrong_str}.\n"
            f"The correct computation is ({base_str})^{exp} = "
            f"{_expanded_form(base_str, exp)} = {result_str}.\n"
            f"{name} multiplied the base by the exponent instead of "
            f"using the base as a factor {exp} times."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MC,
                               Difficulty.MEDIUM, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.MEDIUM,
            dok=2,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_latex_text,
            answer_text=correct_letter,
            answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices,
            context_scenario="error analysis for exponents",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5,
            variant_index=variant_idx
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
            self.stem4_at_nr,
            self.stem5_above_mc,
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
            4: self.stem4_at_nr,
            5: self.stem5_above_mc,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-5.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 6.NS.8 question variants...")
    gen = Stem6NS8(seed=42)
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
