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
