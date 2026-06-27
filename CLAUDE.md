# CLAUDE.md — Company (orientation for Claude Code sessions)

There are **no human developers** here; this codebase is built and grown entirely by AI agents. Orient before acting.

## Read first (the constitution)
**`AGENTS.md`** is the source of truth for how to work in this repo — the rules, the "where does this go?" table, and the self-description discipline. Then `MAP.md` (structure + live registry), `STATE.md` (current status / how to run + verify), and the `AGENTS.md` of the module you're touching. `HANDOFF.md` carries the latest session narrative + the live-surface/voice/ops how-to.

## This repo is a knowledge vault — follow the convention when you write ANY note
`~/company` is **simultaneously code and an Obsidian vault**: the same markdown that instructs you is the navigable self-model. The canonical rules are **`docs/vault-conventions.md`** — read it before adding or editing any `.md`. In short:
- **Every folder has an `AGENTS.md` constitution** (the folder-note); **`MAP.md`** is the one vault home.
- **Frontmatter on every self-description note** (`type · register · aliases · tags · status` + typed relations); **links use aliases** (`[[runtime — constitution]]`), and **relations are typed by the frontmatter key** (`calls`, `depends-on`, `indexed-by`, `launched-by`, `prospected-for`, … — open vocabulary).
- **`register: descriptive | prescriptive`** — is this note a *map of what is*, or a *binding rule*? (descriptive maps are never blueprints.)
- **`status` is confirmed-only on terrain-entries** (default `unconfirmed` — never assert live/dead by inference); a module's own build-state (`living`/`building`/`planned`) is a different, legitimate use.
- **`coverage: {files_read, files_total, last_read}`** on terrain-entries — never imply a completeness you didn't verify.
- Working docs (`build-prep/`, `channel-memory/`, `foundation/exchanges/`) keep their own frontmatter; the strict schema governs the self-description layer. **The knowledge face must not depend on the Obsidian app** — frontmatter + a generated index + greppable links carry it.

## Know where the Company actually lives — the orienteering ledger
The Company is **more than this folder**: its model/voice engines, the session-recall index, TLS certs, the ~20 `company-*` systemd services, and a tail of scattered work/data live **outside** `~/company`, wired in by systemd. The map of all of it is **`orienteering/INDEX.md`** (the terrain ledger — one note per thing, with what it is, where it physically is, what it connects to, and whether it's live/dormant/moving).
- **Before acting on anything outside `~/company`** (a venv, the recall index `~/.cache/company`, a connected tool, a scattered folder), check its `orienteering/entries/<name>.md` first.
- **When something new appears in the Company's orbit, or a path moves/dies, update the ledger** — it is part of the change, not optional. See `orienteering/AGENTS.md` + `docs/vault-conventions.md` for the schema; it is a **map, not a blueprint** (its layout is provisional — don't copy it as "how the Company should be structured").
