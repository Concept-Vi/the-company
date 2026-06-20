"""runtime/operator_memory.py — the file-discovered OPERATOR-MEMORY registry (GC15 — Tim 2026-06-10:
"having growing memory of me in the system is a major feature value that currently doesn't have any
real definition." This file is the definition.)

An OPERATOR-MEMORY row is ONE declared thing known about working with Tim — a rule, a preference, a
standing approval, an articulated principle — with its EVIDENCE attached (his verbatim words, and
where known the exchange:// addresses of the moments that taught it). The registry is the memory ALL
agents get (the RHM, crew, the coldest external agent through the MCP) — not any one harness's
private notes.

THE LIFECYCLE (the same propose→confirm circuit as everything else): the transcript mining PROPOSES
rows when patterns recur (status='proposed'); TIM'S CONFIRMATION makes them standing
(status='confirmed', `confirmed` records when/how — his verbatim where given). A proposed row is
visible but clearly second-class; consumers act on confirmed rows.

SCOPING (designed, partially delivered): each row may declare `scope` — `when` (the GC14
condition-clause: the activity during which this matters most) and/or `where` (a ui://-prefix it
attaches to). Today scope is DATA consumers may filter by; the GC14 injection mechanism (the row
announcing itself when its 'when' is now) is the designed next layer, not built here.

Row shape (REQUIRED: id==stem · rule · why · evidence non-empty list · status confirmed|proposed):
  {id, rule (one sentence, imperative), why (the reason in Tim's terms), evidence:[{quote, source?}],
   scope?: {when?, where?}, status, confirmed?: str}
`operator_memory/AGENTS.md` is the drift home. Pure DATA — nothing here executes, resolves, or
dispatches (the floor; the loader is scanned by the source-invariant).
"""
import importlib.util
import os

ROW_FIELDS = ("id", "rule", "why", "evidence", "status")
STATUSES = ("confirmed", "proposed")


class OperatorMemoryRegistry:
    """The file-discovered operator-memory registry — operator_memory/<id>.py rows, fail-loud."""

    def __init__(self):
        self._rows: dict = {}

    def discover(self, dirs=(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "operator_memory"),)) -> "OperatorMemoryRegistry":
        # ^ dir anchored to the REPO ROOT, not cwd: the old relative default ("operator_memory") returned []
        #   SILENTLY when cwd≠root → the fabric was rule-BLIND on the operator rules (a no-silent-failure
        #   violation, + a likely feeder of the confirming-bias epidemic). 2026-06-21.
        self._rows = {}
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                stem = fn[:-3]
                spec = importlib.util.spec_from_file_location(f"opmem_{stem}", os.path.join(d, fn))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                row = getattr(mod, "MEMORY", None)
                if row is None:
                    raise ValueError(f"operator_memory/{fn}: must declare a module-level MEMORY dict.")
                missing = [f for f in ROW_FIELDS if f not in row]
                if missing:
                    raise ValueError(f"operator_memory/{fn}: MEMORY missing {missing} (required: {ROW_FIELDS}).")
                if row["id"] != stem:
                    raise ValueError(f"operator_memory/{fn}: id {row['id']!r} != stem {stem!r}.")
                if row["status"] not in STATUSES:
                    raise ValueError(f"operator_memory/{fn}: status {row['status']!r} not in {STATUSES}.")
                ev = row["evidence"]
                if not isinstance(ev, list) or not ev or not all(isinstance(e, dict) and e.get("quote") for e in ev):
                    raise ValueError(f"operator_memory/{fn}: evidence must be a NON-EMPTY list of "
                                     f"{{quote, source?}} — a memory of Tim without his words is fabrication.")
                self._rows[stem] = dict(row)
        return self

    def rows(self, status: str | None = None) -> list:
        rs = list(self._rows.values())
        return [r for r in rs if r["status"] == status] if status else rs

    def get(self, rid: str) -> dict:
        if rid not in self._rows:
            raise KeyError(f"unknown operator-memory row {rid!r} — registered: {sorted(self._rows)}.")
        return self._rows[rid]

    def __contains__(self, rid):
        return rid in self._rows

    def __iter__(self):
        return iter(self._rows)
