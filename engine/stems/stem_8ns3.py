"""
Stem generator for 8.NS.3:
  Given a numeric expression with common rational number bases and integer
  exponents, apply the properties of exponents to generate equivalent
  expressions.

Content Limits:
  - Integer exponents and rational number bases
  - Variables may represent a missing base or exponent
  - Expressions must have common rational number bases
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: simple fraction or stand-alone rational number
  Medium: expression uses one operation
  Difficult: expression uses more than one operation

Properties of Exponents:
  - Product of Powers: a^m * a^n = a^(m+n)
  - Quotient of Powers: a^m / a^n = a^(m-n)
  - Power of a Power: (a^m)^n = a^(m*n)
  - Negative Exponent: a^(-n) = 1/a^n
  - Zero Exponent: a^0 = 1

5 Stems from the Item Spec:
  Stem 1 (Below-MC, DOK 2, Easy): Identify expanded notation for a power expression
  Stem 2 (Approaching-MC, DOK 2, Easy): Apply one property to simplify (product of powers)
  Stem 3 (Approaching-NR, DOK 2, Medium): Simplify using quotient or power-of-power
  Stem 4 (At-MC, DOK 2, Medium): Apply multiple properties to simplify
  Stem 5 (Above-NR, DOK 2, Difficult): Find missing exponent in an equation
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


STANDARD_CODE = "8.NS.3"
VARIANTS_PER_STEM = 20


# ============================================================
# HELPERS
# ============================================================

def _exp(base, exp):
    """Format base^exp using caret notation for PDF renderer.

    The PDF renderer converts ^N to superscript automatically.
    """
    return f"{base}^{exp}"


def _exp_latex(base, exp):
    """LaTeX format for base^exp."""
    return f"{base}^{{{exp}}}"


class Stem8NS3:
    """Generates ~20 variants for each of 5 stems from the 8.NS.3 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 2, Easy)
    # Identify expanded notation for a power expression
    # e.g., (5^2)^5 = which expanded notation?
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        base = rng.randint(2, 7)
        inner_exp = rng.randint(2, 3)
        outer_exp = rng.randint(2, 4)
        result_exp = inner_exp * outer_exp

        # Expression: (base^inner)^outer
        inner_str = f"({_exp(base, inner_exp)})"
        expr_text = f"{inner_str}^{outer_exp}"
        expr_latex = f"$({base}^{{{inner_exp}}})^{{{outer_exp}}}$"

        # Correct: (base^inner) repeated outer times = base^(inner*outer)
        correct_expanded = " \u00D7 ".join([inner_str] * outer_exp)
        correct = f"{correct_expanded} = {_exp(base, result_exp)}"

        # Distractors
        distractors = []

        # Common error 1: wrong number of repetitions (inner instead of outer)
        d1_expanded = " \u00D7 ".join([inner_str] * inner_exp)
        distractors.append(f"{d1_expanded} = {_exp(base, inner_exp * inner_exp)}")

        # Common error 2: add exponents instead of multiply
        wrong2 = f"{inner_str} \u00D7 ({_exp(base, outer_exp)}) = {_exp(base, inner_exp + outer_exp)}"
        distractors.append(wrong2)

        # Common error 3: one extra repetition
        wrong3_count = outer_exp + 1
        wrong3_expanded = " \u00D7 ".join([inner_str] * wrong3_count)
        distractors.append(f"{wrong3_expanded} = {_exp(base, inner_exp * wrong3_count)}")

        # Ensure no duplicates with correct
        distractors = [d for d in distractors if d != correct][:3]
        while len(distractors) < 3:
            fallback_exp = result_exp + rng.choice([1, -1, 2])
            fb = f"{inner_str} \u00D7 {inner_str} = {_exp(base, fallback_exp)}"
            if fb != correct and fb not in distractors:
                distractors.append(fb)

        all_options = [(correct, True)] + [(d, False) for d in distractors[:3]]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = (
            f"An expression is given.\n\n"
            f"  {expr_text}\n\n"
            f"Select the equivalent expanded notation."
        )
        stem_latex = (
            f"An expression is given.\n\n"
            f"  {expr_latex}\n\n"
            f"Select the equivalent expanded notation."
        )

        worked = (
            f"{expr_text} means {inner_str} multiplied by itself "
            f"{outer_exp} times.\n"
            f"Using the power of a power rule: {expr_text} "
            f"= {_exp(base, result_exp)}.\n"
            f"Expanded: {correct}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_latex,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="expanded notation for power of power",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - MC (DOK 2, Easy)
    # Apply product of powers to simplify: a^m * a^n = a^(m+n)
    # ================================================================

    def stem2_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        base, exp1, exp2, op, result_exp = gen.exponent_simplify("easy")
        # op is always "multiply" for easy

        expr_text = f"{_exp(base, exp1)} \u00D7 {_exp(base, exp2)}"
        expr_latex = f"${base}^{{{exp1}}} \\cdot {base}^{{{exp2}}}$"

        correct = _exp(base, result_exp)

        # Distractors
        distractors = set()
        # Common error: multiply exponents
        distractors.add(_exp(base, exp1 * exp2))
        # Common error: multiply base too
        distractors.add(_exp(base * base, exp1 + exp2))
        # Common error: subtract exponents
        distractors.add(_exp(base, abs(exp1 - exp2)))
        # Common error: just the larger exponent
        distractors.add(_exp(base, max(exp1, exp2)))

        distractors.discard(correct)
        dist_list = [d for d in distractors if d != correct][:3]
        while len(dist_list) < 3:
            wrong = _exp(base, result_exp + rng.choice([1, -1, 2]))
            if wrong != correct and wrong not in dist_list:
                dist_list.append(wrong)

        all_options = [(correct, True)] + [(d, False) for d in dist_list[:3]]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = (
            f"An expression is given.\n\n"
            f"  {expr_text}\n\n"
            f"Select an equivalent expression."
        )

        worked = (
            f"Using the product of powers rule: a^m \u00D7 a^n = a^(m+n).\n"
            f"{expr_text} = {_exp(base, result_exp)}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="product of powers simplification",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - NR (DOK 2, Medium)
    # Simplify using quotient of powers or power of a power
    # Answer in the form x^y
    # ================================================================

    def stem3_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        base, exp1, exp2, op, result_exp = gen.exponent_simplify("medium")

        if op == "multiply":
            expr_text = f"{_exp(base, exp1)} \u00D7 {_exp(base, exp2)}"
            rule_name = "product of powers"
        else:  # divide
            expr_text = f"{_exp(base, exp1)} \u00F7 {_exp(base, exp2)}"
            rule_name = "quotient of powers"

        correct = _exp(base, result_exp)
        answer_text = correct

        stem_text = (
            f"An expression is given.\n\n"
            f"  {expr_text}\n\n"
            f"Simplify the expression. Write your answer as a "
            f"single base with an exponent."
        )

        worked = (
            f"Using the {rule_name} rule:\n"
            f"{expr_text} = {correct}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_text, answer_latex=f"${correct}$",
            worked_solution=worked,
            context_scenario="simplify using exponent rules",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At Proficiency - MC (DOK 2, Medium)
    # Apply more than one property: e.g., 5^4 * (5^-3)^2
    # ================================================================

    def stem4_at_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        base = rng.randint(2, 7)

        # Generate expression: base^a * (base^b)^c
        a = rng.randint(2, 5)
        b = rng.randint(-3, 3)
        while b == 0:
            b = rng.randint(-3, 3)
        c = rng.randint(2, 3)

        # Step 1: power of a power -> (base^b)^c = base^(b*c)
        inner_result = b * c
        # Step 2: product of powers -> base^a * base^(b*c) = base^(a + b*c)
        final_exp = a + inner_result

        # Display: base^a × (base^b)^c
        expr_text = f"{_exp(base, a)} \u00D7 ({_exp(base, b)})^{c}"

        correct = _exp(base, final_exp)

        # Distractors
        distractors = set()
        # Error: add all exponents
        distractors.add(_exp(base, a + b + c))
        # Error: multiply all exponents
        distractors.add(_exp(base, a * b * c))
        # Error: only do power of power, forget to add a
        distractors.add(_exp(base, inner_result))
        # Error: add a and b, then multiply by c
        distractors.add(_exp(base, (a + b) * c))
        # Error: forget negative sign
        if b < 0:
            distractors.add(_exp(base, a + abs(b) * c))

        distractors.discard(correct)
        dist_list = [d for d in distractors if d != correct][:3]
        while len(dist_list) < 3:
            wrong_exp = final_exp + rng.choice([1, -1, 2, -2])
            wrong = _exp(base, wrong_exp)
            if wrong != correct and wrong not in dist_list:
                dist_list.append(wrong)

        all_options = [(correct, True)] + [(d, False) for d in dist_list[:3]]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = (
            f"An expression is given.\n\n"
            f"  {expr_text}\n\n"
            f"Select an equivalent expression."
        )

        worked = (
            f"Step 1: Apply power of a power rule to ({_exp(base, b)})^{c}:\n"
            f"  ({_exp(base, b)})^{c} = {_exp(base, inner_result)}\n\n"
            f"Step 2: Apply product of powers rule:\n"
            f"  {_exp(base, a)} \u00D7 {_exp(base, inner_result)} = "
            f"{_exp(base, final_exp)}\n\n"
            f"Answer: {correct}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MC,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="multiple exponent properties",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above Proficiency - NR (DOK 2, Difficult)
    # Find missing exponent: base^a * base^b = base^c, find a (or b)
    # May involve negative exponents
    # ================================================================

    def stem5_above_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        base = rng.randint(2, 7)

        # Choose equation type
        eq_type = rng.choice(["product", "quotient", "power_of_power"])

        if eq_type == "product":
            # base^a * base^b = base^c, find a
            b = rng.randint(-4, 6)
            while b == 0:
                b = rng.randint(-4, 6)
            c = rng.randint(-2, 8)
            a = c - b  # since a + b = c
            answer = a

            expr_text = f"{base}^a \u00D7 {_exp(base, b)} = {_exp(base, c)}"
            rule_explain = (
                f"Product of powers: a + {b} = {c}\n"
                f"a = {c} - {b} = {answer}"
            )
        elif eq_type == "quotient":
            # base^a / base^b = base^c, find a
            b = rng.randint(1, 5)
            c = rng.randint(-2, 5)
            a = c + b  # since a - b = c
            answer = a

            expr_text = f"{base}^a \u00F7 {_exp(base, b)} = {_exp(base, c)}"
            rule_explain = (
                f"Quotient of powers: a - {b} = {c}\n"
                f"a = {c} + {b} = {answer}"
            )
        else:  # power_of_power
            # (base^a)^b = base^c, find a
            b = rng.randint(2, 4)
            c = rng.randint(4, 12)
            # c must be divisible by b for clean answer
            c = b * rng.randint(1, 4)
            a = c // b
            answer = a

            expr_text = f"({base}^a)^{b} = {_exp(base, c)}"
            rule_explain = (
                f"Power of a power: a \u00D7 {b} = {c}\n"
                f"a = {c} \u00F7 {b} = {answer}"
            )

        answer_text = str(answer)

        stem_text = (
            f"An equation is given.\n\n"
            f"  {expr_text}\n\n"
            f"What is the value of a?"
        )

        worked = (
            f"Using exponent rules:\n"
            f"{rule_explain}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.NR,
                               Difficulty.DIFFICULT, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_text, answer_latex=f"${answer_text}$",
            worked_solution=worked,
            context_scenario="find missing exponent",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_approaching_mc,
            self.stem3_approaching_nr,
            self.stem4_at_mc,
            self.stem5_above_nr,
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
            2: self.stem2_approaching_mc,
            3: self.stem3_approaching_nr,
            4: self.stem4_at_mc,
            5: self.stem5_above_nr,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-5.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 8.NS.3 question variants...")
    gen = Stem8NS3(seed=42)
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
