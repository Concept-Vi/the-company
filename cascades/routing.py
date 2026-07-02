"""cascades/routing.py — derive the ROUTING face (A's agent_decorator cascade, priority 50).

**Hand-made-powers-the-generator (Tim's standing methodology, THE-CONTAINER §methodology).** A's generated
@<type> decorators hardcoded a single agent UUID+provider (place-not-derive). But the GHOST decorators
@research / @diagnostic (and @build / @design) were HAND-AUTHORED and RICHER — they carry mode +
affinity_bucket + routing to a real agent (Research Scout · QA & Verification). That hand-made richness is
the SPEC for the generator's next level: **a type declares which agent handles its kind of work.** Harvested
here as the routing face — `faces.routing = {mode, affinity_bucket, agent}` — so every type (generated or
reconstructed) can carry the routing the ghosts showed, derive-never-place."""

CASCADE = {
    "id": "routing",
    "target": "agent_routing",
    "priority": 50,
    "requires": ["routing"],
    "desc": "a type declares which agent handles its kind of work (mode/affinity_bucket/agent) — harvested "
            "from the hand-authored @research/@diagnostic decorators (hand-made powers the generator)",
}


def handle(type_row: dict, ctx: dict) -> dict:
    face = (type_row.get("faces") or {}).get("routing") or {}
    return {
        "type": type_row["id"],
        "mode": face.get("mode"),
        "affinity_bucket": face.get("affinity_bucket"),
        "agent": face.get("agent"),                        # a resolved routing target, not a placed UUID
        "event": face.get("event"),                        # optional: the event that triggers this routing
    }
