---
type: terrain-entry
name: wizard-run-1
register: descriptive
aliases: ["wizard-run-1"]
path: /home/tim/company/migration-pending/wizard-run-1
relation: external
kind: work
status: unconfirmed
created: 2026-06-04
last_active: 2026-06-09
size: 59M
coverage: { files_read: 4, files_total: 57, last_read: 2026-06-26 }
git_remote: none
derived-from: ["[[corpora]]", "[[company-scan]]"]
relates-to: ["[[mcp-mining]]"]
secrets: false
move_intent: done
corpus: ElevenLabs Wizard project (~5,000 real files)
substrate: wizard.db (SQLite, 1.6M) + registries/{projections,markdown_lifters,prompts}.json
cascade: local 4B (bulk, structured-output) → embeddings → cluster/dedup → cloud reasoning model
prototype_of: Company engine node-types / tools (project→product pipeline, by hand)
tags: [model, embedding, memory]
---

# wizard-run-1

## What it is
A **hand-run prototype** (2026-06-04 → 09) of the **project→product pipeline** — Tim's repeatable process for turning abandoned/unfinished projects into deployed products — executed for real against the **ElevenLabs Wizard** corpus (~5,000 files). It is explicitly framed as a *prototype of would-be Company engine node-types and tools*: bulk local-4B concurrency with enforced structured output, embeddings, clustering/dedup, a projections registry, a SQLite substrate, and a local→cloud reasoning cascade — all driven by hand, looking at each output to steer the next move.

Evidence: `SESSION_FIELD_REPORT.md` (28.9K, first-person recount) — *"actually running an early by-hand version of the pipeline on a real corpus — the ElevenLabs Wizard project — to discover how the process really behaves. That run **is** this report."* It is self-described as **evidence from one real run, not a settled spec**, with the reframes and dead-ends called out as "signal: they tell you what NOT to rebuild."

## How it works
The folder holds the full pipeline as loose scripts + their outputs (57 files):
- **Scan / extract** — `scan.py`, `extract.py`, `code_extract.py`, `target_extract.py` → `scan.jsonl`, `extract.jsonl`, `code_extract.jsonl`, `target_extract.jsonl`; manifests `manifest_full.txt`, `manifest_design_code.txt`.
- **Embed / cluster / dedup** — `embed.py` → `embed.jsonl` (46M), `cluster.py` / `latent_cluster.py` → `clusters.txt`, `dedup.py`, `carve.json`.
- **Aggregate** — `agg_*` / `clean_*` txt files (components, decisions, gaps_or_contradictions, latent_or_abandoned, open_questions).
- **Form survey** — `form_survey.py` → `form_survey.jsonl` (1.2M); `forms.py`.
- **Capture / projections** — `capture.py` / `capture2.py`, `lift.py`, `db.py` → **`wizard.db`** (SQLite substrate, 1.6M; two prior snapshots `*.capped-ambiguous-*` and `*.preStageFix-*` kept side-by-side) and **`registries/`** (`projections.json` 4K, `markdown_lifters.json`, `prompts.json`).
- **Fleet** — `fleet.py` (model-concurrency driver); logs `serve_scan.log`/`serve_scan2.log`, `restore_4b.log`, `restore_embed.log`.
- Docs: `BUILD_PLAN.md`, `FINDINGS.md`, `SESSION_FIELD_REPORT.md`.

## What it connects to
- **[[company-scan]]** — the upstream: company-scan *recovered* the Wizard design (2026-06-01); this run then *ran the pipeline* on that corpus (2026-06-04+).
- **[[mcp-mining]]** — sibling local-4B-at-scale prototype; this one is the project→product / capture-and-projection instance.
- **The Company engine** — the report is addressed to whoever builds **MCP tools for model-concurrency + embedding runs**; the node-types, projections, cascade economics, and "render-not-judge / look-at-output-first" disciplines here are inputs to the engine. `move_intent: into-company` — its substrate + method are meant to fold into the Company later, alongside the recollection work.

## When / where
Created 2026-06-04, last active 2026-06-09 (SESSION_FIELD_REPORT touched 2026-06-09; `wizard.db` mtime 06-04 21:22; folder mtime 06-26 reflects the recent recollection work touching it). Path `/home/tim/company/migration-pending/wizard-run-1`, 59M, 57 files. No git. Read 4 of 57 (SESSION_FIELD_REPORT head, scan_projects-class scripts via company-scan, registries/db listing, directory listing); the large `.jsonl`/`.txt`/`.db` data were sized, not parsed.

## Notes / evidence
- State **dormant** (a finished hand-run), but `move_intent: into-company` — the substrate (`wizard.db`, `registries/`) and method are designated to migrate into the Company **later, with the recollection work**, not now.
- The field report is explicit that it is **out of date on current app/engine state** — treat it as deep on one layer (model-concurrency / capture / embeddings), not current on architecture.
- Coverage caveat: classification rests on the field report + build plan framing + the file inventory; I did not parse the data files or read `FINDINGS.md`/`BUILD_PLAN.md` in full.
