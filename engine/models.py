"""
Data models for the ILEARN Math Question Generator.
All question types, proficiency levels, and data structures.
"""

from dataclasses import dataclass, field
from fractions import Fraction
from enum import Enum
from typing import Optional


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    DIFFICULT = "difficult"


class ProficiencyLevel(Enum):
    BELOW = "below"
    APPROACHING = "approaching"
    AT = "at"
    ABOVE = "above"


class ItemType(Enum):
    MC = "multiple_choice"        # 4 options, 1 correct
    MS = "multiple_select"        # 5-7 options, 2-4 correct
    NR = "numeric_response"       # text entry, numeric answer
    EQ = "equation_response"      # text entry, equation answer
    MP = "multi_part"             # Part A + Part B
    ER = "extended_response"      # open-ended + rubric
    TI = "table_input"            # fill in table cells
    DD = "drag_and_drop"          # drag items to targets
    TM = "table_matching"         # match items in table


@dataclass
class RationalNumber:
    """Represents a nonnegative rational number with display formatting."""
    value: Fraction
    display_as: str  # "whole", "decimal", "fraction", "mixed"

    def __post_init__(self):
        if isinstance(self.value, (int, float)):
            self.value = Fraction(self.value).limit_denominator(1000)
        if self.value < 0:
            raise ValueError(f"RationalNumber must be nonnegative, got {self.value}")

    @property
    def is_whole(self) -> bool:
        return self.value.denominator == 1

    @property
    def as_whole(self) -> Optional[int]:
        if self.is_whole:
            return int(self.value)
        return None

    @property
    def as_decimal_str(self) -> str:
        f = float(self.value)
        if f == int(f):
            return str(int(f))
        return f"{f:g}"

    @property
    def as_fraction_str(self) -> str:
        if self.is_whole:
            return str(int(self.value))
        return f"{self.value.numerator}/{self.value.denominator}"

    @property
    def as_mixed_str(self) -> str:
        if self.is_whole:
            return str(int(self.value))
        whole = int(self.value)
        remainder = self.value - whole
        if whole == 0:
            return f"{remainder.numerator}/{remainder.denominator}"
        return f"{whole} {remainder.numerator}/{remainder.denominator}"

    def display(self) -> str:
        """Return the number formatted according to its display_as mode."""
        if self.display_as == "whole":
            return str(int(self.value)) if self.is_whole else self.as_decimal_str
        elif self.display_as == "decimal":
            return self.as_decimal_str
        elif self.display_as == "fraction":
            return self.as_fraction_str
        elif self.display_as == "mixed":
            return self.as_mixed_str
        return str(self.value)

    def latex(self) -> str:
        """Return LaTeX representation."""
        if self.display_as == "whole":
            return str(int(self.value)) if self.is_whole else self.as_decimal_str
        elif self.display_as == "decimal":
            return self.as_decimal_str
        elif self.display_as == "fraction":
            if self.is_whole:
                return str(int(self.value))
            return f"\\frac{{{self.value.numerator}}}{{{self.value.denominator}}}"
        elif self.display_as == "mixed":
            if self.is_whole:
                return str(int(self.value))
            whole = int(self.value)
            remainder = self.value - whole
            if whole == 0:
                return f"\\frac{{{remainder.numerator}}}{{{remainder.denominator}}}"
            return f"{whole}\\frac{{{remainder.numerator}}}{{{remainder.denominator}}}"
        return str(self.value)

    def __str__(self):
        return self.display()

    def __repr__(self):
        return f"RationalNumber({self.value}, '{self.display_as}')"


@dataclass
class QuestionChoice:
    """A single choice in a multiple-choice question."""
    key: str               # "a", "b", "c", "d"
    text: str              # plain text
    text_latex: str         # LaTeX formatted
    is_correct: bool
    distractor_rationale: Optional[str] = None
    render_data: Optional[dict] = None  # Special rendering (e.g., number_line diagrams)


@dataclass
class QuestionPart:
    """A part in a multi-part question (Part A, Part B, etc.)."""
    label: str             # "Part A", "Part B"
    prompt: str            # plain text prompt
    prompt_latex: str       # LaTeX formatted prompt
    answer: str            # plain text answer
    answer_latex: str       # LaTeX formatted answer
    item_type: ItemType    # type of this specific part


@dataclass
class GeneratedQuestion:
    """A complete generated question with all metadata."""
    question_id: str                # e.g., "6AF3-BL-EQ-D-001"
    standard_code: str              # e.g., "6.AF.3"
    proficiency_level: ProficiencyLevel
    difficulty: Difficulty
    dok: int                        # Depth of Knowledge (1-3)
    item_type: ItemType
    stem_text: str                  # plain text question
    stem_latex: str                 # LaTeX formatted question
    answer_text: str                # plain text answer
    answer_latex: str               # LaTeX formatted answer
    worked_solution: str            # step-by-step solution
    choices: Optional[list[QuestionChoice]] = None
    parts: Optional[list[QuestionPart]] = None
    context_scenario: Optional[str] = None  # description of the scenario used
    seed: Optional[int] = None      # for reproducibility
    stem_index: Optional[int] = None  # which stem template (1-7 for 6.AF.3)
    variant_index: Optional[int] = None  # which variant (0-19)
    render_data: Optional[dict] = None  # Special rendering (e.g., rectangle_diagram)

    @property
    def id_short(self) -> str:
        """Short display ID like '6AF3-AT-MP-E-003'."""
        return self.question_id


def make_question_id(standard_code: str, proficiency: ProficiencyLevel,
                     item_type: ItemType, difficulty: Difficulty,
                     stem_idx: int, variant_idx: int) -> str:
    """Generate a unique question ID.

    Format: {grade}{domain}{num}-{proficiency}-{type}-{difficulty}-{stem}{variant}
    Example: 6AF3-AT-MP-E-S5V003
    """
    code = standard_code.replace(".", "")
    prof_map = {"below": "BL", "approaching": "AP", "at": "AT", "above": "AB"}
    type_map = {
        "multiple_choice": "MC", "multiple_select": "MS",
        "numeric_response": "NR", "equation_response": "EQ",
        "multi_part": "MP", "extended_response": "ER",
        "table_input": "TI", "drag_and_drop": "DD", "table_matching": "TM"
    }
    diff_map = {"easy": "E", "medium": "M", "difficult": "D"}

    prof = prof_map[proficiency.value]
    typ = type_map[item_type.value]
    diff = diff_map[difficulty.value]

    return f"{code}-{prof}-{typ}-{diff}-S{stem_idx}V{variant_idx:03d}"
