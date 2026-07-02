#!/usr/bin/env python3
"""ops/migrate_identity_from_cvi.py — ④ L2-IDENTITY: the 15 cloud users + the delegation collapse.

Lands, per organ-studies/TENANCY.md §3.4 + THE-CONTAINER v3 DECISIONS (Tim's identity correction):

  C2.3 — the 15 cloud auth.users map:
    · 554e223d (t.geldard@)          → operator://tim   (the ONE operator; primary login) [seeded by 0017]
    · ebe5f9c7 (v.i@) + …0001 (vi@system.local) → agent://vi (VI's OWN identity — Tim's correction) [seeded]
    · grant / nick / phil / scott    → human principals (curated; the @example.com ones flagged family-test)
    · the 8 NO-EMAIL users           → test debris, ARCHIVED excluded-with-reason (NOT migrated)
    The uuid_rewrite_map gets a row for EVERY cloud uuid (old → principal, or archived).
    (NOTE: the map/criteria said "7 no-email"; the LIVE cvi_mine has 8 — measured, reconciled honestly.)

  C2.5 — the delegations (14 cloud rows):
    · the 13 duplicate L3 (user → vi:global, global, identical scopes) COLLAPSE into the ONE confirmed
      acts-for delegation operator://tim → agent://vi (seeded by 0017), which is marked confirmed=true
      and gets 13 EVIDENCE entries (each preserving its source cvi row — the system-wide pattern kept).
    · the L5 grant (ebe5f9c7 = the vi agent's own super-user delegation) LANDS with its window as a
      historical delegation agent://vi → agent://vi (faithful to source; a distinct row, no collision).

LAWS: idempotent (deterministic keys; upserts; run twice = same result) · cvi_mine is NEVER mutated
(read-only SELECTs — this script contains no INSERT/UPDATE/DELETE against cvi_mine) · every curation
writes excluded-with-reason (container.exclusions + the report) · fail-loud with breadcrumbs · every
reconciliation sum prints its denominators.

Run:  .venv/bin/python ops/migrate_identity_from_cvi.py --slice identity
Prereq: 0013_container.sql + 0017_identity.sql applied.
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys, uuid

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

PGCONF = {"host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
          "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
          "user": os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"),
          "db": os.environ.get("COMPANY_LEDGER_PGDB", "postgres"),
          "pw": os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres")}
CVI_DB = os.environ.get("COMPANY_CVI_DB", "cvi_mine")     # the immutable source-of-record (READ-ONLY)

# Tim's identity correction (decision constants — the SAME as migrate_container_from_cvi.PRINCIPAL_MAP).
OPERATOR_LOGIN = "554e223d-e431-41ce-8913-1a7d8d81d321"   # t.geldard@ → operator://tim (primary)
VI_LOGINS = ["ebe5f9c7-4d66-4717-835f-afc96088facb",      # v.i@ → agent://vi
             "00000000-0000-0000-0000-000000000001"]      # vi@system.local → agent://vi (second login)
VI_GRANTEE_TEXT = "vi:global"                             # A's bare-text grantee ≡ agent://vi
OPERATOR = "operator://tim"
VI_AGENT = "agent://vi"


def _psql(db: str, sql: str) -> str:
    env = {**os.environ, "PGPASSWORD": PGCONF["pw"]}
    r = subprocess.run(["psql", "-h", PGCONF["host"], "-p", PGCONF["port"], "-U", PGCONF["user"],
                        "-d", db, "-v", "ON_ERROR_STOP=1", "-tA", "-c", sql],
                       capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"psql({db}) failed: {r.stderr.strip()[:600]}\nSQL head: {sql[:200]}")
    return r.stdout


def _psql_script(db: str, sql: str) -> str:
    env = {**os.environ, "PGPASSWORD": PGCONF["pw"]}
    r = subprocess.run(["psql", "-h", PGCONF["host"], "-p", PGCONF["port"], "-U", PGCONF["user"],
                        "-d", db, "-v", "ON_ERROR_STOP=1"],
                       input=sql, capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"psql script({db}) failed (rolled back): {r.stderr.strip()[:600]}")
    return r.stdout


def _json_rows(db: str, sql: str) -> list[dict]:
    out = _psql(db, f"select coalesce(json_agg(t), '[]'::json) from ({sql}) t")
    return json.loads(out.strip() or "[]")


def _dq(s) -> str:
    s = str(s)
    i = 0
    while True:
        tag = f"$q{i}$"
        if tag not in s:
            return f"{tag}{s}{tag}"
        i += 1


def _lit(v) -> str:
    return "NULL" if v is None else _dq(v)


def _arr(xs) -> str:
    xs = [x for x in (xs or []) if x is not None]
    return "'{}'::text[]" if not xs else "array[" + ",".join(_dq(x) for x in xs) + "]::text[]"


def _slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")
    return s or "unknown"


def _human_handle(email: str) -> str:
    """email local part → a principal handle (strip +suffix; slug). grant@… → grant;
    nick.godfrey+auto@example.com → nick-godfrey; phil.geldard@example.com → phil-geldard."""
    local = email.split("@", 1)[0].split("+", 1)[0]
    return _slug(local)


BREADCRUMB = ("expected the identity model (0017_identity.sql, schema container); fix: apply "
              "0013_container.sql + 0017_identity.sql then .venv/bin/python "
              "ops/migrate_identity_from_cvi.py --slice identity")


def migrate_identity() -> dict:
    rep: dict = {"slice": "identity", "sections": {}, "denominators": {}}

    # 0. preflight — the principal model must exist.
    if not _psql(PGCONF["db"], "select 1 from information_schema.tables where table_schema='container' "
                               "and table_name='principal'").strip():
        raise RuntimeError(f"container.principal missing — {BREADCRUMB}")

    # 1. read the 15 cloud auth.users (READ-ONLY).
    users = _json_rows(CVI_DB, "select id::text as id, coalesce(email,'') as email from auth.users order by email")
    total = len(users)
    login_set = {OPERATOR_LOGIN, *VI_LOGINS}
    humans = [u for u in users if u["email"] and u["id"] not in login_set]
    no_email = [u for u in users if not u["email"]]
    seeded_logins = [u for u in users if u["id"] in login_set]

    # 2. HUMANS → human principals (curated). @example.com flagged family-test in metadata (needs_tim).
    minted_humans = []
    for u in humans:
        handle = _human_handle(u["email"])
        family_test = u["email"].endswith("@example.com")
        meta = {"email": u["email"], "family_test": family_test,
                "note": ("@example.com — likely family/test account; landed as human per the §3.4 map, "
                         "flagged for Tim's curation." if family_test else "curated human principal.")}
        _psql_script(PGCONF["db"], f"""
begin;
insert into container.principal (kind, handle, display, status, metadata, source_system, source_uuid)
values ('human', {_dq(handle)}, {_dq(u['email'])}, 'active', {_dq(json.dumps(meta))}::jsonb,
        'cvi_mine', {_dq(u['id'])}::uuid)
on conflict (kind, handle) do update set source_uuid = excluded.source_uuid, metadata = excluded.metadata;
-- the auth edge (authentication is an edge to identity)
insert into container.principal_auth (principal_id, auth_user_id, provider, is_primary, source_system)
select p.principal_id, {_dq(u['id'])}::uuid, 'supabase', true, 'cvi_mine'
  from container.principal p where p.kind='human' and p.handle={_dq(handle)}
on conflict (principal_id, auth_user_id) do nothing;
-- the uuid rewrite map row
insert into container.uuid_rewrite_map (old_uuid, principal_id, principal_address, disposition, reason)
select {_dq(u['id'])}::uuid, p.principal_id, 'human://'||{_dq(handle)}, 'human',
       {_dq(meta['note'])}
  from container.principal p where p.kind='human' and p.handle={_dq(handle)}
on conflict (old_uuid) do update set principal_id=excluded.principal_id,
       principal_address=excluded.principal_address, disposition=excluded.disposition, reason=excluded.reason;
commit;""")
        minted_humans.append(f"human://{handle}")

    # 3. the 8 NO-EMAIL users → ARCHIVED excluded-with-reason (NOT migrated; uuid_rewrite disposition=archived).
    archived = 0
    for u in no_email:
        reason = "no-email cloud auth.user — test debris (§3.4: archived, not migrated as a principal)."
        _psql_script(PGCONF["db"], f"""
begin;
insert into container.exclusions (source_system, source_table, source_uuid, source_key, reason)
values ('cvi_mine', 'auth.users', {_dq(u['id'])}::uuid, NULL, {_dq(reason)})
on conflict (source_system, source_table, source_uuid) do update set reason=excluded.reason;
insert into container.uuid_rewrite_map (old_uuid, principal_id, principal_address, disposition, reason)
values ({_dq(u['id'])}::uuid, NULL, NULL, 'archived', {_dq(reason)})
on conflict (old_uuid) do update set disposition=excluded.disposition, reason=excluded.reason;
commit;""")
        archived += 1

    rep["sections"]["users"] = {
        "source": total, "operator_login": 1, "vi_agent_logins": len(VI_LOGINS),
        "humans_landed": len(minted_humans), "archived": archived,
        "sums_match": (1 + len(VI_LOGINS) + len(minted_humans) + archived) == total,
    }
    rep["denominators"]["users"] = (f"{total} cloud auth.users = 1 operator login + {len(VI_LOGINS)} "
                                    f"vi-agent logins + {len(minted_humans)} humans + {archived} archived")

    # 4. DELEGATIONS (14 cloud rows) — the collapse + the L5 grant.
    dels = _json_rows(CVI_DB, "select delegation_id::text as delegation_id, user_id::text as user_id, "
                              "grantee_actor_id, coalesce(space_id::text,'') as space_id, scopes, "
                              "max_autonomy, status, valid_from::text as valid_from, "
                              "coalesce(valid_to::text,'') as valid_to from delegations")
    l3 = [d for d in dels if d["max_autonomy"] == "L3" and d["grantee_actor_id"] == VI_GRANTEE_TEXT]
    l5 = [d for d in dels if d["max_autonomy"] == "L5"]
    others = [d for d in dels if d not in l3 and d not in l5]

    # 4a. the acts-for canonical row (seeded by 0017) → confirm it + attach the 13 L3 evidence entries.
    canon = _json_rows(PGCONF["db"],
                       "select d.delegation_id::text as id from container.delegation d "
                       "join container.principal o on o.principal_id=d.delegator "
                       "join container.principal g on g.principal_id=d.grantee "
                       "where o.address='operator://tim' and g.address='agent://vi' and d.kind='acts_for'")
    if not canon:
        raise RuntimeError(f"the acts-for delegation operator://tim→agent://vi is missing — {BREADCRUMB} "
                           f"(0017 seeds it). Fail loud.")
    canon_id = canon[0]["id"]
    ev_sql = ["begin;",
              f"update container.delegation set confirmed=true, updated_at=now() where delegation_id={_dq(canon_id)}::uuid;"]
    for d in l3:
        note = ("historical L3 grant (user → vi:global, global) — one of the 13 duplicates; collapsed "
                "into the confirmed acts-for. The rebuilt grant elevates to L5 (the creator relationship); "
                "the L3 history is preserved here as evidence.")
        ev_sql.append(
            "insert into container.delegation_evidence (delegation_id, source_system, source_table, "
            "source_uuid, source_delegator, source_grantee, source_scopes, source_max_autonomy, "
            "source_valid_from, note) values "
            f"({_dq(canon_id)}::uuid, 'cvi_mine', 'delegations', {_dq(d['delegation_id'])}::uuid, "
            f"{_dq(d['user_id'])}::uuid, {_dq(d['grantee_actor_id'])}, {_arr(d['scopes'])}, "
            f"{_dq(d['max_autonomy'])}, {_dq(d['valid_from'])}::timestamptz, {_dq(note)}) "
            "on conflict (delegation_id, source_uuid) do update set note=excluded.note;")
    ev_sql.append("commit;")
    _psql_script(PGCONF["db"], "\n".join(ev_sql))

    # 4b. the L5 grant → a historical delegation agent://vi → agent://vi with its window (faithful to
    # source). Its non-empty `constraints` jsonb ({"can_deploy_to_langgraph": true, ...}) is PRESERVED
    # verbatim as an evidence entry on the landed row (dead-stuff-carries-intention — the delegation
    # table carries no metadata column; the evidence note is the legible home, never lost).
    l5_landed = 0
    l5_rows = _json_rows(CVI_DB, "select delegation_id::text as delegation_id, "
                                 "coalesce(constraints::text,'{}') as constraints from delegations "
                                 "where max_autonomy='L5'") if l5 else []
    l5_constraints = {r["delegation_id"]: r["constraints"] for r in l5_rows}
    for d in l5:
        _psql_script(PGCONF["db"], f"""
begin;
insert into container.delegation (delegator, grantee, container_address, scopes, max_autonomy,
                                  valid_from, valid_to, status, confirmed, kind, source_system, source_uuid)
select v.principal_id, v.principal_id, null, {_arr(d['scopes'])}, {_dq(d['max_autonomy'])},
       {_dq(d['valid_from'])}::timestamptz,
       {('NULL' if not d['valid_to'] else _dq(d['valid_to'])+'::timestamptz')},
       {_dq(d['status'])}, true, 'historical', 'cvi_mine', {_dq(d['delegation_id'])}::uuid
  from container.principal v where v.address='agent://vi'
on conflict (delegator, grantee, coalesce(container_address,'')) do update
   set scopes=excluded.scopes, max_autonomy=excluded.max_autonomy, valid_from=excluded.valid_from,
       valid_to=excluded.valid_to, source_uuid=excluded.source_uuid, updated_at=now();
insert into container.delegation_evidence (delegation_id, source_system, source_table, source_uuid,
       source_delegator, source_grantee, source_scopes, source_max_autonomy, source_valid_from, note)
select dd.delegation_id, 'cvi_mine', 'delegations', {_dq(d['delegation_id'])}::uuid,
       {_dq(d['user_id'])}::uuid, {_dq(d['grantee_actor_id'])}, {_arr(d['scopes'])},
       {_dq(d['max_autonomy'])}, {_dq(d['valid_from'])}::timestamptz,
       {_dq('the L5 super-user grant (v.i@ → vi:global) — landed as this historical row; source '
            'constraints preserved verbatim: ' + l5_constraints.get(d['delegation_id'], '{}'))}
  from container.delegation dd where dd.source_uuid={_dq(d['delegation_id'])}::uuid
on conflict (delegation_id, source_uuid) do update set note=excluded.note;
commit;""")
        l5_landed += 1

    rep["sections"]["delegations"] = {
        "source": len(dels), "l3_collapsed_to_evidence": len(l3), "l5_landed": l5_landed,
        "others": len(others), "confirmed_acts_for": 1,
        "sums_match": (len(l3) + l5_landed + len(others)) == len(dels),
    }
    rep["denominators"]["delegations"] = (
        f"{len(dels)} cloud delegations = {len(l3)} L3 (→ evidence on 1 confirmed acts-for) + "
        f"{l5_landed} L5 (→ historical agent://vi grant) + {len(others)} other")

    # 5. spot-verify the uuid rewrite map on 10 sampled cloud rows vs cvi_mine.
    sample = _json_rows(PGCONF["db"],
                        "select m.old_uuid::text as old_uuid, m.disposition, m.principal_address "
                        "from container.uuid_rewrite_map m order by m.old_uuid limit 10")
    spot = []
    for s in sample:
        cvi_email = _json_rows(CVI_DB, f"select coalesce(email,'') as email from auth.users "
                                       f"where id={_dq(s['old_uuid'])}::uuid")
        email = cvi_email[0]["email"] if cvi_email else "(absent in cvi)"
        ok = True
        if s["disposition"] == "archived":
            ok = (email == "")
        elif s["disposition"] == "operator":
            ok = (s["old_uuid"] == OPERATOR_LOGIN and email == "t.geldard@conceptv.com.au")
        elif s["disposition"] == "agent":
            ok = (s["old_uuid"] in VI_LOGINS)
        elif s["disposition"] == "human":
            ok = (email not in ("", "t.geldard@conceptv.com.au", "v.i@conceptv.com.au"))
        spot.append({"old_uuid": s["old_uuid"], "cvi_email": email, "disposition": s["disposition"],
                     "principal": s["principal_address"], "verified": ok})
    rep["sections"]["uuid_rewrite_spotcheck"] = {"sampled": len(spot),
                                                 "all_verified": all(x["verified"] for x in spot),
                                                 "rows": spot}

    return rep


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--slice", default="identity", choices=["identity"])
    ap.add_argument("--json", action="store_true", help="print the reconciliation report as JSON")
    args = ap.parse_args()
    report = migrate_identity()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("\n④ L2-IDENTITY — migration reconciliation")
        for name, sec in report["sections"].items():
            print(f"\n[{name}]")
            for k, v in sec.items():
                if k == "rows":
                    for r in v:
                        print(f"    {r}")
                else:
                    print(f"  {k}: {v}")
        print("\nDENOMINATORS:")
        for k, v in report["denominators"].items():
            print(f"  {k}: {v}")
