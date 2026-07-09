"""
Stem generator for 7.DSP.4:
  Understand that the probability of a chance event is a number between 0 and 1.
  Probability near 0 is unlikely, around 1/2 is neither unlikely nor likely,
  near 1 is likely. Probability of 1 is certain, 0 is impossible.
  Classify as impossible, unlikely, equally likely, likely, or certain.

Content Limits:
  - Rational numbers
  - Probabilities NOT given as percentages (fractions only)
  - Calculator: ALLOWED

Difficulty Tiers:
  Easy: Focus on impossible (0) and certain (1)
  Medium: Focus on unlikely, likely, equally likely (not 0 or 1)
  Difficult: Multiple probabilities as correct answers

4 Stems:
  Stem 1 (Below-MC, DOK 1):       Classify likelihood given probability 0, 1/2, or 1
  Stem 2 (Approaching-MC, DOK 1): Classify likelihood of events from situation
  Stem 3 (At-MC, DOK 1):          Classify probabilities as fractions on likelihood scale
  Stem 4 (Above-MC, DOK 1):       Compare likelihood of events given probabilities
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
from engine.svg_helpers import spinner_svg


STANDARD_CODE = "7.DSP.4"
VARIANTS_PER_STEM = 20


LIKELIHOOD_SCALE = {
    "impossible": (Fraction(0), "impossible (probability = 0)"),
    "unlikely": (None, "unlikely (probability close to 0)"),
    "equally_likely": (Fraction(1, 2), "equally likely (probability = 1/2)"),
    "likely": (None, "likely (probability close to 1)"),
    "certain": (Fraction(1), "certain (probability = 1)"),
}

# Spinner/bag scenarios
SCENARIOS = [
    {"type": "bag", "object": "marbles",
     "desc": "A bag contains {items}. One marble is drawn at random."},
    {"type": "bag", "object": "tiles",
     "desc": "A bag contains {items}. One tile is drawn at random."},
    {"type": "spinner", "object": "sections",
     "desc": "A spinner is divided into {n} equal sections labeled {items}. The spinner is spun once."},
    {"type": "number_cube", "object": "sides",
     "desc": "A number cube has faces labeled {items}. The cube is rolled once."},
]


def _frac_str(f):
    """Format a Fraction as a display string."""
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


class Stem7DSP4:
    """Generates 20 variants for each of 4 stems from the 7.DSP.4 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx, variant_idx):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ----------------------------------------------------------------
    # Stem 1: Below – Classify likelihood given probability 0, 1/2, or 1 (MC, DOK 1)
    # ----------------------------------------------------------------
    def _stem1(self, variant_idx):
        gen, rng = self._make_gen(1, variant_idx)

        # Pick a probability value
        prob_type = rng.choice(["impossible", "equally_likely", "certain"])
        if prob_type == "impossible":
            prob = Fraction(0)
            correct_class = "impossible"
        elif prob_type == "equally_likely":
            prob = Fraction(1, 2)
            correct_class = "equally likely"
        else:
            prob = Fraction(1)
            correct_class = "certain"

        stem = (f"An event has a probability of {_frac_str(prob)}. "
                f"Which word best describes the likelihood of this event?")

        options = ["impossible", "unlikely", "equally likely", "likely", "certain"]
        wrong = [o for o in options if o != correct_class]
        rng.shuffle(wrong)
        wrong = wrong[:3]

        all_choices = [(correct_class, True)] + [(w, False) for w in wrong]
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
            difficulty=Difficulty.EASY, dok=1, item_type=ItemType.MC,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_key, answer_latex=answer_key,
            worked_solution=f"A probability of {_frac_str(prob)} means the event is {correct_class}.",
            choices=choices,
            seed=gen.seed, stem_index=1, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 2: Approaching – Classify likelihood from spinner situation (MC, DOK 1)
    # ----------------------------------------------------------------
    def _stem2(self, variant_idx):
        gen, rng = self._make_gen(2, variant_idx)

        # Build a spinner with named sections
        colors = ["red", "blue", "green", "yellow", "orange", "purple"]
        rng.shuffle(colors)
        n_sections = rng.choice([4, 5, 6])
        section_colors = colors[:n_sections]

        # Make unequal sections
        counts = {}
        for c in section_colors:
            counts[c] = 1
        # Add extra to some colors
        extras = rng.randint(1, 3)
        for _ in range(extras):
            c = rng.choice(section_colors)
            counts[c] += 1
        total = sum(counts.values())

        # Pick an event to classify
        target_color = rng.choice(section_colors)
        prob = Fraction(counts[target_color], total)

        if prob == 0:
            correct = "impossible"
        elif prob < Fraction(1, 4):
            correct = "unlikely"
        elif prob == Fraction(1, 2):
            correct = "equally likely"
        elif prob > Fraction(3, 4):
            correct = "likely"
        elif prob >= Fraction(1, 2):
            correct = "likely"
        else:
            correct = "unlikely"

        # Build spinner SVG
        # Expand counts into individual sections for spinner
        spinner_sections = []
        for c in section_colors:
            for _ in range(counts[c]):
                spinner_sections.append({'label': c, 'fraction': 1 / total})

        svg = spinner_svg(spinner_sections)

        items_desc = ", ".join(f"{counts[c]} {c}" for c in section_colors if counts[c] > 0)
        stem = (f"A spinner has {total} equal sections: {items_desc}. "
                f"[FIGURE] The spinner is spun once. "
                f"The probability of landing on {target_color} is {_frac_str(prob)}. "
                f"Which word best describes this event?")

        options = ["impossible", "unlikely", "equally likely", "likely", "certain"]
        wrong = [o for o in options if o != correct]
        rng.shuffle(wrong)
        wrong = wrong[:3]

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
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING,
                                         ItemType.MC, Difficulty.MEDIUM, 2, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.MC,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_key, answer_latex=answer_key,
            worked_solution=f"P({target_color}) = {_frac_str(prob)}. Since {float(prob):.2f} is {correct}.",
            choices=choices,
            render_data={"svg_html": svg, "type": "svg_html"},
            seed=gen.seed, stem_index=2, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 3: At – Classify probabilities on likelihood scale (MC, DOK 1)
    # ----------------------------------------------------------------
    def _stem3(self, variant_idx):
        gen, rng = self._make_gen(3, variant_idx)

        # Generate a probability fraction and classify it
        prob_options = [
            (Fraction(1, 8), "unlikely"),
            (Fraction(1, 6), "unlikely"),
            (Fraction(1, 5), "unlikely"),
            (Fraction(1, 4), "unlikely"),
            (Fraction(1, 3), "unlikely"),
            (Fraction(1, 2), "equally likely"),
            (Fraction(2, 3), "likely"),
            (Fraction(3, 4), "likely"),
            (Fraction(4, 5), "likely"),
            (Fraction(5, 6), "likely"),
            (Fraction(7, 8), "likely"),
        ]
        prob, correct = rng.choice(prob_options)

        stem = (f"An event has a probability of {_frac_str(prob)}. "
                f"Which classification best describes the likelihood of this event occurring?")

        options = ["impossible", "unlikely", "equally likely", "likely", "certain"]
        wrong = [o for o in options if o != correct]
        rng.shuffle(wrong)
        wrong = wrong[:3]

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
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.AT,
                                         ItemType.MC, Difficulty.MEDIUM, 3, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.MEDIUM, dok=1, item_type=ItemType.MC,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_key, answer_latex=answer_key,
            worked_solution=f"{_frac_str(prob)} = {float(prob):.3f}. This is {correct}.",
            choices=choices,
            seed=gen.seed, stem_index=3, variant_index=variant_idx,
        )

    # ----------------------------------------------------------------
    # Stem 4: Above – Compare likelihood of events (MC, DOK 1)
    # ----------------------------------------------------------------
    def _stem4(self, variant_idx):
        gen, rng = self._make_gen(4, variant_idx)

        # Generate 3 events with different probabilities
        events = [
            ("Event A", Fraction(rng.randint(1, 3), 8)),
            ("Event B", Fraction(rng.randint(4, 5), 8)),
            ("Event C", Fraction(rng.randint(6, 7), 8)),
        ]
        rng.shuffle(events)

        # Question: which is most likely?
        most_likely = max(events, key=lambda e: e[1])

        events_desc = ". ".join(
            f"{name} has a probability of {_frac_str(prob)}" for name, prob in events)
        stem = f"Three events are described. {events_desc}. Which event is most likely to occur?"

        correct = most_likely[0]
        wrong_events = [e[0] for e in events if e[0] != correct]
        wrong_events.append("All events are equally likely")

        all_choices = [(correct, True)] + [(w, False) for w in wrong_events]
        rng.shuffle(all_choices)
        keys = "abcd"
        choices = []
        answer_key = ""
        for i, (text, is_c) in enumerate(all_choices):
            choices.append(QuestionChoice(key=keys[i], text=text, text_latex=text, is_correct=is_c))
            if is_c:
                answer_key = keys[i]

        return GeneratedQuestion(
            question_id=make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE,
                                         ItemType.MC, Difficulty.DIFFICULT, 4, variant_idx),
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.DIFFICULT, dok=2, item_type=ItemType.MC,
            stem_text=stem, stem_latex=stem,
            answer_text=answer_key, answer_latex=answer_key,
            worked_solution=(f"Compare: {', '.join(f'{n}={_frac_str(p)}' for n,p in events)}. "
                             f"{most_likely[0]} has the highest probability ({_frac_str(most_likely[1])})."),
            choices=choices,
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
