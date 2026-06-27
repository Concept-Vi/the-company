---
type: terrain-entry
name: actions-runner
register: descriptive
aliases: ["actions-runner"]
path: /home/tim/actions-runner
relation: external
kind: engine
status: unconfirmed
created: 2026-04-30
last_active: 2026-04-30
size: 1.8G
coverage: { files_read: 2, files_total: 2, last_read: 2026-06-26 }
git_remote: none (runner binary, not a repo)
ports: []
models: []
service_units: [github-runner]
launched_by: github-runner.service → /home/tim/actions-runner/run.sh
launched-by: ["[[company-systemd]]"]
part-of: ["[[company]]"]
secrets: true
move_intent: none
tags: [control]
---

# actions-runner

## What it is
A 1.8G self-hosted GitHub Actions runner install — the agent that lets GitHub workflows execute on this workstation. Bound to repo `Concept-Vi/ollama-pipeliner` (per the unit description). The tree holds two runner versions side by side (`bin` + `bin.2.321.0` + `bin.2.334.0`, same for `externals`), plus `_work` (checkouts), `_diag` (logs), `config.sh`, `run.sh`.

## How it works
- `github-runner.service` → `ExecStart=/home/tim/actions-runner/run.sh`, `WorkingDirectory=/home/tim/actions-runner`, `Restart=always`, `After=network-online.target`.
- The unit passes through `PATH=/home/tim/.local/bin:…` and `HOME=/home/tim` with the comment "Pass through credentials/PATH so the runner can find claude, gh, python, etc." — i.e. it is set up to run CI jobs that invoke `claude` and `gh`.

Direct single-hop wire: ExecStart runs the runner's own `run.sh`.

## What it connects to
- `[[company]]` / `[[company-systemd]]` — the unit is part of the systemd set; the runner's PATH is wired to reach `~/.local/bin` (where the `company` CLI symlink lives).
- External: GitHub repo `Concept-Vi/ollama-pipeliner` — the control/CI surface that triggers jobs here.

## When / where
`/home/tim/actions-runner`, 1.8G. Unit mtime 2026-04-30 (the oldest control-plane unit). Multiple `bin.<version>` dirs show in-place runner upgrades.

## Notes / evidence
- Read: `github-runner.service` (verbatim ExecStart + repo binding + PATH passthrough), dir listing.
- `secrets: true` — a self-hosted runner holds registration credentials (`.credentials`/`.runner` in the tree) for the bound GitHub repo.
