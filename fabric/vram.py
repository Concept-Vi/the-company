"""fabric/vram.py — the VRAM gate (S6). See fabric/AGENTS.md.

Bounds concurrent LOCAL model calls so the 16 GB card can't OOM (the reviewer flagged
this as an unmet runtime guarantee before model-nodes land). Cloud calls don't acquire
(they use no local VRAM). A real implementation would also read live `nvidia-smi`; this
is the concurrency bound — the per-model fit logic comes when local-model nodes land.
"""
from __future__ import annotations
import threading
from contextlib import contextmanager


class VramGate:
    def __init__(self, limit: int = 1):
        self.limit = limit
        self._sem = threading.Semaphore(limit)

    @contextmanager
    def slot(self):
        self._sem.acquire()
        try:
            yield
        finally:
            self._sem.release()
