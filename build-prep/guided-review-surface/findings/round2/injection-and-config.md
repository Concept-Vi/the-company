# Round 2 — Injection State & Enriched-Config Axis

> **Scope.** Targeted reads of `runtime/cognition.py`, `runtime/rules.py`, `runtime/suite.py`
> (chat_parts injection path, MODE_REGISTRY, `_chat_part_core`, `rhm_config`/`set_rhm_config`).
> Coverage `cognition.md` (the full territory walk, 2026-06-08) used as prior evidence.
>
> **Evidence convention.** *Observed(file:line)* = read directly from the file.
> *Inferred* = pattern-matched, not execution-verified. Nothing here is painted green.

---

## PART (a) — Injection state: what is complete, what is partial, what is needed

### The injection edge — COMPLETE for recall + ground today

**The full path, observed end-to-end:**

1. **Rule fire** — `chat_parts()` gathers candidate rules from two sources (Observed suite.py:5394–5409):
   - The canonical `INJECTION_RULE` from `cognition.py` (`recall.relevant AND ground.in_scope`, a declared AST rule with `destination="inject"`).
   - Any AST-shaped `rules` a cast role declares (the general path — descriptive `{id,reads,effect,kind}` entries are explicitly skipped at suite.py:5397–5399 via the comment "descriptive {id,reads,effect,kind} role entries are NOT AST rules → skipped").

2. **Readiness gate** — before firing, the rule's declared inputs are checked against the resolved set (suite.py:5414): if not `rule.inputs <= set(resolved)`, skip. This is per-rule readiness (R2-FOLD H2), not a global barrier — a rule referencing a role absent from this turn's wave is cleanly skipped.

3. **Decision + inject-destination filter** — `rule.decide(resolved)` fires; if `fire=True` and `rule.destination == "inject"` and there is a value, `inject_text` is set and a `cognition.inject` event is emitted (suite.py:5419–5438).

4. **Part 2 receives the injected text** — `_chat_part_core` is called with `inject=inject_text` (suite.py:5447). Inside `_chat_part_core` (Observed suite.py:5075–5077):
   ```python
   if inject:
       user_content = (f"{message}\n\n[CONTEXT recalled this turn (use it if relevant): {inject}]")
   ```
   The resolved role value is folded into the Part 2 user content. **The injection edge is fully consumed** — not just wired but proven by reading the final hop.

**Conclusion:** For the canonical `INJECTION_RULE`, the full path from `run://` role output → rule fire → `inject_text` → Part 2 user content is **complete and Observed**. When recall + ground are both in the walkthrough cast (i.e. after K1's 6 `mode_scope` edits), this leg fires immediately with no further code changes.

---

### Single `inject_text` slot — a real bound to name

**Observed (suite.py:5419):** `inject_text = str(decision_r["value"])` — `inject_text` is a scalar string, assigned (not appended) per firing rule. When only one rule fires per turn this is fine. But if a fully-enriched walkthrough cast produces multiple rules with `destination="inject"`, each successive fire **overwrites** the previous value. Only the last rule's injection lands in Part 2.

This is NOT a bug today (only the canonical `INJECTION_RULE` produces a value; connect/check/voice have no AST inject-rules yet). It becomes a limit when future roles have their own `destination="inject"` AST rules. **Accumulation (appending multiple injections into one coherent context block) is net-new when that arrives.** Flagging it now so it is not discovered at wiring time.

---

### G3/G4 partial — connect / check / voice do NOT yet inject

**Observed (roles/connect.py, roles/check.py, roles/voice.py — from coverage cognition.md §3.1):**
The `rules` blocks in connect, check, and voice carry **descriptive** `{id, reads, effect, kind}` dicts, not AST-shaped rules (no `when` op-tree). These are explicitly skipped at suite.py:5397–5399. Additionally, voice's rule carries `kind: "route"` — not an `inject` destination — so even if it were AST-shaped it would not match the `destination=="inject"` check.

**Consequence:** these three roles fire and write their outputs to `run://<turn>/<role>` addresses when in the walkthrough cast. Their structured outputs are present in the store. But nothing in `chat_parts()` currently acts on them — the data is there, the consumption leg is absent. This is what "G3/G4 partial" means concretely: the declared rules need to be promoted to AST form with a `destination` before they produce any effect in a reply.

**Also observed:** `route()` in rules.py handles all five DESTINATION_KINDS (inject / chain / address / surface / lane — Observed rules.py:491–586). However, `chat_parts()` only acts on `destination=="inject"` rules (the check at suite.py:5418). The other four destinations are not consumed during a live turn's part assembly. Chain, surface, and lane destinations would require driver-level wiring beyond the current per-rule loop — this is the G4 job.

---

### What is needed for an enriched guided turn to actually USE the swarm's outputs

Precisely ordered:

| Step | State | What it unlocks |
|---|---|---|
| K1: add `"walkthrough"` to mode_scope of focus/recall/ground/connect/check/voice | Not done — 6 one-line edits in roles/*.py | Fires the swarm during guided turns; lights up CognitionView |
| recall + ground inject via canonical INJECTION_RULE | **Complete** — no new code | Memory-recall and live grounding fold into Part 2 on day 1 after K1 |
| connect / check / voice outputs used in Part 2 | **Partial (G3/G4)** — rules are descriptive, not AST | Requires authoring AST rules with `destination="inject"` per role; then the existing loop in chat_parts picks them up automatically |
| Multiple injections accumulated (not overwritten) | **Net-new** — single `inject_text` slot today | Needed when 2+ roles have inject rules; requires accumulation logic in the chat_parts loop |

**The short answer for the build:** K1's 6 mode_scope edits make the swarm fire AND make recall/ground inject. That is 80% of an "enriched guided turn." Connect/check/voice fire and are stored but dormant until they get AST rules (G3/G4). That is the honest partial state.

---

## PART (b) — The enriched-config axis: where it lives and how it is read

### The question

The guided-turn cast posture (lean vs enriched, and degree) should be a **configurable axis** — mode/sub-mode registry default, tunable at runtime. Where in the existing architecture does this axis belong?

### Layer 1: Declarative default in MODE_REGISTRY (the one source)

**Observed (suite.py:1220–1330):** MODE_REGISTRY is the single source for all mode properties (`grain`, `shape`, `stage`, `brain_config`, `live`, `reserve_r`, etc.). The `walkthrough` mode already carries a `subtypes` dict with `"guided": {}` and `"show-me": {"budget": 8000}` (Observed suite.py:1284–1286).

The natural declarative home for cast posture is a **new axis on the MODE_REGISTRY row**, sibling to `grain`/`shape`/`stage`. Example:

```python
"walkthrough": {
    ...
    "cast_posture": "enriched",   # "enriched" | "lean" | "off"
    "subtypes": {
        "guided":   {"cast_posture": "enriched"},
        "show-me":  {"cast_posture": "lean"},   # show-me drives; lighter cast
    },
    ...
}
```

This follows the same override-by-subtype pattern the `budget` axis already uses (`show-me` overrides `budget` from 6000 to 8000 today). The cast posture axis would be read the same way: top-level mode default, subtype override.

**Observed gap (coverage cognition.md §3.5):** the subtype axis is not currently threaded to the cast system — `cast_for_mode()` keys on the top-level mode string only (Observed runtime/roles.py:210–214 `cast_for_mode`). So per-subtype posture is net-new wiring, not a free flip. The MODE_REGISTRY declaration is cheap; wiring the subtype resolution into `cast_for_mode()` and the `fireable` filter in `chat_parts()` is the real cost.

### Layer 2: Runtime override in rhm_config (the existing precedent)

**Observed (suite.py:1819–1925 `set_rhm_config`):** every persistent runtime config slot lives in `rhm_config` and is validated through `set_rhm_config`'s whitelist. The precedent for a mode-related config axis is `MODE_AUTODETECT` (Observed suite.py:1821): it is declared in the MODE_REGISTRY's spirit, persisted in the rhm node, returned in `rhm_config()`, and settable via `set_rhm_config`.

The `brain_knobs` slot (Observed suite.py:1807, 1823–1836) is the precedent for a **tunable sub-configuration within a mode** — it allows per-call overrides (temperature/max_tokens/top_p) without changing the mode itself.

A `cast_posture` slot following this pattern:

```python
# in rhm_config() return dict:
"cast_posture": c.get("cast_posture", "enriched"),

# in set_rhm_config whitelist:
if k in (..., "cast_posture")
# validated: "enriched" | "lean" | "off"
```

This would make the posture runtime-tunable without a redeploy — the operator can flip it from the settings surface (the same `configure` verb path that sets brain_knobs today).

### Layer 3: How it is read at guided-turn time

**Observed (suite.py:5333–5340):** the `fireable` list is derived from `cast_for_mode(mode)` filtered by `can_fire` and `not is_jury`. The cast-posture axis would gate or subset this list:

```python
posture = self.rhm_config().get("cast_posture", "enriched")
if posture == "off":
    fireable = []
elif posture == "lean":
    fireable = [r for r in cast if r.id in ("recall", "ground") and r.can_fire and not r.is_jury]
# "enriched" = all fireable (current behavior after K1)
```

This is a one-place read in `chat_parts()` — no other code changes. The MODE_REGISTRY declarative default is the value that populates `rhm_config`'s default on first read; the runtime override lets Tim flip it without touching the registry.

### Recommendation

**Two-layer: MODE_REGISTRY declares the per-mode default + subtype overrides; rhm_config holds the live runtime value.** This is exactly how `mode` itself works (registry defines the valid set; rhm_config holds the live selection). The `cast_posture` axis is:

- **Default `"enriched"`** (a right-hand-man reviewing a screen should have memory of past decisions — Tim's own framing from K1).
- **Subtype-overridable** in MODE_REGISTRY (e.g. `"show-me"` could default `"lean"` since the RHM is driving; different posture suits different subtypes).
- **Runtime-tunable** via `set_rhm_config` using the brain_knobs / MODE_AUTODETECT precedent.
- **Read once in `chat_parts()`** at the `fireable` filter (single read point, no branching elsewhere).

**Net-new work:** (a) add `cast_posture` axis to MODE_REGISTRY row + subtypes, (b) add slot to `rhm_config()`/`set_rhm_config()`, (c) add the posture filter in `chat_parts()` at the `fireable` derivation, (d) if per-subtype posture is wanted: thread the subtype resolution into `cast_for_mode()` (flagged net-new by coverage §3.5). Items (a)–(c) are small; (d) is moderate and only needed if guided vs show-me want different casts out of the box.

---

## Summary of findings

| Question | Finding | Status |
|---|---|---|
| Is the injection edge (G3/G4) complete or partial? | **Complete for recall + ground** (canonical INJECTION_RULE full path Observed end-to-end); **partial for connect/check/voice** (rules descriptive, not AST — skipped at suite.py:5397) | Observed |
| Does `_chat_part_core` actually consume `inject`? | **Yes** — `inject` is folded into Part 2 user content as `[CONTEXT recalled this turn: ...]` (Observed suite.py:5075–5077) | Observed |
| What does K1 unlock immediately? | Recall + ground injection into guided turns, zero additional code, on day 1 of K1 | Inferred (same verified path for listening turns; Inferred for walkthrough by extension) |
| What remains partial after K1? | Connect/check/voice fire, write run://, but outputs go unused until AST rules are authored (G3/G4) | Observed |
| Where does the enriched-config axis live? | Declarative: new `cast_posture` axis in MODE_REGISTRY (sibling to grain/shape/stage); runtime: `rhm_config` slot following MODE_AUTODETECT/brain_knobs precedent | Observed (precedent); Inferred (new axis) |
| How is it read at guided-turn time? | Single filter in `chat_parts()` at the `fireable` derivation — one read point, default `"enriched"` | Inferred |

---

## Config criterion (ready for Completion Criteria)

> **Cast-posture axis:** The guided-turn cognition cast posture is a configurable axis. Default `"enriched"` (full cast, recall + ground injecting on day 1 via canonical INJECTION_RULE; connect/check/voice fire-and-store pending G3/G4 AST rules). `"lean"` = recall + ground only. `"off"` = empty cast (today's default behavior). Declared in MODE_REGISTRY as a per-mode/per-subtype default; runtime-tunable via `rhm_config.cast_posture` using the brain_knobs/MODE_AUTODETECT slot pattern; read once at the `fireable` filter in `chat_parts()`.

---

*Written by round-2 research agent, 2026-06-08.*
*Path: /home/tim/company/build-prep/guided-review-surface/findings/round2/injection-and-config.md*
