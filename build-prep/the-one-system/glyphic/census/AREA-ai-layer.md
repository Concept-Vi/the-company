# AREA — app/ai/ (the AI layer) — census, read in full 2026-07-03

> Reader lens: UNIFICATION. All 7 files read line-by-line (1,641 lines / ~99K). Grounded first in
> feedback-glyphic-course-corrections.md, CRITERIA.md (+ AMENDMENTS A1-A5), ROADMAP.md, ADVISOR-AUDIT.md
> §4-§8, READING-LEDGER.md, GUIDE.md tail ("THE CORRECTED LAWS"), SYNTHESIS.md ROUND 7. Cross-checked
> against the live engine (assets/icons/cv-meaning.js, R1/R2 diff regions), the Company `roles/glyph_*.py`
> role files, and `system/*.html` consumers. Read-only on all sources; this file is the only write.

---

## §A · File-by-file account (file:line)

### `ai-registry.js` (390 lines) — CV_AI, the registry engine itself
The fifth single-source registry, deliberately mirroring `CV_REGISTRY`'s API (`register/registerMany/
update/remove/get/all/query/resolve/lineage/subscribe`, LS-persisted user/vi provenance, built-ins in
memory). **Observed** structure:
- Five layers (`provider < behaviour < skill < capability < context`, ai-registry.js:45-52), inheritance
  via `extends` (lineage flattening, leaf-wins, ai-registry.js:135-153) — same shape as `CV_REGISTRY.resolve`.
- `resolveProvider` (ai-registry.js:199-239): binds a provider entry to ITS live runtime. Three built-in
  kinds hardcoded (`claude`, `openai-image`), then a **delegation door** to `CV_HOST.resolveProviderRuntime`
  for anything else (ai-registry.js:234-238) — loud if nothing claims it.
- **A1 role-indirection** (ai-registry.js:242-266): `ROLE_PROVIDERS = { text:'claude', image:'openai-image',
  embed:'company' }` — a capability declares `role:'text'` instead of a literal provider id; flipping every
  text-touch to the Company is `setRoleProvider('text','company')`, ONE call, not ~40 pinned edits. This is
  A1/A2 from ROADMAP.md, and it is REAL — not aspirational. `providerIdFor` (ai-registry.js:254) is the
  resolution order: explicit `provider` wins, else `role` via `providerForRole` (loud if unbound).
- `execute()` (ai-registry.js:306-347) — THE generative path: resolve capability → resolve context →
  resolve provider (only if the cap declares one — pure-fn caps need no live LLM) → `run()` OR
  `build→complete→parse`. Every failure loud (no silent fallback; ai-registry.js:344 explicitly restores
  loud-fail against "no silent claude fallback").
- `ACTIVE` surface state (ai-registry.js:354-358) + `subscribe/notify` — the reactivity substrate every
  panel/inspector reads.
- Convenience `AI.complete()` / `AI.embed()` (ai-registry.js:371-383) route through role-indirection, not a
  hardcoded provider — this is the correct shape for "the AI's one door in."

### `ai-seed.js` (224 lines) — providers, behaviours, skills, context (DATA only)
**Observed:** 4 providers (`claude`, `openai-image`, `company`, `vision`; ai-seed.js:21-55). The `company`
provider (ai-seed.js:37-47) is real and detailed: `runtime.completeRole:'complete_text'`, same-origin only,
`maxPromptChars:100000` documented as "an honest conservative floor... never assume claude's 200k" — this
matches the A0 walking-skeleton concern in ROADMAP.md about schema-forward proof. 2 behaviours
(`voice.conceptv`, `angle`, `diversity`), 8 skills (7 doc-transforms + `skill.theme`), 4 context resolvers
(`generic/pages/widget/wizard`) — **NONE glyphic-specific**; glyphic context is a separate file
(`context.glyphic` lives in ai-glyphic-language.js, not here — see §B).
- `AI._seeded = true` flag (ai-seed.js:223) — a load-order assertion primitive AIEngine.jsx can check.
- The `CV_HOST:ai-entries` anchor comment (ai-seed.js:220) is the **serializer insertion point** —
  confirmed live: `host-serializer.js`'s `ai.entry` serializer (host-serializer.js:73-80) targets exactly
  this file at exactly this anchor. This is a genuinely closed loop: Vi-authored capabilities (via
  `ds.propose`) land in the SAME file a human would edit, at the SAME place — one home, both authors.

### `ai-glyphic.js` (104 lines) — the ICON-FOUNDRY AI face (CV_ICONS, not CV_MEANING)
**Observed:** two capabilities — `glyphic.generate` (propose N candidate 24px SVG symbol records from a
brief; ai-glyphic.js:59-90) and `glyphic.save` (commit a chosen candidate into `CV_ICONS`; ai-glyphic.js:92-
103). This operates on **symbol geometry + taxonomy** (denotation — "what shape is this"), never on
CV_MEANING (contextual meaning). The header (ai-glyphic.js:9-11) states this explicitly as the reason the
two files are siblings, not one file (see §B for the verdict).
- `glyphic.generate`'s `run()` (ai-glyphic.js:64-89) has TWO paths: if the bound text provider can
  `runRole` (the Company), it fires the `glyph_symbol_candidates` ROLE (schema-enforced output — ai-
  glyphic.js:69-83, citing "the prompt-built JSON-array path breaks on JSON-in-text escaping; proven in
  A4"); else it falls back to the original `buildPrompt→complete→parseCandidates` regex-JSON-extraction
  path (ai-glyphic.js:26-57, 85-88). Both paths converge on the same `CV_GLYPHIC.validateSymbol` gate.
  **This is A2's "model-using caps become typed roles" pattern, already landed for this one capability** —
  concrete evidence the A-phase migration pattern proved on at least one real capability before ROADMAP.md's
  A2 was written as "safe to fan out once the pattern proves on one."

### `ai-glyphic-language.js` (156 lines) — the LANGUAGE'S AI face (CV_MEANING; G0.4/G8.3)
**Observed**, capability by capability:
- `glyphic.author` (line 27-33) — wraps `M.author.setField(facet, value, feeling, senses, extra)`. Declared
  `params: { facet, value, feeling, senses }` (line 30) — **`extra` is NOT in the declared params schema**,
  yet `run()` (line 32) passes `p.extra` straight through. `extra` is the ONLY channel through which R1's
  `directed`/`inverse` and R2's `kindWord`/`opWord`/`determiner` reach `setField` (see cv-meaning.js:497-517,
  540-556 — `Object.assign({}, rec, {...})` spreads the raw record first, so any key an author sets survives;
  this is the "dropped-field trap" R2 dissolved, per READING-LEDGER.md's R2 section).
- `glyphic.author-relation` (line 37-43) — wraps `setRelation`/`setOperator`. Declared `params: { id,
  feeling, senses, operator, symbol }` (line 40) — same gap: no `extra` in the schema, though `run()`
  (line 42) forwards `p.extra` to `setRelation`, and `setRelation` IS `setField('edge', id, feeling, senses,
  extra)` (cv-meaning.js:516) — the exact path `directed`/`inverse` must travel to author a verb-pair.
- `glyphic.author-gloss` (line 45-51) — wraps `setGloss`. Unaffected by R1/R2 (no `directed`/`inverse`/
  referent-word surface here).
- `glyphic.read` (line 55-65) — wraps `M.field(facet, value)` (no-arg mode lists the whole profile). `M.field`
  (cv-meaning.js:540-556) is the SAME normalizer that now returns `directed`/`inverse` (cv-meaning.js:551-555)
  on every read — **this path is current, not stale**: an AI calling `glyphic.read({facet:'edge',
  value:'contains'})` today gets back `{directed:true, inverse:{feeling:'contained by',...}, ...}` in full.
- `glyphic.describe` (line 71-77) — wraps `M.describe` (the FACET INSPECTOR, deliberately NOT the language;
  correctly kept separate per Tim's 2026-06-30 distinction, cited verbatim in the file's own comment).
- `glyphic.transglyph` — **deliberately unregistered** (line 79-83): the comment states `readGraph`/
  `referent` are consumed directly by surfaces and a capability wrapper "stays unregistered until a caller
  needs the read-out THROUGH the registry." Confirmed by grep: no surface calls `CV_MEANING.readGraph`
  through `CV_AI.execute` anywhere in claude-ds; all three consumers (`system/language.html:175,179`,
  `system/the-whole-thing.html:442`, `system/glyphgraph-generator.html:225,232`) call `M.readGraph` directly
  on `window.CV_MEANING`. **The AI has no registered capability to invoke readGraph at all** — this is an
  intentional gap (documented, reasoned), not drift, but it means R1's inverse-composition-by-focus and the
  octagon-oracle sentence generation are not reachable through `CV_AI.execute()` by any caller — only by an
  agent that knows to call `window.CV_MEANING.readGraph` off-registry. See §B for the disposition question.
- `glyphic.assist` (line 90-137) — A6, the collaborative hand. Reads `window.CV_GLYPHGRAPH_SESSION`
  (confirmed live: `system/glyphgraph-generator.html:207-208` sets exactly this global, matching the
  capability's expectation at line 100). Builds a payload of `{instruction, selection, nodes, edges, vocab}`
  and fires the Company's `glyph_assist` role, THEN atomically validates every returned op against the live
  registries (line 124-134) before returning — loud on any bad op, nothing partial applied. **Concrete
  staleness found here** (see §B.1): the `edges` payload (line 117) is `{from, to, kind, line}` and
  `vocab.edge_kinds` (line 111) is a bare `Object.keys(M.valuesFor('edge'))` id list — NEITHER carries
  `directed`/`inverse`. Verified against the Python role (`roles/glyph_assist.py:16,34-41`): `kind` is typed
  as an opaque string "one of vocab.edge_kinds" with zero mention of direction. The collaborative AI can
  choose an edge kind but has no way to know or express which way it points, or that an inverse telling
  exists — R1's grammar is invisible to this capability.
- `context.glyphic` (line 142-155) — projects `activeProfile/meaningFacets/meaningTypes/facetCounts` into
  the prompt context. **Observed:** this does NOT include `directed`/`inverse` per-field (it counts bindings,
  not their shape) — a second, milder instance of the same staleness: the context an AI gets about "the
  language as it stands" doesn't surface which relations are verb-paired.

### `host-runtime.js` (451 lines) — CV_HOST, the Environment/Host registry
**Observed:** a SIXTH registry (beyond the CLAUDE.md's stated four: tokens/types/engine/AI) — runtimes
(`review` floor / `fsapi` / `native`), ranked by capability, resolved via `best(cap)` (host-runtime.js:135-
139). The **review floor is always available** (host-runtime.js:77-83) so the system is "never dead, only
degraded, and degraded explicitly" — this is the loud-fail law applied to environment capability itself.
- `KINDS` registry + `registerKind(kind, fn)` (host-runtime.js:60-68) — **this IS the A1 seam ROADMAP.md
  names** ("`CV_HOST.registerKind(kind,resolverFn)` + role-indirection → `CV_AI` resolves entries from the
  one home"). Confirmed real and wired: `resolveProviderRuntime` (host-runtime.js:164-181) checks
  `KINDS.has(kind)` FIRST (line 167) before falling through to the three hardcoded kinds (`host-fs`,
  `native-model`/`mcp-model`, line 169-179) — additive, nothing yet migrated INTO a registered kind. No
  caller in this corpus actually calls `registerKind` — **it exists as an unused extension point**, proven
  ready but not yet exercised (see §C).
- `changes`/`commit`/`applySerialized` (host-runtime.js:233-336) — the review-first change pipeline: every
  proposed change is staged (localStorage), applied only when a writer is connected AND auto-apply is on,
  else handed off per `handoffMode` (`review`/`stash`/`download`). This is the mechanism `ds.propose`/
  `ds.apply` (host-serializer.js) ride.
- `describe()` (host-runtime.js:343-362) — the self-documenting projection the Bridge panel reads; no
  hand-written status string exists elsewhere (verified: no other file in app/ai constructs a status object).

### `host-serializer.js` (197 lines) — serializers + host capabilities
**Observed:** 5 serializers registered (`ai.entry`→ai-seed.js, `type`→types-seed.js, `css.token`→
colors_and_type.css, `card`→preview/*.html, `file`→escape hatch; host-serializer.js:73-124), each the single
home for "how an X is written to source" — confirmed each targets the SAME files CLAUDE.md's four-registry
table names as the single homes (ai-seed.js for AI, types-seed.js for types, colors_and_type.css for tokens).
This is the write-side mirror of the read-side registries — a genuinely unifying piece: it means an AI
authoring a NEW capability produces the literal `AI.register({...})` text a human would hand-write, landed
in the same file, same anchor. 5 host capabilities (`repo.read/list`, `ds.propose/apply`; host-serializer.js:
161-194) run on the `host-fs` provider CV_HOST binds (host-serializer.js:132-137).
- No glyphic-specific serializer exists (no `kind:'meaning-field'` or `kind:'relationship-type'`). Authoring
  a language field via `glyphic.author` mutates the LIVE in-memory profile (`CV_MEANING.author.setField`)
  but does **not** produce a durable source-file change through this pipeline — the two authoring paths
  (CV_HOST's serialize-to-source vs CV_MEANING's live-profile mutation) are parallel and never joined. See
  §B.4.

### `ai-capabilities-canvas.js` (119 lines) — canvas-move catalogue
**Observed:** 27 TEXT capabilities + 2 IMAGE + 1 bespoke (`deck.titlechain`) registered as thin
`role:'text'` wrappers around each canvas's own prompt (the canvas keeps its parse; the registry just
catalogues the move exists — ai-capabilities-canvas.js:26-28, 81-96). **None are glyphic-specific** — no
`glyphgraph.*` or `language.*` entries appear in this canvas list; the glyphic AI surface lives entirely in
the two sibling files (`ai-glyphic.js`, `ai-glyphic-language.js`), not here. This confirms the folder charter
line "capabilities registered from elsewhere (AIEngine.jsx)" refers to the 11 composer block-level
capabilities + this canvas catalogue — a DIFFERENT population from glyphic's, not overlapping.

### `AIEngine.jsx` (1830 lines, `app/canvases/workshop/`) — NOT in app/ai/, but the fourth registration site
**Observed** (targeted grep, not full read — outside my assigned 7 files, flagged for the registry-area
reader): exactly one `CV_AI.register` call at line 1243 (a single composite registration, not a loop) —
confirmed this is where the composer's 11 block-level capabilities live, matching CLAUDE.md §5's Traps
note ("`CV_AI` capabilities that need the composer's prompt helpers are registered from `AIEngine.jsx`").
This is the fourth of four capability-registration sites: `ai-seed.js` (data-only), `ai-glyphic.js` +
`ai-glyphic-language.js` (glyphic), `ai-capabilities-canvas.js` (per-canvas thin wrappers), `AIEngine.jsx`
(composer, helper-dependent). All four converge on the ONE `CV_AI` registry — confirmed no second registry
object exists anywhere (grep for `window.CV_AI =` returns exactly one assignment, ai-registry.js:365).

---

## §B · UNIFICATION findings

### B.1 · THE AI-FACE STALENESS VERDICT (the critical question)
**Split verdict — not uniformly stale, but concretely stale in three specific spots:**

1. **`glyphic.read` is CURRENT.** Because `M.field()` spreads the raw record before computing normalized
   keys (cv-meaning.js:540-556, the R2 "dropped-field trap" fix), every read through `glyphic.read` already
   returns R1's `directed`/`inverse` and R2's `kindWord`/`opWord`/`determiner` today, live, with zero code
   change needed on the AI-face side. **This is the one place the engine's growth reached the AI face for
   free** — a genuine unification success, worth naming as a pattern: because the read path is "spread the
   whole record," new engine fields propagate to every reader (including the AI face) automatically. This is
   the shape G0.1/A1's "profile data, not consts" law is FOR.
2. **`glyphic.author`/`glyphic.author-relation`'s declared `params` schema UNDERSELLS the write surface —
   concrete, fixable staleness.** The mechanical plumbing (`p.extra` forwarded to `setField`/`setRelation`)
   already carries `directed`/`inverse`/`kindWord`/`opWord`/`determiner` through to the engine (verified: no
   code change would be needed to author these fields via the existing capabilities). But an AI (or a human)
   introspecting the capability's `params: {...}` to learn what it can pass would never discover this channel
   — `extra` doesn't appear in either capability's declared params (ai-glyphic-language.js:30, 40). This is a
   **documentation/discoverability lag behind the engine**, not a functional block. Fix: declare `extra:
   null` in both params objects (or better, name the specific fields the engine now expects — `directed`,
   `inverse`, `kindWord`, `opWord`, `determiner` — as documented optional params), so introspection matches
   capability.
3. **`glyphic.assist`'s payload construction (A6) genuinely LAGS the engine — the sharpest finding.** The
   `vocab.edge_kinds` list and per-edge `{kind}` field carry NO directed/inverse information (ai-glyphic-
   language.js:111,117); the Company's `glyph_assist` role (`roles/glyph_assist.py:16,34-41`) treats `kind`
   as an opaque enum. The collaborative AI can pick an edge kind to add, but cannot reason about or express
   direction, cannot be told "add a contains-edge, but I mean the inverse telling," and has no way to
   discover which kinds are verb-paired vs symmetric. **This is the one place R1's law is invisible to an
   AI actor** — worth booking explicitly (see §E).
4. **`context.glyphic`'s `resolveCtx` is a milder instance of the same gap** — it counts bindings but does
   not surface the directed/inverse shape per relation, so ambient context an AI receives about "the language
   as it stands" (line 145-154) doesn't include the edge law either.
5. **`glyphic.transglyph` is reserved, not stale** — the file's own comment (line 79-83) reasons through
   why it stays unregistered (no caller needs it through the registry yet; a wrapper now would just alias a
   direct call). This is a legitimate documented deferral matching A5's "correctability-by-use" spirit, but
   it does mean the readGraph/inverse-COMPOSITION mechanism (as opposed to the raw directed/inverse DATA) is
   currently unreachable by any `CV_AI.execute()` caller — only `glyphic.read` (raw data) and direct
   `window.CV_MEANING.readGraph` calls (browser surfaces only) reach it.

**Verdict in one line:** the AI face's READ path absorbed R1/R2 for free (engine-shape success); its WRITE
path can author the new fields but doesn't advertise it (schema lag, cheap fix); its COLLABORATIVE path
(`glyphic.assist`) is the one genuinely under-informed consumer, because its payload is hand-built rather
than routed through the same "spread the whole record" read path `glyphic.read` uses.

### B.2 · THE TWO-FILES VERDICT (`ai-glyphic.js` vs `ai-glyphic-language.js`)
**Correctly separate — not drift, not one-system-two-names.** The split mirrors a REAL engine boundary
Tim named (2026-06-30, cited in ai-glyphic-language.js:9-11 and GUIDE.md's north-stars): `CV_GLYPHIC`/
`CV_ICONS` (symbol geometry — intrinsic, denotation, "what shape is this") vs `CV_MEANING` (contextual
meaning — the loadable, authorable dictionary). `ai-glyphic.js` operates ONLY on the former (`glyphic.
generate`/`glyphic.save` touch `CV_ICONS.add`/`CV_GLYPHIC.schema`, never `CV_MEANING`); `ai-glyphic-
language.js` operates ONLY on the latter. This is the SAME separation CRITERIA.md's verification protocol
insists on for humans ("describe=facet inspector, transglyph=the language — TWO READ-OUTS NEVER
CONFLATED") — applied consistently to the AI face. **Recommendation: keep them separate; the names could be
sharper** (`ai-glyphic.js` reads as "the glyphic AI file" when it is actually "the icon/symbol foundry AI
file" — a future reader will make the same two-files-why-two question I did). A rename to `ai-icon-
foundry.js` would remove the ambiguity without any functional change; flagging as a naming candidate, not a
structural fix (see §F).

### B.3 · The A-phase state, concretely (part c of the brief)
- **A0 (walking skeleton):** the `company` provider (ai-seed.js:37-47) exists with the exact shape A0
  describes (same-origin, `completeRole:'complete_text'`, honest `maxPromptChars` floor) — this is the
  provider entry A0 would resolve through, present and seeded, though I did not execute a live fire (out of
  scope — read-only mandate; ROADMAP.md records A0 pre-flight as already passed elsewhere).
- **A1 (role-indirection + one-registry):** REAL and load-bearing (ai-registry.js:242-266, `ROLE_PROVIDERS`
  + `providerForRole` + `setRoleProvider`). Every glyphic AI-touching capability already declares `role:
  'text'` (ai-glyphic.js:61 `role:'text'` with an inline comment citing A1 directly; ai-capabilities-
  canvas.js:84 same pattern for all 27 canvas caps; ai-glyphic-language.js's `glyphic.assist` resolves via
  `AI.providerForRole('text')` at line 103). **The migration ROADMAP.md describes as "collapse the ~33
  'claude' pins to one binding" is materially DONE for every file in app/ai/** — I found zero literal
  `provider:'claude'` pins among the glyphic/canvas capabilities; all use `role:'text'`. host-serializer.js's
  `repo.*`/`ds.*` capabilities correctly use `provider:'host-fs'` (a literal, correct — they are NOT
  text-generation capabilities, so role-indirection doesn't apply to them).
- **A2 (model caps → roles):** proven on at least `glyphic.generate` (ai-glyphic.js:69-83, the `runRole`
  branch) — a concrete existence proof the pattern works before ROADMAP.md's "fan out once it proves on
  one" gate. `glyphic.assist` also already uses `runRole` (ai-glyphic-language.js:120) for `glyph_assist`.
  Two roles proven; `glyph_extract`/`glyph_compose` exist as files (`roles/glyph_extract.py`, `roles/
  glyph_compose.py`) but I found NO caller in app/ai/ that fires them — A5 (extract/compose roles, "the real
  NL→graph") is genuinely unbuilt from the AI-face side, matching ROADMAP.md's own listing.
- **A6 (collaborative AI):** REAL — `glyphic.assist` + `CV_GLYPHGRAPH_SESSION` is a working, atomic,
  registry-validated loop (see §A), confirmed wired to a real DOM global set by `glyphgraph-generator.html`.
  The one gap is B.1's edge-law blindness, not the mechanism itself.
- **CV_HOST role-indirection (the A1 seam on the environment side):** `registerKind` exists
  (host-runtime.js:65-68) and is checked first in resolution (host-runtime.js:167), but has ZERO registered
  kinds anywhere in this corpus — a proven-ready, unexercised extension point (see §C).

### B.4 · host-runtime/host-serializer: what the host projection is, who consumes it (part d)
`CV_HOST` answers "what can Vi do to the environment it's running in" — a SIXTH registry, same shape as the
other five, with `review`/`fsapi`/`native` runtimes ranked by capability and a uniform op surface
(`read/list/write`) that resolves to the best available one, loud otherwise. It is consumed by: (i) `CV_AI.
resolveProvider` for any provider whose `runtime.kind` isn't `claude`/`openai-image` (the delegation door,
ai-registry.js:234-238); (ii) the `host-fs` provider's `repo.*`/`ds.*` capabilities (host-serializer.js);
(iii) — by its own comment — "the Bridge panel + the AI card" (host-runtime.js:14, 339-341), UI surfaces
outside app/ai/ I did not read (out of my assigned territory) but which the `describe()` projection exists
specifically to feed. **No glyphic-specific consumer of CV_HOST exists** — the language/icon AI capabilities
never call `repo.*`/`ds.propose` to durably persist an authored field; authoring stays in-memory/localStorage
via `CV_MEANING.author`'s own persistence (see B.1 point 5's "two authoring paths, never joined" — worth
naming again here as the same seam viewed from the host side).

---

## §C · Disconnected / unused

1. **`CV_HOST.registerKind`** (host-runtime.js:65-68) — a real, correctly-built extension point with **zero
   callers** anywhere in this corpus. It is the exact mechanism ROADMAP.md's A1 names ("`CV_HOST.
   registerKind(kind,resolverFn)`") but the migration it enables (collapsing hardcoded kinds into registered
   ones) has not started on the environment side, even though the AI-registry side (`ROLE_PROVIDERS`) is done.
2. **`glyph_extract.py` / `glyph_compose.py`** — Company role files exist (confirmed via find) but no file in
   app/ai/ fires them. A5 ("Extract/compose roles — the real NL→graph") is unbuilt end-to-end from this side.
3. **`glyphic.transglyph`** — reserved id, never registered (documented, not accidental — see B.1.5).
4. **`vision` provider** (ai-seed.js:49-55) — declared, `caps.exportOnly:true`; no capability in any of the
   7 files or `ai-capabilities-canvas.js` resolves it. It exists as a catalogue entry with no consumer yet
   (an honest "declared ahead of use," consistent with the folder's "designing ahead of time" unification
   lens, but worth naming as currently inert).
5. **`native-model` / `mcp-tools` providers** (host-serializer.js:143-154) — same pattern: declared,
   export-only, zero current consumers in-repo.
6. **The `M.author` write surface has no serializer.** Unlike every other registry (AI entries, Types, CSS
   tokens all have a `host-serializer.js` entry that turns a live mutation into durable source text),
   authoring a meaning field via `glyphic.author` never reaches `CV_HOST.commit`/`serialize` — it is
   memory/localStorage-only on the `CV_MEANING` side (confirmed: no serializer `kind` in host-serializer.js
   matches anything meaning/relationship-shaped). This is a genuine gap in the "one unified system" claim:
   four of five registries have a durable-write path through CV_HOST; the language engine's authoring
   (arguably the newest, most actively-grown one, per R1/R2) does not.
7. **`context.glyphic`'s `resolveCtx`** is registered but I found no capability in this corpus that
   explicitly requests `surface:'glyphic'`/`'meaning'` context resolution to exercise it (the glyphic
   capabilities themselves don't call `resolveContext` — they read `M.active`/`M.field` directly). It would
   fire correctly if `CV_AI.execute` were called with `surface:'glyphic'`, but nothing in this corpus does
   so today — likely exercised from a UI panel outside app/ai/ (not verified, out of territory).

---

## §D · Corrections to plan/ledger/audit claims

1. **ADVISOR-AUDIT.md §6 ranked item 7 ("MEDIUM — app/ai/* before the G8.3 user panel or any A-phase
   continuation") undersells how far A-phase already reached into app/ai/.** My read finds A1 (role-
   indirection) essentially COMPLETE across every capability in this folder (zero literal `'claude'` pins
   found among glyphic/canvas capabilities — contradicts ROADMAP.md's framing of A1 as forward work "collapse
   the ~33 claude pins to one binding," which reads as not-yet-done; in app/ai/ specifically, it already is).
   The remaining A-phase work concentrated in app/ai/ is narrower than "the whole area needs a pass": it is
   specifically A5 (extract/compose roles unfired) and CV_HOST's `registerKind` (built, unexercised).
2. **CRITERIA.md G0.4 status (☑, "ai-glyphic-language.js = the AI face; the user panel rides G7") is
   accurate for the READ half but overstates the WRITE half's discoverability** — the capability exists and
   the plumbing works (verified: `extra` reaches `setField`), but the declared params schema doesn't name the
   channel. Not a criterion violation (the criterion says "the API is reachable," which is true), but a
   footnote worth adding: reachable ≠ discoverable, and G8.3's eventual user panel will hit the same gap
   (a form built from `params:{...}` would not expose `directed`/`inverse` fields either) unless this is fixed
   first.
3. **CRITERIA.md G8.3 (◐ "AI face ☑ ai-glyphic-language.js; the USER PANEL ☐")** — confirmed accurate: I
   found zero user-facing panel code in app/ai/ (none expected here; this folder is capability-registration
   only). No correction needed, but flagging for the reader who builds G8.3 that they will hit the same
   `params` schema discoverability gap named in D.2/B.1.2 when they build the form.
4. **ROADMAP.md's PHASE A A2 "the `glyph_*` role files are independent drop-ins → safe to fan out once the
   pattern proves on one"** — the pattern has ALREADY proven on two (`glyph_symbol_candidates` via `ai-
   glyphic.js`, `glyph_assist` via `ai-glyphic-language.js`), not zero. The "fan out" gate is met for these
   two; only `glyph_extract`/`glyph_compose` remain genuinely unfired (matches D.1 above).
5. **No claim in any plan file mentions the `glyphic.assist` edge-law blindness (B.1.3)** — this is a new
   finding, not a correction to an existing claim, but it directly affects how "done" A6 should be considered:
   ROADMAP.md lists A6 under DONE-adjacent language ("A — the AI union — DESIGNED + decisions settled"), but
   A6's live payload construction predates R1 (the edge law) and was never revisited after R1 landed. This is
   exactly the "process debt" class ADVISOR-AUDIT.md §4 flags for R1/R2's OTHER consumers — I found one more
   instance of the same class here, in app/ai/, that the audit's file-by-file sweep didn't reach (the audit's
   own scope was cv-meaning/cv-edges/relationships-seed/types-core, not app/ai/).
6. **The folder charter's line "capabilities registered from elsewhere (AIEngine.jsx is referenced in the
   folder charter — where do canvas caps actually live)"** — resolved: `AIEngine.jsx` (composer, 1 registration
   call, helper-dependent) and `ai-capabilities-canvas.js` (27 thin per-canvas wrappers, IN this folder) are
   two DIFFERENT non-overlapping populations, both real, both wired into the one `CV_AI`. Not drift — by
   design, per CLAUDE.md §5's own Traps note.

---

## §E · Inputs for PHASE RECONCILE + the G8.3 user panel + PHASE A continuation

**For PHASE RECONCILE (R1/R2 debt, since this area is a DIRECT consumer of both):**
- Add to the R1 Tim-visible vehicle (ADVISOR-AUDIT.md §8 directive #2): `glyphic.assist`'s payload
  construction (ai-glyphic-language.js:108-118) needs the SAME directed/inverse enrichment `glyphic.read`
  gets for free — either route the payload through `M.field()` per edge kind (reusing the read path,
  zero new mechanism) or hand-build the enrichment; either way this is now-identified debt, not
  hypothetical. Concretely: `vocab.edge_kinds` should become `vocab.relations: edgeKinds.map(k => ({id:k,
  ...M.field('edge',k)}))` so the LLM role sees `directed`/`inverse` per kind, and the Python role's
  `kind` field description should name that a directed kind has a legal inverse-telling choice.
- `context.glyphic`'s `resolveCtx` (ai-glyphic-language.js:145-154) should likewise surface directed/inverse
  shape, not just binding counts — same fix, smaller surface.
- Both `glyphic.author` and `glyphic.author-relation`'s declared `params` should name `directed`, `inverse`,
  `kindWord`, `opWord`, `determiner` explicitly (even as commented-optional) so the write surface's
  discoverability matches its actual (already-working) reach — cheap, no engine change, pure documentation-
  as-schema fix. This directly serves A5's "correctability-by-use" law: the correction path is only easy if
  it's discoverable, not just mechanically possible.

**For G8.3 (the user panel):** build the panel's field-list FROM the same enriched shape (whatever fixes the
point above), not from the current bare `params:{...}` — otherwise the user panel inherits the identical
discoverability gap the AI face has right now, and G0.4's "one API, two faces" mandate would be satisfied
mechanically but not experientially for either face.

**For PHASE A continuation:** A5 (extract/compose) is the one clearly unbuilt piece INSIDE app/ai/'s scope —
no caller fires `glyph_extract`/`glyph_compose` anywhere. CV_HOST's `registerKind` is ready for A1's
environment-side migration (collapsing the 3 hardcoded runtime kinds into registered ones) whenever that
work is picked up — currently correctly deferred (additive, nothing broken by leaving it unexercised).

---

## §F · PROPOSED PLAN-FILE EDITS (tentative — for the lead's judgment, not applied)

1. **ROADMAP.md PHASE A, A1 line:** soften "collapse the ~33 'claude' pins to one binding" — my census
   found this essentially complete for every capability in app/ai/ (0 literal `'claude'` provider pins found
   among the ~35 capabilities across ai-glyphic.js/ai-glyphic-language.js/ai-capabilities-canvas.js). Suggest
   rephrasing to note app/ai/ is DONE for A1 and any remaining `'claude'` pins (if they exist) live in
   AIEngine.jsx or elsewhere outside this folder — a scope note for whichever reader covers that file.
2. **ROADMAP.md PHASE A, A2 line:** note the pattern has proven on two capabilities already (`glyphic.
   generate`, `glyphic.assist`), not zero — the "fan out once it proves on one" language reads as forward-
   looking when it is partly retrospective.
3. **CRITERIA.md G0.4:** consider a sub-note distinguishing "mechanically reachable" (true today) from
   "discoverably reachable via the capability's own declared schema" (the params-shape gap in B.1.2/D.2) —
   this is exactly the class of thing G8.3's user panel will need resolved first.
4. **New line for CRITERIA.md or a G8.3 sub-criterion:** "the collaborative AI's edge vocabulary (glyphic.
   assist's payload) carries the SAME directed/inverse shape the read capability does" — currently absent
   as an explicit criterion anywhere, and now a named, evidenced gap (B.1.3/§E).
5. **A naming suggestion, non-binding:** `ai-glyphic.js` → a name that reads as "icon/symbol foundry" rather
   than "glyphic" bare, since `ai-glyphic-language.js` is the one that's actually "the glyphic language."
   Purely cosmetic; not proposing a file move without the lead's call given the DesignSync/canonical-sync
   surface this would touch (G7.2).
