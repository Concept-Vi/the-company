# Coverage Audit → full build + integration into the system (the return-to spec)

*Tim 2026-06-30: prove the use case first (the front + actual analysis of the data), but note EVERYTHING a full build/integration requires so we can return to it. This is the requirements ledger; it grows as the proof surfaces more. Root-fix issues as found (background upgrades are landing in another session, so expect a few).*

## The goal
The coverage audit (4B as auditor-vs-ground-truth, finds what the deterministic extractor MISSED) running as a first-class IN-SYSTEM operation — a role, routed, schema-validated, recorded, fanned over the corpus, with results that feed fixes + a front to see them. Not the bespoke `ops/ledger_coverage_audit.py` urllib harness (to be retired).

## Requirements for the full build (grows as we prove it)
### Model / infra
- [ ] **Concurrency** — 4B loaded at `max-num-seqs 2`; raise it so a full 4,540-file sweep isn't hours. (doing now)
- [ ] **`think=False` for bulk** — reasoning is ~30× the tokens; the scaled audit must run no-think. Only `run_role` exposes `think`; `run_draft_items`/`run_items` do NOT → the audit likely needs to be a **registered role** run with think=False, OR add a think axis to the batch tools.
- [ ] **Registry drift fix (ROOT)** — the live 4B (`RedHatAI/Qwen3.5-4B-FP8`, :8001, 64k) ≠ the registered `chat-4b` (:8000, AWQ, 16k). The model registry/services entry must reflect what's actually loaded.
- [ ] **Stale provider on loadout change (ROOT)** — the engine held a dead provider binding after the 4B loaded (fixed only by `/mcp` reconnect). A model swap should trigger an engine provider-reload, not require a manual reconnect.

### The role + input assembly
- [ ] **Register a `coverage_audit` role** (output_schema: `missing: list[str]`, `notes: str`) — validated in draft form; promote it.
- [ ] **Input assembly addressable** — each audit needs (file content + its ledger-extracted symbols). For `run_draft_items`/`run_items` to fan over `code://` addresses cleanly, the resolver should return **content + the ledger symbols** for a `code://` file address (today it returns content only). Either enrich `resolve_address`, or a CLI driver assembles items.
- [ ] **Two passes** (with-contract conformance / without-contract discovery) — the contract text becomes part of the role; the diff = candidate new contract items.

### Results → action + the FRONT
- [ ] **Persist results** — audit findings (per file: missing[], a tags+counts coverage signal) written back to the ledger (e.g. a `coverage_audit` jsonb / edge), not just `run://` ephemera.
- [ ] **The blind-spot map** — aggregate by language/extractor → which extractors are weak → drives extractor fixes → cheap re-run (needs F6 carry-forward).
- [ ] **A front** — surface the audit results to Tim's eye (the interface that renders the ledger): which files flagged, what's missing, per-extractor health. Recognition-level. (Prove the use case includes seeing it.)
- [ ] **Close the loop** — flagged extractor gaps → fix the extractor → re-extract only affected files → re-audit.

### The bigger rebuild (related)
- [ ] **The interpretive sweep itself** should be the existing `interpret_file` role (+ `dragnet_*`) via the engine, not the bespoke `ledger_interpret_*` producers. The coverage audit is the smaller proof of the same "into the system" move.

## Proof-of-use-case progress (this session)
- [x] Mechanism validated in-system (clean / gap / clean-JS cases) — schema-validated, `run://` provenance.
- [x] **Registered as a real role** (`roles/coverage_audit.py`, output_schema `CoverageAuditOut`, reflected in roles/AGENTS.md) — the in-system, reusable form.
- [x] **`run_role(think=False)` is the reliable path** — thinking-on times out on this task (confirmed twice via run_draft); think=False runs fast + clean. The bulk audit MUST be run_role(think=False) over items (run_draft_items/run_items don't expose think — see requirement).
- [x] **REAL-DATA gap found** (the use case proven): `dials/anticipation.py` → `{missing:["DIAL"], notes:"module-level dict DIAL = {...} present but missing from extracted symbols"}`. The audit found a real systematic extractor gap.
- [ ] Concurrency raised (configured 32 but running stale at 2 — see root issues).
- [ ] Real sampled batch via `run_role(think=False)` over items → the blind-spot map by language/extractor.
- [ ] A front to view it.

## Root issues found (resolve at root — Tim 2026-06-30)
1. **Extractor misses module-level constants/dicts** (CONFIRMED by the audit's first real finding). `parse_python` (code_archaeology.py / ledger_build.py) captures functions/classes but not `NAME = {...}` module assignments → the entire `dials/` registry (and likely role `DIAL`/`RULE` rows, config dicts) extract ZERO symbols. *Root fix:* capture module-level constant/dict assignments as symbols (kind=`constant`/`module_dict`), re-extract. This is exactly what the coverage audit exists to surface.
2. **Registry drift** — live 4B (`chat-4b-fp8`, :8001, FP8, 64k) ≠ registered `chat-4b` (:8000, AWQ). The everyday brain is now `chat-4b-fp8` (combos.interaction migrated) — tools/harnesses must target it.
3. **Concurrency configured-but-not-applied** — `chat-4b-fp8` config = `max_num_seqs 32, gpu_util 0.9`, but the RUNNING process is stale at `--max-num-seqs 2 --gpu-util 0.5`. Applying needs a brain RESTART; GPU is at 0.1GB free so 0.9-util needs evicting co-residents (tts-kokoro etc.). Risky to do blindly (safety-critical live brain + active other session) — coordinate.
4. **Stale provider binding on loadout change** — engine couldn't reach the freshly-loaded 4B until `/mcp` reconnect. A model swap should trigger an engine provider-reload.
5. **Thinking-on timeouts** — long reasoning exceeds the engine request timeout (→ `content:None` / `TimeoutError`). think=False is the mitigation; also consider raising the engine timeout for thinking roles.
