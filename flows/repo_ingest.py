"""flows/repo_ingest.py — ① the repo-exocortex ingest as a registered flow row. ONE call ingests a
bounded batch of repo files into the queryable embedded corpus (space='repo'): deterministic walk
(hidden-dirs skipped as a class, paths normalized — one file, one code:// id) → repo_digest MAP →
capture+embed. Hash-aware incremental (G25): unchanged files skip, CHANGED files re-ingest and their
vectors refresh — re-running keeps the corpus current. PROPOSES corpus records only."""
import sys

FLOW = {
    "id": "repo_ingest",
    "label": "Repo-exocortex ingest (codebase → queryable embedded corpus, bounded batches)",
    "description": (
        "Walks the repo (.py/.md, junk/hidden dirs skipped), digests each file with the resident "
        "model, and captures+embeds the digests into the 'repo' space keyed code://<path> — so "
        "corpus(op='query') can ASK the codebase instead of cold-reading it. Incremental by content "
        "hash: re-runs ingest only new/changed files. The floor for the drift-radar and "
        "ask-the-codebase flows."),
    "params": {
        "max_files": {"desc": "files per call (batches compose; the response reports `remaining`)",
                      "default": 60},
        "root": {"desc": "walk root (repo-relative)", "default": "."},
    },
    "proposes_only": True,
}


def run(max_files: int = 60, root: str = ".") -> dict:
    sys.path.insert(0, "/home/tim/company")
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore
    s = Suite(FsStore("/home/tim/company/.data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")
    return s.ingest_paths(roots=[root], project="company", session="ingest-flow", round="r1",
                          max_files=int(max_files))
