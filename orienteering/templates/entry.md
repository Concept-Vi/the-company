---
type: terrain-entry
register: descriptive
aliases: ["<name>"]              # the vault link target for this entry
tags: []                         # cross-cutting themes only (#voice #model #memory #embedding #fabric #mcp #control #image)
status: unconfirmed              # CONFIRMED-only field — leave `unconfirmed` unless Tim has confirmed a lifecycle
coverage: { files_read: 0, files_total: 0, last_read: 2026-06-26 }
relation:    # company | external | connected | candidate | resource   (orbit membership)
kind:        # (external only) work | data | config | engine
path:        # absolute, always
created:     # YYYY-MM-DD (earliest evidence)
last_active: # YYYY-MM-DD (latest evidence — a fact from mtime, not a judgment)
size:
git_remote: none
secrets: false
move_intent: none               # none | into-company | delete | archive | done
# typed relations (zero or more; key = relation kind, values = [[aliases]]). Examples:
relates-to: []
# indexed-by: ["[[…]]"]   launched-by: ["[[…]]"]   depends-on: ["[[…]]"]
# data-of: ["[[…]]"]      derived-from: ["[[…]]"]  aimed-at: ["[[…]]"]   prospected-for: ["[[…]]"]
---

# {{name}}

## What it is
<plain-meaning + evidence cited>

## How it works
<entry points / services / what runs — if anything>

## What it connects to
<the relations, in prose; the typed link fields above carry them as graph edges>

## When / where
<created, last active, path, size>

## Coverage / evidence
<files actually read vs exist, when last read, commands run, caveats>
