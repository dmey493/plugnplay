"""
Stem generator for 6.NS.7:
  Apply properties of operations (e.g., distributive, associative, commutative)
  to create equivalent linear expressions, including situations that involve
  factoring (e.g., 12x + 8 = 4(3x + 2)). Justify whether two expressions
  are equivalent using substitution.

Content Limits:
  - Expressions may have more than one unique variable
  - Limit to whole numbers with fractions/decimals used sparingly
  - No negative integers in combining like terms
  - Calculator: NOT ALLOWED

Difficulty Tiers:
  Easy: 3 or fewer terms
  Medium: 4 terms
  Difficult: 5+ terms

5 Stems from the Item Spec:
  Stem 1 (Below-MC, DOK 1, easy): Identify parts of expression (variable, coefficient, constant, term)
  Stem 2 (Below-NR, DOK 2, easy): Combine like terms (e.g., 6r + 6 + r + 2 + 2r = 9r + 8)
  Stem 3 (Approaching-MC, DOK 2, medium): Select equivalent expression (associative/commutative)
  Stem 4 (At-NR, DOK 2, easy): Apply distributive property (e.g., 3(2x + 5) = 6x + 15)
  Stem 5 (Above-NR, DOK 3, easy): Write expression equivalent to a given one using multiple properties
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


STANDARD_CODE = "6.NS.7"
VARIANTS_PER_STEM = 20


# ============================================================
# VOCABULARY FOR EXPRESSION PARTS (Stem 1)
# ============================================================

EXPRESSION_PARTS = [
    {
        "question_type": "coefficient",
        "question_template": "In the expression {expr}, what is the coefficient of {var}?",
        "answer_fn": "coefficient",
    },
    {
        "question_type": "constant",
        "question_template": "In the expression {expr}, what is the constant term?",
        "answer_fn": "constant",
    },
    {
        "question_type": "num_terms",
        "question_template": "How many terms are in the expression {expr}?",
        "answer_fn": "num_terms",
    },
    {
        "question_type": "variable",
        "question_template": "In the expression {expr}, identify the variable(s).",
        "answer_fn": "variable",
    },
]


def _format_term(coeff, var):
    """Format a term like 3x, x, or 7."""
    if var is None:
        return str(coeff)
    if coeff == 1:
        return var
    return f"{coeff}{var}"


def _format_expression(terms):
    """Format a list of (coeff, var_or_None) into an expression string.
    Uses + between terms; all coefficients are positive (per content limits).
    """
    parts = []
    for i, (coeff, var) in enumerate(terms):
        term_str = _format_term(coeff, var)
        if i == 0:
            parts.append(term_str)
        else:
            parts.append(f" + {term_str}")
    return "".join(parts)


class Stem6NS7:
    """Generates ~20 variants for each of 5 stems from the 6.NS.7 item spec."""

    def __init__(self, seed: int = 42):
        self.base_seed = seed

    def _make_gen(self, stem_idx: int, variant_idx: int):
        seed = self.base_seed * 1000 + stem_idx * 100 + variant_idx
        return NumberGenerator(seed), random.Random(seed)

    # ================================================================
    # STEM 1: Below Proficiency - MC (DOK 1, Easy)
    # Identify parts of an expression (variable, coefficient, constant, term)
    # ================================================================

    def stem1_below_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(1, variant_idx)

        var = rng.choice(["x", "y", "n", "r", "m", "p"])
        coeff = int(gen.whole_number(2, 12))
        constant = int(gen.whole_number(1, 20))

        expr = f"{coeff}{var} + {constant}"

        # Randomly pick what to ask about
        ask_type = rng.choice(["coefficient", "constant", "num_terms"])

        if ask_type == "coefficient":
            stem_text = (
                f"An expression is given.\n\n"
                f"  {expr}\n\n"
                f"What is the coefficient of {var}?"
            )
            correct = str(coeff)
            distractors = set()
            distractors.add(str(constant))
            distractors.add(str(coeff + constant))
            distractors.add(str(var))
            distractors.discard(correct)
            distractors = [d for d in distractors if d != correct][:3]
            while len(distractors) < 3:
                d = coeff + rng.choice([-2, -1, 1, 2, 3])
                if d > 0 and str(d) != correct and str(d) not in distractors:
                    distractors.append(str(d))
            scenario = "identify coefficient"
            worked = f"In {expr}, the number multiplying {var} is {coeff}. So the coefficient is {coeff}."

        elif ask_type == "constant":
            stem_text = (
                f"An expression is given.\n\n"
                f"  {expr}\n\n"
                f"What is the constant term?"
            )
            correct = str(constant)
            distractors = set()
            distractors.add(str(coeff))
            distractors.add(str(coeff + constant))
            distractors.add("0")
            distractors.discard(correct)
            distractors = [d for d in distractors if d != correct][:3]
            while len(distractors) < 3:
                d = constant + rng.choice([-2, -1, 1, 2, 3])
                if d >= 0 and str(d) != correct and str(d) not in distractors:
                    distractors.append(str(d))
            scenario = "identify constant"
            worked = f"In {expr}, the term without a variable is {constant}. So the constant is {constant}."

        else:  # num_terms
            stem_text = (
                f"An expression is given.\n\n"
                f"  {expr}\n\n"
                f"How many terms are in this expression?"
            )
            correct = "2"
            distractors = ["1", "3", "4"]
            scenario = "count terms"
            worked = f"The expression {expr} has two terms: {coeff}{var} and {constant}."

        distractors = distractors[:3]

        all_options = [(correct, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

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
            answer_text=correct_letter,
            answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices,
            context_scenario=scenario,
            seed=self.base_seed * 1000 + 100 + variant_idx,
            stem_index=1,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 2: Below Proficiency - NR (DOK 2, Easy)
    # Combine like terms (e.g., 6r + 6 + r + 2 + 2r = 9r + 8)
    # ================================================================

    def stem2_below_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(2, variant_idx)

        var = rng.choice(["r", "x", "n", "m", "y", "p"])

        # Generate 3 variable terms and 2 constant terms (easy: 3 or fewer unique groups)
        coeff1 = int(gen.whole_number(1, 8))
        coeff2 = int(gen.whole_number(1, 5))
        coeff3 = int(gen.whole_number(1, 6))
        const1 = int(gen.whole_number(1, 10))
        const2 = int(gen.whole_number(1, 10))

        total_coeff = coeff1 + coeff2 + coeff3
        total_const = const1 + const2

        # Build the unsimplified expression
        # Mix the terms in a random order
        terms = [
            (coeff1, var),
            (const1, None),
            (coeff2, var),
            (const2, None),
            (coeff3, var),
        ]
        # Remove one term randomly to keep it manageable (3-4 terms for easy)
        if rng.random() < 0.5:
            # Use 3 variable terms + 2 constants (5 terms total but still easy concept)
            pass
        else:
            # Use 2 variable terms + 1 constant (3 terms for easy)
            total_coeff = coeff1 + coeff2
            total_const = const1
            terms = [
                (coeff1, var),
                (const1, None),
                (coeff2, var),
            ]

        rng.shuffle(terms)
        expr_str = _format_expression(terms)

        stem_text = (
            f"Simplify the expression by combining like terms.\n\n"
            f"  {expr_str}"
        )

        # The simplified form
        if total_const == 0:
            answer_text = f"{total_coeff}{var}"
        else:
            answer_text = f"{total_coeff}{var} + {total_const}"

        worked_parts = []
        var_terms = [f"{c}{var}" for c, v in terms if v is not None]
        const_terms = [str(c) for c, v in terms if v is None]
        worked_parts.append(f"Variable terms: {' + '.join(var_terms)} = {total_coeff}{var}")
        if const_terms:
            worked_parts.append(f"Constant terms: {' + '.join(const_terms)} = {total_const}")
        worked_parts.append(f"Simplified: {answer_text}")
        worked = "\n".join(worked_parts)

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.BELOW, ItemType.NR,
                               Difficulty.EASY, 2, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.BELOW,
            difficulty=Difficulty.EASY,
            dok=2,
            item_type=ItemType.NR,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=answer_text,
            answer_latex=f"${answer_text}$",
            worked_solution=worked,
            context_scenario="combine like terms",
            seed=self.base_seed * 1000 + 200 + variant_idx,
            stem_index=2,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 3: Approaching Proficiency - MC (DOK 2, Medium)
    # Select equivalent expression using associative/commutative property
    # ================================================================

    def stem3_approaching_mc(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(3, variant_idx)

        var = rng.choice(["x", "y", "n", "m"])

        # Generate a 4-term expression (medium difficulty)
        coeff1 = int(gen.whole_number(2, 8))
        coeff2 = int(gen.whole_number(1, 6))
        const1 = int(gen.whole_number(1, 10))
        const2 = int(gen.whole_number(1, 10))

        total_coeff = coeff1 + coeff2
        total_const = const1 + const2

        # Original expression (unsimplified, 4 terms)
        terms = [(coeff1, var), (const1, None), (coeff2, var), (const2, None)]
        rng.shuffle(terms)
        expr_str = _format_expression(terms)

        # Correct simplified expression
        correct = f"{total_coeff}{var} + {total_const}"

        # Distractors
        distractors = set()
        # Added coefficients to constant
        distractors.add(f"{total_coeff + total_const}{var}")
        # Swapped coeff and const
        distractors.add(f"{total_const}{var} + {total_coeff}")
        # Only combined one pair
        distractors.add(f"{coeff1}{var} + {coeff2}{var} + {total_const}")
        # Multiplied instead of added
        distractors.add(f"{coeff1 * coeff2}{var} + {const1 + const2}")
        distractors.discard(correct)
        distractors = [d for d in distractors if d != correct][:3]
        while len(distractors) < 3:
            d = f"{total_coeff + rng.choice([-1, 1, 2])}{var} + {total_const + rng.choice([-1, 1, 2])}"
            if d != correct and d not in distractors:
                distractors.append(d)
        distractors = distractors[:3]

        stem_text = (
            f"Which expression is equivalent to {expr_str}?"
        )

        all_options = [(correct, True)] + [(d, False) for d in distractors]
        rng.shuffle(all_options)

        choices = []
        for i, (text, is_correct) in enumerate(all_options):
            choices.append(QuestionChoice(
                key=chr(ord('a') + i), text=text, text_latex=f"${text}$",
                is_correct=is_correct,
            ))

        correct_letter = next(c.key for c in choices if c.is_correct)

        worked = (
            f"Combine like terms in {expr_str}:\n"
            f"Variable terms: {coeff1}{var} + {coeff2}{var} = {total_coeff}{var}\n"
            f"Constant terms: {const1} + {const2} = {total_const}\n"
            f"Result: {correct}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.APPROACHING, ItemType.MC,
                               Difficulty.MEDIUM, 3, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.APPROACHING,
            difficulty=Difficulty.MEDIUM,
            dok=2,
            item_type=ItemType.MC,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=correct_letter,
            answer_latex=correct_letter,
            worked_solution=worked,
            choices=choices,
            context_scenario="equivalent expression via combining like terms",
            seed=self.base_seed * 1000 + 300 + variant_idx,
            stem_index=3,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 4: At Proficiency - NR (DOK 2, Easy)
    # Apply distributive property: e.g., 3(2x + 5) = 6x + 15
    # ================================================================

    def stem4_at_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(4, variant_idx)

        var = rng.choice(["x", "y", "n", "m", "p"])

        # Generate a(bx + c) where a, b, c are whole numbers
        a = int(gen.whole_number(2, 8))
        b = int(gen.whole_number(1, 6))
        c = int(gen.whole_number(1, 10))

        product_ab = a * b
        product_ac = a * c

        factored = f"{a}({b}{var} + {c})"
        expanded = f"{product_ab}{var} + {product_ac}"

        # Randomly choose direction: expand or factor
        if rng.random() < 0.6:
            # Expand
            stem_text = (
                f"Use the distributive property to expand the expression.\n\n"
                f"  {factored}"
            )
            answer_text = expanded
            worked = (
                f"{factored}\n"
                f"= {a} * {b}{var} + {a} * {c}\n"
                f"= {product_ab}{var} + {product_ac}"
            )
        else:
            # Factor
            stem_text = (
                f"Use the distributive property to write an equivalent expression "
                f"in factored form.\n\n"
                f"  {expanded}"
            )
            answer_text = factored
            worked = (
                f"{expanded}\n"
                f"GCF of {product_ab} and {product_ac} is {a}\n"
                f"= {a}({product_ab // a}{var} + {product_ac // a})\n"
                f"= {factored}"
            )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.AT, ItemType.NR,
                               Difficulty.EASY, 4, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.AT,
            difficulty=Difficulty.EASY,
            dok=2,
            item_type=ItemType.NR,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=answer_text,
            answer_latex=f"${answer_text}$",
            worked_solution=worked,
            context_scenario="distributive property",
            seed=self.base_seed * 1000 + 400 + variant_idx,
            stem_index=4,
            variant_index=variant_idx
        )

    # ================================================================
    # STEM 5: Above Proficiency - NR (DOK 3, Easy)
    # Write equivalent expression using multiple properties
    # ================================================================

    def stem5_above_nr(self, variant_idx: int) -> GeneratedQuestion:
        gen, rng = self._make_gen(5, variant_idx)

        var = rng.choice(["x", "y", "n", "m"])

        # Generate a more complex expression that requires multiple steps
        # Form: a(bx + c) + dx + e
        a = int(gen.whole_number(2, 5))
        b = int(gen.whole_number(1, 4))
        c = int(gen.whole_number(1, 6))
        d = int(gen.whole_number(1, 5))
        e = int(gen.whole_number(1, 8))

        # Expanded form: abx + ac + dx + e = (ab+d)x + (ac+e)
        total_coeff = a * b + d
        total_const = a * c + e

        original = f"{a}({b}{var} + {c}) + {d}{var} + {e}"
        simplified = f"{total_coeff}{var} + {total_const}"

        stem_text = (
            f"Simplify the expression completely.\n\n"
            f"  {original}\n\n"
            f"Show your simplified expression."
        )

        answer_text = simplified

        worked = (
            f"Step 1: Apply distributive property\n"
            f"  {a}({b}{var} + {c}) = {a * b}{var} + {a * c}\n\n"
            f"Step 2: Rewrite the expression\n"
            f"  {a * b}{var} + {a * c} + {d}{var} + {e}\n\n"
            f"Step 3: Combine like terms\n"
            f"  Variable terms: {a * b}{var} + {d}{var} = {total_coeff}{var}\n"
            f"  Constant terms: {a * c} + {e} = {total_const}\n\n"
            f"Result: {simplified}"
        )

        qid = make_question_id(STANDARD_CODE, ProficiencyLevel.ABOVE, ItemType.NR,
                               Difficulty.EASY, 5, variant_idx)

        return GeneratedQuestion(
            question_id=qid,
            standard_code=STANDARD_CODE,
            proficiency_level=ProficiencyLevel.ABOVE,
            difficulty=Difficulty.EASY,
            dok=3,
            item_type=ItemType.NR,
            stem_text=stem_text,
            stem_latex=stem_text,
            answer_text=answer_text,
            answer_latex=f"${answer_text}$",
            worked_solution=worked,
            context_scenario="simplify using multiple properties",
            seed=self.base_seed * 1000 + 500 + variant_idx,
            stem_index=5,
            variant_index=variant_idx
        )

    # ================================================================
    # MAIN GENERATION METHODS
    # ================================================================

    def generate_all_variants(self, variants_per_stem: int = VARIANTS_PER_STEM) -> list[GeneratedQuestion]:
        all_questions = []
        stem_methods = [
            self.stem1_below_mc,
            self.stem2_below_nr,
            self.stem3_approaching_mc,
            self.stem4_at_nr,
            self.stem5_above_nr,
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
            4: self.stem4_at_nr,
            5: self.stem5_above_nr,
        }
        fn = stem_methods.get(stem_index)
        if not fn:
            raise ValueError(f"Invalid stem index: {stem_index}. Must be 1-5.")
        return [fn(v) for v in range(variants_per_stem)]


if __name__ == "__main__":
    print("Generating 6.NS.7 question variants...")
    gen = Stem6NS7(seed=42)
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
