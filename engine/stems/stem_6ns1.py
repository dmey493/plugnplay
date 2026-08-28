"""
Stem generator for 6.NS.1:
  Use positive and negative numbers to represent and compare quantities
  in real-world contexts, explaining the meaning of 0 in each situation.

Content Limits:
  - Positive and negative integers, decimals, and fractions
  - Real-world contexts: temperature, elevation, money, football, time, floors
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: integers only
  Medium: positive/negative decimals or fractions
  Difficult: mixture of rational numbers

5 Stems from the Item Spec:
  Stem 1 (Below-MC):  Which situation is best represented by a negative number? (DOK 1, easy)
  Stem 2 (Below-MC):  Identify the number that represents a real-world situation (DOK 2, easy)
  Stem 3 (Approaching-MC): Identify values that model a situation with decimals (DOK 2, medium)
  Stem 4 (At-NR):     Write the rational number for a real-world situation (DOK 2, medium)
  Stem 5 (Above-MC):  Interpret game scores recorded as changes and select true statement (DOK 3, easy)
  Stem 6 (Below-MC):    Infer the sign when the amount is withheld (DOK 2, easy)
  Stem 7 (At-NR):       Interpret a table of signed differences against a goal (DOK 2, medium)
  Stem 8 (Above-ER):    Critique a signed representation and explain the error (DOK 3, difficult)
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
from engine.context_pools import CONTEXTS_6NS1, pick_name


STANDARD_CODE = "6.NS.1"
VARIANTS_PER_STEM = 20


# ============================================================
# HELPERS
# ============================================================

def _fmt(val):
    """Format a signed rational value for display (plain string, no RationalNumber).

    Handles int, float, and Fraction inputs.
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
    """Format a Fraction as a fraction string (e.g. 3/4 or -3/4)."""
    if val.denominator == 1:
        return str(int(val))
    return f"{val.numerator}/{val.denominator}"


# Situations that are always negative
NEGATIVE_SITUATIONS = [
    ("a temperature of 15 degrees below zero", -15),
    ("an elevation of 200 feet below sea level", -200),
    ("a withdrawal of $50 from a bank account", -50),
    ("a loss of 7 yards in football", -7),
    ("3 seconds before launch (countdown)", -3),
    ("2 floors underground (basement level 2)", -2),
    ("a debt of $120", -120),
    ("a drop in temperature of 8 degrees", -8),
    ("10 feet below sea level", -10),
    ("a loss of $35", -35),
    ("a decrease of 6 points", -6),
    ("5 degrees below zero", -5),
    ("spending $45 from savings", -45),
    ("a submarine diving 300 feet", -300),
    ("a penalty of 15 yards", -15),
    ("losing 12 points in a game", -12),
    ("an overdraft of $25 in a bank account", -25),
    ("descending 4 floors in an elevator", -4),
    ("a weight loss of 3 pounds", -3),
    ("falling 20 feet below ground level", -20),
]

# Situations that are always positive
POSITIVE_SITUATIONS = [
    ("the elevation of a mountain at 5,280 feet", 5280),
    ("the number of students in a class: 28", 28),
    ("a summer temperature of 95 degrees", 95),
    ("earning $75 from a job", 75),
    ("a gain of 12 yards in football", 12),
    ("a deposit of $200 into a bank account", 200),
    ("climbing 3 floors up in an elevator", 3),
    ("a height of 150 feet above sea level", 150),
    ("scoring 25 points in a game", 25),
    ("running 4 miles", 4),
    ("growing 2 inches taller", 2),
    ("an increase of 10 degrees", 10),
    ("saving $60", 60),
    ("5 seconds after launch", 5),
    ("gaining 8 pounds", 8),
    ("a profit of $500", 500),
    ("an altitude of 35,000 feet", 35000),
    ("walking 15 blocks forward", 15),
    ("a raise of $3 per hour", 3),
    ("reading 40 pages", 40),
]


class Stem6NS1:
    """Generates ~20 variants for each of 5 stems from the 6.NS.1 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 1, Easy)
    # Which situation is best represented by a negative number?
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        # Pick one negative situation (correct) and three positive (distractors)
        neg = rng.choice(NEGATIVE_SITUATIONS)
        pos_pool = rng.sample(POSITIVE_SITUATIONS, 3)

        correct_text = neg[0]
        distractors = [p[0] for p in pos_pool]

        all_options = [(correct_text, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        stem_text = "Which situation is best represented by a negative number?"

        worked = (
            f"A negative number represents a decrease, loss, debt, or value below a reference point. "
            f"\"{correct_text}\" represents a negative quantity ({neg[1]})."
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
            choices=choices, context_scenario="identify negative situation",
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1, variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Below Proficiency - MC (DOK 2, Easy)
    # Identify the number that represents a real-world situation
    # e.g., "An elevation of 200 feet below sea level" -> choose -200
    # ================================================================

    def stem2_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        ctx = rng.choice(CONTEXTS_6NS1)
        # Generate an integer value for easy difficulty
        magnitude = rng.randint(5, 500)
        # Decide positive or negative
        is_negative = rng.choice([True, False])

        if is_negative:
            description = ctx["negative"].format(val=magnitude)
            correct_val = -magnitude
        else:
            description = ctx["positive"].format(val=magnitude)
            correct_val = magnitude

        correct_str = _fmt(correct_val)

        # Distractors: wrong sign, magnitude errors
        distractors = set()
        distractors.add(_fmt(-correct_val))            # wrong sign
        distractors.add(_fmt(abs(correct_val) + rng.randint(10, 100)))  # too large
        distractors.add("0")                            # zero
        distractors.discard(correct_str)
        dist_list = [d for d in distractors if d != correct_str][:3]
        while len(dist_list) < 3:
            offset = rng.choice([10, 50, 100, -10, -50])
            d = _fmt(correct_val + offset)
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
            f"Which number best represents the following situation?\n\n"
            f"\"{description}\""
        )

        zero_meaning = ctx["zero_meaning"]
        worked = (
            f"The situation describes {description}.\n"
            f"This is represented by {correct_str}.\n"
            f"{zero_meaning}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.MC,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario=f"signed number for {ctx['context']}",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2, variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - MC (DOK 2, Medium)
    # Identify values that model a situation with decimals
    # e.g., "A temperature drop of 3.5 degrees" -> select -3.5
    # ================================================================

    def stem3_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        ctx = rng.choice(CONTEXTS_6NS1)

        # Medium difficulty: decimals
        # Generate a 1-decimal-place value
        magnitude_tenths = rng.randint(10, 999)  # 1.0 to 99.9
        magnitude = magnitude_tenths / 10.0

        is_negative = rng.choice([True, False])

        if is_negative:
            description = ctx["negative"].format(val=_fmt(magnitude))
            correct_val = -magnitude
        else:
            description = ctx["positive"].format(val=_fmt(magnitude))
            correct_val = magnitude

        correct_str = _fmt(correct_val)

        # Distractors
        distractors = set()
        distractors.add(_fmt(-correct_val))                     # wrong sign
        distractors.add(_fmt(correct_val * 10))                 # decimal place error
        distractors.add(_fmt(abs(correct_val) + rng.choice([0.5, 1.0, 2.5])))  # nearby wrong
        distractors.discard(correct_str)
        dist_list = [d for d in distractors if d != correct_str][:3]
        while len(dist_list) < 3:
            offset = rng.choice([0.1, 0.5, 1.5, -0.1, -0.5])
            d = _fmt(correct_val + offset)
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
            f"Which number best represents the following situation?\n\n"
            f"\"{description}\""
        )

        zero_meaning = ctx["zero_meaning"]
        worked = (
            f"The situation describes {description}.\n"
            f"This is represented by {correct_str}.\n"
            f"{zero_meaning}"
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
            choices=choices, context_scenario=f"decimal signed number for {ctx['context']}",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3, variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At Proficiency - NR (DOK 2, Medium)
    # Write the rational number for a real-world situation
    # e.g., "Cost reduced by $23.57" -> answer: -23.57
    # ================================================================

    def stem4_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        ctx = rng.choice(CONTEXTS_6NS1)

        # Medium difficulty: use decimals (2 places for money, 1 place for others)
        if ctx["context"] == "money":
            cents = rng.randint(100, 9999)  # $1.00 to $99.99
            magnitude = cents / 100.0
        else:
            tenths = rng.randint(10, 999)
            magnitude = tenths / 10.0

        is_negative = rng.choice([True, False])

        if is_negative:
            description = ctx["negative"].format(val=_fmt(magnitude))
            correct_val = -magnitude
        else:
            description = ctx["positive"].format(val=_fmt(magnitude))
            correct_val = magnitude

        correct_str = _fmt(correct_val)

        stem_text = (
            f"Write a positive or negative number to represent the following situation.\n\n"
            f"\"{description}\"\n\n"
            f"Write your answer in the box."
        )

        zero_meaning = ctx["zero_meaning"]
        worked = (
            f"The situation describes {description}.\n"
            f"{'A decrease, loss, or amount below the reference' if is_negative else 'An increase, gain, or amount above the reference'} "
            f"is represented by a {'negative' if is_negative else 'positive'} number.\n"
            f"Answer: {correct_str}\n"
            f"The meaning of 0 in this context: {zero_meaning}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.MEDIUM, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_str, answer_latex=correct_str,
            worked_solution=worked,
            context_scenario=f"write signed number for {ctx['context']}",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4, variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above Proficiency - MC (DOK 3, Easy)
    # Interpret game scores recorded as changes over rounds
    # and select the true statement
    # ================================================================

    def stem5_above_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        name1 = pick_name(rng)
        name2 = pick_name(rng)
        while name2 == name1:
            name2 = pick_name(rng)

        # Generate 4 rounds of score changes (integers for easy difficulty)
        rounds = 4
        changes1 = [rng.randint(-10, 10) for _ in range(rounds)]
        changes2 = [rng.randint(-10, 10) for _ in range(rounds)]

        # Ensure they're not identical
        while changes1 == changes2:
            changes2 = [rng.randint(-10, 10) for _ in range(rounds)]

        total1 = sum(changes1)
        total2 = sum(changes2)

        # Build true and false statements
        statements = []

        # True statement about totals
        if total1 > total2:
            true_stmt = f"{name1} has a higher total score than {name2}."
        elif total2 > total1:
            true_stmt = f"{name2} has a higher total score than {name1}."
        else:
            true_stmt = f"{name1} and {name2} have the same total score."

        statements.append((true_stmt, True))

        # False statements
        if total1 != total2:
            statements.append((f"{name1} and {name2} have the same total score.", False))
        else:
            statements.append((f"{name1} has a higher total score than {name2}.", False))

        # False: wrong total claim
        wrong_total = total1 + rng.choice([2, 3, 5, -2, -3])
        statements.append((f"{name1}'s total score is {wrong_total}.", False))

        # False: claim about who had biggest single gain
        max1 = max(changes1)
        max2 = max(changes2)
        if max1 >= max2:
            statements.append((f"{name2} had the largest single-round gain.", False))
        else:
            statements.append((f"{name1} had the largest single-round gain.", False))

        # Ensure exactly 4 options, 1 correct
        options = statements[:4]
        rng.shuffle(options)

        choices = []
        for i, (text, is_correct) in enumerate(options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=text,
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        # Build data table for rendering
        table_headers = ["Player"] + [f"R{i+1}" for i in range(rounds)]
        table_rows = [
            [name1] + [f"{c:+d}" for c in changes1],
            [name2] + [f"{c:+d}" for c in changes2],
        ]

        stem_text = (
            f"{name1} and {name2} are playing a game where points are recorded "
            f"as positive (gains) or negative (losses) each round.\n\n"
            f"Which statement is true?"
        )

        worked = (
            f"{name1}'s total: {' + '.join([f'({c:+d})' for c in changes1])} = {total1}\n"
            f"{name2}'s total: {' + '.join([f'({c:+d})' for c in changes2])} = {total2}\n"
            f"Therefore: {true_stmt}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.MC,
                               Difficulty.EASY, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid, standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.EASY, dok=3, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=correct_letter, answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices, context_scenario="interpret game score changes",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5, variant_index=variant_idx,
            render_data={
                "type": "data_table",
                "headers": table_headers,
                "rows": table_rows,
            }
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    # ================================================================
    # STEM 6: Below Proficiency - MC (DOK 2, Easy)
    # NEW. The amount is deliberately withheld: the student must realise a
    # deduction is negative without a value to work from. That is a step up
    # from stem 2, where the quantity is stated.
    # ================================================================
    def stem6_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(6, variant_idx)
        name = pick_name(rng)

        start = rng.choice([20, 25, 40, 50, 75, 100])
        answer = -rng.randint(2, 15)

        setting, event, unit = rng.choice([
            ("in a bank account", "A fee is taken out of the account", "dollars"),
            ("on a gift card", "A purchase is made with the card", "dollars"),
            ("in a savings jar", "Some money is spent from the jar", "dollars"),
            ("of credit on a phone plan", "A call uses some of the credit", "dollars"),
            ("of battery charge left", "The battery drains", "percent"),
        ])

        options = [
            (str(answer), True, None),
            (str(-answer), False, "Right size, wrong sign: a deduction is negative"),
            ("0", False, "Zero would mean nothing was taken out"),
            (str(start), False, "This is the starting amount, not the change"),
        ]
        rng.shuffle(options)
        choices = [QuestionChoice(key=chr(ord("a") + i), text=t, text_latex=t,
                                  is_correct=c, distractor_rationale=r)
                   for i, (t, c, r) in enumerate(options)]
        key = next(c.key for c in choices if c.is_correct).upper()

        stem_text = (
            f"{name} has {start} {unit} {setting}.\n\n"
            f"{event}.\n\n"
            f"Which number could represent this change?"
        )
        worked = (
            f"The amount is not given, so decide the sign instead of the size.\n"
            f"The quantity goes down, and a decrease is written as a negative "
            f"number.\n"
            f"{answer} is the only negative choice, so it is the one that could "
            f"represent the change."
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW,
                                         ItemType.MC, Difficulty.EASY, 6, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=f"{key}. {answer}", answer_latex=f"{key}. {answer}",
            worked_solution=worked, choices=choices,
            context_scenario="infer the sign with the amount withheld",
            seed=self.base_seed * 1000 + 600 + variant_idx,
            stem_index=6, variant_index=variant_idx,
        )

    # ================================================================
    # STEM 7: At Proficiency - NR (DOK 2, Medium)
    # NEW. A table of signed differences against a goal, open response with no
    # answer choices. Zero appears deliberately: it means the goal was met
    # exactly, which is the "interpret the meaning of 0" half of the At
    # descriptor.
    # ================================================================
    def stem7_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(7, variant_idx)
        name = pick_name(rng)

        days = rng.choice([5, 6])
        n_under = rng.randint(1, 3)
        n_zero = rng.randint(0, 1)
        n_over = days - n_under - n_zero

        diffs = ([-round(rng.uniform(0.2, 1.8), 1) for _ in range(n_under)]
                 + [0.0] * n_zero
                 + [round(rng.uniform(0.2, 1.8), 1) for _ in range(n_over)])
        rng.shuffle(diffs)

        goal, unit, activity = rng.choice([
            (3, "miles", "walking"),
            (2, "miles", "running"),
            (30, "minutes", "reading"),
            (4, "laps", "swimming"),
        ])

        labels = ["Day %d" % (i + 1) for i in range(days)]
        table = "\n".join(
            f"{lab}: {('+' if d > 0 else '')}{_fmt(d)}" for lab, d in zip(labels, diffs))

        stem_text = (
            f"{name} sets a goal of {activity} {goal} {unit} each day for "
            f"{days} days.\n\n"
            f"Each day {name} records the difference between the goal and the "
            f"actual amount. A positive number means more than the goal and a "
            f"negative number means less.\n\n"
            f"{table}\n\n"
            f"On how many days did {name} fall short of the goal?"
        )

        worked = (
            f"A negative difference means less than the goal.\n"
            f"Negative entries: "
            f"{', '.join(_fmt(d) for d in diffs if d < 0) or 'none'}\n"
            + (f"A difference of 0 means the goal was met exactly, so it does "
               f"not count as falling short.\n" if n_zero else "")
            + f"{name} fell short on {n_under} day{'' if n_under == 1 else 's'}."
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.AT,
                                         ItemType.NR, Difficulty.MEDIUM, 7, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=str(n_under), answer_latex=str(n_under),
            worked_solution=worked,
            context_scenario="interpret signed differences against a goal",
            seed=self.base_seed * 1000 + 700 + variant_idx,
            stem_index=7, variant_index=variant_idx,
        )

    # ================================================================
    # STEM 8: Above Proficiency - ER (DOK 3, Difficult)
    # NEW. Above is "critique a representation ... or explain the structure of
    # a model". The existing Above stem asks which statement is true, which is
    # interpretation rather than critique.
    # ================================================================
    def stem8_above_er(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(8, variant_idx)
        student = pick_name(rng)

        amount = rng.randint(3, 15)
        rising = rng.random() < 0.5

        setting, up_word, down_word, unit, zero_means = rng.choice([
            ("the temperature outside", "warmer", "colder", "degrees",
             "the temperature is unchanged from yesterday"),
            ("the water level in a tank", "higher", "lower", "inches",
             "the level is unchanged"),
            ("a hiker's position", "above", "below", "feet",
             "the hiker is back at sea level"),
        ])

        direction = up_word if rising else down_word
        claimed = -amount if rising else amount
        correct = amount if rising else -amount

        stem_text = (
            f"A student writes {claimed} to show that {setting} is {amount} "
            f"{unit} {direction} than yesterday.\n\n"
            f"Is the student correct? Explain your answer."
        )

        answer = (
            f"The student is not correct. Writing {claimed} says the change is "
            f"{'a decrease' if rising else 'an increase'}, but {direction} means "
            f"the opposite.\n"
            f"The correct number is {correct}, because a change of "
            f"{amount} {unit} {direction} is "
            f"{'above' if rising else 'below'} the starting point.\n"
            f"The sign carries the direction of the change; the size {amount} "
            f"was already right. A value of 0 would mean {zero_means}."
        )

        worked = (
            f"Decide what the sign has to mean before checking the number.\n"
            f"{direction} is {'an increase' if rising else 'a decrease'}, so the "
            f"number must be {'positive' if rising else 'negative'}.\n"
            f"The student wrote {claimed}, which has the wrong sign.\n"
            f"Correct representation: {correct}"
        )

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE,
                                         ItemType.ER, Difficulty.DIFFICULT, 8, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=ItemType.ER,
            stem_text=stem_text, stem_latex=stem_text,
            answer_text=answer, answer_latex=answer,
            worked_solution=worked,
            context_scenario="critique a signed representation",
            seed=self.base_seed * 1000 + 800 + variant_idx,
            stem_index=8, variant_index=variant_idx,
        )

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_below_mc,
            self.stem3_approaching_mc,
            self.stem4_at_nr,
            self.stem5_above_mc,
            self.stem6_below_mc,
            self.stem7_at_nr,
            self.stem8_above_er,
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
            2: self.stem2_below_mc,
            3: self.stem3_approaching_mc,
            4: self.stem4_at_nr,
            5: self.stem5_above_mc,
            6: self.stem6_below_mc,
            7: self.stem7_at_nr,
            8: self.stem8_above_er,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-5.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 6.NS.1 question variants...")
    gen = Stem6NS1(seed=42)
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
