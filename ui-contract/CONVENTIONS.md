---
type: contract-conventions
captured: 2026-06-12
status: living — updated in place (no-versioning law)
---

# CONVENTIONS — uniform vocabulary, envelopes, laws

## Uniform op verbs (closed — anything else is a resource or a named act)
**list · get · create · update · delete · act (named acts) · watch · search**

## Named-act registry (append-only — one line per act; lanes ADD lines, never rewrite)
- `post` — on `session`: append a durable routed message intent (deliver/wake/consult/auto/queue).
- `inject` — on `session`: direct synchronous push of one turn into a SUPERVISED session (no mailbox).
- `interrupt` — on `session`: stop the in-flight turn of a busy supervised session.
- `stop` — on `session`: tear down supervision of one session (subprocess killed; record stays, closed).
- `export` — on `transcript`: fire/arm the jsonl→markdown export job.

## The uniform error envelope (target shape) + per-face carriers — FIELD-REALITY HONESTY
Target (CONTRACT-FORMAT §9.5, a code-side obligation): every face emits
`{error: {code, message, teach, details?, retryable}}`.

**Reality as of 2026-06-12 — the envelope is NOT yet implemented on any face.** What each
face actually emits today (every refusal DOES carry teach-text; structured codes do not exist
in the wire shapes yet — error `code:` values in this corpus are contract-assigned names,
machine-emission pending):
| face | carrier today |
|---|---|
| supervisor-http | HTTP status (400/404/409/429/500) + JSON `{"error": "<teaching text>"}` |
| mcp-company | MCP tool error (raised ValueError → SDK error result), message IS the teaching text |
| cli-local | stderr teaching text + exit code 1 (supervisor-down teaches `company up session-supervisor`) |
| bridge-http | (no fabric routes yet — planned) |

HTTP status mapping used by the supervisor: 400 malformed body/missing field · 404 unknown
path/session · 409 state conflict (busy/closed/not-busy) · 429 over the concurrency cap ·
500 internal (fail-loud, never silent).

## Cursor / pagination law
Reads over ordered logs are seq-cursor shaped: pass `since` (exclusive; `-1` = everything),
results come OLDEST-first, `limit` keeps the FIRST N after the cursor (pagination never
skips), and the response's `next_since` (or the last row's `seq`) is your next call's
`since`. Two cursor disciplines exist and are both contracted: CLIENT-HELD (you keep
`next_since`; re-reading is safe, nothing is consumed destructively — the inbox read) and
DURABLE PER-CONSUMER REFS (`agent-mail-cursor://<consumer>` — monotonic, regression refused;
the supervisor's own mailbox cursor is a byte-offset ref `agent_sessions/cursor:supervisor`,
an internal detail stated for honesty, not a consumer surface).

## Address grammar
- `session://<id>` — LIVE scheme (in `contracts/address.py` SCHEMES): a Claude Code session.
  `<id>` is canonically the claude session uuid; the supervisor also accepts its own local
  handles (`as-<8 hex>`) minted before init names the uuid.
- `cas://<hash>` — content-addressed body store (mail bodies ride it; reads resolve it for you).
- PLANNED, not in code yet (CONTRACT-FORMAT §9.7 obligation): `msg://`, `thread://`,
  `consumer://`. Today mail ids are plain strings `mail-<seq>` and thread ids are plain
  strings (defaulting to the founding mail id) — they are NOT dereferenceable addresses, and
  no entry in this corpus claims them as schemes.

## Purpose-free vocabulary (V5 seed list — extendable, never shrinkable)
Banned in Description/Semantics prose: "the user wants", "the UI should", "button", "panel",
"screen", "click", "frontend", "page". `tasks:`/`alias:` fields are EXEMPT (the deliberate
retrieval bridge to consumer vocabulary). Escapes need an inline `lint-ok:` justification.

## Journey ambiguity classes (V19 — each MUST have a journey)
- "history vs live vs messages": a transcript is the past, a watch is the present, mail is
  addressed communication — `journeys/message-and-read-reply.md` carries the disambiguation.
- "session state management" (F2): rewind/restore REVERTS, targeted-summarize COMPRESSES one
  side, compact COMPRESSES the whole conversation, clear DISCARDS-and-parks, fork COPIES-and-
  preserves — five overlapping mechanisms, five distinct meanings. `journeys/manage-session-state.md`
  carries the chooser (intent -> mechanism) and the two deciding axes (touches-files? preserves-original?).
- `remember` — on `claude-memory`: save a learning to auto-memory, or (on request) append an instruction to CLAUDE.md. (planned; today a Claude Code conversational behavior, not a company API)
- `forget` — on `claude-memory`: trim/delete a stale memory entry. (planned; today via /memory or a direct edit)
- `cap-budget` — on `cost-usage`: set the headless `--max-budget-usd` ceiling that stops a session when exceeded. (planned; a Claude Code headless flag the supervisor could thread through session.create)

## Named-act registry — F3 additions (Execution & control; append-only)
Lane F3 uses the uniform verb `act` with an internal `act:` discriminator on control/config
resources whose every operation is a steer rather than a CRUD. The discriminator VALUES are the
named acts (registered here for V2 closure); ALL are `planned` against the company today except where
re-exposed by an F1 op (noted):
- `set-at-spawn` / `set-mode` — on `permission`: launch under a chosen mode+rules / change a live
  session's mode mid-session (planned — the spawn carries no permission param; mid-session set is the
  SDK setPermissionMode analogue).
- `set-at-spawn` / `set-model` / `set-effort` — on `model`: choose model/effort/thinking/fallback at
  launch / switch model or effort mid-session (planned — the spawn carries no --model/--effort).
- `create-team` / `spawn-teammate` / `assign-task` / `message-teammate` / `shutdown-teammate` /
  `cleanup-team` — on `agent-team`: the native agent-team control verbs (planned — no native-team
  company face; the LIVE parallel path is `session.post` verb=consult).
- `turn` / `interrupt` / `set-output` — on `headless-control`: write a user turn / interrupt the
  in-flight turn / select output-format+schema. `turn` and `interrupt` are RE-EXPOSED today via
  [[session#op: session.inject]] / [[session#op: session.interrupt]] (building); `set-output` is
  planned (the spawn hardcodes --output-format stream-json).

## Purpose-free vocabulary — F3 note (lint-ok carve-outs)
`ultrathink`/`ultracode` are Claude Code reserved keywords (a prompt keyword and an effort setting),
NOT UI directives — they appear in F3 prose with inline `lint-ok:` where the V5 seed list might
otherwise flag them. The mode/effort enum VALUES (plan/acceptEdits/etc.) are Claude Code identifiers,
not the banned UI words.

## Named-act registry — F7 additions (Reach: voice / remote / code-intel / computer-use / code-review; append-only)
Lane F7 uses the uniform verb `act` with an internal `act:` discriminator. The discriminator VALUES
are the named acts (registered here for V2 closure). Voice acts are `building` (real bridge routes);
all others are `planned` (native/hosted surfaces the company exposes no face for, gap named per op):
- `switch` / `load` / `unload` / `toggle` — on `voice`: set the active engine/voice/persona / load a
  GPU ear or TTS engine (VRAM-budgeted via the shared resource-manager) / unload (cgroup stop) /
  toggle per-mode voice on-off. ALL `building` — real bridge routes (/api/voice/switch,
  /api/voice/{load,unload}); fail-loud on unknown id or no-VRAM-fit, NEVER a silent kokoro fallback.
- `remote-control` / `deep-link` — on `remote`: start native `--remote-control` / open a `claude://`
  deep link (planned — Anthropic-hosted relay, NOT bridged; the company's mobile path is the tailnet PWA).
- `definition` / `references` / `hover` / `document-symbols` / `workspace-symbol` / `implementations`
  / `call-hierarchy` / `diagnostics` — on `code-intel`: the native LSP tool's navigation + post-edit
  diagnostics (planned — the LSP tool runs in-session; no company endpoint).
- `web-fetch` / `web-search` / `browser` / `computer` — on `computer-use`: WebFetch/WebSearch (native
  session tools, NOT in the fabric grant) / Claude-in-Chrome browser automation (beta, NOT WSL) /
  API computer-use (beta header) (all planned — no company face; default fabric grant is mcp__company only).
- `review-local` / `security-review-local` / `review-pr` — on `code-review`: /code-review &
  /security-review (TUI), managed GitHub Code Review, or a claude -p CI review (planned — no company
  review face; the CI claude -p path is buildable on the fabric but un-packaged).

## Purpose-free vocabulary — F7 note (lint-ok carve-outs)
`/code-review`, `/security-review`, `/voice`, `/remote-control`, `/mobile` are Claude Code reserved
slash-command names (and `claude://` is the native deep-link scheme), NOT UI directives — they appear
in F7 prose where the V5 seed list ("page"/"screen"/"click") might otherwise flag adjacent words;
the slash-command and scheme identifiers are Claude Code surface names, carried with inline `lint-ok:`
where needed. "push-to-talk"/"tap-to-record" are native voice-dictation mode names (voice-dictation.md),
not UI directives. Browser/Chrome/computer-use prose names native tool actions (open tab, click, type,
screenshot) — these describe the NATIVE tool's documented behavior, lint-ok as capability description,
never a UI instruction.

## Named-act registry — F4 additions (Extension fabric; append-only)
Lane F4 uses the uniform verb `act` with an internal `act:` discriminator on the extension-fabric
control resources (hooks/mcp-servers/extensions/output-style), whose write operations are steers over
native Claude Code config rather than CRUD on a fabric object. ALL are `planned` against the company
(no bridge route exists — every binding names the gap and rides the `claude-cli`/`claude-tui`
non-fabric transports). The discriminator VALUES, registered here for V2 closure:
- `add-hook` / `update-hook` / `remove-hook` / `set-flag` — on `hooks`: add/update/remove a hook
  handler in a chosen settings scope / flip `disableAllHooks` (planned — no settings-writer endpoint).
- `add` / `add-json` / `remove` / `authenticate` / `import-desktop` / `reset-project-choices` — on
  `mcp-servers`: the native `claude mcp …` management verbs + the `/mcp` OAuth flow (planned — no
  config-writer or auth bridge).
- `create-skill` / `update-skill` / `delete-skill` / `scaffold-plugin` / `package-plugin` /
  `add-marketplace` / `install-plugin` / `uninstall-plugin` / `enable-plugin` / `disable-plugin` / `reload-plugins`
  — on `extensions`: skill authoring + the `/plugin` + `claude plugin` management
  surface (planned — no authoring or install bridge; the company's /api/cognition/create_skill is a
  COMPOSITION skill, unrelated).
- `set-style` / `create-style` / `delete-style` / `set-statusline` / `clear-statusline` — on
  `output-style`: the `/config` output-style picker + `/statusline` generator (planned — no
  presentation-config writer; /api/presentation-pref is the company UI's own altitude preference,
  unrelated).

## Purpose-free vocabulary — F4 note (lint-ok carve-outs)
F4 prose names Claude Code reserved identifiers that the V5 seed list might otherwise flag: the hook
EVENT names (`MessageDisplay`, `PostToolBatch`, etc.) and the output-style names (`Proactive`,
`Explanatory`, `Learning`) are Claude Code identifiers, not UI directives. The word "panel" appears
ONLY inside quoted native-surface names (the `/mcp` panel) where it is the product's own term, carried
verbatim from the docs — `lint-ok:` because it names a Claude Code surface, not a company UI element.

## Named-act registry — F1/F2 resource-control additions (native-surface steers; append-only)
These lanes use the uniform verb `act` with an internal `act:` discriminator on resources whose
write operations are steers over native Claude Code surfaces (auth, CI, git, routines, settings,
diagnostics, workflows) rather than CRUD on a fabric object. The discriminator VALUES are the named
acts, registered here for V2 closure. ALL are `planned` against the company today (no bridge route
exists; every binding names the gap and rides the native `cli-local`/`tui-interactive`/`supervisor-http`
transports) except where a spawn-extension is noted. Definitions restate the owning op's documented
native behavior (each op fence cites its Claude Code doc URL + runtime line).

### auth (credential steer — REOPENED as buildable R3 host-config acts; Tim's sole-operator steer)
The arch's original ruling treated these as host actions with no company op (absence-of-row =
boundary). Tim's sole-operator steer OVERRIDES that: the operator is the only user and is trusted, so
these are ENABLED as consent-gated R3 ops on `auto.auth` op="act" (`building`) — NEVER locked out,
NEVER a multi-user auth wall; consent-not-lockdown with re-login / git-revert as the backstop. The
company face (`mcp_face/tools/automation.py` auth tool + the `auto.auth` handler) builds the argv via
the `auto.auth:<act>` cli_allowlist row; the config_writer R3 service shells it (the floor — the face
never shells). Grounded in authentication.md / troubleshoot-install.md:
- `relogin` — on `auth`: re-authenticate / switch the active subscription/Console account via
  `claude auth login` (OAuth; reads the pasted code from stdin on WSL/SSH/containers — the operator's
  path). exec-tier. Takes effect on the NEXT session start, not mid-session.
- `logout` — on `auth`: clear / switch the stored credential via `claude auth logout`. write-tier;
  reversed by `relogin` (the git-revert-equivalent backstop for a host credential).
- `setup-token` — on `auth`: mint a one-year inference-scoped `CLAUDE_CODE_OAUTH_TOKEN` via
  `claude setup-token` (prints the token to stdout, saves nothing; cannot establish Remote Control).
  exec-tier, `returns_secret`: the config_writer surfaces the printed token to the CONSENTING OPERATOR
  terminal ONLY; the handler returns NO token field (the redaction floor §5.2 C3 honoured by NOT
  returning the secret, not by post-hoc stripping).

### ci (in-CI invocation — direction:inbound; the CI provider drives, no company face participates)
- `mention` — on `ci`: a `@claude` mention in a GitHub/GitLab issue/PR/MR comment (interactive mode,
  auto-detected from comment events; trigger phrase configurable, defaults to `@claude`).
- `event` — on `ci`: a CI event (pull_request/push/`schedule:`/manual) matching the workflow trigger,
  driving an automation-mode run with a fixed `prompt:` on the CI provider's runner.

### diagnostics (single-session diagnostic steer — native levers the headless spawn omits)
- `doctor` — on `diagnostics`: run `/doctor` (install/settings/MCP/context health). Interactive-host only;
  no headless per-session form exists — a per-session health object would be net-new company work.
- `set-debug` — on `diagnostics`: spawn with `--debug <filter>` (e.g. `api,hooks`) for category debug logging
  (spawn threads `--verbose` but no `--debug` today).
- `safe-mode` — on `diagnostics`: spawn under `--safe-mode`/`--bare` to isolate a problem (note: `--bare`
  skips the MCP/keychain/CLAUDE.md the fabric depends on — isolation only, would break mcp__company access).

### git (everyday git steer — native Bash-tool git under the session's permission posture)
- `commit` — on `git`: stage + commit with a generated message; Claude emits `git add`/`git commit` via the
  Bash tool under [[permission]]; the sha rides the turn transcript, not a structured company field.
- `open-pr` — on `git`: create a pull request (`gh pr create` via Bash); needs the GitHub CLI/App in the session env.
- `resume-from-pr` — on `git`: resume the session linked to a PR via the native `claude --from-pr <number|url>`
  launch flag (the company spawn carries no `--from-pr` passthrough).
- `rebase` — on `git`: rebase/merge/cherry-pick a branch via plain `git` through the Bash tool; none company-wrapped.

### git worktree (isolation steer — `git.worktree` op; parallel-session/subagent file-collision isolation)
- `create` / `enter` / `subagent-isolate` — on `git`: create an isolated worktree (`claude --worktree <name>`/`-w`,
  default `.claude/worktrees/<name>/` on branch `worktree-<name>`, base = `worktree.baseRef`) / switch into one
  (the `EnterWorktree` tool) / isolate subagents via `isolation: worktree` frontmatter (each gets a temp worktree,
  auto-removed if it finishes without changes). `remove` reuses the F4 `remove` act. The company drives none, though
  it IS the company's own self-build isolation mechanism internally.

### routines (control surface for an existing routine — native claude.ai/code/routines + session-tool acts)
- `run-now` — on `routines`: run a cloud routine immediately without waiting for the schedule (`/schedule run`).
- `pause` — on `routines`: pause/resume a routine's schedule (the Repeats toggle on the routine detail page).
- `one-off` — on `routines`: schedule a single non-repeating fire that auto-disables to **Ran** after firing.
- `cancel-session-task` — on `routines`: cancel a session-scoped scheduled task by its 8-char id via the native
  `CronDelete` tool (`Esc` clears a pending `/loop` wakeup; `CLAUDE_CODE_DISABLE_CRON=1` disables the scheduler).

### settings (per-session configuration steer — native `--settings`/`--add-dir`/`env` levers the spawn omits)
- `set-env` — on `settings`: set an environment variable for a session (planned spawn-extension: an `env` map ->
  per-process environment; the spawn carries no env override today, inheriting the service account's settings).
- `add-dirs` — on `settings`: grant a session access to extra directories (planned: an `add_dirs` array -> repeated
  `--add-dir`). `set-at-spawn` (thread a settings file/inline JSON at spawn) reuses the F3 `set-at-spawn` act.

### workflows (single steer over the native keep-going modes — none wired through the company)
- `set-goal` — on `workflows`: set a `/goal <condition>` so a session keeps working toward a verifiable end
  state without per-step prompting (evaluator = the configured small-fast model, default Haiku; needs hooks enabled).
- `goal-status` — on `workflows`: check the goal status (`/goal` alone), surfacing the evaluator's short reason.
- `clear-goal` — on `workflows`: clear/stop the goal (`/goal clear|stop|off|reset|none|cancel`).
- `loop` — on `workflows`: start an interval keep-going loop (`/loop <interval> <prompt>`, cron-backed, session-scoped;
  runs until `Esc`/expiry). The live MULTI-session capability is NOT here — it is [[session#op: session.post]] verb=consult.
