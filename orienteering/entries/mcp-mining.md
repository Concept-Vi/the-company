---
type: terrain-entry
name: mcp-mining
register: descriptive
aliases: ["mcp-mining"]
path: /home/tim/mcp-mining
relation: external
kind: work
status: unconfirmed
created: 2026-05-30
last_active: 2026-05-31
size: 59M
coverage: { files_read: 5, files_total: 17, last_read: 2026-06-26 }
git_remote: none
derived-from: ["[[corpora]]"]
relates-to: ["[[wizard-run-1]]", "[[company-scan]]"]
secrets: false
move_intent: none
pipeline: extract → 4B-read (vLLM :8000) → bge-m3 embed (vLLM :8001) → cluster → name/dialectic (4B + deepseek-v4-pro cloud)
output_vault: /mnt/c/Users/Workstation001/Documents/Conversation-Mind
models: ["cyankiwi/Qwen3.5-4B-AWQ-4bit @ :8000", "BAAI/bge-m3 @ :8001", "deepseek-v4-pro:cloud"]
run_status: finished (status.json phase=enrich-done; run.log "DONE: 151 subtopics, 5 deep-dives")
tags: [memory, model, embedding]
---

# mcp-mining

## What it is
A **completed overnight conversation-mining pipeline** (run 2026-05-30 → 31) that read all of Tim's Claude Code chat history and synthesised it bottom-up into an emergent Obsidian "Conversation-Mind" vault on the Windows side. Despite the folder name, it is **not about MCP** — `orchestrate.py:5` states the design explicitly: *"NO predefined categories/questions. NO MCP framing. Synthesis bottom-up & bounded. NO Gemini."* The name is a misnomer left over from the launch context; the actual deliverable is an idea-map of Tim's thinking, quoted verbatim with provenance.

Evidence: `orchestrate.py` docstring (the "full spec, robust model strategy"), `tim_messages.jsonl` (18.9M of extracted source messages), `extracted.jsonl` (2.1M of processed units), `embeddings.npy` (38M numpy array), `clusters.json` (38K), `status.json` (`phase: "enrich-done"`).

## How it works
A single self-directing orchestrator (`orchestrate.py`, 16K) runs a phased pipeline, holding **exactly one vLLM model resident per phase** (a deliberate fix after a 35B OOM failure — the local 35B was dropped because it needs 17.2 GiB and doesn't fit):
- **Phase A** — local 4B (`cyankiwi/Qwen3.5-4B-AWQ-4bit`, vLLM `:8000`) reads every message.
- **Phase B** — `BAAI/bge-m3` (vLLM `:8001`) embeds (4B stopped first to free VRAM).
- **Phase C** — clustering in code.
- **Phase D/E** — 4B for volume naming; **deepseek-v4-pro:cloud** for the heavier interpretive/dialectic steps (cloud = no local resource cost), with 4B as fallback.

It manages models via `systemctl --user start/stop` and health-polls `/v1/models`. It is checkpointed/resumable via `status.json`. Companion scripts: `enrich.py` / `enrich2.py` (perspective + dialectic enrichment), `regen_dialectics.py`, `extract_tim_prose.py`. Output is written to the vault `/mnt/c/Users/Workstation001/Documents/Conversation-Mind` (Windows-side Obsidian).

## What it connects to
- **[[corpora]]** — same class of input (Tim's session history), though this run read directly from `~/.claude/projects` rather than the curated corpora copy.
- **[[wizard-run-1]]** and **[[company-scan]]** — sibling hand-run prototypes of the same era exploring local-4B-at-scale + embedding + cluster pipelines; this is the conversation-corpus instance of that pattern, where they are the project-corpus instances.
- The one-model-per-phase VRAM discipline prefigures the Company's later model-loadout/resource-manager thinking.

## When / where
Created 2026-05-30, last active 2026-05-31 (all file mtimes 22:54–09:53 across those two days). Path `/home/tim/mcp-mining`, 59M, 17 files. No git. Read 5 of 17 (orchestrate.py, status.json, run.log + directory listing of the rest); the large `.jsonl`/`.npy` data files were sized but not parsed.

## Notes / evidence
- State **dormant**: a finished run, not a live service — `status.json` shows `phase: enrich-done` and `run.log` ends `"DONE: 151 subtopics, 5 deep-dives -> …/Conversation-Mind"`.
- The output vault lives on the **Windows side**, not in this folder — the 59M here is the working substrate (messages, embeddings, clusters, logs), not the deliverable.
- Coverage caveat: I did not open `enrich.py`/`enrich2.py`/`regen_dialectics.py` line-by-line, nor inspect the produced vault; classification rests on the orchestrator docstring + status/log evidence.
