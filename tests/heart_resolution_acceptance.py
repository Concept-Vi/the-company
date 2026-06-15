"""tests/heart_resolution_acceptance.py — Heart unit H1.1: "follow one typed edge across two registries,
through the ONE resolver" (the cross-registry resolution/traversal seed — clone-cacc9e8b's scoping).

The Heart claim in miniature: the board, sessions, skills, capabilities are NODES in ONE addressed
graph. This proves it BY USE, on REAL data:
  • resolve_address spans MULTIPLE registries uniformly — board:// (cc_board) · session:// (agent-session
    registry) · skill:// (SkillRegistry) — ONE resolver, different registries. (board:// was register-but-
    defer; H1.1 wires its resolver branch.)
  • traverse() FOLLOWS a board item's typed edge and resolves the target THROUGH resolve_address, landing
    in a DIFFERENT registry — the edge is followed across, not returned as a string. That single hop IS
    the "one addressed state" claim.
  • FAIL LOUD both ends — an unresolvable board:// raises (never the blob/vec silent-empty anti-pattern);
    traverse over an unregistered edge-kind raises naming the valid kinds.

Falsify-first floor. Plain-assert harness (mirrors cc_board / cc_channels acceptance). Run:
    .venv/bin/python tests/heart_resolution_acceptance.py
"""
import glob
import os
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from runtime import cc_board as cb            # noqa: E402
from runtime.cognition import resolve_address  # noqa: E402
from store.fs_store import FsStore            # noqa: E402

PASS, FAIL = [], []


def check(n, c, d=""):
    (PASS if c else FAIL).append(n)
    print(f"  {'PASS' if c else 'FAIL'}  {n}" + (f"  — {d}" if d and not c else ""))


def raises(fn, exc=Exception, sub=""):
    try:
        fn()
        return False
    except exc as e:
        return sub in str(e) if sub else True
    except Exception:
        return False


store = FsStore(os.path.join(REPO, ".data", "store"))

# ── dynamically pick REAL fixtures (robust + non-littering — assert against what exists) ──────────────
items = sorted(glob.glob(os.path.join(cb.NOTICEBOARD_DIR, "*.md")))
real_item_id = os.path.basename(items[0])[:-3] if items else None

skills = [os.path.basename(p)[:-3] for p in sorted(glob.glob(os.path.join(REPO, "skills", "*.py")))
          if not os.path.basename(p).startswith("_")]
real_skill = skills[0] if skills else None

# a real agent-session id that actually load_agent_session-resolves
real_session = None
for p in sorted(glob.glob(os.path.join(REPO, ".data", "store", "agent_sessions", "*")))[:50]:
    sid = os.path.basename(p)
    sid = sid[:-5] if sid.endswith(".json") else sid
    try:
        if store.load_agent_session(sid) is not None:
            real_session = sid
            break
    except Exception:
        continue

check("0 fixtures present (real board item · skill · agent-session)",
      bool(real_item_id and real_skill and real_session),
      f"item={real_item_id} skill={real_skill} session={real_session}")

# ── ONE resolver, MANY registries (the unification) ──────────────────────────────────────────────────
r_board = resolve_address(store, f"board://{real_item_id}")
check("1 resolve_address board://<id> → the board item record (board registry)",
      isinstance(r_board, dict) and r_board.get("id") == real_item_id)

r_sess = resolve_address(store, f"session://{real_session}")
check("2 resolve_address session://<id> → a real agent-session record — DIFFERENT registry, SAME resolver",
      isinstance(r_sess, dict))

r_skill = resolve_address(store, f"skill://{real_skill}")
check("3 resolve_address skill://<id> → the skill content — a THIRD registry, same resolver",
      bool(r_skill))

# ── FAIL LOUD (the blob/vec anti-pattern guard — never a silent empty) ────────────────────────────────
check("4 resolve_address board://<missing> RAISES (fail-loud, never silent-empty)",
      raises(lambda: resolve_address(store, "board://item-nonexistent-zzz"), ValueError))
check("5 exchange:// is REGISTERED but resolver-DEFERRED → raises 'not content-resolvable yet' (recollection's lane)",
      raises(lambda: resolve_address(store, "exchange://sid/3"), ValueError, "not content-resolvable"))

# ── traverse: follow a typed edge ACROSS registries, through the one resolver ─────────────────────────
tmp = tempfile.mkdtemp(prefix="company-heart-")
# a board item whose edges point at OTHER registries (session + skill) — resolvable independent of the
# board dir, so the source can live in tmp (no littering of the real board).
src = cb.file_item("idea", "H1.1 traverse fixture",
                   "edges point across registries to prove the one-addressed-state traversal.",
                   author_session="ch-al7jdfdr",
                   links=[{"kind": "authored_by", "target": f"session://{real_session}"},
                          {"kind": "sourced_from", "target": f"skill://{real_skill}"}],
                   board_dir=tmp)

hops = cb.traverse(src["id"], store=store, board_dir=tmp)
check("6 traverse follows BOTH typed edges (returns one hop per link)", len(hops) == 2)
check("7 ★ traverse resolves authored_by ACROSS to the real SESSION record (not a string) — the one-addressed-state line",
      any(h["kind"] == "authored_by" and isinstance(h["resolved"], dict) for h in hops))
check("8 traverse resolves sourced_from ACROSS to the SKILL registry content",
      any(h["kind"] == "sourced_from" and h["resolved"] for h in hops))

one = cb.traverse(src["id"], "authored_by", store=store, board_dir=tmp)
check("9 traverse(kind=authored_by) follows ONLY that edge → the resolved session record",
      len(one) == 1 and one[0]["kind"] == "authored_by" and isinstance(one[0]["resolved"], dict))

# ── traverse FAIL LOUD on an unregistered edge-kind (names the valid kinds) ───────────────────────────
check("10 traverse over an UNREGISTERED edge-kind RAISES, naming valid kinds",
      raises(lambda: cb.traverse(src["id"], "blocks", store=store, board_dir=tmp), cb.BoardError, "kind"))

print(f"\n{'='*60}\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", ", ".join(FAIL))
    sys.exit(1)
print("ALL GREEN — Heart H1.1: ONE resolver spans board://·session://·skill:// (different registries);\n"
      "traverse follows a board item's typed edge ACROSS to a real record in another registry, through\n"
      "that one resolver; fail-loud on a missing address and an unregistered edge-kind. One addressed state.")
