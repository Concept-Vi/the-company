---
type: terrain-entry
register: descriptive
aliases: ["the ledger", "supabase docker", "the address tree substrate"]
tags: [orienteering, terrain, ledger, supabase, docker, postgres]
status: unconfirmed
relates-to: ["[[orienteering — constitution]]", "[[Company Map]]"]
depends-on: ["Docker Desktop (Windows side)"]
ports: [15432, 15421, 15423, 15424]
coverage: {files_read: 0, files_total: "n/a (a running system, not a folder)", last_read: "2026-07-08"}
---

# supabase-ledger-docker — the local Supabase (postgres) the Company is moving into

**What it is:** the local Supabase stack in Docker — postgres on **127.0.0.1:15432** (plus 1542x
siblings) holding schema `ledger.*` (entry · edge · latest_run · embedding · container/keeper rungs
via 0023_keeper.sql). Tim (2026-07-07): things are being moved in, **designed along the way**; the
address tree is **pre-formed** there (addresses are nodes, file paths are addresses, extensions are
types, names are ids). Destination substrate for the mesh (see build-prep/mesh/THE-ONE-IDEA.md).

**What lives in it (observed via consumers, not yet surveyed):** `ledger.entry`/`ledger.edge`/
`ledger.latest_run` (the code-side ledger; capability rows project='platforms' feed Suite init's
CapabilityRegistry via ops/ledger_capabilities.py) · `ledger.embedding` incl. **space='exchange'
(6983 rows — recollection's migrated conversation embeddings, the merge-intention spine)** ·
keeper config rungs. Writers/readers: ops/ledger_build.py (+_psql), ops/ledger_capabilities.py,
runtime/scope.py, runtime/type_registry.py, ops/migrate_* — all via shelled psql, config
COMPANY_LEDGER_PG* (defaults 127.0.0.1:15432 postgres/postgres).

**How it runs:** Docker **Desktop** (Windows side) — NO WSL docker.service unit. Launchable from
WSL: `"/mnt/c/Program Files/Docker/Docker/Docker Desktop.exe"` (verified path 2026-07-08). Container
names/compose location: **unconfirmed** (docker was down at first survey — complete this on a live
engine).

**⚠ The half-dead-proxy trap (2026-07-08, paid for):** when the docker engine dies, the Windows
port proxy still ACCEPTS on :15432 and forwards into nothing — psql hangs on the handshake forever
(0 CPU, no error). Suite init hung system-wide ~7h. Fixed: PGCONNECT_TIMEOUT=10 +
subprocess backstop in ops/ledger_build.py::_pgenv/_psql. If Suite inits report cap rows = 0,
check `timeout 5 docker ps` FIRST.

**Prior read of contents:** [[ledger state & unification path]] memory — 88% noise ingest, weak
extractor, 66% dangling edges; 5-step unification path. The mesh's L0/L1 layers attach here
(PLAN.md Phase 1 = the recon that completes this entry).
