#!/usr/bin/env python3
"""ops/ledger_capabilities.py — persist platform CAPABILITIES into the LEDGER as addressed nodes.

The convergence (Tim 2026-06-28, option C): a source's capabilities become first-class nodes in the SAME
addressed graph as code — `cap://<platform>[@version]/<kind>/<name>` entries + typed edges
(capability→platform, capability→axis) — so "what can codex do" is a graph query, version-aware, and
deep-linkable to the code that uses it. GENERAL FOR ANY SOURCE: it iterates the PlatformRegistry and
discovers each platform via the unchanged introspection engine — drop a platforms/<id>.py row and its
capabilities flow into the ledger here, no edit. Per-platform fail-isolation (a binary that won't probe
is recorded as an error node-run note, never blocks the others).

Reuses the ledger's run/entry/edge schema (no migration — a capability is node_type='capability'). One
run per invocation, scoped project='platforms', purpose='capability-registry'.

Run:  python3 ops/ledger_capabilities.py            # discover all platforms, load capability nodes
      python3 ops/ledger_capabilities.py --only codex-cli,gh-cli
"""
from __future__ import annotations
import argparse, json, os, sys, uuid, tempfile, csv, subprocess
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
from ops.ledger_build import _psql, _pgenv, _psql_base, _git_sha, _j, _write_csv, PGCONF, SCHEMA_VERSION  # reuse
from contracts.address import cap_address
from contracts.capability_entry import is_known_kind

SESSION = os.environ.get("COMPANY_SESSION_ID", "session://consolidation-lead")


def discover_platform_caps(platform):
    """Engine DISCOVER+CLASSIFY for one platform → list[CapabilityEntry]. Raises if the binary won't
    probe (caller isolates)."""
    from introspection import discover as D, engine as E
    rows = D.discover(platform)
    return E.classify_entries(rows, platform)


def _prior_caps(pid: str) -> list:
    """The platform's capability nodes from the PRIOR latest run — for CARRY-FORWARD when a flaky binary
    fails to discover this run (so claude's 390 are never erased by a 20s init-session timeout). Returns
    [{path, node_type, kind, what_it_does, extra}]. Empty ONLY when there is no prior run; a ledger
    read failure RAISES loud (never silent-empty on a down DB — that would erase caps via carry-forward)."""
    out = []
    try:
        # the MOST RECENT run that actually HAS this platform's caps (NOT latest_run — a prior failed/partial
        # run may have clobbered latest; we want the last run where this platform was really discovered).
        rid = _psql(
            "select e.run_id from ledger.entry e join ledger.run r using(run_id) "
            f"where r.project='platforms' and e.node_type='capability' and e.path like 'cap://{pid}/%' "
            "order by r.started_at desc limit 1").strip().split("\n")[0]
        if not rid:
            return out
        rows = _psql(
            "select e.path||chr(9)||e.kind||chr(9)||coalesce(e.what_it_does,'')||chr(9)||coalesce(e.extra::text,'{}') "
            f"from ledger.entry e where e.run_id='{rid}' and e.node_type='capability' and e.path like 'cap://{pid}/%'").splitlines()
        for line in rows:
            parts = line.split(chr(9))
            if len(parts) >= 4:
                try:
                    extra = json.loads(parts[3])
                except Exception:
                    extra = {}
                out.append({"path": parts[0], "node_type": "capability", "kind": parts[1],
                            "what_it_does": parts[2], "extra": extra})
    except Exception as e:
        # LOUD FAIL (Tim 2026-06-30): a DB-unreachable / read error must NOT masquerade as "this platform
        # has no prior caps" — that silent empty makes carry-forward erase a platform's real capabilities.
        # _psql raises RuntimeError on a failed query; surface it. (A genuine no-prior-run returns [] above.)
        raise RuntimeError(f"_prior_caps({pid!r}): ledger read failed — refusing to return empty caps "
                           f"(carry-forward would silently erase prior capabilities): {e}") from e
    return out


def build_rows(only=None):
    from introspection.platforms import PlatformRegistry
    preg = PlatformRegistry().discover([os.path.join(REPO, "platforms")])
    entries, edges, notes = [], [], {}
    for pid in sorted(preg.ids()):
        if only and pid not in only:
            continue
        p = preg[pid]
        # the platform itself is a node (cap://<platform>) — parent of its capabilities
        paddr = f"cap://{pid}"
        entries.append({"path": paddr, "node_type": "platform", "kind": "platform",
                        "what_it_does": getattr(p, "display_name", pid),
                        "extra": {"display_name": getattr(p, "display_name", ""),
                                  "invocation_kind": getattr(p, "invocation_kind", "")}})
        try:
            caps = discover_platform_caps(p)
        except Exception as e:  # noqa: BLE001 — one platform's probe failure must not block the rest
            # CARRY-FORWARD: a flaky/slow binary (e.g. claude's init-session timeout) must NOT erase its
            # known capabilities. Re-emit the prior run's nodes + their capability-of edges. Fail-loud-legible.
            carried = _prior_caps(pid)
            for cnode in carried:
                entries.append(cnode)
                edges.append({"from": cnode["path"], "kind": "capability-of", "to": paddr})
            notes[pid] = (f"discovery FAILED ({type(e).__name__}: {str(e)[:90]}) — carried forward "
                          f"{len(carried)} prior capabilities (not erased)")
            continue
        ver = None
        for c in caps:
            addr = cap_address(pid, c.kind, c.name)  # cap://<platform>/<kind>/<name>
            entries.append({
                "path": addr, "node_type": "capability", "kind": c.kind,
                "what_it_does": (c.description or "")[:400],
                "extra": {"platform": pid, "name": c.name, "posture": c.posture,
                          "posture_rule": c.posture_rule, "axis": c.axis, "takes_value": c.takes_value,
                          "value_type": c.value_type, "known_kind": is_known_kind(c.kind),
                          "aliases": c.aliases}})
            # edge: capability → its platform
            edges.append({"from": addr, "kind": "capability-of", "to": paddr})
            # edge: consent capability → its axis (cap://<platform>/axis/<axis>)
            if c.posture == "consent" and c.axis:
                edges.append({"from": addr, "kind": "on-axis", "to": f"cap://{pid}/axis/{c.axis}"})
        notes[pid] = f"{sum(1 for c in caps)} capabilities"
    return entries, edges, notes


def load(entries, edges, notes):
    run_id = str(uuid.uuid4())
    tmp = tempfile.mkdtemp(prefix="ledger-caps-")
    ep, gp = os.path.join(tmp, "e.csv"), os.path.join(tmp, "g.csv")
    ecols = ["run_id", "project", "path", "node_type", "parent", "depth", "ext", "language",
             "address", "coverage_state", "kind", "what_it_does", "extra", "extractor",
             "extractor_version", "produced_by_session", "pass"]
    erows = []
    for e in entries:
        erows.append([run_id, "platforms", e["path"], e["node_type"], "", 0, "", "",
                      e["path"], "deterministic", e.get("kind", ""), e.get("what_it_does", ""),
                      _j(e.get("extra", {})), "introspection", "cap-v1", SESSION, "capability-v1"])
    _write_csv(ep, erows)
    gcols = ["run_id", "from_ref", "kind", "to_raw", "to_resolved", "produced_by_session", "pass"]
    grows = [[run_id, g["from"], g["kind"], g["to"], g["to"], SESSION, "capability-v1"] for g in edges]
    _write_csv(gp, grows)
    stats = {"entries": len(entries), "edges": len(edges), "platforms": notes, "schema_version": SCHEMA_VERSION}
    script = (
        "BEGIN;\n"
        "INSERT INTO ledger.run (run_id, project, channel, purpose, layer, session_id, tool_git_sha, "
        "tool_version, schema_version, status, stats, started_at) VALUES "
        f"('{run_id}', 'platforms', 'channel://ch-9', 'capability-registry', 'introspection', "
        f"$q${SESSION}$q$, $q${_git_sha()}$q$, 'ledger_capabilities@v1', {SCHEMA_VERSION}, 'running', "
        f"$q${_j(stats)}$q$::jsonb, now());\n"
        f"\\copy ledger.entry ({','.join(ecols)}) FROM '{ep}' WITH (FORMAT csv)\n"
        f"\\copy ledger.edge ({','.join(gcols)}) FROM '{gp}' WITH (FORMAT csv)\n"
        f"UPDATE ledger.run SET status='complete', ended_at=now() WHERE run_id='{run_id}';\n"
        "COMMIT;\n")
    sf = os.path.join(tmp, "load.sql")
    open(sf, "w").write(script)
    r = subprocess.run(_psql_base() + ["-f", sf], capture_output=True, text=True, env=_pgenv())
    if r.returncode != 0:
        raise RuntimeError(f"capability load FAILED (rolled back): {r.stderr.strip()[:300]}")
    return run_id


import re
# how each platform's binary is invoked in code — a file is a CONSUMER of platform P only if it both
# matches this invocation pattern AND contains an exact flag token of P (high precision, no stray matches).
_INVOKE = {"codex-cli": re.compile(r"\bcodex\b"), "gh-cli": re.compile(r"\bgh\b"),
           "claude-code": re.compile(r"\bclaude\b")}
_ROOTS = {"company": REPO, "counterpart-design": "/home/tim/repos/counterpart/design",
          "claude-ds": os.path.join(REPO, "design", "claude-ds")}


def deep_link() -> dict:
    """STEP 7 — auto consumer→capability edges (the deep-link). ⚠ EXPERIMENTAL — string-match precision is
    INSUFFICIENT and produces FICTION (proven 2026-06-28: `contracts/address.py` matched codex flags it
    only MENTIONS in docstrings; short tokens like `-b` over-match). The string-level rule cannot tell
    "mentions a flag in a comment" from "invokes the binary with that flag", so its output was pulled from
    the ledger. The CORRECT version is invocation-CONTEXT matching: AST-parse each file for subprocess/exec
    calls where argv[0] IS the platform binary, and link only the flags inside THAT call. Until that lands,
    do NOT persist these edges (this function is kept as the concept + the negative result; --link is gated).
    For each code file that INVOKES a platform's binary, it links exact-token flags → `uses-capability`."""
    # the flag capabilities currently in the ledger, grouped by platform
    rows = _psql("select e.path from ledger.entry e join ledger.latest_run r using(run_id) "
                 "where r.project='platforms' and e.node_type='capability' and e.kind='flag'").splitlines()
    flags = {}
    for capaddr in [x for x in rows if x]:
        from contracts.address import parse_cap_address
        p = parse_cap_address(capaddr)
        flags.setdefault(p["platform"], []).append((p["name"], capaddr))
    # candidate consumer files: code entries in the source projects
    code = _psql("select r.project||chr(9)||e.path from ledger.entry e join ledger.latest_run r using(run_id) "
                 "where e.node_type='file' and e.ext in ('.py','.sh','.ts','.tsx','.js','.mjs')").splitlines()
    edges = []
    for line in code:
        if chr(9) not in line: continue
        proj, path = line.split(chr(9), 1)
        if proj not in _ROOTS: continue
        try:
            src = open(os.path.join(_ROOTS[proj], path), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for pid, fl in flags.items():
            if pid not in _INVOKE or not _INVOKE[pid].search(src):
                continue  # file does not invoke this platform's binary → not a consumer
            for name, capaddr in fl:
                # exact word-bounded flag token (so '--model' matches but not '--modeling')
                if re.search(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", src):
                    edges.append((f"code://{proj}/{path}", "uses-capability", capaddr))
    # write the edges (idempotent: replace prior uses-capability on the platforms run)
    if edges:
        import tempfile, subprocess
        rid = _psql("select run_id from ledger.latest_run where project='platforms' and purpose='capability-registry'").strip().split("\n")[0]
        td = tempfile.mkdtemp(prefix="caplink-")
        gp = os.path.join(td, "g.csv"); _write_csv(gp, [[rid, f, k, t, t, SESSION, "deep-link-v1"] for f, k, t in edges])
        script = ("BEGIN;\n"
                  f"DELETE FROM ledger.edge WHERE run_id='{rid}' AND kind='uses-capability';\n"
                  f"\\copy ledger.edge (run_id,from_ref,kind,to_raw,to_resolved,produced_by_session,pass) FROM '{gp}' WITH (FORMAT csv)\n"
                  "COMMIT;\n")
        sf = os.path.join(td, "l.sql"); open(sf, "w").write(script)
        r = subprocess.run(_psql_base() + ["-f", sf], capture_output=True, text=True, env=_pgenv())
        if r.returncode != 0:
            raise RuntimeError(f"deep-link load failed: {r.stderr.strip()[:200]}")
    return {"uses_capability_edges": len(edges), "sample": edges[:6]}


def load_into_registry(reg) -> int:
    """Populate a CapabilityRegistry FROM THE LEDGER (the spawn-free, all-platforms path — the operational
    fix for the live cap:// timeout: claude's binary discovery times out, but the ledger nodes are already
    discovered + persisted). Reconstructs CapabilityEntry rows from the `platforms`-project capability nodes
    and inserts them keyed by their nested id, so cap://<platform>/<kind>/<name> resolves with NO subprocess.
    Returns the count loaded. registry-is-truth: if the ledger has no capability nodes, loads nothing (the
    caller can still fall back to live discovery) — never fabricates."""
    from contracts.capability_entry import CapabilityEntry
    from contracts.address import parse_cap_address
    rows = _psql(
        "select e.path||chr(9)||e.kind||chr(9)||coalesce(e.what_it_does,'')||chr(9)||coalesce(e.extra::text,'{}') "
        "from ledger.entry e join ledger.latest_run r using(run_id) "
        "where r.project='platforms' and e.node_type='capability'").splitlines()
    n = 0
    for line in rows:
        parts = line.split(chr(9))
        if len(parts) < 4:
            continue
        path, kind, desc, extra_json = parts[0], parts[1], parts[2], parts[3]
        try:
            extra = json.loads(extra_json)
            p = parse_cap_address(path)
        except Exception:
            continue
        e = CapabilityEntry(
            id=f"{kind}/{p['name']}", kind=kind, name=p["name"], description=desc,
            platform_id=extra.get("platform", p["platform"]),
            posture=extra.get("posture", "unmatched") or "unmatched",
            posture_rule=extra.get("posture_rule", ""), axis=extra.get("axis", ""),
            takes_value=bool(extra.get("takes_value", False)), value_type=extra.get("value_type", ""),
            aliases=extra.get("aliases", []) or [], source="ledger")
        reg.entries[p["full_id"]] = e
        reg.platforms.add(p["platform"])
        n += 1
    return n


import ast as _ast


def _py_invocations(src: str, bin_to_pid: dict) -> list:
    """AST-precise: find flags used in actual subprocess/exec CALLS where argv[0] is a platform binary.
    Returns [(platform_id, flag_name)]. Platform from argv[0]: a string literal containing the binary
    name, OR a Name whose identifier resolves to a binary (assigned from a literal containing it, or named
    like it e.g. CODEX→codex). Only flag LITERALS inside the call count — so a flag MENTIONED in a docstring
    or comment is NEVER matched (that was the string-match's fiction)."""
    try:
        tree = _ast.parse(src)
    except (SyntaxError, ValueError):
        return []
    var_pid = {}
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Assign):
            try:
                rhs = _ast.unparse(node.value)
            except Exception:
                rhs = ""
            for binname, pid in bin_to_pid.items():
                if binname in rhs.lower():
                    for t in node.targets:
                        if isinstance(t, _ast.Name):
                            var_pid[t.id] = pid
    out = []
    for node in _ast.walk(tree):
        if not isinstance(node, _ast.Call):
            continue
        try:
            fn = _ast.unparse(node.func)
        except Exception:
            continue
        if not ("subprocess" in fn or fn.endswith(".run") or fn.endswith(".Popen")
                or fn.endswith(".check_output") or fn.endswith(".call") or "run_capture" in fn):
            continue
        if not node.args or not isinstance(node.args[0], (_ast.List, _ast.Tuple)):
            continue
        elts = node.args[0].elts
        if not elts:
            continue
        first, pid = elts[0], None
        if isinstance(first, _ast.Constant) and isinstance(first.value, str):
            for binname, p in bin_to_pid.items():
                if binname in first.value.lower():
                    pid = p
        elif isinstance(first, _ast.Name):
            pid = var_pid.get(first.id)
            if not pid:
                for binname, p in bin_to_pid.items():       # var NAMED like the binary (CODEX→codex)
                    if binname in first.id.lower():
                        pid = p
        if not pid:
            continue
        seen_sub = False
        for e in elts[1:]:
            if not (isinstance(e, _ast.Constant) and isinstance(e.value, str)):
                continue
            v = e.value
            if v.startswith("-"):
                out.append((pid, "flag", v.split("=", 1)[0]))
            elif not seen_sub and v and v.replace("-", "").isalnum():
                # the first bare token after the binary is the SUBCOMMAND (gh 'pr', codex 'exec')
                out.append((pid, "subcommand", v)); seen_sub = True
    return out


def deep_link_ast() -> dict:
    """STEP 7 (precise) — true consumer→capability edges via AST invocation-context (replaces the pulled
    string-match). For each PYTHON file in the ledger, find subprocess/exec calls whose argv[0] is a
    platform binary, and link the flag literals in that call to cap://<platform>/flag/<flag>. No fiction:
    a flag in a comment/docstring is never matched (only call arguments). Idempotent."""
    # binary-name → platform id (from the registry's executable_locator)
    from introspection.platforms import PlatformRegistry
    preg = PlatformRegistry().discover([os.path.join(REPO, "platforms")])
    bin_to_pid = {}
    for pid in preg.ids():
        loc = getattr(preg[pid], "executable_locator", None)
        nm = getattr(loc, "name", "") if loc else ""
        if nm:
            bin_to_pid[nm.lower()] = pid
    # known flag capabilities per platform (to only link real caps)
    capset = set(x for x in _psql(
        "select e.path from ledger.entry e join ledger.latest_run r using(run_id) "
        "where r.project='platforms' and e.node_type='capability' and e.kind in ('flag','subcommand')").splitlines() if x)
    # scan the LIVE filesystem (current state — finds files created since the last ledger run, e.g. the
    # producers themselves), not the ledger's possibly-stale code list. Link to cap nodes (which ARE in the ledger).
    from ops.code_archaeology import enumerate_files
    code = []
    for proj, root in _ROOTS.items():
        try:
            fs, _ = enumerate_files(root)
        except Exception:
            continue
        for f in fs:
            if f["rel_path"].endswith(".py"):
                code.append((proj, f["rel_path"], f["abs_path"]))
    edges, seen = [], set()
    for proj, path, abs_path in code:
        try:
            src = open(abs_path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for pid, ckind, name in _py_invocations(src, bin_to_pid):
            capaddr = cap_address(pid, ckind, name)
            if capaddr in capset:
                key = (f"code://{proj}/{path}", capaddr)
                if key not in seen:
                    seen.add(key)
                    edges.append((f"code://{proj}/{path}", "uses-capability", capaddr))
    if edges:
        import tempfile, subprocess
        rid = _psql("select run_id from ledger.latest_run where project='platforms' and purpose='capability-registry'").strip().split("\n")[0]
        td = tempfile.mkdtemp(prefix="caplink-")
        gp = os.path.join(td, "g.csv"); _write_csv(gp, [[rid, f, k, t, t, SESSION, "deep-link-ast-v1"] for f, k, t in edges])
        script = ("BEGIN;\n"
                  f"DELETE FROM ledger.edge WHERE run_id='{rid}' AND kind='uses-capability';\n"
                  f"\\copy ledger.edge (run_id,from_ref,kind,to_raw,to_resolved,produced_by_session,pass) FROM '{gp}' WITH (FORMAT csv)\n"
                  "COMMIT;\n")
        sf = os.path.join(td, "l.sql"); open(sf, "w").write(script)
        r = subprocess.run(_psql_base() + ["-f", sf], capture_output=True, text=True, env=_pgenv())
        if r.returncode != 0:
            raise RuntimeError(f"deep-link-ast load failed: {r.stderr.strip()[:200]}")
    return {"uses_capability_edges": len(edges), "sample": edges[:10]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="comma-sep platform ids to limit to")
    ap.add_argument("--link", action="store_true", help="STEP 7: build consumer→capability deep-link edges (AST-precise)")
    a = ap.parse_args()
    if a.link:
        print(json.dumps(deep_link_ast(), indent=2)); return 0
    only = set(x.strip() for x in a.only.split(",") if x.strip()) or None
    entries, edges, notes = build_rows(only)
    run_id = load(entries, edges, notes)
    print(json.dumps({"run": run_id, "entries": len(entries), "edges": len(edges), "per_platform": notes}, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
