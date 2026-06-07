"""runtime/registry.py — the live node-type registry (C2/S4/C5). See runtime/AGENTS.md.

Node-types are DISCOVERED from files, not hardcoded. Each module becomes a NodeType (C2)
descriptor; the registry is a queryable type-graph (S4) and serves /object_info (C5). It is
dict-like (`reg[name] -> module`) so it drops in wherever node_types went. Adding a node =
dropping a file (the self-extending property; nothing else changes — runtime/AGENTS.md).
"""
from __future__ import annotations
import importlib.util
import os

from contracts.node_type import NodeType, Ports
from contracts.object_info import build_object_info

CONTENT_KINDS = ("constant", "document", "code", "file", "image", "source", "portal")


def _infer_kind(name: str) -> str:
    return "content" if name in CONTENT_KINDS else "process"


def _read_output_schema(mod) -> dict:
    """Read a module's declared OUTPUT_SCHEMA (C1.4). Accepts either a plain dict (a JSON-shape /
    json-schema spec) OR a Pydantic BaseModel subclass (we serialize it via .model_json_schema()).
    Anything else, or an absent attribute, → {} (the additive default — node-type unchanged). Pure
    read, no side effects; fail loud only on a declared-but-malformed value (never a silent wrong)."""
    decl = getattr(mod, "OUTPUT_SCHEMA", None)
    if decl is None:
        return {}
    if isinstance(decl, dict):
        return dict(decl)
    # a Pydantic model class → its json-schema (duck-typed: has model_json_schema)
    schema_fn = getattr(decl, "model_json_schema", None)
    if callable(schema_fn):
        return schema_fn()
    raise TypeError(
        f"register_module: OUTPUT_SCHEMA on node-type module {mod!r} must be a dict or a Pydantic "
        f"BaseModel subclass, got {type(decl).__name__} (fail loud — never a silent wrong schema)."
    )


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_node_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


class NodeRegistry:
    def __init__(self):
        self._modules: dict = {}          # name -> module (executes via .run)
        self.types: dict[str, NodeType] = {}

    def discover(self, dirs: list[str]) -> "NodeRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                if not hasattr(mod, "run"):       # not a node module
                    continue
                self.register_module(name, mod)
        return self

    def rediscover(self, dirs: list[str]) -> "NodeRegistry":
        """Rebuild from the filesystem (clear + discover) — so a removed file (e.g. after a
        git revert of a self-applied node) actually un-registers. discover() only adds."""
        self._modules.clear()
        self.types.clear()
        return self.discover(dirs)

    def register_module(self, name: str, mod) -> None:
        self._modules[name] = mod
        self.types[name] = NodeType(
            name=name,
            kind=getattr(mod, "KIND", _infer_kind(name)),
            ports=Ports(inputs=dict(getattr(mod, "PORTS_IN", {})),
                        outputs=dict(getattr(mod, "PORTS_OUT", {}))),
            config_schema=dict(getattr(mod, "CONFIG", {})),
            # C1.4 (Concurrent Cognition G1): a module may DECLARE an OUTPUT_SCHEMA — a JSON-shape
            # dict (or the json-schema of a Pydantic model). It is read into NodeType.output_schema
            # so the registry carries it SINGLE-SOURCE (the cognition driver reads it to validate a
            # role's output via complete()'s existing validate/retry — fabric/client.py). Additive:
            # a module that declares none keeps the empty default (every existing node-type unchanged).
            output_schema=_read_output_schema(mod),
            version=int(getattr(mod, "VERSION", "1")),
        )

    # --- queryable type-graph (S4) ---
    def produces(self, port_type: str) -> list[str]:
        return [n for n, nt in self.types.items() if port_type in nt.ports.outputs.values()]

    def consumes(self, port_type: str) -> list[str]:
        return [n for n, nt in self.types.items() if port_type in nt.ports.inputs.values()]

    # --- C5 serialization to the frontend ---
    def object_info(self) -> dict:
        return build_object_info(self.types)

    # --- dict-like, so it IS the node_types mapping for the runtime ---
    def __getitem__(self, name: str):
        return self._modules[name]

    def __contains__(self, name: str) -> bool:
        return name in self._modules

    def get(self, name: str, default=None):
        return self._modules.get(name, default)
