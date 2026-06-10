"""coherence_actions — chains/graphs as configurable saveable ACTIONS (Group E, the SAVING side).

A saved chain/graph promoted to a declared, named, LLM-configurable, fireable ACTION. Coherence owns the
saving side: DECLARE + VALIDATE (one `build_action` door, mirrors _build_role) + SAVE + REGISTER, plus the
calibrated config from D (experiment→calibrate→save the winner). The RUNNER is cognition's engine
(run_items/run_reduce) + the existing run_graph — NOT built here (E3). E5 (compose + RUN across models AND
embeddings, swappable per config) is the end-state, gated on the engine; here it is declared + validated +
saved, the run is the convergence-round seam.

Laws: registry-is-truth (a step's model is a REGISTRY ref, never a hardcoded literal — the no-hardcoding law,
enforced in build_action); additive; fail-loud; reflects-never-owns (build_coherence_info is a pure projection).
"""
from __future__ import annotations

import json
import os

from runtime import coherence_detect as _cd

_VALID_OPS = ("generate", "embed", "similarity", "retrieve", "detect", "reduce", "check")


def build_action(decl: dict, *, models: set, roles: set | None = None, rule_resolver=None,
                 check_resolver=None, panel_resolver=None, jury_roles: set | None = None) -> dict:
    """Validate an action declaration through ONE door (compiled / hand-written / saved all gate here —
    mirrors _build_role / the CC-1 build_chain insight). Enforces registry-is-truth: every step's `model`
    must be a member of `models` (the live model registry — chat + embed), never a hardcoded literal (the
    no-hardcoding law).

    N3 — SAVE/RUN PARITY (additive; the cold-agent eval found save-ok decls the runner rejected): when the
    caller supplies `roles` (the live role-registry ids) and/or `rule_resolver` (cognition.resolve_reduce_rule
    — resolves static names AND parameterised patterns like 'tally-by:<field>'), the gate also enforces what
    the RUNNER requires, so ok:True ⇒ runnable: a role is REQUIRED on every step EXCEPT a reduce step with
    reduce_mode='rule' (where a rule is pure — no model, the role was only an address label and is optional);
    a declared role must be REGISTERED; a rule-reduce's reduce_rule must RESOLVE; fan_field must be a
    non-empty string on an items-shaped step. Fail-loud with TEACHING errors. Returns {ok, action} or
    {ok:False, error}."""
    name = decl.get("name")
    steps = decl.get("steps")
    if not name or not isinstance(name, str):
        return {"ok": False, "error": "action declaration needs a name"}
    if not steps or not isinstance(steps, list):
        return {"ok": False, "error": "action declaration needs a non-empty steps list"}
    for i, step in enumerate(steps):
        op = step.get("op")
        if op not in _VALID_OPS:
            return {"ok": False, "error": f"step {i}: unknown op {op!r} (valid: {_VALID_OPS})"}
        model = step.get("model")
        if model is not None and model not in models:
            return {"ok": False, "error": f"step {i}: model {model!r} is not in the model REGISTRY "
                    f"({sorted(models)}) — registry-is-truth: a step's model is a declared registry ref, "
                    f"never a hardcoded literal (no-hardcoding)"}
        # N3 runner-parity checks (only when the caller supplies the live registries):
        is_rule_reduce = (op == "reduce" and step.get("reduce_mode", "role") == "rule")
        is_retrieve = (op == "retrieve")                     # G4: role-less semantic fetch
        is_check = (op == "check")                           # G3·S3a: role-less deterministic gate
        is_panel = (step.get("kind") == "panel")             # G3·S3b: role-less (panel= names the row)
        role_id = step.get("role")
        if roles is not None:
            if not role_id and not is_rule_reduce and not is_retrieve and not is_check and not is_panel:
                return {"ok": False, "error": f"step {i}: declares no `role` — every step fires a model IN "
                        f"a role EXCEPT a rule-reduce, retrieve, or check (all role-less: pure rule / "
                        f"semantic fetch / deterministic gate). Add a registered role id, or use one of "
                        f"those step kinds."}
            if role_id and role_id not in roles:
                return {"ok": False, "error": f"step {i}: role {role_id!r} is not a REGISTERED role "
                        f"(registry-is-truth — author it first via create(kind='role'), or pick from the "
                        f"live set: {sorted(roles)})"}
        if is_rule_reduce and rule_resolver is not None:
            rname = step.get("reduce_rule")
            if not rname or rule_resolver(rname) is None:
                return {"ok": False, "error": f"step {i}: reduce_mode='rule' names reduce_rule {rname!r} "
                        f"which does not resolve — pick a named rule (see reduce_rule_names()) or the "
                        f"parameterised 'tally-by:<field>' pattern."}
        if step.get("kind") == "jury" and jury_roles is not None:
            if role_id not in jury_roles:
                return {"ok": False, "error": f"step {i}: kind='jury' needs a JURY role (draws>1 + a "
                        f"verdict_rule) — {role_id!r} is not one. Jury roles: {sorted(jury_roles)}."}
        if is_panel:
            pname = step.get("panel")
            if not pname:
                return {"ok": False, "error": f"step {i}: kind='panel' needs `panel` — a registered "
                        f"verdict_panels/<id> row name."}
            if panel_resolver is not None:
                try:
                    panel_resolver(pname)
                except KeyError as e:
                    return {"ok": False, "error": f"step {i}: {e.args[0]}"}
        if op == "check":
            cname = step.get("check")
            if not cname:
                return {"ok": False, "error": f"step {i}: op='check' needs `check` — a registered "
                        f"checks/<id> row name (the declared deterministic gate)."}
            if check_resolver is not None:
                try:
                    check_resolver(cname)
                except KeyError as e:
                    return {"ok": False, "error": f"step {i}: {e.args[0]}"}
            of = step.get("on_fail", "flag")
            if of not in ("flag", "drop"):
                return {"ok": False, "error": f"step {i}: on_fail {of!r} — declared modes are "
                        f"flag (annotate, thread all) | drop (thread passing; drops recorded)."}
        uc = step.get("unit_ctx")
        if uc is not None and (not isinstance(uc, dict)
                               or not all(isinstance(k, str) and isinstance(v, str) and "{" in v
                                          for k, v in uc.items())):
            return {"ok": False, "error": f"step {i}: unit_ctx must map input names to address TEMPLATES "
                    "containing {field} placeholders substituted from each unit dict "
                    "(e.g. {'ground': 'run://<turn>/screen_reader/{mockup}'}) — S1, the per-unit context."}
        fan = step.get("fan_field")
        if fan is not None and (not isinstance(fan, str) or not fan):
            return {"ok": False, "error": f"step {i}: fan_field must be a non-empty string naming a LIST "
                    f"field of the previous step's output (e.g. 'groups')."}
        mt = step.get("max_tokens")
        if mt is not None and (not isinstance(mt, int) or isinstance(mt, bool) or mt <= 0):
            return {"ok": False, "error": f"step {i}: max_tokens {mt!r} must be a positive int — the "
                    f"optional per-step output BUDGET (a multi-doc synth step may need ~5000 where the "
                    f"runner default is 256; declare it ON the step, the runner honours it)."}
    shared = decl.get("shared")
    if shared is not None:
        if not isinstance(shared, dict):
            return {"ok": False, "error": "shared must be a dict of name -> {address|text|corpus_query}"}
        for sname, sspec in shared.items():
            if not isinstance(sspec, dict) or len(sspec.keys() & {"address", "text", "corpus_query"}) != 1:
                return {"ok": False, "error": f"shared entry {sname!r}: exactly one of "
                        "{address|text|corpus_query} (S2 — the resolve-once shared inputs; richer "
                        "staging belongs in a flow that prepares run:// addresses first)."}
    action = {"name": name, "steps": steps, "output_schema": decl.get("output_schema", {}),
              "schema_ver": decl.get("schema_ver", 1)}
    if shared is not None:
        action["shared"] = shared
    return {"ok": True, "action": action}


class ActionRegistry:
    """The action registry — saved actions as declared rows in one source (registry-is-truth), persisted to a
    json file so a reload sees them (persistence-survives-reload). Discovered/saved, never a hardcoded list."""

    def __init__(self, path: str):
        self.path = path
        self._actions: dict = {}
        if os.path.exists(path):
            self._actions = {a["name"]: a for a in json.load(open(path, encoding="utf-8")).get("actions", [])}

    def _flush(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"_doc": "saved actions — declared rows (registry-is-truth)",
                       "actions": list(self._actions.values())}, f, indent=2)
        os.replace(tmp, self.path)   # atomic

    def save(self, action: dict):
        self._actions[action["name"]] = action
        self._flush()

    def save_calibration(self, name: str, calibration: dict):
        """D4 — attach the calibrated winning config to the action (experiment→calibrate→SAVE)."""
        if name not in self._actions:
            raise KeyError(f"no action {name!r} to calibrate")
        self._actions[name]["calibration"] = calibration
        self._flush()

    def get(self, name: str) -> dict | None:
        return self._actions.get(name)

    def all(self) -> list:
        return list(self._actions.values())


def build_coherence_info(store) -> dict:
    """E4 — the coherence model's READ-FACE projection (the third sibling beside object_info +
    build_cognition_info). Projects the burn-down + the finding-kind vocabulary (DERIVED from real findings,
    never hardcoded) + the disposition vocabulary (so a surface/CLI reads it from one source —
    registry-is-truth). reflects-never-owns: a pure projection, it writes nothing."""
    roll = _cd.burn_down(store)
    finding_kinds = sorted(roll["by_kind"].keys())                 # derived from the real findings
    return {"burn_down": roll,
            "finding_kinds": finding_kinds,
            "dispositions": list(_cd._VALID_DISPOSITIONS),
            "open_findings": roll["open_findings"]}
