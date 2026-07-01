# Durable launcher for the page-face service on 0.0.0.0:8774 (phone-reachable over tailscale).
# Uses the REAL page_face.serve (render_page + no-script CSP). Survives WSL restart (not in /tmp).
import sys, os
sys.path.insert(0, "/home/tim/company"); os.chdir("/home/tim/company")
from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from runtime import page_face as pf
suite = Suite(FsStore(".data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")
print("[pages] real page-face service on 0.0.0.0:8774", flush=True)
pf.serve(suite, host="0.0.0.0", port=8774).serve_forever()
