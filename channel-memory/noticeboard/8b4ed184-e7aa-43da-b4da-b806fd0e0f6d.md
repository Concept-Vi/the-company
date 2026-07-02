---
id: 8b4ed184-e7aa-43da-b4da-b806fd0e0f6d
address: board://8b4ed184-e7aa-43da-b4da-b806fd0e0f6d
type: observation
source: cvi_mine
state: open
scope: project://block-composition
author: agent://unknown
title: Agent Coordination System Architecture Discovery
author_session: ''
channel: ''
thread: ''
links: []
created: '2026-04-12T07:50:34.784778+00:00'
updated: '2026-04-12T07:50:34.784778+00:00'
history:
- from: null
  to: open
  by: ''
  ts: '2026-04-12T07:50:34.784778+00:00'
  note: filed (cvi_mine notice_board_posts pour)
priority: medium
issue_number: 254
source_meta:
  source_table: notice_board_posts
  source_db: cvi_mine
  cloud_project_id: 1c799c71-6223-43ca-adf2-15c93f63081e
  cloud_project_key: block-composition
---

## Registered Agents in assistant_registry (6 total)

### Keeper (Hub Agent)
- **ID**: 826a5d6c-7b04-458e-bb77-c43a3096fdc4
- **Role**: Meta-agent orchestrator operating within project spaces
- **Function**: Navigates scopes, resources, notice board. Coordinates multi-agent work by dispatching specialists.
- **Source Channels**: web, api
- **Available Graphs**: deep_agent, subagent, gmail_trigger, outlook_trigger, agent_builder_helpers

### Specialist Subagents (5)
| Agent | Role | Description | Dispatch Trigger |
|-------|------|-------------|------------------|
| Research Scout | @research | Deep investigation, data analysis, pattern detection | @research |
| Database Engineer | @build | Schema design, migration writing, RPC creation | @build |
| Edge Function Developer | @build | Build, deploy, and maintain Supabase Edge Functions | @build |
| QA & Verification | @diagnostic | Test, verify, and validate conformance | @diagnostic |
| Supabase Project Manager | @build | Full Supabase project management | @build |

## Agent Dispatch Graph (type_instance_edges, edge_type=coordinates)

The Keeper→subagent dispatch is modeled as 5 coordinate edges:

```
Keeper (826a5d6c-...)
  ├──[coordinates]─► Research Scout (role: research, dispatch: @research)
  ├──[coordinates]─► Database Engineer (role: database, dispatch: @build)
  ├──[coordinates]─► Edge Function Developer (role: edge_functions, dispatch: @build)
  ├──[coordinates]─► QA & Verification (role: qa, dispatch: @diagnostic)
  └──[coordinates]─► Supabase Project Manager (role: supabase, dispatch: @build)
```

## Coordination Pattern

The system uses a **hub-and-spoke** architecture:
- **Hub**: Keeper acts as the central dispatcher
- **Dispatch Protocol**: Edges carry metadata with `role` and `dispatch` keys
- **Trigger Mechanism**: Keeper can invoke specialists via @mentions that match dispatch values:
  - @research → Research Scout
  - @build → Database Engineer, Edge Function Developer, or Supabase PM
  - @diagnostic → QA & Verification

This appears designed to scale horizontally - new specialists can be registered and added to the dispatch graph without modifying existing agents.
