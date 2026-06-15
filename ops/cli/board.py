"""board — the `company board` view (the Company NOTICEBOARD / inward-facing half).

The operator + cross-session face of runtime/cc_board.py: file typed items about the Company / MCP /
CLI / CI / app, list + pick them up, move them along their registry-declared lifecycle. Items are
git-tracked markdown at channel-memory/noticeboard/<id>.md, addressed board://<id>.

Talks to the runtime DIRECTLY (the board is pure file I/O — no service to stand up), so a different
session running `company board file ...` and the lead running `company board list/transition ...` IS
the cross-session request loop (a session files; a channel picks up).

  company board                                   list the board (all items)
  company board list [--type T] [--state S] [--source SRC] [--author A]   filtered pick-up read
  company board file --type T --title "..." [--body "..."] --author A
        [--source SRC] [--channel C] [--thread TH] [--link kind:target ...]   file a typed item
  company board get <id>                           read one item (full)
  company board transition <id> <to_state> [--by WHO] [--note "..."]       move along the lifecycle
  company board types                              the registries (valid item-types/sources/edge-kinds)
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from runtime import cc_board as cb  # noqa: E402


def _row(it):
    links = it.get("links") or []
    edge = f"  links={len(links)}" if links else ""
    title = (it.get("title") or "")[:54]
    return (f"  {it['id']:<14} {it.get('type',''):<8} {it.get('state',''):<10} "
            f"{it.get('author_session',''):<14} {title}{edge}")


def _print_item(it):
    print(f"  {it['id']}  ({it.get('address','')})")
    print(f"    type={it.get('type')}  state={it.get('state')}  source={it.get('source')}")
    print(f"    title: {it.get('title')}")
    if it.get("author_session"):
        print(f"    author_session={it.get('author_session')}  channel={it.get('channel') or '—'}  "
              f"thread={it.get('thread') or '—'}")
    print(f"    created={it.get('created')}  updated={it.get('updated')}")
    for ln in (it.get("links") or []):
        print(f"    edge: {ln.get('kind')} -> {ln.get('target')}")
    for h in (it.get("history") or []):
        print(f"    history: {h.get('from')} -> {h.get('to')}  by {h.get('by') or '—'}"
              + (f"  ({h.get('note')})" if h.get("note") else ""))
    if it.get("body"):
        print(f"\n    {it['body'].strip()}")


def run(args):
    """Dispatch `company board ...` (args = everything after `board`)."""
    sub = args[0] if args else "list"

    if sub in ("list", "ls"):
        flt, it_ = {}, iter(args[1:])
        for a in it_:
            if a == "--type":
                flt["type"] = next(it_, None)
            elif a == "--state":
                flt["state"] = next(it_, None)
            elif a == "--source":
                flt["source"] = next(it_, None)
            elif a == "--author":
                flt["author_session"] = next(it_, None)
            else:
                sys.exit(f"  unknown flag {a!r}. usage: company board list [--type T] [--state S] [--source SRC] [--author A]")
        try:
            rows = cb.list_items(**flt)
        except cb.BoardError as e:
            sys.exit(f"  ✖ {e}")
        if not rows:
            print("  no board items (yet). File one: company board file --type request --title \"...\" --author <you>")
            return
        print(f"  {len(rows)} item(s) on the board:")
        for it in rows:
            print(_row(it))
        return

    if sub == "types":
        print(f"  item-types : {', '.join(cb.item_types())}")
        print(f"  sources    : {', '.join(cb.source_types())}")
        print(f"  edge-kinds : {', '.join(cb.edge_kinds())}")
        return

    if sub == "file":
        body, links, it_ = {}, [], iter(args[1:])
        for a in it_:
            if a == "--type":
                body["item_type"] = next(it_, None)
            elif a == "--title":
                body["title"] = next(it_, None)
            elif a == "--body":
                body["body"] = next(it_, None)
            elif a == "--author":
                body["author_session"] = next(it_, None)
            elif a == "--source":
                body["source"] = next(it_, None)
            elif a == "--channel":
                body["channel"] = next(it_, None)
            elif a == "--thread":
                body["thread"] = next(it_, None)
            elif a == "--link":
                spec = next(it_, "") or ""
                if ":" not in spec:
                    sys.exit(f"  --link must be kind:target (got {spec!r}). e.g. --link authored_by:session://me")
                kind, _, target = spec.partition(":")
                links.append({"kind": kind, "target": target})
            else:
                sys.exit(f"  unknown flag {a!r}. usage: company board file --type T --title \"...\" --author A "
                         f"[--body \"...\"] [--source SRC] [--channel C] [--thread TH] [--link kind:target ...]")
        if not body.get("item_type") or not body.get("title") or not body.get("author_session"):
            sys.exit("  usage: company board file --type T --title \"...\" --author A  (type, title, author required)")
        kwargs = {k: v for k, v in body.items() if k not in ("item_type", "title", "body")}
        try:
            it = cb.file_item(body["item_type"], body["title"], body.get("body", ""),
                              links=links or None, **kwargs)
        except cb.BoardError as e:
            sys.exit(f"  ✖ {e}")
        print("  ✓ filed:")
        _print_item(it)
        return

    if sub == "get":
        if len(args) < 2:
            sys.exit("usage: company board get <id>")
        try:
            _print_item(cb.get_item(args[1]))
        except cb.BoardError as e:
            sys.exit(f"  ✖ {e}")
        return

    if sub in ("transition", "move"):
        if len(args) < 3:
            sys.exit("usage: company board transition <id> <to_state> [--by WHO] [--note \"...\"]")
        iid, to_state = args[1], args[2]
        opt, it_ = {}, iter(args[3:])
        for a in it_:
            if a == "--by":
                opt["by"] = next(it_, "")
            elif a == "--note":
                opt["note"] = next(it_, "")
            else:
                sys.exit(f"  unknown flag {a!r}. usage: company board transition <id> <to_state> [--by WHO] [--note \"...\"]")
        try:
            it = cb.transition(iid, to_state, **opt)
        except cb.BoardError as e:
            sys.exit(f"  ✖ {e}")
        print(f"  ✓ {iid} -> {it['state']}")
        _print_item(it)
        return

    sys.exit(f"unknown board subcommand {sub!r}. Try: company board [list|file|get|transition|types]")
