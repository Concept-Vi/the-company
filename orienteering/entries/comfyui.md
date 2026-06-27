---
type: terrain-entry
name: ComfyUI
register: descriptive
aliases: ["ComfyUI", "Comfy"]
status: unconfirmed
coverage: { files_read: 2, files_total: unknown, last_read: 2026-06-26 }
relation: candidate
path: /home/tim/ComfyUI
created: 2026-05-28
last_active: 2026-06-06
size: 636M
git_remote: https://github.com/comfyanonymous/ComfyUI.git
secrets: false
move_intent: none
connection_evidence: none — zero /home/tim/company references
depends-on: ["[[comfyui-data]]"]
tags: [image]
---

# ComfyUI

## What it is
"ComfyUI — the most powerful and modular AI engine for content creation" — a node-graph image/video generation app. Source: `/home/tim/ComfyUI/README.md`.

## How it works
Entry point: `/home/tim/ComfyUI/main.py` (confirmed present). The model weights it runs on live separately in `[[comfyui-data]]` (`~/comfyui-data/models`, ~36G).

**venv removed.** `/home/tim/ComfyUI/REINSTALL_VENV.md`: the venv `./.venv` was deleted 2026-06-06 to reclaim ~7.3G "because ComfyUI was not in active use. Nothing else was touched — your models in `~/comfyui-data/models` (~36G), custom nodes, and all code remain intact." Recreate via `python3.12 -m venv .venv` + `pip install -r requirements.txt`. Confirmed gone: both `/home/tim/ComfyUI/venv` and `/home/tim/ComfyUI/.venv` return "No such file or directory".

## What it connects to
**Relation = candidate (no Company link now).** `grep -rn "home/tim/company"` returned **zero hits**. Connects only to `[[comfyui-data]]` (its weights/workflows store). Standalone image-gen app; plausibly joins later if the Company drives image generation, but no committed intent.

## When / where
- **Path:** `/home/tim/ComfyUI`
- **created / last_active:** shallow clone — earliest AND latest commit both `2026-05-28 01:03:28 -0700` (single commit in history; not a meaningful install date). Effective last activity: venv removed 2026-06-06 (dormant since).
- **size:** 636M (code only; weights in comfyui-data). **files_total:** not counted. **files_read:** 2 (README.md, REINSTALL_VENV.md).

## Notes / evidence
Git remote = upstream `comfyanonymous/ComfyUI` (not a fork). Verified: README.md, REINSTALL_VENV.md, venv-absence, grep for company refs.
