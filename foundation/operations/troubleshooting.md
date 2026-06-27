---
type: operations
title: Troubleshooting — known failures + fixes
date_started: 2026-05-27
tags: [foundation, operations, troubleshooting]
---

# Troubleshooting

> [[_operations-index|← Operations hub]]

## Purpose

Failure modes that were diagnosed during substrate setup. Each entry pairs a symptom with the underlying cause and the fix that resolves it. The goal is that future agents don't re-derive these — the cost of figuring them out is paid once and recorded here.

## Service won't start

### Symptom: `Active: activating (auto-restart)` in a loop

The service crashes within 10s of start; systemd retries; crashes again.

**Step 1**: Read the actual error.

```
journalctl --user -u vllm-chat.service -n 100 --no-pager
```

Look for the first `ERROR`, `Traceback`, or `RuntimeError` line — that's the cause; everything after is cascade.

**Common causes** (in order of frequency observed):

| Error contains | Cause | Fix |
|---|---|---|
| `cannot find -lcudart` or `cannot find -lcuda` | flashinfer linker can't find CUDA stubs | Re-establish symlinks per [[cuda-toolchain#Linker symlinks]] |
| `CUDA compiler and CUDA toolkit headers are incompatible` | CCCL major.minor mismatch with toolkit | Re-pin cu13 packages to 13.0.x per [[cuda-toolchain#Re-pin command]] |
| `Free memory on device cuda:0 ... less than desired` | Another process holds GPU memory | Check `nvidia-smi`; close Chrome / lower `--gpu-memory-utilization` |
| `No available memory for cache blocks` | Model loaded but no KV-cache slots left | Lower `--max-num-seqs`, lower `--max-model-len`, or both |
| `max_num_seqs (N) exceeds available Mamba cache blocks (M)` | Hybrid Mamba-attention KV constraint | Set `--max-num-seqs <= M` for the current config |
| `unrecognized arguments: --xxx` | vLLM 0.21 flag mismatch (some 0.20 flags renamed) | Check `vllm serve --help`; flag changed in 0.21 |
| `Permission denied: ...serve.sh` | Launcher not executable | `chmod +x ~/vllm-tests/serve*.sh` |
| Module not found errors | Wrong venv activated | Check launcher activates the right venv (`vllm-env` for chat/embed; `jina-v4-env` for jina-v4) |

### Symptom: Service "starts" but endpoint doesn't respond

The service is `Active: active (running)` but `curl http://localhost:8000/v1/models` hangs or returns connection refused.

**Cause**: vLLM is in cold-start (torch.compile + CUDAGraphs + model loading). Typical 60–180s for a model that hasn't been compiled before; ~30–60s with warm caches.

**Diagnosis**:

```
journalctl --user -u vllm-chat.service -f
```

Watch for the lines:

- `Loading weights took N seconds`
- `Model loading took N seconds`
- `torch.compile took N seconds`
- `Graph capturing finished`
- `Application startup complete.`

The endpoint becomes responsive after `Application startup complete`. Until then, the service is healthy from systemd's view but not serving.

## Inference works but output is wrong

### Symptom: Model emits `Thinking Process:` or `<think>` blocks before answering

**Cause**: Qwen 3.5 thinking mode is on. Either:

- The chat-template patch isn't loaded (server started without `--chat-template ~/vllm-tests/chat_template_nothink.jinja`)
- The request explicitly enabled it (`chat_template_kwargs: {"enable_thinking": true}`)

**Fix**: confirm `--chat-template` flag is in `~/vllm-tests/serve.sh` and is being passed at launch (`journalctl --user -u vllm-chat | grep chat-template`). If the patched template is loaded, the model should NOT emit thinking blocks for default requests.

See [[chat-template-patch]] for the full explanation.

### Symptom: Tool calls fail with `400 Bad Request`

**Cause**: Server launched without tool-calling enabled.

**Fix**: launcher must include:

```
--enable-auto-tool-choice \
--tool-call-parser qwen3_xml \
```

(Or the appropriate parser for the model family — see [[../models/qwen3_5-4b-awq#Quirks]].)

Restart the service after editing.

### Symptom: Tool calls return as text content instead of structured `tool_calls`

**Cause**: parser mismatch. The model emits XML-style tool tags but vLLM is configured with a different parser (e.g. `hermes`), so the parser doesn't recognise them and they pass through as plain text.

**Fix**: ensure `--tool-call-parser qwen3_xml` matches the model's emission format. Confirm with a probe request — see the example in [[../models/qwen3_5-4b-awq#Tool calling]].

### Symptom: Model output is gibberish / repetitive / nonsensical

**Causes** (in order of probability):

1. **Sampling**: `temperature=0.0` (greedy) on a small model causes repetition loops. Use 0.7 with `top_p=0.9` and `repetition_penalty=1.05`.
2. **Raw `llm.generate()` on a chat-tuned model**: not applying the chat template. Use `llm.chat([messages])` or the `/v1/chat/completions` endpoint, not `/v1/completions`.
3. **`enforce_eager=True`** in vLLM config: disables compile-time optimisations including those that fix some quant-load issues. Should not be set in production.
4. **Wrong quant variant for the model family**: e.g. an AWQ quant with incompatible group size for the model architecture. Verify the packager (cyankiwi, QuantTrio, etc.) targets the right family.

## VRAM / memory issues

### Symptom: OOM during torch.compile or CUDAGraphs warmup

**Cause**: vLLM 0.21's memory profiler over-reserves VRAM for graph capture. Tight-VRAM models trigger this even when they would fit at runtime.

**Fix**: set `VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=0` in the launcher env. See [[cuda-toolchain]].

### Symptom: System RAM pressure → engine killed

**Cause**: Parallel HF downloads + multiple services + system tasks exceed WSL's RAM budget.

**Fix**:

1. Identify RAM-heavy processes: `ps aux --sort=-%mem | head`
2. Pause downloads: `pkill -f "hf download"` (resumable; can restart later)
3. If recurring, consider WSL `.wslconfig` memory cap

See [[boot-and-linger#WSL-specific boot quirks]].

### Symptom: Three services were running, now one is gone

**Cause**: probably OOM killed by the kernel under RAM pressure.

**Diagnosis**:

```
dmesg | grep -i "killed\|oom" | tail -20
```

Or `journalctl --user -u <service> -n 100` should show the systemd auto-restart kicking in.

**Fix**: same as above — relieve RAM pressure. The service should auto-restart per `Restart=on-failure`.

## Symptom families not yet documented here

(Examples; more accumulate as failures occur.)

- WSL memory ballooning under host pressure
- Ollama-side specific failures (model not found, Modelfile syntax errors, cloud-route auth)
- Open WebUI failures (container won't start, model not appearing in dropdown)
- Bench script failures (httpx connection errors, payload parse errors)
- Multi-tenant interference (two long-running benches against the same service)

## Open at this topic

- The list above is incomplete by design — it grows as failures occur and get recorded. Future agents should add new entries with the same shape: symptom → cause → fix.
- A diagnostic CLI — `vllm-stack diagnose` would automate the most common health checks (toolchain pinning, symlinks present, services running, ports listening, sample inference).
- Linking from this file to the source archive — when a fix was historically applied in a specific bench log or chat transcript, that source can be cited for ground-truth verification.

## Connects to

- [[_operations-index]] — hub
- [[cuda-toolchain]] — most common service-start failures land here
- [[chat-template-patch]] — most common inference failures land here
- [[systemd-services]] — the lifecycle layer
- [[vram-budget]] — VRAM-side failure modes
