"""tests/cc_clone_reflection_persist_acceptance.py — the reflection-PERSISTENCE bug + clone:// addressing.

FALSIFY-FIRST (run against UNMODIFIED code first — the persistence assertions MUST fail, proving the bug:
onboard_clone returns the reflection but never writes it to the durable clone record). Then the fix turns
them green. Covers: reflection persisted onto the clone record; clone:// address derived (provenance-stable
clone://<source_sid>/<at>); get_by_address(clone://) → clone+reflection (the point-lookup consumer).
Supervisor/msg mocked (no live clone). Run: python3 tests/cc_clone_reflection_persist_acceptance.py
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from runtime import cc_clone

PASS, FAIL = [], []


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'ok ' if cond else 'FAIL'} {name}" + (f"  — {detail}" if detail and not cond else ""))


tmp = tempfile.mkdtemp(prefix="cc_clone_refl_")
cc_clone.CLONES_DIR = os.path.join(tmp, "clones")
os.makedirs(cc_clone.CLONES_DIR)

# a clone record on disk (as clone_at would have written it)
rec = {"kind": "supervised-clone", "handle": "clone-deadbeef", "supervisor_session": "as-x",
       "session_id": "newsid-1", "source_sid": "bda8ce28-6dfb-4a76-b13a-bc016b8574ca",
       "source_path": "/x.jsonl", "at": "uuid:f7187860-7efb-4512-97a4-c7faa7a80763",
       "cwd": "/home/tim", "description": "the registry/Heart era", "started": "2026-06-15T00:00:00"}
json.dump(rec, open(os.path.join(cc_clone.CLONES_DIR, "clone-deadbeef.json"), "w"))

# mock the live DM so onboard_clone gets a reflection without a real supervised clone
REFLECTION = "I am the Heart-era clone. We were working out the registry/Heart frame — everything is registries with typed edges."
cc_clone.msg_clone = lambda h, m, timeout=240: {"handle": "clone-deadbeef", "session_id": "newsid-1",
                                                "at": rec["at"], "source_sid": rec["source_sid"], "reply": REFLECTION}

res = cc_clone.onboard_clone("clone-deadbeef", phase="reflect")
ok("onboard_clone returns the reflection (existing behaviour)", res.get("reflection") == REFLECTION)

# ★ THE BUG (falsify-first): the reflection must be PERSISTED on the durable clone record.
on_disk = json.load(open(os.path.join(cc_clone.CLONES_DIR, "clone-deadbeef.json")))
ok("reflection is PERSISTED on the clone record (the bug-fix — fails on unmodified code)",
   on_disk.get("reflection") == REFLECTION)

# clone:// address — provenance-stable, derived from (source_sid, at), verbatim cut token
expected_addr = f"clone://{rec['source_sid']}/{rec['at']}"
ok("clone:// address derived provenance-stable (clone://<source_sid>/<at>)",
   cc_clone.clone_address(rec) == expected_addr)
ok("clone:// address is on the persisted record",
   on_disk.get("address") == expected_addr)

# get_by_address(clone://) → the clone + its reflection (the point-lookup consumer)
got = cc_clone.get_by_address(expected_addr)
ok("get_by_address(clone://) resolves to the clone record",
   got.get("handle") == "clone-deadbeef" and got.get("source_sid") == rec["source_sid"])
ok("get_by_address(clone://) carries the persisted reflection (consumer payload)",
   got.get("reflection") == REFLECTION)
# fail-loud on an unknown clone address
try:
    cc_clone.get_by_address("clone://bda8ce28-6dfb-4a76-b13a-bc016b8574ca/uuid:does-not-exist")
    ok("get_by_address fails loud on an unknown clone address", False)
except cc_clone.CloneError:
    ok("get_by_address fails loud on an unknown clone address", True)

import shutil
shutil.rmtree(tmp, ignore_errors=True)

print(f"\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", ", ".join(FAIL))
    sys.exit(1)
print("ALL GREEN — reflection persisted on the clone record + clone://<source_sid>/<at> provenance-stable "
      "address + get_by_address point-lookup (clone+reflection). The distributed-memory payload is durable + addressed.")
