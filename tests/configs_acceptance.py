"""tests/configs_acceptance.py — RHM configs (slice 3, E1-E2).

"Everything must be configurable" (Tim). The RHM's model/provider and persona are config on
the SAME rhm node (system graph), set by the same verbs, persistent. The model+base_url drive
the fabric call (any OpenAI-compatible provider — NOT Claude-locked); persona shapes the voice.
Config storage/resolution proven here; the swap actually driving the call is proven by use.
"""
import os, sys, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from fabric import config as fcfg

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


store_dir = tempfile.mkdtemp(prefix="cfg-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    c = suite.rhm_config()
    check("default model is the configured brain (not Claude)", c["model"] == fcfg.DEFAULT_BRAIN)
    check("default persona is empty", c["persona"] == "")
    check("default base_url is the fabric endpoint", c["base_url"] == fcfg.DEFAULT_BASE_URL)

    # swap model/provider + set a persona — configurable
    suite.set_rhm_config({"model": "deepseek-v4-flash:cloud", "persona": "a terse naval officer"})
    c = suite.rhm_config()
    check("model swap persists", c["model"] == "deepseek-v4-flash:cloud")
    check("persona persists", c["persona"] == "a terse naval officer")
    suite.set_rhm_config({"base_url": "http://localhost:4100/v1"})
    check("provider/base_url is configurable", suite.rhm_config()["base_url"] == "http://localhost:4100/v1")

    # mode + config coexist on the one node (don't clobber each other)
    suite.set_mode("focus")
    c = suite.rhm_config()
    check("mode and model coexist", c["mode"] == "focus" and c["model"] == "deepseek-v4-flash:cloud")

    # persists across sessions
    s2 = Suite(FsStore(os.path.join(store_dir, "store")), reg, nodes_dir=NODES)
    c2 = s2.rhm_config()
    check("config persists across sessions", c2["model"] == "deepseek-v4-flash:cloud"
          and c2["persona"] == "a terse naval officer" and c2["mode"] == "focus")

    # only known keys are accepted (no arbitrary config injection)
    s2.set_rhm_config({"model": "x", "evil": "rm -rf"})
    check("unknown config keys are ignored", "evil" not in s2._rhm_cfg())

    print(f"\nALL {PASS} CHECKS PASS — RHM model/provider + persona configurable & persistent")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
