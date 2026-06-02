---
type: constitution
module: docs
aliases: ["docs — constitution"]
tags: [company, constitution, docs, meta]
governs: []
relates-to: ["[[Company Map]]", "[[Vault Conventions]]", "[[Company — read first]]"]
status: living
---

# docs/ — module constitution

**Is:** the repo's **meta-documentation** — notes *about* the repo as a knowledge space, as
opposed to the per-module constitutions (which live in each module's own `AGENTS.md`). The
home of cross-cutting conventions that don't belong to a single code module.
**Guarantees:** holds **convention + navigation** material, never code and never a duplicate
of a live source. Its canonical inhabitant is [[Vault Conventions]] — the definition of the
dual repo+vault form every `.md` obeys.
**Where new things go:** a new cross-cutting convention or repo-wide explainer = a note here
(frontmatter per [[Vault Conventions]]). A doc that belongs to one module goes in *that
module's* `AGENTS.md`, not here.
**To extend:** add a note; link it from [[Company Map]] so it's reachable.
**Seam:** referenced by [[Company — read first]] and [[Company Map]]; governs no code.
**Never:** put code here · duplicate a registry/spec that has a single source elsewhere ·
let a convention note drift from how the repo actually is (the [[Coherence Gate — Spec]] is
meant to catch that).
