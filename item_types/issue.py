ITEM_TYPE = {
    "id": "issue",
    "label": "issue",
    "desc": "A bug / wrong-behaviour report from using the tools / CI / app. PROVENANCE: this type "
            "supersedes the legacy hand-kept SYSTEM-GAPS.md ledger — gap-pressure graduating from a "
            "hand-maintained markdown file into a first-class typed registry record.",
    "initial": "open",
    "states": ["open", "triaged", "fixing", "resolved", "wontfix"],
    "transitions": {
        "open": ["triaged", "wontfix"],
        "triaged": ["fixing", "wontfix"],
        "fixing": ["resolved", "wontfix"],
        "resolved": [],
        "wontfix": ["open"],
    },
}
