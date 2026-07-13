#!/usr/bin/env python3
"""_system/bundle_append.py — the LOCAL bundle recompiler (additive, format-4-faithful).

_ds_bundle.js is normally compiled by the Claude Design CLOUD tooling ("rebuilds at end of turn"
there) — the repo has no local compiler, so components landed here between cloud sessions leave the
bundle STALE (the U6 landing proved it: 10 new components on disk, absent from the bundle; the
operator app had to import source as a workaround). This script closes that gap DETERMINISTICALLY:

  • reads the bundle's own header manifest (format 4) → knows what's already compiled;
  • for each components/<Name>.jsx ON DISK but not in the manifest: transforms the source the same
    way the cloud compiler does for the ES-import convention (import React → /* global React */ with
    const h intact; export default/named → Object.assign(__ds_scope, {...})), wraps it in the exact
    try/IIFE/catch shape, and inserts it BEFORE the trailing __ds_ns copy block;
  • appends the matching `__ds_ns.<Name> = __ds_scope.<Name>;` lines to that copy block;
  • updates the header manifest's components[] + sourceHashes (12-hex sha256 prefix, matching the
    existing hash style).

SCOPE (deliberate): components/*.jsx ONLY — the createElement-only convention means no JSX transform
is needed (Glyphic, the one JSX file, is already compiled). A source file containing real JSX (<Tag)
is REFUSED loud — that still needs the cloud compiler or a Babel pass. Idempotent: already-manifested
files are skipped; run it any time. The cloud compiler remains the canonical owner — when it next
regenerates the whole bundle these entries are simply re-produced from the same sources (hashes agree).
"""
import hashlib
import json
import os
import re
import sys

DS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE = os.path.join(DS, "_ds_bundle.js")


def transform(src: str, rel: str) -> tuple[str, list[str]]:
    """ES-convention component source → bundle-body form. Returns (body, exported_names)."""
    if re.search(r"<[A-Za-z]", re.sub(r"//[^\n]*|/\*.*?\*/|\"[^\"]*\"|'[^']*'|`[^`]*`", "", src, flags=re.S)):
        raise SystemExit(f"REFUSED: {rel} appears to contain JSX — the local recompiler is "
                         f"createElement-only; use the cloud compiler (or add a Babel pass) for it.")
    names: list[str] = []
    out = src
    # import React (any form) → the bundle's global-React convention
    out = re.sub(r'^import\s+React[^;\n]*from\s+["\']react["\'];?\s*$', "/* global React */",
                 out, flags=re.M)
    if re.search(r"^import\s", out, flags=re.M):
        raise SystemExit(f"REFUSED: {rel} has non-React imports — the bundle inlines nothing; "
                         f"restructure or use the cloud compiler.")
    # export default <Name>;  /  export default function <Name>...
    m = re.search(r"^export\s+default\s+function\s+([A-Za-z0-9_]+)", out, flags=re.M)
    if m:
        names.append(m.group(1))
        out = re.sub(r"^export\s+default\s+function\s+", "function ", out, count=1, flags=re.M)
    m = re.search(r"^export\s+default\s+([A-Za-z0-9_]+)\s*;?\s*$", out, flags=re.M)
    if m:
        names.append(m.group(1))
        out = re.sub(r"^export\s+default\s+[A-Za-z0-9_]+\s*;?\s*$", "", out, count=1, flags=re.M)
    # export function/const <Name>
    for mm in re.finditer(r"^export\s+(?:function|const)\s+([A-Za-z0-9_]+)", out, flags=re.M):
        names.append(mm.group(1))
    out = re.sub(r"^export\s+(function|const)\s+", r"\1 ", out, flags=re.M)
    # export { A, B };
    for mm in re.finditer(r"^export\s*\{([^}]*)\}\s*;?\s*$", out, flags=re.M):
        names += [n.strip().split(" as ")[-1] for n in mm.group(1).split(",") if n.strip()]
    out = re.sub(r"^export\s*\{[^}]*\}\s*;?\s*$", "", out, flags=re.M)
    names = list(dict.fromkeys(n for n in names if n))
    if not names:
        raise SystemExit(f"REFUSED: {rel} exports nothing recognizable — nothing to expose.")
    slug = re.sub(r"[^A-Za-z0-9]", "_", rel).strip("_")
    expose = ", ".join([f"{n}" for n in names] +
                       [f"__ds_default_{slug}: {names[0]}"])
    body = out.rstrip() + f"\nObject.assign(__ds_scope, {{ {expose} }});"
    return body, names


def main() -> None:
    bundle = open(BUNDLE, encoding="utf-8").read()
    header_line, rest = bundle.split("\n", 1)
    mjson = header_line[len("/* @ds-bundle: "):-len(" */")]
    manifest = json.loads(mjson)
    have = {c["sourcePath"] for c in manifest["components"]} | set(manifest["sourceHashes"])

    comp_dir = os.path.join(DS, "components")
    new = sorted(f for f in os.listdir(comp_dir)
                 if f.endswith(".jsx") and f"components/{f}" not in have)
    if not new:
        print("bundle already current — nothing to append.")
        return

    blocks, ns_lines = [], []
    for fn in new:
        rel = f"components/{fn}"
        src = open(os.path.join(comp_dir, fn), encoding="utf-8").read()
        body, names = transform(src, rel)
        blocks.append(
            f"\n// {rel}\ntry {{ (() => {{\n{body}\n}})(); }} catch (e) {{ "
            f"__ds_ns.__errors.push({{ path: \"{rel}\", error: String((e && e.message) || e) }}); }}\n")
        ns_lines += [f"\n__ds_ns.{n} = __ds_scope.{n};\n" for n in names]
        manifest["components"] += [{"name": n, "sourcePath": rel} for n in names]
        manifest["sourceHashes"][rel] = hashlib.sha256(src.encode()).hexdigest()[:12]
        print(f"  + {rel} → {', '.join(names)}")

    # insert the new IIFEs before the trailing ns-copy block (the first __ds_ns.X = __ds_scope.X line),
    # and the new copy lines INSIDE the final IIFE (before its closing `})();`).
    anchor = re.search(r"\n__ds_ns\.[A-Za-z0-9_]+ = __ds_scope\.", rest)
    if not anchor:
        raise SystemExit("REFUSED: could not find the trailing ns-copy block — format changed?")
    i = anchor.start()
    rest = rest[:i] + "".join(blocks) + rest[i:]
    close = rest.rstrip().rfind("})();")
    if close < 0:
        raise SystemExit("REFUSED: could not find the final IIFE close — format changed?")
    rest = rest[:close] + "".join(ns_lines) + "\n" + rest[close:]
    manifest["sourceHashes"] = dict(sorted(manifest["sourceHashes"].items()))
    out = "/* @ds-bundle: " + json.dumps(manifest, separators=(",", ":")) + " */\n" + rest
    open(BUNDLE, "w", encoding="utf-8").write(out)
    print(f"bundle updated: +{len(new)} sources, +{len(ns_lines)} exposed names.")


if __name__ == "__main__":
    main()
