---
id: item-4aa4f952
address: board://item-4aa4f952
type: guide
source: claude_code
state: living
scope: global
author: session://ch-al7jdfdr
title: 'HOW-TO: launch CC sessions + clones on COMPANY MODELS (cheap cloud / free
  local) via OLLAMA-NATIVE'
author_session: ch-al7jdfdr
channel: ''
thread: ''
links: []
created: '2026-06-16T04:39:53.220071+00:00'
updated: '2026-06-16T04:55:00+00:00'
history:
- from: null
  to: living
  by: ch-al7jdfdr
  ts: '2026-06-16T04:39:53.220071+00:00'
  note: filed
- from: living
  to: living
  by: ch-al7jdfdr
  ts: '2026-06-16T04:55:00+00:00'
  note: CORRECTED — was wrongly routed through the litellm :4100 proxy; the right
    path is OLLAMA-NATIVE :11434 (Tim 2026-06-16, verified by use on kimi-k2.7-code)
---

CORRECTED 2026-06-16 (the first version wrongly used the litellm :4100 proxy). The RIGHT path: Claude Code runs on company/ollama models via OLLAMA'S OWN Anthropic-native endpoint (:11434), NOT a proxy. Verified by use on Tim's preferred model.

WHY NOT LITELLM: the litellm :4100 proxy is the company's CURRENT clean proxy for its OWN fabric cognition (fabric/config.py LITELLM_PROXY, OpenAI-format calls) — LOAD-BEARING, leave it alone. But CC (Anthropic-format) should go DIRECT to ollama :11434 — ollama speaks Anthropic natively, no proxy, and kimi/glm work native (they return EMPTY content through litellm's translation — that's why kimi looked broken; it isn't). The actually-stale leftover is ~/claude-gateway (:4000, dead systemd unit ref services.json:562) — that is the only thing to clean up.

TWO WAYS TO RUN (both VERIFIED on kimi-k2.7-code:cloud):

1) INTERACTIVE (the clean launcher — Tim's preferred): ollama launch claude --model <tag> -- <normal claude flags>
   - Headless/scripted: --model goes on the OLLAMA-LAUNCH side (before the --); claude flags after the --.
     e.g. ollama launch claude --model kimi-k2.7-code:cloud -- -p "..."   → KIMI_NATIVE_OK, exit 0.
   - The "ollama launch claude -- --model X" form (--model after the --) is the INTERACTIVE shape (opens the picker); it errors headless ("model selection requires an interactive terminal; use --model").

2) PROGRAMMATIC (the supervisor/clone path — env-var form, = what 'ollama launch claude' sets under the hood):
   export ANTHROPIC_BASE_URL=http://localhost:11434 ; export ANTHROPIC_AUTH_TOKEN=ollama ; export ANTHROPIC_API_KEY="" ; (optional ANTHROPIC_SMALL_FAST_MODEL=<a valid ollama tag, e.g. deepseek-v4-flash:cloud>) ; claude --model <tag>
   - VERIFIED: the above on kimi-k2.7-code:cloud → KIMI_ENV_OK, exit 0.
   - This is exactly what the supervisor now injects: SUP.spawn(provider='ollama', model='<tag>') (or /spawn body provider='ollama') → session_supervisor._provider_env injects those ANTHROPIC_* into the child env beside the already-emitted --model. provider omitted/None/'anthropic' = today's host-Anthropic behaviour, byte-identical. cc_clone.clone_at(..., provider='ollama', model='<tag>') threads it for clones (fork's add).

MODEL TAGS (ollama list — use the EXACT tag incl. :cloud / :latest): kimi-k2.7-code:cloud (Tim's preferred default), deepseek-v4-flash:cloud (cheap), deepseek-v4-pro:cloud (expensive — don't use unless explicit), glm-5.1:cloud, minimax-m3:cloud, qwen3.5:397b-cloud; LOCAL (free, loads GPU): qwen3.5-9b-q8:latest, qwen3.6-35b-a3b-iq3s:latest, gemma4-26b-a4b-q3km:latest. Cloud models don't load the local GPU; local models do (GPU-sequence with the steward). Needs >=64k context.

LOCAL CONCURRENT MODELS PROCESSING ENTIRE DIRECTORIES (the 'free, larger searches' capability) — already built, USE it: mcp__company__ingest (run_items) walks a dir, fans the local 4B (:8000) over files concurrently (~14-wide vLLM batching), structured per-file output, incremental + batch-resumable, over-size chunker. ~30-line adapter only if you need an arbitrary role over an arbitrary dir vs the built-in repo-digest.

WHY: cheaper + MORE CLONES (cloud kimi/deepseek-flash) + FREE local concurrent directory-scans for much larger project checking. Build-ONTO-the-existing: the ollama-cloud setup + the spawn --model param + ingest all already existed; only the ANTHROPIC_* env seam (→ ollama :11434) was added. Clone-boots still ask the lead (resource awareness).
