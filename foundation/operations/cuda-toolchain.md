---
type: operations
title: CUDA toolchain (WSL, cu13.0 pinning)
date_started: 2026-05-27
tags: [foundation, operations, cuda, wsl]
---

# CUDA toolchain — WSL, cu13.0 pinning

> [[_operations-index|← Operations hub]]

This is the load-bearing operational fix for the entire vLLM substrate. Without the version pinning + linker symlinks documented here, vLLM's flashinfer JIT compilation fails and the engine doesn't load. The fix is in place as of 2026-05-26 and applies to `~/vllm-env/`.

## State

| Component | Pinned version | Path inside venv |
|---|---|---|
| nvidia-cuda-runtime | 13.0.96 | (Python package) |
| nvidia-cuda-cupti | 13.0.85 | |
| nvidia-cuda-nvrtc | 13.0.88 | |
| nvidia-nvtx | 13.0.85 | |
| nvidia-nvjitlink | 13.0.88 | |
| nvidia-cuda-nvcc | 13.0.88 | |
| nvidia-cuda-cccl | 13.0.85 | |
| nvidia-cuda-crt | 13.0.88 | |
| nvidia-nvvm | 13.0.88 | |

All pinned to `cu13.0.x` because torch 2.11.0+cu130 was built against CUDA 13.0. CCCL's compatibility check fails on major.minor mismatch — was discovered after vLLM came up with mixed cu13.0/cu13.2 packages.

## Linker symlinks

`flashinfer`'s ninja-driven JIT build expects libraries in specific locations and names. These symlinks bridge the layout difference between the pip-installed nvidia/cu13 packages and what flashinfer's build expects:

| Symlink | Target | Why |
|---|---|---|
| `~/vllm-env/lib/python3.12/site-packages/nvidia/cu13/lib64` | `lib` (sibling) | flashinfer looks in `lib64/`; nvidia/cu13 puts libs in `lib/` |
| `~/vllm-env/lib/python3.12/site-packages/nvidia/cu13/lib/libcudart.so` | `libcudart.so.13` | flashinfer's linker passes `-lcudart`; needs the unversioned `.so` symlink |
| `~/vllm-env/lib/python3.12/site-packages/nvidia/cu13/lib/libcuda.so` | `/usr/lib/wsl/lib/libcuda.so.1` | flashinfer's linker passes `-lcuda`; needs an unversioned `libcuda.so` |

The `libcuda.so` link target is the WSL-side stub library. It's a Linux ELF inside the WSL filesystem (despite the `/usr/lib/wsl/` path); resolved by the dynamic linker once at `dlopen` time. No per-CUDA-call overhead. The actual WSL ↔ Windows kernel transition for GPU work happens regardless of this symlink — the link is build-time scaffolding, not a runtime cost.

## Environment variables (set in service launchers)

```bash
export CUDA_HOME="$HOME/vllm-env/lib/python3.12/site-packages/nvidia/cu13"
export PATH="$CUDA_HOME/bin:$PATH"
export VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=0
```

`CUDA_HOME` is required because WSL has no system CUDA toolkit; everything lives in the pip-installed `nvidia/cu13/` tree. The `PATH` extension makes `nvcc` available to JIT compilers.

`VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=0` disables a CUDA graph memory estimate that was over-reserving VRAM. Models that fit tightly (Gemma-4-E4B-FP8 during early testing) would OOM on this estimate even though they actually fit at runtime.

`VLLM_USE_FLASHINFER_SAMPLER=0` was set as a workaround when flashinfer JIT was broken; **now unset** — the toolchain fix re-enabled flashinfer. Documented as historical context only; do not re-set unless flashinfer fails again.

## Why this matters operationally

When a new vLLM version is installed, or when `nvidia/cu13` packages get pulled in by a transitive dependency upgrade, the pinning can drift. Symptoms of drift:

- vLLM engine fails to start with `CUDA compiler and CUDA toolkit headers are incompatible` (the CCCL compatibility check)
- `flashinfer/jit/cpp_ext.py` errors with `Ninja build failed` and `cannot find -lcudart` or `cannot find -lcuda`
- vLLM falls back to slower sampling paths (sub-2x throughput observed during pre-fix tests)

Recovery procedure:

1. Verify versions: `~/vllm-env/bin/python -c "import importlib.metadata as m; [print(d.name, d.version) for d in m.distributions() if 'nvidia-cu' in d.name or 'nvidia-nvvm' in d.name]"`
2. Re-pin all to 13.0.x using the same `uv pip install` command used at original setup (see below)
3. Verify symlinks exist (the three listed above)
4. Restart the affected service

## Re-pin command (from the source archive)

```bash
source ~/vllm-env/bin/activate
uv pip install --upgrade \
  'nvidia-cuda-runtime==13.0.96' \
  'nvidia-cuda-cupti==13.0.85' \
  'nvidia-cuda-nvrtc==13.0.88' \
  'nvidia-nvtx==13.0.85' \
  'nvidia-nvjitlink==13.0.88' \
  'nvidia-cuda-nvcc==13.0.88' \
  'nvidia-cuda-cccl==13.0.85' \
  'nvidia-cuda-crt==13.0.88' \
  'nvidia-nvvm==13.0.88'

# Re-establish symlinks if needed
CU13=~/vllm-env/lib/python3.12/site-packages/nvidia/cu13
ln -sfn lib "$CU13/lib64"
ln -sf libcudart.so.13 "$CU13/lib/libcudart.so"
ln -sf /usr/lib/wsl/lib/libcuda.so.1 "$CU13/lib/libcuda.so"
```

## Side-by-side venvs

[[#jina-v4-env]] (at `~/jina-v4-env/`) does **not** have its own pinned cu13 toolchain. It reuses `~/vllm-env/lib/python3.12/site-packages/nvidia/cu13/` via the `CUDA_HOME` env var in its launcher. Means: this single toolchain fix covers both venvs. Means also: changes to the vllm-env toolchain affect jina-v4-env.

## Open at this topic

- vLLM version-upgrade procedure when 0.22+ becomes worth running (will likely shift CUDA dep pins; this whole topic file gets revised)
- Whether to keep `VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=0` long-term or remove once tight-VRAM cases are eliminated
- WSL kernel updates — historically Microsoft's WSL CUDA support has changed across releases; not currently affecting anything but a regression vector
- Native Linux dual-boot or migration — would remove the WSL constraints entirely; not on near-term radar

## Connects to

- [[_operations-index]] — hub
- [[runtimes]] — what depends on this
- [[troubleshooting]] — symptoms of toolchain drift
- Source: `~/vllm-tests/env.sh`, `~/vllm-tests/serve.sh`
