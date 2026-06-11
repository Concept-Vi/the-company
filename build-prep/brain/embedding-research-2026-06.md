# Embedding Research — 2026-06

Research lanes for the Company's embedding layer. Each lane is appended by its research agent. Provisional — findings reflect what is verifiable on the web as of 2026-06-11; quantized-repo claims are labeled Observed (page says it) vs Verified (measured numbers shown) vs Inferred.

## Lane 1 · nomic-embed-code quantization

Researched 2026-06-11. Sources: HuggingFace model cards + HF API file trees (exact byte sizes), Nomic's official GGUF README, Ollama registry, vLLM docs, jina-embeddings-v4-gguf measured benchmarks.

### What the model is (base + architecture)

- **Base model: `Qwen/Qwen2.5-Coder-7B-Instruct`** — stated in the official model card frontmatter (`base_model:` field). https://huggingface.co/nomic-ai/nomic-embed-code
- Architecture in `config.json`: `Qwen2Model` (the decoder stack without the LM head), `model_type: qwen2` — so every tool that handles Qwen2 GGUFs/safetensors handles this model.
- **7B params (~7.6B actual)**, hidden_size **3584 → embedding dimension 3584**, 28 layers, GQA (28 attention heads / 4 KV heads), `max_position_embeddings` **32768**, vocab 152064.
- **Pooling: last-token pooling** (not mean pooling). This matters operationally — serving with the wrong pooling silently produces garbage retrieval (see Serving below).
- **Query prefix required**: queries must start with `Represent this query for searching relevant code: `. Documents/code are embedded raw, no prefix. (Official README, both base and GGUF repos.)
- Trained on CoRNStack (dual-consistency filtering + curriculum hard-negative mining); supports Python, Java, Ruby, PHP, JavaScript, Go. Apache 2.0. Tech report: https://arxiv.org/abs/2412.01007
- CodeSearchNet (model card): Python 81.7 / Java 80.5 / Ruby 81.8 / PHP 72.3 / JS 77.1 / Go 93.8 — beats Voyage Code 3 and OpenAI Embed 3 Large on most languages.
- **The original safetensors repo ships fp32** — `torch_dtype: float32`, 28.28 GB total across 6 shards (verified via HF API tree). Loading it naively with transformers pulls 28 GB; you must cast to fp16/bf16 or use a quant.

### Quantized versions available today

Full quantized-from list: https://huggingface.co/models?other=base_model:quantized:nomic-ai/nomic-embed-code

#### 1. Official GGUF — `nomic-ai/nomic-embed-code-GGUF` (Verified sizes via HF API)

https://huggingface.co/nomic-ai/nomic-embed-code-GGUF — quantized by Nomic themselves, with their own per-quant quality guidance:

| File | Size | Nomic's quality note |
|---|---|---|
| f32 | 28.29 GB | full FP32 |
| f16 / bf16 | 14.15 GB | full half-precision |
| Q8_0 | 7.52 GB | "Extremely high quality, generally unneeded but max available" |
| Q6_K | 5.81 GB | "Very high quality, near perfect, **recommended**" |
| Q5_K_M | 5.07 GB | "High quality, **recommended**" |
| Q5_K_S | 4.94 GB | "High quality, **recommended**" |
| Q4_1 | 4.53 GB | legacy, Apple-silicon friendly |
| Q4_K_M | 4.38 GB | "Good quality, default size for most use cases, **recommended**" |
| Q4_K_S | 4.15 GB | "Slightly lower quality with more space savings, **recommended**" |
| Q4_0 | 4.12 GB | legacy, ARM/AVX online repacking |
| Q3_K_L | 3.85 GB | "Lower quality but usable, good for low RAM" |
| Q3_K_M | 3.57 GB | "Low quality" |
| Q3_K_S | 3.26 GB | "Low quality, **not recommended**" |
| Q2_K | 2.84 GB | "Very low quality but surprisingly usable" |

#### 2. imatrix GGUF — `mradermacher/nomic-embed-code-i1-GGUF` (Verified sizes)

https://huggingface.co/mradermacher/nomic-embed-code-i1-GGUF — importance-matrix quants, go lower than the official set: IQ1_S 1.72 GB, IQ2_M 2.55 GB, IQ3_M 3.34 GB, IQ3_XXS 2.88 GB, IQ4_XS 3.93 GB, IQ4_NL 4.13 GB, plus i1 variants of Q2–Q6 (i1-Q4_K_M 4.38 GB, i1-Q6_K 5.81 GB). Static (non-imatrix) set also exists: https://huggingface.co/mradermacher/nomic-embed-code-GGUF

#### 3. Other GGUF mirrors (same quant ladder, different packagers)

- https://huggingface.co/lmstudio-community/nomic-embed-code-GGUF (LM Studio packaging)
- https://huggingface.co/bartowski/nomic-ai_nomic-embed-code-GGUF (bartowski, imatrix-calibrated)
- https://huggingface.co/Mungert/nomic-embed-code-GGUF
- https://huggingface.co/ExpedientFalcon/nomic-embed-code-Q5_K_M-GGUF (single Q5_K_M)
- https://huggingface.co/manutic/nomic-embed-code-f16-gguf (f16 only)

#### 4. AWQ — `pyrymikko/nomic-embed-code-W4A16-AWQ` (Observed; quality claim unverified)

https://huggingface.co/pyrymikko/nomic-embed-code-W4A16-AWQ
- AWQ W4A16 via **llm-compressor**, one-shot PTQ, group size 128, **compressed-tensors format** (so it loads in vLLM directly, not AutoAWQ-format).
- **model.safetensors = 4.46 GB** (verified via HF API tree).
- 6,207 downloads — the most-used non-GGUF quant of this model.
- Card claims "minimal degradation (<1% on most embedding tasks)" — **no benchmark numbers shown; treat as unverified marketing**. Calibration dataset not documented.

#### 5. FP8 — `duydq12/nomic-embed-code-FP8-dynamic` (Observed)

https://huggingface.co/duydq12/nomic-embed-code-FP8-dynamic
- FP8-dynamic via llm-compressor: per-channel static FP8 weights + per-token dynamic FP8 activations; linear layers only. Tensor types F32 + F8_E4M3.
- Shards total **~10.9 GB** on disk (5.00 + 3.72 + 2.18 GB — larger than the theoretical ~7.6 GB because non-linear tensors are kept in F32).
- Card shows the vLLM usage: `LLM(model=..., task="embed")` then `.embed(texts)`.
- Eval results marked "private" on the card — no public quality numbers.
- FP8 compute needs Ada/Hopper (RTX 4080 = Ada, qualifies).

#### 6. Other formats

- CoreML (Apple): https://huggingface.co/rsvalerio/nomic-embed-code-coreml
- **No GPTQ build exists on HF** as of today (searched the quantized-from listing + HF search). The AWQ-W4A16 compressed-tensors repo fills that niche.
- **Ollama registry**: https://ollama.com/manutic/nomic-embed-code — `latest` = 7.5 GB (Q8_0-sized), `7b` = 14 GB (f16), 32K context, 6,715 pulls. No official `library/nomic-embed-code` (only nomic-embed-text and nomic-embed-text-v2-moe are official).

### How to serve it

**llama.cpp** (the path Nomic documents themselves, from the official GGUF README):
```bash
llama-server -m nomic-embed-code.Q4_0.gguf --embeddings --pooling last
```
- `--pooling last` is **mandatory** — this is a last-token-pooled decoder embedder; default/mean pooling gives wrong vectors.
- Exposes OpenAI-compatible `POST /v1/embeddings`. Nomic's README includes a worked example (factorial query vs FizzBuzz doc → 0.49 vs 0.32 similarity) usable as a smoke test that pooling+prefix are right.
- llama.cpp embedding quants are first-class: any of the GGUF files above work; `-ngl 99` to fully offload to GPU; `--ctx-size` / `--ubatch-size` control the activation buffer.

**Ollama**: pulls Qwen2-arch embedding GGUFs fine. Either `ollama pull manutic/nomic-embed-code` or pull a specific official quant straight from HF: `ollama pull hf.co/nomic-ai/nomic-embed-code-GGUF:Q4_K_M`. Use the `/api/embed` endpoint. (Inferred from Ollama's standard hf.co-GGUF support + the manutic listing; not execution-verified here.)

**vLLM**: serve as a pooling model — `vllm serve <model> --runner pooling` (newer versions; older flag was `--task embed`). https://docs.vllm.ai/en/v0.19.0/models/pooling_models/embed/
- vLLM's embedding-usages docs tree explicitly carries quantization examples for pooling models: **AutoAWQ, BitsAndBytes, FP8 W8A8, GGUF, GPTQModel** — i.e., quantized embedding serving is a documented vLLM path, not a hack.
- The AWQ-W4A16 (compressed-tensors) and FP8-dynamic repos above are the vLLM-native quants; vLLM auto-detects compressed-tensors from config.
- Default pooling for converted models is "normalized hidden state of the last token" — which matches this model's last-token pooling, and the base repo carries sentence-transformers config metadata.
- Caveat from our own stack: vLLM holds its full VRAM allocation while resident (`gpu_memory_utilization`); for a 16 GB card sharing with a chat model, llama.cpp's exact-footprint serving is the friendlier resident embedder. (Inferred from our vLLM ops experience, not from this research.)

### VRAM at fp16 / 8-bit / 4-bit

Weights are the dominant term — embedding inference is single-forward-pass, no generative KV-cache growth. Add ~0.5–1.5 GB for activations/context buffer depending on batch size and ctx (a full 32k fp16 KV buffer for this GQA config is ~1.9 GB; typical chunk-embedding at 2–8k ctx needs far less).

| Precision | Weights on disk | Realistic serve VRAM (full GPU offload) |
|---|---|---|
| fp32 (original safetensors) | 28.3 GB | not viable on consumer cards |
| fp16 / bf16 | 14.15 GB | ~15–17 GB → **does not coexist with anything on a 16 GB RTX 4080** |
| Q8_0 / 8-bit | 7.52 GB | ~8–9 GB |
| FP8-dynamic (vLLM) | ~10.9 GB disk (F32-kept tensors) | card claims ~50% memory vs fp16 → ~8–9 GB |
| Q6_K | 5.81 GB | ~6.5–7 GB |
| Q5_K_M | 5.07 GB | ~6 GB |
| Q4_K_M / AWQ W4A16 | 4.38 / 4.46 GB | ~5–5.5 GB |
| IQ3_M (imatrix) | 3.34 GB | ~4 GB |
| Q2_K / IQ2 | 2.8 / 2.3–2.6 GB | ~3–3.5 GB |

### Reported quality loss for retrieval

**Direct measurements on nomic-embed-code: none published.** The AWQ card claims <1% without numbers; the FP8 card's eval is private; no MTEB/CodeSearchNet runs of the GGUF quants were found. What exists is adjacent evidence:

1. **Nomic's own per-quant guidance** (table above) — they recommend Q6_K/Q5/Q4_K as the floor of "recommended," call Q3_K_S not-recommended, Q2_K "surprisingly usable." That's the model authors' own quality read on their quants.

2. **Closest measured analogue — jina-embeddings-v4 GGUF** (also a Qwen2.5-based decoder embedding model, so the quant-sensitivity profile should transfer): https://github.com/jina-ai/jina-embeddings-v4-gguf — NDCG@5 on NanoHotpotQA:
   - F16 0.7940 (baseline) · Q8_0 0.7938 (~0%) · Q6_K 0.7951 (~0%) · Q5_K_M 0.7927 (~0%) · **Q4_K_M 0.8029 (+1%)** · IQ3_M 0.8106 (+2%) · IQ2_XXS 0.7236 (−9%) · IQ1_S 0.6369 (−20%).
   - Pattern: **retrieval quality is essentially flat from F16 down through 4-bit (sometimes noise puts Q4 above F16), and falls off a cliff below 3-bit.** Their pick: IQ3_S as the size/speed sweet spot.

3. **General findings**: 8-bit weight quantization ≈ negligible retrieval loss is the consistent result across studies (HF embedding-quantization blog https://huggingface.co/blog/embedding-quantization — note: that blog is about quantizing output vectors, a separate axis; arXiv https://arxiv.org/html/2501.10534v1 finds 8-bit "maintains retrieval accuracy with only slight degradation" and group-wise quantization alleviates 4-bit loss — exactly what Q4_K/AWQ-g128 do).

4. **Operational quality risks bigger than quantization** (from the serving docs + community threads):
   - Wrong pooling (`--pooling last` missing) or missing query prefix degrades retrieval far more than any ≥4-bit quant.
   - Embed the corpus and the queries with the **same served artifact** — don't mix an fp16-embedded corpus with Q4-embedded queries; cross-precision vectors are close but the deltas compound at ranking margins. (Inferred from the quant-delta data; not separately benchmarked.)

### Read for our stack (16 GB RTX 4080, resident alongside chat model)

- **Q6_K (5.81 GB) or Q5_K_M (5.07 GB) GGUF via llama.cpp `--embeddings --pooling last`** is the evidence-backed sweet spot: ~6–7 GB VRAM, measurably indistinguishable from fp16 on the closest analogue, Nomic-recommended, and llama.cpp's exact-footprint serving fits the company resource-manager model better than vLLM's reservation.
- AWQ W4A16 via vLLM is the option if we want it inside the existing vLLM loadout machinery (~5 GB weights + vLLM overhead) — but its <1% claim is unverified.
- fp16 is not a coexistence option on 16 GB; it's a "whole card" mode.
- Whatever quant is chosen, run Nomic's factorial/FizzBuzz smoke test + a small self-retrieval probe on our own corpus before committing the index — that converts the analogue evidence into Verified for our artifact.

## Lane 2 · small code embedders

Researched 2026-06-11. Scope: best code-specific embedding models under ~2B params as of mid-2026. Evidence labels: everything below is **Observed** from the cited pages unless marked *Inferred*. Nothing here is Verified-by-use on our hardware/corpus yet.

### The benchmark landscape first (scores are NOT cross-comparable)

Three different scoreboards are in play, and vendors quote whichever flatters them:

- **CoIR** (Code Information Retrieval, ACL 2025) — 10 datasets, 8 retrieval tasks, nDCG@10 average. Official leaderboard: https://archersama.github.io/coir/ — **observed to be stale**: its top entry is SFR-Embedding-Code-2B_R at 67.41 and it lists neither Qodo-Embed (68.53), jina-code-embeddings, nor anything from 2026. GitHub: https://github.com/CoIR-team/coir
- **MTEB-Code / MTEB(Code, v1)** — the live comparison surface now (13 code datasets inside MTEB; https://huggingface.co/spaces/mteb/leaderboard). Qwen3, Granite R2, and LightOn all quote this.
- **Jina's "25 code retrieval benchmarks"** — jina's own extended suite (MTEB code splits + SWE-Bench, CommitPackFT, Spider, MBPP, CoSQA…). Their 78–79% numbers live on this suite, not raw CoIR.

So "X scored 79, Y scored 68" across rows below does not mean X>Y unless the suite matches. Same-suite comparisons are flagged inline.

### Comparison table (sub-~2B, code-capable)

| Model | Params | Ctx | Dim | License | Code score (suite) | Released | Serving |
|---|---|---|---|---|---|---|---|
| **LateOn-Code** (LightOn) | 130M | 2048 doc / 256 query (trained) | multi-vector (ColBERT-style) | not stated in blog — *unverified* | **74.12 MTEB-Code** (top of 100–300M class) | **2026-02-12** | PyLate, ONNX, ColGrep CLI (CPU-friendly); NOT single-vector → not vLLM/pgvector-shaped |
| **LateOn-Code-edge** (LightOn) | **17M** | same | multi-vector | not stated — *unverified* | 66.64 MTEB-Code | 2026-02-12 | same; int8 ONNX, runs on CPU |
| **jina-code-embeddings-1.5b** | 1.54B | 32,768 | 1536 (MRL 128–1536) | **CC-BY-NC-4.0** ⚠ | **79.04 avg / jina 25-bench suite**; 78.94 MTEB-Code avg (their eval) | 2025-09-04 | transformers, sentence-transformers, **vLLM (on card)**, GGUF 1–4 bit |
| **jina-code-embeddings-0.5b** | 494M | 32,768 | 896 (MRL 64–896) | **CC-BY-NC-4.0** ⚠ | 78.41 avg / same suite; 78.72 MTEB-Code avg (their eval) | 2025-09-04 | same (vLLM usage on card; GGUF) |
| **Qwen3-Embedding-0.6B** | ~0.6B | 32K | 1024 (MRL 32–1024) | **Apache-2.0** | **75.41 MTEB-Code** (Qwen's eval); 73.49 on jina's suite (same suite as jina's 78.41 → jina-0.5b beats it there) | 2025-06-05 | **vLLM native (≥0.8.5)**, sentence-transformers, transformers, TEI; GGUF/Ollama exist *(Inferred — community builds; not on official card)* |
| **Qodo-Embed-1-1.5B** | 1.5B (gte-Qwen2-1.5B-instruct backbone) | 32K | 1536 | **QodoAI-Open-RAIL-M** ⚠ (use-restriction license) | **68.53 CoIR** (best open <7B at release, beat OpenAI + SFR-2B on CoIR) | 2025-02 | sentence-transformers, transformers (trust_remote_code); vLLM *(Inferred — Qwen2-arch embed models serve in vLLM; not documented on card)* |
| **CodeSage-large-v2** (Amazon) | 1.3B | **2048** ⚠ | 2048 (MRL) | Apache-2.0 | 64.18 CoIR (official leaderboard) | 2025-02 (v2) | transformers/sentence-transformers (remote code); no vLLM |
| **CodeSage-base-v2** | 356M | 2048 | 1024 (MRL) | Apache-2.0 | (below large; per-task numbers on card) | 2025-02 | same |
| **CodeSage-small-v2** | 130M | 2048 | 1024 (MRL) | Apache-2.0 | — | 2025-02 | same |
| **SFR-Embedding-Code-2B_R** (Salesforce CodeXEmbed) | 2B (at the cap) | — | — | **CC-BY-NC-4.0** ⚠ | 67.41 CoIR (#1 on stale official board) | 2025-01 | transformers/sentence-transformers (remote code) |
| **SFR-Embedding-Code-400M_R** | 400M | 8192 | — | **CC-BY-NC-4.0** ⚠ | 61.9 CoIR | 2025-01 | same |
| **CodeRankEmbed** (nomic-ai / CoRNStack) | 137M | 8192 | 768 | **MIT** | 60.1 CoIR; **77.9 MRR CodeSearchNet** | 2024-12 | sentence-transformers (trust_remote_code); vLLM *(Inferred — nomic-bert arch is in vLLM's model list; unverified for this checkpoint)* |
| **granite-embedding-311m-multilingual-r2** (IBM) | 311M | 32,768 | 768 (MRL→128) | **Apache-2.0** | 63.8 MTEB-Code | **2026-05-14** (newest found) | **vLLM, Ollama/llama.cpp, ONNX+OpenVINO CPU**, sentence-transformers |
| **granite-embedding-97m-multilingual-r2** | 97M | 32,768 | 384 | Apache-2.0 | 60.4 MTEB-Code | 2026-05-14 | same |
| **jina-embeddings-v2-base-code** (the old jina code model) | 161M | 8192 | 768 | Apache-2.0 | superseded by everything above | 2024 | transformers, sentence-transformers; widely packaged |

### Per-model notes

**LateOn-Code + ColGrep (LightOn, Feb 2026)** — https://huggingface.co/blog/lightonai/colgrep-lateon-code — the most interesting *new* thing this lane found.
- Late-interaction (multi-vector, ColBERT-style) rather than dense single-vector: per-token vectors, MaxSim scoring. 130M model hits **74.12 MTEB-Code** — within ~1.3 pts of Qwen3-Embedding-0.6B's 75.41 at ~5x smaller, and "strongly outperforming EmbeddingGemma-300M, closing in on much larger LLM-based models". The 17M edge model (66.64) beats IBM's 149M granite-english-r2 by 9.4 pts.
- Backbones: ModernBERT family (edge = Ettin-17M via mixedbread edge-colbert; full = GTE-ModernColBERT-v1). Pre-trained on CoRNStack (same corpus as CodeRankEmbed/nomic-embed-code), fine-tuned on CoIR data. Pretrain-only checkpoints also released for our own fine-tuning.
- **ColGrep**: Rust CLI, ONNX runtime, tree-sitter parsing for 23 languages, incremental hash-based indexing, fully local, "reproduces the grep interface agents already know, augmented with semantic ranking". Their agent eval: 70% win-rate vs vanilla grep, 15.7% token savings, 56% fewer search calls. Repo: https://github.com/lightonai/next-plaid/tree/main/colgrep
- Trade-offs: multi-vector index ≠ pgvector/Qdrant single-vector row — needs PLAID-style storage (their Next-Plaid) or PyLate. Context trained at 2048-doc. License not stated in the blog post — **must check the HF model cards before adoption**.

**jina-code-embeddings 0.5b/1.5b (Sep 2025)** — https://jina.ai/news/jina-code-embeddings-sota-code-retrieval-at-0-5b-and-1-5b/ · https://huggingface.co/jinaai/jina-code-embeddings-0.5b
- Qwen2.5-Coder backbones, last-token pooling, 32K ctx, Matryoshka dims, five task-prefix instructions (nl2code / qa / code2code / code2nl / code2completion — retrieval quality depends on sending the right prefix).
- Highest raw numbers of any sub-2B code embedder found: 0.5b = 78.41, 1.5b = 79.04 on their 25-benchmark suite; on that same suite Qwen3-Embedding-0.6B = 73.49, voyage-code-3 = 79.23 (API), gemini-embedding-001 = 77.38, jina-embeddings-v4 (3.8B) = 74.11. i.e. the 0.5b beats models 5–8x its size.
- **License blocker: CC-BY-NC-4.0** (commercial use needs a Jina deal). GGUF 1–4 bit exists (https://huggingface.co/jinaai/jina-code-embeddings-1.5b-GGUF), vLLM usage is documented on the card.

**Qwen3-Embedding-0.6B (Jun 2025)** — https://qwenlm.github.io/blog/qwen3-embedding/ · https://huggingface.co/Qwen/Qwen3-Embedding-0.6B
- **75.41 MTEB-Code**, Apache-2.0, 32K ctx, instruction-aware (+1–5% with task instructions), MRL 32–1024 dims, native vLLM. The best *permissive-license, vLLM-native* code-capable embedder under 2B found in this sweep. General-purpose too (multilingual MTEB 64.33) — one resident model could cover prose + code lanes.

**Qodo-Embed-1-1.5B (Feb 2025)** — https://huggingface.co/Qodo/Qodo-Embed-1-1.5B · https://www.qodo.ai/blog/qodo-embed-1-code-embedding-code-retrieval/
- CoIR **68.53** — above SFR-2B_R (67.41) and "surpassing larger 7B models" at release; 9 languages. Built on gte-Qwen2-1.5B-instruct, 1536-dim, 32K ctx.
- License is **QodoAI-Open-RAIL-M** — RAIL = behavioral use restrictions; commercial use broadly allowed but it is not Apache/MIT; needs a read before adoption.

**CodeRankEmbed 137M (Dec 2024)** — https://huggingface.co/nomic-ai/CodeRankEmbed
- MIT, 8192 ctx, Snowflake arctic-embed-m-long backbone, trained on CoRNStack (21M curated pairs, InfoNCE). CSN 77.9 MRR / CoIR 60.1. **Requires the literal query prefix** "Represent this query for searching relevant code". Paper: https://arxiv.org/abs/2412.01007. Still the strongest *MIT-licensed tiny dense* option; now outclassed on MTEB-Code by LateOn-Code (74.12 @ 130M, but multi-vector).

**CodeSage v2 (small/base/large)** — https://huggingface.co/codesage/codesage-large-v2
- Apache-2.0, Matryoshka, Stack-V2 contrastive training, 9 languages. Main liability: **2048-token context** (vs 32K elsewhere) and custom remote-code arch (no vLLM). Large-v2 = 64.18 CoIR.

**SFR-Embedding-Code / CodeXEmbed (Salesforce)** — https://huggingface.co/Salesforce/SFR-Embedding-Code-400M_R · paper https://arxiv.org/abs/2411.12644
- The 400M_R (61.9 CoIR, 8192 ctx) and 2B_R (67.41 CoIR) are both **CC-BY-NC-4.0** — research-only for us. The 7B sibling held the CoIR crown before Qodo. Mostly relevant as benchmark anchors now.

**Granite-Embedding-R2 multilingual (IBM, May 2026 — newest release found)** — https://huggingface.co/blog/ibm-granite/granite-embedding-multilingual-r2
- 97M/311M, Apache-2.0, **32K ctx**, explicit code-retrieval training (Python, Go, Java, JS, PHP, Ruby, SQL, C, C++) incl. cross-lingual code search; MTEB-Code 60.4/63.8. Not the top scorer, but the best *ops story* of the small ones: vLLM + Ollama/llama.cpp + ONNX/OpenVINO CPU paths all first-party, plus 200-language multilingual coverage in the same model.

### Over-the-cap / API context anchors (not candidates, for calibration)

- **nomic-embed-code 7B** — Apache-2.0, CoRNStack-trained, 81.7% Python / 80.5% Java CodeSearchNet; Lane 1's subject. https://huggingface.co/nomic-ai/nomic-embed-code
- **voyage-code-3** — API-only, 32K ctx; 79.23 on jina's suite — the jina-1.5b matches it locally. https://modal.com/blog/6-best-code-embedding-models-compared
- **jina-embeddings-v4 (3.8B)** — has a code adapter but scores *below* jina-code-0.5b on code (74.11 vs 78.41, same suite).
- **jina-embeddings-v5** (Feb–May 2026, 0.2B/0.6B text + 1B/2B omni) — newest jina generation, CC-BY-NC-4.0, **no code-retrieval scores published**; no v5 code model exists yet. https://huggingface.co/jinaai/jina-embeddings-v5-text-small
- **EmbeddingGemma-300M** (Google, Sep 2025) — general-purpose small model often recommended for its open license; LightOn's blog shows LateOn-Code-130M "strongly outperforming" it on MTEB-Code.

### Lane 2 read (provisional, for the cross-lane synthesis)

- **Permissive + vLLM-native + strong + dual-purpose:** Qwen3-Embedding-0.6B (Apache-2.0, 75.41 MTEB-Code, 32K, MRL) is the safe registry default for a code lane on our stack.
- **Highest sub-2B retrieval quality:** jina-code-embeddings-1.5b (and even 0.5b) — but CC-BY-NC-4.0 is a real blocker the moment the Company is commercial; otherwise it matches voyage-code-3 locally at ~1GB-class weights.
- **The 2026 wildcard:** LateOn-Code 130M — near-Qwen3 quality at 130M, CPU-viable, ships with an agent-shaped retrieval CLI (ColGrep) that matches our grep-replacement use-pattern. Cost: multi-vector storage breaks the "one pgvector/Qdrant column" assumption and license needs confirming. Worth a hands-on probe.
- **MIT tiny dense fallback:** CodeRankEmbed 137M. **Best ops/multilingual small:** Granite R2 311M.
- All scores above are vendor/leaderboard numbers (**Observed** from cited pages, none Verified on our corpus). Per the Lane 1 pattern: whatever shortlist survives the license filter should get a self-retrieval probe on the Company's own repo before any index is committed.

Sources: https://archersama.github.io/coir/ · https://github.com/CoIR-team/coir · https://huggingface.co/blog/lightonai/colgrep-lateon-code · https://jina.ai/news/jina-code-embeddings-sota-code-retrieval-at-0-5b-and-1-5b/ · https://huggingface.co/jinaai/jina-code-embeddings-0.5b · https://qwenlm.github.io/blog/qwen3-embedding/ · https://huggingface.co/Qwen/Qwen3-Embedding-0.6B · https://huggingface.co/Qodo/Qodo-Embed-1-1.5B · https://www.qodo.ai/blog/qodo-embed-1-code-embedding-code-retrieval/ · https://huggingface.co/nomic-ai/CodeRankEmbed · https://huggingface.co/codesage/codesage-large-v2 · https://huggingface.co/Salesforce/SFR-Embedding-Code-400M_R · https://huggingface.co/blog/ibm-granite/granite-embedding-multilingual-r2 · https://huggingface.co/jinaai · https://huggingface.co/jinaai/jina-embeddings-v5-text-small · https://modal.com/blog/6-best-code-embedding-models-compared · https://arxiv.org/abs/2412.01007 · https://arxiv.org/abs/2411.12644

## Lane 3 · the frontier (open scan)

Researched 2026-06-11. Open-ended web scan per the directive "look for the latest available, don't only research what you already know to ask for." Everything below is Observed-from-source (page/announcement says it) unless marked Inferred; nothing here is Verified-by-us on our hardware. Dates and sizes carried with every item so later passes can re-check.

### The headline shifts (mid-2025 → mid-2026)

1. **Multimodal embedding went from exotic to default.** Every major lab shipped a unified text+image(+video/audio) embedding space in the last ~8 months: Qwen3-VL-Embedding (Jan 2026, open), Gemini Embedding 2 (Mar 2026, API), jina-embeddings-v5-omni (May 2026, open-weights NC), Amazon Nova Multimodal (Oct 2025, API). "One index, all media" is the new product framing.
2. **Small open text embedders got dramatically better via distillation.** 97M–677M models now post numbers that needed 4B–8B a year ago (jina-v5-text, Granite R2, EmbeddingGemma). The 7B-embedder era is ending for text-only.
3. **Contextual embeddings productized.** Embedding a chunk *with respect to its surrounding document* is now a model feature (pplx-embed-context-v1), not just a trick (late chunking / Anthropic contextual retrieval). There's a benchmark for it (ConTEB).
4. **Late-interaction/multi-vector crossed into infrastructure.** First dedicated workshop (LIR @ ECIR 2026), MUVERA in Qdrant's FastEmbed and a DeepLearning.AI course, OpenSearch shipping late-interaction support, 17M-param edge ColBERTs. The storage-cost objection is being engineered away (MUVERA/WARP/CRISP/token-pooling).
5. **Benchmark trust collapsed and was rebuilt.** MTEB top-list is acknowledged as overfit; the MTEB team shipped RTEB (Oct 2025) with *private held-out* retrieval sets, and DeepMind published LIMIT showing single-vector retrieval has *theoretical* ceilings — direct ammunition for multi-vector/hybrid designs.
6. **No BGE-M3 successor appeared.** BGE-M3 (568M, dense+sparse+multi-vector in one) remains un-replaced as a single hybrid artifact; the field replaced it *by role* instead (details below).

### New text embedding models (open weights first)

- **pplx-embed-v1 / pplx-embed-context-v1 — Perplexity, released 2026-02-26.** MIT license, weights on HF (https://huggingface.co/collections/perplexity-ai/pplx-embed). Two sizes: **0.6B → 1024-dim** and **4B → 2560-dim**. 32K context, ~30 languages (250B training tokens). Novel bits: *diffusion-based continued pretraining* to turn a causal LLM into a bidirectional encoder; **quantization-aware training so INT8 (4×) and binary (32×) embeddings work natively**; no instruction prefixes needed. Claimed: 4B matches Qwen3-Embedding-4B on MTEB (69.66 nDCG@10); context variant is SOTA on ConTEB (81.96). The context variant embeds passages conditioned on full-document context — the productized form of late chunking. https://research.perplexity.ai/articles/pplx-embed-state-of-the-art-embedding-models-for-web-scale-retrieval
- **jina-embeddings-v5-text — Jina/Elastic, released 2026-02-18.** Two sizes: **nano 239M** and **small 677M**. Built by "task-targeted embedding distillation" from larger teachers (paper: https://arxiv.org/html/2602.15547v1). Release blog claims small ≈ matches jina-v4 (3.8B) retrieval at 5.6× smaller (~63.3 avg over retrieval benchmarks), ≈67.0 MMTEB task-avg / ~71 MTEB-English-v2 (numbers approximate — snippets disagreed slightly between the blog, HF card, and announcement posts; re-check the HF cards before relying on a specific decimal). Matryoshka to extreme truncation (release blog touts 2KB→128 bytes, 94% compression). **License not confirmed in this scan — the omni siblings are CC BY-NC 4.0, so assume NC until checked** (Inferred). https://www.elastic.co/search-labs/blog/jina-embeddings-v5-text · https://huggingface.co/jinaai/jina-embeddings-v5-text-nano
- **Granite Embedding Multilingual R2 — IBM, released 2026-04-29 (Granite 4.1 family).** **Apache 2.0.** 97M-param variant + an unspecified larger one; 200+ languages; "dramatically increased context length"; positioned as SOTA-for-size on MTEB. The interesting property for us: genuinely permissive license at CPU-runnable size. Dimensions/benchmarks not in the announcement — needs a HF-card pass. https://research.ibm.com/blog/granite-4-1-ai-foundation-models
- **Standing champions, unchanged:** Qwen3-Embedding 0.6B/4B/8B (June 2025, Apache 2.0) is still the consensus open text king (8B ≈ 70.6 MTEB multilingual) per multiple 2026 roundups (https://www.baseten.co/blog/the-best-open-source-embedding-models/, https://app.ailog.fr/en/blog/news/embedding-models-2026); EmbeddingGemma 308M (Sept 2025) still the on-device pick (https://developers.googleblog.com/introducing-embeddinggemma/).

### Multimodal embedders — the big new front

- **★ Qwen3-VL-Embedding-2B/8B + Qwen3-VL-Reranker-2B/8B — Alibaba, released 2026-01-08. Apache 2.0.** The headline release for a self-hosted 16GB box. Text/images/**screenshots**/video + mixed inputs in one space. 2B: 2048-dim; 8B: 4096-dim; **MRL user-selectable 64–2048 (2B)**; 32K context; instruction-aware (task-specific instructions change the embedding); BF16, flash_attention_2 recommended. Dual-tower embedder + single-tower cross-attention reranker — a matched open multimodal retrieve→rerank pair, which didn't exist before. Benchmarks: 2B = 73.2 MMEB-v2, 63.87 MMTEB; 8B = 79.2 MMEB-v2-retrieval avg, 86.3 visual-document, 74.9 MMTEB-retrieval, 66.7 ViDoRe-v3. Third-party (Milvus, below) found the 2B *beating closed APIs on cross-modal tasks*. Repo: https://github.com/QwenLM/Qwen3-VL-Embedding · https://huggingface.co/Qwen/Qwen3-VL-Embedding-2B · paper https://arxiv.org/abs/2601.04720 · https://www.alibabacloud.com/blog/qwen3-vl-embedding-and-qwen3-vl-reranker-for-the-next-generation-of-multimodal-retrieval_602796. Inferred (not verified by us): 2B at BF16 ≈ 4–5 GB VRAM — coexistence with our resident chat model is plausible but must be proven through `company up` telemetry.
- **jina-embeddings-v5-omni — Jina under Elastic (Elastic acquired Jina's model line; announcement is Elastic's), released 2026-05-11.** **The first sub-2B open-weights model family covering text+image+video+AUDIO in one vector space.** Two sizes: **omni-small ~1.74B, 1024-dim** and **omni-nano ~1.04B**. MRL truncation 32→1024 with L2 renorm; 32K context; last-token pooling; BF16; PDFs supported as input. Architecture is notable: frozen modality towers joined by tiny (~5.5M-param) cross-modal projectors, "geometry-preserving" (paper: https://arxiv.org/html/2605.08384v2). Claims best-in-class on MIEB-Lite (image), MMEB-V (video), MAEB (audio) under 2B. **License: CC BY-NC 4.0 — non-commercial. That's a real constraint for the Company; usable for experiments, not for anything revenue-touching without a Jina/Elastic license.** https://huggingface.co/jinaai/jina-embeddings-v5-omni-small · https://www.elastic.co/search-labs/blog/jina-embeddings-v5-omni-all-media-one-index · https://www.businesswire.com/news/home/20260511351933/en/
- **Gemini Embedding 2 — Google, public preview 2026-03-10. API-only.** Google's first *natively multimodal* embedding: text (8K tokens), images (≤6/request), video (≤120s), audio (no transcription step), PDFs (≤6 pages), **interleaved multi-modality in a single request**. 3072-dim default, MRL → 1536/768. 100+ languages. No open weights. https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-embedding-2/
- **Amazon Nova Multimodal Embeddings — AWS Bedrock, 2025-10-28. API-only.** Text/docs/images/video/audio unified. https://aws.amazon.com/blogs/aws/amazon-nova-multimodal-embeddings-now-available-in-amazon-bedrock/
- **Independent 2026 comparison worth keeping (Milvus, 2026-03-26):** benchmarked 10 models on cross-modal / cross-lingual / long-doc / dimension-compression. Verdicts: Gemini Embedding 2 best all-rounder (cross-lingual 0.997); **Qwen3-VL-2B top cross-modal (0.945), beating closed APIs**; Voyage Multimodal 3.5 best dimension-compression (0.880 ρ); jina-v4 strong MRL (0.833); BGE-M3 still solid cross-lingual (0.940) at 568M; mxbai-embed-large and nomic-embed-text effectively monolingual (cross-lingual 0.120 / 0.154). https://milvus.io/blog/choose-embedding-model-rag-2026.md

### Rerankers

- **jina-reranker-v3 — Sept–Oct 2025.** 0.6B (Qwen3-0.6B backbone + MLP projector 1024→512→256), multilingual, **"last but not late interaction"** — a *listwise* architecture that scores up to 64 documents in one forward pass with cross-document attention, rather than per-pair cross-encoding or per-token late interaction. 61.85 BEIR avg vs bge-reranker-v2-m3's 56.51 at the same size. A genuinely new reranker architecture class. https://huggingface.co/jinaai/jina-reranker-v3 · paper https://arxiv.org/html/2509.25085v3 (License: Jina's models trend CC BY-NC — check the card. Inferred.)
- **Qwen3-VL-Reranker-2B/8B — Jan 2026, Apache 2.0.** First strong open *multimodal* reranker (query+image/page/video candidate scoring via cross-attention). Pairs natively with Qwen3-VL-Embedding. https://huggingface.co/Qwen/Qwen3-VL-Reranker-2B
- **Cohere Rerank 4.0 (Fast + Pro) — April–May 2026. API-only** (Cohere API, Azure Foundry, OCI 2026-05-09, AWS Marketplace). The closed reference point current listicles compare against. https://docs.cohere.com/changelog/rerank-v4.0
- **Standing open defaults:** Qwen3-Reranker 0.6B/4B/8B (June 2025) and bge-reranker-v2-m3 remain what most 2026 self-hosted guides actually deploy; mxbai-rerank-v2 (Mar 2025) still cited. 2026 roundup for the landscape: https://futureagi.com/blog/best-rerankers-for-rag-2026/

### Late-interaction / multi-vector — research → infrastructure

- **LIR @ ECIR 2026** — first dedicated workshop on late interaction & multi-vector retrieval; its overview doubles as a field map: ColBERT→ColBERTv2/PLAID→ColPali (visual)→VideoColBERT (2025); efficiency line = token pooling (2024), **MUVERA** fixed-dimensional encodings (2024, makes multi-vector searchable by ordinary dense ANN), **WARP** engine (2025), **CRISP** cluster-based pruning (2025). Named open problems: storage/compute overhead, software-stack integration, theory of query augmentation, and **instruction-handling in agentic/reasoning retrieval** (i.e., late interaction doesn't yet follow instructions well). https://arxiv.org/html/2511.00444v1
- **MUVERA is mainstreaming:** Qdrant ships it in FastEmbed postprocessing (https://qdrant.tech/documentation/fastembed/fastembed-postprocessing/), OpenSearch shipped late-interaction support (https://opensearch.org/blog/boost-search-relevance-with-late-interaction-models/), and there's a Qdrant×DeepLearning.AI short course building a full ColPali+MUVERA multimodal RAG pipeline. Pattern: store one MUVERA-encoded dense vector for fast ANN, keep token vectors for exact late-interaction rescoring of the top-k.
- **mxbai-edge-colbert-v0 — Mixedbread, 2025-10.** ColBERTs at **17M and 32M params** (Ettin backbones, projection dim 48), long-context, claimed to outperform ColBERTv2 while being deployable "anywhere, including consumer CPUs." Late-interaction reranking at near-zero VRAM cost. https://huggingface.co/mixedbread-ai/mxbai-edge-colbert-v0-17m · https://www.mixedbread.com/blog/edge-v0 · tech report https://arxiv.org/html/2510.14880v1
- **PyLate** (LightOn) is the de-facto training/research framework; GTE-ModernColBERT and Reason-ModernColBERT (2025) are the current strong open checkpoints in that line.

### Closed-API frontier (awareness, not for our stack)

- **Voyage 4 family — 2026-01-15, now MongoDB-owned, API-only.** Notable architecture even if we can't run it: **MoE embedders with a shared embedding space across the whole family** — embed documents once with the big model, embed queries with the cheap small model, mix-and-match against the same index. That asymmetric pattern is worth stealing for our own registry (big-model corpus embeds + small-model query embeds only works if spaces are shared/aligned). https://blog.voyageai.com/2026/01/15/voyage-4/ · https://www.prnewswire.com/news-releases/mongodb-sets-a-new-standard-for-retrieval-accuracy-with-voyage-4-models-for-production-ready-ai-applications-302662558.html
- Gemini API also shipped a fully-managed RAG "File Search Tool" (Nov 2025) — signal that hosted RAG is being absorbed into model APIs. https://blog.google/innovation-and-ai/technology/developers-tools/file-search-gemini-api/

### Benchmarks & theory — what changed under our feet

- **RTEB (Retrieval Embedding Benchmark) — MTEB team, Oct 2025.** Retrieval-only, with **private held-out datasets** scored server-side so models can't train on the test set. Direct response to MTEB-leaderboard overfitting. Use RTEB rank, not MTEB-overall, when picking retrieval models. https://www.infoq.com/news/2025/10/rteb-benchmark/ · https://huggingface.co/spaces/mteb/leaderboard
- **LIMIT — Google DeepMind, Aug 2025.** Proof + dataset showing single-vector embeddings have *representational* limits: there exist simple relevance patterns no single-vector model can encode regardless of training; SOTA models score badly on a trivially-easy-looking dataset. The theoretical case for multi-vector / sparse / hybrid as architecture, not tuning. https://github.com/google-deepmind/limit
- **ConTEB** — benchmark for *context-conditioned* embeddings (does the model use surrounding-document context); pplx-embed-context-v1 currently tops it. New axis: MMEB-v2 (multimodal), MIEB-Lite (image), MMEB-V (video), **MAEB (audio — new)**, ViDoRe v3 (visual documents).
- Caveat from the scan itself: many "Best of 2026" listicles are stale or wrong (one top result still crowned NV-Embed-v2). Roundups ≠ evidence; the model cards and papers above are the ground truth.

### Technique currents (what people are building, not just shipping)

- **Context engineering > naive RAG** — RAGFlow's 2025 year-end review (https://ragflow.io/blog/rag-review-2025-from-rag-to-context): nothing replaced retrieval (long-context = overload+cost, KV-cache tricks don't scale, grep-only fails on unstructured data), but RAG is becoming a "context engine" assembling domain knowledge + tool metadata + memory. TreeRAG (LLM-built hierarchical doc trees, "locate precisely, then expand") over GraphRAG (entity extraction costs several-to-dozens× the original tokens and is noisy). This maps cleanly onto the Company's address/registry substrate — our addresses already are the tree.
- **Reasoning-intensive / agentic retrieval is the open frontier:** retrievers that follow instructions and serve multi-step agent loops are measurably weak; active 2026 work includes Critic-R (closing the agent↔retriever feedback loop, https://arxiv.org/html/2606.00590v1) and "Rethinking Reasoning-Intensive Retrieval" evals (May 2026). LIR lists instruction-handling as an open problem. Nothing settled to adopt yet — watch lane.
- **The BGE-M3 question answered by role, not by successor:** text-dense → Qwen3-Embedding / jina-v5-text / pplx-embed / Granite R2; multimodal → Qwen3-VL-Embedding; visual documents → ColPali-line or Qwen3-VL; hybrid sparse+dense → still BGE-M3's built-in sparse, or SPLADE-family + dense composed at the DB layer (Qdrant/OpenSearch both support it natively now). No single new artifact does all three the way BGE-M3 did.
- **Vector-DB layer: stable, with one new feature axis.** Qdrant / LanceDB / sqlite-vec / pgvector unchanged as the self-hosted set; the differentiator that moved in 2025-26 is **native multi-vector + MUVERA support** (Qdrant ahead here). No disruptive new local engine surfaced in this scan.

### What this means for our 16GB box (Inferred — none of this measured on our hardware yet)

- **The single most consequential release for us is Qwen3-VL-Embedding-2B + Reranker-2B**: Apache 2.0, instruction-aware, MRL 64–2048, screenshots-as-first-class-input (our canvas/surface screenshots become retrievable), ~4–5 GB BF16 (Inferred from 2B params; must verify via `company up --wait` + telemetry), and it slots into the existing vLLM/registry pattern alongside jina-v4.
- **pplx-embed-0.6B** is the interesting text candidate: MIT, 32K context, native INT8/binary embeddings (storage 4–32× down without a quantization-quality gamble), contextual variant available at the same size.
- **mxbai-edge-colbert-17M** makes late-interaction *rescoring* essentially free — pairs with MUVERA-style storage in Qdrant if we go multi-vector.
- **License tripwire:** the impressive Jina v5 line (text + omni) is CC BY-NC — fine to evaluate, not fine to build the Company's commercial spine on. Apache-2.0 lane: Qwen3-VL-Embedding, Qwen3-Embedding, Granite R2, EmbeddingGemma. MIT lane: pplx-embed.
- Open questions this lane leaves for the next pass: GGUF/AWQ availability for Qwen3-VL-Embedding-2B (none observed yet); actual VRAM coexistence with the resident chat loadout; jina-v5-text license confirmation; Granite R2 dims/benchmarks from the HF card; whether RTEB private-set ranks reorder our shortlist.
