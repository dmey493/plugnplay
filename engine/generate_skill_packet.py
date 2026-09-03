"""
Generate a skill intervention packet PDF using a gradual-release structure:
  Student pages:
    Page 1: Worked Example (1, fully solved by teacher) -> Diagnose (2) ->
            We Do (2, guided) -> You Do (3, independent)
    Page 2: Exit Ticket (2, on its own page so it's collectable) + Reflection

  Teacher companion (optional second half):
    Quick Reference (canonical error) -> Optional "Teaching Note" block
    sourced from the skill's `coaching_note` field -> Prereq check ->
    Vocabulary -> Concrete/visual -> per-question answer + watch-for +
    redirect script. NO per-question strategy boxes (those felt scripted).

Usage:
  echo '{"standard":"6.AF.1","skill_id":"6AF1-S1"}' | python engine/generate_skill_packet.py
"""

import json
import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.pdf_generator import (
    MathPDF, PAGE_MARGIN,
    SB_YELLOW, SB_BROWN, SB_DARK, SB_FOOTER_HEIGHT,
    _draw_sb_header, _STRUGGLE_QUOTES,
)


def _clean(text):
    """Replace unicode chars that basic fonts can't handle."""
    return (text
            .replace('\u2014', '--')
            .replace('\u2013', '-')
            .replace('\u2018', "'")
            .replace('\u2019', "'")
            .replace('\u201c', '"')
            .replace('\u201d', '"')
            .replace('\u2026', '...')
            .replace('\u00d7', 'x')
            .replace('\u00f7', '/')
            # Deliberately NOT stripped: U+2212 MINUS SIGN and
            # U+2192 RIGHTWARDS ARROW. Arial carries both and the
            # PDF is Unicode. A hyphen beside a numeral reads as a
            # dash; '->' reads as two punctuation marks.
            )


def clean_dict(d):
    if isinstance(d, str):
        return _clean(d)
    if isinstance(d, dict):
        return {k: clean_dict(v) for k, v in d.items()}
    if isinstance(d, list):
        return [clean_dict(item) for item in d]
    return d


PLD_BAND_LABELS = {
    "below": "Below Proficiency",
    "approaching": "Approaching Proficiency",
    "at": "At Proficiency",
    "above": "Above Proficiency",
}


def load_skill_data(standard_code, skill_id):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Bundled layout (engine ships inside the web app): skills at content/skills.
    # Fallbacks cover the original authoring dev data and monorepo web/ layouts.
    bundled_dir = os.path.join(base, "content", "skills")
    skills_dir = os.path.join(base, "authoring", "data", "skills")
    web_skills_dir = os.path.join(base, "web", "content", "skills")
    for d in [bundled_dir, skills_dir, web_skills_dir]:
        path = os.path.join(d, f"{standard_code}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for skill in data["skills"]:
                if skill["skill_id"] == skill_id:
                    return skill, data
    return None, None


def _draw_footer(pdf, standard_code, skill_name):
    footer_h = SB_FOOTER_HEIGHT
    footer_y = pdf.h - footer_h
    pdf.set_fill_color(*SB_YELLOW)
    pdf.rect(0, footer_y, pdf.w, footer_h, style="F")
    pdf.set_draw_color(*SB_BROWN)
    pdf.set_line_width(0.4)
    pdf.line(0, footer_y, pdf.w, footer_y)
    # Student pages repeat the first sentence frame here so the language is
    # still in reach during Your Turn (the callout only prints once, up in
    # the guided section). Companion pages keep the struggle quote —
    # `pdf._pnp_frame` is set for student pages and cleared before the
    # teacher pages.
    frame = getattr(pdf, "_pnp_frame", None)
    if frame:
        text = frame.strip()
        if len(text) > 70:
            cut = text[:70].rsplit(" ", 1)[0]
            text = cut + "..."
        left = f'Say it:  "{text}"'
    else:
        quote = _STRUGGLE_QUOTES[hash(standard_code + skill_name) % len(_STRUGGLE_QUOTES)]
        left = f'"{quote}"'
    pdf.set_text_color(*SB_BROWN)
    pdf.set_font(pdf.ff, "I", 7)
    pdf.set_xy(PAGE_MARGIN, footer_y + 2)
    pdf.cell(pdf.w * 0.55, 5, left)
    pdf.set_font(pdf.ff, "", 7)
    # The skill id has to be on the paper: a teacher holding a printed sheet
    # otherwise has no way to look the skill up in the app, and the routing
    # chips on the skill cards have nothing to match against.
    tag = getattr(pdf, "skill_tag", "") or ""
    label = (f"Plug N Play  |  {tag}  |  Page {pdf.page_no()}"
             if tag else f"Plug N Play  |  Page {pdf.page_no()}")
    lw = pdf.get_string_width(label)
    pdf.set_xy(pdf.w - PAGE_MARGIN - lw, footer_y + 2)
    pdf.cell(lw, 5, label)
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_line_width(0.3)


def _section_label(pdf, label, usable_w):
    """Bold section header like DIAGNOSE, PRACTICE, EXIT TICKET."""
    pdf.set_font(pdf.ff, "B", 12)
    pdf.set_text_color(*SB_DARK)
    pdf.set_x(PAGE_MARGIN)
    pdf.cell(usable_w, 7, label, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(pdf.ff, "I", 8)
    pdf.set_text_color(120, 120, 120)


# --- Column helpers -------------------------------------------------------
# Student-handout sections render in two columns to use page space well.
# Renderers below read `pdf._pnp_col_x` / `pdf._pnp_col_w` and fall back to
# full-width (PAGE_MARGIN / pdf usable width) when the page is in single-
# column mode (e.g., the teacher companion).
def _col_x(pdf):
    return getattr(pdf, "_pnp_col_x", PAGE_MARGIN)

def _col_w(pdf):
    w = getattr(pdf, "_pnp_col_w", None)
    if w is None:
        return pdf.w - 2 * PAGE_MARGIN
    return w

def _set_column(pdf, side, gutter=6):
    """Switch the renderer's notion of left margin / column width.
    side ∈ {"left", "right", "full"}.
    """
    full = pdf.w - 2 * PAGE_MARGIN
    if side == "full":
        pdf._pnp_col_x = PAGE_MARGIN
        pdf._pnp_col_w = full
        return
    col_w = (full - gutter) / 2
    if side == "left":
        pdf._pnp_col_x = PAGE_MARGIN
    else:
        pdf._pnp_col_x = PAGE_MARGIN + col_w + gutter
    pdf._pnp_col_w = col_w

def _render_two_column_block(pdf, items, q_num_start, render_fn):
    """Render `items` across two columns, ROW BY ROW.

    The previous implementation pre-split items into "first half left, second
    half right" — that broke when the left column overflowed before the right
    column had been rendered (the right column landed on the wrong page).

    Row-by-row: for each pair (left_item, right_item) we
      1. decide if the row fits in remaining page space — page-break before
         the row if not (so both halves of the row stay on the same page),
      2. render left column at `row_y`, capture y_left_end,
      3. render right column at `row_y`, capture y_right_end,
      4. advance y to max(y_left_end, y_right_end) for the next row.

    Numbering reads left → right, top → bottom: 1L 2R / 3L 4R / 5L 6R …
    """
    if not items:
        return q_num_start

    qn = q_num_start
    page_bottom_safe = pdf.h - SB_FOOTER_HEIGHT - 8
    # Items above this estimated height get promoted to a full-width row —
    # too tall for a column to hold cleanly (long word problems, multi-part
    # items, big tables). Threshold ~ half a usable page.
    FULL_WIDTH_THRESHOLD = 110

    # We manage page breaks at the row level. If fpdf2's auto-page-break is
    # also on, it can fire DURING a render and add an extra page, leaving
    # blank pages between rows. Disable it for the duration of this block
    # and restore on exit.
    saved_auto = pdf.auto_page_break
    saved_margin = pdf.b_margin
    pdf.set_auto_page_break(auto=False)

    i = 0
    while i < len(items):
        left_item = items[i]
        left_h = _estimate_item_height(left_item)

        # Long items render full-width on their own row.
        if left_h >= FULL_WIDTH_THRESHOLD:
            if pdf.get_y() + left_h + 4 > page_bottom_safe:
                _draw_footer(pdf, getattr(pdf, "_pnp_standard", ""),
                             getattr(pdf, "_pnp_skill_name", ""))
                pdf.add_page()
            _set_column(pdf, "full")
            render_fn(pdf, qn, left_item, _col_w(pdf))
            qn += 1
            i += 1
            continue

        right_item = items[i + 1] if i + 1 < len(items) else None
        # If the right item alone is too tall for a column, render the
        # left as a full-width single (no pairing) so the right one can
        # take its own full-width row next iteration.
        if right_item is not None and _estimate_item_height(right_item) >= FULL_WIDTH_THRESHOLD:
            if pdf.get_y() + left_h + 4 > page_bottom_safe:
                _draw_footer(pdf, getattr(pdf, "_pnp_standard", ""),
                             getattr(pdf, "_pnp_skill_name", ""))
                pdf.add_page()
            _set_column(pdf, "full")
            render_fn(pdf, qn, left_item, _col_w(pdf))
            qn += 1
            i += 1
            continue

        # Page-break if the row won't fit. Use the taller of the two as the
        # row's reserved height.
        row_h = left_h + 4
        if right_item is not None:
            row_h = max(row_h, _estimate_item_height(right_item) + 4)
        if pdf.get_y() + row_h > page_bottom_safe:
            _draw_footer(pdf, getattr(pdf, "_pnp_standard", ""),
                         getattr(pdf, "_pnp_skill_name", ""))
            pdf.add_page()

        row_y = pdf.get_y()

        # Left column
        _set_column(pdf, "left")
        pdf.set_y(row_y)
        render_fn(pdf, qn, left_item, _col_w(pdf))
        qn += 1
        y_left_end = pdf.get_y()

        # Right column (if present) starts at the SAME row_y on the SAME page.
        y_right_end = row_y
        if right_item is not None:
            _set_column(pdf, "right")
            pdf.set_y(row_y)
            render_fn(pdf, qn, right_item, _col_w(pdf))
            qn += 1
            y_right_end = pdf.get_y()

        # Reset to full-width and advance y past the taller of the two.
        _set_column(pdf, "full")
        pdf.set_y(max(y_left_end, y_right_end))

        i += 2

    # Restore auto-page-break to whatever the caller had configured.
    pdf.set_auto_page_break(auto=saved_auto, margin=saved_margin)

    return qn


# ── Print design tokens ─────────────────────────────────────────────
# One quiet, editorial vocabulary for the whole sheet: a small rounded
# tinted chip names each section, a hairline rule carries the eye across,
# and content sits on plain white with a thin accent bar where a block
# needs grouping. No boxes-in-boxes.
RULE_GRAY = (216, 219, 226)
ANNOT_GRAY = (112, 117, 128)
LINE_GRAY = (150, 154, 162)   # student writing lines

# Uniform mastery rule printed in every companion's NEXT STEPS box so the
# advance-vs-reteach decision rests on a stated criterion, not an undefined
# "pass" of a 2-item exit ticket (review priority #2).
MASTERY_CRITERION = (
    "Mastered = BOTH Show-What-You-Know items correct AND a sound written "
    "explanation. 1 or fewer correct (or a shaky explanation) → reteach this "
    "skill before advancing."
)

# One-line dosage/pacing guidance so a coach can score fidelity and a teacher
# can run a fixed pull-out block (review priority #6).
SESSION_DOSAGE = (
    "Session at a glance: ~30 min, 3-5x/week, groups of 3-5. Pacing -- fluency 3 / "
    "Watch & learn 5 / Let's try together 7 / Your turn 8 / exit 5 min. "
    "Short on time? Cut in this order -- Remember these, then the LEVEL UP items, "
    "then Find the mistake. Never cut the exit ticket: it is the only measure. "
    "Recheck placement about every 6 sessions."
)

# v4 pacing: Watch & learn gains the micro-checks, Let's try together is the
# guided faded problem (not a 3-item set), Your turn ends with Find the Mistake.
SESSION_DOSAGE_V4 = (
    "Session at a glance: ~30 min, 3-5x/week, groups of 3-5. Pacing -- fluency 3 / "
    "Watch & learn + checks 6 / You finish it 4 / Let's try together 5 / "
    "Your turn + Find the mistake 8 / exit 4 min. "
    "Short on time? Cut in this order -- Remember these, then the LEVEL UP items, "
    "then Find the mistake. Never cut the exit ticket: it is the only measure. "
    "Recheck placement about every 6 sessions."
)

# The closed menu of thinking moves (schema_version 4 micro-checks). Student-
# facing names teachers can call out ("do your Name the Trap"). The enum ids
# are the only values valid in `worked_solution.steps[*].check.move`
# (validate_content.py Gate 6). See authoring/directives/skill_authoring/
# thinking_moves.md for the glossary.
THINKING_MOVES = {
    "spot_signal": "Spot the Signal",
    "show_it":     "Show It",
    "call_it":     "Call It",
    "say_why":     "Say Why",
    "check_it":    "Check It",
    "name_trap":   "Name the Trap",
}


def _chip_header(pdf, label, subtitle, tint, ink, usable_w):
    """Section header: rounded tinted chip + hairline rule to the right
    margin, optional italic subtitle underneath."""
    ff = pdf.ff
    y0 = pdf.get_y()
    pdf.set_font(ff, "B", 9.5)
    bw = pdf.get_string_width(label) + 9
    pdf.set_fill_color(*tint)
    pdf.rect(PAGE_MARGIN, y0, bw, 6.5, style="F",
             round_corners=True, corner_radius=3.2)
    pdf.set_xy(PAGE_MARGIN, y0 + 0.7)
    pdf.set_text_color(*ink)
    pdf.cell(bw, 5.2, label, align="C")
    pdf.set_draw_color(*RULE_GRAY)
    pdf.set_line_width(0.25)
    pdf.line(PAGE_MARGIN + bw + 4, y0 + 3.4, PAGE_MARGIN + usable_w, y0 + 3.4)
    pdf.set_y(y0 + 8.2)
    if subtitle:
        pdf.set_font(ff, "I", 8)
        pdf.set_text_color(*ANNOT_GRAY)
        pdf.set_x(PAGE_MARGIN)
        pdf.cell(usable_w, 4, subtitle, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(0.5)
    pdf.set_text_color(*SB_DARK)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)


def _accent_bar(pdf, x, y_top, y_bottom, ink):
    """Thin vertical accent bar grouping a block, in place of a full box."""
    pdf.set_fill_color(*ink)
    pdf.rect(x, y_top, 1.1, max(2, y_bottom - y_top), style="F",
             round_corners=True, corner_radius=0.55)


def _is_short_answer_item(item):
    """True when an open-response item only needs a short answer line
    (a one-word classification like "Addition") rather than a work area.
    Anything that involves computing, writing, or explaining gets space
    to show thinking."""
    stem_text = (item.get("stem") or "").strip().lower()
    answer_text = str(item.get("answer") or "").strip()
    one_word = len(answer_text) <= 14 and "\n" not in answer_text
    classification = "operation" in stem_text and "expression" not in stem_text
    return classification and one_word


def _write_student_question(pdf, num, item, usable_w):
    """Write a question on the student sheet.

    Handles diagrams (number_line / coordinate_grid / svg) via render_data
    and multi-part (Part A / Part B) prompts via the parts array. Authored
    items have neither and fall through to the simple stem + choices path.
    """
    ff = pdf.ff
    col_x = _col_x(pdf)
    # Per-question page-break logic only fires in single-column mode.
    # In two-column mode the caller (_render_two_column_block) does row-level
    # page breaks; if we ALSO break here we'd page-break in the middle of a
    # row and the right column would land on the wrong page.
    in_columns = getattr(pdf, "_pnp_col_w", None) is not None and \
                 abs(pdf._pnp_col_w - (pdf.w - 2 * PAGE_MARGIN)) > 1
    if not in_columns:
        # Reserve enough space for this question — if it won't fit on the
        # current page, break to the next page so the question stays whole.
        needed = _estimate_item_height(item) + 4
        page_bottom_safe = pdf.h - SB_FOOTER_HEIGHT - 8
        if pdf.get_y() + needed > page_bottom_safe:
            _draw_footer(pdf, getattr(pdf, "_pnp_standard", ""),
                         getattr(pdf, "_pnp_skill_name", ""))
            pdf.add_page()
    # Stretch items get a small "LEVEL UP" chip so a quick finisher sees a
    # signposted challenge instead of undifferentiated practice (review #10).
    if item.get("difficulty") == "stretch":
        _cy = pdf.get_y()
        pdf.set_font(ff, "B", 6.5)
        pdf.set_fill_color(255, 237, 213)   # orange-100
        pdf.set_text_color(154, 52, 18)     # orange-800
        _chip = "LEVEL UP"
        _cw = pdf.get_string_width(_chip) + 5
        pdf.rect(col_x, _cy, _cw, 4, style="F", round_corners=True, corner_radius=2)
        pdf.set_xy(col_x, _cy + 0.4)
        pdf.cell(_cw, 3.2, _chip, align="C")
        pdf.set_y(_cy + 4.8)
        pdf.set_draw_color(0, 0, 0)
        pdf.set_text_color(*SB_DARK)

    pdf.set_font(ff, "B", 10)
    pdf.set_text_color(*SB_DARK)
    pdf.set_x(col_x)
    pdf.cell(7, 5, f"{num}", new_x="RIGHT", new_y="TOP")

    # Stem text — uses the math-aware writer so a/b fractions render as
    # stacked numerator-over-denominator and ^N renders as superscript.
    pdf.set_font(ff, "", 10)
    stem = item.get("stem", "")
    _write_text_or_math(pdf, stem, x=col_x + 9,
                        max_width=usable_w - 9, font_size=10)

    # Error-analysis items: boxed "student work" + find-and-fix prompts
    # with workspace. Renders its own tail, so return early.
    if item.get("type") == "error_analysis" and item.get("shown_work"):
        # Draw the item's diagram first (if any) — the flawed work often
        # refers to a figure.
        ea_rd = item.get("render_data")
        if ea_rd:
            pdf.ln(1)
            rd_top = pdf.get_y()
            h = _draw_render_data(pdf, col_x + 8, rd_top, ea_rd,
                                  max_width=usable_w - 16)
            if h:
                pdf.set_y(rd_top + h + 2)
        pdf.ln(1.5)
        y_box = pdf.get_y()
        box_x = col_x + 8
        box_w = usable_w - 12
        pdf.set_fill_color(252, 245, 245)
        pdf.set_draw_color(228, 180, 180)
        pdf.set_line_width(0.3)
        pdf.set_xy(box_x + 2, y_box + 1.5)
        pdf.set_font(ff, "B", 7)
        pdf.set_text_color(153, 27, 27)
        pdf.cell(0, 3.5, "STUDENT WORK", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(ff, "B", 10)
        pdf.set_text_color(*SB_DARK)
        for line in item["shown_work"]:
            pdf.set_x(box_x + 4)
            _write_text_or_math(pdf, str(line), x=box_x + 4,
                                max_width=box_w - 8, font_size=10)
            pdf.ln(0.5)
        y_box_end = pdf.get_y() + 1.5
        pdf.rect(box_x, y_box, box_w, y_box_end - y_box, style="D",
                 round_corners=True, corner_radius=2)
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.3)
        pdf.set_y(y_box_end + 2)
        pdf.set_font(ff, "", 9)
        pdf.set_x(col_x + 8)
        pdf.multi_cell(usable_w - 12, 4.5,
                       "Circle the mistake in the work above. Then fix it:",
                       new_x="LMARGIN", new_y="NEXT")
        pdf.ln(18)
        pdf.set_x(col_x + 8)
        pdf.set_font(ff, "B", 9)
        pdf.set_text_color(*ANNOT_GRAY)
        aw = pdf.get_string_width("Correct answer:") + 2
        pdf.cell(aw, 5, "Correct answer:", new_x="RIGHT", new_y="TOP")
        pdf.set_draw_color(*LINE_GRAY)
        pdf.set_line_width(0.3)
        pdf.line(pdf.get_x() + 2, pdf.get_y() + 4,
                 col_x + usable_w * 0.8, pdf.get_y() + 4)
        pdf.set_draw_color(0, 0, 0)
        pdf.set_text_color(*SB_DARK)
        pdf.set_font(ff, "", 10)
        pdf.ln(8)
        pdf.ln(4)
        return

    # Diagram (number line, coordinate grid, SVG figure) — drawn beneath the
    # stem before the choices.
    rd = item.get("render_data")
    if rd:
        pdf.ln(1)
        # Capture y BEFORE the diagram. Some renderers (data_table)
        # leave pdf.y at the last row, not at the bottom — so we can't
        # rely on `pdf.get_y()` after the call to compute the bottom edge.
        rd_top = pdf.get_y()
        h = _draw_render_data(pdf, col_x + 8, rd_top, rd,
                              max_width=usable_w - 16)
        if h:
            pdf.set_y(rd_top + h + 2)

    # Multi-part prompts (Part A, Part B). Each part may have its own answer
    # line; we don't render answers here (student copy).
    parts = item.get("parts") or []
    if parts:
        for p in parts:
            label = p.get("label", "Part")
            prompt = p.get("prompt", "")
            pdf.set_font(ff, "B", 10)
            pdf.set_x(col_x + 5)
            pdf.cell(0, 5, label, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font(ff, "", 10)
            pdf.set_x(col_x + 8)
            pdf.multi_cell(usable_w - 11, 5, prompt, new_x="LMARGIN", new_y="NEXT")
            # Answer line per part (write-in space)
            pdf.ln(1)
            pdf.set_draw_color(*LINE_GRAY)
            pdf.set_line_width(0.3)
            pdf.line(col_x + 10, pdf.get_y() + 3,
                     col_x + usable_w * 0.7, pdf.get_y() + 3)
            pdf.set_draw_color(0, 0, 0)
            pdf.ln(7)

    choices = item.get("choices")
    choices_render = item.get("choices_render")
    if choices and not parts:
        labels = ["a", "b", "c", "d", "e", "f"]
        pdf.ln(1)
        for j, choice in enumerate(choices):
            lbl = labels[j] if j < len(labels) else str(j + 1)
            cr = choices_render[j] if (choices_render and j < len(choices_render)) else None
            pdf.set_font(ff, "", 10)
            if cr:
                # Choice carries its own diagram (e.g. number-line MC).
                pdf.set_x(col_x + 10)
                pdf.cell(8, 5, f"{lbl}.", new_x="RIGHT", new_y="TOP")
                cr_top = pdf.get_y()
                h = _draw_render_data(pdf, col_x + 18, cr_top, cr,
                                      max_width=usable_w - 28)
                if h:
                    pdf.set_y(cr_top + h + 2)
                else:
                    pdf.ln(5)
            else:
                pdf.set_x(col_x + 10)
                pdf.multi_cell(usable_w - 12, 5, f"{lbl}.  {choice}",
                               new_x="LMARGIN", new_y="NEXT")
    elif not parts and not choices:
        # If the question is a data-table item (Yes/No truth table etc.), the
        # student writes inside the table that was just rendered — no answer
        # line or workspace needed below it.
        rd_type_local = (rd or {}).get("type") if isinstance(rd, dict) else None
        if rd_type_local == "data_table":
            pass
        else:
            # Open-response: every item gets a real work area + labeled
            # answer line so students can show steps. The single short line
            # is reserved for classification prompts with one-word answers
            # ("What operation ...?" -> "Addition") where there is no work
            # to show.
            if _is_short_answer_item(item):
                pdf.ln(3)
                pdf.set_x(col_x + 8)
                pdf.set_draw_color(*LINE_GRAY)
                pdf.set_line_width(0.3)
                pdf.line(col_x + 8, pdf.get_y() + 3, col_x + usable_w * 0.6, pdf.get_y() + 3)
                pdf.set_draw_color(0, 0, 0)
                pdf.ln(8)
            else:
                # Blank work area then an answer line so the final answer has
                # one obvious home. A figure already gives the student spatial
                # context (and figure items are usually read-off / light work),
                # so those get a compact work area; pure-computation items get
                # the full ~5 handwriting lines to show steps.
                pdf.ln(14 if item.get("render_data") else 26)
                pdf.set_x(col_x + 8)
                pdf.set_font(ff, "B", 9)
                pdf.set_text_color(*ANNOT_GRAY)
                aw = pdf.get_string_width("Answer:") + 2
                pdf.cell(aw, 5, "Answer:", new_x="RIGHT", new_y="TOP")
                pdf.set_draw_color(*LINE_GRAY)
                pdf.set_line_width(0.3)
                pdf.line(pdf.get_x() + 2, pdf.get_y() + 4,
                         col_x + usable_w * 0.75, pdf.get_y() + 4)
                pdf.set_draw_color(0, 0, 0)
                pdf.set_text_color(*SB_DARK)
                pdf.set_font(ff, "", 10)
                pdf.ln(8)

    pdf.ln(4)


def _first_sentences(text, n=2):
    """Return at most the first n sentences of a block of text."""
    if not text:
        return ""
    parts = text.replace("\r\n", "\n").split("\n")
    # Take first non-empty paragraph
    paragraph = next((p.strip() for p in parts if p.strip()), "")
    # Split into sentences on ". "
    sentences = [s.strip() for s in paragraph.replace(". ", ".|").split("|") if s.strip()]
    snippet = " ".join(sentences[:n])
    return snippet


def _write_teacher_question(pdf, num, item, skill, _section_name, usable_w):
    """Write one item on the teacher companion. Column-aware: respects
    `_pnp_col_x` / `_pnp_col_w` so the caller can stack two items side-by-side.

    Per-skill guidance (canonical_error, redirect script) is printed ONCE
    in the Quick Reference at the top — not repeated under every item.
    Each item gets: question + answer + (engine source tag if applicable).
    """
    ff = pdf.ff
    col_x = _col_x(pdf)
    y_start = pdf.get_y()

    # Question number + stem
    pdf.set_font(ff, "B", 9)
    pdf.set_text_color(*SB_DARK)
    pdf.set_xy(col_x, y_start)
    pdf.cell(7, 4, f"{num}.")

    pdf.set_font(ff, "", 9)
    pdf.set_xy(col_x + 7, y_start)
    _write_text_or_math(pdf, item.get("stem", ""),
                        x=col_x + 7, max_width=usable_w - 10,
                        font_size=9)

    # Error-analysis items: show the flawed work so the key reads in context.
    if item.get("type") == "error_analysis" and item.get("shown_work"):
        pdf.set_font(ff, "I", 8)
        pdf.set_text_color(153, 27, 27)
        for line in item["shown_work"]:
            pdf.set_x(col_x + 10)
            pdf.multi_cell(usable_w - 13, 3.8, str(line),
                           new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*SB_DARK)

    # Diagram beneath the stem (number_line / coordinate_grid / SVG).
    # Capture y BEFORE the diagram — some renderers (data_table) leave
    # pdf.y at the last row, not the bottom. Without this guard the
    # caller advanced ~2× the table height per question (this was the S3
    # page bloat).
    rd = item.get("render_data")
    if rd:
        pdf.ln(0.5)
        rd_top = pdf.get_y()
        h = _draw_render_data(pdf, col_x + 8, rd_top, rd,
                              max_width=usable_w - 16)
        if h:
            pdf.set_y(rd_top + h + 1)

    # Multi-part prompts under the stem, with per-part answer.
    parts = item.get("parts") or []
    if parts:
        for p in parts:
            pdf.set_font(ff, "B", 9)
            pdf.set_text_color(*SB_DARK)
            pdf.set_x(col_x + 7)
            pdf.cell(0, 4, p.get("label", "Part"), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font(ff, "", 9)
            pdf.set_x(col_x + 10)
            pdf.multi_cell(usable_w - 13, 4.2, p.get("prompt", ""),
                           new_x="LMARGIN", new_y="NEXT")
            pdf.set_font(ff, "B", 9)
            pdf.set_text_color(30, 120, 50)
            pdf.set_x(col_x + 10)
            pdf.multi_cell(usable_w - 13, 4.5, f"Answer: {p.get('answer', '')}",
                           new_x="LMARGIN", new_y="NEXT")
            pdf.ln(0.5)
        pdf.set_text_color(*SB_DARK)

    # Show choices (if MC) with the correct one highlighted, no per-distractor
    # placeholder text.
    choices = item.get("choices")
    choices_render = item.get("choices_render")
    answer = item.get("answer", "")
    if choices and not parts:
        labels = ["a", "b", "c", "d", "e", "f"]
        for j, choice in enumerate(choices):
            lbl = labels[j] if j < len(labels) else str(j + 1)
            is_correct = (str(choice).strip() == str(answer).strip())
            cr = choices_render[j] if (choices_render and j < len(choices_render)) else None
            if is_correct:
                pdf.set_font(ff, "B", 9)
                pdf.set_text_color(0, 120, 0)
            else:
                pdf.set_font(ff, "", 9)
                pdf.set_text_color(110, 110, 110)
            if cr:
                pdf.set_x(col_x + 10)
                pdf.cell(8, 4, f"{lbl}.", new_x="RIGHT", new_y="TOP")
                cr_top = pdf.get_y()
                h = _draw_render_data(pdf, col_x + 18, cr_top, cr,
                                      max_width=usable_w - 28)
                if h:
                    pdf.set_y(cr_top + h + 1)
                else:
                    pdf.ln(4)
            else:
                pdf.set_x(col_x + 10)
                pdf.multi_cell(usable_w - 12, 4, f"{lbl}.  {choice}",
                               new_x="LMARGIN", new_y="NEXT")

    # Top-level answer line (skipped for multi-part — those have per-part answers).
    if not parts:
        pdf.ln(0.5)
        pdf.set_font(ff, "B", 9)
        pdf.set_text_color(30, 120, 50)
        pdf.set_x(col_x + 10)
        pdf.multi_cell(usable_w - 12, 4.5, f"Answer: {answer}",
                       new_x="LMARGIN", new_y="NEXT")

    # Engine-source tag — small grey pill so the teacher knows the
    # question came from the procedural engine vs an authored item.
    if item.get("_source") == "engine":
        pdf.set_font(ff, "I", 7)
        pdf.set_text_color(140, 140, 140)
        pdf.set_x(col_x + 10)
        pdf.cell(0, 3.5, "(engine-generated)", new_x="LMARGIN", new_y="NEXT")

    # Light separator to make rows scannable.
    pdf.ln(1.5)
    sep_y = pdf.get_y()
    pdf.set_draw_color(220, 220, 220)
    pdf.set_line_width(0.2)
    pdf.line(col_x, sep_y, col_x + usable_w, sep_y)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)
    pdf.set_text_color(*SB_DARK)
    pdf.ln(2)


# Map skill column → ProficiencyLevel value used by the question engine.
# Foundation skills are well below grade level; on-grade skills are at level;
# looking_forward skills are above. The engine's enum values are
# "below", "approaching", "at", "above".
_COLUMN_TO_PROFICIENCY = {
    "foundation":      "below",
    "looking_back":    "approaching",
    "on_grade":        "at",
    "looking_forward": "above",
}


_FRACTION_RE = __import__("re").compile(r"(?<![A-Za-z\d_/.])(-?\d+)/(\d+)(?![\d./])")


def _has_fractions(text):
    """True if `text` contains a/b that should render as a stacked fraction.

    We match `int/int` only, with negative-num support, and require word
    boundaries on both sides so we don't catch things like 'm/s' or '1/2/3'.
    """
    if not text:
        return False
    return bool(_FRACTION_RE.search(text))


def _write_text_or_math(pdf, text, x, max_width, font_style="", font_size=None):
    """Render `text` to the PDF starting at `(x, current_y)`.

    If the text contains fractions or exponents, route through the engine's
    `_write_line_with_math` (which draws stacked fractions and superscripts).
    Otherwise fall through to standard `multi_cell` for word-wrap.

    `_write_line_with_math` only renders ONE line (no wrap), so for long
    fraction-bearing stems we split on existing line breaks and call it
    per line. That covers our use case — engine stems with fractions are
    typically a single math line, sometimes preceded by a word-problem
    sentence.
    """
    if not text:
        return
    has_math = _has_fractions(text) or "^" in text
    if not has_math:
        pdf.set_x(x)
        pdf.multi_cell(max_width, 5, text, new_x="LMARGIN", new_y="NEXT")
        return

    # Split on existing newlines first; render each line through the math
    # writer. For lines that DON'T contain fractions/exponents, fall back to
    # multi_cell so word-wrap still works for long prose.
    for line in text.split("\n"):
        if not line:
            pdf.ln(2)
            continue
        if _has_fractions(line) or "^" in line:
            pdf._write_line_with_math(line, x, font_style=font_style,
                                      font_size=font_size, max_width=max_width)
        else:
            pdf.set_x(x)
            pdf.multi_cell(max_width, 5, line, new_x="LMARGIN", new_y="NEXT")


def _draw_render_data(pdf, x, y, render_data, max_width=120):
    """Draw a render_data block (number line, coordinate grid, SVG figure)
    using MathPDF's existing draw helpers. Returns the height consumed.

    These helpers are inherited from the engine's MathPDF — they operate on
    `self` (the pdf instance) so they work fine on our subclass too. We're
    just reusing what the Struggle Bus worksheet renderer already does
    instead of reimplementing.
    """
    if not render_data:
        return 0
    rd_type = render_data.get("type")

    # Diagrams have a default authored width (~80mm). When we're rendering
    # in a narrower column we shrink to fit, but with a floor that keeps the
    # diagram readable. If even the floor doesn't fit, the renderer trims to
    # `max_width` — better a slightly cramped line than overflow into the
    # next column.
    MIN_DIAGRAM_W = 70
    def _fit_w(default_w):
        target = render_data.get("width", default_w)
        if max_width and target > max_width:
            return max(MIN_DIAGRAM_W, min(target, max_width))
        return target

    try:
        if rd_type == "number_line":
            return pdf._draw_number_line(
                x, y,
                value=render_data.get("value", 0),
                circle_type=render_data.get("circle_type", "closed"),
                direction=render_data.get("direction", "right"),
                width=_fit_w(80),
                blank=render_data.get("blank", False),
            )
        if rd_type == "number_line_point":
            return pdf._draw_number_line_point(
                x, y,
                ticks=render_data.get("ticks", []),
                point_value=render_data.get("point_value"),
                point_label=render_data.get("point_label", "P"),
                points=render_data.get("points"),
                width=_fit_w(80),
            )
        if rd_type == "double_number_line":
            kwargs = {k: v for k, v in render_data.items()
                      if k in ("top_label", "bottom_label")}
            kwargs["width"] = _fit_w(render_data.get("width", 80))
            return pdf._draw_double_number_line(
                x, y,
                top_ticks=render_data.get("top_ticks", []),
                bottom_ticks=render_data.get("bottom_ticks", []),
                **kwargs,
            )
        if rd_type == "coordinate_grid":
            kw = {}
            if "grid_size" in render_data:
                kw["grid_size"] = render_data["grid_size"]
            if "label_step" in render_data:
                kw["label_step"] = render_data["label_step"]
            if "hide_labels" in render_data:
                kw["hide_labels"] = render_data["hide_labels"]
            return pdf._draw_coordinate_grid(
                x, y,
                x_range=render_data.get("x_range", (-10, 10)),
                y_range=render_data.get("y_range", (-10, 10)),
                points=render_data.get("points", []),
                lines=render_data.get("lines", []),
                **kw,
            )
        if rd_type == "data_table":
            # Yes/No truth table, etc. The MathPDF helper already does column
            # sizing; we pass max_width so it fits the column.
            return pdf._draw_data_table(
                x, y,
                headers=render_data.get("headers", []),
                rows=render_data.get("rows", []),
                orientation=render_data.get("orientation", "vertical"),
                compact=render_data.get("compact", False),
                max_width=max_width,
            )
        if rd_type == "svg_html" or render_data.get("svg_html"):
            svg = render_data.get("svg_html") or ""
            if not svg:
                return 0
            return pdf._render_svg_figure(x, y, svg,
                                          max_width=max_width,
                                          max_height=80)
        # Parametric shape figures (geometry/measurement stems): convert to
        # SVG with the worksheet renderer's own converters, then draw.
        svg = _shape_render_data_to_svg(render_data)
        if svg:
            return pdf._render_svg_figure(x, y, svg,
                                          max_width=max_width,
                                          max_height=80)
    except Exception:
        # Fail soft — better to skip a diagram than break the whole packet.
        return 0
    return 0


def _shape_render_data_to_svg(render_data):
    """Convert parametric shape render_data (composite_shape,
    polygon_angles, rectangular_prism) to an SVG string using the
    converters the worksheet renderer already ships. Returns None for
    non-shape types."""
    rd_type = (render_data or {}).get("type")
    try:
        from engine.pdf_generator import (
            _composite_shape_to_svg,
            _polygon_angles_to_svg,
            _rectangular_prism_to_svg,
        )
        if rd_type == "composite_shape":
            return _composite_shape_to_svg(render_data)
        if rd_type == "polygon_angles":
            return _polygon_angles_to_svg(render_data)
        if rd_type == "rectangular_prism":
            return _rectangular_prism_to_svg(render_data)
    except Exception:
        return None
    return None


def _estimate_render_height(render_data):
    """Conservative height estimate for a render_data block. Used by the
    page-break logic so questions with diagrams don't get orphaned at the
    bottom of a page."""
    if not render_data:
        return 0
    rd_type = render_data.get("type")
    if rd_type in ("number_line", "number_line_point"):
        return 18
    if rd_type == "double_number_line":
        return 26
    if rd_type == "coordinate_grid":
        # _draw_coordinate_grid returns ~grid_size + axis labels; default
        # grid_size is 55mm, so reserve 70 conservatively.
        return render_data.get("grid_size", 55) + 18
    if rd_type == "data_table":
        # Header row (~7mm) + data rows (~7mm each) + a little padding.
        rows = render_data.get("rows") or []
        return 10 + (len(rows) + 1) * 7
    if rd_type == "svg_html" or render_data.get("svg_html"):
        return 80
    if rd_type in ("composite_shape", "polygon_angles", "rectangular_prism"):
        return 65
    return 20


def _engine_question_to_sample_item(q):
    """Convert a GeneratedQuestion from the engine into the sample_items
    shape the renderer expects.

    Carries (in addition to the basic stem/answer/choices):
      - stem_latex: LaTeX-rendered stem so superscripts/fractions display correctly.
      - render_data: number_line, coordinate_grid, svg_html, etc. — drives
        the diagram dispatch in _write_engine_question.
      - parts: multi-part (Part A / Part B) sub-prompts.
      - item_type: MC / MS / NR / EQ / MP / TM / TI etc. (string form).
      - choices_render: per-choice render_data (e.g. number-line choices).
    """
    # "[FIGURE]" is a worksheet-renderer positioning sentinel; the packet
    # and projection draw the diagram from render_data, so strip the token
    # from visible text.
    def _strip_fig(text):
        return _clean(text).replace("[FIGURE]", "").replace("  ", " ").strip()

    item = {
        "stem": _strip_fig(getattr(q, "stem_text", "") or ""),
        "answer": _strip_fig(getattr(q, "answer_text", "") or ""),
        "stem_latex": _strip_fig(getattr(q, "stem_latex", "") or ""),
        "answer_latex": _strip_fig(getattr(q, "answer_latex", "") or ""),
    }
    raw_choices = getattr(q, "choices", None)
    if raw_choices:
        item["choices"] = [_clean(c.text) for c in raw_choices]
        # Carry per-choice render_data so number-line-as-choice items work.
        choices_render = []
        any_render = False
        for c in raw_choices:
            cr = getattr(c, "render_data", None)
            choices_render.append(cr)
            if cr:
                any_render = True
        if any_render:
            item["choices_render"] = choices_render
        for c in raw_choices:
            if c.is_correct:
                item["answer"] = _clean(c.text)
                break

    rd = getattr(q, "render_data", None)
    if rd:
        item["render_data"] = rd

    parts = getattr(q, "parts", None)
    if parts:
        item["parts"] = [
            {
                "label": p.label,
                "prompt": _clean(p.prompt or ""),
                "prompt_latex": _clean(getattr(p, "prompt_latex", "") or ""),
                "answer": _clean(p.answer or ""),
                "item_type": getattr(p.item_type, "value", str(p.item_type)),
            }
            for p in parts
        ]

    it_type = getattr(q, "item_type", None)
    if it_type is not None:
        item["item_type"] = getattr(it_type, "value", str(it_type))
    return item


def _load_stem_class(standard_code):
    """Dynamically load the stem generator class for a standard code.

    Bypasses the bulk import in engine/generate_worksheet.py — that file has
    one bad-cased import (stem_7GM3) that crashes the whole module load on
    case-sensitive imports. We do the import ourselves with importlib and
    a couple of casing fallbacks.

    Returns None if no stem class can be found for the given standard.
    """
    import importlib

    # "6.AF.1" -> "6af1"; "7.DSP.4" -> "7dsp4"
    code = standard_code.replace(".", "").lower()
    candidate_modules = [
        f"engine.stems.stem_{code}",
        # Try original case in case the file is uppercased (stem_7GM3.py).
        f"engine.stems.stem_{standard_code.replace('.', '')}",
    ]
    candidate_classes = [
        # Stem6AF1, Stem7DSP4, etc.
        "Stem" + standard_code.replace(".", ""),
    ]

    for mod_name in candidate_modules:
        try:
            mod = importlib.import_module(mod_name)
        except Exception:
            continue
        for cls_name in candidate_classes:
            cls = getattr(mod, cls_name, None)
            if cls is not None:
                return cls
    return None


def _fill_items_from_engine(skill, standard_code, target_count=10, session=1,
                            exclude_stems=None):
    """Build a deterministic problem set for this skill + session.

    Two sessions = two non-overlapping problem sets for the same skill.
    Session 1 gets the first `target_count` items, session 2 gets the next
    `target_count`. Same (skill_id, session) → same items every time, so a
    teacher who prints session 1 in the morning and projects session 1 in
    the afternoon sees identical problems.

    Strategy:
      1. Authored items (from skill.sample_items) come first, in order.
      2. Engine fill (deterministic, seeded by skill_id) is appended to
         build a master pool of at least 2 * target_count unique items.
      3. We then slice [(session-1)*target_count : session*target_count]
         from that master pool. Authored items are intentionally given to
         session 1 first (they're the highest-quality on-skill items).

    Failures are silent — if the engine import or generation throws, we
    return whatever items we already had. The packet still renders, just
    with fewer items.
    """
    def _stem_key(text):
        """Match stems by content, not by typing. The same problem is authored
        with different internal spacing in different blocks ('Write < or >:  105
        __ 89' in the ladder, single-spaced in sample_items), so exact matching
        silently let duplicates through."""
        return " ".join((text or "").split()).casefold()

    _excluded_stems = {_stem_key(s) for s in (exclude_stems or []) if s and s.strip()}
    # sample_items must be filtered too, not just practice_problems: most of
    # the ladder-problem reprints came from here, and an unfiltered
    # sample_items[0] is exactly what the exit ticket draws from first.
    authored = [it for it in (skill.get("sample_items", []) or [])
                if _stem_key(it.get("stem")) not in _excluded_stems]
    # Strip any stale _source tags from authored items (they shouldn't
    # have one, but defend against bad input).
    for it in authored:
        if it.get("_source") == "engine":
            it.pop("_source", None)

    # Fold in the curated practice_problems (v2 schema): hand-sequenced
    # items with a difficulty label (warm_up / core / stretch). They rank
    # as authored quality and their difficulty drives ordering in
    # _allocate_items. Dedupe against sample_items by stem.
    # Stems claimed by a dedicated slot elsewhere on the sheet (e.g. the v4
    # "Find the Mistake" item) are kept out of the pool so they can't print
    # twice.
    excluded = _excluded_stems
    seen = {_stem_key(it.get("stem")) for it in authored} | excluded
    diff_rank = {"warm_up": 0, "core": 1, "stretch": 2}
    curated = sorted(
        (p for p in (skill.get("practice_problems") or [])
         if (p.get("stem") or "").strip() and _stem_key(p.get("stem")) not in seen),
        key=lambda p: diff_rank.get(p.get("difficulty"), 1),
    )
    curated_items = [{
        "stem": p.get("stem", ""),
        "answer": p.get("answer", ""),
        "choices": None,
        "difficulty": p.get("difficulty"),
        # Conceptual item-type extensions (error_analysis, number_line).
        "type": p.get("type"),
        "shown_work": p.get("shown_work"),
        "render_data": p.get("render_data"),
    } for p in curated]
    # Insert after the first 3 sample_items (worked example + 2 exit slots)
    # so the curated ladder fills session 1's practice sections instead of
    # sitting past the session-1 slice at the end of a 20-item pool.
    authored = authored[:3] + curated_items + authored[3:]

    # We want at least 2 sessions worth of items in the master pool.
    master_target = target_count * 2

    engine_stems = skill.get("engine_stems") or []
    gen_class = _load_stem_class(standard_code) if engine_stems else None

    engine_items = []
    if engine_stems and gen_class is not None:
        # Seed includes the skill_id only — NOT the session — so the
        # master pool is stable. Slicing by session below produces the
        # disjoint sets.
        # IMPORTANT: use a stable hash (md5) not Python's built-in hash().
        # Python randomizes string hashes per-process for security, which
        # made the same skill produce different engine items in different
        # Python invocations — projection didn't match the printed packet.
        import hashlib
        seed_str = skill.get("skill_id", standard_code)
        seed = int(hashlib.md5(seed_str.encode("utf-8")).hexdigest()[:8], 16) % (2 ** 31 - 1)
        try:
            gen = gen_class(seed=seed)
        except Exception:
            gen = None

        if gen is not None:
            pool = []
            # Over-generate so duplicate-skipping has room to work and we
            # comfortably hit master_target unique items.
            per_stem = max(20, master_target)
            for stem_idx in engine_stems:
                variants = []
                # Some stem classes expose generate_stem_variants(idx, count);
                # others only expose _stemN(variant_idx). Try the convenience
                # method first, then fall back to direct method calls.
                try:
                    variants = gen.generate_stem_variants(stem_idx,
                                                          variants_per_stem=per_stem)
                except (AttributeError, NotImplementedError):
                    variants = []
                except Exception:
                    variants = []
                if not variants:
                    method = (getattr(gen, f"_stem{stem_idx}", None)
                              or getattr(gen, f"stem{stem_idx}", None))
                    if method is not None:
                        for v in range(per_stem):
                            try:
                                variants.append(method(v))
                            except Exception:
                                continue
                pool.extend(variants)

            # Keep deterministic generation order — difficulty ordering
            # happens per-section in _allocate_items, not by item format.
            ordered = pool

            # Skip duplicates of authored items and of each other.
            #
            # Key on the stem AND the choices. A multiple-choice stem often
            # holds the question constant and varies only the options
            # ("Which situation is best represented by a negative number?"),
            # so keying on stem text alone collapsed 20 distinct questions
            # into one and starved session 2.
            def _dedup_key(item):
                stem_text = (item.get("stem") or "").strip()
                choices = item.get("choices") or []
                if choices:
                    parts = []
                    for c in choices:
                        parts.append((c if isinstance(c, str)
                                      else getattr(c, "text", str(c))).strip())
                    return stem_text + "||" + "|".join(sorted(parts))
                return stem_text

            seen_stems = {_dedup_key(it) for it in authored}
            for q in ordered:
                new_item = _engine_question_to_sample_item(q)
                stem_text = (new_item.get("stem") or "").strip()
                key = _dedup_key(new_item)
                if not stem_text or key in seen_stems:
                    continue
                new_item["_source"] = "engine"
                engine_items.append(new_item)
                seen_stems.add(key)
                if len(authored) + len(engine_items) >= master_target:
                    break

    # Master pool: authored first (best-quality, sub-skill-matched), then
    # engine fillers in deterministic order.
    master_pool = authored + engine_items

    # Slice for the requested session.
    start = max(0, (session - 1)) * target_count
    end = start + target_count
    sliced = master_pool[start:end]

    # If session 2 has nothing (skill is sparse and engine couldn't fill),
    # silently fall back to wrapping into session 1's pool — better than
    # rendering an empty packet.
    if not sliced and master_pool:
        sliced = master_pool[:target_count]
    return sliced


def _allocate_items(items):
    """Slice the skill's items into the gradual-release sections.

    Target allocation: 1 worked example, 3 diagnose (Try It), 2 we do,
    2 you do, 2 exit = 10 items per session.

    SUB-SKILL FIDELITY: items tagged with `_source: "engine"` are
    procedurally generated at the *standard* level (e.g., 6.AF.1) — they're
    on-standard but not necessarily on-sub-skill. The Worked Example and
    Exit Ticket are the two sections where sub-skill alignment matters most
    (you're modeling THIS skill, then testing THIS skill at the end). So
    we hand authored items to those sections first; engine items are only
    used to fill out the middle (Try It / We Do / You Do).
    """
    if not items:
        return {"worked_example": [], "diagnose": [], "we_do": [],
                "you_do": [], "exit": []}

    # Split by source. Items without a `_source` field are authored.
    authored = [it for it in items if it.get("_source") != "engine"]
    engine = [it for it in items if it.get("_source") == "engine"]

    # ----------------------------------------------------------------
    # Step 1: Worked Example and Exit Ticket get authored items first.
    # ----------------------------------------------------------------
    we_section = []
    exit_section = []
    auth_idx = 0

    if auth_idx < len(authored):
        we_section = [authored[auth_idx]]
        auth_idx += 1

    # Exit Ticket wants 2; take what authored has, up to 2.
    exit_target = 2
    take = min(exit_target, len(authored) - auth_idx)
    if take > 0:
        exit_section = authored[auth_idx:auth_idx + take]
        auth_idx += take

    # ----------------------------------------------------------------
    # Step 2: Try It / We Do / You Do consume the rest of authored,
    # then engine fillers, in order. Allocation: 3 / 2 / 2.
    # ----------------------------------------------------------------
    middle = list(authored[auth_idx:]) + list(engine)

    # Order practice easy -> hard: curated items carry a difficulty label
    # (warm_up / core / stretch); everything else counts as core. Stable
    # sort preserves authored/engine order within a band.
    _diff_rank = {"warm_up": 0, "core": 1, "stretch": 2}
    middle.sort(key=lambda it: _diff_rank.get(it.get("difficulty"), 1))

    # Worked Example fallback: if no authored item filled the WE slot, take
    # the first engine item from `middle` so the packet still gets an
    # I-Do block. Better an engine-generated worked example than none.
    if not we_section and middle:
        we_section = [middle[0]]
        middle = middle[1:]

    diagnose_section = middle[0:3]
    we_do_section    = middle[3:5]
    you_do_section   = middle[5:7]

    # If Exit Ticket got nothing from authored (because authored < 3),
    # fall back to engine items so the packet still has an exit.
    if not exit_section and len(middle) > 7:
        exit_section = middle[7:9]

    return {
        "worked_example": we_section,
        "diagnose":       diagnose_section,
        "we_do":          we_do_section,
        "you_do":         you_do_section,
        "exit":           exit_section,
    }


def _resolve_fluency_items(skill, standard_data, count=12, session=1):
    """Warm-up items from ALREADY-MASTERED content (IES rec 6: brief timed
    practice on taught content only).

    Source priority: authored `fluency_warmup` override -> `fluency_source`
    skill id -> walk the prerequisite_skill chain to a foundation skill ->
    any foundation skill with short open-response items. Returns
    {"title", "items"} or None (block is skipped)."""
    override = skill.get("fluency_warmup")
    if override and override.get("items"):
        return {"title": override.get("title", "Fluency Sprint"),
                "items": override["items"][:count]}

    all_skills = {s.get("skill_id"): s for s in standard_data.get("skills", [])}

    src = None
    src_id = skill.get("fluency_source")
    if src_id and src_id in all_skills:
        src = all_skills[src_id]

    if src is None:
        cur = skill
        for _ in range(6):
            prev_id = (cur.get("prerequisite_skill") or {}).get("skill_id")
            if not prev_id or prev_id not in all_skills:
                cur = None
                break
            cur = all_skills[prev_id]
            if cur.get("column") == "foundation":
                break
        if cur is not None and cur.get("skill_id") != skill.get("skill_id"):
            src = cur

    def short_items(s):
        return [it for it in (s.get("sample_items") or [])
                if not it.get("choices") and len((it.get("stem") or "")) <= 48]

    if src is None or len(short_items(src)) < 6:
        for s in standard_data.get("skills", []):
            if s.get("column") == "foundation" and len(short_items(s)) >= 6:
                src = s
                break

    if src is None:
        return None
    pool = short_items(src)
    if len(pool) < 6:
        return None

    # Deterministic pick: same (skill, session) -> same sprint, session 2
    # gets a different slice.
    import hashlib
    seed = int(hashlib.md5(f"{skill.get('skill_id')}-fluency".encode()).hexdigest()[:8], 16)
    rnd = random.Random(seed)
    shuffled = list(pool)
    rnd.shuffle(shuffled)
    # Never print the same question twice in one timed sprint: a pool of 6-9
    # short items cannot fill 12 slots, and wrapping it silently repeated
    # items (every CP1 sheet did). Take at most one full pass of the pool.
    n = min(count, len(shuffled))
    start = ((session - 1) * n) % max(1, len(shuffled))
    picked = (shuffled + shuffled)[start:start + n]
    return {"title": src.get("name", "Fluency Sprint"), "items": picked}


def _write_fluency_block(pdf, fluency, usable_w):
    """Timed warm-up grid + 'Meet or Beat' self-graph boxes."""
    ff = pdf.ff

    _chip_header(pdf, "Fluency sprint",
                 "Quick warm-up on facts you already know. Your teacher will time you -- beat your best!",
                 (254, 243, 199), (146, 64, 14), usable_w)
    pdf.ln(1)

    # Item grid with a light writing blank per item. The column count adapts
    # to the LONGEST prompt so nothing overflows its cell into the neighbor
    # (ratio / "median of a, b, c, d" prompts are far longer than "4 + 5" and
    # used to collide in a fixed 3-column grid). Blank + padding are reserved
    # to the right of each prompt.
    items = fluency["items"]
    BLANK_W, CELL_PAD = 13.0, 5.0
    pdf.set_font(ff, "", 9)

    def _fluency_stem_w(stem):
        stem = (stem or "").strip()
        if _has_fractions(stem) or "^" in stem:
            return pdf._measure_math_line(stem, 9)
        return pdf.get_string_width(stem)

    max_w = max((_fluency_stem_w(it.get("stem")) for it in items), default=0)
    cols = 1
    for c in (3, 2, 1):
        if max_w <= (usable_w - 4) / c - (BLANK_W + CELL_PAD):
            cols = c
            break
    col_w = (usable_w - 4) / cols
    row_h = 9.5
    for r in range(0, len(items), cols):
        row = items[r:r + cols]
        y = pdf.get_y()
        for c, it in enumerate(row):
            x = PAGE_MARGIN + 2 + c * col_w
            stem = (it.get("stem") or "").strip()
            pdf.set_font(ff, "", 9)
            pdf.set_text_color(*SB_DARK)
            if _has_fractions(stem) or "^" in stem:
                # The math writer advances y; anchor it to the row and restore
                # so sibling cells and the answer blank stay on the same line.
                pdf.set_xy(x, y)
                pdf._write_line_with_math(stem, x, font_size=9)
                pdf.set_y(y)
            else:
                pdf.set_xy(x, y)
                pdf.cell(col_w - BLANK_W - CELL_PAD, 5, stem)
            pdf.set_draw_color(*LINE_GRAY)
            pdf.set_line_width(0.3)
            pdf.line(x + col_w - BLANK_W, y + 4, x + col_w - 4, y + 4)
        pdf.set_y(y + row_h)

    # Meet-or-Beat self-graph: 5 session boxes the student fills with
    # their score, so growth is visible to THEM (self-graphing, IES rec 6).
    pdf.ln(1.5)
    pdf.set_font(ff, "B", 8)
    pdf.set_text_color(146, 64, 14)
    pdf.set_x(PAGE_MARGIN + 2)
    pdf.cell(40, 5, "Meet or beat -- my score:")
    box_w, box_h = 14, 9
    bx = PAGE_MARGIN + 46
    by = pdf.get_y() - 1.5
    pdf.set_font(ff, "", 6.5)
    pdf.set_text_color(*ANNOT_GRAY)
    for i in range(5):
        x = bx + i * (box_w + 3)
        pdf.set_fill_color(252, 250, 243)
        pdf.set_draw_color(*RULE_GRAY)
        pdf.set_line_width(0.35)
        pdf.rect(x, by, box_w, box_h, style="DF",
                 round_corners=True, corner_radius=1.6)
        pdf.set_xy(x, by + box_h + 0.5)
        pdf.cell(box_w, 3, f"Session {i + 1}", align="C")
    pdf.set_y(by + box_h + 5)

    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)
    pdf.set_text_color(*SB_DARK)
    pdf.ln(4)


def _write_worked_solution(pdf, ws, usable_w):
    """TRUE worked example on the student page: stem + numbered, annotated
    solution steps (IES rec 1). Replaces the old blank-problem 'worked
    example' when the skill carries an authored `worked_solution`."""
    ff = pdf.ff

    _chip_header(pdf, "Watch & learn",
                 "Follow each step with your teacher.",
                 (219, 234, 254), (30, 64, 175), usable_w)
    pdf.ln(0.5)

    body_top = pdf.get_y()
    pdf.set_font(ff, "B", 10.5)
    _write_text_or_math(pdf, ws.get("stem", ""), x=PAGE_MARGIN + 5,
                        max_width=usable_w - 10, font_size=10.5)
    pdf.ln(2.5)

    # Draw the figure the example reasons about (L-shape, number line, etc.)
    # right where it's modeled — the "I do" anchor should be seen, not just
    # described (review priority #1). Additive: no render_data => no change.
    rd = ws.get("render_data")
    if rd:
        rd_top = pdf.get_y()
        h = _draw_render_data(pdf, PAGE_MARGIN + 8, rd_top, rd, max_width=usable_w - 20)
        if h:
            pdf.set_y(rd_top + h + 2)

    # Micro-checks (v4): steps may carry a `check` — a 5-second student
    # action from the closed thinking-moves menu. Letters run a/b/c over
    # the steps that HAVE checks (not every step gets one).
    def _draw_check(check, letter):
        """One micro-check row: checkbox, letter, move chip, prompt.

        Drawn ABOVE the step it belongs to. The page asks; the teacher
        leads the reveal. A student meets the question before the answer.
        """
        cy = pdf.get_y() + 0.8
        pdf.set_draw_color(30, 64, 175)
        pdf.set_line_width(0.35)
        pdf.rect(PAGE_MARGIN + 13, cy + 0.6, 3.2, 3.2, style="D",
                 round_corners=True, corner_radius=0.7)
        pdf.set_font(ff, "B", 8)
        pdf.set_text_color(30, 64, 175)
        pdf.set_xy(PAGE_MARGIN + 17.5, cy)
        pdf.cell(4, 4.4, f"{letter}.")
        move_label = THINKING_MOVES.get(check.get("move"),
                                        check.get("move") or "")
        pdf.set_font(ff, "B", 6.5)
        chip_w = pdf.get_string_width(move_label.upper()) + 4
        pdf.set_fill_color(219, 234, 254)
        pdf.rect(PAGE_MARGIN + 22, cy + 0.2, chip_w, 4, style="F",
                 round_corners=True, corner_radius=2)
        pdf.set_xy(PAGE_MARGIN + 22, cy + 0.4)
        pdf.cell(chip_w, 3.6, move_label.upper(), align="C")
        pdf.set_font(ff, "", 8)
        pdf.set_text_color(*SB_DARK)
        pdf.set_xy(PAGE_MARGIN + 22 + chip_w + 2, cy)
        pdf.multi_cell(usable_w - (22 + chip_w + 2) - 8, 4.4,
                       check.get("prompt", ""),
                       new_x="LMARGIN", new_y="NEXT")
        if pdf.get_y() < cy + 4.6:
            pdf.set_y(cy + 4.6)
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.3)

    check_letter = 0
    any_checks = any(s.get("check") for s in ws.get("steps", []))
    for i, step in enumerate(ws.get("steps", []), start=1):
        # Ask before revealing: the check for this step prints above it.
        check = step.get("check")
        if check and check.get("prompt"):
            _draw_check(check, chr(ord("a") + check_letter))
            check_letter += 1
        y = pdf.get_y()
        pdf.set_xy(PAGE_MARGIN + 6, y)
        pdf.set_font(ff, "B", 9)
        pdf.set_text_color(30, 64, 175)
        pdf.cell(6, 5, f"{i}.")
        pdf.set_font(ff, "B", 10)
        pdf.set_text_color(*SB_DARK)
        _write_text_or_math(pdf, step.get("math", "") or "", x=PAGE_MARGIN + 13,
                            max_width=usable_w - 60, font_size=10)
        ann = step.get("annotation", "")
        if ann:
            pdf.set_font(ff, "I", 8)
            pdf.set_text_color(*ANNOT_GRAY)
            pdf.set_x(PAGE_MARGIN + 13)
            pdf.multi_cell(usable_w - 20, 3.8, ann, new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(*SB_DARK)
        pdf.ln(1.5)

    ans = ws.get("answer", "")
    if ans:
        pdf.set_font(ff, "B", 9.5)
        pdf.set_text_color(21, 128, 61)
        full = f"Answer: {ans}"
        aw = pdf.get_string_width(full) + 8
        avail = usable_w - 12
        ay = pdf.get_y()
        pdf.set_fill_color(233, 249, 236)
        if aw <= avail:
            # Short answer: compact centered pill.
            pdf.rect(PAGE_MARGIN + 6, ay, aw, 6.5, style="F",
                     round_corners=True, corner_radius=3.2)
            pdf.set_xy(PAGE_MARGIN + 6, ay + 0.7)
            pdf.cell(aw, 5.2, full, align="C")
            pdf.set_y(ay + 7.5)
        else:
            # Long answer (e.g. a data-comparison explanation): wrap inside a
            # tinted panel so it never runs off the page. Count wrapped lines
            # first so the fill sits behind the text, not over it.
            pad, lh = 2.5, 5.0
            box_w = avail
            text_w = box_w - 2 * pad
            n_lines, cur = 1, ""
            for word in full.split(" "):
                cand = word if not cur else cur + " " + word
                if pdf.get_string_width(cand) > text_w and cur:
                    n_lines += 1
                    cur = word
                else:
                    cur = cand
            box_h = n_lines * lh + 2 * pad
            pdf.rect(PAGE_MARGIN + 6, ay, box_w, box_h, style="F",
                     round_corners=True, corner_radius=3.2)
            pdf.set_xy(PAGE_MARGIN + 6 + pad, ay + pad)
            pdf.multi_cell(text_w, lh, full, new_x="LMARGIN", new_y="NEXT")
            pdf.set_y(ay + box_h + 1)
        pdf.set_text_color(*SB_DARK)

    _accent_bar(pdf, PAGE_MARGIN + 1.2, body_top, pdf.get_y(), (147, 187, 245))
    pdf.ln(5)


def _write_fade_block(pdf, fe, usable_w, label, subtitle, tint, ink, bar_rgb):
    """Faded worked example: the given steps are printed, the missing ones
    become labeled blanks the student supplies (IES rec 1: strategically
    faded steps). Parameterized so the same block renders both fade rungs:
    "You finish it" (faded_example, last step blank) and "Let's try
    together" (guided_example, only the first step given)."""
    ff = pdf.ff

    _chip_header(pdf, label, subtitle, tint, ink, usable_w)
    pdf.ln(0.5)

    body_top = pdf.get_y()
    pdf.set_font(ff, "B", 10.5)
    _write_text_or_math(pdf, fe.get("stem", ""), x=PAGE_MARGIN + 5,
                        max_width=usable_w - 10, font_size=10.5)
    pdf.ln(2.5)

    # Same figure the student will finish from — drawn, not just described.
    rd = fe.get("render_data")
    if rd:
        rd_top = pdf.get_y()
        h = _draw_render_data(pdf, PAGE_MARGIN + 8, rd_top, rd, max_width=usable_w - 20)
        if h:
            pdf.set_y(rd_top + h + 2)

    for i, step in enumerate(fe.get("steps", []), start=1):
        y = pdf.get_y()
        pdf.set_xy(PAGE_MARGIN + 6, y)
        pdf.set_font(ff, "B", 9)
        pdf.set_text_color(*ink)
        pdf.cell(6, 5, f"{i}.")
        pdf.set_text_color(*SB_DARK)
        if step.get("given") and step.get("math"):
            pdf.set_font(ff, "B", 10)
            _write_text_or_math(pdf, step["math"], x=PAGE_MARGIN + 13,
                                max_width=usable_w - 60, font_size=10)
        else:
            # Blank step: writing line the student fills in.
            pdf.set_draw_color(*LINE_GRAY)
            pdf.set_line_width(0.3)
            pdf.line(PAGE_MARGIN + 13, y + 4, PAGE_MARGIN + usable_w * 0.55, y + 4)
            pdf.set_y(y + 6)
        ann = step.get("annotation", "")
        if ann:
            pdf.set_font(ff, "I", 8)
            pdf.set_text_color(*ANNOT_GRAY)
            pdf.set_x(PAGE_MARGIN + 13)
            pdf.multi_cell(usable_w - 20, 3.8, ann, new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(*SB_DARK)
        pdf.ln(1.5)

    _accent_bar(pdf, PAGE_MARGIN + 1.2, body_top, pdf.get_y(), bar_rgb)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)
    pdf.ln(5)


def _resolve_mixed_review(skill, standard_data, session=1, count=3):
    """Interleaved cumulative-review items from earlier skills in the
    progression (IES rec 1: mix previously learned problem types so
    students must discriminate). Prefers authored `mixed_review_items`;
    otherwise pulls core practice from the 1-2 nearest non-foundation
    ancestors in the prerequisite chain."""
    authored = skill.get("mixed_review_items") or []
    if authored:
        return [{
            "stem": it.get("stem", ""),
            "answer": it.get("answer", ""),
            "choices": it.get("choices"),
            "render_data": it.get("render_data"),
            "type": it.get("type"),
            "shown_work": it.get("shown_work"),
            "_mixed_source": it.get("source_skill_id", ""),
        } for it in authored[:count]]

    all_skills = {s.get("skill_id"): s for s in standard_data.get("skills", [])}
    ancestors = []
    cur = skill
    for _ in range(6):
        prev_id = (cur.get("prerequisite_skill") or {}).get("skill_id")
        if not prev_id or prev_id not in all_skills:
            break
        cur = all_skills[prev_id]
        if cur.get("column") != "foundation":
            ancestors.append(cur)
        if len(ancestors) >= 2:
            break
    if not ancestors:
        return []

    import hashlib
    seed = int(hashlib.md5(f"{skill.get('skill_id')}-mixed-{session}".encode()).hexdigest()[:8], 16)
    rnd = random.Random(seed)

    picked = []
    for anc in ancestors:
        pool = [p for p in (anc.get("practice_problems") or [])
                if p.get("difficulty") == "core"]
        if not pool:
            pool = [it for it in (anc.get("sample_items") or []) if it.get("stem")]
        if not pool:
            continue
        take = rnd.sample(pool, min(2 if len(ancestors) == 1 else 1 + (len(picked) == 0), len(pool)))
        for p in take:
            picked.append({
                "stem": p.get("stem", ""),
                "answer": p.get("answer", ""),
                "choices": p.get("choices"),
                "render_data": p.get("render_data"),
                "type": p.get("type"),
                "shown_work": p.get("shown_work"),
                "_mixed_source": anc.get("skill_id", ""),
            })
            if len(picked) >= count:
                return picked
    return picked


def _write_sentence_starters(pdf, starters, usable_w):
    """Small callout printed above the guided section: language frames the
    student uses to voice their reasoning (IES rec 2)."""
    if not starters:
        return
    ff = pdf.ff
    y0 = pdf.get_y()
    pdf.set_font(ff, "B", 8)
    pdf.set_text_color(30, 64, 175)
    pdf.set_xy(PAGE_MARGIN + 6, y0 + 1)
    pdf.cell(usable_w - 6, 4, "Say it like this:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(ff, "I", 8.5)
    pdf.set_text_color(*ANNOT_GRAY)
    for s in starters:
        pdf.set_x(PAGE_MARGIN + 6)
        pdf.multi_cell(usable_w - 12, 4, f'"{s}"', new_x="LMARGIN", new_y="NEXT")
    _accent_bar(pdf, PAGE_MARGIN + 1.2, y0 + 1, pdf.get_y(), (147, 187, 245))
    pdf.set_text_color(*SB_DARK)
    pdf.ln(3)


def _write_worked_example(pdf, item, i_do_script, usable_w, show_answer=False):
    """Render the Worked Example as a normal numbered question wrapped in a
    light blue header band + box outline.

    Inside the box we delegate to _write_student_question so the WE
    handles diagrams, multi-part, MC choices, and data tables identically
    to the practice items below. The student copy hides the answer; the
    teacher copy shows it via show_answer=True (still through the same
    question renderer)."""
    ff = pdf.ff
    if not item:
        return

    col_x = _col_x(pdf)

    _chip_header(pdf, "Watch & learn",
                 "Your teacher models this one -- follow along.",
                 (219, 234, 254), (30, 64, 175), usable_w)
    pdf.ln(0.5)
    y0 = pdf.get_y()

    # Render the question normally inside the box. The box gives a couple
    # mm of inner padding by inset of `col_x`; we set _pnp_col_x/_pnp_col_w
    # so _write_student_question's positioning math respects the inset.
    saved_x = getattr(pdf, "_pnp_col_x", None)
    saved_w = getattr(pdf, "_pnp_col_w", None)
    pdf._pnp_col_x = col_x + 3
    pdf._pnp_col_w = usable_w - 6
    _write_student_question(pdf, "EX", item, usable_w - 6)
    # Restore column state.
    if saved_x is not None:
        pdf._pnp_col_x = saved_x
    if saved_w is not None:
        pdf._pnp_col_w = saved_w

    # Teacher view — show the answer line + I-Do script under the question.
    if show_answer:
        answer = item.get("answer", "")
        if answer:
            pdf.set_x(col_x + 3)
            pdf.set_font(ff, "B", 10)
            pdf.set_text_color(30, 120, 50)
            pdf.multi_cell(usable_w - 6, 5, f"Answer: {answer}",
                           new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        if i_do_script:
            pdf.set_x(col_x + 3)
            pdf.set_font(ff, "I", 9)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(usable_w - 6, 4.5, i_do_script,
                           new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(*SB_DARK)

    # Accent bar (drawn last so it spans the rendered content).
    _accent_bar(pdf, col_x + 1.2, y0, pdf.get_y() + 1, (147, 187, 245))
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)
    pdf.set_text_color(*SB_DARK)
    pdf.ln(5)


def _write_printable_artifact_page(pdf, artifact, skill, standard_code, usable_w):
    """Render a single 'ready-to-cut' printable manipulative on its own page.

    Driven by the `printable_artifact` field on the skill JSON. Currently
    handles three kinds:
      - sort_cards: a grid of word/expression cards meant to be cut and
        sorted under category cards (e.g., keyword → operation).
      - chart: a blank chart with column headers (the student fills it in).
      - reference_card: a standalone anchor chart with title + bullets
        (e.g., a fact-fluency reference card).

    Each artifact gets its own page so it can be printed and used directly
    by the teacher — no 'go make this on chart paper' step."""
    if not artifact:
        return
    ff = pdf.ff
    # Force a clean page boundary. Disable auto-page-break so internal
    # draws (rect grids, dashed borders) don't trigger a stray extra page
    # when they nick the bottom margin. Also raise the bottom margin to 0
    # so fpdf2 has no threshold left to trip on.
    pdf.set_auto_page_break(auto=False, margin=0)
    pdf.add_page()

    title = artifact.get("title") or "Classroom Tool"
    instructions = artifact.get("instructions") or ""
    kind = (artifact.get("kind") or "").lower()

    # Top header — title + instructions for the teacher/student.
    pdf.set_font(ff, "B", 16)
    pdf.set_text_color(*SB_DARK)
    pdf.set_x(PAGE_MARGIN)
    pdf.cell(usable_w, 9, title, new_x="LMARGIN", new_y="NEXT")

    pdf.set_font(ff, "I", 9)
    pdf.set_text_color(110, 110, 110)
    pdf.set_x(PAGE_MARGIN)
    pdf.multi_cell(usable_w, 4.5,
                   f"For: {skill['name']} ({standard_code})",
                   new_x="LMARGIN", new_y="NEXT")
    if instructions:
        pdf.set_font(ff, "", 10)
        pdf.set_text_color(60, 60, 60)
        pdf.set_x(PAGE_MARGIN)
        pdf.multi_cell(usable_w, 5, instructions,
                       new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*SB_DARK)
    pdf.ln(4)

    if kind == "sort_cards":
        _render_sort_cards(pdf, artifact, usable_w)
    elif kind == "picture_sort":
        _render_picture_sort(pdf, artifact, usable_w)
    elif kind == "chart":
        _render_chart(pdf, artifact, usable_w)
    elif kind == "reference_card":
        _render_reference_card(pdf, artifact, usable_w)
    elif kind in _MASTER_RENDERERS:
        _MASTER_RENDERERS[kind](pdf, artifact, usable_w)
    else:
        # Unknown kind — fall back to a plain text panel so we don't fail.
        pdf.set_font(ff, "", 10)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(usable_w, 5,
                       artifact.get("body", "(printable artifact data missing)"),
                       new_x="LMARGIN", new_y="NEXT")

    _draw_footer(pdf, standard_code, skill["name"])


def _is_emoji_codepoint(cp: int) -> bool:
    """True for codepoints we want to render via the emoji fallback font.
    Roughly: any character beyond the BMP, plus the Miscellaneous Symbols
    + Dingbats blocks. Excludes basic Latin, Greek, math operators, arrows,
    geometric shapes — those should render in the primary font."""
    # Any char beyond BMP (>= U+10000) — most emoji live here.
    if cp >= 0x10000:
        return True
    # Miscellaneous Symbols (U+2600–U+26FF) and Dingbats (U+2700–U+27BF)
    if 0x2600 <= cp <= 0x27BF:
        return True
    return False


def _render_mixed_label_centered(pdf, x, y, w, h, label, base_font, base_size,
                                  emoji_font="NotoEmoji"):
    """Center-render a label in a (w, h) box, using `base_font` for primary
    text and `emoji_font` for emoji codepoints. Splits the label into
    (text, is_emoji) runs and measures each in its own font so the total
    width is correct, then draws each run at the right x position.

    Works around fpdf2's one-way fallback: once a fallback font activates
    inside a single cell, characters the fallback can't render are dropped.
    By segmenting up-front we keep each character on a font that has it."""
    # Split into runs — consecutive emoji or consecutive non-emoji.
    runs = []
    cur_text = ""
    cur_emoji = None
    for ch in label:
        is_e = _is_emoji_codepoint(ord(ch))
        if cur_emoji is None:
            cur_emoji = is_e
            cur_text = ch
        elif is_e == cur_emoji:
            cur_text += ch
        else:
            runs.append((cur_text, cur_emoji))
            cur_text = ch
            cur_emoji = is_e
    if cur_text:
        runs.append((cur_text, cur_emoji))

    # Measure total width by setting each font in turn.
    total_w = 0.0
    widths = []
    for text, is_e in runs:
        font = emoji_font if is_e else base_font
        try:
            pdf.set_font(font, "B" if not is_e else "", base_size)
        except Exception:
            pdf.set_font(base_font, "B", base_size)
        rw = pdf.get_string_width(text)
        widths.append(rw)
        total_w += rw

    # Render runs starting from the centered x.
    cur_x = x + (w - total_w) / 2
    # Vertical center-ish: cell-style baseline. fpdf2 places text at y +
    # font's ascender; for our cards we approximate with y + h/2 + size*0.35.
    text_y = y + h / 2 + base_size * 0.35
    for (text, is_e), rw in zip(runs, widths):
        font = emoji_font if is_e else base_font
        try:
            pdf.set_font(font, "B" if not is_e else "", base_size)
        except Exception:
            pdf.set_font(base_font, "B", base_size)
        pdf.text(cur_x, text_y, text)
        cur_x += rw

    # Restore primary font / weight for downstream callers.
    pdf.set_font(base_font, "B", base_size)


def _render_picture_sort(pdf, artifact, usable_w):
    """Picture-based sort. Each card carries a small visual scene (emoji
    or short pictographic string) instead of a vocabulary keyword. Same
    cut-and-sort workflow as sort_cards, but the cards are taller and the
    label font is larger so the picture reads from across a small group
    table.

    Schema: items is a list of {label, answer} objects. `answer` is the
    correct category for self-grading (renderer doesn't surface it on the
    student copy)."""
    ff = pdf.ff
    categories = artifact.get("categories") or []
    items = artifact.get("items") or []

    # Category header strip — same look as sort_cards so the two artifacts
    # feel like a family.
    if categories:
        n = len(categories)
        cw = usable_w / n
        ch = 18
        y0 = pdf.get_y()
        for i, cat in enumerate(categories):
            x0 = PAGE_MARGIN + i * cw
            pdf.set_fill_color(255, 247, 220)
            pdf.set_draw_color(180, 130, 20)
            pdf.set_line_width(0.6)
            pdf.rect(x0 + 1.5, y0, cw - 3, ch, style="DF")
            pdf.set_xy(x0, y0)
            pdf.set_font(ff, "B", 22)
            pdf.set_text_color(146, 64, 14)
            pdf.cell(cw, ch, str(cat), align="C")
        pdf.set_y(y0 + ch + 6)
        pdf.set_text_color(*SB_DARK)
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.3)

    if not items:
        return

    # Picture cards — taller than vocabulary cards so the visual has room
    # to breathe. 3 per row keeps the label legible.
    cols = 3
    rows = (len(items) + cols - 1) // cols
    card_w = usable_w / cols
    card_h = 28
    for r in range(rows):
        y0 = pdf.get_y()
        for c in range(cols):
            idx = r * cols + c
            if idx >= len(items):
                break
            x0 = PAGE_MARGIN + c * card_w
            pdf.set_fill_color(252, 250, 245)
            pdf.set_draw_color(120, 140, 180)
            pdf.set_line_width(0.4)
            pdf.set_dash_pattern(dash=1.2, gap=1.2)
            pdf.rect(x0 + 2, y0, card_w - 4, card_h, style="DF")
            pdf.set_dash_pattern()

            # Item is a dict {label, answer}; fall back to bare-string in
            # case of a hand-authored artifact that uses the simpler shape.
            it = items[idx]
            label = it["label"] if isinstance(it, dict) else str(it)

            pdf.set_text_color(40, 60, 110)
            _render_mixed_label_centered(
                pdf, x0, y0, card_w, card_h,
                label=label, base_font=ff, base_size=14,
            )
        pdf.set_y(y0 + card_h + 3)
    pdf.set_text_color(*SB_DARK)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)


def _render_sort_cards(pdf, artifact, usable_w):
    """Grid of cut-out cards. Categories printed across the top as larger
    'header cards', then `items` rendered as a grid below."""
    ff = pdf.ff
    categories = artifact.get("categories") or []
    items = artifact.get("items") or []

    # Category header strip.
    if categories:
        n = len(categories)
        cw = usable_w / n
        ch = 18
        y0 = pdf.get_y()
        for i, cat in enumerate(categories):
            x0 = PAGE_MARGIN + i * cw
            pdf.set_fill_color(255, 247, 220)
            pdf.set_draw_color(180, 130, 20)
            pdf.set_line_width(0.6)
            pdf.rect(x0 + 1.5, y0, cw - 3, ch, style="DF")
            pdf.set_xy(x0, y0)
            pdf.set_font(ff, "B", 22)
            pdf.set_text_color(146, 64, 14)
            pdf.cell(cw, ch, str(cat), align="C")
        pdf.set_y(y0 + ch + 6)
        pdf.set_text_color(*SB_DARK)
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.3)

    if not items:
        return

    # Item card grid — 4 cards per row, padded for cutting.
    cols = 4
    rows = (len(items) + cols - 1) // cols
    card_w = usable_w / cols
    card_h = 20
    for r in range(rows):
        y0 = pdf.get_y()
        for c in range(cols):
            idx = r * cols + c
            if idx >= len(items):
                break
            x0 = PAGE_MARGIN + c * card_w
            pdf.set_fill_color(248, 250, 253)
            pdf.set_draw_color(120, 140, 180)
            pdf.set_line_width(0.4)
            # Dashed border to imply 'cut here'.
            pdf.set_dash_pattern(dash=1.2, gap=1.2)
            pdf.rect(x0 + 2, y0, card_w - 4, card_h, style="DF")
            pdf.set_dash_pattern()
            # Center text.
            pdf.set_xy(x0, y0)
            pdf.set_font(ff, "B", 11)
            pdf.set_text_color(40, 60, 110)
            pdf.cell(card_w, card_h, str(items[idx]), align="C")
        pdf.set_y(y0 + card_h + 3)
    pdf.set_text_color(*SB_DARK)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)


def _render_chart(pdf, artifact, usable_w):
    """Blank chart with header labels and N empty rows for the student."""
    ff = pdf.ff
    headers = artifact.get("categories") or artifact.get("headers") or []
    rows = int(artifact.get("rows") or 6)
    if not headers:
        return
    n = len(headers)
    cw = usable_w / n
    # Header row
    y0 = pdf.get_y()
    pdf.set_fill_color(220, 234, 250)
    pdf.set_draw_color(60, 100, 160)
    pdf.set_line_width(0.5)
    for i, h in enumerate(headers):
        x0 = PAGE_MARGIN + i * cw
        pdf.rect(x0, y0, cw, 10, style="DF")
        pdf.set_xy(x0, y0)
        pdf.set_font(ff, "B", 12)
        pdf.set_text_color(30, 64, 175)
        pdf.cell(cw, 10, str(h), align="C")
    pdf.set_y(y0 + 10)
    # Empty rows
    pdf.set_text_color(*SB_DARK)
    pdf.set_draw_color(160, 170, 200)
    row_h = 14
    for _r in range(rows):
        y0 = pdf.get_y()
        for i in range(n):
            x0 = PAGE_MARGIN + i * cw
            pdf.rect(x0, y0, cw, row_h, style="D")
        pdf.set_y(y0 + row_h)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)


def _render_reference_card(pdf, artifact, usable_w):
    """A printable anchor-chart-style reference: title + bulleted facts."""
    ff = pdf.ff
    bullets = artifact.get("items") or []
    if not bullets:
        return
    # Big bordered panel.
    y0 = pdf.get_y()
    pdf.set_fill_color(252, 252, 240)
    pdf.set_draw_color(200, 175, 60)
    pdf.set_line_width(0.7)
    pdf.rect(PAGE_MARGIN, y0, usable_w, 4, style="F")  # top sliver placeholder

    pdf.set_y(y0 + 4)
    pdf.set_text_color(*SB_DARK)
    for b in bullets:
        pdf.set_font(ff, "B", 14)
        pdf.set_x(PAGE_MARGIN + 6)
        pdf.cell(8, 8, "•")
        pdf.set_font(ff, "", 12)
        pdf.set_x(PAGE_MARGIN + 14)
        pdf.multi_cell(usable_w - 20, 7, str(b),
                       new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
    y_end = pdf.get_y() + 4
    pdf.set_draw_color(200, 175, 60)
    pdf.set_line_width(0.7)
    pdf.rect(PAGE_MARGIN, y0, usable_w, y_end - y0, style="D")
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)


# ── Blackline masters (grounded-rote plan, Layer B) ──────────────────────
# Six reusable math-model masters activities can reference by name. All are
# blank templates the student writes on — the model is the point, so keep
# every line crisp and every label slot empty unless the artifact says
# otherwise.

def _render_hundredths_grid(pdf, artifact, usable_w):
    """`copies` (default 4) blank 10x10 hundredths grids, two per row.
    Optional `shaded` fills that many cells (row-major) on the FIRST grid
    only — a worked demo the student mirrors on the blank ones."""
    copies = int(artifact.get("copies") or 4)
    shaded = int(artifact.get("shaded") or 0)
    per_row = 2
    gap = 12
    gsize = min((usable_w - gap * (per_row - 1)) / per_row, 78)
    cell = gsize / 10
    y = pdf.get_y() + 2
    pdf.set_line_width(0.25)
    for c in range(copies):
        col = c % per_row
        if col == 0 and c > 0:
            y += gsize + 10
        x0 = PAGE_MARGIN + col * (gsize + gap)
        for i in range(100):
            cx = x0 + (i % 10) * cell
            cy = y + (i // 10) * cell
            if c == 0 and i < shaded:
                pdf.set_fill_color(180, 205, 245)
                pdf.rect(cx, cy, cell, cell, style="DF")
            else:
                pdf.rect(cx, cy, cell, cell, style="D")
        pdf.set_line_width(0.7)
        pdf.rect(x0, y, gsize, gsize, style="D")
        pdf.set_line_width(0.25)
        # Write-on line under each grid: fraction / decimal / percent.
        pdf.set_font(pdf.ff, "", 9)
        pdf.set_text_color(110, 110, 110)
        pdf.text(x0, y + gsize + 5.5, "/100 =            = ______ %")
        pdf.set_text_color(*SB_DARK)
    pdf.set_y(y + gsize + 12)


def _render_percent_bar(pdf, artifact, usable_w):
    """`bars` (default 5) percent/tape bars. Each bar spans the page,
    divided into `parts` (default 10) equal pieces, with 0%/100% end labels
    (override with `end_labels: [left, right]`) and a blank line above for
    the quantity the bar represents."""
    bars = int(artifact.get("bars") or 5)
    parts = int(artifact.get("parts") or 10)
    left_lab, right_lab = (artifact.get("end_labels") or ["0%", "100%"])[:2]
    bar_h = 13
    block_h = bar_h + 22
    y = pdf.get_y() + 4
    for _b in range(bars):
        # Write-on line above the bar (what does the whole bar stand for?)
        pdf.set_font(pdf.ff, "", 9)
        pdf.set_text_color(110, 110, 110)
        pdf.text(PAGE_MARGIN, y, "The whole bar is: ______________")
        pdf.set_text_color(*SB_DARK)
        by = y + 3
        pdf.set_line_width(0.25)
        pw = usable_w / parts
        for i in range(parts):
            pdf.rect(PAGE_MARGIN + i * pw, by, pw, bar_h, style="D")
        pdf.set_line_width(0.7)
        pdf.rect(PAGE_MARGIN, by, usable_w, bar_h, style="D")
        pdf.set_line_width(0.25)
        pdf.set_font(pdf.ff, "", 9)
        pdf.text(PAGE_MARGIN, by + bar_h + 5, str(left_lab))
        rw = pdf.get_string_width(str(right_lab))
        pdf.text(PAGE_MARGIN + usable_w - rw, by + bar_h + 5, str(right_lab))
        y += block_h
    pdf.set_y(y)


def _render_number_line_strip(pdf, artifact, usable_w):
    """`lines` (default 6) blank number lines with `tick_count` (default 11)
    unlabeled ticks and arrowheads both ways — students label the ticks."""
    lines = int(artifact.get("lines") or 6)
    tick_count = max(2, int(artifact.get("tick_count") or 11))
    block_h = 24
    y = pdf.get_y() + 8
    pad = 8
    span = usable_w - 2 * pad
    step = span / (tick_count - 1)
    for _l in range(lines):
        ly = y
        pdf.set_line_width(0.5)
        pdf.line(PAGE_MARGIN + 2, ly, PAGE_MARGIN + usable_w - 2, ly)
        # arrowheads
        for ax, s in ((PAGE_MARGIN + 2, 1), (PAGE_MARGIN + usable_w - 2, -1)):
            pdf.line(ax, ly, ax + 2.5 * s, ly - 1.8)
            pdf.line(ax, ly, ax + 2.5 * s, ly + 1.8)
        pdf.set_line_width(0.35)
        for t in range(tick_count):
            tx = PAGE_MARGIN + pad + t * step
            pdf.line(tx, ly - 2.2, tx, ly + 2.2)
        y += block_h
    pdf.set_y(y)


def _render_fraction_bars(pdf, artifact, usable_w):
    """The classic fraction-bar anchor chart: one whole on top, then rows
    split into `rows` (default [2,3,4,5,6,8,10,12]) equal pieces, each
    piece labeled with its unit fraction."""
    rows = artifact.get("rows") or [2, 3, 4, 5, 6, 8, 10, 12]
    bar_h = 12
    gap = 3
    y = pdf.get_y() + 2
    pdf.set_line_width(0.35)
    pdf.set_font(pdf.ff, "B", 10)

    def draw_bar(parts, label_num):
        nonlocal y
        pw = usable_w / parts
        for i in range(parts):
            pdf.rect(PAGE_MARGIN + i * pw, y, pw, bar_h, style="D")
            lab = "1" if parts == 1 else f"1/{parts}"
            lw = pdf.get_string_width(lab)
            pdf.text(PAGE_MARGIN + i * pw + (pw - lw) / 2, y + bar_h / 2 + 1.6, lab)
        y += bar_h + gap

    draw_bar(1, "1")
    for parts in rows:
        draw_bar(int(parts), None)
    pdf.set_y(y)


def _render_grid_paper(pdf, artifact, usable_w):
    """Full-remaining-page square grid (`cell_mm`, default 7) for slope
    staircases, tile proofs, and area work."""
    cell = float(artifact.get("cell_mm") or 7)
    y0 = pdf.get_y() + 2
    y_end = pdf.h - SB_FOOTER_HEIGHT - 8
    cols = int(usable_w // cell)
    rows_n = int((y_end - y0) // cell)
    w = cols * cell
    h = rows_n * cell
    pdf.set_draw_color(150, 165, 195)
    pdf.set_line_width(0.18)
    for i in range(cols + 1):
        pdf.line(PAGE_MARGIN + i * cell, y0, PAGE_MARGIN + i * cell, y0 + h)
    for j in range(rows_n + 1):
        pdf.line(PAGE_MARGIN, y0 + j * cell, PAGE_MARGIN + w, y0 + j * cell)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)
    pdf.set_y(y0 + h)


def _render_dot_plot_frame(pdf, artifact, usable_w):
    """`frames` (default 3) blank dot-plot axes: a horizontal line with
    `tick_count` (default 11) ticks, label blanks beneath each tick, and
    stacking room above for the dots."""
    frames = int(artifact.get("frames") or 3)
    tick_count = max(2, int(artifact.get("tick_count") or 11))
    stack_h = 42
    block_h = stack_h + 22
    pad = 10
    span = usable_w - 2 * pad
    step = span / (tick_count - 1)
    y = pdf.get_y() + 4
    for _f in range(frames):
        ly = y + stack_h
        pdf.set_line_width(0.5)
        pdf.line(PAGE_MARGIN + 2, ly, PAGE_MARGIN + usable_w - 2, ly)
        pdf.set_line_width(0.35)
        pdf.set_font(pdf.ff, "", 8)
        pdf.set_text_color(110, 110, 110)
        for t in range(tick_count):
            tx = PAGE_MARGIN + pad + t * step
            pdf.line(tx, ly, tx, ly + 2.5)
            pdf.line(tx - 3.5, ly + 8, tx + 3.5, ly + 8)  # label blank
        # Title blank for the axis.
        pdf.text(PAGE_MARGIN + usable_w / 2 - 14, ly + 15, "____________")
        pdf.set_text_color(*SB_DARK)
        y += block_h
    pdf.set_y(y)


_MASTER_RENDERERS = {
    "hundredths_grid": _render_hundredths_grid,
    "percent_bar": _render_percent_bar,
    "tape_diagram": _render_percent_bar,        # same master, different name
    "number_line_strip": _render_number_line_strip,
    "fraction_bars": _render_fraction_bars,
    "grid_paper": _render_grid_paper,
    "dot_plot_frame": _render_dot_plot_frame,
}


def _estimate_exit_ticket_height(exit_items):
    """Rough mm needed to render the Exit Ticket block (header + items +
    reflection). Used to decide whether to pull a single-item Exit Ticket
    up onto page 1 instead of spawning its own page."""
    h = 26  # header band + skill line + framing line
    if exit_items:
        # Items render two-up: each row's height is the taller of its pair.
        for r in range(0, len(exit_items), 2):
            pair = exit_items[r:r + 2]
            h += max(_estimate_item_height(it) for it in pair) + 4
        h += 28  # "How do you know?" explanation block (prompt + 2 lines)
    else:
        h += 12
    h += 26  # reflection block
    return h


def _write_exit_ticket_block(pdf, exit_items, skill, usable_w,
                              start_q_num=1, include_reflection=True,
                              header_size="full"):
    """Render the Exit Ticket section. Used both for the dedicated-page
    layout and the page-1 pull-up layout when there's only one exit item."""
    ff = pdf.ff

    # Header / framing always renders full-width regardless of column state.
    full_w = pdf.w - 2 * PAGE_MARGIN
    y0 = pdf.get_y()
    title_h = 7
    pdf.set_font(ff, "B", 9.5)
    label = "Show what you know"
    bw = pdf.get_string_width(label) + 9
    pdf.set_fill_color(219, 234, 254)
    pdf.rect(PAGE_MARGIN, y0, bw, 6.5, style="F",
             round_corners=True, corner_radius=3.2)
    pdf.set_xy(PAGE_MARGIN, y0 + 0.7)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(bw, 5.2, label, align="C")
    # Name line on the right of the chip row.
    pdf.set_font(ff, "", 9)
    pdf.set_text_color(*ANNOT_GRAY)
    name_label = "Name: "
    nl_w = pdf.get_string_width(name_label)
    pdf.set_xy(PAGE_MARGIN + full_w * 0.55, y0 + 0.7)
    pdf.cell(nl_w, title_h - 2, name_label, new_x="RIGHT", new_y="TOP")
    line_y = y0 + 5
    pdf.set_draw_color(*LINE_GRAY)
    pdf.set_line_width(0.3)
    pdf.line(pdf.get_x(), line_y, PAGE_MARGIN + full_w, line_y)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_y(y0 + title_h + 3)
    pdf.set_text_color(*SB_DARK)

    # Skill name + brief framing
    pdf.set_font(ff, "B", 10)
    pdf.set_x(PAGE_MARGIN)
    pdf.cell(full_w, 5, f"Skill: {skill['name']}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(ff, "I", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.set_x(PAGE_MARGIN)
    pdf.cell(full_w, 4,
             "Show what you know. No help on these -- this is just for me to see how you're doing.",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*SB_DARK)
    pdf.ln(4)

    q_num = start_q_num
    if exit_items:
        # Two-column layout for the items.
        q_num = _render_two_column_block(pdf, exit_items, q_num,
                                         _write_student_question)
        # Verbalization demand (IES rec 2): one written explanation per
        # exit check, tied to the last problem.
        pdf.ln(2)
        pdf.set_font(ff, "B", 10)
        pdf.set_text_color(*SB_DARK)
        pdf.set_x(PAGE_MARGIN)
        pdf.cell(full_w, 5,
                 f"How do you know? Explain your thinking on #{q_num - 1}:",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(150, 150, 150)
        for _ln in range(2):
            pdf.ln(8)
            pdf.line(PAGE_MARGIN, pdf.get_y(), PAGE_MARGIN + full_w, pdf.get_y())
        pdf.set_draw_color(0, 0, 0)
        pdf.ln(2)
    else:
        pdf.set_font(ff, "I", 9)
        pdf.set_text_color(150, 150, 150)
        pdf.set_x(PAGE_MARGIN)
        pdf.multi_cell(full_w, 5,
                       "(Exit Ticket items pending. Add more sample_items to this skill in the data file.)",
                       new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*SB_DARK)

    if include_reflection:
        pdf.ln(6 if header_size == "small" else 8)
        pdf.set_font(ff, "B", 10)
        pdf.set_x(PAGE_MARGIN)
        pdf.cell(full_w, 6, "Reflection", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(ff, "I", 9)
        pdf.set_text_color(120, 120, 120)
        pdf.set_x(PAGE_MARGIN)
        pdf.cell(full_w, 5, "What was the trickiest part of this skill for you?",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(8 if header_size == "small" else 10)
        pdf.set_x(PAGE_MARGIN)
        pdf.cell(full_w, 5, "What would help you next time?",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(6 if header_size == "small" else 10)
        pdf.set_text_color(*SB_DARK)


def _write_teacher_solution_steps(pdf, solution, usable_w):
    """The teacher's mirror of the student's Watch & learn: every step as the
    student sees it, plus the micro-check prompt and its answer."""
    ff = pdf.ff
    steps = solution.get("steps") or []
    if not steps:
        pdf.ln(2)
        return

    block_y0 = pdf.get_y()
    pdf.set_fill_color(243, 248, 255)
    pdf.set_draw_color(140, 180, 220)
    pdf.set_line_width(0.4)
    pdf.rect(PAGE_MARGIN, block_y0, usable_w, 6.5, style="DF")
    pdf.set_xy(PAGE_MARGIN + 3, block_y0 + 1)
    pdf.set_font(ff, "B", 9)
    pdf.set_text_color(30, 80, 140)
    pdf.cell(0, 4.5, "The student sees these same steps. Ask each check before "
                     "you reveal the line under it.")
    pdf.set_y(block_y0 + 7.5)

    letter = 0
    for n, st in enumerate(steps, start=1):
        check = st.get("check")
        if check:
            # Ask first, then reveal -- the order the student sheet prints.
            name = THINKING_MOVES.get(check.get("move"), check.get("move") or "")
            tag = chr(ord("a") + letter)
            letter += 1
            pdf.set_font(ff, "B", 8)
            pdf.set_text_color(146, 64, 14)
            pdf.set_x(PAGE_MARGIN + 4)
            pdf.multi_cell(usable_w - 8, 4,
                           f"({tag}) {name.upper()}  {check.get('prompt', '')}",
                           new_x="LMARGIN", new_y="NEXT")
            ans = str(check.get("answer") or "").strip()
            if ans:
                pdf.set_font(ff, "I", 8)
                pdf.set_text_color(30, 120, 50)
                pdf.set_x(PAGE_MARGIN + 8)
                pdf.multi_cell(usable_w - 12, 3.8, f"looking for: {ans}",
                               new_x="LMARGIN", new_y="NEXT")
        math_txt = st.get("math")
        if math_txt:
            pdf.set_font(ff, "B", 8.5)
            pdf.set_text_color(*SB_DARK)
            pdf.set_x(PAGE_MARGIN + 4)
            pdf.cell(6, 4.4, f"{n}.")
            _write_text_or_math(pdf, math_txt, x=PAGE_MARGIN + 10,
                                max_width=usable_w - 14, font_size=8.5)
        ann = (st.get("annotation") or "").strip()
        if ann:
            pdf.set_font(ff, "", 8)
            pdf.set_text_color(90, 90, 100)
            pdf.set_x(PAGE_MARGIN + 10)
            pdf.multi_cell(usable_w - 14, 3.8, ann, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*SB_DARK)
    pdf.ln(2)


def _write_worked_example_teacher_block(pdf, item, skill, usable_w,
                                         section_badges, num, solution=None):
    """Render the Worked Example on the TEACHER companion as a scripted
    walkthrough.

    Layout:
      [WORKED EXAMPLE badge]
      Q1. <stem>
          Answer: <answer>     (green pop)

      Say this to your students:
        1. Say:  "..."
        2. Ask:  "..."
        3. Show: "..."

    The script comes from _build_worked_example_script — uses the authored
    `worked_example_script` array if present, otherwise auto-splits
    `i_do_script`. Designed for a teacher who has never taught math: every
    step is read-aloud or do-this, no derivation expected of them."""
    ff = pdf.ff

    # Section badge
    bg, fg = section_badges.get("worked", ((229, 240, 255), (30, 60, 130)))
    pdf.ln(1)
    y0 = pdf.get_y()
    label = "WORKED EXAMPLE - Teacher models"
    pdf.set_font(ff, "B", 10)
    bw = pdf.get_string_width(label) + 10
    pdf.set_fill_color(*bg)
    pdf.set_text_color(*fg)
    pdf.set_draw_color(*fg)
    pdf.set_line_width(0.4)
    pdf.rect(PAGE_MARGIN, y0, bw, 6, style="DF")
    pdf.set_xy(PAGE_MARGIN, y0 + 0.5)
    pdf.cell(bw, 5, label, align="C")
    pdf.set_text_color(*SB_DARK)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)
    pdf.ln(8)

    # Q-num + stem. `num` is None when the caller wants no number, which is
    # the case for the worked example: the student's Watch & learn is
    # unnumbered, so numbering it here would shift every following item.
    pdf.set_font(ff, "B", 9)
    pdf.set_text_color(*SB_DARK)
    pdf.set_x(PAGE_MARGIN)
    if num is not None:
        pdf.cell(7, 4, f"{num}.")
    pdf.set_font(ff, "", 9)
    pdf.set_xy(PAGE_MARGIN + 7, pdf.get_y())
    _write_text_or_math(pdf, item.get("stem", ""),
                        x=PAGE_MARGIN + 7, max_width=usable_w - 10,
                        font_size=9)

    # Answer
    pdf.set_font(ff, "B", 9)
    pdf.set_text_color(30, 120, 50)
    pdf.set_x(PAGE_MARGIN + 10)
    pdf.multi_cell(usable_w - 12, 4.5, f"Answer: {item.get('answer', '')}",
                   new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*SB_DARK)
    pdf.ln(2)

    # v4: mirror the student's Watch & learn exactly -- the same steps, in
    # the same order, with the micro-check prompts and their key. The
    # Say/Ask/Show script is written around whatever example the author had in
    # mind and cannot be trusted to match this problem, so v4 does not use it.
    if solution:
        _write_teacher_solution_steps(pdf, solution, usable_w)
        return

    # Scripted steps (v3)
    steps = _build_worked_example_script(skill)
    if not steps:
        pdf.ln(2)
        return

    # Pale-blue script block so it visually reads as a guided panel.
    block_x = PAGE_MARGIN + 3
    block_w = usable_w - 6
    block_y0 = pdf.get_y()
    pdf.set_fill_color(243, 248, 255)
    pdf.set_draw_color(140, 180, 220)
    pdf.set_line_width(0.4)
    pdf.rect(PAGE_MARGIN, block_y0, usable_w, 6.5, style="DF")
    pdf.set_xy(block_x, block_y0 + 1)
    pdf.set_font(ff, "B", 9)
    pdf.set_text_color(30, 80, 140)
    pdf.cell(0, 4.5, "Use these prompts to draw out their thinking — lean on the asks first.")
    pdf.set_y(block_y0 + 7.5)

    # Per-step prefix styling
    KIND_LABEL = {
        "say":   ("Say:",   (30, 80, 140)),
        "ask":   ("Ask:",   (146, 64, 14)),
        "show":  ("Show:",  (21, 128, 61)),
        "watch": ("Watch:", (153, 27, 27)),
    }

    for idx, step in enumerate(steps, start=1):
        kind = step.get("kind", "say")
        text = step.get("text", "")
        if not text:
            continue
        prefix, color = KIND_LABEL.get(kind, KIND_LABEL["say"])

        # Numbered step on its own line: "1. Say:  ..."
        pdf.set_x(block_x)
        pdf.set_font(ff, "B", 8.5)
        pdf.set_text_color(80, 80, 80)
        num_str = f"{idx}."
        nw = pdf.get_string_width(num_str) + 1
        pdf.cell(nw, 4.5, num_str, new_x="RIGHT", new_y="TOP")

        pdf.set_font(ff, "B", 8.5)
        pdf.set_text_color(*color)
        pw = pdf.get_string_width(prefix) + 2
        pdf.cell(pw, 4.5, prefix, new_x="RIGHT", new_y="TOP")

        pdf.set_font(ff, "", 8.5)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(block_w - nw - pw, 4.2,
                       f' "{text}"' if kind in ("say", "ask") else f" {text}",
                       new_x="LMARGIN", new_y="NEXT")
        pdf.ln(0.5)

    block_y_end = pdf.get_y() + 2
    pdf.set_draw_color(140, 180, 220)
    pdf.rect(PAGE_MARGIN, block_y0, usable_w, block_y_end - block_y0, style="D")
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)
    pdf.set_text_color(*SB_DARK)
    pdf.ln(3)

    # Light separator before the next section.
    sep_y = pdf.get_y()
    pdf.set_draw_color(220, 220, 220)
    pdf.set_line_width(0.2)
    pdf.line(PAGE_MARGIN, sep_y, PAGE_MARGIN + usable_w, sep_y)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)
    pdf.ln(2)


def _build_worked_example_script(skill):
    """Return a list of {kind, text} steps for the teacher to follow when
    modeling the worked example.

    Preferred source: skill["worked_example_script"] — an authored list of
    {kind: "say"|"ask"|"show"|"watch", text: "..."} steps. When that's not
    present, fall back to splitting i_do_script by sentence and labelling
    each as a Say step. Sentences ending in '?' become Ask steps.

    Designed for non-math teachers — every step is something the teacher
    can read aloud or do without needing to derive math themselves."""
    authored = skill.get("worked_example_script")
    if isinstance(authored, list) and authored:
        steps = []
        for raw in authored:
            if not isinstance(raw, dict):
                continue
            kind = (raw.get("kind") or "say").lower()
            text = (raw.get("text") or "").strip()
            if not text:
                continue
            steps.append({"kind": kind, "text": text})
        if steps:
            return steps

    # Fallback — auto-split i_do_script. Convert directive sentences into
    # inquiry prompts where we can. The teacher companion is meant to coach
    # the student to think, not narrate the solution.
    i_do = (skill.get("i_do_script") or "").strip()
    if not i_do:
        return []
    import re as _re
    sentences = _re.split(r"(?<=[.!?])\s+", i_do)
    sentences = [s.strip() for s in sentences if s.strip()]

    # Cues that indicate a "show me / point to" demonstration step. These
    # stay as `show` rather than getting flipped into questions.
    SHOW_CUES = ("write ", "show ", "point ", "draw ", "circle ", "underline ")
    # Cues that indicate a directive step we want to flip into a question.
    DIRECTIVE_CUES = (
        "first", "next", "then", "now", "start by", "begin by",
        "remember", "notice", "look at", "think about", "make sure",
        "we ", "you ", "let's", "let us",
    )

    def _to_inquiry(text: str) -> str:
        """Best-effort rewrite of a declarative coaching line into an open
        question. Keeps the original meaning but shifts who's doing the
        thinking. Falls back to wrapping in "What do you notice about ...?"
        when no clean rewrite is available."""
        t = text.rstrip(".!").strip()
        low = t.lower()

        # Already a question — use as-is.
        if t.endswith("?"):
            return t + ("" if t.endswith("?") else "?")

        # "First, look at the parentheses" → "Where would you start? What do you see first?"
        if low.startswith(("first,", "first ", "start by", "begin by")):
            return "Where would you start? What do you notice first?"
        # "Notice that X" → "What do you notice about X?"
        if low.startswith("notice that "):
            return "What do you notice about " + t[len("Notice that "):].rstrip(".!") + "?"
        if low.startswith("notice "):
            return "What do you notice about " + t[len("Notice "):].rstrip(".!") + "?"
        # "Remember X" / "Remember that X" → "What rule do you remember about X?"
        if low.startswith("remember that "):
            return "What rule do you remember about " + t[len("Remember that "):].rstrip(".!") + "?"
        if low.startswith("remember,") or low.startswith("remember "):
            tail = t.split(" ", 1)[1] if " " in t else t
            return "What do you remember about " + tail.rstrip(".!,") + "?"
        # "Look at the X" → "What do you see in the X?"
        if low.startswith("look at "):
            return "What do you see in " + t[len("Look at "):].rstrip(".!") + "?"
        # "Think about X" → "What are you thinking about X?"
        if low.startswith("think about "):
            return "What are you thinking about when you see " + t[len("Think about "):].rstrip(".!") + "?"
        # "We need to X" / "You need to X" → "What do we need to do here?"
        if low.startswith(("we need to", "you need to", "we have to", "you have to")):
            return "What do we need to do here? Why?"
        # "Now X" / "Then X" / "Next X" → "What's the next step? Why?"
        if low.startswith(("now ", "next ", "then ")):
            return "What's the next step? Why does that come next?"
        # Generic fallback — turn the declarative into an open prompt.
        return f"What do you notice about this part? ({t})"

    steps = []
    for s in sentences:
        low = s.lower()
        if s.endswith("?"):
            steps.append({"kind": "ask", "text": s})
            continue
        if any(low.startswith(c) for c in SHOW_CUES):
            steps.append({"kind": "show", "text": s})
            continue
        if any(low.startswith(c) for c in DIRECTIVE_CUES):
            steps.append({"kind": "ask", "text": _to_inquiry(s)})
            continue
        # Default: keep as a Say step but only for genuinely declarative
        # framing lines (e.g., "An equation is given.").
        steps.append({"kind": "say", "text": s})
    return steps


def _estimate_item_height(item):
    """Rough estimate of how much vertical space a student question needs.

    Used to decide whether a section header + first item will fit on the
    current page or whether we should jump to a new page first. Avoids the
    orphan-header bug where a section title prints at the page bottom and
    its first question wraps to the next page."""
    if not item:
        return 30
    stem = item.get("stem", "") or ""
    # Stem height: count *physical* lines (each \n is forced) plus a
    # wrap allowance per line. In two-column mode a line wraps at ~38 chars;
    # in single-column it's ~70. We assume column-mode here because that's
    # the page-break-sensitive case and over-estimating slightly is harmless.
    chars_per_line = 38
    line_h = 5
    physical_lines = stem.split("\n") if stem else [""]
    wrapped = 0
    for pl in physical_lines:
        if not pl:
            wrapped += 1  # blank line
            continue
        wrapped += max(1, (len(pl) + chars_per_line - 1) // chars_per_line)
    base = 8 + wrapped * line_h
    if item.get("difficulty") == "stretch":
        base += 5  # "LEVEL UP" chip row
    choices = item.get("choices") or []
    # Choice lines also wrap in a column — give each two lines of slack.
    base += len(choices) * 6
    # Diagram space (number line, coordinate grid, SVG figure).
    base += _estimate_render_height(item.get("render_data"))
    # Multi-part items: prompt block + the answer line. ~18mm per part is
    # closer to reality than the old 14.
    parts = item.get("parts") or []
    base += len(parts) * 18
    # Error-analysis items: student-work box + prompt + workspace + line.
    if item.get("type") == "error_analysis" and item.get("shown_work"):
        return base + 14 + 6 * len(item["shown_work"]) + 40
    # Open-response items get a work area + answer line (~34mm) unless
    # they're short-answer classification prompts (single line, ~11mm).
    if not choices and not parts:
        rd = item.get("render_data")
        rd_type = rd.get("type") if isinstance(rd, dict) else None
        if rd_type != "data_table":
            if _is_short_answer_item(item):
                base += 11
            elif rd:
                base += 22   # figure item: compact work area (see _write_student_question)
            else:
                base += 34
    return base


def _write_section_header_safe(pdf, label, subtitle, color, usable_w,
                                next_item_height=30):
    """Wrapper around _write_section_header that breaks to a new page if
    the header + the next item won't fit on the current page. Eliminates
    the 'YOU DO' orphan we saw on engine-mapped packets."""
    needed = 18 + next_item_height  # header band + subtitle + first item
    page_bottom_safe = pdf.h - SB_FOOTER_HEIGHT - 8
    if pdf.get_y() + needed > page_bottom_safe:
        _draw_footer(pdf, getattr(pdf, "_pnp_standard", ""),
                     getattr(pdf, "_pnp_skill_name", ""))
        pdf.add_page()
    _write_section_header(pdf, label, subtitle, color, usable_w)


def _write_section_header(pdf, label, subtitle, color, usable_w):
    """Coloured section header for a student-handout section — delegates
    to the shared chip-and-rule style so every section reads the same."""
    bg, fg = color
    _chip_header(pdf, label, subtitle, bg, fg, usable_w)
    pdf.ln(1)


# Student-handout sections a caller may switch off. All default to True, so
# an older client that sends nothing still gets the full packet.
SECTION_KEYS = (
    "fluency_sprint",     # Fluency sprint
    "watch_learn",        # Watch & learn
    "you_finish",         # You finish it
    "lets_try",           # Let's try together
    "your_turn",          # Your turn
    "level_up",           # the stretch items inside Your turn
    "find_mistake",       # Find the mistake
    "remember_these",     # Remember these?
    "show_what_you_know",  # Show what you know (exit ticket)
)


def generate_skill_packet_pdf(skill, standard_data, output_path,
                               student_copies=1, include_teacher_companion=True,
                               include_printable_artifact=True, session=1,
                               sections=None):
    """Generate a skill packet PDF following the gradual-release flow.

    Sections (student handout, in order):
      Page 1: Worked Example -> Diagnose -> We Do -> You Do
      Page 2: Exit Ticket (own page) -> Reflection

    Teacher companion (if requested):
      Quick Reference (canonical error) -> Optional Teaching Note -> Prereq
      check -> Vocabulary -> Concrete/visual -> per-section question blocks
      with answer + watch-for + redirect script.
    """
    # Unknown keys are ignored; missing keys default to on.
    sections = dict(sections or {})
    inc = {k: bool(sections.get(k, True)) for k in SECTION_KEYS}

    standard_code = standard_data["standard_code"]
    # Top up sample_items from the question engine when the skill JSON has
    # fewer than 10 authored items. The engine returns standard-aligned
    # questions at the right proficiency band; they're not sub-skill-tuned,
    # but they fill out the packet so every section gets enough problems.
    # 10 items per session: 1 worked example + 3 try it + 2 we do +
    # 2 you do + 2 exit. Two sessions provide 20 unique items per skill
    # so a teacher can run the same skill twice without repeats.
    # v4 (schema_version 4) skills carry a `guided_example` — the middle rung
    # of the backward fade — and end "Your turn" with a fixed Find the
    # Mistake slot sourced from the error_analysis practice problem. Claim
    # that problem's stem up front so the general item pool can't reprint it.
    guided_example = skill.get("guided_example")
    ftm_item = None
    if guided_example:
        for p in (skill.get("practice_problems") or []):
            if p.get("type") == "error_analysis" and p.get("shown_work"):
                ftm_item = {
                    "stem": p.get("stem", ""),
                    "answer": p.get("answer", ""),
                    "choices": None,
                    "type": "error_analysis",
                    "shown_work": p.get("shown_work"),
                    "render_data": p.get("render_data"),
                }
                break

    # Anything the v4 ladder already shows the student must not come back as an
    # item, and above all not as an exit-ticket item: the exit ticket is the
    # whole mastery decision, and re-asking the problem the teacher just
    # modelled measures page-flipping. Excludes the worked, faded and guided
    # stems alongside the Find-the-Mistake stem.
    _excluded = [ftm_item["stem"]] if ftm_item else []
    for _blk in ("worked_solution", "faded_example", "guided_example"):
        _stem = (skill.get(_blk) or {}).get("stem")
        if _stem:
            _excluded.append(_stem)

    items = _fill_items_from_engine(
        skill, standard_code, target_count=10, session=session,
        exclude_stems=_excluded or None)

    # Slice into the gradual-release sections.
    sections = _allocate_items(items)
    we_items   = sections["worked_example"]
    diag_items = sections["diagnose"]
    we_do_items = sections["we_do"]
    you_do_items = sections["you_do"]
    exit_items = sections["exit"]
    we_item = we_items[0] if we_items else None

    pdf = MathPDF()
    pdf.skill_tag = skill.get("skill_id", "")
    ff = pdf.ff
    pdf.set_auto_page_break(auto=False)
    pdf.header = lambda: None
    pdf.footer = lambda: None
    # Stash for footer/section-header helpers that need them on page break.
    pdf._pnp_standard = standard_code
    pdf._pnp_skill_name = skill["name"]

    usable_w = pdf.w - 2 * PAGE_MARGIN

    # Section badge color palette — used by _write_section_header to give
    # I Do / We Do / You Do / Exit Ticket distinct visual signatures.
    SECTION_COLORS = {
        "diagnose":  ((247, 220, 220), (153, 27, 27)),    # red-ish — pre-check
        "we_do":     ((254, 243, 199), (146, 64, 14)),    # amber — guided
        "you_do":    ((219, 250, 219), (21, 128, 61)),    # green — independent
        "exit":      ((219, 234, 254), (30, 64, 175)),    # navy/blue — formal
    }

    # Session Sheet v2 resources (v3 schema; every piece degrades
    # gracefully when the field is absent on older skill files).
    fluency = _resolve_fluency_items(skill, standard_data, session=session)
    worked_solution = skill.get("worked_solution")
    mixed_items = _resolve_mixed_review(skill, standard_data, session=session)
    faded_example = skill.get("faded_example")
    sentence_starters = skill.get("sentence_starters") or []

    # v4 full backward fade: the guided_example (same problem structure,
    # only the lead step given) replaces the engine diagnose items in
    # "Let's try together" — those items switched problem type mid-sheet
    # and broke the fade. Legacy skills keep the diagnose block.
    if guided_example:
        diag_items = []

    # ---- ONE NUMBERING FOR BOTH SHEETS ----------------------------------
    # When a teacher says "number 4", it has to be the student's number 4.
    # The companion used to run its own counter that started on the worked
    # example -- which the student page never numbers -- so every item from
    # there to the exit ticket was off by one.
    #
    # Number the sections in the order the STUDENT page prints them:
    #   Let's try together -> Your turn -> Find the mistake ->
    #   Remember these -> Show what you know
    # then hand the companion those starts. Watch & learn stays unnumbered on
    # both sheets. Section toggles are applied here too, so switching a
    # section off drops it from the answer key as well as the handout.
    _keep_stretch = inc["level_up"]

    def _sheet_side(items):
        if not inc["your_turn"]:
            return []
        return [it for it in items
                if _keep_stretch or it.get("difficulty") != "stretch"]

    sheet_diag = list(diag_items) if inc["lets_try"] else []
    sheet_we_do = _sheet_side(we_do_items)
    sheet_you_do = _sheet_side(you_do_items)
    sheet_ftm = ftm_item if (ftm_item and inc["find_mistake"]) else None
    sheet_mixed = list(mixed_items) if inc["remember_these"] else []
    sheet_exit = list(exit_items) if inc["show_what_you_know"] else []

    N_DIAG = 1
    N_WE_DO = N_DIAG + len(sheet_diag)
    N_YOU_DO = N_WE_DO + len(sheet_we_do)
    N_FTM = N_YOU_DO + len(sheet_you_do)
    N_MIXED = N_FTM + (1 if sheet_ftm else 0)
    N_EXIT = N_MIXED + len(sheet_mixed)

    # v4 student pages repeat the first sentence frame in the footer (cleared
    # again before the teacher companion). Legacy skills keep the quote so
    # their packets render exactly as before.
    pdf._pnp_frame = (sentence_starters[0]
                      if (guided_example and sentence_starters) else None)

    def _ensure_room(needed):
        page_bottom_safe = pdf.h - SB_FOOTER_HEIGHT - 8
        if pdf.get_y() + needed > page_bottom_safe:
            _draw_footer(pdf, standard_code, skill["name"])
            pdf.add_page()

    # ================================================================
    # STUDENT PAGES (repeated for each copy)
    # Session arc (evidence-based): Fluency Sprint (timed, mastered
    # content, self-graphed) -> true Worked Example -> Faded Example ->
    # guided practice w/ sentence starters -> independent practice ->
    # interleaved Mixed Review -> exit check w/ explanation.
    # ================================================================
    for _copy in range(student_copies):
        q_num = 1

        pdf.add_page()

        _draw_sb_header(pdf, PAGE_MARGIN, 5, usable_w, 22,
                        title=f"Plug N Play  -  {standard_code}",
                        standard_code="",
                        r=3, include_name=True, font_title=12, font_name=9)
        pdf.set_y(29)
        # Plain-English topic under the code, so a student or parent knows the
        # skill at a glance instead of just "6.GM.4" (review quick-win).
        pdf.set_font(pdf.ff, "B", 9.5)
        pdf.set_text_color(*SB_DARK)
        pdf.set_x(PAGE_MARGIN)
        pdf.multi_cell(usable_w, 4.6, skill.get("name", ""),
                       new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1.5)

        # ---- FLUENCY SPRINT (timed warm-up on mastered content) ----
        if fluency and inc["fluency_sprint"]:
            _set_column(pdf, "full")
            _write_fluency_block(pdf, fluency, usable_w)

        # ---- WORKED EXAMPLE ----
        # v3 skills carry a true worked solution (annotated steps printed
        # for the student); older skills fall back to the boxed problem
        # the teacher models from the companion script.
        if worked_solution and inc["watch_learn"]:
            ws_steps = worked_solution.get("steps", [])
            n_checks = sum(1 for s in ws_steps if s.get("check"))
            _ensure_room(24 + 14 * len(ws_steps) + 8 * n_checks
                         + (6 if n_checks else 0))
            _write_worked_solution(pdf, worked_solution, usable_w)
        elif we_item and inc["watch_learn"]:
            _set_column(pdf, "full")
            _write_worked_example(pdf, we_item, skill.get("i_do_script", ""),
                                  _col_w(pdf), show_answer=False)

        # ---- FADED EXAMPLE (student supplies the missing step) ----
        if faded_example and inc["you_finish"]:
            _ensure_room(24 + 12 * len(faded_example.get("steps", [])))
            _write_fade_block(pdf, faded_example, usable_w,
                              "You finish it",
                              "Fill in the missing steps yourself.",
                              (219, 250, 219), (21, 128, 61), (134, 209, 156))

        # ---- GUIDED EXAMPLE (v4: the middle fade rung) ----
        # Same problem structure with only the lead step given — the student
        # does the rest with the teacher. Replaces the engine diagnose items.
        if guided_example and inc["lets_try"]:
            _ensure_room(24 + 12 * len(guided_example.get("steps", []))
                         + (14 + 5 * len(sentence_starters) if sentence_starters else 0))
            _write_sentence_starters(pdf, sentence_starters, usable_w)
            _write_fade_block(pdf, guided_example, usable_w,
                              "Let's try together",
                              "Same kind of problem, all yours. Use the clue under each line. Say your thinking out loud.",
                              SECTION_COLORS["we_do"][0], SECTION_COLORS["we_do"][1],
                              (240, 200, 120))

        # Practice items flow in two labeled blocks so the gradual release
        # is visible to the student: guided ("Let's Try Together") then
        # independent ("Your Turn"). Kid-friendly labels, not teacher
        # jargon — the teacher companion keeps the internal section names.
        guided_items = sheet_diag
        independent_items = sheet_we_do + sheet_you_do
        if guided_items:
            _write_section_header_safe(
                pdf, "Let's try together",
                "Work these with your teacher. Say your thinking out loud.",
                SECTION_COLORS["we_do"], usable_w,
                next_item_height=_estimate_item_height(guided_items[0])
                + (14 + 5 * len(sentence_starters) if sentence_starters else 0))
            _write_sentence_starters(pdf, sentence_starters, usable_w)
            q_num = _render_two_column_block(pdf, guided_items, q_num,
                                             _write_student_question)
        if independent_items:
            _write_section_header_safe(
                pdf, "Your turn",
                "Try these on your own. Show your work.",
                SECTION_COLORS["you_do"], usable_w,
                next_item_height=_estimate_item_height(independent_items[0]))
            q_num = _render_two_column_block(pdf, independent_items, q_num,
                                             _write_student_question)

        # ---- FIND THE MISTAKE (v4: fixed error-analysis slot) ----
        # Always targets this skill's canonical error — the student-side
        # mirror of the teacher companion's WATCH FOR box. It carries its own
        # heading, so it stands alone when "Your turn" is switched off.
        if ftm_item and inc["find_mistake"]:
            _ensure_room(_estimate_item_height(ftm_item) + 8)
            pdf.set_font(ff, "B", 8.5)
            pdf.set_text_color(21, 128, 61)
            pdf.set_x(PAGE_MARGIN)
            pdf.cell(usable_w, 4.5,
                     "Find the mistake -- someone already tried this one. Catch the error.",
                     new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(*SB_DARK)
            pdf.ln(0.5)
            _set_column(pdf, "full")
            _write_student_question(pdf, q_num, ftm_item, _col_w(pdf))
            q_num += 1

        # ---- MIXED REVIEW (interleaved items from earlier skills) ----
        if sheet_mixed:
            _write_section_header_safe(
                pdf, "Remember these?",
                "Mixed practice from skills you've already worked on -- watch out, they're not all the same kind!",
                SECTION_COLORS["exit"], usable_w,
                next_item_height=_estimate_item_height(sheet_mixed[0]))
            q_num = _render_two_column_block(pdf, sheet_mixed, q_num,
                                             _write_student_question)

        # ---- Exit Ticket placement ----
        # Switched off: close the page out here and skip the whole block,
        # including the dedicated page it would otherwise claim.
        if not inc["show_what_you_know"]:
            _draw_footer(pdf, standard_code, skill["name"])
            continue

        # Estimate space the Exit Ticket section needs. If there's only one
        # item AND it fits in what's left of page 1, render it inline.
        # Otherwise put it on its own page so it's collectable.
        page_bottom_safe = pdf.h - SB_FOOTER_HEIGHT - 8
        exit_block_h = _estimate_exit_ticket_height(exit_items)
        room_left = page_bottom_safe - pdf.get_y()
        # Pull-up rule: render on the current page whenever the whole block
        # fits — the teacher can cut the exit strip off to collect it. A
        # dedicated page only happens when there genuinely isn't room.
        pull_up = exit_block_h <= room_left - 4

        if pull_up:
            _write_exit_ticket_block(pdf, exit_items, skill, usable_w,
                                     start_q_num=q_num,
                                     include_reflection=True,
                                     header_size="small")
            q_num += len(exit_items)
            _draw_footer(pdf, standard_code, skill["name"])
        else:
            _draw_footer(pdf, standard_code, skill["name"])
            pdf.add_page()
            _write_exit_ticket_block(pdf, exit_items, skill, usable_w,
                                     start_q_num=q_num,
                                     include_reflection=True,
                                     header_size="full")
            q_num += len(exit_items)
            _draw_footer(pdf, standard_code, skill["name"])

    # ================================================================
    # TEACHER COMPANION (optional)
    # ================================================================
    if not include_teacher_companion:
        pdf.output(output_path)
        return output_path

    # Companion pages keep the struggle-quote footer, not the student frame.
    pdf._pnp_frame = None

    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    _draw_sb_header(pdf, PAGE_MARGIN, 5, usable_w, 18,
                    title="Teacher Companion",
                    standard_code=standard_code,
                    r=3, include_name=False, font_title=12, font_name=9)
    pdf.set_y(26)

    # Skill name
    pdf.set_font(ff, "B", 11)
    pdf.set_text_color(*SB_DARK)
    pdf.set_x(PAGE_MARGIN)
    pdf.cell(usable_w, 6, f"Skill: {skill['name']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    # Proficiency band + the state's own descriptor for it. A teacher needs
    # to know a "below proficiency" skill is grade-level work at its least
    # complex entry point, not lower-grade content.
    band = skill.get("pld_band")
    descriptors = (standard_data or {}).get("pld_descriptors") or {}
    if band and descriptors.get(band):
        label = PLD_BAND_LABELS.get(band, band)
        pdf.set_font(ff, "B", 8)
        pdf.set_text_color(*SB_DARK)
        pdf.set_x(PAGE_MARGIN)
        pdf.cell(usable_w, 4, f"ILEARN proficiency level: {label}",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(ff, "", 7.5)
        pdf.set_text_color(*ANNOT_GRAY)
        pdf.set_x(PAGE_MARGIN)
        pdf.multi_cell(usable_w, 3.4, _clean(descriptors[band]),
                       new_x="LMARGIN", new_y="NEXT")
        if band in ("below", "approaching"):
            pdf.set_font(ff, "I", 7)
            pdf.set_x(PAGE_MARGIN)
            pdf.multi_cell(usable_w, 3.2,
                           "This is grade-level work at the entry point of the standard, "
                           "not content from a lower grade.",
                           new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*SB_DARK)
        pdf.ln(2)
    # Dosage / pacing one-liner so a coach can score fidelity (review #6).
    pdf.set_font(ff, "I", 7.5)
    pdf.set_text_color(*ANNOT_GRAY)
    pdf.set_x(PAGE_MARGIN)
    pdf.multi_cell(usable_w, 3.4,
                   SESSION_DOSAGE_V4 if guided_example else SESSION_DOSAGE,
                   new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*SB_DARK)
    pdf.ln(2.5)

    # Quick Reference box — canonical error + redirect script.
    # The redirect script (STOP/PROMPT/PRAISE) prints HERE, not under every
    # item. It's per-skill, not per-question — duplicating it under each
    # item bloated the companion to 4 pages of repeated text.
    error = skill.get("canonical_error", {})
    redirect = skill.get("redirect_script", {})
    y0 = pdf.get_y()
    pdf.set_fill_color(255, 250, 230)
    pdf.set_draw_color(*SB_YELLOW)
    pdf.set_line_width(0.5)
    pdf.rect(PAGE_MARGIN, y0, usable_w, 7, style="DF")
    pdf.set_xy(PAGE_MARGIN + 3, y0 + 1)
    pdf.set_font(ff, "B", 9)
    pdf.set_text_color(*SB_DARK)
    pdf.cell(0, 5, "Quick Reference - Use This Throughout the Session")
    pdf.set_y(y0 + 8)

    # Common error block
    pdf.set_x(PAGE_MARGIN + 3)
    pdf.set_font(ff, "B", 8)
    pdf.set_text_color(180, 50, 50)
    pdf.cell(0, 4, "WATCH FOR:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(ff, "", 8)
    pdf.set_text_color(80, 80, 80)
    pdf.set_x(PAGE_MARGIN + 3)
    pdf.multi_cell(usable_w - 6, 4, error.get("pattern", ""),
                   new_x="LMARGIN", new_y="NEXT")
    if error.get("example"):
        pdf.set_x(PAGE_MARGIN + 3)
        pdf.set_font(ff, "I", 8)
        pdf.multi_cell(usable_w - 6, 4, f"Example: {error.get('example', '')}",
                       new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    # Redirect script — STOP / PROMPT / PRAISE in three colored mini-blocks
    for phase, color, label in [
        ("stop",   (200, 40, 40),  "STOP"),
        ("prompt", (180, 130, 20), "PROMPT"),
        ("praise", (30, 140, 50),  "PRAISE"),
    ]:
        text = redirect.get(phase, "")
        if not text:
            continue
        pdf.set_x(PAGE_MARGIN + 3)
        pdf.set_font(ff, "B", 8)
        pdf.set_text_color(*color)
        label_str = f"{label}: "
        lw = pdf.get_string_width(label_str) + 1
        pdf.cell(lw, 4, label_str, new_x="RIGHT", new_y="TOP")
        pdf.set_font(ff, "", 8)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(usable_w - 6 - lw, 4, text, new_x="LMARGIN", new_y="NEXT")

    y_end = pdf.get_y() + 2
    pdf.set_draw_color(*SB_YELLOW)
    pdf.rect(PAGE_MARGIN, y0, usable_w, y_end - y0, style="D")
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)
    pdf.set_text_color(*SB_DARK)
    pdf.ln(4)

    # Optional Teaching Note — author-written guidance for this specific skill.
    # Only renders when the skill JSON has a non-empty `coaching_note` field.
    # Replaces the per-question "Strategy Tip" boxes the prior version used.
    coaching_note = (skill.get("coaching_note") or "").strip()
    if coaching_note:
        cn_y0 = pdf.get_y()
        pdf.set_fill_color(245, 240, 255)
        pdf.set_draw_color(130, 100, 200)
        pdf.set_line_width(0.5)
        pdf.rect(PAGE_MARGIN, cn_y0, usable_w, 7, style="DF")
        pdf.set_xy(PAGE_MARGIN + 3, cn_y0 + 1)
        pdf.set_font(ff, "B", 9)
        pdf.set_text_color(80, 50, 150)
        pdf.cell(0, 5, "Teaching Note")
        pdf.set_y(cn_y0 + 8)
        pdf.set_x(PAGE_MARGIN + 3)
        pdf.set_font(ff, "", 9)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(usable_w - 6, 4.2, coaching_note, new_x="LMARGIN", new_y="NEXT")
        cn_y_end = pdf.get_y() + 2
        pdf.set_draw_color(130, 100, 200)
        pdf.rect(PAGE_MARGIN, cn_y0, usable_w, cn_y_end - cn_y0, style="D")
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.3)
        pdf.set_text_color(*SB_DARK)
        pdf.ln(4)

    # --- PREREQUISITE CHECK ---
    prereq = skill.get("prerequisite_skill", {})
    prereq_check = prereq.get("check_question", "")
    if prereq_check:
        pdf.set_font(ff, "B", 9)
        pdf.set_text_color(130, 50, 180)
        pdf.set_x(PAGE_MARGIN)
        pdf.cell(usable_w, 5, "PREREQUISITE CHECK (before you start):", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(ff, "", 8)
        pdf.set_text_color(80, 80, 80)
        pdf.set_x(PAGE_MARGIN + 3)
        prereq_desc = prereq.get("description", "")
        prereq_grade = prereq.get("grade", "")
        if prereq_desc:
            pdf.multi_cell(usable_w - 6, 3.5, f"Skill: {prereq_desc} (Grade {prereq_grade})",
                           new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(ff, "I", 8)
        pdf.set_x(PAGE_MARGIN + 3)
        pdf.multi_cell(usable_w - 6, 3.5, f'Ask: "{prereq_check}"',
                       new_x="LMARGIN", new_y="NEXT")
        check_answer = prereq.get("check_answer", "")
        if check_answer:
            pdf.set_font(ff, "B", 8)
            pdf.set_text_color(30, 120, 50)
            pdf.set_x(PAGE_MARGIN + 3)
            pdf.cell(usable_w - 6, 4, "Correct answer:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font(ff, "", 8)
            pdf.set_text_color(60, 60, 60)
            pdf.set_x(PAGE_MARGIN + 6)
            pdf.multi_cell(usable_w - 9, 3.5, check_answer, new_x="LMARGIN", new_y="NEXT")
        if_says = prereq.get("if_student_says", "")
        if if_says:
            pdf.set_font(ff, "B", 8)
            pdf.set_text_color(200, 100, 0)
            pdf.set_x(PAGE_MARGIN + 3)
            pdf.cell(usable_w - 6, 4, "If student answers incorrectly:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font(ff, "", 8)
            pdf.set_text_color(60, 60, 60)
            pdf.set_x(PAGE_MARGIN + 6)
            pdf.multi_cell(usable_w - 9, 3.5, if_says, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(ff, "", 7)
        pdf.set_text_color(130, 50, 180)
        pdf.set_x(PAGE_MARGIN + 3)
        pdf.cell(usable_w - 6, 3.5, "If they can't answer this, go to the prerequisite skill first.",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*SB_DARK)
        pdf.ln(3)

    # --- VOCABULARY ---
    vocab = skill.get("vocabulary", [])
    if vocab:
        pdf.set_font(ff, "B", 9)
        pdf.set_text_color(20, 100, 140)
        pdf.set_x(PAGE_MARGIN)
        pdf.cell(usable_w, 5, "KEY VOCABULARY:", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
        for v in vocab:
            pdf.set_font(ff, "B", 8)
            pdf.set_text_color(*SB_DARK)
            pdf.set_x(PAGE_MARGIN + 3)
            term = v.get("term", "")
            defn = v.get("definition", "")
            pdf.cell(pdf.get_string_width(term) + 2, 3.5, term, new_x="RIGHT", new_y="TOP")
            pdf.set_font(ff, "", 8)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 3.5, f" -- {defn}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*SB_DARK)
        pdf.ln(3)

    # --- MANIPULATIVE / VISUAL SUGGESTION ---
    # If the skill ships a `printable_artifact` AND the user kept the
    # printable activity toggle on, the manipulative is already made and
    # renders on the last page — don't re-print the "go make this" prose.
    # Show a one-line pointer instead. If the artifact is toggled off,
    # fall through to the prose so the teacher still sees the suggestion.
    artifact_for_pointer = skill.get("printable_artifact") if include_printable_artifact else None
    manip = skill.get("manipulative_visual", "")
    if artifact_for_pointer:
        pdf.set_font(ff, "B", 9)
        pdf.set_text_color(20, 120, 60)
        pdf.set_x(PAGE_MARGIN)
        pdf.cell(usable_w, 5, "CONCRETE / VISUAL:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(ff, "I", 8)
        pdf.set_text_color(80, 80, 80)
        pdf.set_x(PAGE_MARGIN + 3)
        pdf.multi_cell(usable_w - 6, 3.5,
                       f'A ready-to-print "{artifact_for_pointer.get("title", "manipulative")}" is included on the last page of this packet -- no prep needed.',
                       new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*SB_DARK)
        pdf.ln(3)
    elif manip:
        pdf.set_font(ff, "B", 9)
        pdf.set_text_color(20, 120, 60)
        pdf.set_x(PAGE_MARGIN)
        pdf.cell(usable_w, 5, "CONCRETE / VISUAL:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(ff, "", 8)
        pdf.set_text_color(80, 80, 80)
        pdf.set_x(PAGE_MARGIN + 3)
        pdf.multi_cell(usable_w - 6, 3.5, manip, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*SB_DARK)
        pdf.ln(3)

    # ---- Per-section question blocks (teacher-facing) ----
    # Numbers come from the student page (N_* above), not a local counter.

    # Section colors keyed by lowercase label prefix — so the teacher
    # companion gets the same red/amber/green/navy badges the student
    # handout uses, not just an inline bold line.
    _SECTION_BADGE = {
        "worked": ((229, 240, 255), (30, 60, 130)),   # blue
        "diagnose": ((247, 220, 220), (153, 27, 27)),
        "we do": ((254, 243, 199), (146, 64, 14)),
        "you do": ((219, 250, 219), (21, 128, 61)),
        "exit": ((219, 234, 254), (30, 64, 175)),
    }

    def _teacher_section(label, items_for_section, start_num):
        if not items_for_section:
            return
        # Pick a badge color by prefix.
        key = next((k for k in _SECTION_BADGE if label.lower().startswith(k)), None)
        bg, fg = _SECTION_BADGE.get(key, ((240, 240, 240), (60, 60, 60)))
        pdf.ln(1)
        y0 = pdf.get_y()
        pdf.set_font(ff, "B", 10)
        bw = pdf.get_string_width(label) + 10
        pdf.set_fill_color(*bg)
        pdf.set_text_color(*fg)
        pdf.set_draw_color(*fg)
        pdf.set_line_width(0.4)
        pdf.rect(PAGE_MARGIN, y0, bw, 6, style="DF")
        pdf.set_xy(PAGE_MARGIN, y0 + 0.5)
        pdf.cell(bw, 5, label, align="C")
        pdf.set_text_color(*SB_DARK)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.3)
        pdf.ln(8)
        # Two-column layout — same row-pair logic as the student page so
        # numbering reads left → right, top → bottom and rows page-break
        # together. Items too tall for a column auto-promote to full width.
        section_label_local = label.lower()

        def _render_one(p, n, it, w):
            _write_teacher_question(p, n, it, skill, section_label_local, w)

        _render_two_column_block(pdf, items_for_section, start_num,
                                 _render_one)

    # Worked Example gets its own scripted block — the teacher follows the
    # numbered Say/Ask/Show steps live in front of students. Designed for a
    # non-math teacher: every step is something they can read aloud or do.
    if we_items or worked_solution:
        # Unnumbered: the student's "Watch & learn" carries no number either.
        # v4 models the student's own worked_solution, not a second problem.
        we_teacher_item = ({"stem": worked_solution.get("stem", ""),
                            "answer": worked_solution.get("answer", "")}
                           if worked_solution else we_items[0])
        _write_worked_example_teacher_block(
            pdf, we_teacher_item, skill, usable_w, _SECTION_BADGE, None,
            solution=worked_solution)

    _teacher_section("DIAGNOSE",           sheet_diag,   N_DIAG)
    _teacher_section("WE DO - Guided",     sheet_we_do,  N_WE_DO)
    _teacher_section("YOU DO - Independent", sheet_you_do, N_YOU_DO)
    _teacher_section("EXIT TICKET",        sheet_exit,   N_EXIT)

    # Scoring note for the exit ticket's written explanation.
    if exit_items:
        dl = (exit_items[-1].get("distractor_logic") or "").strip()
        note = ("Explanation item: accept any reasoning that shows the key idea"
                + (f" -- watch for: {dl}" if dl else
                   " (see the WATCH FOR box on page 1 of this companion)."))
        pdf.ln(1)
        pdf.set_font(ff, "I", 8)
        pdf.set_text_color(100, 100, 100)
        pdf.set_x(PAGE_MARGIN)
        pdf.multi_cell(usable_w, 4, note, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*SB_DARK)

    # Mixed review key, tagged with source skills so the teacher knows
    # which earlier skill each interleaved item exercises.
    if sheet_mixed:
        _teacher_section("MIXED REVIEW", sheet_mixed, N_MIXED)
        sources = sorted({it.get("_mixed_source", "") for it in mixed_items if it.get("_mixed_source")})
        if sources:
            pdf.set_font(ff, "I", 8)
            pdf.set_text_color(100, 100, 100)
            pdf.set_x(PAGE_MARGIN)
            pdf.multi_cell(usable_w, 4,
                           "Pulled from earlier skills: " + ", ".join(sources)
                           + ". A miss here means that skill needs a refresh.",
                           new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(*SB_DARK)

    # Fluency sprint answer strip + faded-example answer.
    extras = []
    if fluency:
        key = "   ".join(
            f"{(it.get('stem') or '').strip()} {it.get('answer', '')}"
            for it in fluency["items"])
        extras.append(("FLUENCY SPRINT KEY (" + fluency.get("title", "") + ")", key))
    if faded_example:
        extras.append(("FADED EXAMPLE",
                       f"Final answer: {faded_example.get('answer', '')}. The blank steps are the student's to voice -- any correct chain of reasoning counts."))
    if guided_example:
        extras.append(("LET'S TRY TOGETHER (guided example)",
                       f"Final answer: {guided_example.get('answer', '')}. Only the first step is given -- the student carries the rest; prompt with the cued thinking move, not the math."))
    if sheet_ftm:
        extras.append((f"FIND THE MISTAKE (#{N_FTM} on the student page)",
                       f"Answer: {ftm_item.get('answer', '')}. Mirrors the WATCH FOR error above -- if the student can't find it, reteach from the Quick Reference redirect."))
    for label, body in extras:
        pdf.ln(2)
        pdf.set_font(ff, "B", 8)
        pdf.set_text_color(*SB_DARK)
        pdf.set_x(PAGE_MARGIN)
        pdf.cell(usable_w, 4, label, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(ff, "", 8)
        pdf.set_text_color(80, 80, 80)
        pdf.set_x(PAGE_MARGIN)
        pdf.multi_cell(usable_w, 3.8, body, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*SB_DARK)

    # --- NEXT STEPS ---
    next_steps = skill.get("next_steps", {})
    if next_steps:
        pdf.ln(5)
        y0 = pdf.get_y()
        pdf.set_fill_color(235, 245, 255)
        pdf.set_draw_color(100, 150, 220)
        pdf.set_line_width(0.5)
        pdf.rect(PAGE_MARGIN, y0, usable_w, 7, style="DF")
        pdf.set_xy(PAGE_MARGIN + 3, y0 + 1)
        pdf.set_font(ff, "B", 9)
        pdf.set_text_color(*SB_DARK)
        pdf.cell(0, 5, "NEXT STEPS")
        pdf.set_y(y0 + 8)

        # Mastery criterion — "pass" used to be undefined (review priority #2).
        pdf.set_font(ff, "B", 8)
        pdf.set_text_color(90, 90, 100)
        pdf.set_x(PAGE_MARGIN + 3)
        pdf.multi_cell(usable_w - 6, 3.6, MASTERY_CRITERION,
                       new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1.5)
        pdf.set_text_color(*SB_DARK)

        if_pass = next_steps.get("if_pass", "")
        if_fail = next_steps.get("if_fail", "")

        if if_pass:
            pdf.set_font(ff, "B", 8)
            pdf.set_text_color(30, 140, 50)
            pdf.set_x(PAGE_MARGIN + 3)
            pdf.cell(usable_w - 6, 4, "If student PASSES exit ticket:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font(ff, "", 8)
            pdf.set_text_color(60, 60, 60)
            pdf.set_x(PAGE_MARGIN + 6)
            pdf.multi_cell(usable_w - 9, 3.5, if_pass, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)

        if if_fail:
            pdf.set_font(ff, "B", 8)
            pdf.set_text_color(200, 50, 50)
            pdf.set_x(PAGE_MARGIN + 3)
            pdf.cell(usable_w - 6, 4, "If student DOES NOT pass exit ticket:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font(ff, "", 8)
            pdf.set_text_color(60, 60, 60)
            pdf.set_x(PAGE_MARGIN + 6)
            pdf.multi_cell(usable_w - 9, 3.5, if_fail, new_x="LMARGIN", new_y="NEXT")

        y_end = pdf.get_y() + 2
        pdf.set_draw_color(100, 150, 220)
        pdf.rect(PAGE_MARGIN, y0, usable_w, y_end - y0, style="D")
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.3)
        pdf.set_text_color(*SB_DARK)
    else:
        pdf.ln(5)
        pdf.set_font(ff, "B", 8)
        pdf.set_text_color(90, 90, 100)
        pdf.set_x(PAGE_MARGIN)
        pdf.multi_cell(usable_w, 3.6, MASTERY_CRITERION, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
        pdf.set_font(ff, "I", 8)
        pdf.set_text_color(100, 100, 100)
        pdf.set_x(PAGE_MARGIN)
        pdf.multi_cell(usable_w, 4,
                       "If correct on exit ticket: Ready to move on!\n"
                       "If wrong on exit ticket: Repeat this skill next session.",
                       new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*SB_DARK)

    # Printable artifact (sort cards / chart / reference card) — last page,
    # so a teacher can grab and print just this page as a student-ready
    # manipulative without making it themselves. Honors the modal's
    # include_printable_artifact toggle.
    artifact = skill.get("printable_artifact") if include_printable_artifact else None
    if artifact:
        _write_printable_artifact_page(pdf, artifact, skill, standard_code, usable_w)

    pdf.output(output_path)
    return output_path


# ── Activity materials (grounded-rote plan follow-up) ────────────────────
# Turns an activity's `content` payload into hand-out-ready pages: cut-apart
# decks for card sorts and matchings, student slips for error analyses, and
# auto-attached blackline masters for hands-on work. Every activity card in
# the web app gets a "Print materials" button that calls this via
# mode: "activity_materials".

_MATERIALS_MASTER_MAP = [
    ("grid paper", "grid_paper", "Grid Paper"),
    ("graph paper", "grid_paper", "Grid Paper"),
    ("fraction strip", "fraction_bars", "Fraction Bar Chart"),
    ("fraction bar", "fraction_bars", "Fraction Bar Chart"),
    ("fraction-bar", "fraction_bars", "Fraction Bar Chart"),
    ("hundredths grid", "hundredths_grid", "Hundredths Grids"),
    ("hundred grid", "hundredths_grid", "Hundredths Grids"),
    ("percent bar", "percent_bar", "Percent Bars"),
    ("tape diagram", "percent_bar", "Percent / Tape Bars"),
    ("number line", "number_line_strip", "Number Line Strips"),
    ("dot plot", "dot_plot_frame", "Dot Plot Frames"),
    ("mini grid", "grid_paper", "Grid Paper"),
]


def _wrap_lines(pdf, text, w):
    """Greedy word-wrap for card text at the current font. Returns lines."""
    words = str(text).split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if pdf.get_string_width(trial) <= w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [""]


def _cut_card_grid(pdf, items, usable_w, cols=3, fill=(248, 250, 253),
                   border=(120, 140, 180), tcolor=(40, 60, 110), font_size=11,
                   min_h=16):
    """Dashed cut-apart card grid with wrapped text; adaptive row height."""
    ff = pdf.ff
    card_w = usable_w / cols
    inner = card_w - 8
    pdf.set_font(ff, "B", font_size)
    line_h = font_size * 0.42
    i = 0
    while i < len(items):
        row = items[i:i + cols]
        wrapped = [_wrap_lines(pdf, it, inner) for it in row]
        card_h = max(min_h, max(len(wl) for wl in wrapped) * line_h + 7)
        # page-break if the row won't fit above the footer
        if pdf.get_y() + card_h > pdf.h - SB_FOOTER_HEIGHT - 8:
            pdf.add_page()
        y0 = pdf.get_y()
        for c, wl in enumerate(wrapped):
            x0 = PAGE_MARGIN + c * card_w
            pdf.set_fill_color(*fill)
            pdf.set_draw_color(*border)
            pdf.set_line_width(0.4)
            pdf.set_dash_pattern(dash=1.2, gap=1.2)
            pdf.rect(x0 + 2, y0, card_w - 4, card_h, style="DF")
            pdf.set_dash_pattern()
            pdf.set_text_color(*tcolor)
            ty = y0 + (card_h - len(wl) * line_h) / 2 + line_h * 0.75
            for ln in wl:
                lw = pdf.get_string_width(ln)
                pdf.text(x0 + (card_w - lw) / 2, ty, ln)
                ty += line_h
        pdf.set_y(y0 + card_h + 3)
        i += cols
    pdf.set_text_color(*SB_DARK)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)


def _materials_subhead(pdf, usable_w, label):
    pdf.ln(2)
    pdf.set_font(pdf.ff, "B", 11)
    pdf.set_text_color(*SB_DARK)
    pdf.set_x(PAGE_MARGIN)
    pdf.cell(usable_w, 7, label, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def write_activity_materials_pdf(standard_code, skill, activity, output_path):
    """One activity, teacher-ready: run sheet + student materials + masters."""
    import hashlib
    title = activity.get("title") or "Activity"
    pdf = MathPDF(title=f"Activity: {title}", standard=standard_code)
    # Manual page management throughout — the grids/keys check remaining
    # height themselves, and footers draw near the bottom margin, so fpdf's
    # auto page break would only spawn ghost pages.
    pdf.set_auto_page_break(auto=False, margin=0)
    pdf.add_page()
    ff = pdf.ff
    usable_w = pdf.w - 2 * PAGE_MARGIN

    # ---- run sheet -------------------------------------------------------
    pdf.set_font(ff, "B", 16)
    pdf.set_text_color(*SB_DARK)
    pdf.set_x(PAGE_MARGIN)
    pdf.cell(usable_w, 9, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(ff, "I", 9)
    pdf.set_text_color(110, 110, 110)
    pdf.set_x(PAGE_MARGIN)
    meta_bits = [t for t in (
        (activity.get("type") or "").replace("_", " "),
        f"{activity.get('time_minutes')} min" if activity.get("time_minutes") else "",
        (activity.get("grouping") or "").replace("_", " "),
    ) if t]
    pdf.multi_cell(usable_w, 4.5,
                   f"For: {skill.get('name','')} ({standard_code})  |  " + "  ·  ".join(meta_bits),
                   new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    mats = activity.get("materials") or []
    if mats:
        _materials_subhead(pdf, usable_w, "Materials")
        pdf.set_font(ff, "", 10)
        pdf.set_text_color(60, 60, 60)
        for m in mats:
            pdf.set_x(PAGE_MARGIN + 2)
            pdf.multi_cell(usable_w - 4, 5, f"[  ]  {m}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*SB_DARK)

    instr = activity.get("instructions") or ""
    if instr:
        _materials_subhead(pdf, usable_w, "How to run it")
        pdf.set_font(ff, "", 10)
        pdf.set_text_color(60, 60, 60)
        for line in instr.split("\n"):
            pdf.set_x(PAGE_MARGIN + 2)
            pdf.multi_cell(usable_w - 4, 5, line, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(0.5)
        pdf.set_text_color(*SB_DARK)

    content = activity.get("content") or {}

    # Teacher answer key on the run sheet (never on student pages).
    key_rows = []
    if content.get("cards"):
        key_rows = [(c.get("text", ""), c.get("category", "")) for c in content["cards"]]
        key_head = ("Card", "Belongs under")
    elif content.get("pairs"):
        key_rows = [(p.get("left", ""), p.get("right", "")) for p in content["pairs"]]
        key_head = ("Left card", "Matches")
    if key_rows:
        _materials_subhead(pdf, usable_w, "Answer key (teacher only)")
        pdf.set_font(ff, "B", 8.5)
        pdf.set_text_color(90, 90, 100)
        cw1, cw2 = usable_w * 0.62, usable_w * 0.38
        pdf.set_x(PAGE_MARGIN)
        pdf.cell(cw1, 5, key_head[0])
        pdf.cell(cw2, 5, key_head[1], new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(ff, "", 8.5)
        for left, right in key_rows:
            if pdf.get_y() > pdf.h - SB_FOOTER_HEIGHT - 12:
                pdf.add_page()
            y0 = pdf.get_y()
            pdf.set_xy(PAGE_MARGIN, y0)
            pdf.multi_cell(cw1, 4.2, str(left), new_x="RIGHT", new_y="TOP")
            x_after = PAGE_MARGIN + cw1
            pdf.set_xy(x_after, y0)
            pdf.multi_cell(cw2, 4.2, str(right), new_x="LMARGIN", new_y="NEXT")
            pdf.set_y(max(pdf.get_y(), y0 + 4.2))
        pdf.set_text_color(*SB_DARK)
    if content.get("decoys"):
        pdf.set_font(ff, "I", 8.5)
        pdf.set_text_color(150, 60, 60)
        pdf.set_x(PAGE_MARGIN)
        pdf.multi_cell(usable_w, 4.2,
                       "Decoys (match nothing): " + ", ".join(str(d) for d in content["decoys"]),
                       new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*SB_DARK)
    if content.get("error_step") or content.get("why"):
        _materials_subhead(pdf, usable_w, "Teacher key")
        pdf.set_font(ff, "", 9)
        pdf.set_text_color(60, 60, 60)
        if content.get("error_step"):
            pdf.set_x(PAGE_MARGIN + 2)
            pdf.multi_cell(usable_w - 4, 4.6, "The wrong move: " + content["error_step"],
                           new_x="LMARGIN", new_y="NEXT")
        if content.get("why"):
            pdf.set_x(PAGE_MARGIN + 2)
            pdf.multi_cell(usable_w - 4, 4.6, "Why / the fix: " + content["why"],
                           new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*SB_DARK)
    _draw_footer(pdf, standard_code, skill.get("name", ""))

    # ---- student materials ----------------------------------------------
    rng_seed = int(hashlib.md5((skill.get("skill_id", "") + title).encode()).hexdigest()[:8], 16)
    rng = random.Random(rng_seed)
    atype = (activity.get("type") or "").lower()

    if content.get("cards"):
        pdf.set_auto_page_break(auto=False, margin=0)
        pdf.add_page()
        pdf.set_font(ff, "B", 13)
        pdf.set_x(PAGE_MARGIN)
        pdf.cell(usable_w, 8, f"{title} -- cut-apart cards", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        cats = content.get("categories") or sorted({c.get("category", "") for c in content["cards"]} - {""})
        if cats:
            _materials_subhead(pdf, usable_w, "Category headers")
            _cut_card_grid(pdf, cats, usable_w, cols=min(3, max(1, len(cats))),
                           fill=(255, 247, 220), border=(180, 130, 20),
                           tcolor=(146, 64, 14), font_size=13, min_h=18)
        deck = [c.get("text", "") for c in content["cards"]]
        # Trap decoys belong in students' hands, not just the teacher key —
        # skip any decoy that duplicates a real card's text.
        deck += [str(d) for d in (content.get("decoys") or []) if str(d) not in deck]
        rng.shuffle(deck)
        _materials_subhead(pdf, usable_w, "Cards (shuffled)")
        _cut_card_grid(pdf, deck, usable_w, cols=3)
        _draw_footer(pdf, standard_code, skill.get("name", ""))

    if content.get("pairs"):
        pdf.set_auto_page_break(auto=False, margin=0)
        pdf.add_page()
        pdf.set_font(ff, "B", 13)
        pdf.set_x(PAGE_MARGIN)
        pdf.cell(usable_w, 8, f"{title} -- matching decks", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        lefts = [p.get("left", "") for p in content["pairs"]]
        rights = [p.get("right", "") for p in content["pairs"]] + [str(d) for d in (content.get("decoys") or [])]
        rng.shuffle(lefts)
        rng.shuffle(rights)
        _materials_subhead(pdf, usable_w, "Deck A")
        _cut_card_grid(pdf, lefts, usable_w, cols=3)
        _materials_subhead(pdf, usable_w, "Deck B (includes decoys)")
        _cut_card_grid(pdf, rights, usable_w, cols=3,
                       fill=(240, 252, 244), border=(60, 150, 90), tcolor=(20, 100, 50))
        _draw_footer(pdf, standard_code, skill.get("name", ""))

    if content.get("worked_problem"):
        pdf.set_auto_page_break(auto=False, margin=0)
        pdf.add_page()
        pdf.set_font(ff, "B", 13)
        pdf.set_x(PAGE_MARGIN)
        pdf.cell(usable_w, 8, f"{title} -- student slips", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        slip_h = (pdf.h - SB_FOOTER_HEIGHT - pdf.get_y() - 16) / 3
        for _s in range(3):
            y0 = pdf.get_y()
            pdf.set_draw_color(120, 140, 180)
            pdf.set_line_width(0.4)
            pdf.set_dash_pattern(dash=1.5, gap=1.5)
            pdf.rect(PAGE_MARGIN, y0, usable_w, slip_h, style="D")
            pdf.set_dash_pattern()
            pdf.set_xy(PAGE_MARGIN + 4, y0 + 3)
            pdf.set_font(ff, "B", 10)
            pdf.multi_cell(usable_w - 8, 5, content["worked_problem"],
                           new_x="LMARGIN", new_y="NEXT")
            pdf.set_x(PAGE_MARGIN + 4)
            pdf.set_font(ff, "", 9)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(usable_w - 8, 4.6,
                           "1. Circle the exact line where the work goes wrong.\n"
                           "2. Fix it and finish the problem correctly.\n"
                           "3. In one sentence: WHY is the wrong move tempting, and what does the model say instead?",
                           new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(*SB_DARK)
            pdf.set_y(y0 + slip_h + 4)
        _draw_footer(pdf, standard_code, skill.get("name", ""))

    # ---- auto-attached blackline masters ---------------------------------
    attached = set()
    for m in mats:
        ml = str(m).lower()
        for kw, kind, mtitle in _MATERIALS_MASTER_MAP:
            if kw in ml and kind not in attached:
                attached.add(kind)
                _write_printable_artifact_page(
                    pdf,
                    {"kind": kind, "title": mtitle,
                     "instructions": f"Master for '{title}' -- print one per pair/group as the materials list calls for."},
                    skill, standard_code, usable_w)

    pdf.output(output_path)
    return output_path


def main():
    raw = sys.stdin.read()
    params = json.loads(raw)

    standard = params["standard"]
    skill_id = params["skill_id"]

    skill, standard_data = load_skill_data(standard, skill_id)
    if not skill:
        print(json.dumps({"error": f"Skill {skill_id} not found for {standard}"}))
        sys.exit(1)

    skill = clean_dict(skill)

    # System temp dir: always writable, including on read-only container
    # filesystems (e.g. Cloud Run, where only /tmp is guaranteed writable).
    import tempfile
    tmp_dir = tempfile.gettempdir()
    os.makedirs(tmp_dir, exist_ok=True)
    output_path = os.path.join(tmp_dir, f"skill_{skill_id}_{random.randint(1000,9999)}.pdf")

    student_copies = int(params.get("student_copies", 1))
    include_teacher = params.get("include_teacher_companion", True)
    include_artifact = params.get("include_printable_artifact", True)
    session = int(params.get("session", 1))
    if session not in (1, 2):
        session = 1

    # `mode: "items"` returns the resolved problem set as JSON instead of
    # rendering a PDF. The projection page calls this so the projected
    # problems match the printed packet exactly for the same (skill, session).
    mode = (params.get("mode") or "pdf").lower()
    # `mode: "activity_materials"` renders one activity's hand-out pages
    # (cut-apart decks, slips, masters) instead of the packet.
    if mode == "activity_materials":
        idx = int(params.get("activity_index", 0))
        acts = skill.get("activities") or []
        if idx < 0 or idx >= len(acts):
            print(json.dumps({"error": f"activity_index {idx} out of range (skill has {len(acts)} activities)"}))
            sys.exit(1)
        write_activity_materials_pdf(
            standard_data["standard_code"] if isinstance(standard_data, dict) else standard,
            skill, acts[idx], output_path)
        print(json.dumps({"path": output_path}))
        return

    if mode == "items":
        items = _fill_items_from_engine(skill, standard["standard_code"] if isinstance(standard, dict) else standard,
                                        target_count=10, session=session)
        sections = _allocate_items(items)
        # Tag each item with its section so the projection runner can
        # show the same colored badges the packet does.
        labeled = []
        # Section labels mirror the printed session sheet so the board and
        # the paper say the same thing. When the skill has an authored
        # worked_solution, the pool worked-example item is skipped here too
        # (the sheet prints the annotated solution instead) — the projection
        # gets a dedicated worked-example slide from the payload below.
        def _webify_rd(rd):
            """Pre-convert parametric shape render_data to svg_html so the
            web projection renders figures without knowing the shape types."""
            if not rd:
                return rd
            svg = _shape_render_data_to_svg(rd)
            if svg:
                return {"type": "svg_html", "svg_html": svg}
            return rd

        def _webify_ws(block):
            """Webify the figure inside a worked_solution / faded_example so
            the deck draws it at the modeling moment (review priority #1)."""
            if not block or not block.get("render_data"):
                return block
            out = dict(block)
            out["render_data"] = _webify_rd(block["render_data"])
            return out

        has_ws = bool(skill.get("worked_solution"))
        # v4 skills replace the diagnose items with the guided_example block
        # on paper — mirror that here so the board matches the sheet.
        has_guided = bool(skill.get("guided_example"))
        section_plan = [
            ("we_do", "Your Turn"),
            ("you_do", "Your Turn"),
            ("exit", "Show What You Know"),
        ]
        if not has_guided:
            section_plan.insert(0, ("diagnose", "Let's Try Together"))
        if not has_ws:
            section_plan.insert(0, ("worked_example", "Worked Example"))
        for sec_key, label in section_plan:
            for it in sections[sec_key]:
                labeled.append({
                    "stem": it.get("stem", ""),
                    "answer": it.get("answer", ""),
                    "choices": it.get("choices"),
                    "section": label,
                    # Diagrams + multi-part for the projection's InlineDiagram
                    # component. None means the projection just renders text.
                    "render_data": _webify_rd(it.get("render_data")),
                    "choices_render": [
                        _webify_rd(cr) for cr in it["choices_render"]
                    ] if it.get("choices_render") else None,
                    "parts": it.get("parts"),
                    # Conceptual item types (error_analysis shows its work).
                    "type": it.get("type"),
                    "shown_work": it.get("shown_work"),
                })
        # Interleaved mixed-review items (Session Sheet v2) so the projected
        # sequence matches the printed sheet. Inserted before the exit items.
        mixed = _resolve_mixed_review(skill, standard_data, session=session)
        if mixed:
            exit_count = len(sections["exit"])
            insert_at = len(labeled) - exit_count
            mixed_labeled = [{
                "stem": it.get("stem", ""),
                "answer": it.get("answer", ""),
                "choices": it.get("choices"),
                "section": "Remember These?",
                "render_data": _webify_rd(it.get("render_data")),
                "choices_render": None,
                "parts": None,
                "type": it.get("type"),
                "shown_work": it.get("shown_work"),
            } for it in mixed]
            labeled = labeled[:insert_at] + mixed_labeled + labeled[insert_at:]

        # Session-sheet extras so the projection can open with the same
        # arc the paper prints: fluency sprint, worked example, faded
        # example, sentence starters.
        fluency = _resolve_fluency_items(skill, standard_data, session=session)
        print(json.dumps({
            "items": labeled,
            "session": session,
            "fluency": fluency,
            "worked_solution": _webify_ws(skill.get("worked_solution")),
            "faded_example": _webify_ws(skill.get("faded_example")),
            "guided_example": _webify_ws(skill.get("guided_example")),
            "sentence_starters": skill.get("sentence_starters"),
        }))
        return

    # Note: a previous version of this generator accepted a `strategies` array
    # forwarded from the Next.js API route. That feature is gone — per-question
    # "Strategy Tip" boxes felt like AI slop. The teacher's pedagogical guidance
    # now comes from a single optional `coaching_note` field on the skill JSON.
    # We silently ignore any legacy `strategies` payload to stay backward-compat
    # with older API clients during deploy.

    generate_skill_packet_pdf(skill, standard_data, output_path,
                               student_copies=student_copies,
                               include_teacher_companion=include_teacher,
                               include_printable_artifact=include_artifact,
                               session=session,
                               sections=params.get("sections"))
    print(json.dumps({"path": output_path, "size": os.path.getsize(output_path)}))


if __name__ == "__main__":
    main()
