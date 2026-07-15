# -*- coding: utf-8 -*-
"""Representation-coverage checker for the skill-intervention JSONs.

Catches the two ways a lesson's visual can silently fail on screen:
  1. A render_data/visual whose `type` no web renderer supports — the
     projection and skill pages render NOTHING for it (the printed packet
     may still work, which is how these hide).
  2. Text that promises a visual ("the table shows...", "shown below",
     "the double number line below") with no render_data attached and no
     shown_work lines to carry it.

Exit 1 on any finding. Run alongside validate_content.py; when a new visual
type is added to web/src/components/intervention/InlineMath.tsx (or the
engine's _shape_render_data_to_svg), add it to WEB_SUPPORTED here.

Run:  python engine/check_representations.py
"""
import json, io, glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web", "content", "skills")
if not os.path.isdir(WEB):
    WEB = os.path.join(ROOT, "content", "skills")  # bundled layout

# InlineDiagram's dispatch + the engine's shape->svg conversions.
WEB_SUPPORTED = {
    "number_line", "number_line_point", "coordinate_grid", "svg_html",
    "hundredths_grid", "bar_model", "percent_bar", "tape_diagram",
    "fraction_bars", "double_number_line", "data_table",
    "composite_shape", "polygon_angles", "rectangular_prism",
}

PROMISE = re.compile(
    r"\b(the (double number line|number line|tape diagram|table|graph|grid|"
    r"dot plot|scatter ?plot|model|diagram|figure|picture) "
    r"(below|shown|shows|above))|\bshown (below|above)\b|\bpictured\b", re.I)


def main():
    findings = []
    for f in sorted(glob.glob(os.path.join(WEB, "*.json"))):
        if f.endswith(".bak"):
            continue
        d = json.load(io.open(f, encoding="utf-8"))
        std = d.get("standard_code", os.path.basename(f))
        for s in d.get("skills", []):
            sid = s.get("skill_id", "?")
            script_has_visual = any(st.get("visual")
                                    for st in (s.get("worked_example_script") or []))

            def visit(surface, obj, in_script=False):
                rd = (obj or {}).get("render_data") or (obj or {}).get("visual")
                txt = (obj or {}).get("stem") or (obj or {}).get("text") or ""
                t = (rd or {}).get("type")
                if t and t not in WEB_SUPPORTED:
                    findings.append(f"{std} {sid} [{surface}]: unsupported visual type '{t}'")
                elif not t and PROMISE.search(txt):
                    # A visual earlier in the same script, or shown_work
                    # lines, already put the promised thing on screen.
                    if in_script and script_has_visual:
                        return
                    if (obj or {}).get("shown_work"):
                        return
                    findings.append(f"{std} {sid} [{surface}]: text promises a visual, none attached: \"{txt[:70]}\"")

            for it in (s.get("sample_items") or []):
                visit("item", it)
                for ch in (it.get("choices_render") or []):
                    visit("choice", {"render_data": ch})
                for p in (it.get("parts") or []):
                    visit("part", p)
            for it in (s.get("practice_problems") or []):
                visit("practice", it)
            visit("worked_solution", s.get("worked_solution"))
            visit("faded_example", s.get("faded_example"))
            for st in (s.get("worked_example_script") or []):
                visit("we_step", st, in_script=True)

    if findings:
        print(f"REPRESENTATION CHECK FAILED ({len(findings)} finding(s)):")
        for x in findings:
            print("  -", x)
        sys.exit(1)
    print("REPRESENTATION CHECK PASSED")


if __name__ == "__main__":
    main()
