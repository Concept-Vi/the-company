"""codebase — a content node that reads the repo's own source+docs into one context blob.

The first-purpose substrate: the system's code, linked into a composition so it can be
asked about (and, later, changed). Content kind. Fail-loud if it exceeds the context budget
(no silent truncation — the mining-failure lesson); past that, retrieval is needed.
See nodes/AGENTS.md.
"""
import glob
import os

VERSION = "1"
KIND = "content"
VOLATILE = True          # reads the live filesystem → never memo-cache (output isn't pure; red-team F1)
PORTS_IN: dict = {}
PORTS_OUT = {"context": "Text"}

DEFAULT_GLOBS = ["AGENTS.md", "MAP.md", "README.md",
                 "contracts/*.py", "runtime/*.py", "store/*.py",
                 "fabric/*.py", "nodes/*.py", "mcp_face/*.py"]


def run(inputs: dict, config: dict):
    root = config.get("root") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ~/company
    globs = config.get("globs", DEFAULT_GLOBS)
    max_chars = int(config.get("max_chars", 400000))   # bumped as the repo grew (was 160k); past this, retrieval
    parts, total = [], 0
    for g in globs:
        for p in sorted(glob.glob(os.path.join(root, g))):
            try:
                text = open(p, encoding="utf-8").read()
            except Exception:
                continue
            chunk = f"\n===== {os.path.relpath(p, root)} =====\n{text}\n"
            total += len(chunk)
            if total > max_chars:                       # fail loud, never silently truncate
                raise ValueError(
                    f"codebase exceeds max_chars ({max_chars}) at {os.path.relpath(p, root)} — "
                    "this needs retrieval (embed+retrieve), not context-stuffing.")
            parts.append(chunk)
    return "".join(parts)
