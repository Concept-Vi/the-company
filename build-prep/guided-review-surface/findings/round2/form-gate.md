# FORM Gate Wiring — Round 2 Verification Finding

**Date:** 2026-06-08
**Scope:** Does the design-lint (check.py) FORM gate fire on guided-review-surface FE when built via the generate→autonomous-claude→commit path?

---

## Evidence Classification

All claims are marked per the Evidence Classification Protocol:
- **Observed:** directly read from file:line — structural fact, no execution required
- **Verified:** confirmed by execution/test run
- **Inferred:** pattern-matched from structure — labelled; not verified by execution

---

## 1. What the FORM Gate Is

**Observed (design/_system/check.py:101–133, 136–167):**
The FORM gate is `design/_system/check.py` invoked with `--target <file> --fail-on`. In mode B (design-lint), it scans `.tsx`/`.css` files for:
- Hardcoded off-token colour literals (hex, rgba) — flags single occurrence (gate semantics, not recurrence)
- Bespoke elements — currently a documented stub (`_find_bespoke_elements` returns `[]` at line 98, to graduate with F4/F1)

With `--fail-on`, it exits non-zero when any off-token literal is found — so it can gate a build.

---

## 2. The Build Path for the Guided-Review-Surface FE

**Observed (ANCHOR.md:139):**
> "The wire: `runtime/implement.py` (`dispatch_decision`, launch/verify/git-checkpoint)."

**Observed (ANCHOR.md:49–51, §3):**
> "GENERATE (you click): RHM composes the plans/requests from everything discussed → SHOWS you through → you APPROVE the batch → dispatched to autonomous Claude → committed to git → revert if it breaks"

The guided-review-surface build path is **operator-approve → `dispatch_decision` → `implement.launch` (`claude -p`) → verify → close or surface-back**.

**Observed (runtime/implement.py:481, 497):**
The docstring of the batch watcher (`drive_dispatchable`) explicitly states: "all through dispatch_decision" (line 481) and "the default launcher/verifier/committer are dispatch_decision's own" (line 497).

**Observed (runtime/implement.py:545–547):**
```python
out = suite.dispatch_decision(sid, seq, launcher=launcher, verifier=verifier,
                              suite_runner=suite_runner, critic=critic, repo=repo,
                              committer=committer)
```
The batch watcher calls `suite.dispatch_decision` — confirmed at line 545. Every dispatched build goes through `dispatch_decision`, no exception.

---

## 3. Where the FORM Gate Is Wired

**Observed (runtime/suite.py:7515):**
`_design_critic(result.get("changed_files", []))` is called UNCONDITIONAL inside `dispatch_decision`, after `launch()` returns and after the injectable verifier runs. The comment at line 7502–7509 makes this explicit:

> "7b — H4/F9 FORM GATE (UNCONDITIONAL — a structural gate, like the scope-diff, NOT inside the replaceable verifier). A build that touched an operator-facing surface (canvas/) is run through the LIVE machine FORM gate…"
> "The STRUCTURAL gates — refresh, FORM, scope-diff — are UNCONDITIONAL, below + above; they are NOT replaceable by an injected verifier, so a loop's scenario verifier can never close a surface build."

**Observed (runtime/suite.py:7190–7281):**
`_design_critic` calls `_touches_surface(changed_files)` (line 7209), which checks each path against `_SURFACE_PREFIXES = ("canvas/",)` (line 6947). Any changed `.tsx`/`.css` under `canvas/` becomes a lint target.

**Observed (runtime/implement.py:23, 383):**
Changed files are captured via `git diff` ground truth (NOT the model's self-report) — `changed_delta(repo=repo, before=before)`. So every file the autonomous claude actually writes to disk under `canvas/` will appear in `changed_files` and be passed to `_design_critic`.

**Conclusion (Observed):** For the guided-review-surface FE built via `dispatch_decision` (the generate→approve→dispatch path), the FORM gate FIRES.

---

## 4. The Gap: FE Written OUTSIDE the Wire

**Observed (runtime/suite.py:6947, 7168–7178):**
`_SURFACE_PREFIXES = ("canvas/",)` — only paths under `canvas/` trigger the gate. The gate lives exclusively inside `dispatch_decision`.

**Observed (.git/hooks/):**
All files in `.git/hooks/` are `.sample` (inactive). No pre-commit hook is installed.

**Observed (canvas/app/package.json:5):**
npm scripts are only `dev` and `build` — no design-lint step.

**Observed (no `.github/` directory):**
No CI pipeline exists.

**Conclusion (Observed):**
The FORM gate fires **only through `dispatch_decision`**. FE written by any path that bypasses `dispatch_decision` — a raw `claude -p` session that is not routed through the wire, a directly-written agent edit, a worktree session — commits canvas files that are **never checked by the design-lint**. No git hook, no CI, no npm build step catches them.

This is a real gap: not a hypothetical side case. The existing `canvas/app/src` already carries 2 off-token literals (`app.css:1426` and `app.css:1515`, both `#fff`) that were written outside the FORM gate or before it existed. Those literals exist in the tree and would not have been caught by any current catch-all.

---

## 5. Existing Off-Token Debt in canvas/app/src

**Verified (executed: `python3 design/_system/check.py --target canvas/app/src`):**
```
design-lint (off-token + bespoke gate) — target: canvas/app/src
  files_scanned: 34
  off_token_literals: 2
  bespoke_elements: 0
  → off-token literals (file:line literal):
      canvas/app/src/app.css:1426  #fff (colour)
      canvas/app/src/app.css:1515  #fff (colour)
```

Two off-token literals, both in `app.css` (not in any `.tsx` component file). The component files are clean. This is low-debt — the corpus token `--white` or `--surface` likely covers both; these are candidates to replace with `var(--…)`.

---

## 6. The Gap-Closing Fix

### Root diagnosis
The wire gate is structurally sound for all builds routed through `dispatch_decision`. The gap is commits that bypass `dispatch_decision` — specifically the absence of a git pre-commit hook. A hook binds at the only universal choke point (every commit, regardless of write path).

### Critical constraint from the wire (suite.py:7219)
> "Lint only the surface files THIS build changed — a clean change must not be gated by pre-existing dirt elsewhere."

The hook MUST follow the same logic: lint only staged files, not the whole `canvas/app/src` tree. Linting the whole dir would fail on the 2 existing `#fff` literals in `app.css` — blocking every canvas commit. The wire correctly avoids this; the hook must too.

### The fix: a tracked git pre-commit hook that lints staged files only

**Hook shell (to write at a tracked path, e.g. `hooks/pre-commit`, then wire via `core.hooksPath`):**

```bash
#!/usr/bin/env bash
# FORM gate: design-lint on STAGED canvas/ .tsx/.css before commit (mirrors wire's per-file lint)
# Lints only the staged files — not the whole tree. Pre-existing off-token dirt elsewhere
# does NOT gate a clean change (same constraint as _design_critic in suite.py).
set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPT="$REPO_ROOT/design/_system/check.py"

if [ ! -f "$SCRIPT" ]; then
  echo "FORM pre-commit: design-lint script missing at $SCRIPT — refusing commit (fail-safe)" >&2
  exit 1
fi

# Only staged canvas .tsx/.css files — same logic as _touches_surface in suite.py
staged_form=$(git diff --cached --name-only --diff-filter=ACM | grep -E '^canvas/.*\.(tsx|css)$' || true)

if [ -z "$staged_form" ]; then
  exit 0  # no lintable surface in this commit
fi

echo "FORM pre-commit: design-lint on staged canvas surface files..."
failed=0
while IFS= read -r rel; do
  full="$REPO_ROOT/$rel"
  if [ -f "$full" ]; then
    python3 "$SCRIPT" --target "$full" --fail-on || failed=1
  else
    echo "FORM pre-commit: staged file $rel not on disk — refusing commit (fail-safe)" >&2
    failed=1
  fi
done <<< "$staged_form"

exit $failed
```

**Wiring it durably (AI-native repo requirement):**
`.git/hooks/` is ephemeral (not tracked, lost across fresh clones/worktrees). The correct approach for this repo:

1. Write hook to a TRACKED directory: `hooks/pre-commit` (alongside `design/_system/` and `runtime/`)
2. Configure git to find it: `git config core.hooksPath hooks` (one command, persists in `.git/config`)
3. Add one line to root `AGENTS.md` — the constitution under which agents work: "After cloning, run `git config core.hooksPath hooks` to activate the FORM gate." This makes the hook path-of-least-resistance for all sessions.

This is the AI-native equivalent of a CI gate: self-describing, traceable, and picked up by fresh sessions that read `AGENTS.md` before acting.

---

## 7. Acceptance Test — Does It Cover Live canvas/?

**Observed (tests/design_gate_acceptance.py:22):**
> "Self-contained: every surface file is planted in a TEMP tree (never the real repo's canvas/), so the tests are hermetic and never touch the live app."

The acceptance test does NOT lint live `canvas/app/src`. It tests `_design_critic`'s logic using planted temp files. This is correct (hermetic tests are right), but it means the acceptance test does NOT catch off-token debt in the actual canvas source. The pre-commit hook fills this gap.

---

## 8. Summary Table

| Question | Answer | Evidence |
|---|---|---|
| Is FORM gate wired for wire-routed builds (via `dispatch_decision`)? | YES — unconditional, non-bypassable | Observed suite.py:7515, 7502–7509 |
| Does the guided-review-surface build path go through `dispatch_decision`? | YES — operator-approve → `dispatch_decision` → `_design_critic` | Observed ANCHOR.md:139, implement.py:545 |
| Does it fire for FE written outside `dispatch_decision`? | NO — no git hook, no CI, no npm lint | Observed .git/hooks/ (all .sample), package.json:5 |
| Is there existing off-token debt in canvas/app/src? | YES — 2 literals (`#fff` in app.css:1426,1515) | Verified: check.py --target canvas/app/src run |
| Does the acceptance test cover live canvas source? | NO — hermetic temp files only | Observed design_gate_acceptance.py:22 |
| Smallest fix? | Tracked `hooks/pre-commit` linting only staged canvas .tsx/.css; wired via `core.hooksPath` + one AGENTS.md line | Mechanism already exists; hook path is the universal choke point |

---

## Status Markers

- **FORM gate in the wire (for dispatch_decision path):** ✅ Observed / structurally confirmed
- **Build path for this surface goes through dispatch_decision:** ✅ Observed (ANCHOR.md:139, implement.py:545)
- **Gate for directly-written FE (bypassing dispatch_decision):** 🔴 Confirmed gap (no hook, no CI, no npm step)
- **Existing off-token debt in canvas/app/src:** 🟡 2 literals (`#fff` x2 in app.css) — known, named, actionable
- **Fix proposed (pre-commit hook + core.hooksPath + AGENTS.md line):** 🟡 Code-complete-untested (hook text above; needs `chmod +x` + an end-to-end `git commit` test to verify it fires correctly on a staged off-token file)
