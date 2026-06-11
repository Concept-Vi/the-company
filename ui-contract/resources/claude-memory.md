---
type: contract-entry
resource: claude-memory
summary: The persistent-instruction data model a UI renders and edits — the CLAUDE.md scope hierarchy (managed-policy → user → project → local, loaded broadest-to-specific) plus auto-memory (Claude-written MEMORY.md + topic files, per-repo). Today a filesystem data model with NO company endpoint; the surface is planned, the gap named.
schemes: []
status: planned
relates-to: ["[[transcript]]", "[[knowledge-corpus]]", "[[cost-usage]]"]
---

# Resource: claude-memory

## Identity
**A memory artifact is identified by its SCOPE + on-disk path: a CLAUDE.md file at one of the
fixed scope locations, or an auto-memory file under a project's memory directory; there is no
opaque id and no address scheme — the path IS the identity, and the scope determines load
order and ownership.**
This resource contracts the DATA MODEL Claude Code maintains on the local filesystem so a UI
can render and edit it. It is `planned`: NO company endpoint reads or writes CLAUDE.md/auto-
memory today (verified — `grep -rilE 'claude_md|autoMemory|MEMORY\.md' runtime/ mcp_face/ ops/`
returns nothing in `~/company`). The honest interim path is a direct filesystem read/edit of
the paths below (they are plain markdown, owned by the operator).
Source of every fact here: the Claude Code Atlas + docs mirror — search it via
[[knowledge-corpus#op: knowledge-corpus.search]] (`vault: claude-code-atlas`). Primary cites:
`Docs/claude-code/memory.md`, `Docs/claude-code/glossary.md`, the research note `Memory
Systems.md`.

## Representation
**Two complementary systems, both loaded at every session start, both treated as CONTEXT not
enforced config: CLAUDE.md files (operator-written instructions, scope-stacked, loaded in
full) and auto-memory (Claude-written learnings, per-repo, the MEMORY.md index capped at the
first 200 lines or 25 KB).** (Source: `Docs/claude-code/memory.md#claudemd-vs-auto-memory`.)

### CLAUDE.md scope hierarchy — load order broadest → most-specific
A specific scope appears in context AFTER (and so refines) a broader one. (Source:
`Docs/claude-code/memory.md#choose-where-to-put-claudemd-files`.)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/claude-memory.claude-md-file",
  "type": "object",
  "required": ["scope", "path", "writer"],
  "properties": {
    "scope":  { "enum": ["managed-policy", "user", "project", "local", "subdir"],
                "description": "load order: managed-policy → user → project → local; subdir files load ON DEMAND when Claude reads files in that subdir" },
    "path":   { "type": "string",
                "description": "managed-policy: /etc/claude-code/CLAUDE.md (Linux/WSL), /Library/Application Support/ClaudeCode/CLAUDE.md (macOS), C:\\Program Files\\ClaudeCode\\CLAUDE.md (Windows) · user: ~/.claude/CLAUDE.md · project: ./CLAUDE.md or ./.claude/CLAUDE.md · local: ./CLAUDE.local.md (gitignore it)" },
    "writer": { "const": "operator", "description": "you write CLAUDE.md; Claude writes auto-memory (the other system)" },
    "loaded": { "enum": ["full-at-launch", "on-demand"],
                "description": "hierarchy-above-cwd files load in FULL at launch; subdir CLAUDE.md/CLAUDE.local.md load on demand when Claude reads matching files" },
    "shared_with": { "type": "string", "description": "managed-policy=org · user=just you (all projects) · project=team via VCS · local=just you (this project)" } } }
```
Two adjacent CLAUDE.md mechanisms a UI must surface:
- **Imports** — `@path/to/file.md` anywhere in a CLAUDE.md expands that file inline at launch;
  relative paths resolve relative to the importing file (not cwd); recursion max depth 4;
  `~/` and absolute paths allowed. Imports do NOT save tokens (imported content loads in full).
  (Source: `Docs/claude-code/memory.md#import-additional-files`.)
- **Rules** — modular files in `.claude/rules/` loaded alongside CLAUDE.md; a rule with YAML
  `paths:` frontmatter is path-scoped (loads only when Claude reads a matching file).
  `claudeMdExcludes` (settings) skips other teams' CLAUDE.md in monorepos.
  (Source: `Docs/claude-code/glossary.md#rules`, `memory.md`.)

### Auto-memory data model — Claude-written, per-repository
(Source: `Docs/claude-code/memory.md#auto-memory/how-it-works`, `glossary.md#auto-memory`.)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/claude-memory.auto-memory-dir",
  "type": "object",
  "required": ["dir", "index", "topic_files"],
  "properties": {
    "dir":   { "type": "string", "description": "default ~/.claude/projects/<project>/memory/ — <project> derived from the git repo root, so ALL worktrees + subdirs of one repo SHARE one memory dir; outside a git repo the project root is used. Overridable via the autoMemoryDirectory setting (any scope; absolute or ~/; project-scope honored only after the workspace-trust dialog)" },
    "index": { "type": "object", "required": ["file", "load_limit"],
               "properties": {
                 "file":       { "const": "MEMORY.md", "description": "the concise index, loaded at every session start" },
                 "load_limit": { "const": "first 200 lines OR 25 KB, whichever hits first — content beyond is NOT loaded at start (this is the limit Tim's MEMORY.md is currently AT — see reality column)" } } },
    "topic_files": { "type": "array",
                     "description": "e.g. debugging.md, api-conventions.md — NOT loaded at startup; Claude reads them on demand. MEMORY.md indexes what's stored where",
                     "items": { "type": "string" } },
    "enabled": { "type": "boolean", "description": "toggle via /memory or CLAUDE_CODE_DISABLE_AUTO_MEMORY=1; subagents can keep their OWN auto-memory (sub-agents#enable-persistent-memory)" } } }
```
| property | reality (measured on Tim's install, 2026-06-12) |
|---|---|
| auto-memory dir | `/home/tim/.claude/projects/-home-tim/memory/` (the `<project>` segment is the cwd-derived hash, here `-home-tim`) |
| MEMORY.md size | 25,829 bytes / 109 lines — OVER the 25 KB load cap: only the first 25 KB loads at session start (this exact condition is live in Tim's MEMORY.md, which carries a self-warning to shorten index entries) |
| topic files | 113 markdown files (`feedback-*.md`, `project-*.md`, …) — none auto-load; read on demand |
| CLAUDE.md (user) | `/home/tim/.claude/CLAUDE.md` present and loaded in full every session (this build's own instruction source) |
| writer split | MEMORY.md + topic files = Claude-written; CLAUDE.md = operator-written — a UI must NOT conflate the two writers |

## State model
**State model: stateless.** (Memory files are plain markdown — read, edited, deleted at any
time by the operator or by Claude during a session. There is no lifecycle FSM; the only
"transition" is a session-start LOAD, and that is a property of the session, not of the file.)

## Caller
**No fabric identity applies — these are local files on the operator's machine. The CALLER
distinction that matters is the WRITER: the operator owns CLAUDE.md (all scopes); Claude Code
owns auto-memory (it writes MEMORY.md/topic files during a session; you see "Writing memory" /
"Recalled memory" in the interface). Auto-memory is machine-local and NOT shared across
machines or cloud environments — a UI rendering it must scope to THIS machine.**

## Operations

## op: claude-memory.list
**`claude-memory.list` is the loaded-context inventory: every CLAUDE.md, CLAUDE.local.md, and
rules file active in a session plus the auto-memory directory — the exact data the `/memory`
command renders, and what a UI mirrors to show "what is Claude actually reading right now".**
```contract:op
op: claude-memory.list
resource: claude-memory
kind: list
status: planned
direction: outbound
atlas: [CC-23.3]
tasks:
  - phrase: "what CLAUDE.md and memory files are loaded in this session"
  - phrase: "show the memory hierarchy"
  - alias: "what is Claude remembering"
  - alias: "list my CLAUDE.md files"
bindings:
  - { kind: cli, command: "claude /memory   (the interactive command — lists loaded CLAUDE.md/CLAUDE.local.md/rules, links the auto-memory folder, toggles auto-memory)", transport: cli-local, exposure: "exposure.json#cli-local", status: planned, note: "this is a Claude Code BUILT-IN slash command, NOT a company `company ...` route — the company exposes NO programmatic list of loaded memory; interim = the built-in /memory or a direct read of the scope paths in Representation" }
liveness: snapshot
live-twin: "none — static (a point-in-time view of loaded context)"
emits: []
verification:
  no-company-endpoint: {state: unverified, note: "GAP (named): no company list endpoint exists; /memory is Claude Code's own interactive UI, not machine-readable. A company surface would walk the scope paths + the autoMemoryDirectory and return the data model above — an F10.1 gap-adoption candidate"}
```
Interim honest path: read the scope paths directly (Representation) and the auto-memory dir
(`~/.claude/projects/<project>/memory/MEMORY.md` + topic files) — all plain markdown, granted.
The `InstructionsLoaded` hook logs exactly which instruction files load, when, and why — the
machine-readable provenance a programmatic list would build on. (Source:
`Docs/claude-code/memory.md#troubleshoot-memory-issues`.)
Adjacent: [[claude-memory#op: claude-memory.act]] (remember/forget), [[claude-memory#op:
claude-memory.update]] (edit a file).

## op: claude-memory.update
**`claude-memory.update` is the direct edit of one memory file — add a convention to CLAUDE.md,
trim a stale MEMORY.md, fix a rule — the operator-write half of the model; planned as a company
op, today a plain file edit.**
```contract:op
op: claude-memory.update
resource: claude-memory
kind: update
status: planned
direction: outbound
atlas: [CC-23.4]
tasks:
  - phrase: "add a convention to CLAUDE.md"
  - phrase: "trim my MEMORY.md index"
  - alias: "edit a memory file"
  - alias: "fix a project rule"
bindings:
  - { kind: cli, command: "(edit the file)   — open via `claude /memory` then select, or edit the scope path directly", transport: cli-local, exposure: "exposure.json#cli-local", status: planned, note: "NO company endpoint; CLAUDE.md/rules/memory files are operator-edited markdown. A company update op would be a guarded file-write to a scope-validated path" }
liveness: none
emits: []
consequences:
  - when: "a CLAUDE.md/rule/MEMORY.md file is edited"
    expect: []
    evidence: "filesystem snapshot of the edited path; the change takes effect at the NEXT session load (CLAUDE.md is re-read fresh after compaction too) — there is no live reload event"
correlate: []
verification:
  no-company-endpoint: {state: unverified, note: "GAP (named): edits land via the operator's editor / a future guarded company write op; F10.1 gap-adoption candidate. Scope validation (refuse a write to a path outside the known scopes) is the load-bearing safety the op must carry"}
```
Adjacent: [[claude-memory#op: claude-memory.act]] (Claude-driven remember/forget),
[[claude-memory#op: claude-memory.list]] (what's loaded).

## op: claude-memory.act
**`claude-memory.act` is the Claude-driven memory verbs — `remember` (save a learning to
auto-memory or, on request, append to CLAUDE.md) and `forget` (trim/delete) — the named acts
that distinguish "Claude writes this for itself" from the operator's direct edit.**
```contract:op
op: claude-memory.act
resource: claude-memory
kind: act
status: planned
direction: outbound
atlas: [CC-23.5]
tasks:
  - phrase: "remember that the API tests need a local Redis"
    params: {act: remember, target: auto-memory}
  - phrase: "add this to CLAUDE.md"
    params: {act: remember, target: claude-md}
  - phrase: "forget the stale build-command note"
    params: {act: forget}
  - alias: "save this preference"
  - alias: "stop remembering this"
named-acts: [remember, forget]
bindings:
  - { kind: cli, command: "(conversational)   — ask Claude 'remember X' (→ auto-memory) or 'add X to CLAUDE.md' (→ CLAUDE.md); 'forget'/edit via /memory", transport: cli-local, exposure: "exposure.json#cli-local", status: planned, note: "these are CONVERSATIONAL behaviors of Claude Code, not a company API. A company act op would target the data model above. NOTE: writing to auto-memory is the agentic-write class — gate per the path-of-least-resistance + consent laws" }
liveness: none
emits: []
consequences:
  - when: "act=remember, target=auto-memory"
    expect: []
    evidence: "a new/updated entry in ~/.claude/projects/<project>/memory/ (MEMORY.md index + possibly a topic file); the 'Writing memory' interface signal is the live indicator"
  - when: "act=remember, target=claude-md"
    expect: []
    evidence: "an appended instruction in the chosen-scope CLAUDE.md (the operator's, by request)"
correlate: []
verification:
  no-company-endpoint: {state: unverified, note: "GAP (named): remember/forget are Claude Code conversational behaviors; no company act op exists. F10.1 gap-adoption candidate"}
```
Where to put it: CLAUDE.md for "always do X" rules Claude should hold every session; a skill
or a path-scoped rule for multi-step or single-area procedures; a hook for "must run at point
X regardless" (memory is context, not enforcement — to BLOCK an action use a PreToolUse hook).
(Source: `Docs/claude-code/memory.md`.)
Adjacent: [[claude-memory#op: claude-memory.update]] (operator's direct edit),
[[knowledge-corpus]] (the SEPARATE searchable-knowledge capability — memory is per-session
loaded context; knowledge-corpus is on-demand semantic retrieval).

## Errors
**The failure modes are scope and trust, not transport: an edit to an unknown/invalid scope
path is refused (a memory file outside the known scopes is not memory); a project-scope
`autoMemoryDirectory` is honored only after the workspace-trust dialog; an oversized MEMORY.md
does not error — it silently loads only its first 25 KB / 200 lines, which a UI must surface
as a visible truncation, never hide.**
```contract:error
code: claude-memory.invalid-scope | retryable: false
when: a write targets a path that is not a recognized CLAUDE.md / rules / auto-memory scope
teach: "Valid scopes are in [[claude-memory#Representation]]. A memory edit must land at a known scope path; arbitrary paths are not loaded as memory and writing there is a no-op for Claude's context."
```
```contract:error
code: claude-memory.untrusted-workspace | retryable: false
when: a project-scoped autoMemoryDirectory (or hooks) is set but the workspace-trust dialog was not accepted
teach: "Accept the workspace trust dialog for this folder (the same gate that governs hooks), or set autoMemoryDirectory at user scope. Until trusted, the project-scope override is not honored."
```

## Links
**No address scheme — paths are the identity. The DIRECTIONAL relations a UI renders: a
CLAUDE.md `@import` edge points to another markdown file (recursion ≤4); a `.claude/rules/`
file with `paths:` frontmatter edges to the file-globs that trigger it; the auto-memory
MEMORY.md index edges to its topic files. These three edge-types ARE the memory graph. The
transcript corpus ([[transcript]]) is a DIFFERENT memory — durable history of past sessions,
not loaded-context instructions; [[knowledge-corpus]] is on-demand retrievable knowledge.
Three distinct memories, one lane, kept distinct ([[which-corpus]] disambiguates corpus from
transcript; this Links note disambiguates instruction-memory from both).**
