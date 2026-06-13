"""introspection/adapters/stream_init.py - StreamInitDiscoverer (DiscoverySourceType 'stream-init').
LEVEL 1 (platform-agnostic) - Mirror-Registry System, LANE-INTROSPECTION-CORE.

Captures a running session's INIT event (the platform's self-declaration of its live runtime surface:
the tools it has, the tool-servers attached, the model/permission posture) and parses it into
CapabilityEntry rows. The PARSE RULE is generic - it knows the init-event SHAPE (a JSON object whose
fields name capability collections), not any specific platform/tool name. ZERO platform-name literals
(F-FIX-10).

How the init event is obtained (the SHAPE, observed via the consumer's session reader): the platform
is run under a newline-delimited-JSON event transport; the FIRST event matching the
DiscoverySource.event_filter ({"type":"system","subtype":"init"}) carries the field set.
StreamInitDiscoverer spawns a SHORT scratch session (run-with-timeout via the SubprocessAdapter),
reads stdout line-by-line as NDJSON, and returns the first event whose fields match event_filter. The
spawn command + the event_filter + the field->kind map all arrive as platform DATA on the
DiscoverySource - this file holds none of those strings as literals (F-FIX-10).

  LEAD-only live verification: discover() spawns a real session. This module is unit-verified with a
  STUB transport (a fixture init event) - the live spawn is 'built - lead live-verify queued'
  (the lead runs the live-binary acceptance C-CORE-2; a subagent forbidden from spawning a session
  cannot fire it).

field->kind map (DiscoverySource.field_kind_map, platform DATA): which init-event field projects to
which CapabilityEntry.kind, e.g. {"tools":"tool", "servers":"mcp_tool", ...}. A field PRESENT in
the init event but ABSENT from the map lands in raw_extra with a fail-loud note (never silently
dropped - the no-self-report=gap law). The id is f'{kind}/{name}' (F-FIX-14).
"""
from __future__ import annotations
import json
from typing import Any

from contracts.capability_entry import CapabilityEntry
from introspection.adapters.subprocess_invoke import SubprocessAdapter


class StreamInitDiscoverer:
    """Discovers capabilities from a running session's init self-declaration. Stateless; the platform
    DATA (DiscoverySource + resolved executable + field_kind_map) drives every value. Engine selects
    this adapter by DiscoverySource.type == 'stream-init'."""

    source_type = "stream-init"

    # Fields on a typical init event that are POSTURE/metadata, not capability collections — these
    # are recorded on the platform but are NOT individual capability rows. Kept generic (structural),
    # not platform-named: a field is treated as a collection ONLY if the field_kind_map names it.
    def discover(self, executable: str, src, *, invoker: "SubprocessAdapter | None" = None) -> dict:
        """Spawn a short scratch session, read NDJSON stdout, return the FIRST event matching
        src.event_filter (the init event dict). LEAD-only: this fires a real session. Fail loud if
        no matching event appears before the stream ends (a session that never declares init is a
        broken read, not 'no capabilities')."""
        invoker = invoker or SubprocessAdapter()
        cmd = [tok.replace("{binary}", executable) for tok in src.command]
        if not cmd:
            raise ValueError(
                f"stream-init discover: empty command for source {src.type!r} - the DiscoverySource"
                f".command must carry the scratch-session spawn argv (with {{binary}}). Fail loud.")
        stdin_payload = getattr(src, "stdin_payload", None)
        proc = invoker.run_capture(cmd, stderr_merge=getattr(src, "stderr_merge", False),
                                   timeout_s=getattr(src, "timeout_s", 30), stdin=stdin_payload)
        raw = proc.stdout or ""
        event = self._first_matching_event(raw, getattr(src, "event_filter", {}) or {})
        if event is None:
            raise RuntimeError(
                f"stream-init discover: command {cmd!r} produced NO event matching event_filter="
                f"{getattr(src, 'event_filter', {})!r} (rc={proc.returncode}) - refusing to return "
                f"an empty self-declaration (fail-loud; the live session declared nothing matching).")
        return event

    @staticmethod
    def _first_matching_event(raw: str, event_filter: dict) -> "dict | None":
        """Scan NDJSON lines, return the first parsed object whose top-level fields equal every
        key/value in event_filter (e.g. {"type":"system","subtype":"init"}). Non-JSON chatter is
        skipped (the event contract is the JSON line, mirroring the supervisor reader)."""
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            if not isinstance(ev, dict):
                continue
            if all(ev.get(k) == v for k, v in event_filter.items()):
                return ev
        return None

    def parse(self, event: dict, src, *, platform_id: str = "", version: str = "") -> list[CapabilityEntry]:
        """Parse the init event into CapabilityEntry rows. field_kind_map (DiscoverySource DATA) names
        which event fields are capability COLLECTIONS and which CapabilityEntry.kind each projects to.

        A collection field maps a list (e.g. tool names) or a dict (e.g. {server: {...}}) into one row
        per member. A field PRESENT in the event but NOT in field_kind_map AND not declared metadata is
        a GAP: it is captured into a single 'sdk_event' raw_extra row with a fail-loud note rather than
        silently dropped (no-self-report=gap law). The fail_loud flag may escalate this to a raise."""
        field_kind_map: dict[str, str] = dict(getattr(src, "field_kind_map", {}) or {})
        metadata_fields: set[str] = set(getattr(src, "metadata_fields", []) or [])
        entries: list[CapabilityEntry] = []
        seen: set[str] = set()
        unmapped: dict[str, Any] = {}

        for field, value in event.items():
            if field in metadata_fields:
                continue
            kind = field_kind_map.get(field)
            if kind is None:
                # not a declared collection, not declared metadata → a GAP (captured, never dropped).
                unmapped[field] = value
                continue
            for name in self._members(value):
                entry_id = f"{kind}/{name}"
                if entry_id in seen:
                    continue
                seen.add(entry_id)
                entries.append(CapabilityEntry(
                    id=entry_id,
                    kind=kind,
                    name=name,
                    visible=True,
                    source="init-event",
                    platform_id=platform_id or "",
                    discovered_at=version,
                ))

        if unmapped:
            note = ("init fields present in the live self-declaration but NOT in field_kind_map "
                    "or metadata_fields - captured here, NOT silently dropped (gap-surfaced for "
                    "the curator: each is a new field→kind decision or a new metadata field).")
            if getattr(src, "fail_loud", True) and not field_kind_map:
                # an EMPTY map against a non-empty event is a misconfiguration, not a discovery.
                raise RuntimeError(
                    f"stream-init parse: field_kind_map is empty but the init event carries fields "
                    f"{sorted(unmapped)} - refusing to return an empty registry from a populated "
                    f"self-declaration. Fail loud. {note}")
            entries.append(CapabilityEntry(
                id="sdk_event/init.unmapped",
                kind="sdk_event",
                name="init.unmapped",
                description=note,
                visible=True,
                source="init-event",
                platform_id=platform_id or "",
                discovered_at=version,
                raw_extra=unmapped,
            ))
        return entries

    @staticmethod
    def _members(value):
        """Yield the member NAMES of a collection field. A list[str] yields its strings; a list[dict]
        yields each dict's 'name' (or its first string value); a dict yields its keys. Generic shape
        handling - no field/name literals."""
        if isinstance(value, dict):
            for k in value.keys():
                yield str(k)
            return
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    yield item
                elif isinstance(item, dict):
                    nm = item.get("name")
                    if nm:
                        yield str(nm)
                    else:
                        # first string-valued field as the name (generic fallback).
                        strs = [v for v in item.values() if isinstance(v, str)]
                        if strs:
                            yield strs[0]
            return
        if isinstance(value, str):
            yield value
