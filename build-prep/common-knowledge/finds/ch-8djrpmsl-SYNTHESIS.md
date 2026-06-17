# UNION SYNTHESIS — the COMPANY-layer RESOLUTION SUBSTRATE (fork, ch-8djrpmsl)

```
trust: fabric-derived. author: ch-8djrpmsl (fork). date: 2026-06-17.
purpose: Tim's LAW (scan-before-build) — my stream's scan, posted for the lead to assemble into the union.
method: 4 parallel scan sub-agents (address-spine · models#71 · loadable-brain/clones/fabric · history+principles),
        arbitrated against fork's own first-hand build knowledge (verification-states are mine, not the agents').
```

## WHAT MY AREA IS
The **resolution substrate** — the floor the other three areas (DNA / factory / gallery) resolve THROUGH. It is
ONE substrate with three faces of the same act ("resolve a pointer into the thing it names"):
1. **ADDRESS resolution** — `resolve_address` over a 16-scheme grammar → `territory_for` composes any address
   into brain-ready context. (Everything-is-an-address.)
2. **MODEL resolution** — `resolve_model(intent)` picks WHICH model answers (clone · role · capability). (#71.)
3. **BRAIN loading + the clone fleet + the fabric** — the loadable Claude Code brain bound AT an address;
   clones as addressed channel members; the cross-session coordination mesh.

Tim's frame names it exactly: "#71 + the address spine = THE COMPANY layer — the floor everything resolves
through." DNA-identity, factory-types, gallery-scenes are three views; the Company is what they pick models +
resolve addresses through.

## THE PRINCIPLES (the laws this stream obeys)
**Tim's standing laws (the spine):**
- **Registry-is-truth** — which model/tier satisfies an intent lives in `model_capabilities.json` + role
  `requires`; re-tiering is a DATA edit, zero engine code.
- **ONE resolver, not many (no second router)** — every selection routes through the one thing that exists
  (`resolve_address`, `resolve_model`, `territory_for`); a 2nd router/composer is the anti-pattern #71 unifies away.
- **Met-at-the-address / file-disjoint** — parts meet at `contracts.address`; fork PROPOSES a diff, the owner
  applies (never edit another stream's hot file). The bridge handoffs are proposed diffs, not fork edits.
- **Fail-loud, no silent fallback** — an unresolvable intent RAISES + surfaces a Notice/Gap; never a silent wrong model.
- **Verify-by-use / no-green-paint** — GREEN only via a real run/spawn/resolve (the `run://` trail, the spawned
  process's model), never code-reading. Pattern-matching is not verification.
- **Extraction-vs-judgment** — the 4B EXTRACTS (fan-out, cheap, many); a wide reasoner JUDGES/synthesizes
  (central, few). Encoded as capability TIERS, never hardcode.
- **Clone model pick by context size** — kimi-k2.7-code:cloud (256K) default; deepseek-v4-flash:cloud (1M) when
  est. context > kimi window; never auto -pro (512K); explicit non-kimi honored.

**Laws sharpened/discovered IN this stream (the new value):**
- **★ The FLOOR + `satisfied` (no-green-paint, advisor-caught)** — `roles.resolve_binding` does NOT raise when no
  provider matches a role with a `default_model`; it returns the DEFAULT (`provider="default", satisfied=False`),
  the brain floor. So a re-tier can "look resolved" while silently floored to the 4B. `resolve_model` surfaces
  `satisfied` verbatim — callers assert a REAL match, NOT a non-empty model. **"Assert satisfied, not truthiness."**
- **★ Registry-is-truth OVER spec-prose** — the spec said kimi provides `[wide,code]`; neither is a CAPABILITY_TAG
  (would fail discovery's ⊆ check). Grounded provides from live `ollama show` = `[chat,json,tools,thinking,
  reasoning,vision]`. The live registry beats the prose.
- **★ The brain is LOADABLE per SCALE (D2 resolved)** — FOCUS (the Company's own RHM) at overlord altitude; PANEL
  (`run_turn`, real Claude Code) at drill; SPAWN dropped (reuse-don't-parallel). The composer is BRAIN-AGNOSTIC:
  scale decides FOCUS vs PANEL at HANDOFF, not in `territory_for`.
- **★ Addressed-state = ONE projection** — the UI is the rendered projection of one addressed state; "there are no
  modes — the mode is an argument to resolution" (`resolve(address × frame × mode-template) → surface`),
  structurally guaranteed because an address holds nothing presentational.
- **★ The address is BIDIRECTIONAL** — because every element/section/mode is an address in one grammar, the brain
  navigates the interface through the EXACT grammar Tim does. Tim directs AT an address; the brain loads AT that
  address — they co-locate. "AI addressable-WITH-Tim at each part," not "AI embedded in each part."
- **★ The degrade contract has THREE failure cases** (advisor-hardened) — (1) non-address → `territory_for` RAISES;
  (2) non-resolvable scheme → identity noted-absent, relations still tried; (3) resolvable scheme + NONEXISTENT
  record → `resolve_address` raises → guarded to noted-absent. `territory_prose` (bridge-facing) NEVER raises.
- **Model backend = OLLAMA-NATIVE :11434, not litellm :4100** — CC (Anthropic format) goes direct to ollama's
  Anthropic endpoint; litellm :4100 is the fabric's OWN OpenAI-format cognition (leave it). kimi via :4100 → 401.

## THE SHAPE (the unbroken circuit)
```
ADDRESS (scheme://id, 16 schemes)
  → resolve_address(store, addr)         9 resolvable (run·cas·skill·context·session·cap·board·clone·mind)
                                          + 6 deferred (blob·vec·code·exchange·file·project → raise) + bare-name
  → territory_for(address)               per-scheme IDENTITY leg · CORPUS-RECORD leg · CONTEXT leg (ui://) ·
                                          RELATIONS leg (H1.2 edges, any scheme) — each guarded, degrade-clean
  → territory_prose(address)             → the [Operator context] block (NEVER raises)

INTENT → resolve_model(intent)           clone → context-size pick · role → requires⊆provides · capability → provider
                                          resident-first ordering · `satisfied` surfaces the floor

BRAIN ROUND-TRIP (drill→talk→write):
  drill(address) → bind brain → talk (POST /api/claude/turn, context = territory_prose(address), --resume stream)
  → reply in-surface → direction routes back (gallery:direction → POST /api/territory/write → suite.mark at the
  element sub-address) → gallery:rerender

CLONE LIFECYCLE: materialize_at_point(@cut) → ollama launch claude --model <tag> → register channel-member →
  onboard (era-reflection FIRST) → contribute → end (deregister; presence=truth)

FABRIC: lead + members; transport-agnostic dispatch (HTTP-to-port for live sessions, supervisor-inject for clones)
```

## THE OUTPUTS
`resolve_address` record · `territory_for` dict (`{address,scheme,identity,identity_kind,context_items,chats,
relations,corpus_record,corpus_content,notes,legs_present}`) · `territory_prose` block · `resolve_model` dict
(`{model,base_url,provider,why,satisfied,…}`) · the model CATALOG (`model_capabilities.json`, 49 models) + the
live PROVIDER set (`capability_providers()`) · the re-tiered roles (focus→fast/4B, reduce_synth→reasoning/nemotron)
· the `/api/claude/turn` NDJSON stream · the clone fleet (addressed, channel-member) · the channel membership +
mail/threads · the marks route-back vocabulary (comment/reaction/favour) · the FE gallery-brain hooks.

## THE SEAMS (to the other areas — where the union binds)
- **★ GALLERY (the primary seam):** `renderGallery(address)` resolves content THROUGH `resolve_address`/
  `territory_for`; the gallery BINDS the loadable brain to a rendered unit (`gallery:rendered` → POST
  `/api/claude/turn`); DIRECTION routes back (`gallery:direction` → `/api/territory/write` → `suite.mark`). The
  first slice — see field → click a point → talk to its brain → it changes → re-render — is mostly assemblable
  from BUILT+VERIFIED pieces (remaining: 3 proposed bridge diffs + the FE listener).
- **DNA:** DNA owns the LOOK (re-skins `.brain-ask`/`.brain-panel`/`.brain-reply`); fork owns the WIRE. DNA's
  faces resolve through the address spine; the interface gets designed INTO DNA's gallery (the liked look).
- **FACTORY:** archetypes/components/types are REGISTRIES → resolved through the Company; the model/capability
  tiers ARE registries (the same registry-is-truth mechanism). Composition's own union synthesis (noticeboard
  item-333b6b21) confirms the shared resolver/registry laws — DNA & factory are areas of one thing.
- **COMPANY-internal:** cognition firing (Phase-2 `resolve=` wire, byte-identical, R13) · the GPU/services layer
  (`capability_providers` reads services.json; gpu.py is the VRAM authority) · corpus/recollection (:8007 lenses
  enrich the relations leg) · the session-supervisor (clone launch + inject/watch).

## OPEN SEAMS + GAPS (honest state)
- **#71 Phase 2** (lead-gated, NOT started): wire `resolve=` into `run_swarm`/`run_role` byte-identically; enroll
  `model_routing.py` in `COG_SOURCES` (free today); clone base_url stays informational. Co-scope cognition.py/
  suite.py with the lead FIRST (R13).
- **kimi-cloud-for-COGNITION** (FILED, non-blocking): `capability_providers()` is local-only (surface :cloud
  catalog rows @ OLLAMA_DIRECT) + kimi via :4100 → 401 (reach via :11434/v1 or wire the key). kimi STAYS the
  working build/clone brain; this only extends it to the engine transport.
- **3 PROPOSED bridge diffs** (built+verified on fork's side, not applied — projection's hot file): the
  territory_prose composer-swap (READ half) · the /api/territory/write route (WRITE half) · COMPANY_SESSION_ID
  injection at /spawn (self-id keystone).
- **recollection's semantic-4 lenses** (find/decisions/timeline/drift) — HELD for the :8007 window; the relations
  leg is lens-independent today.
- **content-markdown = the ONE missing scheme** — the 16-scheme grammar has `ui://` for UI elements but no scheme
  for content-markdown elements; vi-visual's document-mode element-walker is a running reference impl (`mdel://`).
- **The half-circuit** — the agent-facing half is built (the element-walker, 17 ways); the Tim-facing RENDERER is
  the consistently-missing face. The substrate exists; the face is unbound.
- **Wire reconcile** — the click→talk PANEL wire (per-turn `claude --resume` subprocess, `ui_claude_session`) is a
  DIFFERENT mechanism from the fabric/clone transport (supervised inject/watch). Both are real Claude Code; the
  lead's convergence conflated them — surfaced for reconcile.

## THE TRAJECTORY
Toward **the overlord interface as the rendered projection of one addressed state, with a model-resolution spine
underneath.** #71 → Phase 2 makes "which model" a single registry-driven query (a RHM turn runs extractors on the
4B and judges on a wide brain simultaneously — Tim's "the small model no longer builds complex things"). The
loadable-brain round-trip is Tim's literal "click on stuff and talk about it with Claude Code." The gallery↔Company
seam is the binding act: projection's Instrument (the field) ⊕ wildcard's element-direction (the touch) ⊕ fork's
loadable-brain (the talk), over the address spine, in DNA's identity — the surface that gets Tim out of the
Claude-Code seat and into the overlord altitude.
```
fork commits (my area): b5e0e67 resolve_model · 35fd8e3 role re-tier (path A) · 6c2226b/ae68bb9/6a16835 finds+gap
  · 201f8ff LANE-B territory_prose + /api/territory/write + gallery hook · + cc_clone/territory/mark_types history.
```
