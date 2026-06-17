---
type: design
module: forms
status: draft (design-grounding — read-only investigation, NOT built)
date: 2026-06-17
governs: [P1, K2, "the capture→forms wire"]
relates-to: ["forms/AGENTS.md", "runtime/forms.py", "runtime/corpus.py", "runtime/cognition.py", "runtime/suite.py", "generation_policies/AGENTS.md"]
---

# DESIGN — the FORM system PROPERLY BUILT INTO the Company

**What this is.** `runtime/forms.py` + `forms/*.py` are a complete, tested, file-discovered registry
(`route(text, meta) → Form{stage, policy}`) — but it is **wired to NOTHING**. No capture/ingest path
calls `route()`; there is no scope dimension; there is no `create_form`; and a form selects only an
effort `stage` + a `policy` id, neither of which can presently reach the model. This document designs
the four pieces that turn the registry into a working organ.

**Read this disclaimer first (epistemic status).** Everything below is *Observed* from the code (file:line
refs given) or *Inferred design* (labelled). Nothing here is built or verified. The current four forms
(`decision`/`log`/`prose`/`registry`) are **Tim's placeholders** — this designs the **MECHANISM**, not the
taxonomy; forms get authored from coverage-pressure later, to Tim's principles.

**The grounding facts (Observed).**
- `route()` checks non-fallthrough forms first (id order), then fallthrough, returns the first `Form` whose
  `match(text, meta=)` is True; fail-loud on empty registry / all-False (`runtime/forms.py:171-193`).
- A `Form` carries `id · stage · policy? · fallthrough? · desc?`; `match` is a **Python callable**
  (`runtime/forms.py:65-87`, schema docstring `:20-38`).
- The capture engine `run_items` fans **ONE role over N units** at **ONE `max_tokens`**, and calls
  `run_role` **without `policy=`** (`runtime/cognition.py:1204-1211`, the run_role call `:1344-1345`). So
  no capture path can presently tier effort OR select a generation-policy per unit.
- The three capture wrappers — `ingest_paths` (`suite.py:10474`), `capture_corpus` (`:10575`),
  `capture_corpus_lenses` (`:10662`) — each apply a **uniform** role + `max_tokens` to every unit. None
  imports `forms` or calls `route()` (grep-verified: no `route(`/`form_registry`/`FormRegistry` in any
  capture method body).
- `run_role` **already** reads a `generation_policy` by id and runs its rep_penalty ladder when
  `policy="<id>"` is passed (`cognition.py:203-356`, the ladder path `:332-356`); a `GenerationPolicy`
  carries `budget`/`json_schema`/`temperature` (`generation_policies.py:96-108`). The plumbing the form's
  `policy` field needs **exists** — only the passthrough from the capture path is missing.
- The shared author gate `_write_registry_file` (`suite.py:9840-9931`) renders a row as a pprint Python
  literal, gates it in a tempdir through the registry's own `discover()`, atomic-writes, commits,
  rediscovers. It **explicitly refuses any callable field** (`:9886-9891`) — which is *exactly why* `form`
  and `lifter` are **excluded** from the `_CORPUS_REGISTRIES` table (`:348-371`, the reasoning `:348-359`).
- Prior art for a **data scope field**: `roles.py` `mode_scope` — a declared `frozenset` on the row; the
  consumer filters by it (`roles.py:91`, `:112-113`, `in_cast` `:262-263`). Prior art for a **data
  predicate** (no lambda): `mode_detection_rules` expresses its `when` as a `rules.RULE_OPS` **data-AST** —
  "the ONE predicate language — never a lambda" (`suite.py:303-305`).
- `project` is **always an explicit argument** (default `"company"`) on every capture call — there is **no
  active-project singleton** anywhere (grep-verified: no `active_project`/`current_project`). The
  project-scope tier must therefore be fed the project the capture call already names.

---

## PART 1 — the OPTIONAL capture→forms wire (effort-routing, off by default)

### The intent
A capture/ingest pass reads each unit's **shape** via `route(text, meta)` → `{stage, policy}`, and uses
that to **TIER effort**: `deep` = the heavy pass, `legibility` = the cheap broad pass, `skip` = don't
capture at all. An **available switch, OFF by default** (a plain capture stays byte-identical).

### The blocking reality (Observed — the advisor's pivot)
`run_items` cannot carry effort today: it is **one role × N units × one `max_tokens`**, calling
`run_role` with **no `policy=`** (`cognition.py:1204-1211`, `:1344`). So even the *existing* `policy` field
on a form has no path to the model, and one `run_items` call is uniform. A wire that just calls `route()`
and logs the stage would **ship hollow** — relabel, not retier. To make effort real end-to-end, two things:

### (1a) BUCKET-BY-BAND in the capture wrapper — the mechanism *(BUILD, small)*
Where today `ingest_paths` builds one flat `units` list and fires one `run_items`
(`suite.py:10550-10551`), the form-aware path instead:

```
forms = self.form_registry                      # already discovered (suite.py:337)
buckets: dict[(stage, policy), list[unit]] = {}
for f in files:
    form = forms.route(f["text"], meta={"path": f["path"], "project": project})
    if form.stage == "skip":
        skipped_by_form.append(f["path"])         # DROPPED from the item list — named, never silent
        continue
    buckets[(form.stage, form.policy)].append(unit_for(f))
for (stage, policy), units in buckets.items():
    band = effort_band_registry.get(stage)        # stage → {max_tokens, slice_chars}  (see PART 4)
    run_items(rd, units, store, turn_id=..., max_tokens=band.max_tokens, policy=policy)
```

- `skip` units are **removed from the item list entirely** (the real effort saving — the whole point: ~half
  a corpus is bookkeeping). Named in the response (`skipped_by_form`), never a silent drop (no-silent-failure
  floor).
- `deep` vs `legibility` differ because each bucket fires its **own `run_items`** at the band's `max_tokens`
  and `policy` — so effort genuinely changes per band.
- `run_items` itself is **untouched** (still one role × N units) — we call it once per bucket. This honours
  reuse-don't-parallel: no second fan path.

### (1b) `policy=` passthrough `run_items → run_role` *(BUILD, small)*
Add an optional `policy: str | None = None` param to `run_items` (`cognition.py:1204`) and forward it on the
`run_role` call (`cognition.py:1344`). `run_role` already consumes it (`:334-356`). Default `None` =
**byte-identical** to today. This is the one-line bridge that lets a form's `policy` reach the model.

### Where the switch lives (OFF by default)
A `by_form: bool = False` parameter on `ingest_paths` / `capture_corpus_lenses` (and the MCP `ingest`
tool, `mcp_face/tools/ingest.py:15`). `by_form=False` (default) = the **exact current flat path**
(one bucket, no `route()`, no skip, no policy) — provably unchanged. `by_form=True` activates the
bucket-by-band path above. The MCP `capture` tool (`server.py:829`) takes **explicit units already
shaped by the caller**, so it stays as-is; the form wire belongs in the **walk-based** wrappers
(`ingest_paths`, `capture_corpus_lenses`) that discover units themselves.

### Hook point (exact)
- `ingest_paths`: between the walk (`suite.py:10501-10545`) and the single `run_items`
  (`:10550-10551`) — replace the flat fire with the bucket loop.
- `capture_corpus_lenses`: between the walk (`:10755-10764`) and its `run_items` (the multi-lens fan) —
  same bucket-by-band insertion; the lens schema is orthogonal (PART 4).

**REUSE vs BUILD:** `route()` = REUSE (+ `meta` already supported). bucket-by-band loop = BUILD(small).
`run_items` policy passthrough = BUILD(small, one param + one forward). The skip-drop + named-skip = BUILD(small).

---

## PART 2 — GLOBAL / PROJECT / USER scoping

### The gap (Observed)
Forms is **flat file-discovery** — every `forms/<id>.py` is always in play; no scope dimension exists
(grep-verified). Tim wants three tiers: **global** (always), **project** (linked to the running project),
**user** (per-user; one user today).

### The design — mirror `mode_scope` (a DATA field + a consumer filter) *(BUILD, small)*
Add an OPTIONAL `scope` field to the form row schema (`FORM_FIELDS`, `runtime/forms.py:61`), schema-additive:

```python
FORM = {
    "id": "decision", "match": _match, "stage": "deep", "policy": "capture_default",
    "scope": "global",                 # OPTIONAL — "global" | "project" | "user"
    "project": "recollection",         # REQUIRED iff scope=="project" (which project it links to)
    "user": "tim",                     # REQUIRED iff scope=="user"   (one user now; future-multi)
}
```
- `scope` defaults to **`"global"`** when absent — so the four current forms (no `scope`) stay global and
  **nothing changes** (behaviour-preserving). `_build_form` (`forms.py:98`) validates: `scope ∈
  {global, project, user}`; a `project`-scoped form MUST declare `project`; a `user`-scoped form MUST
  declare `user`; fail-loud otherwise (mirrors the existing field validation `:104-137`).
- This mirrors `mode_scope` exactly: a declared data field on the row; the **consumer filters by it** at
  read time. No new mechanism.

### route() resolves across the three tiers *(BUILD, small)*
`route()` grows two keyword args fed from the capture call's lineage (which already carries `project`):
`route(text, *, meta=None, project=None, user=None)`. The current signature stays valid (both default
`None` → behave as today, all forms in scope).

**Precedence — the subtle collision the advisor flagged.** Naive "all user forms before any project/global"
lets a *user fallthrough* mask a *global narrow* form. Robust resolution = **collect ALL in-scope matching
forms, then pick by a composite key**:
1. **In-scope filter:** a form is in scope iff `scope=="global"` OR (`scope=="project"` and `f.project ==
   project`) OR (`scope=="user"` and `f.user == user`). A project/user-scoped form whose link doesn't match
   the call is simply **not considered** (not an error).
2. **Collect** every in-scope form whose `match()` is True.
3. **Pick** by sort key `(scope_rank, fallthrough_rank, id)` where `scope_rank: user=0 < project=1 <
   global=2` and `fallthrough_rank: non-fallthrough=0 < fallthrough=1`. So a **narrow global** form beats a
   **fallthrough user** form (narrowness wins within the cross-product), but between two equally-narrow
   forms the **more specific scope** wins. This generalizes the current "specific-before-fallthrough"
   ordering (`forms.py:186-188`) into a 2-axis sort.
4. **Fail-loud** unchanged: no in-scope form matches → RAISE (declare a global fallthrough — the existing
   `prose` form, which is global by default, guarantees a match for any project/user).

### How 'project' links to the active project
There is **no active-project singleton** (Observed). The project-scope tier is fed the **`project` argument
the capture call already names** (`ingest_paths(project=...)` etc., `suite.py:10475`). The capture wrapper
passes that same `project` into `route(..., project=project)`. So "the running project" = the project the
capture pass is running under — explicit, not ambient. (`user` similarly threads from the call's lineage;
one user = `"tim"` today, so it's effectively always-matched, but the dimension is real for the future.)

### Should this generalize to ALL file-discovered registries? *(NOTE — do not build everywhere)*
**Yes, eventually — and forms is the right pilot.** Roles already scope by `mode_scope`; the same
`scope/project/user` triple is meaningful for projections (a project-specific lens), generation_policies
(a project-tuned regime), lifters, etc. The clean home is the **shared registry base** the `lifters.py`
docstring already names as a future reuse pass ("A shared base for the eventual corpus registries is a
FUTURE NEWMOD reuse pass — surfaced, not built", `lifters.py:24-26`). The scope field + the in-scope
filter belong **on that base** when it lands, with **forms as the pilot implementation**. Building scope
into all six registries now would fork six copies of the filter — exactly what reuse-don't-parallel
forbids. **Recommendation:** build scope on forms now; flag it for promotion to the shared base. Note for
Tim: this is a decision point, not an automatic generalization.

**REUSE vs BUILD:** scope field = BUILD(small, schema-additive, mirrors `mode_scope`). route() scope filter +
2-axis precedence = BUILD(small). Generalization to other registries = NOTE/flagged (do not build now).

---

## PART 3 — `create_form` authoring — and the fork the task instruction hits

### The collision (Observed — the BIGGEST design risk)
The task says "design `create_form` on the existing `create()` gate pattern." But the existing gate
(`_write_registry_file`, `suite.py:9840`) **renders the row as a pprint Python literal and explicitly
RAISES on any callable field** (`:9886-9891`). A form's `match` **IS a Python callable** (`forms.py:122`).
This is *precisely* why `form` is **excluded** from `_CORPUS_REGISTRIES` (`suite.py:348-359`). So:

> **`create_form` on the existing gate is IMPOSSIBLE while `match` stays a Python callable.** The task's
> "existing gate" phrasing collides with the code's hard refusal of callables. This fork decides whether
> forms become **truly authorable data** or a **permanently-gated code island.**

There are two honest resolutions. Present both to Tim; do not silently pick one.

### Option A — `match` STAYS a callable → `create_form` is a NET-NEW gated code-render path *(BUILD, larger)*
Keep `match` as Python. Then `create_form` cannot use `_write_registry_file`; it needs a **code-authoring**
contract — the path the code itself leans toward ("a lifter/form needs a CODE-render+gate authoring
contract (create_role-style render of a `def`, or the gated propose→apply path)", `suite.py:355-357`).
Shape: render a `forms/<id>.py` module **source** (the `def _match(...)` + the `FORM = {...}` literal)
either from agent-supplied source text or via a gated `propose→apply` flow, gate it in a tempdir through
`FormRegistry().discover()` (the form registry's **own** `_build_form`, reusing the gate *mechanism* even
though not the *literal* helper), atomic-write, commit, rediscover. This is net-new and unspecified — and it
keeps `match` arbitrarily expressive (any Python the recognizer needs).
- **Cost:** a new code-render+gate path (more surface, executable-code authoring stays a gated affordance).
- **Wins:** zero change to existing matchers; full expressivity.

### Option B — `match` becomes a DATA-AST predicate → `create_form` drops onto the existing shared gate *(BUILD, medium)*
Replace the `match` callable with a **`rules.RULE_OPS` data-AST** — exactly the prior art
`mode_detection_rules` uses ("the ONE predicate language — never a lambda", `suite.py:303-305`). Then a
form row is **pure data**, so:
- `form` joins `_CORPUS_REGISTRIES` as **one new row** (`suite.py:360-371`), and `create_form` becomes a
  **one-liner** like `create_projection` (`suite.py:9933-9939`): `return self._write_registry_file("form",
  spec)`. The existing gate works unchanged.
- Forms become **fully authorable data** — which is what Tim's "NOTHING static / add-a-row = a FILE,
  no code edit" wants (`forms/AGENTS.md:23-25`).
- **Honest cost:** the current matchers use shape-recognition the predicate language must express —
  regex-on-the-first-N-lines (`decision`/`log`/`registry` all do `head = "\n".join(splitlines()[:8])`),
  and **line-ratio counts** (`registry`: `linky/len(lines) > 0.6`, `forms/registry.py:24-25`; `log`:
  `ts_lines >= 3`). `RULE_OPS` would need **shape ops** added (regex-on-head, line-count, link-ratio).
  Either extend the predicate vocab (a real but bounded build) — OR go **hybrid** (next).

### Option C (recommended) — HYBRID: data-AST forms are `create_form`-able; callable forms stay gated *(BUILD, medium)*
`match` accepts **either** a callable (today's matchers, hand-authored, code) **or** a `RULE_OPS` data-AST.
- `_build_form` already validates `callable(match)` (`forms.py:122-126`); extend it to **also** accept a
  data-AST dict (validate it parses under `RULE_OPS`), and `route()` evaluates whichever form it is.
- `create_form` accepts **only data-AST specs** (pure data → rides the existing shared gate as a new
  `_CORPUS_REGISTRIES` row). A callable-match form is **authored as a file by a developer** and stays the
  gated code path (consistent with how node-types/lifters are treated).
- This satisfies the task's "existing gate" phrasing for the data-AST case **and** preserves the existing
  callable matchers **and** matches Tim's principles for new agent-authored forms — without forcing a
  rewrite of the four placeholder matchers on day one. The shape-recognition vocab gets added to `RULE_OPS`
  as forms demand it (coverage-driven, like the rest of the taxonomy).

**Recommendation: Option C.** It is the only one that honours the literal task instruction (data-create on
the existing gate), the floor (executable code stays gated), and Tim's "everything authorable as data"
direction simultaneously — at the cost of one shared predicate-vocab extension rather than a whole new
code-author path. **This is a Tim decision point**, not an agent call: it changes the form schema contract.

**REUSE vs BUILD:** Option A = BUILD(larger, net-new code-render+gate path). Option B = REUSE the shared gate
(one `_CORPUS_REGISTRIES` row + one-line `create_form`) **+** BUILD(medium: RULE_OPS shape ops). Option C =
B's reuse for data forms + keep callable forms gated = BUILD(medium). All three REUSE the `FormRegistry`
discover/`_build_form` validation as the gate mechanism.

---

## PART 4 — how a form selects CONTEXT-PACKAGE + OUTPUT-FORM + effort-stage + policy

### The intent
"Different contexts and outputs by file type" — and the design-intent recall: *"small models can't make
determinations unless the registry contents fit their context."* So a form must size **BOTH ENDS**: the
INPUT (what context the digest model sees, and how much) and the OUTPUT (which lens/schema + how much it may
generate). The form is the per-shape **dossier** the digest model runs under. Mechanism only — NOT which
context for which file type (that's authored from coverage, to Tim's principles).

### The four selectors a form already implies, and the missing two
A form **already** carries the effort `stage` and the `policy` id (`forms.py:27-30`). Add two OPTIONAL,
schema-additive fields (`FORM_FIELDS`, `forms.py:61`):

| selector | field | what it sizes/picks | reuse |
|---|---|---|---|
| **effort-stage** | `stage` (exists) | the band → `max_tokens` + input slice size (below) | the bucket loop (PART 1) |
| **generation policy** | `policy` (exists) | rep_penalty ladder + `budget` + `json_schema` + `temperature` | `run_role` ladder (`cognition.py:332-356`); `GenerationPolicy` (`generation_policies.py:96-108`) |
| **context-package** | `context` (NEW, optional) | what to assemble for the model: a list of `context://` ids and/or input-slice size | `ContextRegistry` already resolves `context://` (`cognition.py:92-95`) |
| **output-form** | `lens` (NEW, optional) | which projection lens(es)/schema the digest produces | `capture_corpus_lenses`' dynamic-schema-from-lenses builder (`suite.py:10731-10752`) |

### Sizing the INPUT (the "contents must fit the model's context" intent)
Today the per-file slice is a **uniform hardcode** `WALK_MAX_CHARS = 6000` (`corpus.py:255`) applied to
every unit (`walk_files` `:285`, and the explicit-path read `:10522`). That hardcode is exactly what the
**band/form should drive**: a `legibility` log needs a small head-slice; a `deep` decision note needs the
full unit. So the **effort-band** (the `stage`, resolved via a small `stage → {max_tokens, slice_chars}`
registry — itself a file-discovered registry to keep it DATA, see below) sets the slice the form's units are
cut to, replacing the global constant on the form-aware path. The form's optional `context` field can
additionally name `context://` packages (resolved through the existing `ContextRegistry`) to **prepend** to
the unit — the assembled package the small model reads.

### Sizing the OUTPUT
The form's `policy` → `GenerationPolicy.budget` → the bucket's `max_tokens` (the form, via its band+policy,
sets how much the model may generate), and `policy.json_schema` selects structured-output mode. The form's
optional `lens` field selects **which** projection lens(es) the digest produces — fed straight into the
**existing** dynamic-schema-from-lenses builder in `capture_corpus_lenses` (`suite.py:10731-10752`), which
already builds one output_schema field per lens from the registry. So "output-form by file type" =
**reuse** that builder, driven by the form's `lens` instead of a caller-passed `lenses` list.

### The `stage → band` registry *(BUILD, small — or fold into forms)*
The mapping `legibility → {max_tokens: 200, slice_chars: 1500}` / `deep → {max_tokens: 768, slice_chars:
6000}` / `skip → drop` should be **DATA, not a hardcode** (the whole module's law). Two options:
(a) a small file-discovered `effort_bands/<stage>.py` registry (cleanest — mirrors the pattern); or
(b) fold `max_tokens`/`slice_chars` directly onto each `Form` row as optional fields. **Recommendation: (a)**
— because `stage` is open-vocab and multiple forms share a band; a band registry keeps the sizing DATA in one
addressable place rather than copied across form rows. Flag as a Tim decision (it adds one more registry).

**REUSE vs BUILD:** `context` field → ContextRegistry = REUSE (registry exists). `lens` field → dynamic
schema = REUSE (`capture_corpus_lenses` builder). `policy.budget`/`json_schema`/`temperature` = REUSE
(`run_role`/`GenerationPolicy`). The two new form fields = BUILD(small, schema-additive). The
`stage → band` sizing registry (replacing the `WALK_MAX_CHARS` hardcode on the form path) = BUILD(small).

---

## ~15-line SUMMARY

1. `runtime/forms.py` + `forms/*.py` is a **complete, tested registry wired to nothing** — no capture path
   calls `route()` (grep-verified across `ingest_paths`/`capture_corpus`/`capture_corpus_lenses`).
2. **PART 1** — the effort wire would ship **hollow** as a naive `route()`-and-log: `run_items` is one role
   × N units × one `max_tokens`, calling `run_role` with **no `policy=`** (`cognition.py:1204`, `:1344`).
3. Make it real: the capture wrapper **buckets units by `route()`'s `{stage, policy}`**, fires one
   `run_items` per band at its `max_tokens`/`policy`, and **drops `skip` units** (named, never silent).
4. Plus a one-param `policy=` **passthrough** `run_items → run_role` (run_role already consumes it). Switch =
   `by_form=False` default → byte-identical to today. Hook = `ingest_paths`/`capture_corpus_lenses`.
5. **PART 2** — no scope dimension exists. Add a DATA `scope` field (`global`|`project`|`user`) mirroring
   `roles.mode_scope`; default `global` keeps today's forms unchanged.
6. `route(text, *, project, user)` filters in-scope, collects ALL matches, picks by `(scope_rank,
   fallthrough_rank, id)` — so a **narrow global beats a fallthrough user** (the precedence collision pinned).
7. `project` links via the **explicit `project` arg the capture call already names** — there is NO
   active-project singleton.
8. Scope **should generalize** to all file-discovered registries, on the **future shared base**
   (`lifters.py:24-26`); build it on forms now as the pilot, flag the rest — do NOT fork six copies.
9. **PART 3 (the biggest risk)** — `create_form` "on the existing gate" is **impossible while `match` is a
   Python callable**: the shared gate explicitly RAISES on callables (`suite.py:9886-9891`), which is why
   `form` is excluded from `_CORPUS_REGISTRIES`.
10. Fork: keep `match` a callable (→ net-new gated code-render path) vs make it a **`RULE_OPS` data-AST**
    (→ drops onto the shared gate as one `_CORPUS_REGISTRIES` row + a one-line `create_form`).
11. **Recommended: Option C hybrid** — data-AST forms are `create_form`-able (pure data → existing gate);
    hand-authored callable forms stay developer-gated. Honest cost: add shape-recognition ops (regex-on-head,
    line-ratio) to `RULE_OPS`. This is a **Tim decision** — it changes the form schema contract.
12. **PART 4** — a form sizes BOTH ENDS: INPUT (effort-band drives the per-unit slice, replacing the
    `WALK_MAX_CHARS=6000` hardcode at `corpus.py:255`; optional `context` names `context://` packages) and
    OUTPUT (`policy.budget`→max_tokens, `policy.json_schema`; optional `lens`→the existing
    dynamic-schema-from-lenses builder, `suite.py:10731`).
13. The "small models need the contents to fit their context" intent = the form is the per-shape **dossier**
    that sizes the assembled input AND the allowed output.
14. **Nearly everything is REUSE-plus-a-small-build:** `route()`, ContextRegistry, the lens-schema builder,
    `GenerationPolicy`, the `run_role` ladder all exist; the builds are the bucket loop, the policy
    passthrough, the scope field+filter, the two new form fields, the stage→band registry, and (per the
    fork) `create_form`.
15. The four current forms are **placeholders** — this is the MECHANISM; the taxonomy is authored later from
    coverage-pressure to Tim's principles.

## THE SINGLE BIGGEST DESIGN RISK
**The `match`-as-callable fork (PART 3).** It is the one place the task's "design `create_form` on the
existing gate" instruction **directly collides** with the code's hard refusal of callable fields
(`suite.py:9886-9891`) — the same refusal that excludes `form` from the author table. The choice made there
decides whether forms become **truly authorable data** (data-AST `match`, on the shared gate) or remain a
**permanently-gated code island** (callable `match`, needing a net-new code-author path). Every other piece
in this design is additive and low-risk; this one is a **schema-contract decision that must go to Tim**
before `create_form` can be built either way.
