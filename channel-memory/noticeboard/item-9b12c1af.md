---
id: item-9b12c1af
address: board://item-9b12c1af
type: idea
source: claude_code
state: captured
title: Provider/Platform Registry lane — archaeology-grounded charter (extend System
  A · redesign System B · integrate)
author_session: ch-3mpkjg3r
channel: provider-registry
thread: ''
links: []
created: '2026-06-22T09:36:40.605649+00:00'
updated: '2026-06-22T09:36:40.605649+00:00'
history:
- from: null
  to: captured
  by: ch-3mpkjg3r
  ts: '2026-06-22T09:36:40.605649+00:00'
  note: filed
---

CHARTER for the provider/platform-registry lane (Tim's direction, composed with ChatGPT; LEAD as touchpoint). Grounded in a READ-ONLY archaeology inventory of the existing registries (evidence-not-authority) — NOT assumptions.

FRAME (Tim): existing code is EVIDENCE, not authority. The archaeology decides per-finding: extend / redesign / consolidate / integrate. The build method is archaeology + capability inventory + consolidation, not spec-following.

ARCHAEOLOGY FINDING — there are TWO ORTHOGONAL registry systems today (not one):
• SYSTEM A — Platform + Capability registries (introspection/registry.py · platforms.py · contracts/platform_entry.py + capability_entry.py · platforms/*.py file-discovered Pydantic rows). PRODUCTION-GRADE. Already registers Claude Code (instance #1: flags/tools/slash/mcp_tool/permissions/posture/resource-governance) AND gh-cli (proves the generalization is real). Captures: identity · executable-locator · discovery-sources · invocation-kind · permission-model · tool-surface · tool-server-wiring · resource-governance · projection-targets. cap:// resolves CapabilityEntry rows. State: live, in-memory cached singleton (disk cache not yet built); claude-code live-verify queued (C-REG-1).
• SYSTEM B — the model catalog (ops/services.json + ops/model_capabilities.json + suite.py:capability_providers()). INCOMPLETE + NOT a registry pattern (hand-maintained JSON, no file-discovery / no self-registration / no create_*). Captures intrinsic model capabilities (provides/thinking/json/tool_calling). Adding a model = hand-edit 2 files + hope capability_providers() wires it.

THE 3-MOVE SHAPE (corrects both "build one new registry" AND "just extend the existing"):
1. EXTEND System A with new platform rows (ChatGPT · Codex · Ollama-cloud · Workspace-Agents · Claude-Design · MCP-servers) — additive PlatformEntry, start from the Claude-Code row as template. (Codex needs a 'rest'/app invocation adapter — UNBUILT, surfaces as a gap.)
2. REDESIGN System B into a file-discovered provider-registry (mirror RoleRegistry: providers/*.py + PROVIDER sentinel + create_provider + fail-loud).
3. WIRE the A↔B integration (a platform PROVIDES models; the join is currently invisible/manual).

CAPTURE GAPS (none captured today, in either — the additive fields the lane designs): costs · latency SLOs · safety posture (beyond locked/hazard/consent) · strengths/weaknesses · observed-failures · routing-hints · doc-links · triggers/activation-rules.

cap:// OVERLOAD: platform-surface (live) vs an aspirational, UNWIRED model-binding (minds.py kind=model) — resolve with a distinct scheme (model://) for models, keep cap:// for surfaces.

LANE COMPOSITION (proposed, lean — flows/passes over standing sessions): Registry Archaeologist = the read-only inventory PASS (DONE — this finding) · Schema/Type Integrator = proposes the System-B redesign + the A-extension template (a fresh session) · Platform Examiner = start with the 2 already-registered (Claude Code, Company/RHM) as template, then ChatGPT/Codex as first new entries · Consolidation Guard = an adversarial-verify LENS on each proposal (not a standing session) · Codex Probe = LAST, after the frame is set. ONE fresh driver session; clones only for deliberate perspective; channel `provider-registry` stays provisional (don't rename before the home is known). Full inventory report: the registry-archaeology agent output (this session).

OPEN DIRECTION CALLS FOR TIM (ChatGPT to carry): extend-A confirmed? · redesign-B as a file-discovered registry? · the capture-gap field set? · model:// vs cap:// for models?
