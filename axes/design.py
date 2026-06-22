"""axes/design.py — the DESIGN-LANGUAGE context axis (a visual resolves against its design coordinate).

DNA's criterion-5 "context-resolution" (resolve-on YES): a visual-dna asset declares its design-context, and a
visual RESOLVES against it — resolve(visual-invariant, design-coordinate) → the applicable visual treatment.

★ NAMING-COLLISION CAUGHT (composition, default-to-wrong): this is NOT the `resolution` axis (axes/resolution.py
= coarse/medium/fine GRAIN / depth — the dragnet & MRL multi-scale rollup). DNA's "context-resolution" shares
that informal name but is a DIFFERENT concept — the design-language DIMENSIONS a visual is located by. So it is
its OWN coordinate (`design`), never folded into the grain axis.

★ THE SPINE-TIE: the sub-fields' MEANINGS are SET by the visual-identity DECISIONS (line-language · opacity-meaning
· core-shape · figure-gold-value) — the decisions populate this axis's vocabulary; the axis resolves visuals
against it. decisions → axis → resolve(visual, design) → the applicable visual. (One invariant visual, never
variants; the design-coordinate selects the treatment.)

TENTATIVE: DNA owns the dimension-details (the exact set + each field's value-source on the visual-dna asset);
composition owns the axis-ROW. Modeled as ONE axis with sub-fields (mirrors `device` = w/h/orient) — flag if DNA
prefers 4 separate axis-rows. value_source PENDING recollection's re-bake (the `resolution` field on the 10,568).
"""

AXIS = {
    "id": "design",
    "namespace": "design",
    "fields": {
        "line": "discrete",          # line-language: dashed/solid → meaning (set by the line-language decision)
        "opacity": "continuous",     # realised-ness: faded = less realised (set by the opacity-meaning decision)
        "colour_role": "discrete",   # the colour's role: gold = attention/recommended (set by figure-gold-value + the palette)
        "shape": "discrete",         # typed geometry: octagon=core / hexagon=engine / … (set by the core-shape decision)
    },
    "value_source": "pending",       # ← the visual-dna asset's design-context field, populated by recollection's re-bake of the 10,568 (DNA confirms the field + value-source)
    "desc": "The DESIGN-LANGUAGE context a visual resolves against — line · opacity · colour-role · shape. "
            "resolve(visual, design-coordinate) → the applicable visual treatment (the spine-tie). The sub-fields' "
            "MEANINGS are set by the visual-identity decisions (line-language/opacity-meaning/core-shape/"
            "figure-gold-value). ★ DISTINCT from axes/resolution.py (the grain/depth) — same informal name, "
            "different axis. TENTATIVE: DNA owns the exact dimensions + value-source; composition owns the row.",
}
