# store/ — module constitution

**Is:** the addressed store + the resolver — turns an address into bytes and back. Implements C1 (grammar/provenance) + C4 (Resolver Protocol). Filesystem-first; Supabase later.
**Guarantees:** content at `cas://` is **immutable** — never mutated, never lost (an "update" is a new object + a moved pointer). Reads live truth. The store lives on **ext4 (`~/...`), never `/mnt/c`**. Every write records provenance (`inputs[]` → lineage to source). **Chat turns carry provenance too** — every `append_chat` records `source` (`operator` = Tim, `twin` = the model) and `grade` (`gold`/`working`); the twin's training signal is filtered to operator-gold so the model **never learns from its own output, even laundered back as a role-flipped 'user' turn** (the echo-guard against model-collapse). Any new chat-persist path MUST tag `source`, or the echo-guard silently fails open.
**Where new things go:** a new backend = a new `*_resolver.py` implementing the Protocol.
**To extend:** implement `Resolver` (read/write/head/exists/provenance); select by config; provide a one-time backfill. The graph never changes — that's the whole point of the indirection.
**Seam:** speaks C1 grammar; implements C4; called by `runtime/`.
**Never:** mutate `cas://` content · put a backend type above the Protocol · store the DB under `/mnt/c` · lose old versions · write a chat turn without a `source` tag (breaks the twin echo-guard).
