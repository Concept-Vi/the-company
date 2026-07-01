---
type: research-report
register: descriptive
aliases: ["constrained-decoding repetition research", "guided-JSON loop research"]
tags: [vllm, structured-output, guided-decoding, xgrammar, repetition-loop, qwen3.5, awq, sampling]
status: unconfirmed
created: 2026-06-30
topic: "Greedy + guided-JSON repetition loop on Qwen3.5-4B-AWQ under vLLM"
---

# Constrained-Decoding Repetition Loop — External Research

> Scope: external research only (vLLM GitHub, HuggingFace, Qwen docs, papers, blogs). This file reports **what the community and maintainers know**, not my own diagnosis of Tim's code. Every external claim is tagged **[VERIFIED]** (read from a source I cite) or **[INFERRED]** (my reasoning across sources, not stated by a source). Every source has a URL.

---

## 0. TL;DR / Recommendation

The failure is a **known, named class**: model-level repetition bias amplified by grammar-constrained decoding, made worse by **greedy decoding** and **Qwen3.5's hybrid Mamba/Gated-DeltaNet architecture** and (per community report) by **AWQ quantization** of this exact `cyankiwi` build. vLLM maintainers acknowledged it strongly enough to add a dedicated `repetition_detection` stop parameter.

**The trap in your current setup:** you optimised for *reproducibility* (greedy, temp=0). Qwen's own model card says in plain words: *"DO NOT use greedy decoding, as it can lead to performance degradation and endless repetitions."* Greedy is the single biggest contributor. So the principled fix is **not** "add more rep-penalty on top of greedy" — it is to stop fighting greedy.

Ranked recommendation (details in §3):

1. **Bound the schema** — `maxItems` on `findings[]` (+ `maxLength` on the free-text strings, with a caveat). This is the only remedy that makes the loop *structurally impossible to run forever* and still yields **valid** JSON, because a bounded array lets the grammar reach an accepting (closing) state. **[INFERRED, mechanism-sourced]**
2. **Switch the anti-repetition lever from `repetition_penalty` to `presence_penalty` (~1.5)** and relax greedy to a small temperature (Qwen's blessed profile, or at least `min_p=0.2`). `presence_penalty`/`frequency_penalty` penalise **output-only**; `repetition_penalty` in vLLM penalises **prompt + output**, which is wrong for an extraction task that legitimately echoes identifiers from the input code. **[VERIFIED on the penalty semantics]**
3. **Set `repetition_detection` explicitly** (`max_pattern_size≈20, min_count≈4`) as a **cost backstop + retry trigger**, not as the fix — see the important caveat in §3.3 (it ends generation early, which under a grammar means *invalid/truncated* JSON, just cheaper). **[VERIFIED the param exists; INFERRED its consequence under a grammar]**
4. **`min_p=0.2`** — the community fix reported for *your exact `cyankiwi` AWQ build* on this Qwen3.5 family. **[VERIFIED — community report]**
5. **Try the `guidance` (llguidance) backend** instead of `xgrammar` as an experiment — *unverified* that it loops less; it is verified to have broader schema support. **[INFERRED for the loop claim]**

`repetition_penalty=1.15` is a **working empirical band-aid, not a sound long-term choice** for this task — §4.

---

## 1. Is this a known issue? (Q1) — YES

### 1.1 The core mechanism (the named class)
Multiple sources converge on the same description: a model's mild repetition tendency becomes a **hard loop** when grammar-constrained decoding masks the token space, because the grammar can **prevent the model from emitting EOS / breaking the pattern**, so it re-emits valid-but-repeated array objects until `max_tokens` (`finish_reason=length`). This is exactly your symptom.

- vLLM **Issue #40080 — "Gemma 4 generates infinite repetition loops, especially with structured output (JSON schema)"**. Same shape as yours: valid initial content, then a degenerative cycle repeating phrases with minor variation until `max_tokens`. States `repetition_penalty`/`frequency_penalty` *"partially help but do not fully prevent the issue."* **[VERIFIED]** https://github.com/vllm-project/vllm/issues/40080
- vLLM **Issue #27157 — "Qwen3-VL-30B keeps outputting the same phrases over and over"**: explicitly *"more likely with repetitive structures (lists, multiple JSON objects)"* — matches your "inputs with enumerable/repetitive structure (code files with many similar functions)." (This one is free-text, not guided — shows the bias is model-level, then grammar amplifies it.) **[VERIFIED]** https://github.com/vllm-project/vllm/issues/27157
- vLLM **Issue #13683** — guided decoding (xgrammar / lm-format-enforcer) producing repeated `{{`-type malformed output. **[VERIFIED it exists]** https://github.com/vllm-project/vllm/issues/13683
- vLLM **Issue #15236** — broad report of guided-generation problems through v0.8.1. **[VERIFIED it exists]** https://github.com/vllm-project/vllm/issues/15236
- Academic framing: structured-generation surveys describe *"output degeneration (unnatural token repetition)"* as a recognised failure mode of guided decoding, and a 2025 production paper is dedicated to it ("Solving LLM Repetition Problem in Production"). **[VERIFIED the framing]** https://arxiv.org/pdf/2512.04419 · https://blog.squeezebits.com/guided-decoding-performance-vllm-sglang

### 1.2 Why constraint makes it worse (token/grammar mismatch)
> "Grammar constraints operate at the character level, but the model generates multi-character tokens… When constrained decoding forces the model down an unusual token path, it may produce a non-canonical tokenization the model rarely saw during training, subtly degrading output quality." **[VERIFIED]** — Brenndoerfer, *Constrained Decoding* (https://mbrenndoerfer.com/writing/constrained-decoding-structured-llm-output); echoed by SqueezeBits (above).

**[INFERRED]** Net mechanism: greedy picks the argmax every step; the grammar removes the escape tokens (incl. premature stops) and the off-distribution token path nudges the model toward the lowest-entropy continuation — re-emitting the previous object. With no stochasticity (`temp=0`) there is nothing to break the cycle, so it runs to `max_tokens`. This is consistent with your observation that `temperature=0.4` alone did **not** break it (still concentrated) while `repetition_penalty` did (directly bends the logits).

> **Not the same as #14151** ("Structured output requests can hang the server"): that is *grammar-compilation* CPU-spin on huge schemas, a different failure. Noted to keep them distinct. **[VERIFIED]** https://github.com/vllm-project/vllm/issues/14151

---

## 2. The vendor tension you must decide first (greedy vs. Qwen)

This is the spine of the whole answer. Qwen's official model card (Qwen3 family) states verbatim:

> **"DO NOT use greedy decoding, as it can lead to performance degradation and endless repetitions."** **[VERIFIED]** https://huggingface.co/Qwen/Qwen3-0.6B

Qwen's recommended profile is **sampling, not greedy**, and crucially uses **`presence_penalty`** (not `repetition_penalty`) as the anti-loop lever:
- Non-thinking: `temperature 0.7, top_p 0.8, top_k 20, min_p 0` (model-card defaults); the technical report / framework guidance adds **`presence_penalty=1.5`** *"if you encounter significant endless repetitions,"* explicitly **`repetition_penalty=1.0`**. **[VERIFIED]** https://huggingface.co/Qwen/Qwen3-0.6B · https://muxup.com/2025q2/recommended-llm-parameter-quick-reference
- Tradeoff the card names: a **higher `presence_penalty` may occasionally cause language mixing** and a slight quality dip. **[VERIFIED]**

You chose greedy for *reproducibility*. So the decision is:
- **Path A (keep determinism):** stay low-temp but you MUST add a real anti-repetition lever + schema bounds (you cannot rely on argmax alone — see §1.2). Greedy is also bit-exact only within a fixed batch/version; vLLM is not guaranteed reproducible across batching anyway. **[INFERRED]**
- **Path B (relax determinism):** adopt Qwen's sampling profile (or `min_p=0.2`, §3.4). This is the **vendor-blessed** path and the one least likely to fight the architecture.

---

## 3. Recommended fixes, ranked (Q2)

### 3.1 — #1 Bound the schema (the only *structural* cure that keeps JSON valid)
- Add **`maxItems`** to the `findings` array. A bounded array means the grammar has a reachable **accepting state** (close the array, close the object) — so even a model leaning toward repetition is *forced* to a legal closing structure instead of looping forever. **[INFERRED — mechanism follows directly from how grammar masking works in the cited sources]**
- Reduce the number of **free-text string fields** per object, and add **`maxLength`** to the ones you keep. Free-text fields are where the loop lives (your repeating `findings[].detail`); bounding them shrinks the space the loop can occupy.
- **Caveat — verified vLLM bug:** **`maxLength` is ignored when a `pattern` is also set on a string item** (Issue **#45592**). If you bound a string, do it with `maxLength` *without* a regex `pattern`, or the bound silently won't apply. **[VERIFIED]** https://github.com/vllm-project/vllm/issues/45592
- Related correctness note: empty-array edge cases have had bugs (Issue **#13821**) — test that `findings: []` is still emittable if "no findings" is legal. **[VERIFIED it exists]** https://github.com/vllm-project/vllm/issues/13821

Applies to vLLM: yes, schema constraints are honored by all backends. This is the highest-leverage change because it attacks the cause (unbounded grammar) not the symptom.

### 3.2 — #2 Output-only penalty + relax greedy (the principled sampling fix)
- Prefer **`presence_penalty` ≈ 1.5** (Qwen's value) or **`frequency_penalty`** over `repetition_penalty`. Reason (verified semantics from the vLLM `SamplingParams` doc):
  - `repetition_penalty` *"penalizes new tokens based on whether they appear in **the prompt AND the generated text**."* For your extraction task — outputs that *legitimately* echo function/identifier names from the **input code file** — this penalises correct input-fidelity. **[VERIFIED semantics]**
  - `presence_penalty` and `frequency_penalty` are **output-only** (range −2..2). They suppress *re-saying the same thing again* without taxing legitimate reuse of input tokens. This is the principled lever for "stop repeating yourself." **[VERIFIED semantics]**
  Source: https://docs.vllm.ai/en/latest/api/vllm/sampling_params/
- Pair with a small amount of stochasticity (a low temperature or `min_p`, §3.4) so there is *something* to break the argmax cycle.

Applies to vLLM: yes, all three are first-class `SamplingParams`. Recommended starting point for your task: `presence_penalty=1.5, repetition_penalty=1.0, frequency_penalty=0` (Qwen profile), then nudge `presence_penalty` up toward 2.0 only if a few inputs still loop, watching for language mixing.

### 3.3 — #3 `repetition_detection` — backstop + retry trigger, NOT the fix
vLLM added a dedicated parameter for exactly this failure:
- `SamplingParams.repetition_detection: RepetitionDetectionParams` with fields **`max_pattern_size`** (0 = disabled), **`min_pattern_size`** (0→1), **`min_count`** (must be ≥2). *"If such repetition is detected, generation will be ended early"* (`FINISHED_REPETITION`). **[VERIFIED]** https://docs.vllm.ai/en/latest/api/vllm/sampling_params/ · source: https://github.com/vllm-project/vllm/blob/main/vllm/sampling_params.py
- It is a **scheduler-level stop condition** (checked in `v1/core/sched/utils.py:check_stop`). Available since ~v0.17.0. **[VERIFIED via tt-xla smoke-test issue]** https://github.com/tenstorrent/tt-xla/issues/3708

**Critical caveat — do not crown this as the cure.** It *ends generation early*. With a grammar active, ending early means the JSON is **not at an accepting state** → you still get **truncated/invalid JSON**, just faster and cheaper (no run to `max_tokens`). So its real value is twofold: **(a) a hard cost bound**, and **(b) a clean machine-readable failure signal** (`finish_reason`/`FINISHED_REPETITION`) you can use to **trigger a retry with stronger sampling** — which is precisely the "escalate only on detected truncation" idea in your Q4. **[INFERRED — consequence under a grammar; the param itself is verified]**

> Diagnostic note: you observed **`finish_reason=length`**, not a repetition stop. That is evidence `repetition_detection` was **not active** in your run. A search summary claimed Nov-2025 PRs *auto-enable* it (`max_pattern_size=20, min_count=4`) whenever grammar decoding is on — I could **NOT confirm this in `sampling_params.py`** (the auto-enable, if it exists, lives in the structured-outputs/engine layer, not there). **Treat auto-enable as [UNVERIFIED]; set `repetition_detection` explicitly** rather than relying on it.

### 3.4 — #4 `min_p=0.2` — the community fix for YOUR exact build
The most on-point external source: HF discussion **"Qwen3.5-35B-A3B · vLLM — Looping prevention"** reports the **FP8 and the `cyankiwi` AWQ** builds of this Qwen3.5 hybrid family *"suffer from infinite looping in the default settings,"* fixed by overriding to `temperature 1.0, top_p 1.0, top_k 40, **min_p 0.2**`, with the note that **"the `min_p` setting probably has the greatest positive impact."** A follow-up commenter separately reports **JSON/structured-output failures on the quantized versions while only the unquantized model works.** **[VERIFIED — community report, not a maintainer]** https://huggingface.co/Qwen/Qwen3.5-35B-A3B/discussions/39

`min_p=0.2` truncates the long improbable tail and is cheap to add; it is the lowest-risk single knob to try for *this* model. Applies to vLLM: yes (`SamplingParams.min_p`).

### 3.5 — #5 Backend swap (experiment, loop-claim unverified)
- vLLM supports **xgrammar** and **guidance (llguidance)** (outlines / lm-format-enforcer also historically); default is **`auto`**. Select via CLI **`--structured-outputs-config.backend`** (the old `guided_decoding_backend` API field was removed in v0.12.0 — backend is now a serve-time CLI choice, not per-request). **[VERIFIED]** https://docs.vllm.ai/en/latest/features/structured_outputs/ · https://github.com/vllm-project/vllm/pull/14589
- **guidance/llguidance** has broader/more-correct JSON-schema support and lower invalid-JSON rate (LLGuidance ~0.12% vs xgrammar ~2.21% invalid in one benchmark, after excluding degeneration). Faster TTFT on unique schemas; xgrammar is faster on reused schemas via caching. **[VERIFIED]** https://blog.squeezebits.com/guided-decoding-performance-vllm-sglang · https://developers.redhat.com/articles/2025/06/03/structured-outputs-vllm-guiding-ai-responses
- **Whether guidance *loops less* than xgrammar: [INFERRED / UNVERIFIED].** No source says so. The loop is model-level, so a backend swap may not change it — worth an A/B test, not a guarantee.

### 3.6 — `no_repeat_ngram_size` and `bad_words`
- A SamplingParam **`no_repeat_ngram_size` was requested (Issue #7842) and closed *not planned*.** Hard n-gram blocking is **not** a built-in vLLM sampling field. **[VERIFIED]** https://github.com/vllm-project/vllm/issues/7842
- It *can* be done via a **custom logits processor** passed through `SamplingParams.logits_processors` / `extra_args` (third-party processors implement `no_repeat_ngram_size`, e.g. the MinerU processor, recommended start `=3`). This is the only route to true n-gram blocking in vLLM, but it is custom code. **[VERIFIED the mechanism exists]** https://docs.vllm.ai/en/stable/features/custom_logitsprocs/
- **`bad_words`** is supported but is the wrong tool here (you can't enumerate the looped phrases ahead of time). **[VERIFIED]**

---

## 4. Is `repetition_penalty=1.15` a sound long-term choice? (Q4)

**No — it is a working band-aid, keep it only as a fallback.** Reasons, with the sourced nuance:

1. **It penalises input fidelity for this task.** vLLM `repetition_penalty` penalises tokens from **prompt + output**. Your job is extracting findings from a code file, where reusing input identifiers is *correct*. `presence_penalty`/`frequency_penalty` are **output-only** and are the principled substitute. **[VERIFIED semantics]**
2. **It does NOT corrupt JSON syntax — that fear is unfounded.** Even if `"`, `{`, `,` get their logits penalised, the **grammar leaves them as the only finite-logit (legal) token** at structural positions, so they are still chosen. Grammar masking protects the JSON skeleton from the penalty. **[INFERRED from masking mechanism — consistent across SqueezeBits + Brenndoerfer]** So the real cost of rep-penalty is **content fidelity**, not broken JSON.
3. **It's an empirically-tuned constant, not a guarantee.** You already saw the cliff: 1.1 loops on some, 1.15 clears them, 1.3 over-suppresses. The window is narrow and input-dependent — fragile across new inputs. The cited issues say penalties *"partially help but do not fully prevent"* the loop. **[VERIFIED]**

**More principled long-term design** (combines the above):
- Bounded schema (`maxItems`/`maxLength`) so the loop can't run unbounded → **valid JSON by construction** (§3.1).
- Qwen's sampling profile: `presence_penalty≈1.5, repetition_penalty=1.0`, small temperature **or** `min_p=0.2` (§3.2, §3.4) — vendor-blessed, output-only, fidelity-preserving.
- `repetition_detection` as a **cost cap + retry signal**; on `FINISHED_REPETITION`/`length`, **retry once with escalated `presence_penalty`** (your "escalate only on truncation" idea, done cleanly via the engine signal rather than a fixed global constant) (§3.3).
- Keep `repetition_penalty=1.15` only as the last-resort fallback for stubborn inputs.

---

## 5. AWQ-4bit / Qwen3.5-hybrid-Mamba specifics (Q3)

### 5.1 AWQ-4bit
- AWQ-4bit retains ~98–99% of FP16 perplexity; **no source directly says AWQ *causes* repetition.** **[VERIFIED]** https://www.sitepoint.com/quantization-explained-q4km-vs-awq-vs-fp16-for-local-llms/
- One relevant edge: quantized models *"generate fewer decoding tokens"* and **coding/math tasks are the most quantization-sensitive** — your inputs are code. So quantization plausibly perturbs the output distribution enough to make the borderline loop tip over, but this is **[INFERRED]**, not asserted by a source.
- The strongest AWQ-specific signal is the community report (§3.4): the **`cyankiwi` AWQ build specifically** is named as looping in defaults, and a commenter reports **JSON failures on the quantized build while the unquantized model works**. That is the closest thing to a smoking gun that *this quantization* aggravates structured-output reliability. **[VERIFIED it was reported; causation UNVERIFIED]**

### 5.2 Qwen3.5 hybrid Mamba / Gated-DeltaNet
- Qwen3.5 is **hybrid Gated-DeltaNet (linear-attention) + full-attention + MoE**. DeltaNet/SSM layers maintain a **fixed-size recurrent state** that compresses all prior tokens. **[VERIFIED]** https://github.com/vllm-project/vllm/issues/42960 · https://arxiv.org/pdf/2312.00752
- General SSM literature: SSMs **"struggle with memory recall due to their recurrent nature"** and degrade on coding/reasoning when attention is replaced by SSM/MLP. **[VERIFIED]** https://arxiv.org/pdf/2406.07522 (Samba) · https://arxiv.org/pdf/2312.00752 (Mamba)
- **[INFERRED]** A fixed-size compressed state is *architecturally* more prone to settling into a low-entropy attractor (re-emitting the last object) once content fidelity is stressed by (a) constrained-token paths and (b) greedy argmax — which is consistent with the empirical reports, though no source states the SSM→loop causal chain explicitly. I found **no paper directly linking Mamba/SSM to repetition under constrained decoding** — treat 5.2's causal story as inference.
- Practical vLLM gotchas for this family (not loop-related but relevant to serving it): hybrid GDN models have cache-alignment constraints (reports of needing `--max-num-batched-tokens` tuning) and `VLLM_BATCH_INVARIANT=1` aborting startup on GDN layers. **[VERIFIED reported]** https://github.com/vllm-project/vllm/issues/42960 · https://github.com/QwenLM/Qwen3.6/issues/64

**Net for Q3:** the failure is best explained as **architecture (hybrid SSM, low-entropy recurrent state) × decoding (greedy + grammar masking) × quantization (AWQ perturbation on code inputs)** — three reinforcing factors, all pointing back to the §3 remedies. The single most architecture-aware single-knob is **`min_p=0.2`** (§3.4), the community fix for this exact family.

---

## 6. Concrete settings to try (in order)

```jsonc
// Path A — keep low determinism, attack the cause:
//   1. Schema: add "maxItems": N to findings[]; "maxLength" (NO "pattern") on free-text strings; trim # of free-text fields.
//   2. Sampling:
{
  "temperature": 0.0,            // if you must keep greedy; else 0.3–0.7
  "presence_penalty": 1.5,       // output-only anti-loop (NOT repetition_penalty)
  "repetition_penalty": 1.0,
  "min_p": 0.2,                  // community fix for this Qwen3.5 family
  "repetition_detection": { "max_pattern_size": 20, "min_pattern_size": 1, "min_count": 4 }, // cost cap + retry signal
  "max_tokens": 4000
}
// On finish_reason == "length" OR FINISHED_REPETITION → retry once with presence_penalty 1.8–2.0.

// Path B — vendor-blessed (relax determinism), simplest:
{ "temperature": 0.7, "top_p": 0.8, "top_k": 20, "min_p": 0.0, "presence_penalty": 1.5, "repetition_penalty": 1.0 }
```

Serve-time experiment: add `--structured-outputs-config.backend guidance` and A/B against `xgrammar` on your looping inputs (loop-reduction unverified, schema-correctness improvement verified).

---

## 7. Source index (all external, with URLs)

**vLLM issues/PRs/docs**
- #40080 Gemma infinite repetition w/ JSON schema — https://github.com/vllm-project/vllm/issues/40080
- #27157 Qwen3-VL repeating phrases (lists/JSON) — https://github.com/vllm-project/vllm/issues/27157
- #13683 guided decoding repeated `{{` — https://github.com/vllm-project/vllm/issues/13683
- #15236 broad guided-generation problems — https://github.com/vllm-project/vllm/issues/15236
- #14151 structured-output grammar-compile hang (distinct failure) — https://github.com/vllm-project/vllm/issues/14151
- #45592 maxLength ignored when pattern set — https://github.com/vllm-project/vllm/issues/45592
- #13821 empty-array structured output bug — https://github.com/vllm-project/vllm/issues/13821
- #7842 no_repeat_ngram_size closed not-planned — https://github.com/vllm-project/vllm/issues/7842
- #42960 GDN_ATTN batch-invariant (Qwen3-Next/3.6 hybrid Mamba+GDN) — https://github.com/vllm-project/vllm/issues/42960
- PR #14589 add guidance backend — https://github.com/vllm-project/vllm/pull/14589
- SamplingParams API (penalties, min_p, repetition_detection, bad_words, logits_processors) — https://docs.vllm.ai/en/latest/api/vllm/sampling_params/
- sampling_params.py source — https://github.com/vllm-project/vllm/blob/main/vllm/sampling_params.py
- Structured outputs feature doc (backends, auto, CLI selection) — https://docs.vllm.ai/en/latest/features/structured_outputs/
- Custom logits processors (n-gram via extra_args) — https://docs.vllm.ai/en/stable/features/custom_logitsprocs/

**Qwen / HuggingFace**
- Qwen3 model card — greedy warning + presence_penalty guidance — https://huggingface.co/Qwen/Qwen3-0.6B
- "Qwen3.5-35B-A3B · vLLM — Looping prevention" (cyankiwi AWQ + FP8 loop; min_p=0.2; JSON-on-quant failure) — https://huggingface.co/Qwen/Qwen3.5-35B-A3B/discussions/39
- Qwen3.5-4B AWQ vLLM compat (hybrid GDN serving notes) — https://github.com/QwenLM/Qwen3.6/issues/64
- Vendor parameter quick-reference — https://muxup.com/2025q2/recommended-llm-parameter-quick-reference

**Papers / blogs**
- "Solving LLM Repetition Problem in Production" — https://arxiv.org/pdf/2512.04419
- SqueezeBits — Guided Decoding Performance (degeneration; xgrammar vs guidance) — https://blog.squeezebits.com/guided-decoding-performance-vllm-sglang
- Red Hat — Structured outputs in vLLM (backend choice) — https://developers.redhat.com/articles/2025/06/03/structured-outputs-vllm-guiding-ai-responses
- Brenndoerfer — Constrained Decoding (token/char mismatch, degeneration) — https://mbrenndoerfer.com/writing/constrained-decoding-structured-llm-output
- tt-xla #3708 — repetition_detection available since vLLM v0.17.0 — https://github.com/tenstorrent/tt-xla/issues/3708
- Mamba — https://arxiv.org/pdf/2312.00752 · Samba (hybrid SSM) — https://arxiv.org/pdf/2406.07522
- AWQ quality vs FP16 — https://www.sitepoint.com/quantization-explained-q4km-vs-awq-vs-fp16-for-local-llms/

---
*Verified/inferred discipline maintained throughout. The two load-bearing [UNVERIFIED] items: (a) `repetition_detection` auto-enable on grammar decoding; (b) `guidance` backend loops less than `xgrammar`. Both are flagged inline; do not build on them without an A/B test.*
