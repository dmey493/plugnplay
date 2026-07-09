"""
Generate a 1-page PLACEMENT & SCOPE sheet for a standard, rendered from the
`diagnostic_flow` + `skill_tree` + progression that already live in the skill
JSON but were never surfaced teacher/admin-facing (review priority #8).

It answers "which of these skills do I put this student on, and why" for an
MTSS/RTI coordinator, and doubles as the standard's scope-and-sequence map.

Usage:
  echo '{"standard":"6.NS.4"}' | python engine/generate_placement_sheet.py
Emits JSON: {"path": "<pdf>"} on stdout.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.pdf_generator import (
    MathPDF, PAGE_MARGIN, SB_DARK, _draw_sb_header,
)

RULE_GRAY = (216, 219, 226)
ANNOT_GRAY = (112, 117, 128)

COLUMN_LABELS = [
    ("foundation", "Foundation (below grade)", (254, 226, 226), (153, 27, 27)),
    ("looking_back", "Looking Back", (254, 243, 199), (146, 64, 14)),
    ("on_grade", "On Grade", (219, 234, 254), (30, 64, 175)),
    ("looking_forward", "Looking Forward", (219, 250, 219), (21, 128, 61)),
]


def _load(standard):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "Cooties", "data", "skills", f"{standard}.json")
    if not os.path.exists(path):
        path = os.path.join(root, "web", "content", "skills", f"{standard}.json")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _chip(pdf, label, subtitle, tint, ink, usable_w):
    ff = pdf.ff
    y0 = pdf.get_y()
    pdf.set_font(ff, "B", 9.5)
    bw = pdf.get_string_width(label) + 9
    pdf.set_fill_color(*tint)
    pdf.rect(PAGE_MARGIN, y0, bw, 6.5, style="F", round_corners=True, corner_radius=3.2)
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
        pdf.multi_cell(usable_w, 4, subtitle, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(0.5)
    pdf.set_text_color(*SB_DARK)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)


def generate_placement_sheet(standard, output_path):
    data = _load(standard)
    skills = {s["skill_id"]: s for s in data.get("skills", [])}
    name = lambda sid: skills[sid]["name"] if sid in skills else sid
    flow = data.get("diagnostic_flow", {}) or {}

    pdf = MathPDF()
    pdf.header = lambda: None   # suppress MathPDF's default ILEARN header
    pdf.footer = lambda: None
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    ff = pdf.ff
    usable_w = pdf.w - 2 * PAGE_MARGIN

    _draw_sb_header(pdf, PAGE_MARGIN, 5, usable_w, 16,
                    title=f"Placement Guide  -  {standard}",
                    standard_code="", r=3, include_name=False,
                    font_title=12, font_name=9)
    pdf.set_y(24)
    pdf.set_font(ff, "", 9)
    pdf.set_text_color(*ANNOT_GRAY)
    pdf.set_x(PAGE_MARGIN)
    pdf.multi_cell(usable_w, 4.2, data.get("standard_text", ""),
                   new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_text_color(*SB_DARK)

    # ---- START HERE (entry probe) ----
    entry = flow.get("entry_skill")
    if entry:
        _chip(pdf, "Start here", "Give this skill's exit ticket as a 2-item placement probe.",
              (219, 234, 254), (30, 64, 175), usable_w)
        pdf.set_font(ff, "B", 10)
        pdf.set_x(PAGE_MARGIN + 3)
        pdf.multi_cell(usable_w - 6, 5, f"{entry} - {name(entry)}",
                       new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    # ---- DECISION TREE ----
    _chip(pdf, "Then place them", flow.get("description", ""),
          (254, 243, 199), (146, 64, 14), usable_w)

    def _branch(head, ids, ink):
        if not ids:
            return
        pdf.set_font(ff, "B", 9)
        pdf.set_text_color(*ink)
        pdf.set_x(PAGE_MARGIN + 3)
        pdf.cell(usable_w - 6, 4.6, head, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(ff, "", 9)
        pdf.set_text_color(60, 60, 60)
        for sid in ids:
            pdf.set_x(PAGE_MARGIN + 7)
            pdf.multi_cell(usable_w - 10, 4.2, f"-> {sid}: {name(sid)}",
                           new_x="LMARGIN", new_y="NEXT")
        pdf.ln(0.5)

    _branch("If the student PASSES the probe - confirm / move up with:",
            flow.get("if_pass", []), (21, 128, 61))
    _branch("If the student STRUGGLES - remediate with:",
            flow.get("if_fail", []), (200, 50, 50))
    _branch("For a sharper diagnosis, branch to:",
            flow.get("branch_skills", []), (30, 64, 175))
    pdf.set_text_color(*SB_DARK)
    pdf.ln(2)

    # ---- SKILL MAP (scope & sequence, by column, with prerequisites) ----
    _chip(pdf, "Skill map", "The full progression for this standard. Arrows show the prerequisite each skill builds on.",
          (237, 233, 254) if False else (226, 232, 240), (51, 65, 85), usable_w)
    for col_key, col_label, tint, ink in COLUMN_LABELS:
        col_skills = [s for s in data.get("skills", []) if s.get("column") == col_key]
        if not col_skills:
            continue
        pdf.set_font(ff, "B", 8.5)
        pdf.set_fill_color(*tint)
        pdf.set_text_color(*ink)
        lw = pdf.get_string_width(col_label) + 6
        pdf.set_x(PAGE_MARGIN + 1)
        pdf.cell(lw, 5, f" {col_label}", new_x="LMARGIN", new_y="NEXT", fill=True,
                 align="L")
        pdf.set_text_color(*SB_DARK)
        for s in col_skills:
            sid = s["skill_id"]
            prereq = (s.get("prerequisite_skill") or {}).get("skill_id")
            pdf.set_font(ff, "B", 8.5)
            pdf.set_x(PAGE_MARGIN + 4)
            pdf.cell(20, 4.4, sid, new_x="RIGHT", new_y="TOP")
            pdf.set_font(ff, "", 8.5)
            tail = f"  (from {prereq})" if prereq else ""
            pdf.multi_cell(usable_w - 26, 4.4, f"{s.get('name','')}{tail}",
                           new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    pdf.output(output_path)
    return output_path


def main():
    raw = sys.stdin.read()
    req = json.loads(raw) if raw.strip() else {}
    standard = req.get("standard", "6.NS.4")
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(root, "engine", "output")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"placement_{standard}.pdf")
    generate_placement_sheet(standard, out)
    print(json.dumps({"path": out}))


if __name__ == "__main__":
    main()
