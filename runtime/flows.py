"""runtime/flows.py — the file-discovered FLOW registry (GC1 — the grounded-chain-as-easiest-path law,
Tim's directive 2026-06-10: "make sure that doing so is viable and intuitive through the MCP tools.
Setup of new repeatable or reusable chains, as well as this one in particular").

A FLOW is a registered, multi-primitive PRODUCTION LINE — code that composes the engine's primitives
(run_role/run_items/run_reduce/run_jury + deterministic gates + corpus/surface writes) into a proven,
re-runnable chain. The registry-filling chains (RG10's registry_generation · the transcript miner ·
the pattern cluster) are the founding rows.

WHY a registry (the GC1 evidence): agents — including the one who built the grounded chain — default
to REBUILDING chains ungrounded when the proven chain isn't the easiest path (the rg10 first-draft
failure: all 940 units silently lost). A flow row makes invoking the proven chain ONE call.

THE BOUNDARY (the floor, executable-code half):
  · a flow is AUTHORED in the repo (a committed, reviewed flows/<id>.py) — NEVER through the MCP
    (executable code through the face stays GATED; declarative chains go through save_cascade).
  · a flow is INVOKED through the MCP by NAME with DECLARED params (invoking registered code with
    validated params is exactly what every tool does — run_role runs code too).
  · every flow PROPOSES ONLY (`proposes_only: True` is REQUIRED at discovery — fail loud without it):
    it may compute, write artifacts/corpus records, and surface_review — it must NEVER resolve/
    approve/dispatch or launch claude -p (the source-invariant scan covers flows/*.py).

Mirrors roles/generation_policies EXACTLY (file-discovered, id==filename, fail-loud, rediscover):
each `flows/<id>.py` declares a module-level `FLOW` dict (the row) + a module-level `run(**params)`
(the entry). FLOW fields (all REQUIRED):
  id          — == the file stem (the registry key)
  label       — one human line
  description — what the chain does, at the operator's altitude (the MCP face shows this)
  params      — {name: {"desc": str, "default": <value-or-None-if-required>}} — the DECLARED runnable
                surface; the MCP tool validates against THIS (never **kwargs guessing)
  proposes_only — must be literally True (the floor declaration; discovery REFUSES anything else)

`flows/AGENTS.md` is the drift home (a new row reflects there in the same change).
"""
import importlib.util
import os

FLOW_FIELDS = ("id", "label", "description", "params", "proposes_only")


class Flow:
    """One discovered flow row + its entry. Thin: validation happened at discovery."""

    def __init__(self, spec: dict, run_fn):
        self.spec = spec
        self.id = spec["id"]
        self._run = run_fn

    def run(self, **params) -> dict:
        """Invoke the chain. Unknown param names fail loud HERE (teaching error naming the declared
        set) — never silently ignored, never passed through to a confusing TypeError."""
        declared = set(self.spec["params"])
        unknown = set(params) - declared
        if unknown:
            raise ValueError(
                f"flow {self.id!r} got unknown param(s) {sorted(unknown)} — its declared params are "
                f"{sorted(declared)} (see flows(op='describe', flow={self.id!r})). Fail loud.")
        missing = [n for n, d in self.spec["params"].items()
                   if d.get("default") is None and n not in params]
        if missing:
            raise ValueError(
                f"flow {self.id!r} requires param(s) {sorted(missing)} (no default declared). Fail loud.")
        merged = {n: d.get("default") for n, d in self.spec["params"].items() if d.get("default") is not None}
        merged.update(params)
        return self._run(**merged)


class FlowRegistry:
    """The file-discovered flow registry — flows/<id>.py rows, fail-loud, rediscoverable."""

    def __init__(self):
        self._flows: dict = {}

    def discover(self, dirs=("flows",)) -> "FlowRegistry":
        self._flows = {}
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                path = os.path.join(d, fn)
                stem = fn[:-3]
                spec_l = importlib.util.spec_from_file_location(f"flow_{stem}", path)
                mod = importlib.util.module_from_spec(spec_l)
                spec_l.loader.exec_module(mod)               # an import error fails loud (never skipped)
                row = getattr(mod, "FLOW", None)
                run_fn = getattr(mod, "run", None)
                if row is None or not callable(run_fn):
                    raise ValueError(f"flows/{fn}: must declare a module-level FLOW dict AND a run() "
                                     f"callable — fail loud, never a silent skip of a malformed row.")
                missing = [f for f in FLOW_FIELDS if f not in row]
                if missing:
                    raise ValueError(f"flows/{fn}: FLOW is missing required field(s) {missing} "
                                     f"(required: {FLOW_FIELDS}).")
                if row["id"] != stem:
                    raise ValueError(f"flows/{fn}: FLOW id {row['id']!r} != file stem {stem!r} "
                                     f"(id==filename is the registry law).")
                if row["proposes_only"] is not True:
                    raise ValueError(f"flows/{fn}: proposes_only must be literally True — a flow that "
                                     f"resolves/approves/dispatches is not a flow (the floor).")
                if not isinstance(row["params"], dict):
                    raise ValueError(f"flows/{fn}: params must be a dict of name -> {{desc, default}}.")
                self._flows[stem] = Flow(row, run_fn)
        return self

    def get(self, flow_id: str) -> Flow:
        if flow_id not in self._flows:
            raise KeyError(f"unknown flow {flow_id!r} — registered flows: {sorted(self._flows)} "
                           f"(a flow is a committed flows/<id>.py — authored in the repo, never fabricated).")
        return self._flows[flow_id]

    def rows(self) -> list:
        return [f.spec for f in self._flows.values()]

    def __contains__(self, flow_id):
        return flow_id in self._flows

    def __iter__(self):
        return iter(self._flows)
