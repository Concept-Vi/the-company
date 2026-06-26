# BEAT 1 — wire forms/lifters into the Company capture path (PROPOSED DIFF, for lead/composition review)

*Recall-apex build, Beat 1, built INTO the centre (per the centre-law). Status: PROPOSED — drafted by recollection (ch-83e2cque) for review+apply by the core-seam owner (suite.py = lead's R13 lane; forms = composition's). NOT applied. Closes R9 (forms/lifters built-but-unwired) AND gives recollection's DISTILL its file-type-aware output shape — one wire, both served (union-aid).*

## THE GAP (verified, R9)
`Suite.ingest_paths` (runtime/suite.py ~10549) fans the SINGLE `repo_digest` role over EVERY file flat — same deep digest for a decision-note and a changelog. The `forms`/`lifters` registries are discovered on `self` (suite.py:332-337) but NOTHING in the capture path calls them. Result: flat {output, kind}; deep-capture burned on bookkeeping; no structure on the record. The richer intended shape (file-type → stage/policy + lifter structure) exists but is unwired.

## THE WIRE (proposed — replaces the flat fan at suite.py ~10549 `units = [...]; res = _cog.run_items(rd, units, ...)`)
```python
# BEAT-1: route each file by FORM (file-type → output-shape), attach LIFTER structure.
# REUSE: self.form_registry + self.lifter_registry already discovered (suite.py:332-337). No new machinery.
for f in files:
    form = self.form_registry.route(f["text"])           # the effort-router (a deterministic READ)
    f["form"], f["stage"], f["policy"] = form.id, form.stage, form.policy
    f["structure"] = {lt.id: lt.extract(f["text"]) for lt in self.lifter_registry}  # blocks/frontmatter/links

deep   = [f for f in files if f["stage"] == "deep"]        # decisions/prose → the heavy 4B digest
cheap  = [f for f in files if f["stage"] != "deep"]        # logs/registries/MoCs → structure, not substance

# DEEP: the repo_digest deep fan, carrying the form's generation-policy (the O2 ladder consumes `policy`
#       at cognition.py:334). One run_items per distinct policy (or pass per-unit policy if run_items grows it).
deep_units = [f"FILE {f['path']}:\n\n{f['text']}" for f in deep]
deep_res   = _cog.run_items(rd, deep_units, self.store, turn_id=f"ingest-{session}", max_tokens=200)
#       ^ POLICY THREADING is the one open seam — see "TO CONFIRM" below.

# CHEAP: NO model — the record's output is lifter-derived (frontmatter + heading-spine + link-count).
#       "structure not substance" → don't spend the 4B on a changelog.
def _cheap_output(f):
    s = f["structure"]
    return {"summary": f"{f['form']}: {len(s.get('blocks',[]))} sections, {len(s.get('links',[]))} links",
            "frontmatter": s.get("frontmatter"), "headings": s.get("blocks")}

records = []
# deep records (from deep_res.resolved, as today) + cheap records (_cheap_output) — both carry f["form"],
# f["stage"], f["structure"] on the record alongside output/kind/projection/source_hash.
```
Every record now carries: `form`, `stage`, `structure` (lifter output) — richer than flat {output, kind}.

## REUSE / NO-REPEAT
- `self.form_registry.route()` + `self.lifter_registry[*].extract()` — already built + discovered. Zero new code in forms/lifters; this is purely the CALL-SITE wire.
- The generation_policy ladder (cognition.py:334) already consumes `policy` — the form just supplies it.

## ★ TO CONFIRM before apply (the one real seam)
- **Policy threading:** does `_cog.run_items(role, units, …)` accept a `policy=` (or per-unit policy)? R9 saw `policy` consumed in run_role's O2 path (cognition.py:334) — confirm the path from `run_items` → `run_role(policy=…)`. If run_items doesn't thread policy yet, that's a tiny additive param (lead's core lane) OR group the deep fan by policy and call run_items per group. **Flag for the lead — this is the core-seam.**
- `lifter.extract(text)` signature — confirm it's `(text) -> value` (the registry's `_extract`).

## VERIFICATION (by use, both faces)
- FUNCTION: re-ingest (force) a DECISION file → deep digest + structure attached; a LOG/changelog → cheap lifter-output, NO 4B call (check no digest cost); confirm records carry form/stage/structure. Then `corpus(op='query')` still returns them.
- Coverage-ledger unchanged ({walked, captured, remaining}).
- Closes R9: re-run shows forms/lifters firing in the coverage path.

## CO-SCOPE / WHO APPLIES
- `runtime/suite.py` ingest_paths = the lead's core (R13 byte-identical for run_swarm; this is ingest_paths, adjacent but core-class) → **propose-diff, lead applies or clears me.**
- `forms/` definitions (which file-types → deep vs legibility) = composition's lane → composition confirms the form set is right for the corpus.
- recollection (me): owns this wire's design + the verification; the DISTILL stage of the recall build rides it.

## WHY THIS IS BEAT 1 (into the centre)
It's additive, low-risk, co-owned, closes a standing Company gap (R9), and establishes the file-type-aware output shape that DISTILL (and every downstream recall stage) depends on. Building it INTO the centre (not the recollection island) = the centre improves to hold the typed-distill; recollection's L2 design is absorbed here.
