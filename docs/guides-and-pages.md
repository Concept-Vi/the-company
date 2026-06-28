---
type: concept
register: descriptive
aliases: ["Guides and Pages", "the narrative-guide face", "page-as-a-face"]
tags: [company, guides, pages, registry, addresses, self-documentation, security]
relates-to: ["[[Company Map]]", "[[skills — constitution]]", "[[guides — constitution]]", "[[contracts — constitution]]"]
status: living
---

# Guides & Pages — how the Company documents itself and shows a face

> Built 2026-06-28 (Tim's commission: the Company needs to teach how to USE it, and to host rendered
> pages bound to its addresses). Three reversible, additive builds on the existing registry/address
> spine — no re-architecture. This note is the agent-register map of all three; the per-module
> constitutions + module docstrings carry the fine detail.

## The one idea
Three faces of one substrate (a registry entry / an address, projected):
- a **skill** (`skill://<id>`) — the dense instruction-unit a ROLE reads mid-task (pre-existing).
- a **guide** (`guide://<id>`) — the narrative how-to a human/agent reads to LEARN something (NEW).
- a **page** (`UnionAddressRecord.page`) — a rendered HTML face bound to an ADDRESS, served live (NEW).

These are NOT one magic primitive (the "one primitive, three faces" framing was reviewed and CUT as a
build-driver — it conflated registry-isomorphism with projection-isomorphism). They are three honest
things that SHARE the registry/address substrate. Skill and guide are deliberately separate: a guide is
read by a learner, a skill is executed by a role — keeping them separate is what closes a prompt-
injection path (see Security below).

## 1 · The guide registry (`guide://`) — the narrative-guide face
- **Home:** `guides/` (one `guides/<id>.py` per guide, self-registering — mirrors `skills/`).
  Constitution/drift-home: `guides/AGENTS.md`. Seam: `runtime/guides.py:GuideRegistry` (reuses
  `runtime/skills.py:_load_module`; own richer schema). Resolved by
  `runtime/cognition.py:resolve_address` (`guide://` branch); scheme declared in `contracts/address.py`.
- **Schema (a guide row):** `{id, content, target, grounded_from, source_hash?, label?, description?}`.
  `target` = the address the guide documents; `grounded_from` = a NON-EMPTY list of source addresses.
- **Grounding is mandatory:** an empty `grounded_from` FAILS LOUD at discovery — a guide is
  true-by-construction (authored FROM real sources) or it does not exist.
- **Carrier rule:** guides attach to non-obvious-use systems/capabilities, NOT to operational
  role-inputs (a `summarize` skill needs no how-to; the *skills system* does).
- **Seed:** `guide://using_skills` — documents the skill registry, grounded in `skill://summarize` +
  the skills constitution + `runtime/skills.py`.
- **Authoring:** `create(kind='guide', spec=…)` (live, gated) — the same render→gate→write→commit→
  rediscover path as `create_skill` (`runtime/suite.py:create_guide`, `runtime/authoring.py`).

## 2 · The guide-author — the practice that keeps guides TRUE
`runtime/guide_author.py` — a generator that authors guides FROM sources, with the gates in code:
- **abort-on-cold** — composes only from sources that resolve to content; none → RAISE.
- **freshness by source-hash** — `compute_source_hash` / `is_stale` / `staleness_report`. A guide
  records the hash of its content-resolvable sources; when they change, it is STALE and due re-author.
  (Reuses the hash-diff IDEA, deliberately not the embedding-reconcile fn — that is the open
  no-auto-reindex concern.)
- **propose-diff, never clobber** — re-authoring an existing guide DEFAULTS to proposing the new source
  (writes nothing); a human-edited guide is safe. Overwrite is an explicit opt-in.
- **human-read guides ONLY** — it never authors role-executed skill `content` (the security boundary).
- **model-compose is injected** (`model_composer` = a role-resolved model, cognition-is-role-resolved).
  Composing on a real model is the lead-verify slice (not yet run; see Status).

## 3 · Page-as-a-face (`UnionAddressRecord.page`) — the strong artifact
`runtime/page_face.py` + the additive `page` field (`contracts/ui_info.py`, SCHEMA_VER 3).
- A page is a FIELD an address accumulates (the accumulation idea), not a flat dead copy. The page
  CONTENT lives at a content-addressed source (`store.put_content(html) -> cas://`); the binding
  (address → {source, title}) lives in the `design/_system/page_bindings.json` overlay.
- `attach_page` (store + bind) · `page_for` (read) · `render_page` (pure: resolve → headers+body) ·
  `serve` (the live separate-origin server).
- Beats the claude.ai artifact: bound to an address (discoverable/linkable), live/regenerable, and it
  references shared DNA once instead of inlining. Generalises "the gallery is the visible surface."

### Security posture (built IN — the 3-review CRITICALs, mitigated by construction)
Serving stored HTML naively had two CRITICALs: same-origin privilege escalation (a page fetching the
control plane) and the bridge's missing transport auth. Page-face is safe without waiting on auth:
- **Separate origin** — `PAGE_PORT` 8774, NEVER the bridge control plane (8770) / supervisor (8771).
  A browser cannot cross-origin `fetch` the control plane.
- **No-script CSP** — `default-src 'none'`, no `script-src`, `connect-src` none: no JS executes and no
  network call can be made FROM a page. Kills escalation + XSS by construction (pages are static
  HTML+CSS design artifacts, so this costs nothing).
- **Scheme allow-list** — a page `source` must be `cas://`/`blob://` (immutable, system/Tim-authored);
  arbitrary/`run://` sources are REFUSED 403 fail-loud.
- **Fail-loud** — no binding → 404; disallowed scheme → 403.
- **Auth** (who may reach the port) rides the later **Supabase** move; the separate-origin + no-script
  CSP are the load-bearing mitigations now and hold regardless of auth.

## Status (honest)
- **Verified by execution:** `guides_acceptance` 27/27 · `guide_author_acceptance` 16/16 ·
  `page_face_acceptance` 16/16 · `skills_contexts` 34/34 · `conv_howto` 22/22 · `ui_registry` pass ·
  `roles_acceptance` 39/39 · `cognition_governance` 43/43.
- **Now GREEN FOR REAL (the former lead-verify items, run live):**
  (a) a live `create_guide` commit — `36dd56b [self-apply]`.
  (b) the guide-author's model-compose on a REAL model — `guide://using_corpus_pipeline` (5118 chars,
      grounded in `skill://corpus_pipeline` + `map_reduce_composition` + `patterned_visibility`),
      composed on the live model Qwen3.5-4B at :8000 via the `guide_author` role.
  (c) the page-face `serve` against a real HTTP request — 200 + no-script CSP + correct body, 404 loud.
- **Three pre-existing reds — investigated + RESOLVED (commit baacd80):** `skills_contexts` blob://
  (graduated, dropped from the unbuilt loop), `conv_howto` A2/D2 (corpus hit ~100% howto coverage →
  fixture now derived dynamically + fails loud if unsatisfiable), `ui_registry` orphans (regex now
  skips `${…}` dynamic refs; `ui://tray` registered in `addresses.json`).
- **Follow-ups:** wire a `company` page-face service (systemd, separate port) + an MCP `page`/`attach`
  verb; generate more real guides on more domains — domain #1 = the DNA design system once it is local
  (read via the filesystem, not the lead-only DesignSync tool).

## Read next
[[guides — constitution]] · [[skills — constitution]] · `runtime/guide_author.py` · `runtime/page_face.py`
