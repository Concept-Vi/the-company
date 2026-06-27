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
# v2 (S0, Interactive Addressed Surface): adds the canonical `ui://` grammar +
# the UnionAddressRecord (the one per-address shape both the corpus and the live
# UI_REGISTRY validate against). Additive — the v1 UiComponentEntry/build_ui_info
# above are UNCHANGED; the existing `/api/ui_info` consumers keep reading them.
# v3 (page-as-a-face): adds the OPTIONAL `page` field — a rendered HTML face bound
# to an address (the strong-version artifact: a page is a field an address accumulates,
# served live on a SEPARATE origin with a no-script CSP). Additive (rule 2): an
# address with no page still validates; `page` is None by default. See runtime/page_face.py.
SCHEMA_VER = 3


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


# ──────────────────────────────────────────────────────────────────────────
# S0 · CONTRACT.0 — the ONE canonical `ui://` address grammar (Interactive
# Addressed Surface, criteria line 5 + design-substrate CONTRACT.0/.1).
#
# THE PROBLEM S0 SOLVES (the grammar reconciliation):
#   Two non-interoperable grammars exist today.
#     • Corpus (design/_system/addresses.json, the mockups):
#         element-level, region-keyed, FULL-string `data-ui-ref` carrier,
#         capabilities = LIST of strings, scheme `ui://<region>/<element>`.
#         e.g. ui://inbox/build-review · ui://toolbar/run · ui://inbox (region-only).
#     • Live app (Suite.UI_REGISTRY, FE `data-ui-ref`):
#         region-level, KIND-keyed, scheme `ui://<kind>/<ref>`, kind ∈
#         {chrome,field,canvas,panel,ext}, capabilities = OBJECT of bools.
#         e.g. ui://chrome/inbox · ui://canvas/<node-id>.
#   A corpus `ui://inbox/build-review` does NOT resolve against the live app, and
#   the live `ui://chrome/inbox` is not in the corpus. Only `canvas` overlaps.
#
# THE RECONCILIATION (the lead's call, baked into the criteria):
#   The GRAMMAR is purely STRUCTURAL — `ui://` + one-or-more `/`-segments +
#   optional `[/@state]`. It is permissive ON PURPOSE so BOTH the corpus
#   element-form, the corpus region-only form (`ui://inbox`), AND the live
#   kind-form (`ui://chrome/inbox`) all parse. The SEMANTICS (kind vs region)
#   live in the RECORD, not the string — `kind` and `region` are EXPLICIT
#   fields populated per-side. So:
#     • the string grammar = the shape (the segment structure)
#     • the union RECORD = the teeth (valid kind, non-empty region, bool-caps).
#   The conformance check (S0) validates EACH side against this grammar+record
#   INDIVIDUALLY. It does NOT require the two address SETS to match (an address
#   on one side only is an orphan to reconcile — parse.py/check.py — NOT a
#   license to fabricate the missing entry; rule 8). It does NOT migrate the
#   live strings to region-first — that is S1 (a separate unit), not S0.
#
# Capabilities canonical encoding = bool-object (the live `Capabilities` shape
# the FE already reads). The corpus list-form normalizes to it, mapping the
# corpus vocabulary `driven` / `driven-read-only` → `drivenReadOnly`. An
# UNKNOWN capability string fails LOUD (rule 4) — never silently dropped.
# ──────────────────────────────────────────────────────────────────────────

import re as _re

# The kinds the LIVE resolver dispatches on (App.tsx: canvas→camera, else→DOM
# querySelector). An address's record MUST carry one of these — an address
# without a valid `kind` is unresolvable by the live mechanism (CONTRACT.1).
ADDRESS_KINDS = ("chrome", "field", "canvas", "panel", "ext")

# The canonical capability vocabulary = the live `Capabilities` Pydantic fields
# (bool-object). The corpus list-vocabulary maps INTO this — note `driven` and
# `driven-read-only` both fold to `drivenReadOnly` (the model has no plain
# `driven`; ui_info.py Capabilities, design-substrate CONTRACT.1).
CAPABILITY_FIELDS = ("pointable", "spotlit", "presentable", "openable", "drivenReadOnly")
_CORPUS_CAP_MAP = {
    "pointable": "pointable",
    "spotlit": "spotlit",
    "presentable": "presentable",
    "openable": "openable",
    "driven": "drivenReadOnly",            # corpus `driven` → the model's only read-drive cap
    "driven-read-only": "drivenReadOnly",
    "drivenreadonly": "drivenReadOnly",     # tolerate the already-canonical bool-key spelling
}

# `ui://` + ≥1 path segment, an OPTIONAL trailing state addressed as `/@state`
# OR `@state` (the criteria writes `[/@state]`; the corpus `_what` writes
# `@<state>` — tolerate both). Each segment is a non-empty run of chars that are
# not `/` and not the `@` that opens a state. The grammar is structural; it does
# NOT encode kind/region (those are record fields).
_SEG = r"[^/@]+"
_GRAMMAR_RE = _re.compile(
    r"^ui://"                       # the scheme
    r"(?P<segments>" + _SEG + r"(?:/" + _SEG + r")*)"   # ≥1 `/`-segment
    r"(?:/?@(?P<state>[^/@]+))?"    # optional `/@state` or `@state`
    r"$"
)


def parse_ui_address(address: str) -> dict:
    """Parse a `ui://` address against the ONE canonical grammar.

    Returns {address, segments:[...], state:str|None}. The grammar is purely
    STRUCTURAL (segment shape) — it does NOT assert kind/region (those are the
    union RECORD's job). Both the corpus element-form (`ui://inbox/build-review`),
    the corpus region-only form (`ui://inbox`), and the live kind-form
    (`ui://chrome/inbox`) parse.

    Fail loud (rule 4): a non-`ui://` string, or one with no segments, raises —
    never returns a silently-empty parse that a caller might read as valid.
    """
    if not isinstance(address, str):
        raise TypeError(f"ui address must be a string, got {type(address).__name__}")
    m = _GRAMMAR_RE.match(address)
    if not m:
        raise ValueError(
            f"ui address {address!r} does not match the canonical grammar "
            f"ui://<region>/<element>[/<sub>][/@state]"
        )
    segs = [s for s in m.group("segments").split("/") if s != ""]
    if not segs:
        raise ValueError(f"ui address {address!r} has no path segments")
    return {"address": address, "segments": segs, "state": m.group("state")}


def normalize_capabilities(caps) -> dict:
    """Normalize ANY capability encoding to the canonical bool-object.

    Accepts the corpus LIST form (`["pointable","driven"]`) OR an already-bool
    OBJECT (`{"pointable": true}`) OR a `Capabilities` model. Maps the corpus
    vocabulary (`driven`/`driven-read-only` → `drivenReadOnly`). Returns a dict
    with EVERY CAPABILITY_FIELD present (absent ⇒ False — opt-in).

    Fail loud (rule 4): an UNKNOWN capability string raises — it is never
    silently dropped (a silent drop would lose a real affordance and read as
    "this element can't do X" when the registry says it can).
    """
    out = {f: False for f in CAPABILITY_FIELDS}
    if caps is None:
        return out
    if isinstance(caps, Capabilities):
        caps = caps.model_dump(by_alias=True)
    if isinstance(caps, dict):
        for k, v in caps.items():
            key = _CORPUS_CAP_MAP.get(str(k), _CORPUS_CAP_MAP.get(str(k).lower()))
            if key is None:
                raise ValueError(
                    f"unknown capability {k!r} — not in the canonical vocabulary "
                    f"{sorted(_CORPUS_CAP_MAP)}; fix the registry, never silent-drop"
                )
            out[key] = bool(v)
        return out
    if isinstance(caps, (list, tuple, set)):
        for c in caps:
            key = _CORPUS_CAP_MAP.get(str(c), _CORPUS_CAP_MAP.get(str(c).lower()))
            if key is None:
                raise ValueError(
                    f"unknown capability {c!r} — not in the canonical vocabulary "
                    f"{sorted(_CORPUS_CAP_MAP)}; fix the registry, never silent-drop"
                )
            out[key] = True
        return out
    raise TypeError(
        f"capabilities must be a list/dict/Capabilities, got {type(caps).__name__}"
    )


class UnionAddressRecord(BaseModel):
    """The ONE canonical per-address record (S0 / design-substrate CONTRACT.1).

    The union of the corpus record (region, represents→feature, code) and the
    live `UiComponentEntry` (kind, capabilities bool-object). EVERY address —
    on either side — projects to this shape; that is what makes the two
    registries ONE grammar.

    Fields:
      address       — the full `ui://…` string (the stable key + the carrier).
      kind          — chrome|field|canvas|panel|ext; the field the LIVE resolver
                      dispatches on (canvas→camera, else→DOM). REQUIRED — an
                      address without a valid kind is unresolvable by the live
                      mechanism (CONTRACT.1 / the DON'T in the Guide).
      region        — the coarse grouping (e.g. "inbox"). REQUIRED non-empty.
      capabilities  — the canonical bool-object (normalize_capabilities).
      represents    — the feature-id → the inventory (corpus). OPTIONAL: the 7
                      live entries carry none (rule 8 — don't fabricate a join).
      code          — the powering code ref → the `code://` symbol (corpus;
                      S3 resolves it to a file scope). OPTIONAL, same reason.
      states        — applicable NODE_STATES ids for `@state` addressing. OPT.
      tier          — governance posture for COMMANDS at this address (feeds I4).
                      OPTIONAL — proposed, not all addresses carry it yet.
      title         — human label (live). OPTIONAL.
      howto         — the FOUNDATIONAL AFFORDANCE stratum (D1): plain-language
                      what-this-is / what-you-can-do / how-to-change-it text for
                      this address — the help that resolves AT the locus (the
                      `_r2_howto_at` R2 stratum reads it; `address_help` joins it
                      as the how-to-USE leg). OPTIONAL with a None default — an
                      address with no authored help still validates (it just has
                      no how-to-use leg, and `address_help` degrades that leg
                      cleanly). DATA, not code — the resolution is generic over
                      any address (mode-parameterizable later, E1), never a
                      per-element branch (Tim's not-hardwired correction).

    Schema-additive (rule 2): every join/semantic field is OPTIONAL with a
    default, so a side that lacks it still validates — the record is the union,
    not the intersection.
    """

    address: str
    kind: str
    region: str
    capabilities: dict = Field(default_factory=lambda: {f: False for f in CAPABILITY_FIELDS})
    represents: str | None = None
    code: str | None = None
    states: list[str] = Field(default_factory=list)
    tier: str | None = None
    title: str | None = None
    howto: str | None = None
    page: dict | None = None        # v3: a rendered HTML face bound to this address (page-as-a-face).
                                    # Shape {source: "cas://…"|"blob://…", title?, content_type?} — the
                                    # page CONTENT lives at the content-addressed source; this field is
                                    # the binding. OPTIONAL/None (rule 2 — an address with no page still
                                    # validates). Served by runtime/page_face.py on a SEPARATE origin
                                    # under a no-script CSP (the escalation/XSS mitigation by construction).

    @classmethod
    def from_corpus(cls, address: str, rec: dict) -> "UnionAddressRecord":
        """Project a corpus addresses.json entry → the union record.

        Corpus entries carry NO `kind` (the field the live resolver needs); it
        is DERIVED here (region "canvas" → kind "canvas"; everything else →
        "chrome", the DOM-resolved default). region comes from the entry's
        `region` field. capabilities normalize from the list form.
        """
        parse_ui_address(address)                           # validate the string shape first
        region = rec.get("region") or ""
        kind = "canvas" if region == "canvas" else "chrome"
        return cls(
            address=address,
            kind=kind,
            region=region,
            capabilities=normalize_capabilities(rec.get("capabilities")),
            represents=rec.get("represents"),
            code=rec.get("code"),
            tier=rec.get("tier"),          # I4: governance action_class for COMMANDS at this address
            title=rec.get("title"),
            howto=rec.get("howto"),         # D1: the foundational affordance/how-to-use text (optional)
            page=rec.get("page"),           # v3: the page-as-a-face binding (optional; None if absent)
        )

    @classmethod
    def from_live(cls, ref: str, kind: str, title: str, caps) -> "UnionAddressRecord":
        """Project a live UI_REGISTRY entry → the union record.

        TWO row-forms now coexist in the live registry (S0 anticipated, S1 landed):
          • BARE-ref rows (the 9 region/chrome handles + the '*' canvas): `ref` is a
            bare handle ("inbox", "*"); the canonical ADDRESS is `ui://<kind>/<ref>`
            (the form the live resolver emits — suite.py show/`_registry_ui_target`).
            region = the ref; canvas → "canvas".
          • FULL-STRING rows (S1's 24 corpus element addresses): `ref` is ALREADY the
            full canonical string ("ui://inbox/build-review", region-first grammar) —
            the full-string carrier baked into the corpus/mockups. Here the ref IS the
            address (do NOT re-prefix `ui://<kind>/…` — that would double the scheme);
            region = the address's FIRST segment ("inbox").
        S0 left the bare strings as-is; S1 grew the registry with the corpus
        element-level rows whose ref is the full address (per the guide's S1 unit).
        """
        if ref.startswith("ui://"):
            # S1 full-string row — the ref IS the canonical address (region-first form).
            address = ref
            parsed = parse_ui_address(address)
            region = parsed["segments"][0] if parsed["segments"] else ""
        else:
            # bare-ref row — the canonical address is ui://<kind>/<ref> (the live resolver's form).
            address = f"ui://{kind}/{ref}"
            parse_ui_address(address)
            region = "canvas" if (kind == "canvas") else ref
        return cls(
            address=address,
            kind=kind,
            region=region,
            capabilities=normalize_capabilities(caps),
            title=title,
        )


def validate_address_record(rec: "UnionAddressRecord") -> list[str]:
    """The RECORD-shape teeth: return a list of problems (empty = conformant).

    Asserts what the permissive string grammar deliberately does NOT:
      • the address string parses against the canonical grammar,
      • `kind` ∈ ADDRESS_KINDS (the live resolver dispatch field),
      • `region` is non-empty,
      • every capability key is a canonical bool field.
    Returns problems rather than raising so a conformance check can ENUMERATE
    every failing address (fail loud at the surface, not on the first one).
    """
    problems: list[str] = []
    try:
        parse_ui_address(rec.address)
    except (ValueError, TypeError) as e:
        problems.append(f"{rec.address!r}: bad grammar — {e}")
    if rec.kind not in ADDRESS_KINDS:
        problems.append(
            f"{rec.address!r}: kind {rec.kind!r} not in {ADDRESS_KINDS} "
            f"(the live resolver dispatches on kind — an unknown kind is unresolvable)"
        )
    if not (rec.region or "").strip():
        problems.append(f"{rec.address!r}: empty region (every address needs a coarse grouping)")
    for k in rec.capabilities:
        if k not in CAPABILITY_FIELDS:
            problems.append(f"{rec.address!r}: non-canonical capability key {k!r}")
    return problems


def conform_corpus(addresses: dict) -> dict:
    """Validate a corpus `addresses.json` `{address: {...}}` map against the ONE
    grammar+record. Returns {records:{addr:record-dict}, problems:[...]}.

    Each address is projected to a UnionAddressRecord and validated. A parse or
    projection failure becomes a problem (enumerated, never a silent skip).
    """
    records, problems = {}, []
    for address, rec in (addresses or {}).items():
        try:
            ur = UnionAddressRecord.from_corpus(address, rec)
        except (ValueError, TypeError) as e:
            problems.append(f"{address!r}: {e}")
            continue
        problems.extend(validate_address_record(ur))
        records[address] = ur.model_dump(mode="json")
    return {"records": records, "problems": problems}


def conform_live(ui_registry) -> dict:
    """Validate the live UI_REGISTRY against the ONE grammar+record.

    `ui_registry` = the Suite.UI_REGISTRY shape: an iterable of
    `(ref, kind, title, handle_dict, caps_dict[, extras_dict])` tuples (the 6th
    element is the S0-additive union-extras dict, optional). Returns the same
    {records, problems} shape as conform_corpus.
    """
    records, problems = {}, []
    for row in (ui_registry or []):
        ref, kind, title, _handle, caps = row[0], row[1], row[2], row[3], row[4]
        try:
            ur = UnionAddressRecord.from_live(ref, kind, title, caps)
        except (ValueError, TypeError) as e:
            problems.append(f"live ref {ref!r}: {e}")
            continue
        problems.extend(validate_address_record(ur))
        records[ur.address] = ur.model_dump(mode="json")
    return {"records": records, "problems": problems}
