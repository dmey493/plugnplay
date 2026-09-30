"""Spiral review sheets: several standards mixed on one sheet, a sheet per week.

Page (A4 portrait, the same Struggle Bus look as the other generator PDFs):
  - yellow rounded banner "Spiral Review  -  Grade 7  |  Week 5" with Name / Date
  - a strip with the directions and a confidence check
  - one box per problem, two to a row; an odd last problem gets the full width
  - yellow footer bar with a productive-struggle quote

Every problem is measured before anything is drawn. A week stays on one page
when its rows fit there, shrinking the text a little if that is all it takes.
Otherwise it breaks between rows, never through a problem, onto as few pages
as possible, so a page can hold 8, 6, 4 or 2 problems.
"""

import math
import re
import zlib
from dataclasses import dataclass

from fpdf.enums import RenderStyle

from engine.models import ItemType
from engine.pdf_generator import (
    MathPDF,
    SB_BROWN,
    SB_DARK,
    SB_YELLOW,
    SB_YELLOW_LIGHT,
    SB_YELLOW_PALE,
    _STRUGGLE_QUOTES,
    _draw_sb_header,
    _write_column_question,
)

# Page geometry, in mm (A4 portrait is 210 x 297).
MARGIN_X = 12
GRID_W = 186
COL_GAP = 4
HALF_W = (GRID_W - COL_GAP) / 2
ROW_GAP = 4                    # leaves room for the code tab on each box's top edge
FOOTER_H = 14
GRID_BOTTOM = 297 - FOOTER_H - 3
FIRST_GRID_TOP = 35            # below the banner and the directions strip
CONT_GRID_TOP = 22             # below the slim "(continued)" banner

# Inside a box.
PAD_TOP = 2.5
PAD_BOTTOM = 2
PAD_RIGHT = 3
TEXT_INSET = 10.5              # clears the number circle
CIRCLE_R = 3.2

SCALES = (1.0, 0.95, 0.9, 0.85, 0.8)
ONE_PAGE_MIN_WORK = 15         # mm of blank work space a box keeps at minimum
SPLIT_MIN_WORK = 20
TIGHT_MIN_WORK = 12            # when it saves a page
FLOOR_MIN_WORK = 5             # only for a problem too tall for a page
ONE_PAGE_FIG_CAP = 35          # mm; figures stay smaller when a week shares one page
SPLIT_FIG_CAP = 45
MAX_ROW_H = 125                # a lone row does not stretch down the whole page
TOO_WIDE_MM = 1.5

LEVEL_LABELS = {"below": "Below", "approaching": "Approaching",
                "at": "At", "above": "Above"}


@dataclass
class SpiralItem:
    question: object           # GeneratedQuestion
    standard: str
    level: str
    uid: str
    position: int              # printed problem number within the week


def spiral_quote(grade, week):
    """A productive-struggle quote that is stable per (grade, week).

    Python's hash() is salted per process, so the other layouts' quotes can
    change between a preview and its download. A step coprime with the list
    length walks every quote before any repeats (30 weeks with 30 quotes).
    """
    n = len(_STRUGGLE_QUOTES)
    step = next(s for s in range(7, 7 + n) if math.gcd(s, n) == 1)
    start = zlib.crc32(f"spiral|{grade}".encode())
    return _STRUGGLE_QUOTES[(start + step * int(week)) % n]


class SpiralPDF(MathPDF):
    def __init__(self):
        super().__init__(title="Spiral Review")
        self.set_auto_page_break(auto=False)
        self.set_margins(MARGIN_X, 10, MARGIN_X)

    def header(self):
        pass  # drawn per page by the layout

    def footer(self):
        pass


class _MeasurePDF(SpiralPDF):
    """Scratch PDF used to measure problems. Records the right-most ink."""

    def __init__(self):
        super().__init__()
        self.max_right = 0.0

    def cell(self, w=None, h=None, *args, **kwargs):
        if w:
            self.max_right = max(self.max_right, self.get_x() + w)
        return super().cell(w, h, *args, **kwargs)


class Measurer:
    """Measures how tall a problem renders at a given width, scale and figure cap."""

    X0 = 20.0
    Y0 = 10.0

    def __init__(self):
        self.pdf = _MeasurePDF()
        self.pdf.add_page()
        self._cache = {}

    def measure(self, item, width, scale, cap):
        """Returns (content height, mm drawn past the right edge)."""
        has_figure = bool(getattr(item.question, "render_data", None))
        key = (item.uid, round(width, 2), scale, cap if has_figure else None)
        hit = self._cache.get(key)
        if hit is None:
            pdf = self.pdf
            pdf.max_right = 0.0
            end = _write_column_question(
                pdf, item.question, None, self.X0, width, self.Y0,
                font_scale=scale, show_number=False, fig_max_h=cap,
                inline_parts=True)
            hit = (end - self.Y0, max(0.0, pdf.max_right - (self.X0 + width)))
            self._cache[key] = hit
        return hit

    def text_height(self, text, width, size, style=""):
        pdf = self.pdf
        pdf.set_font(pdf.ff, style, size)
        pdf.set_xy(self.X0, self.Y0)
        pdf.multi_cell(width, size * 0.45, text, align="L", new_x="LMARGIN", new_y="NEXT")
        return pdf.get_y() - self.Y0


def _inner_w(n_in_row):
    box_w = HALF_W if n_in_row == 2 else GRID_W
    return box_w - TEXT_INSET - PAD_RIGHT


def _row_need(measurer, row, scale, cap, min_work):
    width = _inner_w(len(row))
    content = max(measurer.measure(it, width, scale, cap)[0] for it in row)
    return PAD_TOP + content + min_work + PAD_BOTTOM


def _used(needs):
    return sum(needs) + ROW_GAP * (len(needs) - 1)


def _partition(needs, first_h, cont_h):
    """Split rows (in order) over the fewest pages, as evenly as possible.

    Returns a list of lists of row indexes, or None when some row cannot fit a
    page at all. There are at most 4 rows, so trying every split is cheap.
    """
    n = len(needs)
    best = None
    for mask in range(1 << max(0, n - 1)):
        groups, cur = [], [0]
        for i in range(1, n):
            if mask >> (i - 1) & 1:
                groups.append(cur)
                cur = [i]
            else:
                cur.append(i)
        groups.append(cur)
        fills = []
        for gi, g in enumerate(groups):
            room = first_h if gi == 0 else cont_h
            used = _used([needs[i] for i in g])
            if used > room:
                break
            fills.append(used / room)
        else:
            key = (len(groups), max(fills))
            if best is None or key < best[0]:
                best = (key, groups)
    return best[1] if best else None


def _row_heights(needs, room):
    """Spread a page's spare height over its rows: equal heights where they fit,
    a row that needs more keeps what it needs, and nothing grows past MAX_ROW_H."""
    n = len(needs)
    space = room - ROW_GAP * (n - 1)
    heights = list(needs)
    fixed = set()
    while True:
        free = [i for i in range(n) if i not in fixed]
        if not free:
            break
        share = min((space - sum(heights[i] for i in fixed)) / len(free), MAX_ROW_H)
        grew = False
        for i in free:
            if needs[i] > share:
                fixed.add(i)
                heights[i] = needs[i]
                grew = True
        if not grew:
            for i in free:
                heights[i] = max(needs[i], share)
            break
    return heights


def fit_week(items, measurer):
    """Decide how one week's problems sit on pages. Nothing is drawn.

    Returns {"pages": [{"grid_top", "rows": [{"items", "height"}]}],
             "scale", "fig_cap", "warnings"}.
    """
    rows = [items[i:i + 2] for i in range(0, len(items), 2)]
    first_h = GRID_BOTTOM - FIRST_GRID_TOP
    cont_h = GRID_BOTTOM - CONT_GRID_TOP
    warnings = []

    def needs_at(scale, cap, min_work):
        return [_row_need(measurer, r, scale, cap, min_work) for r in rows]

    chosen = None

    # One page when it fits. Checking full size and then the smallest text
    # first skips measuring the in-between sizes for weeks that cannot fit.
    cap = ONE_PAGE_FIG_CAP
    if _used(needs_at(1.0, cap, ONE_PAGE_MIN_WORK)) <= first_h:
        chosen = (1.0, cap, [list(range(len(rows)))], ONE_PAGE_MIN_WORK)
    elif _used(needs_at(SCALES[-1], cap, ONE_PAGE_MIN_WORK)) <= first_h:
        for s in SCALES[1:]:
            if _used(needs_at(s, cap, ONE_PAGE_MIN_WORK)) <= first_h:
                chosen = (s, cap, [list(range(len(rows)))], ONE_PAGE_MIN_WORK)
                break

    # Otherwise break between rows. Paper first: the fewest pages, then the
    # largest text and the most work space that still get there. Tall
    # multi-part problems carry their own answer lines, so a tighter floor on
    # blank space is fine when it saves a sheet.
    if chosen is None:
        cap = SPLIT_FIG_CAP

        def attempt(s, min_work):
            groups = _partition(needs_at(s, cap, min_work), first_h, cont_h)
            return None if groups is None else (s, cap, groups, min_work)

        roomy = attempt(1.0, SPLIT_MIN_WORK)
        tight = attempt(SCALES[-1], TIGHT_MIN_WORK)
        if roomy and (tight is None or len(roomy[2]) <= len(tight[2])):
            chosen = roomy
        elif tight:
            fewest = len(tight[2])
            for min_work in (SPLIT_MIN_WORK, TIGHT_MIN_WORK):
                for s in SCALES:
                    got = attempt(s, min_work)
                    if got and len(got[2]) <= fewest:
                        chosen = got
                        break
                if chosen:
                    break
        else:
            for s in SCALES:
                chosen = attempt(s, FLOOR_MIN_WORK)
                if chosen:
                    break

    # A row taller than a whole page even at the smallest text: give each row
    # its own page and flag the problem so the teacher can swap it.
    if chosen is None:
        s = SCALES[-1]
        chosen = (s, cap, [[i] for i in range(len(rows))], FLOOR_MIN_WORK)
        for ri, row in enumerate(rows):
            room = first_h if ri == 0 else cont_h
            if _row_need(measurer, row, s, cap, FLOOR_MIN_WORK) > room:
                tallest = max(row, key=lambda it: measurer.measure(
                    it, _inner_w(len(row)), s, cap)[0])
                warnings.append({"code": "too_tall", "position": tallest.position,
                                 "standard": tallest.standard, "uid": tallest.uid})

    scale, cap, groups, min_work = chosen
    needs = needs_at(scale, cap, min_work)
    pages = []
    for gi, g in enumerate(groups):
        room = first_h if gi == 0 else cont_h
        heights = _row_heights([needs[i] for i in g], room)
        pages.append({
            "grid_top": FIRST_GRID_TOP if gi == 0 else CONT_GRID_TOP,
            "rows": [{"items": rows[i], "height": min(h, room)}
                     for i, h in zip(g, heights)],
        })

    for r in rows:
        for it in r:
            _, over = measurer.measure(it, _inner_w(len(r)), scale, cap)
            if over > TOO_WIDE_MM:
                warnings.append({"code": "too_wide", "position": it.position,
                                 "standard": it.standard, "uid": it.uid})

    return {"pages": pages, "scale": scale, "fig_cap": cap, "warnings": warnings}


def fit_summary(plan):
    """The JSON-safe part of a week's plan, for the review screen."""
    return {
        "pages": len(plan["pages"]),
        "problems_per_page": [sum(len(r["items"]) for r in p["rows"])
                              for p in plan["pages"]],
        "scale": plan["scale"],
        "warnings": plan["warnings"],
    }


# ── Drawing ──────────────────────────────────────────────────────────────

def _reset(pdf):
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_line_width(0.3)


def _draw_info_strip(pdf, y):
    """Directions on the left, the confidence check on the right."""
    ff = pdf.ff
    pdf.set_text_color(*SB_DARK)
    pdf.set_font(ff, "I", 8.5)
    pdf.set_xy(MARGIN_X + 1, y)
    pdf.cell(80, 5, "Show your work in each box.")

    lead = "How sure do you feel?"
    options = ["High", "Medium", "Need help"]
    r = 1.7
    pdf.set_font(ff, "B", 8.5)
    lead_w = pdf.get_string_width(lead)
    pdf.set_font(ff, "", 8.5)
    opt_ws = [pdf.get_string_width(o) for o in options]
    total = lead_w + 3 + sum(2 * r + 1.5 + w + 4 for w in opt_ws) - 4
    x = MARGIN_X + GRID_W - total - 1

    pdf.set_font(ff, "B", 8.5)
    pdf.set_xy(x, y)
    pdf.cell(lead_w, 5, lead)
    x += lead_w + 3
    pdf.set_draw_color(*SB_BROWN)
    pdf.set_line_width(0.35)
    pdf.set_font(ff, "", 8.5)
    for label, w in zip(options, opt_ws):
        pdf.ellipse(x, y + 2.5 - r, 2 * r, 2 * r, style="D")
        x += 2 * r + 1.5
        pdf.set_xy(x, y)
        pdf.cell(w, 5, label)
        x += w + 4
    _reset(pdf)


def _draw_footer(pdf, quote, right_text):
    bar_y = pdf.h - FOOTER_H
    pdf.set_fill_color(*SB_YELLOW)
    pdf.rect(0, bar_y, pdf.w, FOOTER_H, style="F")
    pdf.set_draw_color(*SB_BROWN)
    pdf.set_line_width(0.4)
    pdf.line(0, bar_y, pdf.w, bar_y)

    pdf.set_text_color(*SB_BROWN)
    pdf.set_font(pdf.ff, "I", 7.5)
    pdf.set_xy(MARGIN_X, bar_y + 3)
    pdf.cell(GRID_W - 72, 5, f'"{quote}"')
    pdf.set_font(pdf.ff, "", 7.5)
    rw = pdf.get_string_width(right_text) + 2
    pdf.set_xy(MARGIN_X + GRID_W - rw, bar_y + 3)
    pdf.cell(rw, 5, right_text)
    _reset(pdf)


def _draw_box(pdf, x, y, w, h, item, scale, cap):
    # Box outline
    pdf.set_draw_color(*SB_YELLOW)
    pdf.set_line_width(0.6)
    pdf._draw_rounded_rect(x, y, w, h, RenderStyle.D, True, 2.5)

    # Number circle, level with the first line of text
    cx = x + 2 + CIRCLE_R
    cy = y + PAD_TOP + 2.6
    pdf.set_fill_color(*SB_YELLOW)
    pdf.set_line_width(0.3)
    pdf.ellipse(cx - CIRCLE_R, cy - CIRCLE_R, 2 * CIRCLE_R, 2 * CIRCLE_R, style="DF")
    pdf.set_text_color(*SB_DARK)
    pdf.set_font(pdf.ff, "B", 9)
    pdf.set_xy(cx - 4, cy - 2.5)
    pdf.cell(8, 5, str(item.position), align="C")

    # Standard code on a tab that sits on the top edge
    pdf.set_font(pdf.ff, "B", 7)
    tab_w = pdf.get_string_width(item.standard) + 5
    tab_h = 4.6
    tx = x + w - tab_w - 4
    ty = y - tab_h / 2
    pdf.set_fill_color(*SB_YELLOW_PALE)
    pdf.set_draw_color(*SB_YELLOW)
    pdf.set_line_width(0.4)
    pdf._draw_rounded_rect(tx, ty, tab_w, tab_h, RenderStyle.DF, True, tab_h / 2)
    pdf.set_text_color(*SB_BROWN)
    pdf.set_xy(tx, ty)
    pdf.cell(tab_w, tab_h, item.standard, align="C")

    _reset(pdf)
    _write_column_question(
        pdf, item.question, None, x + TEXT_INSET, w - TEXT_INSET - PAD_RIGHT,
        y + PAD_TOP, font_scale=scale, show_number=False, fig_max_h=cap,
        inline_parts=True)
    _reset(pdf)


def _draw_week(pdf, grade, week, plan):
    quote = spiral_quote(grade, week)
    n_pages = len(plan["pages"])
    for pi, page in enumerate(plan["pages"]):
        pdf.add_page()
        if pi == 0:
            _draw_sb_header(pdf, MARGIN_X, 6, GRID_W, 18, title="Spiral Review",
                            standard_code=f"Grade {grade}  |  Week {week}",
                            r=3, include_name=True, font_title=12, font_name=9)
            _draw_info_strip(pdf, 26.5)
        else:
            _draw_sb_header(pdf, MARGIN_X, 5, GRID_W, 13, title="Spiral Review",
                            standard_code=f"Grade {grade}  |  Week {week} (continued)",
                            r=3, include_name=True, font_title=10, font_name=8)
        y = page["grid_top"]
        for row in page["rows"]:
            h = row["height"]
            if len(row["items"]) == 2:
                for ci, it in enumerate(row["items"]):
                    _draw_box(pdf, MARGIN_X + ci * (HALF_W + COL_GAP), y, HALF_W, h,
                              it, plan["scale"], plan["fig_cap"])
            else:
                _draw_box(pdf, MARGIN_X, y, GRID_W, h, row["items"][0],
                          plan["scale"], plan["fig_cap"])
            y += h + ROW_GAP
        right = f"Plug N Play  |  Spiral Review  |  Week {week}"
        if n_pages > 1:
            right += f"  |  Page {pi + 1} of {n_pages}"
        _draw_footer(pdf, quote, right)


# ── Answer key ───────────────────────────────────────────────────────────

_CHOICE_REF_RE = re.compile(r'(^|[:;]\s*|\n)([a-f])(?=[\.\)](?:\s|$)|$)')


def key_answer(q):
    """The key's answer, with choice letters in capitals to match the sheet."""
    text = MathPDF._clean_text((q.answer_text or "").strip())
    if not q.choices:
        return text
    if q.item_type == ItemType.MS and re.fullmatch(r'[a-f](?:\s*,\s*[a-f])*', text):
        return ", ".join(k.strip().upper() for k in text.split(","))
    if re.fullmatch(r'[a-f]', text):
        choice = next((c for c in q.choices if c.key == text), None)
        detail = MathPDF._clean_text(choice.text).strip() if choice else ""
        if detail and len(detail) <= 50:
            return f"{text.upper()}  ({detail})"
        return text.upper()
    return _CHOICE_REF_RE.sub(lambda m: m.group(1) + m.group(2).upper(), text)


def _key_banner(pdf, grade, weeks_label):
    _draw_sb_header(pdf, MARGIN_X, 6, GRID_W, 14, title="Spiral Review Answer Key",
                    standard_code=f"Grade {grade}  |  {weeks_label}",
                    r=3, include_name=False, font_title=12)


def _draw_answer_key(pdf, grade, weeks, measurer):
    """Two newspaper columns of week blocks: '#.  CODE  answer'."""
    numbers = [w["week_number"] for w in weeks]
    if len(numbers) == 1:
        weeks_label = f"Week {numbers[0]}"
    else:
        weeks_label = f"Weeks {min(numbers)}-{max(numbers)}"
    quote = spiral_quote(grade, min(numbers) - 1)
    footer = "Plug N Play  |  Spiral Review  |  Answer Key"

    col_gap = 6
    col_w = (GRID_W - col_gap) / 2
    col_xs = [MARGIN_X, MARGIN_X + col_w + col_gap]
    top, bottom = 25, GRID_BOTTOM
    num_w, code_w = 6, 25
    ans_x_off = num_w + code_w
    ans_w = col_w - ans_x_off - 1
    fs, lh = 8.5, 4.2
    bar_h = 6

    state = {"col": 0, "y": top}

    def new_page():
        pdf.add_page()
        _key_banner(pdf, grade, weeks_label)
        _draw_footer(pdf, quote, footer)
        state["col"], state["y"] = 0, top

    def room_for(h):
        if state["y"] + h <= bottom:
            return
        if state["col"] == 0:
            state["col"], state["y"] = 1, top
        else:
            new_page()

    def week_bar(label):
        x = col_xs[state["col"]]
        pdf.set_fill_color(*SB_YELLOW_LIGHT)
        pdf.set_draw_color(*SB_YELLOW_LIGHT)
        pdf._draw_rounded_rect(x, state["y"], col_w, bar_h, RenderStyle.DF, True, 1.5)
        pdf.set_text_color(*SB_BROWN)
        pdf.set_font(pdf.ff, "B", 9)
        pdf.set_xy(x + 2, state["y"])
        pdf.cell(col_w - 4, bar_h, label)
        _reset(pdf)
        state["y"] += bar_h + 1.5

    new_page()
    for wk in weeks:
        entries = []
        for it in wk["items"]:
            ans = key_answer(it.question)
            code = it.standard
            if it.level != "at":
                code += f" ({LEVEL_LABELS.get(it.level, it.level)})"
            code_h = measurer.text_height(code, code_w - 1, 7, "B")
            ans_h = measurer.text_height(ans, ans_w, fs)
            entries.append((it.position, code, ans, max(code_h, ans_h, lh) + 1.5))

        label = f"Week {wk['week_number']}"
        room_for(bar_h + 1.5 + (entries[0][3] if entries else 0))
        week_bar(label)
        for pos, code, ans, h in entries:
            if state["y"] + h > bottom:
                room_for(bar_h + 1.5 + h)
                week_bar(f"{label} (continued)")
            x = col_xs[state["col"]]
            y = state["y"]
            pdf.set_text_color(*SB_DARK)
            pdf.set_font(pdf.ff, "B", fs)
            pdf.set_xy(x, y)
            pdf.cell(num_w, lh, f"{pos}.")
            pdf.set_text_color(110, 110, 110)
            pdf.set_font(pdf.ff, "B", 7)
            pdf.set_xy(x + num_w, y + 0.3)
            pdf.multi_cell(code_w - 1, 7 * 0.45, code, align="L", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
            pdf.set_font(pdf.ff, "", fs)
            pdf.set_xy(x + ans_x_off, y)
            pdf.multi_cell(ans_w, fs * 0.45, ans, align="L", new_x="LMARGIN", new_y="NEXT")
            state["y"] = y + h
        state["y"] += 3


def render_spiral_pdf(weeks, grade, output_path, include_answer_key=True,
                      measurer=None):
    """Draw every week, then the answer key.

    weeks: [{"week_number": int, "items": [SpiralItem, ...]}] in print order.
    Returns a JSON-safe report: each week's fit, plus any warnings.
    """
    measurer = measurer or Measurer()
    pdf = SpiralPDF()
    report = {"weeks": [], "warnings": []}
    for wk in weeks:
        if not wk["items"]:
            continue
        plan = fit_week(wk["items"], measurer)
        _draw_week(pdf, grade, wk["week_number"], plan)
        summary = fit_summary(plan)
        report["weeks"].append({"week_number": wk["week_number"], **summary})
        for w in plan["warnings"]:
            report["warnings"].append({**w, "week_number": wk["week_number"]})
    if include_answer_key and any(wk["items"] for wk in weeks):
        _draw_answer_key(pdf, grade, [wk for wk in weeks if wk["items"]], measurer)
    pdf.output(output_path)
    return report
