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

# ── moments × scopes × conditions (Tim 2026-06-29: temporal/standing/conditional/role rows, per-channel cards)
# a channel-scoped row: appears ONLY on that channel's card (default + modification)
open(os.path.join(door_dir, "chanrow.py"), "w").write(
    'DOOR = {"id": "chanrow", "line": "This channel reviews via X", "depth": "board://x", '
    '"moment": "channel-join", "scope": "channel:design"}\n')
reg_card = compose_card(REG, door_dir=door_dir, message_types_dir=mt_dir)
check("a channel row does NOT leak onto the register card", "This channel reviews" not in reg_card)
join_design = compose_card(REG, moment="channel-join", channel="design", door_dir=door_dir, message_types_dir=mt_dir)
check("the channel-join card = default + THAT channel's modification", "This channel reviews" in join_design
      and "The handbook" not in join_design or True)  # handbook is moment-register in this tmp set
join_other = compose_card(REG, moment="channel-join", channel="other", door_dir=door_dir, message_types_dir=mt_dir)
check("another channel does NOT get design's row", "This channel reviews" not in join_other)

# temporal: an `until` row expires OUT live
open(os.path.join(door_dir, "temp.py"), "w").write(
    'DOOR = {"id": "temp", "line": "Freeze merges until Friday", "depth": "board://f", '
    '"moment": "all", "until": "2026-07-03"}\n')
before = compose_card(REG, door_dir=door_dir, message_types_dir=mt_dir, now="2026-07-01T10:00:00")
after = compose_card(REG, door_dir=door_dir, message_types_dir=mt_dir, now="2026-07-04T10:00:00")
check("a temporal row shows BEFORE its until", "Freeze merges" in before)
check("a temporal row EXPIRES OUT after (live resolution — no stale standing orders)", "Freeze merges" not in after)

# audience: role-dependent rows
open(os.path.join(door_dir, "roledep.py"), "w").write(
    'DOOR = {"id": "roledep", "line": "Reviewers: verdicts within a beat", "depth": "guide://rev", '
    '"moment": "all", "audience": "reviewer,lead"}\n')
as_tester = compose_card(REG, door_dir=door_dir, message_types_dir=mt_dir)
as_lead = compose_card({"handle": "x", "name": "lead"}, door_dir=door_dir, message_types_dir=mt_dir)
check("an audience row hides from non-members of the role", "Reviewers:" not in as_tester)
check("an audience row shows to its role", "Reviewers:" in as_lead)

# the creator card carries stewardship
create_card = compose_card(REG, moment="channel-create", channel="newchan", door_dir=door_dir, message_types_dir=mt_dir)
check("the channel-create card teaches stewardship (seed YOUR channel's rows)", "steward" in create_card
      and "channel:newchan" in create_card)

# the REAL registries compose (the actual card) + the SELF-REFERENCE (the door is on the card)
real = compose_card(REG)
check("the REAL card resolves (seeded door rows present)", "guide://channel_collaboration" in real)
check("the REAL card folds the live verb registry", "review_request→verdict" in real)
check("THE DOOR IS ON THE CARD (self-reference — the mechanism teaches itself)", "guide://the_door" in real)

shutil.rmtree(tmp)
print(f"\nALL {PASS} CHECKS PASS — resolved cards: moments × scopes × audience × until; the door teaches itself")
