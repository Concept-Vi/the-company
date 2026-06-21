"""decisions/dimension-meaning.py — theorem-fork: what "dimension" the instrument drops through (gather F1).
The bedrock is Tim's; the AI-read has erred here (the cube-error) — flag uncertainty, never assert."""

DECISION = {
    "id": "dimension-meaning",
    "meaning": (
        "The instrument should drop through dimensions — but in your math, 'dimension' means the AXES (the "
        "recursive depth), not 3D/2D/1D space. So what IS the dimension it drops through?"
    ),
    "options": [
        {
            "label": "The same knob — depth IS the dimension",
            "implication": "One control: dropping a dimension = dropping a level of recursive depth. The spatial 3D/2D/1D is just how that depth looks.",
        },
        {
            "label": "Two knobs — spatial separate from depth",
            "implication": "The visual 3D/2D/1D is one control; your recursive depth is a separate one. They move independently.",
        },
        {
            "label": "Dimension is a standpoint on the one object",
            "implication": "Not a separate thing to change — a viewpoint on the single object (your viewpoint-duality applied to dimension).",
        },
    ],
    "scope": "global",
    "subtype": "theorem-fork",
    "legibility": {
        "name": "What 'dimension' the instrument drops through",
        "is": "Your theorem — the bedrock is yours",
        "why": (
            "The instrument is meant to drop through dimensions (3D↔2D↔1D), but your written math treats "
            "'dimension' as the axes / recursive depth, not spatial 3D/2D/1D — the two readings need "
            "reconciling. This is your call on what the dimension actually IS: the maths is yours, and the AI's "
            "read has erred here before (the cube correction), so this is flagged as your bedrock, not assumed. "
            "It decides how the cube instrument behaves at its heart."
        ),
    },
}
