"""clone — the `company clone` view (the clone-FLEET: the distributed-memory addressed rows).

The stable, PORTABLE read surface for clone:// records — mirrors `company board get` so an external
process (e.g. recollection's fleet-recall ingest, a Node process) reads a clone's record + its persisted
reflection WITHOUT coupling to the private .data/clones/ layout (the same portability discipline the board
wire used). clone:// = the fleet/provenance axis (clone://<source-sid>/<cut>); records + the persisted
reflection live in runtime/cc_clone.py; the resolver is cognition.resolve_address (clone:// branch).

  company clone                       list the fleet (every clone:// address + handle + has-reflection?)
  company clone list                  same (alias)
  company clone get <clone://addr>    read one clone record + its persisted reflection (the stable read)
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from runtime import cc_clone as cc  # noqa: E402


def _addr(rec):
    try:
        return cc.clone_address(rec)
    except cc.CloneError:
        return "(unaddressable — missing source_sid/at)"


def _print_clone(rec):
    print(f"  {rec.get('handle', '?')}  ({_addr(rec)})")
    print(f"    source_sid={rec.get('source_sid')}  at={rec.get('at')}")
    print(f"    era={rec.get('description') or '—'}")
    print(f"    model={rec.get('model') or '—'}  session_id={rec.get('session_id') or '—'}")
    refl = rec.get("reflection")
    if refl:
        print(f"\n    reflection:\n    {str(refl).strip()}")
    else:
        print("    reflection: — (none persisted yet — (re-)onboard this clone post-fix to capture it)")


def run(args):
    """Dispatch `company clone ...` (args = everything after `clone`)."""
    sub = args[0] if args else "list"

    if sub in ("list", "ls"):
        try:
            clones = cc.list_clones()
        except cc.CloneError as e:
            sys.exit(f"  ✖ {e}")
        if not clones:
            print("  no clones in the fleet (.data/clones/ empty).")
            return
        print(f"  {len(clones)} clone(s) in the fleet:")
        for rec in clones:
            has = "✓refl" if rec.get("reflection") else "—"
            print(f"  {rec.get('handle', '?'):<18} {_addr(rec):<54} {has}")
        return

    if sub == "get":
        if len(args) < 2:
            sys.exit("usage: company clone get <clone://source-sid/cut>")
        try:
            _print_clone(cc.get_by_address(args[1]))
        except cc.CloneError as e:
            sys.exit(f"  ✖ {e}")
        return

    sys.exit(f"  unknown subcommand {sub!r}. usage: company clone [list | get <clone://addr>]")
