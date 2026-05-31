"""FilesystemResolver — the addressed store (C4, skeleton form).

Stdlib-only so the walking skeleton has zero install risk. Content-addressed objects
(immutable), mutable refs (run://), provenance, and a memo index. Pydantic-typed
contracts arrive in stage E1; this proves the mechanism.
See store/AGENTS.md for the constitution (never mutate cas:// content; ext4 only).
"""
import hashlib
import json
from pathlib import Path


class FsStore:
    def __init__(self, root):
        self.root = Path(root)
        for d in ("objects", "refs", "meta", "memo"):
            (self.root / d).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _hash(b: bytes) -> str:
        return "b2:" + hashlib.blake2b(b, digest_size=16).hexdigest()

    @staticmethod
    def _safe(addr: str) -> str:
        return addr.replace(":", "_").replace("/", "__")

    # --- immutable content (cas://) ---
    def put_content(self, data) -> str:
        b = json.dumps(data, sort_keys=True).encode()
        cas = self._hash(b)
        p = self.root / "objects" / self._safe(cas)
        if not p.exists():            # immutable: write once, never mutate
            p.write_bytes(b)
        return cas

    def get_content(self, cas: str):
        return json.loads((self.root / "objects" / self._safe(cas)).read_bytes())

    def exists(self, cas: str) -> bool:
        return (self.root / "objects" / self._safe(cas)).exists()

    # --- mutable pointer (run://) ---
    def set_ref(self, logical: str, cas: str):
        (self.root / "refs" / self._safe(logical)).write_text(cas)

    def head(self, logical: str):
        p = self.root / "refs" / self._safe(logical)
        return p.read_text() if p.exists() else None

    # --- provenance + memo ---
    def write_provenance(self, prov: dict):
        (self.root / "meta" / (self._safe(prov["produced_by"]) + ".json")).write_text(
            json.dumps(prov, indent=2)
        )

    def memo_get(self, sig: str):
        p = self.root / "memo" / self._safe(sig)
        return p.read_text() if p.exists() else None

    def memo_set(self, sig: str, cas: str):
        (self.root / "memo" / self._safe(sig)).write_text(cas)
