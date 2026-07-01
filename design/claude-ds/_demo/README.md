# page-face demo — restart kit

After a WSL restart the two servers die (and /tmp is wiped). Everything else is durable on disk.

**Bring it back:** `bash ~/company/design/claude-ds/_demo/start.sh`

- `run_pages.py` — the real page-face service on 0.0.0.0:8774 (render_page + no-script CSP).
- `gen_faces.py` — regenerates `../face-index.js` from the live page-face bindings (the 3 real guide faces). Run only if the bindings change.
- Studio served from `design/claude-ds/` on :8775; the switcher lives in `app/canvases/Overview.jsx` (FacesPanel, 4 treatments A/B/C/D).

URLs (tailscale IP 100.81.137.106 is stable per-device):
- Studio:  http://100.81.137.106:8775/app/index.html
- A page:  http://100.81.137.106:8774/page?addr=guide://using_corpus_pipeline

OPEN THREAD (2026-06-29): the 4-way FacesPanel switcher is built + served but NOT yet self-verified
in a browser (the headless chrome instance wedged). First thing after restart: open the studio on the
phone, confirm the switcher + all 4 treatments render, fix anything off.
