"""runtime/capability_handlers/ — the DRY handler layer (Capability Fabric ③④⑤ §3.2).

THE SPINE: pure functions over `Suite` — no socket, no MCP decorator, no `claude -p`. TWO faces call
the SAME handler (the MCP op + the bridge route, drift-tested byte-identical — §3.3 DRY teeth), and
EACH handler declares its RAIL + readonly flag (registry-is-truth; the maintainer MUST declare the
executor — AI-path-of-least-resistance, closing critique-C E1). The reduction-to-primitives lives
SERVICE-SIDE (reduction/*), invisible to the resource-shaped corpus grain.

THE FIVE RAILS a handler may declare (the decisive finding — rails exist, NOT one):
  "direct-read" — DECLARATIVE-DIRECT: reads/resolvers that shell nothing, write nothing, spawn nothing
                  (the only READONLY rail). Safe on every face incl. a cold external agent.
  "R3"          — in-process config/VCS: .claude writes, `claude mcp/plugin`, `git`/`gh` (config_writer.py).
  "R1"          — supervisor mailbox deliver/inject (per-session steer; workflows goal).
  "R1-prime"    — a WIDER-allowlist supervised spawn (in-session git/LSP/computer-use); PROSE result.
  "R2"          — headless `claude -p` wire job behind /api/resolve (code-review, workflows loop).

A handler's signature is `fn(suite, op, **params) -> dict`. It NEVER executes the dangerous rail itself
(the floor — the handler builds the intent/job/argv and routes it; a sanctioned SERVICE acts). For
`direct-read` + R3 reads it returns the result on the call.

THE HONEST `building` STUB: a declared-but-unwired Handler's .fn raises NotImplementedError with a
TEACHING message (NO silent no-op, NO green-paint) and .built is False. A lane wires its real fn via
register_handler(key, fn) — that swaps .fn and flips .built True. This makes "declared vs built"
machine-visible (the burndown the contract corpus reads).

SOLE-OPERATOR FLOOR (Tim's steer — overrides any inherited multi-user caution): the operator is the
ONLY user and is TRUSTED. Dangerous capabilities are ENABLED, gated by a CONSENT BEAT + git-revert
backstop — NEVER locked out, NEVER a multi-user auth wall. The gate is a consent MARKER (config_writer
enforces it), not a denial.
"""
from __future__ import annotations
from typing import Callable

# the closed rail vocabulary (the test pins this tuple + order).
RAILS = ("direct-read", "R3", "R1", "R1-prime", "R2")
# the ONLY readonly rail — readonly IFF a read rail (coherence the Handler ctor enforces).
READONLY_RAILS = frozenset({"direct-read"})


def _stub(key: str) -> Callable:
    """The honest `building` stub — raises a TEACHING NotImplementedError (never a silent no-op). A lane
    replaces it via register_handler; until then calling the handler fails LOUD, naming the gap."""
    def _fn(*_a, **_k):
        raise NotImplementedError(
            f"capability handler {key!r} is DECLARED but not yet WIRED (status: building, not live). Its "
            f"lane registers the real fn via capability_handlers.register_handler({key!r}, fn). Calling it "
            f"now fails loud — never a silent no-op, never green-paint.")
    return _fn


class Handler:
    """One capability handler slot. Declares its REQUIRED rail + readonly coherence (§3.2). The ctor
    FAILS LOUD on an incoherent declaration (a write rail marked readonly, a read rail marked writable,
    an unknown rail) — the maintainer cannot register an executor-incoherent capability."""

    __slots__ = ("key", "rail", "readonly", "fn", "built", "summary")

    def __init__(self, key: str, rail: str, readonly: bool, summary: str = ""):
        if rail not in RAILS:
            raise ValueError(f"Handler({key!r}): rail {rail!r} not one of {RAILS} — every handler MUST "
                             f"declare a known executor rail (§3.2; no default).")
        expect_ro = rail in READONLY_RAILS
        if bool(readonly) != expect_ro:
            raise ValueError(
                f"Handler({key!r}): readonly={readonly} is incoherent with rail {rail!r} — readonly is "
                f"True IFF the rail is a read rail ({sorted(READONLY_RAILS)}). A write rail "
                f"(R3/R1/R1-prime/R2) is never readonly; direct-read always is. Fail loud.")
        self.key = key
        self.rail = rail
        self.readonly = bool(readonly)
        self.summary = summary
        self.fn = _stub(key)
        self.built = False


# THE registry: handler key -> Handler. PRE-DECLARED with the complete ③④⑤ §4 inventory (so the
# corpus + the DRY test see every capability up-front; a lane WIRES its fn, it does not add the key).
def _declare(*specs) -> dict:
    d: dict[str, Handler] = {}
    for key, rail, readonly, summary in specs:
        d[key] = Handler(key, rail, readonly, summary)
    return d


HANDLERS: dict[str, Handler] = _declare(
    # ③ CONFIG-AUTHORING (writes → R3 config_writer; patterns is a pure resolver → direct-read)
    ("config.hooks",         "R3",          False, "hooks list/get/act over settings.json hook blocks (CC-12)"),
    ("config.mcp_servers",   "R3",          False, "mcp-servers list/get/act via claude mcp / .mcp.json (CC-11)"),
    ("config.output_style",  "R3",          False, "output-style + statusLine files/pointers (CC-26)"),
    ("config.slash_commands","R3",          False, "slash-command .md authoring under .claude/commands (CC-03)"),
    ("config.extensions",    "R3",          False, "skill authoring + plugin install/enable (CC-13/CC-34)"),
    ("config.patterns",      "direct-read", True,  "extensibility-patterns resolver — pure read (CC-27)"),
    # ── ③ REOPENED BOUNDARIES (Tim's explicit steer: buildable config-face capabilities, NOT out) ──
    ("config.keybindings",   "R3",          False, "keybindings set/remove → ~/.claude/keybindings.json (CC-04, reopened)"),
    ("config.telemetry",     "R3",          False, "telemetry/data-posture set-flag → settings.json env (CC-32, reopened)"),
    ("config.provider",      "R3",          False, "cloud-provider set-provider → settings.json env CLAUDE_CODE_USE_* (CC-29, reopened)"),
    # ④ DEV-BRIDGES
    ("dev.git",              "R3",          False, "git status/log/worktrees + commit/pr/worktree via git/gh (CC-06)"),
    ("dev.code_intel",       "R1-prime",    False, "in-session LSP nav — prose result, liveness:stream (CC-16)"),
    ("dev.computer_use",     "R1-prime",    False, "in-session web-fetch/search; browser/computer host-bounded (CC-17)"),
    ("dev.code_review",      "R2",          False, "headless claude -p review via /api/resolve — job (CC-19)"),
    ("dev.ci",               "R3",          False, "ci list/get + scaffold (.github/workflows write) (CC-30)"),
    # ⑤ AUTOMATION
    ("auto.routines",        "R3",          False, "routines list/get + run-now/pause/one-off (CC-21)"),
    ("auto.workflows",       "R1",          False, "workflows goal-steer (R1) + loop (R2) (CC-22)"),
    ("auto.cost",            "direct-read", True,  "cost/usage fold over agent_sessions.turn usage (CC-20)"),
    ("auto.auth",            "R3",          False, "auth status read (redacted, CC-24.1) + reopened host-config acts relogin/logout/setup-token (CC-24.2/.3/.4)"),
)


def get(key: str) -> Handler:
    """The Handler for a key. FAILS LOUD (KeyError) on unknown — registry-is-truth."""
    if key not in HANDLERS:
        raise KeyError(f"capability_handlers: no handler {key!r} — declared: {sorted(HANDLERS)}")
    return HANDLERS[key]


def rail_of(key: str) -> str:
    return get(key).rail


def register_handler(key: str, fn: Callable) -> Handler:
    """Wire a lane's real fn onto a PRE-DECLARED handler. Swaps .fn, flips .built True. FAILS LOUD:
      · undeclared key → KeyError (a lane cannot invent a capability; it wires a declared one).
      · non-callable fn → TypeError.
    Returns the Handler."""
    if key not in HANDLERS:
        raise KeyError(f"register_handler: {key!r} is not a declared capability — declared: "
                       f"{sorted(HANDLERS)} (a lane WIRES a declared handler, it does not add keys).")
    if not callable(fn):
        raise TypeError(f"register_handler({key!r}): fn must be callable, got {type(fn).__name__}.")
    h = HANDLERS[key]
    h.fn = fn
    h.built = True
    return h


def keys_for_family(family: str) -> list[str]:
    """The handler keys in a family ('config' | 'dev' | 'auto') — the face/bridge lane partition."""
    return [k for k in HANDLERS if k.split(".")[0] == family]


def load_all() -> dict[str, Handler]:
    """Import the three family modules (③④⑤) so they wire their fns onto HANDLERS, then return it.
    Idempotent (re-import is a Python no-op). Callers (the faces, the bridge, the DRY test) call this
    to get a WIRED registry without caring about import order."""
    from runtime.capability_handlers import config_authoring  # noqa: F401  (③ — wires on import)
    from runtime.capability_handlers import dev_bridges        # noqa: F401  (④)
    from runtime.capability_handlers import automation         # noqa: F401  (⑤)
    return HANDLERS
