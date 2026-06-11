#!/usr/bin/env python3
"""
coverage.py — regenerate the UI Contract coverage map (CONTRACT-FORMAT.md §1, §7, F9.3).

Replaces the HAND-DERIVED COVERAGE.md with a machine join:
  class ↔ entries ↔ status  (against atlas/FEATURE-ATLAS.md)
  + the affordance-grain closure (defined vs touched, BOTH directions)
  + the planned/building/live counts
  + the COVERED / PLANNED-ONLY / UNMAPPED class roll-up
  + the buildable-gaps vs out-of-scope split (OUT-OF-SCOPE.md routing).

This is Layer-1 (CONTRACTED) only. Layer-2 (DEMONSTRATED — task verdicts, load.jsonl) is
empty by honest construction: no op is `live`, no driving harness has run. Stated, never decorated.

Outputs:
  coverage/coverage.json   — the machine artifact (generated; hand-edits should fail a future diff check)
  (stdout)                 — the human-readable map + a GROUND-TRUTH COMPARISON against the
                             hand-derived COVERAGE.md headline (11 covered / 24 planned-only / 0
                             unmapped, 123/123 affordances). If the machine join DIVERGES from the
                             hand-derived numbers, that is a REAL FINDING — reported, NOT force-matched.

Usage:
  python3 tools/coverage.py [--corpus DIR] [--write-json] [--render-md]
    --write-json : write coverage/coverage.json
    --render-md  : also rewrite COVERAGE.md with the regenerated map (default: stdout only,
                   so a run is non-destructive unless explicitly asked to render)
Exit code:
  0 = generated cleanly AND matches the hand-derived ground truth
  3 = generated cleanly but DIVERGES from the hand-derived ground truth (a real finding to inspect)
  4 = one or more contract:op fences FAILED TO PARSE (parse_errors non-empty). A malformed fence is
      a HARD failure, not a warning: an op that does not parse contributes no atlas tags, so a broken
      fence that is the SOLE op tagging an affordance would silently drop that affordance from the
      'reached' count and undercount coverage. We refuse to emit a coverage verdict over an
      incompletely-parsed corpus — fix the fence (run tools/validate_contract.py for the precise
      YAML error) and re-run. Checked BEFORE the ground-truth comparison so a parse break can never
      be masked by a coincidental MATCH.
  2 = fatal (corpus not found / unparseable)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("FATAL: PyYAML required to parse contract:op fences.\n")
    sys.exit(2)

OP_FENCE_RE = re.compile(r"```contract:op\n(.*?)\n```", re.S)
BUILDING_LIKE = {"building", "live"}

# the hand-derived ground truth headline (COVERAGE.md, 2026-06-12) — what the machine join is
# compared against. NOT a target to force-match: a divergence is reported as a real finding.
GROUND_TRUTH = {
    "covered_classes": 11,
    "planned_only_classes": 24,
    "unmapped_classes": 0,
    "total_classes": 35,
    "affordances_defined": 123,
    "affordances_reached": 123,
    "affordances_building": 32,
    "affordances_planned_only": 91,
    "covered_set": {"CC-05","CC-07","CC-08","CC-09","CC-14","CC-15","CC-18","CC-23","CC-25","CC-33","CC-35"},
}


def parse_corpus(root: Path):
    res_dir = root / "resources"
    if not res_dir.is_dir():
        sys.stderr.write(f"FATAL: {res_dir} not found.\n")
        sys.exit(2)

    # ----- atlas: defined classes + affordances
    atlas = (root / "atlas" / "FEATURE-ATLAS.md").read_text()
    defined_classes = sorted(set(re.findall(r"\bCC-\d{2}\b", atlas)))
    defined_affordances = sorted(set(re.findall(r"\bCC-\d{2}\.\d+\b", atlas)))
    # class id -> human name (from the | CC-nn | name | table)
    class_names = {}
    for m in re.finditer(r"^\|\s*(CC-\d{2})\s*\|\s*([^|]+?)\s*\|", atlas, re.M):
        class_names[m.group(1)] = m.group(2).strip()

    # ----- out-of-scope affordances (affordance grain)
    oos_text = ""
    oosf = root / "atlas" / "OUT-OF-SCOPE.md"
    if oosf.exists():
        oos_text = oosf.read_text()
    out_of_scope = set(re.findall(r"\bCC-\d{2}\.\d+\b", oos_text))

    # ----- the join: every op's atlas tags + status + owning entry
    # affordance -> { statuses:set, ops:[(entry, opname, status)] }
    aff = {}
    used_affordances = set()
    n_ops = 0
    parse_errors = []
    for mf in sorted(res_dir.glob("*.md")):
        entry = mf.stem
        body = mf.read_text()
        for m in OP_FENCE_RE.finditer(body):
            try:
                f = yaml.safe_load(m.group(1))
            except yaml.YAMLError as e:
                parse_errors.append((entry, str(e).splitlines()[0]))
                continue
            if not isinstance(f, dict):
                continue
            n_ops += 1
            opname = f.get("op", "?")
            status = f.get("status", "?")
            for a in (f.get("atlas") or []):
                a = str(a)
                used_affordances.add(a)
                rec = aff.setdefault(a, {"statuses": set(), "ops": []})
                rec["statuses"].add(status)
                rec["ops"].append({"entry": entry, "op": opname, "status": status})

    return {
        "defined_classes": defined_classes,
        "class_names": class_names,
        "defined_affordances": set(defined_affordances),
        "out_of_scope": out_of_scope,
        "aff": aff,
        "used_affordances": used_affordances,
        "n_ops": n_ops,
        "parse_errors": parse_errors,
    }


def build_coverage(data):
    defined_aff = data["defined_affordances"]
    used_aff = data["used_affordances"]
    aff = data["aff"]

    # closure both directions
    defined_not_used = sorted(defined_aff - used_aff - data["out_of_scope"])  # silent gaps
    used_not_defined = sorted(used_aff - defined_aff)                          # phantom tags
    reached = defined_aff & used_aff

    # affordance status roll-up
    aff_building = sorted(a for a in reached if aff[a]["statuses"] & BUILDING_LIKE)
    aff_planned_only = sorted(a for a in reached if not (aff[a]["statuses"] & BUILDING_LIKE))

    # class roll-up
    classes = data["defined_classes"]
    covered, planned_only, unmapped = [], [], []
    class_affordances = {}  # class -> {building:[], planned:[]}
    for a in reached:
        cls = a.split(".")[0]
        bucket = class_affordances.setdefault(cls, {"building": [], "planned": []})
        if aff[a]["statuses"] & BUILDING_LIKE:
            bucket["building"].append(a)
        else:
            bucket["planned"].append(a)
    for cls in classes:
        if cls not in class_affordances:
            unmapped.append(cls)
        elif class_affordances[cls]["building"]:
            covered.append(cls)
        else:
            planned_only.append(cls)

    return {
        "defined_not_used": defined_not_used,
        "used_not_defined": used_not_defined,
        "reached": sorted(reached),
        "aff_building": aff_building,
        "aff_planned_only": aff_planned_only,
        "covered": sorted(covered),
        "planned_only": sorted(planned_only),
        "unmapped": sorted(unmapped),
        "class_affordances": class_affordances,
    }


def compare_ground_truth(cov, data):
    gt = GROUND_TRUTH
    diffs = []
    checks = [
        ("covered_classes", len(cov["covered"]), gt["covered_classes"]),
        ("planned_only_classes", len(cov["planned_only"]), gt["planned_only_classes"]),
        ("unmapped_classes", len(cov["unmapped"]), gt["unmapped_classes"]),
        ("total_classes", len(data["defined_classes"]), gt["total_classes"]),
        ("affordances_defined", len(data["defined_affordances"]), gt["affordances_defined"]),
        ("affordances_reached", len(cov["reached"]), gt["affordances_reached"]),
        ("affordances_building", len(cov["aff_building"]), gt["affordances_building"]),
        ("affordances_planned_only", len(cov["aff_planned_only"]), gt["affordances_planned_only"]),
    ]
    for name, got, expected in checks:
        if got != expected:
            diffs.append(f"{name}: machine join = {got}, hand-derived COVERAGE.md = {expected}")
    # set-level: which covered classes differ
    machine_covered = set(cov["covered"])
    if machine_covered != gt["covered_set"]:
        only_machine = sorted(machine_covered - gt["covered_set"])
        only_hand = sorted(gt["covered_set"] - machine_covered)
        if only_machine:
            diffs.append(f"COVERED set: machine has extra {only_machine} (hand-derived map missed them, or status changed)")
        if only_hand:
            diffs.append(f"COVERED set: hand-derived map claims {only_hand} but machine join finds no building op for them")
    return diffs


def make_json(cov, data):
    aff = data["aff"]
    return {
        "generated": True,
        "generator": "tools/coverage.py",
        "layer": 1,
        "note": "CONTRACTED layer only; Layer-2 DEMONSTRATED empty (no live op, no harness run).",
        "totals": {
            "classes_defined": len(data["defined_classes"]),
            "classes_covered": len(cov["covered"]),
            "classes_planned_only": len(cov["planned_only"]),
            "classes_unmapped": len(cov["unmapped"]),
            "affordances_defined": len(data["defined_affordances"]),
            "affordances_reached": len(cov["reached"]),
            "affordances_building": len(cov["aff_building"]),
            "affordances_planned_only": len(cov["aff_planned_only"]),
            "ops_parsed": data["n_ops"],
        },
        "classes": {
            "covered": cov["covered"],
            "planned_only": cov["planned_only"],
            "unmapped": cov["unmapped"],
        },
        "closure": {
            "defined_not_reached_and_not_excluded": cov["defined_not_used"],  # silent gaps
            "reached_but_not_defined": cov["used_not_defined"],               # phantom tags
        },
        "affordances": {
            a: {"statuses": sorted(aff[a]["statuses"]), "ops": aff[a]["ops"]}
            for a in cov["reached"]
        },
        "layer2_demonstrated": {
            "demonstrated_affordances": 0,
            "of_total": len(data["defined_affordances"]),
            "reason": "no op is live; the corpus-only driving harness (load.jsonl/drops.jsonl/task verdicts) has not run",
        },
    }


def print_map(cov, data, diffs):
    print("=" * 78)
    print("UI Contract COVERAGE — machine-regenerated (tools/coverage.py)")
    print("=" * 78)
    print(f"classes: {len(data['defined_classes'])} defined | "
          f"{len(cov['covered'])} COVERED | {len(cov['planned_only'])} PLANNED-ONLY | "
          f"{len(cov['unmapped'])} UNMAPPED")
    print(f"affordances: {len(data['defined_affordances'])} defined | {len(cov['reached'])} reached "
          f"({len(cov['aff_building'])} building/live, {len(cov['aff_planned_only'])} planned-only)")
    print(f"ops parsed: {data['n_ops']}")
    print()
    print("COVERED classes (>=1 affordance via a building/live op):")
    print("  " + ", ".join(cov["covered"]))
    print()
    print("PLANNED-ONLY classes (mapped, every covering op planned):")
    print("  " + ", ".join(cov["planned_only"]))
    print()
    print("UNMAPPED classes (no op, no affordance — starvation):")
    print("  " + (", ".join(cov["unmapped"]) if cov["unmapped"] else "NONE — every class opened"))
    print()
    print("Closure (both directions):")
    sg = cov["defined_not_used"]
    pt = cov["used_not_defined"]
    print(f"  silent gaps (defined, unreached, not excluded): {len(sg)} {sg if sg else ''}")
    print(f"  phantom tags (op tags an undefined affordance):  {len(pt)} {pt if pt else ''}")
    print()
    if data["parse_errors"]:
        print("PARSE ERRORS (op fences that did not parse — coverage may undercount):")
        for entry, err in data["parse_errors"]:
            print(f"  {entry}: {err}")
        print()
    print("-" * 78)
    print("GROUND-TRUTH COMPARISON vs hand-derived COVERAGE.md (2026-06-12)")
    print("-" * 78)
    if not diffs:
        print("MATCH — machine join reproduces the hand-derived map exactly:")
        print("  11 covered / 24 planned-only / 0 unmapped · 123/123 affordances · 32 building / 91 planned-only.")
        print("  The hand-derived COVERAGE.md is corroborated by the generator. No divergence.")
    else:
        print("DIVERGENCE — the machine join disagrees with the hand-derived map. This is a REAL")
        print("FINDING (NOT force-matched). Inspect which side is right:")
        for d in diffs:
            print(f"  ! {d}")
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--write-json", action="store_true")
    ap.add_argument("--render-md", action="store_true",
                    help="(reserved) rewrite COVERAGE.md from the join; default is non-destructive stdout")
    args = ap.parse_args()

    root = Path(args.corpus).resolve()
    data = parse_corpus(root)
    cov = build_coverage(data)
    diffs = compare_ground_truth(cov, data)

    print_map(cov, data, diffs)

    if args.write_json:
        out_dir = root / "coverage"
        out_dir.mkdir(exist_ok=True)
        out = out_dir / "coverage.json"
        out.write_text(json.dumps(make_json(cov, data), indent=2) + "\n")
        print(f"wrote {out.relative_to(root)}")

    if args.render_md:
        print("NOTE: --render-md is reserved; COVERAGE.md is the canonical hand-authored prose map. "
              "The generator corroborates it (above) rather than overwriting prose this pass — "
              "rendering the full markdown body is the next safe increment once the ground-truth "
              "comparison stays MATCH across a few corpus edits.")

    # HARD GATE: a malformed contract:op fence undercounts coverage silently (an unparsed op
    # contributes no atlas tags; if it is the SOLE op tagging an affordance, that affordance silently
    # drops from 'reached'). parse_errors is therefore a non-zero exit, checked BEFORE the
    # match/divergence verdict so a parse break can never be masked by a coincidental MATCH. The
    # loud PARSE ERRORS block was already printed by print_map(); here it becomes fail-loud.
    if data["parse_errors"]:
        n = len(data["parse_errors"])
        sys.stderr.write(
            f"FAIL — {n} contract:op fence(s) did not parse (see PARSE ERRORS above). Coverage is "
            f"undercounted and NO verdict is emitted: an unparsed op contributes no atlas tags, so a "
            f"broken fence that is the only op tagging an affordance would silently drop it from the "
            f"'reached' count. Fix the fence(s) — run tools/validate_contract.py for the precise YAML "
            f"error — and re-run.\n"
        )
        sys.exit(4)

    # exit code: 0 match, 3 divergence
    sys.exit(0 if not diffs else 3)


if __name__ == "__main__":
    main()
