---
type: terrain-entry
name: company-scan
register: descriptive
aliases: ["company-scan"]
path: /home/tim/company-scan
relation: external
kind: work
status: unconfirmed
created: 2026-06-01
last_active: 2026-06-01
size: 9.4M
coverage: { files_read: 4, files_total: 12, last_read: 2026-06-26 }
git_remote: none
derived-from: ["[[corpora]]"]
produced: ["[[wizard-run-1]]"]
relates-to: ["[[mcp-mining]]"]
secrets: false
move_intent: none
scanned_tree: /mnt/c/Users/Workstation001/Documents/Claude/Projects
files_scanned: 19361
target_project: ElevenLabs Wizard
model: "cyankiwi/Qwen3.5-4B-AWQ-4bit @ :8000 (12 workers)"
outputs: ["PROJECTS-LANDSCAPE.md", "DESIGN-DIGEST.md"]
tags: [model]
---

# company-scan

## What it is
A **forensic two-pass local-4B scan** (run 2026-06-01) of Tim's Windows project tree that recovered the design of the abandoned **ElevenLabs Wizard** project. Pass 1 cast a wide net — classify *every* source/text file under the tree by WHAT IT IS (form + domain + which project) with no relevance filter — producing `PROJECTS-LANDSCAPE.md` (a terrain map of **19,361 files**). Pass 2 targeted the Wizard specifically and synthesised `DESIGN-DIGEST.md`.

Evidence: `scan_projects.py` docstring (*"Scan EVERY source/text file under the Projects tree with the local 4B… Wide net first… this is how we find everything"*) and its `TARGET` block describing the Wizard (voice-first agent-driven campaign builder: ElevenLabs TTS/voice-clone/conversational-AI + Supabase + runtime-generative UI driven by a provider-agnostic capability registry). `PROJECTS-LANDSCAPE.md` reports "Files mapped: 19361" with kind/domain breakdowns.

## How it works
- `scan_projects.py` — pass-1 scanner: walks `ROOT=/mnt/c/Users/Workstation001/Documents/Claude/Projects`, sends each file (capped 24k chars, ~6k tokens, whole-file for most) to the local 4B at `http://localhost:8000/v1/chat/completions` with 12 worker threads, writing `scan_results.jsonl` incrementally (durable, resume-safe, fail-loud per file).
- `build_index.py` — indexing helper.
- `extract_design.py` → `design_extracts.jsonl` (759K) — pass-2 design extraction targeted at the Wizard.
- `synth_design.py` → `DESIGN-DIGEST.md` — final synthesis.
- Logs: `scan.log`, `design.log`. There is a `scan_results.v1-broad.jsonl` (earlier broad pass) alongside the main `scan_results.jsonl` (8.2M).

## What it connects to
- **[[wizard-run-1]]** — the direct successor: this scan *recovered* the Wizard design; wizard-run-1 (days later, 2026-06-04+) then ran the full project→product pipeline prototype on that same Wizard corpus.
- **[[mcp-mining]]** — sibling local-4B-at-scale extraction prototype from the same week; same model, same fan-out-workers + JSONL-durable pattern, different corpus (project files vs conversations).

## When / where
Created and last active 2026-06-01 (all mtimes 10:30–12:57 that day). Path `/home/tim/company-scan`, 9.4M, 12 files (+ `__pycache__`). No git. Read 4 of 12 (scan_projects.py, PROJECTS-LANDSCAPE.md head, directory listing, DESIGN-DIGEST sized); the large `.jsonl` result files were sized, not parsed.

## Notes / evidence
- State **dormant**: a finished one-day forensic run. The two `.md` outputs are the deliverable; the `.jsonl` files + scripts are the working substrate.
- The scanned tree is on the **Windows side** (`/mnt/c/...`), not in this folder.
- Coverage caveat: I read the landscape map and scanner; I did not parse `design_extracts.jsonl` or read `DESIGN-DIGEST.md`/`synth_design.py` in full.
