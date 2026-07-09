"""
Stem generator for 8.NS.1:
  Give examples of rational and irrational numbers, and explain the
  difference between them. State decimal equivalents for any number.
  For rational numbers, show that the decimal equivalent terminates
  or repeats, and convert a repeating decimal into a rational number.

Content Limits:
  - All irrational numbers, excluding e
  - Rational: integers, fractions, terminating decimals, repeating decimals
  - Irrational: non-repeating non-terminating decimals, sqrt of non-perfect-squares, pi
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: positive numbers, √2/sqrt(3)/pi, single-digit repeating decimals
  Medium: +/- numbers, sqrt of primes and perfect squares, two-digit repeating
  Difficult: sqrt of composites, 3-digit repeating or mixed repeating, non-terminating

6 Stems from the Item Spec:
  Stem 1 (Below-MS, DOK 1, Easy):  Select all numbers that are irrational
  Stem 2 (Below-TM, DOK 1, Medium): Classify numbers as rational or irrational (table)
  Stem 3 (Approaching-NR, DOK 1, Medium): Convert a repeating decimal to a fraction
  Stem 4 (Approaching-TM, DOK 1, Easy): Convert fractions to decimals, classify as
           terminating or repeating
  Stem 5 (At-MC, DOK 1, Difficult): Identify which number is irrational from tricky options
  Stem 6 (Above-MP, DOK 3, Medium): Prove/disprove generalization about rational/irrational
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


STANDARD_CODE = "8.NS.1"
VARIANTS_PER_STEM = 20


# ============================================================
# HELPERS
# ============================================================

# Perfect squares up to 400 for reference
PERFECT_SQUARES = {i*i for i in range(1, 21)}

# Common irrational numbers for easy difficulty
EASY_IRRATIONALS = [
    ("\u221A2", "irrational", "\u221A2 is irrational because 2 is not a perfect square"),
    ("\u221A3", "irrational", "\u221A3 is irrational because 3 is not a perfect square"),
    ("\u03C0", "irrational", "\u03C0 is irrational -- it is non-repeating and non-terminating"),
]

# Non-perfect-square primes for medium difficulty
MEDIUM_SQRT_VALS = [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

# Composite non-perfect-squares for difficult
DIFFICULT_SQRT_VALS = [6, 8, 10, 12, 14, 15, 18, 20, 21, 22, 24, 26, 27, 28, 30]

# Perfect square values for "tricky" rational square roots
PERFECT_SQUARE_LIST = [4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196, 225]


def _repeating_decimal_str(numer, denom):
    """Return a decimal string with ellipsis for repeating decimals.
    E.g., 1/3 -> '0.333...',  1/6 -> '0.1666...',  1/11 -> '0.0909...'
    Uses '...' (ellipsis) since fpdf2 doesn't support overbar.
    """
    if denom == 0:
        return "undefined"
    frac = Fraction(numer, denom)
    if frac.denominator == 1:
        return str(int(frac))

    # Check if terminating
    d = frac.denominator
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5
    if d == 1:
        # Terminating decimal
        val = float(frac)
        return f"{val:.6f}".rstrip('0').rstrip('.')

    # Repeating: compute enough digits to show the pattern
    val = float(frac)
    s = f"{val:.10f}".rstrip('0')
    # Add ellipsis to indicate repeating
    return s + "..."


def _is_terminating(frac):
    """Check if a fraction produces a terminating decimal."""
    d = frac.denominator
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5
    return d == 1


def _fmt_frac(val):
    """Format a Fraction as a simple string."""
    if val.denominator == 1:
        return str(int(val))
    return f"{val.numerator}/{val.denominator}"


class Stem8NS1:
    """Generates ~20 variants for each of 5 stems from the 8.NS.1 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MS (DOK 1, Easy)
    # Select all numbers that are irrational
    # ================================================================

    def stem1_below_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        # Build a pool of 6 numbers: 2-3 irrational, rest rational
        numbers = []

        # Add 2-3 irrational numbers (easy: √2, sqrt(3), pi)
        num_irrational = rng.choice([2, 3])
        irr_pool = list(EASY_IRRATIONALS)
        rng.shuffle(irr_pool)
        for i in range(num_irrational):
            display, classification, reason = irr_pool[i]
            numbers.append((display, True, reason))

        # Add rational numbers to fill up to 6
        rational_pool = []
        # Integer
        rational_pool.append((str(rng.randint(1, 20)), False,
                              "This is an integer, which is rational"))
        # Terminating decimal
        dec = rng.choice([0.5, 0.25, 0.75, 1.5, 2.4, 3.8, 0.125])
        rational_pool.append((str(dec), False,
                              f"{dec} is a terminating decimal, which is rational"))
        # Fraction
        num = rng.randint(1, 7)
        den = rng.choice([2, 3, 4, 5, 8])
        rational_pool.append((f"{num}/{den}", False,
                              f"{num}/{den} is a fraction of integers, which is rational"))
        # Repeating decimal (single repeating digit)
        rep_options = [
            ("0.333...", False, "0.333... = 1/3, a repeating decimal is rational"),
            ("0.666...", False, "0.666... = 2/3, a repeating decimal is rational"),
            ("0.111...", False, "0.111... = 1/9, a repeating decimal is rational"),
        ]
        rational_pool.append(rng.choice(rep_options))
        # Perfect square root
        psq = rng.choice([4, 9, 16, 25, 36, 49, 64, 100])
        root = int(math.isqrt(psq))
        rational_pool.append((f"\u221A{psq}", False,
                              f"\u221A{psq} = {root}, which is a whole number (rational)"))

        rng.shuffle(rational_pool)
        num_rational = 6 - num_irrational
        for i in range(num_rational):
            numbers.append(rational_pool[i])

        rng.shuffle(numbers)

        choices = []
        for i, (display, is_irrational, reason) in enumerate(numbers):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i),
                text=display,
                text_latex=f"${display}$" if display != "pi" else "$\\pi$",
                is_correct=is_irrational,
                distractor_rationale=reason,
            ))

        correct_letters = sorted([c.key for c in choices if c.is_correct])
        answer_str = ", ".join(correct_letters)

        stem_text = "Select all numbers that are irrational."

        irrational_list = [c.text for c in choices if c.is_correct]
        worked = (
            "An irrational number cannot be expressed as a fraction of two integers.\n"
            "It has a non-repeating, non-terminating decimal expansion.\n"
            f"The irrational numbers are: {', '.join(irrational_list)}."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MS,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MS,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_str, answer_latex=answer_str,
            worked_solution=worked,
            choices=choices, context_scenario="classify irrational numbers",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Below Proficiency - TM (DOK 1, Medium)
    # Classify numbers as rational or irrational (table matching)
    # ================================================================

    def stem2_below_tm(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        # Build 5 numbers: mix of rational and irrational
        items = []

        # 2 irrational: sqrt of prime numbers
        primes_for_sqrt = rng.sample(MEDIUM_SQRT_VALS[:8], 2)
        for p in primes_for_sqrt:
            items.append((f"\u221A{p}", "Irrational",
                          f"\u221A{p} is irrational because {p} is not a perfect square"))

        # 3 rational: mix of types
        # Perfect square root
        psq = rng.choice(PERFECT_SQUARE_LIST[:8])
        root = int(math.isqrt(psq))
        items.append((f"\u221A{psq}", "Rational",
                      f"\u221A{psq} = {root}, which is a whole number"))

        # Fraction
        num = rng.randint(1, 9)
        den = rng.choice([2, 3, 4, 5, 7, 8, 9, 11])
        items.append((f"{num}/{den}", "Rational",
                      f"{num}/{den} is a ratio of two integers"))

        # Repeating decimal (two repeating digits)
        rep_options = [
            ("0.1212...", "Rational", "0.1212... = 4/33, a repeating decimal is rational"),
            ("0.2727...", "Rational", "0.2727... = 3/11, a repeating decimal is rational"),
            ("0.3636...", "Rational", "0.3636... = 4/11, a repeating decimal is rational"),
            ("0.4545...", "Rational", "0.4545... = 5/11, a repeating decimal is rational"),
            ("0.0909...", "Rational", "0.0909... = 1/11, a repeating decimal is rational"),
        ]
        items.append(rng.choice(rep_options))

        rng.shuffle(items)

        # Build the question as a table matching problem
        rows_text = []
        for display, classification, reason in items:
            rows_text.append(f"  {display} --> {classification}")

        stem_text = (
            'Select "Rational" or "Irrational" to describe each number.\n\n'
        )
        for display, _, _ in items:
            stem_text += f"  {display}:  [ Rational ]  [ Irrational ]\n"

        answer_lines = []
        for display, classification, _ in items:
            answer_lines.append(f"{display}: {classification}")
        answer_text = "; ".join(answer_lines)

        worked_parts = []
        for display, classification, reason in items:
            worked_parts.append(f"- {display}: {classification} ({reason})")
        worked = (
            "A rational number can be expressed as a ratio of two integers.\n"
            "An irrational number cannot -- it has a non-repeating, "
            "non-terminating decimal.\n\n"
            + "\n".join(worked_parts)
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.TM,
                               Difficulty.MEDIUM, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.TM,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_text, answer_latex=answer_text,
            worked_solution=worked,
            context_scenario="classify rational vs irrational table",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - NR (DOK 1, Medium)
    # Convert a repeating decimal into a fraction
    # ================================================================

    def stem3_approaching_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        # Pick a repeating decimal with a 1 or 2 digit repeating block
        # These are well-known conversions students can do by hand
        repeating_decimals = [
            # (display, fraction_numer, fraction_denom, repeat_digits)
            ("0.333...", 1, 3, "3"),
            ("0.666...", 2, 3, "6"),
            ("0.111...", 1, 9, "1"),
            ("0.222...", 2, 9, "2"),
            ("0.444...", 4, 9, "4"),
            ("0.555...", 5, 9, "5"),
            ("0.777...", 7, 9, "7"),
            ("0.888...", 8, 9, "8"),
            ("0.0909...", 1, 11, "09"),
            ("0.1818...", 2, 11, "18"),
            ("0.2727...", 3, 11, "27"),
            ("0.3636...", 4, 11, "36"),
            ("0.4545...", 5, 11, "45"),
            ("0.5454...", 6, 11, "54"),
            ("0.1212...", 4, 33, "12"),
            ("0.2121...", 7, 33, "21"),
            ("0.1515...", 5, 33, "15"),
        ]

        choice = rng.choice(repeating_decimals)
        display, numer, denom, repeat = choice

        frac = Fraction(numer, denom)
        answer_str = f"{frac.numerator}/{frac.denominator}"

        stem_text = (
            f"Enter {display} as a fraction.\n\n"
            f"Write your answer in the form a/b."
        )

        # Worked solution showing the algebraic method
        repeat_len = len(repeat)
        multiplier = 10 ** repeat_len
        worked = (
            f"Let x = {display}\n"
            f"Then {multiplier}x = {repeat}.{repeat}{repeat[:2]}...\n"
            f"{multiplier}x - x = {repeat}\n"
            f"{multiplier - 1}x = {repeat}\n"
            f"x = {repeat}/{multiplier - 1}\n"
            f"x = {frac.numerator}/{frac.denominator}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.NR,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_str, answer_latex=f"$\\frac{{{frac.numerator}}}{{{frac.denominator}}}$",
            worked_solution=worked,
            context_scenario="convert repeating decimal to fraction",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: Approaching Proficiency - TM (DOK 1, Easy)
    # Convert fractions to decimals, classify as terminating or repeating
    # ================================================================

    def stem4_approaching_tm(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        # Build 4-5 fractions, mix of terminating and repeating
        fractions_pool_term = [
            (Fraction(1, 2), "0.5"),
            (Fraction(1, 4), "0.25"),
            (Fraction(3, 4), "0.75"),
            (Fraction(1, 5), "0.2"),
            (Fraction(2, 5), "0.4"),
            (Fraction(3, 5), "0.6"),
            (Fraction(1, 8), "0.125"),
            (Fraction(3, 8), "0.375"),
            (Fraction(5, 8), "0.625"),
            (Fraction(7, 8), "0.875"),
            (Fraction(1, 10), "0.1"),
            (Fraction(3, 10), "0.3"),
            (Fraction(1, 20), "0.05"),
            (Fraction(1, 25), "0.04"),
        ]

        fractions_pool_rep = [
            (Fraction(1, 3), "0.333..."),
            (Fraction(2, 3), "0.666..."),
            (Fraction(1, 6), "0.1666..."),
            (Fraction(5, 6), "0.8333..."),
            (Fraction(1, 7), "0.142857..."),
            (Fraction(1, 9), "0.111..."),
            (Fraction(2, 9), "0.222..."),
            (Fraction(4, 9), "0.444..."),
            (Fraction(1, 11), "0.0909..."),
            (Fraction(1, 12), "0.08333..."),
        ]

        # Pick 2 terminating and 2 repeating
        terms = rng.sample(fractions_pool_term, 2)
        reps = rng.sample(fractions_pool_rep, 2)

        items = []
        for frac, dec_str in terms:
            items.append((_fmt_frac(frac), dec_str, "Terminating"))
        for frac, dec_str in reps:
            items.append((_fmt_frac(frac), dec_str, "Repeating"))

        rng.shuffle(items)

        stem_text = (
            "Convert each fraction to a decimal. Then classify each "
            "as terminating or repeating.\n\n"
        )
        for frac_str, _, _ in items:
            stem_text += f"  {frac_str}:  decimal = ___   [ Terminating ]  [ Repeating ]\n"

        answer_lines = []
        for frac_str, dec_str, classification in items:
            answer_lines.append(f"{frac_str} = {dec_str} ({classification})")
        answer_text = "; ".join(answer_lines)

        worked_parts = []
        for frac_str, dec_str, classification in items:
            worked_parts.append(f"- {frac_str} = {dec_str} --> {classification}")
        worked = (
            "A terminating decimal has a finite number of digits after the "
            "decimal point.\n"
            "A repeating decimal has a digit or group of digits that repeats "
            "forever.\n\n"
            + "\n".join(worked_parts)
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.TM,
                               Difficulty.EASY, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.TM,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_text, answer_latex=answer_text,
            worked_solution=worked,
            context_scenario="fraction to decimal classification",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: At Proficiency - MC (DOK 1, Difficult)
    # Identify which number is irrational from tricky options
    # (e.g., options include sqrt of fractions, π/π, sqrt(non-perfect)/1)
    # ================================================================

    def stem5_at_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        # The correct answer: an irrational number that might look rational
        # Pick a non-perfect square for the irrational sqrt
        n = rng.choice(DIFFICULT_SQRT_VALS)

        correct_display = f"\u221A{n}"
        correct_reason = (
            f"\u221A{n} is irrational because {n} is not a perfect square. "
            f"Its decimal expansion is non-repeating and non-terminating."
        )

        # Distractors: numbers that look irrational but are actually rational
        distractors = []

        # sqrt of a perfect square
        psq = rng.choice([4, 9, 16, 25, 36, 49, 64])
        root = int(math.isqrt(psq))
        distractors.append((
            f"\u221A{psq}",
            f"\u221A{psq} = {root}, which is rational"
        ))

        # A repeating decimal (looks non-terminating but is rational)
        rep_options = [
            ("0.1234567891011...", "This pattern does not repeat, so it looks irrational, but this specific question asks about the others"),
            ("0.121212...", "0.121212... = 4/33, which is rational"),
            ("0.999...", "0.999... = 1, which is rational"),
            ("0.454545...", "0.454545... = 5/11, which is rational"),
        ]
        rep_choice = rng.choice(rep_options[1:])  # skip the tricky one
        distractors.append(rep_choice)

        # A fraction that looks complex
        frac_n = rng.choice([7, 11, 13, 17, 22])
        frac_d = rng.choice([3, 7, 9, 11, 13])
        if frac_n == frac_d:
            frac_d = frac_n + 1
        distractors.append((
            f"{frac_n}/{frac_d}",
            f"{frac_n}/{frac_d} is a ratio of two integers, which is rational"
        ))

        all_options = [(correct_display, True, correct_reason)]
        for text, reason in distractors[:3]:
            all_options.append((text, False, reason))
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct, reason) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i),
                text=text,
                text_latex=f"${text}$",
                is_correct=is_correct,
                distractor_rationale=reason,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = "Which number is irrational?"

        worked = (
            f"A number is irrational if it cannot be written as a/b where "
            f"a and b are integers.\n\n"
        )
        for _, _, reason in all_options:
            worked += f"- {reason}\n"
        worked += f"\nThe answer is {correct_display}."

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MC,
                               Difficulty.DIFFICULT, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="identify irrational from tricky options",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    # STEM 6: Above Proficiency - MP (DOK 3, Medium)
    # Analyze, justify, and apply reasoning to prove or disprove a
    # generalization about rational or irrational numbers.
    # ================================================================

    def stem6_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)

        # Debate scenarios: two students make claims about rational/irrational
        scenarios = [
            {
                "setup": (
                    "A student claims that the decimal 0.454545... is rational "
                    "because it repeats. Another student argues that not all "
                    "repeating decimals are rational."
                ),
                "partA_prompt": "Which student is correct?",
                "partA_answer": "The first student is correct.",
                "partB_prompt": (
                    "Justify your answer using mathematical reasoning "
                    "about rational and irrational numbers."
                ),
                "partB_answer": (
                    "The first student is correct. A repeating decimal is always "
                    "rational because it can be expressed as a fraction. "
                    "0.454545... = 45/99 = 5/11. Irrational numbers have "
                    "non-repeating, non-terminating decimal expansions."
                ),
            },
            {
                "setup": (
                    "A student claims that the product of two irrational numbers "
                    "is always irrational. Another student disagrees."
                ),
                "partA_prompt": "Which student is correct? Give an example to support your answer.",
                "partA_answer": "The second student is correct.",
                "partB_prompt": "Provide a counterexample that disproves the first student's claim.",
                "partB_answer": (
                    "The second student is correct. √2 x √2 = 2, "
                    "which is rational. So the product of two irrational numbers "
                    "is not always irrational."
                ),
            },
            {
                "setup": (
                    "A student claims that 0.101001000100001... is rational "
                    "because it follows a pattern. Another student says it is irrational."
                ),
                "partA_prompt": "Which student is correct?",
                "partA_answer": "The second student is correct.",
                "partB_prompt": (
                    "Explain why the decimal is rational or irrational using "
                    "the definitions of these number types."
                ),
                "partB_answer": (
                    "The second student is correct. Although 0.101001000100001... "
                    "has a pattern, it does not repeat a fixed block of digits. "
                    "The number of zeros keeps increasing, so it is non-repeating "
                    "and non-terminating, which makes it irrational."
                ),
            },
            {
                "setup": (
                    "A student claims that π/π is irrational because pi "
                    "is irrational. Another student says the result is rational."
                ),
                "partA_prompt": "Which student is correct?",
                "partA_answer": "The second student is correct.",
                "partB_prompt": "Calculate π/π and explain why the result is rational or irrational.",
                "partB_answer": (
                    "The second student is correct. π/π = 1, which is a "
                    "whole number and therefore rational. Dividing any nonzero "
                    "number by itself equals 1."
                ),
            },
            {
                "setup": (
                    "A student claims that √2 + √2 is irrational. "
                    "Another student says it must be rational because addition "
                    "of two numbers gives a rational result."
                ),
                "partA_prompt": "Which student is correct?",
                "partA_answer": "The first student is correct.",
                "partB_prompt": "Simplify the expression and explain your reasoning.",
                "partB_answer": (
                    "The first student is correct. √2 + √2 = 2 x √2, "
                    "which is still irrational. A nonzero rational times an "
                    "irrational number is always irrational."
                ),
            },
            {
                "setup": (
                    "A student claims that the sum of a rational and an "
                    "irrational number is always irrational. Another student "
                    "says this is not always true."
                ),
                "partA_prompt": "Which student is correct?",
                "partA_answer": "The first student is correct.",
                "partB_prompt": "Explain why the sum of a rational and an irrational number is always irrational.",
                "partB_answer": (
                    "The first student is correct. If r is rational and i is "
                    "irrational, suppose r + i = q (rational). Then i = q - r, "
                    "but the difference of two rational numbers is rational, "
                    "which contradicts i being irrational. So r + i must be irrational."
                ),
            },
        ]

        scenario = scenarios[variant_idx % len(scenarios)]

        stem_text = (
            f"{scenario['setup']}\n\n"
            f"Part A: Which student is correct?\n\n"
            f"Part B: Justify your answer using mathematical reasoning about rational and irrational numbers."
        )

        parts = [
            QuestionPart(
                label="Part A",
                prompt=scenario["partA_prompt"],
                prompt_latex=scenario["partA_prompt"],
                answer=scenario["partA_answer"],
                answer_latex=scenario["partA_answer"],
                item_type=ItemType.NR,
            ),
            QuestionPart(
                label="Part B",
                prompt=scenario["partB_prompt"],
                prompt_latex=scenario["partB_prompt"],
                answer=scenario["partB_answer"],
                answer_latex=scenario["partB_answer"],
                item_type=ItemType.ER,
            ),
        ]

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.MEDIUM, 6, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.MEDIUM, dok=3, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"A: {scenario['partA_answer']}",
            answer_latex=f"A: {scenario['partA_answer']}",
            worked_solution=scenario["partB_answer"],
            parts=parts,
            context_scenario="prove/disprove generalization about rational/irrational",
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6, variant_index=variant_idx,
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_ms,
            self.stem2_below_tm,
            self.stem3_approaching_nr,
            self.stem4_approaching_tm,
            self.stem5_at_mc,
            self.stem6_above_mp,
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
            1: self.stem1_below_ms,
            2: self.stem2_below_tm,
            3: self.stem3_approaching_nr,
            4: self.stem4_approaching_tm,
            5: self.stem5_at_mc,
            6: self.stem6_above_mp,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-6.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 8.NS.1 question variants...")
    gen = Stem8NS1(seed=42)
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
