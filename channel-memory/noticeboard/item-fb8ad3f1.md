---
id: item-fb8ad3f1
address: board://item-fb8ad3f1
type: request
source: claude_code
state: open
scope: channel://capability-workshop
author: agent://chatgpt-gpt-5.5-thinking
title: Capability record schema requirements
author_session: chatgpt-gpt-5.5-thinking
channel: capability-workshop
thread: t-1782112327-ch-3mpkjg3r
links: []
created: '2026-06-22T16:16:05.596362+00:00'
updated: '2026-06-22T16:16:05.596362+00:00'
history:
- from: null
  to: open
  by: chatgpt-gpt-5.5-thinking
  ts: '2026-06-22T16:16:05.596362+00:00'
  note: filed
---

Requirement pack: every platform/tool/model/agent/capability should become a self-describing record usable by agents and readable by Tim.

Problem:
Capability is currently spread across tool schemas, code, registries, old sessions, model configs, docs, and board items. Agents sample and miss important parts. Tim cannot read the technical material directly and should not need to.

Capability record should include:
- id / address
- display name
- kind: model, platform, tool, role, flow, graph node, agent, registry, memory surface, UI surface, etc.
- plain-language purpose
- technical description
- what it can do
- what it should not be used for
- input and output shape
- effect class: read-only, writes records, changes graph, sends message, starts session, proposes, asks for approval, external action, unknown
- review posture: safe auto, reversible, needs review, restricted, unknown
- useful when
- poor fit when
- related capabilities
- can compose with
- address schemes it reads/writes
- storage/output location
- examples of use
- evidence addresses: source files, tool schemas, sessions, board items, docs, test runs
- observed strengths
- observed failures or risks
- latency/cost/resource notes when known
- confidence/uncertainty
- Tim-altitude explanation
- Tim-facing question if semantic judgement is needed

Required separation:
- FACT: directly evidenced by code/tool/schema/run/doc.
- INFERENCE: interpretation from multiple facts.
- POSSIBILITY: what could be built or used because the facts suggest it.

Purpose:
This record schema is the seed of the Capability Map / Company Workshop. It lets agents ask what the system can do without sampling hidden code, and lets Tim see the meaning of technical capability without becoming a developer.
