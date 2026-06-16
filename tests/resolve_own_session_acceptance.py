"""tests/resolve_own_session_acceptance.py — the self-serve-memory SAFETY keystone: resolve_own_session
must NOT silently mis-identify self. FALSIFY-FIRST: on UNMODIFIED code an ambiguous dir (2 .jsonl, no
COMPANY_SESSION_ID) returned a newest-mtime GUESS (ambiguous=True) — the self-misidentification hazard;
the fix makes it FAIL LOUD (AmbiguousSelfError) unless allow_ambiguous. Verifies: env/explicit = unambiguous;
single-jsonl = unambiguous; multi-no-id = raise; allow_ambiguous = best-guess. Run: python3 tests/resolve_own_session_acceptance.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import runtime.session_scan as ss

PASS, FAIL = [], []


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'ok ' if cond else 'FAIL'} {name}" + (f"  — {detail}" if detail and not cond else ""))


# build a fake project dir + point PROJECTS_DIR at it; cwd encodes to a known subdir
tmp = tempfile.mkdtemp(prefix="resolve_self_")
ss.PROJECTS_DIR = tmp
CWD = "/home/tim/zzz-test-cwd"
proj = os.path.join(tmp, ss._encode_cwd(CWD))
os.makedirs(proj)
os.environ.pop("COMPANY_SESSION_ID", None)

# one transcript → unambiguous (sole transcript)
open(os.path.join(proj, "aaaa1111.jsonl"), "w").write("{}\n")
r = ss.resolve_own_session(cwd=CWD)
ok("single transcript → unambiguous (newest-mtime sole)", r["session_id"] == "aaaa1111" and not r["ambiguous"])

# add a SECOND transcript → AMBIGUOUS + no id → must FAIL LOUD (the keystone)
import time as _t
_t.sleep(0.01)
open(os.path.join(proj, "bbbb2222.jsonl"), "w").write("{}\n")
try:
    ss.resolve_own_session(cwd=CWD)
    ok("FALSIFY-FIRST: ambiguous + no COMPANY_SESSION_ID → FAILS LOUD (no silent mis-identify)", False)
except ss.AmbiguousSelfError as e:
    ok("FALSIFY-FIRST: ambiguous + no COMPANY_SESSION_ID → FAILS LOUD (no silent mis-identify)",
       "COMPANY_SESSION_ID" in str(e) and "WRONG self" in str(e))

# COMPANY_SESSION_ID env → unambiguous, picks THAT session even amid ambiguity
os.environ["COMPANY_SESSION_ID"] = "bbbb2222"
try:
    r = ss.resolve_own_session(cwd=CWD)
    ok("COMPANY_SESSION_ID env → unambiguous self-id (the injection consumer)",
       r["session_id"] == "bbbb2222" and not r["ambiguous"] and r["how"] == "env COMPANY_SESSION_ID")
finally:
    os.environ.pop("COMPANY_SESSION_ID", None)

# explicit session_id beats everything
r = ss.resolve_own_session(cwd=CWD, session_id="aaaa1111")
ok("explicit session_id → unambiguous", r["session_id"] == "aaaa1111" and r["how"] == "explicit")

# allow_ambiguous=True → opt back into the best-guess (newest-mtime), flagged ambiguous
r = ss.resolve_own_session(cwd=CWD, allow_ambiguous=True)
ok("allow_ambiguous=True → best-guess returned, flagged ambiguous (opt-in to the risk)",
   r["ambiguous"] is True and "AMBIGUOUS guess" in r["how"])

# env pointing at a NON-existent transcript → fail loud (wrong cwd/sid)
os.environ["COMPANY_SESSION_ID"] = "ccccdoesnotexist"
try:
    ss.resolve_own_session(cwd=CWD)
    ok("env sid with no transcript → fails loud", False)
except FileNotFoundError:
    ok("env sid with no transcript → fails loud", True)
finally:
    os.environ.pop("COMPANY_SESSION_ID", None)

import shutil
shutil.rmtree(tmp, ignore_errors=True)

print(f"\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", ", ".join(FAIL))
    sys.exit(1)
print("ALL GREEN — resolve_own_session is the SAFE self-id consumer: env/explicit = unambiguous, "
      "single-transcript = unambiguous, ambiguous+no-id = FAIL LOUD (no silent self-misidentification), "
      "allow_ambiguous = opt-in best-guess. The injection (COMPANY_SESSION_ID at launch) is the lead's seam.")
