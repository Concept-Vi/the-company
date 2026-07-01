# System Map — Editor & Disk-Write Adapter

> Piece 5. The System Map's editor lets you reorganise the codebase **visually** — create, rename,
> duplicate, move (into/across folders), archive and delete files and folders, with animated reflow.
> The browser preview **cannot write project files**, so edits are non-destructive: they mutate the
> in-memory model, persist locally, and emit a typed **operation queue**. A disk-write **adapter**
> (run by Claude Code or any environment with filesystem access) replays that queue to make the
> changes real, after which a **Rescan** shows the true tree. This doc is the contract.

## What the editor produces

Toggle **Edit** in the topbar to show the editor toolbar. Each action acts on the selected node and
appends one operation to the queue (visible via **Operations**, exportable as JSON). Operation schema:

```jsonc
{
  "generatedFrom": 1733000000000,   // diskModel.generatedAt the edits were made against (staleness check)
  "ops": [
    { "op": "createFolder", "path": "axes/rhythm",          "parent": "axes",        "at": 1733… },
    { "op": "createFile",   "path": "axes/rhythm/rhythm-axis.js", "parent": "axes/rhythm", "at": … },
    { "op": "rename",       "from": "tokens/old.css",        "to": "tokens/new.css",  "at": … },
    { "op": "duplicate",    "from": "templates/pitch-deck",  "to": "templates/pitch-deck copy", "at": … },
    { "op": "move",         "from": "app/util.js",           "to": "core/util.js",    "at": … },
    { "op": "archive",      "from": "inspo/old-deck.pdf",    "to": "_archive/old-deck.pdf", "at": … },
    { "op": "delete",       "path": "screenshots/tmp.png",   "at": … }
  ]
}
```

All paths are **project-relative** and identical to a node's `id`/`path` in `system-map.json`. `move`,
`rename`, `archive` and `duplicate` of a folder carry the whole subtree (the editor already updates
descendant paths in-memory; the adapter moves/copies the directory recursively).

## Adapter algorithm (apply in array order)

For each op, in order (order matters — later ops may reference paths created/renamed by earlier ones):

| op | filesystem action |
|---|---|
| `createFolder` | `mkdir -p <path>` |
| `createFile`   | write empty file at `<path>` (create parent dirs if needed) |
| `rename`       | `mv <from> <to>` |
| `move`         | `mv <from> <to>` (ensure `dirname(to)` exists) |
| `archive`      | ensure `_archive/` exists, then `mv <from> <to>` |
| `duplicate`    | `cp -r <from> <to>` |
| `delete`       | `rm -rf <path>` (prefer moving to a trash dir if you want undo) |

Notes for a correct adapter:
- **Staleness guard.** Compare `generatedFrom` to the current `system-map.json` `generatedAt`; if the
  disk changed since (someone else edited), surface a conflict rather than blindly applying.
- **Idempotence / safety.** `createFolder`/`createFile` should no-op if the target already exists;
  `mv`/`cp` should refuse to overwrite (the editor already prevents name clashes in-memory, but guard
  anyway). Treat `delete` as destructive — consider a trash dir.
- **Compiler artifacts.** Never move/delete `_ds_bundle.js`, `_ds_manifest.json`,
  `_adherence.oxlintrc.json` (regenerated). Moving a `.jsx`/`.d.ts` component changes its compiled
  location — re-run `check_design_system` after applying.
- **Re-source after apply.** Regenerate `system/system-map.json` (run `build-system-map.js`) so the
  map's Rescan reflects reality, then have the user **Clear** the local edit queue (now applied).

## How the in-memory editor stays single-sourced

- The edited tree + op queue persist to `localStorage["cv-sysmap-edits-v1"]` as `{data, ops}` so a
  plain reload keeps your visual edits; **Rescan** re-reads disk truth; **Clear** discards local edits
  and reverts to the last scan. The 6-second auto-poll is suppressed while edits are pending so it
  can't clobber them.
- Structural mutation goes through `relocate()` (updates a node + its descendants' paths/ids and
  remaps edges/globals) and the create/duplicate/delete helpers; every change calls `morphEdit()`
  which recomputes the layout and FLIP-morphs survivors. There is **one** code path per op and the
  op queue is the single record of intent — the adapter is the only thing that touches disk.

## For Claude Code: building the live adapter

A minimal Node adapter: read the exported JSON (or `localStorage` dump), `for (const op of ops)`
switch on `op.op` and call the `fs`/`fs.promises` equivalents above, then shell out to regenerate
`system-map.json`. A richer version watches the queue file and applies incrementally, emitting a
result log the map can show. Keep the **op vocabulary** in sync with the editor: add an op type here
and in the editor's emit calls together — same as every other registry in this system, one home.
