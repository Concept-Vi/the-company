ITEM_TYPE = {
    "id": "issue",
    "label": "issue",
    "desc": "A bug / wrong-behaviour report from using the tools / CI / app. PROVENANCE: this type "
            "supersedes the legacy hand-kept SYSTEM-GAPS.md ledger — gap-pressure graduating from a "
            "hand-maintained markdown file into a first-class typed registry record.",
    "initial": "open",
    # `closed` added additively (④ L6 BOARD): the cloud notice_board_posts pour lands 12 issue posts in
    # state `closed` (open 63 · resolved 46 · closed 12) — an additive state is safe for the existing 690
    # engine issue items (nothing removed) and lets the legacy status land without a lossy remap.
    "states": ["open", "triaged", "fixing", "resolved", "wontfix", "closed"],
    "transitions": {
        "open": ["triaged", "wontfix", "closed"],
        "triaged": ["fixing", "wontfix", "closed"],
        "fixing": ["resolved", "wontfix", "closed"],
        "resolved": ["closed"],
        "wontfix": ["open"],
        "closed": ["open"],
    },
}
