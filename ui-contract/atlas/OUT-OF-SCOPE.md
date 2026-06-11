---
type: contract-out-of-scope
captured: 2026-06-12
status: living — shared append-only; lanes ADD rows under their own heading, never rewrite others'
---

# OUT-OF-SCOPE — affordance-grain exclusions (never silent)

Feature-Atlas affordances deliberately NOT exposed as company capabilities — each with what it
would be, why it is out, what to do instead, and aliases (so the exclusion out-retrieves a
lookalike). Partial classes are expressible: an affordance can be out while siblings are in.

## F6 — Knowledge & memory
_No F6 affordance is fully out of scope._ Every CC-20 and CC-23 affordance the F6 lane touches
is contracted as either `building` (CC-23.2, CC-35.1 — real MCP search faces) or `planned`
(CC-20.1/.2/.3, CC-23.3/.4/.5 — data models contracted, company endpoint named-as-gap, all
F10.1 gap-adoption candidates). "Planned" is IN scope (a contracted gap with an adoption path),
NOT out of scope (a deliberate boundary). The genuinely-external endpoints behind some planned
bindings are recorded at ENDPOINT grain in INVENTORY-EXCLUSIONS.md, not here.

## F8 — Platform & admin
These F8 affordances are OUT-OF-LOCAL-SCOPE: they govern the HOST install or the Anthropic ORG, not
the company fabric (which drives one already-installed `claude -p` binary and never installs software,
administers the org, switches providers, or changes a data posture). Each is contracted as a navigable
op that routes to its native path — not a built capability and not a contracted-gap `planned` op. (The
F8 affordances that ARE in scope — CC-24.1, CC-24.2/.3/.4 (REOPENED — Tim's sole-operator steer:
the operator's OWN relogin/logout/setup-token, consent-gated R3 host-config acts, NOT a multi-user
boundary), CC-25.1/.2/.3, CC-33.1/.2/.3/.4, CC-35.1 — are contracted `building`/`planned` in their
entries, not here.) Distinction held per CONTRACT-FORMAT §4.2 / §1
atlas/: "planned" is IN scope (a contracted gap with an adoption path); these are OUT (a deliberate
boundary).

> REOPENING NOTE (2026-06-12, L-⑤-auto): CC-24.2/.3/.4 (relogin/logout/setup-token) were previously a
> row here. Tim's sole-operator steer reopened them — the operator is the only user and is trusted, so
> their OWN credential acts are ENABLED as consent-gated R3 ops (consent-not-lockdown; relogin reverses
> a logout, git-revert-equivalent). They are now contracted `building` in [[auth#op: auth.act]]. What
> REMAINS out of scope is proxying a DIFFERENT user's credential (the usage policy: third parties may
> not route through another user's plan creds) — expressed not as an absence-of-row but as the
> sole-operator scope of the reopened acts.

| affordance | what it would be | why out (reason) | what to do instead | aliases | decided-by | date |
|---|---|---|---|---|---|---|
| CC-01.1 / CC-02.1 | enumerate + drive Claude Code's interactive surfaces (TUI/Desktop/Web/IDE/Chrome) | the company drives EXACTLY ONE surface — headless `claude -p` (the supervisor subprocess); the interactive clients are human-launched and have no programmatic fabric face (a headless `-p` has no TUI). [[feedback-company-ui-disposable]] | drive the one company surface via [[session#op: session.create]]; the static surface set is in [[surfaces#Representation]] | "open desktop", "start the web app", "use the IDE extension", "interactive mode" | F8 lane (surfaces.md) | 2026-06-12 |
| CC-04.1 | read/set keybindings (`~/.claude/keybindings.json`) | keybindings govern the interactive TUI/Desktop the company does not drive; they are inert against a headless session | the data model is documented in [[surfaces#op: surfaces.get-keybindings]] for a config UI; rebinding is a host `/keybindings` action | "rebind keys", "keyboard shortcuts", "customize shortcuts" | F8 lane (surfaces.md) | 2026-06-12 |
| CC-28.1 | administer org managed policy / analytics / managed MCP | managed settings are delivered by an ORG ADMIN (console/MDM/file) and OUTRANK every settings scope; the company is a policy SUBJECT, not an administrator | inherit policy via the host; the model + the one inheritance path are in [[platform#op: platform.enterprise]] | "managed policy", "org settings", "admin console" | F8 lane (platform.md) | 2026-06-12 |
| CC-29.1 | select/switch the inference cloud provider | provider selection is the host env (`CLAUDE_CODE_USE_*`) + provider creds, the highest auth-precedence method; not a company op (the fabric INHERITS it transparently) | set the provider on the host/service env; see [[platform#op: platform.cloud-provider]] and [[auth#Identity]] | "Bedrock", "Vertex AI", "Foundry", "route inference to our cloud" | F8 lane (platform.md) | 2026-06-12 |
| CC-31.1 | set up Claude Code for a monorepo/large codebase (nested CLAUDE.md, sparse worktrees, per-package skills, dev containers) | these configure how a human's `claude` works in a big repo; the fabric spawns with an explicit `cwd` + inherits the project CLAUDE.md but owns none of these setup levers (LSP/code-intel is CC-16, a separate lane) | host/project setup, described in [[platform#op: platform.privacy]] | "monorepo setup", "large codebase", "dev container" | F8 lane (platform.md) | 2026-06-12 |
| CC-32.1 | configure data retention / telemetry / privacy posture | data retention + training behavior are the org's data agreement + the Anthropic data policy; telemetry is a host opt-in (`CLAUDE_CODE_ENABLE_TELEMETRY`) — not a company op. The company's OWN local-persistence boundary IS stated (not silent) | the org agreement + host telemetry config; the company-local boundary is in [[platform#op: platform.privacy]] | "data privacy", "zero data retention", "what data is collected", "telemetry" | F8 lane (platform.md) | 2026-06-12 |
| CC-34.1 | install / update the Claude Code binary; manage platform builds | the company drives an already-installed binary (`_find_claude()`); installing/updating is a host operator concern (native auto-update, brew/winget/npm, `claude install/update`) | the native install/update path, named in [[platform#op: platform.install]] | "install claude code", "update claude code", "claude version" | F8 lane (platform.md) | 2026-06-12 |
