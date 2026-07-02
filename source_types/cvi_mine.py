SOURCE_TYPE = {
    "id": "cvi_mine",
    "label": "cvi_mine notice_board_posts (④ L6 pour)",
    "join_keys": ["author", "path", "time"],
    "desc": "The cloud notice_board_posts store (cvi_mine), poured into the board by ④ L6 BOARD "
            "(ops/migrate_board_from_cvi.py). Marks an item's origin as the migrated cloud operational "
            "board (A2 in organ-studies/BOARD.md), distinct from the default claude_code origin. Correlates "
            "with other sources by the shared author+path+time join.",
}
