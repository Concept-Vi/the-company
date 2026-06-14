"""runtime/routines.py — the file-discovered ROUTINE registry (Session Fabric S-R9.1 / F-CC-21,22).

A ROUTINE is a named, repeatable Claude-Code TASK the Company can FIRE through the session-supervisor:
spawn a real `claude -p` session, inject the routine's prompt, capture the result. It is the
LOCAL-DRIVEN, durable-while-the-machine-is-on equivalent of a cloud routine — reached by DRIVING A
REAL SESSION (the supervisor's spawn/inject), never by reproducing Anthropic's cloud-resident
scheduler (that lives off-machine and is explicitly NOT Company-buildable — see
ui-contract/resources/routines.md).

THE ONE REGISTRY PATTERN. This mirrors runtime/roles.py / runtime/registry.py EXACTLY (the file-
discovered registry; not a fork): a `routines/` dir, one self-registering `<id>.py` per routine,
each declaring a module-level `ROUTINE` dict. Adding a routine = dropping a file; it self-registers
and is queryable + fireable. A removed file un-registers on rediscover. Pure data (imports + one
dict, no def/class), like platforms/claude_code.py.

THE FIRE MECHANISM lives in runtime/routine_runner.py (spawn->inject->capture over the supervisor).
THE TRIGGER LAYER is two arms: (1) schedule — a per-routine systemd .timer bound to company.target
(reuses the ops/systemd/*.timer convention), (2) /fire — the mcp_face/tools/routines.py `routines`
tool (op=fire) + a manual call. This module is just the REGISTRY (what exists); firing + scheduling
are the runner + the trigger arms.
"""
from __future__ import annotations

import importlib.util
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROUTINES_DIR = os.path.join(REPO_ROOT, "routines")

# The routine schema (S-R9.1). Every field except `id` + `prompt` is OPTIONAL; defaults reproduce a
# one-off plan-mode task in the repo. The schema is the closed set — an unknown field FAILS LOUD
# (never a silent typo'd field that no consumer reads), mirroring roles.py's ROLE_FIELDS discipline.
ROUTINE_FIELDS = frozenset({
    "id",              # required; must equal the module name (addressable by file)
    "prompt",          # required; the task the spawned session is asked to do
    "label",           # operator-facing short label
    "description",     # operator-facing description
    "cwd",             # working dir for the spawn (default: the Company repo)
    "model",           # optional model override (e.g. "opus"/"haiku")
    "permission_mode", # default "plan" (read/compute; no unattended edits)
    "cadence",         # OPTIONAL trigger spec: a systemd OnCalendar string OR "every:<seconds>".
                       #   Descriptive here; the schedule arm (systemd timer) reads it. Absent ⇒
                       #   fire-only (manual / mcp op=fire), no schedule.
    "repeats",         # bool: a goal-loop routine re-fires (the runner/evaluator decides); default False
    "max_turns",       # int >= 1: turns to run per fire (default 1 — one prompt, one result)
    "trigger",         # optional free-text description of what should fire it (descriptive)
})


class Routine:
    """One routine, built + validated from a module's `ROUTINE` dict. Dict-passthrough via `.spec`."""

    __slots__ = ("id", "spec")

    def __init__(self, rid: str, spec: dict):
        self.id = rid
        self.spec = spec

    @property
    def prompt(self) -> str:
        return self.spec["prompt"]

    @property
    def cwd(self) -> str:
        return self.spec.get("cwd") or REPO_ROOT

    @property
    def model(self):
        return self.spec.get("model")

    @property
    def permission_mode(self) -> str:
        return self.spec.get("permission_mode") or "plan"

    @property
    def cadence(self):
        return self.spec.get("cadence")

    @property
    def repeats(self) -> bool:
        return bool(self.spec.get("repeats"))

    @property
    def max_turns(self) -> int:
        return int(self.spec.get("max_turns") or 1)

    def record(self) -> dict:
        """The operator/tool-facing projection (what mcp_face/tools/routines.py op=list/get returns)."""
        return {
            "id": self.id, "label": self.spec.get("label"),
            "description": self.spec.get("description"), "prompt": self.prompt,
            "cwd": self.cwd, "model": self.model, "permission_mode": self.permission_mode,
            "cadence": self.cadence, "repeats": self.repeats, "max_turns": self.max_turns,
            "trigger": self.spec.get("trigger"),
        }


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_routine_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


def _build_routine(name: str, decl: dict) -> Routine:
    """Validate + build a Routine. FAIL LOUD on a malformed routine (mirrors roles.py._build_role):
    a declared routine with a bad shape RAISES — never silently skipped (a non-routine file skips)."""
    if not isinstance(decl, dict):
        raise TypeError(
            f"routine module {name!r}: ROUTINE must be a dict, got {type(decl).__name__} — "
            f"fail loud, never a silent malformed routine.")
    rid = decl.get("id")
    if not rid or not isinstance(rid, str):
        raise ValueError(f"routine module {name!r}: ROUTINE declares no string `id` — fail loud.")
    if rid != name:
        raise ValueError(
            f"routine module {name!r}: ROUTINE id {rid!r} != module name {name!r} — the id must "
            f"equal the file name (addressable by file, mirroring roles/nodes). Fail loud.")
    if not decl.get("prompt") or not isinstance(decl.get("prompt"), str):
        raise ValueError(
            f"routine {rid!r}: ROUTINE declares no string `prompt` — a routine IS a task to run; "
            f"fail loud (never a routine that fires an empty turn).")
    unknown = [k for k in decl if k not in ROUTINE_FIELDS]
    if unknown:
        raise ValueError(
            f"routine {rid!r}: unknown field(s) {unknown} — the S-R9.1 schema is "
            f"{sorted(ROUTINE_FIELDS)}. Fail loud (never a silent typo'd field no consumer reads).")
    mt = decl.get("max_turns", 1)
    if not isinstance(mt, int) or mt < 1:
        raise ValueError(f"routine {rid!r}: max_turns must be an int >= 1, got {mt!r} — fail loud.")
    cad = decl.get("cadence")
    if cad is not None and not isinstance(cad, str):
        raise ValueError(f"routine {rid!r}: cadence must be a string (OnCalendar or 'every:<s>') "
                         f"or absent, got {cad!r} — fail loud.")
    return Routine(rid, dict(decl))


class RoutineRegistry:
    """The file-discovered routine registry — mirrors RoleRegistry/NodeRegistry. Dict-like:
    `reg[id] -> Routine`, `id in reg`, `.get(id)`, `.ids()`. Adding a routine = dropping
    `routines/<id>.py`."""

    def __init__(self):
        self.routines: dict[str, Routine] = {}
        self._dirs: list[str] = []

    def discover(self, dirs: "list[str] | None" = None) -> "RoutineRegistry":
        self._dirs = list(dirs) if dirs is not None else [ROUTINES_DIR]
        self.routines = {}
        for d in self._dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "ROUTINE", None)
                if decl is None:
                    continue                      # a non-routine .py in the dir → skip (not a routine)
                routine = _build_routine(name, decl)
                if routine.id in self.routines:
                    raise ValueError(f"duplicate routine id {routine.id!r} across {self._dirs} — "
                                     f"fail loud (one id, one file).")
                self.routines[routine.id] = routine
        return self

    def rediscover(self) -> "RoutineRegistry":
        return self.discover(self._dirs or None)

    def ids(self) -> list:
        return sorted(self.routines)

    def get(self, rid: str):
        return self.routines.get(rid)

    def __getitem__(self, rid: str) -> Routine:
        if rid not in self.routines:
            raise KeyError(f"no routine {rid!r} — registered: {self.ids()}. "
                           f"Add routines/{rid}.py (a ROUTINE dict). Fail loud.")
        return self.routines[rid]

    def __contains__(self, rid: str) -> bool:
        return rid in self.routines


def routine_registry(dirs: "list[str] | None" = None) -> RoutineRegistry:
    """Fresh-discover each call (a routine drop is picked up without restart) — mirrors the
    skill_registry()/context_registry() fresh-discover pattern, NOT a cached singleton."""
    return RoutineRegistry().discover(dirs)
