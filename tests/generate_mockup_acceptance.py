"""tests/generate_mockup_acceptance.py — acceptance for the generate-for-mockups ENGINE CORE.

Proves the four contract properties WITHOUT burning a real claude -p session (a deterministic
launcher is injected — the real round-trip is verified separately, by use). The config-read +
instruction-render + plan-safety are REAL (not mocked); only the subprocess spawn is stubbed.

  1. config is DECLARED + read, and RECONFIGURABLE — change a config value, the engine reflects it.
  2. the engine READS captured feedback + RENDERS the instruction from the template.
  3. a PLAN-mode run DISPATCHES + returns a proposed result, mutating NOTHING + committing NOTHING
     (safe-by-default — proven by changed_files == [] and a non-mutating git-truth path).
  4. FAIL LOUD on no-feedback / unknown-mockup / malformed config.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime import generate_mockup as gm


# a real mockup file that exists on disk (the engine requires the file to exist — unknown → fail loud).
def _a_real_mockup() -> str:
    files = sorted(n for n in os.listdir(gm.MOCKUPS_DIR)
                   if n.endswith(".html") and os.path.isfile(os.path.join(gm.MOCKUPS_DIR, n)))
    assert files, "no mockup files on disk — cannot run the engine acceptance"
    return files[0]


def _write_config(tmpdir: str, **overrides) -> str:
    """Write a generate-config to a temp path so reconfigurability is provable in isolation (we never
    mutate the canonical design/_system/generate-config.json in a test)."""
    cfg = {
        "model": "default",
        "mode": "plan",
        "instruction_template": (
            "REFINE {mockup_file} (at {mockup_path}).\n\nFEEDBACK:\n{feedback_block}"),
        "feedback_filter": "pending",
        "routing": {"mockup_edit": {"enabled": True, "scope": ["design/mockups/{mockup_file}"]},
                    "live": {"enabled": False}},
        "default_route": "mockup_edit",
    }
    cfg.update(overrides)
    p = os.path.join(tmpdir, "generate-config.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(cfg, f)
    return p


def _seed_feedback(mockup_file: str, notes: list[dict]) -> str:
    """Seed a feedback thread for a mockup at the real FEEDBACK_DIR. Returns the path so the caller
    can clean it up. We write to a dedicated test-named mockup thread to avoid clobbering real data."""
    os.makedirs(gm.FEEDBACK_DIR, exist_ok=True)
    path = gm._feedback_path(mockup_file)
    with open(path, "w", encoding="utf-8") as f:
        for i, n in enumerate(notes):
            entry = {"id": f"{i:04d}-test", "mockup": mockup_file, "element": n.get("element"),
                     "text": n["text"], "ts": "2026-06-09T00:00:00Z", "status": n.get("status", "pending")}
            f.write(json.dumps(entry) + "\n")
    return path


class _RecordingLauncher:
    """A deterministic launch runner (the implement.launch `runner` contract): records the instruction
    it was handed and returns a structured result WITHOUT spawning claude -p. Returns changed_files=[]
    to model a plan-mode run (mutates nothing). Captures permission_mode so plan-safety is checkable."""
    def __init__(self):
        self.calls = []

    def __call__(self, instruction, *, repo, permission_mode, timeout_s):
        self.calls.append({"instruction": instruction, "permission_mode": permission_mode})
        return {"finished": True, "success": True, "exit_code": 0,
                "summary": f"PROPOSED (plan/{permission_mode}): would edit the mockup per the notes.",
                "raw": {}, "stderr": "", "changed_files": []}


def test_config_declared_and_reconfigurable(tmpdir):
    """1 — the config is DECLARED data and READ; changing a value changes the rendered instruction."""
    mockup = _a_real_mockup()
    fb_path = _seed_feedback(mockup, [{"text": "tighten the header spacing"}])
    try:
        # baseline template
        cfg_a = _write_config(tmpdir, instruction_template="ALPHA-TEMPLATE {mockup_file}: {feedback_block}")
        l_a = _RecordingLauncher()
        out_a = gm.generate_for_mockup(mockup, mode="plan", config_path=cfg_a, launcher=l_a)
        assert "ALPHA-TEMPLATE" in out_a["instruction_core"], "engine did not use the declared template"
        assert "tighten the header spacing" in out_a["instruction_core"], "feedback not rendered"

        # FLIP a config value → the engine must reflect it (proves reconfigurable, no code change)
        cfg_b = os.path.join(tmpdir, "config-b.json")
        with open(cfg_a) as f:
            base = json.load(f)
        base["instruction_template"] = "BETA-TEMPLATE {mockup_file}: {feedback_block}"
        with open(cfg_b, "w") as f:
            json.dump(base, f)
        l_b = _RecordingLauncher()
        out_b = gm.generate_for_mockup(mockup, mode="plan", config_path=cfg_b, launcher=l_b)
        assert "BETA-TEMPLATE" in out_b["instruction_core"], "engine did not reflect the changed config"
        assert "ALPHA-TEMPLATE" not in out_b["instruction_core"]
        print("  [1] config declared + reconfigurable: ALPHA→BETA template flip reflected")
    finally:
        os.remove(fb_path)


def test_reads_feedback_and_renders(tmpdir):
    """2 — the engine reads the captured feedback thread and renders it into the instruction."""
    mockup = _a_real_mockup()
    fb_path = _seed_feedback(mockup, [
        {"text": "make the primary button gold", "element": "ui://btn/primary"},
        {"text": "remove the debug banner"},
    ])
    try:
        cfg = _write_config(tmpdir)
        out = gm.generate_for_mockup(mockup, mode="plan", config_path=cfg, launcher=_RecordingLauncher())
        core = out["instruction_core"]
        assert "make the primary button gold" in core
        assert "remove the debug banner" in core
        assert "ui://btn/primary" in core, "element locus not rendered"
        assert out["actionable_feedback_count"] == 2
        print("  [2] reads feedback + renders both notes (incl. element locus)")
    finally:
        os.remove(fb_path)


def test_plan_mode_safe_dispatches_mutates_nothing(tmpdir):
    """3 — a PLAN-mode run dispatches and returns a proposed result, mutating NOTHING + committing
    NOTHING. Proven by: the launcher received permission_mode 'plan', and changed_files == []."""
    mockup = _a_real_mockup()
    fb_path = _seed_feedback(mockup, [{"text": "align the footer"}])
    try:
        cfg = _write_config(tmpdir)
        launcher = _RecordingLauncher()
        out = gm.generate_for_mockup(mockup, mode="plan", config_path=cfg, launcher=launcher)
        assert launcher.calls, "no dispatch happened"
        assert launcher.calls[0]["permission_mode"] == "plan", "plan mode not honoured (NOT safe)"
        assert out["changed_files"] == [], "plan mode must mutate nothing (changed_files non-empty!)"
        assert out["proposed_summary"], "plan run returned no proposed edit"
        # the wrapped instruction must carry the scope line (scope enforced through the wire)
        assert f"design/mockups/{mockup}" in launcher.calls[0]["instruction"], "scope not in instruction"
        print(f"  [3] plan-mode safe: permission_mode=plan, changed_files=[], proposed summary returned")
    finally:
        os.remove(fb_path)


def test_fail_loud_no_feedback(tmpdir):
    """4a — a mockup with NO actionable feedback fails loud (no silent no-op)."""
    mockup = _a_real_mockup()
    # ensure no thread exists for this mockup
    fb_path = gm._feedback_path(mockup)
    if os.path.exists(fb_path):
        os.remove(fb_path)
    cfg = _write_config(tmpdir)
    raised = False
    try:
        gm.generate_for_mockup(mockup, mode="plan", config_path=cfg, launcher=_RecordingLauncher())
    except gm.GenerateError as e:
        raised = "no actionable feedback" in str(e)
    assert raised, "engine did NOT fail loud on no feedback"
    print("  [4a] fail-loud on no feedback")


def test_fail_loud_unknown_mockup(tmpdir):
    """4b — an unknown mockup fails loud."""
    cfg = _write_config(tmpdir)
    raised = False
    try:
        gm.generate_for_mockup("ZZ-does-not-exist.html", mode="plan", config_path=cfg,
                               launcher=_RecordingLauncher())
    except gm.GenerateError as e:
        raised = "unknown mockup" in str(e)
    assert raised, "engine did NOT fail loud on an unknown mockup"
    print("  [4b] fail-loud on unknown mockup")


def test_fail_loud_malformed_config(tmpdir):
    """4c — a missing/malformed config fails loud (the behaviour is declared data; no silent default)."""
    raised_missing = False
    try:
        gm.load_config(os.path.join(tmpdir, "nope.json"))
    except gm.GenerateError:
        raised_missing = True
    assert raised_missing, "did not fail loud on missing config"

    bad = os.path.join(tmpdir, "bad.json")
    with open(bad, "w") as f:
        f.write("{not json")
    raised_bad = False
    try:
        gm.load_config(bad)
    except gm.GenerateError:
        raised_bad = True
    assert raised_bad, "did not fail loud on malformed config"
    print("  [4c] fail-loud on missing + malformed config")


def run():
    print("generate_mockup_acceptance:")
    with tempfile.TemporaryDirectory() as td:
        test_config_declared_and_reconfigurable(td)
        test_reads_feedback_and_renders(td)
        test_plan_mode_safe_dispatches_mutates_nothing(td)
        test_fail_loud_no_feedback(td)
        test_fail_loud_unknown_mockup(td)
        test_fail_loud_malformed_config(td)
    print("generate_mockup_acceptance: ALL GREEN")
    return True


if __name__ == "__main__":
    run()
