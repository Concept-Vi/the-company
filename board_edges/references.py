RELATION_TYPE = {
    "id": "references",
    "directed": True,
    "label": "references",
    "inverse": "referenced_by",
    "desc": "A directional cross-reference: this artifact references / is-compared-against / builds-on that "
            "one (any address ↔ any address — image://<id> ↔ image://<src>, image ↔ text, attachment ↔ "
            "attachment). The 'this generated output vs that source' link the comparison workflow needs: "
            "link a generated image to its source image, then traverse the edge to pair them.",
}
