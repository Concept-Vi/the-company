RELATION_TYPE = {
    "id": "reply_to",
    "directed": True,
    "label": "reply-to",
    "inverse": "has_reply",
    "desc": "This board item (a reply) REPLIES TO another comment/note board item — the threading edge. "
            "reply_to → board://<comment-id>. Builds comment THREADS: a comment/note links commented_on → an "
            "address; a reply links reply_to → that comment; reverse_traverse(comment, reply_to) gathers its "
            "replies (nest recursively). The 'replied-to comments' Tim named — annotation is a conversation, "
            "not a flat list.",
}
