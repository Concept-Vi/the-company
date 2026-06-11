"""runtime/config_writer.py — the R3 CONFIG-WRITER service (Capability Fabric ③④⑤ §3.1).

THE ONE genuinely-new rail of the ③④⑤ Capability Fabric (the other two: the session supervisor's
R1/R1-prime interactive sessions in `session_supervisor.py`, and `implement.py`'s R2 headless wire).
The ONLY process that MUTATES `.claude`/host config, shells the native `claude mcp`/`claude plugin`
config CLI, and runs structured `git`/`gh`. The faces NEVER do any of this (the floor, §1.2: the
bridge/MCP face calls this service; this service acts). Like the session-supervisor it is an
operator-sanctioned SERVICE, binds 127.0.0.1 ONLY (exposure law, audit B3 — no env widens it;
widening is a recorded decision + a code change here), and FAILS LOUD with a teaching error on every
genuine breakage (no-silent-failures).

REGISTRY-IS-TRUTH (the binding to the L-FOUND-handlers reduction registries — arch §3.2):
this service holds NO inline allowlist of its own. WHAT each ③ act writes comes from
`capability_handlers.reduction.config_targets` (handler-key → row: kind/pointer/dangerous/teach/
scope path); WHICH native CLI an act runs + its TIER comes from
`capability_handlers.reduction.cli_allowlist` (act → argv-array template + read/write/exec tier).
A new capability is a new REGISTRY ROW, never a code edit here — the registry is the boundary.

────────────────────────────────────────────────────────────────────────────────────────────
SECURITY = CONSENT-NOT-LOCKDOWN (Tim's explicit sole-operator steer — overrides any multi-user
caution the arch doc inherited)
────────────────────────────────────────────────────────────────────────────────────────────
Tim is the ONLY user and is TRUSTED. The dangerous capabilities — hook `command`, skill/command
`body`, MCP stdio `command`, plugin install, git writes — are ENABLED, never locked out, never
behind an auth wall. The floor is: an agent must not do something IRREVERSIBLE without a CONSENT
SIGNAL, and git-revert is the backstop. The gate is a CONSENT BEAT, not a denial:

  · A `write`/`exec`-tier act (config_targets `dangerous=True`, or cli_allowlist tier write/exec)
    needs a consent signal: per-call `consent=true` (the operator-vantage POST — the /api/resolve
    operator-only precedent) OR a standing marker (a store ref `config_writer/consent:<class>`
    holding "granted", set via /consent, revocable).
  · WITHOUT the signal the service does NOT deny — it returns a PENDING-PROPOSAL receipt naming
    exactly what consent unlocks (a cold agent may PROPOSE; the consequential act is operator-
    confirmed). The trusted operator (consent=true) is NEVER refused.
  · `read`-tier acts (reads, the patterns resolver) are DECLARATIVE-DIRECT — ungated, always run.

Beyond the consent beat, every write is also (arch §5.2 — the content-provenance the proposals
under-reached): (1) SCOPE-validated — scope ∈ the registry's real scope set, resolved to the real
on-disk file (the `_safe_mockup_path` realpath+commonpath PATTERN re-derived PER config-file root,
not the single-root function); (2) CONTENT-validated — the dangerous payload's shape is checked and
the teaching text names WHAT will execute; (3) ATOMIC + BACKED-UP — tmp + os.replace, a `.bak` of
the prior file; (4) LOUD — unknown key / bad scope / nonzero CLI exit → a teaching error, never a
silent no-op or fallback.

INTROSPECTIVE-DATA law (arch §5.6): every consequential act writes a run-record event
(`config_writer.*` — who, which row, args REDACTED, exit, evidence-probe) so misuse/drops/refusals
become gap-pressure signal. NOTE (honest, §5.6): the structured {code,teach,retryable} envelope is
NOT yet on any wire (CONVENTIONS admits this) — teach-TEXT today, the envelope a named follow-up.

HTTP API (127.0.0.1:8772 — the ONE number ops/services.json + the unit cite; CONFIG_WRITER_ROUTES
is the inventory source, CONTRACT-FORMAT §9.3/V21, drift-tested both directions):
  GET  /health                                              → {ok, service, bind, model, consent_classes}
  POST /read    {key, scope?, name?, project_dir?}          → a scope-validated .claude READ (no consent)
  POST /write   {key, scope?, name?, block?, body?, consent?, project_dir?}  → a .claude WRITE (gated)
  POST /cli     {act, consent?, **slots}                    → a native claude mcp/plugin CLI (gated by tier)
  POST /git     {act, cwd, consent?, args?}                 → structured git/gh (gated by tier)
  POST /consent {class, grant: true|false}                  → set/clear a standing consent marker

Run: .venv/bin/python runtime/config_writer.py [port]   ·   service: company up config-writer
Proven by: tests/config_writer_acceptance.py (scratch .claude write→re-read round-trip, the
consent-not-lockdown beat — unconsented dangerous act → pending-proposal then consented-succeeds,
standing-consent grant/revoke, scope/path/content refusals, the CLI/VCS tier gate + argv-array
injection-resistance, run-records, route drift — all by USE on an ISOLATED tmp tree). LEAD-ONLY law:
this worker fires NO real config-mutating CLI; the REAL `claude mcp add` (proven by `claude mcp
list`), `claude plugin install`, and a real `git commit` sha are the build lead's **live-verify
pending (lead)** slice — NEVER green-painted here."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from store.fs_store import FsStore
from fabric import config as fcfg
from runtime.capability_handlers.reduction import config_targets as CT   # REGISTRY: what ③ writes
from runtime.capability_handlers.reduction import cli_allowlist as CL    # REGISTRY: which CLI + tier

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PORT = 8772                    # next free beside supervisor 8771 / bridge 8770 (the ONE number)
HOME = os.path.expanduser("~")

# THE INVENTORY SOURCE for the config-writer-http transport (CONTRACT-FORMAT §9.3 / V21: a transport
# without a machine-readable route registry fails contract validation — the BRIDGE_ROUTES /
# SUPERVISOR_ROUTES law applied here, (method, path) from birth §9.1). The acceptance test greps the
# do_GET/do_POST dispatch literals and asserts this tuple EQUALS them, BOTH directions, fail-loud.
CONFIG_WRITER_ROUTES = (
    ("GET", "/health"),
    ("POST", "/read"),
    ("POST", "/write"),
    ("POST", "/cli"),
    ("POST", "/git"),
    ("POST", "/consent"),
)

# the consent CLASSES (the consent-not-lockdown gate's revocable standing-marker keys). Each is
# ENABLED; consent is a SIGNAL, never a wall. A dangerous ③ config write → `config-write`; a cli/git
# `write`/`exec`-tier act → the tier-named class (so a standing grant can be scoped: e.g. allow git
# commits without also pre-consenting plugin installs).
CONSENT_CLASSES = ("config-write", "cli-write", "cli-exec", "git-write")
CONSENT_REF_FMT = "config_writer/consent:{}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class WriteRefusal(Exception):
    """A refusal that TEACHES (the supervisor's TeachingRefusal precedent; never a bare error). This is
    for genuine breakage — unknown key, bad scope, traversal, schema/argv failure, nonzero CLI exit.
    The CONSENT beat is NOT this: an unconsented dangerous act is a PENDING PROPOSAL (consent-not-
    lockdown), not a WriteRefusal. Mapped to HTTP 400 (bad input) / 409 (CLI refused / nonzero exit)."""


def _find_bin(which: str) -> str:
    """Resolve the leading binary (env-overridable for the stub harness — lead-only law). claude reuses
    the panel resolver when available; git/gh fall back to PATH."""
    if which == "claude":
        env = os.environ.get("COMPANY_CLAUDE_BIN")
        if env:
            return env
        try:
            from runtime import ui_claude_session as _panel
            return _panel._find_claude()
        except Exception:
            return shutil.which("claude") or "claude"
    if which == "git":
        return os.environ.get("COMPANY_GIT_BIN") or shutil.which("git") or "git"
    if which == "gh":
        return os.environ.get("COMPANY_GH_BIN") or shutil.which("gh") or "gh"
    raise WriteRefusal(f"unknown CLI binary {which!r} — only claude/git/gh are allowlisted (fail loud).")


# ─────────────────────────── scope + path safety (multi-root, per config-file root) ───────────────────

def assert_under_root(path: str, root: str, what: str) -> str:
    """The `_safe_mockup_path` realpath+commonpath PATTERN re-derived per config-file root (arch §3.1 /
    Critique C: the single-root bridge fn cannot be reused for multi-root .claude writes — the PATTERN
    is, the function is not). Both sides realpath'd; commonpath must equal the root. Traversal → refused
    LOUD (defence in depth — the registry's scope set is the first wall, this is the second)."""
    p = os.path.realpath(path)
    r = os.path.realpath(root)
    if os.path.commonpath([p, r]) != r:
        raise WriteRefusal(
            f"refused {what}: {path!r} resolves outside its allowed root {root!r} (path traversal) — "
            f"the realpath+commonpath wall, applied per config-file root (fail loud).")
    return p


def _abs_scope_path(canonical: str, scope: str, project_dir: str) -> str:
    """config_targets.scope_path returns a CANONICAL path (~ for HOME user-scope, repo-relative for
    project/local, or a per-resource override like .mcp.json / ~/.claude.json). Resolve it to an
    absolute on-disk path against HOME + the project_dir. NO {name} placeholder may survive (that means
    a name was required and not given — fail loud, never a literal '{name}' file)."""
    if "{name}" in canonical:
        raise WriteRefusal(
            f"this write needs a `name` (the command/skill/style id) — the target resolved to "
            f"{canonical!r} with an unfilled placeholder (fail loud, never a literal '{{name}}' file).")
    expanded = os.path.expanduser(canonical)        # ~/.claude/... → absolute under HOME
    if os.path.isabs(expanded):
        return os.path.realpath(expanded)
    return os.path.realpath(os.path.join(os.path.realpath(project_dir), expanded))


def _root_for_scope(scope: str, project_dir: str) -> str:
    """The containment ROOT the write must stay inside, per scope (the second wall's root)."""
    return os.path.join(HOME, ".claude") if scope == "user" else os.path.join(project_dir, ".claude")


import re as _re
_BARE_NAME = _re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*$")

def _safe_name(name) -> str:
    """A file-authoring `name` (command/skill/style id) MUST be a bare id — the FIRST wall before
    it reaches config_targets.scope_path, which interpolates it raw into the path. `..`, slashes,
    backslashes, a leading dot are refused HERE (the bridge `_safe_mockup_path` first-wall pattern);
    assert_under_root is the second wall. Without this, `name='../escape'` walks out of
    .claude/<subdir>/ up into .claude/ — which the per-root containment check alone would still
    accept (the traversal escaped the subdir, not the root). Fail loud."""
    if not isinstance(name, str) or "/" in name or "\\" in name or ".." in name \
            or not _BARE_NAME.fullmatch(name):
        raise WriteRefusal(
            f"refused name {name!r}: a markdown-file act needs a BARE id (letters/digits then "
            f"[._-], no leading dot, no slashes, no '..'). A path component would let the write "
            f"escape its .claude/<subdir>/ root (traversal). Fail loud.")
    return name


# ─────────────────────────── content validation (the §5.2 dangerous-payload gate) ───────────────────

def _validate_settings_block(pointer: str, block) -> None:
    """A settings write merges a sub-block under `pointer` (hooks/env/…). Must be a JSON object. For
    hooks, surface that the handler `command` strings are shell commands Claude Code EXECUTES on a
    lifecycle event (the consent is over real exec — named, not hidden)."""
    if not isinstance(block, dict):
        raise WriteRefusal(
            f"a settings `{pointer}` write `block` must be a JSON object (it merges into settings.json). "
            f"Got {type(block).__name__}.")
    if pointer == "hooks":
        for ev in block:
            if ev not in CT.HOOK_EVENTS:
                raise WriteRefusal(
                    f"settings hooks: {ev!r} is not a Claude Code hook EVENT — one of {list(CT.HOOK_EVENTS)} "
                    f"(grounded in the Atlas; fail loud, never write an event Claude Code won't fire on). "
                    f"Each handler's `command` is a shell command Claude Code RUNS on that event.")


# keybindings (CC-04, reopened): ground truth = Atlas keybindings.md, verified 2026-06-12.
#   file ~/.claude/keybindings.json; object with a `bindings` ARRAY of {context, bindings:{keystroke:
#   action|null}}; action format namespace:action; null UNBINDS; auto-detected (no restart). These are
#   the CLOSED context names and the shortcuts Claude Code REFUSES to rebind — fail-loud on a bad one
#   (never write a context Claude Code won't honour, never pretend a reserved rebind took).
KB_CONTEXTS = (
    "Global", "Chat", "Autocomplete", "Settings", "Confirmation", "Tabs", "Help", "Transcript",
    "HistorySearch", "Task", "ThemePicker", "Attachments", "Footer", "MessageSelector", "DiffDialog",
    "ModelPicker", "Select", "Plugin", "Scroll", "Doctor",
)
# reserved single keystrokes that CANNOT be rebound (Atlas keybindings.md reserved-shortcuts). Compared
# case-insensitively against the keystroke string; a binding (non-null action) to one is refused loud.
KB_RESERVED = ("ctrl+c", "ctrl+d", "ctrl+m")


def _kb_blocks(block) -> list:
    """Normalize a keybindings `block` to a list of {context, bindings} blocks. Accepts either one block
    dict OR a list of them (the handler may set several contexts at once). Fail-loud on a bad shape."""
    if isinstance(block, dict):
        return [block]
    if isinstance(block, list):
        return block
    raise WriteRefusal(
        "a keybindings write `block` must be a {context, bindings} object (or a list of them) — "
        f"got {type(block).__name__}. See Atlas keybindings.md.")


def _validate_keybindings_block(block) -> None:
    """A keybindings write supplies one-or-more {context, bindings:{keystroke: action|null}} blocks.
    Validate the CLOSED context set + the action shape (namespace:action or null=unbind) + the reserved-
    shortcut refusal — the content gate for CC-04 (non-executable, but still: never write a context
    Claude Code won't honour, never claim a reserved rebind)."""
    blocks = _kb_blocks(block)
    if not blocks:
        raise WriteRefusal("a keybindings write needs at least one {context, bindings} block — empty is "
                           "nothing to write.")
    for blk in blocks:
        if not isinstance(blk, dict):
            raise WriteRefusal(f"each keybindings block must be an object {{context, bindings}}; got "
                               f"{type(blk).__name__}.")
        ctx = blk.get("context")
        if ctx not in KB_CONTEXTS:
            raise WriteRefusal(
                f"keybindings: {ctx!r} is not a Claude Code context — one of {list(KB_CONTEXTS)} "
                f"(grounded in the Atlas; fail loud, never write a context Claude Code ignores).")
        km = blk.get("bindings")
        if not isinstance(km, dict) or not km:
            raise WriteRefusal(
                f"keybindings[{ctx}].bindings must be a non-empty object {{keystroke: action|null}} "
                f"(action='namespace:action', or null to UNBIND a default).")
        for keystroke, action in km.items():
            if not isinstance(keystroke, str) or not keystroke.strip():
                raise WriteRefusal(f"keybindings[{ctx}]: a keystroke key must be a non-empty string.")
            # a non-null action binds the keystroke; refuse a BIND to a reserved single shortcut (an
            # unbind, action=null, is harmless — it just clears a chord prefix).
            if action is not None and keystroke.strip().lower() in KB_RESERVED:
                raise WriteRefusal(
                    f"keybindings: {keystroke!r} is a RESERVED shortcut (one of {list(KB_RESERVED)} — "
                    f"hardcoded interrupt/exit/Enter) and cannot be rebound. Claude Code would ignore "
                    f"it; refusing rather than writing a binding that silently won't take (fail loud).")
            if action is not None and (not isinstance(action, str) or ":" not in action):
                raise WriteRefusal(
                    f"keybindings[{ctx}][{keystroke}] action {action!r} must be 'namespace:action' "
                    f"(e.g. 'chat:externalEditor') or null to unbind. Atlas keybindings.md.")


def _merge_keybindings(path: str, block) -> str:
    """Merge the posted {context, bindings} block(s) into the keybindings.json at `path`, returning the
    JSON text to write. Existing context keymaps are updated key-by-key (override / null-unbind); a new
    context is appended; $schema/$docs are preserved. Idempotent re-merge of the same block is a no-op."""
    data = {"bindings": []}
    if os.path.isfile(path):
        raw = open(path, encoding="utf-8").read()
        data = json.loads(raw) if raw.strip() else {"bindings": []}
        if not isinstance(data, dict):
            raise WriteRefusal(f"{path} is not a JSON object — refusing to merge keybindings (the file "
                               f"must be the {{$schema?, $docs?, bindings:[...]}} shape).")
    arr = data.get("bindings")
    if not isinstance(arr, list):
        arr = []
    idx = {b.get("context"): b for b in arr if isinstance(b, dict)}
    for blk in _kb_blocks(block):
        ctx, km = blk.get("context"), (blk.get("bindings") or {})
        cur = idx.get(ctx)
        if cur is None:
            cur = {"context": ctx, "bindings": {}}
            arr.append(cur)
            idx[ctx] = cur
        if not isinstance(cur.get("bindings"), dict):
            cur["bindings"] = {}
        cur["bindings"].update(km)                         # key-by-key (override / null-unbind)
    data["bindings"] = arr
    return json.dumps(data, indent=2) + "\n"


def _validate_text_body(kind: str, body) -> None:
    if not isinstance(body, str) or not body.strip():
        raise WriteRefusal(
            f"a {kind} write needs a non-empty `body` string — it is the file body (skill→SKILL.md an "
            f"agent loads/follows; command→the slash-command prompt; output-style→style instructions). "
            f"Empty is nothing to write.")


# ─────────────────────────── the service ───────────────────────────

class ConfigWriter:
    """The R3 actor. Holds the store (consent markers + run-records); reads always; writes/CLI/git past
    the consent beat. Stateless across requests — the durable state is the config files + the consent
    refs. Construct with a store; the acceptance test passes an isolated tmp store."""

    def __init__(self, store: FsStore):
        self.store = store

    # ---- run-records (Introspective-Data law, args redacted) ----

    def _record(self, op: str, *, klass: str, consented, exit_code, evidence: str, **meta) -> None:
        try:
            self.store.append_event({
                "kind": "config_writer." + op, "summary": f"{op} [{klass}] exit={exit_code}",
                "klass": klass, "consented": consented, "exit_code": exit_code,
                "evidence": evidence, "ts": _now(), **meta})
        except Exception as e:
            print(f"[config-writer] run-record write failed for {op}: {e}", file=sys.stderr, flush=True)

    # ---- the consent beat (consent-not-lockdown) ----

    def _consent_granted(self, klass: str) -> bool:
        return self.store.head(CONSENT_REF_FMT.format(klass)) == "granted"

    def _consent_beat(self, klass: str, consent: bool, teach: str, **echo) -> dict | None:
        """Returns None to PROCEED (operator consented, or a standing grant), or a PENDING-PROPOSAL
        receipt when a dangerous act lacks consent. NEVER a denial — consent-not-lockdown: the capability
        is ENABLED, this is the signal. A cold agent gets a proposal, not a door slammed shut."""
        if consent or self._consent_granted(klass):
            return None
        return {
            "ok": False, "status": "pending-consent", "consent_class": klass, "teach": teach,
            "note": ("PROPOSAL recorded, not executed — this is consent-not-lockdown (Tim's "
                     "sole-operator model): the capability is ENABLED, this beat is the signal. "
                     "Confirm EITHER way: per-call resend with \"consent\": true, OR a standing grant "
                     f"POST /consent {{\"class\":\"{klass}\",\"grant\":true}} (revocable). git-revert "
                     "is the backstop. Nothing is locked out — the path to yes is one signal away."),
            **echo}

    def set_consent(self, klass: str, grant: bool) -> dict:
        if klass not in CONSENT_CLASSES:
            raise WriteRefusal(
                f"unknown consent class {klass!r}. Classes (each ENABLED, consent-gated, never walled): "
                f"{list(CONSENT_CLASSES)}.")
        self.store.set_ref(CONSENT_REF_FMT.format(klass), "granted" if grant else "revoked")
        self._record("consent", klass=klass, consented=grant, exit_code=0,
                     evidence=f"standing consent {'granted' if grant else 'revoked'}")
        return {"ok": True, "class": klass, "granted": bool(grant),
                "note": ("standing consent set — acts of this class no longer need per-call consent "
                         "until revoked." if grant else
                         "standing consent revoked — acts of this class need per-call consent again.")}

    # ---- READ (always allowed — DECLARATIVE-DIRECT) ----

    def read(self, *, key: str, scope: str = "user", name: str | None = None,
             project_dir: str | None = None) -> dict:
        """Scope-validated config READ (no consent — runs nothing, writes nothing). HONEST absence
        (exists:false) when the file is not there, never a fabricated default."""
        project_dir = project_dir or REPO_ROOT
        row = CT.target_for(key)                          # raises KeyError → 400 on unknown key
        if row.get("kind") is None:                       # the patterns resolver — a pure read, no file
            return {"ok": True, "key": key, "kind": None, "content": None,
                    "note": row.get("teach", "pure resolver — no .claude file backs this.")}
        if name is not None:
            _safe_name(name)                              # first wall: bare id only (anti-traversal)
        try:
            canonical = CT.scope_path(key, scope, name)   # raises ValueError on a bad/managed scope
        except ValueError as e:
            raise WriteRefusal(str(e))                    # → 400 teaching, never a raw 500 (no-silent)
        path = _abs_scope_path(canonical, scope, project_dir)
        assert_under_root(path, _root_for_scope(scope, project_dir) if not path.startswith(HOME + os.sep)
                          or scope == "user" else _root_for_scope(scope, project_dir), "read")
        exists = os.path.isfile(path)
        out = {"ok": True, "key": key, "scope": scope, "name": name, "path": path, "exists": exists}
        if not exists:
            out["content"] = None
            out["note"] = "file does not exist yet — a write creates it (honest absence, not a default)."
            return out
        text = open(path, encoding="utf-8").read()
        if path.endswith(".json"):
            try:
                out["content"] = json.loads(text) if text.strip() else {}
            except ValueError as e:
                raise WriteRefusal(f"{path} is not valid JSON ({e}) — refusing to guess its shape.")
        else:
            out["content"] = text
        return out

    # ---- WRITE (.claude blocks/files — consent-gated, scope + content validated, atomic + backed-up) ----

    def write(self, *, key: str, scope: str = "user", name: str | None = None, block=None,
              body=None, consent: bool = False, project_dir: str | None = None) -> dict:
        """Write a .claude config block/file per the config_targets row for `key`. mcp_servers are NOT
        written by a raw edit here (route via /cli `mcp.add`). Sequence: row lookup → resolve+validate
        target (scope) → validate content (what) → CONSENT beat → atomic write + backup → run-record +
        re-read evidence."""
        project_dir = project_dir or REPO_ROOT
        row = CT.target_for(key)                          # raises KeyError → 400 on unknown key
        kind = row.get("kind")
        if kind is None:
            raise WriteRefusal(f"{key} is a pure resolver (config.patterns) — nothing to write.")
        if kind == "mcp-json":
            raise WriteRefusal(
                "mcp_servers are NOT written by a raw file edit here — register them via /cli "
                "(act='mcp.add' or 'mcp.add-json'). That shells `claude mcp …` (the sanctioned, "
                "tier-gated path); hand-editing ~/.claude.json risks corrupting every project's map.")

        if row.get("subdir") is not None:                 # a file-authoring kind needs a bare name
            _safe_name(name)                              # first wall: bare id only (anti-traversal)
        try:
            canonical = CT.scope_path(key, scope, name)   # raises ValueError on a bad/managed scope (§5.5)
        except ValueError as e:
            raise WriteRefusal(str(e))                    # → 400 teaching, never a raw 500 (no-silent)
        path = _abs_scope_path(canonical, scope, project_dir)
        root = _root_for_scope(scope, project_dir)
        if kind != "settings":
            assert_under_root(path, root, "config write")  # file-authoring kinds live under .claude/<subdir>

        # content validation (WHAT)
        if kind == "settings":
            _validate_settings_block(row.get("pointer"), block)
        elif kind == "keybindings":
            _validate_keybindings_block(block)            # a dedicated-JSON kind (CC-04), not a body
        else:
            _validate_text_body(kind, body)

        # CONSENT beat (consent-not-lockdown) — class = config-write iff the payload is dangerous
        klass = "config-write"
        if CT.is_dangerous(key):
            beat = self._consent_beat(klass, consent, row.get("teach", "a consequential config write"),
                                      key=key, scope=scope, name=name)
            if beat is not None:
                self._record("write.proposed", klass=klass, consented=False, exit_code=None,
                             evidence="pending-consent proposal", key=key, scope=scope)
                return beat

        # ── perform the write ──
        backup = self._atomic_settings_or_file(kind, row, path, scope, project_dir, block, body, name)
        verified = self._reread_ok(kind, row, path, block, body)
        self._record("write", klass=klass, consented=bool(consent or not CT.is_dangerous(key)),
                     exit_code=0 if verified else 1,
                     evidence=("re-read matches" if verified else "RE-READ MISMATCH"),
                     key=key, scope=scope, path=path)
        if not verified:
            raise WriteRefusal(f"config write to {path} did not round-trip on re-read — FAIL LOUD "
                               f"(the backup is at {backup}).")
        return {"ok": True, "key": key, "scope": scope, "name": name, "path": path, "backup": backup,
                "verified": "re-read matches written content",
                "consented": bool(consent), "note": "git-revert (or the .bak) is your undo."}

    def _atomic_settings_or_file(self, kind, row, path, scope, project_dir, block, body, name) -> str | None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        backup = None
        if os.path.isfile(path):
            backup = path + ".bak"
            shutil.copy2(path, backup)
        if kind == "settings":
            pointer = row["pointer"]
            data = {}
            if os.path.isfile(path):
                raw = open(path, encoding="utf-8").read()
                data = json.loads(raw) if raw.strip() else {}
                if not isinstance(data, dict):
                    raise WriteRefusal(f"{path} is not a JSON object — cannot merge a settings block.")
            cur = data.get(pointer)
            if isinstance(cur, dict) and isinstance(block, dict):
                cur.update(block)                          # merge a sub-block (hooks/env)
                data[pointer] = cur
            else:
                data[pointer] = block
            payload = json.dumps(data, indent=2) + "\n"
        elif kind == "keybindings":
            # the dedicated keybindings.json (CC-04): an object with a `bindings` ARRAY of
            # {context, bindings:{keystroke: action|null}} blocks. `block` carries one (or more) such
            # blocks; we MERGE by context — the matching context's keymap is updated key-by-key (a
            # later set of ctrl+e overrides an earlier; an action set to null UNBINDS, the native
            # semantics), a new context is appended. $schema/$docs at top level are preserved. This is
            # NOT settings.json's pointer-merge — keybindings has its own array-by-context shape.
            payload = _merge_keybindings(path, block)
        else:
            payload = body if body.endswith("\n") else body + "\n"
        self._atomic_write(path, payload)
        return backup

    @staticmethod
    def _atomic_write(path: str, text: str) -> None:
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".cw-", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(text)
                f.flush()
                os.fsync(f.fileno())                       # crash-durable (the set_ref fsync precedent)
            os.replace(tmp, path)                          # atomic on same filesystem
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    @staticmethod
    def _reread_ok(kind, row, path, block, body) -> bool:
        text = open(path, encoding="utf-8").read()
        if kind == "settings":
            data = json.loads(text)
            cur = data.get(row["pointer"])
            if isinstance(block, dict):
                return all(cur.get(k) == v for k, v in block.items())
            return cur == block
        if kind == "keybindings":
            data = json.loads(text)
            by_ctx = {b.get("context"): (b.get("bindings") or {})
                      for b in (data.get("bindings") or []) if isinstance(b, dict)}
            for blk in _kb_blocks(block):                  # every posted (context, keymap) must have landed
                ctx, km = blk.get("context"), (blk.get("bindings") or {})
                got = by_ctx.get(ctx)
                if got is None or not all(got.get(k) == v for k, v in km.items()):
                    return False
            return True
        return text == (body if body.endswith("\n") else body + "\n")

    # ---- native CLI (claude mcp / plugin) + structured git/gh — both via the cli_allowlist registry ----

    def cli(self, *, act: str, consent: bool = False, run: bool = True, **slots) -> dict:
        """Build (and optionally run) a native config CLI / git / gh from the cli_allowlist row. `run=
        False` = the unit-test path (argv without executing). The TIER drives the consent class:
        read→ungated, write→<tool>-write, exec→cli-exec. Fails loud on nonzero exit."""
        return self._cli_or_git(act, consent=consent, run=run, cwd=None, **slots)

    def git(self, *, act: str, cwd: str, consent: bool = False, run: bool = True, **slots) -> dict:
        """Structured git/gh in `cwd` (the repo). For commit, returns the resulting HEAD sha (the
        structured-sha path — NOT R1-prime prose). `run=False` returns argv (unit-test path)."""
        if not isinstance(cwd, str) or not os.path.isdir(cwd):
            raise WriteRefusal(f"git/gh `cwd` {cwd!r} is not a directory — they run inside a repo.")
        return self._cli_or_git(act, consent=consent, run=run, cwd=cwd, **slots)

    def _cli_or_git(self, act: str, *, consent: bool, run: bool, cwd: str | None, **slots) -> dict:
        try:
            tier = CL.tier_of(act)                          # raises KeyError → 400 on unknown act
        except KeyError as e:
            raise WriteRefusal(str(e))
        try:
            argv = CL.render_argv(act, **slots)             # raises ValueError → 400 on a bad/missing slot
        except ValueError as e:
            raise WriteRefusal(str(e))
        tool = argv[0]                                      # 'claude' | 'git' | 'gh' (registry-provided)
        # consent beat for write/exec tiers (read is ungated). Class names the tier + tool family.
        if tier in ("write", "exec"):
            if tool in ("git", "gh"):
                klass = "git-write"
            else:
                klass = "cli-exec" if tier == "exec" else "cli-write"
            teach = (f"`{' '.join(argv[:3])}…` is a {tier}-tier act — "
                     + ("it registers/fetches+runs code (an exec target)." if tier == "exec"
                        else "it mutates config or the repo."))
            beat = self._consent_beat(klass, consent, teach, act=act, tier=tier)
            if beat is not None:
                self._record("cli.proposed", klass=klass, consented=False, exit_code=None,
                             evidence="pending-consent proposal", act=act, tier=tier)
                return beat
        else:
            klass = "read"
        # render the leading binary (env-overridable for the stub harness; registry gave the bare tool)
        argv = [_find_bin(tool)] + argv[1:]
        if not run:
            return {"ok": True, "act": act, "tier": tier, "argv": argv, "would_run": True}
        res = self._run(argv, cwd)
        is_write = tier in ("write", "exec")
        self._record("cli" if tool == "claude" else "git", klass=klass,
                     consented=(bool(consent) if is_write else "n/a (read)"),
                     exit_code=res["exit"], evidence=("exit 0" if res["exit"] == 0 else "NONZERO"),
                     act=act, tier=tier)
        if res["exit"] != 0:
            raise WriteRefusal(
                f"`{' '.join(argv[1:3])}…` exited {res['exit']} — {res.get('stderr', '')[:400]} "
                f"(fail loud; the CLI refused, never a pretended success).")
        out = {"ok": True, "act": act, "tier": tier, "argv": argv, "exit": res["exit"],
               "stdout": (res.get("stdout") or "")[:8000], "stderr": (res.get("stderr") or "")[:2000],
               "consented": bool(consent) if is_write else "n/a (read)"}
        if act == "dev.git:commit":                             # the structured-sha path
            sha = self._run([_find_bin("git"), "rev-parse", "HEAD"], cwd)
            out["sha"] = (sha.get("stdout") or "").strip() or None
        return out

    @staticmethod
    def _run(argv, cwd) -> dict:
        """Run an argv ARRAY — NEVER shell=True (the injection floor: a value with shell metachars is one
        argv element, never re-parsed). Captures stdout/stderr/exit; fail-loud is the caller's job."""
        try:
            p = subprocess.run(argv, cwd=cwd or REPO_ROOT, capture_output=True, text=True, timeout=300)
            return {"exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
        except FileNotFoundError as e:
            raise WriteRefusal(f"binary not found: {argv[0]!r} ({e}) — install it or set the COMPANY_*_BIN "
                               f"override (fail loud; never a silent skip).")
        except subprocess.TimeoutExpired:
            raise WriteRefusal(f"`{' '.join(argv[:3])}…` timed out after 300s (fail loud).")


# ───────────────────────────── HTTP face ─────────────────────────────

CW: ConfigWriter | None = None


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _send(self, code: int, obj: dict) -> None:
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/health":
            self._send(200, {"ok": True, "service": "config-writer", "bind": "127.0.0.1",
                             "consent_classes": list(CONSENT_CLASSES),
                             "model": "consent-not-lockdown (sole-operator): dangerous config/CLI/VCS "
                                      "ops ENABLED, gated by a consent signal (per-call or standing "
                                      "marker), NEVER walled off; git-revert is the backstop"})
            return
        self._send(404, {"error": f"unknown path {u.path} — GET /health; POST /read · /write · /cli · "
                                  f"/git · /consent"})

    def do_POST(self):
        self.close_connection = True
        u = urlparse(self.path)
        try:
            length = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(length) or b"{}") if length else {}
        except ValueError:
            self._send(400, {"error": "body must be JSON"})
            return
        try:
            if u.path == "/read":
                self._send(200, CW.read(**body)); return
            if u.path == "/write":
                r = CW.write(**body)
                # a pending-consent proposal is a 200 receipt (not an error — consent-not-lockdown);
                # a real success is 200 too. Both carry ok-or-status.
                self._send(200, r); return
            if u.path == "/cli":
                self._send(200, CW.cli(**body)); return
            if u.path == "/git":
                self._send(200, CW.git(**body)); return
            if u.path == "/consent":
                self._send(200, CW.set_consent(body.get("class") or "", bool(body.get("grant")))); return
        except KeyError as e:
            self._send(400, {"error": str(e)}); return
        except WriteRefusal as e:
            # 409 = a CLI/exit refusal; 400 = bad scope/key/content/path. Both carry teach-text.
            msg = str(e)
            code = 409 if "exited" in msg else 400
            self._send(code, {"error": msg}); return
        except TypeError as e:
            self._send(400, {"error": f"bad params: {e}"}); return
        except Exception as e:
            self._send(500, {"error": f"INTERNAL: {e}"}); return
        self._send(404, {"error": f"unknown path {u.path}"})


def main() -> None:
    global CW
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(
        os.environ.get("COMPANY_CONFIG_WRITER_PORT", DEFAULT_PORT))
    CW = ConfigWriter(FsStore(fcfg.STORE_DIR))
    print(f"[config-writer] R3 config/VCS writer at http://127.0.0.1:{port} "
          f"(consent-not-lockdown · classes={list(CONSENT_CLASSES)} · store={fcfg.STORE_DIR})",
          flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()


if __name__ == "__main__":
    main()
