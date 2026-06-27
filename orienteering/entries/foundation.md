---
type: terrain-entry
name: foundation
register: descriptive
aliases: ["foundation", "~/foundation (former path)"]
path: /home/tim/company/foundation
relation: external
kind: data
status: unconfirmed
created: 2026-05-27
last_active: 2026-06-26
size: 756K
coverage: { files_read: 8, files_total: 60, last_read: 2026-06-26 }
git_remote: none
purpose: the Company's memory of its own origins — verbatim founding conversations + synthesized doctrine
part-of: ["[[company]]"]
data-store-for: ["[[company]]"]
secrets: false
move_intent: done
language: markdown
tags: []
---

# foundation

## What it is
The Company's memory of its origins: the verbatim founding conversations between Tim and the agents (`exchanges/`) plus the doctrine synthesized from them (`system/`, `models/`, `operations/`, and `TIM.md`).

Evidence (Observed): `exchanges/` holds numbered verbatim transcripts `01-questions.md` … `20-the-convergence-object.md`. `system/` holds `principles.md`, `architecture.md`, `README.md`. `models/` is a per-model doctrine index (`bge-m3.md`, `jina-embeddings-v4.md`, `qwen3-embedding-8b.md`, … + `_models-index.md`). `operations/` holds runbook doctrine (`vram-budget.md`, `ports.md`, `systemd-services.md`, `model-swap.md`, … + `_operations-index.md`). 60 files, 756K, all markdown.

## How it works
Static markdown — no service. It is READ by live Company code: `/home/tim/company/nodes/model_of_tim.py` opens `~/company/foundation/system/principles.md` (Observed: line 16 `os.path.expanduser("~/company/foundation/system/principles.md")`; the docstring names it "the synthesised principles/laws … Tim's own statements of how"). So foundation is not just archive — it is a live input to the model-of-Tim node.

## What it connects to
`[[company]]` — it now lives INSIDE the folder. MOVED IN on 2026-06-26 from the former `~/foundation` (`move_intent: done`). The live binding `nodes/model_of_tim.py` reads `system/principles.md`, making foundation a doctrine source for the engine, not a detached corpus.

## When / where
Created 2026-05-27 (earliest file `exchanges/01-questions.md`, mtime 2026-05-27 15:21). Path `/home/tim/company/foundation`, 756K, 60 files. last_active 2026-06-26 reflects the MOVE/copy timestamp (newest file mtime 2026-06-26 18:40) — NOT necessarily fresh content authorship; the doctrine itself spans 2026-05-27 onward.

## Notes / evidence
Read: top-level + `exchanges/`, `system/`, `models/`, `operations/` listings; traced the `model_of_tim.py` binding via grep. NOT read: the bodies of the 60 doctrine/transcript files (listing-level catalogue only). Caveat: mtimes were reset by the 2026-06-26 move, so `last_active` is move-date, not edit-date.
