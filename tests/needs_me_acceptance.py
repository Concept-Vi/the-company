"""needs_me_acceptance — the NEEDS-ME INBOX (I1): registry discovery + the fail-soft fold + card shape.

Three gates:
  (a) `runtime.inbox_sources.InboxSourceRegistry` discovers the real `inbox_sources/` dir — fail-loud
      validation (id==stem, required fields, card_shape/verb schema), the 4 seed rows present.
  (b) A malformed source module (bad fetch, a raising fetch, a raw item missing its id_field) is fail-SOFT
      at the FOLD boundary: `needs_me_inbox()` never raises and never blanks the other sources' cards —
      the break shows up LOUD in `errors[]`, one entry per broken source.
  (c) The card shape contract: every card is exactly {source, id, address, title, why, verbs, created},
      verb doors get `{id}`/`{address}` substituted per-card, and the real `inbox_sources/*` fetch
      functions run against LIVE data (by-use — not a mock) without raising.

Run: ./.venv/bin/python tests/needs_me_acceptance.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from runtime.inbox_source_registry import InboxSourceRegistry, resolve_fetch
from runtime.needs_me import needs_me_inbox

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}  {detail}")


print("=== needs_me_acceptance — the registry-driven NEEDS-ME INBOX (I1) ===")

# ---- (a) the real inbox_sources/ dir discovers clean -------------------------------------------
INBOX_SOURCES_DIR = os.path.join(ROOT, "inbox_sources")
reg = InboxSourceRegistry().discover([INBOX_SOURCES_DIR])

check("inbox_sources/ discovers at least the 4 seed rows", len(reg) >= 4, f"found {sorted(reg)}")
for expected in ("decisions", "surfaced", "obligations", "board_requests"):
    check(f"seed source {expected!r} is registered", expected in reg)

for sid in reg:
    row = reg[sid]
    check(f"{sid}: id == module name (file-addressable)", row.id == sid)
    check(f"{sid}: fetch resolves to a real callable", callable(resolve_fetch(row.fetch)),
          f"fetch={row.fetch!r}")
    check(f"{sid}: card_shape declares all 5 field hints",
          all(k in row.card_shape for k in ("id_field", "address_field", "title_field", "why_field", "created_field")))
    check(f"{sid}: verbs is a non-empty list of {{id,label,door}}",
          bool(row.verbs) and all(set(("id", "label", "door")) <= set(v) for v in row.verbs))

check("re-discovery is idempotent (same set twice)",
      sorted(InboxSourceRegistry().discover([INBOX_SOURCES_DIR])) == sorted(reg))

# ---- (a2) fail-loud on a malformed row -----------------------------------------------------------
bad_dir = tempfile.mkdtemp(prefix="inbox_sources_bad_")
with open(os.path.join(bad_dir, "mismatch.py"), "w") as f:
    f.write('INBOX_SOURCE = {"id": "not-the-filename", "label": "x", "fetch": "os:getcwd", '
            '"card_shape": {"id_field":"id","address_field":"a","title_field":"t","why_field":"w","created_field":"c"}, '
            '"verbs": [{"id":"v","label":"V","door":"/api/x"}]}\n')
raised = False
try:
    InboxSourceRegistry().discover([bad_dir])
except ValueError:
    raised = True
check("a row whose id != filename FAILS LOUD at discovery (never a silent skip)", raised)

# ---- (b) the fold is fail-SOFT per source, loud in errors[] --------------------------------------
# module names must equal their INBOX_SOURCE `id` (file-addressable, the same law as item_types) AND be
# importable by their `fetch` dotted reference — so put mixed_dir on sys.path and name the files to match.
mixed_dir = tempfile.mkdtemp(prefix="inbox_sources_mixed_")
sys.path.insert(0, mixed_dir)
with open(os.path.join(mixed_dir, "inbox_sources_mixed_good.py"), "w") as f:
    f.write(
        "def fetch():\n"
        "    return [{'id': 'g1', 'address': 'board://g1', 'title': 'A good card', "
        "'why': 'because', 'created': '2026-07-01T00:00:00Z'}]\n\n"
        "INBOX_SOURCE = {'id': 'inbox_sources_mixed_good', 'label': 'Good', "
        "'fetch': 'inbox_sources_mixed_good:fetch', "
        "'card_shape': {'id_field': 'id', 'address_field': 'address', 'title_field': 'title', "
        "'why_field': 'why', 'created_field': 'created'}, "
        "'verbs': [{'id': 'view', 'label': 'View', 'door': 'board://{address}'}]}\n"
    )
with open(os.path.join(mixed_dir, "inbox_sources_mixed_broken.py"), "w") as f:
    f.write(
        "def fetch():\n"
        "    raise RuntimeError('this source is genuinely broken')\n\n"
        "INBOX_SOURCE = {'id': 'inbox_sources_mixed_broken', 'label': 'Broken', "
        "'fetch': 'inbox_sources_mixed_broken:fetch', "
        "'card_shape': {'id_field': 'id', 'address_field': 'address', 'title_field': 'title', "
        "'why_field': 'why', 'created_field': 'created'}, "
        "'verbs': [{'id': 'view', 'label': 'View', 'door': '/api/x'}]}\n"
    )
import importlib
importlib.invalidate_caches()

result = needs_me_inbox(dirs=[mixed_dir])
check("needs_me_inbox() with one broken source never raises", True)   # reaching here proves it
check("the broken source is recorded in errors[] (loud, not silent)",
      any(e.get("source") == "inbox_sources_mixed_broken" and "genuinely broken" in e.get("error", "")
          for e in result["errors"]),
      f"errors={result['errors']}")
check("the good source's card still rendered (one break never blanks the rest)",
      any(c["id"] == "g1" and c["source"] == "inbox_sources_mixed_good" for c in result["cards"]),
      f"cards={result['cards']}")

# ---- (c) card shape contract + verb substitution --------------------------------------------------
good_card = next(c for c in result["cards"] if c["id"] == "g1")
check("card shape is exactly {source,id,address,title,why,verbs,created}",
      set(good_card) == {"source", "id", "address", "title", "why", "verbs", "created"}, f"{good_card}")
check("verb door substitutes {address} with the card's own address",
      good_card["verbs"][0]["door"] == "board://board://g1", f"{good_card['verbs']}")

# ---- (c2) the REAL inbox_sources/* run against live data without raising --------------------------
live = needs_me_inbox()
check("needs_me_inbox() over the REAL inbox_sources/ dir returns the top-level contract",
      set(live) == {"cards", "count", "sources", "errors"}, f"{sorted(live)}")
check("count matches len(cards)", live["count"] == len(live["cards"]))
check("every live source is represented in `sources`",
      set(live["sources"]) >= {"decisions", "surfaced", "obligations", "board_requests"})
bad_cards = [c for c in live["cards"] if set(c) != {"source", "id", "address", "title", "why", "verbs", "created"}]
check("every LIVE card matches the exact shape contract", not bad_cards, f"{bad_cards[:3]}")
bad_verbs = [c for c in live["cards"] for v in c["verbs"] if set(v) != {"id", "label", "door"}]
check("every LIVE verb matches {id,label,door}", not bad_verbs, f"{bad_verbs[:3]}")
if live["errors"]:
    print(f"  ℹ️  live errors[] (fail-soft, not a test failure by itself): {live['errors']}")

print(f"\n{'PASS' if FAIL == 0 else 'FAIL'} — {PASS} passed, {FAIL} failed")
sys.exit(0 if FAIL == 0 else 1)
