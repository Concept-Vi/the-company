RELATION_TYPE = {
    "id": "commented_on",
    "directed": True,
    "label": "commented-on",
    "inverse": "has_comment",
    "desc": "A comment/feedback board item refers to this address (item -> any address: image://<id>, "
            "board://<id>, code://…, decision://…). The review/critique edge: file a board item whose body "
            "is the comment + a links=[{kind:'commented_on', target:'image://<id>'}]; reverse_traverse the "
            "target to gather every comment ON it. Powers the image-review workflow (compare + annotate).",
}
