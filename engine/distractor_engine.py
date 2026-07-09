"""
Distractor engine for generating plausible wrong answers.
Uses common student error patterns to create realistic distractors
for multiple-choice items.
"""

import random
from fractions import Fraction
from typing import Optional

from engine.models import RationalNumber


class DistractorEngine:
    """Generates plausible wrong answers for MC items based on common student errors."""

    def __init__(self, rng: Optional[random.Random] = None):
        self.rng = rng or random.Random()

    def for_equation_solve(self, correct_x: Fraction, p: Fraction, q: Fraction,
                           equation_form: str, display_as: str = "whole") -> list[RationalNumber]:
        """Generate 3 distractors for 'Solve the equation' items.

        Uses common student errors specific to each equation form:
        - add: student adds instead of subtracts, or multiplies
        - subtract: student subtracts instead of adds
        - multiply: student adds or subtracts instead of divides
        - divide: student divides instead of multiplies

        Args:
            correct_x: the correct answer
            p, q: equation parameters
            equation_form: "add", "subtract", "multiply", "divide"
            display_as: how to format the numbers

        Returns:
            List of 3 RationalNumber distractors
        """
        candidates = set()

        if equation_form == "add":
            # x + p = q, correct: x = q - p
            candidates.add(p + q)           # adds instead of subtracts
            candidates.add(p * q)           # multiplies
            candidates.add(abs(p - q) + 1)  # off by one from correct

        elif equation_form == "subtract":
            # x - p = q, correct: x = q + p
            candidates.add(abs(q - p))      # subtracts wrong direction
            candidates.add(q * p)           # multiplies
            if q > p:
                candidates.add(q - p)       # subtracts instead of adds

        elif equation_form == "multiply":
            # px = q, correct: x = q/p
            candidates.add(q - p)           # subtracts instead of divides
            candidates.add(q + p)           # adds instead of divides
            candidates.add(q * p)           # multiplies instead of divides
            # Reciprocal error (divides p by q instead)
            if q != 0:
                candidates.add(Fraction(p, q) if isinstance(p, int) else p / q)

        elif equation_form == "divide":
            # x/p = q, correct: x = p*q
            candidates.add(abs(q - p))      # subtracts
            if p != 0:
                candidates.add(Fraction(q, p) if isinstance(q, int) else q / p)  # divides wrong way
            candidates.add(q + p)           # adds instead of multiplies

        # Remove correct answer and negatives
        candidates.discard(correct_x)
        candidates = {c for c in candidates if c >= 0 and c != correct_x}

        # Pad to 3 if needed using offset strategy
        attempts = 0
        while len(candidates) < 3 and attempts < 20:
            offset = self.rng.choice([1, 2, -1, -2, Fraction(1, 2), Fraction(-1, 2)])
            candidate = correct_x + offset
            if candidate >= 0 and candidate != correct_x:
                candidates.add(candidate)
            attempts += 1

        # Still not enough? Use multiples
        while len(candidates) < 3:
            mult = self.rng.choice([2, 3, Fraction(1, 2)])
            candidate = correct_x * mult
            if candidate >= 0 and candidate != correct_x and candidate not in candidates:
                candidates.add(candidate)

        # Take exactly 3
        distractors = list(candidates)
        self.rng.shuffle(distractors)
        distractors = distractors[:3]

        return [RationalNumber(d, display_as) for d in distractors]

    def for_equation_selection(self, correct_equation: str, x: Fraction,
                               p: Fraction, q: Fraction,
                               equation_form: str, var: str = "x") -> list[str]:
        """Generate 3 wrong equation strings for 'Select the equation' items.

        Common modeling errors:
        - Wrong operation
        - Swapped roles of variable and constant
        - Reversed order

        Returns:
            List of 3 wrong equation strings
        """
        p_str = self._format_val(p)
        q_str = self._format_val(q)
        x_str = self._format_val(x)

        wrong_equations = set()

        if equation_form == "add":
            # Correct: var + p = q
            wrong_equations.add(f"{p_str} + {q_str} = {var}")     # adds both knowns
            wrong_equations.add(f"{p_str}{var} = {q_str}")         # multiplies instead
            wrong_equations.add(f"{p_str} - {var} = {q_str}")     # subtracts instead

        elif equation_form == "subtract":
            # Correct: var - p = q
            wrong_equations.add(f"{var} + {p_str} = {q_str}")     # adds instead
            wrong_equations.add(f"{p_str} - {var} = {q_str}")     # swapped
            wrong_equations.add(f"{p_str}{var} = {q_str}")         # multiplies

        elif equation_form == "multiply":
            # Correct: p*var = q
            wrong_equations.add(f"{var} + {p_str} = {q_str}")     # adds instead
            wrong_equations.add(f"{var} - {p_str} = {q_str}")     # subtracts instead
            wrong_equations.add(f"{q_str}{var} = {p_str}")         # swapped p and q

        elif equation_form == "divide":
            # Correct: var/p = q
            wrong_equations.add(f"{var} \\cdot {p_str} = {q_str}")  # multiplies instead
            wrong_equations.add(f"{p_str}/{var} = {q_str}")          # flipped
            wrong_equations.add(f"{var} + {p_str} = {q_str}")       # adds instead

        # Remove correct equation
        wrong_equations.discard(correct_equation)

        result = list(wrong_equations)
        self.rng.shuffle(result)
        return result[:3]

    def for_which_equation_has_solution(self, target_x: Fraction,
                                        correct_equation: str,
                                        display_as: str = "fraction") -> list[str]:
        """Generate 3 wrong equations for 'Which equation has solution x = V?' items.

        Creates equations that look similar but have different solutions.
        """
        wrong = set()
        x_val = target_x

        # Generate equations with close but wrong solutions
        # Addition equations: a + x = b where b - a != target_x
        for _ in range(5):
            a = Fraction(self.rng.randint(1, 10))
            b = a + x_val + self.rng.choice([Fraction(1), Fraction(-1), Fraction(2)])
            if b > 0 and b - a != x_val:
                wrong.add(f"{a} + x = {b}")

        # Multiplication equations: ax = b where b/a != target_x
        for _ in range(5):
            a = Fraction(self.rng.randint(2, 10))
            b = a * (x_val + self.rng.choice([Fraction(1), Fraction(-1)]))
            if b > 0 and b / a != x_val:
                wrong.add(f"{a}x = {b}")

        # Subtraction equations
        for _ in range(5):
            a = Fraction(self.rng.randint(1, 10))
            b = a - x_val + self.rng.choice([Fraction(1), Fraction(-1)])
            if b >= 0 and a - b != x_val:
                wrong.add(f"{a} - x = {b}")

        wrong.discard(correct_equation)
        result = list(wrong)
        self.rng.shuffle(result)
        return result[:3]

    @staticmethod
    def _format_val(val: Fraction) -> str:
        """Format a fraction for equation display."""
        if val.denominator == 1:
            return str(int(val))
        f = float(val)
        if f == int(f):
            return str(int(f))
        # Check if it's a clean decimal
        if val.denominator in [2, 4, 5, 10, 20, 25, 50, 100]:
            return f"{f:g}"
        return f"{val.numerator}/{val.denominator}"


def shuffle_choices(correct: str, correct_latex: str,
                    distractors: list, rng: random.Random,
                    distractor_rationales: Optional[list[str]] = None):
    """Shuffle correct answer and distractors into a, b, c, d choices.

    Returns:
        list of QuestionChoice objects
    """
    from engine.models import QuestionChoice

    items = [(correct, correct_latex, True, None)]
    for i, d in enumerate(distractors):
        if isinstance(d, RationalNumber):
            text = d.display()
            latex = d.latex()
        else:
            text = str(d)
            latex = str(d)
        rationale = distractor_rationales[i] if distractor_rationales and i < len(distractor_rationales) else None
        items.append((text, latex, False, rationale))

    rng.shuffle(items)

    choices = []
    for i, (text, latex, is_correct, rationale) in enumerate(items):
        key = chr(ord('a') + i)
        choices.append(QuestionChoice(
            key=key,
            text=text,
            text_latex=latex,
            is_correct=is_correct,
            distractor_rationale=rationale
        ))
    return choices
