"""check.py — the structural coherence pass (no models, free, deterministic).

Two modes (additive — the default is unchanged):

  (A) MOCKUP-SCAN (default, no args):  python3 check.py
      The cheap floor of the design-gate AND recognise-and-propose. Reports:
        • hardcoded literals in the mockups → candidate tokens (matches an existing token
          value = should use var(--x); matches none = candidate NEW token) — the hardcoded→
          tokenised finder;
        • coverage gaps (registered features no view represents);
        • orphan addresses (used-but-unregistered / registered-but-unused — via parse);
        • hygiene (mockups missing the design-system.css link or any data-ui-ref).
      Writes check-report.json + prints a summary. This is Layer-0 of the swarm: the model
      layer (semantic judgement) extends it later; everything here is exact and free.

  (B) DESIGN-LINT against the live app (additive flags):
        python3 check.py --target canvas/app/src [--fail-on] [--include-px] [--report <path>]
      Scans every .tsx/.css under <target> for HARDCODED off-token literals (hex/rgba — the
      app must use var(--x), never raw colour; +px when --include-px) AND bespoke elements,
      and with --fail-on EXITS NON-ZERO when any are found, so it can GATE a build (root
      AGENTS.md rule 9 — design-lint fails loud). Unlike the mockup-scan's recurrence finder
      (count>1, colour-only), the design-lint flags a SINGLE occurrence — a planted off-token
      literal trips it. Does not touch check-report.json (writes its own report if --report
      is given). The mockup-scan behaviour is fully intact; these are additive flags only."""
import os, re, json, collections, argparse, sys, glob
import parse

_HEX = re.compile(r'#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b')
_PX = re.compile(r'\b\d+px\b')
_RGBA = re.compile(r'rgba?\([^)]*\)')


def find_literals(text: str) -> list:
    """Hardcoded colour (hex) + size (px) literals in a blob of HTML/CSS."""
    return _HEX.findall(text) + _PX.findall(text)


def candidate_tokens(screens: dict, token_values: dict) -> list:
    """Aggregate every literal across the corpus → {literal, count, screens[],
    matches_token}. matches_token = the token name whose value equals the literal
    (→ use var); None = candidate NEW token."""
    val2name = {v: k for k, v in token_values.items()}
    counts, where = collections.Counter(), collections.defaultdict(set)
    for name, html in screens.items():
        for lit in find_literals(html):
            counts[lit] += 1
            where[lit].add(name)
    out = []
    for lit, n in counts.items():
        out.append({
            "literal": lit,
            "count": n,
            "screens": sorted(where[lit]),
            "matches_token": val2name.get(lit),
            "kind": "colour" if lit.startswith("#") else "size",
        })
    return sorted(out, key=lambda c: (-c["count"], c["literal"]))


def _resolved_token_values(tokens: dict) -> dict:
    """tokens.json → {token-name: final value} (refs resolved to their primitive)."""
    prims = tokens.get("primitives", {})
    vals = {}
    for g in tokens.get("groups", []):
        for name, spec in g.get("tokens", {}).items():
            vals[name] = prims[spec["ref"]] if "ref" in spec else spec.get("v")
    return vals


# ── DESIGN-LINT (mode B) — additive: gate the live app against the corpus ──────────
# Off-token = a hardcoded colour/size literal in app SOURCE where the app must use a
# token (var(--x)) or a design-system component class. The corpus token VALUES are the
# palette; ANY raw hex/rgba in source is off-token (even one whose value happens to equal
# a token — it should be var(--x), not the literal). This flags a SINGLE occurrence (the
# mockup-scan's count>1 recurrence finder does not), so a planted #abc123 trips it.

def _iter_source_files(target: str):
    """Every .tsx / .css under <target> (a dir, a glob, or a single file)."""
    if os.path.isdir(target):
        for root, _dirs, files in os.walk(target):
            for fn in sorted(files):
                if fn.endswith((".tsx", ".css")):
                    yield os.path.join(root, fn)
    elif any(ch in target for ch in "*?["):
        for p in sorted(glob.glob(target, recursive=True)):
            if p.endswith((".tsx", ".css")) and os.path.isfile(p):
                yield p
    elif os.path.isfile(target):
        yield target
    # else: no match → caller fails loud (empty file set on a given target is suspicious)


# bespoke-element detection is a documented STUB for C0: it becomes meaningful only once
# the app carries data-ui-ref (F4) + the corpus component inventory is reconciled against
# the app (design-substrate §5). It is wired so --fail-on counts it, but returns [] today —
# it must NOT inject spurious failures into the C0 proof. Graduates with F4/F1.
def _find_bespoke_elements(text: str, path: str) -> list:
    return []  # STUB (C0): not live until F4/F1 — see docstring + Implementation Guide C0.


def design_lint(target: str, include_px: bool = False) -> dict:
    """Scan app source for hardcoded off-token literals + bespoke elements. Returns
    {files_scanned, off_token_literals:[{file,line,literal,kind}], bespoke_elements:[...],
     summary:{...}}. Flags single occurrences (gate semantics, not recurrence)."""
    files = list(_iter_source_files(target))
    off_token, bespoke = [], []
    for path in files:
        try:
            text = open(path, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError) as e:
            # fail loud — never silently skip a file (rule 4)
            raise SystemExit(f"check.py --target: cannot read {path}: {e}")
        for ln, line in enumerate(text.splitlines(), 1):
            for m in _HEX.finditer(line):
                off_token.append({"file": path, "line": ln, "literal": m.group(0), "kind": "colour"})
            for m in _RGBA.finditer(line):
                off_token.append({"file": path, "line": ln, "literal": m.group(0), "kind": "colour"})
            if include_px:
                for m in _PX.finditer(line):
                    off_token.append({"file": path, "line": ln, "literal": m.group(0), "kind": "size"})
        bespoke += _find_bespoke_elements(text, path)
    return {
        "target": target,
        "include_px": include_px,
        "files_scanned": len(files),
        "off_token_literals": off_token,
        "bespoke_elements": bespoke,
        "summary": {
            "files_scanned": len(files),
            "off_token_literals": len(off_token),
            "bespoke_elements": len(bespoke),
        },
    }


def run_design_lint(target: str, fail_on: bool, include_px: bool, report_path: str | None) -> int:
    """Run the design-lint, print a summary, optionally write a report, return an exit code.
    With fail_on: exit code != 0 iff any off-token literal or bespoke element is found."""
    result = design_lint(target, include_px=include_px)
    files = list(_iter_source_files(target))
    if not files:
        # a target that matches no .tsx/.css is almost certainly a wrong path — fail loud.
        print(f"design-lint: NO .tsx/.css files under target '{target}' — refusing to "
              f"silently pass (rule 4).", file=sys.stderr)
        return 2
    s = result["summary"]
    print(f"design-lint (off-token + bespoke gate) — target: {target}")
    for k, v in s.items():
        print(f"  {k}: {v}")
    if result["off_token_literals"]:
        shown = result["off_token_literals"][:12]
        print("  → off-token literals (file:line literal):")
        for it in shown:
            print(f"      {os.path.relpath(it['file'])}:{it['line']}  {it['literal']} ({it['kind']})")
        if len(result["off_token_literals"]) > len(shown):
            print(f"      … +{len(result['off_token_literals']) - len(shown)} more")
    if result["bespoke_elements"]:
        print(f"  → bespoke elements: {len(result['bespoke_elements'])}")
    if report_path:
        json.dump(result, open(report_path, "w", encoding="utf-8"), indent=2)
        print(f"  wrote {report_path}")
    found = s["off_token_literals"] + s["bespoke_elements"]
    if fail_on and found:
        print(f"design-lint FAIL: {found} off-token/bespoke finding(s) — build gated (rule 9).",
              file=sys.stderr)
        return 1
    return 0


def mockup_scan():
    here = os.path.dirname(os.path.abspath(__file__))
    design = os.path.dirname(here)
    L = lambda *p: os.path.join(design, *p)
    tokens = json.load(open(os.path.join(here, "tokens.json"), encoding="utf-8"))
    addresses = json.load(open(os.path.join(here, "addresses.json"), encoding="utf-8")).get("addresses", {})
    register = json.load(open(L("register.json"), encoding="utf-8"))
    token_values = _resolved_token_values(tokens)

    mockdir = L("mockups")
    screens = {fn: open(os.path.join(mockdir, fn), encoding="utf-8").read()
               for fn in sorted(os.listdir(mockdir)) if fn.endswith(".html")}

    cands = candidate_tokens(screens, token_values)
    # only flag literals that recur (>1) OR clearly belong to a token — single one-off
    # inline positions (left:452px) aren't worth tokenising; recurrence is the signal.
    should_use_var = [c for c in cands if c["matches_token"]]
    new_colour = [c for c in cands if not c["matches_token"] and c["kind"] == "colour" and c["count"] > 1]

    represented = set()
    for v in register.get("views", []):
        represented.update(v.get("represents", []))
    coverage_gaps = sorted(f["id"] for f in register.get("features", []) if f["id"] not in represented)

    orphans = parse.build_map(screens, addresses)["orphans"]

    missing_link = [fn for fn, h in screens.items() if "design-system.css" not in h]
    missing_addr = [fn for fn, h in screens.items() if "data-ui-ref" not in h]

    report = {
        "should_use_var": should_use_var,
        "candidate_new_colour_tokens": new_colour,
        "coverage_gaps": coverage_gaps,
        "address_orphans": orphans,
        "hygiene": {"missing_css_link": missing_link, "missing_any_data_ui_ref": missing_addr},
        "summary": {
            "screens": len(screens),
            "literals_should_use_var": len(should_use_var),
            "candidate_new_colour_tokens": len(new_colour),
            "coverage_gaps": len(coverage_gaps),
            "address_orphans_unregistered": len(orphans["unregistered"]),
            "address_orphans_unused": len(orphans["unused"]),
            "mockups_missing_css": len(missing_link),
            "mockups_missing_address": len(missing_addr),
        },
    }
    json.dump(report, open(os.path.join(here, "check-report.json"), "w", encoding="utf-8"), indent=2)
    s = report["summary"]
    print("check (structural coherence) — summary:")
    for k, v in s.items():
        print(f"  {k}: {v}")
    if should_use_var:
        print("  → literals that equal an existing token (use var):",
              ", ".join(f"{c['literal']}×{c['count']}→--{c['matches_token']}" for c in should_use_var[:8]))
    if new_colour:
        print("  → candidate NEW colour tokens (recurring, no token yet):",
              ", ".join(f"{c['literal']}×{c['count']}" for c in new_colour[:8]))


def main():
    """Dispatch: no --target → mockup-scan (mode A, unchanged). --target → design-lint (mode B)."""
    ap = argparse.ArgumentParser(description="Design coherence check (mockup-scan) + design-lint gate.")
    ap.add_argument("--target", help="dir / glob / file of app source (.tsx/.css) to design-lint "
                                     "against the corpus tokens. Omit for the default mockup-scan.")
    ap.add_argument("--fail-on", action="store_true", help="exit NON-ZERO when an off-token literal "
                                                           "or bespoke element is found (gate a build).")
    ap.add_argument("--include-px", action="store_true", help="also flag hardcoded px sizes "
                                                              "(default: hex/rgba colour only).")
    ap.add_argument("--report", help="write the design-lint result JSON to this path.")
    args = ap.parse_args()
    if args.target is None:
        mockup_scan()  # mode A — default behaviour intact
        return 0
    return run_design_lint(args.target, args.fail_on, args.include_px, args.report)  # mode B


if __name__ == "__main__":
    sys.exit(main() or 0)
