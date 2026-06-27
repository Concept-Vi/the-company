"""Form-keyed capture schemas. Shared reframed PRIMARY fields (meaning first, surface as unverified) + per-form
add-ons. Maps the surveyed content_form (incl. long-tail) to a schema bucket. Light forms skip the deep AI."""
PRIMARY = ('"what":"<=15-word what this file is",'
 '"principle":"the underlying mental-model PRINCIPLE/INTENT this reaches for (the gold — may be unstated; infer the reach)",'
 '"framing":"how it is put / the angle taken (preserve the voice, do not normalise)",'
 '"reach":"what it grasps toward beyond what it nails",'
 '"surface_claims":["specific decisions/schemas/components AS STATED — these are UNVERIFIED AI assertions, not facts"]')
ADDONS = {
 "prose-design":   '"mechanisms":["how-it-works it describes"],"open_questions":["flagged unresolved"]',
 "schema-contract":'"defines":"what entity/contract","key_fields":["fields/columns/keys w/ type if stated"],"relations":["refs/FKs/links"]',
 "decision-card":  '"decision":"the question","options":["alternatives"],"chosen":"or open","rationale":"why"',
 "math-proof":     '"claim":"asserted","result":"proven|disproven|partial","self_contradictions":["where its own logic/tests break it"]',
 "template":       '"templates_what":"","slots":["fillable parts"]',
 "transcript":     '"ideas_raised":["thinking surfaced"],"threads_open":["left unfinished"]',
 "checklist":      '"criteria":["the items"],"gates_what":""',
}
# surveyed form (and long-tail) -> bucket
def bucket(form):
    f=(form or "").lower()
    if "log" in f or "status" in f or "chronicle" in f: return ("log", True)
    if "index" in f or "moc" in f or "pointer" in f: return ("index", True)
    if "schema" in f or "contract" in f or "spec" in f or "data-model" in f or "registry" in f: return ("schema-contract", False)
    if "decision" in f or "card" in f or "lens" in f or "review" in f: return ("decision-card", False)
    if "math" in f or "proof" in f: return ("math-proof", False)
    if "template" in f or "skeleton" in f or "query-template" in f: return ("template", False)
    if "transcript" in f or "dialogue" in f or "session" in f: return ("transcript", False)
    if "checklist" in f or "criteria" in f: return ("checklist", False)
    return ("prose-design", False)  # prose-design, mixed, research-*, design-*, doctrine, etc.
def schema_for(bk):
    add = ADDONS.get(bk, "")
    return "{" + PRIMARY + ("," + add if add else "") + "}"
