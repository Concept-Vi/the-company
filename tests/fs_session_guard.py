"""tests/fs_session_guard.py — the review-session storage methods cannot silently vanish (T3-SESSION-CHURN).

`save_session`/`load_session`/`list_sessions` (store/fs_store.py) are the durable substrate the
walkthrough/review organ runs on (suite.start_session→save_session; suite.next/_load_session→load_session).
They existed in `main`, were dropped by one build loop, and re-added by the next — an instability signal.
This guard asserts the round-trip behavior by USE so a future layer can't silently drop the capability
again: a session record survives a write→read across a *fresh store instance* (real persistence, not an
in-memory dict), the listing reflects exactly what was written, and a missing id returns None (fail-soft
read, not a crash). It exercises the REAL FsStore on a real temp dir — no mocks.

Run: ./.venv/bin/python tests/fs_session_guard.py
"""
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore

PASS = 0
ok = True


def check(label, cond):
    global PASS, ok
    ok &= bool(cond)
    if cond:
        PASS += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


def main():
    store_dir = tempfile.mkdtemp(prefix="fs-session-guard-")
    try:
        root = os.path.join(store_dir, "store")
        store = FsStore(root)

        # --- the three methods exist + are callable (the capability itself) ---
        check("FsStore.save_session exists", callable(getattr(store, "save_session", None)))
        check("FsStore.load_session exists", callable(getattr(store, "load_session", None)))
        check("FsStore.list_sessions exists", callable(getattr(store, "list_sessions", None)))

        # --- empty to start: list is empty, a missing id reads None (fail-soft, not a crash) ---
        check("list_sessions empty on a fresh store", store.list_sessions() == [])
        check("load_session of a missing id returns None (no crash)", store.load_session("nope") is None)

        # --- round-trip: a real review-session record (the shape start_session writes) ---
        session = {"id": "1717-3", "graph": "review-1717-3", "mode": "walkthrough",
                   "items": ["s1-review", "s2-review", "s3-review"],
                   "cursor": 0, "opened": [], "done": False}
        store.save_session(session)
        got = store.load_session("1717-3")
        check("load_session returns the saved record", got is not None)
        check("round-trip preserves id", got["id"] == "1717-3")
        check("round-trip preserves the item list", got["items"] == ["s1-review", "s2-review", "s3-review"])
        check("round-trip preserves cursor + done", got["cursor"] == 0 and got["done"] is False)
        check("round-trip preserves mode", got["mode"] == "walkthrough")
        check("list_sessions reflects the saved id (stem matches the id)",
              store.list_sessions() == ["1717-3"])

        # --- mutation persists (the walk advances cursor/opened across next() calls) ---
        session["cursor"] = 2
        session["opened"] = [0, 1]
        session["done"] = False
        store.save_session(session)
        got2 = store.load_session("1717-3")
        check("an advanced cursor persists on re-save", got2["cursor"] == 2)
        check("opened steps persist on re-save", got2["opened"] == [0, 1])

        # --- a SECOND session coexists; the listing is sorted + complete ---
        store.save_session({"id": "1800-1", "graph": "review-1800-1", "mode": "watch-and-react",
                            "items": ["sX-review"], "cursor": 0, "opened": [], "done": True})
        check("two sessions both listed, sorted", store.list_sessions() == ["1717-3", "1800-1"])

        # --- CRITICAL: persistence is on DISK, not in-memory — a FRESH store instance sees it ---
        # (this is the guarantee a "future layer can't silently drop them again" check needs: the
        #  methods must hit the filesystem, not a per-instance dict that evaporates on restart.)
        store2 = FsStore(root)
        fresh = store2.load_session("1717-3")
        check("a fresh FsStore instance reads the persisted session (real durability)",
              fresh is not None and fresh["cursor"] == 2 and fresh["opened"] == [0, 1])
        check("a fresh FsStore instance lists both sessions",
              store2.list_sessions() == ["1717-3", "1800-1"])

        print(f"\n" + (f"ALL {PASS} CHECKS PASS — fs_store session methods round-trip + persist (T3-SESSION-CHURN guard)"
                       if ok else "FS SESSION GUARD FAILED"))
        return 0 if ok else 1
    finally:
        shutil.rmtree(store_dir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
