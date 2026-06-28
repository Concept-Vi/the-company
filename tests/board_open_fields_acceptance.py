"""tests/board_open_fields_acceptance.py — F3: the board frontmatter is OPEN, not a closed allowlist.

Proves (by use, round-trip through the real render+parse) that a record key NOT in FRONTMATTER_KEYS still
persists across write→read — so new typed fields (e.g. `active` for block-versions) are never silently
dropped. Also proves existing canonical items serialise unchanged (the canonical keys render first, in order).
Foundation company-improvement #5 / S9 dependency.
"""
import os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_STORE"] = os.path.join(tempfile.mkdtemp(prefix="board-open-"), "store")

from runtime import cc_board as cb

PASS = 0
def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")

board_dir = os.path.join(tempfile.mkdtemp(prefix="board-open-bd-"), "noticeboard")
os.makedirs(board_dir, exist_ok=True)

# 1. an UNLISTED field round-trips (the F3 fix)
rec = cb.file_item("note", "open-fields probe", "body text", "tester", board_dir=board_dir)
# add a field NOT in FRONTMATTER_KEYS directly on the record, re-render, re-read
rec2 = cb.get_item(rec["id"], board_dir=board_dir)
rec2["active"] = "board://rev-xyz"          # the kind of new typed field S9 needs
rec2["custom_axis"] = ["a", "b"]
cb._write(board_dir, rec2)                  # exercises _render
back = cb.get_item(rec["id"], board_dir=board_dir)
check("an unlisted field ('active') persists across write→read", back.get("active") == "board://rev-xyz")
check("an unlisted list field ('custom_axis') persists too", back.get("custom_axis") == ["a", "b"])
check("'active' is NOT in the closed FRONTMATTER_KEYS (proves it's the OPEN path, not a quiet allowlist add)",
      "active" not in cb.FRONTMATTER_KEYS)

# 2. the body is NOT leaked into frontmatter
import io
on_disk = open(os.path.join(board_dir, f"{rec['id']}.md"), encoding="utf-8").read()
fm_block = on_disk.split("---", 2)[1] if on_disk.count("---") >= 2 else ""
check("`body` is not duplicated into frontmatter", "body:" not in fm_block)
check("the body still renders after the fence", "body text" in on_disk)

# 3. canonical keys still render FIRST + in order (existing items unchanged)
fm_keys_in_order = [ln.split(":", 1)[0] for ln in fm_block.strip().splitlines() if ":" in ln and not ln.startswith(" ")]
canonical_present = [k for k in cb.FRONTMATTER_KEYS if k in back]
# the canonical keys that appear must appear in their canonical relative order, before the extras
canon_seq = [k for k in fm_keys_in_order if k in cb.FRONTMATTER_KEYS]
check("canonical keys serialise in their fixed order (existing items unchanged)",
      canon_seq == [k for k in cb.FRONTMATTER_KEYS if k in canon_seq])
check("the extra fields appear AFTER the canonical keys",
      fm_keys_in_order.index("active") > fm_keys_in_order.index("id"))

print(f"\nALL {PASS} CHECKS PASS — board frontmatter is OPEN: new typed fields persist; canonical render unchanged (F3)")
