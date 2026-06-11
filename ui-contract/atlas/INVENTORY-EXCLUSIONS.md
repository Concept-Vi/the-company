---
type: contract-inventory-exclusions
captured: 2026-06-12
status: living — shared append-only; lanes ADD rows under their own heading, never rewrite others'
---

# INVENTORY-EXCLUSIONS — endpoint-grain exclusions (never silent)

Live or referenced endpoints deliberately NOT contracted as company faces — each with a reason,
so the reality join (V22) never phantom-fails on a route the company was never going to own and
the disposable harness's routes never count as gaps. ENDPOINT grain (distinct from
OUT-OF-SCOPE.md's affordance grain).

## F6 — Knowledge & memory
| endpoint | transport | reason | decided-by | date |
|---|---|---|---|---|
| `api.anthropic.com /v1/organizations/usage_report/messages` (+ `/organizations/me`, the Analytics API) | anthropic-admin-api | EXTERNAL Anthropic org API, requires an Admin key; the company does not proxy it today. `cost-usage.get`'s binding on it is `planned` and EXTERNAL, not a company route — excluded from the company reality join so it cannot phantom-fail | F6 lane (cost-usage.md INVENTORY note) | 2026-06-12 |
| Claude Code built-in slash commands `/memory`, `/usage`, `/cost` | cli-local (built-in) | these are Claude Code's OWN interactive commands, not `company …` routes; they are the interim honest paths the F6 entries cite, never company endpoints. Excluded so the company CLI inventory does not claim them | F6 lane (claude-memory.md / cost-usage.md) | 2026-06-12 |
| substrate-mcp tools (`search_semantic`, `list_vaults`, `get_status`, `get_by_address`, …) | substrate-mcp | EXTERNAL MCP server (obsidian-overlord repo) wired into the session; its tools are REAL and used (CC-23.2/CC-35.1 `building`), but they are not company-owned code, so they are inventoried against the external server's tool registry, not the company `OPS`-constant reality join | F6 lane (TRANSPORTS substrate-mcp) | 2026-06-12 |

## F8 — Platform & admin
Host/org/external endpoints the F8 entries reference but that are NOT company faces — each reasoned so
the reality join (V22) never phantom-fails on a route the company was never going to own. ENDPOINT
grain (distinct from OUT-OF-SCOPE.md's affordance grain).

| endpoint | transport | reason | decided-by | date |
|---|---|---|---|---|
| Claude Code built-in interactive commands `/login`, `/logout`, `/status`, `/doctor`, `/config`, `/keybindings`, `/bug`, `/feedback` | cli-local (built-in) + tui-interactive | these are Claude Code's OWN interactive/host commands, not `company …` routes; they are the honest interim paths the F8 entries cite ([[auth]], [[diagnostics]], [[surfaces]], [[settings]]), never company endpoints. Excluded so the company CLI inventory does not claim them | F8 lane (auth.md / diagnostics.md / surfaces.md / settings.md) | 2026-06-12 |
| `claude auth` · `claude setup-token` · `claude install [version]` · `claude update` / `claude upgrade` · `claude doctor` (host CLI subcommands) | cli-local (built-in) | host operator commands that manage credentials and the binary itself; the company drives an already-installed binary and never installs/updates/re-credentials it. Cited by [[auth#op: auth.act]], [[platform#op: platform.install]] as native paths; excluded from the company CLI reality join | F8 lane (auth.md / platform.md) | 2026-06-12 |
| Cloud-provider inference endpoints (AWS Bedrock, Google Vertex AI, Microsoft Foundry) | host env (`CLAUDE_CODE_USE_*`) -> external provider | EXTERNAL provider APIs reached by Claude Code directly when the host env selects a provider; the company neither selects nor proxies them. A fabric session INHERITS provider routing transparently. Cited by [[platform#op: platform.cloud-provider]]; excluded so the reality join cannot phantom-fail on an endpoint the company was never going to own | F8 lane (platform.md) | 2026-06-12 |
| Org managed-policy delivery surfaces: Claude admin console (server-managed), MDM (macOS `com.anthropic.claudecode` plist / Windows `HKLM\SOFTWARE\Policies\ClaudeCode`), file-based (`/etc/claude-code/managed-settings.json` + `managed-settings.d/`), `managed-mcp.json` | org-admin / host OS policy | org/OS-level configuration delivery that OUTRANKS settings.json and is administered by an org admin, not the company (the fabric is a policy subject). Cited by [[platform#op: platform.enterprise]], [[settings#Identity]]; excluded — not a company face | F8 lane (platform.md / settings.md) | 2026-06-12 |
| Host config files inherited but not company-owned: `~/.claude/settings.json` (service account), `~/.claude/keybindings.json`, `~/.claude/.credentials.json` (mode 0600), `~/.claude.json` (OAuth/MCP/trust/caches) | host filesystem | files Claude Code reads at startup that the fabric INHERITS (the service account's) but the company neither edits nor exposes (credentials are never read). Cited by [[settings]], [[auth]], [[surfaces]]; excluded — host filesystem, not a company route | F8 lane (settings.md / auth.md / surfaces.md) | 2026-06-12 |
