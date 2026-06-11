---
type: module-constitution
module: runtime/capability_handlers
build: capability-fabric
governs: ["runtime/capability_handlers/__init__.py", "runtime/capability_handlers/reduction/*.py",
          "runtime/capability_handlers/r3.py", "runtime/capability_handlers/config_authoring.py",
          "runtime/capability_handlers/dev_bridges.py", "runtime/capability_handlers/automation.py",
          "mcp_face/tools/config_authoring.py", "mcp_face/tools/dev_bridges.py", "mcp_face/tools/automation.py"]
relates-to: ["[[MAP]]", "[[Company State]]", "runtime/AGENTS.md",
             "ui-contract/CONTRACT-FORMAT.md", "ui-contract/CONVENTIONS.md"]
status: living
---

# capability_handlers — the DRY handler layer for ③④⑤ (Capability Fabric)

The backend that flips families ③ CONFIG-AUTHORING · ④ DEV-BRIDGES · ⑤ AUTOMATION from `planned`
toward `live` in the UI-Contract corpus. Spec: build-prep "Capability Fabric — 345 Architecture.md".

## The one picture

```
  MCP face  (mcp_face/tools/<resource>.py)  ─┐
  bridge    (runtime/bridge.py  path == arms) ─┤── BOTH call the SAME ──▶  HANDLERS[key].fn(suite, op, **p)
                                               │   (DRY: one handler, two faces, drift-tested)
                                               ▼
                              runtime/capability_handlers/  ── pure fns over Suite
                                 each handler DECLARES its RAIL + reads a reduction registry
                                               │
                 ┌─────────────────────────────┼───────────────────────────────┐
                 ▼            ▼                 ▼                ▼               ▼
            direct-read      R3              R1            R1-prime            R2
            (reads,      config_writer   supervisor     wider-allowlist    headless wire
            resolvers)   (.claude, mcp/  deliver/inject  spawn (LSP/web/    claude -p via
                         plugin, git/gh)  (goal steer)    computer; PROSE)   /api/resolve
```

## What lives here

- `__init__.py` — the `HANDLERS` registry `{key → Handler(fn, rail, readonly, summary)}` + the closed
  `RAILS` vocabulary + `register_handler` / `get` / `rail_of` / `keys_for_family` / `load_all`. The
  complete ③④⑤ §4 inventory is PRE-DECLARED (18 keys); a face+handler lane WIRES its real fn onto a
  declared key, it does not add keys. Until wired, the handler's `.fn` is an honest `building` stub
  that raises a teaching `NotImplementedError` (no silent no-op, no green-paint) and `.built` is False.
- `reduction/` — the SERVICE-SIDE reduction registries (so the faces stay resource-shaped, the
  primitives live here): `config_targets` (③ .claude write targets + consent tier), `cli_allowlist`
  (R3 native-CLI argv templates), `session_capabilities` (R1-prime in-session caps — liveness:stream,
  no typed return_shape), `host_reads` (declarative-direct redacted host reads).
- `r3.py` (the R3 CLIENT — added with L-③-config) — the socket-thin client the ③ (+ ④ git/ci, ⑤ routines) handlers call to reach the config_writer SERVICE without crossing the floor themselves. TWO modes, one law: IN-PROCESS (`r3.bind(writer)` — the bridge binds one ConfigWriter over the live store at startup; the unit tests bind a scratch writer over an isolated tmp store + scratch HOME) OR HTTP (POST to 127.0.0.1:$COMPANY_CONFIG_WRITER_PORT — the same /read /write /cli /git /consent routes) when nothing is bound. A down service raises `R3Unavailable` (teaching, names `company up config-writer`) — NO silent fallback. Either mode, the config_writer stays the SOLE .claude writer.
- `config_authoring.py` (③, WIRED 2026-06-12 — L-③-config) — the CONFIG-AUTHORING family: `hooks` (CC-12, R3 settings hook blocks — DANGEROUS command → consent beat), `mcp_servers` (CC-11, R3 `claude mcp …` — stdio spec EXEC-tier), `output_style` (CC-26, R3 file authoring — non-dangerous; set-style/statusline/delete are named building gaps), `slash_commands` (CC-03, R3 command .md — DANGEROUS prompt body), `extensions` (CC-13 + CC-34 reopened, R3 SKILL.md authoring + `claude plugin …` + the native `claude update`/`install` updater — exec-tier), `patterns` (CC-27, direct-read PURE chooser resolver — documentation-as-data, no file/R3), plus the REOPENED config-face capabilities `keybindings` (CC-04, R3 ~/.claude/keybindings.json — USER-scope only, refuses non-user loud, merge-by-context + null-unbind, reserved-shortcut refusal), `telemetry` (CC-32, R3 settings env data-posture flags — closed flag set), `provider` (CC-29, R3 settings env CLAUDE_CODE_USE_*/ANTHROPIC_* — closed key set). All write through the `r3` client to the config_writer; reads are face-direct via `r3.read`. Wires its nine fns onto HANDLERS on import; the MCP face (`mcp_face/tools/config_authoring.py`) calls `load_all()` + delegates (DRY: one handler, two faces — byte-identical dict). FOUNDATION FIX this lane closed: config_targets `config.keybindings` resolved to settings.json (would have clobbered it); now pinned to ~/.claude/keybindings.json (user-only `scope_files`), and config_writer grew a `keybindings` kind (JSON object, merge `bindings` by context). Proven by `tests/config_authoring_acceptance.py` (46 checks by USE on a scratch tree — consent beats, refusals, redaction, the injection floor, DRY delegation). NEEDED-ARMS reported to the Wire (declared, NOT built — bridge.py is Wire-phase-owned): the `/api/config/*` literal arms below.
- `automation.py` (⑤, WIRED 2026-06-12 — L-⑤-auto) — the AUTOMATION family: `routines` (CC-21, R3 native-CLI intent + direct-read), `workflows` (CC-22, R1 /goal deliver-intent + R2 /loop wire-job + a link to the LIVE consult-fan), `cost` (CC-20, direct-read fold over agent_sessions.turn `usage`), `auth` (CC-24 reopened — op=get direct-read redacted credential method + op=act on R3 for the REOPENED host-config credential acts relogin/logout/setup-token, Tim's sole-operator steer: consent-not-lockdown, never locked out; the `auto.auth:<act>` cli_allowlist rows render the native `claude auth login`/`logout`/`setup-token` argv; setup-token carries returns_secret — its printed token reaches the consenting operator terminal ONLY, never folded into the result). Wires its four fns onto HANDLERS on import; the MCP face (`mcp_face/tools/automation.py`) imports it (NOT `load_all`, to stay file-disjoint from ③④) and delegates. Proven by `tests/automation_acceptance.py` (90 checks, stubs).
- `dev_bridges.py` (④, WIRED 2026-06-12 — L-④-dev) — the DEV-BRIDGES family: `git` (CC-06, R3 structured git/gh via the config_writer — sha/exit, NOT prose), `code_intel` (CC-16, R1-prime in-session LSP — builds a bridge-session spawn intent; PROSE result, liveness:stream, NO return_shape), `computer_use` (CC-17, R1-prime web-fetch/web-search intent; browser/computer REFUSED-LOUD as not-WSL/macOS-interactive host boundaries — never green-painted), `code_review` (CC-19, R2 — writes a wire-job intent + job-id + watch cursor behind /api/resolve; never spawns), `ci` (CC-30, R3 — scaffold a .github/workflows file write + reads; mention/event inbound = no op, boundary). Wires its five fns onto HANDLERS on import; the MCP face (`mcp_face/tools/dev_bridges.py`) calls `load_all()` + delegates (DRY: one handler, two faces — byte-identical dict). Adds the CC-34 native-updater rows (`claude update`/`claude install`) to `cli_allowlist` under config.extensions. Proven by `tests/dev_bridges_acceptance.py` (48 checks, stubs — incl. argv injection-resistance, the host-boundary refusals, the R1-prime/R2 intent shapes, and the DRY delegation). NEEDED-ARM reported to the Wire: a config_writer `/ci-scaffold` generic-file-write for the .github/workflows root.

## Laws this module encodes

- **Every handler declares its rail** (§3.2): the maintainer must name the executor — you cannot add a
  capability without it (AI-path-of-least-resistance). `readonly` is True IFF the rail is `direct-read`;
  the `Handler` ctor fails loud on an incoherent declaration.
- **The face never executes** (§1.2): a handler for a write/act builds an intent/job/argv and routes it;
  a sanctioned SERVICE (config_writer R3 · supervisor R1/R1-prime · wire R2) acts. The handler itself
  shells/spawns nothing on the dangerous rails.
- **The floor is a property of the registries** (§5): the reduction registries carry the allowlist (the
  exec boundary), the content/consent tier (the dangerous-payload gate), and the redaction invariant.
- **Sole-operator floor** (Tim's steer): the operator is the ONLY user and is trusted. Dangerous
  capabilities (native-CLI exec, computer-use, .claude writes, plugin install) are ENABLED, gated by a
  CONSENT BEAT + git-revert backstop — NEVER locked out, NEVER a multi-user auth wall. The reopened
  boundaries (CC-04 keybindings, CC-29 provider, CC-32 telemetry, CC-24 auth read+acts (relogin/logout/setup-token, R3 consent-gated), CC-34 via
  extensions) are buildable config-face capabilities, IN scope. Genuinely-inert classes (CC-01/02 TUI,
  CC-28 org-admin, CC-31 monorepo) stay out (absence-of-row = boundary).

## Adding capability #N (the maintainer path)

1. Add a `HANDLERS` row in `__init__.py`: `(key, rail, readonly, summary)` — the rail DECLARES the executor.
2. Add the matching reduction row(s) (a `.claude` target / an argv template / an R1-prime cap / a host read).
3. In the family face+handler lane, write the pure `fn(suite, op, **p)` and `register_handler(key, fn)`.
4. Add the literal bridge `path ==` arm + the MCP op (both delegate to the SAME handler — DRY).

## Verify

`./.venv/bin/python tests/capability_handlers_registry_acceptance.py` — the foundation teeth (rail
validity, readonly coherence, the §4+reopened inventory, the registration seam + honest stub, ctor
fail-loud, the advisory cross-grain bridge). The HARD one-handler-two-faces drift test is
`tests/capability_handlers_acceptance.py` — BUILT + green (43 checks, 2026-06-12, L-FOUND-DRY-test):
every HANDLERS key wrapped by exactly ONE MCP face tool (both directions), the face delegates the
byte-identical OUTCOME to the handler (a returned dict OR the SAME fail-loud error — proving
delegation regardless of rail availability), and the bridge half is asserted HONESTLY pending (zero
`/api/{config,dev,auto}/*` arms exist — Wire owns bridge.py; the join flips on when the Wire lands
the literal arms, never green-painted before).


## NEEDED-ARMS for the Wire phase (bridge.py literal `path ==` arms — declared here, NOT built by these lanes)

bridge.py is Wire-phase-owned (the lanes do NOT edit it). Each arm dispatches a literal route to the
SAME handler the MCP face calls (DRY at the handler, literal at the dispatch — the drift test stays
intact, §3.3). The Wire appends these to the do_GET/do_POST chain + `BRIDGE_ROUTES`:

### ③ CONFIG-AUTHORING (`/api/config/*` → `HANDLERS["config.*"].fn(self.suite, **body)`)
- `GET  /api/config/hooks`        + `POST /api/config/hooks`        → `config.hooks`        (op=list/get | act)
- `GET  /api/config/mcp-servers`  + `POST /api/config/mcp-servers`  → `config.mcp_servers`  (op=list/get | act)
- `GET  /api/config/output-style` + `POST /api/config/output-style` → `config.output_style` (op=list/get | act)
- `GET  /api/config/commands`     + `POST /api/config/commands`     → `config.slash_commands`(op=list/get | act)
- `GET  /api/config/plugins`      + `POST /api/config/plugins`      → `config.extensions`   (op=list/get | act, incl. CC-34 update-native/install-native)
- `GET  /api/config/patterns`     → `config.patterns` (op=resolve/describe — pure read, no POST)
- `GET  /api/config/keybindings`  + `POST /api/config/keybindings`  → `config.keybindings`  (CC-04 reopened; op=list/get | act)
- `GET  /api/config/telemetry`    + `POST /api/config/telemetry`    → `config.telemetry`    (CC-32 reopened; op=list/get | act=set-flag)
- `GET  /api/config/provider`     + `POST /api/config/provider`     → `config.provider`     (CC-29 reopened; op=list/get | act=set-provider)

The bridge process must `r3.bind(ConfigWriter(...))` (in-process, the live store) OR leave it unbound to
proxy the config_writer service over HTTP — either is the floor (config_writer is the sole writer). The
async/consequence bridge arms for ④ (R1-prime code-intel/computer-use receipts, R2 code-review job) and
⑤ are declared in those lanes' reports.

### ④ DEV-BRIDGES (`/api/dev/*` → `HANDLERS["dev.*"].fn`)
- `GET /api/dev/git`         + `POST /api/dev/git`         → `dev.git`         (op=list/get reads · act{commit/open-pr/rebase/worktree-*})
- `POST /api/dev/code-intel`                               → `dev.code_intel`  (op=act → R1-prime receipt+watch)
- `POST /api/dev/computer-use`                             → `dev.computer_use`(op=act → R1-prime receipt+watch; browser/computer refuse-loud)
- `GET /api/dev/code-review` + `POST /api/dev/code-review` → `dev.code_review` (op=list/get · act → R2 job)
- `GET /api/dev/ci`          + `POST /api/dev/ci`          → `dev.ci`          (op=list/get · act=scaffold)

### ⑤ AUTOMATION (`/api/auto/*` → `HANDLERS["auto.*"].fn`)
- `GET /api/auto/routines`  + `POST /api/auto/routines`  → `auto.routines`  (op=list/get · act{run-now/pause/one-off/cancel-session-task} R3)
- `GET /api/auto/workflows` + `POST /api/auto/workflows` → `auto.workflows` (op=list/get · act{set-goal/goal-status/clear-goal} R1 · act=loop R2)
- `GET /api/auto/cost`                                   → `auto.cost`      (op=read — direct-read fold, no POST)
- `GET /api/auto/auth`      + `POST /api/auto/auth`      → `auto.auth`      (op=get redacted read · op=act{relogin/logout/setup-token} R3 consent-gated — CC-24 REOPENED)

The ⑤ async/consequence acts return a receipt (intent/job + watch cursor + consent path), never a
typed result — the bridge arm forwards the handler dict verbatim (DRY). The operator-vantage seam for
the consequential R3/R1/R2 writes rides the existing `/api/resolve` consent precedent (§5.3); a cold
agent may PROPOSE, the operator confirms.
