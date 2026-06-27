---
type: constitution
register: prescriptive
module: mode_detection_rules
aliases: ["mode_detection_rules — constitution"]
tags: [company, constitution, mode_detection_rules, registry, cognition, activation]
governs: []
relates-to: ["[[Company Map]]", "[[runtime — constitution]]", "[[roles — constitution]]", "[[projections — constitution]]"]
status: living
---

# mode_detection_rules/ — module constitution

**Is:** the **file-discovered MODE-DETECTION-RULE registry** (Concurrent Cognition Group I — the mode
auto-detector). A **mode-detection-rule** is a declared row that maps a SIGNAL CONDITION → a candidate
presence mode. The detector (`runtime/activation.py:detect_mode_candidate`) reads the live
`activity_signal()` snapshot, walks the discovered rules in PRIORITY order (first-match-wins), and
produces a candidate mode — which feeds the EXISTING off/suggest/auto toggle (`Suite.autodetect_mode`).
The rules are a registry **like anything else** (registry-is-truth): a `mode_detection_rules/` dir, one
self-registering `mode_detection_rules/<id>.py` per rule — **exactly mirroring how roles + projections +
node-types self-register** (`roles/`+`runtime/roles.py`; `projections/`+`runtime/projections.py`;
`nodes/`+`runtime/registry.py`). Adding a rule = adding a FILE; it self-registers and is queryable; a
removed file un-registers on `rediscover`.

**Why file-discovered, not a python list (the registry-is-truth BAR — same as projections):** the real
test of "registry-driven" is **add-a-row = a FILE, no code edit.** The detection rules USED to be a
hardcoded `MODE_DETECTION_RULES = [ {..., "when": lambda s: ...} ]` literal in `activation.py` — which
violated two laws at once: (1) add-a-rule meant a CODE EDIT, not a dropped file; (2) a `lambda` is CODE,
not authorable DATA — unvalidatable at discovery, unserializable to a surface, and a SECOND predicate
mechanism beside the G3 rule-engine's declared data-AST. So a rule's condition is now a
**`runtime/rules.py:RULE_OPS` data-AST** (the EXACT grammar the G3 cognition rules use — boolean /
comparison / arithmetic / field-access / membership over a resolved snapshot, NEVER `eval`/`exec`/a
lambda), validated at discovery (`rules.validate_ast`) + evaluated by `rules.evaluate`. reuse-don't-
parallel: the ONE predicate language, the ONE registry mechanism.

**Guarantees:** a rule is **one self-contained declaration** — a module-level `MODE_DETECTION_RULE` dict
over the schema `{id · candidate · why · when · priority}`, **all required**:
- `id` — MUST equal the file stem (addressable by file, like a role/lens/node-type — fail-loud otherwise).
- `candidate` — the presence-mode id this rule proposes (validated ∈ `suite.MODES` at DETECT time — the
  registry can't see the live mode set at discovery, so the detector fail-louds, rule 8).
- `why` — a one-line legible rationale that SURFACES with the suggestion (FORM: legible).
- `when` — the condition data-AST (a `rules.RULE_OPS` tree) over the `activity_signal()` snapshot keys
  (`idle_seconds` · `last_activity` · `mode` · `inbox` · `recent_kinds`). Validated at discovery.
- `priority` — an int; lower fires first. **Detection is ORDER-BEARING (first-match-wins)** — so ordering
  is by this declared integer (then id as a tiebreak), NEVER by `sorted(os.listdir)`/filename order (which
  would couple the detection semantics to filenames — the ordering trap). This is the load-bearing
  difference from the projection/role registries, which are unordered keyed dicts.

A malformed entry (no string id / id≠filename / missing required / unknown field / bad type / a `when`
that fails `validate_ast`) FAILS LOUD at discovery — never a silent skip (a non-`MODE_DETECTION_RULE` /
`_`-file is the one that skips, mirroring the role/projection non-entry skip).

**The None-handling discipline (a real startup correctness point):** at startup / with no operator
activity, `idle_seconds` is **None**. A naive `{ge: [idle_seconds, 900]}` would be `None >= 900` → a
TypeError. So an idle-threshold rule MUST guard the not-None FIRST inside an `and` so the comparison
short-circuits: `{and: [ {ne: [idle_seconds, lit None]}, {ge: [idle_seconds, 900]} ]}` (verified by use:
`rules.evaluate`'s `and` short-circuits + `validate_ast` accepts `lit None`).

**The rules (the live seed set — the drift home; `tests/mode_autodetect_acceptance.py` asserts each is
reflected here, mirroring `projections/AGENTS.md` ← `tests/projections_acceptance.py`):**
- **`background`** (priority 10) — long-idle: when `idle_seconds >= 900` (10 × the 90s idle threshold),
  propose `background` (a low-noise presence). Fires first so a long idle wins.
- **`focus`** (priority 20) — sustained-activity-and-clear-inbox: when `idle_seconds < 90` AND
  `inbox == 0`, propose `focus` (protect deep work with a tight window).
- **`listening`** (priority 30) — work-is-piling-up: when `inbox > 0`, propose `listening` (be present and
  conversational). The fallback "the operator should be engaged" signal.

**Where new things go:** a new rule = a new file `mode_detection_rules/<id>.py` declaring its
`MODE_DETECTION_RULE` dict (its `id` MUST equal the file name; pick a `priority` for its first-match-wins
position). **Update THIS file** (the drift home) when you add one — `tests/mode_autodetect_acceptance.py`
fails loud if a discovered rule isn't reflected here.

**To extend:** drop a `mode_detection_rules/<id>.py`; restart the bridge (or `rediscover`); the rule
appears in the detector's walk with ZERO code change. Tune a rule = edit its `when` AST / `priority` in
its file (file-droppable data, no code edit elsewhere). **Authoring is the file-drop path** (mirroring
projections — no MCP create tool; `mcp_face/server.py` is not this lane's to edit). An MCP
`create_mode_detection_rule` (a data-render+gate authoring contract, like `create_projection`) is a
sensible follow-up but is NEEDS-COORDINATION (it touches the MCP face), not built here.

**Seam:** the registry is instantiated in `Suite.__init__` (`self.mode_detection_rule_registry =
ModeDetectionRuleRegistry().discover([self.mode_detection_rules_dir])`, the `mode_detection_rules/`
sibling of `nodes/`, EXACTLY like `projection_registry`). The detector
(`activation.detect_mode_candidate`) reads `suite.mode_detection_rule_registry.ordered()` + the
`activity_signal()` snapshot; `propose_mode` feeds the candidate to `Suite.autodetect_mode` (the toggle).

**Never:** a `lambda`/string/`eval` condition (use the `rules.RULE_OPS` data-AST — the ONE predicate
language) · ordering by filename/listdir (use the declared `priority`) · a candidate fabricated outside
`suite.MODES` (the detector fail-louds, rule 8) · the detector calling `set_mode` directly (the TOGGLE
owns the posture — suggest surfaces, auto switches; the detector only PRODUCES a candidate) · any
resolve/approve/dispatch effect (the floor: a detection rule produces a candidate, it performs no
consequential action).

> This folder is part of the repo-as-Obsidian-vault — see [[Vault Conventions]].
