# the-one-system — living SCOPE (recurse until empty, verified by real use)

**Standing rule (Tim, 2026-06-28):** anything I come across — mine or not, including the original authors'
deferred/half-done work — goes into this scope and gets implemented RECURSIVELY until nothing is left.
"Complete" = every real-use path exercised through the LIVE system and proven by actually using it (not
fixtures, not `python -c`, not raw SQL). Each fix that surfaces new gaps adds them here. Correct anyone's
behaviour. No silent deferral, no "tests pass = done."

## OPEN (capability/registry lane)
- [x] **Back `cap://` runtime resolution with the LEDGER** — DONE + VERIFIED BY USE (2026-06-28). Suite
      loads the registry from the ledger spawn-free (435 caps, gated COMPANY_CAP_LOAD_FROM_LEDGER=1);
      `resolve_address('cap://codex-cli/flag/--model'|'--sandbox'|gh|legacy-claude)` all resolve through the
      REAL resolver with no timeout. Acceptance tests updated (mechanism isolated) + still green.
- [x] **MCP `capability` tool works live** — VERIFIED BY USE post-reconnect: `capability(op=describe)`
      returns 435 caps with NO timeout; `capability(op=list, platform_id=codex-cli, posture=hazard)` returns
      codex's 2 hazard flags. The ledger-backed registry serves it live.
- [x] **Run ANY capability through the system** (universal invocation layer) — DONE + VERIFIED BY USE.
      `introspection/invoke.py`: selects an invoker by `invocation_kind` (subprocess built; rest/mcp/grpc
      gap-surfaced via MissingInvokerError), POSTURE-GATED via the live registry (locked/hazard REFUSE
      without confirm=True; consent recorded; safe/unknown run). Exposed as MCP tool `mcp_face/tools/platform.py`
      (op=list/describe/gate/invoke). Verified: `codex --version` + `gh --version` run through it; the codex
      hazard flag is REFUSED without confirm; an unbuilt invoker fails loud. Goes live for the MCP face on
      server restart.
- [ ] **Discover SUBCOMMANDS too** (surfaced by the invocation work): the registry holds FLAGS, not
      subcommands (gh `pr`/`issue`, codex `exec`/`mcp`). To truly run "any capability" the discoverer should
      capture the subcommand tree, not just the flag table. Discovery enhancement → into scope.
- [~] **Generalize the producers** — CODEX SIDE DONE (2026-06-28), kimi side still deferred. The codex lane
      is now driven by the ONE `ledger_interpret_producer.py --backend codex` (the dead lane = zero risk to
      consolidate, which is exactly what the original defer was protecting against). `ledger_interpret_codex.py`
      remains only as the registry-binary resolver (`_resolve_codex`) the producer imports — not as a driver.
      The KIMI side stays on `_ollama.py` until the sweep COMPLETES (it is running ON it right now; the v2
      contract also lives there and the producer imports it). Post-sweep: retire `_ollama.py` as a driver too
      (keep the contract home) + fold the Opus workflow in. Honest, partial, recorded.
- [HELD] **Codex lane held — OpenAI/ChatGPT plan out of credits** (2026-06-28, Verified by `codex exec` rc=1
      "Your workspace is out of credits. Add credits to continue."). NOT rate-limiting — permanent until a
      human tops up. FIX shipped: the producer now CLASSIFIES terminal (credits/auth) vs transient (rate
      limit) and raises `TerminalBackendError` → exit code 3 → the codex driver HOLDS (stops) instead of the
      old mislabelled infinite "backoff 900s" that silently failed 120 files/pass. Verified by real use
      (exit 3 + `{"held":true,...}`). The sweep is UNAFFECTED: the kimi lane is project-agnostic (queue spans
      all projects) and finishes all 1066 alone, just slower. Resume codex by topping up credits + relaunching
      `ledger_interpret_codex_drive.sh`. Surfaced to Tim as info (top-up = speed-only, non-blocking).
- [x] **Auto code→capability deep-link (AST-precise)** — DONE + VERIFIED BY USE. `deep_link_ast` parses
      Python files for subprocess/exec calls, resolves argv[0] to a platform binary (literal or var), links
      only the flag literals in that call → `uses-capability` edges. True edge found
      (ledger_interpret_codex.py → cap://codex-cli/flag/--skip-git-repo-check); address.py/cognition.py
      (docstring mentions only) correctly NOT linked. Scans the LIVE filesystem (finds new files). No fiction.
- [x] **SessionStart freshness hook** — VERIFIED LIVE: `cc_registry_freshness_check.sh` fires and reports
      all 3 platforms (claude/codex/gh) via the registry-driven helper.
- [x] **`cc_registry_refresh(platform_id=…)`** — VERIFIED LIVE for codex (first_run, v0.142.3, real diff
      payload added/changed/vanished, surfaced). The claude-hardcoded path is now registry-driven.
- [x] **`discover_capabilities(None)`** — VERIFIED LIVE: all 3 platforms discovered in 15s, per-platform
      isolated (one failing wouldn't block the rest), registry holds all 3.
- [x] **Original-author deferred items** (🟡 C-WIRE/C-REF live-verify) — now substantially DISCHARGED by the
      above live runs (live cap:// resolution, real refresh, freshness firing). Remaining: stamp/cache persist
      post-approval (governance write order) — verify when a curator-approval path is exercised.
- [x] **Subcommand discovery** — DONE + VERIFIED. New `subcommand-list` parse_rule in cli_help.py
      (colon-optional header + row, handles clap 'Commands:' AND cobra 'CORE COMMANDS' / 'auth:'); top-level
      --help discovery source added to codex + gh rows. codex: 24 flags + 23 subcommands; gh: 21 flags + 29
      subcommands. Persisted as cap:// nodes; `cap://gh-cli/subcommand/pr` + `cap://codex-cli/subcommand/exec`
      resolve live. "Run any capability" now covers the command tree, not just flags. Tests green.
- [x] **Carry-forward resilience** — DONE + VERIFIED (found by a regression I caused): a flaky binary
      (claude's init-session timeout) must NOT erase its known capabilities. `_prior_caps` re-emits a
      platform's caps from the most-recent run that had them when discovery fails. Verified: claude's 390
      preserved through a timeout (carried-forward), codex/gh fresh. The persist never loses a platform.
- [ ] **Version-pinned capabilities** actually used (cap://<platform>@<version>/…) — refresh writes version
      stamps; verify the @version address resolves to the right snapshot.

## OPEN (ledger / drift lane)
- [x] **Interpretive sweep COMPLETE** (2026-06-28) — claude-ds 295/295, counterpart-design 859/859,
      company 3460/3461. Verified by gate query on the live ledger (port 15432).
- [ ] **The 1 remaining is DRIFT, not a failure** — `guides/using-skills.py` was renamed to
      `guides/using_skills.py` at 02:15 on 2026-06-28, AFTER the structural snapshot (06-27 16:10). The
      ledger faithfully holds the old (now-deleted) name → the interpreter can't read it; the new name is
      absent from the ledger entirely. The gate reporting "1 remaining" is the drift detector being HONEST,
      not a defect. Left as-is (do NOT hand-patch — that would hide real drift).
- [ ] **★ REAL GAP found: incremental structural refresh ORPHANS the interpretive layer.** `ledger_build.py
      --incremental` on any change writes a brand-new full snapshot run via `extract_folder` + `load_run`,
      which does ONLY deterministic facts (ledger_build.py:13) — `what_it_does` starts NULL for every file.
      So running it would make the new run the latest with ZERO interpretation, orphaning the whole sweep on
      the prior run + reverting the gate to ~3461 remaining for company. **Drift reconciliation is therefore
      currently UNSAFE to run.** FIX needed (recurse-the-mandate): `load_run`/incremental must CARRY FORWARD
      `what_it_does` (+ model/prompt_version) for files whose source_hash is unchanged, re-interpreting only
      changed/new files. This is the drift-reconciliation design the system needs before Stage 3. Recorded,
      not silently deferred.

## DONE (verified — by USE where stated)
- [x] codex registered as platform #3 (24 flags discover+classify, zero engine edits) — engine-verified.
- [x] cap:// nested grammar + legacy alias + open kind vocab + multi-platform registry — unit-verified.
- [x] Capabilities as ledger nodes (438) + capability-of/on-axis edges — verified by live SQL query.
- [x] Refresh flow `platform_id=`/`run_all`, freshness hook registry-driven, constitutions updated — code+import verified.
- [ ] ↑ ALL of the above still need LIVE-USE verification through the running system (the campaign).

## NOTES
- The string-match deep-link produced fiction (address.py "used" codex from its docstrings) → pulled.
- Live finding: codex/gh discover in 0.1-0.2s (cheap --help); only claude's init-session discovery times out.
