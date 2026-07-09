"""
Answer validator for generated questions.
Every question is validated before output to ensure mathematical correctness,
content limit compliance, and proper formatting.
"""

from fractions import Fraction
from typing import Optional
from engine.models import (
    GeneratedQuestion, Difficulty, ItemType,
    ProficiencyLevel, RationalNumber
)
from engine.number_generators import ALLOWED_DENOMINATORS, is_hand_computable


class ValidationError(Exception):
    """Raised when a generated question fails validation."""
    pass


class AnswerValidator:
    """Validates generated questions against item spec constraints."""

    @staticmethod
    def validate_6af3(question: GeneratedQuestion, x: Fraction, p: Fraction,
                      q: Fraction, equation_form: str) -> list[str]:
        """Validate a 6.AF.3 question against all constraints.

        Returns list of error messages (empty = valid).
        """
        errors = []

        # 1. All values must be nonnegative rational
        for name, val in [("x", x), ("p", p), ("q", q)]:
            if val < 0:
                errors.append(f"{name} = {val} is negative (must be nonneg)")
            if not isinstance(val, Fraction):
                errors.append(f"{name} is not a Fraction")

        # 2. Verify equation form is valid
        valid_forms = ["add", "subtract", "multiply", "divide"]
        if equation_form not in valid_forms:
            errors.append(f"Invalid equation form: {equation_form}")

        # 3. Verify the equation is correct
        if equation_form == "add":
            if x + p != q:
                errors.append(f"Equation check failed: {x} + {p} != {q}")
        elif equation_form == "subtract":
            if x - p != q:
                errors.append(f"Equation check failed: {x} - {p} != {q}")
        elif equation_form == "multiply":
            if p * x != q:
                errors.append(f"Equation check failed: {p} * {x} != {q}")
        elif equation_form == "divide":
            if p != 0 and x / p != q:
                errors.append(f"Equation check failed: {x} / {p} != {q}")
            if p == 0:
                errors.append("Division by zero: p = 0")

        # 4. Verify difficulty tier matches number types
        diff = question.difficulty
        if diff == Difficulty.EASY:
            for name, val in [("x", x), ("p", p), ("q", q)]:
                if val.denominator != 1:
                    errors.append(f"Easy difficulty but {name} = {val} is not a whole number")
        elif diff == Difficulty.MEDIUM:
            # At least one should be non-whole, or all whole is ok too
            pass  # Medium allows mix of whole and decimals
        # Difficult: fractions/mixed/decimals expected - no strict check needed

        # 5. Verify hand-computability (no calculator for 6.AF.3)
        for name, val in [("x", x), ("p", p), ("q", q)]:
            if not is_hand_computable(val):
                errors.append(f"{name} = {val} may not be hand-computable (denom={val.denominator})")

        # 6. For MC items, verify choices
        if question.item_type == ItemType.MC and question.choices:
            correct_count = sum(1 for c in question.choices if c.is_correct)
            if correct_count != 1:
                errors.append(f"MC item has {correct_count} correct choices (expected 1)")
            if len(question.choices) != 4:
                errors.append(f"MC item has {len(question.choices)} choices (expected 4)")
            # Check for duplicate choices
            texts = [c.text for c in question.choices]
            if len(set(texts)) != len(texts):
                errors.append("MC item has duplicate choice texts")

        # 7. For multi-part items, verify parts exist
        if question.item_type == ItemType.MP:
            if not question.parts or len(question.parts) < 2:
                errors.append("Multi-part item must have at least 2 parts")

        # 8. Verify DOK is valid
        if question.dok not in [1, 2, 3]:
            errors.append(f"Invalid DOK: {question.dok}")

        return errors

    @staticmethod
    def validate_question(question: GeneratedQuestion) -> list[str]:
        """Generic validation for any question (standard-agnostic checks)."""
        errors = []

        # Required fields
        if not question.question_id:
            errors.append("Missing question_id")
        if not question.standard_code:
            errors.append("Missing standard_code")
        if not question.stem_text.strip():
            errors.append("Empty stem text")
        if not question.answer_text.strip():
            errors.append("Empty answer text")

        # MC must have choices
        if question.item_type == ItemType.MC and not question.choices:
            errors.append("MC item has no choices")

        # MP must have parts
        if question.item_type == ItemType.MP and not question.parts:
            errors.append("MP item has no parts")

        return errors


def validate_and_report(question: GeneratedQuestion,
                        x: Optional[Fraction] = None,
                        p: Optional[Fraction] = None,
                        q: Optional[Fraction] = None,
                        equation_form: Optional[str] = None) -> tuple[bool, list[str]]:
    """Validate a question and return (is_valid, errors).

    Runs both generic and standard-specific validation.
    """
    errors = AnswerValidator.validate_question(question)

    if question.standard_code == "6.AF.3" and x is not None:
        errors.extend(AnswerValidator.validate_6af3(question, x, p, q, equation_form))

    return (len(errors) == 0, errors)
