# Full build & integration — the analysis/interpretive layer INTO the system

*Tim 2026-06-30: "note all the things required to do a full build and integration into the system, so you can return to it… it will be beneficial to fully prove the use case of this, including the FRONT and the actual use in analysis of the data." This is the return-to backlog. The principle: everything the ledger does (interpret · audit · edges · metadata · drift · analysis) should run AS in-system roles/flows (routing, output-schema, run-provenance, reuse) with a FRONT that renders it to Tim's recognition — not bespoke scripts that go around the system. Build derived from the 4B first-run findings (`4B-FINDINGS.md`).*

## A — Model serving / concurrency (the substrate)
- **Resident 4B:** `RedHatAI/Qwen3.5-4B-FP8-dynamic` on `:8001`, systemd `vllm-chat-4b-fp8.service`. Flags: `--max-num-seqs 2 --max-model-len 65536 --gpu-memory-utilization 0.5`. GPU ~15.6/16.4 GB (near full).
- **Raise concurrency:** more seqs ⇒ more KV-cache VRAM, but only ~0.75 GB free. So trade `max-model-len` DOWN (16–32k covers ~all files) for `max-num-seqs` UP (~8–16) at the same VRAM. = a service restart (brief blip). COORDINATE — another session is upgrading this unit.
- **[ROOT] registry drift (F-1):** `ops/services.json` says `chat-4b` = AWQ `:8000`; reality = FP8 `:8001` (`vllm-chat-4b-fp8.service`). Reconcile the registry/loadout to what's actually served (or make the unit config-driven from services.json so they can't drift).
- **[ROOT] provider reload-after-loadout (F-9):** the cognition engine cached a stale provider base_url across a model swap → `run_draft` got `ConnectionRefused` until an MCP `/mcp` reconnect, even though `:8001` was up. Needs a reload hook so a resident-model change re-reads provider config (no manual reconnect).
- **[GAP] `think` on the batch tools:** `run_role` exposes `think=False` (30× fewer tokens) but `run_items`/`run_draft_items` do NOT. For bulk extraction either expose `think` on the MAP tools, or register the role with a think-off default.

## B — The interpretive layer as ROLES (not bespoke producers)
- `interpret_file` (+ `dragnet_coarse/fine/design`) roles ALREADY EXIST. The `ops/ledger_interpret_*` producers should be replaced by running these roles via the engine (`run_items` over file addresses) — routed, schema-validated, recorded.
- **Requires:** `resolve_address(code://…)` returns file content + the ledger's deterministic symbols, so the role input is ONE address (today the producers hand-assemble this).
- The v2 interpretive schema → the role's `output_schema` (enforces no-confidence). Each file's interpretation recorded at `run://` (the bespoke path records nothing).

## C — Coverage audit as a ROLE
- The `coverage_audit` draft (VALIDATED, `4B-FINDINGS.md`) → register it; run via `run_items` over file addresses with `think=False`; missing[]/notes schema.
- Aggregate the per-file `run://` outputs → the blind-spot map by language (confirm F2, drive extractor fixes).
- Two passes (with/without contract) as a role param or two roles. Then **retire `ops/ledger_coverage_audit.py` (urllib)**.

## D — Edges / metadata / change-detection as FLOWS
- `ledger_metadata` · `ledger_fact_edges` · `ledger_changes` are deterministic ops (OK as scripts) but should be **registered flows/cascades** — discoverable, composable, schedulable (drift detection on a routine).
- **Selective re-run / carry-forward (F6):** detect (changed/added/deleted) → re-extract changed structurally → re-interpret via the `interpret_file` role → keep unchanged interpretation. The maintainable incremental update loop. Still UNBUILT — the keystone for keeping the ledger current.

## E — The FRONT (Stage 1 — where the use case is PROVEN to Tim)
- Render the ledger to recognition: tree/graph/filter views, **state-as-colour**, the **edge graph** (42,775 structural + 3,339 observed document/self-description edges), the **metadata** (created/changed/**change-frequency**/size), at-a-glance. (Per LEDGER-SPEC, the ledger IS what this interface renders.)
- Surface the **analysis**: the coverage blind-spot map, the change-detection drift (328 since ingestion), the hot files (change_count), the relation graph — for Tim to recognise + direct, built on the converged channel/board/comment/decision systems.
- **Not proven until Tim can see + use the analyzed data** — not DB counts.

## F — Actual data analysis (prove it does something real)
- Run the coverage audit at scale → real extractor-gap findings → fix extractors at root → re-run (needs F6).
- Query the edge graph for real insight (depends-on, grounded-by, the document/relation graph).
- Use the metadata in analysis (hottest/oldest/most-authored; churn vs interpretation staleness).

## Standing
No confidence (tags+counts) · everything reflects into ops · lean DB/IO (Docker wedged twice) · **find + fix root issues as encountered** (concurrent upgrades in flight from another session — expect drift/breakage, fix at root). Retire bespoke model-invocation (urllib) in favour of the role surface; keep deterministic ops but register them.
