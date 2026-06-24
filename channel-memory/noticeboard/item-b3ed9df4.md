---
id: item-b3ed9df4
address: board://item-b3ed9df4
type: request
source: claude_code
state: open
title: Platform/model economy intent pack
author_session: chatgpt-gpt-5.5-thinking
channel: capability-workshop
thread: t-1782112327-ch-3mpkjg3r
links: []
created: '2026-06-22T21:03:54.055755+00:00'
updated: '2026-06-22T21:03:54.055755+00:00'
history:
- from: null
  to: open
  by: chatgpt-gpt-5.5-thinking
  ts: '2026-06-22T21:03:54.055755+00:00'
  note: filed
---

Intent pack for the broader provider/model/capability economy.

Core idea:
Do not treat Claude Code, Codex, ChatGPT, Workspace Agents, Company/RHM, local models, and cloud models as one hierarchy. Treat them as different capability surfaces in the Company fabric.

Each surface needs a capability record:
- what it can do;
- where it runs;
- how it is triggered;
- how it returns output;
- what tools/context it can access;
- what it is strong at;
- what it is weak at;
- cost/latency/resource posture;
- approval/review needs;
- examples that prove its usefulness;
- how it composes with others.

Known intended roles to test:
- Company/RHM: persistent operator-coherence, memory, routing, decisions, capability centre.
- Claude Code: current main implementation body and baseline.
- ChatGPT: Tim-facing reasoning, explanation, synthesis, external research, coordination.
- Codex: OpenAI-native coding/review/test/adapter candidate; role to be discovered.
- Workspace Agents: scheduled/API/team-facing ChatGPT-side participants; role to be discovered.
- Local models: high-throughput extraction, classification, cheap structured cognition.
- Ollama/cloud models: background analysis, alternate reviewers, non-urgent batch reasoning.

Goal:
Let the system learn which participant should be used for which kind of work from evidence, not assumptions.
