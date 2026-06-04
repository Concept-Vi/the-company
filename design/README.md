# design/ — the corpus is a ONE-WAY SYNCED READ-COPY

> [!warning] NEVER hand-edit anything in this folder.
> The **canonical** design corpus lives at:
> `…/build-prep/design/` (Windows-side: `/mnt/c/Users/Workstation001/Documents/Claude/Projects/counterpart/the Company/build-prep/design/`).
> `~/company/design/` (and the worktree's `design/`) is a **synced read-copy** of that canonical source.

## The sync rule (one-way)

```
build-prep/design/   ──── sync ───▶   ~/company/design/
  (CANONICAL — edit here)              (READ-COPY — never hand-edit)
```

- **Source of truth = `build-prep/design/`.** Every edit — a new token, a new address, a CSS regen, a mockup — happens **there**, then re-syncs down into the repo.
- **This copy is generated/synced, not authored.** A hand-edit here is silently overwritten on the next sync (no-silent-failures, AGENTS.md rule 4) — and it desyncs the copy from canonical with no record.
- **To change the look / addresses:** edit `build-prep/design/_system/tokens.json` (or `addresses.json`) → run `emit.py` / `parse.py` **in canonical** → re-sync. `design-system.css` carries a "GENERATED — DO NOT hand-edit" header for the same reason (its edit point is `tokens.json` → `emit.py`).
- **`design/CLAUDE.md`** is the corpus keeper's charter (the discipline above, in full). This README is the short sync-direction note that gates anyone touching the in-repo copy.

## What's here

The synced corpus the FORM gate and the FE build against:
- `design-system.css` — the emitted token stylesheet the app imports (F1).
- `_system/tokens.json` — the token registry (the look's source of truth, edited canonical-side).
- `_system/addresses.json` — the `ui://` address registry.
- `_system/check.py` — the structural-coherence pass **and** the in-repo **design-lint** (see below).
- `_system/emit.py`, `parse.py`, `symbols.py`, `refcheck.py`, … — the corpus machinery.
- `mockups/` — the grounded screen corpus.

## `check.py` — two modes (the design-lint, C0)

`check.py` keeps its default **mockup-scan** (no args) intact, and adds an additive **design-lint** that gates the live app:

```bash
# default — mockup-scan (unchanged): writes check-report.json
python3 design/_system/check.py

# design-lint — gate app source against the corpus tokens (FORM gate, AGENTS.md rule 9):
python3 design/_system/check.py --target canvas/app/src --fail-on [--include-px] [--report PATH]
```

`--fail-on` exits **non-zero** when it finds a hardcoded off-token literal (raw hex/rgba — the
app must use `var(--…)`; `+px` with `--include-px`) or a bespoke element in `<target>`. Unlike the
mockup-scan's recurrence finder (count>1, colour-only), the design-lint flags a **single** occurrence,
so a planted off-token literal trips it — this is the machine half of the FORM gate (F1/F9 consume it).

> [!note] Bespoke-element detection is a documented **stub** for C0 (returns `[]`) — it graduates
> once the app carries `data-ui-ref` (F4) and the corpus component inventory is reconciled against the
> app (F1). It is wired into `--fail-on` but injects no findings today.
