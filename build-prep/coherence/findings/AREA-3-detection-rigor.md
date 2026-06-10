# Area 3 — Detection rigor: can the system extract its own REAL connection graph, and is a trustworthy graph feasible on THIS codebase?

> Companion to `ANCHOR.md`. This is the **make-or-break** area: for a model an autonomous loop *acts on*,
> a false finding is corrosive — a wrong "unwired" sends an agent to fix nothing, or erodes Tim's trust in
> the whole instrument. Anchor §7.1 names this the engineering heart of the idea. I was asked to be
> rigorous and skeptical, not to confirm. The five sibling areas all hand the hard part *here* (Area 2 §7
> tiers latent detectors and explicitly gates Tier-2 on "Area C's connection graph"). This file answers:
> **what is the measured accuracy gap between the cheap heuristic in place today and a trustworthy graph,
> what hybrid closes it, and what is genuinely achievable now vs aspirational.**
>
> Evidence marking, per Tim's template:
> **Verified** = I executed it this session (real numbers, this run). **Observed** = read in the code
> (file:line). **Inferred** = pattern-match, labelled. **External-prior-art** = from the literature/tools.
> **[my idea]** = design proposal, not yet in the code.

---

## 0 · The one-paragraph thesis (read this first)

The accuracy gap is **not** where the anchor's framing implies. The anchor says the gates are "grep/string-based"
and points at AST as the fix — but the route *extraction* half (bridge side) is **already accurate** on this
codebase (Verified: regex finds exactly the same 115 routes an AST comparison-node walk finds — 115 = 115, zero
divergence), and its fragility is only *latent* (a route string in a future comment would break it). **The entire
live accuracy gap is on the CONSUMER side.** `reachability()` decides "wired" by `route in fe_blob or route in
tests_blob` — a **substring-anywhere** test (suite.py:7121). That is what is *actively wrong right now*: I measured
it, and **of 82 routes the gate currently calls "wired," at least 3 are wired only by a *mention*** — a route name
sitting in a code comment, or a test that merely *asserts the route exists*, with **no real consumer call-site at
all**. The decisive consequence, and the spine of this whole file: **the upgrade is NOT regex→AST.** Even a perfect
AST that extracts `fetch('/api/…')` literals would still mark a wrapper-with-no-caller as "wired," because the
real question is not "does the string appear" but "is this route *reachable from a mount root through a real
call*." That is a strictly bigger analysis. The good news, equally measured: **this codebase is unusually
well-shaped for a real graph** — one centralized `api.ts` client, one module-global `SUITE` the bridge and the
MCP face call by direct attribute (`SUITE.method(...)`, 103 + 20 distinct edges, zero `getattr` route-dispatch),
a file-discovered registry that is *executed* declared-truth, statically-imported FE regions, and an event log
where 58 % of events carry an `address`. A trustworthy graph is **feasible here** — but it is a **three-leg
hybrid (AST static ⋈ registry-as-declared-truth ⋈ event-log runtime edges)**, joined across the Python↔TS HTTP
boundary by a bespoke join no off-the-shelf tool spans, and there is exactly one class (half-migration) it can
only *flag as a candidate*, never *prove*. The rest of this file grounds each clause.

---

## 1 · What the detector does TODAY, exactly (Observed + Verified)

`reachability()` (suite.py:7098-7131) is the whole graph extractor in place. Its body, distilled:

```python
bridge = open(".../runtime/bridge.py").read()
routes = sorted(set(re.findall(r'"(/api/[a-zA-Z0-9_\-/]+)"', bridge)))    # extract  (suite.py:7110)
fe     = "\n".join(read every canvas/app/src/**/*.ts*)                     # consumer corpus (FE)
tests  = "\n".join(read every tests/*.py except the two meta-gates)        # consumer corpus (tests)
for r in routes:
    (wired if (r in fe or r in tests) else orphan).append(r)               # THE DECISION (suite.py:7121)
documented  = orphans listed in self._ORPHAN_ROUTES        # accounted backlog
new_orphans = orphans NOT listed → gate FAILS
stale       = listed but no longer an orphan → self-corrects
```

Three things are load-bearing and each is a distinct rigor problem:

1. **Extraction is a regex over source text** (`re.findall(r'"(/api/...)"')`) — it grabs *any* `/api/…` string
   literal in `bridge.py`, including ones inside comments or docstrings.
2. **The consumer test is `r in fe or r in tests`** — `in` on a giant concatenated string = **substring match
   anywhere**, including inside `//` comments, `#` comments, docstrings, and *tests that mention the route to
   assert it exists rather than to call it*.
3. **The known-set (`_ORPHAN_ROUTES`) is a hand-edited Python dict in source** (suite.py, noted by Area 2 §8) —
   the embryonic disposition store. Out of my scope (Area 2 owns it) but it bounds how the extractor's output is
   *judged*.

The docstring is admirably honest about (1) and the *false-orphan* direction: *"Heuristic (literal-string match —
a route called only via a computed path reads as orphan)"* (suite.py:7105-7106). **What it does NOT flag is the
*false-wire* direction** — a dead route that reads as wired because its name appears somewhere. That direction is
the one I measured as live below, and it is the more dangerous one for an autonomous loop: a false *orphan* sends
an agent to wire something already wired (wasteful, caught by the reviewer gate); a false *wire* **hides a real
dead route forever** (the model says "whole" when it is frayed — the silent failure Tim's own rules forbid).

---

## 2 · The measured accuracy gap on THIS codebase (Verified — real numbers this run)

I did not theorize the gap; I ran it.

### 2.1 Extraction half — already accurate (regex == AST here)
**Verified.** I AST-parsed `bridge.py` and collected every string constant that appears in a `self.path ==`
*comparison node* or a `self.path in (…)` *tuple-membership node* — i.e. strings the parser confirms are
**actually in a routing decision**, not just present in the file:

| extractor | routes found |
|---|---|
| regex `"(/api/...)"` (today) | **115** |
| AST `==` comparisons only | 109 |
| AST `==` + `in (tuple)` comparisons | **115** |

`set(regex) − set(AST) = ∅` and `set(AST) − set(regex) = ∅` — **perfect parity (115 = 115).** The 6-route gap in
my first AST pass was purely my walker not yet handling the `self.path in ("/api/voice/load", "/api/voice/ear/load")`
tuple form (bridge.py:1241) — a 5-line fix, not a method difference. **Reading of this:** on the *current* bridge,
the regex is accurate *because every `/api/` string in the file happens to sit in a real routing comparison* —
there are no `/api/` strings buried in comments today. The regex's fragility is therefore **latent, not active**:
the instant a future session writes `# unlike /api/foo we …` in a comment, or a docstring example route, the regex
over-counts and the AST does not. **The cheap upgrade here (regex→AST) buys structural immunity at near-zero
residual gap. This half is essentially solved.**

### 2.2 Consumer half — actively wrong RIGHT NOW (the real gap)
**Verified.** Of the **82** routes the current gate calls "wired," I reclassified each by whether its references
are *real consumer call-sites* (a non-comment line that is a `fetch(`/`EventSource(`/`requests.*` call) versus
*mere mentions* (comment lines, docstrings, or tests asserting existence). The routes wired **only by mention,
with zero real consumer line:**

| route | how it reads as "wired" | reality |
|---|---|---|
| `/api/mockup-feedback` | 2 FE lines, **both comments** (api.ts:192, Review.tsx:14 — *"RETIRED for this in-app surface"*) | **truly dead** — a retired route the gate calls live. The exact "half-migration leftover" class from anchor §1. |
| `/api/scope` | 7 test lines — incl. `check("bridge.py has an /api/scope route", "/api/scope" in bridge_src)` (address_scope_acceptance.py:152) | a **test that asserts the route's existence** reads as a *caller* of it. No FE consumer. |
| `/api/voice/turn` | 3 test lines, mostly **comments** describing the path (speakable_acceptance.py:161-165) | wired by a test's prose. No FE consumer of this exact path. |
| `/api/stream` | my detector flagged it too — but it has a **real** consumer: `new EventSource('/api/stream?since=' …)` (useAppController.ts:602) | **a false positive in MY measurement** — I looked only for `fetch(`. |

**This last row is itself the most important finding in the file.** Even my *refined* consumer detector — which
already beats `r in fe` by excluding comments — got `/api/stream` wrong, because the FE consumes routes in **at
least three syntactic shapes**: `fetch('/api/…')`, `new EventSource('/api/…')`, and raw-blob `fetch` with
octet-stream bodies (api.ts:130, 143). **There is no single grep or single regex that captures "a real consumer"**
— which is precisely *why* substring-anywhere is the wrong tool and why a real reachability analysis (not a better
pattern) is required.

**The honest headline number:** the substring heuristic mis-states **3 of 82 "wired" routes** as connected when
they have no real consumer (`/api/mockup-feedback`, `/api/scope`, `/api/voice/turn`) — a **~3.7 % false-wire rate**
— and that is a *lower bound*, because my own better detector still mis-classified one route the other way
(`/api/stream`). Both directions of the substring test are noisy. For a model an autonomous loop trusts as
*the definition of done*, a 3–4 % silent-false-wire rate is not a rounding error: it is three dead routes the loop
will *never* return to because the model swears they are whole. **That is the make-or-break, quantified.**

---

## 3 · Why a trustworthy graph IS feasible here (the codebase is unusually well-shaped) (Observed + Verified)

The skeptical question is not "is a call-graph possible in principle" (Python's dynamism makes the *general*
problem undecidable — External-prior-art §6) but "is *this* system's real connection graph extractable with high
enough accuracy to act on." On the evidence, **yes**, because Tim's design choices removed almost every
dynamic-dispatch trap that defeats generic tools:

- **One module-global `SUITE`, called by direct attribute access.** The bridge does **not** route to suite methods
  through a dispatch table or `getattr`. Every handler is `SUITE.<method>(...)` on a known singleton
  (bridge.py:362 `SUITE = Suite(...)`; bridge.py:450-486+ the handlers). **Verified: 103 distinct `SUITE.<method>`
  call-edges** extracted from `bridge.py` by AST `Call(Attribute(Name('SUITE'), attr))` — the *easiest possible*
  case for static call-graph extraction, ~100 % resolvable. (Confirmed there are **zero** `getattr(self, verb)`
  route-dispatch sites in the runtime — the only `getattr`s are `_current_thread` reads, suite.py:4857 etc.)
- **A second, identical-shape consumer: the MCP face.** `mcp_face/server.py` calls **20 distinct `SUITE.<method>`**
  the same direct way (Verified). So the *full* "who calls this capability" picture is two static call-graphs
  (bridge + MCP) over the same singleton — both trivially AST-extractable. A capability with no caller in *either*
  is a real `capability-with-no-consumer` finding (anchor's Tier-2 #1) with no string-matching at all.
- **The FE has ONE centralized client.** Every backend call funnels through the `api` object in `api.ts` (lines
  30-316) as a literal `fetch('/api/…')`. This is a **double-edged** fact and the crux of §4: it is *why* the FE
  side is statically analyzable (one typed chokepoint, ~one literal per route) **and** *why the current check is
  misleading* (the `api.foo` wrapper *existing* is not evidence any mounted component *calls* `api.foo`).
- **FE regions are statically mounted.** **Verified: 18 region components** are `import`ed at App.tsx:30-47 and
  rendered as static JSX tags (`<Toolbar/>`, `<Inbox/>`, `<CognitionView/>`, … — 18 static render sites counted).
  So `FE-component-with-no-mount` (anchor Tier-2 #2) is *statically tractable for the region layer*: an import +
  JSX graph catches an unmounted region cleanly. (The blind spot is the inner registry-driven render — §5.)
- **The registry is *executed* declared-truth, not a string list.** `registry.discover()` (registry.py:55-66)
  `importlib`-loads each `nodes/*.py`, checks `hasattr(mod,'run')`, and reads declared constants into a `NodeType`
  (registry.py:75-90). This is the system *running* its own declaration — the most reliable ground-truth possible
  for "what node-types exist." `rediscover()` (registry.py:68-73) clear+re-walks so a deleted file un-registers.
  **The registry is a leg of the graph that needs no static analysis at all — it is truth by construction.**
- **An addressed event log already exists.** **Verified: 2,106 events in `.data/store/events.jsonl`, 36 distinct
  kinds, and 1,226 (58 %) carry an `address` field** (`{kind, seq, summary, ts, address}`). Kinds like `run`,
  `connect`, `cognition.role.fire`, `op.run`, `chat`, `move`, `config` are *runtime-observed activity at
  coordinates* — exactly the dynamic edges static analysis cannot see.
- **A declared UI address registry.** `design/_system/addresses.json` holds **80 `ui://` entries** (Verified),
  each with `region`/`capabilities`/`represents` — the FE's analog of the backend `object_info`, and the FE reads
  it live via `api.uiInfo()` (api.ts:174-175). This is the FE-side declared-truth leg.

**Net:** the very properties that make this system *hard to navigate by grep* (dynamic, addressed, registry-driven)
are the ones that make it *easy to model by the right three legs* — because the dynamism is **declared in
registries the system already maintains**, not hidden in arbitrary metaprogramming.

---

## 4 · The spine: route-extraction and consumer-detection are two different problems

This is the reframe the anchor's "grep → AST" framing obscures, and the single most important design point.

| | route table (bridge side) | consumer detection (FE/test side) |
|---|---|---|
| current method | regex over `bridge.py` | `route in fe_blob or route in tests_blob` |
| current accuracy | **accurate today** (§2.1, 115=115) | **actively wrong** (§2.2, 3+/82 false-wire) |
| failure mode | *latent* — breaks if a route appears in a future comment | *live* — a comment/test mention counts as a caller |
| right upgrade | AST comparison-node extraction (structural immunity, cheap) | **reachability from a mount root through `api.method` to the `fetch`** — a real graph, not a better pattern |
| residual gap after upgrade | ~0 | the genuine analysis work |

The trap to avoid, which §2.1's satisfying `115 = 115` invites: concluding "AST mostly closes the gap." It closes
the *extraction* gap (small, latent). It does **nothing** for the *consumer* gap (large, live). An AST that pulls
`fetch('/api/x')` literals from `api.ts` would still mark `api.x` "used" while no component imports or calls it.
**The trustworthy consumer signal is a reachability question** — *is route R reachable from a render root, through
a component, through an `api.*` call, to the `fetch`* — which is strictly bigger than literal extraction on either
side. This is the honest core of "cheap heuristic vs trustworthy graph": the cheapness today comes from answering
the *wrong, easier* question (does the string appear) instead of the *right, harder* one (is it reachable).

---

## 5 · The hybrid that closes it — three complementary legs (the answer to "what hybrid")

A trustworthy graph is **not** any one technique; it is three legs where **each covers the others' blind spots.**
This is also the precise build-on-not-beside answer (anchor §4, hard-part #3): every leg already exists.

### Leg A — AST static call-graph (direct edges)
Covers the *direct-call* skeleton, near-100 % accurate on this codebase (§3):
- bridge `self.path` comparisons → the **route table** (AST comparison nodes; §2.1).
- bridge `SUITE.<method>` + MCP `SUITE.<method>` → **capability→caller** edges (103 + 20; §3).
- `api.ts` `fetch('/api/…')`/`EventSource('/api/…')`/blob-`fetch` → **FE-client→route** edges (must handle all
  three shapes — §2.2's `/api/stream` lesson).
- App.tsx `import` + JSX → **region-mount** edges (18 static mounts; §3).
- **Blind to:** dynamic dispatch, registry-driven rendering, computed addresses.
- *External-prior-art:* this is what `pyan`/`code2flow` do for Python and `knip`/`dependency-cruiser`/`madge` do
  for TS — *single-language* call/import graphs. None of them crosses the HTTP boundary (§7). Adapt their
  per-language graph idea; the cross-language join is bespoke (§6).

### Leg B — the registry as declared-truth (the dynamic-dispatch cases Leg A misses)
Covers exactly Leg A's blind spot, with **zero** static analysis — it is truth by construction:
- node-types: `registry.discover()` *executes* `nodes/*.py` (registry.py:55-90) → the live `self.registry.types`.
  A node reached only via the engine's `mod.run()` dispatch is *invisible to AST* but *present in the registry*.
- roles: file-discovered the same way (cognition role registry, exposed via `cognition_capabilities()`).
- FE registry-driven render: `object_info` (node shapes) + `addresses.json` (80 `ui://`) + `cognition_info`
  (roles/edge-kinds) are the FE's declared truth — *"a new role/rule appears here with NO FE code"* (api.ts:181).
  So a component rendered by `.map()` over `object_info` (NodeShape; the inner render App.tsx §3 flagged) is
  **mounted-by-data**: invisible to a static JSX-mount graph, **declared** in the registry it renders from.
- **Reading:** wherever Leg A goes blind (dynamism), the dynamism is *declared in a registry the system already
  maintains*. Leg B reads that declaration instead of trying to statically prove the dispatch.
- *External-prior-art (category match):* this is the **"declared truth vs reality"** discipline that
  `import-linter`/`grimp` (declared allowed-import contracts) and **architecture fitness functions** embody —
  assert the system matches a declared model and fail when it drifts. The system *already has this shape* in
  `doc_drift()` (registry vs written self-description, Area 2 §1). The coherence graph generalizes it: registry
  (should-be) vs Legs A+C (is). *(I did not retrieve grimp/import-linter specifics in search — I map them to the
  category the codebase already implements, not to fabricated feature claims.)*

### Leg C — the event log (runtime-observed edges; positive-only)
Covers what *neither* static nor registry can: computed/`run://` addresses and *liveness confirmation*.
- 1,226 addressed events (§3) are **observed edges**: `connect` (real wiring), `run`/`op.run` (a route/node
  actually executed), `cognition.role.fire` (a role actually fired), `chat`/`act` (a capability actually invoked).
- the 6 *dynamic* `data-ui-ref` in the FE (Verified: `run://${turn?.turn_id}/${rid}` CognitionView.tsx:167,
  `data-ui-ref={p.address}` NodeShape.tsx:140, etc.) are *per-instance* addresses that **cannot** be statically
  enumerated — but **do** appear in the event stream when exercised.
- **The asymmetry, stated explicitly and non-negotiable (Area 6 / patterned-visibility: semantic corroboration is
  positive-only):** a runtime edge **proves an edge exists**; the *absence* of a runtime edge proves **nothing**
  (just "not exercised this window"). Therefore Leg C may **demote** a false orphan (Leg A says "no caller," Leg C
  says "but it ran at T" → not an orphan) but must **never declare** one. A route never seen in the log is *not*
  thereby dead.

### How the three compose (directional, not a vote)
```
Leg A (AST)  proposes the candidate orphan set  (cheap, runs hot, over-approximates "dead")
   → Leg B (registry) demotes the registry-explained ones (node/role/data-driven mounts)
   → Leg C (event log) demotes the runtime-confirmed-live ones
   → the REMAINDER is the trustworthy "real orphan / unwired" set the loop may act on
```
This directionality is what makes it trustworthy: static **proposes** (and may over-call dead — safe direction,
caught downstream); registry + log **only ever demote** (remove false positives); nothing **declares** an edge
dead from absence. The remainder is small, explained, and every member carries its evidence (which leg saw what)
— exactly the anchor's `evidence:` field, now machine-grounded instead of a heuristic's say-so.

---

## 6 · The one piece no off-the-shelf tool gives you: the cross-language route join

**[my idea, grounded]** The Python↔TS edge — *"bridge route `/api/x` is consumed by FE `api.x` / EventSource"* —
is a **string contract across an HTTP boundary**. `pyan`/`vulture`/`code2flow` see only Python; `knip`/`ts-prune`/
`dependency-cruiser`/`madge` see only TS/JS (External-prior-art §7). **No tool spans the boundary** — by design,
because the contract is a runtime string, not a language symbol. So the trustworthy graph requires a **bespoke
join** that none of the prior art provides:

```
route_table   = AST(bridge.py)          # {/api/x → handler-node}             (Leg A)
fe_consumers  = TS-graph(canvas/app/src) # {fetch/ES literal → reachable-from-mount?}  (Leg A)
edge(/api/x)  = route_table ⋈ fe_consumers  ON the literal string, where the
                FE side must be REACHABLE-FROM-A-MOUNT-ROOT, not merely present.
```

What is adaptable: each *single-language* graph (run a TS reachability pass à la knip's mark-and-sweep from the
mount roots; run an AST pass for the route table and `SUITE` edges). What is **yours to build and cannot be
borrowed**: the join on the literal, and the reachability requirement on the FE side that turns "the wrapper
exists" into "a mounted component calls the wrapper that fetches the route." That join is the whole difference
between today's `r in fe` and a trustworthy edge.

---

## 7 · External prior art — what each achieves, where each fails, what's adaptable (External-prior-art)

| tool | does | fails / limitation | adaptable here |
|---|---|---|---|
| **pyan / pyan3** | static Python call-dependency graph (Graphviz) | docs call its analysis *"rather superficial"*; over-approximates; struggles with dynamic method assignment | the AST call-edge *idea* for Leg A — but our `SUITE.method` case is so clean we do it directly, ~100 % |
| **code2flow** | call graph for Python **and** JS | per-language, not cross-language; heuristic name-matching | the dual-language posture — but it won't span the HTTP route boundary (§6) |
| **vulture** | unused functions/classes/vars (dead code) | *"if you do a lot of dynamic access or metaprogramming, Vulture will warn about unused code that is in fact used"* — i.e. it would FALSE-POSITIVE on our registry-`run()` and data-driven mounts | a *cheap candidate-dead pre-filter* — but its output MUST be demoted by Leg B/C, never trusted raw (it would call every `nodes/*.py` `run()` dead) |
| **pyflakes** | error detection; *"tries very hard to never emit false positives"* | intentionally shallow; no call graph, no cross-file reachability | not a graph tool; useful as a *broken-import* sentinel only |
| **import-linter / grimp** | declared import contracts; module-dependency graph | module-level only; declared-truth must be authored; no HTTP/route awareness | **category match**: the "declared truth vs reality" discipline = Leg B + `doc_drift`. *(specifics not retrieved; mapped to the pattern the codebase already runs)* |
| **knip** (the live TS standard; `ts-prune`/`depcheck` archived 2025) | unused files/exports/deps via mark-and-sweep from entry points; some dynamic analysis | *"can't trace dynamic imports or lazy-loaded components — flags components as unused when loaded via React.lazy()"*; *"false positives from dynamic imports, framework conventions, generated files"* | **the mark-and-sweep-from-mount-roots idea is exactly Leg A's FE half** — and knip's documented blind spot (lazy/registry-driven render) is *exactly* our Leg-B blind spot, confirming the leg split is the right shape, not an excuse |
| **dependency-cruiser / madge** | module/import dependency graph + rule validation | import-level, not call-level; same dynamic-import blindness | the import-graph for the region-mount check (App.tsx → regions) — clean here because mounts are static (§3) |
| **code property graphs (CPG)** | unified AST+CFG+DFG; query reachability/data-flow | heavyweight; per-language; tooling (Joern) is C/Java/JS-leaning, costly to stand up | aspirational; overkill — our clean `SUITE` singleton + central `api.ts` make a CPG unnecessary for the edges that matter |
| **architecture fitness functions** | executable assertions that the system matches an intended architecture, run in CI | you must *write* the assertions; they encode intent, not discover it | **this is what the coherence detectors *are*** — each detector is a fitness function over the graph; "more types not more tools" = "declare another fitness function" (Area 2 §6) |

**The through-line:** every mature tool is *single-language* and every one names the *same* blind spot — dynamic
/ lazy / registry-driven dispatch. This is strong external corroboration (External-prior-art) that (a) the
three-leg split is the industry-honest shape, not a local hack, and (b) the cross-language route join is genuinely
not solved by anything off the shelf — it has to be built, and it can be, because this codebase declares its
dynamism instead of hiding it.

---

## 8 · What is genuinely achievable NOW vs aspirational (the unbiased rigor verdict)

Tiered against Area 2's tiering, with the rigor each demands:

### Achievable now, trustworthy (ship it)
- **AST route table** (Leg A, bridge side) — replace the regex with AST comparison-node extraction. ~0 residual
  gap (§2.1), structural immunity to comment-rot. Small, certain win.
- **Consumer reachability for routes** (Leg A FE/test side + the §6 join) — replace `r in fe or r in tests` with:
  (i) FE consumer = a `fetch`/`EventSource`/blob-`fetch` literal **reachable from a mounted region**, NOT a
  substring; (ii) exclude comment/docstring lines; (iii) a test "consumer" must be a real `requests`/`.post`/
  `.get` call, **not a mention or an existence-assertion**. This *directly* fixes the 3 measured false-wires
  (`/api/mockup-feedback`, `/api/scope`, `/api/voice/turn`) and the `/api/stream` shape-blindness (§2.2).
- **capability-with-no-consumer** (Tier-2 #1) — `SUITE.method` AST edges (bridge+MCP, 123 edges) ∖ all suite
  public methods. **Trustworthy now** because dispatch is direct (§3). This is the Tier-2 item Area 2 gated on me,
  and it is *the easy one on this codebase* — a happy surprise the anchor's "AST is hard" framing understates.
- **registry-vs-live / node-on-disk-but-not-registered** (Leg B) — set-difference of `registry.discover(disk)`
  vs `self.registry.types`. Zero analysis, truth by construction.
- **FE-region-with-no-mount** for the **18 statically-imported regions** (Leg A) — import+JSX graph over App.tsx.
  Trustworthy for the region layer.

### Achievable now, but only as a CANDIDATE (must be demoted by B/C, never auto-acted)
- **vulture-style unused-method sweep** beyond the route surface — useful as a cheap pre-filter, but it will
  false-positive on every `nodes/*.py` `run()` and data-driven mount; its output is a *candidate list for Leg B/C
  to demote*, never a finding the loop acts on raw.
- **FE-component-with-no-mount for registry/data-driven inner renders** (NodeShape via `object_info`, `.map()`
  renders) — Leg A is blind here; only Leg B (the registry it renders from) can vouch for it. Trustworthy *only*
  with the registry leg, not from a static mount graph alone.

### Aspirational / honestly bounded (do NOT over-claim)
- **half-migration** (anchor §1's originating incident — the feedback JSONL→annotation-store where the *status
  lifecycle* was silently dropped). **This is NOT a connectivity property and the connection graph cannot prove
  it.** The graph *can* cheaply flag a real **candidate**: *"both the old mechanism (`/api/mockup-feedback`) and
  the new (`/api/annotations`) still have references"* — and indeed `/api/mockup-feedback` is a **live instance**
  of that candidate, sitting dead in the tree right now (§2.2). But *proving the lifecycle was dropped* needs a
  **schema/semantic diff** of the two record shapes (does the new store carry the `pending→applied→dismissed`
  states the old one did?) — out of reach of any call/connection graph. **This is the one place to resist
  optimism:** the graph routes attention to the candidate; it cannot adjudicate the migration. Mark it
  `candidate`, surface it for the RHM/human, never auto-finish.
- **suite-covers-capability** (Area 2 Tier 3) — agreed with Area 2: no clean machine signal; needs either a
  declared `COVERS=[...]` per suite (cheap, honest-by-convention) or coverage instrumentation (heavy). Not a
  spec-able graph detector. Say so.

### The cadence/cost note (anchor §7.6)
Leg A is *cheap* (parse a handful of files — runs every tick/pre-commit). Leg B is *near-free* (read live
registries). Leg C is *free* (read the existing event log; it's already being written). `suite_health`'s
~115-subprocess cost (Area 2 §8) is a *different* detector, not part of the connection graph — the graph itself
is cheap enough to run hot. **So the trustworthy graph does not carry a heavy cadence cost** — the expense in the
anchor's worry is `suite_health`, not extraction.

---

## 9 · Direct answers to the deliverable question

1. **Accuracy gap, cheap heuristic vs trustworthy graph?** *Measured:* the cheap heuristic is **already accurate
   on route extraction** (115=115) but **mis-states ≥3 of 82 "wired" routes** (~3.7 % silent false-wire) and is
   shape-blind on the consumer side (missed `/api/stream`'s `EventSource` consumer). The gap is **entirely on the
   consumer/reachability side**, and the dangerous direction is false-*wire* (a dead route reading as whole — the
   silent-failure class), not false-orphan.
2. **What hybrid closes it?** **AST static call-graph (Leg A) ⋈ registry-as-declared-truth (Leg B) ⋈ event-log
   runtime edges (Leg C)**, composed *directionally*: static proposes the candidate-dead set, registry + log only
   *demote* (positive-only), the remainder is trustworthy. Joined across Python↔TS on the route literal by a
   **bespoke join** no off-the-shelf tool provides (§6), with the FE side requiring *reachability from a mount
   root*, not substring presence.
3. **Achievable now vs aspirational?** *Now, trustworthy:* AST route table, route-consumer reachability,
   capability-with-no-consumer (easy here — direct `SUITE` dispatch), registry-vs-live, region-with-no-mount for
   static regions. *Now, candidate-only:* unused-method sweep, data-driven FE mounts (need Leg B). *Aspirational
   / bounded:* half-migration (graph flags the candidate — `/api/mockup-feedback` proves it — but cannot prove the
   dropped lifecycle; needs schema diff), suite-covers-capability (no clean signal; declared `COVERS` at best).

---

## 10 · Net (the unbiased verdict)

The anchor frames detection rigor as "string → AST" and worries the graph is expensive and hard. The evidence
**partly inverts that.** The *extraction* the anchor worried about is already accurate and the AST upgrade is
cheap and near-perfect. The *real* gap — unflagged by the anchor and by the detector's own docstring — is the
**consumer-side substring test**, which is **wrong right now** (measured: ~3.7 % silent false-wire, the dangerous
direction), because it answers "does the string appear" instead of "is the route reachable from a mount through a
real call." That distinction is the whole game. And the good, equally-measured news: **this codebase is unusually
well-shaped for a trustworthy graph** — a single `SUITE` singleton called by direct attribute (123 clean edges,
zero `getattr` dispatch), a centralized `api.ts`, statically-mounted regions, *executed* registries as declared
truth, and a 58 %-addressed event log — so the dynamism that defeats generic tools is here **declared, not
hidden**. A trustworthy graph is therefore feasible, as a **three-leg directional hybrid** joined across the
HTTP boundary by a bespoke route-literal join, with **one honestly-bounded class** (half-migration: candidate-only,
never proven by connectivity). The discipline that must hold, on pain of corroding the whole instrument: **static
may over-call dead (safe); registry and the event log may only demote (positive-only); nothing declares an edge
dead from absence.** Build the graph that way and the autonomous loop can trust it; ship `r in fe` and the loop
will, three times over, swear a dead route is whole.

— *Area 3, written to leave the idea bigger and more real. The one number to carry forward: 3 of 82.*

---

## ADDENDUM — second-pass corroboration + three complementary findings (2026-06-08, later run)

> A second Area-C agent re-explored independently and **converged on every load-bearing claim above**
> (consumer-side substring is the live gap; three-leg hybrid; half-migration is candidate-only). Rather
> than restate, this addendum records only what the second pass adds that the body above does not have:
> a verified failure-mode of AST itself, an explicit per-edge-type decision matrix, and the verified
> route→**method** binding (the body verified route *extraction* parity, not the method binding). All
> evidence re-anchored. **Verified** = ran a probe this run; **observed** = file:line; **idea** = proposal.

### A1 · The AST-walk-bleed finding — "AST" alone is not the upgrade; *structure-aware* AST is

The body shows regex==AST on route *extraction* (§2.1, 115=115). The complementary risk is on the route→
**method** binding, and it bites hard. **[verified]** My first probe extracted route→method by
`ast.walk(if_node)` collecting `SUITE.*` calls under each `if self.path==R:`. It returned **`/api/run ->
{59 distinct methods}`** — garbage. Cause: `do_POST` is a *flat* `if … return / if … return` sequence
inside one `try` **[observed: `runtime/bridge.py:740-772`]**, and `ast.walk` on an `If` node descends into
the chained/sibling structure, bleeding every later branch's `SUITE.*` calls into the first route.

**The lesson the body doesn't state:** "regex vs AST" is the wrong axis. A *naive* AST fabricates edges
just as a regex does — the real axis is **method-matches-the-control-flow-structure**. Detection rigor is
structural fidelity, not tool choice. This matters for the autonomous loop because a fabricated
route→method edge (`/api/run` "calls" 59 methods) would make *every* one of those 59 read as wired,
manufacturing exactly the false-wire the body measures — via AST, not regex.

**[verified] The structure-aware fix works.** Treating each `if self.path==R:` as its own scoping unit
(collect only `SUITE.*` in that `if`'s own body, recurse through `Try`/nested-`if`, never bleed siblings):
```
routes resolved: 58 | route→method edges: 68 | routes→exactly-1-method: 48/58
  /api/chat -> chat   /api/coa -> coa   /api/capture-idea -> idea_capture
  /api/run -> run, state   /api/move -> set_position, state   (the 2-method = POST-then-return-state)
```
48 of 58 routes bind to **exactly one** Suite method; the rest to two, the second almost always the
read-after-write `state()`. This is the **route→method leg the regex gate produces *none* of** — and it is
what lets a finding become *compound*: "`/api/knobs` binds to `Suite.<m>`, and no FE caller reaches
`/api/knobs`, so `<m>` is operator-unwired — *unless* MCP (the second face) or an internal caller reaches
it." That compound statement is the difference between a finding the loop trusts and one that cries wolf.

### A2 · The per-edge-type rigor matrix (the explicit decision spine)

The body's three-leg hybrid is correct; this makes the *per-edge* method assignment explicit, so the
builder picks the right tool per edge instead of one tool for all. **[idea, grounded in the body's evidence]**

| Edge type | Cheap heuristic | Static AST | Runtime introspection | Recommended |
|---|---|---|---|---|
| FE surface → /api route | **OK** (string literals) | tightens | n/a | cheap-OK; no computed paths exist (body §3) |
| /api route → Suite **method** | **fails** | **exact** (structure-aware, A1) | exact | **static AST** (A1) |
| Suite method → Suite method | fails | partial; **DI seams invisible** | exact (trace) | AST + runtime-cue |
| node-type/model/panel exists | brittle | hard (importlib) | **exact** (live registry) | **introspection** (= Leg B) |
| Suite method → **MCP tool** | fails + **unscanned** | good (`@mcp.tool()`) | exact | **static AST over `mcp_face`** (A3) |
| ui:// → code it represents | n/a | **cannot** (symbolic tag) | n/a | **declare it** (A4) |
| mechanism migrated-to / coexists | fails | **cannot** | **cannot** | **declared migration + git-diff** (body §8) |

The spine claim: **a finding's trust = the trust of its weakest constituent edge.** The regex gate fails
because it asserts a strong conclusion ("unwired") from one weak 2-surface witness; the hybrid earns trust
because the conclusion rests on the *intersection* of independent witnesses, and reports confidence when
they disagree.

### A3 · `mcp_face` is a missed caller surface AND a second dynamic-dispatch exposure

The body counts the MCP face's 20 `SUITE.*` edges (§3) as part of the static graph — correct. The
complementary point: **`reachability()` as written never looks there.** Its caller corpus is *only*
`canvas/app/src` + `tests/` **[observed: `runtime/suite.py:7069-7076`]**. So a Suite method exposed *only*
as an MCP tool (no `/api` route, no FE/test mention) reads as fully unreachable — a guaranteed false
orphan. `mcp_face/server.py` is also a *registry-driven* exposure ("adding a node-type adds zero tools"
**[observed: `mcp_face/server.py:5`]**) — so its reachable *capability* set is registry-driven (Leg B),
not enumerable by reading the file. This is the concrete proof that the false-positive incident is
**structural** (a 2-of-≥6-surface scanner), not bad luck: the missed surfaces are `mcp_face`, `ops/cli`,
`roles/`, `nodes/`, and the internal `runtime/*` call graph **[verified: `grep -rl "/api/"`+`SUITE.`]**.

### A4 · The ui://→code edge is the FE side's broken middle link (E6)

The body notes `addresses.json` as the FE declared-truth leg (§3). The complementary gap: the
address→code link is a **symbolic hand-tag**, not resolvable. `represents` values are `WIRE-review`,
`MOD-registry`, `RHM-modes` **[verified: read from `design/_system/addresses.json`, 71 entries]** — none is
a `code://` address. So the anchor §6 promise "click a finding, drop to the element it's about, RHM
explains it" has a broken middle: ui→`represents` is machine-readable, `represents`→code is human
convention. **[idea]** Make `represents` a real resolvable address (`code://runtime/suite.py#method` or a
typed registry ref) — honours "more types not more tools," and is the small change that lets `address_help`
walk from a clicked gap to the responsible code. Until then, mark E6 *aspirational-pending-declaration*,
not *extractable*.

### A5 · External prior art the body didn't cite (failure-mode-targeted)

Corroborates the body's tool table from the *indirect-dispatch* literature specifically:
- **[external]** FSE-2025 *"Do you have 5 min? Improving Call Graph Analysis with Runtime Cues"* and
  **iResolveX** (arXiv 2601.17888, multi-layered indirect-call resolution) — a few minutes of dynamic
  observation "largely enhances" a static call graph "for free." This is direct external validation of the
  body's Leg C (event log) and of resolving the DI seams (A2 row 3) by runtime cues — the
  state-of-the-art answer for exactly the `critic or self._default_critic` indirect-call pattern
  **[observed: `runtime/suite.py:7225, 7276`]**.
- **[external]** vulture's own remedy for dynamic FPs is a **whitelist + confidence score** (github
  jendrikseipp/vulture); knip's is **declare-your-entry-points** (knip.dev). Both map onto this repo's
  `_ORPHAN_ROUTES` whitelist — so the body's recommendation to add a **confidence signal per finding**
  (registry=certain, AST=high, scan=medium, runtime-cue=corroborating, git-heuristic=low) and gate
  auto-action on it is the industry-standard trust layer, not a local invention.

### A6 · Addendum verdict

Two independent Area-C passes reaching the same thesis from different probes is itself the strongest
signal in this file: the consumer-side reachability gap, the three-leg hybrid, and the
honestly-bounded migration class are **robust conclusions**, not one agent's framing. The additions —
structure-aware AST is the real upgrade (not "AST" as a slogan); the explicit per-edge matrix; the
missed `mcp_face`/CLI surfaces; the broken ui→code link — sharpen *how* to build it without changing
*what* to build. **The make-or-break is winnable as the hybrid; a regex gate with more globs is not it.**

— *Area 3 addendum. Carry-forward numbers: 3 of 82 (false-wire, body) · 48 of 58 (clean route→method, this run) · 2 of 6 surfaces scanned (the structural false-orphan cause).*
