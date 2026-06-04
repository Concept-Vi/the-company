"""RED→GREEN for gallery.py — the self-maintaining gallery. Run: python3 test_gallery.py
Real behaviour: render index.html FROM the register + which mockup files actually
exist (status derived from reality, never hand-set), grouped by area, with thumbs +
live links for produced views. No mocks."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gallery  # RED until gallery.py exists

def run():
    register = {
        "areas": {"A": "Canvas"},
        "views": [
            {"id": "A1", "area": "A", "title": "Empty", "platforms": ["desktop"], "represents": ["X"]},
            {"id": "A2", "area": "A", "title": "Running", "platforms": ["desktop", "mobile"], "represents": ["Y"]},
        ],
        "produced": {"wave1": [
            {"view": "A2", "variant": "desktop", "file": "mockups/A2-canvas-desktop.html",
             "thumb": "mockups/A2-canvas-desktop.jpeg"},
        ]},
    }
    existing = {"mockups/A2-canvas-desktop.html", "mockups/A2-canvas-desktop.jpeg"}
    html = gallery.render_gallery(register, existing)
    assert "Empty" in html and "Running" in html, "all views listed"
    assert "mockups/A2-canvas-desktop.jpeg" in html, "produced thumb shown"
    assert "mockups/A2-canvas-desktop.html" in html, "links the live mockup"
    assert "Canvas" in html, "area grouping present"
    # status derived from reality: A2 produced (file exists) -> grounded; A1 not -> planned
    assert "grounded" in html and "planned" in html, "status derived from file existence"
    print("PASS test_gallery (render from register + real files, status derived)")

run()
