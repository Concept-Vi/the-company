"""portal — one artefact, many live views (context-13 "Portals").

A portal is NOT computed and NOT wired by dataflow. It is a live window onto another
address: `config.ref` (e.g. "run://codebase/answer"). The runtime resolves it BY REFERENCE
at view-time (Suite.state reads head(ref) on every call), so the same artefact can appear in
many places at once, live, never copied — change the source and the portal reflects it.

`RESOLVE='reference'` tells the scheduler to skip firing this node (it has no computation).
run() therefore must never be called; if it is, fail loud (no silent fallback).
"""
VERSION = '1'
KIND = 'content'
RESOLVE = 'reference'          # scheduler skips; output resolved live from config.ref
PORTS_IN = {}
PORTS_OUT = {'view': 'Any'}    # addressable as a view; not wired by dataflow
CONFIG = {'ref': ''}           # the address this portal is a window onto


def run(inputs, config):
    raise RuntimeError(
        "portal is reference-resolved (RESOLVE='reference') — run() must never be called; "
        "its output is read live from config.ref by the runtime, not computed.")
