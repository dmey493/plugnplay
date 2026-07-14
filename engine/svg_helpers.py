"""
SVG generation helpers using drawsvg.
Each function returns an SVG string suitable for embedding in HTML.
"""

import math
import drawsvg as draw


# ============================================================
# RIGHT TRIANGLE
# ============================================================

def right_triangle_svg(a, b, c, labels=None, unit="", right_angle_vertex="C",
                       width=280, height=220):
    """Draw a right triangle with labeled sides and a right-angle marker.

    a, b = legs; c = hypotenuse.
    labels: dict mapping side names to display strings, e.g. {"a": "6", "b": "?", "c": "10"}.
    right_angle_vertex: which vertex has the right angle (always "C" = bottom-left).

    Layout:
      C (bottom-left, right angle) ---- B (bottom-right)
      |                               /
      |                             /
      A (top-left)

    Side a = CB (horizontal leg, bottom)
    Side b = CA (vertical leg, left)
    Side c = AB (hypotenuse, diagonal)
    """
    if labels is None:
        labels = {"a": str(a), "b": str(b), "c": str(c)}

    d = draw.Drawing(width, height)

    margin = 40
    # Triangle vertices
    cx, cy = margin, height - margin          # C (bottom-left, right angle)
    bx, by = width - margin, height - margin  # B (bottom-right)
    ax, ay = margin, margin                   # A (top-left)

    # Draw triangle
    d.append(draw.Lines(cx, cy, bx, by, ax, ay, close=True,
                        fill='#e8f4fd', stroke='#2563eb', stroke_width=2))

    # Right angle marker at C
    sq = 15
    d.append(draw.Lines(cx + sq, cy, cx + sq, cy - sq, cx, cy - sq,
                        close=False, fill='none', stroke='#2563eb', stroke_width=1.5))

    # Label side a (bottom: C to B)
    a_label = labels.get("a", str(a))
    if unit and a_label != "?":
        a_label = f"{a_label} {unit}"
    d.append(draw.Text(a_label, 30, (cx + bx) / 2, cy + 28,
                        text_anchor='middle', fill='#1e40af', font_weight='bold'))

    # Label side b (left: C to A)
    b_label = labels.get("b", str(b))
    if unit and b_label != "?":
        b_label = f"{b_label} {unit}"
    d.append(draw.Text(b_label, 30, cx - 32, (cy + ay) / 2,
                        text_anchor='middle', fill='#1e40af', font_weight='bold'))

    # Label side c (hypotenuse: A to B)
    c_label = labels.get("c", str(c))
    if unit and c_label != "?":
        c_label = f"{c_label} {unit}"
    mid_hx = (ax + bx) / 2 + 14
    mid_hy = (ay + by) / 2 - 10
    d.append(draw.Text(c_label, 30, mid_hx, mid_hy,
                        text_anchor='middle', fill='#1e40af', font_weight='bold'))

    # Vertex labels
    d.append(draw.Text('C', 24, cx - 18, cy + 6, fill='#6b7280'))
    d.append(draw.Text('B', 24, bx + 10, by + 6, fill='#6b7280'))
    d.append(draw.Text('A', 24, ax - 18, ay + 6, fill='#6b7280'))

    return d.as_svg()


# ============================================================
# CIRCLE
# ============================================================

def circle_svg(radius_val, label_text="", show_radius=True, show_diameter=False,
               width=240, height=240):
    """Draw a circle with optional radius/diameter line and label.

    radius_val: numeric value to display.
    label_text: override label (e.g. "r = 7 cm").
    """
    d = draw.Drawing(width, height)
    cx, cy = width / 2, height / 2
    r_px = min(width, height) / 2 - 30  # pixel radius

    # Circle
    d.append(draw.Circle(cx, cy, r_px,
                          fill='#e8f4fd', stroke='#2563eb', stroke_width=2))

    # Center dot
    d.append(draw.Circle(cx, cy, 2.5, fill='#2563eb'))

    if show_diameter:
        # Diameter line (horizontal through center)
        d.append(draw.Line(cx - r_px, cy, cx + r_px, cy,
                           stroke='#2563eb', stroke_width=1.5,
                           stroke_dasharray='6,3'))
        lbl = label_text if label_text else f"d = {radius_val}"
        d.append(draw.Text(lbl, 30, cx, cy - 12,
                           text_anchor='middle', fill='#1e40af', font_weight='bold'))
    elif show_radius:
        # Radius line (center to right)
        d.append(draw.Line(cx, cy, cx + r_px, cy,
                           stroke='#2563eb', stroke_width=1.5,
                           stroke_dasharray='6,3'))
        lbl = label_text if label_text else f"r = {radius_val}"
        d.append(draw.Text(lbl, 30, cx + r_px / 2, cy - 12,
                           text_anchor='middle', fill='#1e40af', font_weight='bold'))

    return d.as_svg()


# ============================================================
# ANNULUS (concentric circles / ring)
# ============================================================

def annulus_svg(r_outer, r_inner, label_outer="", label_inner="",
               width=280, height=280):
    """Draw two concentric circles with the ring region shaded.

    r_outer / r_inner: numeric values for labels (not pixel sizes).
    The shaded region is between the two circles.
    """
    d = draw.Drawing(width, height)
    cx, cy = width / 2, height / 2
    outer_px = min(width, height) / 2 - 30
    inner_px = outer_px * (r_inner / r_outer)

    # Shaded ring using a path with fill-rule evenodd
    # Outer circle clockwise, inner circle counter-clockwise
    ring = draw.Path(fill='#e8f4fd', stroke='none', fill_rule='evenodd')
    # Outer circle (two arcs to form a full circle)
    ring.M(cx + outer_px, cy)
    ring.A(outer_px, outer_px, 0, True, True, cx - outer_px, cy)
    ring.A(outer_px, outer_px, 0, True, True, cx + outer_px, cy)
    ring.Z()
    # Inner circle (two arcs, opposite sweep to cut the hole)
    ring.M(cx + inner_px, cy)
    ring.A(inner_px, inner_px, 0, True, False, cx - inner_px, cy)
    ring.A(inner_px, inner_px, 0, True, False, cx + inner_px, cy)
    ring.Z()
    d.append(ring)

    # Outer circle stroke
    d.append(draw.Circle(cx, cy, outer_px,
                         fill='none', stroke='#2563eb', stroke_width=2))
    # Inner circle stroke
    d.append(draw.Circle(cx, cy, inner_px,
                         fill='none', stroke='#2563eb', stroke_width=2))

    # White fill for inner circle (the hole)
    d.append(draw.Circle(cx, cy, inner_px,
                         fill='white', stroke='none'))
    # Re-draw inner circle stroke on top
    d.append(draw.Circle(cx, cy, inner_px,
                         fill='none', stroke='#2563eb', stroke_width=2))

    # Center dot
    d.append(draw.Circle(cx, cy, 2.5, fill='#2563eb'))

    # Outer radius line (center to right edge of outer circle)
    d.append(draw.Line(cx, cy, cx + outer_px, cy,
                       stroke='#2563eb', stroke_width=1.5,
                       stroke_dasharray='6,3'))

    # Outer radius label
    lbl_outer = label_outer if label_outer else f"R = {r_outer}"
    d.append(draw.Text(lbl_outer, 26, cx + outer_px / 2, cy - 12,
                       text_anchor='middle', fill='#1e40af', font_weight='bold'))

    # Inner radius line (center to right edge of inner circle, slightly below)
    d.append(draw.Line(cx, cy + 6, cx + inner_px, cy + 6,
                       stroke='#dc2626', stroke_width=1.5,
                       stroke_dasharray='6,3'))

    # Inner radius label
    lbl_inner = label_inner if label_inner else f"r = {r_inner}"
    d.append(draw.Text(lbl_inner, 24, cx + inner_px / 2, cy + 28,
                       text_anchor='middle', fill='#dc2626', font_weight='bold'))

    return d.as_svg()


# ============================================================
# SIMPLE RECTANGLE DIAGRAM
# ============================================================

def rectangle_svg(w_val, h_val, label_w=None, label_h=None, title="",
                  unit="", width=300, height=200):
    """Draw a single labeled rectangle (floor plan / blueprint style).

    w_val, h_val: numeric values for dimension labels.
    """
    d = draw.Drawing(width, height)

    margin_x = 50
    margin_top = 30 if not title else 50
    margin_bot = 30

    rect_w = width - 2 * margin_x
    rect_h = height - margin_top - margin_bot

    rx, ry = margin_x, margin_top

    # Rectangle
    d.append(draw.Rectangle(rx, ry, rect_w, rect_h,
                            fill='#fef3c7', stroke='#d97706', stroke_width=2))

    # Title above rectangle
    if title:
        d.append(draw.Text(title, 24, width / 2, 20,
                           text_anchor='middle', fill='#374151', font_weight='bold'))

    # Width label (bottom) — None = auto from values, "" = hide
    if label_w != "":
        lbl_w = label_w if label_w else (f"{w_val} {unit}" if unit else str(w_val))
        d.append(draw.Text(lbl_w, 24, rx + rect_w / 2, ry + rect_h + 22,
                           text_anchor='middle', fill='#1e40af', font_weight='bold'))

    # Height label (right side) — None = auto from values, "" = hide
    if label_h != "":
        lbl_h = label_h if label_h else (f"{h_val} {unit}" if unit else str(h_val))
        d.append(draw.Text(lbl_h, 24, rx + rect_w + 8, ry + rect_h / 2,
                           text_anchor='start', fill='#1e40af', font_weight='bold',
                           transform=f'rotate(90,{rx + rect_w + 8},{ry + rect_h / 2})'))

    return d.as_svg()


# ============================================================
# CYLINDER (pseudo-3D)
# ============================================================

def cylinder_3d_svg(radius_val, height_val, label_r="", label_h="",
                     width=240, height=280):
    """Draw a pseudo-3D cylinder with labeled radius and height."""
    d = draw.Drawing(width, height)
    cx = width / 2
    margin_top = 50
    margin_bot = 40
    r_px = min(width / 2 - 30, 80)  # pixel radius
    h_px = height - margin_top - margin_bot - 40  # pixel height
    ey = r_px * 0.35  # ellipse y-radius

    top_cy = margin_top + ey
    bot_cy = top_cy + h_px

    # Side lines
    d.append(draw.Line(cx - r_px, top_cy, cx - r_px, bot_cy,
                       stroke='#2563eb', stroke_width=2))
    d.append(draw.Line(cx + r_px, top_cy, cx + r_px, bot_cy,
                       stroke='#2563eb', stroke_width=2))

    # Bottom ellipse (full, behind)
    d.append(draw.Ellipse(cx, bot_cy, r_px, ey,
                          fill='#dbeafe', stroke='#2563eb', stroke_width=2))

    # Body fill
    d.append(draw.Rectangle(cx - r_px, top_cy, 2 * r_px, h_px,
                             fill='#e8f4fd', stroke='none'))

    # Top ellipse (full, on top)
    d.append(draw.Ellipse(cx, top_cy, r_px, ey,
                          fill='#bfdbfe', stroke='#2563eb', stroke_width=2))

    # Bottom ellipse front arc (redraw on top of body fill)
    p = draw.Path(fill='none', stroke='#2563eb', stroke_width=2)
    p.M(cx - r_px, bot_cy)
    p.A(r_px, ey, 0, 0, 0, cx + r_px, bot_cy)
    d.append(p)

    # Radius line on top ellipse
    d.append(draw.Line(cx, top_cy, cx + r_px, top_cy,
                       stroke='#dc2626', stroke_width=1.5,
                       stroke_dasharray='5,3'))
    d.append(draw.Circle(cx, top_cy, 2, fill='#dc2626'))

    # Radius label
    r_lbl = label_r if label_r else f"r = {radius_val}"
    d.append(draw.Text(r_lbl, 30, cx + r_px / 2, top_cy - 16,
                       text_anchor='middle', fill='#dc2626', font_weight='bold'))

    # Height line (right side, outside)
    hx = cx + r_px + 18
    d.append(draw.Line(hx, top_cy, hx, bot_cy,
                       stroke='#dc2626', stroke_width=1.5))
    # Arrow heads
    d.append(draw.Lines(hx - 4, top_cy + 6, hx, top_cy, hx + 4, top_cy + 6,
                        close=False, fill='none', stroke='#dc2626', stroke_width=1.5))
    d.append(draw.Lines(hx - 4, bot_cy - 6, hx, bot_cy, hx + 4, bot_cy - 6,
                        close=False, fill='none', stroke='#dc2626', stroke_width=1.5))

    h_lbl = label_h if label_h else f"h = {height_val}"
    d.append(draw.Text(h_lbl, 30, hx + 10, (top_cy + bot_cy) / 2,
                       text_anchor='start', fill='#dc2626', font_weight='bold',
                       dominant_baseline='middle'))

    return d.as_svg()


# ============================================================
# CONE (pseudo-3D)
# ============================================================

def cone_3d_svg(radius_val, height_val, slant_val=None,
                label_r="", label_h="", label_s="",
                width=240, height=280):
    """Draw a pseudo-3D cone with labeled radius, height, and optional slant height."""
    d = draw.Drawing(width, height)
    cx = width / 2
    margin_top = 40
    margin_bot = 40
    r_px = min(width / 2 - 30, 80)
    h_px = height - margin_top - margin_bot - 20
    ey = r_px * 0.3

    apex_y = margin_top
    base_cy = margin_top + h_px

    # Side lines (from apex to base circle tangent points)
    d.append(draw.Line(cx, apex_y, cx - r_px, base_cy,
                       stroke='#2563eb', stroke_width=2))
    d.append(draw.Line(cx, apex_y, cx + r_px, base_cy,
                       stroke='#2563eb', stroke_width=2))

    # Base ellipse (back half dashed, front half solid)
    # Back half (top arc, dashed)
    p_back = draw.Path(fill='none', stroke='#2563eb', stroke_width=1.5,
                       stroke_dasharray='5,3')
    p_back.M(cx - r_px, base_cy)
    p_back.A(r_px, ey, 0, 0, 1, cx + r_px, base_cy)
    d.append(p_back)
    # Front half (bottom arc, solid)
    p_front = draw.Path(fill='none', stroke='#2563eb', stroke_width=2)
    p_front.M(cx - r_px, base_cy)
    p_front.A(r_px, ey, 0, 0, 0, cx + r_px, base_cy)
    d.append(p_front)

    # Fill the cone body (triangle + ellipse area)
    d.append(draw.Lines(cx, apex_y, cx - r_px, base_cy, cx + r_px, base_cy,
                        close=True, fill='#e8f4fd', stroke='none', opacity=0.5))

    # Dashed height line
    d.append(draw.Line(cx, apex_y, cx, base_cy,
                       stroke='#dc2626', stroke_width=1.5,
                       stroke_dasharray='5,3'))

    # Radius line on base
    d.append(draw.Line(cx, base_cy, cx + r_px, base_cy,
                       stroke='#dc2626', stroke_width=1.5,
                       stroke_dasharray='5,3'))
    d.append(draw.Circle(cx, base_cy, 2, fill='#dc2626'))

    # Labels
    r_lbl = label_r if label_r else f"r = {radius_val}"
    d.append(draw.Text(r_lbl, 30, cx + r_px / 2, base_cy + 28,
                       text_anchor='middle', fill='#dc2626', font_weight='bold'))

    h_lbl = label_h if label_h else f"h = {height_val}"
    d.append(draw.Text(h_lbl, 30, cx + 12, (apex_y + base_cy) / 2,
                       text_anchor='start', fill='#dc2626', font_weight='bold'))

    # Optional slant height label
    if slant_val is not None:
        s_lbl = label_s if label_s else f"l = {slant_val}"
        d.append(draw.Text(s_lbl, 30, cx - r_px / 2 - 20, (apex_y + base_cy) / 2,
                           text_anchor='middle', fill='#1e40af', font_weight='bold'))

    return d.as_svg()


# ============================================================
# SPHERE
# ============================================================

def sphere_svg(radius_val, label_text="", width=240, height=240):
    """Draw a sphere with equatorial ellipse and radius line."""
    d = draw.Drawing(width, height)
    cx, cy = width / 2, height / 2
    r_px = min(width, height) / 2 - 30

    # Main circle
    d.append(draw.Circle(cx, cy, r_px,
                         fill='#e8f4fd', stroke='#2563eb', stroke_width=2))

    # Equatorial ellipse (dashed)
    d.append(draw.Ellipse(cx, cy, r_px, r_px * 0.3,
                          fill='none', stroke='#2563eb', stroke_width=1,
                          stroke_dasharray='4,3'))

    # Radius line
    d.append(draw.Line(cx, cy, cx + r_px, cy,
                       stroke='#dc2626', stroke_width=1.5,
                       stroke_dasharray='5,3'))
    d.append(draw.Circle(cx, cy, 2.5, fill='#dc2626'))

    lbl = label_text if label_text else f"r = {radius_val}"
    d.append(draw.Text(lbl, 30, cx + r_px / 2, cy - 14,
                       text_anchor='middle', fill='#dc2626', font_weight='bold'))

    return d.as_svg()


# ============================================================
# SQUARE PYRAMID (pseudo-3D)
# ============================================================

def pyramid_3d_svg(base_side, height_val, label_base="", label_h="",
                    width=280, height=280):
    """Draw a right square pyramid in pseudo-3D with labeled base and height."""
    d = draw.Drawing(width, height)
    cx = width / 2
    margin = 40

    # Base square in pseudo-3D (parallelogram)
    base_px = min(width - 2 * margin, 160)
    half_b = base_px / 2
    depth = half_b * 0.4  # foreshortened depth

    apex_y = margin + 10
    base_y = height - margin - 10

    # Base corners (parallelogram approximation)
    bl = (cx - half_b, base_y)                          # front-left
    br = (cx + half_b, base_y)                          # front-right
    tr = (cx + half_b + depth * 0.6, base_y - depth)    # back-right
    tl = (cx - half_b + depth * 0.6, base_y - depth)    # back-left

    apex = (cx + depth * 0.3, apex_y)

    # Back edges (dashed - hidden)
    d.append(draw.Line(tl[0], tl[1], tr[0], tr[1],
                       stroke='#2563eb', stroke_width=1.5,
                       stroke_dasharray='5,3'))
    d.append(draw.Line(bl[0], bl[1], tl[0], tl[1],
                       stroke='#2563eb', stroke_width=1.5,
                       stroke_dasharray='5,3'))

    # Back edges to apex (dashed)
    d.append(draw.Line(tl[0], tl[1], apex[0], apex[1],
                       stroke='#2563eb', stroke_width=1.5,
                       stroke_dasharray='5,3'))

    # Visible faces
    # Front face
    d.append(draw.Lines(bl[0], bl[1], br[0], br[1], apex[0], apex[1],
                        close=True, fill='#e8f4fd', stroke='#2563eb', stroke_width=2))
    # Right face
    d.append(draw.Lines(br[0], br[1], tr[0], tr[1], apex[0], apex[1],
                        close=True, fill='#dbeafe', stroke='#2563eb', stroke_width=2))

    # Front base edge
    d.append(draw.Line(bl[0], bl[1], br[0], br[1],
                       stroke='#2563eb', stroke_width=2))
    # Right base edge
    d.append(draw.Line(br[0], br[1], tr[0], tr[1],
                       stroke='#2563eb', stroke_width=2))

    # Dashed height line from apex to base center
    base_center = ((bl[0] + tr[0]) / 2, (bl[1] + tr[1]) / 2)
    d.append(draw.Line(apex[0], apex[1], base_center[0], base_center[1],
                       stroke='#dc2626', stroke_width=1.5,
                       stroke_dasharray='5,3'))

    # Right angle at base center
    sq = 8
    d.append(draw.Lines(base_center[0] + sq, base_center[1],
                        base_center[0] + sq, base_center[1] - sq,
                        base_center[0], base_center[1] - sq,
                        close=False, fill='none', stroke='#dc2626', stroke_width=1))

    # Labels
    b_lbl = label_base if label_base else f"s = {base_side}"
    d.append(draw.Text(b_lbl, 30, (bl[0] + br[0]) / 2, base_y + 28,
                       text_anchor='middle', fill='#1e40af', font_weight='bold'))

    h_lbl = label_h if label_h else f"h = {height_val}"
    d.append(draw.Text(h_lbl, 30, base_center[0] + 14, (apex[1] + base_center[1]) / 2,
                       text_anchor='start', fill='#dc2626', font_weight='bold'))

    return d.as_svg()


# ============================================================
# SCALE DRAWING PAIR (two similar polygons side by side)
# ============================================================

def scale_pair_svg(actual_sides, drawing_sides, shape_type="rectangle",
                   label_a="Figure A", label_b="Figure B",
                   unit_a="", unit_b="", width=480, height=240,
                   dim_labels_a=None, dim_labels_b=None):
    """Draw two similar polygons side by side for scale drawing problems.

    actual_sides: list of numeric side lengths for Figure A.
    drawing_sides: list of numeric side lengths for Figure B.
    shape_type: "rectangle" or "triangle".
    """
    d = draw.Drawing(width, height)
    half_w = width / 2
    margin = 30

    if shape_type == "rectangle":
        # Figure A (left side)
        max_a = max(actual_sides[:2])
        scale_a = min((half_w - 2 * margin) / max_a, (height - 2 * margin - 20) / max(actual_sides[1], 1)) * 0.8
        aw = actual_sides[0] * scale_a
        ah = actual_sides[1] * scale_a
        ax = margin + (half_w - 2 * margin - aw) / 2
        ay = margin + (height - 2 * margin - 20 - ah) / 2

        d.append(draw.Rectangle(ax, ay, aw, ah,
                                fill='#e8f4fd', stroke='#2563eb', stroke_width=2))

        la = (dim_labels_a[0] if dim_labels_a else f"{actual_sides[0]}") + (f" {unit_a}" if unit_a else "")
        d.append(draw.Text(la, 15, ax + aw / 2, ay + ah + 15,
                           text_anchor='middle', fill='#1e40af', font_weight='bold'))
        lb = (dim_labels_a[1] if dim_labels_a else f"{actual_sides[1]}") + (f" {unit_a}" if unit_a else "")
        d.append(draw.Text(lb, 15, ax - 8, ay + ah / 2,
                           text_anchor='end', fill='#1e40af', font_weight='bold',
                           dominant_baseline='middle'))

        d.append(draw.Text(label_a, 16, half_w / 2, height - 8,
                           text_anchor='middle', fill='#6b7280', font_weight='bold'))

        # Figure B (right side)
        max_b = max(drawing_sides[:2])
        scale_b = min((half_w - 2 * margin) / max_b, (height - 2 * margin - 20) / max(drawing_sides[1], 1)) * 0.8
        bw = drawing_sides[0] * scale_b
        bh = drawing_sides[1] * scale_b
        bx = half_w + margin + (half_w - 2 * margin - bw) / 2
        by = margin + (height - 2 * margin - 20 - bh) / 2

        d.append(draw.Rectangle(bx, by, bw, bh,
                                fill='#fef3c7', stroke='#d97706', stroke_width=2))

        la2 = (dim_labels_b[0] if dim_labels_b else f"{drawing_sides[0]}") + (f" {unit_b}" if unit_b else "")
        d.append(draw.Text(la2, 15, bx + bw / 2, by + bh + 15,
                           text_anchor='middle', fill='#92400e', font_weight='bold'))
        lb2 = (dim_labels_b[1] if dim_labels_b else f"{drawing_sides[1]}") + (f" {unit_b}" if unit_b else "")
        d.append(draw.Text(lb2, 15, bx - 8, by + bh / 2,
                           text_anchor='end', fill='#92400e', font_weight='bold',
                           dominant_baseline='middle'))

        d.append(draw.Text(label_b, 16, half_w + half_w / 2, height - 8,
                           text_anchor='middle', fill='#6b7280', font_weight='bold'))

    elif shape_type == "triangle":
        # Simple triangles (isoceles/right) side by side
        # actual_sides = [base, height_side], drawing_sides = [base, height_side]
        for i, (sides, lbl, x_off, fill_c, stroke_c, txt_c) in enumerate([
            (actual_sides, label_a, 0, '#e8f4fd', '#2563eb', '#1e40af'),
            (drawing_sides, label_b, half_w, '#fef3c7', '#d97706', '#92400e'),
        ]):
            max_s = max(sides[:2])
            sc = min((half_w - 2 * margin) / max_s, (height - 2 * margin - 20) / max(sides[1], 1)) * 0.7
            bw = sides[0] * sc
            bh = sides[1] * sc
            cx_t = x_off + half_w / 2
            bot_y = height - margin - 20

            p1 = (cx_t - bw / 2, bot_y)
            p2 = (cx_t + bw / 2, bot_y)
            p3 = (cx_t, bot_y - bh)

            d.append(draw.Lines(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1],
                                close=True, fill=fill_c, stroke=stroke_c, stroke_width=2))

            u = unit_a if i == 0 else unit_b
            dlabels = dim_labels_a if i == 0 else dim_labels_b
            bl_str = (dlabels[0] if dlabels else f"{sides[0]}") + (f" {u}" if u else "")
            d.append(draw.Text(bl_str, 15, cx_t, bot_y + 15,
                               text_anchor='middle', fill=txt_c, font_weight='bold'))

            hl_str = (dlabels[1] if dlabels else f"{sides[1]}") + (f" {u}" if u else "")
            d.append(draw.Text(hl_str, 15, p3[0] - 15, (p3[1] + p1[1]) / 2,
                               text_anchor='end', fill=txt_c, font_weight='bold',
                               dominant_baseline='middle'))

            d.append(draw.Text(lbl, 16, x_off + half_w / 2, height - 5,
                               text_anchor='middle', fill='#6b7280', font_weight='bold'))

    return d.as_svg()


# ============================================================
# COORDINATE GRID WITH POLYGON(S)
# ============================================================

def coord_grid_polygon_svg(x_range, y_range, preimage=None, image=None,
                            pre_label="", img_label="",
                            pre_color='#2563eb', img_color='#dc2626',
                            width=360, height=360):
    """Draw a coordinate grid with one or two polygons.

    x_range: (min_x, max_x) for axis.
    y_range: (min_y, max_y) for axis.
    preimage: list of (x,y) vertices for the preimage polygon.
    image: list of (x,y) vertices for the image polygon (optional).
    pre_label/img_label: vertex label prefix (e.g. "" uses A,B,C; "'" appended).
    """
    d = draw.Drawing(width, height)
    margin = 45

    x_min, x_max = x_range
    y_min, y_max = y_range
    gw = width - 2 * margin
    gh = height - 2 * margin

    def to_px(x, y):
        px = margin + (x - x_min) / (x_max - x_min) * gw
        py = margin + (y_max - y) / (y_max - y_min) * gh
        return px, py

    # Grid lines
    for x in range(x_min, x_max + 1):
        px, _ = to_px(x, 0)
        d.append(draw.Line(px, margin, px, margin + gh,
                           stroke='#e5e7eb', stroke_width=0.5))
    for y in range(y_min, y_max + 1):
        _, py = to_px(0, y)
        d.append(draw.Line(margin, py, margin + gw, py,
                           stroke='#e5e7eb', stroke_width=0.5))

    # Axes
    if x_min <= 0 <= x_max:
        ax_px, _ = to_px(0, 0)
        d.append(draw.Line(ax_px, margin, ax_px, margin + gh,
                           stroke='#374151', stroke_width=1.5))
    if y_min <= 0 <= y_max:
        _, ax_py = to_px(0, 0)
        d.append(draw.Line(margin, ax_py, margin + gw, ax_py,
                           stroke='#374151', stroke_width=1.5))

    # Axis labels
    step = 1 if (x_max - x_min) <= 12 else 2
    for x in range(x_min, x_max + 1, step):
        if x == 0:
            continue
        px, py0 = to_px(x, 0)
        ref_py = py0 if y_min <= 0 <= y_max else margin + gh
        d.append(draw.Text(str(x), 15, px, ref_py + 14,
                           text_anchor='middle', fill='#6b7280'))
    for y in range(y_min, y_max + 1, step):
        if y == 0:
            continue
        px0, py = to_px(0, y)
        ref_px = px0 if x_min <= 0 <= x_max else margin
        d.append(draw.Text(str(y), 15, ref_px - 8, py + 4,
                           text_anchor='end', fill='#6b7280'))

    # Axis names
    d.append(draw.Text('x', 16, margin + gw + 8, (margin + gh + 14) if y_min <= 0 <= y_max else margin + gh + 14,
                       fill='#374151', font_weight='bold'))
    _, y_ax_top = to_px(0, y_max)
    d.append(draw.Text('y', 16, (margin + (0 - x_min) / (x_max - x_min) * gw - 14) if x_min <= 0 <= x_max else margin - 14,
                       margin - 8, fill='#374151', font_weight='bold'))

    # Origin label
    if x_min <= 0 <= x_max and y_min <= 0 <= y_max:
        opx, opy = to_px(0, 0)
        d.append(draw.Text('O', 15, opx - 10, opy + 14, fill='#6b7280'))

    vertex_labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def draw_polygon(vertices, color, label_suffix="", filled=True):
        if not vertices:
            return
        pts = [to_px(v[0], v[1]) for v in vertices]
        coords = []
        for p in pts:
            coords.extend(p)
        fill_c = color if filled else 'none'
        d.append(draw.Lines(*coords, close=True,
                            fill=fill_c, stroke=color, stroke_width=2,
                            fill_opacity=0.15 if filled else 0))
        for i, (vx, vy) in enumerate(vertices):
            px, py = pts[i]
            d.append(draw.Circle(px, py, 3.5, fill=color))
            lbl = vertex_labels[i % len(vertex_labels)] + label_suffix
            # Offset label based on quadrant
            ox = 8 if vx >= 0 else -8
            oy = -8 if vy >= 0 else 12
            anchor = 'start' if vx >= 0 else 'end'
            d.append(draw.Text(lbl, 15, px + ox, py + oy,
                               text_anchor=anchor, fill=color, font_weight='bold'))

    draw_polygon(preimage, pre_color, pre_label)
    draw_polygon(image, img_color, img_label)

    return d.as_svg()


# ============================================================
# DOT PLOT (Indiana "line plot")
# ============================================================

def dot_plot_svg(data, x_label="Value", x_min=None, x_max=None,
                 title="", width=420, height=200):
    """Draw a dot plot (number line with stacked dots) for a dataset.

    data: list of numeric values (may have repeats).
    x_label: label for the horizontal axis.
    x_min/x_max: axis range (auto-detected if None).
    """
    from collections import Counter
    counts = Counter(data)

    if x_min is None:
        x_min = min(data)
    if x_max is None:
        x_max = max(data)
    if x_min == x_max:
        x_min -= 1
        x_max += 1

    d = draw.Drawing(width, height)
    margin_l, margin_r, margin_top, margin_bot = 30, 30, 25, 40
    gw = width - margin_l - margin_r
    gh = height - margin_top - margin_bot
    dot_r = min(8, gw / (x_max - x_min + 1) / 2.5)

    # Number line
    baseline_y = margin_top + gh
    d.append(draw.Line(margin_l, baseline_y, margin_l + gw, baseline_y,
                       stroke='#374151', stroke_width=1.5))

    # Determine tick step
    span = x_max - x_min
    if span <= 15:
        step = 1
    elif span <= 30:
        step = 2
    else:
        step = 5

    def x_to_px(val):
        return margin_l + (val - x_min) / (x_max - x_min) * gw

    # Ticks and labels
    v = x_min
    while v <= x_max:
        px = x_to_px(v)
        d.append(draw.Line(px, baseline_y, px, baseline_y + 5,
                           stroke='#374151', stroke_width=1))
        # Format tick label
        if isinstance(v, float) and v == int(v):
            lbl = str(int(v))
        else:
            lbl = str(v)
        d.append(draw.Text(lbl, 15, px, baseline_y + 16,
                           text_anchor='middle', fill='#374151'))
        v += step

    # Dots
    for val, count in sorted(counts.items()):
        px = x_to_px(val)
        for i in range(count):
            cy = baseline_y - dot_r - (i * (dot_r * 2 + 2))
            d.append(draw.Circle(px, cy, dot_r,
                                 fill='#3b82f6', stroke='#1e40af', stroke_width=1))

    # X-axis label
    d.append(draw.Text(x_label, 15, margin_l + gw / 2, height - 4,
                       text_anchor='middle', fill='#374151', font_weight='bold'))

    # Title
    if title:
        d.append(draw.Text(title, 16, width / 2, 14,
                           text_anchor='middle', fill='#1f2937', font_weight='bold'))

    return d.as_svg()


# ============================================================
# HISTOGRAM
# ============================================================

def histogram_svg(bins, frequencies, x_label="Value", y_label="Frequency",
                  title="", width=400, height=260):
    """Draw a histogram with labeled bins and frequency bars.

    bins: list of bin edge labels, e.g. [0, 5, 10, 15, 20] (len = frequencies + 1).
    frequencies: list of frequency counts per bin.
    """
    d = draw.Drawing(width, height)
    margin_l, margin_r, margin_top, margin_bot = 50, 20, 25, 45
    gw = width - margin_l - margin_r
    gh = height - margin_top - margin_bot

    n_bars = len(frequencies)
    max_freq = max(frequencies) if frequencies else 1
    bar_w = gw / n_bars

    # Y-axis
    d.append(draw.Line(margin_l, margin_top, margin_l, margin_top + gh,
                       stroke='#374151', stroke_width=1.5))
    # X-axis
    d.append(draw.Line(margin_l, margin_top + gh, margin_l + gw, margin_top + gh,
                       stroke='#374151', stroke_width=1.5))

    # Y-axis ticks
    y_step = max(1, max_freq // 5) if max_freq > 5 else 1
    y_val = 0
    while y_val <= max_freq:
        py = margin_top + gh - (y_val / max_freq) * gh
        d.append(draw.Line(margin_l - 4, py, margin_l, py,
                           stroke='#374151', stroke_width=1))
        d.append(draw.Text(str(y_val), 15, margin_l - 8, py + 4,
                           text_anchor='end', fill='#374151'))
        if y_val == 0 and y_step == 0:
            break
        y_val += y_step

    # Bars
    for i, freq in enumerate(frequencies):
        bx = margin_l + i * bar_w
        bar_h = (freq / max_freq) * gh if max_freq > 0 else 0
        by = margin_top + gh - bar_h
        d.append(draw.Rectangle(bx, by, bar_w, bar_h,
                                fill='#93c5fd', stroke='#2563eb', stroke_width=1.5))
        # Frequency label on top of bar
        if freq > 0:
            d.append(draw.Text(str(freq), 15, bx + bar_w / 2, by - 4,
                               text_anchor='middle', fill='#1e40af', font_weight='bold'))

    # Bin edge labels
    for i, edge in enumerate(bins):
        px = margin_l + i * bar_w
        lbl = str(int(edge)) if isinstance(edge, float) and edge == int(edge) else str(edge)
        d.append(draw.Text(lbl, 15, px, margin_top + gh + 14,
                           text_anchor='middle', fill='#374151'))

    # Axis labels
    d.append(draw.Text(x_label, 15, margin_l + gw / 2, height - 4,
                       text_anchor='middle', fill='#374151', font_weight='bold'))
    d.append(draw.Text(y_label, 15, 10, margin_top + gh / 2,
                       text_anchor='middle', fill='#374151', font_weight='bold',
                       transform=f'rotate(-90,10,{margin_top + gh / 2})'))

    if title:
        d.append(draw.Text(title, 16, width / 2, 14,
                           text_anchor='middle', fill='#1f2937', font_weight='bold'))

    return d.as_svg()


# ============================================================
# BOX PLOT (one or two side-by-side)
# ============================================================

def box_plot_svg(summaries, labels=None, x_min=None, x_max=None,
                 title="", width=420, height=None):
    """Draw one or two horizontal box-and-whisker plots.

    summaries: list of (min, Q1, median, Q3, max) tuples.
    labels: list of dataset labels (same length as summaries).
    """
    n_plots = len(summaries)
    if height is None:
        height = 100 + n_plots * 60
    if labels is None:
        labels = [f"Dataset {i+1}" for i in range(n_plots)]

    all_vals = [v for s in summaries for v in s]
    if x_min is None:
        x_min = min(all_vals)
    if x_max is None:
        x_max = max(all_vals)
    # Add small padding
    span = x_max - x_min
    if span == 0:
        span = 2
    x_min -= span * 0.05
    x_max += span * 0.05

    d = draw.Drawing(width, height)
    # Single plot: no side labels needed, shrink left margin; add space below for label
    if n_plots == 1:
        margin_l, margin_r, margin_top, margin_bot = 30, 20, 20, 50
    else:
        margin_l, margin_r, margin_top, margin_bot = 70, 20, 20, 35
    gw = width - margin_l - margin_r
    gh = height - margin_top - margin_bot

    def val_to_px(v):
        return margin_l + (v - x_min) / (x_max - x_min) * gw

    # Number line
    axis_y = margin_top + gh
    d.append(draw.Line(margin_l, axis_y, margin_l + gw, axis_y,
                       stroke='#374151', stroke_width=1.5))

    # Tick marks
    nice_span = x_max - x_min
    if nice_span <= 10:
        step = 1
    elif nice_span <= 25:
        step = 2
    elif nice_span <= 50:
        step = 5
    else:
        step = 10

    tick_val = math.ceil(x_min / step) * step
    while tick_val <= x_max:
        px = val_to_px(tick_val)
        d.append(draw.Line(px, axis_y, px, axis_y + 5,
                           stroke='#374151', stroke_width=1))
        lbl = str(int(tick_val)) if tick_val == int(tick_val) else f"{tick_val:.1f}"
        d.append(draw.Text(lbl, 15, px, axis_y + 16,
                           text_anchor='middle', fill='#374151'))
        tick_val += step

    # Draw each box plot
    box_colors = [('#3b82f6', '#dbeafe'), ('#dc2626', '#fee2e2')]
    plot_height = 30
    plot_spacing = gh / n_plots if n_plots > 0 else gh

    for idx, (s, label) in enumerate(zip(summaries, labels)):
        mn, q1, med, q3, mx = s
        cy = margin_top + plot_spacing * (idx + 0.5)
        color, fill_c = box_colors[idx % len(box_colors)]

        # Whiskers
        d.append(draw.Line(val_to_px(mn), cy, val_to_px(q1), cy,
                           stroke=color, stroke_width=1.5))
        d.append(draw.Line(val_to_px(q3), cy, val_to_px(mx), cy,
                           stroke=color, stroke_width=1.5))
        # Min/max end caps
        d.append(draw.Line(val_to_px(mn), cy - plot_height / 4, val_to_px(mn), cy + plot_height / 4,
                           stroke=color, stroke_width=1.5))
        d.append(draw.Line(val_to_px(mx), cy - plot_height / 4, val_to_px(mx), cy + plot_height / 4,
                           stroke=color, stroke_width=1.5))

        # Box
        bx = val_to_px(q1)
        bw = val_to_px(q3) - bx
        d.append(draw.Rectangle(bx, cy - plot_height / 2, bw, plot_height,
                                fill=fill_c, stroke=color, stroke_width=2))

        # Median line
        d.append(draw.Line(val_to_px(med), cy - plot_height / 2,
                           val_to_px(med), cy + plot_height / 2,
                           stroke=color, stroke_width=2.5))

        # Label
        if n_plots == 1:
            # Single box plot: label centered below the axis
            d.append(draw.Text(label, 15, margin_l + gw / 2, axis_y + 30,
                               text_anchor='middle', fill='#374151', font_weight='bold'))
        else:
            # Multiple plots: label on the left to identify each dataset
            d.append(draw.Text(label, 15, margin_l - 5, cy + 4,
                               text_anchor='end', fill='#374151', font_weight='bold'))

    if title:
        d.append(draw.Text(title, 16, width / 2, 14,
                           text_anchor='middle', fill='#1f2937', font_weight='bold'))

    return d.as_svg()


# ============================================================
# SCATTER PLOT
# ============================================================

def scatter_plot_svg(points, x_label="x", y_label="y", line_eq=None,
                     title="", width=360, height=320):
    """Draw a scatter plot with optional line of best fit.

    points: list of (x, y) tuples.
    line_eq: tuple (slope, intercept) for y = mx + b line, or None.
    """
    d = draw.Drawing(width, height)
    # Widened left margin (was 50) so the rotated y-axis label sits clear of
    # the tick numbers and never overlaps the chart, especially when ticks
    # have 3-digit values like 100, 200, 300.
    margin_l, margin_r, margin_top, margin_bot = 65, 20, 25, 45
    gw = width - margin_l - margin_r
    gh = height - margin_top - margin_bot

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x_data_min, x_data_max = min(xs), max(xs)
    y_data_min, y_data_max = min(ys), max(ys)

    # Axis ranges with padding
    x_span = x_data_max - x_data_min or 1
    y_span = y_data_max - y_data_min or 1
    x_lo = x_data_min - x_span * 0.1
    x_hi = x_data_max + x_span * 0.1
    y_lo = y_data_min - y_span * 0.1
    y_hi = y_data_max + y_span * 0.1

    # Snap to nice bounds starting at 0 if data is non-negative
    if x_data_min >= 0:
        x_lo = 0
    if y_data_min >= 0:
        y_lo = 0

    def to_px(x, y):
        px = margin_l + (x - x_lo) / (x_hi - x_lo) * gw
        py = margin_top + (y_hi - y) / (y_hi - y_lo) * gh
        return px, py

    # Grid lines. Aim for ~6-10 ticks across the span so labels never crowd.
    # The earlier table topped out at "step 20 forever past span=100", which
    # means a span of 700 (e.g. weekly savings going to $700) generated 35
    # tick labels stacked on the y-axis.
    def nice_step(span):
        if span <= 5:
            return 1
        elif span <= 15:
            return 2
        elif span <= 40:
            return 5
        elif span <= 100:
            return 10
        elif span <= 200:
            return 20
        elif span <= 500:
            return 50
        elif span <= 1000:
            return 100
        elif span <= 2000:
            return 200
        else:
            return 500

    x_step = nice_step(x_hi - x_lo)
    y_step = nice_step(y_hi - y_lo)

    gx = math.ceil(x_lo / x_step) * x_step
    while gx <= x_hi:
        px, _ = to_px(gx, 0)
        d.append(draw.Line(px, margin_top, px, margin_top + gh,
                           stroke='#e5e7eb', stroke_width=0.5))
        gx += x_step

    gy = math.ceil(y_lo / y_step) * y_step
    while gy <= y_hi:
        _, py = to_px(0, gy)
        d.append(draw.Line(margin_l, py, margin_l + gw, py,
                           stroke='#e5e7eb', stroke_width=0.5))
        gy += y_step

    # Axes
    _, ax_py = to_px(0, y_lo)
    d.append(draw.Line(margin_l, margin_top + gh, margin_l + gw, margin_top + gh,
                       stroke='#374151', stroke_width=1.5))
    d.append(draw.Line(margin_l, margin_top, margin_l, margin_top + gh,
                       stroke='#374151', stroke_width=1.5))

    # Axis tick labels
    gx = math.ceil(x_lo / x_step) * x_step
    while gx <= x_hi:
        px, _ = to_px(gx, 0)
        lbl = str(int(gx)) if gx == int(gx) else f"{gx:.1f}"
        d.append(draw.Text(lbl, 15, px, margin_top + gh + 14,
                           text_anchor='middle', fill='#6b7280'))
        gx += x_step

    gy = math.ceil(y_lo / y_step) * y_step
    while gy <= y_hi:
        _, py = to_px(0, gy)
        lbl = str(int(gy)) if gy == int(gy) else f"{gy:.1f}"
        d.append(draw.Text(lbl, 15, margin_l - 6, py + 3,
                           text_anchor='end', fill='#6b7280'))
        gy += y_step

    # Line of best fit. Draw it across the *data* x-range (not the full
    # axis) so it stays where the data actually lives, and clip to the
    # y-axis bounds so we don't draw segments off-plot. Without this the
    # line streaks from (x_lo, m*x_lo + b) to (x_hi, m*x_hi + b) which can
    # land far outside the plot — e.g. y = -4x + 100 drawn from x=0 sits
    # at 100% battery up in the top-left corner even when the data starts
    # at x=8.
    if line_eq is not None:
        m, b = line_eq

        def y_at(xv):
            return m * xv + b

        # Start with the data domain.
        lx1 = max(x_lo, x_data_min)
        lx2 = min(x_hi, x_data_max)

        ly1 = y_at(lx1)
        ly2 = y_at(lx2)

        # If either endpoint sits outside the y-axis, walk it inward along
        # the line until it hits the y bound. Standard line-clipping —
        # find the x where y == y_lo or y == y_hi and use that instead.
        def clip_endpoint(xv, yv):
            if yv < y_lo and m != 0:
                xv = (y_lo - b) / m
                yv = y_lo
            elif yv > y_hi and m != 0:
                xv = (y_hi - b) / m
                yv = y_hi
            return xv, yv

        lx1, ly1 = clip_endpoint(lx1, ly1)
        lx2, ly2 = clip_endpoint(lx2, ly2)

        # Sanity: only draw if the segment is still inside the data domain.
        if lx1 < lx2:
            px1, py1 = to_px(lx1, ly1)
            px2, py2 = to_px(lx2, ly2)
            d.append(draw.Line(px1, py1, px2, py2,
                               stroke='#dc2626', stroke_width=2,
                               stroke_dasharray='6,3'))

    # Data points
    for x, y in points:
        px, py = to_px(x, y)
        d.append(draw.Circle(px, py, 4,
                             fill='#3b82f6', stroke='#1e40af', stroke_width=1))

    # Axis labels
    d.append(draw.Text(x_label, 15, margin_l + gw / 2, height - 4,
                       text_anchor='middle', fill='#374151', font_weight='bold'))
    # Y-axis label: rotated -90 so it reads bottom-to-top (Western convention
    # for vertical axis titles). Positioned at x=14 — just inside the widened
    # left margin and clear of the tick numbers.
    y_label_cx = 14
    y_label_cy = margin_top + gh / 2
    d.append(draw.Text(y_label, 15, y_label_cx, y_label_cy,
                       text_anchor='middle', fill='#374151', font_weight='bold',
                       transform=f'rotate(-90,{y_label_cx},{y_label_cy})'))

    if title:
        d.append(draw.Text(title, 16, width / 2, 14,
                           text_anchor='middle', fill='#1f2937', font_weight='bold'))

    return d.as_svg()


# ============================================================
# PROPORTIONAL RELATIONSHIP GRAPH (y = mx through origin)
# ============================================================

def proportional_graph_svg(points, x_label="x", y_label="y",
                           show_line=True, x_max=None, y_max=None,
                           title="", width=320, height=300):
    """Draw a Quadrant-I coordinate grid with plotted points on y = mx.

    points: list of (x, y) tuples — integer or half-value coordinates.
    show_line: if True, draw solid line through origin connecting points.
    x_max/y_max: override axis maximums (auto-calculated if None).
    """
    d = draw.Drawing(width, height)
    margin_l, margin_r, margin_top, margin_bot = 60, 20, 20, 55
    gw = width - margin_l - margin_r
    gh = height - margin_top - margin_bot

    # Determine axis range (always start at 0)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    ax_max = x_max if x_max else max(xs) + 1
    ay_max = y_max if y_max else max(ys) + max(ys) * 0.15

    # Round up to nice integer
    ax_max = math.ceil(ax_max)
    ay_max = math.ceil(ay_max)

    def to_px(x, y):
        px = margin_l + (x / ax_max) * gw
        py = margin_top + ((ay_max - y) / ay_max) * gh
        return px, py

    # Determine grid step
    def nice_step(mx):
        if mx <= 6:
            return 1
        elif mx <= 12:
            return 2
        elif mx <= 30:
            return 5
        else:
            return 10

    x_step = nice_step(ax_max)
    y_step = nice_step(ay_max)

    # Grid lines
    gx = x_step
    while gx <= ax_max:
        px, _ = to_px(gx, 0)
        d.append(draw.Line(px, margin_top, px, margin_top + gh,
                           stroke='#e5e7eb', stroke_width=0.5))
        gx += x_step

    gy = y_step
    while gy <= ay_max:
        _, py = to_px(0, gy)
        d.append(draw.Line(margin_l, py, margin_l + gw, py,
                           stroke='#e5e7eb', stroke_width=0.5))
        gy += y_step

    # Axes (bold, through origin)
    ox, oy = to_px(0, 0)
    d.append(draw.Line(margin_l, oy, margin_l + gw, oy,
                       stroke='#374151', stroke_width=1.5))
    d.append(draw.Line(ox, margin_top, ox, margin_top + gh,
                       stroke='#374151', stroke_width=1.5))

    # Tick labels on x-axis
    gx = x_step
    while gx <= ax_max:
        px, _ = to_px(gx, 0)
        lbl = str(int(gx)) if gx == int(gx) else f"{gx:.1f}"
        d.append(draw.Text(lbl, 15, px, oy + 14,
                           text_anchor='middle', fill='#6b7280'))
        gx += x_step

    # Tick labels on y-axis
    gy = y_step
    while gy <= ay_max:
        _, py = to_px(0, gy)
        lbl = str(int(gy)) if gy == int(gy) else f"{gy:.1f}"
        d.append(draw.Text(lbl, 15, ox - 8, py + 3,
                           text_anchor='end', fill='#6b7280'))
        gy += y_step

    # Origin label
    d.append(draw.Text("0", 15, ox - 8, oy + 14,
                       text_anchor='end', fill='#6b7280'))

    # Proportional line through origin (solid)
    if show_line and len(points) >= 1:
        # Calculate slope from first non-origin point
        for px_val, py_val in points:
            if px_val != 0:
                m = py_val / px_val
                break
        else:
            m = 0
        # Draw from origin to edge of graph
        end_x = ax_max
        end_y = m * end_x
        if end_y > ay_max:
            end_y = ay_max
            end_x = ay_max / m if m else ax_max
        px1, py1 = to_px(0, 0)
        px2, py2 = to_px(end_x, end_y)
        d.append(draw.Line(px1, py1, px2, py2,
                           stroke='#2563eb', stroke_width=2))

    # Plot points as solid dots
    for x, y in points:
        px, py = to_px(x, y)
        d.append(draw.Circle(px, py, 5,
                             fill='#2563eb', stroke='#1e40af', stroke_width=1.5))

    # Axis labels (doubled font size for readability)
    d.append(draw.Text(x_label, 22, margin_l + gw / 2, height - 2,
                       text_anchor='middle', fill='#374151', font_weight='bold'))
    d.append(draw.Text(y_label, 22, 6, margin_top + gh / 2,
                       text_anchor='middle', fill='#374151', font_weight='bold',
                       transform=f'rotate(-90,6,{margin_top + gh / 2})'))

    if title:
        d.append(draw.Text(title, 16, width / 2, 14,
                           text_anchor='middle', fill='#1f2937', font_weight='bold'))

    return d.as_svg()


# ============================================================
# SPINNER (circular, divided into sections)
# ============================================================

def spinner_svg(sections, width=240, height=240):
    """Draw a circular spinner divided into labeled sections.

    sections: list of dicts with keys:
        'label': str (section label),
        'fraction': float (fraction of circle, must sum to 1.0).
    Optional: 'color' for custom fill.
    """
    d = draw.Drawing(width, height)
    cx, cy = width / 2, height / 2
    r = min(width, height) / 2 - 25

    palette = ['#bfdbfe', '#fecaca', '#bbf7d0', '#fef08a', '#e9d5ff',
               '#fed7aa', '#a5f3fc', '#fecdd3']

    # Map color name labels to matching fill colors
    color_name_map = {
        'red': '#ef4444', 'blue': '#3b82f6', 'green': '#22c55e',
        'yellow': '#eab308', 'orange': '#f97316', 'purple': '#a855f7',
        'pink': '#ec4899', 'white': '#f3f4f6',
    }

    start_angle = -math.pi / 2  # start from top
    for i, sec in enumerate(sections):
        frac = sec['fraction']
        sweep = frac * 2 * math.pi
        end_angle = start_angle + sweep

        x1 = cx + r * math.cos(start_angle)
        y1 = cy + r * math.sin(start_angle)
        x2 = cx + r * math.cos(end_angle)
        y2 = cy + r * math.sin(end_angle)

        large = 1 if sweep > math.pi else 0
        fill_c = sec.get('color',
                         color_name_map.get(sec.get('label', '').lower(),
                                            palette[i % len(palette)]))

        p = draw.Path(fill=fill_c, stroke='#374151', stroke_width=1.5)
        p.M(cx, cy)
        p.L(x1, y1)
        p.A(r, r, 0, large, 1, x2, y2)
        p.Z()
        d.append(p)

        # Label at midpoint of arc
        mid_angle = start_angle + sweep / 2
        label_r = r * 0.6
        lx = cx + label_r * math.cos(mid_angle)
        ly = cy + label_r * math.sin(mid_angle)
        d.append(draw.Text(sec['label'], 12, lx, ly + 4,
                           text_anchor='middle', fill='#1f2937', font_weight='bold'))

        start_angle = end_angle

    # Center dot
    d.append(draw.Circle(cx, cy, 4, fill='#374151'))

    # Arrow pointer (upward from center)
    arrow_len = r * 0.85
    d.append(draw.Line(cx, cy, cx, cy - arrow_len,
                       stroke='#1f2937', stroke_width=2.5))
    d.append(draw.Lines(cx - 6, cy - arrow_len + 10, cx, cy - arrow_len,
                        cx + 6, cy - arrow_len + 10,
                        close=True, fill='#1f2937', stroke='none'))

    return d.as_svg()


# ============================================================
# TREE DIAGRAM
# ============================================================

def tree_diagram_svg(stages, width=None, height=None):
    """Draw a multi-stage tree diagram for probability/counting.

    stages: list of lists of outcome labels for each stage.
        Example: [['H', 'T'], ['1', '2', '3']]
        means Stage 1 has 2 outcomes, Stage 2 has 3 outcomes per branch.
    """
    n_stages = len(stages)
    total_leaves = 1
    for s in stages:
        total_leaves *= len(s)

    if width is None:
        width = 120 + n_stages * 140
    if height is None:
        height = max(160, total_leaves * 28 + 40)

    d = draw.Drawing(width, height)
    margin_l, margin_r, margin_top, margin_bot = 20, 20, 20, 20
    gw = width - margin_l - margin_r
    gh = height - margin_top - margin_bot

    x_step = gw / (n_stages + 0.5)

    def draw_level(stage_idx, parent_x, parent_y, y_start, y_end):
        """Recursively draw branches for one stage."""
        if stage_idx >= n_stages:
            return

        options = stages[stage_idx]
        n = len(options)
        child_x = parent_x + x_step
        segment_h = (y_end - y_start) / n

        for i, label in enumerate(options):
            child_y = y_start + segment_h * (i + 0.5)

            # Branch line
            d.append(draw.Line(parent_x, parent_y, child_x, child_y,
                               stroke='#6b7280', stroke_width=1.5))

            # Label on the line
            mid_x = (parent_x + child_x) / 2
            mid_y = (parent_y + child_y) / 2
            # Offset label slightly above line
            d.append(draw.Text(label, 11, mid_x, mid_y - 6,
                               text_anchor='middle', fill='#1e40af', font_weight='bold'))

            # Node dot
            d.append(draw.Circle(child_x, child_y, 3, fill='#3b82f6'))

            # Recurse for next stage
            child_y_start = y_start + segment_h * i
            child_y_end = child_y_start + segment_h
            draw_level(stage_idx + 1, child_x, child_y, child_y_start, child_y_end)

    # Root node
    root_x = margin_l + 10
    root_y = margin_top + gh / 2
    d.append(draw.Circle(root_x, root_y, 4, fill='#374151'))

    draw_level(0, root_x, root_y, margin_top, margin_top + gh)

    return d.as_svg()


# ============================================================
# COMPOSITE RECTANGULAR PRISM (L-shape, T-shape)
# ============================================================

def composite_prism_svg(prisms, labels=None, width=320, height=260):
    """Draw a composite shape made of rectangular prisms (2D front view).

    prisms: list of dicts with keys x, y, w, h (in unit space).
    labels: list of dicts with keys text, x, y.
    """
    d = draw.Drawing(width, height)
    margin = 30

    # Find bounding box
    all_x = [p['x'] for p in prisms] + [p['x'] + p['w'] for p in prisms]
    all_y = [p['y'] for p in prisms] + [p['y'] + p['h'] for p in prisms]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)

    range_x = max_x - min_x or 1
    range_y = max_y - min_y or 1
    scale = min((width - 2 * margin) / range_x, (height - 2 * margin - 20) / range_y)

    def to_px(x, y):
        px = margin + (x - min_x) * scale
        py = margin + (max_y - y) * scale  # flip y
        return px, py

    # Draw each prism
    for p in prisms:
        px, py = to_px(p['x'], p['y'] + p['h'])
        pw = p['w'] * scale
        ph = p['h'] * scale
        d.append(draw.Rectangle(px, py, pw, ph,
                                fill='#e8f4fd', stroke='#2563eb', stroke_width=2))

    # Draw labels
    if labels:
        for lbl in labels:
            px, py = to_px(lbl['x'], lbl['y'])
            d.append(draw.Text(lbl['text'], 30, px, py,
                               text_anchor='middle', fill='#1e40af', font_weight='bold',
                               dominant_baseline='middle'))

    return d.as_svg()


def isometric_composite_prism_svg(prisms, labels=None, depth=None, width=360, height=300):
    """Draw a composite shape with oblique 3D projection showing depth.

    prisms: list of dicts with keys x, y, w, h (in unit space, front face).
    labels: list of dicts with keys text, x, y.
    depth: depth value to show (if None, not drawn).
    """
    d = draw.Drawing(width, height)
    margin = 40
    depth_px_ratio = 0.4  # how much depth offsets in px per unit

    # Find bounding box of front face
    all_x = [p['x'] for p in prisms] + [p['x'] + p['w'] for p in prisms]
    all_y = [p['y'] for p in prisms] + [p['y'] + p['h'] for p in prisms]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)

    range_x = max_x - min_x or 1
    range_y = max_y - min_y or 1

    # Reserve space for depth offset
    depth_offset_x = (depth or 0) * depth_px_ratio * 12
    depth_offset_y = (depth or 0) * depth_px_ratio * 8

    avail_w = width - 2 * margin - depth_offset_x
    avail_h = height - 2 * margin - depth_offset_y - 20
    scale = min(avail_w / range_x, avail_h / range_y)

    dx = depth_offset_x  # oblique offset for depth
    dy = -depth_offset_y

    def to_px(x, y):
        px = margin + (x - min_x) * scale
        py = margin + depth_offset_y + (max_y - y) * scale  # flip y
        return px, py

    front_fill = '#dbeafe'
    top_fill = '#bfdbfe'
    side_fill = '#93c5fd'
    stroke_c = '#2563eb'

    # Draw back faces first (depth), then top faces, then front faces
    for p_data in prisms:
        fx, fy = to_px(p_data['x'], p_data['y'] + p_data['h'])
        fw = p_data['w'] * scale
        fh = p_data['h'] * scale

        if depth:
            # Top face (parallelogram)
            top = draw.Path(fill=top_fill, stroke=stroke_c, stroke_width=1.5)
            top.M(fx, fy)
            top.L(fx + dx, fy + dy)
            top.L(fx + fw + dx, fy + dy)
            top.L(fx + fw, fy)
            top.Z()
            d.append(top)

            # Right side face (parallelogram)
            side = draw.Path(fill=side_fill, stroke=stroke_c, stroke_width=1.5)
            side.M(fx + fw, fy)
            side.L(fx + fw + dx, fy + dy)
            side.L(fx + fw + dx, fy + fh + dy)
            side.L(fx + fw, fy + fh)
            side.Z()
            d.append(side)

    # Front faces on top
    for p_data in prisms:
        fx, fy = to_px(p_data['x'], p_data['y'] + p_data['h'])
        fw = p_data['w'] * scale
        fh = p_data['h'] * scale
        d.append(draw.Rectangle(fx, fy, fw, fh,
                                fill=front_fill, stroke=stroke_c, stroke_width=2))

    # Labels
    if labels:
        for lbl in labels:
            px, py = to_px(lbl['x'], lbl['y'])
            d.append(draw.Text(lbl['text'], 30, px, py,
                               text_anchor='middle', fill='#1e40af', font_weight='bold',
                               dominant_baseline='middle'))

    # Depth label
    if depth:
        # Label along the top-right depth edge
        p0 = prisms[0]
        fx, fy = to_px(p0['x'] + p0['w'], p0['y'] + p0['h'])
        mid_x = fx + dx / 2 + 5
        mid_y = fy + dy / 2 - 5
        d.append(draw.Text(str(depth), 30, mid_x, mid_y,
                           text_anchor='middle', fill='#1e40af', font_weight='bold'))

    return d.as_svg()


# ============================================================
# BRICK WITH CYLINDRICAL HOLES (7.GM.3 composite solid)
# ============================================================

def brick_with_holes_svg(l_val, w_val, h_val, n_holes, r_hole,
                         width=360, height=300):
    """Draw an isometric rectangular prism (brick) with cylindrical holes
    visible on the front face.

    l_val, w_val, h_val: brick dimensions (length, width, height).
    n_holes: number of cylindrical holes.
    r_hole: radius of each cylindrical hole.
    """
    import math as _math
    d = draw.Drawing(width, height)
    margin = 40

    # Oblique projection parameters
    depth_ratio = 0.35
    dx = w_val * depth_ratio * 10  # depth offset x
    dy = -w_val * depth_ratio * 7  # depth offset y

    # Scale the front face to fit
    avail_w = width - 2 * margin - abs(dx)
    avail_h = height - 2 * margin - abs(dy) - 20
    scale_x = avail_w / l_val
    scale_y = avail_h / h_val
    scale = min(scale_x, scale_y)

    # Front face rectangle position
    fx = margin
    fy = margin + abs(dy)
    fw = l_val * scale
    fh = h_val * scale

    front_fill = '#dbeafe'
    top_fill = '#bfdbfe'
    side_fill = '#93c5fd'
    stroke_c = '#2563eb'
    hole_fill = '#f1f5f9'
    hole_stroke = '#64748b'

    # Top face (parallelogram)
    top = draw.Path(fill=top_fill, stroke=stroke_c, stroke_width=1.5)
    top.M(fx, fy)
    top.L(fx + dx, fy + dy)
    top.L(fx + fw + dx, fy + dy)
    top.L(fx + fw, fy)
    top.Z()
    d.append(top)

    # Right side face (parallelogram)
    side = draw.Path(fill=side_fill, stroke=stroke_c, stroke_width=1.5)
    side.M(fx + fw, fy)
    side.L(fx + fw + dx, fy + dy)
    side.L(fx + fw + dx, fy + fh + dy)
    side.L(fx + fw, fy + fh)
    side.Z()
    d.append(side)

    # Front face
    d.append(draw.Rectangle(fx, fy, fw, fh,
                            fill=front_fill, stroke=stroke_c, stroke_width=2))

    # Draw cylindrical holes on the front face, laid out with equal gaps so the
    # circles never overlap. If the true radius would collide, shrink the DRAWN
    # radius (the labeled value still carries the real measurement). No dashed
    # inner circle -- a single clean circle per hole.
    r_px = r_hole * scale
    min_gap = 7.0
    max_r_px = (fw - (n_holes + 1) * min_gap) / (2 * n_holes)
    if max_r_px > 3 and r_px > max_r_px:
        r_px = max_r_px
    gap = (fw - n_holes * 2 * r_px) / (n_holes + 1)
    hole_cy = fy + fh / 2  # vertically centered
    hole_centers = []
    for i in range(n_holes):
        hole_cx = fx + gap * (i + 1) + r_px * (2 * i + 1)
        hole_centers.append(hole_cx)
        d.append(draw.Circle(hole_cx, hole_cy, r_px,
                             fill=hole_fill, stroke=hole_stroke, stroke_width=1.5))

    # Dimension labels
    label_c = '#1e40af'
    fs = 26

    # Length label (below front face)
    d.append(draw.Text(f"{l_val}", fs, fx + fw / 2, fy + fh + 22,
                       text_anchor='middle', fill=label_c, font_weight='bold'))

    # Height label (left of front face)
    d.append(draw.Text(f"{h_val}", fs, fx - 14, fy + fh / 2,
                       text_anchor='middle', fill=label_c, font_weight='bold',
                       dominant_baseline='middle'))

    # Width/depth label (along top edge, oblique)
    mid_x = fx + dx / 2
    mid_y = fy + dy / 2 - 8
    d.append(draw.Text(f"{w_val}", fs, mid_x, mid_y,
                       text_anchor='middle', fill=label_c, font_weight='bold'))

    # Hole radius label (on first hole)
    if n_holes > 0:
        h1_cx = hole_centers[0]
        # Radius line from center to edge
        d.append(draw.Line(h1_cx, hole_cy, h1_cx + r_px, hole_cy,
                           stroke='#dc2626', stroke_width=1.5,
                           stroke_dasharray='4,2'))
        d.append(draw.Circle(h1_cx, hole_cy, 2, fill='#dc2626'))
        d.append(draw.Text(f"r = {r_hole}", 22, h1_cx + r_px / 2, hole_cy - 10,
                           text_anchor='middle', fill='#dc2626', font_weight='bold'))

    return d.as_svg()


# ============================================================
# MULTIPLICATION NUMBER LINE (repeated jumps model)
# ============================================================

def multiplication_jumps_svg(jump_size, num_jumps, width=420, height=160):
    """Draw a number line showing multiplication as repeated jumps.

    Models ``jump_size x num_jumps`` as |num_jumps| arcs of size
    |jump_size|, starting from 0. Direction is determined by the sign
    of the product.

    Example: jump_size=-2, num_jumps=3  ->  3 arcs going left by 2
             landing at -6.

    Returns an SVG string.
    """
    product = jump_size * num_jumps

    # Determine the number line range
    endpoints = [0, product]
    lo = min(endpoints)
    hi = max(endpoints)
    # Add some padding
    pad = max(2, abs(hi - lo) // 4, 1)
    line_min = lo - pad
    line_max = hi + pad

    d = draw.Drawing(width, height)

    margin_l = 40
    margin_r = 30
    line_y = height - 50
    line_w = width - margin_l - margin_r

    # Map value to pixel x
    def to_x(val):
        return margin_l + (val - line_min) / (line_max - line_min) * line_w

    # Draw the number line
    d.append(draw.Line(margin_l - 8, line_y, margin_l + line_w + 8, line_y,
                       stroke='#374151', stroke_width=2))
    # Arrowheads on line ends
    for ax_x, direction in [(margin_l - 8, -1), (margin_l + line_w + 8, 1)]:
        d.append(draw.Lines(
            ax_x, line_y,
            ax_x + direction * (-6), line_y - 4,
            ax_x + direction * (-6), line_y + 4,
            close=True, fill='#374151', stroke='none'))

    # Draw tick marks and labels
    for val in range(line_min, line_max + 1):
        px = to_x(val)
        tick_h = 8 if val == 0 else 5
        sw = 2 if val == 0 else 1
        d.append(draw.Line(px, line_y - tick_h, px, line_y + tick_h,
                           stroke='#374151', stroke_width=sw))
        d.append(draw.Text(str(val), 11, px, line_y + 20,
                           text_anchor='middle', fill='#374151'))

    # Draw the jumps as arcs above the number line
    arc_color = '#2563eb'
    arc_radius_y = 22  # height of arcs

    current = 0
    for i in range(abs(num_jumps)):
        nxt = current + jump_size
        x1 = to_x(current)
        x2 = to_x(nxt)

        # Draw arc (quadratic bezier)
        mid_x = (x1 + x2) / 2
        mid_y = line_y - arc_radius_y - i * 3  # stack slightly

        p = draw.Path(fill='none', stroke=arc_color, stroke_width=1.8)
        p.M(x1, line_y - 2)
        p.Q(mid_x, mid_y, x2, line_y - 2)
        d.append(p)

        # Downward arrowhead whose tip lands exactly on the destination tick,
        # so every jump visibly ends on a tick mark.
        d.append(draw.Lines(
            x2, line_y,          # tip on the number line at the tick
            x2 - 3, line_y - 6,
            x2 + 3, line_y - 6,
            close=True, fill=arc_color, stroke='none'))

        current = nxt

    # Mark start (0) and end (product) with dots
    d.append(draw.Circle(to_x(0), line_y, 4, fill='#22c55e', stroke='#166534', stroke_width=1.5))
    d.append(draw.Circle(to_x(product), line_y, 4, fill='#ef4444', stroke='#991b1b', stroke_width=1.5))

    return d.as_svg()


def addition_jump_svg(start, addend, width=440, height=150):
    """Draw a number line that models ``start + addend`` as a single directed jump.

    Marks the starting value, draws one arc of length ``|addend|`` in the
    direction of its sign, and lands the arrowhead on ``start + addend`` (marked
    "?" so the student still computes it). This models ADDITION -- a running total
    that moves by the addend -- rather than the distance between two independent
    points, so a scenario like -4.1 + 9.4 reads as intended instead of looking
    like 9.4 - (-4.1).

    Returns an SVG string.
    """
    import math
    start = float(start)
    addend = float(addend)
    result = start + addend

    def fmt(v):
        return str(int(v)) if v == int(v) else f"{v:.2f}".rstrip('0').rstrip('.')

    lo = min(start, result)
    hi = max(start, result)
    line_min = int(math.floor(lo)) - 1
    line_max = int(math.ceil(hi)) + 1

    d = draw.Drawing(width, height)
    margin_l = 30
    margin_r = 30
    line_y = height - 45
    line_w = width - margin_l - margin_r

    def to_x(val):
        return margin_l + (val - line_min) / (line_max - line_min) * line_w

    # Number line with arrowheads on both ends
    d.append(draw.Line(margin_l - 8, line_y, margin_l + line_w + 8, line_y,
                       stroke='#374151', stroke_width=2))
    for ax_x, direction in [(margin_l - 8, -1), (margin_l + line_w + 8, 1)]:
        d.append(draw.Lines(ax_x, line_y, ax_x + direction * (-6), line_y - 4,
                            ax_x + direction * (-6), line_y + 4,
                            close=True, fill='#374151', stroke='none'))

    # Integer tick marks and labels
    for val in range(line_min, line_max + 1):
        px = to_x(val)
        th = 8 if val == 0 else 5
        sw = 2 if val == 0 else 1
        d.append(draw.Line(px, line_y - th, px, line_y + th,
                           stroke='#374151', stroke_width=sw))
        d.append(draw.Text(str(val), 15, px, line_y + 22,
                           text_anchor='middle', fill='#374151'))

    # The single jump arc from start to result
    arc_color = '#2563eb'
    x1, x2 = to_x(start), to_x(result)
    mid_x = (x1 + x2) / 2
    mid_y = line_y - 34
    p = draw.Path(fill='none', stroke=arc_color, stroke_width=2)
    p.M(x1, line_y - 2)
    p.Q(mid_x, mid_y, x2, line_y - 2)
    d.append(p)
    # Arrowhead tip landing on the result
    d.append(draw.Lines(x2, line_y, x2 - 3, line_y - 7, x2 + 3, line_y - 7,
                        close=True, fill=arc_color, stroke='none'))
    addend_lbl = f"+ {fmt(addend)}" if addend >= 0 else f"- {fmt(abs(addend))}"
    d.append(draw.Text(addend_lbl, 15, mid_x, mid_y - 5,
                       text_anchor='middle', fill=arc_color))

    # Start dot (labeled) and result dot (marked "?" -- the student finds it)
    d.append(draw.Circle(x1, line_y, 4, fill='#22c55e', stroke='#166534', stroke_width=1.5))
    d.append(draw.Text(f"start {fmt(start)}", 13, x1, line_y - 11,
                       text_anchor='middle', fill='#166534'))
    d.append(draw.Circle(x2, line_y, 4, fill='#ef4444', stroke='#991b1b', stroke_width=1.5))
    d.append(draw.Text("?", 16, x2, line_y - 12, text_anchor='middle', fill='#991b1b'))

    return d.as_svg()


# ============================================================
# QUALITATIVE GRAPH (for 8.AF.4 — linear + curved segments)
# ============================================================

def qualitative_graph_svg(segments, x_label="Time", y_label="Value",
                          show_scale=False, width=380, height=280):
    """Draw a qualitative graph with labeled axes and piecewise segments.

    segments: list of dicts, each with:
        - x_start, y_start: start point
        - x_end, y_end: end point
        - curve: 'linear', 'concave_up', 'concave_down' (default 'linear')

    show_scale: if True, add integer tick marks on both axes.

    Returns an SVG string.
    """
    d = draw.Drawing(width, height)

    margin_l = 55
    margin_b = 45
    margin_t = 20
    margin_r = 20
    plot_w = width - margin_l - margin_r
    plot_h = height - margin_b - margin_t

    # Compute data range
    all_x = []
    all_y = []
    for seg in segments:
        all_x.extend([seg['x_start'], seg['x_end']])
        all_y.extend([seg['y_start'], seg['y_end']])
    x_lo, x_hi = min(all_x), max(all_x)
    y_lo, y_hi = min(all_y), max(all_y)
    # Add padding
    x_pad = max(0.5, (x_hi - x_lo) * 0.08)
    y_pad = max(0.5, (y_hi - y_lo) * 0.08)
    x_lo -= x_pad
    x_hi += x_pad
    y_lo -= y_pad
    y_hi += y_pad

    def to_px(x, y):
        px = margin_l + (x - x_lo) / (x_hi - x_lo) * plot_w
        py = margin_t + plot_h - (y - y_lo) / (y_hi - y_lo) * plot_h
        return px, py

    # Draw axes
    origin_px = margin_l
    origin_py = margin_t + plot_h
    # X-axis
    d.append(draw.Line(origin_px, origin_py, origin_px + plot_w, origin_py,
                       stroke='#374151', stroke_width=2))
    # Y-axis
    d.append(draw.Line(origin_px, origin_py, origin_px, margin_t,
                       stroke='#374151', stroke_width=2))

    # Axis labels
    d.append(draw.Text(x_label, 16, origin_px + plot_w / 2, height - 8,
                       text_anchor='middle', fill='#374151'))
    # Y-label rotated
    d.append(draw.Text(y_label, 16, 12, margin_t + plot_h / 2,
                       text_anchor='middle', fill='#374151',
                       transform=f'rotate(-90, 12, {margin_t + plot_h / 2})'))

    # Arrowheads on axes
    ax_top = margin_t
    d.append(draw.Lines(origin_px, ax_top, origin_px - 4, ax_top + 8,
                        origin_px + 4, ax_top + 8,
                        close=True, fill='#374151'))
    ax_right = origin_px + plot_w
    d.append(draw.Lines(ax_right, origin_py, ax_right - 8, origin_py - 4,
                        ax_right - 8, origin_py + 4,
                        close=True, fill='#374151'))

    # Light grid lines
    for i in range(1, 5):
        gy = origin_py - i * plot_h / 4
        d.append(draw.Line(origin_px, gy, origin_px + plot_w, gy,
                           stroke='#e5e7eb', stroke_width=0.5))

    # Tick marks with numbers (when show_scale is True)
    if show_scale:
        x_int_lo = math.ceil(x_lo)
        x_int_hi = math.floor(x_hi)
        for xv in range(x_int_lo, x_int_hi + 1):
            px, _ = to_px(xv, y_lo)
            d.append(draw.Line(px, origin_py - 3, px, origin_py + 3,
                               stroke='#374151', stroke_width=1))
            d.append(draw.Text(str(xv), 15, px, origin_py + 16,
                               text_anchor='middle', fill='#6b7280'))

        y_int_lo = math.ceil(y_lo)
        y_int_hi = math.floor(y_hi)
        for yv in range(y_int_lo, y_int_hi + 1):
            _, py = to_px(x_lo, yv)
            d.append(draw.Line(origin_px - 3, py, origin_px + 3, py,
                               stroke='#374151', stroke_width=1))
            d.append(draw.Text(str(yv), 15, origin_px - 8, py + 4,
                               text_anchor='end', fill='#6b7280'))

    # Draw each segment
    for seg in segments:
        x1, y1 = to_px(seg['x_start'], seg['y_start'])
        x2, y2 = to_px(seg['x_end'], seg['y_end'])
        curve_type = seg.get('curve', 'linear')

        if curve_type == 'linear':
            d.append(draw.Line(x1, y1, x2, y2,
                               stroke='#2563eb', stroke_width=2.5))
        else:
            # Bezier curve: control point determines concavity
            mid_x = (x1 + x2) / 2
            if curve_type == 'concave_up':
                # Control point below the midpoint line
                ctrl_x = mid_x
                ctrl_y = max(y1, y2) + abs(y1 - y2) * 0.3
            elif curve_type == 'concave_down':
                # Control point above the midpoint line
                ctrl_x = mid_x
                ctrl_y = min(y1, y2) - abs(y1 - y2) * 0.3
            else:
                ctrl_x, ctrl_y = mid_x, (y1 + y2) / 2

            p = draw.Path(fill='none', stroke='#2563eb', stroke_width=2.5)
            p.M(x1, y1)
            p.Q(ctrl_x, ctrl_y, x2, y2)
            d.append(p)

    # Draw dots at segment endpoints
    drawn_pts = set()
    for seg in segments:
        for xv, yv in [(seg['x_start'], seg['y_start']),
                        (seg['x_end'], seg['y_end'])]:
            key = (round(xv, 4), round(yv, 4))
            if key not in drawn_pts:
                px, py = to_px(xv, yv)
                d.append(draw.Circle(px, py, 3.5,
                                     fill='#2563eb', stroke='white', stroke_width=1.5))
                drawn_pts.add(key)

    return d.as_svg()


# ============================================================
# CONE INSIDE CYLINDER (composite)
# ============================================================

def cone_in_cylinder_svg(radius_val, height_val,
                         label_r="", label_h="",
                         width=280, height=320):
    """Draw a cone inscribed inside a cylinder (same radius and height).

    Shows the cylinder in pseudo-3D with the cone visible inside it.
    """
    d = draw.Drawing(width, height)
    cx = width / 2
    margin_top = 50
    margin_bot = 50
    r_px = min(width / 2 - 40, 90)  # pixel radius
    h_px = height - margin_top - margin_bot - 40  # pixel height
    ey = r_px * 0.3  # ellipse y-radius

    top_cy = margin_top + ey
    bot_cy = top_cy + h_px

    # --- Cylinder ---
    # Side lines
    d.append(draw.Line(cx - r_px, top_cy, cx - r_px, bot_cy,
                       stroke='#2563eb', stroke_width=2))
    d.append(draw.Line(cx + r_px, top_cy, cx + r_px, bot_cy,
                       stroke='#2563eb', stroke_width=2))

    # Bottom ellipse (full)
    d.append(draw.Ellipse(cx, bot_cy, r_px, ey,
                          fill='#dbeafe', stroke='#2563eb', stroke_width=2))

    # Body fill
    d.append(draw.Rectangle(cx - r_px, top_cy, 2 * r_px, h_px,
                             fill='#e8f4fd', stroke='none', opacity=0.3))

    # --- Cone inside (from top center apex down to base circle) ---
    # Cone body (triangle fill, semi-transparent)
    d.append(draw.Lines(cx, top_cy, cx - r_px, bot_cy, cx + r_px, bot_cy,
                        close=True, fill='#fef3c7', stroke='none', opacity=0.5))

    # Cone side lines
    d.append(draw.Line(cx, top_cy, cx - r_px, bot_cy,
                       stroke='#d97706', stroke_width=2,
                       stroke_dasharray='6,3'))
    d.append(draw.Line(cx, top_cy, cx + r_px, bot_cy,
                       stroke='#d97706', stroke_width=2,
                       stroke_dasharray='6,3'))

    # Top ellipse (cylinder cap, on top of everything)
    d.append(draw.Ellipse(cx, top_cy, r_px, ey,
                          fill='#bfdbfe', stroke='#2563eb', stroke_width=2,
                          opacity=0.6))

    # Bottom ellipse front arc (redraw on top)
    p = draw.Path(fill='none', stroke='#2563eb', stroke_width=2)
    p.M(cx - r_px, bot_cy)
    p.A(r_px, ey, 0, 0, 0, cx + r_px, bot_cy)
    d.append(p)

    # Apex dot
    d.append(draw.Circle(cx, top_cy, 3, fill='#d97706'))

    # --- Labels ---
    # Radius line on bottom
    d.append(draw.Line(cx, bot_cy, cx + r_px, bot_cy,
                       stroke='#dc2626', stroke_width=1.5,
                       stroke_dasharray='5,3'))
    d.append(draw.Circle(cx, bot_cy, 2, fill='#dc2626'))

    r_lbl = label_r if label_r else f"r = {radius_val}"
    d.append(draw.Text(r_lbl, 28, cx + r_px / 2, bot_cy + 28,
                       text_anchor='middle', fill='#dc2626', font_weight='bold'))

    # Height line (right side, outside cylinder)
    hx = cx + r_px + 20
    d.append(draw.Line(hx, top_cy, hx, bot_cy,
                       stroke='#dc2626', stroke_width=1.5))
    # Arrow heads
    d.append(draw.Lines(hx - 4, top_cy + 6, hx, top_cy, hx + 4, top_cy + 6,
                        close=False, fill='none', stroke='#dc2626', stroke_width=1.5))
    d.append(draw.Lines(hx - 4, bot_cy - 6, hx, bot_cy, hx + 4, bot_cy - 6,
                        close=False, fill='none', stroke='#dc2626', stroke_width=1.5))

    h_lbl = label_h if label_h else f"h = {height_val}"
    d.append(draw.Text(h_lbl, 28, hx + 10, (top_cy + bot_cy) / 2,
                       text_anchor='start', fill='#dc2626', font_weight='bold',
                       dominant_baseline='middle'))

    # Legend labels
    d.append(draw.Text("Cylinder", 24, 10, height - 14,
                       fill='#2563eb', font_weight='bold'))
    d.append(draw.Text("Cone", 24, width - 60, height - 14,
                       fill='#d97706', font_weight='bold'))

    return d.as_svg()


# ============================================================
# CUBE (pseudo-3D)
# ============================================================

def cube_3d_svg(side_val, label_side="", width=240, height=260):
    """Draw a pseudo-3D cube with labeled side length."""
    d = draw.Drawing(width, height)
    cx = width / 2
    margin = 40

    s_px = min(width - 2 * margin - 40, height - 2 * margin - 40, 130)
    depth = s_px * 0.35  # foreshortened depth

    # Front face corners
    fl = (cx - s_px / 2, height - margin)             # front-left-bottom
    fr = (cx + s_px / 2, height - margin)             # front-right-bottom
    ftl = (cx - s_px / 2, height - margin - s_px)     # front-left-top
    ftr = (cx + s_px / 2, height - margin - s_px)     # front-right-top

    # Back face corners (offset up-right for 3D effect)
    bl = (ftl[0] + depth * 0.7, ftl[1] - depth)
    br = (ftr[0] + depth * 0.7, ftr[1] - depth)
    bbl = (fl[0] + depth * 0.7, fl[1] - depth)        # back-bottom-left
    bbr = (fr[0] + depth * 0.7, fr[1] - depth)        # back-bottom-right

    # Back edges (dashed, hidden)
    d.append(draw.Line(bl[0], bl[1], bbl[0], bbl[1],
                       stroke='#2563eb', stroke_width=1.5,
                       stroke_dasharray='5,3'))
    d.append(draw.Line(bbl[0], bbl[1], bbr[0], bbr[1],
                       stroke='#2563eb', stroke_width=1.5,
                       stroke_dasharray='5,3'))
    d.append(draw.Line(bl[0], bl[1], br[0], br[1],
                       stroke='#2563eb', stroke_width=1.5,
                       stroke_dasharray='5,3'))

    # Front face (filled)
    d.append(draw.Lines(fl[0], fl[1], fr[0], fr[1], ftr[0], ftr[1], ftl[0], ftl[1],
                        close=True, fill='#e8f4fd', stroke='#2563eb', stroke_width=2))

    # Top face (filled)
    d.append(draw.Lines(ftl[0], ftl[1], ftr[0], ftr[1], br[0], br[1], bl[0], bl[1],
                        close=True, fill='#dbeafe', stroke='#2563eb', stroke_width=2))

    # Right face (filled)
    d.append(draw.Lines(fr[0], fr[1], ftr[0], ftr[1], br[0], br[1], bbr[0], bbr[1],
                        close=True, fill='#bfdbfe', stroke='#2563eb', stroke_width=2))

    # Side length label (front bottom edge)
    s_lbl = label_side if label_side else f"s = {side_val}"
    d.append(draw.Text(s_lbl, 28, (fl[0] + fr[0]) / 2, fl[1] + 26,
                       text_anchor='middle', fill='#dc2626', font_weight='bold'))

    return d.as_svg()


# ============================================================
# PYRAMID + CUBE SIDE-BY-SIDE (single canvas, no nesting)
# ============================================================

def pyramid_and_cube_svg(side_val, height_val,
                         label_base="", label_h="", label_cube="",
                         width=480, height=280):
    """Draw a pyramid and cube side by side in a single canvas.

    Draws both shapes natively (no SVG nesting) for fpdf2 compatibility.
    """
    d = draw.Drawing(width, height)
    half = width / 2
    margin = 30
    bot_y = height - margin - 10

    # --- LEFT: Pyramid ---
    lcx = half / 2  # left half center
    pyr_base = min(half - 2 * margin, 120)
    pyr_half = pyr_base / 2
    pyr_depth = pyr_half * 0.4

    pyr_apex_y = margin + 10
    pyr_base_y = bot_y

    # Base corners (parallelogram)
    pbl = (lcx - pyr_half, pyr_base_y)
    pbr = (lcx + pyr_half, pyr_base_y)
    ptr = (lcx + pyr_half + pyr_depth * 0.6, pyr_base_y - pyr_depth)
    ptl = (lcx - pyr_half + pyr_depth * 0.6, pyr_base_y - pyr_depth)
    apex = (lcx + pyr_depth * 0.3, pyr_apex_y)

    # Back edges (dashed)
    d.append(draw.Line(ptl[0], ptl[1], ptr[0], ptr[1],
                       stroke='#2563eb', stroke_width=1.5, stroke_dasharray='5,3'))
    d.append(draw.Line(pbl[0], pbl[1], ptl[0], ptl[1],
                       stroke='#2563eb', stroke_width=1.5, stroke_dasharray='5,3'))
    d.append(draw.Line(ptl[0], ptl[1], apex[0], apex[1],
                       stroke='#2563eb', stroke_width=1.5, stroke_dasharray='5,3'))

    # Front face
    d.append(draw.Lines(pbl[0], pbl[1], pbr[0], pbr[1], apex[0], apex[1],
                        close=True, fill='#e8f4fd', stroke='#2563eb', stroke_width=2))
    # Right face
    d.append(draw.Lines(pbr[0], pbr[1], ptr[0], ptr[1], apex[0], apex[1],
                        close=True, fill='#dbeafe', stroke='#2563eb', stroke_width=2))

    # Dashed height line
    base_center = ((pbl[0] + ptr[0]) / 2, (pbl[1] + ptr[1]) / 2)
    d.append(draw.Line(apex[0], apex[1], base_center[0], base_center[1],
                       stroke='#dc2626', stroke_width=1.5, stroke_dasharray='5,3'))

    # Labels
    b_lbl = label_base if label_base else f"s = {side_val}"
    d.append(draw.Text(b_lbl, 24, (pbl[0] + pbr[0]) / 2, pyr_base_y + 24,
                       text_anchor='middle', fill='#1e40af', font_weight='bold'))
    h_lbl = label_h if label_h else f"h = {height_val}"
    d.append(draw.Text(h_lbl, 24, base_center[0] + 12, (apex[1] + base_center[1]) / 2,
                       text_anchor='start', fill='#dc2626', font_weight='bold'))

    d.append(draw.Text("Pyramid", 22, lcx, height - 6,
                       text_anchor='middle', fill='#1e40af', font_weight='bold'))

    # --- Divider ---
    d.append(draw.Line(half, 10, half, height - 10,
                       stroke='#94a3b8', stroke_width=1, stroke_dasharray='4,4'))

    # --- RIGHT: Cube ---
    rcx = half + half / 2  # right half center
    s_px = min(half - 2 * margin - 30, 110)
    cdepth = s_px * 0.35

    cfl = (rcx - s_px / 2, bot_y)
    cfr = (rcx + s_px / 2, bot_y)
    cftl = (rcx - s_px / 2, bot_y - s_px)
    cftr = (rcx + s_px / 2, bot_y - s_px)

    cbl = (cftl[0] + cdepth * 0.7, cftl[1] - cdepth)
    cbr = (cftr[0] + cdepth * 0.7, cftr[1] - cdepth)
    cbbl = (cfl[0] + cdepth * 0.7, cfl[1] - cdepth)
    cbbr = (cfr[0] + cdepth * 0.7, cfr[1] - cdepth)

    # Back edges (dashed)
    d.append(draw.Line(cbl[0], cbl[1], cbbl[0], cbbl[1],
                       stroke='#2563eb', stroke_width=1.5, stroke_dasharray='5,3'))
    d.append(draw.Line(cbbl[0], cbbl[1], cbbr[0], cbbr[1],
                       stroke='#2563eb', stroke_width=1.5, stroke_dasharray='5,3'))
    d.append(draw.Line(cbl[0], cbl[1], cbr[0], cbr[1],
                       stroke='#2563eb', stroke_width=1.5, stroke_dasharray='5,3'))

    # Front face
    d.append(draw.Lines(cfl[0], cfl[1], cfr[0], cfr[1], cftr[0], cftr[1], cftl[0], cftl[1],
                        close=True, fill='#e8f4fd', stroke='#2563eb', stroke_width=2))
    # Top face
    d.append(draw.Lines(cftl[0], cftl[1], cftr[0], cftr[1], cbr[0], cbr[1], cbl[0], cbl[1],
                        close=True, fill='#dbeafe', stroke='#2563eb', stroke_width=2))
    # Right face
    d.append(draw.Lines(cfr[0], cfr[1], cftr[0], cftr[1], cbr[0], cbr[1], cbbr[0], cbbr[1],
                        close=True, fill='#bfdbfe', stroke='#2563eb', stroke_width=2))

    # Cube label
    c_lbl = label_cube if label_cube else f"s = {side_val}"
    d.append(draw.Text(c_lbl, 24, (cfl[0] + cfr[0]) / 2, bot_y + 24,
                       text_anchor='middle', fill='#dc2626', font_weight='bold'))

    d.append(draw.Text("Cube", 22, rcx, height - 6,
                       text_anchor='middle', fill='#1e40af', font_weight='bold'))

    return d.as_svg()
