"""RED→GREEN test for the token emitter. Run: python3 test_emit.py
Tests real behaviour: imports emit, resolves a primitive-ref, emits flat tokens +
root_extra, and proves the one-place-change (edit a primitive → every token that
refs it changes). No mocks."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emit  # RED until emit.py exists

def run():
    data = {
        "imports": ["FONTURL"],
        "root_extra": {"font-size": "14px"},
        "primitives": {"mint": "#54d6b0"},
        "groups": [
            {"name": "signal", "tokens": {"acc": {"ref": "mint"}, "ok": {"ref": "mint"}, "flat": {"v": "10px"}}},
        ],
    }
    css = emit.emit(data)
    assert "@import url('FONTURL');" in css, "import line missing"
    assert "--acc:#54d6b0" in css, f"primitive-ref not resolved:\n{css}"
    assert "--ok:#54d6b0" in css, "second ref not resolved"
    assert "--flat:10px" in css, "flat token missing"
    assert "font-size:14px" in css, "root_extra missing"
    assert "GENERATED" in css, "generated-file header missing"
    # the one-place-change proof: edit the primitive → every ref changes
    data["primitives"]["mint"] = "#000000"
    css2 = emit.emit(data)
    assert "--acc:#000000" in css2 and "--ok:#000000" in css2, "primitive change did not propagate to refs"
    print("PASS test_emit (ref-resolution + one-place-change)")

run()
