# -*- coding: utf-8 -*-
"""Build-time content validator for the skill-intervention JSONs.

Fails (exit 1) if any shipped skill would silently degrade the teacher's
close-the-loop experience. Checks, for every standard:
  1. web/content/skills and Cooties/data/skills mirrors parse-equal.
  2. Every non-foundation skill has non-empty next_steps.if_pass AND if_fail
     (an empty route collapses the packet to a generic "repeat this skill",
     which contradicts the authored diagnostic_flow — review priority #4).

Run:  python engine/validate_content.py
Wire into CI as a gate before shipping content.
"""
import json, io, glob, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web", "content", "skills")
COO = os.path.join(ROOT, "Cooties", "data", "skills")

def main():
    failures = []
    for wf in sorted(glob.glob(os.path.join(WEB, "*.json"))):
        base = os.path.basename(wf)
        wj = json.load(io.open(wf, encoding="utf-8"))
        cf = os.path.join(COO, base)
        if not os.path.exists(cf):
            failures.append(f"{base}: missing Cooties mirror")
            continue
        cj = json.load(io.open(cf, encoding="utf-8"))
        if wj != cj:
            failures.append(f"{base}: web/Cooties mirrors differ")
        for s in wj.get("skills", []):
            if s.get("column") == "foundation":
                continue
            sid = s.get("skill_id", "?")
            ns = s.get("next_steps") or {}
            if not (ns.get("if_pass") or "").strip():
                failures.append(f"{sid} ({base}): empty next_steps.if_pass")
            if not (ns.get("if_fail") or "").strip():
                failures.append(f"{sid} ({base}): empty next_steps.if_fail")

    if failures:
        print(f"CONTENT VALIDATION FAILED ({len(failures)} issue(s)):")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    print("CONTENT VALIDATION PASSED")

if __name__ == "__main__":
    main()
