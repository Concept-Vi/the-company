---
type: module-constitution
module: runtime/capability_handlers
build: capability-fabric
governs: ["runtime/capability_handlers/__init__.py", "runtime/capability_handlers/reduction/*.py"]
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
- `automation.py` (⑤, WIRED 2026-06-12 — L-⑤-auto) — the AUTOMATION family: `routines` (CC-21, R3 native-CLI intent + direct-read), `workflows` (CC-22, R1 /goal deliver-intent + R2 /loop wire-job + a link to the LIVE consult-fan), `cost` (CC-20, direct-read fold over agent_sessions.turn `usage`), `auth` (CC-24.1 reopened, direct-read redacted credential method). Wires its four fns onto HANDLERS on import; the MCP face (`mcp_face/tools/automation.py`) imports it (NOT `load_all`, to stay file-disjoint from ③④) and delegates. Proven by `tests/automation_acceptance.py` (73 checks, stubs).
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
  boundaries (CC-04 keybindings, CC-29 provider, CC-32 telemetry, CC-24.1 auth-read, CC-34 via
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
`tests/capability_handlers_acceptance.py` (runs once the faces exist).
