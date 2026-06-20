# GAP (recall reliability): the pplx embedder load HANGS on cuda → :8007 flaps → semantic recall down

*recollection's finding from the 2026-06-20 recall outage (2nd of the day). The chroma rebuild + chunk_id adapter fix (3475aa6) made recall correct; THIS is the separate reliability gap that keeps taking :8007 (and thus all meaning-search recall) down. Escalated to lead + Tim (GPU call needed); captured here so the fix is tracked, not lost in the channel.*

## SYMPTOM
`embed-pplx` (:8007, the company's live embedder) goes down repeatedly. `company health` → embed-pplx ✗; `recall_for_decision` + `session_search` semantic both fail ("embedder DOWN at :8007"). 2 outages on 2026-06-20 (1st ~03:00 recovered transiently; 2nd ~16:00 did NOT self-recover).

## ROOT CAUSE (evidence, not inference)
The model LOAD hangs on cuda — it does NOT complete and does NOT error:
- serve log last line stuck at `[pplx-embed] loading perplexity-ai/pplx-embed-context-v1-4b on cuda dtype=bfloat16…` for 15+ min, no further line, :8007 never binds.
- GPU util during the hang: spiked 4%→19% then fell to 1% (load stalled, then idle) — used VRAM stuck ~3.7GB, the 8.2GB model never goes resident.
- The PRIOR start was SIGKILL'd by systemd: `company-embed-pplx.service: Failed with result 'timeout'` after `Consumed 16min 36s CPU` — i.e. the load exceeded `TimeoutStartSec` and got killed before binding.
- NOT OOM (12GB free, needs 8.2GB) · NOT slow-but-fine (served 0.29s embeds earlier the same day) · NOT a code bug (same binary worked that morning).
→ Diagnosis: a WEDGED CUDA CONTEXT. A hung serve process (e.g. it sat alive-but-not-serving 41 min) appears to leave the GPU in a state where the next load stalls. Restarting `embed-pplx` ALONE does not clear it (the new load hangs the same way) — which is why it flaps.

## WHY IT FLAPS SILENTLY (the systemd interaction)
The serve process hangs WITHOUT EXITING → systemd sees the main process alive → no auto-restart fires → `company health` shows ✗ but nothing recovers it. When systemd's start-timeout DOES fire, it SIGKILLs and restarts, but the fresh load hits the same wedged context → hangs again. Manual `company restart embed-pplx` reproduces the hang (verified).

## THE FIX (options — needs the GPU owner; a clean restart is NOT enough)
1. **Clear the wedged context**: evict/stop the OTHER GPU resident (chat-4b vllm :8000) and/or a full GPU-services reset, THEN load pplx on a clean card. (`company restart embed-pplx --evict`, or stop-all + up.) This is the likely real fix — but it touches the loadout (chat-4b = the slice's render) so it's the GPU owner's (Tim's) call.
2. **A health-watchdog with auto-restart** on embed-pplx: detect port-unbound-while-process-alive (the hang signature) → kill + relaunch. Stops the silent flap (systemd's process-alive check misses it). Reliability follow-up regardless of #1.
3. **Raise `TimeoutStartSec`** only if the load is genuinely just slow under contention — but 15min stuck with util at 1% = hang, not slow, so this alone won't fix it.
4. **Investigate the load-hang trigger**: why does a serve process hang alive-but-not-serving in the first place (the upstream cause of the wedge)? — the deepest fix.

## STATUS / IMPACT
- Recall is DEGRADED, not dead: `session_search` LEXICAL mode (term search, zero models) still works; only meaning-search (embedding) is down. The build slice is NOT blocked (C5 grounding already landed; merge-sa C1 is render+fork).
- The chroma rebuild + chunk_id fix stand — recall is CORRECT, just needs the embedder up.
- Escalated to lead (infra remit) + Tim (GPU nod for evict/reset). Holding for the GPU call; recall comes back the moment :8007 binds (no further code change needed). The watchdog (#2) is the durable fix to stop this recurring — recollection's to build once the immediate outage clears + lead greenlights.
