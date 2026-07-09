"""
Stem generator for 8.AF.2:
  Generate linear equations in one variable with one solution,
  infinitely many solutions, or no solutions. Justify the classification.

Content Limits:
  - No function notation
  - May require simplification on one or both sides
  - Variables may appear on both sides (simplify only, not solve)
  - Calculator: ALLOWED

5 Stems:
  Stem 1 (Below-MC):        Given simplified equation, classify (DOK 1, Easy)
  Stem 2 (Approaching-MS):  Select all equations with one solution (DOK 1, Easy)
  Stem 3 (At-MC):           Find value so equation has infinite solutions (DOK 2, Medium)
  Stem 4 (At-MS):           Select equations with no solution (needs distribution) (DOK 2, Medium)
  Stem 5 (Above-MP):        Analyze claim about solutions, agree/disagree + justify (DOK 3, Difficult)
"""

import random
from fractions import Fraction

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.models import (
    GeneratedQuestion, QuestionPart,
    Difficulty, ProficiencyLevel, ItemType,
    make_question_id
)
from engine.number_generators import NumberGenerator
from engine.distractor_engine import shuffle_choices
from engine.context_pools import pick_name


STANDARD_CODE = "8.AF.2"
VARIANTS_PER_STEM = 20


def _fmt(val: Fraction) -> str:
    if val.denominator == 1:
        return str(int(val))
    av = abs(val)
    if av > 1:
        whole = int(av)
        remainder = av - whole
        if remainder == 0:
            return ("-" if val < 0 else "") + str(whole)
        sign = "-" if val < 0 else ""
        return f"{sign}{whole} {remainder.numerator}/{remainder.denominator}"
    if val < 0:
        return f"-{av.numerator}/{av.denominator}"
    return f"{val.numerator}/{val.denominator}"


def _fmt_linear(coeff: Fraction, const: Fraction, var: str = "x") -> str:
    """Format coeff*x + const as a string."""
    parts = []
    if coeff == 1:
        parts.append(var)
    elif coeff == -1:
        parts.append(f"-{var}")
    elif coeff != 0:
        parts.append(f"{_fmt(coeff)}{var}")
    if const > 0:
        parts.append(f"+ {_fmt(const)}")
    elif const < 0:
        parts.append(f"- {_fmt(abs(const))}")
    return " ".join(parts) if parts else "0"


def _fmt_combined_rhs(c1, k1, c2, k2, var="x"):
    """Format two linear expressions combined: 'c1*x + k1 + c2*x + k2'.

    Handles signs properly so we never get '+ -3' or similar.
    """
    # Start with the first term group
    result = _fmt_linear(c1, k1, var)
    # Append second coefficient term
    if c2 == 1:
        result += f" + {var}"
    elif c2 == -1:
        result += f" - {var}"
    elif c2 > 0:
        result += f" + {_fmt(c2)}{var}"
    elif c2 < 0:
        result += f" - {_fmt(abs(c2))}{var}"
    # Append second constant term
    if k2 > 0:
        result += f" + {_fmt(k2)}"
    elif k2 < 0:
        result += f" - {_fmt(abs(k2))}"
    return result


def _make_equation_str(lc, lk, rc, rk, var="x"):
    """Build 'lc*x + lk = rc*x + rk' string."""
    return f"{_fmt_linear(lc, lk, var)} = {_fmt_linear(rc, rk, var)}"


def _classify(lc, lk, rc, rk):
    """Classify equation lc*x + lk = rc*x + rk."""
    if lc == rc:
        return "infinite" if lk == rk else "none"
    return "one"


class Stem8AF2:
    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below - MC (DOK 1, Easy)
    # Given a simplified equation, classify its number of solutions.
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        solution_type = rng.choice(["one", "infinite", "none"])

        if solution_type == "one":
            x_val = rng.randint(-10, 10)
            while x_val == 0:
                x_val = rng.randint(-10, 10)
            simplified = f"x = {x_val}"
            explanation = f"The equation simplifies to x = {x_val}, which has exactly one solution."
        elif solution_type == "infinite":
            c = rng.randint(1, 20)
            simplified = f"{c} = {c}"
            explanation = f"Both sides are equal ({c} = {c}), so the equation is true for all values of x. It has infinitely many solutions."
        else:
            c1 = rng.randint(1, 15)
            c2 = rng.randint(1, 15)
            while c2 == c1:
                c2 = rng.randint(1, 15)
            simplified = f"{c1} = {c2}"
            explanation = f"The equation simplifies to {c1} = {c2}, which is false. There is no solution."

        correct_label = {
            "one": "One solution",
            "infinite": "Infinitely many solutions",
            "none": "No solution",
        }[solution_type]

        distractors = [v for k, v in {
            "one": "One solution",
            "infinite": "Infinitely many solutions",
            "none": "No solution",
        }.items() if k != solution_type]
        distractors.append("Cannot be determined")

        stem_text = (
            f"How many solutions does the following equation have?\n\n"
            f"{simplified}"
        )

        choices = shuffle_choices(correct_label, correct_label, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct_label}",
            answer_latex=f"{correct_letter}) {correct_label}",
            worked_solution=explanation, choices=choices,
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Approaching - MS (DOK 1, Easy)
    # Select all equations with one solution (no simplification needed).
    # ================================================================

    def stem2_approaching_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        # Generate 5 equations: mix of one/infinite/none
        equations = []
        types_needed = ["one", "one", "infinite", "none", rng.choice(["one", "none"])]
        rng.shuffle(types_needed)

        for sol_type in types_needed:
            lc, lk, rc, rk = gen.equation_solution_type(sol_type)
            eq_str = _make_equation_str(lc, lk, rc, rk)
            actual = _classify(lc, lk, rc, rk)
            equations.append((eq_str, actual))

        # Build choices
        from engine.models import QuestionChoice
        choices = []
        keys = "abcde"
        correct_keys = []
        for i, (eq_str, actual) in enumerate(equations):
            is_correct = (actual == "one")
            choices.append(QuestionChoice(
                key=keys[i], text=eq_str, text_latex=eq_str,
                is_correct=is_correct,
            ))
            if is_correct:
                correct_keys.append(keys[i])

        correct_str = ", ".join(correct_keys)

        stem_text = "Select all equations that have exactly one solution."

        worked_parts = []
        for eq_str, actual in equations:
            label = {"one": "one solution", "infinite": "infinitely many solutions",
                     "none": "no solution"}[actual]
            worked_parts.append(f"{eq_str} -> {label}")
        worked = "\n".join(worked_parts)

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MS,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MS,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_str,
            answer_latex=correct_str,
            worked_solution=worked, choices=choices,
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: At - MC (DOK 2, Medium)
    # Find value of a so equation has infinitely many solutions.
    # ================================================================

    def stem3_at_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        # Equation: a(px + q) = rx + s
        # For infinite solutions: a*p = r and a*q = s  =>  a = r/p and s = a*q
        p = Fraction(rng.randint(1, 5))
        q = Fraction(rng.randint(-8, 8))
        while q == 0:
            q = Fraction(rng.randint(-8, 8))
        a_correct = Fraction(rng.randint(2, 6))
        r = a_correct * p
        s = a_correct * q

        correct = _fmt(a_correct)

        # Distractors
        distractors = []
        for offset in [-1, 1, 2]:
            val = a_correct + offset
            if val != a_correct and val != 0:
                distractors.append(_fmt(val))
        while len(distractors) < 3:
            v = Fraction(rng.randint(1, 10))
            if _fmt(v) != correct and _fmt(v) not in distractors:
                distractors.append(_fmt(v))
        distractors = distractors[:3]

        inner = f"{_fmt(p)}x" + (f" + {_fmt(q)}" if q > 0 else f" - {_fmt(abs(q))}")
        rhs = f"{_fmt(r)}x" + (f" + {_fmt(s)}" if s > 0 else f" - {_fmt(abs(s))}")

        stem_text = (
            f"An equation with a missing value a is given.\n\n"
            f"a({inner}) = {rhs}\n\n"
            f"Enter the value of a so the equation has infinitely many solutions."
        )

        choices = shuffle_choices(correct, correct, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"For infinitely many solutions, both sides must be identical.\n"
            f"Distribute a: a*{_fmt(p)}x + a*{_fmt(q)} = {_fmt(r)}x + {_fmt(s)}\n"
            f"Match coefficients: a*{_fmt(p)} = {_fmt(r)} => a = {_fmt(a_correct)}\n"
            f"Check constants: {_fmt(a_correct)}*{_fmt(q)} = {_fmt(s)} (true)"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MC,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{correct_letter}) a = {correct}",
            answer_latex=f"{correct_letter}) a = {correct}",
            worked_solution=worked, choices=choices,
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At - MS (DOK 2, Medium)
    # Select equations with no solution (needs distribution).
    # ================================================================

    def stem4_at_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        from engine.models import QuestionChoice

        # Generate 5 equations with distribution, 2 have no solution
        target_types = ["none", "none", "one", "infinite", rng.choice(["one", "infinite"])]
        rng.shuffle(target_types)

        equations = []
        for sol_type in target_types:
            # Build equation with distribution: p(qx + r) = sx + t
            p = Fraction(rng.randint(2, 6))
            q = Fraction(rng.randint(1, 4))
            r = Fraction(rng.randint(-6, 6))
            while r == 0:
                r = Fraction(rng.randint(-6, 6))

            if sol_type == "infinite":
                s = p * q
                t = p * r
            elif sol_type == "none":
                s = p * q
                t = p * r + rng.choice([-3, -2, -1, 1, 2, 3])
            else:
                s = p * q + rng.choice([-2, -1, 1, 2])
                t = Fraction(rng.randint(-10, 10))

            # Format: p(qx + r) = sx + t
            inner = f"{_fmt(q)}x" + (f" + {_fmt(r)}" if r > 0 else f" - {_fmt(abs(r))}")
            rhs = _fmt_linear(s, t)
            eq_str = f"{_fmt(p)}({inner}) = {rhs}"

            # Verify classification
            lc = p * q
            lk = p * r
            actual = _classify(lc, lk, s, t)
            equations.append((eq_str, actual))

        choices = []
        keys = "abcde"
        correct_keys = []
        for i, (eq_str, actual) in enumerate(equations):
            is_correct = (actual == "none")
            choices.append(QuestionChoice(
                key=keys[i], text=eq_str, text_latex=eq_str,
                is_correct=is_correct,
            ))
            if is_correct:
                correct_keys.append(keys[i])

        correct_str = ", ".join(correct_keys)

        stem_text = "Select all equations that have no solution."

        worked_parts = []
        for eq_str, actual in equations:
            label = {"one": "one solution", "infinite": "infinitely many",
                     "none": "no solution"}[actual]
            worked_parts.append(f"{eq_str} -> {label}")
        worked = "\n".join(worked_parts)

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MS,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MS,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_str, answer_latex=correct_str,
            worked_solution=worked, choices=choices,
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above - MP (DOK 3, Difficult)
    # Analyze claim about solutions, agree/disagree + justify.
    # ================================================================

    def stem5_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        name = pick_name(rng)

        # Varied scenarios: claim may be correct or incorrect
        scenario = rng.choice([
            ("no", "infinite"),   # claim wrong
            ("no", "one"),        # claim wrong
            ("one", "infinite"),  # claim wrong
            ("one", "none"),      # claim wrong
            ("infinite", "one"),  # claim wrong
            ("infinite", "none"), # claim wrong
            ("no", "none"),       # claim correct
            ("one", "one"),       # claim correct
            ("infinite", "infinite"),  # claim correct
        ])
        claim_type, actual_type = scenario
        should_agree = (claim_type == actual_type)

        claim_labels = {
            "no": "no solutions",
            "one": "exactly one solution",
            "infinite": "infinitely many solutions",
        }
        actual_labels = {
            "none": "no solution",
            "one": "exactly one solution",
            "infinite": "infinitely many solutions",
        }

        # --- Build the equation ---
        # Use distribution on LHS, combined terms on RHS for complexity
        p = Fraction(rng.randint(2, 6))
        q = Fraction(rng.randint(2, 5))
        r = Fraction(rng.randint(1, 8)) * rng.choice([1, -1])

        pq = p * q
        pr = p * r

        if actual_type == "infinite":
            # Both sides simplify to the same expression
            # RHS: split pq*x + pr into multiple terms
            s1 = Fraction(rng.randint(1, max(1, int(pq) - 1)))
            s2 = pq - s1
            t1 = Fraction(rng.randint(1, max(1, abs(int(pr)))))
            if pr < 0:
                t1 = -t1
            t2 = pr - t1
            rhs = _fmt_combined_rhs(s1, t1, s2, t2)
            simplified_rhs = _fmt_linear(pq, pr)
        elif actual_type == "none":
            # Same x-coefficient, different constant
            offset = Fraction(rng.choice([-4, -3, -2, -1, 1, 2, 3, 4]))
            use_split = rng.choice([True, False])
            if use_split:
                s1 = Fraction(rng.randint(1, max(1, int(pq) - 1)))
                s2 = pq - s1
                wrong_const = pr + offset
                t1 = Fraction(rng.randint(-5, 5))
                t2 = wrong_const - t1
                rhs = _fmt_combined_rhs(s1, t1, s2, t2)
            else:
                rhs = _fmt_linear(pq, pr + offset)
            simplified_rhs = _fmt_linear(pq, pr + offset)
        else:  # one solution
            x_offset = Fraction(rng.choice([-3, -2, -1, 1, 2, 3]))
            rhs_const = Fraction(rng.randint(-10, 10))
            use_split = rng.choice([True, False])
            if use_split:
                new_coeff = pq + x_offset
                s1 = Fraction(rng.randint(1, max(1, int(abs(new_coeff)) - 1) if abs(new_coeff) > 1 else 2))
                if new_coeff < 0:
                    s1 = -s1
                s2 = new_coeff - s1
                t1 = Fraction(rng.randint(-5, 5))
                t2 = rhs_const - t1
                rhs = _fmt_combined_rhs(s1, t1, s2, t2)
            else:
                rhs = _fmt_linear(pq + x_offset, rhs_const)
            simplified_rhs = _fmt_linear(pq + x_offset, rhs_const)

        lhs = f"{_fmt(p)}({_fmt_linear(q, r)})"
        simplified_lhs = _fmt_linear(pq, pr)
        eq_str = f"{lhs} = {rhs}"

        # Build answer
        claim_text = claim_labels[claim_type]
        actual_text = actual_labels[actual_type]
        agree_word = "Agree" if should_agree else "Disagree"

        if should_agree:
            answer = f"Agree. The equation has {actual_text}."
        else:
            answer = f"Disagree. The equation has {actual_text}, not {claim_labels[claim_type]}."

        stem_text = (
            f"{name} states that the equation below has {claim_text}.\n\n"
            f"{eq_str}\n\n"
            f"Part A: Do you agree or disagree with {name}?\n\n"
            f"Part B: Justify your answer. Show your work."
        )

        part_a = QuestionPart(
            label="Part A",
            prompt=f"Do you agree or disagree with {name}?",
            prompt_latex=f"Do you agree or disagree with {name}?",
            answer=agree_word,
            answer_latex=agree_word,
            item_type=ItemType.MC,
        )

        part_b = QuestionPart(
            label="Part B",
            prompt="Justify your answer. Show your work.",
            prompt_latex="Justify your answer. Show your work.",
            answer=f"The equation simplifies to {simplified_lhs} = {simplified_rhs}. This has {actual_text}.",
            answer_latex=f"The equation simplifies to {simplified_lhs} = {simplified_rhs}. This has {actual_text}.",
            item_type=ItemType.ER,
        )

        worked = (
            f"Distribute LHS: {simplified_lhs}\n"
            f"Simplify RHS: {simplified_rhs}\n"
            f"The equation has {actual_text}, so {agree_word.lower()} with {name}."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.DIFFICULT, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=worked, parts=[part_a, part_b],
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    # MAIN GENERATION METHOD
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_approaching_ms,
            self.stem3_at_mc,
            self.stem4_at_ms,
            self.stem5_above_mp,
        ]
        for stem_fn in stem_methods:
            for v in range(variants_per_stem):
                all_questions.append(stem_fn(v))
        return all_questions

    def generate_stem_variants(self, stem_index: int,
                               variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        stem_methods = {
            1: self.stem1_below_mc,
            2: self.stem2_approaching_ms,
            3: self.stem3_at_mc,
            4: self.stem4_at_ms,
            5: self.stem5_above_mp,
        }
        fn = stem_methods[stem_index]
        return [fn(v) for v in range(variants_per_stem)]
