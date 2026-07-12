"""emit.py — compiles tokens.json (the design token registry) → design-system.css.
The CSS is GENERATED; tokens.json is the source of truth. Edit tokens.json, re-run:
    python3 emit.py
Layers: `primitives` (raw values) + grouped `tokens` that are either {"v": value}
(flat) or {"ref": <primitive>} (resolves to the primitive — change it in one place,
every ref follows). The :root block is emitted; components.css is appended verbatim."""
import os, json


def emit(data: dict) -> str:
    """tokens dict → full design-system.css text (header + imports + :root)."""
    prims = data.get("primitives", {})
    out = ["/* GENERATED from tokens.json by emit.py — DO NOT hand-edit. "
           "Edit tokens.json + re-run `python3 emit.py`. */"]
    for imp in data.get("imports", []):
        out.append(f"@import url('{imp}');")
    out.append(":root{")
    for g in data.get("groups", []):
        if g.get("name"):
            out.append(f"  /* {g['name']} */")
        if g.get("note"):
            out.append(f"  /* {g['note']} */")
        for name, spec in g.get("tokens", {}).items():
            if "ref" in spec:
                if spec["ref"] not in prims:
                    raise KeyError(f"token --{name} refs unknown primitive '{spec['ref']}' (fail loud)")
                val = prims[spec["ref"]]
            elif "v" in spec:
                val = spec["v"]
            else:
                raise ValueError(f"token --{name} has neither 'v' nor 'ref' (fail loud)")
            out.append(f"  --{name}:{val};")
    for k, v in data.get("root_extra", {}).items():
        out.append(f"  {k}:{v};")
    out.append("}")
    # F4 — AXES (operator-surface, 2026-07-13): attribute-conditional token blocks — the ONE generic
    # mechanism behind data-theme / data-density (and any future axis). Each row emits
    # `[<attr>="<value>"]{ --token:value; extra }` AFTER :root, so the default (no attribute) stays
    # byte-identical and toggling the attribute retunes the vars live. Rows are data (registry-is-truth):
    # a new mode = a new row in tokens.json, zero code. Values may `ref` primitives like any token.
    for ax in data.get("axes", []):
        for req in ("attr", "value", "tokens"):
            if req not in ax:
                raise ValueError(f"axis row missing '{req}' (fail loud): {ax.get('attr')}={ax.get('value')}")
        out.append("")
        if ax.get("note"):
            out.append(f"/* {ax['note']} */")
        out.append(f'[{ax["attr"]}="{ax["value"]}"]{{')
        for name, spec in ax["tokens"].items():
            if isinstance(spec, dict) and "ref" in spec:
                if spec["ref"] not in prims:
                    raise KeyError(f"axis token --{name} refs unknown primitive '{spec['ref']}' (fail loud)")
                val = prims[spec["ref"]]
            elif isinstance(spec, dict) and "v" in spec:
                val = spec["v"]
            else:
                raise ValueError(f"axis token --{name} has neither 'v' nor 'ref' (fail loud)")
            out.append(f"  --{name}:{val};")
        for k, v in ax.get("extra", {}).items():
            out.append(f"  {k}:{v};")
        out.append("}")
    return "\n".join(out) + "\n"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    design = os.path.dirname(here)
    with open(os.path.join(here, "tokens.json"), encoding="utf-8") as f:
        data = json.load(f)
    css = emit(data)
    comp = os.path.join(here, "components.css")
    if os.path.exists(comp):
        with open(comp, encoding="utf-8") as f:
            css = css + "\n" + f.read()
    out = os.path.join(design, "design-system.css")
    with open(out, "w", encoding="utf-8") as f:
        f.write(css)
    print(f"emitted -> {out} ({len(css)} chars)")


if __name__ == "__main__":
    main()
