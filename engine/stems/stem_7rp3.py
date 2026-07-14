"""
Stem generator for 7.RP.3:
  Represent real-world and other mathematical situations that involve
  proportional relationships. Write equations and draw graphs to represent
  these proportional relationships. Apply the definition of unit rate to y = mx. (E)

Content Limits:
  - Rational numbers
  - Constant of proportionality can be expressed as fraction, colon, or words
  - Graphing: ordered pairs involve integers or half values only
  - Equations must be in y = mx form
  - Real-world context should be used most of the time
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: whole numbers only, unit rate is a whole number
  Medium: whole numbers resulting in non-whole unit rate, use variables
  Difficult: more than one proportional relationship, non-whole numbers

6 Stems from the Item Spec:
  Stem 1 (Below-EQ):       Write equation y = mx from a verbal description (DOK 1, easy)
  Stem 2 (Approaching-MC): Identify equation y = mx from a table (DOK 2, medium)
  Stem 3 (At-NR):          Write equation y = mx from a table with non-consecutive values (DOK 2, difficult)
  Stem 4 (Above-MS):       Interpret equation y = mx and select all true statements (DOK 3, easy)
  Stem 5 (Approaching-MC): Identify equation y = mx from a graph (DOK 2, easy)
  Stem 6 (At-MP):          Graph proportional relationship from verbal description (DOK 3, easy)
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
from engine.context_pools import pick_name, CONTEXTS_7RP3
from engine.svg_helpers import proportional_graph_svg


STANDARD_CODE = "7.RP.3"
VARIANTS_PER_STEM = 20


def _fmt(val):
    """Format a Fraction or number for display."""
    if isinstance(val, Fraction):
        f = float(val)
        if f == int(f):
            return str(int(f))
        return f"{f:g}"
    if isinstance(val, float):
        if val == int(val):
            return str(int(val))
        return f"{val:g}"
    return str(val)


def _fmt_money(val):
    """Format a value as dollars with 2 decimal places."""
    f = float(val) if isinstance(val, Fraction) else val
    if f == int(f):
        return f"${int(f)}"
    return f"${f:.2f}"


class Stem7RP3:
    """Generates ~20 variants for each of 4 stems from the 7.RP.3 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - EQ (DOK 1, Easy)
    # Write equation y = mx from a simple verbal description
    # "Apples cost $5 per pound. Write an equation for c and p."
    # ================================================================

    def stem1_below_eq(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)
        name = pick_name(rng)

        rate = rng.randint(2, 12)

        scenarios = [
            {
                "desc": f"Apples cost ${rate} per pound.",
                "equation": f"c = {rate}p",
                "vars": "p pounds and c cost",
            },
            {
                "desc": f"{name} earns ${rate} per hour.",
                "equation": f"e = {rate}h",
                "vars": "h hours and e earnings",
            },
            {
                "desc": f"A car travels {rate} miles per gallon of gas.",
                "equation": f"d = {rate}g",
                "vars": "g gallons and d distance in miles",
            },
            {
                "desc": f"A printer prints {rate} pages per minute.",
                "equation": f"p = {rate}m",
                "vars": "m minutes and p pages",
            },
            {
                "desc": f"{name} reads {rate} pages per day.",
                "equation": f"p = {rate}d",
                "vars": "d days and p pages",
            },
            {
                "desc": f"Tickets cost ${rate} each.",
                "equation": f"c = {rate}t",
                "vars": "t tickets and c cost",
            },
        ]

        scenario = rng.choice(scenarios)

        stem_text = (
            f"{scenario['desc']}\n\n"
            f"Write an equation to represent the relationship between "
            f"{scenario['vars']}."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.EQ,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.EQ,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=scenario["equation"],
            answer_latex=f"${scenario['equation']}$",
            worked_solution=(
                f"The rate is {rate} per unit, so the equation is {scenario['equation']}. "
                f"This is in the form y = mx where m = {rate}."
            ),
            context_scenario="write proportional equation from description",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Approaching Proficiency - MC (DOK 2, Medium)
    # Identify equation y = mx from a table
    # Table includes the ordered pair for the constant of proportionality
    # ================================================================

    def stem2_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)
        name = pick_name(rng)

        ctx = rng.choice(CONTEXTS_7RP3)

        # Medium: unit rate may not be a whole number
        # Use rates like 2.25, 1.5, 3.5, etc.
        rate_options = [
            Fraction(3, 2), Fraction(5, 2), Fraction(7, 2),
            Fraction(9, 4), Fraction(7, 4), Fraction(11, 4),
            Fraction(5, 4), Fraction(3, 1), Fraction(4, 1),
            Fraction(5, 1), Fraction(7, 1),
        ]
        rate = rng.choice(rate_options)
        rate_str = _fmt(rate)

        desc = ctx["desc"].format(name=name, rate=rate_str)

        # Build table: include x=1 (the constant of proportionality pair)
        x_vals = [1, 2, 3, 4, 5]
        y_vals = [rate * x for x in x_vals]

        table_render = {
            "type": "data_table",
            "headers": [ctx['x_label'], ctx['y_label']],
            "rows": [[str(x), _fmt(y)] for x, y in zip(x_vals, y_vals)],
        }

        correct = f"y = {rate_str}x"
        distractors = set()
        distractors.add(f"y = {_fmt(rate + 1)}x")
        distractors.add(f"y = {rate_str} + x")
        # Round the inverse to avoid ugly repeating decimals like 0.285714
        inv = Fraction(1, 1) / rate if rate != 0 else Fraction(1)
        inv_rounded = f"{float(inv):.2f}".rstrip('0').rstrip('.')
        distractors.add(f"y = {inv_rounded}x")
        distractors.discard(correct)
        distractors = list(distractors)[:3]
        while len(distractors) < 3:
            d = f"y = {_fmt(rate * 2)}x"
            if d != correct and d not in distractors:
                distractors.append(d)
            else:
                distractors.append(f"{_fmt(rate)}y = x")

        all_options = [(correct, True)] + [(d, False) for d in distractors[:3]]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = (
            f"{desc}\n\n"
            f"The table shows the relationship.\n\n"
            f"Which equation represents the cost y, in {ctx['y_label'].lower()}, for x {ctx['x_label'].lower()}?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.MEDIUM, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=(
                f"The unit rate is {_fmt(y_vals[0])} / 1 = {rate_str}. "
                f"So the equation is y = {rate_str}x."
            ),
            choices=choices, render_data=table_render,
            context_scenario="equation from table",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: At Proficiency - NR (DOK 2, Difficult)
    # Write equation y = mx from a table with non-consecutive values
    # (does NOT include the ordered pair for the constant of proportionality)
    # ================================================================

    def stem3_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)
        name = pick_name(rng)

        # Use a decimal rate for difficulty
        rate_options = [
            Fraction(249, 100),  # 2.49
            Fraction(199, 100),  # 1.99
            Fraction(325, 100),  # 3.25
            Fraction(175, 100),  # 1.75
            Fraction(450, 100),  # 4.50
            Fraction(275, 100),  # 2.75
            Fraction(150, 100),  # 1.50
            Fraction(225, 100),  # 2.25
            Fraction(350, 100),  # 3.50
        ]
        rate = rng.choice(rate_options)
        rate_str = _fmt(rate)

        items = [
            ("candy", "pounds", "the cost, y", "x pounds"),
            ("cheese", "pounds", "the cost, y", "x pounds"),
            ("fabric", "yards", "the cost, y", "x yards"),
            ("trail mix", "ounces", "the cost, y", "x ounces"),
            ("ribbon", "feet", "the cost, y", "x feet"),
        ]
        item_name, unit, y_desc, x_desc = rng.choice(items)

        # Non-consecutive x-values that skip x=1
        x_vals = sorted(rng.sample([2, 3, 4, 5, 6, 7, 8], 4))
        y_vals = [rate * x for x in x_vals]

        table_render_3 = {
            "type": "data_table",
            "headers": [f"{unit.capitalize()} (x)", "Cost (y)"],
            "rows": [[str(x), f"${_fmt(y)}"] for x, y in zip(x_vals, y_vals)],
            "title": f"{item_name.capitalize()} Prices",
        }

        stem_text = (
            f"A table representing the cost, y, of x {unit} of {item_name} is given.\n\n"
            f"Complete the equation to represent the relationship given in the table.\n\n"
            f"y = ___x"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.DIFFICULT, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=rate_str, answer_latex=rate_str,
            worked_solution=(
                f"To find the constant of proportionality, divide any y-value by its x-value:\n"
                f"${_fmt(y_vals[0])} / {x_vals[0]} = {rate_str}\n"
                f"So y = {rate_str}x"
            ),
            render_data=table_render_3,
            context_scenario="equation from non-consecutive table",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: Above Proficiency - MS (DOK 3, Easy)
    # Interpret equation y = mx and select ALL true statements
    # ================================================================

    def stem4_above_ms(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        rate = rng.randint(2, 10)

        contexts = [
            {
                "equation": f"y = {rate}x",
                "desc": f"the relationship between x, the number of tickets, and y, the total cost in dollars",
                "x_unit": "tickets",
                "y_word": "cost",
            },
            {
                "equation": f"y = {rate}x",
                "desc": f"the relationship between x, the number of hours worked, and y, the total pay in dollars",
                "x_unit": "hours",
                "y_word": "pay",
            },
            {
                "equation": f"y = {rate}x",
                "desc": f"the relationship between x, the number of pounds, and y, the total cost in dollars",
                "x_unit": "pounds",
                "y_word": "cost",
            },
        ]

        ctx = rng.choice(contexts)
        y_word = ctx["y_word"]

        # Generate test values
        test_x1 = rng.randint(3, 6)
        test_y1 = rate * test_x1
        test_x2 = rng.randint(2, 5)
        test_y2 = rate * test_x2

        # Wrong values
        wrong_y = test_x1 + rate  # additive error

        # Build statements - mix of correct and incorrect (shortened to fit PDF)
        correct_statements = [
            (f"The {y_word} for {test_x2} {ctx['x_unit']} is ${test_y2}.", True),
            (f"The point ({test_x1}, {test_y1}) means {test_x1} {ctx['x_unit']} {y_word} ${test_y1}.", True),
            (f"The relationship is proportional.", True),
        ]

        incorrect_statements = [
            (f"The {y_word} for {test_x1} {ctx['x_unit']} is ${wrong_y}.", False),
            (f"The graph is a horizontal line through y = {rate}.", False),
            (f"The graph passes through the point ({rate}, 1).", False),
        ]

        # Pick 3 correct and 3 incorrect
        rng.shuffle(correct_statements)
        rng.shuffle(incorrect_statements)
        all_statements = correct_statements[:3] + incorrect_statements[:3]
        rng.shuffle(all_statements)

        choices = []
        correct_keys = []
        for i, (text, is_correct) in enumerate(all_statements):
            key = chr(ord('a') + i)
            choices.append(QuestionChoice(
                key=key, text=text, text_latex=text,
                is_correct=is_correct,
            ))
            if is_correct:
                correct_keys.append(key)

        answer_str = ", ".join(correct_keys)

        stem_text = (
            f"The equation {ctx['equation']} represents {ctx['desc']}.\n\n"
            f"Select ALL the correct statements."
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MS,
                               Difficulty.EASY, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.EASY, dok=3, item_type=ItemType.MS,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer_str, answer_latex=answer_str,
            worked_solution=(
                f"Using y = {rate}x:\n"
                + "\n".join(
                    f"- '{c.text}' is {'CORRECT' if c.is_correct else 'INCORRECT'}."
                    for c in choices
                )
            ),
            choices=choices,
            context_scenario="interpret proportional equation",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Approaching Proficiency - MC (DOK 2, Easy)
    # Identify equation y = mx from a GRAPH
    # Graph shows points on a proportional line through origin
    # Spec: "identify or write an equation ... given a ... graph that
    #        includes the ordered pair that correlates to the constant
    #        of proportionality"
    # ================================================================

    def stem5_approaching_graph_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        # Whole-number unit rates for easy difficulty
        rate = rng.randint(2, 8)

        graph_contexts = [
            {"x_label": "Hours (x)", "y_label": "Miles (y)",
             "desc": "The graph shows the number of miles traveled over time."},
            {"x_label": "Pounds (x)", "y_label": "Cost in $ (y)",
             "desc": "The graph shows the cost of fruit by weight."},
            {"x_label": "Items (x)", "y_label": "Cost in $ (y)",
             "desc": "The graph shows the total cost for items purchased."},
            {"x_label": "Hours (x)", "y_label": "Earnings in $ (y)",
             "desc": "The graph shows earnings based on hours worked."},
            {"x_label": "Gallons (x)", "y_label": "Miles (y)",
             "desc": "The graph shows miles driven per gallons of gas."},
        ]
        ctx = rng.choice(graph_contexts)

        # Points: include (1, rate) so the unit rate is visible
        x_vals = [1, 2, 3, 4, 5]
        points = [(x, rate * x) for x in x_vals]

        svg = proportional_graph_svg(
            points, x_label=ctx["x_label"], y_label=ctx["y_label"],
            show_line=True,
        )

        correct = f"y = {rate}x"
        distractors = set()
        distractors.add(f"y = {rate + 1}x")
        distractors.add(f"y = {rate - 1}x" if rate > 2 else f"y = {rate + 2}x")
        distractors.add(f"y = x + {rate}")
        distractors.discard(correct)
        distractors = list(distractors)[:3]

        all_options = [(correct, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = (
            f"{ctx['desc']}\n\n"
            f"[FIGURE]\n\n"
            f"Which equation represents the relationship shown in the graph?"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.EASY, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=(
                f"From the graph, when x = 1, y = {rate}. "
                f"The unit rate (slope) is {rate}. "
                f"So the equation is y = {rate}x."
            ),
            choices=choices,
            render_data={"svg_html": svg, "type": "svg_html"},
            context_scenario="equation from graph",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx,
        )

    # ================================================================
    # STEM 6: At Proficiency - MP (DOK 3, Easy)
    # Graph a proportional relationship from a verbal description
    # Student must determine the constant of proportionality, then
    # identify ordered pairs that lie on the graph.
    # Spec: "draw graphs to represent proportional relationships,
    #        given an equation, table, or verbal description where
    #        the constant of proportionality must be calculated"
    # ================================================================

    def stem6_at_graph_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)
        name = pick_name(rng)

        # Verbal descriptions where student must calculate the unit rate
        verbal_contexts = [
            {"desc": f"{rate_n} loaves of banana bread require {rate_d} cups of sugar to bake",
             "y_name": "loaves of banana bread", "x_name": "cups of sugar",
             "y_var": "y", "x_var": "x",
             "rate_n": rate_n, "rate_d": rate_d,
             "x_label": "Cups of Sugar (x)", "y_label": "Loaves (y)"}
            for rate_n, rate_d in [(4, 2), (6, 3), (8, 4), (10, 5), (6, 2), (9, 3)]
        ] + [
            {"desc": f"{name} earns ${rate_n} for {rate_d} hours of work",
             "y_name": "earnings in dollars", "x_name": "hours",
             "y_var": "y", "x_var": "x",
             "rate_n": rate_n, "rate_d": rate_d,
             "x_label": "Hours (x)", "y_label": "Earnings in $ (y)"}
            for rate_n, rate_d in [(24, 3), (30, 5), (36, 4), (40, 8), (21, 3)]
        ] + [
            {"desc": f"A store sells {rate_d} pounds of apples for ${rate_n}",
             "y_name": "cost in dollars", "x_name": "pounds",
             "y_var": "y", "x_var": "x",
             "rate_n": rate_n, "rate_d": rate_d,
             "x_label": "Pounds (x)", "y_label": "Cost in $ (y)"}
            for rate_n, rate_d in [(6, 2), (9, 3), (15, 5), (12, 4)]
        ]

        ctx = rng.choice(verbal_contexts)
        rate = Fraction(ctx["rate_n"], ctx["rate_d"])
        rate_str = _fmt(rate)

        # Part A: What is the unit rate (constant of proportionality)?
        partA_prompt = (
            f"What is the unit rate (constant of proportionality)? "
            f"Express as a whole number or simplified fraction."
        )
        partA_answer = rate_str

        # Part B: Name 3 ordered pairs on the graph (including the origin)
        # Use integer or half-value coordinates per content limits
        graph_points = [(0, 0)]
        for x in range(1, 6):
            y = rate * x
            # Only include if y is integer or half-value
            if y.denominator in (1, 2):
                graph_points.append((int(x), float(y)))
                if len(graph_points) >= 4:
                    break

        # If not enough clean points, use the rate_d multiples
        if len(graph_points) < 4:
            for mult in range(1, 6):
                x = ctx["rate_d"] * mult
                y = rate * x
                pt = (int(x), int(y))
                if pt not in graph_points:
                    graph_points.append(pt)
                if len(graph_points) >= 4:
                    break

        display_pts = graph_points[:4]
        pts_str = ", ".join(f"({p[0]}, {_fmt(p[1])})" for p in display_pts)

        partB_prompt = (
            f"List three ordered pairs (other than the origin) that would "
            f"be on the graph of this proportional relationship."
        )
        # Use the non-origin points
        answer_pts = [p for p in display_pts if p != (0, 0)][:3]
        partB_answer = ", ".join(f"({p[0]}, {_fmt(p[1])})" for p in answer_pts)

        # Part C: Write the equation
        partC_prompt = "Write the equation that represents this relationship in the form y = mx."
        partC_answer = f"y = {rate_str}x"

        parts = [
            QuestionPart(
                label="Part A", prompt=partA_prompt, prompt_latex=partA_prompt,
                answer=partA_answer, answer_latex=partA_answer, item_type=ItemType.NR,
            ),
            QuestionPart(
                label="Part B", prompt=partB_prompt, prompt_latex=partB_prompt,
                answer=partB_answer, answer_latex=partB_answer, item_type=ItemType.NR,
            ),
            QuestionPart(
                label="Part C", prompt=partC_prompt, prompt_latex=partC_prompt,
                answer=partC_answer, answer_latex=partC_answer, item_type=ItemType.EQ,
            ),
        ]

        stem_text = (
            f"{ctx['desc']}.\n\n"
            f"Create a graph to represent this proportional relationship, "
            f"where {ctx['y_var']} = {ctx['y_name']} and {ctx['x_var']} = {ctx['x_name']}."
        )

        # Numbered, labeled blank grid (NOT hide_labels) so students have a scale
        # to plot on: axes show the numbers 0-10 and the context's axis titles.
        blank_grid = {
            "type": "coordinate_grid",
            "x_range": [0, 10],
            "y_range": [0, 10],
            "points": [],
            "lines": [],
            "x_label": ctx["x_label"],
            "y_label": ctx["y_label"],
        }

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MP,
                               Difficulty.EASY, 6, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.EASY, dok=3, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"A: {partA_answer} B: {partB_answer} C: {partC_answer}",
            answer_latex=f"A: {partA_answer} B: {partB_answer} C: {partC_answer}",
            worked_solution=(
                f"Unit rate = {ctx['rate_n']} / {ctx['rate_d']} = {rate_str}. "
                f"Equation: y = {rate_str}x. "
                f"Points on the graph: {pts_str}."
            ),
            parts=parts,
            render_data=blank_grid,
            context_scenario="graph proportional relationship from verbal",
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6, variant_index=variant_idx,
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_eq,
            self.stem2_approaching_mc,
            self.stem3_at_nr,
            self.stem4_above_ms,
            self.stem5_approaching_graph_mc,
            self.stem6_at_graph_mp,
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
            1: self.stem1_below_eq,
            2: self.stem2_approaching_mc,
            3: self.stem3_at_nr,
            4: self.stem4_above_ms,
            5: self.stem5_approaching_graph_mc,
            6: self.stem6_at_graph_mp,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-6.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 7.RP.3 question variants...")
    gen = Stem7RP3(seed=42)
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
