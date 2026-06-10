"""runtime/checks.py — the file-discovered CHECK registry (G3·S3a — the floor as declarable data).

A CHECK is a DETERMINISTIC gate: a pure function over a value → {passed: bool, reasons: [...]}. No
model, no network, no time — the same value always gets the same verdict. This registry is the
generalization of the arc that kept repeating (refcheck → prose_check → the radar's relation filter):
every time a model judgment misfired on a rule-shaped constraint, the rule became code. Now the rule
becomes a ROW — referenceable by NAME from a cascade decl (`{op:'check', check:'<id>'}`), so declared
chains carry their own floors.

Row shape: checks/<id>.py declares CHECK = {id (==stem) · label · description} + a module-level
`check(value, **params) -> {passed, reasons}` callable. Discovery validates both (fail-loud).
`checks/AGENTS.md` is the drift home. THE FLOOR: checks judge values — they never resolve/approve/
dispatch (scanned by the source-invariant); a check's verdict ROUTES units in a chain (flag or
declared drop — never a silent drop).
"""
import importlib.util
import os

CHECK_FIELDS = ("id", "label", "description")


class CheckRegistry:
    """The file-discovered check registry — checks/<id>.py rows, fail-loud, rediscoverable."""

    def __init__(self):
        self._checks: dict = {}

    def discover(self, dirs=("checks",)) -> "CheckRegistry":
        self._checks = {}
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                stem = fn[:-3]
                spec = importlib.util.spec_from_file_location(f"check_{stem}", os.path.join(d, fn))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                row = getattr(mod, "CHECK", None)
                fn_ = getattr(mod, "check", None)
                if row is None or not callable(fn_):
                    raise ValueError(f"checks/{fn}: must declare a CHECK dict AND a check() callable.")
                missing = [f for f in CHECK_FIELDS if f not in row]
                if missing:
                    raise ValueError(f"checks/{fn}: CHECK missing {missing}.")
                if row["id"] != stem:
                    raise ValueError(f"checks/{fn}: id {row['id']!r} != stem {stem!r}.")
                self._checks[stem] = {"spec": dict(row), "fn": fn_}
        return self

    def get(self, cid: str):
        if cid not in self._checks:
            raise KeyError(f"unknown check {cid!r} — registered: {sorted(self._checks)} "
                           f"(a check is a committed checks/<id>.py; never fabricated).")
        return self._checks[cid]["fn"]

    def rows(self) -> list:
        return [c["spec"] for c in self._checks.values()]

    def __contains__(self, cid):
        return cid in self._checks

    def __iter__(self):
        return iter(self._checks)
