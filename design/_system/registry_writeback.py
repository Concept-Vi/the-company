"""registry_writeback.py — RG9, the WRITE-BACK of the registry-generation chain.

WHAT THIS IS (the chain's last operative step). The V-A chain reads the mockup
surface → a swarm PROPOSES registry entries → Tim APPROVES one batch → *this*
runs. It takes a CONFIRMED set of dossier entries (the `register_element` role's
`output_schema`, reconciled + confirmed by the cascade) and performs the
round-trip that makes a once-dead element come alive:

  (a) MERGE the entries additively + dedup-safe into `addresses.json`
      (the canonical registry — the ONE truth, never a parallel one),
  (b) STAMP the `data-ui-ref="ui://…"` attribute into the mockup HTML at the
      element the dossier describes (located by its opening tag),
  (c) RE-RUN the parse (`parse.py:build_map`) so `element-map.json` regenerates
      and the newly-stamped element shows `registered: true` (leaves the
      `orphans.unregistered` list) — the JOIN that proves the round-trip.

Each merged entry carries PROVENANCE (introspective-data law): which `run://`
produced it, which model, the confidence.

★ OPERATOR-ONLY FLOOR (the sacred floor / the consent model). This is a
FUNCTION, NEVER auto-run. It runs ONLY after Tim approves a batch (RG8). It is
not wired to fire from the chain, the cron, or any auto-path; the only caller is
the approve-gate. git-revert is the second net.

★ FAIL LOUD (rule 4). Every ambiguity is an exception, never a guess:
  · an address that is not valid `ui://` grammar,
  · a content-conflict on an address already in the registry (the 82 curated),
  · a mockup file that doesn't exist,
  · an element the TWO-TIER locate (full outerHTML, then opening tag) cannot pin
    to EXACTLY ONE occurrence — not found (stale outerHTML) OR genuinely
    ambiguous (identical elements; needs RG1's selector to disambiguate) — both
    fail loud, because stamping the wrong element corrupts the map,
  · an element whose opening tag already carries a `data-ui-ref`.
A refused stamp is CORRECT under fail-loud + operator-only — the registry is the
one truth; corrupting it is worse than not growing it. The caller surfaces the
problem to the operator.

REUSE, NOT PARALLEL.
  · The registry shape is `addresses.json`'s (`{region, capabilities, represents,
    code, howto}` — howto a STRING; consumer `contracts/ui_info.py:from_corpus`
    reads `rec.get("howto")` as a str, so the dossier's structured howto is
    FLATTENED to the canonical `WHAT: … WHAT YOU CAN DO: … HOW TO CHANGE IT: …`).
  · `region` is DERIVED from the address (`parse_ui_address(addr).segments[0]`) —
    the consumer's `validate_address_record` flags an empty region, so it is
    never left null.
  · The re-parse REUSES `parse.py:build_map` (a pure function) — it does NOT
    shell `parse.py main()` (whose paths are hardcoded to the real files) and
    does NOT write a second parser.
  · stdlib only (regex / `html`), matching parse.py — no bs4/lxml dependency.

★ PATHS ARE PARAMETERS (real ones default). `registry_writeback(entries,
addresses_path=…, mockups_dir=…, element_map_path=…)`. The defaults are the real
design-corpus files; a TEST points all three at a temp copy. This is what keeps
the verify-by-USE round-trip off the real registry AND keeps parse.py untouched.

CONTRACT — the confirmed dossier entry (RG3 `register_element` output_schema,
plus the carrier fields the chain wires through from the candidate unit):
    {
      "address": "ui://inbox/layers",          # proposed ui://, the registry KEY + the stamped value
      "represents": "...",                       # short, the 82's "RUN-run" voice
      "howto": {"what": "...", "what_you_can_do": "...", "how_to_change": "..."},
      "capabilities": ["pointable", ...],        # canonical vocabulary (validated by consumer)
      "maps_to_feature": "<feature-id>" | "proposed",
      "confidence": 0.0..1.0,
      # carrier fields (from the RG1 candidate unit the dossier was produced for):
      "mockup_file": "C1-inbox-desktop.html",   # which mockup to stamp
      "outerHTML": "<button class=...>Layers</button>",  # locate the opening tag from this
      # provenance (introspective-data):
      "run": "run://<turn>/register_element/<i>",
      "model": "<model-id>"
    }
"""
import os
import re
import json
import copy

# REUSE the canonical grammar parser (region derivation + grammar validation)
# and the canonical parser's pure map-builder. Both live beside this file.
from contracts.ui_info import parse_ui_address  # type: ignore
from importlib import import_module


# ── default real paths (the design corpus) ───────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_ADDRESSES = os.path.join(_HERE, "addresses.json")
_DEFAULT_MOCKUPS = os.path.join(os.path.dirname(_HERE), "mockups")
_DEFAULT_ELEMENT_MAP = os.path.join(_HERE, "element-map.json")

# Locate the opening `<tag ...>` of an outerHTML snippet (the bit before the
# first close-bracket of the FIRST tag). We inject the data-ui-ref into this.
_OPEN_TAG_RE = re.compile(r"<\s*([a-zA-Z][\w-]*)\b[^>]*?/?>")
_HAS_REF_RE = re.compile(r'data-ui-ref\s*=')


class WritebackError(Exception):
    """A fail-loud write-back refusal (ambiguity, conflict, missing file/element).

    Carries `address` so the caller can surface WHICH entry was refused; the
    batch as a whole is rejected on the first refusal (the registry is the one
    truth — a half-applied batch is worse than a refused one)."""

    def __init__(self, message: str, *, address: str | None = None):
        super().__init__(message)
        self.address = address


# ── (schema bridge) the confirmed dossier → the canonical addresses.json entry ─
def _flatten_howto(howto) -> str | None:
    """Flatten the dossier's structured howto into the canonical STRING the
    live consumer (`ui_info.from_corpus` → `rec.get('howto')`) reads.

    Accepts the structured object {what, what_you_can_do, how_to_change} OR an
    already-flat string (idempotent). The canonical string format mirrors the 82
    existing entries: `WHAT: … WHAT YOU CAN DO: … HOW TO CHANGE IT: …`."""
    if howto is None:
        return None
    if isinstance(howto, str):
        return howto.strip() or None
    if isinstance(howto, dict):
        parts = []
        what = (howto.get("what") or "").strip()
        cando = (howto.get("what_you_can_do") or "").strip()
        change = (howto.get("how_to_change") or "").strip()
        if what:
            parts.append(f"WHAT: {what}")
        if cando:
            parts.append(f"WHAT YOU CAN DO: {cando}")
        if change:
            parts.append(f"HOW TO CHANGE IT: {change}")
        return " ".join(parts) or None
    raise WritebackError(f"howto must be a dict or str, got {type(howto).__name__}")


def _dossier_to_entry(entry: dict) -> tuple[str, dict]:
    """Project ONE confirmed dossier → (address, addresses.json-shaped record).

    Fail loud on a bad address grammar (the registry key must parse). Derives
    `region` from the address (consumer flags empty region). Carries
    represents/capabilities straight across; FLATTENS howto; attaches a nested
    `provenance` (introspective-data). For a proposed/mockup-only element there
    is NO `code` ref — we DO NOT fabricate one (no-fiction); `maps_to_feature`
    is kept as its own additive field (it is a feature id, not a code ref)."""
    address = entry.get("address")
    if not isinstance(address, str) or not address.strip():
        raise WritebackError(f"entry missing a string `address`: {entry!r}")
    # grammar gate (fail loud) + region derivation in one
    try:
        parsed = parse_ui_address(address)
    except (ValueError, TypeError) as e:
        raise WritebackError(f"address {address!r} fails the ui:// grammar: {e}", address=address)
    region = parsed["segments"][0]

    record: dict = {"region": region}

    caps = entry.get("capabilities")
    if caps is not None:
        if not isinstance(caps, (list, tuple)):
            raise WritebackError(f"{address!r}: capabilities must be a list, got {type(caps).__name__}", address=address)
        record["capabilities"] = list(caps)

    represents = entry.get("represents")
    if represents:
        record["represents"] = represents

    howto = _flatten_howto(entry.get("howto"))
    if howto:
        record["howto"] = howto

    # maps_to_feature: own field (feature id or "proposed"). NOT a code ref —
    # we never fabricate a `code:` file:line for a proposed/mockup-only element.
    mtf = entry.get("maps_to_feature")
    if mtf:
        record["maps_to_feature"] = mtf

    # provenance (introspective-data law): which run, model, confidence produced this.
    prov = {}
    if entry.get("run"):
        prov["run"] = entry["run"]
    if entry.get("model"):
        prov["model"] = entry["model"]
    if entry.get("confidence") is not None:
        prov["confidence"] = entry["confidence"]
    if prov:
        record["provenance"] = prov

    return address, record


def _merge_entry(registry_addresses: dict, address: str, record: dict) -> str:
    """Additive + dedup-safe merge of ONE record into the registry's `addresses`
    map (mutated in place). Returns 'added' or 'skipped'.

    · address NOT present  → add it.
    · address present, the SAME meaningful content (region/represents/howto/
      capabilities/maps_to_feature equal) → skip (idempotent re-run; report it).
    · address present, DIFFERENT meaningful content → FAIL LOUD. We never
      silently overwrite a hand-curated entry (one of the 82) — a content
      conflict is surfaced to the operator, never resolved by the machine."""
    existing = registry_addresses.get(address)
    if existing is None:
        registry_addresses[address] = record
        return "added"
    # present — compare the meaningful (non-provenance) fields.
    cmp_keys = ("region", "represents", "howto", "capabilities", "maps_to_feature")
    same = all(existing.get(k) == record.get(k) for k in cmp_keys)
    if same:
        return "skipped"
    diffs = [k for k in cmp_keys if existing.get(k) != record.get(k)]
    raise WritebackError(
        f"address {address!r} already registered with DIFFERENT content "
        f"(differs on {diffs}); refusing to overwrite a curated entry — "
        f"surface to the operator, never silent-overwrite",
        address=address,
    )


# ── (the stamp) inject data-ui-ref into the mockup HTML at the element ────────
def _inject_into_open_tag(open_tag: str, address: str) -> str:
    """Return `open_tag` with ` data-ui-ref="<address>"` injected before its
    closing '>' (handles a self-closing '/>' too). The opening tag is the only
    thing we mutate — never the element's children/text."""
    if open_tag.endswith("/>"):
        return open_tag[:-2].rstrip() + f' data-ui-ref="{address}"' + " />"
    return open_tag[:-1].rstrip() + f' data-ui-ref="{address}">'


def _stamp_html(html: str, outer_html: str, address: str) -> str:
    """Return `html` with ` data-ui-ref="<address>"` injected into the opening
    tag of the element identified by `outer_html`. Fail loud on every ambiguity.

    Locate strategy — a TWO-TIER EXACT-SUBSTRING match (stdlib, mirrors parse.py's
    regex approach — no bs4/lxml, no regex-from-arbitrary-HTML, no offset-mapping;
    every tier acts only on a substring that occurs EXACTLY ONCE, so it is
    safe-by-construction — it can never stamp the wrong element):

      TIER 1 — the FULL outerHTML. If the exact `outer_html` substring occurs
        once in the mockup, inject the ref into its opening tag and splice that
        single occurrence back. This wins LEAF COLLISIONS — many elements share
        an opening tag (e.g. several `<button class="btn">`) but the full
        outerHTML (open tag + text + children) is unique. (Measured on the real
        corpus: this alone uniquely locates ~84% of candidates.)

      TIER 2 — the OPENING TAG only (`<tag …>` up to its first `>`). Used when
        the full outerHTML did NOT occur exactly once. This wins WHITESPACE
        CONTAINERS — parse.py's extractor collapses internal whitespace when it
        serialises a candidate's outerHTML, so a container's full outerHTML may
        not byte-match the raw mockup (count 0), yet its opening tag is unique
        (e.g. `<aside class="panel">`). It also covers in-batch nested stamping:
        stamping a CHILD mutates a parent's stored outerHTML so tier-1 misses,
        but the parent's short opening tag is unaffected and still lands.
        (Tier-2 recovers a further ~12% — combined ~96% on the real corpus.)

    Both tiers require count == 1. The residual (~4%) is GENUINELY identical
    elements (e.g. two `<span class="vol">VOLATILE</span>` with the same tag,
    text, and no distinguishing children) — those FAIL LOUD here, because
    stamping the wrong one corrupts the element-map join. Disambiguating them
    needs RG1's per-element `selector` (the named hardening path)."""
    if not isinstance(outer_html, str) or not outer_html.strip():
        raise WritebackError(f"{address!r}: no outerHTML to locate the element by", address=address)
    outer_html = outer_html.strip()
    m = _OPEN_TAG_RE.match(outer_html)
    if not m:
        raise WritebackError(
            f"{address!r}: outerHTML does not start with an opening tag: {outer_html[:80]!r}",
            address=address,
        )
    open_tag = m.group(0)  # e.g. '<button class="tb-btn primary">'

    if _HAS_REF_RE.search(open_tag):
        raise WritebackError(
            f"{address!r}: the element's opening tag ALREADY carries a data-ui-ref "
            f"({open_tag[:120]!r}) — refusing to double-stamp; surface to operator",
            address=address,
        )

    # ── TIER 1: locate by the full outerHTML (disambiguates leaf collisions) ──
    if html.count(outer_html) == 1:
        stamped_outer = _inject_into_open_tag(open_tag, address) + outer_html[len(open_tag):]
        return html.replace(outer_html, stamped_outer, 1)

    # ── TIER 2: fall back to the opening tag (whitespace containers / nesting) ──
    open_count = html.count(open_tag)
    if open_count == 1:
        return html.replace(open_tag, _inject_into_open_tag(open_tag, address), 1)

    # ── neither tier uniquely located it → fail loud (no guessing) ──
    full_count = html.count(outer_html)
    if open_count == 0:
        raise WritebackError(
            f"{address!r}: element not found in the mockup — neither the full "
            f"outerHTML nor its opening tag ({open_tag[:120]!r}) occurs there; "
            f"the outerHTML may be stale vs the mockup.",
            address=address,
        )
    raise WritebackError(
        f"{address!r}: element is AMBIGUOUS — the full outerHTML occurs {full_count}× "
        f"and the opening tag {open_count}× in the mockup; refusing to guess which "
        f"element to stamp (stamping the wrong one corrupts the element-map join). "
        f"(Hardening path: selector-based disambiguation once RG1's selector is wired.)",
        address=address,
    )


# ── the round-trip re-parse (REUSES parse.py:build_map) ───────────────────────
def _reparse(mockups_dir: str, registry_addresses: dict) -> dict:
    """Regenerate the element-map by REUSING `parse.py:build_map` (the pure
    function — NOT parse.py's main(), whose paths are hardcoded). Reads every
    `.html` in `mockups_dir` against the (now-grown) registry addresses."""
    parse_mod = import_module("design._system.parse") if _importable_as_pkg() else _load_parse_module()
    build_map = parse_mod.build_map
    screens = {}
    for fn in sorted(os.listdir(mockups_dir)):
        if fn.endswith(".html"):
            with open(os.path.join(mockups_dir, fn), encoding="utf-8") as f:
                screens[fn] = f.read()
    return build_map(screens, registry_addresses)


def _importable_as_pkg() -> bool:
    try:
        import_module("design._system.parse")
        return True
    except Exception:
        return False


def _load_parse_module():
    """Load parse.py beside this file by path (when not import-able as a package)."""
    import importlib.util
    path = os.path.join(_HERE, "parse.py")
    spec = importlib.util.spec_from_file_location("_rg_parse_for_writeback", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── the public entry point (operator-gated; NEVER auto-run) ───────────────────
def registry_writeback(
    entries: list,
    *,
    addresses_path: str = _DEFAULT_ADDRESSES,
    mockups_dir: str = _DEFAULT_MOCKUPS,
    element_map_path: str = _DEFAULT_ELEMENT_MAP,
    write: bool = True,
    skip_already_stamped: bool = False,
) -> dict:
    """Apply a CONFIRMED, OPERATOR-APPROVED batch of dossier entries.

    The round-trip: merge → stamp → re-parse. ALL-OR-NOTHING per batch — the
    merge + every stamp are computed first (in memory); if ANY raises
    WritebackError the batch is refused and NOTHING is written (the registry is
    the one truth — never half-applied). Only when the whole batch validates is
    it written to disk and the element-map regenerated.

    Args:
      entries: list of confirmed dossier dicts (see module docstring CONTRACT).
      addresses_path / mockups_dir / element_map_path: the targets. DEFAULT to
        the REAL design corpus; a TEST points all three at a temp copy.
      write: if False, validate + compute everything but write nothing (a dry
        run; the report still shows what WOULD happen). Defaults True.

    Returns a report dict:
      {merged:[{address, status}], stamped:[{address, mockup_file}],
       registered_after:[address...], summary:{...}, element_map_summary:{...}}

    Raises WritebackError (fail loud) on any ambiguity/conflict — see module
    docstring. The caller (the approve-gate) surfaces the refusal to the
    operator; nothing partial is left behind."""
    if not isinstance(entries, list):
        raise WritebackError(f"entries must be a list, got {type(entries).__name__}")
    if not entries:
        raise WritebackError("entries is empty — nothing to write back (fail loud, not a silent no-op)")

    # ── load the registry ──
    with open(addresses_path, encoding="utf-8") as f:
        registry = json.load(f)
    if not isinstance(registry, dict) or "addresses" not in registry:
        raise WritebackError(
            f"{addresses_path}: not the expected {{_what, scheme, addresses}} shape"
        )
    # work on a deep copy so a mid-batch failure leaves the on-disk file untouched.
    new_registry = copy.deepcopy(registry)
    addr_map = new_registry["addresses"]

    # ── PHASE 1: validate + project + merge (in memory) ──
    merged = []
    for entry in entries:
        address, record = _dossier_to_entry(entry)
        status = _merge_entry(addr_map, address, record)
        merged.append({"address": address, "status": status})

    # ── PHASE 2: stamp every mockup (in memory) ──
    # Group entries by mockup file so each file is loaded once and all its
    # stamps apply to the same (progressively-stamped) buffer.
    by_file: dict = {}
    for entry in entries:
        mf = entry.get("mockup_file")
        if not mf:
            raise WritebackError(
                f"{entry.get('address')!r}: entry has no `mockup_file` — cannot stamp",
                address=entry.get("address"),
            )
        by_file.setdefault(mf, []).append(entry)

    stamped = []
    stamp_skipped = []                                   # reported, never silent
    file_buffers: dict = {}
    for mf, file_entries in by_file.items():
        mock_path = os.path.join(mockups_dir, mf)
        if not os.path.isfile(mock_path):
            raise WritebackError(
                f"mockup file not found: {mock_path} (entry address "
                f"{file_entries[0].get('address')!r})",
                address=file_entries[0].get("address"),
            )
        with open(mock_path, encoding="utf-8") as f:
            buf = f.read()
        for entry in file_entries:
            address = entry["address"]
            # skip_already_stamped (additive, default False = the original fail-loud): an element
            # whose outerHTML ROOT already carries an (ancestor's) data-ui-ref cannot take a second
            # stamp — with the flag, its registry entry still merges and the skip is REPORTED
            # (stamp_skipped), never silent. Without the flag the batch refuses, as before.
            try:
                buf = _stamp_html(buf, entry.get("outerHTML"), address)
                stamped.append({"address": address, "mockup_file": mf})
            except WritebackError as _se:
                _msg = str(_se)
                if skip_already_stamped and ("ALREADY carries a data-ui-ref" in _msg
                                             or "AMBIGUOUS" in _msg):
                    # both stamp-conflict classes (ancestor-stamped root · ambiguous locate) are
                    # RECORDED for the selector-hardening pass — the registry entry still merges.
                    stamp_skipped.append({"address": address, "mockup_file": mf,
                                          "why": _msg[:160]})
                else:
                    raise
        file_buffers[mock_path] = buf

    # ── PHASE 3: write (only now that the WHOLE batch validated) ──
    if write:
        for mock_path, buf in file_buffers.items():
            with open(mock_path, "w", encoding="utf-8") as f:
                f.write(buf)
        with open(addresses_path, "w", encoding="utf-8") as f:
            json.dump(new_registry, f, indent=2, ensure_ascii=False)
            f.write("\n")

    # ── PHASE 4: round-trip re-parse (the JOIN that proves it) ──
    # Re-parse against the grown registry. When write=True the mockups on disk
    # carry the new refs; when write=False we re-parse the in-memory buffers so
    # the dry-run report still shows the join outcome.
    if write:
        element_map = _reparse(mockups_dir, addr_map)
    else:
        element_map = _reparse_buffers(mockups_dir, file_buffers, addr_map)

    if write:
        with open(element_map_path, "w", encoding="utf-8") as f:
            json.dump(element_map, f, indent=2)

    # The JOIN assertion data: which stamped addresses now resolve as registered.
    registered_now = {
        e["address"] for e in element_map["elements"] if e.get("registered")
    }
    stamped_addrs = {s["address"] for s in stamped}
    registered_after = sorted(stamped_addrs & registered_now)
    still_unregistered = sorted(stamped_addrs - registered_now)

    return {
        "merged": merged,
        "stamp_skipped": stamp_skipped,
        "stamped": stamped,
        "registered_after": registered_after,
        "still_unregistered": still_unregistered,  # should be empty on a clean round-trip
        "wrote": write,
        "summary": {
            "entries": len(entries),
            "added": sum(1 for m in merged if m["status"] == "added"),
            "skipped": sum(1 for m in merged if m["status"] == "skipped"),
            "stamped": len(stamped),
            "registered_after": len(registered_after),
        },
        "element_map_summary": element_map["summary"],
    }


def _reparse_buffers(mockups_dir: str, file_buffers: dict, registry_addresses: dict) -> dict:
    """Re-parse for a DRY RUN: the on-disk mockups for files we didn't stamp,
    the in-memory stamped buffers for files we did — so the dry-run join is
    accurate without writing anything."""
    parse_mod = import_module("design._system.parse") if _importable_as_pkg() else _load_parse_module()
    build_map = parse_mod.build_map
    stamped_names = {os.path.basename(p) for p in file_buffers}
    screens = {}
    for fn in sorted(os.listdir(mockups_dir)):
        if not fn.endswith(".html"):
            continue
        if fn in stamped_names:
            # use the in-memory stamped buffer
            for p, buf in file_buffers.items():
                if os.path.basename(p) == fn:
                    screens[fn] = buf
                    break
        else:
            with open(os.path.join(mockups_dir, fn), encoding="utf-8") as f:
                screens[fn] = f.read()
    return build_map(screens, registry_addresses)
