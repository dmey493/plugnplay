"""
Stem generator for 7.NS.5:
  Find the prime factorization of whole numbers and write the results
  using exponents.

Content Limits:
  - Limit numbers to 225 or less
  - The prime factorization of a prime number should be written as the
    number itself (e.g., 17 is 17, not 17 x 1)
  - Students must understand prime and composite numbers
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: Numbers < 100 with two or fewer prime factors
  Medium: Numbers < 100 with three or four prime factors
  Difficult: Numbers from 100 to 225; prime factorization uses an exponent of 1

The 2026-08-17 revision moved the missing-exponent task down to Approaching
(stem 5), narrowed Below to multiples of 10 built from 2, 3 and 5 (stem 2),
and added a missing-factor bullet at Below (stem 6). Above became analyze
and justify for numbers 225 or greater, so stem 7 was written for it.
Stems 1, 3 and 4 already match their descriptors and were left untouched.

7 Stems from the Item Spec:
  Stem 1 (Below-MS):       Classify numbers as prime or composite (DOK 1, easy)
  Stem 2 (Below-NR):       Prime factorization without exponents (DOK 1, medium)
  Stem 3 (Approaching-MC): Prime factorization with exponents (DOK 1, easy)
  Stem 4 (At-NR):          Generate prime factorization using exponents (DOK 2, difficult)
  Stem 5 (Approaching-MC): Determine the missing exponent in a prime factorization (DOK 2, medium)
  Stem 6 (Below-NR):    Find a missing factor when all factors are 2, 3 or 5 (DOK 1, easy)
  Stem 7 (Above-ER):    Analyze and justify a prime factorization of a number 225 or greater (DOK 3, difficult)
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


STANDARD_CODE = "7.NS.5"
VARIANTS_PER_STEM = 20


# ============================================================
# HELPERS
# ============================================================

# Primes up to 225 for classification tasks (spec content limit: numbers <= 225)
PRIMES_TO_225 = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
    53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
    127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199,
    211, 223
]
PRIMES_TO_100 = [p for p in PRIMES_TO_225 if p < 100]
PRIMES_SET = set(PRIMES_TO_225)

# Composites in useful ranges
COMPOSITES_TO_100 = [n for n in range(4, 100) if n not in PRIMES_SET and n > 1]
COMPOSITES_100_225 = [n for n in range(100, 226) if n not in PRIMES_SET]


def prime_factorize(n):
    """Return dict mapping prime -> exponent for n."""
    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = 1
    return factors


def factors_to_str_no_exp(factors):
    """Format prime factorization without exponents, e.g. '2 x 3 x 7'."""
    parts = []
    for p in sorted(factors.keys()):
        for _ in range(factors[p]):
            parts.append(str(p))
    return " x ".join(parts)


def factors_to_str_exp(factors):
    """Format prime factorization with exponents, e.g. '2^3 x 3 x 5'."""
    parts = []
    for p in sorted(factors.keys()):
        e = factors[p]
        if e == 1:
            parts.append(str(p))
        else:
            parts.append(f"{p}^{e}")
    return " x ".join(parts)


def _fmt(val):
    """Format a signed rational value for display."""
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return str(int(val))
        f = float(val)
        if f == int(f):
            return str(int(f))
        s = f"{f:.4f}".rstrip('0').rstrip('.')
        return s
    if isinstance(val, float):
        if val == int(val):
            return str(int(val))
        s = f"{val:.4f}".rstrip('0').rstrip('.')
        return s
    return str(val)


class Stem7NS5:
    """Generates ~20 variants for each of 5 stems from the 7.NS.5 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MS (DOK 1, Easy)
    # Select prime numbers from a list
    # e.g., "Select three prime numbers: 2, 21, 47, 73, 76"
    # ================================================================

    def stem1_below_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        # Pick 3 primes and 2 composites (all < 100)
        primes_chosen = rng.sample(PRIMES_TO_100, 3)
        composites_chosen = rng.sample(COMPOSITES_TO_100, 2)

        all_numbers = primes_chosen + composites_chosen
        rng.shuffle(all_numbers)

        # Build choices
        choices = []
        for i, n in enumerate(all_numbers):
            is_prime = n in PRIMES_SET
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=str(n), text_latex=f"${n}$",
                is_correct=is_prime,
            ))

        correct_letters = ", ".join(c.key for c in choices if c.is_correct)

        stem_text = "Select three prime numbers."

        # Worked solution
        explanations = []
        for n in all_numbers:
            if n in PRIMES_SET:
                explanations.append(f"{n} is prime (only divisible by 1 and itself)")
            else:
                # Find a factor
                for d in range(2, n):
                    if n % d == 0:
                        explanations.append(f"{n} is composite ({n} = {d} x {n // d})")
                        break
        worked = "Classify each number:\n" + "\n".join(f"  {e}" for e in explanations)

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MS,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MS,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letters, answer_latex=correct_letters,
            worked_solution=worked,
            choices=choices, context_scenario="classify prime vs composite",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Below Proficiency - NR (DOK 1, Medium)
    # Prime factorization without exponents
    # e.g., "What is the prime factorization of 42?"
    # Answer: 2 x 3 x 7
    # ================================================================

    def stem2_below_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        # Medium: number < 100, 3-4 prime factors (counting multiplicity)
        # NOTE: NumberGenerator.prime_factorization("medium") has an infinite
        # loop bug when p1*p2*p3 >= 100 and all exponents are 1.
        # Generate directly here to avoid that bug.
        # Pick 3 distinct small primes, compute product, ensure < 100.
        # The 2026-08-17 Below descriptor limits identification to "whole
        # numbers that are multiples of 10 using only the prime numbers 2, 3,
        # and 5", so the old pool (24, 42, 66, 78 and friends) no longer fits.
        _medium_candidates = [
            20, 30, 40, 50, 60, 90, 100, 120, 150, 180, 200, 250, 300,
        ]
        n = rng.choice(_medium_candidates)
        factors = prime_factorize(n)

        answer_str = factors_to_str_no_exp(factors)

        stem_text = f"What is the prime factorization of {n}?"

        # Build factor tree explanation
        worked = f"Find the prime factorization of {n}:\n"
        temp = n
        steps = []
        for p in sorted(factors.keys()):
            for _ in range(factors[p]):
                steps.append(f"  {temp} / {p} = {temp // p}")
                temp //= p
        worked += "\n".join(steps)
        worked += f"\n\n{n} = {answer_str}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.NR,
                               Difficulty.MEDIUM, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_str, answer_latex=f"${answer_str}$",
            worked_solution=worked,
            context_scenario="prime factorization without exponents",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - MC (DOK 1, Easy)
    # Identify the correct prime factorization with exponents
    # e.g., "What is the prime factorization of 63?"
    # Options: 3 x 7, 3 x 21, 3 x 7^2, 3^2 x 7
    # ================================================================

    def stem3_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        # Easy: number < 100, <=2 distinct primes
        n, factors = gen.prime_factorization("easy")

        correct_str = factors_to_str_exp(factors)

        # Build distractors based on common errors
        distractors = set()

        # Error 1: wrong exponents (swap exponents if 2 factors)
        sorted_primes = sorted(factors.keys())
        if len(sorted_primes) >= 2:
            swapped = {}
            exps = [factors[p] for p in sorted_primes]
            for i, p in enumerate(sorted_primes):
                swapped[p] = exps[-(i + 1)]
            swap_str = factors_to_str_exp(swapped)
            if swap_str != correct_str:
                distractors.add(swap_str)

        # Error 2: include a non-prime factor (e.g., 3 x 21 instead of 3 x 7)
        if len(sorted_primes) >= 2:
            # Combine two primes into one composite factor
            p1, p2 = sorted_primes[0], sorted_primes[1]
            composite = p1 * p2
            remaining = dict(factors)
            remaining[p1] = max(0, remaining[p1] - 1)
            remaining[p2] = max(0, remaining[p2] - 1)
            parts = []
            for p in sorted(remaining.keys()):
                e = remaining[p]
                if e == 0:
                    continue
                if e == 1:
                    parts.append(str(p))
                else:
                    parts.append(f"{p}^{e}")
            parts.append(str(composite))
            parts.sort()
            err_str = " x ".join(parts)
            if err_str != correct_str:
                distractors.add(err_str)

        # Error 3: all exponents set to 1
        no_exp = {}
        for p in factors:
            no_exp[p] = 1
        no_exp_str = factors_to_str_exp(no_exp)
        if no_exp_str != correct_str:
            distractors.add(no_exp_str)

        # Error 4: one exponent off by 1
        if sorted_primes:
            p_adj = sorted_primes[0]
            adj_factors = dict(factors)
            adj_factors[p_adj] = factors[p_adj] + 1
            adj_str = factors_to_str_exp(adj_factors)
            if adj_str != correct_str:
                distractors.add(adj_str)

        dist_list = list(distractors)[:3]
        # Fill if needed with a hard cap to prevent infinite loops
        fill_attempts = 0
        while len(dist_list) < 3 and fill_attempts < 30:
            fill_attempts += 1
            # Strategy 1: adjust an exponent
            p_adj = rng.choice(sorted_primes)
            adj_factors = dict(factors)
            adj_offset = rng.choice([-1, 1, 2, -2])
            adj_factors[p_adj] = max(1, factors[p_adj] + adj_offset)
            adj_str = factors_to_str_exp(adj_factors)
            if adj_str != correct_str and adj_str not in dist_list:
                dist_list.append(adj_str)
                continue
            # Strategy 2: add a new prime
            new_p = rng.choice([2, 3, 5, 7, 11, 13])
            if new_p not in factors:
                extra = dict(factors)
                extra[new_p] = 1
                extra_str = factors_to_str_exp(extra)
                if extra_str != correct_str and extra_str not in dist_list:
                    dist_list.append(extra_str)

        dist_list = dist_list[:3]

        all_options = [(correct_str, True)] + [(d, False) for d in dist_list]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = f"What is the prime factorization of {n}?"

        # Build factor tree
        worked = f"Find the prime factorization of {n}:\n"
        temp = n
        for p in sorted(factors.keys()):
            for _ in range(factors[p]):
                worked += f"  {temp} / {p} = {temp // p}\n"
                temp //= p
        worked += f"\n{n} = {correct_str}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.EASY, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="prime factorization with exponents (MC)",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At Proficiency - NR (DOK 2, Difficult)
    # Generate prime factorization using exponents for numbers 100-225
    # e.g., "Find the prime factorization of 120. Write using exponents."
    # Answer: 2^3 x 3 x 5
    # ================================================================

    def stem4_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        # Difficult: number 100-225
        # NOTE: NumberGenerator.prime_factorization("difficult") has an
        # infinite loop bug when exponent adjustments oscillate.
        # Use a curated candidate list instead.
        _difficult_candidates = [
            100, 104, 108, 112, 120, 125, 126, 128, 132, 135,
            140, 144, 147, 150, 152, 156, 160, 162, 168, 175,
            176, 180, 189, 192, 196, 198, 200, 204, 207, 208,
            210, 216, 220, 224, 225
        ]
        n = rng.choice(_difficult_candidates)
        factors = prime_factorize(n)

        correct_str = factors_to_str_exp(factors)

        stem_text = (
            f"Find the prime factorization of {n}. Write the answer using exponents."
        )

        # Build factor tree
        worked = f"Find the prime factorization of {n}:\n"
        temp = n
        for p in sorted(factors.keys()):
            for _ in range(factors[p]):
                worked += f"  {temp} / {p} = {temp // p}\n"
                temp //= p
        worked += f"\n{n} = {correct_str}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.DIFFICULT, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_str, answer_latex=f"${correct_str}$",
            worked_solution=worked,
            context_scenario="prime factorization with exponents (100-225)",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above Proficiency - MC (DOK 1, Difficult)
    # Identify the missing exponent in a given prime factorization
    # e.g., "The prime factorization of 150 is 2 x 3 x 5^x = 150.
    #         What is the missing exponent x?"
    # Answer: 2
    # ================================================================

    def stem5_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        # Difficult: number 100-225
        # NOTE: NumberGenerator.prime_factorization("difficult") has an
        # infinite loop bug. Use curated candidates instead.
        _difficult_candidates = [
            100, 104, 108, 112, 120, 125, 126, 128, 132, 135,
            140, 144, 147, 150, 152, 156, 160, 162, 168, 175,
            176, 180, 189, 192, 196, 198, 200, 204, 207, 208,
            210, 216, 220, 224, 225
        ]
        n = rng.choice(_difficult_candidates)
        factors = prime_factorize(n)

        sorted_primes = sorted(factors.keys())

        # Pick a prime with exponent > 1 to hide (if possible)
        primes_with_exp = [p for p in sorted_primes if factors[p] > 1]
        if primes_with_exp:
            hidden_prime = rng.choice(primes_with_exp)
        else:
            hidden_prime = rng.choice(sorted_primes)

        hidden_exp = factors[hidden_prime]

        # Build the expression with the hidden exponent as 'x'
        parts = []
        for p in sorted_primes:
            e = factors[p]
            if p == hidden_prime:
                if e == 1:
                    parts.append(f"{p}^x")
                else:
                    parts.append(f"{p}^x")
            else:
                if e == 1:
                    parts.append(str(p))
                else:
                    parts.append(f"{p}^{e}")
        expr_str = " x ".join(parts)

        correct_str = str(hidden_exp)

        # Distractors: nearby exponents
        dist_set = set()
        for offset in [1, -1, 2, -2]:
            candidate = hidden_exp + offset
            if candidate > 0 and str(candidate) != correct_str:
                dist_set.add(str(candidate))
        dist_list = list(dist_set)[:3]
        while len(dist_list) < 3:
            d = str(rng.randint(1, 6))
            if d != correct_str and d not in dist_list:
                dist_list.append(d)
        dist_list = dist_list[:3]

        all_options = [(correct_str, True)] + [(d, False) for d in dist_list]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = (
            f"The prime factorization of {n} is given.\n\n"
            f"{expr_str} = {n}\n\n"
            f"What is the missing exponent, x?"
        )

        full_factorization = factors_to_str_exp(factors)
        worked = (
            f"The prime factorization of {n} is {full_factorization}.\n"
            f"The prime {hidden_prime} appears {hidden_exp} time(s).\n"
            f"So x = {hidden_exp}."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.MEDIUM, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="missing exponent in prime factorization",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    # ================================================================
    # STEM 6: Below Proficiency - NR (DOK 1, Easy)
    # NEW for the 2026-08-17 revision. Below gained "find a missing factor in
    # a prime factorization equality statement when all factors are 2, 3, or 5".
    # ================================================================
    def stem6_below_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)

        # Multiples of 10 whose factorisation uses only 2, 3 and 5, matching
        # the Below content limit.
        candidates = [20, 30, 40, 50, 60, 90, 100, 120, 150, 180, 200, 250, 300]
        n = rng.choice(candidates)

        factors = []
        rest = n
        for p in (2, 3, 5):
            while rest % p == 0:
                factors.append(p)
                rest //= p
        rng.shuffle(factors)
        hidden = rng.randrange(len(factors))
        answer = factors[hidden]
        shown = ["______" if i == hidden else str(f) for i, f in enumerate(factors)]

        stem_text = (
            "An equation is given."
            "\n\n" + " x ".join(shown) + f" = {n}"
            "\n\nWhat is the missing factor?"
        )

        others = [f for i, f in enumerate(factors) if i != hidden]
        worked = (
            f"Multiply the factors that are shown: "
            f"{' x '.join(str(f) for f in others)} = {n // answer}\n"
            f"{n} / {n // answer} = {answer}\n"
            f"The missing factor is {answer}."
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW,
                                         ItemType.NR, Difficulty.EASY, 6, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=str(answer), answer_latex=str(answer),
            worked_solution=worked,
            context_scenario="missing factor in a prime factorization",
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6, variant_index=variant_idx,
        )

    # ================================================================
    # STEM 7: Above Proficiency - ER (DOK 3, Difficult)
    # NEW for the 2026-08-17 revision. Above became "analyze and justify the
    # accuracy of a prime factorization expressed with exponents, including
    # multi-step decomposition of whole numbers 225 or greater". Stem 5 moved
    # down to Approaching, so without this Above would have no coverage.
    # ================================================================
    def stem7_above_er(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(7, variant_idx)
        student = pick_name(rng)

        # Whole numbers 225 or greater, as the descriptor requires.
        candidates = [225, 240, 252, 270, 288, 300, 315, 324, 336, 350,
                      360, 375, 392, 400, 432, 450, 486, 500, 504, 540]
        n = rng.choice(candidates)

        counts = {}
        rest = n
        p = 2
        while p * p <= rest:
            while rest % p == 0:
                counts[p] = counts.get(p, 0) + 1
                rest //= p
            p += 1
        if rest > 1:
            counts[rest] = counts.get(rest, 0) + 1

        def render(cs):
            parts = []
            for base in sorted(cs):
                e = cs[base]
                parts.append(f"{base}^{e}" if e > 1 else str(base))
            return " x ".join(parts)

        correct = render(counts)

        # The classic error: stop one decomposition short, leaving a composite
        # factor in place. Pick a prime with an exponent to fold back up.
        foldable = [b for b, e in counts.items() if e >= 2]
        if foldable:
            base = rng.choice(foldable)
            wrong = dict(counts)
            wrong[base] -= 2
            if wrong[base] == 0:
                del wrong[base]
            composite = base * base
            wrong_parts = [render(wrong)] if wrong else []
            wrong_parts.append(str(composite))
            claimed = " x ".join(p for p in wrong_parts if p)
            flaw = (f"{composite} is not prime; it is {base} x {base}, so the "
                    f"factorization is not finished")
        else:
            base = max(counts)
            claimed = render({b: e for b, e in counts.items() if b != base}) + f" x {base}^2"
            flaw = f"the exponent on {base} is wrong; {base} appears only once"

        stem_text = (
            f"{student} writes the prime factorization of {n} as:"
            f"\n\n{claimed}"
            f"\n\nIs {student} correct? Analyze the factorization and use "
            f"words and equations to justify your answer."
        )

        answer = (
            f"{student} is not correct. The product does reach {n}, but {flaw}.\n"
            f"Decomposing completely gives {n} = {correct}.\n"
            f"A prime factorization is finished only when every factor is prime."
        )

        worked = (
            f"Check the product first, then check that every factor is prime.\n"
            f"{student} wrote: {claimed}\n"
            f"Problem: {flaw}.\n"
            f"Correct factorization: {n} = {correct}"
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE,
                                         ItemType.ER, Difficulty.DIFFICULT, 7, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=ItemType.ER,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=worked,
            context_scenario="analyze and justify a prime factorization",
            seed=self.base_seed * 1000 + 700 + variant_idx,
            stem_index=7, variant_index=variant_idx,
        )

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_ms,
            self.stem2_below_nr,
            self.stem3_approaching_mc,
            self.stem4_at_nr,
            self.stem5_approaching_mc,
            self.stem6_below_nr,
            self.stem7_above_er,
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
            2: self.stem2_below_nr,
            3: self.stem3_approaching_mc,
            4: self.stem4_at_nr,
            5: self.stem5_approaching_mc,
            6: self.stem6_below_nr,
            7: self.stem7_above_er,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-5.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 7.NS.5 question variants...")
    gen = Stem7NS5(seed=42)
    all_q = gen.generate_all_variants(variants_per_stem=3)
    for q in all_q:
        print(f"\n{'='*60}")
        print(f"ID: {q.question_id}")
        print(f"Stem {q.stem_index} | {q.proficiency_level.value} | {q.difficulty.value} | DOK {q.dok} | {q.item_type.value}")
        print(f"\n{q.stem_text}")
        if q.choices:
            for c in q.choices:
                marker = " *" if c.is_correct else ""
                print(f"  {c.key}. {c.text}{marker}")
        print(f"\nAnswer: {q.answer_text}")
        print(f"\nWorked Solution:\n{q.worked_solution}")
    print(f"\n{'='*60}")
    print(f"Total: {len(all_q)}")
