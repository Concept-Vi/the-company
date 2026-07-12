"""tests/door_card_acceptance.py — THE DOOR CARD IS RESOLVED, NEVER BAKED (Tim's check, 2026-06-29:
"any changes to registries automatically results with the current set").

Proves by use, against TEMP registry dirs: (1) the card's verb table folds LIVE from message_types —
ADD a verb row → it appears on the next card; REMOVE it → gone; (2) the card's depth entries fold LIVE
from door/ — add a door row → a new line; (3) malformed rows fail loud; (4) the REAL repo registries
compose (the actual card renders with the seeded rows + live verbs).
"""
import os, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from runtime.door import compose_card, door_rows, verb_table

PASS = 0
def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")

tmp = tempfile.mkdtemp(prefix="door-")
mt_dir = os.path.join(tmp, "message_types"); os.makedirs(mt_dir)
door_dir = os.path.join(tmp, "door"); os.makedirs(door_dir)
REG = {"handle": "ch-test1234", "name": "tester"}

# seed one verb + one door row
open(os.path.join(mt_dir, "mention.py"), "w").write(
    'MESSAGE_TYPE = {"id": "mention", "obligation": "reply"}\n')
open(os.path.join(door_dir, "handbook.py"), "w").write(
    'DOOR = {"id": "handbook", "line": "The handbook", "depth": "guide://handbook", "order": 1}\n')

card1 = compose_card(REG, door_dir=door_dir, message_types_dir=mt_dir)
check("card carries the live verb", "mention→reply" in card1)
check("card carries the door line + depth address", "The handbook → guide://handbook" in card1)
check("card carries the member identity", 'name="tester"' in card1)

# ADD a verb row → the NEXT card shows it (no code change anywhere)
open(os.path.join(mt_dir, "escalate.py"), "w").write(
    'MESSAGE_TYPE = {"id": "escalate", "obligation": "verdict", "label": "Escalation"}\n')
card2 = compose_card(REG, door_dir=door_dir, message_types_dir=mt_dir)
check("ADDING a verb ROW changes the card automatically", "escalate→verdict" in card2)

# ADD a door row → a new depth line appears
open(os.path.join(door_dir, "newcap.py"), "w").write(
    'DOOR = {"id": "newcap", "line": "A brand new capability", "depth": "guide://newcap", "order": 2}\n')
card3 = compose_card(REG, door_dir=door_dir, message_types_dir=mt_dir)
check("ADDING a door ROW changes the card automatically", "A brand new capability → guide://newcap" in card3)
check("door rows respect order", card3.index("The handbook") < card3.index("A brand new capability"))

# REMOVE the verb row → gone from the next card
os.remove(os.path.join(mt_dir, "escalate.py"))
card4 = compose_card(REG, door_dir=door_dir, message_types_dir=mt_dir)
check("REMOVING a verb row removes it from the card (current set, always)", "escalate" not in card4)

# malformed door row fails loud
open(os.path.join(door_dir, "bad.py"), "w").write('DOOR = {"id": "bad", "line": "no depth"}\n')
try:
    compose_card(REG, door_dir=door_dir, message_types_dir=mt_dir)
    check("a malformed door row fails loud", False)
except ValueError:
    check("a malformed door row fails loud (missing depth)", True)
os.remove(os.path.join(door_dir, "bad.py"))

# the REAL registries compose (the actual card)
real = compose_card(REG)
check("the REAL card resolves (seeded door rows present)", "guide://channel_collaboration" in real)
check("the REAL card folds the live verb registry", "review_request→verdict" in real)

shutil.rmtree(tmp)
print(f"\nALL {PASS} CHECKS PASS — the door card is RESOLVED from the registries; a registry edit IS a card edit")
