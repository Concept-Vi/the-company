"""tests/channels_for_self_acceptance.py — P2: the self→channel-membership join, by use.

Proves: (1) with a registration present for THIS process's claude-ancestor pid, channels_for_self
resolves the handle + folds exactly the channels whose members carry the session (archived excluded);
(2) a registered-but-joined-nowhere session gets channels=[] honestly; (3) no registration → FAIL LOUD
(a scope default never guesses the caller). Uses a temp store + a temp registration keyed to the REAL
claude pid (restored after), so the join is exercised end-to-end, not mocked.
"""
import json, os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.session_scan import _claude_ancestor_pid
from runtime import session_channels as sc

PASS = 0
def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")

cp = _claude_ancestor_pid()
if cp is None:
    print("no claude ancestor (not a live session) — the fail-loud branch is still provable")

REGDIR = os.path.join(ROOT, ".data", "channels")
os.makedirs(REGDIR, exist_ok=True)
probe = os.path.join(REGDIR, "zz-p2probe.json")
# find any existing registration for THIS pid — the test must not fight it; park it aside if present
parked = []
for fn in os.listdir(REGDIR):
    if fn.endswith(".json") and not fn.startswith("_"):
        try:
            r = json.load(open(os.path.join(REGDIR, fn)))
        except (OSError, ValueError):
            continue
        if r.get("claude_pid") == cp:
            parked.append((fn, open(os.path.join(REGDIR, fn)).read()))
            os.remove(os.path.join(REGDIR, fn))

store = FsStore(os.path.join(tempfile.mkdtemp(prefix="cfs-"), "store"))
try:
    # 3 — no registration → fail loud
    try:
        sc.channels_for_self(store)
        check("no registration → FAIL LOUD", False)
    except ValueError as e:
        check("no registration → FAIL LOUD (never guess the caller)", "register_self" in str(e))

    # register a probe row for this pid with a known sid
    SID = "p2-probe-sid"
    json.dump({"handle": "zz-p2probe", "name": "p2probe", "session_id": SID, "cwd": ROOT,
               "pid": cp, "claude_pid": cp, "port": 0, "transport": "mail",
               "started": "2026-07-13T00:00:00"}, open(probe, "w"))

    # 2 — registered, joined nowhere → channels=[] honestly
    me = sc.channels_for_self(store)
    check("registered-but-joined-nowhere resolves with channels=[]",
          me["handle"] == "zz-p2probe" and me["channels"] == [])

    # 1 — join two channels (one archived) → exactly the active one folds
    c1 = sc.create_channel(store, name="p2-chan-a", members=[{"session": SID}], registry=None)
    c2 = sc.create_channel(store, name="p2-chan-b", members=[{"session": SID}], registry=None)
    sc.archive_channel(store, c2["id"])
    me = sc.channels_for_self(store)
    ids = [c["id"] for c in me["channels"]]
    check("folds exactly the ACTIVE channels carrying the session", ids == [c1["id"]])
    check("carries participation + name for the scope-render",
          me["channels"][0]["name"] == "p2-chan-a" and me["channels"][0]["participation"] != None)
finally:
    if os.path.exists(probe):
        os.remove(probe)
    for fn, content in parked:
        open(os.path.join(REGDIR, fn), "w").write(content)

print(f"\nALL {PASS} CHECKS PASS — channels_for_self: the self→membership join, fail-loud, archived excluded (P2)")
