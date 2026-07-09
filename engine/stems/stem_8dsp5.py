"""
Stem generator for 8.DSP.5:
  Understand the use of the multiplication counting principle.
  Develop and apply it to situations with a large number of outcomes.

Content Limits:
  - Small-scale: no more than 3 elements to be combined
  - Large-scale: 4 or more elements to be combined
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: Number of outcomes at each stage is 4 or less
  Medium: Total outcomes of compound event up to 100
  Difficult: Total outcomes may exceed 100

4 Stems:
  Stem 1 (Below-MC, DOK 2):       Show multiplication counting = listing method
  Stem 2 (Approaching-NR, DOK 1-2): Expression for small-scale situation
  Stem 3 (At-NR, DOK 2):          Solve large-scale problem
  Stem 4 (Above-NR, DOK 3):       Constraints on order or repetition
"""

import random
from fractions import Fraction

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.models import (
    GeneratedQuestion, QuestionChoice, QuestionPart,
    Difficulty, ProficiencyLevel, ItemType, make_question_id
)
from engine.number_generators import NumberGenerator
from engine.svg_helpers import tree_diagram_svg


STANDARD_CODE = "8.DSP.5"
VARIANTS_PER_STEM = 20


# Context pools for counting problems
SMALL_CONTEXTS = [
    {"desc": "{name} is choosing an outfit",
     "stages": [
         ("shirts", ["red shirt", "blue shirt", "white shirt"]),
         ("pants", ["jeans", "khakis"]),
     ]},
    {"desc": "{name} is ordering lunch",
     "stages": [
         ("sandwiches", ["turkey", "ham", "veggie"]),
         ("drinks", ["water", "juice", "milk"]),
     ]},
    {"desc": "{name} is making a flag with two stripes",
     "stages": [
         ("top stripe", ["red", "blue", "green"]),
         ("bottom stripe", ["white", "yellow"]),
     ]},
    {"desc": "{name} is choosing a movie night combination",
     "stages": [
         ("movies", ["comedy", "action", "animated"]),
         ("snacks", ["popcorn", "chips", "candy"]),
     ]},
]

LARGE_CONTEXTS = [
    {"desc": "A lock has {n} dials, each with digits 0-9",
     "stage_sizes": None, "n_dials": True},
    {"desc": "A restaurant menu has {s1} appetizers, {s2} entrees, {s3} sides, and {s4} desserts",
     "categories": ["appetizer", "entree", "side", "dessert"]},
    {"desc": "A license plate has {n1} letters followed by {n2} digits",
     "letters_digits": True},
    {"desc": "An ice cream shop has {s1} flavors, {s2} cone types, and {s3} toppings",
     "categories": ["flavor", "cone type", "topping"]},
]

NAMES = ["Marcus", "Sofia", "Jayden", "Aaliyah", "Wei", "Priya", "Carlos", "Maya",
         "Ethan", "Lin", "Amir", "Emma", "Diego", "Zara", "Leo", "Grace",
         "Kai", "Rosa", "Tyler", "Fatima"]


class Stem8DSP5:
    """Generates 20 variants for each of 4 stems from the 8.DSP.5 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx, variant_idx):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ----------------------------------------------------------------
    # Stem 1: Below – Show multiplication counting = listing (MC, DOK 2)
    # ----------------------------------------------------------------
    def _stem1(self, variant_idx):
        gen, rng = self._make_gen(1, variant_idx)
        name = rng.choice(NAMES)

        ctx = rng.choice(SMALL_CONTEXTS)
        desc = ctx["desc"].format(name=name)
        stages = ctx["stages"]

        # Build tree diagram
        stage_labels = [s[1] for s in stages]
        svg = tree_diagram_svg(stage_labels)

        sizes = [len(s[1]) for s in stages]
        total = 1
        for s in sizes:
            total *= s

        expression = " x ".join(str(s) for s in sizes)
        items_desc = " and ".join(f"{len(s[1])} {s[0]}" for s in stages)

        stem = (f"{desc}. There are {items_desc}. [FIGURE] "
                f"Which expression shows how to find the total number of "
                f"possible combinations?")

        correct = f"{expression} = {total}"
        wrong = [
            f"{' + '.join(str(s) for s in sizes)} = {sum(sizes)}",
            f"{expression} = {total + sizes[0]}",
            f"{sizes[0]} x {sizes[0]} = {sizes[0]**2}",
        ]

        all_choices = [(correct, True)] + [(w, False) for w in wrong]
        rng.shuffle(all_choices)
        keys = "abcd"
        choices = []
        answer_key = ""
        for i, (text, is_c) in enumerate(all_choices):
            choices.append(QuestionChoice(key=keys[i], text=text, text_latex=text, is_correct=is_c))
            if is_c:
                answer_key = keys[i]

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW,
                                         ItemType.MC, Difficulty.EASY, 1, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.MC,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_key, answer_latex=answer_key,
            worked_solution=f"Multiplication counting principle: {expression} = {total} outcomes.",
            choices=choices,
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=gen.seed, stem_index=1, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 2: Approaching – Expression for small-scale situation (NR, DOK 1-2)
    # ----------------------------------------------------------------
    def _stem2(self, variant_idx):
        gen, rng = self._make_gen(2, variant_idx)
        name = rng.choice(NAMES)

        # 2-3 stages, small numbers
        n_stages = rng.choice([2, 3])
        categories = rng.sample(["shirts", "pants", "shoes", "hats", "socks"], n_stages)
        sizes = [rng.randint(2, 4) for _ in range(n_stages)]
        total = 1
        for s in sizes:
            total *= s

        items_desc = ", ".join(f"{sizes[i]} {categories[i]}" for i in range(n_stages))
        stem = (f"{name} has {items_desc}. How many different combinations "
                f"can {name} make choosing one of each?")

        answer_str = str(total)
        expression = " x ".join(str(s) for s in sizes)

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING,
                                         ItemType.NR, Difficulty.EASY, 2, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.EASY, dok=2, item_type=ItemType.NR,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_str, answer_latex=answer_str,
            worked_solution=f"Multiply: {expression} = {total}.",
            seed=gen.seed, stem_index=2, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 3: At – Solve large-scale problem (NR, DOK 2)
    # ----------------------------------------------------------------
    def _stem3(self, variant_idx):
        gen, rng = self._make_gen(3, variant_idx)

        scenario_type = rng.choice(["menu", "code", "plate"])

        if scenario_type == "menu":
            cats = rng.sample(["appetizers", "entrees", "sides", "desserts", "drinks"], 4)
            sizes = [rng.randint(3, 8) for _ in range(4)]
            total = 1
            for s in sizes:
                total *= s
            items_desc = ", ".join(f"{sizes[i]} {cats[i]}" for i in range(4))
            stem = (f"A restaurant offers {items_desc}. A customer orders one "
                    f"of each. How many different meal combinations are possible?")
            expression = " x ".join(str(s) for s in sizes)

        elif scenario_type == "code":
            n_digits = rng.choice([3, 4, 5])
            digit_range = 10
            total = digit_range ** n_digits
            stem = (f"A {n_digits}-digit code uses digits 0 through 9. "
                    f"Each digit can be repeated. How many different codes are possible?")
            expression = " x ".join(["10"] * n_digits)

        else:  # plate
            n_letters = rng.choice([2, 3])
            n_numbers = rng.choice([2, 3, 4])
            total = (26 ** n_letters) * (10 ** n_numbers)
            stem = (f"A license plate format uses {n_letters} letters followed by "
                    f"{n_numbers} digits. Each letter and digit can be repeated. "
                    f"How many different license plates are possible?")
            parts = ["26"] * n_letters + ["10"] * n_numbers
            expression = " x ".join(parts)

        answer_str = str(total)

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.AT,
                                         ItemType.NR, Difficulty.MEDIUM, 3, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=2, item_type=ItemType.NR,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_str, answer_latex=answer_str,
            worked_solution=f"Multiplication counting: {expression} = {total}.",
            seed=gen.seed, stem_index=3, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 4: Above – Constraints on order or repetition (NR, DOK 3)
    # ----------------------------------------------------------------
    def _stem4(self, variant_idx):
        gen, rng = self._make_gen(4, variant_idx)

        scenario_type = rng.choice(["no_repeat_code", "arrangement", "president"])

        if scenario_type == "no_repeat_code":
            n_digits = rng.choice([3, 4])
            # Digits 0-9, no repetition
            total = 1
            factors = []
            for i in range(n_digits):
                total *= (10 - i)
                factors.append(str(10 - i))
            stem = (f"A {n_digits}-digit code uses digits 0 through 9, but "
                    f"no digit can be repeated. How many different codes are possible?")
            expression = " x ".join(factors)

        elif scenario_type == "arrangement":
            n_people = rng.randint(4, 7)
            n_seats = rng.choice([3, 4])
            if n_seats > n_people:
                n_seats = n_people - 1
            total = 1
            factors = []
            for i in range(n_seats):
                total *= (n_people - i)
                factors.append(str(n_people - i))
            stem = (f"From a group of {n_people} students, {n_seats} are chosen "
                    f"to stand in a line. How many different arrangements are possible?")
            expression = " x ".join(factors)

        else:  # president
            n_members = rng.randint(5, 10)
            positions = rng.choice([3, 4])
            pos_names = ["president", "vice president", "secretary", "treasurer"][:positions]
            total = 1
            factors = []
            for i in range(positions):
                total *= (n_members - i)
                factors.append(str(n_members - i))
            pos_str = ", ".join(pos_names[:-1]) + f", and {pos_names[-1]}"
            stem = (f"A club with {n_members} members needs to elect a {pos_str}. "
                    f"No member can hold more than one position. "
                    f"How many different ways can the positions be filled?")
            expression = " x ".join(factors)

        answer_str = str(total)

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE,
                                         ItemType.NR, Difficulty.DIFFICULT, 4, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=3, item_type=ItemType.NR,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_str, answer_latex=answer_str,
            worked_solution=f"Without repetition: {expression} = {total}.",
            seed=gen.seed, stem_index=4, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    def generate_all_variants(self, variants_per_stem=VARIANTS_PER_STEM):
        questions = []
        for v in range(variants_per_stem):
            questions.append(self._stem1(v))
            questions.append(self._stem2(v))
            questions.append(self._stem3(v))
            questions.append(self._stem4(v))
        return questions
