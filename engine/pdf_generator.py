"""
PDF worksheet generator for ILEARN math practice.
Produces clean, professional worksheets mimicking standardized test format.

Uses fpdf2 for PDF creation. Supports:
- Inline stacked fractions (numerator over bar over denominator)
- Superscript exponents (x^2 → x²)
- Number line diagrams for inequality questions
- Proper Unicode math symbols (≥, ≤) via Arial TTF
"""

import os
import re
from io import BytesIO
from fpdf import FPDF

from engine.models import GeneratedQuestion, ItemType, Difficulty, ProficiencyLevel


# ============================================================
# CONSTANTS
# ============================================================

FONT_SIZE_TITLE = 14
FONT_SIZE_HEADER = 11
FONT_SIZE_BODY = 11
FONT_SIZE_SMALL = 9
FONT_SIZE_QUESTION_NUM = 11

LINE_HEIGHT = 6  # mm
FRAC_LINE_HEIGHT = 9  # mm - taller line for lines containing fractions
PAGE_MARGIN = 15  # mm
ANSWER_LINE_WIDTH = 60  # mm

PROFICIENCY_LABELS = {
    ProficiencyLevel.BELOW: "Below Proficiency",
    ProficiencyLevel.APPROACHING: "Approaching Proficiency",
    ProficiencyLevel.AT: "At Proficiency",
    ProficiencyLevel.ABOVE: "Above Proficiency",
}

DIFFICULTY_LABELS = {
    Difficulty.EASY: "Easy",
    Difficulty.MEDIUM: "Medium",
    Difficulty.DIFFICULT: "Difficult",
}

# ============================================================
# PLUG N PLAY BRANDING COLORS (RGB tuples)
# ============================================================

SB_YELLOW = (255, 200, 0)           # Primary yellow
SB_YELLOW_LIGHT = (255, 235, 150)  # Light wash for backgrounds
SB_YELLOW_PALE = (255, 245, 200)   # Very pale for subtle fills
SB_BROWN = (80, 60, 0)             # Dark warm text on yellow
SB_DARK = (40, 40, 40)             # Near-black body text

SB_HEADER_HEIGHT = 28              # mm - header banner height
SB_FOOTER_HEIGHT = 14              # mm - footer bar height
SB_Q_CIRCLE_R = 4                  # mm - question number circle radius

# Matches mixed numbers "W N/D" (groups 1,2,3) or fractions "N/D" (groups 4,5).
# N and D can be digits, decimals (14.60), or single-letter variables (x, s).
FRAC_RE = re.compile(r'(\d+)\s+(\d+)/(\d+)|(\d+(?:\.\d+)?|[a-z])/(\d+(?:\.\d+)?|[a-z])')

# Matches exponent patterns like ^2, ^3
EXPONENT_RE = re.compile(r'\^(-?\d+|[a-z])')

# Arial font paths -- bundled fonts first, then Windows system fonts
_FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
_FONT_CANDIDATES = [
    (_FONT_DIR, "arial.ttf", "arialbd.ttf", "ariali.ttf"),
    ("C:/Windows/Fonts", "arial.ttf", "arialbd.ttf", "ariali.ttf"),
]


def _fmt_tick(v):
    """Format a number-line tick label.

    Ticks are often passed as floats (e.g. -1.0, 0.0, 1.0). When a tick lands on
    a whole number, show it as an integer ("-1", "0", "1") rather than "-1.0" so
    integer-stepped number lines read correctly; keep genuine fractional ticks
    (e.g. 0.5) as clean decimals.
    """
    try:
        fv = float(v)
    except (TypeError, ValueError):
        return str(v)
    if fv == int(fv):
        return str(int(fv))
    return f"{fv:.2f}".rstrip("0").rstrip(".")


def _clip_line_to_rect(lx1, ly1, lx2, ly2, rx_min, rx_max, ry_min, ry_max):
    """Clip a line segment to a rectangle using Liang-Barsky algorithm.

    Preserves the line's slope (no independent x/y clamping).
    Returns (cx1, cy1, cx2, cy2) or None if the segment is fully outside.
    """
    dx = lx2 - lx1
    dy = ly2 - ly1
    t0 = 0.0
    t1 = 1.0

    for p, q in [
        (-dx, lx1 - rx_min),   # left edge
        (dx,  rx_max - lx1),   # right edge
        (-dy, ly1 - ry_min),   # bottom edge
        (dy,  ry_max - ly1),   # top edge
    ]:
        if abs(p) < 1e-12:
            if q < -1e-12:
                return None
        else:
            r = q / p
            if p < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
        if t0 > t1 + 1e-12:
            return None

    return (
        lx1 + t0 * dx,
        ly1 + t0 * dy,
        lx1 + t1 * dx,
        ly1 + t1 * dy,
    )


def _find_arial_fonts():
    """Return (regular, bold, italic) paths or None."""
    for directory, reg, bold, italic in _FONT_CANDIDATES:
        r = os.path.join(directory, reg)
        b = os.path.join(directory, bold)
        i = os.path.join(directory, italic)
        if os.path.exists(r) and os.path.exists(b) and os.path.exists(i):
            return r, b, i
    return None


def _register_arial(pdf):
    """Register Arial TTF for Unicode support. Falls back to Helvetica."""
    paths = _find_arial_fonts()
    if paths:
        pdf.add_font("Arial", "", paths[0], uni=True)
        pdf.add_font("Arial", "B", paths[1], uni=True)
        pdf.add_font("Arial", "I", paths[2], uni=True)
        return "Arial"
    return "Helvetica"


def _register_emoji_fallback(pdf):
    """Register NotoEmoji as a fallback font for the primary face. fpdf2's
    `set_fallback_fonts` walks the fallback list whenever the active font
    doesn't have a glyph — used here so emoji literals (apples, cookies,
    dogs) in any cell automatically render via NotoEmoji while regular
    text stays in Arial."""
    here = os.path.dirname(os.path.abspath(__file__))
    emoji_path = os.path.join(here, "fonts", "NotoEmoji.ttf")
    if not os.path.exists(emoji_path):
        return  # silently skip; emoji-bearing cells will just lose those glyphs
    try:
        # Register the same TTF under all three style slots — emoji glyphs
        # aren't really bold/italic, but fpdf2's fallback chain matches by
        # *style*, so a bold cell needs a bold-registered fallback.
        pdf.add_font("NotoEmoji", "", emoji_path, uni=True)
        pdf.add_font("NotoEmoji", "B", emoji_path, uni=True)
        pdf.add_font("NotoEmoji", "I", emoji_path, uni=True)
        # fpdf2 >= 2.7 supports set_fallback_fonts; older versions silently
        # skip this without raising.
        if hasattr(pdf, "set_fallback_fonts"):
            pdf.set_fallback_fonts(["NotoEmoji"])
    except Exception:
        pass


class MathPDF(FPDF):
    """Custom PDF class with math-friendly formatting."""

    def __init__(self, title: str = "ILEARN Practice", standard: str = "",
                 category: str = "", subdomain: str = "",
                 calculator: str = "Not Allowed", orientation: str = "P",
                 format: str = "A4"):
        super().__init__(orientation=orientation, format=format)
        self.worksheet_title = title
        self.standard = standard
        self.category = category
        self.subdomain = subdomain
        self.calculator = calculator
        self._setup_fonts()

    def _setup_fonts(self):
        """Register Arial for Unicode math symbols (≥, ≤) and NotoEmoji
        as the auto-fallback for emoji glyphs."""
        self.set_auto_page_break(auto=True, margin=20)
        self.ff = _register_arial(self)  # font family: "Arial" or "Helvetica"
        _register_emoji_fallback(self)

    def header(self):
        """Page header with standard info."""
        self.set_font(self.ff, "B", FONT_SIZE_TITLE)
        self.cell(0, 8, self.worksheet_title, new_x="LMARGIN", new_y="NEXT", align="L")

        self.set_font(self.ff, "", FONT_SIZE_SMALL)
        if self.standard:
            self.cell(0, 5, f"Standard: {self.standard}", new_x="LMARGIN", new_y="NEXT")
        if self.category and self.subdomain:
            self.cell(0, 5, f"{self.category}: {self.subdomain}", new_x="LMARGIN", new_y="NEXT")

        self.cell(0, 5, f"Calculator: {self.calculator}", new_x="LMARGIN", new_y="NEXT")

        self.line(PAGE_MARGIN, self.get_y() + 2,
                  self.w - PAGE_MARGIN, self.get_y() + 2)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.ff, "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    # ============================================================
    # MATH DETECTION
    # ============================================================

    # Detects expression-like text: a single variable letter next to a digit,
    # e.g. "2x", "5n", "x +", indicating a math expression.
    _EXPR_RE = re.compile(r'\d[a-z]|[a-z]\d|[a-z]\^|[a-z]\(|\)[a-z]')

    @staticmethod
    def _has_math(text: str) -> bool:
        """Check if text contains fractions, exponents, or expression variables."""
        return (bool(FRAC_RE.search(text))
                or '^' in text
                or bool(MathPDF._EXPR_RE.search(text)))

    @staticmethod
    def _parse_fractions(text: str) -> list:
        """Parse text into segments: ('text', str), ('fraction', n, d), ('mixed', w, n, d)."""
        # Tighten stray spaces just inside parentheses/brackets so math like
        # "( -3/2 )" lays out as "(-3/2)" instead of with gaps. Shared by the
        # measurer and the writer, so wrapping stays in sync.
        text = re.sub(r"([(\[])[ \t]+", r"\1", text)
        text = re.sub(r"[ \t]+([)\]])", r"\1", text)
        # Tighten a fraction coefficient onto its single-letter variable
        # ("33/10 y" -> "33/10y") so it reads as a coefficient, not a fraction
        # with a stray gap. Only a lone variable letter (word boundary) is
        # affected, so words like "3/4 of" are left alone.
        text = re.sub(r"(\d+[ \t]*/[ \t]*\d+)[ \t]+([a-z])(?![a-zA-Z])", r"\1\2", text)
        segments = []
        last_end = 0
        for m in FRAC_RE.finditer(text):
            if m.start() > last_end:
                segments.append(('text', text[last_end:m.start()]))
            if m.group(1) is not None:
                segments.append(('mixed', m.group(1), m.group(2), m.group(3)))
            else:
                segments.append(('fraction', m.group(4), m.group(5)))
            last_end = m.end()
        if last_end < len(text):
            segments.append(('text', text[last_end:]))
        return segments

    # ============================================================
    # FRACTION RENDERING
    # ============================================================

    def _draw_stacked_fraction(self, x, y_center, numerator, denominator,
                                font_size=None):
        """Draw a stacked fraction. Returns width consumed."""
        frac_fs = (font_size or FONT_SIZE_BODY) * 0.78
        self.set_font(self.ff, "", frac_fs)

        num_str = str(numerator)
        den_str = str(denominator)
        num_w = self.get_string_width(num_str)
        den_w = self.get_string_width(den_str)

        content_w = max(num_w, den_w)
        side_pad = 0.75
        frac_w = content_w + 2 * side_pad

        cell_h = frac_fs * 0.4
        gap = 0.3

        # Bar
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.3)
        self.line(x + side_pad, y_center, x + frac_w - side_pad, y_center)

        # Numerator centered above bar
        self.set_xy(x, y_center - gap - cell_h)
        self.cell(frac_w, cell_h, num_str, align="C")

        # Denominator centered below bar
        self.set_xy(x, y_center + gap + 0.2)
        self.cell(frac_w, cell_h, den_str, align="C")

        return frac_w

    # ============================================================
    # EXPONENT RENDERING
    # ============================================================

    def _write_text_with_exponents(self, text, x, y, font_style, fs, lh):
        """Write a text segment, rendering ^N as superscripts. Returns new x."""
        parts = EXPONENT_RE.split(text)
        # split gives: [before1, exp1, before2, exp2, ...]
        for i, part in enumerate(parts):
            if not part:
                continue
            if i % 2 == 0:
                # Normal text
                self.set_font(self.ff, font_style, fs)
                w = self.get_string_width(part)
                self.set_xy(x, y)
                self.cell(w, lh, part)
                x += w
            else:
                # Superscript exponent
                exp_fs = fs * 0.65
                self.set_font(self.ff, font_style, exp_fs)
                w = self.get_string_width(part)
                self.set_xy(x, y - 1.8)  # raised position
                self.cell(w, lh, part)
                self.set_font(self.ff, font_style, fs)
                x += w
        return x

    # ============================================================
    # MATH LINE MEASUREMENT (dry-run width, mirrors the writers above)
    # ============================================================

    def _measure_stacked_fraction(self, numerator, denominator, font_size=None):
        """Width `_draw_stacked_fraction` would consume — no drawing."""
        frac_fs = (font_size or FONT_SIZE_BODY) * 0.78
        self.set_font(self.ff, "", frac_fs)
        num_w = self.get_string_width(str(numerator))
        den_w = self.get_string_width(str(denominator))
        return max(num_w, den_w) + 2 * 0.75  # side_pad on each edge

    def _measure_text_with_exponents(self, text, fs, font_style=""):
        """Width `_write_text_with_exponents` would consume — no drawing."""
        parts = EXPONENT_RE.split(text)
        x = 0.0
        for i, part in enumerate(parts):
            if not part:
                continue
            if i % 2 == 0:
                self.set_font(self.ff, font_style, fs)
            else:
                self.set_font(self.ff, font_style, fs * 0.65)
            x += self.get_string_width(part)
        self.set_font(self.ff, font_style, fs)
        return x

    def _measure_math_line(self, text, fs, font_style=""):
        """Total width `_write_line_with_math` would consume for `text`.

        Mirrors the segment walk (including the negative-sign preprocessing
        and inter-segment gaps) so wrapping decisions match what is drawn.
        """
        segments = self._parse_fractions(text)
        processed = []
        for i, seg in enumerate(segments):
            if (seg[0] == 'text'
                    and i + 1 < len(segments)
                    and segments[i + 1][0] in ('fraction', 'mixed')):
                stripped = seg[1].rstrip()
                if stripped.endswith('-'):
                    remainder = stripped[:-1]
                    if remainder:
                        processed.append(('text', remainder))
                    processed.append(('neg',))
                    continue
            processed.append(seg)
        segments = processed

        x = 0.0
        prev_seg = None
        for si, seg in enumerate(segments):
            if seg[0] == 'text':
                piece = seg[1]
                if '^' in piece:
                    x += self._measure_text_with_exponents(piece, fs, font_style)
                else:
                    self.set_font(self.ff, font_style, fs)
                    x += self.get_string_width(piece)
            elif seg[0] == 'neg':
                self.set_font(self.ff, "B", fs * 1.2)
                x += 0.5 + self.get_string_width("-") + 1.0
                self.set_font(self.ff, font_style, fs)
            elif seg[0] == 'fraction':
                if prev_seg and prev_seg[0] == 'text':
                    trailing = prev_seg[1].rstrip()
                    if trailing.endswith(('(', '[')):
                        x += 0.8
                    elif trailing:
                        x += 1
                x += self._measure_stacked_fraction(seg[1], seg[2], fs) + 0.6
                if si + 1 < len(segments):
                    nxt = segments[si + 1]
                    if nxt[0] == 'text' and nxt[1].lstrip().startswith((')', ']')):
                        x += 0.4
            elif seg[0] == 'mixed':
                self.set_font(self.ff, font_style, fs)
                x += self.get_string_width(seg[1]) + 1.0
                x += self._measure_stacked_fraction(seg[2], seg[3], fs) + 0.6
                if si + 1 < len(segments):
                    nxt = segments[si + 1]
                    if nxt[0] == 'text' and nxt[1].lstrip().startswith((')', ']')):
                        x += 0.4
            prev_seg = seg
        self.set_font(self.ff, font_style, fs)
        return x

    # ============================================================
    # COMBINED MATH LINE WRITER
    # ============================================================

    def _write_line_with_math(self, text, x_start,
                               font_style="", font_size=None, max_width=None):
        """Write a single line with inline fractions and exponents.

        Text should already be _clean_text'd. Advances y after writing.

        When `max_width` is given and the rendered line would overflow it,
        the line is greedily wrapped on spaces and drawn one sub-line per
        row (each sub-line re-rendered through this same writer so fractions
        / exponents still lay out correctly). Callers that omit `max_width`
        get the original single-unwrapped-line behavior unchanged.
        """
        fs = font_size or FONT_SIZE_BODY

        if max_width and self._measure_math_line(text, fs, font_style) > max_width:
            words = text.split(" ")
            cur = ""
            for wd in words:
                cand = wd if not cur else cur + " " + wd
                if cur and self._measure_math_line(cand, fs, font_style) > max_width:
                    self._write_line_with_math(cur, x_start,
                                               font_style=font_style, font_size=fs)
                    cur = wd
                else:
                    cur = cand
            if cur:
                self._write_line_with_math(cur, x_start,
                                           font_style=font_style, font_size=fs)
            return

        segments = self._parse_fractions(text)

        # Pre-process: extract negative signs before fractions so they
        # render at fraction-bar height instead of text baseline.
        processed = []
        for i, seg in enumerate(segments):
            if (seg[0] == 'text'
                    and i + 1 < len(segments)
                    and segments[i + 1][0] in ('fraction', 'mixed')):
                stripped = seg[1].rstrip()
                if stripped.endswith('-'):
                    remainder = stripped[:-1]
                    if remainder:
                        processed.append(('text', remainder))
                    processed.append(('neg',))
                    continue
            processed.append(seg)
        segments = processed

        has_frac = any(s[0] not in ('text', 'neg') for s in segments)
        has_exp = '^' in text

        if not has_frac and not has_exp:
            self.set_font(self.ff, font_style, fs)
            self.set_x(x_start)
            plain = segments[0][1] if segments else text
            self.cell(0, LINE_HEIGHT, plain, new_x="LMARGIN", new_y="NEXT")
            return

        y = self.get_y()
        x = x_start
        lh = FRAC_LINE_HEIGHT if has_frac else LINE_HEIGHT
        y_center = y + lh * 0.42  # fraction bar position

        prev_seg = None
        for si, seg in enumerate(segments):
            if seg[0] == 'text':
                piece = seg[1]
                if '^' in piece:
                    text_y = y + (lh - LINE_HEIGHT) / 2 if has_frac else y
                    x = self._write_text_with_exponents(
                        piece, x, text_y, font_style, fs, LINE_HEIGHT)
                else:
                    self.set_font(self.ff, font_style, fs)
                    w = self.get_string_width(piece)
                    self.set_xy(x, y + (lh - LINE_HEIGHT) / 2)
                    self.cell(w, LINE_HEIGHT, piece)
                    x += w
            elif seg[0] == 'neg':
                # Draw negative sign at fraction-bar height (enlarged)
                neg_fs = fs * 1.2
                self.set_font(self.ff, "B", neg_fs)
                neg_w = self.get_string_width("-")
                x += 0.5  # small gap before the minus (keep it near an open paren)
                neg_cell_h = 4
                self.set_xy(x, y_center - neg_cell_h / 2)
                self.cell(neg_w, neg_cell_h, "-")
                x += neg_w + 1.0  # more breathing room between the sign and the fraction
                self.set_font(self.ff, font_style, fs)
            elif seg[0] == 'fraction':
                # Gap before fraction so it isn't cramped against text
                if prev_seg and prev_seg[0] == 'text':
                    trailing = prev_seg[1].rstrip()
                    if trailing.endswith(('(', '[')):
                        x += 0.8  # snug gap after an opening paren
                    elif trailing:
                        x += 1    # general gap from preceding text
                w = self._draw_stacked_fraction(x, y_center, seg[1], seg[2], fs)
                x += w + 0.6
                # Gap before closing paren/bracket
                if si + 1 < len(segments):
                    nxt = segments[si + 1]
                    if nxt[0] == 'text' and nxt[1].lstrip().startswith((')', ']')):
                        x += 0.4
            elif seg[0] == 'mixed':
                # Whole number part
                self.set_font(self.ff, font_style, fs)
                ws = seg[1]
                ww = self.get_string_width(ws)
                self.set_xy(x, y + (lh - LINE_HEIGHT) / 2)
                self.cell(ww, LINE_HEIGHT, ws)
                x += ww + 1.0  # gap between whole number and fraction
                # Fraction part
                w = self._draw_stacked_fraction(x, y_center, seg[2], seg[3], fs)
                x += w + 0.6
                # Gap before a closing paren/bracket (snug, like a fraction)
                if si + 1 < len(segments):
                    nxt = segments[si + 1]
                    if nxt[0] == 'text' and nxt[1].lstrip().startswith((')', ']')):
                        x += 0.4
            prev_seg = seg

        self.set_font(self.ff, font_style, fs)
        self.set_y(y + lh)

    # ============================================================
    # NUMBER LINE RENDERING
    # ============================================================

    def _draw_number_line(self, x, y, value, circle_type, direction,
                          width=65, blank=False):
        """Draw a number line diagram for an inequality.

        If blank=True, draws a generic number line with only a horizontal
        line and tick marks (hashes) -- no numbers, no arrowheads, no dots,
        no directional arrows.  Students fill it in themselves.
        """
        height = 14
        line_y = y + 5
        pad = 5
        arrow_ext = 3  # extend line past ticks for arrow room
        tick_x1 = x + pad + arrow_ext
        tick_x2 = x + width - pad - arrow_ext
        line_x1 = x + pad
        line_x2 = x + width - pad

        float_val = float(value)

        if float_val == int(float_val):
            center = int(float_val)
        else:
            center = round(float_val)

        tick_start = center - 3
        n_ticks = 7
        tick_spacing = (tick_x2 - tick_x1) / (n_ticks - 1)

        # Main horizontal line
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.4)
        self.line(line_x1, line_y, line_x2, line_y)

        # Arrowheads on both ends — larger and separated from ticks
        self.set_line_width(0.5)
        self.line(line_x1, line_y, line_x1 + 2.5, line_y - 1.5)
        self.line(line_x1, line_y, line_x1 + 2.5, line_y + 1.5)
        self.line(line_x2, line_y, line_x2 - 2.5, line_y - 1.5)
        self.line(line_x2, line_y, line_x2 - 2.5, line_y + 1.5)

        # Tick marks
        self.set_line_width(0.25)
        for i in range(n_ticks):
            tx = tick_x1 + i * tick_spacing
            self.line(tx, line_y - 1.5, tx, line_y + 1.5)

        if not blank:
            # Numeric labels below ticks
            self.set_font(self.ff, "", 6.5)
            for i in range(n_ticks):
                tick_val = tick_start + i
                tx = tick_x1 + i * tick_spacing
                label = _fmt_tick(tick_val)
                lw = self.get_string_width(label)
                self.set_xy(tx - lw / 2, line_y + 2)
                self.cell(lw + 0.5, 3, label, align="C")

            # Circle position
            cx = tick_x1 + (float_val - tick_start) * tick_spacing
            r = 1.5

            # Arrow (shaded region)
            self.set_line_width(1.0)
            self.set_draw_color(0, 0, 0)
            if direction == "left":
                self.line(cx, line_y, line_x1, line_y)
                self.set_line_width(0.5)
                self.line(line_x1, line_y, line_x1 + 2.5, line_y - 1.5)
                self.line(line_x1, line_y, line_x1 + 2.5, line_y + 1.5)
            else:
                self.line(cx, line_y, line_x2, line_y)
                self.set_line_width(0.5)
                self.line(line_x2, line_y, line_x2 - 2.5, line_y - 1.5)
                self.line(line_x2, line_y, line_x2 - 2.5, line_y + 1.5)

            # Circle
            self.set_line_width(0.4)
            self.set_draw_color(0, 0, 0)
            if circle_type == "closed":
                self.set_fill_color(0, 0, 0)
                self.ellipse(cx - r, line_y - r, 2 * r, 2 * r, style="DF")
            else:
                self.set_fill_color(255, 255, 255)
                self.ellipse(cx - r, line_y - r, 2 * r, 2 * r, style="DF")

        self.set_line_width(0.3)
        self.set_draw_color(0, 0, 0)
        return height

    # ============================================================
    # NUMBER LINE WITH POINT (e.g. integer placement)
    # ============================================================

    def _draw_number_line_point(self, x, y, ticks, point_value=None, point_label="P",
                                points=None, width=80):
        """Draw a number line with labeled ticks and marked point(s).

        Supports single point (point_value/point_label) or multiple points
        via points=[{"value": v, "label": "L"}, ...].
        """
        height = 18
        line_y = y + 6
        pad = 8
        line_x1 = x + pad
        line_x2 = x + width - pad

        n_ticks = len(ticks)
        if n_ticks < 2:
            return height
        tick_spacing = (line_x2 - line_x1) / (n_ticks - 1)
        tick_min = ticks[0]
        tick_max = ticks[-1]

        def _val_to_x(val):
            if tick_max != tick_min:
                return line_x1 + (val - tick_min) / (tick_max - tick_min) * (line_x2 - line_x1)
            return (line_x1 + line_x2) / 2

        # Main line with arrows
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.4)
        self.line(line_x1 - 4, line_y, line_x2 + 4, line_y)
        # Left arrow
        self.set_line_width(0.35)
        self.line(line_x1 - 4, line_y, line_x1 - 1, line_y - 1.5)
        self.line(line_x1 - 4, line_y, line_x1 - 1, line_y + 1.5)
        # Right arrow
        self.line(line_x2 + 4, line_y, line_x2 + 1, line_y - 1.5)
        self.line(line_x2 + 4, line_y, line_x2 + 1, line_y + 1.5)

        # Ticks and labels
        self.set_font(self.ff, "", 6.5)
        self.set_line_width(0.25)
        for i, tick_val in enumerate(ticks):
            tx = line_x1 + i * tick_spacing
            self.line(tx, line_y - 2, tx, line_y + 2)
            label = _fmt_tick(tick_val)
            lw = self.get_string_width(label)
            self.set_xy(tx - lw / 2, line_y + 3)
            self.cell(lw + 0.5, 3, label, align="C")

        # Build list of points to draw
        pts = []
        if points:
            pts = points
        elif point_value is not None:
            pts = [{"value": point_value, "label": point_label}]

        # Draw all points
        for pt in pts:
            cx = _val_to_x(pt["value"])
            r = 1.0
            self.set_line_width(0.4)
            self.set_fill_color(0, 0, 0)
            self.ellipse(cx - r, line_y - r, 2 * r, 2 * r, style="DF")

            # Point label above
            lbl = pt.get("label", "")
            if lbl:
                self.set_font(self.ff, "B", 7)
                lw = self.get_string_width(lbl)
                self.set_xy(cx - lw / 2, line_y - 6)
                self.cell(lw + 0.5, 3, lbl, align="C")

        self.set_line_width(0.3)
        self.set_draw_color(0, 0, 0)
        return height

    # ============================================================
    # DOUBLE NUMBER LINE (e.g. ratio visualization)
    # ============================================================

    def _draw_double_number_line(self, x, y, top_ticks, bottom_ticks,
                                  top_label="", bottom_label="", width=80):
        """Draw two parallel number lines showing a ratio relationship."""
        height = 32
        pad = 8
        line_x1 = x + pad
        line_x2 = x + width - pad
        top_y = y + 6
        bot_y = y + 22

        n_ticks = max(len(top_ticks), len(bottom_ticks))
        if n_ticks < 2:
            return height
        tick_spacing = (line_x2 - line_x1) / (n_ticks - 1)

        for line_y, ticks, label in [(top_y, top_ticks, top_label),
                                      (bot_y, bottom_ticks, bottom_label)]:
            # Main line with arrows
            self.set_draw_color(0, 0, 0)
            self.set_line_width(0.4)
            self.line(line_x1 - 4, line_y, line_x2 + 4, line_y)
            # Arrows
            self.set_line_width(0.35)
            self.line(line_x1 - 4, line_y, line_x1 - 1, line_y - 1.2)
            self.line(line_x1 - 4, line_y, line_x1 - 1, line_y + 1.2)
            self.line(line_x2 + 4, line_y, line_x2 + 1, line_y - 1.2)
            self.line(line_x2 + 4, line_y, line_x2 + 1, line_y + 1.2)

            # Ticks and labels
            self.set_font(self.ff, "", 6.5)
            self.set_line_width(0.25)
            is_top = (line_y == top_y)
            for i, tick_val in enumerate(ticks):
                tx = line_x1 + i * tick_spacing
                self.line(tx, line_y - 1.5, tx, line_y + 1.5)
                t_label = _fmt_tick(tick_val)
                lw = self.get_string_width(t_label)
                if is_top:
                    self.set_xy(tx - lw / 2, line_y - 5)
                else:
                    self.set_xy(tx - lw / 2, line_y + 2.5)
                self.cell(lw + 0.5, 3, t_label, align="C")

        self.set_line_width(0.3)
        self.set_draw_color(0, 0, 0)
        return height

    # ============================================================
    # RECTANGLE DIAGRAM (e.g. zoo enclosure)
    # ============================================================

    def _draw_rectangle_diagram(self, x, y, side, cut_l, cut_w):
        """Draw a square with two rectangular cutouts, labeled with dimensions.

        Represents: side^2 - 2 * cut_l * cut_w
        """
        # Outer square
        sq_size = 40  # mm
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.5)
        self.rect(x, y, sq_size, sq_size)

        # Draw two shaded rectangular cutouts (top-left and bottom-right)
        cut_w_mm = sq_size * 0.22  # visual width of cutout
        cut_h_mm = sq_size * 0.35  # visual height of cutout

        # Cutout 1: top-left corner
        self.set_fill_color(220, 220, 220)
        self.rect(x, y, cut_w_mm, cut_h_mm, style="DF")

        # Cutout 2: bottom-right corner
        self.rect(x + sq_size - cut_w_mm, y + sq_size - cut_h_mm,
                  cut_w_mm, cut_h_mm, style="DF")

        # Dimension labels
        self.set_font(self.ff, "", 7)
        self.set_text_color(0, 0, 0)

        # Side label (along right side)
        side_label = str(side)
        lw = self.get_string_width(side_label)
        self.set_xy(x + sq_size + 1.5, y + sq_size / 2 - 2)
        self.cell(lw + 1, 4, side_label)

        # Top side label
        self.set_xy(x + sq_size / 2 - lw / 2, y - 4)
        self.cell(lw + 1, 4, side_label)

        # Cutout dimension labels (cut_l x cut_w on cutout 1)
        cl_label = str(cut_l)
        cw_label = str(cut_w)
        # Label cut_l along the top of cutout 1
        self.set_font(self.ff, "", 6)
        self.set_xy(x + cut_w_mm / 2 - self.get_string_width(cw_label) / 2, y + cut_h_mm + 0.5)
        self.cell(self.get_string_width(cw_label) + 1, 3, cw_label)
        # Label cut_w along the side of cutout 1
        self.set_xy(x + cut_w_mm + 0.5, y + cut_h_mm / 2 - 1)
        self.cell(self.get_string_width(cl_label) + 1, 3, cl_label)

        self.set_line_width(0.3)
        self.set_text_color(0, 0, 0)
        return sq_size + 8  # total height used

    # ============================================================
    # DATA TABLE RENDERING
    # ============================================================

    def _draw_table_cell(self, cx, cy, cw, cell_h, text, fs):
        """Draw one data-cell's text centered in its box.

        A mixed number ("2 1/2") or simple fraction ("3/4") is rendered as a
        real stacked fraction (numerator over denominator) instead of a slash;
        anything else (integers, decimals) is drawn as plain centered text.
        """
        text = str(text)
        mixed = re.fullmatch(r'\s*(-?\d+)\s+(\d+)/(\d+)\s*', text)
        simple = re.fullmatch(r'\s*(-?\d+)/(\d+)\s*', text)
        y_center = cy + cell_h / 2
        if mixed:
            whole, num, den = mixed.group(1), mixed.group(2), mixed.group(3)
            self.set_font(self.ff, "", fs)
            whole_w = self.get_string_width(whole + " ")
            frac_w = self._measure_stacked_fraction(num, den, fs)
            start_x = cx + (cw - (whole_w + frac_w)) / 2
            self.set_xy(start_x, cy)
            self.cell(whole_w, cell_h, whole + " ", align="L")
            self._draw_stacked_fraction(start_x + whole_w, y_center, num, den, fs)
            self.set_font(self.ff, "", fs)
        elif simple:
            num, den = simple.group(1), simple.group(2)
            frac_w = self._measure_stacked_fraction(num, den, fs)
            self._draw_stacked_fraction(cx + (cw - frac_w) / 2, y_center, num, den, fs)
            self.set_font(self.ff, "", fs)
        else:
            self.set_font(self.ff, "", fs)
            self.set_xy(cx, cy)
            self.cell(cw, cell_h, text, align="C")

    def _draw_data_table(self, x, y, headers, rows, orientation="vertical",
                         compact=False, max_width=None):
        """Draw a bordered data table. Returns total height consumed.

        orientation="vertical": headers across top, data rows go down.
        orientation="horizontal": headers become row labels, data goes across.
        compact: if True, use smaller fonts/cells for tight spaces (exit ticket).
        max_width: if set, scale columns proportionally to fit within this width.
        """
        cell_h = 5 if compact else 7
        pad = 1.5 if compact else 2
        fs = 7 if compact else FONT_SIZE_SMALL

        if orientation == "horizontal":
            # Each header is a row; data values go across columns
            n_data_cols = len(rows)
            n_rows = len(headers)

            # Measure header column width
            self.set_font(self.ff, "B", fs)
            header_col_w = max(self.get_string_width(h) for h in headers) + 2 * pad
            header_col_w = max(header_col_w, 12 if compact else 16)

            # Measure data column width
            self.set_font(self.ff, "", fs)
            max_data_w = 8 if compact else 10
            for row in rows:
                for cell in row:
                    cw = self.get_string_width(str(cell)) + 2 * pad
                    max_data_w = max(max_data_w, cw)
            data_col_w = max(max_data_w, 10 if compact else 12)

            # Scale to fit max_width if needed
            if max_width:
                total_w = header_col_w + n_data_cols * data_col_w
                if total_w > max_width:
                    scale = max_width / total_w
                    header_col_w *= scale
                    data_col_w *= scale

            for r in range(n_rows):
                for c in range(n_data_cols + 1):
                    if c == 0:
                        cx = x
                        cw = header_col_w
                        self.set_font(self.ff, "B", fs)
                        text = headers[r]
                    else:
                        cx = x + header_col_w + (c - 1) * data_col_w
                        cw = data_col_w
                        self.set_font(self.ff, "", fs)
                        text = str(rows[c - 1][r])
                    cy = y + r * cell_h
                    self.rect(cx, cy, cw, cell_h)
                    if c == 0:
                        self.set_xy(cx, cy)
                        self.cell(cw, cell_h, text, align="C")
                    else:
                        self._draw_table_cell(cx, cy, cw, cell_h, text, fs)

            total_h = n_rows * cell_h + 3
        else:
            # Standard vertical: headers across top, data rows below
            n_cols = len(headers)

            # Measure column widths
            col_widths = []
            for i in range(n_cols):
                self.set_font(self.ff, "B", fs)
                w = self.get_string_width(headers[i]) + 2 * pad
                self.set_font(self.ff, "", fs)
                for row in rows:
                    if i < len(row):
                        cw = self.get_string_width(str(row[i])) + 2 * pad
                        w = max(w, cw)
                col_widths.append(max(w, 10 if compact else 14))

            # Scale columns to fit max_width if needed
            if max_width:
                total_w = sum(col_widths)
                if total_w > max_width:
                    scale = max_width / total_w
                    col_widths = [cw * scale for cw in col_widths]

            # Header row
            self.set_font(self.ff, "B", fs)
            cx = x
            for i, h in enumerate(headers):
                self.rect(cx, y, col_widths[i], cell_h)
                self.set_xy(cx, y)
                self.cell(col_widths[i], cell_h, h, align="C")
                cx += col_widths[i]

            # Data rows
            self.set_font(self.ff, "", fs)
            for r_idx, row in enumerate(rows):
                ry = y + (r_idx + 1) * cell_h
                cx = x
                for i, cell in enumerate(row):
                    self.rect(cx, ry, col_widths[i], cell_h)
                    self._draw_table_cell(cx, ry, col_widths[i], cell_h, str(cell), fs)
                    cx += col_widths[i]

            total_h = (len(rows) + 1) * cell_h + 3

        self.set_font(self.ff, "", FONT_SIZE_BODY)
        return total_h

    # ============================================================
    # COORDINATE GRID RENDERING
    # ============================================================

    def _draw_coordinate_grid(self, x, y, x_range, y_range, points, lines,
                              grid_size=55, label_step=None,
                              hide_labels=False, x_label=None, y_label=None):
        """Draw a coordinate grid with axes, grid lines, points, and lines.

        x_label / y_label add axis titles (the x title is centered below the
        grid; the y title is rotated up the left side). Returns total height
        consumed.
        """
        x_min, x_max = x_range
        y_min, y_max = y_range
        x_span = x_max - x_min
        y_span = y_max - y_min

        def to_pdf_x(cx):
            return x + (cx - x_min) / x_span * grid_size

        def to_pdf_y(cy):
            return y + grid_size - (cy - y_min) / y_span * grid_size

        # Grid lines (light gray)
        self.set_draw_color(220, 220, 220)
        self.set_line_width(0.15)
        for gx in range(x_min, x_max + 1):
            px = to_pdf_x(gx)
            self.line(px, y, px, y + grid_size)
        for gy in range(y_min, y_max + 1):
            py = to_pdf_y(gy)
            self.line(x, py, x + grid_size, py)

        # Axes (black, thicker)
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.5)
        if y_min <= 0 <= y_max:
            ax_y = to_pdf_y(0)
            self.line(x, ax_y, x + grid_size, ax_y)
            # Arrow
            self.line(x + grid_size, ax_y, x + grid_size - 2, ax_y - 1)
            self.line(x + grid_size, ax_y, x + grid_size - 2, ax_y + 1)
        if x_min <= 0 <= x_max:
            ax_x = to_pdf_x(0)
            self.line(ax_x, y, ax_x, y + grid_size)
            # Arrow
            self.line(ax_x, y, ax_x - 1, y + 2)
            self.line(ax_x, y, ax_x + 1, y + 2)

        # Tick labels (skip when hide_labels is set for blank grids)
        if not hide_labels:
            self.set_font(self.ff, "", 8)  # readable axis numbers when printed
            # Auto-compute label_step if not provided: show at most ~10 labels
            if label_step is None:
                label_step = max(1, (x_span + 1) // 10)
            for gx in range(x_min, x_max + 1):
                if gx % label_step != 0:
                    continue
                px = to_pdf_x(gx)
                label = str(gx)
                lw = self.get_string_width(label)
                if y_min <= 0 <= y_max:
                    label_y = to_pdf_y(0) + 1.5
                else:
                    label_y = y + grid_size + 1.5
                self.set_xy(px - lw / 2, label_y)
                self.cell(lw + 0.5, 3, label, align="C")

            y_label_step = label_step
            for gy in range(y_min, y_max + 1):
                if gy % y_label_step != 0:
                    continue
                if gy == 0 and x_min <= 0 <= x_max:
                    continue  # skip 0 at origin if axes present
                py = to_pdf_y(gy)
                label = str(gy)
                lw = self.get_string_width(label)
                if x_min <= 0 <= x_max:
                    label_x = to_pdf_x(0) - lw - 1.5
                else:
                    label_x = x - lw - 1
                self.set_xy(label_x, py - 1.5)
                self.cell(lw + 0.5, 3, label, align="R")

        # Line segments (blue) — clip to grid rect preserving slope
        self.set_draw_color(0, 80, 180)
        self.set_line_width(0.8)
        for ln in lines:
            clipped = _clip_line_to_rect(
                ln["x1"], ln["y1"], ln["x2"], ln["y2"],
                x_min, x_max, y_min, y_max,
            )
            if clipped:
                cx1, cy1, cx2, cy2 = clipped
                self.line(to_pdf_x(cx1), to_pdf_y(cy1),
                          to_pdf_x(cx2), to_pdf_y(cy2))

        # Points (filled circles). Labels are placed to avoid sitting on the
        # graphed line: below-right for an up-right (non-negative slope) line,
        # above-right otherwise, and flipped to the left of the point if the
        # label would run past the right edge of the grid.
        line_slope = None
        if lines:
            _l = lines[0]
            _dx = _l["x2"] - _l["x1"]
            line_slope = (_l["y2"] - _l["y1"]) / _dx if _dx != 0 else float("inf")
        self.set_fill_color(0, 80, 180)
        self.set_draw_color(0, 80, 180)
        self.set_line_width(0.3)
        for pt in points:
            px = to_pdf_x(pt["x"])
            py = to_pdf_y(pt["y"])
            r = 1.2
            self.ellipse(px - r, py - r, 2 * r, 2 * r, style="DF")
            if pt.get("label"):
                self.set_font(self.ff, "", 8)  # readable point labels
                self.set_text_color(0, 0, 0)
                lw = self.get_string_width(pt["label"])
                # Vertical: put the label on the side away from the line.
                ly = py + 1.6 if (line_slope is not None and line_slope >= 0) else py - 4.0
                # Horizontal: right of the point; flip left near the right edge
                # or for points just left of the y-axis (so the label doesn't
                # run across the axis and its numbers).
                near_yaxis = (x_min <= 0 <= x_max) and (-2 <= pt["x"] <= 0)
                flip_left = (px + 2 + lw > x + grid_size) or (near_yaxis and px - lw - 2 >= x)
                lx = px - lw - 2 if flip_left else px + 2
                self.set_xy(lx, ly)
                self.cell(lw + 1, 3.2, pt["label"])

        # Axis titles (for labeled grids that provide them).
        if not hide_labels and (x_label or y_label):
            self.set_font(self.ff, "", 8)
            self.set_text_color(0, 0, 0)
            if x_label:
                lw = self.get_string_width(x_label)
                self.set_xy(x + grid_size / 2 - lw / 2, y + grid_size + 5.5)
                self.cell(lw, 3, x_label, align="C")
            if y_label:
                lw = self.get_string_width(y_label)
                # Rotate 90 deg CCW around the text's own anchor so it reads
                # bottom-to-top up the left side, vertically centered on the axis.
                px = x - 9
                py = y + grid_size / 2 + lw / 2
                with self.rotation(angle=90, x=px, y=py):
                    self.text(px, py, y_label)

        # Reset
        self.set_draw_color(0, 0, 0)
        self.set_fill_color(255, 255, 255)
        self.set_text_color(0, 0, 0)
        self.set_line_width(0.3)
        self.set_font(self.ff, "", FONT_SIZE_BODY)
        return grid_size + (16 if (x_label and not hide_labels) else 10)

    # ============================================================
    # SVG FIGURE RENDERING
    # ============================================================

    def _render_svg_figure(self, x, y, svg_html, max_width=80, max_height=90):
        """Render an SVG figure into the PDF.

        Delegates to the shared _render_svg_inline function.
        Returns total height consumed (mm).
        """
        try:
            return _render_svg_inline(self, x, y, svg_html, max_width, max_height)
        except Exception:
            # Fallback placeholder on error
            vb_match = re.search(r'viewBox="([^"]*)"', svg_html)
            if vb_match:
                parts = vb_match.group(1).split()
                vb_w, vb_h = float(parts[2]), float(parts[3])
                aspect = vb_h / vb_w
                rh = min(max_width * aspect, max_height)
            else:
                rh = 20
            self.set_draw_color(180, 180, 180)
            self.rect(x, y, max_width, rh)
            self.set_font("Helvetica", "I", 7)
            self.set_text_color(120, 120, 120)
            self.text(x + 2, y + rh / 2, "[Figure could not be rendered]")
            self.set_text_color(0, 0, 0)
            self.set_draw_color(0, 0, 0)
            return rh

    # ============================================================
    # QUESTION WRITING
    # ============================================================

    def _draw_question_number(self, num):
        """Draw the question number. Subclasses can override for styling."""
        self.set_font(self.ff, "B", FONT_SIZE_QUESTION_NUM)
        self.cell(10, LINE_HEIGHT, f"{num}.", new_x="RIGHT", new_y="TOP")

    def _draw_question_divider(self, compact=False):
        """Draw spacing/divider between questions. Subclasses can override."""
        self.ln(2 if compact else 6)

    def write_question(self, num: int, question: GeneratedQuestion,
                       compact: bool = False):
        """Write a single question to the PDF."""
        # Estimate extra height needed for render_data (grid, table, etc.)
        rd = getattr(question, 'render_data', None) or {}
        extra_h = 0
        if rd.get('type') == 'coordinate_grid':
            extra_h = 45 if rd.get('hide_labels') else 65
        elif rd.get('type') == 'data_table':
            extra_h = (len(rd.get('rows', [])) + 1) * 7 + 15
        elif rd.get('type') in ('number_line', 'number_line_point', 'double_number_line'):
            extra_h = 25
        elif rd.get('type') == 'rectangle_diagram':
            extra_h = 55  # 40mm square + 8mm padding + labels
        elif rd.get('type') == 'composite_shape':
            extra_h = 60
        elif rd.get('type') == 'polygon_angles':
            extra_h = 55
        elif rd.get('type') == 'rectangular_prism':
            extra_h = 55
        elif rd.get('svg_html') or rd.get('type') == 'svg_html':
            extra_h = 50

        # Account for multi-part questions needing more text space
        parts = getattr(question, 'parts', None) or []
        part_h = len(parts) * 28  # ~28mm per part (label + answer lines/box)

        # Estimate text height from stem content, accounting for text wrapping
        stem_text = getattr(question, 'stem_text', '') or ''
        avail_w = self.w - 25 - PAGE_MARGIN  # approx text area width
        text_h = 0
        for sl in stem_text.split('\n'):
            if not sl.strip():
                text_h += 3  # blank line spacing
            else:
                # Estimate wrapped line count using string width
                self.set_font(self.ff, "", FONT_SIZE_BODY)
                sw = self.get_string_width(sl)
                wrap_lines = max(1, int(sw / avail_w) + 1)
                text_h += wrap_lines * (LINE_HEIGHT + 1)

        # Also account for MC choices
        choices = getattr(question, 'choices', None) or []
        choice_h = len(choices) * (LINE_HEIGHT + 1) if choices else 0

        min_space = max(50, text_h + 15) + extra_h + part_h + choice_h
        if self.get_y() > self.h - min_space:
            self.add_page()

        ff = self.ff
        self._draw_question_number(num)
        x_body = self.get_x()

        self.set_font(ff, "", FONT_SIZE_BODY)
        stem = self._clean_text(question.stem_text)
        # Keep [FIGURE] as a sentinel; render inline during the line loop
        stem = stem.strip()

        lines = stem.split("\n")
        choices_written = False
        figure_rendered = False

        for line in lines:
            line = line.strip()
            if not line:
                self.ln(1 if compact else 3)
                continue

            # Render figure inline where [FIGURE] appears in stem text
            if "[FIGURE]" in line:
                # Strip the marker; render any surrounding text first
                before = line.split("[FIGURE]")[0].strip()
                after = line.split("[FIGURE]", 1)[1].strip()
                if before:
                    self.set_x(x_body)
                    if self._has_math(before):
                        self._write_line_with_math(before, x_body)
                    else:
                        self.multi_cell(self.w - x_body - PAGE_MARGIN, LINE_HEIGHT,
                                       before, new_x="LMARGIN", new_y="NEXT")
                # Render the figure now
                _sp = 1 if compact else 3
                if rd.get('type') == 'composite_shape':
                    self.ln(_sp)
                    fig_y = self.get_y()
                    if fig_y + 60 > self.h - 25:
                        self.add_page()
                        fig_y = self.get_y()
                    svg_str = _composite_shape_to_svg(rd)
                    h = self._render_svg_figure(x_body + 5, fig_y, svg_str,
                                                max_width=85, max_height=70)
                    self.set_font(self.ff, "", FONT_SIZE_BODY)
                    self.set_y(fig_y + h + 2)
                elif rd.get('type') == 'polygon_angles':
                    self.ln(_sp)
                    fig_y = self.get_y()
                    if fig_y + 55 > self.h - 25:
                        self.add_page()
                        fig_y = self.get_y()
                    svg_str = _polygon_angles_to_svg(rd)
                    h = self._render_svg_figure(x_body + 5, fig_y, svg_str,
                                                max_width=80, max_height=65)
                    self.set_font(self.ff, "", FONT_SIZE_BODY)
                    self.set_y(fig_y + h + 2)
                elif rd.get('type') == 'rectangular_prism':
                    self.ln(_sp)
                    fig_y = self.get_y()
                    if fig_y + 55 > self.h - 25:
                        self.add_page()
                        fig_y = self.get_y()
                    svg_str = _rectangular_prism_to_svg(rd)
                    h = self._render_svg_figure(x_body + 5, fig_y, svg_str,
                                                max_width=80, max_height=65)
                    self.set_font(self.ff, "", FONT_SIZE_BODY)
                    self.set_y(fig_y + h + 2)
                elif rd.get('svg_html'):
                    self.ln(_sp)
                    fig_y = self.get_y()
                    if fig_y + 70 > self.h - 25:
                        self.add_page()
                        fig_y = self.get_y()
                    h = self._render_svg_figure(x_body + 5, fig_y, rd['svg_html'],
                                                max_width=rd.get('fig_max_w', 90),
                                                max_height=rd.get('fig_max_h', 80))
                    self.set_font(self.ff, "", FONT_SIZE_BODY)
                    self.set_y(fig_y + h + 2)
                elif rd.get('type') == 'rectangle_diagram':
                    self.ln(_sp)
                    diag_y = self.get_y()
                    if diag_y + 50 > self.h - 25:
                        self.add_page()
                        diag_y = self.get_y()
                    h = self._draw_rectangle_diagram(
                        x_body + 10, diag_y,
                        side=rd['side'], cut_l=rd['cut_l'], cut_w=rd['cut_w'])
                    self.set_y(diag_y + h)
                elif rd.get('type') == 'data_table':
                    self.ln(_sp)
                    table_y = self.get_y()
                    est_h = (len(rd.get('rows', [])) + 1) * 7 + 5
                    if table_y + est_h > self.h - 25:
                        self.add_page()
                        table_y = self.get_y()
                    h = self._draw_data_table(
                        x_body + 5, table_y,
                        headers=rd['headers'], rows=rd['rows'],
                        orientation=rd.get('orientation', 'vertical'))
                    self.set_y(table_y + h)
                elif rd.get('type') == 'coordinate_grid':
                    self.ln(_sp)
                    grid_y = self.get_y()
                    grid_sz = 38 if rd.get('hide_labels') else 55
                    if grid_y + grid_sz + 10 > self.h - 25:
                        self.add_page()
                        grid_y = self.get_y()
                    h = self._draw_coordinate_grid(
                        x_body + 10, grid_y,
                        x_range=rd['x_range'], y_range=rd['y_range'],
                        points=rd.get('points', []), lines=rd.get('lines', []),
                        grid_size=grid_sz, label_step=rd.get('label_step'),
                        hide_labels=rd.get('hide_labels', False), x_label=rd.get('x_label'), y_label=rd.get('y_label'))
                    self.set_y(grid_y + h)
                elif rd.get('type') in ('number_line', 'number_line_point', 'double_number_line'):
                    self.ln(_sp)
                    nl_y = self.get_y()
                    if nl_y + 35 > self.h - 25:
                        self.add_page()
                        nl_y = self.get_y()
                    if rd['type'] == 'number_line':
                        h = self._draw_number_line(
                            x_body + 5, nl_y, value=rd['value'],
                            circle_type=rd['circle_type'], direction=rd['direction'],
                            blank=rd.get('blank', False))
                    elif rd['type'] == 'number_line_point':
                        h = self._draw_number_line_point(
                            x_body + 5, nl_y, ticks=rd['ticks'],
                            point_value=rd.get('point_value'),
                            point_label=rd.get('point_label', 'P'),
                            points=rd.get('points'))
                    else:
                        h = self._draw_double_number_line(
                            x_body + 5, nl_y,
                            top_ticks=rd['top_ticks'], bottom_ticks=rd['bottom_ticks'],
                            top_label=rd.get('top_label', ''),
                            bottom_label=rd.get('bottom_label', ''))
                    self.set_y(nl_y + h)
                figure_rendered = True
                # Render any text after the [FIGURE] marker
                if after:
                    self.set_x(x_body)
                    if self._has_math(after):
                        self._write_line_with_math(after, x_body)
                    else:
                        self.multi_cell(self.w - x_body - PAGE_MARGIN, LINE_HEIGHT,
                                       after, new_x="LMARGIN", new_y="NEXT")
                    self.set_x(x_body)
                continue

            if line.startswith("- "):
                self.set_x(x_body + 5)
                self.set_font(ff, "", FONT_SIZE_BODY)
                self.cell(5, LINE_HEIGHT, "\u2022", new_x="RIGHT", new_y="TOP")
                bullet_text = line[2:]
                if self._has_math(bullet_text):
                    self._write_line_with_math(bullet_text, self.get_x(),
                                               max_width=self.w - self.get_x() - PAGE_MARGIN)
                else:
                    self.multi_cell(self.w - x_body - PAGE_MARGIN - 10, LINE_HEIGHT,
                                   bullet_text, new_x="LMARGIN", new_y="NEXT")
                self.set_x(x_body)

            elif line.startswith("Part A:") or line.startswith("Part B:") or line.startswith("Part C:"):
                is_part_a = line.startswith("Part A:")
                is_part_b = line.startswith("Part B:")
                is_part_c = line.startswith("Part C:")

                # Before Part B: insert MC choices if not yet written
                if is_part_b and not choices_written and question.choices:
                    self.ln(2)
                    has_nl = any(
                        getattr(c, 'render_data', None)
                        and c.render_data.get('type') == 'number_line'
                        for c in question.choices
                    )
                    if has_nl:
                        self._write_number_line_choices(question.choices, x_body)
                    else:
                        self._write_choices(question.choices, x_body)
                    choices_written = True
                    self.ln(1 if compact else 3)

                # Part label in bold + content
                self.set_x(x_body)
                self.set_font(ff, "B", FONT_SIZE_BODY)
                part_label = line.split(":")[0] + ":"
                rest = ":".join(line.split(":")[1:]).strip()
                self.cell(self.get_string_width(part_label) + 2, LINE_HEIGHT,
                          part_label, new_x="RIGHT", new_y="TOP")
                self.set_font(ff, "", FONT_SIZE_BODY)
                if self._has_math(rest):
                    self._write_line_with_math(rest, self.get_x(),
                                               max_width=self.w - self.get_x() - PAGE_MARGIN)
                else:
                    self.multi_cell(self.w - self.get_x() - PAGE_MARGIN, LINE_HEIGHT,
                                   rest, new_x="LMARGIN", new_y="NEXT")
                self.set_x(x_body)

                # Answer area: depends on part type
                if is_part_a and question.choices:
                    # Part A with MC: no answer line (choices serve as answer)
                    self.ln(2)
                elif (is_part_b or is_part_c) and any(w in rest.lower() for w in ("explain", "describe", "justify")):
                    # Explanation: draw multiple answer lines
                    self._draw_explain_lines(x_body + 5, num_lines=3)
                else:
                    # Standard answer line
                    self.ln(2)
                    self.set_x(x_body + 5)
                    self._draw_answer_line()
                self.ln(1 if compact else 3)
                self.set_x(x_body)

            elif line.startswith("Select ") or line.startswith("In the box"):
                self.set_x(x_body)
                self.set_font(ff, "I", FONT_SIZE_BODY)
                self.multi_cell(self.w - x_body - PAGE_MARGIN, LINE_HEIGHT,
                               line, new_x="LMARGIN", new_y="NEXT")
                self.set_font(ff, "", FONT_SIZE_BODY)
                self.set_x(x_body)

            elif line.startswith("Solve"):
                self.set_x(x_body)
                self.set_font(ff, "B", FONT_SIZE_BODY)
                self.cell(0, LINE_HEIGHT, line, new_x="LMARGIN", new_y="NEXT")
                self.set_font(ff, "", FONT_SIZE_BODY)
                self.set_x(x_body)

            else:
                self.set_x(x_body)
                if self._is_equation_line(line):
                    self.ln(2)
                    if self._has_math(line):
                        self._write_line_with_math(
                            line, x_body + 10, font_size=FONT_SIZE_BODY + 1)
                    else:
                        self.set_font(ff, "", FONT_SIZE_BODY + 1)
                        self.set_x(x_body + 10)
                        self.cell(0, LINE_HEIGHT + 2, self._format_equation(line),
                                 new_x="LMARGIN", new_y="NEXT")
                        self.set_font(ff, "", FONT_SIZE_BODY)
                    self.ln(2)
                elif self._has_math(line) and len(line) < 100:
                    self._write_line_with_math(line, x_body)
                else:
                    self.multi_cell(self.w - x_body - PAGE_MARGIN, LINE_HEIGHT,
                                   line, new_x="LMARGIN", new_y="NEXT")
                self.set_x(x_body)

        # Diagram / table / grid rendering from render_data
        # (skip if already rendered inline via [FIGURE] marker)
        rd = getattr(question, 'render_data', None) or {}
        _sp = 1 if compact else 3  # spacing for compact mode
        if figure_rendered:
            pass  # already rendered inline
        elif rd.get('type') == 'rectangle_diagram':
            self.ln(_sp)
            diag_x = x_body + 10
            diag_y = self.get_y()
            if diag_y + 50 > self.h - 25:
                self.add_page()
                diag_y = self.get_y()
            h = self._draw_rectangle_diagram(
                diag_x, diag_y,
                side=rd['side'], cut_l=rd['cut_l'], cut_w=rd['cut_w']
            )
            self.set_y(diag_y + h)
        elif rd.get('type') == 'data_table':
            self.ln(_sp)
            table_x = x_body + 5
            table_y = self.get_y()
            est_h = (len(rd.get('rows', [])) + 1) * 7 + 5
            if table_y + est_h > self.h - 25:
                self.add_page()
                table_y = self.get_y()
            h = self._draw_data_table(
                table_x, table_y,
                headers=rd['headers'],
                rows=rd['rows'],
                orientation=rd.get('orientation', 'vertical')
            )
            self.set_y(table_y + h)
        elif rd.get('tables'):
            # Multiple tables rendered side by side (e.g. Stem 8.AF.7 Stem 4)
            self.ln(_sp)
            table_list = rd['tables']
            gap = 20  # horizontal gap between tables
            start_x = x_body + 5
            table_y = self.get_y()
            # Estimate height from first table
            est_h = (max(len(t.get('rows', [])) for t in table_list) + 1) * 7 + 5
            if table_y + est_h > self.h - 25:
                self.add_page()
                table_y = self.get_y()
            # Draw labels and tables
            max_h = 0
            cur_x = start_x
            for idx, tbl in enumerate(table_list):
                # Draw label above table
                label = f"Table {idx + 1}"
                self.set_font(self.ff, "B", FONT_SIZE_SMALL)
                self.set_xy(cur_x, table_y)
                self.cell(0, 6, label, new_x="LEFT", new_y="TOP")
                self.set_font(self.ff, "", FONT_SIZE_BODY)
                h = self._draw_data_table(
                    cur_x, table_y + 7,
                    headers=tbl['headers'],
                    rows=tbl['rows'],
                    orientation=tbl.get('orientation', 'vertical')
                )
                # Calculate width of this table to offset the next one
                n_cols = len(tbl['headers'])
                col_w = 14  # minimum col width from _draw_data_table
                for ci in range(n_cols):
                    self.set_font(self.ff, "B", FONT_SIZE_SMALL)
                    w = self.get_string_width(tbl['headers'][ci]) + 4
                    self.set_font(self.ff, "", FONT_SIZE_SMALL)
                    for row in tbl['rows']:
                        if ci < len(row):
                            w = max(w, self.get_string_width(str(row[ci])) + 4)
                    col_w = max(col_w, w)
                table_w = col_w * n_cols
                cur_x += table_w + gap
                max_h = max(max_h, h + 7)
            self.set_y(table_y + max_h)
        elif rd.get('type') == 'coordinate_grid':
            self.ln(_sp)
            grid_x = x_body + 10
            grid_y = self.get_y()
            grid_sz = 38 if rd.get('hide_labels') else 55
            if grid_y + grid_sz + 10 > self.h - 25:
                self.add_page()
                grid_y = self.get_y()
            h = self._draw_coordinate_grid(
                grid_x, grid_y,
                x_range=rd['x_range'],
                y_range=rd['y_range'],
                points=rd.get('points', []),
                lines=rd.get('lines', []),
                grid_size=grid_sz,
                label_step=rd.get('label_step'),
                hide_labels=rd.get('hide_labels', False), x_label=rd.get('x_label'), y_label=rd.get('y_label'),
            )
            self.set_y(grid_y + h)
        elif rd.get('type') == 'number_line':
            self.ln(_sp)
            nl_x = x_body + 5
            nl_y = self.get_y()
            if nl_y + 20 > self.h - 25:
                self.add_page()
                nl_y = self.get_y()
            h = self._draw_number_line(
                nl_x, nl_y,
                value=rd['value'],
                circle_type=rd['circle_type'],
                direction=rd['direction'],
                blank=rd.get('blank', False),
            )
            self.set_y(nl_y + h)
        elif rd.get('type') == 'number_line_point':
            self.ln(_sp)
            nl_x = x_body + 5
            nl_y = self.get_y()
            if nl_y + 20 > self.h - 25:
                self.add_page()
                nl_y = self.get_y()
            h = self._draw_number_line_point(
                nl_x, nl_y,
                ticks=rd['ticks'],
                point_value=rd.get('point_value'),
                point_label=rd.get('point_label', 'P'),
                points=rd.get('points'),
            )
            self.set_y(nl_y + h)
        elif rd.get('type') == 'double_number_line':
            self.ln(_sp)
            dnl_x = x_body + 5
            dnl_y = self.get_y()
            if dnl_y + 35 > self.h - 25:
                self.add_page()
                dnl_y = self.get_y()
            h = self._draw_double_number_line(
                dnl_x, dnl_y,
                top_ticks=rd['top_ticks'],
                bottom_ticks=rd['bottom_ticks'],
                top_label=rd.get('top_label', ''),
                bottom_label=rd.get('bottom_label', ''),
            )
            self.set_y(dnl_y + h)
        elif rd.get('type') == 'composite_shape':
            self.ln(_sp)
            fig_y = self.get_y()
            if fig_y + 60 > self.h - 25:
                self.add_page()
                fig_y = self.get_y()
            svg_str = _composite_shape_to_svg(rd)
            h = self._render_svg_figure(
                x_body + 5, fig_y, svg_str,
                max_width=85, max_height=70,
            )
            self.set_font(self.ff, "", FONT_SIZE_BODY)
            self.set_y(fig_y + h + 2)
        elif rd.get('type') == 'polygon_angles':
            self.ln(_sp)
            fig_y = self.get_y()
            if fig_y + 55 > self.h - 25:
                self.add_page()
                fig_y = self.get_y()
            svg_str = _polygon_angles_to_svg(rd)
            h = self._render_svg_figure(
                x_body + 5, fig_y, svg_str,
                max_width=80, max_height=65,
            )
            self.set_font(self.ff, "", FONT_SIZE_BODY)
            self.set_y(fig_y + h + 2)
        elif rd.get('type') == 'rectangular_prism':
            self.ln(_sp)
            fig_y = self.get_y()
            if fig_y + 55 > self.h - 25:
                self.add_page()
                fig_y = self.get_y()
            svg_str = _rectangular_prism_to_svg(rd)
            h = self._render_svg_figure(
                x_body + 5, fig_y, svg_str,
                max_width=80, max_height=65,
            )
            self.set_font(self.ff, "", FONT_SIZE_BODY)
            self.set_y(fig_y + h + 2)
        elif rd.get('svg_html'):
            # Render SVG geometry figures (circles, triangles, 3D shapes, etc.)
            self.ln(_sp)
            fig_y = self.get_y()
            fig_h_est = 70  # estimated max height
            if fig_y + fig_h_est > self.h - 25:
                self.add_page()
                fig_y = self.get_y()
            h = self._render_svg_figure(
                x_body + 5, fig_y, rd['svg_html'],
                max_width=rd.get('fig_max_w', 90),
                max_height=rd.get('fig_max_h', 80),
            )
            self.set_font(self.ff, "", FONT_SIZE_BODY)
            self.set_y(fig_y + h + 2)

        # MC choices (if not already written inside Part A/B flow)
        if question.choices and not choices_written:
            self.ln(2)
            has_nl = any(
                getattr(c, 'render_data', None)
                and c.render_data.get('type') == 'number_line'
                for c in question.choices
            )
            if has_nl:
                self._write_number_line_choices(question.choices, x_body)
            else:
                self._write_choices(question.choices, x_body)

        # NR/EQ answer line (non-multi-part only)
        if question.item_type in (ItemType.NR, ItemType.EQ) and not question.parts:
            self.ln(_sp)
            self.set_x(x_body + 5)
            self._draw_answer_line()
            self.ln(2)

        # ER answer box (non-multi-part only)
        if question.item_type == ItemType.ER and not question.parts:
            self.ln(_sp)
            self.set_x(x_body)
            self._draw_answer_box(x_body)

        self._draw_question_divider(compact=compact)

    def _write_choices(self, choices, x_body):
        """Write MC choices. 1-col only for genuinely wide choices, else 2-col.

        Expression choices (containing variables) are rendered in italic
        for a more mathematical appearance.  Short math choices (like "5/8")
        use 2-column layout with stacked-fraction support.
        """
        self.set_font(self.ff, "", FONT_SIZE_BODY)

        # Detect if choices are math expressions (variables + numbers)
        is_expression = any(self._EXPR_RE.search(c.text) for c in choices)
        expr_style = "I" if is_expression else ""

        # Only force 1-col when choices are genuinely wide (>20 chars).
        # Short math like "5/8", "2x + 3" fits fine in 2-col.
        col_width = (self.w - x_body - PAGE_MARGIN) / 2
        max_text_len = max(len(c.text) for c in choices) if choices else 0
        use_single_col = max_text_len > 20

        if use_single_col:
            # Wrap long choices within the page so they never run off the
            # right edge (a common complaint on wordy DSP answer choices).
            avail_w = self.w - PAGE_MARGIN - (x_body + 5)
            for choice in choices:
                self.set_x(x_body + 5)
                text = f"{choice.key}. {self._clean_text(choice.text)}"
                if self._has_math(text):
                    self._write_line_with_math(text, x_body + 5,
                                               font_style=expr_style,
                                               max_width=avail_w)
                else:
                    self.set_font(self.ff, expr_style, FONT_SIZE_BODY)
                    self.set_x(x_body + 5)
                    self.multi_cell(avail_w, LINE_HEIGHT, text,
                                    new_x="LMARGIN", new_y="NEXT")
            self.ln(1)
        else:
            # 2-column layout with stacked-fraction / exponent support
            row_lh = LINE_HEIGHT
            for i, choice in enumerate(choices):
                col_x = x_body + 5 if i % 2 == 0 else x_body + 5 + col_width
                text = f"{choice.key}. {self._clean_text(choice.text)}"

                if i % 2 == 0:
                    # Start of a new row
                    if i > 0:
                        self.set_y(self.get_y() + row_lh)
                    # Determine row height: use taller height if either
                    # column in this row contains math
                    row_has_math = self._has_math(text)
                    if i + 1 < len(choices):
                        right_text = f"{choices[i+1].key}. {self._clean_text(choices[i+1].text)}"
                        row_has_math = row_has_math or self._has_math(right_text)
                    row_lh = FRAC_LINE_HEIGHT if row_has_math else LINE_HEIGHT

                if self._has_math(text):
                    y_before = self.get_y()
                    self._write_line_with_math(text, col_x, font_style=expr_style)
                    # Reset y so right column starts at same row
                    if i % 2 == 0 and i + 1 < len(choices):
                        self.set_y(y_before)
                else:
                    self.set_font(self.ff, expr_style, FONT_SIZE_BODY)
                    self.set_xy(col_x, self.get_y())
                    self.cell(col_width - 5, row_lh, text,
                             new_x="RIGHT", new_y="TOP")

            self.set_y(self.get_y() + row_lh)
            self.set_font(self.ff, "", FONT_SIZE_BODY)

    def _write_number_line_choices(self, choices, x_body):
        """Write MC choices as number line diagrams."""
        nl_width = min(70, self.w - x_body - PAGE_MARGIN - 15)

        for choice in choices:
            if self.get_y() > self.h - 25:
                self.add_page()

            rd = getattr(choice, 'render_data', None) or {}

            self.set_font(self.ff, "B", FONT_SIZE_BODY)
            self.set_x(x_body + 3)
            self.cell(8, LINE_HEIGHT, f"{choice.key}.", new_x="RIGHT", new_y="TOP")

            if rd.get('type') == 'number_line':
                nl_x = x_body + 12
                nl_y = self.get_y()
                h = self._draw_number_line(
                    nl_x, nl_y,
                    value=rd['value'],
                    circle_type=rd['circle_type'],
                    direction=rd['direction'],
                    width=nl_width
                )
                self.set_y(nl_y + h + 1)
            else:
                self.set_font(self.ff, "", FONT_SIZE_BODY)
                self.cell(0, LINE_HEIGHT, self._clean_text(choice.text),
                         new_x="LMARGIN", new_y="NEXT")
                self.ln(2)

    def _draw_answer_line(self):
        """Draw a single horizontal answer line."""
        y = self.get_y() + 3
        x = self.get_x()
        self.line(x, y, x + ANSWER_LINE_WIDTH, y)
        self.ln(5)

    def _draw_explain_lines(self, x_start, num_lines=4, line_spacing=8):
        """Draw multiple horizontal answer lines for written explanations."""
        self.ln(3)
        line_width = self.w - x_start - PAGE_MARGIN
        for _ in range(num_lines):
            y = self.get_y()
            self.line(x_start, y, x_start + line_width, y)
            self.ln(line_spacing)

    def _draw_answer_box(self, x_body):
        """Draw a box for extended response answers."""
        x = x_body
        y = self.get_y()
        w = self.w - x - PAGE_MARGIN
        h = 50

        if y + h > self.h - 25:
            self.add_page()
            y = self.get_y()

        self.rect(x, y, w, h)
        self.set_y(y + h + 3)

    def _is_equation_line(self, line: str) -> bool:
        """Check if a line looks like a standalone equation."""
        line = line.strip()
        if not line:
            return False
        has_equals = "=" in line
        is_short = len(line) < 30
        has_variable = any(c.isalpha() and c not in "ABCD" for c in line)
        is_not_sentence = not line[0].isupper() or len(line.split()) < 4
        return has_equals and is_short and has_variable and is_not_sentence

    def _format_equation(self, eq: str) -> str:
        eq = eq.replace("\u00f7", "/")
        eq = eq.replace("\u00d7", "*")
        return eq

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean text for PDF output."""
        text = text.replace("\u00f7", "/")
        text = text.replace("\u00d7", "\u00d7")  # keep × as-is (Arial supports it)
        # Convert text operators to proper Unicode math symbols
        text = text.replace(">=", "\u2265")  # ≥
        text = text.replace("<=", "\u2264")  # ≤
        return text


class AnswerKeyPDF(FPDF):
    """Separate PDF for answer key."""

    def __init__(self, title: str = "ANSWER KEY"):
        super().__init__()
        self.key_title = title
        self.set_auto_page_break(auto=True, margin=20)
        self.ff = _register_arial(self)

    def header(self):
        self.set_font(self.ff, "B", FONT_SIZE_TITLE)
        self.cell(0, 8, self.key_title, new_x="LMARGIN", new_y="NEXT", align="L")
        self.line(PAGE_MARGIN, self.get_y() + 2,
                  self.w - PAGE_MARGIN, self.get_y() + 2)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.ff, "I", 8)
        self.cell(0, 10, f"Answer Key - Page {self.page_no()}/{{nb}}", align="C")

    def write_answer(self, num: int, question: GeneratedQuestion):
        if self.get_y() > self.h - 40:
            self.add_page()

        self.set_font(self.ff, "B", FONT_SIZE_BODY)
        self.cell(10, LINE_HEIGHT, f"{num}.", new_x="RIGHT", new_y="TOP")
        x_body = self.get_x()

        self.set_font(self.ff, "B", FONT_SIZE_BODY)
        answer = MathPDF._clean_text(question.answer_text)
        self.multi_cell(self.w - x_body - PAGE_MARGIN, LINE_HEIGHT,
                       f"Answer: {answer}", new_x="LMARGIN", new_y="NEXT")

        self.set_x(x_body)
        self.set_font(self.ff, "", FONT_SIZE_SMALL)
        prof = PROFICIENCY_LABELS.get(question.proficiency_level, "")
        diff = DIFFICULTY_LABELS.get(question.difficulty, "")
        meta = f"DOK: {question.dok}  |  {prof}  |  {diff}  |  {question.item_type.value}"
        self.cell(0, LINE_HEIGHT, meta, new_x="LMARGIN", new_y="NEXT")

        if question.worked_solution:
            self.set_x(x_body)
            self.set_font(self.ff, "", FONT_SIZE_SMALL)
            solution = MathPDF._clean_text(question.worked_solution)
            for line in solution.split("\n"):
                self.set_x(x_body)
                self.cell(0, LINE_HEIGHT - 1, line.strip(), new_x="LMARGIN", new_y="NEXT")

        self.ln(2)
        self.line(PAGE_MARGIN, self.get_y(), self.w - PAGE_MARGIN, self.get_y())
        self.ln(3)


class PlugNPlayAnswerKeyPDF(AnswerKeyPDF):
    """Answer key PDF with Plug N Play branding."""

    def __init__(self, title="ANSWER KEY", standard_code=""):
        super().__init__(title=title)
        self.standard_code = standard_code
        self._quote = _STRUGGLE_QUOTES[hash(standard_code) % len(_STRUGGLE_QUOTES)]
        self.set_auto_page_break(auto=True, margin=SB_FOOTER_HEIGHT + 8)

    def header(self):
        """Rounded yellow answer key header — first page only."""
        if self.page_no() > 1:
            self.set_y(PAGE_MARGIN)
            return
        _draw_sb_header(self, PAGE_MARGIN, 5, self.w - 2 * PAGE_MARGIN, 16,
                        title="Plug N Play Answer Key",
                        standard_code=self.standard_code,
                        r=3, include_name=False, font_title=12)
        self.set_y(24)

    def footer(self):
        """Yellow footer bar with quote and page number."""
        bar_y = self.h - SB_FOOTER_HEIGHT

        self.set_fill_color(*SB_YELLOW)
        self.rect(0, bar_y, self.w, SB_FOOTER_HEIGHT, style="F")

        self.set_draw_color(*SB_BROWN)
        self.set_line_width(0.4)
        self.line(0, bar_y, self.w, bar_y)

        self.set_text_color(*SB_BROWN)
        self.set_font(self.ff, "I", 7)
        self.set_xy(PAGE_MARGIN, bar_y + 2)
        self.cell(0, 5,
                  f'"{self._quote}"   |   Answer Key - Page {self.page_no()}/{{nb}}',
                  align="C")

        self.set_text_color(0, 0, 0)
        self.set_draw_color(0, 0, 0)
        self.set_fill_color(255, 255, 255)
        self.set_line_width(0.3)

    def write_answer(self, num: int, question: GeneratedQuestion):
        """Write answer with yellow divider line."""
        if self.get_y() > self.h - 40:
            self.add_page()

        self.set_font(self.ff, "B", FONT_SIZE_BODY)
        self.cell(10, LINE_HEIGHT, f"{num}.", new_x="RIGHT", new_y="TOP")
        x_body = self.get_x()

        self.set_font(self.ff, "B", FONT_SIZE_BODY)
        answer = MathPDF._clean_text(question.answer_text)
        self.multi_cell(self.w - x_body - PAGE_MARGIN, LINE_HEIGHT,
                       f"Answer: {answer}", new_x="LMARGIN", new_y="NEXT")

        self.set_x(x_body)
        self.set_font(self.ff, "", FONT_SIZE_SMALL)
        prof = PROFICIENCY_LABELS.get(question.proficiency_level, "")
        diff = DIFFICULTY_LABELS.get(question.difficulty, "")
        meta = f"DOK: {question.dok}  |  {prof}  |  {diff}  |  {question.item_type.value}"
        self.cell(0, LINE_HEIGHT, meta, new_x="LMARGIN", new_y="NEXT")

        if question.worked_solution:
            self.set_x(x_body)
            self.set_font(self.ff, "", FONT_SIZE_SMALL)
            solution = MathPDF._clean_text(question.worked_solution)
            for line in solution.split("\n"):
                self.set_x(x_body)
                self.cell(0, LINE_HEIGHT - 1, line.strip(), new_x="LMARGIN", new_y="NEXT")

        # Yellow divider instead of black
        self.ln(2)
        self.set_draw_color(*SB_YELLOW)
        self.set_line_width(0.5)
        self.line(PAGE_MARGIN, self.get_y(), self.w - PAGE_MARGIN, self.get_y())
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.3)
        self.ln(3)


def _build_worksheet(questions, title, standard, category, subdomain,
                     calculator, compact=False):
    """Build a MathPDF worksheet (without saving). Used by two-pass logic."""
    pdf = MathPDF(
        title=title, standard=standard,
        category=category, subdomain=subdomain, calculator=calculator
    )
    pdf.alias_nb_pages()
    pdf.add_page()
    for i, q in enumerate(questions, 1):
        pdf.write_question(i, q, compact=compact)
    return pdf


def generate_worksheet_pdf(questions: list[GeneratedQuestion],
                           output_path: str,
                           title: str = "ILEARN Practice",
                           standard_code: str = "",
                           standard_text: str = "",
                           category: str = "Algebra and Functions",
                           subdomain: str = "Equations and Inequalities",
                           calculator: str = "Not Allowed",
                           include_answer_key: bool = True) -> str:
    """Generate a PDF worksheet from a list of questions."""
    if not questions:
        raise ValueError("No questions provided")

    full_title = f"{title} - {standard_code}" if standard_code else title
    standard = (f"{standard_code}: {standard_text[:100]}..."
                if standard_text else standard_code)

    # First pass: normal layout
    pdf = _build_worksheet(questions, full_title, standard,
                           category, subdomain, calculator, compact=False)

    # If it barely overflows (last page < 35% used), retry with compact spacing
    if pdf.page_no() > 1:
        last_page_pct = pdf.get_y() / pdf.h
        if last_page_pct < 0.35:
            pdf = _build_worksheet(questions, full_title, standard,
                                   category, subdomain, calculator,
                                   compact=True)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    pdf.output(output_path)

    if include_answer_key:
        key_path = output_path.replace(".pdf", "_answer_key.pdf")
        key_pdf = AnswerKeyPDF(
            title=f"ANSWER KEY - {standard_code}" if standard_code else "ANSWER KEY"
        )
        key_pdf.alias_nb_pages()
        key_pdf.add_page()

        for i, q in enumerate(questions, 1):
            key_pdf.write_answer(i, q)

        key_pdf.output(key_path)
        print(f"Answer key saved to: {key_path}")

    print(f"Worksheet saved to: {output_path}")
    return output_path


# ============================================================
# STRUGGLEBUS PDF LAYOUTS
# ============================================================

def _draw_bus_icon(pdf, x, y, w=20, h=12):
    """No-op: icon removed. The title text handles branding."""
    pass


# Productive struggle quotes for PDF footers
_STRUGGLE_QUOTES = [
    "Mistakes are proof you're trying.",
    "The struggle is where the learning happens.",
    "Stuck? Good. That's where the magic happens.",
    "Your brain grows stronger when you work through hard problems.",
    "Progress, not perfection.",
    "Be brave enough to be bad at something new.",
    "Confusion is the beginning of understanding.",
    "Plug in. Play on.",
    "Hard is not the same as impossible.",
    "Every expert was once a beginner.",
    "You don't have to be perfect to be amazing.",
    "The only real mistake is the one you don't learn from.",
    "Struggling means you're growing.",
    "Math is not about speed. It's about understanding.",
    "If it doesn't challenge you, it doesn't change you.",
    "Your best work happens outside your comfort zone.",
    "Effort is what turns ability into achievement.",
    "Not yet doesn't mean not ever.",
    "The view from the top is worth the climb.",
    "Smart is not something you are. It's something you become.",
    "You are braver than you believe and stronger than you seem.",
    "Mistakes are just detours, not dead ends.",
    "Keep going - the answer is closer than you think.",
    "Think of hard problems as brain push-ups.",
    "Great things never come from comfort zones.",
    "Fall seven times, stand up eight.",
    "The challenge you face today is building the strength you need tomorrow.",
    "Every try makes the next one easier.",
    "A smooth sea never made a skilled sailor.",
    "Believe in the power of yet.",
]


def _draw_sb_header(pdf, x, y, w, h, title, standard_code, r=3,
                     include_name=True, font_title=10, font_name=7):
    """Draw a rounded-corner yellow Plug N Play header banner.

    Args:
        pdf: FPDF instance
        x, y: top-left corner of the banner
        w, h: width and height of the banner
        title: e.g. "Plug N Play Exit Ticket"
        standard_code: e.g. "6.AF.1" (displayed after the title)
        r: corner radius in mm
        include_name: whether to draw a Name line
        font_title: font size for the title
        font_name: font size for the name line
    """
    from fpdf.enums import RenderStyle

    ff = getattr(pdf, 'ff', 'Helvetica')

    # Rounded yellow filled box
    pdf.set_fill_color(*SB_YELLOW)
    pdf.set_draw_color(*SB_YELLOW)
    pdf.set_line_width(0.1)
    pdf._draw_rounded_rect(x, y, w, h, RenderStyle.DF, True, r)

    text_x = x + 3

    # Top row: "Plug N Play - 7.AF.3" left, "Date: ___" right
    pdf.set_text_color(*SB_BROWN)
    pdf.set_font(ff, "B", font_title)
    label = f"{title}  -  {standard_code}" if standard_code else title
    pdf.set_xy(text_x, y + 1)
    pdf.cell(w * 0.6, h * 0.45, label)

    # Name and Date on the same row below the title
    if include_name:
        pdf.set_text_color(*SB_DARK)
        pdf.set_font(ff, "", font_name)
        pdf.set_xy(text_x, y + h * 0.55)
        pdf.cell(w * 0.5, h * 0.4, "Name: _________________________")

        date_text = "Date: _______________"
        date_w = pdf.get_string_width(date_text) + 4
        pdf.set_xy(x + w - date_w, y + h * 0.55)
        pdf.cell(date_w, h * 0.4, date_text)

    # Reset colors
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)


class ExitTicketPDF(MathPDF):
    """PDF with one question repeated in 4 quadrants with dashed cut lines."""

    def __init__(self, standard_code="", standard_text=""):
        super().__init__(standard=standard_code)
        self.standard_code = standard_code
        self.standard_text = standard_text
        self.set_auto_page_break(auto=False)

    def header(self):
        pass  # No header in exit ticket (handled per-quadrant)

    def footer(self):
        pass  # No footer in exit ticket


class PlugNPlayPDF(MathPDF):
    """MathPDF subclass with Plug N Play branding -- school-bus yellow theme."""

    def __init__(self, title="Plug N Play", standard_code="", standard_text="",
                 calculator="Not Allowed"):
        super().__init__(
            title=title,
            standard=f"{standard_code}: {standard_text[:80]}..." if len(standard_text) > 80 else f"{standard_code}: {standard_text}",
            category="",
            subdomain="",
            calculator=calculator,
        )
        self.standard_code = standard_code
        self._quote = _STRUGGLE_QUOTES[hash(standard_code) % len(_STRUGGLE_QUOTES)]
        self.set_auto_page_break(auto=True, margin=SB_FOOTER_HEIGHT + 8)

    def header(self):
        """Rounded yellow banner header — first page only."""
        if self.page_no() > 1:
            self.set_y(PAGE_MARGIN)
            return

        banner_w = self.w - 2 * PAGE_MARGIN
        _draw_sb_header(self, PAGE_MARGIN, 5, banner_w, 20,
                        title="Plug N Play",
                        standard_code=self.standard_code,
                        r=3, include_name=True, font_title=12, font_name=9)

        # Reset and position after banner
        self.set_text_color(0, 0, 0)
        self.set_fill_color(255, 255, 255)
        self.set_draw_color(0, 0, 0)
        self.set_y(SB_HEADER_HEIGHT + 3)

    def footer(self):
        """Yellow footer bar with bus icon, motivational quote, page number."""
        bar_y = self.h - SB_FOOTER_HEIGHT

        # Yellow footer bar
        self.set_fill_color(*SB_YELLOW)
        self.rect(0, bar_y, self.w, SB_FOOTER_HEIGHT, style="F")

        # Thin dark line at top of bar
        self.set_draw_color(*SB_BROWN)
        self.set_line_width(0.4)
        self.line(0, bar_y, self.w, bar_y)

        # Mini bus icon
        _draw_bus_icon(self, PAGE_MARGIN, bar_y + 3, w=10, h=6)

        # Motivational quote
        self.set_text_color(*SB_BROWN)
        self.set_font(self.ff, "I", 7)
        self.set_xy(PAGE_MARGIN + 14, bar_y + 2)
        self.cell(self.w - 2 * PAGE_MARGIN - 60, 5, f'"{self._quote}"')

        # Page number + brand
        self.set_font(self.ff, "", 7)
        page_text = f"Plug N Play  |  Page {self.page_no()}/{{nb}}"
        page_w = self.get_string_width(page_text)
        self.set_xy(self.w - PAGE_MARGIN - page_w, bar_y + 2)
        self.cell(page_w, 5, page_text)

        # Reset
        self.set_text_color(0, 0, 0)
        self.set_draw_color(0, 0, 0)
        self.set_fill_color(255, 255, 255)
        self.set_line_width(0.3)

    def _draw_question_number(self, num):
        """Draw question number inside a yellow circle."""
        x = self.get_x()
        y = self.get_y()
        r = SB_Q_CIRCLE_R
        cx = x + r + 1
        cy = y + LINE_HEIGHT / 2

        # Yellow filled circle
        self.set_fill_color(*SB_YELLOW)
        self.set_draw_color(*SB_YELLOW)
        self.set_line_width(0.3)
        self.ellipse(cx - r, cy - r, 2 * r, 2 * r, style="DF")

        # Number text centered in circle
        self.set_text_color(*SB_DARK)
        self.set_font(self.ff, "B", FONT_SIZE_QUESTION_NUM)
        num_str = str(num)
        num_w = self.get_string_width(num_str)
        self.set_xy(cx - num_w / 2, cy - LINE_HEIGHT / 2)
        self.cell(num_w + 1, LINE_HEIGHT, num_str)

        # Reset and position after circle
        self.set_draw_color(0, 0, 0)
        self.set_text_color(0, 0, 0)
        self.set_fill_color(255, 255, 255)
        self.set_xy(x + 2 * r + 3, y)

    def _draw_question_divider(self, compact=False):
        """Draw a yellow dashed line with center dot between questions."""
        self.ln(1 if compact else 3)
        y = self.get_y()
        x_start = PAGE_MARGIN + 5
        x_end = self.w - PAGE_MARGIN - 5

        # Yellow dashed line
        self.set_draw_color(*SB_YELLOW)
        self.set_line_width(0.8)
        dash_len = 4
        gap_len = 2
        x = x_start
        while x < x_end:
            x2 = min(x + dash_len, x_end)
            self.line(x, y, x2, y)
            x += dash_len + gap_len

        # Small yellow dot at center
        mid_x = (x_start + x_end) / 2
        d = 1.2
        self.set_fill_color(*SB_YELLOW)
        self.ellipse(mid_x - d, y - d, 2 * d, 2 * d, style="F")

        # Reset
        self.set_draw_color(0, 0, 0)
        self.set_fill_color(255, 255, 255)
        self.set_line_width(0.3)
        self.ln(1 if compact else 3)


# ================================================================
# RENDER-DATA → SVG CONVERTERS
# ================================================================

def _composite_shape_to_svg(rd):
    """Convert composite_shape render_data to an SVG string.

    Handles rectangles, triangles, dimension labels, and dashed lines.
    Uses absolute coordinates (no transform groups) so _render_svg_inline
    can correctly position text labels.
    """
    svg_w = rd.get('svg_width', 300)
    svg_h = rd.get('svg_height', 250)
    ox = rd.get('offset_x', 25)
    oy = rd.get('offset_y', 20)

    # Pad the viewBox on every side. Vertical dimension labels are drawn at
    # `mx - 8` with text-anchor="middle", so a label on a line near the left
    # edge can land at x < 0. fpdf draws outside a viewBox fine, but a browser
    # clips to it (the projection showed "5 ft" cut to "; ft"). A margin keeps
    # edge labels inside the box for both. (polygon_angles already uses a
    # non-zero viewBox origin, so the PDF coordinate mapper handles this.)
    PAD_L, PAD_T, PAD_R, PAD_B = 24, 12, 14, 12
    vb_x, vb_y = -PAD_L, -PAD_T
    vb_w, vb_h = svg_w + PAD_L + PAD_R, svg_h + PAD_T + PAD_B
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" '
             f'viewBox="{vb_x} {vb_y} {vb_w} {vb_h}" '
             f'width="{vb_w}" height="{vb_h}">']

    def _offset_points(pts_str):
        """Add ox/oy offset to a polygon points string."""
        coords = pts_str.strip().split()
        shifted = []
        for c in coords:
            xy = c.split(',')
            shifted.append(f'{float(xy[0]) + ox},{float(xy[1]) + oy}')
        return ' '.join(shifted)

    # Draw shapes (with offset applied)
    for s in rd.get('shapes', []):
        stroke = s.get('stroke', '#333')
        sw = s.get('stroke_width', '1.5')
        fill = s.get('fill', '#dbeafe')
        dash = f' stroke-dasharray="{s["stroke_dasharray"]}"' if s.get('stroke_dasharray') else ''
        if s['type'] == 'rect':
            parts.append(
                f'<rect x="{s["x"] + ox}" y="{s["y"] + oy}" '
                f'width="{s["width"]}" height="{s["height"]}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash}/>')
        elif s['type'] == 'triangle':
            parts.append(
                f'<polygon points="{_offset_points(s["points"])}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash}/>')

    # Dashed separator lines (with offset)
    for dl in rd.get('dashed_lines', []):
        parts.append(
            f'<line x1="{dl["x1"] + ox}" y1="{dl["y1"] + oy}" '
            f'x2="{dl["x2"] + ox}" y2="{dl["y2"] + oy}" '
            f'stroke="#666" stroke-width="1" stroke-dasharray="5,3"/>')

    # Dimension lines with labels (with offset)
    for dim in rd.get('dimensions', []):
        x1, y1 = dim['x1'] + ox, dim['y1'] + oy
        x2, y2 = dim['x2'] + ox, dim['y2'] + oy
        dashed = dim.get('dashed', False)
        dash_attr = ' stroke-dasharray="4,3"' if dashed else ''
        # Draw the dimension line
        parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="#555" stroke-width="0.8"{dash_attr}/>')
        # End ticks (small perpendicular marks)
        is_vertical = abs(x2 - x1) < abs(y2 - y1)
        if is_vertical:
            parts.append(f'<line x1="{x1-3}" y1="{y1}" x2="{x1+3}" y2="{y1}" stroke="#555" stroke-width="0.8"/>')
            parts.append(f'<line x1="{x2-3}" y1="{y2}" x2="{x2+3}" y2="{y2}" stroke="#555" stroke-width="0.8"/>')
        else:
            parts.append(f'<line x1="{x1}" y1="{y1-3}" x2="{x1}" y2="{y1+3}" stroke="#555" stroke-width="0.8"/>')
            parts.append(f'<line x1="{x2}" y1="{y2-3}" x2="{x2}" y2="{y2+3}" stroke="#555" stroke-width="0.8"/>')
        # Label at midpoint
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        if is_vertical:
            # Place vertical label to the left of the line
            parts.append(
                f'<text x="{mx - 8}" y="{my + 4}" font-size="12" '
                f'text-anchor="middle">{dim["label"]}</text>')
        else:
            parts.append(
                f'<text x="{mx}" y="{my - 4}" font-size="12" '
                f'text-anchor="middle">{dim["label"]}</text>')

    parts.append('</svg>')
    return '\n'.join(parts)


def _polygon_angles_to_svg(rd):
    """Convert polygon_angles render_data to an SVG string.

    Handles triangles, quadrilaterals, and compound figures with
    angle labels, right-angle squares, and vertex labels.
    """
    vertices = rd.get('vertices', [])
    angles = rd.get('angles', [])
    offsets = rd.get('label_offsets', [])
    right_indices = rd.get('right_angle_indices', [])
    shape = rd.get('shape', 'triangle')

    # Determine viewBox from vertex extents
    xs = [v['x'] for v in vertices]
    ys = [v['y'] for v in vertices]
    min_x = min(xs) - 50
    min_y = min(ys) - 50
    max_x = max(xs) + 50
    max_y = max(ys) + 50
    vb_w = max_x - min_x
    vb_h = max_y - min_y

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" '
             f'viewBox="{min_x} {min_y} {vb_w} {vb_h}" '
             f'width="{int(vb_w)}" height="{int(vb_h)}">']

    # Draw the polygon
    if shape == 'compound':
        # Compound figure: quadrilateral + diagonal
        pts_str = ' '.join(f'{v["x"]},{v["y"]}' for v in vertices)
        parts.append(
            f'<polygon points="{pts_str}" fill="#e0f2fe" '
            f'stroke="#333" stroke-width="1.5"/>')
        diag = rd.get('diagonal')
        if diag:
            parts.append(
                f'<line x1="{diag["x1"]}" y1="{diag["y1"]}" '
                f'x2="{diag["x2"]}" y2="{diag["y2"]}" '
                f'stroke="#333" stroke-width="1" stroke-dasharray="5,3"/>')
    else:
        pts_str = ' '.join(f'{v["x"]},{v["y"]}' for v in vertices)
        parts.append(
            f'<polygon points="{pts_str}" fill="#e0f2fe" '
            f'stroke="#333" stroke-width="1.5"/>')

    # Right-angle squares
    import math as _math
    for ri in right_indices:
        v = vertices[ri]
        # Get adjacent vertices
        n = len(vertices)
        if shape == 'compound':
            # For compound, right_angle_indices maps differently
            continue
        v_prev = vertices[(ri - 1) % n]
        v_next = vertices[(ri + 1) % n]
        # Compute direction vectors
        dx1 = v_prev['x'] - v['x']
        dy1 = v_prev['y'] - v['y']
        dx2 = v_next['x'] - v['x']
        dy2 = v_next['y'] - v['y']
        d1 = _math.sqrt(dx1*dx1 + dy1*dy1) or 1
        d2 = _math.sqrt(dx2*dx2 + dy2*dy2) or 1
        sq_sz = 10
        ux1 = dx1 / d1 * sq_sz
        uy1 = dy1 / d1 * sq_sz
        ux2 = dx2 / d2 * sq_sz
        uy2 = dy2 / d2 * sq_sz
        p1x = v['x'] + ux1
        p1y = v['y'] + uy1
        p2x = v['x'] + ux1 + ux2
        p2y = v['y'] + uy1 + uy2
        p3x = v['x'] + ux2
        p3y = v['y'] + uy2
        parts.append(
            f'<polygon points="{v["x"]},{v["y"]} {p1x},{p1y} '
            f'{p2x},{p2y} {p3x},{p3y}" '
            f'fill="none" stroke="#333" stroke-width="1"/>')

    # Angle labels
    if shape == 'compound':
        # For compound figures, angles map to specific positions (not 1:1 with vertices)
        # Use vertex_labels for vertex letters, and place angle labels near their vertices
        v_labels = rd.get('vertex_labels', [])
        for vl in v_labels:
            parts.append(
                f'<text x="{vl["x"]}" y="{vl["y"]}" font-size="14" '
                f'text-anchor="middle" font-weight="bold">{vl["text"]}</text>')
        # Place angle labels using provided offsets
        # For compound, angles have vertex info; use label_offsets positionally
        # Angles are: a1@A, a2@B(upper), b1@B(lower), b2@C, a3@D(lower), ?@D(upper)
        # Map them near their vertex positions
        angle_vertex_map = rd.get('angle_vertex_map', [0, 1, 1, 2, 3, 3])
        for i, ang in enumerate(angles):
            vi = angle_vertex_map[i] if i < len(angle_vertex_map) else 0
            v = vertices[vi]
            off = offsets[i] if i < len(offsets) else {"dx": 0, "dy": 0}
            lx = v['x'] + off['dx']
            ly = v['y'] + off['dy']
            parts.append(
                f'<text x="{lx}" y="{ly}" font-size="24" '
                f'text-anchor="middle">{ang["label"]}</text>')
    else:
        for i, ang in enumerate(angles):
            if i >= len(vertices) or i >= len(offsets):
                break
            v = vertices[i]
            off = offsets[i]
            lx = v['x'] + off['dx']
            ly = v['y'] + off['dy']
            parts.append(
                f'<text x="{lx}" y="{ly}" font-size="24" '
                f'text-anchor="middle">{ang["label"]}</text>')

    parts.append('</svg>')
    return '\n'.join(parts)


def _rectangular_prism_to_svg(rd):
    """Convert rectangular_prism render_data to an SVG string.

    Renders three visible faces (front, top, right) and hidden dashed edges.
    """
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" '
             'viewBox="0 0 300 250" width="300" height="250">']

    # Three visible faces with different shading
    parts.append(
        f'<polygon points="{rd["front_face"]}" '
        f'fill="#dbeafe" stroke="#333" stroke-width="1.5"/>')
    parts.append(
        f'<polygon points="{rd["top_face"]}" '
        f'fill="#bfdbfe" stroke="#333" stroke-width="1.5"/>')
    parts.append(
        f'<polygon points="{rd["right_face"]}" '
        f'fill="#93c5fd" stroke="#333" stroke-width="1.5"/>')

    # Hidden edges (dashed)
    for edge in rd.get('hidden_edges', []):
        parts.append(
            f'<line x1="{edge["x1"]}" y1="{edge["y1"]}" '
            f'x2="{edge["x2"]}" y2="{edge["y2"]}" '
            f'stroke="#999" stroke-width="0.8" stroke-dasharray="4,3"/>')

    # Dimension labels
    for key, label_key in [('length_label', 'length_label_pos'),
                           ('width_label', 'width_label_pos'),
                           ('height_label', 'height_label_pos')]:
        label = rd.get(key, '')
        pos = rd.get(label_key, {})
        if label and pos:
            parts.append(
                f'<text x="{pos["x"]}" y="{pos["y"]}" '
                f'font-size="12" text-anchor="middle">{label}</text>')

    parts.append('</svg>')
    return '\n'.join(parts)


def _render_svg_inline(pdf, x, y, svg_html, max_width, max_height):
    """Render an SVG figure into any FPDF-based PDF.

    Strips <text> elements (unsupported by fpdf2), renders shapes,
    then re-draws text labels using PDF text methods.

    Returns height consumed (mm).
    """
    # Parse viewBox (min-x, min-y, width, height)
    vb_min_x, vb_min_y = 0.0, 0.0
    vb_match = re.search(r'viewBox="([^"]*)"', svg_html)
    if vb_match:
        parts = vb_match.group(1).split()
        vb_min_x, vb_min_y = float(parts[0]), float(parts[1])
        vb_w, vb_h = float(parts[2]), float(parts[3])
    else:
        w_match = re.search(r'\bwidth="(\d+)"', svg_html)
        h_match = re.search(r'\bheight="(\d+)"', svg_html)
        vb_w = float(w_match.group(1)) if w_match else 200
        vb_h = float(h_match.group(1)) if h_match else 200

    # Calculate render size preserving aspect ratio
    aspect = vb_h / vb_w if vb_w else 1
    render_w = max_width
    render_h = render_w * aspect
    if render_h > max_height:
        render_h = max_height
        render_w = render_h / aspect
    scale = render_w / vb_w

    # Extract and strip text elements. Parse the transform attribute too —
    # SVG y-axis labels typically use rotate(-90, cx, cy) so the text reads
    # bottom-to-top. The earlier renderer ignored transform and drew them
    # horizontally, which caused y-axis labels like "battery level (%)" to
    # land sideways across the chart.
    text_elems = re.findall(r'<text\s+([^>]*)>([^<]*)</text>', svg_html)
    parsed_texts = []
    rotate_re = re.compile(r'rotate\s*\(\s*(-?[\d.]+)(?:\s*[,\s]\s*(-?[\d.]+)\s*[,\s]\s*(-?[\d.]+))?\s*\)')
    for attrs_str, content in text_elems:
        attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', attrs_str))
        rotate_angle = 0.0
        rotate_cx = None
        rotate_cy = None
        tf = attrs.get('transform', '')
        if tf:
            m = rotate_re.search(tf)
            if m:
                rotate_angle = float(m.group(1))
                if m.group(2) is not None:
                    rotate_cx = float(m.group(2))
                    rotate_cy = float(m.group(3))
        parsed_texts.append({
            'x': float(attrs.get('x', 0)),
            'y': float(attrs.get('y', 0)),
            'text': content,
            'font_size': float(attrs.get('font-size', 12)),
            'anchor': attrs.get('text-anchor', 'start'),
            'bold': 'bold' in attrs.get('font-weight', ''),
            'rotate': rotate_angle,
            'rotate_cx': rotate_cx,
            'rotate_cy': rotate_cy,
        })

    svg_clean = re.sub(r'<text[^>]*>[^<]*</text>', '', svg_html)

    # Render SVG shapes
    pdf.image(BytesIO(svg_clean.encode('utf-8')), x=x, y=y, w=render_w)

    # Re-draw text labels (account for viewBox origin offset)
    for t in parsed_texts:
        px = x + (t['x'] - vb_min_x) * scale
        py = y + (t['y'] - vb_min_y) * scale
        fs = max(5, min(t['font_size'] * scale, 24))
        pdf.set_font("Helvetica", "B" if t['bold'] else "", fs)
        tw = pdf.get_string_width(t['text'])
        if t['anchor'] == 'middle':
            px -= tw / 2
        elif t['anchor'] == 'end':
            px -= tw

        if t['rotate']:
            # Pivot point for the rotation, in PDF coordinates.
            if t['rotate_cx'] is not None:
                rcx = x + (t['rotate_cx'] - vb_min_x) * scale
                rcy = y + (t['rotate_cy'] - vb_min_y) * scale
            else:
                rcx, rcy = px, py
            with pdf.rotation(angle=-t['rotate'], x=rcx, y=rcy):
                pdf.text(px, py, t['text'])
        else:
            pdf.text(px, py, t['text'])

    return render_h


def _write_math_line(pdf, text, x, y, font_size, line_h, max_w, ff="Helvetica",
                     font_style=""):
    """Write a line of text with stacked fractions and superscript exponents.

    Works with any FPDF-based PDF instance (not just MathPDF).
    Returns (new_x, new_y) after rendering, or None if no math was found
    (caller should fall back to multi_cell).
    """
    has_frac = bool(FRAC_RE.search(text))
    has_exp = '^' in text

    if not has_frac and not has_exp:
        return None  # Caller should use regular multi_cell

    segments = MathPDF._parse_fractions(text)
    frac_lh = line_h * 1.8 if has_frac else line_h
    y_center = y + frac_lh * 0.42
    cur_x = x

    for seg in segments:
        if seg[0] == 'text':
            piece = seg[1]
            if '^' in piece:
                # Handle exponents
                parts = EXPONENT_RE.split(piece)
                for i, part in enumerate(parts):
                    if not part:
                        continue
                    if i % 2 == 0:
                        pdf.set_font(ff, font_style, font_size)
                        w = pdf.get_string_width(part)
                        text_y = y + (frac_lh - line_h) / 2 if has_frac else y
                        pdf.set_xy(cur_x, text_y)
                        pdf.cell(w, line_h, part)
                        cur_x += w
                    else:
                        exp_fs = font_size * 0.65
                        pdf.set_font(ff, font_style, exp_fs)
                        w = pdf.get_string_width(part)
                        text_y = y + (frac_lh - line_h) / 2 if has_frac else y
                        pdf.set_xy(cur_x, text_y - 1.2)
                        pdf.cell(w, line_h, part)
                        cur_x += w
            else:
                pdf.set_font(ff, font_style, font_size)
                w = pdf.get_string_width(piece)
                if cur_x + w > x + max_w and cur_x > x + 5:
                    # Line wrap
                    cur_x = x
                    y += frac_lh
                    y_center = y + frac_lh * 0.42
                text_y = y + (frac_lh - line_h) / 2 if has_frac else y
                pdf.set_xy(cur_x, text_y)
                pdf.cell(w, line_h, piece)
                cur_x += w

        elif seg[0] == 'fraction':
            # Add spacing before fraction when next to parentheses
            cur_x += 0.8
            frac_fs = font_size * 0.78
            pdf.set_font(ff, "", frac_fs)
            num_str, den_str = str(seg[1]), str(seg[2])
            num_w = pdf.get_string_width(num_str)
            den_w = pdf.get_string_width(den_str)
            content_w = max(num_w, den_w)
            side_pad = 0.5
            frac_w = content_w + 2 * side_pad
            cell_h = frac_fs * 0.4

            # Bar
            pdf.set_draw_color(0, 0, 0)
            pdf.set_line_width(0.25)
            pdf.line(cur_x + side_pad, y_center,
                     cur_x + frac_w - side_pad, y_center)
            # Numerator
            pdf.set_xy(cur_x, y_center - 0.3 - cell_h)
            pdf.cell(frac_w, cell_h, num_str, align="C")
            # Denominator
            pdf.set_xy(cur_x, y_center + 0.3 + 0.2)
            pdf.cell(frac_w, cell_h, den_str, align="C")
            cur_x += frac_w + 0.8

        elif seg[0] == 'mixed':
            # Add spacing before mixed number when next to parentheses
            cur_x += 0.8
            # Whole number
            pdf.set_font(ff, font_style, font_size)
            ws = seg[1]
            ww = pdf.get_string_width(ws)
            text_y = y + (frac_lh - line_h) / 2
            pdf.set_xy(cur_x, text_y)
            pdf.cell(ww, line_h, ws)
            cur_x += ww + 1.5
            # Fraction part
            frac_fs = font_size * 0.78
            pdf.set_font(ff, "", frac_fs)
            num_str, den_str = str(seg[2]), str(seg[3])
            num_w = pdf.get_string_width(num_str)
            den_w = pdf.get_string_width(den_str)
            content_w = max(num_w, den_w)
            side_pad = 0.5
            frac_w = content_w + 2 * side_pad
            cell_h = frac_fs * 0.4

            pdf.set_draw_color(0, 0, 0)
            pdf.set_line_width(0.25)
            pdf.line(cur_x + side_pad, y_center,
                     cur_x + frac_w - side_pad, y_center)
            pdf.set_xy(cur_x, y_center - 0.3 - cell_h)
            pdf.cell(frac_w, cell_h, num_str, align="C")
            pdf.set_xy(cur_x, y_center + 0.3 + 0.2)
            pdf.cell(frac_w, cell_h, den_str, align="C")
            cur_x += frac_w + 0.8

    pdf.set_font(ff, font_style, font_size)
    return (cur_x, y + frac_lh)


def generate_exit_ticket_pdf(question, output_path, standard_code="",
                              standard_text="", include_answer_key=True):
    """Generate a PDF with one question in 4 identical quadrants.

    Each quadrant has: header, question, name line, dashed cut lines.
    Second page: answer key.
    """
    # Build exit ticket PDF
    pdf = ExitTicketPDF(standard_code=standard_code, standard_text=standard_text)
    pdf.add_page()

    page_w = pdf.w  # 210 mm (A4) or letter
    page_h = pdf.h  # 297 mm
    mid_x = page_w / 2
    mid_y = page_h / 2

    # Draw dashed cut lines (yellow)
    pdf.set_draw_color(*SB_YELLOW)
    pdf.set_line_width(0.5)
    dash_len = 3
    gap_len = 3

    # Vertical dashed line
    y = 0
    while y < page_h:
        y_end = min(y + dash_len, page_h)
        pdf.line(mid_x, y, mid_x, y_end)
        y += dash_len + gap_len

    # Horizontal dashed line
    x = 0
    while x < page_w:
        x_end = min(x + dash_len, page_w)
        pdf.line(x, mid_y, x_end, mid_y)
        x += dash_len + gap_len

    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)

    # Render question in each quadrant
    quadrants = [
        (8, 8),                     # top-left
        (mid_x + 5, 8),            # top-right
        (8, mid_y + 5),            # bottom-left
        (mid_x + 5, mid_y + 5),    # bottom-right
    ]

    quad_w = mid_x - 13  # available width per quadrant

    # ── Estimate content height to decide font scaling ──
    stem_raw = MathPDF._clean_text(question.stem_text).replace("[FIGURE]", "").strip()
    rd_pre = getattr(question, 'render_data', None) or {}
    _est_lines = sum(1 + max(0, len(ln) // 45) for ln in stem_raw.split("\n") if ln.strip())
    _est_blank = stem_raw.count("\n\n")
    _est_h = (_est_lines * 4) + (_est_blank * 2)
    _est_h += 23  # banner + question number area
    if question.choices:
        _est_h += len(question.choices) * 5
    if question.parts:
        _est_h += len(question.parts) * 5
    if rd_pre.get('type') == 'data_table' or rd_pre.get('tables'):
        _est_h += 30
    elif rd_pre.get('svg_html') or rd_pre.get('type') in ('svg_html', 'coordinate_grid'):
        _est_h += 40
    if not question.choices and not question.parts:
        _est_h += 8  # answer line

    _avail_h = mid_y - 25
    et_compact = _est_h > _avail_h  # use smaller fonts if content overflows
    et_fs = 7 if et_compact else 8       # stem text font size
    et_fs_b = 8 if et_compact else 9     # question number font size
    et_lh = 3.5 if et_compact else 4     # line height
    et_blank_h = 1.5 if et_compact else 2  # blank line height

    for qx, qy in quadrants:
        # Rounded yellow banner header
        banner_h = 14
        _draw_sb_header(pdf, qx, qy, quad_w, banner_h,
                        title="Plug N Play Exit Ticket",
                        standard_code=standard_code,
                        r=2, font_title=7, font_name=6)

        # Render question text below banner
        q_start_y = qy + banner_h + 1
        pdf.set_font(pdf.ff, "B", et_fs_b)
        pdf.set_xy(qx, q_start_y)
        pdf.cell(5, et_lh, "1.", new_x="RIGHT", new_y="TOP")

        q_text_x = qx + 6
        pdf.set_font(pdf.ff, "", et_fs)
        pdf.set_xy(q_text_x, q_start_y)

        # Clean and write stem text
        stem = MathPDF._clean_text(question.stem_text)
        # Remove [FIGURE] marker for exit ticket (space constraints)
        stem = stem.replace("[FIGURE]", "").strip()

        # Split by lines and render
        max_q_height = (mid_y - 25) if qy < mid_y else (page_h - qy - 20)
        lines = stem.split("\n")
        cur_y = q_start_y

        choices_written_et = False
        for line in lines:
            line = line.strip()
            if not line:
                cur_y += et_blank_h
                continue
            if cur_y > qy + max_q_height:
                break

            # Insert MC choices before Part B (so they appear under Part A)
            if line.startswith("Part B") and question.choices and not choices_written_et:
                cur_y += 1
                labels_et = ['A', 'B', 'C', 'D', 'E', 'F']
                for idx_et, choice_et in enumerate(question.choices):
                    if cur_y > qy + max_q_height:
                        break
                    pdf.set_font(pdf.ff, "B", et_fs)
                    pdf.set_xy(q_text_x + 2, cur_y)
                    lbl_et = labels_et[idx_et] if idx_et < len(labels_et) else str(idx_et + 1)
                    c_text_et = MathPDF._clean_text(choice_et.text)
                    pdf.cell(5, et_lh, f"{lbl_et}.", new_x="RIGHT", new_y="TOP")
                    choice_x_et = q_text_x + 7
                    result_et = _write_math_line(pdf, c_text_et, choice_x_et, cur_y, et_fs, et_lh,
                                                  quad_w - 16, ff=pdf.ff)
                    if result_et is not None:
                        _, cur_y = result_et
                    else:
                        pdf.set_font(pdf.ff, "", et_fs)
                        pdf.set_xy(choice_x_et, cur_y)
                        pdf.multi_cell(quad_w - 16, et_lh, c_text_et, new_x="LMARGIN", new_y="NEXT")
                        cur_y = pdf.get_y()
                choices_written_et = True
                cur_y += 1

            # Bold rendering for Part A / Part B labels
            if line.startswith("Part A") or line.startswith("Part B"):
                pdf.set_font(pdf.ff, "B", et_fs)
                pdf.set_xy(q_text_x, cur_y)
                pdf.multi_cell(quad_w - 8, et_lh, line, new_x="LMARGIN", new_y="NEXT")
                cur_y = pdf.get_y()
                pdf.set_font(pdf.ff, "", et_fs)
                continue

            # Try stacked fraction rendering
            result = _write_math_line(pdf, line, q_text_x, cur_y, et_fs, et_lh,
                                      quad_w - 8, ff=pdf.ff)
            if result is not None:
                _, cur_y = result
            else:
                pdf.set_xy(q_text_x, cur_y)
                pdf.multi_cell(quad_w - 8, et_lh, line, new_x="LMARGIN", new_y="NEXT")
                cur_y = pdf.get_y()

        # Render figure from render_data if present
        rd = getattr(question, 'render_data', None) or {}
        fig_w = quad_w - 10  # available width for figures in quadrant
        remaining_h = qy + max_q_height - cur_y - 10

        if rd.get('type') == 'data_table' and remaining_h > 15:
            cur_y += 1
            h = pdf._draw_data_table(
                q_text_x, cur_y,
                headers=rd['headers'],
                rows=rd['rows'],
                orientation=rd.get('orientation', 'vertical'),
                compact=True,
            )
            cur_y += h
        elif rd.get('tables') and remaining_h > 15:
            cur_y += 1
            table_list = rd['tables']
            gap_t = 3
            t_x = q_text_x
            max_h = 0
            tbl_fs = 7  # must match _draw_data_table compact=True
            tbl_pad = 1.5
            tbl_min_col = 10
            label_h = 3
            for idx_t, tbl in enumerate(table_list):
                # Table label
                label_t = tbl.get('title', f"Table {idx_t + 1}")
                pdf.set_font(pdf.ff, "B", 6)
                pdf.set_xy(t_x, cur_y)
                pdf.cell(0, label_h, label_t, new_x="LEFT", new_y="TOP")
                h = pdf._draw_data_table(
                    t_x, cur_y + label_h,
                    headers=tbl['headers'],
                    rows=tbl['rows'],
                    orientation=tbl.get('orientation', 'vertical'),
                    compact=True,
                )
                # Advance t_x by actual drawn table width (same logic as _draw_data_table compact)
                n_cols = len(tbl['headers'])
                tbl_w = 0
                for ci in range(n_cols):
                    pdf.set_font(pdf.ff, "B", tbl_fs)
                    w = pdf.get_string_width(tbl['headers'][ci]) + 2 * tbl_pad
                    pdf.set_font(pdf.ff, "", tbl_fs)
                    for row in tbl['rows']:
                        if ci < len(row):
                            w = max(w, pdf.get_string_width(str(row[ci])) + 2 * tbl_pad)
                    tbl_w += max(w, tbl_min_col)
                t_x += tbl_w + gap_t
                max_h = max(max_h, h + label_h)
            cur_y += max_h
        elif rd.get('type') == 'number_line' and remaining_h > 15:
            nl_w = min(fig_w, 65)
            h = pdf._draw_number_line(
                q_text_x, cur_y,
                value=rd['value'],
                circle_type=rd['circle_type'],
                direction=rd['direction'],
                width=nl_w,
                blank=rd.get('blank', False),
            )
            cur_y += h + 1
        elif rd.get('type') == 'number_line_point' and remaining_h > 15:
            h = pdf._draw_number_line_point(
                q_text_x, cur_y,
                ticks=rd['ticks'],
                point_value=rd.get('point_value'),
                point_label=rd.get('point_label', 'P'),
                points=rd.get('points'),
                width=min(fig_w, 65),
            )
            cur_y += h + 1
        elif rd.get('type') == 'double_number_line' and remaining_h > 20:
            h = pdf._draw_double_number_line(
                q_text_x, cur_y,
                top_ticks=rd['top_ticks'],
                bottom_ticks=rd['bottom_ticks'],
                top_label=rd.get('top_label', ''),
                bottom_label=rd.get('bottom_label', ''),
                width=min(fig_w, 65),
            )
            cur_y += h + 1
        elif rd.get('type') == 'coordinate_grid' and remaining_h > 25:
            grid_sz = min(fig_w - 5, 35)
            h = pdf._draw_coordinate_grid(
                q_text_x, cur_y,
                x_range=rd['x_range'],
                y_range=rd['y_range'],
                points=rd.get('points', []),
                lines=rd.get('lines', []),
                grid_size=grid_sz,
                label_step=rd.get('label_step'),
                hide_labels=rd.get('hide_labels', False), x_label=rd.get('x_label'), y_label=rd.get('y_label'),
            )
            cur_y += h
        elif rd.get('type') == 'rectangle_diagram' and remaining_h > 25:
            h = pdf._draw_rectangle_diagram(
                q_text_x, cur_y,
                side=rd['side'], cut_l=rd['cut_l'], cut_w=rd['cut_w']
            )
            cur_y += h
        elif rd.get('type') == 'composite_shape' and remaining_h > 25:
            svg_str = _composite_shape_to_svg(rd)
            h = pdf._render_svg_figure(
                q_text_x, cur_y, svg_str,
                max_width=min(fig_w, 60), max_height=min(remaining_h - 5, 45),
            )
            pdf.set_font(pdf.ff, "", et_fs)
            cur_y += h + 1
        elif rd.get('type') == 'polygon_angles' and remaining_h > 25:
            svg_str = _polygon_angles_to_svg(rd)
            h = pdf._render_svg_figure(
                q_text_x, cur_y, svg_str,
                max_width=min(fig_w, 60), max_height=min(remaining_h - 5, 45),
            )
            pdf.set_font(pdf.ff, "", et_fs)
            cur_y += h + 1
        elif rd.get('type') == 'rectangular_prism' and remaining_h > 25:
            svg_str = _rectangular_prism_to_svg(rd)
            h = pdf._render_svg_figure(
                q_text_x, cur_y, svg_str,
                max_width=min(fig_w, 60), max_height=min(remaining_h - 5, 45),
            )
            pdf.set_font(pdf.ff, "", et_fs)
            cur_y += h + 1
        elif rd.get('svg_html') and remaining_h > 20:
            fig_max_h = min(40, remaining_h - 10)
            if fig_max_h > 15:
                h = pdf._render_svg_figure(
                    q_text_x, cur_y, rd['svg_html'],
                    max_width=fig_w, max_height=fig_max_h,
                )
                pdf.set_font(pdf.ff, "", et_fs)
                cur_y += h + 1

        # Write MC choices if present (and not already written before Part B)
        if question.choices and not choices_written_et:
            cur_y += 1
            labels = ['A', 'B', 'C', 'D', 'E', 'F']
            for idx, choice in enumerate(question.choices):
                if cur_y > qy + max_q_height:
                    break
                pdf.set_font(pdf.ff, "B", et_fs)
                pdf.set_xy(q_text_x + 2, cur_y)
                lbl = labels[idx] if idx < len(labels) else str(idx + 1)
                c_text = MathPDF._clean_text(choice.text)
                pdf.cell(5, et_lh, f"{lbl}.", new_x="RIGHT", new_y="TOP")
                choice_x = q_text_x + 7
                result = _write_math_line(pdf, c_text, choice_x, cur_y, et_fs, et_lh,
                                          quad_w - 16, ff=pdf.ff)
                if result is not None:
                    _, cur_y = result
                else:
                    pdf.set_font(pdf.ff, "", et_fs)
                    pdf.set_xy(choice_x, cur_y)
                    pdf.multi_cell(quad_w - 16, et_lh, c_text, new_x="LMARGIN", new_y="NEXT")
                    cur_y = pdf.get_y()

        # Answer line for NR/EQ types
        if not question.choices and not question.parts:
            cur_y += 3
            if cur_y < qy + max_q_height - 5:
                pdf.set_xy(q_text_x, cur_y)
                pdf.set_font(pdf.ff, "", et_fs)
                pdf.cell(quad_w - 10, et_lh, "Answer: ___________________",
                         new_x="LMARGIN", new_y="NEXT")

        # Motivational quote at the bottom of each quadrant
        quote_y = qy + (mid_y - 8) - 5 if qy < mid_y else (page_h - 8)
        quote = _STRUGGLE_QUOTES[hash(standard_code + str(qx + qy)) % len(_STRUGGLE_QUOTES)]
        pdf.set_font(pdf.ff, "I", 6)
        pdf.set_text_color(*SB_BROWN)
        pdf.set_xy(qx, quote_y)
        pdf.cell(quad_w, 3, f'"{quote}"', align="C")
        pdf.set_text_color(0, 0, 0)

    # Page 2: Answer key with yellow branding
    if include_answer_key:
        pdf.add_page()

        # Rounded yellow banner header
        _draw_sb_header(pdf, PAGE_MARGIN, 5, pdf.w - 2 * PAGE_MARGIN, 16,
                        title="Plug N Play Answer Key",
                        standard_code=standard_code,
                        r=3, include_name=False, font_title=12)
        pdf.set_xy(PAGE_MARGIN, 24)

        pdf.set_font(pdf.ff, "B", FONT_SIZE_BODY)
        pdf.set_x(PAGE_MARGIN)
        answer = MathPDF._clean_text(question.answer_text)
        pdf.cell(10, LINE_HEIGHT, "1.", new_x="RIGHT", new_y="TOP")
        pdf.set_font(pdf.ff, "", FONT_SIZE_BODY)
        pdf.multi_cell(pdf.w - PAGE_MARGIN * 2 - 10, LINE_HEIGHT,
                       f"Answer: {answer}", new_x="LMARGIN", new_y="NEXT")

        if question.worked_solution:
            pdf.set_x(PAGE_MARGIN + 10)
            pdf.set_font(pdf.ff, "", FONT_SIZE_SMALL)
            solution = MathPDF._clean_text(question.worked_solution)
            for sol_line in solution.split("\n"):
                pdf.set_x(PAGE_MARGIN + 10)
                pdf.cell(0, LINE_HEIGHT, sol_line.strip(), new_x="LMARGIN", new_y="NEXT")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    pdf.output(output_path)
    return output_path


def _write_column_question(pdf, question, num, col_x, col_w, start_y,
                           font_scale=1.0):
    """Render a question within a constrained column.

    font_scale: 0.5-1.0 multiplier applied to font sizes, line heights,
                and figure dimensions so content shrinks to fit the page.
    Returns the y position after the question is rendered.
    """
    ff = pdf.ff
    fs_body = max(6, 10 * font_scale)
    fs_small = max(5, 9 * font_scale)
    line_h = max(3, 5 * font_scale)
    text_w = col_w - 8  # indent from number

    cur_y = start_y

    # Question number
    pdf.set_font(ff, "B", fs_body)
    pdf.set_xy(col_x, cur_y)
    pdf.cell(5, line_h, f"{num}.", new_x="RIGHT", new_y="TOP")
    q_text_x = col_x + 6

    # Stem text
    pdf.set_font(ff, "", fs_body)
    stem = MathPDF._clean_text(question.stem_text)
    stem = stem.replace("[FIGURE]", "").strip()

    for line in stem.split("\n"):
        line = line.strip()
        if not line:
            cur_y += 2
            continue

        # Try rendering with stacked fractions/exponents
        result = _write_math_line(pdf, line, q_text_x, cur_y, fs_body,
                                  line_h, text_w, ff=ff)
        if result is not None:
            _, cur_y = result
        else:
            pdf.set_xy(q_text_x, cur_y)
            pdf.multi_cell(text_w, line_h, line, new_x="LMARGIN", new_y="NEXT")
            cur_y = pdf.get_y()

    # Render_data diagrams — use MathPDF drawing methods scaled to column width
    rd = getattr(question, 'render_data', None) or {}
    fig_w = text_w - 2  # available width for figures

    if rd.get('type') == 'data_table':
        cur_y += 1
        h = pdf._draw_data_table(
            q_text_x, cur_y,
            headers=rd['headers'],
            rows=rd['rows'],
            orientation=rd.get('orientation', 'vertical'),
            max_width=text_w
        )
        cur_y += h
    elif rd.get('type') == 'number_line':
        cur_y += 1
        h = pdf._draw_number_line(
            q_text_x, cur_y,
            value=rd['value'],
            circle_type=rd['circle_type'],
            direction=rd['direction'],
            width=fig_w,
            blank=rd.get('blank', False),
        )
        cur_y += h
    elif rd.get('type') == 'number_line_point':
        cur_y += 1
        h = pdf._draw_number_line_point(
            q_text_x, cur_y,
            ticks=rd['ticks'],
            point_value=rd.get('point_value'),
            point_label=rd.get('point_label', 'P'),
            points=rd.get('points'),
            width=fig_w,
        )
        cur_y += h
    elif rd.get('type') == 'double_number_line':
        cur_y += 1
        h = pdf._draw_double_number_line(
            q_text_x, cur_y,
            top_ticks=rd['top_ticks'],
            bottom_ticks=rd['bottom_ticks'],
            top_label=rd.get('top_label', ''),
            bottom_label=rd.get('bottom_label', ''),
            width=fig_w,
        )
        cur_y += h
    elif rd.get('type') == 'rectangle_diagram':
        cur_y += 1
        h = pdf._draw_rectangle_diagram(
            q_text_x, cur_y,
            side=rd['side'], cut_l=rd['cut_l'], cut_w=rd['cut_w']
        )
        cur_y += h
    elif rd.get('type') == 'coordinate_grid':
        cur_y += 1
        grid_sz = min(fig_w - 5, 50 * font_scale)  # fit within column
        h = pdf._draw_coordinate_grid(
            q_text_x, cur_y,
            x_range=rd['x_range'],
            y_range=rd['y_range'],
            points=rd.get('points', []),
            lines=rd.get('lines', []),
            grid_size=grid_sz,
            label_step=rd.get('label_step'),
            hide_labels=rd.get('hide_labels', False), x_label=rd.get('x_label'), y_label=rd.get('y_label'),
        )
        cur_y += h
    elif rd.get('tables'):
        # Multiple tables — constrain each to fit within the column
        cur_y += 1
        table_list = rd['tables']
        gap_t = 3
        n_tables = len(table_list)

        # Each table gets an equal share of the available width
        per_table_w = (text_w - gap_t * max(0, n_tables - 1)) / max(n_tables, 1)

        t_x = q_text_x
        max_h = 0
        for idx_t, tbl in enumerate(table_list):
            label_t = tbl.get('title', f"Table {idx_t + 1}")
            pdf.set_font(ff, "B", fs_small)
            pdf.set_xy(t_x, cur_y)
            pdf.cell(per_table_w, line_h, label_t, new_x="LEFT", new_y="TOP")
            h = pdf._draw_data_table(
                t_x, cur_y + line_h,
                headers=tbl['headers'],
                rows=tbl['rows'],
                orientation=tbl.get('orientation', 'vertical'),
                max_width=per_table_w
            )
            t_x += per_table_w + gap_t
            max_h = max(max_h, h + line_h)
        cur_y += max_h
    elif rd.get('type') == 'composite_shape':
        cur_y += 1
        svg_str = _composite_shape_to_svg(rd)
        fig_max_h = max(25, 50 * font_scale)
        h = pdf._render_svg_figure(
            q_text_x, cur_y, svg_str,
            max_width=fig_w, max_height=fig_max_h,
        )
        cur_y += h + 1
    elif rd.get('type') == 'polygon_angles':
        cur_y += 1
        svg_str = _polygon_angles_to_svg(rd)
        fig_max_h = max(25, 50 * font_scale)
        h = pdf._render_svg_figure(
            q_text_x, cur_y, svg_str,
            max_width=fig_w, max_height=fig_max_h,
        )
        cur_y += h + 1
    elif rd.get('type') == 'rectangular_prism':
        cur_y += 1
        svg_str = _rectangular_prism_to_svg(rd)
        fig_max_h = max(25, 50 * font_scale)
        h = pdf._render_svg_figure(
            q_text_x, cur_y, svg_str,
            max_width=fig_w, max_height=fig_max_h,
        )
        cur_y += h + 1
    elif rd.get('svg_html'):
        # Render SVG geometry figures (triangles, circles, 3D shapes, etc.)
        cur_y += 1
        fig_max_h = max(30, 70 * font_scale)
        h = pdf._render_svg_figure(
            q_text_x, cur_y, rd['svg_html'],
            max_width=fig_w, max_height=fig_max_h,
        )
        cur_y += h + 1

    # Reset font after any figure rendering
    if rd:
        pdf.set_font(ff, "", fs_body)

    # MC choices
    if question.choices:
        cur_y += 1
        labels = ['A', 'B', 'C', 'D', 'E', 'F']
        for idx, choice in enumerate(question.choices):
            pdf.set_font(ff, "B", fs_small)
            pdf.set_xy(q_text_x + 1, cur_y)
            lbl = labels[idx] if idx < len(labels) else str(idx + 1)
            c_text = MathPDF._clean_text(choice.text)
            pdf.cell(4, line_h, f"{lbl}.", new_x="RIGHT", new_y="TOP")
            lbl_end_x = q_text_x + 5
            # Try stacked fraction rendering
            result = _write_math_line(pdf, c_text, lbl_end_x, cur_y,
                                      fs_small, line_h, text_w - 6, ff=ff)
            if result is not None:
                _, cur_y = result
            else:
                pdf.set_font(ff, "", fs_small)
                pdf.set_xy(lbl_end_x, cur_y)
                pdf.multi_cell(text_w - 6, line_h, c_text, new_x="LMARGIN", new_y="NEXT")
                cur_y = pdf.get_y()

    # Answer line for NR/EQ types
    from engine.models import ItemType
    if question.item_type in (ItemType.NR, ItemType.EQ) and not question.parts:
        cur_y += 2
        pdf.set_font(ff, "", fs_small)
        pdf.set_xy(q_text_x, cur_y)
        pdf.cell(text_w, line_h, "Answer: ______________", new_x="LMARGIN", new_y="NEXT")
        cur_y = pdf.get_y()

    # Multi-part questions
    if question.parts:
        for part in question.parts:
            cur_y += 1
            pdf.set_font(ff, "B", fs_small)
            pdf.set_xy(q_text_x, cur_y)
            part_label = part.label + ":" if part.label else ""
            prompt = MathPDF._clean_text(part.prompt) if part.prompt else ""
            lbl_w = pdf.get_string_width(part_label) + 1
            pdf.cell(lbl_w, line_h, part_label, new_x="RIGHT", new_y="TOP")
            prompt_x = q_text_x + lbl_w
            result = _write_math_line(pdf, prompt, prompt_x, cur_y,
                                      fs_small, line_h,
                                      text_w - lbl_w - 2, ff=ff)
            if result is not None:
                _, cur_y = result
            else:
                pdf.set_font(ff, "", fs_small)
                pdf.set_xy(prompt_x, cur_y)
                pdf.multi_cell(text_w - lbl_w - 2, line_h,
                               prompt, new_x="LMARGIN", new_y="NEXT")
                cur_y = pdf.get_y()
            # Answer line for each part
            cur_y += 1
            pdf.set_xy(q_text_x + 2, cur_y)
            pdf.cell(text_w - 4, line_h, "_______________", new_x="LMARGIN", new_y="NEXT")
            cur_y = pdf.get_y()

    # ER answer box
    if question.item_type == ItemType.ER and not question.parts:
        cur_y += 2
        pdf.set_draw_color(0, 0, 0)
        box_h = max(10, 20 * font_scale)
        pdf.rect(q_text_x, cur_y, text_w, box_h)
        cur_y += box_h + 1

    return cur_y


def generate_mms_pdf(questions_by_tier, output_path, standard_code="",
                     standard_text="", mms_axis="difficulty",
                     include_answer_key=True):
    """Generate Mild/Medium/Spicy PDF: 3 side-by-side columns (portrait).

    Layout: Mild (left) | Medium (center) | Spicy (right)
    questions_by_tier: list of (tier_name, [questions]) tuples
    """
    tier_labels = {
        'easy': ('MILD', '*'),
        'medium': ('MEDIUM', '* *'),
        'difficult': ('SPICY', '* * *'),
        'below': ('MILD', '*'),
        'approaching': ('MEDIUM', '* *'),
        'at': ('SPICY', '* * *'),
        'above': ('SPICY', '* * *'),
    }

    # For proficiency axis, use positional labels
    if mms_axis == 'proficiency':
        pos_labels = [('MILD', '*'), ('MEDIUM', '* *'), ('SPICY', '* * *')]
    else:
        pos_labels = None

    # Build the PDF in landscape for wider columns (MathPDF for drawing methods)
    pdf = MathPDF(orientation='L')
    pdf.set_auto_page_break(auto=False)
    # Suppress default header/footer — we draw our own
    pdf.header = lambda: None
    pdf.footer = lambda: None
    ff = pdf.ff
    pdf.add_page()

    # --- Rounded yellow branded header ---
    header_h = 20
    _draw_sb_header(pdf, PAGE_MARGIN, 3, pdf.w - 2 * PAGE_MARGIN, header_h,
                    title="Plug N Play - Mild / Medium / Spicy",
                    standard_code=standard_code,
                    r=3, include_name=True, font_title=12, font_name=9)

    header_bottom = 3 + header_h + 3

    # --- Column geometry ---
    usable_w = pdf.w - 2 * PAGE_MARGIN  # ~180mm on A4
    gutter = 3  # mm between columns
    col_w = (usable_w - 2 * gutter) / 3  # ~58mm each
    col_xs = [
        PAGE_MARGIN,
        PAGE_MARGIN + col_w + gutter,
        PAGE_MARGIN + 2 * (col_w + gutter),
    ]

    # Vertical dashed divider positions
    div_x1 = PAGE_MARGIN + col_w + gutter / 2
    div_x2 = PAGE_MARGIN + 2 * col_w + 1.5 * gutter

    page_bottom = pdf.h - 15  # leave room for footer quote

    # Draw vertical dashed dividers (yellow)
    def draw_dividers():
        pdf.set_draw_color(*SB_YELLOW)
        pdf.set_line_width(0.5)
        for div_x in (div_x1, div_x2):
            y = header_bottom
            while y < page_bottom:
                y2 = min(y + 3, page_bottom)
                pdf.line(div_x, y, div_x, y2)
                y += 5
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.3)

    draw_dividers()

    # --- Measurement pass: compute column heights at default scale ---
    available_h = page_bottom - (header_bottom + 7)
    col_heights = []
    measure_pdf = MathPDF(orientation='L')
    measure_pdf.set_auto_page_break(auto=False)
    measure_pdf.header = lambda: None
    measure_pdf.footer = lambda: None
    measure_pdf.add_page()
    m_qnum = 1
    for tier_idx, (tier_name, tier_questions) in enumerate(questions_by_tier):
        if tier_idx >= 3:
            break
        if not tier_questions:
            col_heights.append(0)
            continue
        m_y = header_bottom + 7
        for q in tier_questions:
            m_y = _write_column_question(measure_pdf, q, m_qnum,
                                         col_xs[min(tier_idx, 2)],
                                         col_w, m_y)
            m_y += 4
            m_qnum += 1
        col_heights.append(m_y - (header_bottom + 7))
    del measure_pdf

    max_content_h = max(col_heights) if col_heights else 1
    font_scale = min(1.0, available_h / max_content_h) if max_content_h > 0 else 1.0
    font_scale = max(0.5, font_scale)  # never shrink below 50%
    gap = 4 * font_scale  # inter-question gap scales too

    # --- Render each column ---
    question_num = 1

    for tier_idx, (tier_name, tier_questions) in enumerate(questions_by_tier):
        if tier_idx >= 3:
            break
        if not tier_questions:
            continue

        col_x = col_xs[tier_idx] if tier_idx < len(col_xs) else col_xs[-1]

        # Tier label
        if pos_labels:
            label, pips = pos_labels[tier_idx] if tier_idx < len(pos_labels) else ('', '')
        else:
            label, pips = tier_labels.get(tier_name, (tier_name.upper(), ''))

        lbl_fs = max(7, 10 * font_scale)
        pdf.set_font(ff, "B", lbl_fs)
        pdf.set_xy(col_x, header_bottom)
        pdf.cell(col_w, 6, f"{label}  {pips}", new_x="LMARGIN", new_y="NEXT")

        cur_y = header_bottom + 7

        # Render each question in this column
        for q in tier_questions:
            cur_y = _write_column_question(pdf, q, question_num, col_x, col_w,
                                           cur_y, font_scale=font_scale)
            cur_y += gap  # gap between questions
            question_num += 1

    # --- Yellow footer bar ---
    quote = _STRUGGLE_QUOTES[hash(standard_code) % len(_STRUGGLE_QUOTES)]
    footer_y = pdf.h - SB_FOOTER_HEIGHT
    pdf.set_fill_color(*SB_YELLOW)
    pdf.rect(0, footer_y, pdf.w, SB_FOOTER_HEIGHT, style="F")
    pdf.set_draw_color(*SB_BROWN)
    pdf.set_line_width(0.4)
    pdf.line(0, footer_y, pdf.w, footer_y)
    _draw_bus_icon(pdf, PAGE_MARGIN, footer_y + 3, w=10, h=6)
    pdf.set_text_color(*SB_BROWN)
    pdf.set_font(ff, "I", 7)
    pdf.set_xy(PAGE_MARGIN + 14, footer_y + 2)
    pdf.cell(pdf.w - 2 * PAGE_MARGIN - 60, 5, f'"{quote}"')
    pdf.set_font(ff, "", 7)
    page_label = "Plug N Play  |  Mild / Medium / Spicy"
    pl_w = pdf.get_string_width(page_label)
    pdf.set_xy(pdf.w - PAGE_MARGIN - pl_w, footer_y + 2)
    pdf.cell(pl_w, 5, page_label)
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_line_width(0.3)

    # --- Answer key on page 2 (full-width, branded) ---
    if include_answer_key:
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=20)

        # Rounded yellow answer key header
        _draw_sb_header(pdf, PAGE_MARGIN, 5, pdf.w - 2 * PAGE_MARGIN, 16,
                        title="Plug N Play Answer Key",
                        standard_code=standard_code,
                        r=3, include_name=False, font_title=12)
        pdf.set_xy(PAGE_MARGIN, 24)

        question_num = 1
        for tier_name, tier_questions in questions_by_tier:
            for q in tier_questions:
                if pdf.get_y() > pdf.h - 40:
                    pdf.add_page()

                pdf.set_font(ff, "B", FONT_SIZE_BODY)
                pdf.cell(10, LINE_HEIGHT, f"{question_num}.", new_x="RIGHT", new_y="TOP")
                x_ans = pdf.get_x()
                answer = MathPDF._clean_text(q.answer_text)
                pdf.set_font(ff, "", FONT_SIZE_BODY)
                pdf.multi_cell(pdf.w - x_ans - PAGE_MARGIN, LINE_HEIGHT,
                               f"Answer: {answer}", new_x="LMARGIN", new_y="NEXT")

                if q.worked_solution:
                    pdf.set_x(x_ans)
                    pdf.set_font(ff, "", FONT_SIZE_SMALL)
                    solution = MathPDF._clean_text(q.worked_solution)
                    for sol_line in solution.split("\n"):
                        pdf.set_x(x_ans)
                        pdf.cell(0, LINE_HEIGHT - 1, sol_line.strip(),
                                 new_x="LMARGIN", new_y="NEXT")

                # Yellow divider
                pdf.ln(2)
                pdf.set_draw_color(*SB_YELLOW)
                pdf.set_line_width(0.5)
                pdf.line(PAGE_MARGIN, pdf.get_y(), pdf.w - PAGE_MARGIN, pdf.get_y())
                pdf.set_draw_color(0, 0, 0)
                pdf.set_line_width(0.3)
                pdf.ln(3)
                question_num += 1

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    pdf.output(output_path)
    return output_path


def _build_proficiency(questions, standard_code, standard_text, compact=False):
    """Build a PlugNPlayPDF (questions only, no answer key). Used by two-pass."""
    pdf = PlugNPlayPDF(
        title="Plug N Play",
        standard_code=standard_code,
        standard_text=standard_text,
    )
    pdf.alias_nb_pages()
    pdf.add_page()
    for i, q in enumerate(questions, 1):
        pdf.write_question(i, q, compact=compact)
    return pdf


def generate_proficiency_pdf(questions, output_path, standard_code="",
                              standard_text="", proficiency_level="at",
                              include_answer_key=True):
    """Generate a practice set PDF: up to 6 questions at one proficiency level."""
    # First pass: normal layout
    pdf = _build_proficiency(questions, standard_code, standard_text,
                             compact=False)

    # If it barely overflows (last page < 35% used), retry with compact spacing
    if pdf.page_no() > 1:
        last_page_pct = pdf.get_y() / pdf.h
        if last_page_pct < 0.35:
            pdf = _build_proficiency(questions, standard_code, standard_text,
                                     compact=True)

    # Answer key page -- branded sub-header
    if include_answer_key:
        pdf.add_page()
        # Rounded yellow answer key header
        _draw_sb_header(pdf, PAGE_MARGIN, 5, pdf.w - 2 * PAGE_MARGIN, 16,
                        title="Plug N Play Answer Key",
                        standard_code=standard_code,
                        r=3, include_name=False, font_title=12)
        pdf.set_xy(PAGE_MARGIN, 24)
        pdf.ln(2)

        for i, q in enumerate(questions, 1):
            if pdf.get_y() > pdf.h - 40:
                pdf.add_page()

            pdf.set_font(pdf.ff, "B", FONT_SIZE_BODY)
            pdf.cell(10, LINE_HEIGHT, f"{i}.", new_x="RIGHT", new_y="TOP")
            x_ans = pdf.get_x()
            answer = MathPDF._clean_text(q.answer_text)
            pdf.set_font(pdf.ff, "", FONT_SIZE_BODY)
            pdf.multi_cell(pdf.w - x_ans - PAGE_MARGIN, LINE_HEIGHT,
                           f"Answer: {answer}", new_x="LMARGIN", new_y="NEXT")

            if q.worked_solution:
                pdf.set_x(x_ans)
                pdf.set_font(pdf.ff, "", FONT_SIZE_SMALL)
                solution = MathPDF._clean_text(q.worked_solution)
                for sol_line in solution.split("\n"):
                    pdf.set_x(x_ans)
                    pdf.cell(0, LINE_HEIGHT - 1, sol_line.strip(),
                             new_x="LMARGIN", new_y="NEXT")

            # Yellow divider
            pdf.ln(2)
            pdf.set_draw_color(*SB_YELLOW)
            pdf.set_line_width(0.5)
            pdf.line(PAGE_MARGIN, pdf.get_y(), pdf.w - PAGE_MARGIN, pdf.get_y())
            pdf.set_draw_color(0, 0, 0)
            pdf.set_line_width(0.3)
            pdf.ln(3)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    pdf.output(output_path)
    return output_path


# ============================================================
# INTERVENTION SESSION PDFs
# ============================================================

import random as _random

# Rotation counter for varying STOP/PROMPT/PRAISE language across questions
_script_rotation = {"counter": 0}


def _generate_question_specific_misconception(question):
    """Generate a WATCH FOR / STOP / PROMPT / PRAISE script specific to
    the actual generated question, based on its wrong choices and content.

    Returns a dict with keys: description, stop, prompt, praise
    or None if we can't generate one.
    """
    stem = question.stem_text or ""
    answer = question.answer_text or ""
    solution = question.worked_solution or ""
    choices = question.choices or []

    # For MC questions, use the correct choice's text as the answer
    # (answer_text might be just the key letter like "c")
    correct_choices = [c for c in choices if c.is_correct]
    if correct_choices:
        answer = correct_choices[0].text

    # Get wrong choices
    wrong_choices = [c for c in choices if not c.is_correct]
    if not wrong_choices:
        # Non-MC question: generate from worked solution
        return _misconception_from_solution(stem, answer, solution)

    # Try to identify what error each wrong choice represents
    best = _analyze_distractor(stem, answer, solution, wrong_choices)
    if best:
        return best

    # Fallback: generic but still referencing the actual problem
    return _misconception_from_solution(stem, answer, solution)


def _analyze_distractor(stem, answer, solution, wrong_choices):
    """Analyze wrong choices to identify the specific misconception."""
    stem_lower = stem.lower()
    answer_clean = MathPDF._clean_text(answer)

    for wc in wrong_choices:
        # If distractor_rationale exists, use it directly
        if wc.distractor_rationale:
            return {
                "description": wc.distractor_rationale,
                "stop": "Let's pause here. Walk me through what you did step by step.",
                "prompt": f"{wc.distractor_rationale} Let's work through it together to find the correct answer.",
                "praise": "Great work correcting that! You identified the right approach.",
            }

    # --- Pattern matching on problem structure ---

    # Expression writing: verbal description -> expression
    if "description" in stem_lower and ("expression" in stem_lower or "write" in stem_lower):
        return _analyze_expression_writing(stem, answer_clean, wrong_choices)

    # Expression evaluation: substitute and compute
    if ("evaluate" in stem_lower or "value" in stem_lower or
            "expression" in stem_lower and "=" in solution):
        return _analyze_evaluation(stem, answer_clean, solution, wrong_choices)

    # Real-world modeling: word problem -> expression
    if ("which expression" in stem_lower or "represents" in stem_lower or
            "models" in stem_lower or "total cost" in stem_lower):
        return _analyze_word_problem(stem, answer_clean, solution, wrong_choices)

    # Equation solving
    if ("solve" in stem_lower or "solution" in stem_lower or
            "value of" in stem_lower):
        return _analyze_equation_solving(stem, answer_clean, solution, wrong_choices)

    # Equivalent expressions / properties
    if ("equivalent" in stem_lower or "simplif" in stem_lower or
            "property" in stem_lower or "factor" in stem_lower):
        return _analyze_equivalent_expr(stem, answer_clean, solution, wrong_choices)

    return None


def _analyze_expression_writing(stem, answer, wrong_choices):
    """Analyze expression-writing problems (verbal -> algebraic)."""
    stem_lower = stem.lower()
    rot = _script_rotation["counter"]
    _script_rotation["counter"] += 1

    # Detect key verbal phrases
    phrases = {
        "twice": "multiply by 2",
        "triple": "multiply by 3",
        "product": "multiply",
        "sum": "add",
        "difference": "subtract",
        "quotient": "divide",
        "decreased by": "subtract",
        "increased by": "add",
        "more than": "add",
        "less than": "subtract",
        "divided by": "divide",
        "squared": "raise to the power of 2",
        "cubed": "raise to the power of 3",
    }

    key_phrase = None
    key_operation = None
    for phrase, operation in phrases.items():
        if phrase in stem_lower:
            key_phrase = phrase
            key_operation = operation
            break

    if key_phrase:
        stop_variants = [
            f"Let's pause. Can you reread the problem and underline \"{key_phrase}\"? What operation does that tell us to use?",
            f"Hold on - look at the phrase \"{key_phrase}\" in the problem. Before picking an answer, what math operation does that word mean?",
            f"Before we go further, circle \"{key_phrase}\" in the problem. Now, what does that phrase tell you to do with the numbers?",
        ]
        prompt_variants = [
            f"\"{key_phrase}\" means we {key_operation}. Now match each part of the description to a piece of the expression.",
            f"Remember, \"{key_phrase}\" tells us to {key_operation}. Look at each part of the phrase separately - which number comes first, and what happens to it?",
            f"Here's the key: \"{key_phrase}\" = {key_operation}. Now build the expression one piece at a time from the description.",
        ]
        praise_variants = [
            f"You correctly translated \"{key_phrase}\" into the right operation. That's a key algebra skill!",
            f"Nice work! You matched \"{key_phrase}\" to the correct operation and built the expression accurately.",
            f"Excellent! You identified that \"{key_phrase}\" means {key_operation} and wrote the expression correctly.",
        ]
        return {
            "description": f"Students often confuse \"{key_phrase}\" with the wrong operation.",
            "stop": stop_variants[rot % len(stop_variants)],
            "prompt": prompt_variants[rot % len(prompt_variants)],
            "praise": praise_variants[rot % len(praise_variants)],
        }

    stop_fallback = [
        "Let's slow down. Read the description one phrase at a time. What operation does each phrase suggest?",
        "Hold on - let's break this apart. Point to each math word in the description and tell me what operation it means.",
        "Before answering, underline the key math words. What does each one tell you to do?",
    ]
    prompt_fallback = [
        "Match each word to a math operation: 'sum' = add, 'difference' = subtract, 'product' = multiply, 'quotient' = divide.",
        "Use the keyword chart: find the math word in the description, then write the matching operation. Build the expression piece by piece.",
        "Start with the keyword table. Which operation word do you see? Write that operation first, then fill in the numbers.",
    ]
    praise_fallback = [
        "Great job matching the words to the math! You translated the description correctly.",
        "You broke down the description and matched each piece to the right operation. Well done!",
        "Nicely done - you read carefully and wrote exactly what the description asked for.",
    ]
    return {
        "description": "Students may misread the verbal description and pick the wrong operation.",
        "stop": stop_fallback[rot % len(stop_fallback)],
        "prompt": prompt_fallback[rot % len(prompt_fallback)],
        "praise": praise_fallback[rot % len(praise_fallback)],
    }


def _analyze_evaluation(stem, answer, solution, wrong_choices):
    """Analyze evaluate-an-expression problems."""
    rot = _script_rotation["counter"]
    _script_rotation["counter"] += 1
    stops = [
        "Walk me through your steps. Where did you start, and what did you do next?",
        "Show me how you substituted the value. Which part of the expression did you replace?",
        "Let's trace through this together. Point to where you plugged in the number.",
    ]
    prompts = [
        "First substitute the value, then follow PEMDAS: Parentheses, Exponents, Multiply/Divide, Add/Subtract.",
        "Replace the variable with the number, then work through each operation one at a time. What comes first in PEMDAS?",
        "Step 1: swap the variable for the given number. Step 2: simplify using order of operations, starting with parentheses.",
    ]
    praises = [
        "You followed the order of operations correctly. Nice, careful work!",
        "Great job substituting and calculating step by step! You got it right.",
        "You plugged in the value and worked through each operation in the right order. Well done!",
    ]
    return {
        "description": "Students may skip a step, use wrong order of operations, or substitute incorrectly.",
        "stop": stops[rot % len(stops)],
        "prompt": prompts[rot % len(prompts)],
        "praise": praises[rot % len(praises)],
    }


def _analyze_word_problem(stem, answer, solution, wrong_choices):
    """Analyze word-problem-to-expression problems."""
    rot = _script_rotation["counter"]
    _script_rotation["counter"] += 1
    stops = [
        "Let's reread the problem. Which number stays the same no matter what, and which number depends on how many?",
        "Before you pick, tell me: what's the one amount that changes in this situation? That's your variable.",
        "Hold on - read the problem again. What quantity is multiplied by how many, and what's just added or subtracted?",
    ]
    prompts = [
        "Find the fixed cost (a number by itself) and the rate (a number times something). The rate goes with the variable.",
        "Look for two types of numbers: one that repeats per item (rate) and one that stays flat (fixed). The rate gets multiplied by the variable.",
        "Ask yourself: 'What happens each time?' That number gets the variable. 'What happens just once?' That's the constant.",
    ]
    praises = [
        "You identified the fixed and variable parts correctly! That's exactly how to set up these expressions.",
        "Nice work! You figured out what changes and what stays the same, then wrote the expression to match.",
        "You separated the rate from the constant and built the right expression. Great real-world math thinking!",
    ]
    return {
        "description": "Students may confuse which value is the fixed amount and which changes with the variable.",
        "stop": stops[rot % len(stops)],
        "prompt": prompts[rot % len(prompts)],
        "praise": praises[rot % len(praises)],
    }


def _analyze_equation_solving(stem, answer, solution, wrong_choices):
    """Analyze equation-solving problems."""
    rot = _script_rotation["counter"]
    _script_rotation["counter"] += 1
    stops = [
        "Show me your steps. What did you do to both sides of the equation?",
        "Let's look at your work. Which operation did you undo first, and did you do it to both sides?",
        "Pause here. Walk me through each line - what did you do, and why?",
    ]
    prompts = [
        "To undo an operation, use its inverse: undo addition with subtraction, undo multiplication with division. Apply the same step to BOTH sides.",
        "Work backward from the variable: what's the last thing done to it? Undo that first. Then undo the next operation. Always do the same thing to both sides.",
        "Think of it like unwrapping a present - peel off one layer at a time. Subtract first if something was added, then divide if something was multiplied.",
    ]
    praises = [
        "You isolated the variable correctly using inverse operations. Great systematic solving!",
        "Nice job! You undid each operation in the right order and kept both sides balanced.",
        "You solved it step by step, keeping the equation balanced. That's exactly how to do it!",
    ]
    return {
        "description": "Students may use the wrong inverse operation or make a sign error when isolating the variable.",
        "stop": stops[rot % len(stops)],
        "prompt": prompts[rot % len(prompts)],
        "praise": praises[rot % len(praises)],
    }


def _analyze_equivalent_expr(stem, answer, solution, wrong_choices):
    """Analyze equivalent expression / simplification problems."""
    rot = _script_rotation["counter"]
    _script_rotation["counter"] += 1
    stops = [
        "Let's check your work. Did you apply the operation to every term inside the parentheses?",
        "Hold on - look at each term you combined. Do they have the same variable and exponent?",
        "Before we move on, show me which terms you combined and why they go together.",
    ]
    prompts = [
        "Multiply the outside number by EACH term inside. Then combine only like terms (same variable and exponent).",
        "Distribute step by step: outside times first term, then outside times second term. After that, group like terms and add their coefficients.",
        "Check two things: Did you distribute to ALL terms? And did you only combine terms that match (same variable, same power)?",
    ]
    praises = [
        "You distributed and combined like terms correctly! Nice work simplifying.",
        "Great job! You applied the operation to every term and only combined matching terms.",
        "You simplified the expression accurately. You clearly understand how to distribute and combine like terms!",
    ]
    return {
        "description": "Students may forget to distribute to all terms or combine unlike terms.",
        "stop": stops[rot % len(stops)],
        "prompt": prompts[rot % len(prompts)],
        "praise": praises[rot % len(praises)],
    }


def _generate_choice_rationales(question):
    """Generate a reason why a student might choose each wrong option.

    For MC: returns {choice_key: rationale_string} for wrong choices.
    For open-ended (NR/EQ/etc): returns a list of 2 common mistake strings.
    """
    choices = question.choices or []
    stem_lower = (question.stem_text or "").lower()
    solution = question.worked_solution or ""
    answer = question.answer_text or ""

    # For MC questions with choices
    if choices:
        correct = [c for c in choices if c.is_correct]
        correct_text = correct[0].text if correct else answer
        rationales = {}

        for c in choices:
            if c.is_correct:
                continue

            # Use existing rationale if available
            if c.distractor_rationale:
                rationales[c.key] = c.distractor_rationale
                continue

            wrong = c.text.strip()
            correct_t = correct_text.strip()

            # Try to infer what error produced this wrong answer
            rationale = _infer_choice_error(stem_lower, correct_t, wrong, solution)
            rationales[c.key] = rationale

        return {"type": "mc", "rationales": rationales}

    # For open-ended questions (NR, EQ, etc.)
    return {"type": "open", "mistakes": _infer_open_ended_mistakes(stem_lower, answer, solution)}


def _infer_choice_error(stem_lower, correct, wrong, solution):
    """Infer why a student might choose a specific wrong answer."""

    # Try numeric comparison first (evaluation problems)
    def _parse_num(s):
        s = s.strip().replace('$', '').replace(',', '').replace(' ', '')
        try:
            return float(s)
        except ValueError:
            return None

    c_val = _parse_num(correct)
    w_val = _parse_num(wrong)

    if c_val is not None and w_val is not None and c_val != 0:
        if w_val == c_val * 2:
            return "May have doubled the answer or applied an operation twice"
        if w_val == -c_val:
            return "May have a sign error (positive vs. negative)"
        if abs(w_val) > abs(c_val) * 5:
            return "May have multiplied values that should have been added"
        if abs(w_val) < abs(c_val) * 0.6:
            return "May have only computed part of the expression, missing a term"
        if abs(w_val - c_val) < abs(c_val) * 0.15:
            return "May have made a small arithmetic error in the final calculation"
        return "May have used the wrong operation or skipped a step"

    # Expression writing: compare structure of algebraic expressions
    if "expression" in stem_lower or "description" in stem_lower or "write" in stem_lower:
        ops = {'+': 'added', '-': 'subtracted', '*': 'multiplied', '/': 'divided'}
        for op, word in ops.items():
            if op in correct and op not in wrong:
                alt_op = [o for o in ops if o in wrong and o != op]
                if alt_op:
                    return f"May have {ops[alt_op[0]]} instead of {word}"
        # Check for swapped coefficient and constant
        import re
        c_nums = re.findall(r'\d+', correct)
        w_nums = re.findall(r'\d+', wrong)
        if sorted(c_nums) == sorted(w_nums) and c_nums != w_nums:
            return "May have swapped the coefficient and the constant"
        if set(c_nums) != set(w_nums):
            return "May have used the wrong number from the description"
        return "May have confused the operation or the order of terms"

    # Word problems: which value is fixed vs variable
    if "represent" in stem_lower or "model" in stem_lower or "total" in stem_lower:
        if any(c in wrong for c in ['s', 'x', 'n', 'p', 'y']):
            # Has a variable — check if it's attached to the wrong number
            return "May have attached the variable to the wrong quantity (fixed vs. rate)"
        return "May have used the wrong operation to model the situation"

    # Equation solving
    if "solve" in stem_lower or "solution" in stem_lower or "value of" in stem_lower:
        return "May have used the wrong inverse operation or made a sign error"

    # Equivalent expressions / factoring
    if "equivalent" in stem_lower or "simplif" in stem_lower or "factor" in stem_lower:
        return "May have distributed or combined terms incorrectly"

    # Property identification
    if "property" in stem_lower:
        return "May have confused this property with another"

    # Generic fallback
    return "May have misread the problem or made a procedural error"


def _infer_open_ended_mistakes(stem_lower, answer, solution):
    """Generate 2 common mistakes for open-ended questions."""
    mistakes = []

    if "expression" in stem_lower or "write" in stem_lower:
        mistakes.append("Writing the wrong operation (e.g., + instead of x or vice versa)")
        mistakes.append("Putting terms in the wrong order or forgetting a term")
    elif "solve" in stem_lower or "equation" in stem_lower:
        mistakes.append("Using the wrong inverse operation (e.g., subtracting instead of dividing)")
        mistakes.append("Forgetting to apply the operation to both sides")
    elif "evaluat" in stem_lower or "value" in stem_lower:
        mistakes.append("Not following order of operations (PEMDAS)")
        mistakes.append("Substituting the value into the wrong position")
    elif "simplif" in stem_lower or "combin" in stem_lower:
        mistakes.append("Combining unlike terms (e.g., adding 3x + 2y as 5xy)")
        mistakes.append("Forgetting to distribute to all terms in parentheses")
    else:
        # Generic but useful
        mistakes.append("Computation or arithmetic error in the steps")
        mistakes.append("Misreading the problem or skipping a required step")

    return mistakes


def _misconception_from_solution(stem, answer, solution):
    """Generate a generic but problem-specific misconception from the worked solution."""
    if not solution:
        return None

    rot = _script_rotation["counter"]
    _script_rotation["counter"] += 1

    answer_clean = MathPDF._clean_text(answer)
    sol_preview = MathPDF._clean_text(solution[:150])

    stops = [
        "Let's pause and check our work. Walk me through what you did step by step.",
        "Hold on - before we look at the answer, tell me your thinking. What was your first step?",
        "Let's slow down. Can you explain how you got your answer? Show me each step.",
    ]
    prompts = [
        f"Here are the correct steps:\n{sol_preview}\nThe answer is {answer_clean}. Where did your work differ?",
        f"Let me walk you through it:\n{sol_preview}\nThe answer is {answer_clean}. Can you spot where your steps went differently?",
        f"Watch how I work through it:\n{sol_preview}\nSo the answer is {answer_clean}. Now try it again using these steps.",
    ]
    praises = [
        "You worked through it correctly! Great job showing your steps.",
        "Nice work! You followed the steps carefully and got the right answer.",
        "Excellent! Your step-by-step work is clear and accurate.",
    ]
    return {
        "description": "Student may make a computation or procedural error on this problem.",
        "stop": stops[rot % len(stops)],
        "prompt": prompts[rot % len(prompts)],
        "praise": praises[rot % len(praises)],
    }


def _select_session_questions(all_questions, intervention_data, pld_level, seed=42):
    """Select and distribute questions for a 30-min intervention session.

    Uses a difficulty ladder for practice: easy → medium → hard.
    Returns {"diagnose": [...], "practice": [...], "exit_check": [...]}.
    """
    from engine.models import Difficulty

    rng = _random.Random(seed)

    # Get stem indices at this PLD from intervention data
    target_stems = intervention_data.get("target_stems", [])
    pld_stem_indices = [
        s["stem_index"] for s in target_stems
        if s.get("proficiency") == pld_level
    ]

    if not pld_stem_indices:
        pld_stem_indices = [s["stem_index"] for s in target_stems]

    # Build pool: primary = matching PLD, extended = one level up for harder questions
    pld_order = ["below", "approaching", "at", "above"]
    pld_idx = pld_order.index(pld_level) if pld_level in pld_order else 0
    next_pld = pld_order[pld_idx + 1] if pld_idx + 1 < len(pld_order) else None

    # All stem indices across current and next proficiency band
    all_stem_indices = set(pld_stem_indices)
    next_pld_stems = []
    if next_pld:
        next_pld_stems = [
            s["stem_index"] for s in target_stems
            if s.get("proficiency") == next_pld
        ]
        all_stem_indices.update(next_pld_stems)

    # Primary pool: questions at this PLD level
    primary_pool = [
        q for q in all_questions
        if q.stem_index in pld_stem_indices
        and q.proficiency_level.value == pld_level
    ]
    # Extended pool: questions from next PLD up (for harder practice)
    extended_pool = [
        q for q in all_questions
        if q.stem_index in next_pld_stems
        and q.proficiency_level.value == next_pld
    ] if next_pld else []

    full_pool = primary_pool + extended_pool
    if not full_pool:
        full_pool = [q for q in all_questions if q.stem_index in all_stem_indices]
    if not full_pool:
        raise ValueError(f"No questions available for PLD level '{pld_level}'")

    rng.shuffle(primary_pool)
    rng.shuffle(extended_pool)

    # Group all questions by difficulty
    by_difficulty = {"easy": [], "medium": [], "difficult": []}
    for q in primary_pool + extended_pool:
        by_difficulty[q.difficulty.value].append(q)

    used_content = set()  # (stem_index, variant_index) to prevent duplicates

    def _is_duplicate(q):
        return (q.stem_index, q.variant_index) in used_content

    def _mark_used(q):
        used_content.add((q.stem_index, q.variant_index))

    def pick_by_difficulty(difficulty_str, count=1):
        """Pick `count` unused questions at the given difficulty."""
        results = []
        for q in by_difficulty.get(difficulty_str, []):
            if not _is_duplicate(q):
                _mark_used(q)
                results.append(q)
                if len(results) >= count:
                    break
        return results

    def pick_from_pool(pool_list, count=1):
        """Pick from a specific pool regardless of difficulty."""
        results = []
        for q in pool_list:
            if not _is_duplicate(q):
                _mark_used(q)
                results.append(q)
                if len(results) >= count:
                    break
        return results

    # ---- DIAGNOSE: 2 easy questions (baseline assessment) ----
    diagnose = pick_by_difficulty("easy", 2)
    # Fall back to any primary pool questions if not enough easy
    if len(diagnose) < 2:
        diagnose += pick_from_pool(primary_pool, 2 - len(diagnose))

    # ---- PRACTICE: difficulty ladder (2 easy, 2 medium, 1-2 hard) ----
    practice = []

    # 2 easy practice questions
    easy_practice = pick_by_difficulty("easy", 2)
    practice.extend(easy_practice)

    # 2 medium practice questions
    medium_practice = pick_by_difficulty("medium", 2)
    practice.extend(medium_practice)

    # 1-2 hard practice questions (from current or next PLD)
    hard_practice = pick_by_difficulty("difficult", 2)
    if not hard_practice:
        # If no "difficult" tagged questions, use medium from next PLD
        hard_practice = pick_by_difficulty("medium", 2)
    practice.extend(hard_practice)

    # Ensure minimum 5 practice questions, fill from any available
    while len(practice) < 5:
        filled = pick_from_pool(primary_pool + extended_pool, 1)
        if not filled:
            break
        practice.extend(filled)

    # Cap at 6 practice questions max
    practice = practice[:6]

    # ---- EXIT CHECK: 2 medium questions ----
    exit_check = pick_by_difficulty("medium", 2)
    if len(exit_check) < 2:
        exit_check += pick_by_difficulty("easy", 2 - len(exit_check))
    if not exit_check:
        exit_check = pick_from_pool(primary_pool, 2)

    return {
        "diagnose": diagnose,
        "practice": practice,
        "exit_check": exit_check,
    }


def _draw_intervention_section_header(pdf, title, color=None):
    """Draw a bold section header with colored underline."""
    if pdf.get_y() > pdf.h - 30:
        pdf.add_page()

    if color is None:
        color = SB_YELLOW

    pdf.set_font(pdf.ff, "B", 13)
    pdf.set_text_color(*SB_DARK)
    pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")

    # Colored underline
    y = pdf.get_y()
    pdf.set_draw_color(*color)
    pdf.set_line_width(1.0)
    pdf.line(PAGE_MARGIN, y, pdf.w - PAGE_MARGIN, y)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)
    pdf.ln(3)


def _draw_intervention_table(pdf, headers, rows, col_widths=None):
    """Draw a table with yellow header row and text wrapping."""
    usable_w = pdf.w - 2 * PAGE_MARGIN
    if col_widths is None:
        n = len(headers)
        col_widths = [usable_w / n] * n

    line_h = 4.5  # line height for wrapped text

    # Header row
    pdf.set_fill_color(*SB_YELLOW)
    pdf.set_font(pdf.ff, "B", 8)
    pdf.set_text_color(*SB_DARK)
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 6, MathPDF._clean_text(h),
                 border=1, fill=True, align="C",
                 new_x="RIGHT", new_y="TOP")
    pdf.ln()

    # Data rows with text wrapping
    pdf.set_font(pdf.ff, "", 8)
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(*SB_YELLOW_PALE)

    for r_idx, row in enumerate(rows):
        fill = r_idx % 2 == 1

        # Measure row height: find tallest cell
        row_h = line_h
        for i, cell_text in enumerate(row):
            text = MathPDF._clean_text(str(cell_text))
            if text:
                # Estimate number of lines needed
                pdf.set_font(pdf.ff, "", 8)
                text_w = pdf.get_string_width(text)
                cell_inner_w = col_widths[i] - 2  # padding
                if cell_inner_w > 0 and text_w > cell_inner_w:
                    n_lines = int(text_w / cell_inner_w) + 1
                    needed_h = n_lines * line_h
                    row_h = max(row_h, needed_h)

        # Check for page break
        if pdf.get_y() + row_h > pdf.h - 25:
            pdf.add_page()

        row_y = pdf.get_y()
        x_start = pdf.get_x()

        # Draw cell backgrounds and borders first
        x = x_start
        for i in range(len(row)):
            if fill:
                pdf.set_fill_color(*SB_YELLOW_PALE)
                pdf.rect(x, row_y, col_widths[i], row_h, style="DF")
            else:
                pdf.rect(x, row_y, col_widths[i], row_h)
            x += col_widths[i]

        # Write text into cells with wrapping
        x = x_start
        for i, cell_text in enumerate(row):
            text = MathPDF._clean_text(str(cell_text))
            pdf.set_font(pdf.ff, "", 8)
            pdf.set_text_color(0, 0, 0)
            align = "C" if i > 0 else "L"
            pdf.set_xy(x + 1, row_y + 0.5)
            pdf.multi_cell(col_widths[i] - 2, line_h, text, align=align)
            x += col_widths[i]

        pdf.set_xy(x_start, row_y + row_h)

    pdf.set_fill_color(255, 255, 255)
    pdf.ln(3)


def _draw_checkbox_row(pdf, label, num_boxes=4, box_labels=None):
    """Draw a row with label and empty checkbox squares."""
    pdf.set_font(pdf.ff, "", 8)
    pdf.cell(30, 5, label, new_x="RIGHT", new_y="TOP")

    box_size = 4
    gap = 1
    if box_labels:
        for i, bl in enumerate(box_labels):
            x = pdf.get_x()
            y = pdf.get_y()
            pdf.rect(x, y + 0.5, box_size, box_size)
            pdf.set_font(pdf.ff, "", 6)
            pdf.set_xy(x + box_size + 1, y)
            w = max(15, pdf.get_string_width(bl) + 2)
            pdf.cell(w, 5, bl, new_x="RIGHT", new_y="TOP")
    else:
        for i in range(num_boxes):
            x = pdf.get_x()
            y = pdf.get_y()
            pdf.rect(x, y + 0.5, box_size, box_size)
            pdf.set_xy(x + box_size + gap + 2, y)
    pdf.ln(7)


def _draw_misconception_card_pdf(pdf, misconception):
    """Render one misconception card with Stop/Prompt/Praise bars."""
    if pdf.get_y() > pdf.h - 50:
        pdf.add_page()

    start_y = pdf.get_y()

    # Description header
    pdf.set_font(pdf.ff, "B", 9)
    pdf.set_text_color(*SB_DARK)
    pdf.multi_cell(pdf.w - 2 * PAGE_MARGIN, 5,
                   MathPDF._clean_text(misconception["description"]),
                   new_x="LMARGIN", new_y="NEXT")

    # Why it happens
    pdf.set_font(pdf.ff, "I", 7.5)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(pdf.w - 2 * PAGE_MARGIN, 4.5,
                   "Why: " + MathPDF._clean_text(misconception.get("why_it_happens", "")),
                   new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    script = misconception.get("redirect_script", {})
    steps = [
        ("STOP", script.get("stop", ""), (239, 68, 68)),       # red
        ("PROMPT", script.get("prompt", ""), (245, 158, 11)),   # amber
        ("PRAISE", script.get("praise", ""), (34, 197, 94)),    # green
    ]

    for label, text, color in steps:
        if not text:
            continue
        y = pdf.get_y()
        if y > pdf.h - 25:
            pdf.add_page()
            y = pdf.get_y()

        # Colored left bar
        pdf.set_fill_color(*color)
        pdf.rect(PAGE_MARGIN, y, 2, 9, style="F")

        # Label
        pdf.set_xy(PAGE_MARGIN + 4, y)
        pdf.set_font(pdf.ff, "B", 7)
        pdf.set_text_color(*color)
        pdf.cell(15, 4, label, new_x="RIGHT", new_y="TOP")

        # Text
        pdf.set_xy(PAGE_MARGIN + 4, y + 3.5)
        pdf.set_font(pdf.ff, "", 7.5)
        pdf.set_text_color(*SB_DARK)
        pdf.multi_cell(pdf.w - 2 * PAGE_MARGIN - 6, 4,
                       MathPDF._clean_text(text),
                       new_x="LMARGIN", new_y="NEXT")
        pdf.ln(0.5)

    # Reset
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(255, 255, 255)

    # Divider
    pdf.ln(2)
    pdf.set_draw_color(*SB_YELLOW)
    pdf.set_line_width(0.3)
    pdf.line(PAGE_MARGIN + 10, pdf.get_y(), pdf.w - PAGE_MARGIN - 10, pdf.get_y())
    pdf.set_draw_color(0, 0, 0)
    pdf.ln(3)


def _draw_frayer_compact(pdf, vocab_item, x, y, w, h):
    """Draw a compact Frayer Model (2x2 grid) for one vocabulary term."""
    half_w = w / 2
    half_h = (h - 6) / 2  # reserve 6mm for term header

    # Term header (centered across the box)
    pdf.set_fill_color(*SB_YELLOW_LIGHT)
    pdf.rect(x, y, w, 6, style="DF")
    pdf.set_font(pdf.ff, "B", 8)
    pdf.set_text_color(*SB_DARK)
    term = MathPDF._clean_text(vocab_item.get("term", ""))
    tw = pdf.get_string_width(term)
    pdf.set_xy(x + (w - tw) / 2, y + 0.5)
    pdf.cell(tw, 5, term)

    grid_y = y + 6
    quadrants = [
        ("Definition", vocab_item.get("definition", ""), (239, 246, 255)),
        ("Characteristics", vocab_item.get("characteristics", []), (240, 253, 244)),
        ("Examples", vocab_item.get("examples", []), (255, 251, 235)),
        ("Non-Examples", vocab_item.get("non_examples", []), (254, 242, 242)),
    ]

    positions = [
        (x, grid_y),
        (x + half_w, grid_y),
        (x, grid_y + half_h),
        (x + half_w, grid_y + half_h),
    ]

    for i, (label, content, bg_color) in enumerate(quadrants):
        qx, qy = positions[i]
        pdf.set_fill_color(*bg_color)
        pdf.rect(qx, qy, half_w, half_h, style="DF")

        # Label
        pdf.set_font(pdf.ff, "B", 6)
        pdf.set_text_color(80, 80, 80)
        pdf.set_xy(qx + 1, qy + 0.5)
        pdf.cell(half_w - 2, 3, label)

        # Content
        pdf.set_font(pdf.ff, "", 6)
        pdf.set_text_color(*SB_DARK)
        if isinstance(content, list):
            text = ", ".join(str(c) for c in content[:3])
        else:
            text = str(content)
        text = MathPDF._clean_text(text)
        # Truncate if too long
        max_chars = int(half_w * 3)
        if len(text) > max_chars:
            text = text[:max_chars - 3] + "..."
        pdf.set_xy(qx + 1, qy + 3.5)
        pdf.multi_cell(half_w - 2, 3, text)

    # Outer border
    pdf.set_draw_color(180, 180, 180)
    pdf.rect(x, y, w, h)
    pdf.set_draw_color(0, 0, 0)

    # Reset
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(255, 255, 255)


def _draw_reflection_box(pdf):
    """Draw a reflection box with prompts and ample writing space."""
    if pdf.get_y() > pdf.h - 80:
        pdf.add_page()

    y_start = pdf.get_y()
    box_w = pdf.w - 2 * PAGE_MARGIN
    box_h = 70  # larger box for real writing

    # Yellow border
    pdf.set_draw_color(*SB_YELLOW)
    pdf.set_line_width(1.0)
    pdf.rect(PAGE_MARGIN, y_start, box_w, box_h)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)

    # Title
    pdf.set_xy(PAGE_MARGIN + 3, y_start + 2)
    pdf.set_font(pdf.ff, "B", 11)
    pdf.set_text_color(*SB_DARK)
    pdf.cell(0, 6, "Reflection")

    # Prompt 1
    pdf.set_xy(PAGE_MARGIN + 3, y_start + 10)
    pdf.set_font(pdf.ff, "I", 9)
    pdf.cell(0, 5, "What mistake did I make?")
    for i in range(3):
        y_line = y_start + 17 + i * 7
        pdf.set_draw_color(200, 200, 200)
        pdf.line(PAGE_MARGIN + 3, y_line, PAGE_MARGIN + box_w - 6, y_line)

    # Prompt 2
    pdf.set_xy(PAGE_MARGIN + 3, y_start + 40)
    pdf.cell(0, 5, "How will I avoid it next time?")
    for i in range(3):
        y_line = y_start + 47 + i * 7
        pdf.set_draw_color(200, 200, 200)
        pdf.line(PAGE_MARGIN + 3, y_line, PAGE_MARGIN + box_w - 6, y_line)

    pdf.set_draw_color(0, 0, 0)
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(y_start + box_h + 3)


def _draw_reinforcement_grid(pdf):
    """Draw a 4x5 grid of empty tally boxes for 4:1 tracking."""
    _draw_intervention_section_header(pdf, "Positive Reinforcement Tracker", (34, 197, 94))

    pdf.set_font(pdf.ff, "", 8)
    pdf.cell(0, 5, "Goal: 4 positive interactions for every 1 correction",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Labels
    labels = [("Positive (+)", (34, 197, 94)), ("Corrective (-)", (245, 158, 11))]
    box_size = 5
    cols = 10
    y_start = pdf.get_y()

    for row_idx, (label, color) in enumerate(labels):
        y = y_start + row_idx * (box_size + 8)
        pdf.set_xy(PAGE_MARGIN, y)
        pdf.set_font(pdf.ff, "B", 8)
        pdf.set_text_color(*color)
        pdf.cell(30, box_size, label)

        pdf.set_draw_color(*color)
        for c in range(cols):
            bx = PAGE_MARGIN + 32 + c * (box_size + 1.5)
            pdf.rect(bx, y, box_size, box_size)

    pdf.set_draw_color(0, 0, 0)
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(y_start + 2 * (box_size + 8) + 3)


def generate_student_session_pdf(session_questions, output_path,
                                  standard_code="", standard_text="",
                                  pld_level="below",
                                  calculator="Not Allowed"):
    """Generate the student-facing intervention session worksheet."""
    pld_label = "Below Proficiency" if pld_level == "below" else "Approaching Proficiency"

    pdf = PlugNPlayPDF(
        title=f"Intervention Session",
        standard_code=standard_code,
        standard_text=standard_text,
        calculator=calculator,
    )
    pdf.alias_nb_pages()
    pdf.add_page()

    # PLD badge below header
    pdf.set_font(pdf.ff, "B", 10)
    badge_w = pdf.get_string_width(pld_label) + 10
    badge_x = (pdf.w - badge_w) / 2
    badge_y = pdf.get_y()
    if pld_level == "below":
        pdf.set_fill_color(254, 202, 202)
        pdf.set_text_color(153, 27, 27)
    else:
        pdf.set_fill_color(254, 243, 199)
        pdf.set_text_color(146, 64, 14)
    pdf.set_draw_color(200, 200, 200)
    pdf.rect(badge_x, badge_y, badge_w, 7, style="DF")
    pdf.set_xy(badge_x, badge_y + 0.5)
    pdf.cell(badge_w, 6, pld_label, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(0, 0, 0)
    pdf.ln(10)

    # --- PRE-ASSESSMENT ---
    num = 1
    diagnose_qs = session_questions.get("diagnose", [])
    if diagnose_qs:
        _draw_intervention_section_header(pdf, "PRE-ASSESSMENT")
        pdf.set_font(pdf.ff, "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, "Try each problem. Show your thinking.",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)
        for q in diagnose_qs:
            pdf.write_question(num, q)
            num += 1

    # --- PRACTICE (new page) ---
    practice_qs = session_questions.get("practice", [])
    if practice_qs:
        pdf.add_page()
        _draw_intervention_section_header(pdf, "PRACTICE")
        pdf.set_font(pdf.ff, "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, "Work through each problem carefully. Show your work.",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)
        for q in practice_qs:
            pdf.write_question(num, q, compact=True)
            num += 1

    # --- EXIT TICKET (new page) ---
    exit_qs = session_questions.get("exit_check", [])
    if exit_qs:
        pdf.add_page()
        _draw_intervention_section_header(pdf, "EXIT TICKET", (255, 83, 72))
        pdf.set_font(pdf.ff, "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, "Show what you know - no help on this one!",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)
        for q in exit_qs:
            pdf.write_question(num, q)
            num += 1

    # --- REFLECTION ---
    pdf.ln(3)
    _draw_reflection_box(pdf)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    pdf.output(output_path)
    return output_path


def generate_teacher_companion_pdf(session_questions, intervention_data,
                                    output_path, standard_code="",
                                    standard_text="", pld_level="below",
                                    calculator="Not Allowed"):
    """Generate the teacher companion guide for an intervention session."""
    pld_label = "Below Proficiency" if pld_level == "below" else "Approaching Proficiency"
    all_qs = (session_questions.get("diagnose", [])
              + session_questions.get("practice", [])
              + session_questions.get("exit_check", []))

    pdf = PlugNPlayPDF(
        title="Teacher Companion",
        standard_code=standard_code,
        standard_text=standard_text,
        calculator=calculator,
    )
    pdf.alias_nb_pages()
    pdf.add_page()

    # PLD badge
    pdf.set_font(pdf.ff, "B", 10)
    badge_w = pdf.get_string_width(pld_label) + 10
    badge_x = (pdf.w - badge_w) / 2
    badge_y = pdf.get_y()
    if pld_level == "below":
        pdf.set_fill_color(254, 202, 202)
        pdf.set_text_color(153, 27, 27)
    else:
        pdf.set_fill_color(254, 243, 199)
        pdf.set_text_color(146, 64, 14)
    pdf.set_draw_color(200, 200, 200)
    pdf.rect(badge_x, badge_y, badge_w, 7, style="DF")
    pdf.set_xy(badge_x, badge_y + 0.5)
    pdf.cell(badge_w, 6, pld_label, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(0, 0, 0)
    pdf.ln(10)

    # ====== PAGE 1: SESSION PROTOCOL ======
    _draw_intervention_section_header(pdf, "30-Minute Session Protocol")

    n_diag = len(session_questions.get("diagnose", []))
    n_prac = len(session_questions.get("practice", []))
    protocol_rows = [
        ["Diagnose", "5 min", f"Student works problems 1-{n_diag}", "Observe and note errors"],
        ["Model", "5 min", "Student listens, asks questions", "I Do think-aloud (see scripts)"],
        ["Guided Practice", "10 min", f"Problems {n_diag+1}-{n_diag+n_prac} with teacher", "Use misconception cards"],
        ["Independent Practice", "5 min", f"Problems {n_diag+n_prac+1}-{n_diag+n_prac+len(session_questions.get('exit_check',[]))-1+n_prac}", "Monitor, mark correct/incorrect"],
        ["Reflect + Exit", "5 min", f"Problem {len(all_qs)} + reflection", "Check mastery, plan next session"],
    ]
    usable_w = pdf.w - 2 * PAGE_MARGIN
    _draw_intervention_table(pdf,
        ["Phase", "Time", "Student Does", "Teacher Does"],
        protocol_rows,
        [usable_w * 0.18, usable_w * 0.10, usable_w * 0.36, usable_w * 0.36])

    # ====== PAGE 2: ANSWER KEY ======
    pdf.add_page()
    _draw_intervention_section_header(pdf, "Answer Key with Worked Solutions")

    for i, q in enumerate(all_qs, 1):
        if pdf.get_y() > pdf.h - 35:
            pdf.add_page()

        # Section label for first question of each group
        if i == 1:
            pdf.set_font(pdf.ff, "I", 8)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 4, "Diagnose", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
        elif i == len(session_questions.get("diagnose", [])) + 1:
            pdf.set_font(pdf.ff, "I", 8)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 4, "Practice", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
        elif i == len(all_qs):
            pdf.set_font(pdf.ff, "I", 8)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 4, "Exit Check", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)

        pdf.set_font(pdf.ff, "B", 9)
        pdf.cell(8, 5, f"{i}.", new_x="RIGHT", new_y="TOP")
        x_body = pdf.get_x()

        answer = MathPDF._clean_text(q.answer_text)
        pdf.cell(0, 5, f"Answer: {answer}", new_x="LMARGIN", new_y="NEXT")

        if q.worked_solution:
            pdf.set_x(x_body)
            pdf.set_font(pdf.ff, "", 7.5)
            solution = MathPDF._clean_text(q.worked_solution)
            for line in solution.split("\n"):
                line = line.strip()
                if line:
                    pdf.set_x(x_body)
                    pdf.cell(0, 4, line, new_x="LMARGIN", new_y="NEXT")

        # Divider
        pdf.ln(1)
        pdf.set_draw_color(*SB_YELLOW)
        pdf.set_line_width(0.3)
        pdf.line(PAGE_MARGIN, pdf.get_y(), pdf.w - PAGE_MARGIN, pdf.get_y())
        pdf.set_draw_color(0, 0, 0)
        pdf.ln(2)

    # ====== PAGE 3: MISCONCEPTION CARDS ======
    pdf.add_page()
    _draw_intervention_section_header(pdf, "Misconception Cards")
    pdf.set_font(pdf.ff, "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 4, "Use the Stop / Prompt / Praise scripts when you see these errors.",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)

    # Get stem indices at this PLD
    target_stems = intervention_data.get("target_stems", [])
    pld_stem_indices = set(
        s["stem_index"] for s in target_stems
        if s.get("proficiency") == pld_level
    )

    misconceptions = intervention_data.get("misconceptions", [])
    relevant_misconceptions = [
        m for m in misconceptions
        if set(m.get("affects_stems", [])) & pld_stem_indices
    ]
    if not relevant_misconceptions:
        relevant_misconceptions = misconceptions  # show all if none match

    for m in relevant_misconceptions:
        _draw_misconception_card_pdf(pdf, m)

    # ====== PAGE 4: TEACHING SCRIPTS + VOCABULARY ======
    pdf.add_page()
    _draw_intervention_section_header(pdf, "Teaching Scripts (I Do / We Do / You Do)")

    teaching = intervention_data.get("teaching_script", {})
    scripts = [
        ("I Do (Teacher Models)", teaching.get("i_do", ""), (64, 139, 251)),
        ("We Do (Guided Practice)", teaching.get("we_do", ""), (245, 158, 11)),
        ("You Do (Independent Practice)", teaching.get("you_do", ""), (34, 197, 94)),
    ]

    for title_text, body, color in scripts:
        if pdf.get_y() > pdf.h - 35:
            pdf.add_page()

        y = pdf.get_y()
        # Colored left bar
        pdf.set_fill_color(*color)
        pdf.rect(PAGE_MARGIN, y, 2.5, 5, style="F")

        pdf.set_xy(PAGE_MARGIN + 5, y)
        pdf.set_font(pdf.ff, "B", 9)
        pdf.set_text_color(*color)
        pdf.cell(0, 5, title_text, new_x="LMARGIN", new_y="NEXT")

        pdf.set_x(PAGE_MARGIN + 5)
        pdf.set_font(pdf.ff, "", 8)
        pdf.set_text_color(*SB_DARK)
        pdf.multi_cell(pdf.w - 2 * PAGE_MARGIN - 7, 4.5,
                       MathPDF._clean_text(body),
                       new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(255, 255, 255)

    # Vocabulary
    vocab = intervention_data.get("vocabulary", [])
    if vocab:
        if pdf.get_y() > pdf.h - 60:
            pdf.add_page()
        _draw_intervention_section_header(pdf, "Vocabulary Quick-Reference (Frayer Model)")

        frayer_w = (pdf.w - 2 * PAGE_MARGIN - 5) / 2
        frayer_h = 32
        for i, v in enumerate(vocab):
            col = i % 2
            row = i // 2
            x = PAGE_MARGIN + col * (frayer_w + 5)
            y = pdf.get_y() if col == 0 else y_row_start

            if col == 0:
                if pdf.get_y() > pdf.h - frayer_h - 5:
                    pdf.add_page()
                y_row_start = pdf.get_y()

            _draw_frayer_compact(pdf, v, x, y_row_start if col == 1 else pdf.get_y(), frayer_w, frayer_h)

            if col == 1 or i == len(vocab) - 1:
                pdf.set_y(y_row_start + frayer_h + 3)

    # ====== PAGE 5: PREREQUISITES + TOOLS ======
    pdf.add_page()

    # Prerequisite Skills
    prereqs = intervention_data.get("prerequisite_skills", [])
    if prereqs:
        _draw_intervention_section_header(pdf, "Prerequisite Skill Checks")
        pdf.set_font(pdf.ff, "I", 7.5)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 4, "If a student has a prerequisite gap, check these skills first:",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

        prereq_rows = []
        for p in prereqs:
            prereq_rows.append([
                p.get("skill", ""),
                p.get("grade_level", ""),
                p.get("check_question", ""),
            ])
        _draw_intervention_table(pdf,
            ["Skill", "Grade Level", "Quick-Check Question"],
            prereq_rows,
            [usable_w * 0.25, usable_w * 0.15, usable_w * 0.60])

    # CRA Tips
    if pdf.get_y() > pdf.h - 35:
        pdf.add_page()
    _draw_intervention_section_header(pdf, "Concrete -> Visual -> Abstract")
    _draw_intervention_table(pdf,
        ["Concrete", "Visual", "Abstract"],
        [["Use manipulatives, counters, fraction tiles, algebra tiles",
          "Draw diagrams, number lines, bar models, area models",
          "Write expressions, equations, use symbols and notation"]],
        [usable_w / 3] * 3)

    # Think-Aloud Prompts
    _draw_intervention_section_header(pdf, "Think-Aloud Prompts")
    pdf.set_font(pdf.ff, "", 8)
    prompts = [
        "What do I know? What am I looking for?",
        "What operation does this word/phrase tell me to use?",
        "I notice... I'm choosing this because...",
        "Does my answer make sense? Let me check by...",
        "Where did I get confused? Let me try again from there.",
        "Can I draw a picture or use objects to help me see this?",
    ]
    for p in prompts:
        pdf.cell(5, 5, "-", new_x="RIGHT", new_y="TOP")
        pdf.cell(0, 5, p, new_x="LMARGIN", new_y="NEXT")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    pdf.output(output_path)
    return output_path


def generate_combined_session_pdf(session_questions, intervention_data,
                                   output_path, standard_code="",
                                   standard_text="", pld_level="below",
                                   calculator="Not Allowed"):
    """Generate a single PDF with student worksheet pages followed by teacher companion pages."""
    # Reset script rotation so each PDF gets fresh language variation
    _script_rotation["counter"] = 0

    pld_label = "Below Proficiency" if pld_level == "below" else "Approaching Proficiency"
    all_qs = (session_questions.get("diagnose", [])
              + session_questions.get("practice", [])
              + session_questions.get("exit_check", []))
    usable_w = 210 - 2 * PAGE_MARGIN  # A4 width assumption

    pdf = PlugNPlayPDF(
        title="Intervention Session",
        standard_code=standard_code,
        standard_text=standard_text,
        calculator=calculator,
    )
    pdf.alias_nb_pages()

    # ================================================================
    # PART 1: STUDENT WORKSHEET
    # ================================================================
    pdf.add_page()

    # PLD badge
    pdf.set_font(pdf.ff, "B", 10)
    badge_w = pdf.get_string_width(pld_label) + 10
    badge_x = (pdf.w - badge_w) / 2
    badge_y = pdf.get_y()
    if pld_level == "below":
        pdf.set_fill_color(254, 202, 202)
        pdf.set_text_color(153, 27, 27)
    else:
        pdf.set_fill_color(254, 243, 199)
        pdf.set_text_color(146, 64, 14)
    pdf.set_draw_color(200, 200, 200)
    pdf.rect(badge_x, badge_y, badge_w, 7, style="DF")
    pdf.set_xy(badge_x, badge_y + 0.5)
    pdf.cell(badge_w, 6, pld_label, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(0, 0, 0)
    pdf.ln(10)

    # --- WORKED EXAMPLE (reference anchor for students) ---
    teaching = intervention_data.get("teaching_script", {})
    i_do = teaching.get("i_do", "")
    if i_do:
        box_w = pdf.w - 2 * PAGE_MARGIN
        y0 = pdf.get_y()
        # Light blue background box
        pdf.set_fill_color(240, 248, 255)
        pdf.set_draw_color(*SB_YELLOW)
        pdf.set_line_width(0.8)
        pdf.rect(PAGE_MARGIN, y0, box_w, 6, style="DF")
        pdf.set_xy(PAGE_MARGIN + 3, y0 + 1)
        pdf.set_font(pdf.ff, "B", 10)
        pdf.set_text_color(*SB_DARK)
        pdf.cell(0, 4, "EXAMPLE - How to approach this skill:")
        pdf.set_y(y0 + 7)
        pdf.set_x(PAGE_MARGIN + 3)
        pdf.set_font(pdf.ff, "", 9)
        pdf.set_text_color(50, 50, 50)
        # Use first 2-3 sentences as concise example
        sentences = [s.strip() for s in i_do.replace('. ', '.\n').split('\n') if s.strip()]
        example_text = '. '.join(sentences[:3])
        if not example_text.endswith('.'):
            example_text += '.'
        pdf.multi_cell(box_w - 6, 4.5, MathPDF._clean_text(example_text),
                       new_x="LMARGIN", new_y="NEXT")
        y_end = pdf.get_y() + 2
        box_h = y_end - y0
        pdf.set_draw_color(*SB_YELLOW)
        pdf.rect(PAGE_MARGIN, y0, box_w, box_h, style="D")
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.3)
        pdf.set_text_color(0, 0, 0)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_y(y_end + 4)

    # --- PAGE 1: PRE-ASSESSMENT (DIAGNOSE) ---
    num = 1
    diagnose_qs = session_questions.get("diagnose", [])
    if diagnose_qs:
        _draw_intervention_section_header(pdf, "PRE-ASSESSMENT")
        pdf.set_font(pdf.ff, "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, "Try each problem. Show your thinking.",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)
        for q in diagnose_qs:
            pdf.write_question(num, q)
            num += 1

    # --- PAGE 2 (and maybe 3): PRACTICE ---
    practice_qs = session_questions.get("practice", [])
    if practice_qs:
        pdf.add_page()
        _draw_intervention_section_header(pdf, "PRACTICE")
        pdf.set_font(pdf.ff, "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, "Work through each problem carefully. Show your work.",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

        # Track which practice page we're on and how many questions per page
        practice_page_num = 1
        qs_on_current_page = 0
        page_usable_h = pdf.h - 15  # bottom margin

        for qi, q in enumerate(practice_qs):
            remaining_qs = len(practice_qs) - qi

            # Smart page break: only spill to page 2 if:
            # - remaining questions >= 2 (never just 1 on a new page)
            if pdf.get_y() > page_usable_h - 40 and practice_page_num == 1:
                if remaining_qs >= 2:
                    pdf.add_page()
                    practice_page_num = 2
                    qs_on_current_page = 0

            pdf.write_question(num, q, compact=True)
            num += 1
            qs_on_current_page += 1

    # --- EXIT TICKET (new page) ---
    exit_qs = session_questions.get("exit_check", [])
    if exit_qs:
        pdf.add_page()
        _draw_intervention_section_header(pdf, "EXIT TICKET", (255, 83, 72))
        pdf.set_font(pdf.ff, "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, "Show what you know - no help on this one!",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)
        for q in exit_qs:
            pdf.write_question(num, q)
            num += 1

    # --- REFLECTION ---
    pdf.ln(5)
    _draw_reflection_box(pdf)

    # ================================================================
    # PART 2: TEACHER COMPANION (starts on new page)
    # ================================================================
    pdf.add_page()

    # Teacher companion header
    _draw_sb_header(pdf, PAGE_MARGIN, 5, pdf.w - 2 * PAGE_MARGIN, 13,
                    title="Teacher Companion",
                    standard_code=standard_code,
                    r=3, include_name=False, font_title=11)
    pdf.set_y(20)

    # PLD badge
    pdf.set_font(pdf.ff, "B", 10)
    badge_w = pdf.get_string_width(pld_label) + 10
    badge_x = (pdf.w - badge_w) / 2
    badge_y = pdf.get_y()
    if pld_level == "below":
        pdf.set_fill_color(254, 202, 202)
        pdf.set_text_color(153, 27, 27)
    else:
        pdf.set_fill_color(254, 243, 199)
        pdf.set_text_color(146, 64, 14)
    pdf.set_draw_color(200, 200, 200)
    pdf.rect(badge_x, badge_y, badge_w, 7, style="DF")
    pdf.set_xy(badge_x, badge_y + 0.5)
    pdf.cell(badge_w, 6, pld_label, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(0, 0, 0)
    pdf.ln(5)

    # --- QUICK REFERENCE: Keyword-to-Operation Table ---
    pdf.set_font(pdf.ff, "B", 9)
    pdf.set_text_color(*SB_DARK)
    pdf.cell(0, 5, "Quick Reference - Math Keywords:", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    kw_data = [
        ["sum, more than, increased by, plus", "ADD (+)"],
        ["difference, less than, decreased by, minus", "SUBTRACT (-)"],
        ["product, times, twice, triple, of", "MULTIPLY (x)"],
        ["quotient, divided by, per, ratio", "DIVIDE (/)"],
        ["squared, cubed, to the power of", "EXPONENT (^)"],
    ]
    kw_col1 = usable_w * 0.65
    kw_col2 = usable_w * 0.35
    # Header
    pdf.set_fill_color(*SB_YELLOW)
    pdf.set_font(pdf.ff, "B", 8)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(kw_col1, 5, "  Keywords in problem", border=1, fill=True,
             new_x="RIGHT", new_y="TOP")
    pdf.cell(kw_col2, 5, "  Operation", border=1, fill=True,
             new_x="LMARGIN", new_y="NEXT")
    # Rows
    pdf.set_font(pdf.ff, "", 7.5)
    pdf.set_text_color(*SB_DARK)
    pdf.set_fill_color(255, 255, 255)
    for row in kw_data:
        pdf.cell(kw_col1, 4, "  " + row[0], border=1,
                 new_x="RIGHT", new_y="TOP")
        pdf.set_font(pdf.ff, "B", 7.5)
        pdf.cell(kw_col2, 4, "  " + row[1], border=1,
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(pdf.ff, "", 7.5)
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(255, 255, 255)
    pdf.ln(2)

    # --- Helper: get misconceptions for a question's stem ---
    misconceptions = intervention_data.get("misconceptions", [])
    def _get_misconceptions_for(q):
        return [m for m in misconceptions if q.stem_index in m.get("affects_stems", [])]

    # --- Helper: write math-aware text in teacher columns ---
    def _write_math_cell(text, x, max_w, font_style="", font_size=10):
        """Write text with proper exponent/fraction rendering at current position.
        Falls back to plain cell if no math detected. Returns y after writing."""
        clean = MathPDF._clean_text(text)
        if pdf._has_math(clean):
            pdf._write_line_with_math(clean, x, font_style, font_size)
        else:
            pdf.set_font(pdf.ff, font_style, font_size)
            pdf.set_x(x)
            pdf.cell(max_w, lh, clean, new_x="LMARGIN", new_y="NEXT")
        return pdf.get_y()

    # --- Helper: draw two-column problem row ---
    col_left_w = usable_w * 0.52
    col_right_w = usable_w * 0.48
    col_gap = 3  # mm gap between columns
    lh = 5  # line height for body text (compact)

    def _estimate_row_height(num, q, extra_notes=None):
        """Estimate the height a row will take by measuring text lines."""
        h = 0
        # Stem text
        stem = MathPDF._clean_text(q.stem_text.replace("[FIGURE]", "").strip())
        stem_lines = max(1, len(stem) // 40 + 1)  # rough chars per line
        h += stem_lines * lh + 6  # stem + number line

        # Choices + rationales
        if q.choices:
            for ch in q.choices:
                h += lh  # choice line
                if not ch.is_correct:
                    h += 5  # rationale line
        else:
            h += 20  # open-ended mistakes

        # Right column: answer + solution + misconception + scripts
        right_h = 5  # answer line
        if q.worked_solution:
            sol_lines = len([l for l in q.worked_solution.split("\n") if l.strip()][:2])
            right_h += sol_lines * 4
        right_h += 45  # watch for + stop/prompt/praise estimate (compact)

        if extra_notes:
            right_h += len(extra_notes) * 5

        return max(h, right_h) + 4  # +4 for divider + spacing

    def _draw_two_col_row(num, q, extra_notes=None):
        """Draw problem on left, answer + misconceptions on right."""
        # Estimate height and check if row fits on current page
        est_height = _estimate_row_height(num, q, extra_notes)
        remaining = pdf.h - pdf.get_y() - 15  # 15mm bottom margin
        if est_height > remaining:
            pdf.add_page()

        row_y = pdf.get_y()
        left_x = PAGE_MARGIN
        right_x = PAGE_MARGIN + col_left_w + col_gap

        # --- LEFT COLUMN: Problem ---
        pdf.set_xy(left_x, row_y)
        pdf.set_font(pdf.ff, "B", 11)
        pdf.set_text_color(*SB_DARK)
        pdf.cell(8, 6, f"{num}.", new_x="RIGHT", new_y="TOP")

        pdf.set_font(pdf.ff, "", 10)
        pdf.set_text_color(0, 0, 0)
        stem = MathPDF._clean_text(q.stem_text.replace("[FIGURE]", "").strip())
        pdf.multi_cell(col_left_w - 10, lh, stem, new_x="LMARGIN", new_y="NEXT")
        left_bottom = pdf.get_y()

        # Choices with per-choice rationales
        choice_info = _generate_choice_rationales(q)

        if q.choices:
            for ch in q.choices:
                if ch.is_correct:
                    pdf.set_text_color(34, 197, 94)  # green for correct
                    _write_math_cell(f"{ch.key}. {ch.text}", left_x + 10,
                                     col_left_w - 12, "B", 10)
                else:
                    pdf.set_text_color(0, 0, 0)
                    _write_math_cell(f"{ch.key}. {ch.text}", left_x + 10,
                                     col_left_w - 12, "", 10)
                pdf.set_text_color(0, 0, 0)

                # Add rationale for wrong choices in italics
                if not ch.is_correct and choice_info.get("type") == "mc":
                    rationale = choice_info["rationales"].get(ch.key, "")
                    if rationale:
                        pdf.set_x(left_x + 16)
                        pdf.set_font(pdf.ff, "I", 8)
                        pdf.set_text_color(150, 80, 80)
                        pdf.multi_cell(col_left_w - 18, 4,
                                       MathPDF._clean_text(rationale),
                                       new_x="LMARGIN", new_y="NEXT")
                        pdf.set_text_color(0, 0, 0)
            left_bottom = pdf.get_y()
        else:
            # Open-ended: show 2 common mistakes below the problem
            if choice_info.get("type") == "open":
                pdf.set_x(left_x + 4)
                pdf.ln(1)
                pdf.set_x(left_x + 4)
                pdf.set_font(pdf.ff, "B", 8)
                pdf.set_text_color(150, 80, 80)
                pdf.cell(col_left_w - 6, 4, "Common mistakes:",
                         new_x="LMARGIN", new_y="NEXT")
                pdf.set_font(pdf.ff, "I", 8)
                for mistake in choice_info.get("mistakes", []):
                    pdf.set_x(left_x + 6)
                    pdf.multi_cell(col_left_w - 8, 4,
                                   "- " + MathPDF._clean_text(mistake),
                                   new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(0, 0, 0)
            left_bottom = pdf.get_y()

        # --- RIGHT COLUMN: Answer + Notes ---
        pdf.set_xy(right_x, row_y)
        pdf.set_text_color(34, 197, 94)  # green
        _write_math_cell(f"Answer: {q.answer_text}", right_x, col_right_w, "B", 10)

        # Worked solution (compact, math-aware)
        if q.worked_solution:
            pdf.set_text_color(100, 100, 100)
            solution = q.worked_solution
            sol_lines = [l.strip() for l in solution.split("\n") if l.strip()]
            for sl in sol_lines[:2]:  # max 2 lines
                pdf.set_x(right_x)
                _write_math_cell(sl, right_x, col_right_w, "", 8)

        # Question-specific misconception (generated from the actual problem)
        m = _generate_question_specific_misconception(q)
        if m:
            pdf.set_x(right_x)
            pdf.ln(1)
            pdf.set_x(right_x)
            pdf.set_font(pdf.ff, "B", 8)
            pdf.set_text_color(239, 68, 68)  # red
            pdf.cell(col_right_w, 4, "WATCH FOR:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_x(right_x)
            pdf.set_font(pdf.ff, "I", 8)
            pdf.set_text_color(100, 100, 100)
            pdf.multi_cell(col_right_w, 3.5,
                           MathPDF._clean_text(m["description"]),
                           new_x="LMARGIN", new_y="NEXT")

            for label, key, color in [
                ("STOP", "stop", (239, 68, 68)),
                ("PROMPT", "prompt", (245, 158, 11)),
                ("PRAISE", "praise", (34, 197, 94)),
            ]:
                text = m.get(key, "")
                if not text:
                    continue
                pdf.set_x(right_x)
                pdf.set_font(pdf.ff, "B", 8)
                pdf.set_text_color(*color)
                pdf.cell(16, 4, label + ":", new_x="RIGHT", new_y="TOP")
                pdf.set_font(pdf.ff, "", 8)
                pdf.set_text_color(*SB_DARK)
                pdf.multi_cell(col_right_w - 17, 3.5,
                               MathPDF._clean_text(text),
                               new_x="LMARGIN", new_y="NEXT")

        # Extra notes (for guided practice prompts, etc.)
        if extra_notes:
            for note in extra_notes:
                pdf.set_x(right_x)
                pdf.set_font(pdf.ff, "I", 8)
                pdf.set_text_color(64, 139, 251)
                pdf.multi_cell(col_right_w, 3.5,
                               MathPDF._clean_text(note),
                               new_x="LMARGIN", new_y="NEXT")

        right_bottom = pdf.get_y()
        pdf.set_text_color(0, 0, 0)

        # Use the taller column
        row_bottom = max(left_bottom, right_bottom)
        pdf.set_y(row_bottom)

        # Divider line
        pdf.ln(1)
        pdf.set_draw_color(*SB_YELLOW)
        pdf.set_line_width(0.4)
        pdf.line(PAGE_MARGIN, pdf.get_y(), pdf.w - PAGE_MARGIN, pdf.get_y())
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.3)
        pdf.ln(1.5)

    # --- Helper: draw phase header bar ---
    def _draw_phase_bar(title, time_str, color):
        # If less than 20% of usable page height remains, start a new page
        usable_h = pdf.h - 25
        remaining_pct = (pdf.h - pdf.get_y() - 15) / usable_h
        if remaining_pct < 0.20:
            pdf.add_page()
        y = pdf.get_y()
        pdf.set_fill_color(*color)
        pdf.rect(PAGE_MARGIN, y, usable_w, 7, style="F")
        pdf.set_font(pdf.ff, "B", 11)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(PAGE_MARGIN + 3, y + 1)
        pdf.cell(0, 5, f"{title}  ({time_str})")
        pdf.set_text_color(0, 0, 0)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_y(y + 9)

    # ====================================================
    # PHASE 1: DIAGNOSE
    # ====================================================
    n_diag = len(diagnose_qs)
    n_prac = len(practice_qs)
    _draw_phase_bar("PRE-ASSESSMENT", "5 min", (64, 139, 251))

    num = 1
    for q in diagnose_qs:
        _draw_two_col_row(num, q)
        num += 1

    # ====================================================
    # PHASE 2: MODEL
    # ====================================================
    pdf.ln(1)
    _draw_phase_bar("MODEL", "5 min", (245, 158, 11))

    teaching = intervention_data.get("teaching_script", {})

    # I Do script
    pdf.set_font(pdf.ff, "B", 10)
    pdf.set_text_color(64, 139, 251)
    pdf.cell(0, 5, "I Do (Teacher Models) - Read this aloud:",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(pdf.ff, "", 9)
    pdf.set_text_color(*SB_DARK)
    pdf.multi_cell(usable_w, 5,
                   MathPDF._clean_text(teaching.get("i_do", "")),
                   new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    # Key vocabulary (compact inline)
    vocab = intervention_data.get("vocabulary", [])
    if vocab:
        pdf.set_font(pdf.ff, "B", 9)
        pdf.set_text_color(*SB_DARK)
        pdf.cell(0, 5, "Key Vocabulary:", new_x="LMARGIN", new_y="NEXT")
        for v in vocab:
            term = MathPDF._clean_text(v.get("term", ""))
            defn = MathPDF._clean_text(v.get("definition", ""))
            pdf.set_font(pdf.ff, "B", 9)
            pdf.cell(pdf.get_string_width(term) + 2, 5, term + ": ",
                     new_x="RIGHT", new_y="TOP")
            pdf.set_font(pdf.ff, "", 9)
            pdf.multi_cell(usable_w - pdf.get_string_width(term) - 4, 5,
                           defn, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    # ====================================================
    # PHASE 3: GUIDED PRACTICE
    # ====================================================
    pdf.ln(1)
    _draw_phase_bar("GUIDED PRACTICE", "10 min", (245, 158, 11))

    # We Do script first
    pdf.set_font(pdf.ff, "B", 10)
    pdf.set_text_color(245, 158, 11)
    pdf.cell(0, 5, "We Do (Guided Practice) - Work through together:",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(pdf.ff, "", 9)
    pdf.set_text_color(*SB_DARK)
    pdf.multi_cell(usable_w, 5,
                   MathPDF._clean_text(teaching.get("we_do", "")),
                   new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    # Practice problems with prompts
    guided_prompts = [
        "Ask: \"What should we do first?\"",
        "Ask: \"Why did you choose that step?\"",
    ]
    for q in practice_qs:
        _draw_two_col_row(num, q, extra_notes=guided_prompts)
        num += 1

    # ====================================================
    # PHASE 4: INDEPENDENT PRACTICE
    # ====================================================
    # (independent problems are actually the exit check)

    # ====================================================
    # PHASE 5: EXIT CHECK + REFLECT
    # ====================================================
    pdf.ln(1)
    _draw_phase_bar("EXIT TICKET + REFLECT", "5 min", (255, 83, 72))

    for q in exit_qs:
        _draw_two_col_row(num, q, extra_notes=[
            "If correct: Ready to move on!",
            "If wrong: Repeat this skill next session.",
        ])
        num += 1

    pdf.ln(1)
    pdf.set_font(pdf.ff, "B", 10)
    pdf.set_text_color(*SB_DARK)
    pdf.cell(0, 5, "Reflection Prompts (ask the student):",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(pdf.ff, "", 9)
    pdf.cell(0, 5, "- \"What mistake did I used to make?\"",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "- \"How will I avoid it next time?\"",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "- \"What strategy works best for me?\"",
             new_x="LMARGIN", new_y="NEXT")

    # ====================================================
    # FINAL PAGE: Prerequisites (if gap identified)
    # ====================================================
    prereqs = intervention_data.get("prerequisite_skills", [])
    if prereqs:
        pdf.ln(2)
        if pdf.get_y() > pdf.h - 40:
            pdf.add_page()
        _draw_intervention_section_header(pdf, "If You Identified a Prerequisite Gap")
        pdf.set_font(pdf.ff, "I", 7.5)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 4, "Use these quick-check questions to pinpoint what the student is missing:",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)
        prereq_rows = [[p.get("skill", ""), p.get("grade_level", ""),
                         p.get("check_question", ""),
                         p.get("follow_up", f"Reteach {p.get('skill', 'this skill')} before retrying this standard.")]
                       for p in prereqs]
        _draw_intervention_table(pdf,
            ["Skill", "Grade", "Quick-Check Question", "If Student Misses This"],
            prereq_rows,
            [usable_w * 0.18, usable_w * 0.10, usable_w * 0.37, usable_w * 0.35])

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    pdf.output(output_path)
    return output_path


# ============================================================
# THINKING CLASSROOM TASK SLIDES PDF
# ============================================================

def generate_task_slides_pdf(tasks, output_path):
    """Generate a landscape PDF with one slide per task for classroom projection.

    Args:
        tasks: list of task dicts from the database
        output_path: where to save the PDF
    Returns:
        output_path
    """
    pdf = MathPDF(orientation='L', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)

    page_w = 297  # A4 landscape width mm
    page_h = 210  # A4 landscape height mm
    margin = 15
    usable_w = page_w - 2 * margin

    for task in tasks:
        pdf.add_page()

        # --- Yellow header bar ---
        pdf.set_fill_color(*SB_YELLOW)
        pdf.rect(0, 0, page_w, 18, style='F')

        # Standard badges (left)
        pdf.set_xy(margin, 3)
        pdf.set_font(pdf.ff, "B", 12)
        pdf.set_text_color(*SB_DARK)
        standards = task.get('indiana_standards', '')
        pdf.cell(usable_w * 0.7, 12, standards)

        # Grade (right)
        grade = task.get('grade_level', '')
        pdf.set_xy(page_w - margin - 60, 3)
        pdf.set_font(pdf.ff, "B", 12)
        pdf.cell(60, 12, f"Grade {grade}", align='R')

        # --- Title ---
        pdf.set_y(28)
        pdf.set_font(pdf.ff, "B", 28)
        pdf.set_text_color(*SB_DARK)
        title = task.get('title', 'Untitled')
        pdf.set_x(margin)
        pdf.multi_cell(usable_w, 14, title, align='C')

        pdf.ln(5)

        # --- Task text (large, readable) ---
        pdf.set_font(pdf.ff, "", 20)
        pdf.set_text_color(55, 55, 55)
        task_text = MathPDF._clean_text(task.get('task_text', ''))
        pdf.set_x(margin + 10)
        pdf.multi_cell(usable_w - 20, 10, task_text, align='L')

        # --- Launch prompt section ---
        launch = task.get('launch_prompt', '')
        if launch:
            y_before_launch = pdf.get_y()
            # Only draw if there's room (at least 40mm)
            if y_before_launch < page_h - 55:
                pdf.ln(6)

                # Launch prompt background box
                launch_y = pdf.get_y()
                pdf.set_fill_color(255, 251, 235)  # cream
                pdf.set_draw_color(*SB_YELLOW)
                pdf.set_line_width(0.8)

                # Measure text height first
                pdf.set_font(pdf.ff, "I", 14)
                launch_clean = MathPDF._clean_text(launch)

                # Draw box
                box_x = margin + 5
                box_w = usable_w - 10
                pdf.rect(box_x, launch_y, box_w, 30, style='DF')

                # Label
                pdf.set_xy(box_x + 5, launch_y + 2)
                pdf.set_font(pdf.ff, "B", 11)
                pdf.set_text_color(180, 130, 0)
                pdf.cell(0, 6, "HOW TO LAUNCH THIS TASK:")
                pdf.set_xy(box_x + 5, launch_y + 9)
                pdf.set_font(pdf.ff, "I", 13)
                pdf.set_text_color(80, 70, 40)
                pdf.multi_cell(box_w - 10, 6, launch_clean)

        # --- Footer bar ---
        pdf.set_y(page_h - 18)
        pdf.set_fill_color(240, 240, 240)
        pdf.rect(0, page_h - 18, page_w, 18, style='F')

        pdf.set_xy(margin, page_h - 15)
        pdf.set_font(pdf.ff, "", 10)
        pdf.set_text_color(120, 120, 120)

        dok = task.get('dok_level', 2)
        entry = task.get('entry_type', '').replace('_', ' ').title()
        source = task.get('source_name', 'Original')
        footer_text = f"DOK: {dok}  |  Entry: {entry}  |  Source: {source}"
        pdf.cell(usable_w * 0.7, 10, footer_text)

        # Plug N Play branding (right)
        pdf.set_x(page_w - margin - 80)
        pdf.set_font(pdf.ff, "B", 10)
        pdf.set_text_color(*SB_DARK)
        pdf.cell(80, 10, "Plug N Play", align='R')

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    pdf.output(output_path)
    return output_path


# ============================================================
# CLI ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

    from engine.stems.stem_6af3 import Stem6AF3

    gen = Stem6AF3(seed=42)
    questions = gen.generate_all_variants(variants_per_stem=2)

    output = os.path.join(os.path.dirname(__file__), '..', '.tmp', 'test_worksheet.pdf')
    generate_worksheet_pdf(
        questions=questions[:10],
        output_path=output,
        standard_code="6.AF.3",
        standard_text="Solve equations of the form x + p = q, x - p = q, px = q, and x/p = q",
        include_answer_key=True
    )
