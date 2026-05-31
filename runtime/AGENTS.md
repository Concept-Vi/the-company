# runtime/ — module constitution

**Is:** the heart — the reactive scheduler (watch the store; a node fires the instant its input **addresses** resolve), the memo gate (skip nodes whose output-address already exists), the compile step (workflow→execution, C5), and context-variable resolution for the right-hand-man (C6). This is Invariant II made real (S1).
**Guarantees:** a node runs **only** when its inputs resolve · a cached node is **never** re-run and a cached model node **never** re-hits the GPU · pause/retry/branch are addressing operations (stop dispatch / clear an address / new `@branch`) · model dispatch passes a **VRAM semaphore** so the 16 GB card can't OOM · never blocks waiting on Tim.
**Where new things go:** a new context-variable → `context_variables/`. Scheduler logic stays **generic over node-type**.
**To extend:** register a `ContextVariable` (C6); never special-case a node-type inside the scheduler.
**Seam:** uses `store/` (C1/C4), operates on C3 records, runs `compile` (C5), resolves context (C6), calls `fabric/`.
**Never:** bake a node-type into the scheduler · bypass the memo gate · re-hit the GPU on a cached result · introduce a second "graph" notion (no workflow-engine; durability comes from the addressed store).
