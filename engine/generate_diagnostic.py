"""
Generate a diagnostic or progress monitoring PDF for a standard.

DIAGNOSTIC: Tests every skill in the standard.
  - Foundation skills: 1 question each
  - Looking Back / On Grade / Looking Forward: 2 questions each
  - Each question tagged with [S1], [S2], [F1], etc.

PROGRESS MONITORING: Tests only the skills the teacher selects.
  - Same format as diagnostic
  - Same question counts per skill type

Usage:
  echo '{"standard":"6.AF.1","mode":"diagnostic"}' | python engine/generate_diagnostic.py
  echo '{"standard":"6.AF.1","mode":"progress","skill_ids":["6AF1-S1","6AF1-S5"]}' | python engine/generate_diagnostic.py
"""

import json
import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.pdf_generator import (
    MathPDF, PAGE_MARGIN, SB_YELLOW, SB_BROWN, SB_DARK, SB_FOOTER_HEIGHT,
    _draw_sb_header, _STRUGGLE_QUOTES,
)
from engine.generate_skill_packet import _clean, clean_dict, load_skill_data


def load_standard_skills(standard_code):
    """Load full standard data including all skills."""
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
                return json.load(f)
    return None


def _draw_footer(pdf, standard_code, label):
    footer_h = SB_FOOTER_HEIGHT
    footer_y = pdf.h - footer_h
    pdf.set_fill_color(*SB_YELLOW)
    pdf.rect(0, footer_y, pdf.w, footer_h, style="F")
    pdf.set_draw_color(*SB_BROWN)
    pdf.set_line_width(0.4)
    pdf.line(0, footer_y, pdf.w, footer_y)
    quote = _STRUGGLE_QUOTES[hash(standard_code + label) % len(_STRUGGLE_QUOTES)]
    pdf.set_text_color(*SB_BROWN)
    pdf.set_font(pdf.ff, "I", 7)
    pdf.set_xy(PAGE_MARGIN, footer_y + 2)
    pdf.cell(pdf.w * 0.55, 5, f'"{quote}"')
    pdf.set_font(pdf.ff, "", 7)
    text = f"Plug N Play  |  {label}  |  Page {pdf.page_no()}"
    tw = pdf.get_string_width(text)
    pdf.set_xy(pdf.w - PAGE_MARGIN - tw, footer_y + 2)
    pdf.cell(tw, 5, text)
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_line_width(0.3)


def _estimate_q_height(item):
    """Rough mm a tagged question needs (stem + choices/answer line)."""
    stem_len = len(item.get("stem", ""))
    h = 12 + (stem_len // 70) * 5
    choices = item.get("choices") or []
    h += len(choices) * 5
    if not choices:
        h += 12
    return h + 4  # trailing pdf.ln(4)


def _write_question_with_tag(pdf, q_num, item, skill_id_short, usable_w,
                              standard_code=None, label=None):
    """Write a question with a skill tag like [S1] in front of the number.

    Manually checks for page overflow and breaks to a new page when there
    isn't room. With auto_page_break disabled (to prevent phantom blank
    pages from the footer cell), we have to drive page breaks ourselves."""
    ff = pdf.ff
    # Manual page-break check.
    page_bottom_safe = pdf.h - SB_FOOTER_HEIGHT - 8
    if pdf.get_y() + _estimate_q_height(item) > page_bottom_safe:
        if standard_code is not None and label is not None:
            _draw_footer(pdf, standard_code, label)
        pdf.add_page()
    pdf.set_font(ff, "B", 10)
    pdf.set_text_color(*SB_DARK)
    pdf.set_x(PAGE_MARGIN)

    # Skill tag in a colored badge
    tag = f"[{skill_id_short}]"
    is_foundation = skill_id_short.startswith("F")
    badge_bg = (254, 226, 226) if is_foundation else (219, 234, 254)
    badge_fg = (153, 27, 27) if is_foundation else (30, 64, 175)

    tag_w = pdf.get_string_width(tag) + 4
    pdf.set_fill_color(*badge_bg)
    pdf.set_text_color(*badge_fg)
    pdf.set_draw_color(*badge_fg)
    pdf.set_line_width(0.2)
    y_top = pdf.get_y()
    pdf.rect(PAGE_MARGIN, y_top, tag_w, 5, style="DF")
    pdf.set_xy(PAGE_MARGIN, y_top + 0.3)
    pdf.set_font(ff, "B", 7)
    pdf.cell(tag_w, 4, tag, align="C")

    # Question number after the tag
    pdf.set_font(ff, "B", 10)
    pdf.set_text_color(*SB_DARK)
    pdf.set_xy(PAGE_MARGIN + tag_w + 2, y_top)
    pdf.cell(7, 5, f"{q_num}", new_x="RIGHT", new_y="TOP")

    # Question stem
    pdf.set_font(ff, "", 10)
    text_x = PAGE_MARGIN + tag_w + 9
    pdf.set_xy(text_x, y_top)
    pdf.multi_cell(usable_w - (tag_w + 11), 5, item["stem"], new_x="LMARGIN", new_y="NEXT")

    # Choices (if MC) or answer line
    choices = item.get("choices")
    if choices:
        labels = ["a", "b", "c", "d", "e", "f"]
        pdf.ln(1)
        for j, choice in enumerate(choices):
            lbl = labels[j] if j < len(labels) else str(j + 1)
            pdf.set_font(ff, "", 10)
            pdf.set_x(PAGE_MARGIN + tag_w + 12)
            pdf.cell(usable_w - (tag_w + 14), 5, f"{lbl}.  {choice}", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.ln(2)
        pdf.set_x(PAGE_MARGIN + tag_w + 12)
        pdf.set_draw_color(0, 0, 0)
        pdf.line(PAGE_MARGIN + tag_w + 12, pdf.get_y() + 3,
                 PAGE_MARGIN + usable_w * 0.7, pdf.get_y() + 3)
        pdf.ln(8)

    pdf.ln(4)


def _write_teacher_question_short(pdf, q_num, item, skill, skill_id_short, usable_w):
    """Compact teacher question entry: tag + question + answer + WATCH FOR."""
    ff = pdf.ff

    if pdf.get_y() > pdf.h - 50:
        pdf.add_page()

    y_start = pdf.get_y()

    # Skill tag
    tag = f"[{skill_id_short}]"
    is_foundation = skill_id_short.startswith("F")
    badge_bg = (254, 226, 226) if is_foundation else (219, 234, 254)
    badge_fg = (153, 27, 27) if is_foundation else (30, 64, 175)
    tag_w = pdf.get_string_width(tag) + 4

    pdf.set_fill_color(*badge_bg)
    pdf.set_text_color(*badge_fg)
    pdf.set_draw_color(*badge_fg)
    pdf.set_line_width(0.2)
    pdf.rect(PAGE_MARGIN, y_start, tag_w, 4.5, style="DF")
    pdf.set_xy(PAGE_MARGIN, y_start + 0.2)
    pdf.set_font(ff, "B", 7)
    pdf.cell(tag_w, 4, tag, align="C")

    # Question number
    pdf.set_font(ff, "B", 9)
    pdf.set_text_color(*SB_DARK)
    pdf.set_xy(PAGE_MARGIN + tag_w + 2, y_start)
    pdf.cell(6, 4, f"{q_num}.")

    # Stem
    pdf.set_font(ff, "", 8)
    pdf.set_xy(PAGE_MARGIN + tag_w + 8, y_start)
    pdf.multi_cell(usable_w - (tag_w + 10), 4, item["stem"], new_x="LMARGIN", new_y="NEXT")

    # Answer
    answer = item.get("answer", "")
    pdf.set_font(ff, "B", 8)
    pdf.set_text_color(30, 120, 50)
    pdf.set_x(PAGE_MARGIN + tag_w + 8)
    pdf.cell(usable_w - (tag_w + 10), 4, f"Answer: {answer}", new_x="LMARGIN", new_y="NEXT")

    # If they get it wrong, this skill is the gap
    error = skill.get("canonical_error", {})
    pdf.set_font(ff, "I", 7)
    pdf.set_text_color(120, 120, 120)
    pdf.set_x(PAGE_MARGIN + tag_w + 8)
    pdf.multi_cell(usable_w - (tag_w + 10), 3.5,
                   f"If wrong: {error.get('pattern', 'Check this skill.')}",
                   new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*SB_DARK)
    pdf.ln(2)

    # Separator
    pdf.set_draw_color(220, 220, 220)
    pdf.line(PAGE_MARGIN, pdf.get_y(), PAGE_MARGIN + usable_w, pdf.get_y())
    pdf.set_draw_color(0, 0, 0)
    pdf.ln(2)


def select_questions(skill, count):
    """Pick `count` items from a skill's sample_items."""
    items = skill.get("sample_items", [])
    if not items:
        return []
    if count >= len(items):
        return items[:count]
    return random.sample(items, count)


def _short_skill_id(skill_id):
    """6AF1-S1 -> S1, 6AF1-F2 -> F2"""
    parts = skill_id.split("-")
    return parts[-1] if len(parts) > 1 else skill_id


def generate_diagnostic_pdf(standard_data, output_path,
                              mode="diagnostic", skill_ids=None,
                              student_copies=1, include_teacher_companion=True,
                              questions_per_skill=None):
    """Generate diagnostic or progress monitoring PDF.

    `questions_per_skill` only applies in progress mode; diagnostic mode
    keeps the foundation=1, others=2 default because it tests every
    skill and a higher per-skill count would overwhelm the page.
    """
    standard_code = standard_data["standard_code"]
    all_skills = standard_data["skills"]

    # Filter skills based on mode
    if mode == "progress" and skill_ids:
        skills = [s for s in all_skills if s["skill_id"] in skill_ids]
    else:
        skills = all_skills

    # Per-skill question count.
    # Diagnostic mode: keep historical defaults (foundation=1, rest=2).
    # Progress mode: honor the user's `questions_per_skill` (1, 2, or 3),
    # applied uniformly across selected skills regardless of column.
    if mode == "progress" and questions_per_skill in (1, 2, 3):
        per_skill_count = int(questions_per_skill)
    else:
        per_skill_count = None  # fall back to per-skill default

    # Build the question list: each entry is (skill, item, skill_id_short)
    questions = []
    for skill in skills:
        if per_skill_count is not None:
            count = per_skill_count
        else:
            is_foundation = skill.get("column") == "foundation"
            count = 1 if is_foundation else 2
        items = select_questions(skill, count)
        short_id = _short_skill_id(skill["skill_id"])
        for item in items:
            questions.append((skill, item, short_id))

    if not questions:
        raise ValueError("No questions to generate")

    label = "Diagnostic" if mode == "diagnostic" else "Progress Check"

    pdf = MathPDF()
    ff = pdf.ff
    # Disable auto-page-break: we manually call _draw_footer + add_page per
    # student copy. With auto-break on, the footer cell at the bottom of
    # each page tripped a phantom page-break and produced 1-2 blank pages
    # before the teacher companion.
    pdf.set_auto_page_break(auto=False, margin=0)
    pdf.header = lambda: None
    pdf.footer = lambda: None
    usable_w = pdf.w - 2 * PAGE_MARGIN

    # ================================================================
    # STUDENT PAGES (repeated for each copy)
    # ================================================================
    for _copy in range(student_copies):
        pdf.add_page()

        # Header
        _draw_sb_header(pdf, PAGE_MARGIN, 5, usable_w, 22,
                        title=f"Plug N Play  -  {standard_code}",
                        standard_code="",
                        r=3, include_name=True, font_title=12, font_name=9)
        pdf.set_y(30)

        # Mode badge
        pdf.set_font(ff, "B", 9)
        if mode == "diagnostic":
            badge_bg = (254, 226, 226)
            badge_fg = (153, 27, 27)
            badge_text = "DIAGNOSTIC"
        else:
            badge_bg = (220, 252, 231)
            badge_fg = (21, 128, 61)
            badge_text = "PROGRESS CHECK"

        bw = pdf.get_string_width(badge_text) + 10
        pdf.set_fill_color(*badge_bg)
        pdf.set_text_color(*badge_fg)
        pdf.set_draw_color(200, 200, 200)
        pdf.rect(PAGE_MARGIN, pdf.get_y(), bw, 6, style="DF")
        pdf.set_xy(PAGE_MARGIN, pdf.get_y() + 0.5)
        pdf.cell(bw, 5, badge_text, align="C")
        pdf.set_text_color(*SB_DARK)
        pdf.set_fill_color(255, 255, 255)
        pdf.ln(9)

        # Instructions
        pdf.set_font(ff, "", 9)
        pdf.set_text_color(80, 80, 80)
        pdf.set_x(PAGE_MARGIN)
        if mode == "diagnostic":
            instructions = "Try every problem. It's okay if you don't know an answer -- just show your thinking. We use this to find out what to teach next."
        else:
            instructions = "Show what you've learned. Try every problem and show your work."
        pdf.multi_cell(usable_w, 4, instructions, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*SB_DARK)
        pdf.ln(3)

        # Render all questions. Pass standard_code + label so the helper
        # can draw a footer + spawn a new page when the next question
        # won't fit on the current page.
        for i, (skill, item, short_id) in enumerate(questions):
            _write_question_with_tag(pdf, i + 1, item, short_id, usable_w,
                                     standard_code=standard_code, label=label)

        _draw_footer(pdf, standard_code, label)

    # ================================================================
    # TEACHER COMPANION
    # ================================================================
    if not include_teacher_companion:
        pdf.output(output_path)
        return output_path

    # Re-enable auto-page-break for the teacher companion. The Skill
    # Tracker is now on its own page; the Answer Key gets its own page
    # too, with auto-break taking care of overflow inside the answer
    # list.
    pdf.set_auto_page_break(auto=True, margin=20)

    # ----- Skill Tracker page -----
    pdf.add_page()
    _draw_sb_header(pdf, PAGE_MARGIN, 5, usable_w, 18,
                    title=f"Teacher {label} - Skill Tracker",
                    standard_code=standard_code,
                    r=3, include_name=False, font_title=12, font_name=9)
    pdf.set_y(26)

    # How to use
    pdf.set_font(ff, "B", 10)
    pdf.set_text_color(*SB_DARK)
    pdf.set_x(PAGE_MARGIN)
    pdf.cell(usable_w, 6, "How to Use", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(ff, "", 8)
    pdf.set_text_color(80, 80, 80)
    pdf.set_x(PAGE_MARGIN)
    if mode == "diagnostic":
        how_to = ("Each question is tagged with a skill code (e.g., [S1], [F2]). "
                  "If a student misses a question, that's the skill they need work on. "
                  "Mark which skills are gaps below, then generate Skill Packets for those specific skills.")
    else:
        how_to = ("Each question is tagged with the skill being assessed. "
                  "Compare results to the original diagnostic -- did the intervention move the needle? "
                  "If they still miss a skill, repeat that Skill Packet.")
    pdf.multi_cell(usable_w, 4, how_to, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*SB_DARK)
    pdf.ln(4)

    # Tracker title
    pdf.set_font(ff, "B", 12)
    pdf.set_text_color(*SB_DARK)
    pdf.set_x(PAGE_MARGIN)
    pdf.cell(usable_w, 7, "Skill Tracker", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Tracker grid — bigger row height now that the table owns the page
    pdf.set_font(ff, "B", 9)
    pdf.set_fill_color(245, 245, 245)
    pdf.set_draw_color(180, 180, 180)
    pdf.set_line_width(0.2)

    col_tag_w = 18
    col_name_w = usable_w - col_tag_w - 36
    col_check_w = 36

    pdf.set_x(PAGE_MARGIN)
    pdf.cell(col_tag_w, 7, "Tag", border=1, fill=True, align="C")
    pdf.cell(col_name_w, 7, "Skill", border=1, fill=True)
    pdf.cell(col_check_w, 7, "Mastered? (Y/N)", border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font(ff, "", 9)
    pdf.set_text_color(60, 60, 60)
    for skill in skills:
        short_id = _short_skill_id(skill["skill_id"])
        pdf.set_x(PAGE_MARGIN)
        pdf.cell(col_tag_w, 7, short_id, border=1, align="C")
        pdf.cell(col_name_w, 7, skill["name"][:80], border=1)
        pdf.cell(col_check_w, 7, "", border=1)
        pdf.ln()

    pdf.set_text_color(*SB_DARK)

    # ----- Answer Key page (its own page, after the tracker) -----
    pdf.add_page()
    _draw_sb_header(pdf, PAGE_MARGIN, 5, usable_w, 18,
                    title=f"Teacher {label} - Answer Key",
                    standard_code=standard_code,
                    r=3, include_name=False, font_title=12, font_name=9)
    pdf.set_y(26)

    pdf.set_font(ff, "B", 12)
    pdf.set_text_color(*SB_DARK)
    pdf.set_x(PAGE_MARGIN)
    pdf.cell(usable_w, 7, "Answer Key", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    for i, (skill, item, short_id) in enumerate(questions):
        _write_teacher_question_short(pdf, i + 1, item, skill, short_id, usable_w)

    pdf.output(output_path)
    return output_path


def main():
    raw = sys.stdin.read()
    params = json.loads(raw)

    standard = params["standard"]
    mode = params.get("mode", "diagnostic")
    skill_ids = params.get("skill_ids", [])
    student_copies = int(params.get("student_copies", 1))
    include_teacher = params.get("include_teacher_companion", True)
    questions_per_skill = params.get("questions_per_skill")
    if questions_per_skill is not None:
        try:
            questions_per_skill = int(questions_per_skill)
        except (TypeError, ValueError):
            questions_per_skill = None

    standard_data = load_standard_skills(standard)
    if not standard_data:
        print(json.dumps({"error": f"Standard {standard} not found"}))
        sys.exit(1)

    standard_data = clean_dict(standard_data)

    # System temp dir: always writable, including on read-only container
    # filesystems (e.g. Cloud Run, where only /tmp is guaranteed writable).
    import tempfile
    tmp_dir = tempfile.gettempdir()
    os.makedirs(tmp_dir, exist_ok=True)
    safe = standard.replace(".", "_")
    output_path = os.path.join(tmp_dir, f"{mode}_{safe}_{random.randint(1000,9999)}.pdf")

    try:
        generate_diagnostic_pdf(standard_data, output_path,
                                 mode=mode, skill_ids=skill_ids,
                                 student_copies=student_copies,
                                 include_teacher_companion=include_teacher,
                                 questions_per_skill=questions_per_skill)
        print(json.dumps({"path": output_path, "size": os.path.getsize(output_path)}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
