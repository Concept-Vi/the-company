"""mark_types/comment.py — INTERACTION mark-type: comment (operator direction at an addressed element).

The disposition the operator writes when commenting/directing on a rendered gallery element — the
route-back of `gallery:direction` → `runtime.territory.territory_write` → `suite.mark`. The sub-type
rides in `annotation_type` (note/direction/correction/question/praise/discuss — wildcard's
taxonomies.json content types); `value` is the free-text comment. direction `surface` (operator input —
positive signal, not denoising). An INTERACTION mark-type, beside the analysis types
(ai_fingerprint/strain/…); registry-is-truth, additive. id MUST equal the file stem (`comment`).
"""

MARK_TYPE = {
    "id": "comment",
    "value_shape": "free",
    "direction": "surface",
    "desc": "an operator comment/direction at an addressed element (sub-type in annotation_type: note/direction/correction/question/praise/discuss) — the route-back of gallery:direction",
}
