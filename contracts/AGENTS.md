# contracts/ — module constitution

**Is:** the pinned data shapes — C1 addresses · C2 node-type · C3 node-record · C4 resolver · C5 object_info/compile · C6 context-variable · C7 MCP tools · C8 bridge. The **spine** every other module composes against.
**Guarantees:** every shape carries `schema_ver`. Growth is **additive only** — new *optional* fields. A breaking change is a **new versioned shape side-by-side**, never an edit to an existing one. No backend types leak in here (shapes are storage-agnostic).
**Where new things go:** a new contract = a new file `Cn.py`; a new field = additive on the existing shape.
**To extend:** add an optional field + bump `schema_ver`; OR add a new versioned shape. Update the vault spec (`build-prep/contracts/`) to match — the vault is source of truth.
**Seam:** everything imports from here; this imports from nothing in the repo.
**Never:** break/rename/remove an existing field · couple a shape to a storage backend · change a contract without CONFIRM (it's the widest-blast-radius act).
