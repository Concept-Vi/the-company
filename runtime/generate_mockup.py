"""runtime/generate_mockup.py — the generate-for-mockups ENGINE CORE.

The configurable, autonomous "generate" step behind the guided design-review surface: take ONE
reviewed mockup + its captured reviewer feedback → render an instruction from declared config →
run a (plan-by-default, SAFE) `claude -p` dispatch SCOPED to that one mockup file → return the
PROPOSED edit/diff (plan) or apply+commit it (apply, git-revertible).

DESIGN (Tim's two binding directives):
  1. AUTONOMOUS — this runs without Tim in the loop; safety is git-revert + plan-by-default
     (a plan-mode run changes NOTHING, commits NOTHING).
  2. REGISTRY-DRIVEN — the generate BEHAVIOUR is DECLARED DATA in design/_system/generate-config.json
     (the instruction template, model, default mode, routing, scope rule). NO prompt/model/mode literal
     is baked into this code; changing generate behaviour = editing that JSON, no code change. The config
     is read FRESH each call (mirrors implement.permission_mode()'s call-time read) so an edit takes
     effect with no restart, and `config_path` is injectable so a test can prove reconfigurability.

REUSE (no parallel claude -p spawning):
  - implement.launch() is the wire. It builds the instruction (wrapping our CORE template with the
    repo's universal STANDARDS_BLOCK + the authorized-scope line derived from the scope[] we pass),
    spawns `claude -p ... --output-format json --permission-mode <mode>`, and captures a STRUCTURED
    result + GIT-ground-truth changed_files. We pass a synthetic `decision` carrying our rendered spec
    + the scoped path; we do NOT touch suite.py's dispatch_decision (held by cognition) — launch() is
    the thin, testable unit the task points at (its plan default, its injectable runner, its git diff).

  - The feedback CAPTURE lives in bridge.py (held by B1). We do NOT import bridge.py — it instantiates
    a Suite at module import (bridge.py:362 `SUITE = Suite(...)`), which would couple us to the held
    suite.py. Instead we REPLICATE the tiny JSONL read (the format is the contract: one JSON entry per
    line at design/mockups/.feedback/<file>.html.jsonl) so we read a mockup's feedback thread WITHOUT
    touching bridge.py. (write/capture stays bridge.py's; we only READ.)

FAIL LOUD (Tim's no-silent law): an unknown mockup raises; a mockup with no actionable feedback raises;
a malformed config raises. No silent no-op, no fabricated success.
"""
from __future__ import annotations

import json
import os
import re

from runtime import implement


# --- paths (mirrors bridge.py's layout — the same dirs, derived independently so we never import it) ---
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOCKUPS_DIR = os.path.join(ROOT, "design", "mockups")
FEEDBACK_DIR = os.path.join(MOCKUPS_DIR, ".feedback")
DEFAULT_CONFIG_PATH = os.path.join(ROOT, "design", "_system", "generate-config.json")

# the same bare-basename gate bridge.py uses (one rule, replicated) so a junk name can never traverse.
_NAME_RE = re.compile(r"[A-Za-z0-9._-]+\.html")


class GenerateError(RuntimeError):
    """A generate request failed LOUD: unknown mockup, no actionable feedback, malformed/missing
    config, or an unimplemented route. NEVER swallowed — no silent no-op, no fabricated success."""


def load_config(config_path: str | None = None) -> dict:
    """Read the DECLARED generate-config FRESH (call-time, not import-time — so an edit takes effect
    with no restart; mirrors implement.permission_mode()'s call-time env read). `config_path` is
    injectable so a test can point at a modified copy and PROVE reconfigurability. Fail loud on a
    missing or malformed config (a generate behaviour that can't be read is a hard stop, not a default)."""
    path = config_path or DEFAULT_CONFIG_PATH
    if not os.path.isfile(path):
        raise GenerateError(f"generate-config not found at {path!r} — the engine's behaviour is "
                            f"DECLARED DATA; with no config there is nothing to run (fail loud)")
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except json.JSONDecodeError as e:
        raise GenerateError(f"generate-config at {path!r} is not valid JSON: {e} (fail loud)") from e
    if not isinstance(cfg, dict):
        raise GenerateError(f"generate-config at {path!r} must be a JSON object, got "
                            f"{type(cfg).__name__} (fail loud)")
    return cfg


def _feedback_path(mockup_file: str) -> str:
    """The JSONL path for a mockup's feedback thread (replicates bridge.py's _feedback_path contract:
    design/mockups/.feedback/<file>.html.jsonl). Validates the bare-basename name (no traversal) and a
    realpath-contains second wall — defence in depth, the same two gates bridge.py uses. Raises on junk."""
    if not isinstance(mockup_file, str) or not _NAME_RE.fullmatch(mockup_file):
        raise GenerateError(f"refused mockup name {mockup_file!r}: must be a bare <file>.html basename "
                            f"(no path, no traversal) — fail loud")
    p = os.path.realpath(os.path.join(FEEDBACK_DIR, mockup_file + ".jsonl"))
    if os.path.commonpath([p, os.path.realpath(FEEDBACK_DIR)]) != os.path.realpath(FEEDBACK_DIR):
        raise GenerateError(f"refused mockup name {mockup_file!r}: resolves outside the feedback dir")
    return p


def read_feedback(mockup_file: str) -> list[dict]:
    """Read a mockup's captured feedback thread → list of entries (oldest-first), [] if no file.
    Replicates bridge.py's _read_feedback (the JSONL format is the contract). A malformed line is
    skipped (one bad line must not blank the thread) — but a TOTALLY empty/absent thread is a real
    state the caller turns into a fail-loud no-feedback error, not a silent default."""
    path = _feedback_path(mockup_file)
    if not os.path.isfile(path):
        return []
    out: list[dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                entry = json.loads(ln)
                if isinstance(entry, dict):
                    out.append(entry)
            except json.JSONDecodeError:
                continue  # skip one bad line (do not blank the whole thread) — mirrors bridge.py
    return out


def _actionable(entries: list[dict], feedback_filter: str) -> list[dict]:
    """Select the feedback entries that DRIVE the edit, per the config's feedback_filter:
    'pending' → only status=='pending' notes; 'all' → every note. Unknown filter → fail loud."""
    if feedback_filter == "all":
        return list(entries)
    if feedback_filter == "pending":
        return [e for e in entries if e.get("status", "pending") == "pending"]
    raise GenerateError(f"generate-config feedback_filter {feedback_filter!r} unknown — "
                        f"expected 'pending' or 'all' (fail loud)")


def _render_feedback_block(actionable: list[dict], all_entries: list[dict]) -> str:
    """Render the feedback thread for the instruction. The ACTIONABLE notes are listed first as the
    notes to apply; any non-actionable notes (applied/dismissed under the 'pending' filter) follow as
    read-only context. Each line: status + optional element locus + text. Concrete, legible, ordered."""
    lines: list[str] = []
    for e in actionable:
        loc = f" @ {e['element']}" if e.get("element") else ""
        lines.append(f"- [APPLY · {e.get('status', 'pending')}{loc}] {str(e.get('text', '')).strip()}")
    context_only = [e for e in all_entries if e not in actionable]
    for e in context_only:
        loc = f" @ {e['element']}" if e.get("element") else ""
        lines.append(f"- [context · {e.get('status', '')}{loc}] {str(e.get('text', '')).strip()}")
    return "\n".join(lines)


def render_instruction(mockup_file: str, config: dict, *, feedback: list[dict] | None = None) -> tuple[str, list[str]]:
    """Render the CORE generate instruction from the declared template + the mockup's captured
    feedback, and resolve the authorized scope. Returns (instruction_core, scope_paths).

    The template (config['instruction_template']) is the SINGLE source of the prompt wording — no
    literal prompt text in this code. Placeholders {mockup_file} {mockup_path} {feedback_block} are
    substituted. The scope comes from config['routing'][route]['scope'] with {mockup_file} substituted
    (the scope_rule — the dispatch may change ONLY this one mockup file).

    NOTE: this returns the CORE; implement.build_instruction wraps it with the repo's universal
    STANDARDS_BLOCK + the 'authorized to change ONLY these paths' line (from the scope we pass through
    the decision payload). So the final prompt = wrapper(core). Fail loud on a missing template/route."""
    template = config.get("instruction_template")
    if not isinstance(template, str) or not template.strip():
        raise GenerateError("generate-config has no usable 'instruction_template' string (fail loud)")

    route_name = config.get("default_route", "mockup_edit")
    routing = config.get("routing") or {}
    route = routing.get(route_name)
    if not isinstance(route, dict):
        raise GenerateError(f"generate-config routing has no entry {route_name!r} (fail loud)")
    if not route.get("enabled", False):
        raise GenerateError(f"generate-config route {route_name!r} is declared but not enabled "
                            f"(it is config-declared for the future; not runnable yet) — fail loud")

    mockup_path = os.path.join("design", "mockups", mockup_file)
    entries = feedback if feedback is not None else read_feedback(mockup_file)
    actionable = _actionable(entries, config.get("feedback_filter", "pending"))
    feedback_block = _render_feedback_block(actionable, entries)

    # render — only the declared placeholders; an unknown placeholder in the template would KeyError,
    # which we surface as a loud config error rather than a cryptic traceback.
    try:
        instruction_core = template.format(
            mockup_file=mockup_file, mockup_path=mockup_path, feedback_block=feedback_block)
    except (KeyError, IndexError) as e:
        raise GenerateError(f"generate-config instruction_template references an unknown placeholder "
                            f"{e} — allowed: {{mockup_file}} {{mockup_path}} {{feedback_block}} (fail loud)") from e

    scope_tmpl = route.get("scope") or []
    scope_paths = [s.format(mockup_file=mockup_file) for s in scope_tmpl if isinstance(s, str)]
    if not scope_paths:
        raise GenerateError(f"generate-config route {route_name!r} declares no scope — the dispatch "
                            f"must be scoped to the one mockup file (fail loud)")
    return instruction_core, scope_paths


def generate_for_mockup(mockup_file: str, *, mode: str | None = None,
                        config_path: str | None = None, launcher=None,
                        repo: str | None = None) -> dict:
    """THE engine entry point. Refine ONE mockup from its captured reviewer feedback, autonomously.

    Sequence:
      1. load the DECLARED generate-config FRESH (reconfigurable; fail loud if missing/malformed).
      2. read the mockup's captured feedback (replicated JSONL read — no bridge.py import).
         FAIL LOUD if there is no actionable feedback (no silent no-op) or the mockup is unknown.
      3. render the instruction CORE from the template + feedback, resolve the scoped path.
      4. REUSE implement.launch() — spawn `claude -p` under the config's mode (default plan = SAFE),
         scoped to design/mockups/<file>. launch() wraps our core with the repo's standards + scope
         line and captures a STRUCTURED result + GIT-ground-truth changed_files.
      5. return the result + the engine's own metadata.

    mode: overrides the config's default ('plan' | 'apply'); None → config's mode (default 'plan').
    PLAN mode is read-only/safe: changes NOTHING, commits NOTHING (changed_files == []). APPLY is the
    live, git-revertible change-making run. `launcher`/`config_path`/`repo` are injectable for tests
    (a deterministic launcher proves the dispatch path without burning a real session)."""
    config = load_config(config_path)

    # validate the mockup exists (unknown mockup → fail loud, never a silent skip). The name gate in
    # _feedback_path also refuses traversal; here we additionally require the actual mockup file.
    if not _NAME_RE.fullmatch(mockup_file or ""):
        raise GenerateError(f"refused mockup name {mockup_file!r}: must be a bare <file>.html basename")
    mockup_abs = os.path.join(MOCKUPS_DIR, mockup_file)
    if not os.path.isfile(mockup_abs):
        raise GenerateError(f"unknown mockup {mockup_file!r}: no file at {mockup_abs} (fail loud)")

    entries = read_feedback(mockup_file)
    actionable = _actionable(entries, config.get("feedback_filter", "pending"))
    if not actionable:
        raise GenerateError(
            f"mockup {mockup_file!r} has no actionable feedback "
            f"(filter={config.get('feedback_filter', 'pending')!r}, {len(entries)} total note(s)) — "
            f"nothing to generate from (fail loud, no silent no-op)")

    instruction_core, scope_paths = render_instruction(mockup_file, config, feedback=entries)

    resolved_mode = mode if mode is not None else config.get("mode", "plan")
    if resolved_mode not in ("plan", "apply"):
        raise GenerateError(f"mode {resolved_mode!r} unknown — expected 'plan' or 'apply' (fail loud)")
    # the engine speaks plan|apply; implement.launch speaks the claude posture plan|acceptEdits.
    permission_mode = "plan" if resolved_mode == "plan" else "acceptEdits"

    # the synthetic decision carries our rendered spec + the scoped path. implement.build_instruction
    # turns scope[] into the 'authorized to change ONLY these paths' line — so the scope_rule is
    # enforced through the SAME wire, not a parallel one. (We do not mint a substrate decision/seq;
    # this is a standalone generate, not a governed self-build of the system's own code.)
    decision = {"payload": {"spec": instruction_core, "scope": scope_paths,
                            "why": f"generate-for-mockups: refine {mockup_file} from reviewer feedback"}}

    launch_kwargs = {"permission_mode": permission_mode}
    if launcher is not None:
        launch_kwargs["runner"] = launcher
    if repo is not None:
        launch_kwargs["repo"] = repo
    result = implement.launch(decision, **launch_kwargs)

    return {
        "mockup_file": mockup_file,
        "mode": resolved_mode,
        "permission_mode": result.get("permission_mode", permission_mode),
        "model": config.get("model", "default"),
        "route": config.get("default_route", "mockup_edit"),
        "scope": scope_paths,
        "actionable_feedback_count": len(actionable),
        "instruction_core": instruction_core,
        "result": result,                              # the full launch result (summary/proposed diff)
        "proposed_summary": result.get("summary", ""),  # the proposed edit (plan) / applied summary
        "changed_files": result.get("changed_files", []),  # [] in plan (proof: mutated nothing)
        "success": result.get("success"),
    }
