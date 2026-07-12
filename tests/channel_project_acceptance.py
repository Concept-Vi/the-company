"""tests/channel_project_acceptance.py — P1: channels belong to projects (the relational half).

The project ENTITY already exists (schema `container`, the container lane — container.projects,
project:// resolvable). This proves the P1 remainder BY USE against the REAL registry (read-only):
(1) create_channel(project='company') validates + the fold carries it; (2) an UNKNOWN project fails
loud (registry-is-truth); (3) None = the unparented special case; (4) set_channel_project re-parents +
detaches (audited events, fold follows); (5) channels_of_project folds project→channels (1→N, archived
excluded). Channel writes hit a TEMP store; container.projects is only read.
"""
import os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime import session_channels as sc

PASS = 0
def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")

store = FsStore(os.path.join(tempfile.mkdtemp(prefix="chproj-"), "store"))
SID = "p1-probe-sid"

# 1 — create with a REAL project (container.projects carries 'company')
c1 = sc.create_channel(store, name="p1-chan-a", members=[{"session": SID}], project="company", registry=None)
check("create_channel(project='company') validates against container.projects + the fold carries it",
      c1.get("project") == "company")

# 2 — unknown project fails loud
try:
    sc.create_channel(store, name="p1-chan-bad", project="no-such-project-xyz", registry=None)
    check("an UNKNOWN project fails loud", False)
except ValueError as e:
    check("an UNKNOWN project fails loud (registry-is-truth)", "unknown project" in str(e))

# 3 — None = unparented (the declared special case)
c2 = sc.create_channel(store, name="p1-chan-b", members=[{"session": SID}], registry=None)
check("a channel without a project is the legal special case (project=None)", c2.get("project") is None)

# 4 — re-parent + detach, audited via events, the fold follows
sc.set_channel_project(store, c2["id"], "company")
check("set_channel_project re-parents (fold follows the event)",
      sc.get_channel(store, c2["id"]).get("project") == "company")
sc.set_channel_project(store, c2["id"], None)
check("detach back to unparented", sc.get_channel(store, c2["id"]).get("project") is None)

# 5 — the project→channels fold (1→N; archived excluded)
c3 = sc.create_channel(store, name="p1-chan-c", project="company", registry=None)
sc.archive_channel(store, c3["id"])
ids = [r["id"] for r in sc.channels_of_project(store, "company")]
check("channels_of_project folds the ACTIVE channels of the project (1→N, archived excluded)",
      ids == [c1["id"]])

print(f"\nALL {PASS} CHECKS PASS — channels belong to projects, validated against the REAL container registry (P1)")
