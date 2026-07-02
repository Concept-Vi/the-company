---
type: constitution
register: prescriptive
module: scope_grammar
aliases: ["scope_grammar — constitution", "the scope grammar registry"]
tags: [company, container, identity, scope-grammar, registry]
status: living
---

# scope_grammar/ — the ONE scope-grammar registry (④ L2-IDENTITY)

**What it is.** The single registered grammar for the authorization scope vocabulary — the missing
unifier the TENANCY organ study named (organ-studies/TENANCY.md §3.3): *"one registered grammar
`<domain>:<resource>:<verb>` — A's five verbs are the verb set; `write:leads` and `company:design:write`
both parse into it. The grammar is a registry, not convention."*

Before this, three grammars ran unparsed: A's `read/write/execute/admin/approve` + `write:leads`
(verb-first), C's `company:design:write` (verb-last), B's `permission='use'`. This registry is the ONE
verb vocabulary they all normalize into.

**The law it carries (constitution rule 8 + THE-CONTAINER law 3): vocabulary = files.** The scope
VERBS are gated, git-lifecycled files here; instance scope VALUES (a delegation's `scopes[]`, a
membership's `scopes[]`) are DB data. A verb with no file is a ghost — the parser FAILS LOUD.

## The row
Each `scope_grammar/<verb>.py` declares a module-level `SCOPE_VERB` dict — a registry ROW:
```python
SCOPE_VERB = {
    "verb": "write",              # MUST equal the file stem
    "means": "…",                 # one line: what this verb authorizes
    "reversible": False,          # a hint for the posture/ceiling layer (reversible → cheaper posture)
}
```
`verb` must equal the file name (addressable by file, mirroring mark_types/ · roles/).

## The parser (one door)
`contracts/scope_grammar.py` discovers this dir and parses ANY scope token into
`{verb, domain, resource, object, raw}`: it splits on `:`, finds the ONE segment that is a registered
verb (exactly one — 0 or >1 FAILS LOUD), and reads the segments before it as domain/resource and after
it as the object qualifier. So `read` → verb=read; `write:leads` → verb=write, object=leads;
`create:intent` → verb=create, object=intent; `company:design:write` → verb=write, domain=company,
resource=design. A scope whose verb is not registered here RAISES — registry-is-truth, never guess.

## Extend
Add a verb = drop a `scope_grammar/<verb>.py`. Reflect it here + in
`tests/identity_acceptance.py`. Never hand-list verbs in code — read them from this registry.
