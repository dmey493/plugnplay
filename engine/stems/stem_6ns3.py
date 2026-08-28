"""
Stem generator for 6.NS.3:
  Compare and order rational numbers and plot them on a number line.
  Write, interpret, and explain statements of order for rational numbers
  in real-world contexts.

Content Limits:
  - Rational numbers including integers, fractions, decimals, and mixed numbers
  - Number line placement
  - Inequality statements (<, >, =)
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: two integers not close together
  Medium: more than two numbers, mix of integer/rational
  Difficult: non-integer only, close together

6 Stems from the Item Spec:
  Stem 1 (Below-MC):  Compare two integers - which is greater? (DOK 1, easy)
  Stem 2 (Below-NR):  Place integer on a number line (identify position) (DOK 1, easy)
  Stem 3 (Approaching-MC): True/false for comparison statements about 3+ numbers (DOK 2, medium)
  Stem 4 (Approaching-MC): Which inequality correctly compares two temperatures? (DOK 2, easy)
  Stem 5 (At-NR):     Order a list of non-integer rationals from least to greatest (DOK 2, difficult)
  Stem 6 (Above-MC):  Student claims -72 > -71.99, another claims -71.99 > -72 - who is correct? (DOK 3, medium)
  Stem 7 (Below-MC):    Order three decimals to the thousandths (DOK 2, easy)
  Stem 8 (Below-MC):    Which number is closest to a target (DOK 2, easy)
  Stem 9 (Approaching-MC): Compare a fraction against a decimal benchmark (DOK 2, medium)
  Stem 10 (At-NR):      Name a rational number between two given values (DOK 2, medium)
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


STANDARD_CODE = "6.NS.3"
VARIANTS_PER_STEM = 20


# ============================================================
# HELPERS
# ============================================================

def _fmt(val):
    """Format a signed rational value for display (plain string).

    Handles int, float, and Fraction inputs. Does NOT use RationalNumber
    since we need to support negative values.
    """
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


def _fmt_frac(val):
    """Format a Fraction as a/b or -a/b string. Whole numbers as integers."""
    if val.denominator == 1:
        return str(int(val))
    return f"{val.numerator}/{val.denominator}"


def _fmt_mixed(val):
    """Format a Fraction as a mixed number string (e.g., -2 3/4)."""
    if val.denominator == 1:
        return str(int(val))
    sign = -1 if val < 0 else 1
    abs_val = abs(val)
    whole = int(abs_val)
    remainder = abs_val - whole
    if whole == 0:
        prefix = "-" if sign < 0 else ""
        return f"{prefix}{remainder.numerator}/{remainder.denominator}"
    prefix = "-" if sign < 0 else ""
    return f"{prefix}{whole} {remainder.numerator}/{remainder.denominator}"


def _fmt_auto(val):
    """Auto-format a Fraction: uses mixed number for fractions, decimal for decimals."""
    if val.denominator == 1:
        return str(int(val))
    # Check if it's a terminating decimal with at most 2 places
    d = val.denominator
    temp = d
    while temp % 2 == 0:
        temp //= 2
    while temp % 5 == 0:
        temp //= 5
    if temp == 1:
        # Terminating decimal
        return _fmt(val)
    # Otherwise show as fraction or mixed number
    return _fmt_mixed(val)


# Pools of close negative values for difficult stems
CLOSE_NEGATIVE_FRACS = [
    (Fraction(-3, 4), Fraction(-7, 10)),       # -0.75 vs -0.7
    (Fraction(-1, 3), Fraction(-3, 10)),       # -0.333 vs -0.3
    (Fraction(-5, 8), Fraction(-3, 5)),        # -0.625 vs -0.6
    (Fraction(-2, 3), Fraction(-7, 10)),       # -0.667 vs -0.7
    (Fraction(-1, 4), Fraction(-3, 10)),       # -0.25 vs -0.3
    (Fraction(-5, 6), Fraction(-4, 5)),        # -0.833 vs -0.8
    (Fraction(-7, 8), Fraction(-9, 10)),       # -0.875 vs -0.9
    (Fraction(-1, 6), Fraction(-1, 5)),        # -0.167 vs -0.2
]


class Stem6NS3:
    """Generates ~20 variants for each of 6 stems from the 6.NS.3 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 1, Easy)
    # Compare two integers - which is greater?
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        # Generate 4 distinct integers to plot on a number line (spec example)
        values = set()
        while len(values) < 4:
            v = rng.randint(-7, 8)
            values.add(v)
        values = sorted(values)

        # Number line from -7 to 8
        ticks = list(range(-7, 9))

        # Build points with labels
        point_data = [{"value": v, "label": ""} for v in values]

        # Correct choice shows the values in order
        correct_order = ", ".join(str(v) for v in values)

        # Build MC: which number line correctly shows these values plotted?
        # Since we can't show multiple graphical choices easily,
        # ask: "Which list shows these numbers in order from left to right on the number line?"
        wrong1 = ", ".join(str(v) for v in sorted(values, reverse=True))
        wrong2_vals = list(values)
        rng.shuffle(wrong2_vals)
        while wrong2_vals == values:
            rng.shuffle(wrong2_vals)
        wrong2 = ", ".join(str(v) for v in wrong2_vals)
        # Swap two adjacent values
        wrong3_vals = list(values)
        if len(wrong3_vals) >= 2:
            idx = rng.randint(0, len(wrong3_vals) - 2)
            wrong3_vals[idx], wrong3_vals[idx + 1] = wrong3_vals[idx + 1], wrong3_vals[idx]
        wrong3 = ", ".join(str(v) for v in wrong3_vals)

        distractors = list(dict.fromkeys([wrong1, wrong2, wrong3]))
        distractors = [d for d in distractors if d != correct_order][:3]
        while len(distractors) < 3:
            shuf = list(values)
            rng.shuffle(shuf)
            s = ", ".join(str(v) for v in shuf)
            if s != correct_order and s not in distractors:
                distractors.append(s)

        all_options = [(correct_order, True)] + [(d, False) for d in distractors[:3]]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        vals_display = ", ".join(str(v) for v in values)
        stem_text = (
            f"The numbers {vals_display} are plotted on the number line below.\n\n"
            f"Which list shows these numbers in order from left to right on the number line?"
        )

        worked = (
            f"On a number line, numbers increase from left to right.\n"
            f"From left to right: {correct_order}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="plot integers on number line",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx,
            render_data={
                "type": "number_line_point",
                "ticks": ticks,
                "points": point_data,
            }
        )

    # ================================================================
    # STEM 2: Below Proficiency - NR (DOK 1, Easy)
    # Place integer on a number line (identify position)
    # ================================================================

    def stem2_below_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        # Generate a target integer on a number line
        target = rng.randint(-20, 20)

        # Define the number line range with tick marks every 1 unit
        # Show a window of integers around the target
        line_min = target - rng.randint(3, 6)
        line_max = target + rng.randint(3, 6)
        ticks = list(range(line_min, line_max + 1))

        stem_text = (
            f"A number line is shown below. Point P is marked on the number line.\n\n"
            f"What integer is Point P located at?\n\n"
            f"Write your answer in the box."
        )

        correct_str = str(target)

        worked = (
            f"Point P is at position {target} on the number line.\n"
            f"Counting from 0: {'move right' if target > 0 else 'move left'} "
            f"{abs(target)} units to reach {target}."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.NR,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_str, answer_latex=correct_str,
            worked_solution=worked,
            context_scenario="number line integer placement",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx,
            render_data={
                "type": "number_line_point",
                "ticks": ticks,
                "point_value": target,
                "point_label": "P",
            }
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - MC (DOK 2, Medium)
    # True/false for comparison statements about 3+ numbers
    # ================================================================

    def stem3_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        # Spec: Game points table + "which comparison is true?" (medium difficulty)
        # Generate 5 players with integer point values (mix of positive/negative)
        player_names = ["Sarah", "Julie", "Amir", "Laurenz", "Kali",
                        "Marcus", "Priya", "David", "Elena", "Chen"]
        names = rng.sample(player_names, 5)
        points = []
        while len(points) < 5:
            p = rng.randint(-50, 50)
            if p not in points:
                points.append(p)

        # Build table data
        table_rows = [[n, str(p)] for n, p in zip(names, points)]

        # Build one TRUE comparison and three FALSE ones
        sorted_pts = sorted(range(5), key=lambda i: points[i])

        # True statement: pick two players with correct comparison
        i, j = rng.sample(range(5), 2)
        if points[i] < points[j]:
            true_stmt = f"{names[i]}'s points < {names[j]}'s points ({points[i]} < {points[j]})"
        else:
            true_stmt = f"{names[i]}'s points > {names[j]}'s points ({points[i]} > {points[j]})"

        # False statements
        false_stmts = []
        # Reverse the true comparison
        if points[i] < points[j]:
            false_stmts.append(f"{names[i]}'s points > {names[j]}'s points ({points[i]} > {points[j]})")
        else:
            false_stmts.append(f"{names[i]}'s points < {names[j]}'s points ({points[i]} < {points[j]})")

        # Claim lowest > highest
        lo, hi = sorted_pts[0], sorted_pts[-1]
        false_stmts.append(f"{names[lo]}'s points > {names[hi]}'s points ({points[lo]} > {points[hi]})")

        # Claim two different values are equal
        k, m = rng.sample(range(5), 2)
        while points[k] == points[m]:
            k, m = rng.sample(range(5), 2)
        false_stmts.append(f"{names[k]}'s points = {names[m]}'s points ({points[k]} = {points[m]})")

        # Deduplicate
        unique_false = []
        for f in false_stmts:
            if f not in unique_false and f != true_stmt:
                unique_false.append(f)
        while len(unique_false) < 3:
            a_idx, b_idx = rng.sample(range(5), 2)
            if points[a_idx] != points[b_idx]:
                if points[a_idx] > points[b_idx]:
                    s = f"{names[a_idx]}'s points < {names[b_idx]}'s points ({points[a_idx]} < {points[b_idx]})"
                else:
                    s = f"{names[a_idx]}'s points > {names[b_idx]}'s points ({points[a_idx]} > {points[b_idx]})"
                if s != true_stmt and s not in unique_false:
                    unique_false.append(s)
        unique_false = unique_false[:3]

        all_options = [(true_stmt, True)] + [(f, False) for f in unique_false]
        rng.shuffle(all_options)

        choices = []
        for idx, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + idx), text=text, text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = (
            f"A group of friends are playing a game. Players can gain or lose points. "
            f"Each player's total number of points is given in the table.\n\n"
            f"Which comparison statement is TRUE?"
        )

        sorted_names = [names[idx] for idx in sorted_pts]
        sorted_points = [points[idx] for idx in sorted_pts]
        worked = (
            f"Order from least to greatest: {', '.join(f'{n}({p})' for n, p in zip(sorted_names, sorted_points))}\n"
            f"The true statement is: {true_stmt}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="game points comparison table",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx,
            render_data={
                "type": "data_table",
                "headers": ["Names", "Total Points"],
                "rows": table_rows,
                "orientation": "vertical",
            }
        )

    # ================================================================
    # STEM 4: Approaching Proficiency - MC (DOK 2, Easy)
    # Which inequality correctly compares two temperatures?
    # ================================================================

    def stem4_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        # Two integer temperatures not close together
        temp1 = rng.randint(-30, 40)
        temp2 = rng.randint(-30, 40)
        while temp2 == temp1 or abs(temp1 - temp2) < 5:
            temp2 = rng.randint(-30, 40)

        name = pick_name(rng)

        # The correct inequality
        if temp1 < temp2:
            correct_ineq = f"{temp1} < {temp2}"
        else:
            correct_ineq = f"{temp1} > {temp2}"

        # Distractors: reversed, wrong symbol, equals
        distractors = []
        if temp1 < temp2:
            distractors.append(f"{temp1} > {temp2}")       # reversed
            distractors.append(f"{temp2} < {temp1}")        # both wrong
            distractors.append(f"{temp1} = {temp2}")        # equals (wrong)
        else:
            distractors.append(f"{temp1} < {temp2}")
            distractors.append(f"{temp2} > {temp1}")
            distractors.append(f"{temp1} = {temp2}")

        # Ensure no duplicate of correct
        distractors = [d for d in distractors if d != correct_ineq][:3]

        all_options = [(correct_ineq, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        context_detail = rng.choice([
            f"The temperature in the morning was {temp1} degrees. The temperature in the afternoon was {temp2} degrees.",
            f"On Monday, the temperature was {temp1} degrees Fahrenheit. On Tuesday, it was {temp2} degrees Fahrenheit.",
            f"{name} recorded temperatures of {temp1} degrees and {temp2} degrees on two different days.",
        ])

        stem_text = (
            f"{context_detail}\n\n"
            f"Which inequality correctly compares these two temperatures?"
        )

        warmer = max(temp1, temp2)
        colder = min(temp1, temp2)
        worked = (
            f"{warmer} degrees is warmer than {colder} degrees.\n"
            f"On a number line, {warmer} is to the right of {colder}.\n"
            f"Therefore: {correct_ineq}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.EASY, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="temperature inequality comparison",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: At Proficiency - NR (DOK 2, Difficult)
    # Order a list of non-integer rationals from least to greatest
    # ================================================================

    def stem5_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        # Generate 5 distinct non-integer rational numbers that are close together
        # Mix of fractions, decimals, and negative values
        values = set()
        attempts = 0
        while len(values) < 5 and attempts < 100:
            attempts += 1
            kind = rng.choice(["frac", "dec", "mixed"])
            if kind == "frac":
                num = rng.randint(-9, 9)
                if num == 0:
                    num = 1
                den = rng.choice([2, 3, 4, 5, 6, 8])
                val = Fraction(num, den)
            elif kind == "dec":
                val = Fraction(rng.randint(-30, 30), 10)
            else:  # mixed
                sign = rng.choice([-1, 1])
                whole = rng.randint(1, 3)
                num = rng.randint(1, 3)
                den = rng.choice([2, 3, 4, 5])
                val = sign * (Fraction(whole) + Fraction(num, den))

            # Ensure non-integer
            if val.denominator != 1:
                values.add(val)
            elif kind == "dec" and val.denominator == 1:
                # Decimals that are integers don't count; skip
                continue

        # If we couldn't get 5, fill with known close fracs
        fallbacks = [Fraction(-3, 4), Fraction(-1, 2), Fraction(1, 3),
                     Fraction(2, 5), Fraction(3, 4), Fraction(-1, 5),
                     Fraction(7, 8), Fraction(-5, 6), Fraction(1, 6)]
        while len(values) < 5:
            val = rng.choice(fallbacks)
            values.add(val)

        values = list(values)[:5]

        # Display each with appropriate format
        display_map = {}
        for v in values:
            # Check if it's a terminating decimal
            d = v.denominator
            temp = d
            while temp % 2 == 0:
                temp //= 2
            while temp % 5 == 0:
                temp //= 5
            if temp == 1:
                display_map[v] = _fmt(v)
            else:
                display_map[v] = _fmt_mixed(v)

        sorted_vals = sorted(values)
        display_list = [display_map[v] for v in values]
        sorted_display = [display_map[v] for v in sorted_vals]

        correct_order = ", ".join(sorted_display)

        stem_text = (
            f"Order the following numbers from least to greatest.\n\n"
            f"{', '.join(display_list)}\n\n"
            f"Write your answer in order, separated by commas."
        )

        # Worked solution: convert all to decimals for comparison
        decimal_explanations = []
        for v in sorted_vals:
            decimal_explanations.append(f"{display_map[v]} = {float(v):.4f}".rstrip('0').rstrip('.'))

        worked = (
            f"Convert to decimals for comparison:\n"
            + "\n".join(f"  {exp}" for exp in decimal_explanations)
            + f"\n\nOrder from least to greatest: {correct_order}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.DIFFICULT, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_order, answer_latex=correct_order,
            worked_solution=worked,
            context_scenario="order non-integer rationals",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    # STEM 6: Above Proficiency - MC (DOK 3, Medium)
    # Student A claims val1 > val2, Student B claims val2 > val1.
    # Who is correct? (Close negative values that confuse students)
    # ================================================================

    def stem6_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)

        name1 = pick_name(rng)
        name2 = pick_name(rng)
        while name2 == name1:
            name2 = pick_name(rng)

        # Real-world context for comparing negative numbers
        context_pool = [
            {"unit": "degrees Fahrenheit", "thing": "temperature"},
            {"unit": "degrees Celsius", "thing": "temperature"},
            {"unit": "feet", "thing": "elevation"},
            {"unit": "dollars", "thing": "account balance"},
        ]
        ctx = rng.choice(context_pool)

        # Generate two close negative values
        base_int = -rng.randint(10, 99)
        offset_hundredths = rng.randint(1, 99)
        close_decimal = Fraction(base_int * 100 + offset_hundredths, 100)

        val_a = Fraction(base_int)
        val_b = close_decimal

        display_a = _fmt(val_a)
        display_b = _fmt(val_b)

        if val_a > val_b:
            correct_person = name1
        else:
            correct_person = name2

        # Generate a third value for ordering in Part B
        third_offset = rng.randint(1, 50)
        val_c = Fraction(base_int * 100 - third_offset, 100)
        display_c = _fmt(val_c)

        sorted_vals = sorted([val_a, val_b, val_c])
        sorted_display = [_fmt(v) for v in sorted_vals]

        stem_text = (
            f"Three {ctx['thing']} readings are recorded: "
            f"{display_a}, {display_b}, and {display_c} {ctx['unit']}.\n\n"
            f"{name1} claims that {display_a} > {display_b}.\n"
            f"{name2} claims that {display_b} > {display_a}.\n\n"
            f"Part A: Who is correct? Explain your reasoning.\n\n"
            f"Part B: Order all three values from least to greatest."
        )

        part_a = QuestionPart(
            label="Part A",
            prompt="Who is correct? Explain.",
            prompt_latex="Who is correct? Explain.",
            answer=(f"{correct_person} is correct. "
                    f"{display_b if val_b > val_a else display_a} is closer to 0 "
                    f"on the number line, so it is greater."),
            answer_latex=f"{correct_person}",
            item_type=ItemType.ER,
        )
        part_b = QuestionPart(
            label="Part B",
            prompt="Order from least to greatest",
            prompt_latex="Order from least to greatest",
            answer=", ".join(sorted_display),
            answer_latex=", ".join(sorted_display),
            item_type=ItemType.EQ,
        )

        worked = (
            f"Compare {display_a} and {display_b}:\n"
            f"  {display_a} as a decimal: {float(val_a)}\n"
            f"  {display_b} as a decimal: {float(val_b)}\n"
            f"  {correct_person} is correct.\n"
            f"  Negative numbers closer to 0 are greater.\n"
            f"Ordering: {' < '.join(sorted_display)}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.MEDIUM, 6, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.MEDIUM, dok=3, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"Part A: {correct_person}; Part B: {', '.join(sorted_display)}",
            answer_latex=f"Part A: {correct_person}; Part B: {', '.join(sorted_display)}",
            worked_solution=worked,
            parts=[part_a, part_b],
            context_scenario="debate about negative number comparison",
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6, variant_index=variant_idx
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    # ================================================================
    # STEM 7: Below Proficiency - MC (DOK 2, Easy)
    # NEW. Ordering decimals to the THOUSANDTHS now sits at Below. The prices
    # deliberately share their leading digits so place value has to be read
    # all the way out rather than judged at a glance.
    # ================================================================
    def stem7_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(7, variant_idx)

        # Two prices share their tenths digit and one does not, matching the
        # specification's own example (3.489 / 3.455 / 3.502). That mix is what
        # makes the item work: one comparison is settled at the tenths place,
        # the other only at the hundredths or thousandths.
        whole = rng.randint(2, 5)
        tenth = rng.randint(3, 7)
        pair = rng.sample(range(tenth * 100, tenth * 100 + 100), 2)
        odd_tenth = tenth + rng.choice([-1, 1])
        odd = rng.randrange(odd_tenth * 100, odd_tenth * 100 + 100)
        thousandths = pair + [odd]
        values = [whole + th / 1000.0 for th in thousandths]

        kind, names, unit = rng.choice([
            ("gas stations", ["FuelMax", "QuickFuel", "SpeedyGas"], "per gallon"),
            ("markets", ["Green Grocer", "Fresh Mart", "Value Foods"], "per pound"),
            ("suppliers", ["Northline", "Beacon", "Crestway"], "per litre"),
        ])
        pairs = list(zip(names, values))
        rng.shuffle(pairs)

        listing = "\n".join(f"{n}: ${v:.3f}" for n, v in pairs)
        ordered = [n for n, _ in sorted(pairs, key=lambda p: p[1])]

        def render(seq):
            return ", ".join(seq)

        correct = render(ordered)
        options = [
            (correct, True, None),
            (render(list(reversed(ordered))), False,
             "Ordered from greatest to least instead"),
            (render([ordered[1], ordered[0], ordered[2]]), False,
             "Compares only the first decimal place"),
            (render([ordered[0], ordered[2], ordered[1]]), False,
             "Compares only the first two decimal places"),
        ]
        rng.shuffle(options)
        choices = [QuestionChoice(key=chr(ord("a") + i), text=t, text_latex=t,
                                  is_correct=c, distractor_rationale=r)
                   for i, (t, c, r) in enumerate(options)]
        key = next(c.key for c in choices if c.is_correct).upper()

        stem_text = (
            f"Three {kind} list their prices {unit}.\n\n{listing}\n\n"
            f"Which list shows the {kind} in order from least to greatest price?"
        )
        worked = (
            f"All three prices share the same whole number, so compare the "
            f"decimals place by place.\n"
            + "\n".join(f"{n}: {v:.3f}" for n, v in sorted(pairs, key=lambda p: p[1]))
            + f"\nFrom least to greatest: {correct}"
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW,
                                         ItemType.MC, Difficulty.EASY, 7, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{key}. {correct}", answer_latex=f"{key}. {correct}",
            worked_solution=worked, choices=choices,
            context_scenario="order decimals to the thousandths",
            seed=self.base_seed * 1000 + 700 + variant_idx,
            stem_index=7, variant_index=variant_idx,
        )

    # ================================================================
    # STEM 8: Below Proficiency - MC (DOK 2, Easy)
    # NEW. "Closest to" asks about position on the number line without
    # comparing formally, so the options sit on both sides of the target.
    # ================================================================
    def stem8_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(8, variant_idx)

        target = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
        offsets = rng.sample([0.1, 0.2, 0.3, 0.6, 0.8, 1.1, 1.4], 4)
        nearest = min(offsets)
        candidates = []
        for off in offsets:
            sign = rng.choice([-1, 1])
            candidates.append(round(target + sign * off, 2))
        # Guard against two options landing the same distance away, which would
        # leave the item with two defensible answers.
        while len({round(abs(c - target), 3) for c in candidates}) != 4:
            offsets = rng.sample([0.1, 0.2, 0.3, 0.6, 0.8, 1.1, 1.4], 4)
            nearest = min(offsets)
            candidates = [round(target + rng.choice([-1, 1]) * o, 2) for o in offsets]

        correct_val = min(candidates, key=lambda c: abs(c - target))
        options = []
        for c in candidates:
            if c == correct_val:
                options.append((_fmt(c), True, None))
            else:
                options.append((_fmt(c), False,
                                f"{abs(round(c - target, 2))} away from {target}, "
                                f"which is further than {nearest}"))
        rng.shuffle(options)
        choices = [QuestionChoice(key=chr(ord("a") + i), text=t, text_latex=t,
                                  is_correct=cr, distractor_rationale=r)
                   for i, (t, cr, r) in enumerate(options)]
        key = next(c.key for c in choices if c.is_correct).upper()

        stem_text = f"Which number is closest to {target} on the number line?"
        worked = (
            f"Find how far each number is from {target}.\n"
            + "\n".join(f"{_fmt(c)} is {abs(round(c - target, 2))} away"
                         for c in sorted(candidates, key=lambda c: abs(c - target)))
            + f"\n{_fmt(correct_val)} is the closest."
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW,
                                         ItemType.MC, Difficulty.EASY, 8, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{key}. {_fmt(correct_val)}",
            answer_latex=f"{key}. {_fmt(correct_val)}",
            worked_solution=worked, choices=choices,
            context_scenario="closeness on the number line",
            seed=self.base_seed * 1000 + 800 + variant_idx,
            stem_index=8, variant_index=variant_idx,
        )

    # ================================================================
    # STEM 9: Approaching Proficiency - MC (DOK 2, Medium)
    # NEW. The revision's Approaching items mix number types, so the student
    # must convert a fraction to a decimal (or the reverse) before comparing.
    # ================================================================
    def stem9_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(9, variant_idx)

        benchmark = Fraction(rng.choice([3, 5, 7, 9, 11]), 2) / rng.choice([1, 1, 2])
        bench_dec = float(benchmark)

        # Distinct values only. Sampling with replacement used to let the same
        # fraction appear as two different options, and a duplicate choice has
        # no defensible answer. Fractions that reduce to a whole number are
        # dropped too, since the item is about converting between forms.
        def pool():
            seen = set()
            out = []
            for _ in range(60):
                f = Fraction(rng.randint(1, 15), rng.choice([2, 4, 5, 8]))
                if f.denominator == 1 or float(f) == bench_dec or f in seen:
                    continue
                seen.add(f)
                out.append(f)
            return out

        candidates = pool()
        above = [f for f in candidates if float(f) > bench_dec]
        below = [f for f in candidates if float(f) < bench_dec]
        tries = 0
        while (not above or len(below) < 3) and tries < 20:
            tries += 1
            candidates = pool()
            above = [f for f in candidates if float(f) > bench_dec]
            below = [f for f in candidates if float(f) < bench_dec]
        if not above or len(below) < 3:
            benchmark = Fraction(3, 2); bench_dec = 1.5
            above = [Fraction(7, 4)]
            below = [Fraction(1, 2), Fraction(5, 4), Fraction(1, 4)]

        # Prefer the distractors nearest the benchmark: a wrong option that is
        # obviously tiny does not test the conversion.
        below = sorted(below, key=lambda f: bench_dec - float(f))
        above = sorted(above, key=lambda f: float(f) - bench_dec)

        correct = above[0]
        wrong = below[:3]

        # The benchmark prints as a decimal and the options as fractions, so a
        # conversion is forced in every variant.
        def show(f):
            return _fmt_frac(f)

        options = [(show(correct), True, None)]
        for w in wrong:
            options.append((show(w), False,
                            f"{show(w)} = {float(w):g}, which is less than {bench_dec:g}"))
        rng.shuffle(options)
        choices = [QuestionChoice(key=chr(ord("a") + i), text=t, text_latex=t,
                                  is_correct=c, distractor_rationale=r)
                   for i, (t, c, r) in enumerate(options)]
        key = next(c.key for c in choices if c.is_correct).upper()

        item, unit = rng.choice([
            ("package weights", "pounds"), ("bottle volumes", "litres"),
            ("board lengths", "metres"), ("bag weights", "kilograms"),
        ])
        stem_text = (
            f"A store compares {item} to {bench_dec:g} {unit}.\n\n"
            f"Which weight is greater than {bench_dec:g} {unit}?"
        )
        worked = (
            f"Write each fraction as a decimal, then compare to {bench_dec:g}.\n"
            + "\n".join(f"{show(f)} = {float(f):g}" for f in [correct] + list(wrong))
            + f"\nOnly {show(correct)} = {float(correct):g} is greater than {bench_dec:g}."
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING,
                                         ItemType.MC, Difficulty.MEDIUM, 9, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{key}. {show(correct)}", answer_latex=f"{key}. {show(correct)}",
            worked_solution=worked, choices=choices,
            context_scenario="compare across number forms",
            seed=self.base_seed * 1000 + 900 + variant_idx,
            stem_index=9, variant_index=variant_idx,
        )

    # ================================================================
    # STEM 10: At Proficiency - NR (DOK 2, Medium)
    # NEW. "Identify a rational number that lies between two given rational
    # numbers." Open response, no options, and any value strictly between the
    # two endpoints is acceptable.
    # ================================================================
    def stem10_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(10, variant_idx)

        low_whole = rng.randint(-6, 4)
        low = round(low_whole - rng.choice([0.1, 0.2, 0.4, 0.6, 0.8]), 2)
        high = low_whole + rng.choice([0, 1])
        if high <= low:
            high = low_whole + 1
        example = round((low + high) / 2, 2)

        stem_text = (
            f"A rational number, x, is located between {_fmt(low)} and "
            f"{_fmt(high)} on the number line.\n\n"
            f"What is a possible value for x?"
        )
        answer = (
            f"Any value strictly between {_fmt(low)} and {_fmt(high)}, "
            f"for example {_fmt(example)}"
        )
        worked = (
            f"The value must be greater than {_fmt(low)} and less than "
            f"{_fmt(high)}.\n"
            f"Halfway between them is ({_fmt(low)} + {_fmt(high)}) / 2 = "
            f"{_fmt(example)}, which works.\n"
            f"Any other number in that interval is also correct."
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.AT,
                                         ItemType.NR, Difficulty.MEDIUM, 10, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=worked,
            context_scenario="name a value between two rationals",
            seed=self.base_seed * 1000 + 1000 + variant_idx,
            stem_index=10, variant_index=variant_idx,
        )

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_below_nr,
            self.stem3_approaching_mc,
            self.stem4_approaching_mc,
            self.stem5_at_nr,
            self.stem6_above_mp,
            self.stem7_below_mc,
            self.stem8_below_mc,
            self.stem9_approaching_mc,
            self.stem10_at_nr,
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
            4: self.stem4_approaching_mc,
            5: self.stem5_at_nr,
            6: self.stem6_above_mp,
            7: self.stem7_below_mc,
            8: self.stem8_below_mc,
            9: self.stem9_approaching_mc,
            10: self.stem10_at_nr,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-6.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 6.NS.3 question variants...")
    gen = Stem6NS3(seed=42)
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
