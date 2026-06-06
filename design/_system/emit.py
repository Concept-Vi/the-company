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
