"""runtime/dials.py — the file-discovered DIALS registry (Track-1, 2026-06-10: Tim — "yes they
should be dials. I should be able to adjust them, and not need to make a decision").

A DIAL is an adjustable CHARACTER TRAIT of the entity — not a one-time design decision but a knob
Tim turns whenever he likes. Definitions are registry rows (dials/<id>.py, file-discovered like
everything); VALUES persist on the system graph's dials config node (the same seam as the presence
mode) and are set through Suite.set_dial / the MCP `dials` tool.

Row shape (REQUIRED: id==stem · label · governs · positions non-empty · default in positions):
  DIAL = {id, label, governs (what reads this dial — the consumer seams, named honestly),
          positions: [{name, meaning}, ...] (ordered, low→high), default}

Values may carry condition-scoped OVERRIDES ({when, value}) — Tim confirmed conditions COMBINE; the
`when` is declared data in the rules-engine shape. Overrides are STORED + VALIDATED today and
EVALUATED once the now-organ + rules wiring exists (the flat value applies until then — stated
honestly everywhere, never silently). Pure data; nothing here executes (the floor)."""
import importlib.util
import os

ROW_FIELDS = ("id", "label", "governs", "positions", "default")


class DialRegistry:
    """The file-discovered dials registry — dials/<id>.py rows, fail-loud."""

    def __init__(self):
        self._rows: dict = {}

    def discover(self, dirs=("dials",)) -> "DialRegistry":
        self._rows = {}
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                stem = fn[:-3]
                spec = importlib.util.spec_from_file_location(f"dial_{stem}", os.path.join(d, fn))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                row = getattr(mod, "DIAL", None)
                if row is None:
                    raise ValueError(f"dials/{fn}: must declare a module-level DIAL dict.")
                missing = [f for f in ROW_FIELDS if f not in row]
                if missing:
                    raise ValueError(f"dials/{fn}: DIAL missing {missing} (required: {ROW_FIELDS}).")
                if row["id"] != stem:
                    raise ValueError(f"dials/{fn}: id {row['id']!r} != stem {stem!r}.")
                pos = row["positions"]
                if (not isinstance(pos, list) or not pos
                        or not all(isinstance(p, dict) and p.get("name") and p.get("meaning") for p in pos)):
                    raise ValueError(f"dials/{fn}: positions must be a NON-EMPTY ordered list of "
                                     f"{{name, meaning}} — a dial without named positions is not adjustable.")
                names = [p["name"] for p in pos]
                if len(set(names)) != len(names):
                    raise ValueError(f"dials/{fn}: duplicate position names {names}.")
                if row["default"] not in names:
                    raise ValueError(f"dials/{fn}: default {row['default']!r} not a position "
                                     f"(one of {names}).")
                self._rows[stem] = dict(row)
        return self

    def rows(self) -> list:
        return list(self._rows.values())

    def get(self, did: str) -> dict:
        if did not in self._rows:
            raise KeyError(f"unknown dial {did!r} — registered: {sorted(self._rows)}.")
        return self._rows[did]

    def position_names(self, did: str) -> list:
        return [p["name"] for p in self.get(did)["positions"]]

    def __contains__(self, did):
        return did in self._rows

    def __iter__(self):
        return iter(self._rows)
