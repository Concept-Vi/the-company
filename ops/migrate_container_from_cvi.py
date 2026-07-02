#!/usr/bin/env python3
"""ops/migrate_container_from_cvi.py — ④ L1-SPINE: the curated container transplant + the ledger backfill.

The SPINE's data landing (organ-studies/SPINE.md §4 "Data landing" + THE-CONTAINER v2 dispositions,
confirmed by v3 "9-not-12 projects"):

  --slice spine (the only slice today):
    1. ONE Space minted (Tim decided: one Space; the cloud's 55 spaces — 15 unnamed personal +
       40 per-project — are ALL excluded-with-reason; the ownership frame collapses to one).
    2. The 4 ledger labels minted as container.projects rows (company · counterpart-design ·
       platforms · claude-ds), root_path set (PROJECT_ROOTS dies as code, lives as data — C1.5;
       `platforms`, the live defect, finally gets a root). counterpart-design is DRESSED.
    3. the-fusion minted NEW — the 10th live project, first born at home.
    4. The 9 curated cloud projects migrate (ci-processing, workshop-v2, vi-coder-config, dev-tracers,
       block-composition, project-system, universal-types, vi-chat, el-external-wizardry);
       bobs-cars + miro-integration + default-project are excluded-with-reason (v2 disposition).
    5. Their 86 scopes: 76 migrate under surviving projects; 10 (under the 3 excluded projects)
       excluded-with-reason. 483 resources migrate. 41 project_content rows FOLD INTO resources
       (a parallel lane, same organ — SPINE). Addresses rewritten to the ONE grammar
       (project://<key>/<scope>/<resource-key>); originals kept in source_meta.
    6. members: 11 migrate (principals remapped to ADDRESSES per Tim's identity correction:
       ebe5f9c7/v.i@ → agent://vi · 554e223d/t.geldard@ → operator://tim · agent keys → agent://<key>);
       3 (on excluded projects) excluded-with-reason. The minimal identity SEED (operator://tim +
       agent://vi) lands as member rows on every minted project (full principal model is L2's).
    7. The ledger backfill: ledger.entry/run/coverage_findings.project_id set by label join —
       100% by construction, count-verified with printed denominators (C1.4).
    8. Reconciliation report (source → landed → excluded, sums match) printed AND landed as a
       resource at project://the-fusion/ore/reconciliation-spine (CA.1's archive home).

LAWS: idempotent (deterministic keys; upserts; run twice = same result) · resumable (each section
upserts independently) · cvi_mine is NEVER mutated (read-only SELECTs; verified: this script contains
no INSERT/UPDATE/DELETE against cvi_mine) · every curation writes excluded-with-reason
(container.exclusions + the report) · fail-loud with breadcrumbs.

Also exports create_project() — C1.7's ONE ATOMIC CIRCUIT (space-if-needed → project → membership →
keeper binding → ledger label reservation) in a single transaction; a failed step rolls the whole
circuit back. The migration itself mints its new projects through it (reuse-don't-parallel).

Run:  .venv/bin/python ops/migrate_container_from_cvi.py --slice spine
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys, uuid

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

# one convention with ops/ledger_interpret.py + runtime/scope.py (env-overridable)
PGCONF = {"host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
          "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
          "user": os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"),
          "db": os.environ.get("COMPANY_LEDGER_PGDB", "postgres"),
          "pw": os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres")}
CVI_DB = os.environ.get("COMPANY_CVI_DB", "cvi_mine")   # the immutable source-of-record (READ-ONLY)

# ── the curation (THE-CONTAINER v2 disposition table, confirmed v3 "9-not-12") ────────────────────────
MIGRATE_PROJECTS = ("ci-processing", "workshop-v2", "vi-coder-config", "dev-tracers", "block-composition",
                    "project-system", "universal-types", "vi-chat", "el-external-wizardry")
EXCLUDE_PROJECTS = {
    "bobs-cars": "demo/test scaffolding (a car-inventory demo; no resources, 3 empty scopes) — v2 archive disposition",
    "miro-integration": "abandoned integration shell (no resources) — v2 archive disposition",
    "default-project": "auto-minted default scaffolding (the ~11-duplicate default-space disease) — v2 archive disposition",
}
# the 4 ledger labels → root_path (PROJECT_ROOTS dies as code, lives as data — C1.5)
LABEL_PROJECTS = {
    "company":            {"root": REPO, "type": "operations",
                           "desc": "The Vi composition suite — the engine repo (ledger label; 161,835 entries)."},
    "counterpart-design": {"root": "/home/tim/repos/counterpart/design", "type": "design",
                           "desc": "counterpart/design — the addressed design-DNA substrate (ledger label; dressed per Tim: one of the two living projects the window renders)."},
    "platforms":          {"root": os.path.join(REPO, "platforms"), "type": "meta",
                           "desc": "The external-platform capability registry (cap:// rows; the PROJECT_ROOTS gap this migration closes)."},
    "claude-ds":          {"root": os.path.join(REPO, "design", "claude-ds"), "type": "design",
                           "desc": "The claude design-system exploration (ledger label)."},
}
FUSION_KEY = "the-fusion"
FUSION_ROOT = os.path.join(REPO, "build-prep", "the-one-system")
SPACE_KEY = "tim"                                        # the ONE Space (Tim decided)
OPERATOR = "operator://tim"
VI_AGENT = "agent://vi"

# Tim's identity correction (THE-CONTAINER v3 DECISIONS): v.i@ is VI's OWN identity (agent), t.geldard@ is Tim.
PRINCIPAL_MAP = {
    "ebe5f9c7-4d66-4717-835f-afc96088facb": (VI_AGENT, "agent"),
    "user:ebe5f9c7-4d66-4717-835f-afc96088facb": (VI_AGENT, "agent"),
    "554e223d-e431-41ce-8913-1a7d8d81d321": (OPERATOR, "operator"),
}


def _psql(db: str, sql: str, *, quiet: bool = False) -> str:
    env = {**os.environ, "PGPASSWORD": PGCONF["pw"]}
    r = subprocess.run(["psql", "-h", PGCONF["host"], "-p", PGCONF["port"], "-U", PGCONF["user"],
                        "-d", db, "-v", "ON_ERROR_STOP=1", "-tA", "-c", sql],
                       capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"psql({db}) failed: {r.stderr.strip()[:600]}\nSQL head: {sql[:200]}")
    return r.stdout


def _psql_script(db: str, sql: str) -> str:
    """Run a multi-statement script (BEGIN..COMMIT) with ON_ERROR_STOP — a failed step rolls back all."""
    env = {**os.environ, "PGPASSWORD": PGCONF["pw"]}
    r = subprocess.run(["psql", "-h", PGCONF["host"], "-p", PGCONF["port"], "-U", PGCONF["user"],
                        "-d", db, "-v", "ON_ERROR_STOP=1"],
                       input=sql, capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"psql script({db}) failed (transaction rolled back): {r.stderr.strip()[:600]}")
    return r.stdout


def _json_rows(db: str, sql: str) -> list[dict]:
    out = _psql(db, f"select coalesce(json_agg(t), '[]'::json) from ({sql}) t")
    return json.loads(out.strip() or "[]")


def _dq(s) -> str:
    """Dollar-quote with a tag guaranteed absent (the ledger_interpret._dq pattern)."""
    s = str(s)
    i = 0
    while True:
        tag = f"$q{i}$"
        if tag not in s:
            return f"{tag}{s}{tag}"
        i += 1


def _lit(v) -> str:
    if v is None:
        return "NULL"
    return _dq(v)


def _arr(xs) -> str:
    xs = [x for x in (xs or []) if x is not None]
    if not xs:
        return "'{}'::text[]"
    return "array[" + ",".join(_dq(x) for x in xs) + "]::text[]"


def _jsonb(v) -> str:
    if v is None:
        return "NULL"
    return _dq(json.dumps(v)) + "::jsonb"


def _slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")
    return s or "untitled"


def _principal(raw: str) -> tuple[str, str]:
    """cloud created_by/user_id/agent_key → (principal ADDRESS, member_type). Unknown strings stay
    verbatim (source provenance — L2's uuid rewrite map formalizes; never fabricate an identity)."""
    if raw in PRINCIPAL_MAP:
        return PRINCIPAL_MAP[raw]
    return raw, "agent"


BREADCRUMB = ("expected container.projects (schema container, Postgres "
              f"{PGCONF['host']}:{PGCONF['port']}); previously the cloud projects table (cvi_mine) / "
              "PROJECT_ROOTS in ops/ledger_interpret.py; fix: .venv/bin/python "
              "ops/migrate_container_from_cvi.py --slice spine")


# ── C1.7 — create_project: ONE ATOMIC CIRCUIT (A's proven mechanic, rebuilt) ──────────────────────────
def create_project(project_key: str, *, project_type: str | None = None, description: str | None = None,
                   root_path: str | None = None, keeper_role: str | None = None,
                   space_key: str = SPACE_KEY, created_by: str = OPERATOR,
                   source_system: str = "create_project", source_uuid: str | None = None,
                   source_meta: dict | None = None, status: str = "active") -> dict:
    """space-if-needed → project → membership (operator + vi seed) → keeper binding → ledger label
    reservation, in ONE transaction — a failed step rolls the WHOLE circuit back (C1.7). Fail-loud on an
    existing key (a circuit, not an upsert; the migration checks existence first). Provenance-stamped.

    Ledger label reservation = the project row IS the reservation (project_key UNIQUE, the ONE join key
    across lanes) + any PRE-EXISTING ledger rows carrying this bare label are ADOPTED (project_id set) —
    so a label can never dangle unowned once its project exists."""
    if not project_key or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", project_key):
        raise ValueError(f"create_project: bad project_key {project_key!r} — want lowercase slug "
                         f"([a-z0-9._-]). Fail loud.")
    exists = _psql(PGCONF["db"], f"select 1 from container.projects where project_key={_dq(project_key)}").strip()
    if exists:
        raise ValueError(f"create_project: project {project_key!r} already exists — the circuit mints, "
                         f"it never overwrites. Resolve it via project://{project_key}; {BREADCRUMB}")
    pid = str(uuid.uuid4())
    sql = f"""
begin;
-- step 1: space-if-needed (the ONE Space unless another key is asked for)
insert into container.spaces (space_key, kind, owner, description, source_system)
values ({_dq(space_key)}, 'operator', {_dq(OPERATOR)},
        'The one Space — the ownership frame (Tim decided: one Space).', {_dq(source_system)})
on conflict (space_key) do nothing;
-- step 2: the project row (provenance-stamped; address DERIVED by the generated column)
insert into container.projects (project_id, space_id, project_key, project_type, root_path, keeper_role,
                                status, description, source_system, source_uuid, source_meta)
select {_dq(pid)}::uuid, s.space_id, {_dq(project_key)}, {_lit(project_type)}, {_lit(root_path)},
       {_lit(keeper_role)}, {_dq(status)}, {_lit(description)}, {_dq(source_system)},
       {_lit(source_uuid)}{'::uuid' if source_uuid else ''}, {_jsonb(source_meta)}
from container.spaces s where s.space_key={_dq(space_key)};
-- step 3: membership — the minimal identity seed (operator + the vi agent; full model is L2's).
-- These rows are MINTED by the circuit, so their provenance is 'create_project' — NOT the caller's
-- source_system (that belongs on the PROJECT row above, step 2). A transplanted cloud member carries
-- its own source_system + source_uuid; a seed carries neither uuid (source_uuid stays NULL — the shape
-- that distinguishes a minted seed from a landed transplant, keyed on by the honesty relabel).
insert into container.members (project_id, member_type, principal, role, source_system)
values ({_dq(pid)}::uuid, 'operator', {_dq(OPERATOR)}, 'owner', 'create_project'),
       ({_dq(pid)}::uuid, 'agent',    {_dq(VI_AGENT)}, 'member', 'create_project')
on conflict (project_id, principal, role) do nothing;
-- step 4: keeper binding rode the project row (keeper_role above; L7 resolves it to a cast)
-- step 5: ledger label reservation — adopt any pre-existing bare-label rows (never a dangling label)
update ledger.entry             set project_id={_dq(pid)}::uuid where project={_dq(project_key)} and project_id is null;
update ledger.run               set project_id={_dq(pid)}::uuid where project={_dq(project_key)} and project_id is null;
update ledger.coverage_findings set project_id={_dq(pid)}::uuid where project={_dq(project_key)} and project_id is null;
commit;
"""
    _psql_script(PGCONF["db"], sql)
    row = _json_rows(PGCONF["db"], f"select project_id, project_key, address from container.projects "
                                   f"where project_key={_dq(project_key)}")
    if not row:
        raise RuntimeError(f"create_project: circuit committed but no row landed for {project_key!r} — "
                           f"fail loud. {BREADCRUMB}")
    return row[0]


# ── the spine slice ───────────────────────────────────────────────────────────────────────────────────
def _exclude(rows: list[str]) -> None:
    if rows:
        _psql_script(PGCONF["db"], "begin;\n" + "\n".join(rows) + "\ncommit;")


def _exclusion_sql(table: str, src_uuid: str | None, key: str | None, reason: str) -> str:
    return (f"insert into container.exclusions (source_system, source_table, source_uuid, source_key, reason) "
            f"values ('cvi_mine', {_dq(table)}, {_lit(src_uuid)}{'::uuid' if src_uuid else ''}, "
            f"{_lit(key)}, {_dq(reason)}) on conflict (source_system, source_table, source_uuid) "
            f"do update set reason=excluded.reason;")


def migrate_spine() -> dict:
    rep: dict = {"slice": "spine", "sections": {}}

    # 0. preflight — the container schema must exist (the numbered migration applies it)
    if not _psql(PGCONF["db"], "select 1 from information_schema.schemata where schema_name='container'").strip():
        raise RuntimeError("container schema missing — expected schema `container` (0013_container.sql); "
                           "previously nothing (this is the first slice); fix: psql -h "
                           f"{PGCONF['host']} -p {PGCONF['port']} -U {PGCONF['user']} -d {PGCONF['db']} "
                           "-f build-prep/claude-design/supabase/supabase/migrations/0013_container.sql")

    # 1. SPACES — mint the ONE Space; exclude all 55 cloud spaces with reason.
    spaces = _json_rows(CVI_DB, "select space_id, space_key, space_type, name from spaces")
    _psql_script(PGCONF["db"], f"""
begin;
insert into container.spaces (space_key, kind, owner, description, source_system)
values ({_dq(SPACE_KEY)}, 'operator', {_dq(OPERATOR)},
        'The one Space — the ownership frame (Tim decided: one Space, two dressed projects).', 'migrate_container_from_cvi')
on conflict (space_key) do nothing;
commit;""")
    excl = []
    for s in spaces:
        why = ("unnamed personal space — cloud debris (Vi's per-user memory frame; superseded by the one Space)"
               if s["space_type"] == "personal" else
               "per-project cloud space — collapsed into the one Space (Tim decided: one Space); "
               "its project re-homes under space 'tim'")
        excl.append(_exclusion_sql("spaces", s["space_id"], s.get("space_key") or s.get("name"), why))
    _exclude(excl)
    rep["sections"]["spaces"] = {"source": len(spaces), "landed": 0, "excluded": len(spaces), "minted": 1}

    # 2+3. the 4 LABEL projects + the-fusion — minted through the ONE atomic circuit (reuse).
    minted = 0
    for key, spec in LABEL_PROJECTS.items():
        if not _psql(PGCONF["db"], f"select 1 from container.projects where project_key={_dq(key)}").strip():
            create_project(key, project_type=spec["type"], description=spec["desc"], root_path=spec["root"],
                           source_system="migrate_container_from_cvi")
            minted += 1
    if not _psql(PGCONF["db"], f"select 1 from container.projects where project_key={_dq(FUSION_KEY)}").strip():
        create_project(FUSION_KEY, project_type="meta", root_path=FUSION_ROOT,
                       description=("THE FUSION — the one-system campaign: the container rebuilt from the many, "
                                    "the self-recording case study. First project born at home."),
                       source_system="migrate_container_from_cvi")
        minted += 1
    # the-fusion's authored shelves (the back-write's landing scopes)
    shelf_sql = ["begin;"]
    for sk, sdesc in (("decisions", "The campaign's DECIDED record (①–④ decision lists, provenance-stamped)."),
                      ("ore", "Harvested ore: study findings, reconciliation reports, glowing fragments."),
                      ("concepts", "The settled design laws + concepts (the 11 laws)."),
                      ("sequence", "The fusion path's ordered record (C4.5's scope).")):
        shelf_sql.append(
            f"insert into container.scopes (project_id, scope_key, scope_type, address, description, source_system) "
            f"select p.project_id, {_dq(sk)}, 'folder', {_dq(f'project://{FUSION_KEY}/{sk}')}, {_dq(sdesc)}, "
            f"'migrate_container_from_cvi' from container.projects p where p.project_key={_dq(FUSION_KEY)} "
            f"on conflict (address) do nothing;")
    shelf_sql.append("commit;")
    _psql_script(PGCONF["db"], "\n".join(shelf_sql))

    # 4. the 9 curated cloud projects (+ 3 exclusions-with-reason)
    cloud = _json_rows(CVI_DB, "select project_id, project_key, project_name, project_type, project_path::text, "
                               "keeper_agent, description, status, phase, decorators, tags, entry_points, "
                               "metadata, notice_board is not null and notice_board::text not in ('[]','null') as has_board "
                               "from projects")
    by_key = {p["project_key"]: p for p in cloud}
    unknown = set(by_key) - set(MIGRATE_PROJECTS) - set(EXCLUDE_PROJECTS)
    if unknown:
        raise RuntimeError(f"cvi_mine projects not covered by the curation: {sorted(unknown)} — the curation "
                           f"is 9 migrate + 3 excluded (THE-CONTAINER v2); a NEW cloud row means the curation "
                           f"must be re-decided, never silently defaulted. Fail loud.")
    landed_p = 0
    for key in MIGRATE_PROJECTS:
        p = by_key.get(key)
        if p is None:
            raise RuntimeError(f"curated project {key!r} missing from cvi_mine — source drifted; fail loud.")
        if _psql(PGCONF["db"], f"select 1 from container.projects where project_key={_dq(key)}").strip():
            landed_p += 1
            continue
        meta = {"cloud_project_path": p.get("project_path"), "cloud_keeper_agent": p.get("keeper_agent"),
                "cloud_metadata": p.get("metadata"), "cloud_had_notice_board": p.get("has_board"),
                "cloud_project_name": p.get("project_name")}
        create_project(key, project_type=p.get("project_type"), description=p.get("description"),
                       keeper_role=None,  # cloud keeper_agent values are NOT registered roles — carried in
                                          # source_meta verbatim; L7 binds real keeper roles (never fabricate
                                          # a registry ref — registry-is-truth)
                       source_system="cvi_mine", source_uuid=p["project_id"], source_meta=meta,
                       status=p.get("status") or "active")
        landed_p += 1
    excl = [_exclusion_sql("projects", by_key[k]["project_id"], k, why)
            for k, why in EXCLUDE_PROJECTS.items() if k in by_key]
    _exclude(excl)
    rep["sections"]["projects"] = {"source": len(cloud), "landed": landed_p, "excluded": len(excl),
                                   "minted_new": minted, "curation": {"migrate": list(MIGRATE_PROJECTS),
                                                                      "excluded": list(EXCLUDE_PROJECTS)}}

    # project_id lookup (target)
    tmap = {r["project_key"]: r["project_id"]
            for r in _json_rows(PGCONF["db"], "select project_key, project_id from container.projects")}
    smap_cloud = {p["project_id"]: p["project_key"] for p in cloud}   # cloud uuid → key

    # 5a. SCOPES — 76 migrate; 10 (excluded projects') excluded-with-reason.
    scopes = _json_rows(CVI_DB, "select scope_id, project_id, scope_key, scope_name, scope_path::text, scope_type, "
                                "description, decorators, tags, scope_address, resource_count from project_scopes")
    sql, excl, landed_s = ["begin;"], [], 0
    for s in scopes:
        pkey = smap_cloud.get(s["project_id"])
        if pkey in EXCLUDE_PROJECTS:
            excl.append(_exclusion_sql("project_scopes", s["scope_id"], f"{pkey}/{s['scope_key']}",
                                       f"parent project '{pkey}' excluded: {EXCLUDE_PROJECTS[pkey]}"))
            continue
        addr = f"project://{pkey}/{s['scope_key']}"
        meta = {"cloud_scope_path": s.get("scope_path"), "cloud_scope_address": s.get("scope_address"),
                "cloud_scope_name": s.get("scope_name"),
                "cloud_resource_count_denormalized_stale": s.get("resource_count")}
        sql.append(
            f"insert into container.scopes (project_id, scope_key, scope_type, address, description, decorators, "
            f"tags, source_system, source_uuid, source_meta) values ({_dq(tmap[pkey])}::uuid, {_dq(s['scope_key'])}, "
            f"{_dq(s.get('scope_type') or 'folder')}, {_dq(addr)}, {_lit(s.get('description'))}, "
            f"{_arr(s.get('decorators'))}, {_arr(s.get('tags'))}, 'cvi_mine', {_dq(s['scope_id'])}::uuid, "
            f"{_jsonb(meta)}) on conflict (address) do update set source_uuid=excluded.source_uuid, "
            f"source_meta=excluded.source_meta;")
        landed_s += 1
    sql.append("commit;")
    _psql_script(PGCONF["db"], "\n".join(sql))
    _exclude(excl)
    rep["sections"]["scopes"] = {"source": len(scopes), "landed": landed_s, "excluded": len(excl)}

    # scope lookup by cloud uuid → (target scope_id, address, project_key)
    tscopes = {r["source_uuid"]: r for r in _json_rows(
        PGCONF["db"], "select source_uuid, scope_id, address, project_id from container.scopes "
                      "where source_uuid is not null")}

    # 5b. RESOURCES — all 483 belong to surviving projects (verified: excluded projects carry 0).
    res = _json_rows(CVI_DB, "select resource_id, scope_id, project_id, resource_key, resource_name, resource_type, "
                             "content, decorators, tags, uri_refs, ref_uris, created_by, resource_address, "
                             "resource_path::text, address_tree::text, category, version, "
                             "array_to_json(version_history) as version_history, content_hash, "
                             "fssf_context is not null as had_fssf, embedding is not null as had_embedding "
                             "from project_resources")
    sql, excl, landed_r = ["begin;"], [], 0
    for r in res:
        pkey = smap_cloud.get(r["project_id"])
        ts = tscopes.get(r["scope_id"])
        if pkey in EXCLUDE_PROJECTS or ts is None:
            excl.append(_exclusion_sql("project_resources", r["resource_id"], f"{pkey}/{r['resource_key']}",
                                       f"parent project/scope excluded or unlanded (project '{pkey}')"))
            continue
        addr = f"{ts['address']}/{r['resource_key']}"
        created_by, _ = _principal(r.get("created_by") or "")
        meta = {"cloud_resource_address": r.get("resource_address"), "cloud_resource_path": r.get("resource_path"),
                "cloud_address_tree": r.get("address_tree"), "cloud_resource_name": r.get("resource_name"),
                "cloud_category": r.get("category"), "cloud_ref_uris": r.get("ref_uris"),
                "cloud_created_by_verbatim": r.get("created_by"),
                "cloud_had_fssf_context": r.get("had_fssf"),
                "cloud_had_dead_embedding": r.get("had_embedding")}  # dead vector(384) NOT migrated — the ONE pipeline embeds
        sql.append(
            f"insert into container.resources (project_id, scope_id, resource_key, resource_type, address, title, "
            f"content, content_hash, version, version_history, decorators, tags, uri_refs, created_by, "
            f"source_system, source_uuid, source_meta) values ({_dq(tmap[pkey])}::uuid, {_dq(ts['scope_id'])}::uuid, "
            f"{_dq(r['resource_key'])}, {_dq(r['resource_type'])}, {_dq(addr)}, {_lit(r.get('resource_name'))}, "
            f"{_jsonb(r.get('content'))}, {_lit(r.get('content_hash'))}, {int(r.get('version') or 1)}, "
            f"coalesce({_jsonb(r.get('version_history'))}, '[]'::jsonb), {_arr(r.get('decorators'))}, "
            f"{_arr(r.get('tags'))}, {_arr(r.get('uri_refs'))}, {_dq(created_by)}, 'cvi_mine', "
            f"{_dq(r['resource_id'])}::uuid, {_jsonb(meta)}) on conflict (address) do update set "
            f"content=excluded.content, source_meta=excluded.source_meta;")
        landed_r += 1
        if len(sql) >= 120:
            sql.append("commit;"); _psql_script(PGCONF["db"], "\n".join(sql)); sql = ["begin;"]
    sql.append("commit;")
    _psql_script(PGCONF["db"], "\n".join(sql))
    _exclude(excl)
    rep["sections"]["resources"] = {"source": len(res), "landed": landed_r, "excluded": len(excl)}

    # 5c. PROJECT_CONTENT → FOLDS INTO resources (the parallel lane, same organ — SPINE).
    content = _json_rows(CVI_DB, "select content_id, project_id, scope_id, content_type, content_data, title, "
                                 "category, decorators, created_by from project_content")
    sql, excl, landed_c = ["begin;"], [], 0
    for c in content:
        pkey = smap_cloud.get(c["project_id"])
        ts = tscopes.get(c["scope_id"])
        if pkey in EXCLUDE_PROJECTS or ts is None:
            excl.append(_exclusion_sql("project_content", c["content_id"], f"{pkey}/{c.get('title')}",
                                       f"parent project/scope excluded or unlanded (project '{pkey}')"))
            continue
        rkey = f"{_slug(c['title'])}-{c['content_id'][:8]}"       # deterministic + collision-proof → idempotent
        addr = f"{ts['address']}/{rkey}"
        created_by, _ = _principal(c.get("created_by") or "")
        meta = {"folded_from": "project_content", "cloud_content_type": c.get("content_type"),
                "cloud_category": c.get("category"), "cloud_created_by_verbatim": c.get("created_by")}
        sql.append(
            f"insert into container.resources (project_id, scope_id, resource_key, resource_type, address, title, "
            f"content, decorators, created_by, source_system, source_uuid, source_meta) values "
            f"({_dq(tmap[pkey])}::uuid, {_dq(ts['scope_id'])}::uuid, {_dq(rkey)}, {_dq(c['content_type'])}, "
            f"{_dq(addr)}, {_lit(c.get('title'))}, {_jsonb(c.get('content_data'))}, {_arr(c.get('decorators'))}, "
            f"{_dq(created_by)}, 'cvi_mine', {_dq(c['content_id'])}::uuid, {_jsonb(meta)}) "
            f"on conflict (address) do update set content=excluded.content, source_meta=excluded.source_meta;")
        landed_c += 1
    sql.append("commit;")
    _psql_script(PGCONF["db"], "\n".join(sql))
    _exclude(excl)
    rep["sections"]["project_content_folded"] = {"source": len(content), "landed": landed_c, "excluded": len(excl)}

    # 6.0 HONESTY FIX 1(b) — relabel mislabeled SEED member rows.
    # create_project now stamps its seed members 'create_project' (see step 3). But seed rows minted by
    # the ORIGINAL (pre-fix) build carry the caller's source_system leaked onto them ('cvi_mine' on the 9
    # transplanted projects, 'migrate_container_from_cvi' on the 5 minted ones). Correct them idempotently,
    # keyed on the true PROVENANCE SHAPE — a minted seed has source_uuid IS NULL; a transplanted cloud
    # member ALWAYS carries its source_uuid — so this sweeps every seed and touches no transplant. Idempotent:
    # a corrected (or freshly-minted 'create_project') row matches nothing on re-run.
    relabeled = _psql(PGCONF["db"],
        "with fixed as (update container.members set source_system='create_project' "
        "where source_uuid is null and source_system is distinct from 'create_project' returning 1) "
        "select count(*) from fixed").strip()
    rep["sections"]["members_seed_relabel"] = {
        "relabeled_to_create_project": int(relabeled or 0),
        "provenance_shape": "source_uuid IS NULL and source_system<>'create_project' (a minted seed, "
                            "never a transplanted cloud member) — subsumes the 18 'cvi_mine' + 10 "
                            "'migrate_container_from_cvi' seed rows; the caller's source_system belongs on "
                            "the PROJECT row only, not its seeded members"}

    # 6. MEMBERS — principals become ADDRESSES (Tim's identity correction); excluded projects' members excluded.
    # HONESTY FIX 1(a): 'landed' is counted POST-insert (the rows that actually got a cvi_mine provenance
    # row), never pre-incremented before `on conflict do nothing`. FIX 1(c): source rows dropped by the
    # conflict (a transplant whose (project_id, principal, role) already exists as a seed) are ABSORBED —
    # written excluded-with-reason like any other non-landed source row, so the members sum CLOSES AT ROW
    # LEVEL (source = landed + excluded + absorbed).
    mem = _json_rows(CVI_DB, "select member_id, project_id, member_type, user_id, agent_key, role from project_members")
    sql, proj_excl, attempted = ["begin;"], [], {}
    for m in mem:
        pkey = smap_cloud.get(m["project_id"])
        if pkey in EXCLUDE_PROJECTS:
            proj_excl.append(_exclusion_sql("project_members", m["member_id"],
                                            f"{pkey}/{m.get('user_id') or m.get('agent_key')}",
                                            f"parent project '{pkey}' excluded: {EXCLUDE_PROJECTS[pkey]}"))
            continue
        raw = m.get("user_id") or m.get("agent_key") or ""
        principal, ptype = _principal(str(raw))
        if not principal.startswith(("operator://", "agent://")):
            principal = f"agent://{_slug(principal.lstrip('@'))}"   # agent keys ('ci-keeper-agent', '@keeper') → agent:// addresses
        sql.append(
            f"insert into container.members (project_id, member_type, principal, role, source_system, source_uuid) "
            f"values ({_dq(tmap[pkey])}::uuid, {_dq(ptype if m['member_type'] == 'user' else 'agent')}, "
            f"{_dq(principal)}, {_dq(m.get('role') or 'member')}, 'cvi_mine', {_dq(m['member_id'])}::uuid) "
            f"on conflict (project_id, principal, role) do nothing;")
        attempted[m["member_id"]] = {"pkey": pkey, "principal": principal, "role": m.get("role") or "member"}
    sql.append("commit;")
    _psql_script(PGCONF["db"], "\n".join(sql))

    # LANDED = the transplant rows that actually took a cvi_mine provenance row (source_uuid preserved).
    # A row absorbed by the seed keeps no cvi_mine row, so its source_uuid never appears → detected here
    # (the absorbed uuids are RE-DERIVED from cvi_mine, never hardcoded).
    landed_uuids = {r["su"] for r in _json_rows(PGCONF["db"],
        "select source_uuid::text as su from container.members "
        "where source_system='cvi_mine' and source_uuid is not null")}
    landed_ids   = [mid for mid in attempted if mid in landed_uuids]
    absorbed_ids = [mid for mid in attempted if mid not in landed_uuids]
    absorb_excl = [_exclusion_sql(
        "project_members", mid, f"{attempted[mid]['pkey']}/{attempted[mid]['principal']}",
        "absorbed-by-existing-membership (identity remap 554e223d→operator://tim; effective "
        "membership identical)") for mid in absorbed_ids]
    _exclude(proj_excl + absorb_excl)
    rep["sections"]["members"] = {
        "source": len(mem), "landed": len(landed_ids), "excluded": len(proj_excl),
        "absorbed": len(absorbed_ids),
        "absorbed_source_uuids": sorted(absorbed_ids),
        "row_level_close": f"{len(mem)} = {len(landed_ids)} landed + {len(proj_excl)} excluded "
                           f"+ {len(absorbed_ids)} absorbed",
        "identity_note": "ebe5f9c7/v.i@ → agent://vi · 554e223d/t.geldard@ → operator://tim (Tim's "
                         "correction); minted projects carry the operator://tim + agent://vi seed rows "
                         "(source_system='create_project'); the 2 t.geldard owner transplants are "
                         "ABSORBED by that seed (effective membership identical) — L2 = full model"}

    # 7. THE LEDGER BACKFILL (C1.4) — project_id by label join; 100% with printed denominators.
    _psql_script(PGCONF["db"], """
begin;
update ledger.entry e set project_id = p.project_id from container.projects p
  where p.project_key = e.project and e.project_id is null;
update ledger.run r set project_id = p.project_id from container.projects p
  where p.project_key = r.project and r.project_id is null;
update ledger.coverage_findings c set project_id = p.project_id from container.projects p
  where p.project_key = c.project and c.project_id is null;
commit;""")
    bf = _json_rows(PGCONF["db"], "select project, count(*)::int as total, count(project_id)::int as backfilled "
                                  "from ledger.entry group by project order by project")
    runs = _json_rows(PGCONF["db"], "select project, count(*)::int as total, count(project_id)::int as backfilled "
                                    "from ledger.run group by project order by project")
    cov = _json_rows(PGCONF["db"], "select coalesce(project,'(null)') as project, count(*)::int as total, "
                                   "count(project_id)::int as backfilled from ledger.coverage_findings "
                                   "group by 1 order by 1")
    rep["sections"]["ledger_backfill"] = {"entry": bf, "run": runs, "coverage_findings": cov}
    for row in bf:
        if row["total"] != row["backfilled"]:
            raise RuntimeError(f"ledger.entry backfill NOT 100% for '{row['project']}': "
                               f"{row['backfilled']}/{row['total']} — a label without a container.projects "
                               f"row; {BREADCRUMB}")

    # 8. reconciliation — sums must match; archived at project://the-fusion/ore/reconciliation-spine (CA.1).
    for name, sec in rep["sections"].items():
        if {"source", "landed", "excluded"} <= set(sec):
            absorbed_n = sec.get("absorbed", 0)   # a source row dropped by conflict is absorbed-with-reason
            if sec["source"] != sec["landed"] + sec["excluded"] + absorbed_n:
                raise RuntimeError(f"reconciliation FAILED for {name}: source {sec['source']} != landed "
                                   f"{sec['landed']} + excluded {sec['excluded']} + absorbed {absorbed_n} — "
                                   f"fail loud, never a silent drop. The sum must CLOSE at row level.")
            sec["sums_match"] = True
    fus_scope = _json_rows(PGCONF["db"], f"select scope_id, project_id from container.scopes "
                                         f"where address={_dq(f'project://{FUSION_KEY}/ore')}")
    if fus_scope:
        addr = f"project://{FUSION_KEY}/ore/reconciliation-spine"
        _psql_script(PGCONF["db"], f"""
begin;
insert into container.resources (project_id, scope_id, resource_key, resource_type, address, title, content,
                                 created_by, source_system, provenance)
values ({_dq(fus_scope[0]['project_id'])}::uuid, {_dq(fus_scope[0]['scope_id'])}::uuid, 'reconciliation-spine',
        'report', {_dq(addr)}, 'L1-SPINE migration reconciliation (cvi_mine -> container)', {_jsonb(rep)},
        {_dq(VI_AGENT)}, 'migrate_container_from_cvi',
        {_jsonb({'source_doc': 'ops/migrate_container_from_cvi.py', 'source_db': 'cvi_mine (read-only)'})})
on conflict (address) do update set content=excluded.content, updated_at=now();
commit;""")
        rep["report_address"] = addr
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slice", default="spine", choices=["spine"])
    a = ap.parse_args()
    rep = migrate_spine()
    print(json.dumps(rep, indent=2))
    # the human-legible denominator lines (C1.4's contract: denominators PRINTED)
    for row in rep["sections"]["ledger_backfill"]["entry"]:
        print(f"  ledger.entry[{row['project']}]: {row['backfilled']}/{row['total']} backfilled (100% required)",
              file=sys.stderr)


if __name__ == "__main__":
    main()
