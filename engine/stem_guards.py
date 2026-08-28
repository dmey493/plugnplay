# -*- coding: utf-8 -*-
"""Guards that keep a generated question well formed.

Several stems derive all four answer options from one small parameter draw, so
an unlucky draw makes two of them render identically. Real examples found by
engine/check_stems.py:

    6.RP.2 stem 1   a == b, so "earned $6 for 6 hours" appears twice
    6.AF.5 stem 1   two coordinate distractors both land on (-1, -1)
    6.RP.3 stem 2   two ratio distractors both reduce to 2:2

A multiple-choice question with the same text twice has no defensible key, and
these were shipping to teachers.

The fix is deliberately NOT to invent a replacement option, which would put an
answer choice in front of a student that the stem's author never wrote. Instead
we re-roll the variant from a nudged seed: same stem, same structure, same
pedagogy, just not the degenerate parameter draw.
"""
import functools


def distinct_choices(fn):
    """Re-roll a stem variant whose answer choices are not all distinct.

    The nudged variant index is kept on the returned question so its
    question_id stays unique and stable for a given seed, which is what the
    review flow relies on when it rebuilds a PDF from stored ids.

    If every attempt collides the last one is returned rather than raising:
    a slightly flawed question beats a blank worksheet, and check_stems.py
    will still report it.
    """
    @functools.wraps(fn)
    def wrapper(self, variant_idx, *args, **kwargs):
        question = None
        for attempt in range(8):
            idx = variant_idx if attempt == 0 else variant_idx + 1000 * attempt
            question = fn(self, idx, *args, **kwargs)
            if not question.choices:
                return question
            texts = [c.text for c in question.choices]
            if len(set(texts)) == len(texts):
                return question
        return question

    return wrapper
