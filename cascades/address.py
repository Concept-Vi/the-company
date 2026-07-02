"""cascades/address.py — derive the ADDRESS TEMPLATE face (A's address_template cascade, priority 100).

From faces.address.template, derive the address grammar a type's instances are minted at (A's ltree
vi.{user}.<t>.{id}, reframed as text address = identity, law 1). Pure derivation; the resolver mints real
addresses at instance-create time."""

CASCADE = {
    "id": "address",
    "target": "project_resources",
    "priority": 100,
    "requires": ["address"],
    "desc": "the address template a type's instances are minted at, derived from faces.address",
}


def handle(type_row: dict, ctx: dict) -> dict:
    tid = type_row["id"]
    face = (type_row.get("faces") or {}).get("address") or {}
    template = face.get("template") or f"vi.{{user}}.{tid}.{{id}}"
    return {"type": tid, "template": template}
