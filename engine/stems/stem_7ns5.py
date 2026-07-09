"""
Stem generator for 7.NS.5:
  Find the prime factorization of whole numbers and write the results
  using exponents.

Content Limits:
  - Limit numbers to 200 or less
  - The prime factorization of a prime number should be written as the
    number itself (e.g., 17 is 17, not 17 x 1)
  - Students must understand prime and composite numbers
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: Numbers < 100 with two or fewer prime factors
  Medium: Numbers < 100 with three or four prime factors
  Difficult: Numbers from 100 to 200; prime factorization uses an exponent of 1

5 Stems from the Item Spec:
  Stem 1 (Below-MS):       Classify numbers as prime or composite (DOK 1, easy)
  Stem 2 (Below-NR):       Prime factorization without exponents (DOK 1, medium)
  Stem 3 (Approaching-MC): Prime factorization with exponents (DOK 1, easy)
  Stem 4 (At-NR):          Generate prime factorization using exponents (DOK 2, difficult)
  Stem 5 (Above-MC):       Identify missing exponent in a given prime factorization (DOK 1, difficult)
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

# Primes up to 200 for classification tasks
PRIMES_TO_200 = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
    53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
    127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199
]
PRIMES_TO_100 = [p for p in PRIMES_TO_200 if p < 100]
PRIMES_SET = set(PRIMES_TO_200)

# Composites in useful ranges
COMPOSITES_TO_100 = [n for n in range(4, 100) if n not in PRIMES_SET and n > 1]
COMPOSITES_100_200 = [n for n in range(100, 201) if n not in PRIMES_SET]


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
        _medium_candidates = [
            # n = product of 3+ prime factors with multiplicity, n < 100
            30, 42, 60, 66, 70, 78,    # 3 distinct primes
            12, 18, 20, 24, 28, 36,    # 2 primes, 3-4 factors total
            40, 44, 45, 48, 50, 54,
            56, 72, 75, 80, 84, 90, 96,
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
    # Generate prime factorization using exponents for numbers 100-200
    # e.g., "Find the prime factorization of 120. Write using exponents."
    # Answer: 2^3 x 3 x 5
    # ================================================================

    def stem4_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        # Difficult: number 100-200
        # NOTE: NumberGenerator.prime_factorization("difficult") has an
        # infinite loop bug when exponent adjustments oscillate.
        # Use a curated candidate list instead.
        _difficult_candidates = [
            100, 104, 108, 112, 120, 125, 126, 128, 132, 135,
            140, 144, 147, 150, 152, 156, 160, 162, 168, 175,
            176, 180, 189, 192, 196, 198, 200
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
            context_scenario="prime factorization with exponents (100-200)",
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

    def stem5_above_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        # Difficult: number 100-200
        # NOTE: NumberGenerator.prime_factorization("difficult") has an
        # infinite loop bug. Use curated candidates instead.
        _difficult_candidates = [
            100, 104, 108, 112, 120, 125, 126, 128, 132, 135,
            140, 144, 147, 150, 152, 156, 160, 162, 168, 175,
            176, 180, 189, 192, 196, 198, 200
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

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MC,
                               Difficulty.DIFFICULT, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=1, item_type=ItemType.MC,
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

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_ms,
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
            1: self.stem1_below_ms,
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
