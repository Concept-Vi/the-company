"""runtime/message_types.py — the file-discovered TYPED-MESSAGE registry (Tim, 2026-06-29).

A MESSAGE-TYPE is a declared KIND of member-to-member board message WITH its OBLIGATION — what the
addressed member is held to (the "conversational contract"). This is the generalization of the mention
loop: `mention` obliges a reply; `ask` obliges an answer; `review_request` obliges a verdict; `handoff`
obliges an acknowledgement; `fyi` obliges nothing. The pending-obligations fold + the UserPromptSubmit
nag hook enforce the obligation MECHANICALLY: a typed message re-surfaces in the addressed session's
context every turn until its closing action lands on the board — it cannot silently rot.

Mirrors the ONE registry mechanism (item_types/source_types/relation_types): os.listdir → importlib,
fail-loud, id == filename, dict-like, rediscover. Adding a message kind (a "verb") = dropping a
message_types/<id>.py — ZERO code change. HOW-TO: read guide://adding_message_verbs (the guide is
itself a registry row — the handbook lives in the fabric, not in a session).

## The message-type schema — each message_types/<id>.py declares a module-level MESSAGE_TYPE dict:
  - id          — required; MUST equal the module name.
  - obligation  — required; one of OBLIGATIONS below — what closes it:
                    reply   → a threaded board reply by the addressed member
                    verdict → a reply whose body carries an explicit verdict line
                    ack     → a reply (acknowledgement) — semantically lighter than reply
                    none    → nothing owed (informational)
  - label       — optional; human label.
  - desc        — optional; when to use this kind + what the addressed member is held to.
A malformed entry FAILS LOUD at discovery — never a silent skip.
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass

MESSAGE_TYPE_FIELDS = ("id", "obligation", "label", "desc")
REQUIRED_FIELDS = ("id", "obligation")
OBLIGATIONS = ("reply", "verdict", "ack", "none")


@dataclass
class MessageType:
    id: str
    obligation: str
    label: str = ""
    desc: str = ""


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"message_types.{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return name, mod


def _build(name: str, decl: dict) -> MessageType:
    if not isinstance(decl, dict):
        raise ValueError(f"message_types/{name}.py: MESSAGE_TYPE must be a dict. Fail loud.")
    unknown = [k for k in decl if k not in MESSAGE_TYPE_FIELDS]
    if unknown:
        raise ValueError(f"message_types/{name}.py: unknown fields {unknown} — valid: "
                         f"{list(MESSAGE_TYPE_FIELDS)}. Fail loud.")
    missing = [k for k in REQUIRED_FIELDS if not decl.get(k)]
    if missing:
        raise ValueError(f"message_types/{name}.py: missing required {missing}. Fail loud.")
    if decl["id"] != name:
        raise ValueError(f"message_types/{name}.py: id {decl['id']!r} != filename {name!r}. Fail loud.")
    if decl["obligation"] not in OBLIGATIONS:
        raise ValueError(f"message_types/{name}.py: obligation {decl['obligation']!r} not in "
                         f"{OBLIGATIONS}. Fail loud.")
    return MessageType(id=decl["id"], obligation=decl["obligation"],
                       label=decl.get("label", ""), desc=decl.get("desc", ""))


class MessageTypeRegistry:
    def __init__(self):
        self.entries: dict[str, MessageType] = {}

    def discover(self, dirs: list[str]) -> "MessageTypeRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "MESSAGE_TYPE", None)
                if decl is None:
                    continue
                self.entries[name] = _build(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "MessageTypeRegistry":
        self.entries.clear()
        return self.discover(dirs)

    def __getitem__(self, k: str) -> MessageType:
        if k not in self.entries:
            raise KeyError(
                f"unknown message type {k!r} — registered: {sorted(self.entries)}. "
                f"(a kind is a registry row; add message_types/<id>.py to extend — "
                f"see guide://adding_message_verbs.)")
        return self.entries[k]

    def __contains__(self, k: str) -> bool:
        return k in self.entries

    def __iter__(self):
        return iter(self.entries)
