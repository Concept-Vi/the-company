---
type: contract-journey
journey: which-corpus
summary: Recall something — but which of the three memories holds it? The cross-resource disambiguation between searchable knowledge, past-session history, and loaded instruction-context, with the routing logic between them.
status: building
relates-to: ["[[knowledge-corpus]]", "[[transcript]]", "[[claude-memory]]"]
---

# Journey: which memory answers this?

**Three distinct things all read as "memory", and routing to the wrong one returns a confident
wrong answer. This journey owns the F6 ambiguity class: pick the memory by the SHAPE of the
question, not by the word "remember".**

## The disambiguation this journey owns (V19's ambiguity class)
- **[[knowledge-corpus]] is RETRIEVABLE KNOWLEDGE** — embedded, semantically searchable
  reference corpora (the Claude Code Atlas, the platform-docs mirror, the company repo-
  exocortex). Ask it "how does X work" / "what does the doc say" / "where in the codebase".
  It is `building` (proven-by-use over the substrate + company MCP faces). Answers carry a
  cited, dereferenceable source.
- **[[transcript]] is PAST-SESSION HISTORY** — the filtered, redacted markdown of what
  sessions actually DID. Ask it "what did a past session decide" / "find the session that
  edited file Y". The corpus exists on disk (1,040 md); its SEARCH is `planned` (vault not yet
  registered) — interim is `session.list q=` + direct file reads.
- **[[claude-memory]] is LOADED INSTRUCTION-CONTEXT** — the CLAUDE.md scope stack + Claude's
  auto-memory, loaded at session start to STEER behavior. Ask it "what are my conventions" /
  "what is Claude remembering about this repo". It is `planned` as a company surface; interim
  is the built-in `/memory` + direct reads of the scope paths.

## Routing logic (the decision a consumer makes first)
1. **Is the answer a FACT about how something works (Claude Code, the API, the codebase)?**
   → [[knowledge-corpus#op: knowledge-corpus.search]]. Pick the vault by domain: Claude Code
   behavior → `claude-code-atlas`; Anthropic API/platform → `claude-platform-docs`; the company
   source → the company `corpus` space `repo`.
2. **Is the answer something that HAPPENED in a prior conversation/session?**
   → [[transcript#op: transcript.search]] (planned) / interim file reads over
   `~/corpora/claude-sessions/`.
3. **Is the answer a STANDING INSTRUCTION/preference that should shape behavior?**
   → [[claude-memory#op: claude-memory.list]] for what's loaded; edit via
   [[claude-memory#op: claude-memory.update]] / the remember/forget acts.

## Ordered ops (the common "I need to recall X" flow)
1. Classify the question by the routing logic above (the load-bearing step — most wrong answers
   are routing errors, not search errors).
2. **[[knowledge-corpus#op: knowledge-corpus.list]]** — if routing to knowledge, confirm the
   target corpus is indexed (files/chunks > 0) before searching.
3. **[[knowledge-corpus#op: knowledge-corpus.search]]** — search the chosen vault; follow each
   hit's `source` address to the document for the full context.
4. If the search returns only off-topic chunks, that is a `drop` (append to
   `coverage/drops.jsonl`), AND a re-route signal: the answer may live in a different one of the
   three memories — go back to step 1.

## Pass shape
PASSES when the question is routed to the correct memory AND that memory returns an answer whose
source dereferences to a real document containing it (knowledge-corpus), or the correct interim
path is taken with the planned op honestly flagged (transcript-search, claude-memory). A
confident answer from the WRONG memory is a `fail`, not a pass — the routing IS the test.
