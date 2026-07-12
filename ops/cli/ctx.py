"""ctx — the `company ctx` view (the RESOLVED-CONTEXT substrate: conversation units/chains/ledger).

The operator + cross-session face of the ctx schema (local Supabase PG :15432 — see
build-prep/the-one-system/glyphic/resolved-context/). Conversation as bounded, typed, addressed
units on a containment axis (scale-relative: sentence⊂message⊂session⊂project) with a state axis
(registry-declared lifecycles; transitions pg_notify). Chains = the closure of reference edges.
A chain BRIEF is the boot-context a chain-scoped fork receives (fork-per-chain: the fork registers
in the fabric as a CHILD of the main session — member-registry lineage; spawn+registration is the
interactive-session half, this CLI owns the headless half).

  company ctx units [--type T] [--state S]      list units (address-ordered)
  company ctx open                              the ANTI-LOSS view: units awaiting return
  company ctx chain <id-or-address>             the chain: closure of edges from a unit (CTE, both directions)
  company ctx brief <id-or-address>             the FORK BRIEF: the chain serialized (states+verdicts) for a chain-scoped fork
  company ctx crossings                         cross-chain v0: units referenced by 2+ distinct source units
  company ctx types                             the unit-type registry (lifecycles) + edge kinds
"""
import json
import os
import subprocess
import sys

PGHOST = os.environ.get("CTX_PGHOST", "127.0.0.1")
PGPORT = os.environ.get("CTX_PGPORT", "15432")


def _psql(sql, tuples=True):
    env = dict(os.environ, PGPASSWORD=os.environ.get("CTX_PGPASSWORD", "postgres"))
    cmd = ["psql", "-h", PGHOST, "-p", PGPORT, "-U", "postgres", "-d", "postgres", "-X", "-v", "ON_ERROR_STOP=1"]
    cmd += ["-tA", "-F", "\t"] if tuples else []
    cmd += ["-c", sql]
    r = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise SystemExit(f"ctx: substrate unreachable or query failed (psql rc={r.returncode}):\n{r.stderr.strip()}\n"
                         f"(is the local Supabase PG up on {PGHOST}:{PGPORT}? migrations applied?)")
    return r.stdout.rstrip("\n")


def _resolve(ref):
    """id-or-address → uuid. Fail loud on 0 or 2+ matches."""
    ref = ref.replace("'", "''")
    rows = _psql(
        "select id, address_path from ctx.unit "
        f"where id::text = '{ref}' or address_path = '{ref}' or address_path like '%/{ref}' or id::text like '{ref}%';"
    ).splitlines()
    if not rows:
        raise SystemExit(f"ctx: no unit matches '{ref}' (try `company ctx units`)")
    if len(rows) > 1:
        listing = "\n".join("  " + r.replace("\t", "  ") for r in rows[:8])
        raise SystemExit(f"ctx: '{ref}' is ambiguous — {len(rows)} matches:\n{listing}")
    return rows[0].split("\t")[0]


def _chain_sql(uid):
    return f"""
with recursive chain(id, depth) as (
  select '{uid}'::uuid, 0
  union
  select case when e.from_id = c.id then e.to_id else e.from_id end, c.depth + 1
  from chain c join ctx.unit_edge e on (e.from_id = c.id or e.to_id = c.id)
  where c.depth < 20
)
select distinct u.id, u.address_path, u.type, u.state,
       coalesce(u.meta->'verdict'->>'kind','-') as kind,
       coalesce(u.meta->'verdict'->>'salience','-') as salience,
       coalesce(u.body,'') as body
from chain c join ctx.unit u on u.id = c.id
order by u.address_path;"""


def run(args):
    if not args or args[0] in ("-h", "--help", "help"):
        print(__doc__.strip())
        return 0
    cmd, rest = args[0], args[1:]

    if cmd == "units":
        where = ["true"]
        if "--type" in rest:
            where.append(f"type = '{rest[rest.index('--type')+1]}'")
        if "--state" in rest:
            where.append(f"state = '{rest[rest.index('--state')+1]}'")
        out = _psql("select address_path, type, state, coalesce(left(body,70),'') from ctx.unit "
                    f"where {' and '.join(where)} order by address_path;")
        print(out or "(no units)")
        return 0

    if cmd == "open":
        out = _psql("select address_path, type, coalesce(left(body,70),'') from ctx.unit "
                    "where state = 'open' order by ts;")
        print(out if out else "nothing open — every unit has been returned to.")
        return 0

    if cmd == "chain":
        if not rest:
            raise SystemExit("usage: company ctx chain <id-or-address>")
        uid = _resolve(rest[0])
        out = _psql(_chain_sql(uid))
        print(out or f"(unit {uid} has no edges — a chain of one)")
        return 0

    if cmd == "brief":
        if not rest:
            raise SystemExit("usage: company ctx brief <id-or-address>")
        uid = _resolve(rest[0])
        rows = _psql(_chain_sql(uid)).splitlines()
        print(f"# CHAIN BRIEF — fork boot-context for the chain around {uid[:8]}")
        print("# (a chain-scoped fork holds THIS hot; it registers in the fabric as a child of the")
        print("#  spawning session — parent lineage in the member registry. Units address-ordered.)")
        print()
        for r in rows:
            f = r.split("\t")
            if len(f) < 7:
                continue
            _id, addr, typ, state, kind, sal, body = f[0], f[1], f[2], f[3], f[4], f[5], "\t".join(f[6:])
            print(f"[{state}] {addr}  ({typ} · kind={kind} · salience={sal})")
            if body:
                print(f"    {body}")
        edges = _psql(f"""select e.kind, uf.address_path, ut.address_path from ctx.unit_edge e
          join ctx.unit uf on uf.id=e.from_id join ctx.unit ut on ut.id=e.to_id
          where e.from_id in (select id from ({_chain_sql(uid).rstrip(';')}) q)
             or e.to_id   in (select id from ({_chain_sql(uid).rstrip(';')}) q);""")
        if edges:
            print("\n# relations")
            for e in edges.splitlines():
                k, a, b = e.split("\t")
                print(f"  {a}  —{k}→  {b}")
        return 0

    if cmd == "crossings":
        out = _psql("""select ut.address_path, count(distinct e.from_id) as referrers,
              coalesce(left(ut.body,60),'') from ctx.unit_edge e
              join ctx.unit ut on ut.id = e.to_id
              group by ut.id having count(distinct e.from_id) >= 2 order by referrers desc;""")
        print(out if out else "(no cross-chain referents yet — no unit is referenced by 2+ units)")
        return 0

    if cmd == "types":
        print("unit types (lifecycles):")
        print(_psql("select type, states::text, transitions::text from ctx.unit_type order by type;"))
        print("\nedge kinds:")
        print(_psql("select kind, description from ctx.edge_kind order by kind;"))
        return 0

    raise SystemExit(f"ctx: unknown subcommand '{cmd}' — see `company ctx help`")
