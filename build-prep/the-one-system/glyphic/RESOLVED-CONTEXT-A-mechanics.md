# A — Resolved-Context: the empirical mechanics (verified, 2026-07-02)

> Ground truth for the "dynamic context management" system (hooks + local judges resolve/inject/recompose an
> agent's context). What's PROVEN by experiment on THIS machine + the authoritative hook contracts. Marked
> Verified (ran it) / Doc (official contract) / Blocked (hit a real guard). Store target = LOCAL Supabase.

## Verified by experiment
- **V1 · UserPromptSubmit stdout INJECTS into the model's context.** A headless `claude -p` with a
  UserPromptSubmit hook echoing `INJECTED-CONTEXT-MARKER: … ZEBRA-77` → the model quoted the marker back
  verbatim. **This is the live turn-resolution channel, and it works today.** (exit 0, stdout → system-reminder.)
- **V2 · Sessions are addressable + resumable headless.** `claude -p --output-format json` returns `session_id`;
  the transcript lands at `~/.claude/projects/<cwd-slug>/<session_id>.jsonl`; `--resume <id>` continues it.
- **V3 · The transcript is a parentUuid TREE (fork-safe).** Parsed the live 0e68d462 jsonl: 6,315 nodes, 560
  leaves — a two-session accidental co-write produced real branches; any lineage is reconstructable to a tip.
  (So "history is an editable/addressable substrate" is literally true structurally.)

## Blocked — a real guard (needs Tim's call)
- **B1 · Editing a session .jsonl is BLOCKED by the auto-mode classifier** ("Session Transcript Tampering").
  Rewriting `~/.claude/projects/**/*.jsonl` in place is refused in auto mode — clears only on the user seeing
  the permission prompt (i.e. outside auto mode, with review). **Consequence:** direct in-place history
  mutation of a LIVE CLI session is not a quiet-automation path. The supported recomposition paths are the
  boundary ones below + the SDK (which owns its own messages array, no CLI transcript guard).

## Doc-confirmed contracts (official, cited)
- **Injection events (stdout exit 0 → context as a system-reminder):** `UserPromptSubmit`, `SessionStart`,
  and `additionalContext` on `PostToolUse`/`PostToolBatch`. These are the sanctioned "add resolved context" seams.
- **SessionStart `matcher:"compact"`** fires AFTER compaction (source ∈ startup|resume|clear|compact) → the
  clean way to **re-inject** resolved context that survives the built-in compaction. **This is the fix to the
  exact failure we hit** (compaction dropping the depth): a compact-matched SessionStart hook re-resolves and
  re-injects the true salient context.
- **PreCompact** — observe-only. CANNOT block or instruct the summarizer. (So steer via SessionStart:compact,
  not PreCompact. Corrects the earlier assumption that PreCompact could guide the summary.)
- **Every hook receives** `session_id`, `prompt_id`, `transcript_path`, `cwd`, `permission_mode`, `effort` +
  event-specifics (`prompt`, `tool_name`/`tool_input`, `source`, `compact_reason`).
- **Blocking/decision:** exit 2 = block (stderr → feedback); PreToolUse `permissionDecision: allow|deny|ask|defer`.
- **Config is LIVE-reloaded** (`~/.claude/settings.json` / `.claude/settings.json` / `.claude/rules/*.md` — file
  watcher, no restart). Rich event set beyond the basics: PostToolBatch, SubagentStart/Stop, InstructionsLoaded,
  FileChanged, ConfigChange, TaskCreated/Completed, PermissionDenied(`{retry:true}`), etc.
- Docs: code.claude.com/docs/en/{hooks,hooks-guide,sessions,headless}.md

## The store — LOCAL Supabase (verified up)
- Docker stack live: `supabase_studio` (:15423), `_rest`, `_realtime`, `_auth`, `_storage`, `_pg_meta`,
  `_edge_runtime`; **Postgres 17.6 on :15432** (pgvector). Kong gateway present (/ returns 404 = up, no root route).
- **The embedding session's `ledger.*` schema already lives here** (entry/run/embedding/symbol/path/edge/
  interpretation/…). So the context-ledger + vector recall ride the SAME local Postgres — convergence, not a new store.
- **pplx-2560 embedder @ :8007** + `run_role` schema-judges (0.72s) already proven = the match+judge layer.

## What this means for the architecture (the honest shape A→B carries)
1. **Turn-resolution (LIVE, works now):** UserPromptSubmit hook → bridge (embed the prompt → match the context-
   ledger/vector spaces → local judge returns a typed verdict) → **stdout the resolved context** → it enters the turn.
2. **Boundary-recomposition (supported path):** SessionStart:compact re-injects the resolved salient context after
   compaction — the depth-preserving fix. Full history *rewrite* of a live CLI session is guarded (B1) → do
   recomposition via (a) re-injection at boundaries, or (b) the **agent-SDK loop** where the Company owns the
   messages array outright (the no-limits path, already how the Company runs its own sessions).
3. **Store = local Supabase/Postgres** (the context-ledger: typed verdicts about spans — kind/state/salience/
   supersededness — + vector recall), beside `ledger.*`.
4. **The viewport/LOD idea holds** but is realised through *what the resolver injects* (semantic zoom = the
   resolver choosing full-text vs gloss vs omit per span), NOT by editing the raw transcript in place.
