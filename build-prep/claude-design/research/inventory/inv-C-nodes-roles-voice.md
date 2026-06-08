---
type: research
source: fast-inventory
region: nodes/ + roles/ + mcp_face/ + voice/
scan_date: 2026-06-08
method: coverage (not deep)
---

# Inventory: Nodes, Roles, MCP Face, and Voice Stack

Fast coverage scan of the node-types, cognition roles, agent interface, and voice subsystems.

---

## Folder Structure

### mcp_face/
```
mcp_face/
  AGENTS.md              (constitution)
  server.py              (FastMCP agent face — C7)
```

### nodes/
```
nodes/
  AGENTS.md              (constitution — node-type registry)
  ask.py                 (query-answering node — first-purpose)
  codebase.py            (content node: repo reader)
  constant.py            (skeleton: constant value)
  embed.py               (text → Vector via fabric)
  gate.py                (conditional routing)
  join.py                (fan-in skeleton)
  llm.py                 (AI process node — S6/C2)
  model_of_tim.py        (explicit Tim model — context escalation)
  pair.py                (non-commutative fan-in)
  portal.py              (artefact multi-view — context-13)
  retrieve.py            (Vector + corpus → top-K)
  rhm_mode.py            (RHM presence as a node)
  similarity.py          (Vector cosine similarity)
  titlecase.py           (skeleton: text transform)
  uppercase.py           (skeleton: text transform)
  wordcount.py           (skeleton: text metric)
  __pycache__/
```

### roles/
```
roles/
  AGENTS.md              (constitution — role registry)
  check.py               (CHECK role — listening cast C2.3)
  connect.py             (CONNECT role — listening cast C2.3)
  focus.py               (FOCUS role — listening cast C2.3)
  ground.py              (GROUND role — listening cast C2.3)
  judge.py               (JUDGE role — role #0, finished-thought C2.2)
  recall.py              (RECALL role — listening cast C2.3)
  verify_jury.py         (VERIFY_JURY role — jury role C2.4)
  voice.py               (VOICE role — listening cast C2.3)
  __pycache__/
```

### voice/
```
voice/
  AGENTS.md              (constitution — voice subsystem)
  FROM-OPS-CLI-SESSION.md (session notes)
  lifecycle.py           (voice service load/unload/status)
  loop.py                (voice turn loop integration)
  personas.py            (voice persona definitions)
  speakable.py           (text → natural-speech transform layer)
  stt.py                 (swappable speech-to-text provider)
  tts_service.py         (Kokoro local text-to-speech)
  trial_manifest.json    (engine trial manifest)
  
  ears/                  (GPU STT engines)
    AGENTS.md            (ears constitution)
    REQUIREMENTS.md
    _stt_service.py      (shared HTTP shell)
    canary.py            (NVIDIA Canary-Qwen 2.5B → :2032)
    granite.py           (IBM Granite Speech 4.0 1B → :2033)
    parakeet.py          (NVIDIA Parakeet-TDT 0.6B v3 → :2031)
    __pycache__/
  
  engines/               (trial TTS engines — 5 total)
    AGENTS.md            (engines constitution)
    REQUIREMENTS.md
    _service.py          (shared HTTP shell)
    chatterbox.py        (Chatterbox-TTS → :4124)
    cosyvoice.py         (CosyVoice2 → :4126)
    orpheus.py           (Orpheus-TTS → :4125)
    qwen3tts.py          (Qwen3-TTS VoiceDesign → :4128)
    xtts.py              (XTTS-v2 Coqui → :4127)
    __pycache__/
  
  ops/                   (operations + systemd units)
    README.md
    make_reference_clip.sh
    test_ears.py
    verify_voice.py
    voice-stack          (launch script)
    voice.env            (environment)
    systemd/             (8 service units)
      company-stt-canary.service
      company-stt-granite.service
      company-stt-parakeet.service
      company-voice-chatterbox.service
      company-voice-cosyvoice.service
      company-voice-orpheus.service
      company-voice-qwen3tts.service
      company-voice-xtts.service
  
  models/                (pre-downloaded)
    kokoro-v1.0.onnx     (Kokoro model)
    voices-v1.0.bin      (voice pack)
  
  ref/
    company_voice_ref.wav (reference recording)
```

---

## Inventory Table

| Module | File | Purpose | PRIORITY | Note |
|--------|------|---------|----------|------|
| **mcp_face** | AGENTS.md | Constitution: agent-face governance (C7) | **YES** | Module contract & guarantees |
| | server.py | FastMCP server exposing generic verbs (C7) | **YES** | Agent interface — one face of Suite |
| **nodes** | AGENTS.md | Constitution: node-type library (C2) | **YES** | Registry + self-registration guarantees |
| | llm.py | First AI process node-type (S6/C2) | **YES** | Core: model calls via guarded fabric |
| | embed.py | Text → Vector (E1–E5 fabric) | **YES** | Core: embedding pipeline |
| | retrieve.py | Vector+corpus → top-K ranked | **YES** | Core: semantic retrieval |
| | ask.py | Context-grounded Q&A (first-purpose) | **YES** | First working node |
| | codebase.py | Content node: repo reader | **YES** | Self-describing (reads its own codebase) |
| | model_of_tim.py | Explicit Tim model (context escalation rung 2) | **YES** | Grounding twin's reasoning |
| | gate.py | Conditional routing (B5/branching) | Maybe | Control flow |
| | join.py | Fan-in skeleton | Maybe | Data aggregation |
| | pair.py | Non-commutative fan-in | Maybe | Ordered aggregation |
| | portal.py | Artefact multi-view (context-13) | Maybe | Presentation layer |
| | rhm_mode.py | RHM presence as a node (context-05) | Maybe | Status/mode representation |
| | constant.py | Constant value skeleton | No | Template node |
| | similarity.py | Vector cosine similarity | No | Metric node |
| | titlecase.py | Text transform skeleton | No | Template node |
| | uppercase.py | Text transform skeleton | No | Template node |
| | wordcount.py | Text metric skeleton | No | Template node |
| **roles** | AGENTS.md | Constitution: cognition role registry (C2.1–C2.5) | **YES** | File-discovered role registry |
| | judge.py | Finished-thought judge (role #0, C2.2) | **YES** | Voice circuit endpoint — config-only |
| | check.py | CHECK role (listening cast C2.3) | **YES** | Concurrent Cognition swarm |
| | connect.py | CONNECT role (listening cast C2.3) | **YES** | Link relevance judgment |
| | focus.py | FOCUS role (listening cast C2.3) | **YES** | Intent extraction + auxiliary routing |
| | ground.py | GROUND role (listening cast C2.3) | **YES** | Scope + citable grounding |
| | recall.py | RECALL role (listening cast C2.3) | **YES** | Memory snippet + relevance |
| | voice.py | VOICE role (listening cast C2.3) | **YES** | Tone + phrasing + label |
| | verify_jury.py | VERIFY_JURY role (jury, C2.4) | Maybe | Verdict verification |
| **voice** | AGENTS.md | Constitution: voice subsystem (G2–G4) | **YES** | STT swappable registry + TTS Kokoro + lifecycle |
| | stt.py | Speech-to-text swappable provider | **YES** | Catalog: whisper.cpp + GPU ears + AssemblyAI |
| | tts_service.py | Kokoro local text-to-speech (CPU) | **YES** | Core: on-machine speech synthesis |
| | speakable.py | Text → natural-speech transform | **YES** | Universal layer: markdown cleaning + expression mapping |
| | lifecycle.py | Voice service load/unload/status | **YES** | VRAM resource mgmt convergence (2026-06-06) |
| | loop.py | Voice turn loop integration | **YES** | Speaking + listening circuit |
| | personas.py | Voice persona definitions | Maybe | Tone/identity registry |
| | FROM-OPS-CLI-SESSION.md | Session notes | No | Temporary record |
| | trial_manifest.json | Engine trial manifest | No | Config/metadata |
| **voice/ears** | AGENTS.md | Constitution: GPU STT ears | **YES** | 3 ears self-registering in catalog |
| | _stt_service.py | Shared HTTP shell (ears) | Maybe | Infrastructure |
| | parakeet.py | NVIDIA Parakeet-TDT (:2031) | Maybe | ~3.05 GB VRAM |
| | canary.py | NVIDIA Canary-Qwen 2.5B (:2032) | Maybe | ~10.06 GB VRAM |
| | granite.py | IBM Granite Speech 4.0 1B (:2033) | Maybe | ~4.66 GB VRAM |
| **voice/engines** | AGENTS.md | Constitution: trial TTS engines | **YES** | 5 engines self-registering in catalog |
| | _service.py | Shared HTTP shell (engines) | Maybe | Infrastructure |
| | qwen3tts.py | Qwen3-TTS VoiceDesign (:4128) | Maybe | ~6 GB VRAM, 2700 tok/s measured |
| | chatterbox.py | Chatterbox-TTS (:4124) | Maybe | Lightweight alternative |
| | orpheus.py | Orpheus-TTS (:4125) | Maybe | Expression support |
| | cosyvoice.py | CosyVoice2 (:4126) | Maybe | Multilingual candidate |
| | xtts.py | XTTS-v2 Coqui (:4127) | Maybe | Voice cloning support |

---

## Summary

**Total files scanned:** 68  
**Regions covered:** 4 (nodes, roles, mcp_face, voice)

### Spread

- **Node-types:** 19 defined (7 live/core, 12 skeletons or experimental)
- **Cognition roles:** 9 defined (1 config-only judge, 6 listening-cast, 1 jury)
- **Voice components:** 
  - **STT:** 1 swappable registry (whisper.cpp default, 3 GPU ears, cloud optional)
  - **TTS:** 1 core (Kokoro CPU), 5 trial engines (GPU-intensive)
  - **Architecture:** lifecycle + stt + tts_service + speakable (universal layer) + loop integration
- **Agent interface:** 1 FastMCP server (C7) — generic verbs, no per-type tools

### Top 10 Priority Files for Deep-Read

1. `nodes/AGENTS.md` — Node-type library contract & self-registration guarantees (C2)
2. `roles/AGENTS.md` — Cognition role registry & file-discovery pattern (C2.1–C2.5)
3. `voice/AGENTS.md` — STT swappable + TTS + lifecycle converged VRAM mgmt (G2–G4)
4. `mcp_face/server.py` — Agent interface: generic verbs over Suite (C7)
5. `nodes/llm.py` — First AI node-type: model + fabric guard (S6/C2)
6. `nodes/ask.py` — First working node: context-grounded Q&A
7. `voice/speakable.py` — Universal text→speech transform (V-C to V-D mapping)
8. `voice/lifecycle.py` — VRAM resource mgmt convergence (keeper pattern, 2026-06-06)
9. `nodes/model_of_tim.py` — Explicit Tim model for context escalation
10. `voice/stt.py` — Speech-to-text provider registry (catalog pattern)

### Architecture Insights

- **Self-Registering Patterns:** Nodes (`nodes/*.py`) + Roles (`roles/*.py`) + Voice engines/ears discover themselves via file presence, no central registry needed (C2, C2.1–C2.5, G2)
- **Fabric Guards:** AI nodes (`llm`, `embed`, `retrieve`, `ask`) delegate to `fabric/` for safety (non-empty/JSON-repair/validate)
- **Swappable Registries:** STT providers, TTS engines, roles all catalog-based (PROVIDER_LIST, ENGINE_REGISTRY, ROLE_REGISTRY)
- **Convergence Point:** Voice lifecycle unified VRAM authority with `ops/cli/gpu.py` (the keeper, 2026-06-06) — closed old dual-authority bug
- **Universal Layers:** Speakable (text→speech transform engine-aware) + Suite (shared brain for UI + agent faces)

### Legacy/Experimental Notes

- Skeleton nodes (constant, uppercase, titlecase, etc.) appear to be templates for node-type authoring patterns
- 5 trial TTS engines (qwen3tts, chatterbox, orpheus, cosyvoice, xtts) coexist but VRAM conflict requires on-demand policy (not all resident)
- 3 GPU STT ears similarly compete with brain + embedding models — boot-default is whisper.cpp (CPU, zero-install)
- `verify_jury.py` role exists but may be experimental (jury pattern in flux per C2.4 context)
