---
type: constitution
register: prescriptive
module: modes
aliases: ["modes — constitution"]
tags: [company, constitution, modes, presence, rhm]
status: living
---

# modes/ — the file-discovered presence-MODE registry

**Is:** the OPEN, file-discovered registry of the Right-Hand-Man **presence modes** — one `modes/<id>.py`
per mode declaring a module-level `MODE` dict. Discovered by `runtime/modes_registry.discover_modes`
(mirrors `roles.py` / `mode_detection_rules.py`: os.listdir → importlib, fail-loud, id == filename stem).
Replaced the former hardcoded `MODE_REGISTRY` literal in suite.py (WS0, 2026-06-28) — modes are now a
starter set you grow by dropping a file, not a code edit (Tim: "open set, all in registries, adjustable").

**A mode declares (the axis schema):** `order` (int — sequencing; modes are order-bearing, lower first) ·
`label` · `directive` (the behavioural prose injected into the RHM prompt) · `resolution`
{strata · howto_detail · budget} (context-gather) · `consent` (offer|act|none) · `grain` · `shape` ·
`stage` (reply shaping) · `live` · `reserve_r` · `per_role_ctx` · `main_ctx_tokens` (activation budget) ·
`brain_config` (the loadout the mode wants — WS1 links this to a loadout class). `subtypes` optional.
`order` is discovery-only — stripped from the decl so each entry is byte-for-byte what every derived view
(MODE_SPECS / MODES / MODE_DIRECTIVES / PART_GRAIN / ACTIVATION_ALLOCATION) reads.

**The id is the filename stem VERBATIM** — hyphens kept (`text-only`, `watch-and-react`, `decide-for-me`
are real mode ids the dial/set_mode validate). 

**Where new things go:** a new mode = a new `modes/<id>.py` with a `MODE` dict (give it an `order`); it's
discovered + on the dial. Edit a mode = edit its file. The 8 shipped are a STARTER SET — none final.

**Never:** re-hardcode a mode in a class dict (the thing WS0 retired) · drop a required axis (fail-loud) ·
collide an id. Discovery is at startup (a restart picks up changes); live rediscover is a noted follow-on.
