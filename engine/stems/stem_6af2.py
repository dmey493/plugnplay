"""
Stem generator for 6.AF.2:
  Demonstrate which values from a specified set, if any, make the equation or
  inequality true. Use substitution to determine whether a given number in a
  specified set makes an equation or inequality true.

Content Limits:
  - Limit to rational numbers
  - Items will not require students to compute with negative numbers
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: whole numbers only
  Medium: mixture of whole numbers and decimals; exponents may be used
  Difficult: only decimals, fractions, or mixed numbers; exponents may be used

6 Stems from the Item Spec:
  Stem 1 (Below-MC): Substitute values into equation to find solution (DOK 1, difficult)
  Stem 2 (Below-MS): Select all equations with a given solution y=N (DOK 1, easy)
  Stem 3 (Approaching-TM): Determine if values make inequality true/false, table (DOK 1, difficult)
  Stem 4 (Approaching-MS): Select two inequalities where N is a solution (DOK 1, easy)
  Stem 5 (At-MC): Which set of numbers contains only solutions to inequality? (DOK 2, difficult)
  Stem 6 (Above-MP): Real-world inequality, Part A: select valid combos, Part B: explain (DOK 3, easy)
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
from engine.number_generators import NumberGenerator, ALLOWED_DENOMINATORS
from engine.context_pools import pick_name


STANDARD_CODE = "6.AF.2"
VARIANTS_PER_STEM = 20


class Stem6AF2:
    """Generates ~20 variants for each of 6 stems from the 6.AF.2 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    @staticmethod
    def _pick_display(val):
        if val.denominator == 1:
            return "whole"
        d = val.denominator
        while d % 2 == 0: d //= 2
        while d % 5 == 0: d //= 5
        if d == 1:
            return "decimal"
        if val >= 1:
            return "mixed"
        return "fraction"

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 1, Difficult)
    # "2.45x = 15.19  Which value of x makes the equation true?"
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        # Generate equation: ax = b where answer is a decimal
        a = gen.decimal_2place(1.00, 9.99)
        x_correct = gen.decimal_1place(2.0, 15.0)
        b = a * x_correct

        a_rn = RationalNumber(a, "decimal")
        b_rn = RationalNumber(b, "decimal")
        x_rn = RationalNumber(x_correct, "decimal")

        var = rng.choice(["x", "y", "n"])

        # Generate plausible wrong answers (close decimals)
        distractors = set()
        # Common errors: off by 0.01, 0.1, wrong operation
        for offset in [Fraction(1, 100), Fraction(-1, 100),
                       Fraction(1, 10), Fraction(-2, 10)]:
            d = x_correct + offset
            if d > 0 and d != x_correct:
                distractors.add(d)

        distractors = list(distractors)
        rng.shuffle(distractors)
        distractors = distractors[:3]

        # Pad if needed
        while len(distractors) < 3:
            d = x_correct + Fraction(rng.randint(1, 5), 10)
            if d != x_correct and d not in distractors:
                distractors.append(d)

        all_options = [(x_correct, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (val, is_correct) in enumerate(all_options):
            rn = RationalNumber(val, "decimal")
            choices.append(QuestionChoice(
                key=chr(ord('a') + i),
                text=rn.display(),
                text_latex=rn.display(),
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        # Pick equation form
        forms = [
            (f"{a_rn.display()}{var} = {b_rn.display()}", "multiplication"),
            (f"{var} + {a_rn.display()} = {RationalNumber(x_correct + a, 'decimal').display()}", "addition"),
        ]
        eq_text, eq_type = rng.choice(forms)

        # Recalculate for addition form
        if eq_type == "addition":
            b = x_correct + a
            b_rn = RationalNumber(b, "decimal")
            eq_text = f"{var} + {a_rn.display()} = {b_rn.display()}"

        stem_text = (
            f"An equation is given.\n\n"
            f"{eq_text}\n\n"
            f"Which value of {var} makes the equation true?"
        )

        worked = f"Substitute each value into {eq_text} and check which makes it true. {var} = {x_rn.display()} is the solution."

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.DIFFICULT, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.DIFFICULT,
            dok=1,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=correct_letter,
            answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices,
            context_scenario="substitution into equation",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Below Proficiency - MS (DOK 1, Easy)
    # "Select all the equations with the solution y = 4."
    # ================================================================

    def stem2_below_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        var = rng.choice(["y", "x", "n"])
        target = int(gen.whole_number(2, 15))

        # Generate 5 equations, some true for var=target, some false
        equations = []

        # 2-3 correct equations
        num_correct = rng.randint(2, 3)

        # Correct: addition
        a1 = int(gen.whole_number(1, 20))
        equations.append((f"{var} + {a1} = {target + a1}", True))

        # Correct: multiplication
        a2 = int(gen.whole_number(2, 10))
        equations.append((f"{a2}{var} = {a2 * target}", True))

        if num_correct == 3:
            # Correct: subtraction
            a3 = int(gen.whole_number(1, target - 1)) if target > 2 else 1
            equations.append((f"{var} - {a3} = {target - a3}", True))

        # Wrong equations (2-3)
        num_wrong = 5 - num_correct

        # Wrong: addition with wrong sum
        w1 = int(gen.whole_number(1, 20))
        wrong_sum = w1 + target + rng.choice([1, 2, -1])
        if wrong_sum > 0 and wrong_sum != w1 + target:
            equations.append((f"{var} + {w1} = {wrong_sum}", False))
            num_wrong -= 1

        # Wrong: multiplication with wrong product
        w2 = int(gen.whole_number(2, 10))
        wrong_prod = w2 * target + rng.choice([1, -1, 2])
        if wrong_prod > 0 and wrong_prod != w2 * target:
            equations.append((f"{w2}{var} = {wrong_prod}", False))
            num_wrong -= 1

        # Wrong: division
        while num_wrong > 0:
            w3 = int(gen.whole_number(2, 8))
            wrong_quot = w3 * target + rng.choice([w3, -w3, 1])
            if wrong_quot > 0:
                equations.append((f"{var} * {w3} = {wrong_quot}", False))
                num_wrong -= 1

        # Ensure we have exactly 5
        equations = equations[:5]
        rng.shuffle(equations)

        choices = []
        for i, (eq_text, is_correct) in enumerate(equations):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i),
                text=eq_text,
                text_latex=f"${eq_text}$",
                is_correct=is_correct,
            ))

        correct_letters = ", ".join(c.key for c in choices if c.is_correct)

        stem_text = (
            f"Select all the equations with the solution {var} = {target}."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MS,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY,
            dok=1,
            item_type=ItemType.MS,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=correct_letters,
            answer_latex=correct_letters,
            worked_solution=f"Substitute {var} = {target} into each equation. The true equations are: {correct_letters}.",
            choices=choices,
            context_scenario="select all true equations",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - TM (DOK 1, Difficult)
    # "Inequality given. Determine whether each value of c makes it true."
    # Table with Yes/No for each value.
    # ================================================================

    def stem3_approaching_tm(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        var = rng.choice(["c", "x", "n", "t"])

        # Generate inequality with decimals (difficult)
        threshold = gen.decimal_1place(1.0, 20.0)
        op = rng.choice(["<", ">", "<=", ">="])
        threshold_rn = RationalNumber(threshold, "decimal")

        # Generate 4 test values, mix of true and false
        test_values = []
        # Ensure at least 1 true and 1 false
        for _ in range(4):
            v = gen.decimal_1place(0.5, 25.0)
            test_values.append(v)

        # Determine truth for each
        results = []
        for v in test_values:
            if op == "<":
                is_true = v < threshold
            elif op == ">":
                is_true = v > threshold
            elif op == "<=":
                is_true = v <= threshold
            else:  # >=
                is_true = v >= threshold
            results.append((v, is_true))

        # Make sure we have at least one true and one false
        has_true = any(r[1] for r in results)
        has_false = any(not r[1] for r in results)
        if not has_true:
            # Force first value to be on correct side
            if op in ["<", "<="]:
                results[0] = (threshold - Fraction(1, 10), True)
            else:
                results[0] = (threshold + Fraction(1, 10), True)
        if not has_false:
            if op in ["<", "<="]:
                results[-1] = (threshold + Fraction(1, 10), False)
            else:
                results[-1] = (threshold - Fraction(1, 10), False)

        op_display = {"<": "<", ">": ">", "<=": "<=", ">=": ">="}.get(op, op)
        ineq_text = f"{var} {op_display} {threshold_rn.display()}"

        # Build table text
        table_lines = []
        for v, is_true in results:
            v_rn = RationalNumber(v, "decimal")
            yn = "Yes" if is_true else "No"
            table_lines.append(f"  {var} = {v_rn.display()}: {yn}")

        # Build data table for Yes/No display
        tm_table_headers = [f"Value of {var}", "Yes", "No"]
        tm_table_rows = []
        for v, is_true in results:
            v_rn = RationalNumber(v, "decimal")
            tm_table_rows.append([
                f"{var} = {v_rn.display()}",
                "",  # Students fill in Yes/No
                "",
            ])

        stem_text = (
            f"An inequality is given.\n\n"
            f"{ineq_text}\n\n"
            f"Determine whether each value of {var} makes the inequality true. "
            f"Select Yes or No for each value."
        )

        answer_lines = []
        for v, is_true in results:
            v_rn = RationalNumber(v, "decimal")
            answer_lines.append(f"{var} = {v_rn.display()}: {'Yes' if is_true else 'No'}")

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.TM,
                               Difficulty.DIFFICULT, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.DIFFICULT,
            dok=1,
            item_type=ItemType.TM,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text="; ".join(answer_lines),
            answer_latex="; ".join(answer_lines),
            worked_solution=f"Substitute each value into {ineq_text} and check if the inequality is true.\n" + "\n".join(table_lines),
            context_scenario="inequality truth table",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3,
            variant_index=variant_idx,
            render_data={
                "type": "data_table",
                "headers": tm_table_headers,
                "rows": tm_table_rows,
            }
        )

    # ================================================================
    # STEM 4: Approaching Proficiency - MS (DOK 1, Easy)
    # "Select the two inequalities in which 11 is a solution."
    # ================================================================

    def stem4_approaching_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        target = int(gen.whole_number(3, 25))

        # Generate 5 inequalities, exactly 2 where target is a solution
        inequalities = []

        # 2 correct: target satisfies these
        # Correct 1: x > something_less
        a1 = int(gen.whole_number(1, target - 1)) if target > 1 else 1
        inequalities.append((f"x > {a1}", True))

        # Correct 2: x < something_greater
        a2 = int(gen.whole_number(target + 1, target + 20))
        inequalities.append((f"x < {a2}", True))

        # 3 wrong: target does NOT satisfy these
        # Wrong 1: x < something_less
        w1 = int(gen.whole_number(1, max(target - 1, 2)))
        if w1 >= target:
            w1 = target - 1
        inequalities.append((f"x < {w1}", False))

        # Wrong 2: x > something_greater
        w2 = int(gen.whole_number(target + 1, target + 20))
        inequalities.append((f"x > {w2}", False))

        # Wrong 3: x < negative or x > large
        w3 = int(gen.whole_number(target + 5, target + 30))
        inequalities.append((f"x > {w3}", False))

        rng.shuffle(inequalities)
        inequalities = inequalities[:5]

        choices = []
        for i, (ineq_text, is_correct) in enumerate(inequalities):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i),
                text=ineq_text,
                text_latex=f"${ineq_text}$",
                is_correct=is_correct,
            ))

        correct_letters = ", ".join(c.key for c in choices if c.is_correct)

        stem_text = f"Select the two inequalities in which {target} is a solution."

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MS,
                               Difficulty.EASY, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY,
            dok=1,
            item_type=ItemType.MS,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=correct_letters,
            answer_latex=correct_letters,
            worked_solution=f"Substitute x = {target} into each inequality. Only {correct_letters} are true.",
            choices=choices,
            context_scenario="select inequalities with solution",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: At Proficiency - MC (DOK 2, Difficult)
    # "Which set of numbers contains only solutions to the inequality x < 1/2?"
    # ================================================================

    def stem5_at_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        # Generate inequality with fraction threshold
        threshold = gen.proper_fraction(6)
        op = rng.choice(["<", ">"])
        threshold_rn = RationalNumber(threshold, "fraction")

        var = "x"
        ineq_text = f"{var} {op} {threshold_rn.display()}"

        def is_solution(val):
            if op == "<":
                return val < threshold
            return val > threshold

        # Generate correct set: all values satisfy the inequality
        correct_set = []
        attempts = 0
        while len(correct_set) < 4 and attempts < 50:
            f = gen.proper_fraction(6)
            if is_solution(f) and f not in correct_set:
                correct_set.append(f)
            attempts += 1

        # Pad if needed
        if len(correct_set) < 4:
            for i in range(4 - len(correct_set)):
                if op == "<":
                    val = threshold - Fraction(i + 1, 12)
                else:
                    val = threshold + Fraction(i + 1, 12)
                if val > 0:
                    correct_set.append(val)

        correct_set = correct_set[:4]

        # Generate 3 wrong sets: each has at least one non-solution
        wrong_sets = []
        for _ in range(3):
            ws = []
            # Mix of solutions and non-solutions
            for j in range(4):
                if j == 0:
                    # At least one non-solution
                    if op == "<":
                        v = threshold + Fraction(rng.randint(1, 5), rng.choice([2, 3, 4, 5, 6]))
                    else:
                        v = threshold - Fraction(rng.randint(1, 5), rng.choice([2, 3, 4, 5, 6]))
                    if v <= 0:
                        v = Fraction(1, 6)
                    ws.append(v)
                else:
                    v = gen.proper_fraction(6)
                    ws.append(v)
            wrong_sets.append(ws)

        def fmt_set(vals):
            parts = []
            for v in vals:
                rn = RationalNumber(v, "fraction" if v < 1 else "mixed")
                parts.append(rn.display())
            return "{  " + ",  ".join(parts) + "  }"

        all_options = [(fmt_set(correct_set), True)]
        for ws in wrong_sets:
            all_options.append((fmt_set(ws), False))
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i),
                text=text,
                text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = (
            f"Which set of numbers contains only solutions to the inequality?\n\n"
            f"{ineq_text}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MC,
                               Difficulty.DIFFICULT, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT,
            dok=2,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=correct_letter,
            answer_latex=correct_letter,
            worked_solution=f"Substitute each value from each set into {ineq_text}. Only set {correct_letter} has all values satisfying the inequality.",
            choices=choices,
            context_scenario="solution set identification",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 6: Above Proficiency - MP (DOK 3, Easy)
    # "Truck carries crates: 340 + 30a + 45g <= 2000
    #  Part A: Which combinations can be safely carried?
    #  Part B: Explain your answer."
    # ================================================================

    def stem6_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)

        name = pick_name(rng)

        # Generate scenario. Each scenario carries its own line templates so
        # "crate of" wording only appears with crate-style scenarios. The
        # earlier elevator scenario was dropped — its weights-per-person
        # math read awkwardly ("one adult weighs 36 pounds").
        scenarios = [
            {
                "setup": "A truck carrying crates of {item1} and {item2} can hold up to {max_weight} pounds.",
                "items": [("apples", "oranges"), ("books", "equipment"),
                          ("supplies", "materials"), ("produce", "dairy")],
                "weight_thing": "machine to load and unload the crates",
                "unit_line": "- One crate of {item}, {var}, weighs {w} pounds.",
                "var1_desc": "crates of {item1}",
                "var2_desc": "crates of {item2}",
                "safety_line": "The truck can travel safely if the given inequality is satisfied.",
            },
        ]

        scen = rng.choice(scenarios)
        item1, item2 = rng.choice(scen["items"])

        fixed_weight = int(gen.whole_number(100, 500))
        w1 = int(gen.whole_number(15, 50))  # weight per item1
        w2 = int(gen.whole_number(20, 60))  # weight per item2
        max_weight = int(gen.whole_number(1500, 3000))

        var1 = item1[0]
        var2 = item2[0]
        if var1 == var2:
            var2 = chr(ord(var2) + 1)

        # Inequality: fixed + w1*a + w2*g <= max_weight
        ineq = f"{fixed_weight} + {w1}{var1} + {w2}{var2} <= {max_weight}"

        # Generate 4 test combinations, 2 valid, 2 invalid
        combos = []
        remaining = max_weight - fixed_weight

        # Valid combo 1
        a1 = int(gen.whole_number(5, 20))
        g1 = int((remaining - w1 * a1) // w2) - rng.randint(1, 5)
        if g1 < 1:
            g1 = 1
            a1 = int((remaining - w2 * g1) // w1) - 1
        combos.append((a1, g1, w1 * a1 + w2 * g1 + fixed_weight <= max_weight))

        # Valid combo 2
        a2 = int(gen.whole_number(3, 15))
        g2 = int((remaining - w1 * a2) // w2) - rng.randint(2, 8)
        if g2 < 1:
            g2 = 2
        combos.append((a2, g2, w1 * a2 + w2 * g2 + fixed_weight <= max_weight))

        # Invalid combo 1
        a3 = int(gen.whole_number(20, 40))
        g3 = int(gen.whole_number(15, 30))
        combos.append((a3, g3, w1 * a3 + w2 * g3 + fixed_weight <= max_weight))

        # Invalid combo 2
        a4 = int(gen.whole_number(25, 45))
        g4 = int(gen.whole_number(20, 35))
        combos.append((a4, g4, w1 * a4 + w2 * g4 + fixed_weight <= max_weight))

        rng.shuffle(combos)

        combo_lines = []
        for i, (av, gv, valid) in enumerate(combos):
            combo_lines.append(f"- {av} {scen['var1_desc'].format(item1=item1)} and {gv} {scen['var2_desc'].format(item2=item2)}")

        valid_combos = [f"{av} {item1} and {gv} {item2}"
                        for av, gv, valid in combos if valid]
        invalid_combos = [f"{av} {item1} and {gv} {item2}"
                          for av, gv, valid in combos if not valid]

        # Stem: scenario setup + per-unit weights + the inequality. The
        # Part A / Part B prompts are NOT repeated here — they live on the
        # QuestionPart objects below, which the renderer surfaces. The
        # combination list (the four options Part A is asking about) IS in
        # the stem because it's data both parts reason over.
        stem_text = (
            f"{scen['setup'].format(item1=item1, item2=item2, max_weight=max_weight)}\n\n"
            f"{scen['unit_line'].format(item=item1, var=var1, w=w1)}\n"
            f"{scen['unit_line'].format(item=item2, var=var2, w=w2)}\n"
            f"- A {scen['weight_thing']} must always be present. It weighs {fixed_weight} pounds.\n\n"
            f"{scen['safety_line']}\n\n"
            f"{ineq}\n\n"
            f"Combinations:\n"
            + "\n".join(combo_lines)
        )

        part_a_answer = "; ".join(valid_combos) if valid_combos else "None"
        part_b_answer = (
            f"Substitute each combination into {ineq}. "
            f"The combinations that produce a total <= {max_weight} are valid."
        )

        part_a = QuestionPart(
            label="Part A",
            prompt="Which combinations can be safely carried?",
            prompt_latex="Which combinations can be safely carried?",
            answer=part_a_answer,
            answer_latex=part_a_answer,
            item_type=ItemType.MS,
        )
        part_b = QuestionPart(
            label="Part B",
            prompt="Explain your answer.",
            prompt_latex="Explain your answer.",
            answer=part_b_answer,
            answer_latex=part_b_answer,
            item_type=ItemType.ER,
        )

        worked_lines = []
        for av, gv, valid in combos:
            total = fixed_weight + w1 * av + w2 * gv
            result = "<=" if total <= max_weight else ">"
            worked_lines.append(
                f"  {fixed_weight} + {w1}({av}) + {w2}({gv}) = {total} {result} {max_weight} -> {'Safe' if valid else 'NOT safe'}"
            )

        worked = "Substitute each combination:\n" + "\n".join(worked_lines)

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
            answer_text=f"Part A: {part_a_answer}\nPart B: {part_b_answer}",
            answer_latex=f"Part A: {part_a_answer}\nPart B: {part_b_answer}",
            worked_solution=worked,
            parts=[part_a, part_b],
            context_scenario="real-world inequality substitution",
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6,
            variant_index=variant_idx
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_below_ms,
            self.stem3_approaching_tm,
            self.stem4_approaching_ms,
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
            1: self.stem1_below_mc,
            2: self.stem2_below_ms,
            3: self.stem3_approaching_tm,
            4: self.stem4_approaching_ms,
            5: self.stem5_at_mc,
            6: self.stem6_above_mp,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-6.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 6.AF.2 question variants...")
    gen = Stem6AF2(seed=42)
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
