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
