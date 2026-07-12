---
type: terrain-entry
register: descriptive
aliases: ["ctx substrate", "resolved-context substrate", "conversation units"]
tags: [resolved-context, substrate, supabase, ctx]
status: confirmed
coverage: {files_read: 5, files_total: 5, last_read: 2026-07-13}
depends-on: "[[local Supabase stack]]"
indexed-by: "[[MAP]]"
---
# ctx — the resolved-context substrate (conversation as typed, addressed units)

**What**: schema `ctx` in the LOCAL Supabase PG (127.0.0.1:15432) — conversation as ONE recursive unit
table (scale-relative containment; `address` is native **ltree**), typed with registry-declared lifecycles
(ctx.unit_type), reference edges (ctx.unit_edge), and a SELF-JUDGING loop: INSERT → pg_net → the bridge
(:8770 run_role ctx_salience) → verdict swept into unit.meta.verdict by pg_cron ('ctx-sweep-verdicts',
every minute). State transitions pg_notify('ctx_state', …).
**Faces**: `company ctx` (units/open/chain/brief/crossings/types) · the migrations + docs at
build-prep/the-one-system/glyphic/resolved-context/ · the judge role roles/ctx_salience.py.
**Physically**: tables in the supabase docker PG; pg_net calls reach the host bridge via host.docker.internal.
**Live/dormant**: LIVE (verified by use 2026-07-13 — self-judge loop observed end-to-end).
