"""runtime/verdict_panels.py — the file-discovered VERDICT-PANEL registry (GC7 — Tim 2026-06-10: the jury is "like a
panel, and it would be easy to add additional roles").

A PANEL is a declared set of SEATS — each seat a distinct LENS role — plus a quorum rule. It is the
PERSPECTIVE-DIVERSE form of the jury: where run_jury measures one role's self-consistency (N varied
draws of the SAME role), run_panel measures agreement across DIFFERENT judgments (each seat looks at
a different failure mode: grounding / voice / element-fit / ...). Diversity catches what redundancy
can't; the E4 caveat (correlated draws ≠ independent error) is the reason this registry exists.

THE SEAT CONTRACT: every seat role's output carries `grounded: bool` (+ prose). The combine is
DETERMINISTIC (grounded-seats >= quorum), no model — L2, exactly like the jury's verdict_rule.
Add a seat = edit the declared row; add a panel = add a FILE (verdict_panels/<id>.py with a module-level
PANEL dict). Mirrors flows/roles/generation_policies (file-discovered, id==stem, fail-loud,
rediscoverable). `verdict_panels/AGENTS.md` is the drift home. THE FLOOR: a panel JUDGES — its verdict
flags/confirms for the operator's review; it never resolves/approves/dispatches.

PANEL fields (all REQUIRED):
  id          — == the file stem
  label       — one human line
  description — what this panel judges, at the operator's altitude
  seats       — [role ids] (>=2 — one seat is just a role; resolved against the live role registry
                AT RUN TIME, fail-loud on an unregistered seat)
  quorum      — int: the MINIMUM grounded-seats for a True verdict (1..len(seats))
"""
import importlib.util
import os

PANEL_FIELDS = ("id", "label", "description", "seats", "quorum")


class PanelRegistry:
    """The file-discovered panel registry — verdict_panels/<id>.py rows, fail-loud, rediscoverable."""

    def __init__(self):
        self._panels: dict = {}

    def discover(self, dirs=("verdict_panels",)) -> "PanelRegistry":
        self._panels = {}
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                stem = fn[:-3]
                spec_l = importlib.util.spec_from_file_location(f"panel_{stem}", os.path.join(d, fn))
                mod = importlib.util.module_from_spec(spec_l)
                spec_l.loader.exec_module(mod)
                row = getattr(mod, "PANEL", None)
                if row is None:
                    raise ValueError(f"verdict_panels/{fn}: must declare a module-level PANEL dict (fail loud).")
                missing = [f for f in PANEL_FIELDS if f not in row]
                if missing:
                    raise ValueError(f"verdict_panels/{fn}: PANEL missing required field(s) {missing}.")
                if row["id"] != stem:
                    raise ValueError(f"verdict_panels/{fn}: PANEL id {row['id']!r} != file stem {stem!r}.")
                seats = row["seats"]
                if not isinstance(seats, (list, tuple)) or len(seats) < 2 or \
                        not all(isinstance(x, str) and x for x in seats):
                    raise ValueError(f"verdict_panels/{fn}: seats must be a list of >=2 role ids "
                                     f"(one seat is just a role — use run_role/run_jury).")
                q = row["quorum"]
                if not isinstance(q, int) or isinstance(q, bool) or not (1 <= q <= len(seats)):
                    raise ValueError(f"verdict_panels/{fn}: quorum {q!r} must be an int in 1..{len(seats)}.")
                self._panels[stem] = dict(row)
        return self

    def get(self, panel_id: str) -> dict:
        if panel_id not in self._panels:
            raise KeyError(f"unknown panel {panel_id!r} — registered: {sorted(self._panels)} "
                           f"(a panel is a committed verdict_panels/<id>.py; never fabricated).")
        return self._panels[panel_id]

    def rows(self) -> list:
        return list(self._panels.values())

    def __contains__(self, pid):
        return pid in self._panels

    def __iter__(self):
        return iter(self._panels)
