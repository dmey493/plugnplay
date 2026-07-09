"""
Skill authoring driver — pure Python orchestrator. No LLM calls.

The driver reads a live skill from `Cooties/data/skills/{standard}.json`,
runs it through the 5-gate pipeline, and writes the authored result to
`Cooties/data/skills/_staging/{standard}.json`. Each gate is run by a
Claude Code subagent reading the matching directive in
`Cooties/directives/skill_authoring/`. The driver itself is the glue:

  1. `prepare_input(skill_id, gate_name)` — emits the JSON the next
     subagent needs as input.
  2. (subagent runs externally via Claude Code Agent tool)
  3. `accept_output(skill_id, gate_name, output_json)` — validates the
     subagent's output against the directive's expected shape, applies it
     to the staging copy, and appends gate_log entries on rejection.

Two ways to drive this:

  - Interactive: a session (this one) calls `prepare_input`, spawns a
    subagent with the directive + input, then calls `accept_output`.
  - Batch: a script loops over a list of skill_ids and gates, but still
    needs a Claude Code session to drive the subagent calls. There's no
    standalone autopilot — that would require an API key, which we're not
    using.

Run gates manually:
    python engine/agents/author_skill.py prepare 6.AF.1 6AF1-F1 map_skill
    # -> prints JSON input for the map_skill agent

    # ... subagent produces output, save to file or paste back ...

    python engine/agents/author_skill.py accept 6.AF.1 6AF1-F1 map_skill output.json
    # -> validates + applies to staging
"""

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LIVE_DIR = ROOT / "Cooties" / "data" / "skills"
STAGING_DIR = LIVE_DIR / "_staging"
DIRECTIVES_DIR = ROOT / "Cooties" / "directives" / "skill_authoring"

GATES = ["map_skill", "author_stems", "check_math", "check_subskill_fit", "author_strategy"]


# ---------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------

def _live_path(standard: str) -> Path:
    return LIVE_DIR / f"{standard}.json"


def _staging_path(standard: str) -> Path:
    return STAGING_DIR / f"{standard}.json"


def _gate_log_path(standard: str) -> Path:
    return STAGING_DIR / f"{standard}.gate_log.md"


def _scratch_path(standard: str, skill_id: str, gate: str) -> Path:
    """Where intermediate gate outputs land between steps. Cleared after
    a skill promotes; useful for debugging and for resuming a partial
    pipeline run."""
    p = STAGING_DIR / "_scratch" / standard / skill_id
    p.mkdir(parents=True, exist_ok=True)
    return p / f"{gate}.json"


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _append_log(standard: str, line: str) -> None:
    p = _gate_log_path(standard)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(line if line.endswith("\n") else line + "\n")


def _ensure_staging_copy(standard: str) -> dict:
    """Make sure a staging copy of the live file exists. Subagent edits
    apply to the staging copy, never to live, until promotion."""
    sp = _staging_path(standard)
    if not sp.exists():
        live = _load_json(_live_path(standard))
        _save_json(sp, copy.deepcopy(live))
    return _load_json(sp)


def _find_skill(data: dict, skill_id: str) -> dict | None:
    for s in data.get("skills", []):
        if s.get("skill_id") == skill_id:
            return s
    return None


def _sibling_skills(data: dict, skill_id: str) -> list[dict]:
    return [
        {"skill_id": s["skill_id"], "name": s["name"]}
        for s in data.get("skills", [])
        if s.get("skill_id") != skill_id
    ]


# ---------------------------------------------------------------------
# Engine stem inventory
# ---------------------------------------------------------------------
# The mapper needs a list of available engine stems with their shapes so
# it can decide whether engine_stems applies. We build this at runtime
# from the existing engine.stems package — for each standard, list the
# stems and a one-line shape description (best-effort, drawn from the
# stem class's __doc__ or first stem method).

def _available_engine_stems(standard: str) -> list[dict]:
    """Return [{"index": N, "shape": "..."}] for stems the engine has
    for this standard. Best-effort — if the import fails we return an
    empty list and the mapper just won't suggest engine_stems."""
    try:
        sys.path.insert(0, str(ROOT))
        from engine.generate_skill_packet import _load_stem_class  # noqa: E402

        cls = _load_stem_class(standard)
        if cls is None:
            return []
        try:
            inst = cls(seed=1)
        except Exception:
            return []
        results = []
        for i in range(1, 12):
            method = getattr(inst, f"_stem{i}", None) or getattr(inst, f"stem{i}", None)
            if method is None:
                continue
            doc = (method.__doc__ or "").strip().split("\n")[0]
            results.append({"index": i, "shape": doc or "(no docstring)"})
        return results
    except Exception:
        return []


# ---------------------------------------------------------------------
# prepare_input — emit JSON the next subagent needs
# ---------------------------------------------------------------------

def prepare_input(standard: str, skill_id: str, gate: str) -> dict:
    """Emit the JSON the named gate's subagent needs as input. The
    subagent reads the matching directive file alongside this input."""
    if gate not in GATES:
        raise ValueError(f"Unknown gate: {gate}. Must be one of {GATES}.")

    staging = _ensure_staging_copy(standard)
    skill = _find_skill(staging, skill_id)
    if skill is None:
        raise ValueError(f"Skill {skill_id} not found in {standard}.")

    if gate == "map_skill":
        return {
            "skill_id": skill["skill_id"],
            "name": skill.get("name", ""),
            "column": skill.get("column", ""),
            "parent_standard": standard,
            "standard_text": staging.get("standard_text", ""),
            "canonical_error": skill.get("canonical_error", {}),
            "i_do_script": skill.get("i_do_script", ""),
            "redirect_script": skill.get("redirect_script", {}),
            "existing_sample_items": skill.get("sample_items", []),
            "available_engine_stems": _available_engine_stems(standard),
        }

    # All later gates depend on the map_skill output being saved.
    map_path = _scratch_path(standard, skill_id, "map_skill")
    if not map_path.exists():
        raise RuntimeError(
            f"map_skill must run first. Expected {map_path} to exist."
        )
    map_out = _load_json(map_path)

    if gate == "author_stems":
        return {
            "skill_id": skill["skill_id"],
            "name": skill.get("name", ""),
            "canonical_error": skill.get("canonical_error", {}),
            "i_do_script": skill.get("i_do_script", ""),
            "target_item_count": map_out.get("target_item_count", 18),
            "item_shape": map_out.get("item_shape", {}),
            "notes_for_stem_author": map_out.get("notes_for_stem_author", ""),
            "existing_sample_items": skill.get("sample_items", []),
        }

    # check_math, check_subskill_fit, author_strategy all need the items
    # produced by author_stems.
    stems_path = _scratch_path(standard, skill_id, "author_stems")
    if not stems_path.exists():
        raise RuntimeError(f"author_stems must run before {gate}.")
    stems_out = _load_json(stems_path)
    items = stems_out.get("sample_items", [])
    indexed = [{"index": i, **it} for i, it in enumerate(items)]

    if gate == "check_math":
        return {
            "skill_id": skill["skill_id"],
            "item_shape": map_out.get("item_shape", {}),
            "items": indexed,
        }

    if gate == "check_subskill_fit":
        return {
            "skill_id": skill["skill_id"],
            "name": skill.get("name", ""),
            "canonical_error": skill.get("canonical_error", {}),
            "i_do_script": skill.get("i_do_script", ""),
            "items": indexed,
            "sibling_skills": _sibling_skills(staging, skill_id),
        }

    if gate == "author_strategy":
        # Filter to items that survived both math + sub-skill gates.
        surviving = _surviving_items(standard, skill_id, items)
        return {
            "skill_id": skill["skill_id"],
            "name": skill.get("name", ""),
            "column": skill.get("column", ""),
            "canonical_error": skill.get("canonical_error", {}),
            "i_do_script": skill.get("i_do_script", ""),
            "redirect_script": skill.get("redirect_script", {}),
            "vocabulary": skill.get("vocabulary", []),
            "sample_items": surviving,
            "printable_artifact_decision": map_out.get("printable_artifact", {}),
        }

    raise ValueError(f"Unhandled gate: {gate}")


def _surviving_items(standard: str, skill_id: str, items: list[dict]) -> list[dict]:
    """Apply both gate results, drop rejected items, return the rest in
    original order with `_source` cleared."""
    keep = [True] * len(items)
    for gate in ("check_math", "check_subskill_fit"):
        path = _scratch_path(standard, skill_id, gate)
        if not path.exists():
            continue
        out = _load_json(path)
        results = out.get("results", [])
        for r in results:
            i = r.get("index")
            if not isinstance(i, int) or i >= len(keep):
                continue
            if not r.get("pass" if gate == "check_math" else "fits", True):
                keep[i] = False
    surviving = [it for i, it in enumerate(items) if keep[i]]
    return surviving


# ---------------------------------------------------------------------
# accept_output — validate + apply
# ---------------------------------------------------------------------

def accept_output(standard: str, skill_id: str, gate: str, output: dict) -> dict:
    """Validate the subagent's output against the directive's expected
    shape, save it to the scratch dir, and (for the final gate) merge it
    into the staging copy of the skill JSON."""
    if gate not in GATES:
        raise ValueError(f"Unknown gate: {gate}.")

    # Always persist the raw output for resumability + debugging.
    _save_json(_scratch_path(standard, skill_id, gate), output)

    if "error" in output:
        _append_log(standard, f"## {skill_id} -- {gate}: ERROR\n- {output['error']}: {output.get('reason', '')}\n")
        return {"ok": False, "reason": output["error"]}

    # Per-gate validation.
    if gate == "map_skill":
        for k in ("target_item_count", "item_shape", "engine_stems",
                  "printable_artifact", "notes_for_stem_author"):
            if k not in output:
                return {"ok": False, "reason": f"map_skill output missing field: {k}"}
        return {"ok": True}

    if gate == "author_stems":
        items = output.get("sample_items", [])
        if not isinstance(items, list) or len(items) == 0:
            return {"ok": False, "reason": "author_stems produced no items."}
        if "warning" in output:
            _append_log(standard,
                        f"## {skill_id} -- author_stems: short\n"
                        f"- Produced {output.get('produced')} of {output.get('target')} items.\n"
                        f"- {output.get('reason', '')}\n")
        return {"ok": True, "items_produced": len(items)}

    if gate == "check_math":
        results = output.get("results", [])
        failed = [r for r in results if not r.get("pass", False)]
        if failed:
            lines = [f"## {skill_id} -- check_math\n",
                     f"- Rejected {len(failed)}/{len(results)} items.\n"]
            for r in failed:
                lines.append(
                    f"- Item {r.get('index')}: authored '{r.get('authored_answer')}', "
                    f"computed '{r.get('computed_answer')}'. {r.get('issue', '')}\n"
                )
            _append_log(standard, "".join(lines))
        return {"ok": True, "passed": len(results) - len(failed), "failed": len(failed)}

    if gate == "check_subskill_fit":
        results = output.get("results", [])
        failed = [r for r in results if not r.get("fits", False)]
        if failed:
            lines = [f"## {skill_id} -- check_subskill_fit\n",
                     f"- Rejected {len(failed)}/{len(results)} items.\n"]
            for r in failed:
                lines.append(
                    f"- Item {r.get('index')}: belongs to {r.get('fit_target')}. "
                    f"{r.get('issue', '')}\n"
                )
            _append_log(standard, "".join(lines))
        return {"ok": True, "passed": len(results) - len(failed), "failed": len(failed)}

    if gate == "author_strategy":
        # Final gate — merge everything into staging.
        return _merge_into_staging(standard, skill_id, output)

    return {"ok": False, "reason": f"Unhandled gate: {gate}"}


def _merge_into_staging(standard: str, skill_id: str, strategy_out: dict) -> dict:
    """Apply the entire pipeline's output to the staging skill JSON."""
    staging = _load_json(_staging_path(standard))
    skill = _find_skill(staging, skill_id)
    if skill is None:
        return {"ok": False, "reason": f"Skill {skill_id} not in staging."}

    # Items that survived both gates
    stems_out = _load_json(_scratch_path(standard, skill_id, "author_stems"))
    items = stems_out.get("sample_items", [])
    surviving = _surviving_items(standard, skill_id, items)
    if not surviving:
        return {"ok": False, "reason": "No items survived gates; nothing to merge."}
    skill["sample_items"] = surviving

    # engine_stems decision from the mapper
    map_out = _load_json(_scratch_path(standard, skill_id, "map_skill"))
    es = map_out.get("engine_stems", {})
    if es.get("applies") and es.get("indices"):
        skill["engine_stems"] = es["indices"]
    elif "engine_stems" in skill and not es.get("applies"):
        # Mapper said no — clear any stale mapping.
        skill.pop("engine_stems", None)

    # Strategy outputs
    if "worked_example_script" in strategy_out and strategy_out["worked_example_script"]:
        skill["worked_example_script"] = strategy_out["worked_example_script"]
    if strategy_out.get("coaching_note"):
        skill["coaching_note"] = strategy_out["coaching_note"]
    elif "coaching_note" in skill:
        skill.pop("coaching_note", None)
    if strategy_out.get("printable_artifact"):
        skill["printable_artifact"] = strategy_out["printable_artifact"]

    _save_json(_staging_path(standard), staging)
    _append_log(standard,
                f"## {skill_id} -- MERGED\n"
                f"- {len(surviving)} items, "
                f"engine_stems={skill.get('engine_stems', 'none')}, "
                f"artifact={'yes' if skill.get('printable_artifact') else 'no'}\n")
    return {"ok": True, "items_kept": len(surviving)}


# ---------------------------------------------------------------------
# Promotion — staging -> live
# ---------------------------------------------------------------------

def promote(standard: str) -> dict:
    """Copy staging file to live. Caller (you) reviews the gate log before
    running this. Backs up live first."""
    sp = _staging_path(standard)
    lp = _live_path(standard)
    if not sp.exists():
        return {"ok": False, "reason": f"No staging file for {standard}."}
    backup = lp.with_suffix(".json.bak")
    if lp.exists():
        backup.write_text(lp.read_text(encoding="utf-8"), encoding="utf-8")
    lp.write_text(sp.read_text(encoding="utf-8"), encoding="utf-8")
    return {"ok": True, "backup": str(backup), "live": str(lp)}


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Skill authoring driver.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("prepare", help="Emit JSON input for a gate's subagent.")
    p.add_argument("standard")
    p.add_argument("skill_id")
    p.add_argument("gate", choices=GATES)
    p.add_argument("--out", default=None,
                    help="Write to this path (UTF-8). Default: stdout.")

    p = sub.add_parser("accept", help="Apply a gate's output to staging.")
    p.add_argument("standard")
    p.add_argument("skill_id")
    p.add_argument("gate", choices=GATES)
    p.add_argument("output_path", help="Path to JSON file with the subagent's output.")

    p = sub.add_parser("promote", help="Copy staging skill file to live.")
    p.add_argument("standard")

    p = sub.add_parser("show", help="Print staging file path + gate log.")
    p.add_argument("standard")

    args = parser.parse_args()

    if args.cmd == "prepare":
        out = prepare_input(args.standard, args.skill_id, args.gate)
        if args.out:
            # File path always UTF-8 — bypasses Windows console codepage so
            # em-dashes / smart quotes / emoji survive the round trip.
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(out, f, indent=2, ensure_ascii=False)
            print(args.out)
        else:
            print(json.dumps(out, indent=2, ensure_ascii=False))
    elif args.cmd == "accept":
        with open(args.output_path, "r", encoding="utf-8") as f:
            output = json.load(f)
        result = accept_output(args.standard, args.skill_id, args.gate, output)
        print(json.dumps(result, indent=2))
    elif args.cmd == "promote":
        print(json.dumps(promote(args.standard), indent=2))
    elif args.cmd == "show":
        sp = _staging_path(args.standard)
        lp = _gate_log_path(args.standard)
        print(f"Staging: {sp}  ({'exists' if sp.exists() else 'not yet'})")
        print(f"Gate log: {lp}  ({'exists' if lp.exists() else 'not yet'})")
        if lp.exists():
            print("\n--- gate log ---")
            print(lp.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
