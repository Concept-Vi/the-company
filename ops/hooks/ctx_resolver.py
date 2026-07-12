#!/usr/bin/env python3
"""ops/hooks/ctx_resolver.py — the resolved-context TURN RESOLVER (Tim, 2026-07-13: "context injection
on a trigger, not just a CLAUDE.md — this keeps growing, resolve it dynamically").

A UserPromptSubmit hook (sibling of pending_mentions_nag.py — the SAME proven pattern: project-scoped
~/company/.claude/settings.json, per-turn, fail-soft): resolves what the ctx substrate holds that THIS
turn should know —
  • the ANTI-LOSS view: open units awaiting return (state axis; capped, salience-ordered when judged)
  • relevance: units matching the prompt's terms (v0 lexical; the embed space is the v1 upgrade)
  • the discoverability line: WHAT this is + the doors (company ctx …) — so no agent needs telling.
Injects a compact <ctx-substrate> block ONLY when there is something to say (conditioned, like the nag).
Fail-soft ALWAYS (exit 0, silent on any error): a hook must never break a session — but a REACHABLE
substrate that errors mid-query prints a one-line RESOLVER ERROR (never a silent wrong answer).
The substrate: schema ctx in the local Supabase PG (see orienteering/entries/ctx-substrate.md).
"""
import json
import os
import re
import subprocess
import sys

PGH = os.environ.get("CTX_PGHOST", "127.0.0.1")
PGP = os.environ.get("CTX_PGPORT", "15432")


def psql(sql: str) -> str:
    r = subprocess.run(
        ["psql", "-h", PGH, "-p", PGP, "-U", "postgres", "-d", "postgres", "-tA", "-F", "\t", "-c", sql],
        capture_output=True, text=True, timeout=6,
        env={**os.environ, "PGPASSWORD": os.environ.get("CTX_PGPASSWORD", "postgres")})
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip().splitlines()[0] if r.stderr.strip() else "psql failed")
    return r.stdout.strip()


try:
    data = json.load(sys.stdin) if not sys.stdin.isatty() else {}
    prompt = (data.get("prompt") or "")[:2000]

    # quick reachability probe — substrate down = silent (fail-soft; sessions must not break)
    try:
        psql("select 1;")
    except Exception:
        sys.exit(0)

    lines = []

    # 1 · the anti-loss view (conditioned: only when something is open)
    open_rows = psql(
        "select address_path, coalesce(meta->'verdict'->>'kind','?'), coalesce(left(body,90),'') "
        "from ctx.unit where state='open' "
        "order by coalesce((meta->'verdict'->>'salience')::float, 0.5) desc, ts asc limit 5;")
    n_open = int(psql("select count(*) from ctx.unit where state='open';") or "0")
    if n_open:
        lines.append(f"open units awaiting return ({n_open}):")
        for row in open_rows.splitlines():
            f = row.split("\t")
            if len(f) >= 3:
                lines.append(f"  [{f[1]}] {f[0]} :: {f[2]}")

    # 2 · relevance to THIS prompt (v0 lexical; skip stop-shaped words)
    terms = [w for w in re.findall(r"[A-Za-z0-9_-]{4,}", prompt)][:8]
    if terms:
        conds = " + ".join(
            "(case when body ilike '%" + t.replace("'", "''") + "%' then 1 else 0 end)" for t in terms)
        rel = psql(
            f"select address_path, state, coalesce(left(body,90),'') from "
            f"(select *, {conds} as score from ctx.unit where body is not null) q "
            f"where score > 0 and state <> 'open' order by score desc, ts desc limit 3;")
        if rel:
            lines.append("substrate units matching this turn:")
            for row in rel.splitlines():
                f = row.split("\t")
                if len(f) >= 3:
                    lines.append(f"  [{f[1]}] {f[0]} :: {f[2]}")

    if lines:
        print(f"<ctx-substrate>")
        print("The resolved-context substrate (conversation as typed, addressed, state-bearing units — "
              "schema ctx, local Supabase). Doors: `company ctx open|chain|brief|units` · docs: "
              "build-prep/the-one-system/glyphic/resolved-context/. This block is RESOLVED per turn "
              "by ops/hooks/ctx_resolver.py.")
        print("\n".join(lines))
        print("</ctx-substrate>")
except Exception:
    # fail-soft: never break the session; a substrate query error after reachability passed
    # is loud-but-tiny (one line), never a fabricated answer
    sys.exit(0)
sys.exit(0)
