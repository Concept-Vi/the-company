# Wizard run-1 — discovery findings (overnight, autonomous)

> An early **by-hand run of the Project→Product pipeline** on the real ElevenLabs Wizard corpus
> (`/mnt/c/Users/Workstation001/Documents/Claude/Projects/Visual Designer`), done the *designed* way:
> cheap-local-4B for bulk per-file work (concurrent), bge-m3 embeddings for structure, me + strong models for
> synthesis. **Discovery, not conclusions** — everything cites real counts/paths; the scatter, gaps, and
> contradictions are surfaced faithfully (that's the point), not smoothed. Built up across rounds.

## Round 0 — the landscape (type-scan of ALL 5,052 content files, local 4B, 0 errors)
- **Built vs not:** ~487 code-ish · **2,227 pure design-only** · 1,180 "unclear" · **1,155 generated**.
  → **well under 10% is code that runs.** The corpus is overwhelmingly *design/intent that was never built* —
  confirmed by classification, not assumption.
- **Kind:** 2,887 `notes` (scattered/informal) · 1,067 `design-spec` · 416 `code` · 295 `config-data` ·
  67 `intent-vision` · 38 `architecture` · 25 `decision-record` · + audits, syntheses, a "vision".
- **Domain spread:** agent-identity (1,355) · ui-surface (836) · **business-gtm (433)** · workspace-infra (318) ·
  voice-audio (296) · knowledge-corpus (296) · compliance-consent (12) · telephony (7) · secrets-payment (22).
  → there's real **business/market** thinking in here, not just product; **telephony + compliance are thin**
  (the legally-loaded outbound-calling necessities are barely covered — an early hint at the product-gap).
- **The bodies (top-level areas):** Visual-DNA-Vault 1,796 · content-workbench 1,738 · packages 1,411 ·
  Visual_DNA 60 · Corpus-Extraction-Vault 29. → **three large tangled bodies**, not one project.

## Round 1 — structure & redundancy (bge-m3 embeddings of all 2,036 md + clustering, CPU)
- **~1,594 genuinely-distinct documents behind 2,030 files (~21% redundant); 1,509 are unique singletons.**
- **The redundancy is concentrated + diagnostic:**
  - **A runaway artifact: 288 near-identical copies** of `(Gap) …REACTIVE_UPDATE_TIMEOUT.md`
    (`Visual-DNA-Vault/notes/gaps/`) — the *same error logged 288 times* with ticking timestamps. A **broken
    loop spamming one gap note** — a real pathology the run surfaced mechanically. *(This is a Body-2-style
    symptom: a process running without producing, logging the same failure.)*
  - **Vault-bootstrap templates copied across ~7 sub-vaults each** (`00_project_brief`, `01_glossary`,
    `round-1-instructions`, `workshop-preparation-pack`) — the same scaffolding instantiated in
    content-workbench/{math-verification,vault,vi-workbench}, Corpus-Extraction-Vault, etc.
  - **Cross-body mirroring:** the ElevenLabs files exist *twice* — `packages/elevenlabs-mcp/vault/ElevenLabs-Wizard/`
    AND `Visual-DNA-Vault/ElevenLabs-Wizard/` are near-duplicate trees.
- **The themes (clusters, 40-way):** a dominant **discovery-rounds apparatus** (R0–R10 rounds/audits/synthesis —
  the iterative multi-agent "discovery loop," very large) · **help-agent** (scattered across content-workbench +
  Visual-DNA-Vault + outbox) · **event-skills / step-skills** (step-query/decide/wait/branch/remember — a
  skill-grammar) · **elevenlabs-mcp operational** (duplicated across two vaults) · **tasks/surfaces/recipes**
  (content-workbench UI) · **substrate-audits** (channel-architecture, vi-sync).

## Emerging shape (held loosely — discovery, NOT conclusion; awaiting the semantic extract)
- The corpus is **three entangled bodies** with heavy internal duplication and one runaway-log pathology — i.e.
  the "scattered, AI-generated, never-reviewed" reality, quantified.
- A **huge fraction is *process/meta* apparatus** (the discovery-rounds, the vault-bootstrap, the gap-logs) —
  the machinery of *trying to build*, distinct from the *product design* itself. (The wizard-of-wizards / Body-2
  pattern, but — per Tim — NOT to be written off; it needs his interpretation.)
- The **ElevenLabs product** proper (voice/telephony/agent/campaign) is a *minority* of the corpus and its
  product-reality domains (telephony, compliance, payment) are **thin** — consistent with built-bottom /
  missing-top.

*(Next rounds: the semantic discovery-extract — intent · components · decisions · open-questions ·
gaps/contradictions · latent/abandoned — across all md, then aggregate the latent/abandoned + contradictions
across the whole corpus, then strong-model/panel discovery synthesis. Appended as they complete.)*

## Round 2 — concentration map (domain × built-status, body × built-status; from the scan)
**The product-reality gap, quantified (the `require` thesis, confirmed by data):**
- **business-gtm: 433 files, 0 built** — a large business/strategy/GTM design layer, *entirely unimplemented*.
- **telephony: 7 files · compliance-consent: 12 (8% built) · secrets-payment: 22** — the legally-critical
  outbound-calling necessities (consent, telephony, payment) are **barely present and mostly unbuilt.** A real
  deployed outbound-voice product *needs* these; they're nearly absent → the single clearest product-gap.
- **Most-built domains:** mcp-tools 63% · telephony-the-little-there-is 42% · **voice-audio 33%** (the real
  ElevenLabs voice work) · ui-surface 15% · agent-identity 10%.
- agent-identity (1,355) + ui-surface (836) are the bulk of the *design*, ~10–15% built.

**The bodies, by what's actually built (a genuine surprise):**
- **content-workbench is the MOST-implemented body — 367 built-code files** (+786 unclear), *more real code than
  the ElevenLabs packages (89).* The "project" is really **several products**, and the most-built one is **not the
  ElevenLabs Wizard** — it's content-workbench (a separate content-transformation product).
- **packages (ElevenLabs)**: ~89 real code files + 757 generated snapshots → the Wizard proper is a *small MCP
  server + a large design vault*, not a built product.
- **Visual-DNA-Vault**: 1,796 files, only 21 built-code, 1,046 design-only — almost pure design/vault/notes.

**Discovery (held loosely):** what was pointed at as "the ElevenLabs Wizard" is a **multi-product corpus** where
(a) the most *built* thing is content-workbench, (b) the ElevenLabs voice/MCP layer is real but small, (c) a huge
business/strategy layer is wholly unbuilt, and (d) the product-reality domains for shipping outbound voice
(telephony/consent/payment) are the thinnest of all. The "missing top" is concretely: the business layer + the
compliance/telephony/payment product-reality + the surface — almost none of it built.

---
## ⚙️ INFRA NOTE — ✅ RESTORED (Company stack whole again)
To read whole files at 32K (not 4K heads), I swapped the GPU servers:
- **Stopped:** production 4B (`serve.sh` config @ :8000, was --max-model-len 4096) + bge-m3 (`:8001`, embeddings
  were done). jina-v4 (:118xx via serve_jina_v4.py) left running.
- **Started:** `serve_scan.sh` — 4B @ :8000, **32K window**, gpu-util 0.80, 16 seqs (Tim's own scan launcher).
- **TO RESTORE production after the run:** `pkill -f "vllm serve"` then `nohup ~/vllm-tests/serve.sh > /tmp/vllm-serve.log 2>&1 &`
  (restores the 4B with tool-parser/auto-tool-choice for the Company engine) and `nohup ~/vllm-tests/serve_embed.sh ... &`
  (restores bge-m3 @ :8001 for the Company's embed node). *Will do this once the heavy 4B passes (extract +
  code-extract) are complete.*

## Round 3 — semantic discovery-extract (1,760 good of 2,036 md; whole-file, 32K local 4B)
Per-file pull of intent · components · decisions · open-questions · gaps/contradictions · latent/abandoned.
Aggregated across all, then **denoised** (the runaway `viewready/REACTIVE_UPDATE_TIMEOUT/stats-update` gap-log
dominated raw counts — 295 records dropped) to expose the real signal. Full lists: `~/wizard-run-1/clean_*.txt`.

## Round 4 — discovery synthesis (MY read, grounded; held loosely where it's interpretation)
> Not conclusions — discoveries + my reasoning, the way you asked. Each is grounded in the aggregated extracts;
> the *interpretation* is mine and flagged as yours to confirm/correct.

**① The big one — this corpus is an *earlier, scattered attempt at the Company itself.*** The design *values*
recur across the files and they are **the Company's own principles, before the Company existed:**
- "prohibition of external architectural frameworks" (your framework-rejection),
- "types drive automated routing" (schema-is-spec / type-driven dispatch),
- "ai auto-resolves fields from context without asking" (decide-don't-specify / content-resolution),
- "refused silent degradation; persisted as evidence trail" (~290× — your no-silent-failures law),
- "agents must not judge completeness" + "prioritize full coverage over selective sampling" (the scan discipline),
- "deliberate protection of incompleteness as design principle" + "contradictions as refinements not errors"
  (your open-future-writing / expansion-ratio worldview),
- "workshop serves as the forcing function to extract human mental models" (≈ the **collaborative-design mode**
  §5t — extracting *your* intent — prefigured here!).
  → **Discovery:** the "wizard-of-wizards" you told me not to write off *is* a proto-Company. These scattered
  principles **could come together as a principle-set** — and they corroborate the Company's design from an
  independent prior attempt. *(Interpretation — yours to confirm; but the textual evidence is strong.)*

**② A real, distinctive intellectual thread: a *mathematical substrate theory*** — recurring components
`sheaf` · `holonic structure` · `well-founded recursion` · DAG/gluing, with its OWN tests catching its OWN
contradictions ("initial claim of 8 universal structures contradicted by topology tests"; "DAG violation breaks
sheaf gluing"). An ambitious formal model of the substrate, **partially self-refuted, never resolved.** Latent.
Could be deep value or a rabbit-hole — a genuine *your-call* item.

**③ The core trust pathology, faithfully surfaced: pervasive status-vs-reality dishonesty.** The most common
*real* contradictions are all one shape — the corpus **claims states/capabilities it doesn't have:** "status
claims audit-only but design is empty" · "marked as stub but claims high-priority/auto-mode" · "agents dormant
but expected to be reasoning" · "all layers marked pending with no data." → You **cannot trust the corpus's own
status claims** — which is *exactly why execution-grounding is non-negotiable* (the Body-2 lesson, evidenced in
your own material). And the Body-2 stall signal is literally here: decisions set to **"awaiting-tim-direction."**

**④ Concrete reusable components that are actually real** (recur, and many are `code-that-runs`): a **capability
registry** · **substrate_ledger** · **closure_tracker** · **accumulation engine** · **providerRegistry** ·
**channel_events** · **frontmatter-schema-driven routing** · the **autonomy modes (manual-assist / full-auto)** ·
**HelpAgentPanel** · RLS policies + edge functions. These are the salvageable building blocks (subject to the
trust caveat — verify by execution before reuse).

**⑤ Abandoned product directions worth knowing about** (latent, never finished): **template marketplace** ·
**plugin API** · **unified voice transport layer (mic/speaker toggles)** · **configurable ollama known-capabilities
list** · **role-based perspectives for subjective quality** · a **"phase-8 migration"** planned (25×) but
seemingly never completed · a **"universal mechanics system"** named repeatedly but **never defined**.

**⑥ A design-system body with internal contradictions** — a theme/token system (dark-mode hex vs gray-scale
conflicts, gold-shadow light-but-not-dark, breathing-animation 4s unmapped to a token, ease-in motion mismatches).
A real but inconsistent visual-design layer.

### What I'd surface to you as decisions (when the system can, per §5l/§8 surface-when-relevant)
- The **proto-Company principle-set** (①) → collect + reconcile against the Company's current principles? (high value)
- The **mathematical substrate theory** (②) → pursue, archive, or drop? (a real fork — needs your read)
- The **"universal mechanics system"** → define it, or let it go? (named-but-never-defined; could be central or noise)
- The **salvageable components** (④) → which to `transform-place` into the Company (after execution-verification)?
- The **abandoned directions** (⑤) → any you want revived?

*(These are exactly the kind of `design-gap`/decision seeds §8 says the RHM should surface at the moment of need.)*

## Round 5 — the three-way diagnosis (intended ∨ actual ∨ required) — the real `diagnose`+`require` output
As-built from 382 code files (294 real-working / 57 stub / 23 partial / 7 scaffold; 0 errors).

**ACTUAL (what's genuinely built):**
- **content-workbench is the real product — 254 real-working code files** — a content-transformation app with
  **real Supabase + Anthropic integration**, a **registry-driven architecture** (variable / provider / task /
  capability registries — "types drive routing," built), variable-system, state management, localStorage.
- **ElevenLabs side: ~40 real files** — a working **MCP server** connecting the **ElevenLabs API + Supabase**
  (listModels/call/stream/checkAvailability). Real but small.
- **The mathematical substrate theory is *actually coded*** — Tarski fixed-point iteration, Curry-Howard limits,
  sheaf/DAG double-counting + boundary proofs, coalgebra-vs-state-machine, a 4-layer verification stratification,
  a `formalisation-registry`. Executable proof code, not just design.

**INTENDED (the reach, from the design corpus):** an AI-native agent-interface / operating-system where types
drive everything, agents discover+build, no silent degradation, incompleteness-as-feature — expressed across an
ElevenLabs voice-wizard, content-workbench, a universal-mechanics math substrate, and the proto-Company principles.

**REQUIRED-FOR-PRODUCT vs covered:** depends which product —
- *ElevenLabs outbound-voice product:* needs telephony · consent/compliance · billing · onboarding ·
  campaign-batch · monitoring → **nearly all absent** (the thinnest domains). Mostly-vision, not near-ship.
- *content-workbench:* the **only thing close to shippable** — real integrations + architecture already built.

**THE GAP / the reframe (the real diagnosis):** what was handed to me as "the ElevenLabs Wizard" is actually
**three different things tangled together**, and the build-leverage is *not* where the name pointed:
1. **One nearly-real product — content-workbench** (Supabase+Anthropic+registries, 254 real files). *If the goal
   is "ship something," this is the diagnose→require→build target* — closest to a deployable product.
2. **One big-vision-mostly-unbuilt — the ElevenLabs voice wizard / agent-interface-system** (a small real MCP
   server + a huge design vault). To deploy it needs almost the entire product-reality layer built.
3. **A pile of intellectual ASSETS, not products — the proto-Company principle-set + the math substrate** (some
   coded). These are to *harvest into the Company* (verify-by-execution first), not to ship.

→ **The single highest-value action the pipeline would surface:** target **content-workbench** for the
ship-path (it's real), **harvest the principle-set + registries** into the Company (they corroborate + extend it),
and treat the **ElevenLabs voice product** as a generate-from-near-nothing build (the product-reality layer is the
work). *All grounded; the three-way split + the "ship content-workbench first" call are my read — yours to confirm.*


**✅ RESTORED (run complete):** production 4B @ :8000 (4096 + tool-parser, for the Company agent face) + bge-m3 @ :8001 (Company embed node) both back up; jina untouched. The 32K scan server is stopped. Verified: :8000 max_model_len=4096 + tool-call-parser present, :8001 bge-m3 responding.

## Round 6 — mechanical theme-clustering of contradictions + latent (bge-m3 embeddings → KMeans)
Clustering the 5,200+ contradictions and 4,100+ latent items by similarity (not my read) — the recurring
*shapes* of the corpus's problems, mechanically:
- **Chronic claim-vs-reality mismatch (the dominant shape, ~6 themes):** count discrepancies ("14 registries
  claimed but 16 exist"; "38 entities vs 47"; "24 listed but 20 detailed") · status paradoxes (the discovery
  rounds: "r7 completed while r6.1 in-flight"; closure_tracker inconsistencies) · **architecture-described-but-
  never-instantiated** (detailed design, no code; frontend missing) · **agents defined-but-unwired** ·
  **schema-exists-but-implementation-sparse**. → the corpus *systematically over-claims* — mechanically confirms
  the trust pathology (Round 4 ③): **never trust its self-reports; execution-ground everything.**
- **Recurring real code gap:** missing error handling (its own cluster) · no conflict-resolution strategy.
- **The vi-sync / canvas / mobile UI body:** proto-canvas without canvas tables, mobile maps desktop but lacks
  touch patterns, overlay exists but no interaction design — a real UI design layer, design-ahead-of-implementation.
- **The meta-tension:** "vault is inconsistent yet needs unified design" (its own recurring self-description).
- **★ NEW discovery — a proto-Company *identity/continuity* thread:** a cluster of undefined half-ideas —
  *"no definition of 'what I'm becoming'"* · *"'absence as data'"* · *"'continue' criteria"* · *"'new session'
  criteria"* · *"definition of 'Tim' or relationship."* This is an **identity / continuity / self-model
  exploration** (what am I becoming · absence-as-data · defining Tim-and-the-relationship) — undefined, latent,
  and *strikingly Company-like* (entity-identity, continuity-across-sessions). Reinforces Round 4 ① — the corpus
  was reaching for the Company's *identity* layer too, not just its mechanics. *(Yours to interpret.)*

---
## Run-1 — done. Artifacts (all in `~/wizard-run-1/`)
`scan.jsonl` (5,052) · `embed.jsonl` (2,036 vectors) · `extract.jsonl` (1,760 design) · `code_extract.jsonl`
(382 code) · `clean_*.txt` (denoised aggregates) · this `FINDINGS.md`. Stack restored. The back-half stages
(scenarios→build→deploy) need the net-new pipeline node-types built — they didn't run (correctly).
