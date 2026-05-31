# mcp/ — module constitution

**Is:** the agent face — a FastMCP server exposing the **generic verbs** the right-hand-man (and any agent) uses to drive everything (C7). Thin: it calls the same internal API the canvas's actions call.
**Guarantees:** verbs are **generic over node-type** — there is **no tool-per-node-type**; tools consult the registries to act on any type. `ToolAnnotations` (readonly/destructive/idempotent) are honest and feed governance (S7/D4). One brain, two faces (this + the canvas).
**Where new things go:** adding a node-type/model/source adds **zero tools**. A genuinely **new kind of operation** = one new verb (rare).
**To extend:** only add a verb for an operation the system never had; otherwise nothing here changes when the system grows.
**Seam:** implements C7; reads the registries (C2/S3); calls runtime; governed by S7.
**Never:** add a tool per node-type · leave a destructive verb unannotated · duplicate logic that belongs in the internal API.
