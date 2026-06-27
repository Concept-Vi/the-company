---
type: terrain-entry
name: company-cli
register: descriptive
aliases: ["company-cli"]
path: /home/tim/.local/bin/company
relation: external
kind: engine
status: unconfirmed
created: 2026-06-04
last_active: 2026-06-04
size: symlink (29 bytes) → in-repo body
coverage: { files_read: 1, files_total: 1, last_read: 2026-06-26 }
git_remote: none
ports: []
models: []
service_units: []
launched_by: invoked by the user / agents on PATH (not a service)
part-of: ["[[company]]"]
secrets: false
move_intent: none
tags: [control]
---

# company-cli

## What it is
`/home/tim/.local/bin/company` — the `company` control CLI on the user's PATH, the one control surface for the whole Company system (services, models, GPU/resource manager, config). It is an **external pointer with an in-repo body**: the file is a symlink, and the actual code lives inside `~/company`.

## How it works
- `ls -la` shows: `/home/tim/.local/bin/company -> /home/tim/company/ops/company` (29-byte symlink).
- The target `ops/company` is a thin shim whose own header says: *"company — launcher. The console itself lives in the cli/ package next to this file. This thin shim keeps the ~/.local/bin/company symlink valid and runs cli/app.py."*

So the PATH entry is external, but it resolves straight back into the repo (`ops/company` → `ops/cli/app.py`). It is invoked directly by Tim/agents — there is no systemd unit for it (it is the control surface, not a daemon).

## What it connects to
- `[[company]]` — the symlink target and all CLI code live inside `~/company/ops`. This entry is essentially a PATH alias INTO the repo.

## When / where
Symlink at `/home/tim/.local/bin/company`, mtime 2026-06-04. The rest of `~/.local` is generic user-tooling, NOT Company — only this single symlink is the Company control surface.

## Notes / evidence
- Read: `ls -la` of the symlink (target shown verbatim), shim header of `ops/company`.
- **Note per advisor:** `relation: external` here means "external PATH pointer"; the body is in-repo. Recorded the symlink as the path, with the in-repo target made explicit so this isn't mistaken for a separate copy of the CLI.
