"""tests/cc_attachments_acceptance.py — structural gate for runtime/cc_attachments.py (channel-attachment
as a file-discovered binding registry). NO live channel needed: channel-existence is stubbed. Covers the
contract: type validated fail-loud, channel validated, multi enforced, manifest = projection of rows,
detach is presence=truth, target stored opaque. Run: python3 tests/cc_attachments_acceptance.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from runtime import cc_attachments as ca

PASS, FAIL = [], []


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'ok ' if cond else 'FAIL'} {name}" + (f"  — {detail}" if detail and not cond else ""))


# isolate the binding store + stub channel-existence (file-disjoint: we don't touch real channels)
tmp = tempfile.mkdtemp(prefix="cc_att_test_")
DIR = os.path.join(tmp, "attachments")
ca._channel_exists = lambda c: c in ("ch-real", "noticeboard")   # stub: these channels "exist"

# the 5 seed attachment-types are discovered from the real attachment_types/ dir
ok("attachment_types registry discovers the seed kinds",
   set(["board_items", "sessions", "docs", "recall", "cloning"]).issubset(set(ca.attachment_types())))

# attach a board item (the actual board://item-e523b30d use-case) to a real channel
a1 = ca.attach("ch-real", "board_items", "board://item-e523b30d", attachments_dir=DIR)
ok("attach returns a binding row with the exact schema",
   set(a1.keys()) == {"id", "channel", "attachment_type", "target", "added"}
   and a1["channel"] == "ch-real" and a1["attachment_type"] == "board_items")
ok("attach stores `target` VERBATIM (opaque ref — never parsed)",
   a1["target"] == "board://item-e523b30d")
ok("binding id is att-<8hex>", a1["id"].startswith("att-") and len(a1["id"]) == 12)

# unknown attachment_type → fail loud
try:
    ca.attach("ch-real", "not_a_kind", "x", attachments_dir=DIR)
    ok("attach unknown type fails loud", False)
except ca.AttachmentError as e:
    ok("attach unknown type fails loud", "unknown attachment_type" in str(e))

# unknown channel → fail loud (never a dangling attach)
try:
    ca.attach("ch-ghost", "docs", "/tmp/x.md", attachments_dir=DIR)
    ok("attach to a non-existent channel fails loud", False)
except ca.AttachmentError as e:
    ok("attach to a non-existent channel fails loud", "not found" in str(e))

# multi=False enforcement: recall is non-multi → a 2nd recall attach to the same channel fails
ca.attach("ch-real", "recall", "scope:project=company", attachments_dir=DIR)
try:
    ca.attach("ch-real", "recall", "scope:project=other", attachments_dir=DIR)
    ok("non-multi type rejects a 2nd binding on the same channel", False)
except ca.AttachmentError as e:
    ok("non-multi type rejects a 2nd binding on the same channel", "non-multi" in str(e))
# but multi=True (board_items) allows many
ca.attach("ch-real", "board_items", "board://item-ffb8dac6", attachments_dir=DIR)
ok("multi=True type allows many bindings",
   len([a for a in ca.list_attachments(channel="ch-real", attachment_type="board_items", attachments_dir=DIR)]) == 2)

# manifest = PROJECTION of the rows grouped by type (a view, not stored)
m = ca.manifest("ch-real", attachments_dir=DIR)
ok("manifest projects rows grouped by type",
   set(m["attachments"].keys()) == {"board_items", "recall"}
   and sorted(m["attachments"]["board_items"]) == ["board://item-e523b30d", "board://item-ffb8dac6"]
   and m["attachments"]["recall"] == ["scope:project=company"]
   and m["count"] == 3)

# list filtered by channel only returns that channel's rows
ca.attach("noticeboard", "docs", "/home/tim/company/README.md", attachments_dir=DIR)
ok("list_attachments filters by channel",
   all(a["channel"] == "ch-real" for a in ca.list_attachments(channel="ch-real", attachments_dir=DIR))
   and len(ca.list_attachments(channel="noticeboard", attachments_dir=DIR)) == 1)

# detach is presence=truth (removes the binding; fail-loud on unknown)
det = ca.detach(a1["id"], attachments_dir=DIR)
ok("detach removes the binding (presence=truth)",
   det["detached"] == a1["id"]
   and not any(a["id"] == a1["id"] for a in ca.list_attachments(channel="ch-real", attachments_dir=DIR)))
try:
    ca.detach("att-deadbeef", attachments_dir=DIR)
    ok("detach unknown fails loud", False)
except ca.AttachmentError:
    ok("detach unknown fails loud", True)

# require_channel=False allows a forward binding (channel created later)
fwd = ca.attach("ch-future", "sessions", "session://ch-future", require_channel=False, attachments_dir=DIR)
ok("require_channel=False permits a forward binding", fwd["channel"] == "ch-future")

import shutil
shutil.rmtree(tmp, ignore_errors=True)

print(f"\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", ", ".join(FAIL))
    sys.exit(1)
print("ALL GREEN — channel-attachment binding registry: type/channel/multi fail-loud, manifest=projection, "
      "target opaque, detach=presence-truth, file-disjoint (channel read-only).")
