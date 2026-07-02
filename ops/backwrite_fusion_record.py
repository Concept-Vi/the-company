#!/usr/bin/env python3
"""ops/backwrite_fusion_record.py — ④ L1-SPINE, C1.6: THE BACK-WRITE MOMENT.

The campaign's decided record lands INSIDE the container it built — the-fusion project's authored
shelves — so the fusion is self-recording from its first slice (the case study records itself):

  project://the-fusion/decisions/…   the ①–④ DECIDED lists (NORTH-STAR.md §①/②/③ DECISIONS +
                                     THE-CONTAINER.md §DECISIONS), one resource per organ's list.
  project://the-fusion/ore/…         the 7 organ rebuild studies + the hollow-types investigation
                                     (organ-studies/*.md), full text, one resource per study.
  project://the-fusion/concepts/…    the 11 settled design laws (THE-CONTAINER.md laws 1–10 + Law 11)
                                     + the 2 standing methodologies, one resource each.

Every resource is PROVENANCE-STAMPED: {source_doc: repo-relative path, commit_sha: the doc's last git
commit, extracted_at}. Idempotent (upsert on the UNIQUE address; run twice = same rows, refreshed
content). Queryable back through the ONE resolver: resolve_address("project://the-fusion/decisions/…").

LAWS: derive-never-place (the record derives from the source docs — re-run to refresh) · registry-is-truth
(a missing source doc / missing shelf FAILS LOUD, never a silent skip) · fail-loud breadcrumbs.

Run:  .venv/bin/python ops/backwrite_fusion_record.py
"""
from __future__ import annotations
import importlib.util, json, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
DOCS = os.path.join(REPO, "build-prep", "the-one-system")

# REUSE the migration's DB helpers + identity constants (one convention, no parallel connection code)
_spec = importlib.util.spec_from_file_location(
    "migrate_container_from_cvi", os.path.join(REPO, "ops", "migrate_container_from_cvi.py"))
_mig = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mig)
_psql, _psql_script, _json_rows = _mig._psql, _mig._psql_script, _mig._json_rows
_dq, _lit, _jsonb, _arr, _slug = _mig._dq, _mig._lit, _mig._jsonb, _mig._arr, _mig._slug
PGDB, FUSION_KEY, VI_AGENT = _mig.PGCONF["db"], _mig.FUSION_KEY, _mig.VI_AGENT

STUDIES = ("SPINE", "CIRCUIT", "REGISTRY", "BOARD", "KEEPER", "TENANCY", "GRAPH-PATH", "HOLLOW-TYPES")


def _read(relpath: str) -> str:
    p = os.path.join(REPO, relpath)
    if not os.path.isfile(p):
        raise RuntimeError(f"backwrite: source doc missing: {p} — expected the campaign doc at that path; "
                           f"previously (never — this is the first back-write); fix: restore the doc or "
                           f"correct the path in ops/backwrite_fusion_record.py. Fail loud.")
    return open(p, encoding="utf-8").read()


def _sha(relpath: str) -> str:
    r = subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%H", "--", relpath],
                       capture_output=True, text=True)
    sha = (r.stdout or "").strip()
    return sha or "uncommitted"


def _prov(relpath: str) -> dict:
    return {"source_doc": relpath, "commit_sha": _sha(relpath), "written_by": "ops/backwrite_fusion_record.py"}


def _section(text: str, start_pat: str, *, stop_pat: str = r"^# ") -> str:
    """The block from the heading matching start_pat to the next heading matching stop_pat (or EOF).
    FAIL-LOUD if the start heading is absent (the doc drifted — never a silent empty record)."""
    lines = text.splitlines()
    start = next((i for i, ln in enumerate(lines) if re.match(start_pat, ln)), None)
    if start is None:
        raise RuntimeError(f"backwrite: section {start_pat!r} not found in the source doc — the doc "
                           f"drifted; update ops/backwrite_fusion_record.py's extraction. Fail loud.")
    end = next((j for j in range(start + 1, len(lines)) if re.match(stop_pat, lines[j])), len(lines))
    return "\n".join(lines[start:end]).strip()


def _shelves() -> dict:
    rows = _json_rows(PGDB, "select s.scope_key, s.scope_id, s.project_id, s.address from container.scopes s "
                            "join container.projects p using(project_id) "
                            f"where p.project_key = {_dq(FUSION_KEY)}")
    got = {r["scope_key"]: r for r in rows}
    for need in ("decisions", "ore", "concepts"):
        if need not in got:
            raise RuntimeError(f"backwrite: the-fusion shelf '{need}' missing — expected "
                               f"project://{FUSION_KEY}/{need} (container.scopes); previously nothing; "
                               f"fix: .venv/bin/python ops/migrate_container_from_cvi.py --slice spine")
    return got


def _upsert(shelf: dict, key: str, rtype: str, title: str, content: dict, prov: dict,
            tags: list | None = None) -> str:
    addr = f"{shelf['address']}/{key}"
    _psql_script(PGDB, f"""
begin;
insert into container.resources (project_id, scope_id, resource_key, resource_type, address, title, content,
                                 tags, created_by, source_system, provenance)
values ({_dq(shelf['project_id'])}::uuid, {_dq(shelf['scope_id'])}::uuid, {_dq(key)}, {_dq(rtype)},
        {_dq(addr)}, {_dq(title)}, {_jsonb(content)}, {_arr(tags)}, {_dq(VI_AGENT)},
        'backwrite_fusion_record', {_jsonb(prov)})
on conflict (address) do update set content=excluded.content, title=excluded.title,
        provenance=excluded.provenance, tags=excluded.tags, updated_at=now();
commit;""")
    return addr


def backwrite() -> dict:
    shelves = _shelves()
    landed = {"decisions": [], "ore": [], "concepts": []}

    # ── decisions/ — the ①–④ DECIDED lists ──────────────────────────────────────────────────────────
    ns_rel = "build-prep/the-one-system/NORTH-STAR.md"
    ns = _read(ns_rel)
    ns_prov = _prov(ns_rel)
    organs = [
        ("1-vector-cutover", r"^# ① ", "① the vector read-path cutover — Tim's decided list"),
        ("2-address-surface", r"^# ② ", "② the address surface change — Tim's decided list"),
        ("3-the-window", r"^# ③ ", "③ the fork / the window — Tim's decided list"),
    ]
    for key, organ_pat, title in organs:
        organ_block = _section(ns, organ_pat)
        decided = _section(organ_block, r"^## DECISIONS", stop_pat=r"^#{1,2} ")
        landed["decisions"].append(_upsert(
            shelves["decisions"], key, "decision-record", title,
            {"text": decided, "organ": key.split("-")[0]}, ns_prov, tags=["decided", "north-star"]))
    tc_rel = "build-prep/the-one-system/THE-CONTAINER.md"
    tc = _read(tc_rel)
    tc_prov = _prov(tc_rel)
    decided4 = _section(tc, r"^## DECISIONS", stop_pat=r"^## ")
    landed["decisions"].append(_upsert(
        shelves["decisions"], "4-the-container", "decision-record",
        "④ the container — Tim's decided list (v3)",
        {"text": decided4, "organ": "4"}, tc_prov, tags=["decided", "the-container"]))

    # ── ore/ — the organ rebuild studies (full text; dead-stuff and glow both ride whole) ────────────
    for st in STUDIES:
        rel = f"build-prep/the-one-system/organ-studies/{st}.md"
        txt = _read(rel)
        landed["ore"].append(_upsert(
            shelves["ore"], f"study-{st.lower()}", "organ-study",
            f"Organ rebuild study — {st}", {"text": txt}, _prov(rel), tags=["organ-study", st.lower()]))

    # ── concepts/ — the 11 laws + the 2 standing methodologies ───────────────────────────────────────
    laws_block = _section(tc, r"^## The recurring design laws", stop_pat=r"^## ")
    items = re.findall(r"^(\d+)\.\s+(.*?)(?=^\d+\.\s|\Z)", laws_block, flags=re.M | re.S)
    if len(items) != 10:
        raise RuntimeError(f"backwrite: expected 10 numbered laws in THE-CONTAINER.md's laws block, "
                           f"found {len(items)} — the doc drifted; fix the extraction. Fail loud.")
    for n, body in items:
        body = " ".join(body.split())
        m = re.match(r"\*\*(.+?)\*\*", body)
        title = m.group(1).rstrip(".") if m else body[:80]
        landed["concepts"].append(_upsert(
            shelves["concepts"], f"law-{int(n):02d}", "design-law", f"Law {n}: {title}",
            {"text": body, "law": int(n)}, tc_prov, tags=["law", "settled"]))
    law11 = _section(tc, r"^## Law 11", stop_pat=r"^## ")
    landed["concepts"].append(_upsert(
        shelves["concepts"], "law-11", "design-law",
        "Law 11: types declare their states; state is a resolution axis",
        {"text": law11, "law": 11}, tc_prov, tags=["law", "settled", "tim"]))
    for key, pat, title in (
            ("methodology-hand-made-powers-the-generator", r"^## Standing methodology .*hand-made",
             "Standing methodology: hand-made powers the generator"),
            ("methodology-dead-stuff-carries-intention", r"^## Standing methodology .*dead stuff",
             "Standing methodology: dead stuff carries intention")):
        block = _section(tc, pat, stop_pat=r"^## ")
        landed["concepts"].append(_upsert(
            shelves["concepts"], key, "methodology", title, {"text": block}, tc_prov,
            tags=["methodology", "tim"]))

    # ── read one back through the ONE resolver (the by-use proof, in-process) ────────────────────────
    from runtime.cognition import resolve_address
    probe = landed["concepts"][0]
    rec = resolve_address(None, probe)
    if rec.get("kind") != "resource" or not (rec.get("record") or {}).get("content"):
        raise RuntimeError(f"backwrite: read-back through resolve_address failed for {probe} — landed but "
                           f"not resolvable; fail loud.")
    return {"landed": landed,
            "counts": {k: len(v) for k, v in landed.items()},
            "read_back_ok": probe}


if __name__ == "__main__":
    print(json.dumps(backwrite(), indent=2))
