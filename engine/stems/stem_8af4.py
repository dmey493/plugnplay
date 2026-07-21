"""
Stem generator for 8.AF.4:
  Describe qualitatively the functional relationship between two quantities
  by analyzing a graph (increasing/decreasing, linear/nonlinear, max/min).

Content Limits:
  - Include linear and nonlinear relationships
  - Graphs may have quantitative or qualitative axes
  - Types: increasing/decreasing, linear/nonlinear, constant/variable,
    comparing rates (faster/slower), initial values, max/min
  - Only continuous graphs
  - Calculator: ALLOWED

5 Stems:
  Stem 1 (Below-MC):        Match graph to qualitative description (DOK 1, Easy)
  Stem 2 (Below-MC):        Identify true statement about a graph (DOK 2, Medium)
  Stem 3 (Approaching-MC):  Context: which description matches the situation? (DOK 2, Medium)
  Stem 4 (At-MP):           Graph in context: identify behavior + interpret (DOK 2, Difficult)
  Stem 5 (Above-MP):        Interpret graph intervals & extrema in context (DOK 3, Difficult)
"""

import random
from fractions import Fraction

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.models import (
    GeneratedQuestion, QuestionChoice, QuestionPart,
    Difficulty, ProficiencyLevel, ItemType,
    make_question_id
)
from engine.number_generators import NumberGenerator
from engine.distractor_engine import shuffle_choices
from engine.context_pools import pick_name
from engine.svg_helpers import qualitative_graph_svg


STANDARD_CODE = "8.AF.4"
VARIANTS_PER_STEM = 20


# ----------------------------------------------------------------
# Graph-behavior helpers
# ----------------------------------------------------------------

BEHAVIOR_CATALOG = [
    {
        "key": "increasing",
        "label": "The function is always increasing.",
        "short": "constantly increasing",
    },
    {
        "key": "decreasing",
        "label": "The function is always decreasing.",
        "short": "constantly decreasing",
    },
    {
        "key": "inc_then_dec",
        "label": "The function increases then decreases.",
        "short": "increasing then decreasing",
    },
    {
        "key": "dec_then_inc",
        "label": "The function decreases then increases.",
        "short": "decreasing then increasing",
    },
    {
        "key": "constant",
        "label": "The function is constant (no change).",
        "short": "constant",
    },
    {
        "key": "inc_then_const",
        "label": "The function increases then stays constant.",
        "short": "increasing then constant",
    },
    {
        "key": "const_then_dec",
        "label": "The function stays constant then decreases.",
        "short": "constant then decreasing",
    },
]


def _make_graph(rng, behavior: str):
    """Return (points, render_data) for the given behavior.

    Nonlinear behaviors (inc_then_dec, dec_then_inc) use curved segments;
    linear behaviors use straight segments.
    """
    if behavior == "increasing":
        y0 = rng.randint(1, 3)
        slope = rng.randint(1, 2)
        pts = [(0, y0), (2, y0 + slope * 2), (4, y0 + slope * 4), (6, y0 + slope * 6)]
        curves = ['linear'] * 3
    elif behavior == "decreasing":
        y0 = rng.randint(8, 10)
        slope = rng.randint(1, 2)
        pts = [(0, y0), (2, y0 - slope * 2), (4, y0 - slope * 4), (6, y0 - slope * 6)]
        curves = ['linear'] * 3
    elif behavior == "inc_then_dec":
        y0 = rng.randint(1, 3)
        peak = rng.randint(7, 9)
        y_end = rng.randint(1, 4)
        pts = [(0, y0), (3, peak), (6, y_end)]
        curves = ['linear', 'linear']
    elif behavior == "dec_then_inc":
        y0 = rng.randint(6, 9)
        valley = rng.randint(1, 3)
        y_end = rng.randint(6, 9)
        pts = [(0, y0), (3, valley), (6, y_end)]
        curves = ['linear', 'linear']
    elif behavior == "constant":
        y_val = rng.randint(3, 6)
        pts = [(0, y_val), (3, y_val), (6, y_val)]
        curves = ['linear', 'linear']
    elif behavior == "inc_then_const":
        y0 = rng.randint(1, 3)
        y_flat = rng.randint(6, 8)
        pts = [(0, y0), (3, y_flat), (6, y_flat)]
        curves = ['linear', 'linear']
    elif behavior == "const_then_dec":
        y_flat = rng.randint(6, 8)
        y_end = rng.randint(1, 3)
        pts = [(0, y_flat), (3, y_flat), (6, y_end)]
        curves = ['linear', 'linear']
    else:
        raise ValueError(behavior)

    # Build segments for qualitative_graph_svg
    segments = []
    for i in range(len(pts) - 1):
        segments.append({
            'x_start': pts[i][0], 'y_start': pts[i][1],
            'x_end': pts[i + 1][0], 'y_end': pts[i + 1][1],
            'curve': curves[i],
        })

    svg = qualitative_graph_svg(segments, x_label="x", y_label="y",
                               show_scale=True)
    rd = {"type": "svg_html", "svg_html": svg}
    return pts, rd


# Contextual scenarios for stems 3-5
_CONTEXT_SCENARIOS = [
    {
        "context": "{name} drives to work. The car speeds up leaving home, drives at a constant speed on the highway, then slows down arriving at work.",
        "behavior": "inc_then_const_then_dec",
        "x_label": "Time", "y_label": "Speed",
        "segments": [
            ("speeds up from home", "increasing"),
            ("constant on the highway", "constant"),
            ("slows down arriving", "decreasing"),
        ],
    },
    {
        "context": "{name} heats water on the stove. The temperature rises quickly at first, then more slowly as it nears boiling, then stays constant at boiling.",
        "behavior": "fast_inc_then_slow_inc_then_const",
        "x_label": "Time", "y_label": "Temperature",
        "segments": [
            ("rises quickly at first", "increasing"),
            ("rises slowly near boiling", "increasing"),
            ("stays constant at boiling", "constant"),
        ],
    },
    {
        "context": "{name} throws a ball straight up. The ball rises quickly, slows down, reaches a maximum height, then falls back down.",
        "behavior": "inc_then_dec",
        "x_label": "Time", "y_label": "Height",
        "segments": [
            ("rises to maximum height", "increasing"),
            ("falls back down", "decreasing"),
        ],
    },
    {
        "context": "A bathtub is being filled with water, then {name} turns off the faucet and pulls the plug. The water level rises, stays briefly, then drops.",
        "behavior": "inc_const_dec",
        "x_label": "Time", "y_label": "Water Level",
        "segments": [
            ("water fills the tub", "increasing"),
            ("faucet off, plug still in", "constant"),
            ("plug pulled, water drains", "decreasing"),
        ],
    },
    {
        "context": "{name} bikes downhill to a store, shops for a while, then bikes uphill back home.",
        "behavior": "dec_const_inc_speed",
        "x_label": "Time", "y_label": "Distance from Home",
        "segments": [
            ("bikes to the store", "increasing"),
            ("shopping at the store", "constant"),
            ("bikes back home", "decreasing"),
        ],
    },
    {
        "context": "A roller coaster climbs a hill, plunges down, then climbs back up to the station.",
        "behavior": "inc_dec_inc",
        "x_label": "Time", "y_label": "Height",
        "segments": [
            ("climbs the first hill", "increasing"),
            ("plunges down", "decreasing"),
            ("climbs back to station", "increasing"),
        ],
    },
]


def _make_context_graph(rng, scenario: dict, name: str):
    """Build a 3-segment piecewise graph from a scenario dict.

    Uses curved segments for transitions between increasing/decreasing
    behaviors to look more realistic.
    """
    segs = scenario["segments"]
    x_per_seg = 3
    pts = []
    y = rng.randint(2, 4)
    pts.append((0, y))
    for i, (_, seg_type) in enumerate(segs):
        x_next = (i + 1) * x_per_seg
        if seg_type == "increasing":
            y = y + rng.randint(2, 4)
        elif seg_type == "decreasing":
            y = max(1, y - rng.randint(2, 4))
        # else constant: y stays the same
        pts.append((x_next, y))

    # All segments are piecewise linear (straight-line connections)
    curve_types = ['linear'] * len(segs)

    # Build segments for qualitative_graph_svg
    svg_segments = []
    for i in range(len(pts) - 1):
        svg_segments.append({
            'x_start': pts[i][0], 'y_start': pts[i][1],
            'x_end': pts[i + 1][0], 'y_end': pts[i + 1][1],
            'curve': curve_types[i],
        })

    svg = qualitative_graph_svg(svg_segments,
                                 x_label=scenario["x_label"],
                                 y_label=scenario["y_label"],
                                 show_scale=True)
    rd = {"type": "svg_html", "svg_html": svg}
    return pts, rd


class Stem8AF4:
    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below - MC (DOK 1, Easy)
    # A graph is shown. Which description matches?
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        # Pick a behavior for this variant
        simple_behaviors = ["increasing", "decreasing", "inc_then_dec", "dec_then_inc"]
        chosen = rng.choice(simple_behaviors)
        pts, rd = _make_graph(rng, chosen)

        correct_label = next(b["label"] for b in BEHAVIOR_CATALOG if b["key"] == chosen)
        distractors = [b["label"] for b in BEHAVIOR_CATALOG
                       if b["key"] != chosen and b["key"] in simple_behaviors]
        distractors = rng.sample(distractors, 3)

        stem_text = "A graph is shown below.\n\nWhich best describes the behavior of the function?"

        choices = shuffle_choices(correct_label, correct_label, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = f"The graph {correct_label.lower()[:-1]} The answer is {correct_letter}."

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 1, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct_label}",
            answer_latex=f"{correct_letter}) {correct_label}",
            worked_solution=worked, choices=choices,
            render_data=rd,
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Below - MC (DOK 2, Medium)
    # A graph with multiple features is shown. Which statement is true?
    # ================================================================

    def stem2_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        # Use a multi-segment behavior
        multi_behaviors = ["inc_then_dec", "dec_then_inc", "inc_then_const", "const_then_dec"]
        chosen = rng.choice(multi_behaviors)
        pts, rd = _make_graph(rng, chosen)

        # Build true/false statements about the graph
        y_vals = [p[1] for p in pts]
        max_y = max(y_vals)
        min_y = min(y_vals)
        max_idx = y_vals.index(max_y)
        min_idx = y_vals.index(min_y)

        true_statements = []
        false_statements = []

        if chosen == "inc_then_dec":
            true_statements.append(f"The function has a maximum value of {max_y}.")
            true_statements.append(f"The function increases from x = {pts[0][0]} to x = {pts[max_idx][0]}.")
            false_statements.append("The function is always increasing.")
            false_statements.append("The function is always decreasing.")
            false_statements.append(f"The function has a minimum value at x = {pts[max_idx][0]}.")
        elif chosen == "dec_then_inc":
            true_statements.append(f"The function has a minimum value of {min_y}.")
            true_statements.append(f"The function decreases from x = {pts[0][0]} to x = {pts[min_idx][0]}.")
            false_statements.append("The function is always increasing.")
            false_statements.append("The function is always decreasing.")
            false_statements.append(f"The function has a maximum value at x = {pts[min_idx][0]}.")
        elif chosen == "inc_then_const":
            true_statements.append(f"The function increases then stays constant.")
            true_statements.append(f"The maximum value is {max_y}.")
            false_statements.append("The function is always increasing.")
            false_statements.append("The function decreases at the end.")
            false_statements.append(f"The function has a minimum at x = {pts[-1][0]}.")
        elif chosen == "const_then_dec":
            true_statements.append(f"The function stays constant then decreases.")
            true_statements.append(f"The starting value is {pts[0][1]}.")
            false_statements.append("The function is always decreasing.")
            false_statements.append("The function increases at the start.")
            false_statements.append(f"The minimum value is {pts[0][1]}.")

        correct = rng.choice(true_statements)
        distractors = rng.sample(false_statements, min(3, len(false_statements)))
        while len(distractors) < 3:
            distractors.append("The function is linear throughout.")

        stem_text = "A graph is shown below.\n\nWhich statement about the function is true?"

        choices = shuffle_choices(correct, correct, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = f"Analyzing the graph: {correct} The answer is {correct_letter}."

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.MEDIUM, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct}",
            answer_latex=f"{correct_letter}) {correct}",
            worked_solution=worked, choices=choices,
            render_data=rd,
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching - MC (DOK 2, Medium)
    # Context: which qualitative description matches the situation?
    # ================================================================

    def stem3_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)
        name = pick_name(rng)

        scenario = rng.choice(_CONTEXT_SCENARIOS)
        context_text = scenario["context"].format(name=name)

        # Build the correct description from segments
        seg_descs = [f"{scenario['y_label'].lower()} is {s[1]}" for s in scenario["segments"]]
        correct = f"The {scenario['y_label'].lower()} " + ", then ".join(
            s[1] for s in scenario["segments"]) + "."

        # Build distractors by shuffling segment order or changing types
        wrong_orders = []
        seg_types = [s[1] for s in scenario["segments"]]
        for _ in range(10):
            shuffled = seg_types[:]
            rng.shuffle(shuffled)
            desc = f"The {scenario['y_label'].lower()} " + ", then ".join(shuffled) + "."
            if desc != correct and desc not in wrong_orders:
                wrong_orders.append(desc)
            if len(wrong_orders) >= 3:
                break

        # Pad if needed — with DISTINCT fallbacks. When segment types repeat
        # (e.g. rises/stays/rises) the shuffle pool collapses below 3 unique
        # orders, and appending the same string produced duplicate choices.
        y_lab = scenario['y_label'].lower()
        fallbacks = [
            f"The {y_lab} is constant throughout.",
            f"The {y_lab} rises steadily the whole time.",
            f"The {y_lab} falls steadily the whole time.",
            f"The {y_lab} " + ", then ".join(reversed(seg_types)) + ".",
        ]
        for fb in fallbacks:
            if len(wrong_orders) >= 3:
                break
            if fb != correct and fb not in wrong_orders:
                wrong_orders.append(fb)

        distractors = wrong_orders[:3]

        stem_text = (
            f"{context_text}\n\n"
            f"Which best describes how the {scenario['y_label'].lower()} changes over {scenario['x_label'].lower()}?"
        )

        choices = shuffle_choices(correct, correct, distractors, rng)
        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = f"Based on the description: {correct} The answer is {correct_letter}."

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{correct_letter}) {correct}",
            answer_latex=f"{correct_letter}) {correct}",
            worked_solution=worked, choices=choices,
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At - MP (DOK 2, Difficult)
    # Graph in context. Part A: describe interval. Part B: interpret feature.
    # ================================================================

    def stem4_at_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)
        name = pick_name(rng)

        scenario = _CONTEXT_SCENARIOS[variant_idx % len(_CONTEXT_SCENARIOS)]
        context_text = scenario["context"].format(name=name)
        pts, rd = _make_context_graph(rng, scenario, name)

        segs = scenario["segments"]
        y_vals = [p[1] for p in pts]
        max_y = max(y_vals)
        min_y = min(y_vals)
        max_pt = pts[y_vals.index(max_y)]
        min_pt = pts[y_vals.index(min_y)]

        # Part A: What happens between two specific x-values?
        seg_idx = rng.randint(0, len(segs) - 1)
        x_start = pts[seg_idx][0]
        x_end = pts[seg_idx + 1][0]
        seg_desc, seg_type = segs[seg_idx]

        part_a_answer = f"The {scenario['y_label'].lower()} is {seg_type} from x = {x_start} to x = {x_end} ({seg_desc})."

        # Part B: What does the highest/lowest point represent?
        if max_y > min_y:
            if rng.random() < 0.5:
                part_b_prompt = f"What does the highest point on the graph represent?"
                part_b_answer = f"The maximum {scenario['y_label'].lower()} of {max_y} occurs at {scenario['x_label'].lower()} = {max_pt[0]}."
            else:
                part_b_prompt = f"What does the lowest point on the graph represent?"
                part_b_answer = f"The minimum {scenario['y_label'].lower()} of {min_y} occurs at {scenario['x_label'].lower()} = {min_pt[0]}."
        else:
            part_b_prompt = "What does the starting point represent?"
            part_b_answer = f"The initial {scenario['y_label'].lower()} is {pts[0][1]}."

        stem_text = (
            f"{context_text}\n\n"
            f"The graph below shows {scenario['y_label'].lower()} over {scenario['x_label'].lower()}.\n\n"
            f"Part A: Describe what happens to the {scenario['y_label'].lower()} "
            f"from {scenario['x_label'].lower()} = {x_start} to {scenario['x_label'].lower()} = {x_end}.\n\n"
            f"Part B: {part_b_prompt}"
        )

        part_a = QuestionPart(
            label="Part A",
            prompt=f"Describe the graph from x = {x_start} to x = {x_end}.",
            prompt_latex=f"Describe the graph from x = {x_start} to x = {x_end}.",
            answer=part_a_answer, answer_latex=part_a_answer,
            item_type=ItemType.ER,
        )
        part_b = QuestionPart(
            label="Part B",
            prompt=part_b_prompt,
            prompt_latex=part_b_prompt,
            answer=part_b_answer, answer_latex=part_b_answer,
            item_type=ItemType.ER,
        )

        worked = f"Part A: {part_a_answer}\nPart B: {part_b_answer}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.MP,
                               Difficulty.DIFFICULT, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"A: {part_a_answer}\nB: {part_b_answer}",
            answer_latex=f"A: {part_a_answer}\nB: {part_b_answer}",
            worked_solution=worked, parts=[part_a, part_b],
            render_data=rd,
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above - MP (DOK 3, Difficult)
    # Interpret graph intervals, rate changes, and extrema in context.
    # ================================================================

    def stem5_above_mp(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)
        name = pick_name(rng)

        scenario = _CONTEXT_SCENARIOS[(variant_idx + 3) % len(_CONTEXT_SCENARIOS)]
        context_text = scenario["context"].format(name=name)
        pts, rd = _make_context_graph(rng, scenario, name)

        segs = scenario["segments"]
        y_vals = [p[1] for p in pts]
        max_y = max(y_vals)
        min_y = min(y_vals)

        # Part A: On which interval(s) is the function increasing?
        inc_intervals = []
        dec_intervals = []
        const_intervals = []
        for i, (desc, seg_type) in enumerate(segs):
            interval = f"from {scenario['x_label'].lower()} = {pts[i][0]} to {scenario['x_label'].lower()} = {pts[i + 1][0]}"
            if seg_type == "increasing":
                inc_intervals.append(interval)
            elif seg_type == "decreasing":
                dec_intervals.append(interval)
            else:
                const_intervals.append(interval)

        if inc_intervals:
            part_a_answer = f"The function is increasing {' and '.join(inc_intervals)}."
        elif dec_intervals:
            part_a_answer = f"The function is never increasing. It decreases {' and '.join(dec_intervals)}."
        else:
            part_a_answer = "The function is constant throughout."

        # Part B: What do the maximum and minimum values represent?
        max_pt = pts[y_vals.index(max_y)]
        min_pt = pts[y_vals.index(min_y)]
        part_b_answer = (
            f"The maximum {scenario['y_label'].lower()} is {max_y} "
            f"at {scenario['x_label'].lower()} = {max_pt[0]}. "
            f"The minimum {scenario['y_label'].lower()} is {min_y} "
            f"at {scenario['x_label'].lower()} = {min_pt[0]}."
        )

        # Part C: Is the overall function linear or nonlinear?
        all_same_type = len(set(s[1] for s in segs)) == 1
        if all_same_type and len(segs) == 1:
            linearity = "linear"
            lin_reason = "it has a constant rate of change throughout"
        else:
            linearity = "nonlinear"
            lin_reason = "the rate of change is not constant across all intervals"

        part_c_answer = f"The function is {linearity} because {lin_reason}."

        stem_text = (
            f"{context_text} [FIGURE]\n\n"
            f"Part A: On which interval(s) is the {scenario['y_label'].lower()} increasing?\n\n"
            f"Part B: What are the maximum and minimum values?\n\n"
            f"Part C: Is the relationship linear or nonlinear? Explain."
        )

        part_a = QuestionPart(
            label="Part A", prompt="On which interval(s) is the function increasing?",
            prompt_latex="On which interval(s) is the function increasing?",
            answer=part_a_answer, answer_latex=part_a_answer,
            item_type=ItemType.ER,
        )
        part_b = QuestionPart(
            label="Part B", prompt="What are the maximum and minimum values?",
            prompt_latex="What are the maximum and minimum values?",
            answer=part_b_answer, answer_latex=part_b_answer,
            item_type=ItemType.ER,
        )
        part_c = QuestionPart(
            label="Part C", prompt="Is the relationship linear or nonlinear?",
            prompt_latex="Is the relationship linear or nonlinear?",
            answer=part_c_answer, answer_latex=part_c_answer,
            item_type=ItemType.ER,
        )

        worked = f"Part A: {part_a_answer}\nPart B: {part_b_answer}\nPart C: {part_c_answer}"

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MP,
                               Difficulty.DIFFICULT, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=ItemType.MP,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"A: {part_a_answer}\nB: {part_b_answer}\nC: {part_c_answer}",
            answer_latex=f"A: {part_a_answer}\nB: {part_b_answer}\nC: {part_c_answer}",
            worked_solution=worked, parts=[part_a, part_b, part_c],
            render_data=rd,
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx
        )

    # ================================================================
    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        for stem_fn in [self.stem1_below_mc, self.stem2_below_mc,
                        self.stem3_approaching_mc, self.stem4_at_mp, self.stem5_above_mp]:
            for v in range(variants_per_stem):
                all_questions.append(stem_fn(v))
        return all_questions

    def generate_stem_variants(self, stem_index: int,
                               variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        methods = {1: self.stem1_below_mc, 2: self.stem2_below_mc,
                   3: self.stem3_approaching_mc, 4: self.stem4_at_mp, 5: self.stem5_above_mp}
        return [methods[stem_index](v) for v in range(variants_per_stem)]
