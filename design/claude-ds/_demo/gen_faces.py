import sys, os, json, re
sys.path.insert(0, "/home/tim/company"); os.chdir("/home/tim/company")
from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from runtime.cognition import guide_registry
from runtime import page_face as pf
suite = Suite(FsStore(".data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")
TAILSCALE = "100.81.137.106"

# REMOVE the hand-written (hardcoded-restatement) canvas faces — Tim rejected them.
import contracts  # noqa
binds_path = "design/_system/page_bindings.json"
binds = json.load(open(binds_path))
for bad in ("ui://canvas/colors", "ui://canvas/components"):
    if bad in binds:
        del binds[bad]; print("removed fabricated face:", bad)
json.dump(binds, open(binds_path, "w"), indent=2, sort_keys=True)

# Build the face-index from the REAL guide faces (model-authored, grounded). Real excerpt from real content.
def excerpt(md):
    # first real prose line (skip headings/blank), trimmed — REAL content, not fabricated
    for ln in md.splitlines():
        s = ln.strip()
        if s and not s.startswith("#") and not s.startswith("*"):
            s = re.sub(r"[`*]", "", s)
            return (s[:150] + "…") if len(s) > 150 else s
    return ""

reg = guide_registry()
index = {}
for gid in reg:
    g = reg[gid]
    addr = "guide://" + gid
    if addr not in binds:   # only ones that actually have a page bound
        continue
    subject = g.target.split("://",1)[-1].replace("_"," ")
    index[gid] = {
        "id": gid, "address": addr, "title": g.label or gid,
        "subject": subject, "kind": "guide",
        "faceof": f"the how-to for the {subject}",
        "excerpt": excerpt(g.content),
        "url": f"http://{TAILSCALE}:8774/page?addr=" + addr.replace("://","%3A%2F%2F"),
    }
out = "/home/tim/company/design/claude-ds/face-index.js"
with open(out, "w") as fh:
    fh.write("// face-index.js — GENERATED from the live page-face bindings (the REAL guide faces).\n")
    fh.write("// content is model-authored & grounded; this index carries title/subject/excerpt/url — no hardcoded restatement.\n")
    fh.write("window.CV_FACES = " + json.dumps(index, indent=2) + ";\n")
print("\nface-index now =", list(index.keys()))
print(json.dumps(index, indent=2)[:700])
