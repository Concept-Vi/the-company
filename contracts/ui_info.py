"""C1 (UI registry) — `/api/ui_info` serialization: UI components → frontend.

A SIBLING of `contracts.object_info`, not an extension of it. `object_info`
serializes the C2 `NodeType` library and is `NodeType`-hardwired (object_info.py
:46,74-78); UI components are a *different shape* — they are not node-types — so
this is a parallel registry, mirroring object_info's idiom (a Pydantic entry +
a `build_*` serializer keyed by a stable ref), never a coupling to NodeType.

This is the **addressing layer** behind `ui://<kind>/<ref>` (see
`contracts.address`). The `ui://` scheme is a label only; resolution is built
elsewhere (the runtime's `build_ui_info`/`ui_info` + the frontend resolver). This
module defines only the SHAPE the served map carries — what the RHM's `show`
verb validates against, and what the frontend dispatches on:

  ui://<kind>/<ref>
    kind=canvas → resolve via `camera_ref` (a node-id → editor camera, reuse)
    kind=chrome|field|panel|ext → resolve via `dom_handle` (a `data-ui-ref` value)

reflects-never-owns: this is a projection of what the UI exposes; it owns no UI
state, it only describes targets so they can be pointed-at / presented.

Schema-additive: new serialized fields carry defaults; an older frontend ignores
fields it doesn't know, so backend and frontend evolve at different speeds. A
breaking change is a new versioned shape side-by-side, never an edit-in-place.
See build-prep RHM Walkthrough Organ — Implementation Guide, section C1–C2.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

# Bumped when the SERIALIZATION shape changes (additively). Lets the frontend
# reason about which served fields it can expect. Mirrors object_info.SCHEMA_VER;
# distinct from any single record's own version marker.
SCHEMA_VER = 1


class Capabilities(BaseModel):
    """What the RHM may DO to a UI component — all default False (opt-in).

    A component declares only the capabilities it actually supports; an absent
    one reads False, so a target is never assumed actionable. Drives the `show`
    verb's affordances (point / spotlight / present / open / drive read-only).
    """

    pointable: bool = False        # `show` can point a cursor/arrow at it
    spotlit: bool = False          # `show` can highlight it (.ui-spotlight / select)
    presentable: bool = False      # its content can be presented in-place (portal/scroll)
    openable: bool = False         # it can be opened/expanded (e.g. a collapsed panel)
    drivenReadOnly: bool = False   # the RHM may drive it read-only (demonstrate, not mutate)


class UiComponentEntry(BaseModel):
    """One UI component in the served registry — the shape `show` codes against.

    `ref` is the `<ref>` in `ui://<kind>/<ref>` and the DICT KEY in the served
    map (matching object_info, where the node-type name is the key), so it is
    the stable handle the RHM addresses; it is repeated as a field here for
    round-tripping / validation, the same way object_info keys by name.

    Exactly one of `dom_handle` / `camera_ref` is meaningful per `kind`:
      kind=canvas → `camera_ref` (a node-id the frontend zooms the camera to)
      kind in {chrome, field, panel, ext} → `dom_handle` (the `data-ui-ref` value
        the frontend resolves with `querySelector('[data-ui-ref="..."]')`).
    Both are optional with `None` defaults — schema-additive — so neither is
    required for a component that only needs a title + capabilities.
    """

    ref: str
    kind: Literal["chrome", "field", "canvas", "panel", "ext"]
    title: str
    capabilities: Capabilities = Field(default_factory=Capabilities)
    # camelCase on the wire (`domHandle`/`cameraRef`) to match the served shape
    # the frontend resolver reads (Implementation Guide C1–C2, line 70); the
    # Python field stays snake_case. Emit with `model_dump(by_alias=True)`.
    dom_handle: str | None = Field(default=None, alias="domHandle")
    camera_ref: str | None = Field(default=None, alias="cameraRef")
    version: int = 1

    model_config = {"populate_by_name": True}


def build_ui_info(entries: list[UiComponentEntry]) -> dict:
    """Serialize the UI-component registry for the frontend.

    Returns a plain JSON-serializable dict: ``{ "<ref>": { ...fields... } }`` —
    mirroring `object_info.build_object_info`'s ``{ "<name>": {...} }``. The CORE
    lane's runtime `build_ui_info`/`ui_info` projects the live registry through
    this shape; this is the contract both sides agree on.

    Keys are emitted in the served (wire) casing via `by_alias=True`, so
    `domHandle`/`cameraRef` match what the frontend resolver querySelects /
    reads — the rest stay as declared.

    Fail loud (rule 4): a non-`UiComponentEntry` value, or a duplicate `ref`
    (two components claiming the same address — one source would be violated),
    raises rather than emitting a silently-wrong or last-write-wins registry.
    """
    out: dict = {}
    for entry in entries:
        if not isinstance(entry, UiComponentEntry):
            raise TypeError(
                f"/ui_info: entry is {type(entry).__name__}, expected "
                f"UiComponentEntry"
            )
        if entry.ref in out:
            raise ValueError(
                f"/ui_info: duplicate ref {entry.ref!r} — two UI components "
                f"claim the same ui:// address; one source (rule 3) violated"
            )
        out[entry.ref] = entry.model_dump(mode="json", by_alias=True)
    return out
