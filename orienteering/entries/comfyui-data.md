---
type: terrain-entry
name: comfyui-data
register: descriptive
aliases: ["comfyui-data"]
status: unconfirmed
coverage: { files_read: 0, files_total: 36, last_read: 2026-06-26 }
relation: candidate
path: /home/tim/comfyui-data
created: 2026-05-29
last_active: 2026-06-01
size: 36G
git_remote: none
secrets: false
move_intent: none
connection_evidence: none — zero /home/tim/company references
data-of: ["[[ComfyUI]]"]
tags: [image]
---

# comfyui-data

## What it is
ComfyUI's external **model-weights + saved-workflows** store — the data dir the ComfyUI REINSTALL note points to (`~/comfyui-data/models`, ~36G). Two top-level dirs: `models/` and `workflows/`.

## How it works
Not runnable — a weights/workflows store consumed by `[[comfyui]]`.
- **`models/` subdirs:** checkpoints, controlnet, clip, text_encoders, vae, loras, animatediff_models, insightface, instantid, mimicmotion, annotators, diffusion_models, facerestore_models, densepose, upscale_models.
- **Biggest weights:** `text_encoders/t5xxl_fp16.safetensors` 9.1G; `checkpoints/realvisxlV50_v50LightningBakedvae.safetensors` 6.5G; `checkpoints/ltx-video-2b-v0.9.5.safetensors` 5.9G; `mimicmotion/MimicMotion_1-1.pth` 2.8G; `controlnet/instantid-controlnet.safetensors` 2.3G.
- **Saved workflows** (`/home/tim/comfyui-data/workflows/`, 13 JSON): 01-character-basic, 02-character-with-scene, 03-character-with-pose, 04-multiple-characters, 05-character-with-style, 06-ipadapter-faceid, 07-ipadapter-ideal-faceid, 08-ipadapter-portrait, 10-video-mimicmotion, A-upscale-and-restore, A1-enhance-reference-images, B-enhance-detail, B-enhance-with-tile. Theme: character image generation + IPAdapter/FaceID + upscaling + video.

## What it connects to
**Relation = candidate (no Company link now).** `grep -rn "home/tim/company"` over `*.json/*.md` returned **zero hits**. Connects only to `[[comfyui]]` (the app that loads it). Joins the Company only if image generation does.

## When / where
- **Path:** `/home/tim/comfyui-data`
- **created:** 2026-05-29 (dir mtime). **last_active:** 2026-06-01 (`workflows/` 2026-06-01 20:23). Oldest file mtime 2022-01-28 (a preserved old weight timestamp).
- **size:** 36G, 36 files (few but very large). **files_read:** 0 (structure + dir listings only — weight files not opened).

## Notes / evidence
Not a git repo (`git status` → fatal). Verified: dir structure, workflow listing, grep for company refs. Coverage = structural inventory only (no weight files read — they are binaries).
