"""runtime/scope.py — THE SHARED ui://→code:// RESOLVER (② of NORTH-STAR; one function → two faces).

The pointing mechanism's core: given a ui:// address, answer {what symbols power it, what files that means},
LEDGER-BACKED (the join is DERIVED inside every deterministic ledger build — ledger_build.py PASS C — never
a curated registry). This module is the ONE implementation both faces call:
  · UI face   — Suite.resolve_scope delegates here (bridge routes /api/scope, /api/address-help, intents…)
  · AGENT face — the MCP `scope` surface (the face that never existed before ②)

CONTRACT (pinned by ~17 acceptance tests; consumers in UI-CODE-JOIN-ACCOUNTING.md):
  resolve_scope(ui_addr) -> {address, symbols:[sorted], scope:[sorted repo-relative files], stale, note}
  · malformed ui:// → raises (S0 grammar gate, contracts/ui_info.parse_ui_address)
  · well-formed but UNJOINED → empty symbols+scope, stale=False, legible note — NEVER raises, NEVER
    fabricates. EMPTY SCOPE = DENY-ALL downstream (the load-bearing safety semantic; must never invert).
  · source unreachable → empty + stale=True + a REGENERATE breadcrumb (fail loud, legible to agents).

Replaces the design/_system/code-symbols.json sidecar (hand-made seed, frozen at 71 registered addresses,
3 weeks stale, lossy code://<stem> ids). Tim's rule: the sidecar read is COMMENTED OUT at its call sites,
not deleted. Every error carries the old path + the new source + the fix command (agents resolve issues,
never humans).
"""
from __future__ import annotations
import os
import subprocess

# the ledger connection — same env-overridable home as ops/ledger_build.py PGCONF (one convention)
_PG = {
    "host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
    "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
    "user": os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"),
    "db":   os.environ.get("COMPANY_LEDGER_PGDB", "postgres"),
    "pw":   os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres"),
}
_BREADCRUMB = ("source = ledger.edge kind='powered-by' (Supabase {host}:{port}, derived by ops/ledger_build.py "
               "PASS C every build; was design/_system/code-symbols.json pre-2026-07-02). If the join is missing, "
               "re-run: .venv/bin/python ops/ledger_build.py --all --load").format(host=_PG["host"], port=_PG["port"])


def _q(sql: str) -> tuple[bool, str]:
    """One ledger query. (ok, stdout|error) — never raises; the caller folds failure into stale+note."""
    try:
        r = subprocess.run(["psql", "-h", _PG["host"], "-p", _PG["port"], "-U", _PG["user"], "-d", _PG["db"],
                            "-tAc", sql], capture_output=True, text=True, timeout=20,
                           env={**os.environ, "PGPASSWORD": _PG["pw"]})
        if r.returncode != 0:
            return False, (r.stderr or "psql failed").strip()[:300]
        return True, r.stdout
    except Exception as e:                                       # unreachable DB → stale, loud note
        return False, f"{type(e).__name__}: {e}"


def _lit(s: str) -> str:
    # Dollar-quote with a tag guaranteed ABSENT from the value (mirrors ops/migrate_container_from_cvi._dq).
    # The old form stripped any literal '$scope$' substring out of the value — silent data corruption; a
    # collision-avoiding tag preserves the value verbatim instead.
    s = str(s)
    i = 0
    while True:
        tag = f"$s{i}$"
        if tag not in s:
            return f"{tag}{s}{tag}"
        i += 1


def resolve_scope(ui_addr: str, *, source=None) -> dict:
    """ui:// → the code that powers it. See the module contract. `source` = injectable rows for tests:
    a list of (ui_addr, powered_by_code_addr) tuples that REPLACES the ledger read (the seam
    conv_blast_acceptance shadows — was _corpus_dir, now this)."""
    from contracts.ui_info import parse_ui_address
    parse_ui_address(ui_addr)                                    # S0 gate — malformed RAISES (TypeError/ValueError)

    if source is not None:                                       # test/fixture seam
        rows = [(u, t) for (u, t) in source if u == ui_addr or (u.endswith("*") and ui_addr.startswith(u[:-1]))]
        ok = True
    else:
        # exact node OR template family (ui://x/y falls under ui://x/* if no exact node binds it)
        got = _q("select e.from_ref, e.to_resolved from ledger.edge e join ledger.latest_run r using(run_id) "
                 f"where e.kind='powered-by' and (e.from_ref = {_lit(ui_addr)} "
                 f"or (e.from_ref like 'ui://%*' and {_lit(ui_addr)} like replace(e.from_ref,'*','')||'%'))")
        ok = got[0]
        rows = [tuple(l.split("|", 1)) for l in got[1].splitlines() if "|" in l] if ok else []

    if not ok:
        return {"address": ui_addr, "symbols": [], "scope": [], "stale": True,
                "note": f"ledger unreachable ({rows if isinstance(rows, str) else got[1][:200]}) — DENY-ALL until restored. {_BREADCRUMB}"}
    if not rows:
        return {"address": ui_addr, "symbols": [], "scope": [], "stale": False,
                "note": f"no powered-by join derived for this address (unregistered in any FE, or a pure-CSS/"
                        f"orphan ref) — DENY-ALL. {_BREADCRUMB}"}
    targets = sorted({t for (_u, t) in rows if t})
    scope = sorted({t.split("::")[0].removeprefix("code://").split("/", 1)[1]     # code://<proj>/<path> → repo path
                    for t in targets if t.startswith("code://") and "/" in t.removeprefix("code://")})
    return {"address": ui_addr, "symbols": targets, "scope": scope, "stale": False,
            "note": f"derived join: {len(rows)} powered-by edge(s) from the ledger (recomputed every build)."}


def symbol_record(code_id: str) -> dict:
    """code:// id → its symbol record {file, referenced_by(ui://), kind, exists} — blast_radius's other need.
    Accepts BOTH the canonical code://<project>/<path>::<symbol> AND the legacy lossy code://<stem>/<symbol>
    (persisted build-intent payloads + FE navigation still carry it — the alias, resolved via the ledger
    where unambiguous; ambiguous legacy ids return exists=False + a legible note, never a guess)."""
    if not isinstance(code_id, str) or not code_id.startswith("code://"):
        raise ValueError(f"symbol_record: not a code:// id: {code_id!r}")
    body = code_id.removeprefix("code://")
    if "::" in body or body.count("/") > 1:                      # canonical (project/path[::symbol])
        path = body.split("::")[0].split("/", 1)[1] if "/" in body else body
        name = body.split("::")[-1].split(".")[-1] if "::" in body else ""
        cond = (f"s.parent_path = {_lit(path)}" + (f" and s.name = {_lit(name)}" if name else ""))
    else:                                                        # legacy code://<stem>/<symbol> or code://<stem>
        stem, _, name = body.partition("/")
        cond = (f"(s.parent_path like '%/' || {_lit(stem)} || '.%' or s.parent_path like {_lit(stem)} || '.%')"
                + (f" and s.name = {_lit(name)}" if name else ""))
    ok, out = _q("select distinct s.parent_path, s.name, s.symbol_kind from ledger.symbol_latest s "
                 f"where {cond} limit 5")
    if not ok:
        return {"id": code_id, "exists": False, "stale": True, "note": f"ledger unreachable — {_BREADCRUMB}"}
    hits = [l.split("|") for l in out.splitlines() if l]
    if not hits:
        return {"id": code_id, "exists": False, "stale": False,
                "note": f"no such symbol in the ledger (checked canonical + legacy forms). {_BREADCRUMB}"}
    files = sorted({h[0] for h in hits})
    if len(files) > 1:                                           # ambiguous legacy stem — refuse to guess
        return {"id": code_id, "exists": False, "stale": False, "ambiguous": files,
                "note": f"legacy id matches {len(files)} files ({files[:3]}…) — use the canonical "
                        f"code://<project>/<path>::<symbol> form. {_BREADCRUMB}"}
    okr, refs = _q("select distinct e.from_ref from ledger.edge e join ledger.latest_run r using(run_id) "
                   f"where e.kind='powered-by' and e.to_resolved like '%' || {_lit(files[0])} || '%'")
    return {"id": code_id, "exists": True, "file": files[0], "kind": hits[0][2] if len(hits[0]) > 2 else "",
            "referenced_by": sorted(l for l in refs.splitlines() if l) if okr else [], "stale": False, "note": ""}
