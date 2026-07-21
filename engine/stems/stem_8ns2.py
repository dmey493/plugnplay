"""
Stem generator for 8.NS.2:
  Use rational approximations of irrational numbers to compare the size
  of irrational numbers, plot them approximately on a number line, and
  estimate the value of expressions involving irrational numbers.

Content Limits:
  - Irrational numbers: sqrt(k), k*pi where k is positive
  - Approximations in the form of integers only
  - No cube roots
  - Irrational expressions use only one operation
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: sqrt(2), sqrt(3); number lines with integer intervals
  Medium: sqrt of primes < 100; number lines with halves
  Difficult: sqrt of composites, expressions, sqrt > 100; number lines with quarters

5 Stems from the Item Spec:
  Stem 1 (Below-MC, DOK 2, Easy): Approximate value of sqrt to nearest whole number
  Stem 2 (Approaching-MC, DOK 1, Medium): Which range contains the value of sqrt(n)?
  Stem 3 (Approaching-MS, DOK 2, Difficult): Select all numbers in a given range
  Stem 4 (At-TM, DOK 2, Medium): Compare irrational and rational numbers (true/false)
  Stem 5 (Above-MS, DOK 2, Difficult): Select expressions > a given value
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


STANDARD_CODE = "8.NS.2"
VARIANTS_PER_STEM = 20


# ============================================================
# HELPERS
# ============================================================

PERFECT_SQUARES = {i*i for i in range(1, 21)}

# Easy: sqrt(2), sqrt(3), sqrt(5), sqrt(6), sqrt(7), sqrt(8)
EASY_SQRT = [2, 3, 5, 6, 7, 8]

# Medium: primes < 100 that are not perfect squares
MEDIUM_SQRT = [10, 11, 13, 14, 15, 17, 19, 21, 23, 26, 28, 29, 30,
               31, 33, 34, 37, 38, 39, 41, 42, 43, 46, 47]

# Difficult: composites and larger numbers
DIFFICULT_SQRT = [50, 55, 60, 65, 70, 75, 80, 85, 90, 95,
                  101, 105, 110, 115, 120, 125, 130, 140, 150]


def _sqrt_bounds(n):
    """Return (lower, upper) integers such that lower < sqrt(n) < upper."""
    lower = int(math.isqrt(n))
    if lower * lower == n:
        return (lower, lower)  # perfect square
    return (lower, lower + 1)


def _approx_sqrt(n):
    """Return approximate decimal value of sqrt(n)."""
    return math.sqrt(n)


class Stem8NS2:
    """Generates ~20 variants for each of 5 stems from the 8.NS.2 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 2, Easy)
    # What is the approximate value of sqrt(n) to the nearest whole number?
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        n = rng.choice(EASY_SQRT)
        actual = math.sqrt(n)
        nearest = round(actual)
        lower, upper = _sqrt_bounds(n)

        stem_text = (
            f"What is the approximate value of \u221A{n}, "
            f"to the nearest whole number?"
        )
        stem_latex = (
            f"What is the approximate value of $\\sqrt{{{n}}}$, "
            f"to the nearest whole number?"
        )

        correct_str = str(nearest)

        # Distractors: nearby integers
        distractors = set()
        distractors.add(str(lower))
        distractors.add(str(upper))
        distractors.add(str(nearest + 2))
        if nearest > 2:
            distractors.add(str(nearest - 2))
        distractors.add(str(n))  # common error: confuse n with sqrt(n)
        distractors.discard(correct_str)
        dist_list = sorted(distractors)[:3]

        # Small radicands (e.g. sqrt(2)) can collapse the pool below 3
        # distractors; pad with further-out integers to guarantee 4 choices.
        pad = nearest + 3
        while len(dist_list) < 3:
            s = str(pad)
            if s != correct_str and s not in dist_list:
                dist_list.append(s)
            pad += 1

        all_options = [(correct_str, True)] + [(d, False) for d in dist_list]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"\u221A{n} is between {lower} and {upper} "
            f"because {lower}\u00B2 = {lower**2} and {upper}\u00B2 = {upper**2}.\n"
            f"\u221A{n} is approximately {actual:.3f}.\n"
            f"Rounded to the nearest whole number: {nearest}."
        )

        # Numerically labeled number line: consecutive integer ticks
        # bracketing sqrt(n) so the root falls inside the shown range.
        # (e.g. sqrt(5) ~ 2.24 -> ticks [0, 1, 2, 3])
        tick_lo = max(0, lower - 1)
        tick_hi = upper + 1
        nl_render = {
            "type": "number_line_point",
            "ticks": list(range(tick_lo, tick_hi + 1)),
        }

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_latex,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="approximate sqrt to nearest whole",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx,
            render_data=nl_render,
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - MC (DOK 1, Medium)
    # Which range contains the value of sqrt(n)?
    # ================================================================

    def stem2_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        n = rng.choice(MEDIUM_SQRT)
        lower, upper = _sqrt_bounds(n)

        stem_text = f"Which range contains the value of \u221A{n}?"
        stem_latex = f"Which range contains the value of $\\sqrt{{{n}}}$?"

        correct = f"Between {lower} and {upper}"

        # Distractors: wrong ranges
        distractors = []
        if lower >= 2:
            distractors.append(f"Between {lower - 1} and {lower}")
        distractors.append(f"Between {upper} and {upper + 1}")
        distractors.append(f"Between {lower + 2} and {lower + 3}")
        # Common error: confuse n with sqrt(n)
        if n > 10:
            distractors.append(f"Between {n - 1} and {n}")
        if len(distractors) < 3:
            distractors.append(f"Between {lower - 2} and {lower - 1}")

        distractors = [d for d in distractors if d != correct][:3]

        all_options = [(correct, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"We need to find which two consecutive integers \u221A{n} "
            f"falls between.\n"
            f"{lower}\u00B2 = {lower**2} and {upper}\u00B2 = {upper**2}.\n"
            f"Since {lower**2} < {n} < {upper**2}, "
            f"\u221A{n} is between {lower} and {upper}."
        )

        # Numerically labeled number line: consecutive integer ticks
        # bracketing sqrt(n) so the root falls inside the shown range.
        tick_lo = max(0, lower - 1)
        tick_hi = upper + 1
        nl_render = {
            "type": "number_line_point",
            "ticks": list(range(tick_lo, tick_hi + 1)),
        }

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.MEDIUM, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_latex,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="identify range for sqrt",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx,
            render_data=nl_render,
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - MS (DOK 2, Difficult)
    # Select all numbers greater than A and less than B
    # (mix of irrational sqrts and rational numbers)
    # ================================================================

    def stem3_approaching_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        # Set a range [low_bound, high_bound]
        low_int = rng.randint(2, 6)
        high_int = low_int + rng.randint(2, 4)
        low_bound = low_int + rng.choice([0, 0.5])
        high_bound = high_int + rng.choice([0, 0.5])

        # Generate 6 numbers: mix of sqrts and rationals
        options = []

        # Add some irrational numbers (sqrts)
        used_n = set()
        for _ in range(3):
            for attempt in range(50):
                n = rng.randint(2, 99)
                if n in PERFECT_SQUARES or n in used_n:
                    continue
                used_n.add(n)
                val = math.sqrt(n)
                in_range = low_bound < val < high_bound
                options.append((f"\u221A{n}", val, in_range))
                break

        # Add some rational numbers
        for _ in range(3):
            val = rng.randint(1, 10) + rng.choice([0, 0.25, 0.5, 0.75])
            in_range = low_bound < val < high_bound
            display = str(val) if val != int(val) else str(int(val))
            # Avoid duplicates
            if display not in [o[0] for o in options]:
                options.append((display, val, in_range))

        rng.shuffle(options)

        # A multiple-select item carries 2-4 correct answers. Top up
        # whichever side is short by replacing entries from the other side
        # (a single-correct MS reads as a broken multiple-choice item).
        def _display_used(disp):
            return disp in [o[0] for o in options]

        def _make_in_range_entry():
            for _ in range(100):
                n = rng.randint(2, 99)
                if n in PERFECT_SQUARES:
                    continue
                v = math.sqrt(n)
                if low_bound < v < high_bound and not _display_used(f"\u221A{n}"):
                    return (f"\u221A{n}", v, True)
            mid = (low_bound + high_bound) / 2
            disp = f"{mid:g}"
            return None if _display_used(disp) else (disp, mid, True)

        def _make_out_range_entry():
            for _ in range(100):
                v = high_bound + rng.randint(1, 6) + rng.choice([0, 0.5])
                disp = str(v) if v != int(v) else str(int(v))
                if not _display_used(disp):
                    return (disp, v, False)
            return None

        for _ in range(4):
            n_correct = sum(1 for _, _, c in options if c)
            if n_correct < 2:
                entry = _make_in_range_entry()
                idxs = [i for i, o in enumerate(options) if not o[2]]
            elif len(options) - n_correct < 2:
                entry = _make_out_range_entry()
                idxs = [i for i, o in enumerate(options) if o[2]]
            else:
                break
            if entry is None or not idxs:
                break
            options[rng.choice(idxs)] = entry

        choices = []
        for i, (display, val, in_range) in enumerate(options[:6]):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=display,
                text_latex=f"${display}$",
                is_correct=in_range,
            ))

        correct_letters = sorted([c.key for c in choices if c.is_correct])
        answer_str = ", ".join(correct_letters) if correct_letters else "none"

        low_str = str(low_bound) if low_bound != int(low_bound) else str(int(low_bound))
        high_str = str(high_bound) if high_bound != int(high_bound) else str(int(high_bound))

        stem_text = (
            f"Select all numbers that are greater than {low_str} "
            f"and less than {high_str}."
        )

        worked_parts = []
        for display, val, in_range in options[:6]:
            approx = f"{val:.3f}" if "\u221A" in display else display
            status = "IN range" if in_range else "NOT in range"
            worked_parts.append(f"- {display} is approximately {approx}: {status}")

        worked = (
            f"We need values between {low_str} and {high_str}.\n\n"
            + "\n".join(worked_parts)
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MS,
                               Difficulty.DIFFICULT, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.MS,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_str, answer_latex=answer_str,
            worked_solution=worked,
            choices=choices, context_scenario="select numbers in range",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At Proficiency - TM (DOK 2, Medium)
    # Compare irrational and rational numbers: true or false
    # e.g., "sqrt(5) > 2" --> True
    # ================================================================

    def stem4_at_tm(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        comparisons = []
        used_statements = set()

        # Generate 4 unique comparison statements
        attempts = 0
        while len(comparisons) < 4 and attempts < 200:
            attempts += 1
            n = rng.choice(MEDIUM_SQRT[:12])
            sqrt_val = math.sqrt(n)
            lower, upper = _sqrt_bounds(n)

            comp_type = rng.choice(["gt_true", "gt_false", "lt_true", "lt_false"])

            if comp_type == "gt_true":
                # sqrt(n) > some number less than sqrt(n)
                rational = lower
                statement = f"\u221A{n} > {rational}"
                is_true = True
            elif comp_type == "gt_false":
                # sqrt(n) > some number greater than sqrt(n)
                rational = upper
                statement = f"\u221A{n} > {rational}"
                is_true = False
            elif comp_type == "lt_true":
                # sqrt(n) < some number greater than sqrt(n)
                rational = upper
                statement = f"\u221A{n} < {rational}"
                is_true = True
            else:
                # sqrt(n) < some number less than sqrt(n)
                rational = lower
                statement = f"\u221A{n} < {rational}"
                is_true = False

            if statement in used_statements:
                continue
            used_statements.add(statement)
            comparisons.append((statement, is_true, n, sqrt_val, rational))

        stem_text = (
            "Select True or False to indicate whether each comparison is true.\n\n"
        )
        for stmt, _, _, _, _ in comparisons:
            stem_text += f"  {stmt}:  [ True ]  [ False ]\n"

        answer_lines = []
        for stmt, is_true, _, _, _ in comparisons:
            answer_lines.append(f"{stmt}: {'True' if is_true else 'False'}")
        answer_text = "; ".join(answer_lines)

        worked_parts = []
        for stmt, is_true, n, sqrt_val, rational in comparisons:
            lower, upper = _sqrt_bounds(n)
            worked_parts.append(
                f"- {stmt}: \u221A{n} is approximately {sqrt_val:.3f} "
                f"(between {lower} and {upper}), so this is "
                f"{'True' if is_true else 'False'}."
            )

        worked = (
            "To compare, find which two consecutive integers each "
            "square root falls between.\n\n"
            + "\n".join(worked_parts)
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.TM,
                               Difficulty.MEDIUM, 4, variant_idx)

        # Plain numerically-labeled number line spanning the whole numbers
        # referenced in the comparisons. No labeled points -- the question
        # never references them, so we show only the labeled ticks.
        all_rationals = [rational for _, _, _, _, rational in comparisons]
        nl_min = max(0, min(all_rationals) - 1)
        nl_max = max(all_rationals) + 1
        ticks = list(range(nl_min, nl_max + 1))

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.TM,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_text, answer_latex=answer_text,
            worked_solution=worked,
            context_scenario="compare irrational and rational numbers",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx,
            render_data={
                "type": "number_line_point",
                "ticks": ticks,
            }
        )

    # ================================================================
    # STEM 5: Above Proficiency - MS (DOK 2, Difficult)
    # Select all expressions with value greater than a given expression
    # e.g., which expressions have value > 3/4 + 2?
    # ================================================================

    def stem5_above_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        # Generate a target value (rational)
        target_whole = rng.randint(2, 5)
        target_frac = rng.choice([Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)])
        target_val = float(target_whole + target_frac)
        if target_frac == 0:
            target_display = str(target_whole)
        else:
            target_display = f"{target_whole} + {target_frac.numerator}/{target_frac.denominator}"

        # Generate 5 expressions mixing sqrts, pi, and rationals
        expressions = []

        # Expression type 1: rational + sqrt (retry on display collision so
        # the two entries are never identical)
        for _ in range(2):
            for _attempt in range(20):
                rational_part = rng.choice([0.5, 1.0, 1.5, 2.0, 2.5, 0.25, 0.75])
                n = rng.choice([2, 3, 5, 7, 10, 11, 13])
                val = rational_part + math.sqrt(n)
                r_display = str(rational_part) if rational_part != int(rational_part) else str(int(rational_part))
                display = f"{r_display} + \u221A{n}"
                if display not in [d for d, _, _ in expressions]:
                    break
            is_greater = val > target_val
            expressions.append((display, val, is_greater))

        # Expression type 2: integer - decimal
        int_part = rng.randint(3, 7)
        dec_part = rng.choice([0.3, 0.5, 0.7, 1.2, 1.5])
        val = int_part - dec_part
        display = f"{int_part} - {dec_part}"
        is_greater = val > target_val
        expressions.append((display, val, is_greater))

        # Expression type 3: pi + or - something
        pi_offset = rng.choice([-1.0, -0.5, 0, 0.5, 1.0])
        val = math.pi + pi_offset
        if pi_offset > 0:
            display = f"\u03C0 + {pi_offset}" if pi_offset != int(pi_offset) else f"\u03C0 + {int(pi_offset)}"
        elif pi_offset < 0:
            display = f"\u03C0 - {abs(pi_offset)}" if abs(pi_offset) != int(abs(pi_offset)) else f"\u03C0 - {int(abs(pi_offset))}"
        else:
            display = "\u03C0"
        is_greater = val > target_val
        expressions.append((display, val, is_greater))

        # Expression type 4: a whole number
        wn = rng.randint(1, 7)
        val = float(wn)
        display = str(wn)
        is_greater = val > target_val
        expressions.append((display, val, is_greater))

        rng.shuffle(expressions)

        # Guard MS integrity: a multiple-select item needs at least 2 correct
        # AND at least 2 incorrect options (a single-correct MS reads as a
        # broken multiple-choice item on the worksheet).
        for _ in range(3):
            n_greater = sum(1 for _, _, g in expressions if g)
            existing = {d for d, _, _ in expressions}
            if n_greater < 2:
                wn = target_whole + 2   # guaranteed > target
                while str(wn) in existing:
                    wn += 1
                replacement = (str(wn), float(wn), True)
                idxs = [i for i, e in enumerate(expressions) if not e[2]]
            elif len(expressions) - n_greater < 2:
                wn = max(1, target_whole - 2)   # guaranteed < target
                while str(wn) in existing and wn > 1:
                    wn -= 1
                if str(wn) in existing:
                    break
                replacement = (str(wn), float(wn), False)
                idxs = [i for i, e in enumerate(expressions) if e[2]]
            else:
                break
            if not idxs:
                break
            expressions[rng.choice(idxs)] = replacement

        choices = []
        for i, (display, val, is_greater) in enumerate(expressions):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=display,
                text_latex=f"${display}$",
                is_correct=is_greater,
            ))

        correct_letters = sorted([c.key for c in choices if c.is_correct])
        answer_str = ", ".join(correct_letters) if correct_letters else "none"

        stem_text = (
            f"Select all the expressions that have a value greater than "
            f"{target_display}."
        )

        worked_parts = []
        worked_parts.append(f"Target value: {target_display} = {target_val}")
        for display, val, is_greater in expressions:
            status = "GREATER" if is_greater else "NOT greater"
            worked_parts.append(f"- {display} is approximately {val:.3f}: {status}")

        worked = "\n".join(worked_parts)

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MS,
                               Difficulty.DIFFICULT, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.MS,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_str, answer_latex=answer_str,
            worked_solution=worked,
            choices=choices, context_scenario="compare irrational expressions",
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
            self.stem3_approaching_ms,
            self.stem4_at_tm,
            self.stem5_above_ms,
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
            3: self.stem3_approaching_ms,
            4: self.stem4_at_tm,
            5: self.stem5_above_ms,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-5.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 8.NS.2 question variants...")
    gen = Stem8NS2(seed=42)
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
