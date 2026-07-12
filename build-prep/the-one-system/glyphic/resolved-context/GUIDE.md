# Resolved-Context — Implementation Guide (wired to the PROVEN seams)

> How each criterion gets built, against seams verified in RESOLVED-CONTEXT-A-mechanics. Nothing speculative:
> every anchor below was exercised this session.

## The proven seams (use these, don't re-derive)
- **Local Supabase PG**: `psql -h 127.0.0.1 -p 15432 -U postgres -d postgres` (PGPASSWORD=postgres). PG 17.6,
  pgvector. `ledger.*` schema resident (the embedding session's). Realtime container is up.
- **Bridge :8770**: `POST /api/cognition/embed {text}` → 2560-dim vector (fails loud unless ensure:true);
  `POST /api/cognition/run_role {role, utterance}` → schema-validated JSON (~0.7s); `GET /api/corpus-query`.
- **Hooks**: UserPromptSubmit stdout(exit 0) → context (VERIFIED — ZEBRA-77); SessionStart matcher:compact fires
  post-compaction; Stop hook can block with feedback (exit 2 / decision:block); configs LIVE-reload; lab pattern =
  scratchpad dir + project-scoped `.claude/settings.json` + `claude -p --model haiku` (PROVEN — never touch
  ~/.claude/settings.json overnight).
- **Roles**: file-discovered `roles/*.py`, `ROLE = {id, prompt_template, output_schema: BaseModel}` (mirror
  eval_classify/embed shape). Import-validated. Fired via run_role.
- **Transcript tree**: every jsonl line has uuid/parentUuid → units mirror cleanly.

## C1 · SLICE-SUB (the substrate)
Schema `ctx` (coordinate name on the fabric thread first — C1.7). One migration file, committed:
```sql
create schema if not exists ctx;
create table ctx.unit_type (
  type text primary key,
  description text not null,
  states jsonb not null,          -- ["draft","open","answered","superseded","parked",...]
  transitions jsonb not null      -- {"draft":["open"],"open":["answered","superseded","parked"],...}
);
create table ctx.unit (
  id uuid primary key default gen_random_uuid(),
  parent_id uuid references ctx.unit(id),
  type text not null references ctx.unit_type(type),
  state text not null,
  address_path text not null,     -- 'session/msg-47/block-3' — the containment path (correction 1)
  body text,
  meta jsonb default '{}',
  ts timestamptz default now()
);
create table ctx.edge_kind (kind text primary key, description text);
create table ctx.unit_edge (
  from_id uuid references ctx.unit(id), to_id uuid references ctx.unit(id),
  kind text references ctx.edge_kind(kind), ts timestamptz default now(),
  primary key (from_id, to_id, kind)
);
```
- **Lifecycle enforcement** = one trigger fn: on UPDATE of state, look up `unit_type.transitions[old.state]`;
  if new.state not in it → `raise exception` (loud, names the legal set — cc_board's exact pattern).
- **State firing** (correction 2) = same trigger, after pass: `pg_notify('ctx_state', json{id,type,old,new,address_path})`.
  Verify with a `LISTEN ctx_state` psql session observing a real event. (Realtime rides logical replication later —
  pg_notify is the verifiable core tonight.)
- **Address**: BEFORE INSERT trigger derives `address_path` = parent.address_path || '/' || short-id (root units
  supply their own). Descendants query = recursive CTE on parent_id (or `address_path like p || '/%'`).
- Seed types: `block {draft→open→answered|superseded|parked}`, `message`, `session`, `comment`. Seed edge kinds:
  `references, builds_on, supersedes, answers, comments_on`.
- **Verify (C1.3/4/6)**: insert a session→message→block tree; try an illegal transition (expect exception); flip a
  block →open with LISTEN attached (observe the notify); run the open-units query.

## C2 · SLICE-S1 (turn-resolution, lab)
Lab dir: `scratchpad/ctxlab/` with `.claude/settings.json`:
- `UserPromptSubmit` → `resolver.sh` → reads stdin JSON (prompt, session_id) → `curl` bridge embed →
  `psql` nearest/open units (v0: match on tags/recency + the open-units query; embedding-match v1 if time) →
  emits `RESOLVED CONTEXT:` block on stdout; on bridge/psql failure prints a LOUD `RESOLVER ERROR:` line (C2.4)
  + appends a log row (a ctx.unit of type resolver_log, or a jsonl in the lab).
- Seed the substrate with facts a fresh model can't know (e.g. "the project codeword is MOSSWOOD-9; the open
  decision is X") → ask the lab session → it must answer FROM the injection (C2.1/2.2).
- `SessionStart` matcher `compact` → same resolver (source=compact) → verify by forcing a compaction in the lab
  (long prompt loop or /compact) and observing the re-injection in the next turn (C2.3).

## C3 · SLICE-JUDGES
- `roles/ctx_salience.py`: ROLE with prompt_template "Classify this conversation span…" +
  `output_schema: {kind: decision|fact|preference|question|scaffold|noise, salience: 0..1, lod: full|gloss|omit}`.
  Drop in, fire via bridge run_role on 3-4 real spans (from the C-doc's own text), write results into
  `ctx.unit.meta.verdict` via psql. (C3.1/2)
- Stop-hook validator (lab): `Stop` hook → `validator.sh` → reads the draft (transcript tail) → checks rules from
  `rules.json` (data, C3.4): regex/heuristic first (time-estimate patterns: "\d+ (hours|days|weeks)", completion
  claims without "Verified/Observed") — optionally a run_role judge pass; violation → exit 2 with the reason
  (observe the model retry + correct). (C3.3)
## C4 · SLICE-CHAINS (backend)
- Edges: already in C1 schema. Chain = recursive closure over unit_edge from a seed unit (one CTE; both directions).
- Fork-per-chain: spawn = `claude -p` (or Agent tool) with a generated brief = the chain's units serialized
  (address-ordered); register the fork in the fabric (importer path proven) with meta {parent_session, chain_root}.
  Headless-verifiable part: brief generation from a real chain + the registration record. (C4.3)
- Cross-chain v0: SQL — two chains sharing a referenced unit / similar addresses → surface as a report. (C4.4)

## Order + commits
C1 (schema+verify, commit) → C2 (lab resolver, commit) → C3 (role+validator, commit) → C4 (chains, commit).
Each commit message names the criterion. Memory updated per slice. Anything discovered → C-doc scope.
