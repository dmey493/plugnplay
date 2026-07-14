"""
Stem generator for 7.AF.4:
  Solve inequalities of the form px + q (> or >=) r or px + q (< or <=) r,
  where p, q, and r are specific rational numbers. Represent real-world problems
  using inequalities and solve. Graph the solution set on a number line.

Content Limits:
  - Rational numbers only
  - Decimals to the hundredths
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: whole numbers only
  Medium: integers or decimals to the tenths
  Difficult: rational numbers (fractions, 2-place decimals)

6 Stems from the Item Spec:
  Stem 1 (Below-MC):      Which value makes px + q > r true? (DOK 1, Easy)
  Stem 2 (Below-MC):      Choose number line graph of solution (DOK 2, Easy)
  Stem 3 (Approaching-MS): Select all values in solution set (DOK 2, Medium)
  Stem 4 (Approaching-MC): Solve inequality with negatives, may flip sign (DOK 2, Medium)
  Stem 5 (At-MP):         Real-world inequality: write + solve + interpret (DOK 2, Medium)
  Stem 6 (Above-MP):      Critique student's reasoning + write inequality (DOK 3, Easy)
"""

import random
from fractions import Fraction
from typing import Optional

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.models import (
    GeneratedQuestion, QuestionChoice, QuestionPart,
    Difficulty, ProficiencyLevel, ItemType, RationalNumber,
    make_question_id
)
from engine.number_generators import NumberGenerator
from engine.distractor_engine import shuffle_choices
from engine.context_pools import (
    CONTEXTS_7AF4_INEQUALITY, CONTEXTS_7AF4_INEQUALITY_SUB, pick_name
)


STANDARD_CODE = "7.AF.4"
VARIANTS_PER_STEM = 20

# Unicode inequality symbols
GE = "\u2265"  # >=
LE = "\u2264"  # <=

OP_DISPLAY = {">": ">", "<": "<", ">=": GE, "<=": LE}
OP_FLIP = {">": "<", "<": ">", ">=": "<=", "<=": ">="}
OP_WORDS = {">": "greater than", "<": "less than",
            ">=": "greater than or equal to", "<=": "less than or equal to"}


def _fmt(val: Fraction) -> str:
    """Format a number for display (improper fractions, no mixed)."""
    if val.denominator == 1:
        return str(int(val))
    if val < 0:
        return f"-{abs(val).numerator}/{abs(val).denominator}"
    return f"{val.numerator}/{val.denominator}"


def _fmt_dec(val: Fraction) -> str:
    """Format a number as a decimal (for money / dollar contexts)."""
    f = float(val)
    if f == int(f):
        return str(int(f))
    # Use 2 decimal places for money, strip trailing zeros but keep at least 1
    s = f"{f:.2f}"
    return s


def _fmt_num(val: Fraction) -> str:
    """Format a rational as a clean decimal, stripping trailing zeros.

    Used for the approaching-proficiency stems whose 1-place decimal
    coefficients would otherwise reduce to ugly improper fractions like
    312/5 instead of reading as the intended 62.4.
    """
    f = float(val)
    if f == int(f):
        return str(int(f))
    return f"{f:.4f}".rstrip("0").rstrip(".")


def _is_in_solution(x_val: Fraction, boundary: Fraction, op: str) -> bool:
    """Check if x_val is in the solution set for x {op} boundary."""
    if op == ">":
        return x_val > boundary
    elif op == "<":
        return x_val < boundary
    elif op == ">=":
        return x_val >= boundary
    elif op == "<=":
        return x_val <= boundary
    return False


class Stem7AF4:
    """Generates ~20 variants for each of 6 stems from the 7.AF.4 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        """Create a seeded NumberGenerator for a specific stem+variant."""
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - Multiple Choice (DOK 1, Easy)
    # "6x + 4 > 28. Which value for x makes it true?"
    # Student tests by substitution.
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Below Proficiency - Which value makes the inequality true?

        Student tests values by substitution into px + q > r.
        Difficulty: easy (whole numbers)
        """
        gen, rng = self._make_gen(1, variant_idx)

        op = rng.choice([">", "<", ">=", "<="])
        op_disp = OP_DISPLAY[op]

        # Generate px + q {op} r with clean boundary
        p = int(gen.small_whole(2, 8))
        q = int(gen.integer_coefficient(1, 20))
        # Pick boundary so x is a small whole number
        boundary = int(gen.whole_number(2, 10))
        r = p * boundary + q

        # The actual inequality: px + q {op} r => x {op} boundary
        # Generate 4 candidate values: 1 correct, 3 wrong
        # Correct: value that satisfies x {op} boundary
        if op in [">", ">="]:
            correct_val = boundary + rng.randint(1, 5)
            wrong_vals = [boundary - rng.randint(1, 3)]
            # boundary itself: wrong for >, correct for >=
            if op == ">":
                wrong_vals.append(boundary)
            else:
                correct_val = boundary  # use boundary as correct for >=
                wrong_vals = [boundary - rng.randint(1, 3)]
                # Also add a clearly correct one
                alt_correct = boundary + rng.randint(1, 4)
            wrong_vals.extend([boundary - rng.randint(2, 5), boundary - rng.randint(1, 4)])
        else:  # < or <=
            correct_val = boundary - rng.randint(1, 5)
            if correct_val < 0:
                correct_val = max(0, boundary - 1)
            wrong_vals = [boundary + rng.randint(1, 3)]
            if op == "<":
                wrong_vals.append(boundary)
            else:
                correct_val = boundary  # use boundary for <=
                wrong_vals = [boundary + rng.randint(1, 3)]
            wrong_vals.extend([boundary + rng.randint(2, 5), boundary + rng.randint(1, 4)])

        # Ensure uniqueness and exactly 3 wrong values
        wrong_set = {w for w in wrong_vals if w != correct_val and w >= 0}
        attempts = 0
        while len(wrong_set) < 3 and attempts < 200:
            attempts += 1
            extra = rng.randint(0, boundary + 10)
            if extra != correct_val and not _is_in_solution(Fraction(extra), Fraction(boundary), op):
                wrong_set.add(extra)
        # If still short (boundary too small for 3 unique wrong values),
        # add nearby values that aren't the correct answer
        fallback = boundary + 11
        while len(wrong_set) < 3:
            if fallback != correct_val:
                wrong_set.add(fallback)
            fallback += 1
        wrong_list = list(wrong_set)[:3]

        # Format inequality text
        ineq_text = f"{p}x + {q} {op_disp} {r}" if q >= 0 else f"{p}x - {abs(q)} {op_disp} {r}"

        stem_text = (
            f"An inequality is given.\n\n"
            f"  {ineq_text}\n\n"
            f"Which value for x will make the inequality true?"
        )

        correct_str = str(correct_val)
        distractor_strs = [str(w) for w in wrong_list]

        choices = shuffle_choices(correct_str, correct_str, distractor_strs, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        # Verify
        lhs = p * correct_val + q
        check = _is_in_solution(Fraction(lhs), Fraction(r), op.replace("=", ""))
        # For >= and <=, check with equality too
        if op in [">=", "<="]:
            if op == ">=":
                check = lhs >= r
            else:
                check = lhs <= r

        worked = (
            f"Solve: {ineq_text}\n"
            f"  {p}x {op_disp} {r - q}\n"
            f"  x {op_disp} {boundary}\n"
            f"Check x = {correct_val}: {p}({correct_val}) + {q} = {p * correct_val + q} {op_disp} {r} is true."
        )

        # Blank number line for students to graph the solution
        circle_type = "open" if op in [">", "<"] else "closed"
        nl_direction = "right" if op in [">", ">="] else "left"
        nl_render = {
            "type": "number_line",
            "value": float(boundary),
            "circle_type": circle_type,
            "direction": nl_direction,
            "blank": True,
        }

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
            answer_text=f"{correct_letter}) {correct_str}",
            answer_latex=f"{correct_letter}) {correct_str}",
            worked_solution=worked,
            choices=choices,
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1,
            variant_index=variant_idx,
            render_data=nl_render,
        )

    # ================================================================
    # STEM 2: Below Proficiency - Multiple Choice (DOK 2, Easy)
    # "Choose the graph that represents the solution to px + q < r."
    # Number line choices with open/closed circles and arrows.
    # ================================================================

    def stem2_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Below Proficiency - Select number line graph of solution.

        Student solves the inequality and selects the correct number line.
        Uses render_data for SVG number lines.
        Difficulty: easy (whole numbers)
        """
        gen, rng = self._make_gen(2, variant_idx)

        op = rng.choice([">", "<", ">=", "<="])
        op_disp = OP_DISPLAY[op]

        p = int(gen.small_whole(2, 8))
        boundary = int(gen.whole_number(1, 8))
        q = int(gen.integer_coefficient(1, 15))
        r = p * boundary + q

        # Solution: x {op} boundary
        # Circle type: open for strict (>, <), closed for non-strict (>=, <=)
        circle_type = "open" if op in [">", "<"] else "closed"
        direction = "right" if op in [">", ">="] else "left"

        # Correct number line
        correct_rd = {
            "type": "number_line",
            "value": float(boundary),
            "circle_type": circle_type,
            "direction": direction
        }

        # Wrong number lines
        wrong_rds = []
        # Wrong 1: correct value, wrong direction
        wrong_rds.append({
            "type": "number_line",
            "value": float(boundary),
            "circle_type": circle_type,
            "direction": "left" if direction == "right" else "right"
        })
        # Wrong 2: correct value, wrong circle type
        wrong_rds.append({
            "type": "number_line",
            "value": float(boundary),
            "circle_type": "closed" if circle_type == "open" else "open",
            "direction": direction
        })
        # Wrong 3: wrong value
        wrong_boundary = boundary + rng.choice([1, -1, 2])
        if wrong_boundary < 0:
            wrong_boundary = boundary + 2
        wrong_rds.append({
            "type": "number_line",
            "value": float(wrong_boundary),
            "circle_type": circle_type,
            "direction": direction
        })

        # Build choices
        ineq_text = f"{p}x + {q} {op_disp} {r}" if q >= 0 else f"{p}x - {abs(q)} {op_disp} {r}"

        # Describe number lines in text (for PDF fallback)
        def _describe_nl(rd):
            ct = "closed" if rd["circle_type"] == "closed" else "open"
            dr = rd["direction"]
            return f"{ct} circle at {rd['value']}, arrow {dr}"

        correct_desc = _describe_nl(correct_rd)
        wrong_descs = [_describe_nl(w) for w in wrong_rds]

        all_options = [(correct_desc, correct_rd, True)]
        for i, (desc, rd) in enumerate(zip(wrong_descs, wrong_rds)):
            all_options.append((desc, rd, False))

        rng.shuffle(all_options)

        choices = []
        for i, (text, rd, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i),
                text=text,
                text_latex=text,
                is_correct=is_correct,
                render_data=rd,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = (
            f"An inequality is given.\n\n"
            f"  {ineq_text}\n\n"
            f"Choose the graph that represents the solution to the inequality."
        )

        worked = (
            f"{ineq_text}\n"
            f"{p}x {op_disp} {r} - {q}\n"
            f"{p}x {op_disp} {r - q}\n"
            f"x {op_disp} {boundary}\n"
            f"Graph: {circle_type} circle at {boundary}, arrow pointing {direction}."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY,
            dok=2,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"{correct_letter}) x {op_disp} {boundary}",
            answer_latex=f"{correct_letter}) x {op_disp} {boundary}",
            worked_solution=worked,
            choices=choices,
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - Multiple Select (DOK 2, Medium)
    # "Select ALL values that are solutions to the inequality."
    # ================================================================

    def stem3_approaching_ms(self, variant_idx: int) -> GeneratedQuestion:
        """Approaching Proficiency - Select all solutions from a list.

        Given an inequality, student selects all values from a list
        that satisfy it.
        Difficulty: medium (includes decimals)
        """
        gen, rng = self._make_gen(3, variant_idx)

        op = rng.choice([">", "<", ">=", "<="])
        op_disp = OP_DISPLAY[op]

        # Generate with decimals for medium difficulty
        p = gen.decimal_1place(1.0, 5.0)
        while p == 0:
            p = gen.decimal_1place(1.0, 5.0)
        boundary_int = int(gen.whole_number(3, 15))
        boundary = Fraction(boundary_int)
        q = gen.decimal_1place(0.5, 10.0)
        r = p * boundary + q

        # Generate 5 candidate values: mix of solutions and non-solutions
        candidates = []
        # Some in solution set
        for _ in range(3):
            if op in [">", ">="]:
                offset = gen.decimal_1place(0.5, 5.0)
                val = boundary + offset
            else:
                offset = gen.decimal_1place(0.5, 5.0)
                val = boundary - offset
                if val < 0:
                    val = gen.decimal_1place(0.1, float(boundary) - 0.1)
            candidates.append(val)

        # Some NOT in solution set
        for _ in range(2):
            if op in [">", ">="]:
                offset = gen.decimal_1place(0.5, 5.0)
                val = boundary - offset
                if val < 0:
                    val = Fraction(0)
            else:
                offset = gen.decimal_1place(0.5, 5.0)
                val = boundary + offset
            candidates.append(val)

        # Add boundary itself
        candidates.append(boundary)

        # Deduplicate and limit to 5
        seen = set()
        unique_candidates = []
        for c in candidates:
            if c not in seen and c >= 0:
                seen.add(c)
                unique_candidates.append(c)
        while len(unique_candidates) < 5:
            extra = gen.decimal_1place(0.1, 20.0)
            if extra not in seen:
                seen.add(extra)
                unique_candidates.append(extra)
        unique_candidates = unique_candidates[:5]
        rng.shuffle(unique_candidates)

        # Build choices
        choices = []
        for i, val in enumerate(unique_candidates):
            is_sol = _is_in_solution(val, boundary, op)
            choices.append(QuestionChoice(
                key=chr(ord('a') + i),
                text=_fmt_num(val),
                text_latex=_fmt_num(val),
                is_correct=is_sol,
            ))

        correct_letters = [c.key for c in choices if c.is_correct]
        correct_vals = [c.text for c in choices if c.is_correct]

        p_str = _fmt_num(p)
        q_str = _fmt_num(q)
        r_str = _fmt_num(r)
        ineq_text = f"{p_str}x + {q_str} {op_disp} {r_str}"

        stem_text = (
            f"An inequality is given.\n\n"
            f"  {ineq_text}\n\n"
            f"Select ALL the values that are solutions to this inequality."
        )

        worked = (
            f"Solve: {ineq_text}\n"
            f"  {p_str}x {op_disp} {r_str} - {q_str}\n"
            f"  {p_str}x {op_disp} {_fmt_num(r - q)}\n"
            f"  x {op_disp} {boundary_int}\n"
            f"Solutions: {', '.join(correct_vals)}"
        )

        # Blank number line for students to graph the solution
        circle_type = "open" if op in [">", "<"] else "closed"
        nl_direction = "right" if op in [">", ">="] else "left"
        nl_render = {
            "type": "number_line",
            "value": float(boundary),
            "circle_type": circle_type,
            "direction": nl_direction,
            "blank": True,
        }

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MS,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM,
            dok=2,
            item_type=ItemType.MS,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"{', '.join(correct_letters)}) {'; '.join(correct_vals)}",
            answer_latex=f"{', '.join(correct_letters)}) {'; '.join(correct_vals)}",
            worked_solution=worked,
            choices=choices,
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3,
            variant_index=variant_idx,
            render_data=nl_render,
        )

    # ================================================================
    # STEM 4: Approaching Proficiency - Multiple Choice (DOK 2, Medium)
    # "-3.5x + 7 >= -24.5. What is the solution?"
    # Key concept: dividing by negative flips the inequality sign.
    # ================================================================

    def stem4_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        """Approaching Proficiency - Solve inequality with sign flip.

        Inequality with negative coefficient requiring sign flip when dividing.
        Difficulty: medium (decimals, may include negatives)
        """
        gen, rng = self._make_gen(4, variant_idx)

        op = rng.choice([">=", "<=", ">", "<"])
        op_disp = OP_DISPLAY[op]

        # Generate with negative p to force sign flip
        flip = rng.random() < 0.6  # 60% chance of negative p
        if flip:
            p = -gen.decimal_1place(1.0, 5.0)
        else:
            p = gen.decimal_1place(1.0, 5.0)

        boundary = int(gen.whole_number(2, 12))
        q = gen.decimal_1place(1.0, 15.0) * rng.choice([1, -1])

        r = p * Fraction(boundary) + q

        # Solution: if p < 0, sign flips
        if p < 0:
            solution_op = OP_FLIP[op]
        else:
            solution_op = op

        solution_disp = OP_DISPLAY[solution_op]

        correct = f"x {solution_disp} {boundary}"

        # Distractors
        distractors = []
        # Error 1: forgot to flip sign
        if flip:
            d1 = f"x {op_disp} {boundary}"
            distractors.append(d1)

        # Error 2: wrong boundary
        d2 = f"x {solution_disp} {boundary + rng.choice([1, -1, 2])}"
        if d2 != correct:
            distractors.append(d2)

        # Error 3: flipped when shouldn't (or not when should) + wrong value
        wrong_op = OP_FLIP[solution_op]
        d3 = f"x {OP_DISPLAY[wrong_op]} {boundary + rng.choice([0, 1])}"
        if d3 != correct and d3 not in distractors:
            distractors.append(d3)

        # Error 4: different boundary
        d4 = f"x {solution_disp} {boundary * 2}"
        if d4 != correct and d4 not in distractors:
            distractors.append(d4)

        while len(distractors) < 3:
            wb = boundary + rng.choice([1, -1, 3, -2])
            wo = rng.choice(list(OP_DISPLAY.values()))
            d = f"x {wo} {wb}"
            if d != correct and d not in distractors:
                distractors.append(d)

        distractors = distractors[:3]

        p_str = _fmt_num(p)
        q_str = _fmt_num(abs(q))
        r_str = _fmt_num(r)

        if q >= 0:
            ineq_text = f"{p_str}x + {q_str} {op_disp} {r_str}"
        else:
            ineq_text = f"{p_str}x - {q_str} {op_disp} {r_str}"

        stem_text = (
            f"An inequality is given.\n\n"
            f"  {ineq_text}\n\n"
            f"What is the solution to the inequality?"
        )

        choices = shuffle_choices(correct, correct, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        flip_note = ""
        if flip:
            flip_note = f"\n  (Dividing by negative {p_str} flips the inequality sign)"

        worked = (
            f"{ineq_text}\n"
            f"  {p_str}x {op_disp} {r_str} - ({_fmt_num(q)})\n"
            f"  {p_str}x {op_disp} {_fmt_num(r - q)}\n"
            f"  x {solution_disp} {_fmt_num(r - q)} / {p_str}"
            f"{flip_note}\n"
            f"  x {solution_disp} {boundary}"
        )

        # Blank number line for students to graph the solution
        circle_type = "open" if solution_op in [">", "<"] else "closed"
        nl_direction = "right" if solution_op in [">", ">="] else "left"
        nl_render = {
            "type": "number_line",
            "value": float(boundary),
            "circle_type": circle_type,
            "direction": nl_direction,
            "blank": True,
        }

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM,
            dok=2,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct}",
            answer_latex=f"{correct_letter}) {correct}",
            worked_solution=worked,
            choices=choices,
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4,
            variant_index=variant_idx,
            render_data=nl_render,
        )

    # ================================================================
    # STEM 5: At Proficiency - Multi-Part (DOK 2, Medium)
    # Real-world: Part A write inequality, Part B solve, interpret.
    # ================================================================

    def stem5_at_mp(self, variant_idx: int) -> GeneratedQuestion:
        """At Proficiency - Real-world inequality: write and solve.

        Real-world context leading to px + q {op} r.
        Part A: Write the inequality.
        Part B: Solve and interpret in context.
        Difficulty: medium (decimals)
        """
        gen, rng = self._make_gen(5, variant_idx)

        name = pick_name(rng)

        # Generate clean values with a whole-number boundary.
        p = gen.decimal_1place(1.0, 8.0)          # per-unit amount
        q = gen.decimal_1place(1.0, 20.0)         # flat / threshold amount
        boundary = int(gen.whole_number(3, 15))

        # Half the variants use a subtraction inequality (a - bx {op} c) so the
        # bank isn't limited to addition (ax + b {op} c). Isolating x from -bx
        # flips the inequality sign -- the key skill these variants add.
        use_sub = (variant_idx % 2 == 1)
        if use_sub:
            ctx = rng.choice(CONTEXTS_7AF4_INEQUALITY_SUB)
            var = ctx["var_letter"]
            op = ctx["op"]
            op_disp = OP_DISPLAY[op]
            sol_op = OP_FLIP[op]                   # dividing by -b flips the sign
            sol_disp = OP_DISPLAY[sol_op]
            fmt = _fmt_dec if "$" in ctx["setup"] else _fmt_num
            # a - b*boundary = c, so boundary is the exact critical value.
            b, c = p, q
            a = c + b * Fraction(boundary)
            a_str, b_str, c_str = fmt(a), fmt(b), fmt(c)
            setup_text = ctx["setup"].format(name=name, p=b_str, q=c_str, r=a_str, var=var)
            correct_ineq = f"{a_str} - {b_str}{var} {op_disp} {c_str}"
            sol_text = f"{var} {sol_disp} {boundary}"
            worked = (
                f"Part A: {correct_ineq}\n"
                f"Part B:\n"
                f"  {a_str} - {b_str}{var} {op_disp} {c_str}\n"
                f"  -{b_str}{var} {op_disp} {fmt(c - a)}\n"
                f"  {var} {sol_disp} {boundary}   (dividing by -{b_str} flips the inequality)"
            )
            nl_op = sol_op
        else:
            ctx = rng.choice(CONTEXTS_7AF4_INEQUALITY)
            var = ctx["var_letter"]
            op = ctx["op"]
            op_disp = OP_DISPLAY[op]
            fmt = _fmt_dec if "$" in ctx["setup"] else _fmt
            r = p * Fraction(boundary) + q
            p_str, q_str, r_str = fmt(p), fmt(q), fmt(r)
            setup_text = ctx["setup"].format(name=name, p=p_str, q=q_str, r=r_str, var=var)
            correct_ineq = f"{p_str}{var} + {q_str} {op_disp} {r_str}"
            sol_text = f"{var} {op_disp} {boundary}"
            worked = (
                f"Part A: {correct_ineq}\n"
                f"Part B:\n"
                f"  {p_str}{var} + {q_str} {op_disp} {r_str}\n"
                f"  {p_str}{var} {op_disp} {r_str} - {q_str}\n"
                f"  {p_str}{var} {op_disp} {fmt(r - q)}\n"
                f"  {var} {op_disp} {boundary}"
            )
            nl_op = op

        stem_text = (
            f"{setup_text}\n\n"
            f"Part A: Write an inequality to represent this situation.\n\n"
            f"Part B: Solve the inequality. What does the solution mean in context?"
        )

        part_a = QuestionPart(
            label="Part A",
            prompt="Write an inequality to represent this situation.",
            prompt_latex="Write an inequality to represent this situation.",
            answer=correct_ineq,
            answer_latex=correct_ineq,
            item_type=ItemType.EQ
        )

        part_b = QuestionPart(
            label="Part B",
            prompt="Solve the inequality and interpret.",
            prompt_latex="Solve the inequality and interpret.",
            answer=sol_text,
            answer_latex=sol_text,
            item_type=ItemType.NR
        )

        # Blank number line for students to graph the solution (uses the SOLVED
        # inequality's direction, which is flipped for the subtraction form).
        circle_type = "open" if nl_op in [">", "<"] else "closed"
        nl_direction = "right" if nl_op in [">", ">="] else "left"
        nl_render = {
            "type": "number_line",
            "value": float(boundary),
            "circle_type": circle_type,
            "direction": nl_direction,
            "blank": True,
        }

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MP,
                               Difficulty.MEDIUM, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM,
            dok=2,
            item_type=ItemType.MP,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"Part A: {correct_ineq}; Part B: {sol_text}",
            answer_latex=f"Part A: {correct_ineq}; Part B: {sol_text}",
            worked_solution=worked,
            parts=[part_a, part_b],
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5,
            variant_index=variant_idx,
            render_data=nl_render,
        )

    # ================================================================
    # STEM 6: Above Proficiency - Multi-Part (DOK 3, Easy)
    # Critique student reasoning + write inequality + find valid solution.
    # Rectangle perimeter problem: 2x + 2(x+d) <= P
    # ================================================================

    def stem6_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        """Above Proficiency - Critique reasoning and write inequality.

        Perimeter constraint on a rectangle. Student critiques a claim,
        writes the inequality, and selects valid dimensions.
        Difficulty: easy (whole numbers)
        """
        gen, rng = self._make_gen(6, variant_idx)

        # Rectangle: length = width + d
        d = int(gen.small_whole(2, 8))
        max_perimeter = int(gen.whole_number(40, 100))
        # Make max_perimeter divisible by 4 for clean math
        max_perimeter = (max_perimeter // 4) * 4

        op = rng.choice(["<=", "<"])
        op_disp = OP_DISPLAY[op]
        op_word = "no more than" if op == "<=" else "less than"

        # Perimeter = 2w + 2(w + d) = 4w + 2d
        # So 4w + 2d {op} max_perimeter
        # w {op} (max_perimeter - 2d) / 4
        boundary_num = max_perimeter - 2 * d
        boundary = Fraction(boundary_num, 4)

        # Student claims w = some_val. Choose one that's too large.
        too_large = int(boundary) + rng.randint(2, 5)
        too_large_perim = 2 * too_large + 2 * (too_large + d)

        # Generate valid dimensions for Part C
        valid_w = int(boundary) - rng.randint(1, 3)
        if valid_w < 1:
            valid_w = 1
        valid_l = valid_w + d
        valid_perim = 2 * valid_w + 2 * valid_l

        # Also generate wrong dimension options
        wrong_dims = []
        for _ in range(3):
            ww = int(boundary) + rng.randint(1, 5)
            wl = ww + d
            wp = 2 * ww + 2 * wl
            if wp > max_perimeter:
                wrong_dims.append((ww, wl))
            elif (ww, wl) != (valid_w, valid_l):
                wrong_dims.append((ww, wl))

        while len(wrong_dims) < 3:
            ww = int(boundary) + rng.randint(2, 8)
            wl = ww + d
            wrong_dims.append((ww, wl))
        wrong_dims = wrong_dims[:3]

        # Is the student correct?
        is_reasonable = too_large_perim <= max_perimeter if op == "<=" else too_large_perim < max_perimeter
        reason_word = "is" if is_reasonable else "is not"
        comparison = "less than" if too_large_perim < max_perimeter else "more than" if too_large_perim > max_perimeter else "equal to"

        stem_text = (
            f"The length of a rectangular yard is {d} yards more than the width. "
            f"The yard has a fence around it. {op_word.title()} {max_perimeter} yards "
            f"of fence is needed to go around the entire perimeter.\n\n"
            f"Part A: A student says the width could be {too_large} yards. "
            f"Is this reasonable? Explain.\n\n"
            f"Part B: Write an inequality to represent this problem.\n\n"
            f"Part C: What is a possible set of dimensions for the yard?"
        )

        part_a = QuestionPart(
            label="Part A",
            prompt=f"Is a width of {too_large} yards reasonable?",
            prompt_latex=f"Is a width of {too_large} yards reasonable?",
            answer=f"{too_large} yards {reason_word} reasonable because the perimeter would be {too_large_perim} yards, which is {comparison} {max_perimeter} yards.",
            answer_latex=f"{too_large} yards {reason_word} reasonable because the perimeter would be {too_large_perim} yards, which is {comparison} {max_perimeter} yards.",
            item_type=ItemType.ER
        )
        part_b = QuestionPart(
            label="Part B",
            prompt="Write an inequality.",
            prompt_latex="Write an inequality.",
            answer=f"2x + 2(x + {d}) {op_disp} {max_perimeter}",
            answer_latex=f"2x + 2(x + {d}) {op_disp} {max_perimeter}",
            item_type=ItemType.EQ
        )
        part_c = QuestionPart(
            label="Part C",
            prompt="Possible dimensions?",
            prompt_latex="Possible dimensions?",
            answer=f"{valid_w} yards by {valid_l} yards",
            answer_latex=f"{valid_w} yards by {valid_l} yards",
            item_type=ItemType.MC
        )

        worked = (
            f"Part A: If width = {too_large}, length = {too_large + d}.\n"
            f"  Perimeter = 2({too_large}) + 2({too_large + d}) = {too_large_perim}.\n"
            f"  {too_large_perim} is {comparison} {max_perimeter}, so {reason_word} reasonable.\n\n"
            f"Part B: 2x + 2(x + {d}) {op_disp} {max_perimeter}\n"
            f"  Simplify: 4x + {2 * d} {op_disp} {max_perimeter}\n"
            f"  4x {op_disp} {max_perimeter - 2 * d}\n"
            f"  x {op_disp} {_fmt(boundary)}\n\n"
            f"Part C: Width = {valid_w}, Length = {valid_l}.\n"
            f"  Perimeter = {valid_perim} {op_disp} {max_perimeter}. Valid."
        )

        # Blank number line for students to graph the solution
        circle_type = "open" if op in [">", "<"] else "closed"
        nl_direction = "right" if op in [">", ">="] else "left"
        nl_render = {
            "type": "number_line",
            "value": float(boundary),
            "circle_type": circle_type,
            "direction": nl_direction,
            "blank": True,
        }

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.EASY, 6, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.EASY,
            dok=3,
            item_type=ItemType.MP,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=f"Part A: {reason_word} reasonable; Part B: 2x + 2(x + {d}) {op_disp} {max_perimeter}; Part C: {valid_w} by {valid_l}",
            answer_latex=f"Part A: {reason_word} reasonable; Part B: 2x + 2(x + {d}) {op_disp} {max_perimeter}; Part C: {valid_w} by {valid_l}",
            worked_solution=worked,
            parts=[part_a, part_b, part_c],
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6,
            variant_index=variant_idx,
            render_data=nl_render,
        )

    # ================================================================
    # MAIN GENERATION METHOD
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        """Generate all variants for all 6 stems.

        Returns ~120 questions (6 stems x 20 variants).
        """
        all_questions = []

        stem_methods = [
            self.stem1_below_mc,
            self.stem2_below_mc,
            self.stem3_approaching_ms,
            self.stem4_approaching_mc,
            self.stem5_at_mp,
            self.stem6_above_mp,
        ]

        for stem_fn in stem_methods:
            for v in range(variants_per_stem):
                try:
                    question = stem_fn(v)
                    all_questions.append(question)
                except Exception as e:
                    print(f"Error generating {stem_fn.__name__} variant {v}: {e}")
                    continue

        return all_questions

    def generate_stem_variants(self, stem_index: int,
                                variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        """Generate variants for a single stem (1-6)."""
        stem_methods = {
            1: self.stem1_below_mc,
            2: self.stem2_below_mc,
            3: self.stem3_approaching_ms,
            4: self.stem4_approaching_mc,
            5: self.stem5_at_mp,
            6: self.stem6_above_mp,
        }

        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-6.")

        questions = []
        for v in range(variants_per_stem):
            try:
                questions.append(fn(v))
            except Exception as e:
                print(f"Error generating stem {stem_index} variant {v}: {e}")
                continue

        return questions


# ================================================================
# CLI ENTRY POINT FOR TESTING
# ================================================================

if __name__ == "__main__":
    print("Generating 7.AF.4 question variants...")
    print("=" * 60)

    generator = Stem7AF4(seed=42)
    all_questions = generator.generate_all_variants(variants_per_stem=3)

    for q in all_questions:
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
    print(f"Total questions generated: {len(all_questions)}")
