# Conversational Glyphgraph — the CATALOGUE (the unbiased substrate)

> This catalogue is the **neutral, modular, growable substrate** distilled from the 3-wave / 20-area research
> (`../findings/AREA-1…20-*.md`). It exists so the understanding is **not diluted** by living only in a
> conversation or a synthesis. Tim's principle (2026-06-30): *separate the substrate from the views* — the
> atoms here are descriptive truth; `../LIVE-INSTRUMENT.md` is **one view** (a fuse-not-choose synthesis) OVER
> these atoms, never a replacement for them. Views may change or multiply; the substrate is not corrupted by them.

## The laws of this catalogue (do not break)
1. **Descriptive, never prescriptive.** An entry records *what is* (with file:line), NOT what should win, what's
   best, what's done, or what's canonical. No verdicts. No ranking. (Tim: assuming anything is canonical = auto-fail.)
2. **One thing per file.** Atomic. The catalogue grows by ADDING a file, never by bloating one. Modular by construction.
3. **File paths + concept, always.** Every entry carries its real `file:line` anchors AND the concept in plain terms.
4. **Mark evidence.** `Observed (file:line)` / `Inferred` / `External-prior-art` / `Cross-area`. Pattern-match ≠ verification.
5. **Never closure-form.** Open, provisional, growable (`status: open` by default). New findings = new/updated entries.
   Nothing here says "final." (Tim: nothing is final/right/done; there is always more.)
6. **Relations are typed, not ranked.** `instance-of`, `relates-to`, `duplicate-of`, `enacts` (a latent-glyphgraph
   enacts a concept), `gap-of`, `version-of`. Links name *kind of relation*, never priority.
7. **Duplications are kept, not resolved.** Every parallel version is its own entry with its UNIQUE QUALITY recorded.
   Fusion is a VIEW (the map), never done here — here they simply coexist as truth.

## The entry schema (frontmatter + body)
```
---
name: <kebab-id>                      # == filename stem
kind: capability | version | concept | latent-glyphgraph | gap | prior-art | open-decision
register: descriptive                 # always (this is a map of what is)
status: open                          # open | confirmed-observed  (never "final"/"done")
evidence: observed | inferred | external | mixed
file_refs: ["path:line", ...]         # real anchors (empty for pure concepts/prior-art)
relations:                            # typed, open vocabulary
  instance-of: [<capability-name>]
  duplicate-of: [<version-name>, ...]
  enacts: [<concept-name>, ...]
  relates-to: [<name>, ...]
source_areas: [A1, A7, ...]           # which findings this was distilled from
---
**What it is** — plain description.
**Unique quality** — what THIS version/thing uniquely carries (for versions: the part any fusion must keep).
**Notes** — open observations, honest gaps, things to verify. (No verdicts.)
```

## How to grow it
Add an `entries/<name>.md` following the schema; add its one-line to `INDEX.md` with its kind + relations.
A new research finding → a new entry or an updated one (in place, no v2). The map (`../LIVE-INSTRUMENT.md`)
is regenerated/edited as a VIEW when the substrate changes — the substrate leads, the view follows.

## Index
`INDEX.md` — every entry, its kind, its one-line, its typed relations (the one home / map of the catalogue).
