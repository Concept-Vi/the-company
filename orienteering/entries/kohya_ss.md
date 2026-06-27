---
type: terrain-entry
name: kohya_ss
register: descriptive
aliases: ["kohya_ss", "Kohya's GUI", "kohya-ss"]
status: unconfirmed
coverage: { files_read: 1, files_total: unknown, last_read: 2026-06-26 }
relation: candidate
path: /home/tim/kohya_ss
created: 2022-10-30
last_active: 2025-06-23
size: 11G
git_remote: https://github.com/bmaltais/kohya_ss.git
secrets: false
move_intent: none
connection_evidence: none — zero /home/tim/company references
tags: [image]
---

# kohya_ss

## What it is
"Kohya's GUI" — a Gradio-based GUI and CLI for **training diffusion models** (Stable Diffusion). Trains **LoRA, Dreambooth, fine-tuning, and SDXL**, wrapping `kohya-ss/sd-scripts`. Source: `/home/tim/kohya_ss/README.md:8` ("a GUI and CLI for training diffusion models").

## How it works
Entry points (confirmed present): `/home/tim/kohya_ss/gui.sh`, `/home/tim/kohya_ss/gui-uv.sh`, `/home/tim/kohya_ss/kohya_gui.py`, plus `setup.sh` / `setup-runpod.sh`.

## What it connects to
**Relation = candidate (no Company link now).** `grep -rn "home/tim/company"` over `*.py/*.md/*.json` (excl venv/node_modules/.git) returned **zero hits**. Standalone image-model training toolkit; plausibly joins later if the Company trains its own LoRAs/identity models, but no committed intent.

## When / where
- **Path:** `/home/tim/kohya_ss`
- **created:** 2022-10-30 (earliest commit — upstream history, not Tim's clone date).
- **last_active:** 2025-06-23 (latest commit `v25.2.1`).
- **size:** 11G. **files_total:** not counted (huge tree incl venv). **files_read:** 1 (README.md).

## Notes / evidence
Git remote points at upstream `bmaltais/kohya_ss` (not a Concept-Vi fork). Verified: README.md, entry-point existence, grep for company refs. Coverage thin — describing purpose only.
