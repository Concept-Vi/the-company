---
type: terrain-entry
name: cognitive-framework
register: descriptive
aliases: ["cognitive-framework"]
status: unconfirmed
coverage: { files_read: 12, files_total: 6553, last_read: 2026-06-26 }
relation: resource
kind: data
path: /home/tim/.cognitive_framework
created: 2026-03-11
last_active: 2026-03-11
size: 27M
git_remote: none
secrets: false
move_intent: none
prospected-for: ["[[company]]"]
relates-to: ["[[company]]", "[[universal-mechanics]]", "[[creations]]", "[[docs]]", "[[graph-editor]]"]   # company edge = dataflow ancestor of the compositional engine
era: pre-Company prototype
themes: [compositional-dataflow, flow-block-execution, cognitive-process-modeling, corpus-ingestion, projection-roles, runtime-capability-honesty]
concepts: [thought-as-blocks, canonical_flow_graph_v2, compositional_meta_language, thinking-mode-to-executor-kind, typed-edges, source-ref-provenance, layer1-timeline-pipeline]
tags: [memory, model]
---

# cognitive-framework

## What it is
The persisted **store** of an earlier cognitive-process execution system — a direct conceptual ancestor of the Company's compositional dataflow engine. It modeled a unit of thinking as a composition of 10 typed "blocks", wired blocks/thinking-modes into a directed graph ("flow"), and ran that flow over an ingested corpus (here a Slack history) using local-Ollama LLM executors. There is **no code here** — this is the data store of a system whose engine lives elsewhere.

Top-level (`/home/tim/.cognitive_framework/stores/`): `blocks/blocks.db` (sqlite, 10 rows), `flow_definitions/items/` (21 flow graphs), `templates/items/` (3 presets), `import_artifacts/items/` (6528 json — the ingested Slack corpus, the 27M bulk), and four **empty** output stores (`execution_records/`, `structured_outputs/`, `generated_artifacts/`, `output_artifacts/`) plus empty `graphs/`. The snapshot captures the design + ingested data but no preserved run results.

## Key ideas worth mining
The data model, concretely:
- **Thought-as-composition** — `blocks.db` holds 10 foundational typed blocks: `thinking_mode`, `goal`, `purpose`, `focus`, `content`, `conditions`, `constraints`, `modifiers`, `output`, `progression`. Each `structure` is a typed-field JSON schema (e.g. thinking_mode = `{thinkingMode: enum required, modeParameters: object, processingInstructions: array}`). A structured-output contract for "a thought."
- **One canonical graph, many projection roles** — every flow declares `projection_roles: [composer, executor, viewer, reviewer, reconfigurer]` over `graph_format: canonical_flow_graph_v2` / `canonical_model: compositional_meta_language`. The same graph viewed/edited/run/reviewed through different role lenses. Prefigures the Company's role-resolved cognition + operator/reviewer surfaces.
- **Runtime-subset / capability honesty** — each flow self-documents `runtime_subset`/`runtime_capability`: which nodes/modes are *executable* vs *preserved-only*, with a per-node `reason` ("Thinking mode is preserved in the canonical graph but not executed by the current runtime subset"). A built-in "this part isn't wired yet" ledger — ancestor of the Company's no-silent-failure / honest-status discipline.
- **Thinking-mode → executor_kind dispatch** — modes are abstract; they resolve to concrete executors: `llm_structured_extract → llm_chat_structured`, `llm_prompt_transform → llm_chat_text`, `llm_reduce_or_merge → llm_chat_reduce`, `schema_generation → legacy_schema_generation`. AI nodes dispatched by kind — ancestor of the Company's code-node/AI-node dispatch.
- **Typed edges as semantics** — `data_flow | control_flow | condition_flow | parameter_mapping`; edges carry meaning, not just topology.
- **Content-addressed, provenance-pinned ingestion** — every corpus artifact links to `source_refs:[{file_id, relative_path, file_hash(sha256)}]`. The extract-once / source-ref pattern of the current Dragnet/Recall substrate.
- **Layer-1 / timeline pipeline** — the richest executable flow (`flow-b8bbe0fd.json`, `can_execute: true`) is a 5-node `data_flow` chain: `artifact_selector → batch_input_mapping → layer1_generation → timeline_projection → timeline_aggregation`. A concrete reduce/rollup cascade over a corpus.

## How it relates conceptually to the Company
A **conceptual ancestor of the Company's typed compositional dataflow engine** (code + AI nodes wired by structured-output contracts), explicit and structural: flows = graphs of typed nodes + typed edges → the Company's compositional graph (`flows`, `run_graph`, cascades); thinking_mode→executor_kind → AI-node/code-node resolution by kind; 10 blocks as a structured-output contract → everything-is-a-typed-variable wiring; projection_roles → role-resolved cognition + operator/reviewer surfaces; runtime_subset honesty → no-silent-failure + honest-status laws; source_refs hash-pinning → the Dragnet extract-once schema-first substrate. **Not a replacement and not the engine** — a prior, simpler, single-corpus generation whose good parts were carried into the centre. `relation: resource`.

## When / where
Created and last active 2026-03-11 (all store dirs + flow defs mtime that day; corpus ingested 2026-03-10; template metadata dates to 2025-08-24). Path `/home/tim/.cognitive_framework`, 27M, 6553 files, no git. Read 12 of 6553.

## Notes / evidence
- Read: `blocks.db` (full schema + 10 rows), 3 flow_definitions in full (`flow-08b16876`, `flow-b8bbe0fd`, plus decision-node scan across all 21), 1 template (`quick_analysis.json`), ~4 import_artifacts; type-distribution sampled across 800 of the 6528 corpus files.
- Corpus = a Slack export ("TheOneProlific", May 2024–Jul 2025). Type distribution (800 sample): `slack_relationship` 491, `slack_message` 164, `slack_thread` 118, `source_file` 23, `slack_channel` 4. Relationships are edges (e.g. `message_authored_by_user / from_id / to_id`).
- The 4 output stores confirmed **empty** (0 files) — design + ingested data preserved, run results not.
- Secrets: **none** — verified no credentials (the two "secret"/"api_key" grep hits are ordinary words inside Slack message text).
