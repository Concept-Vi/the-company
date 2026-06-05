#!/usr/bin/env python3
"""tests/blueprint_acceptance.py — B1: the importable blueprint is COMPLETE + CONSISTENT.

The B1 proof bar (per the BACKEND-lane task): NOT a full FE rebuild — COMPLETENESS + CONSISTENCY:
  - every component-inventory entry that is `built` maps to a REAL file under canvas/app/src
  - every surface-spec address is REGISTERED in addresses.json (never invented)
  - the blueprint carries its required parts: tokens.json, CONNECTION-CONTRACT.md, the builder README,
    component-inventory.json, the surfaces/ tree, the lint-rule reference, an annotated example
  - the surface-specs cover every register.json view (no view left without a spec)
  - the blueprint is regenerable + idempotent (re-running blueprint_emit.py is a no-op on content)

Run:  /home/tim/company/.venv/bin/python tests/blueprint_acceptance.py   (cwd = repo root)
Self-contained: no bridge, no network. Fails loud with the offending item.
"""
import os, sys, json, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # repo root (worktree)
DESIGN = os.path.join(ROOT, "design")
SYS = os.path.join(DESIGN, "_system")
BLUEPRINT = os.path.join(DESIGN, "blueprint")
SURFACES = os.path.join(BLUEPRINT, "surfaces")

PASS = 0
FAILS = []


def check(label, cond, detail=""):
    global PASS
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAILS.append((label, detail))
        print(f"  XX  {label}" + (f"  — {detail}" if detail else ""))


def load_json(p):
    with open(p) as f:
        return json.load(f)


def main():
    # --- ensure the blueprint is freshly generated (regenerable) ---
    r = subprocess.run([sys.executable, os.path.join(SYS, "blueprint_emit.py")],
                       capture_output=True, text=True)
    check("blueprint_emit.py runs clean (exit 0)", r.returncode == 0, r.stderr.strip()[-300:])

    # --- required parts present ---
    required = {
        "tokens.json":            os.path.join(SYS, "tokens.json"),
        "design-system.css":      os.path.join(DESIGN, "design-system.css"),
        "addresses.json":         os.path.join(SYS, "addresses.json"),
        "check.py (lint rules)":  os.path.join(SYS, "check.py"),
        "CONNECTION-CONTRACT.md": os.path.join(DESIGN, "CONNECTION-CONTRACT.md"),
        "blueprint/README.md":    os.path.join(BLUEPRINT, "README.md"),
        "component-inventory.json": os.path.join(BLUEPRINT, "component-inventory.json"),
        "surfaces/ tree":         SURFACES,
    }
    for name, path in required.items():
        check(f"blueprint part present: {name}", os.path.exists(path), path)

    # an annotated example exists (the build-to-schema walkthrough)
    ex_dir = os.path.join(BLUEPRINT, "examples")
    examples = [f for f in (os.listdir(ex_dir) if os.path.isdir(ex_dir) else []) if f.endswith(".md")]
    check("at least one annotated example present", len(examples) >= 1, str(examples))

    # --- the README references the lint gate (the builder's FORM gate) ---
    readme = open(os.path.join(BLUEPRINT, "README.md")).read()
    check("README references the design-lint FORM gate (check.py --fail-on)",
          "check.py" in readme and "--fail-on" in readme)
    check("README forbids inventing addresses (path-of-least-resistance law)",
          "invent" in readme.lower() and "address" in readme.lower())

    # --- CONSISTENCY 1: every BUILT inventory entry maps to a real file ---
    inv = load_json(os.path.join(BLUEPRINT, "component-inventory.json"))
    for row in inv["regions"]:
        if row["status"] == "built":
            comp = row["component"]
            ok = comp is not None and os.path.exists(os.path.join(ROOT, comp))
            check(f"inventory region '{row['region']}' (built) → real file", ok, comp)
        else:
            # planned rows must NOT claim a component path (honesty)
            check(f"inventory region '{row['region']}' (planned) has no component path",
                  row.get("component") is None)
    for row in inv["shared_components"]:
        if row["status"] == "built":
            ok = os.path.exists(os.path.join(ROOT, row["component"]))
            check(f"inventory shared '{row['name']}' (built) → real file", ok, row["component"])

    # --- CONSISTENCY 2: every surface-spec address is registered ---
    registered = set(load_json(os.path.join(SYS, "addresses.json"))["addresses"].keys())
    reg = load_json(os.path.join(DESIGN, "register.json"))
    view_ids = {v["id"] for v in reg["views"]}

    spec_view_ids = set()
    unregistered = []
    for home in os.listdir(SURFACES):
        hdir = os.path.join(SURFACES, home)
        if not os.path.isdir(hdir):
            continue
        for fn in os.listdir(hdir):
            if not fn.endswith(".json"):
                continue
            spec = load_json(os.path.join(hdir, fn))
            spec_view_ids.add(spec["id"])
            for a in spec.get("addresses", []):
                if a not in registered:
                    unregistered.append(f"{spec['id']}:{a}")
    check("every surface-spec address is REGISTERED in addresses.json (none invented)",
          not unregistered, f"unregistered: {unregistered}")

    # --- COMPLETENESS: every register.json view has a surface-spec ---
    missing = view_ids - spec_view_ids
    extra = spec_view_ids - view_ids
    check("every register.json view has a surface-spec", not missing, f"missing: {sorted(missing)}")
    check("no surface-spec for a non-existent view", not extra, f"extra: {sorted(extra)}")

    # --- CONSISTENCY 3: every inventory address is a real address; every region used by addresses is mapped
    inv_addrs = {a for row in inv["regions"] for a in row["addresses"]}
    check("inventory covers exactly the registered addresses",
          inv_addrs == registered, f"diff: {inv_addrs ^ registered}")

    # --- CONSISTENCY 4: each spec's home_journey matches its directory placement ---
    home_mismatch = []
    for home in os.listdir(SURFACES):
        hdir = os.path.join(SURFACES, home)
        if not os.path.isdir(hdir):
            continue
        for fn in os.listdir(hdir):
            if not fn.endswith(".json"):
                continue
            spec = load_json(os.path.join(hdir, fn))
            if spec.get("home_journey") != home:
                home_mismatch.append(f"{spec['id']}: dir={home} spec.home={spec.get('home_journey')}")
    check("each surface-spec's home_journey == its directory (tree=structure)",
          not home_mismatch, str(home_mismatch))

    # --- idempotent: re-emit produces identical content ---
    before = _snapshot()
    subprocess.run([sys.executable, os.path.join(SYS, "blueprint_emit.py")], capture_output=True)
    after = _snapshot()
    check("blueprint_emit.py is idempotent (re-run = identical content)", before == after,
          "content changed on re-run")

    print(f"\n{'ALL ' + str(PASS) + ' CHECKS PASS' if not FAILS else str(len(FAILS)) + ' CHECK(S) FAILED'}"
          " — B1 blueprint completeness + consistency")
    if FAILS:
        raise SystemExit(1)


def _snapshot():
    """Hash every blueprint file's content for idempotency comparison."""
    import hashlib
    h = {}
    for base in (BLUEPRINT,):
        for dirpath, _, files in os.walk(base):
            for fn in files:
                p = os.path.join(dirpath, fn)
                h[os.path.relpath(p, BLUEPRINT)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return h


if __name__ == "__main__":
    main()
