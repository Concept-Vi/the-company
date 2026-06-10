"""mcp_face/tools/dials.py — the DIALS tool (Track-1 on the face).

ONE resource (the entity's adjustable character traits), an `op` selector. Registry-is-truth
(definitions are dials/ rows, rediscovered per call); VALUES persist on the system graph (the same
seam as the presence mode). Setting a dial is declarative config (reversible, Tim-adjustable by
design) — the whole point is that he turns knobs instead of making decisions."""


def register(mcp, suite):
    @mcp.tool()
    def dials(op: str, dial: str = "", value: str = "", overrides: list | None = None) -> dict:
        """The entity's CHARACTER DIALS — adjustable traits (not one-time decisions): how far ahead
        the brain thinks (anticipation), how much the surface may move on its own (stability), and
        any dial added later as a dials/<id>.py row.

        Pick `op`:
          · 'list'     — every dial: positions, current value, default, what it governs.
          · 'describe' — ONE dial in full (dial= required).
          · 'set'      — turn a dial (dial= + value=, a declared position name) and/or store
                         condition-scoped overrides (overrides=[{when, value}] — declared condition
                         data in the rules-engine shape; conditions COMBINE). Overrides are stored +
                         validated NOW and evaluated once the now-organ/rules wiring exists — until
                         then the flat value applies (state echoes overrides_evaluated=False).

        Consumers read the current value via dial_state; a dial's `governs` names its consumer seams
        honestly (including not-yet-built ones)."""
        if op == "list":
            return suite.dial_state()
        if op == "describe":
            if not dial:
                raise ValueError("dials(op='describe') needs dial= — use op='list' to see them.")
            return suite.dial_state(dial)
        if op == "set":
            if not dial:
                raise ValueError("dials(op='set') needs dial= — use op='list' to see them.")
            if not value and overrides is None:
                raise ValueError("dials(op='set') needs value= (a position name) and/or overrides=.")
            return suite.set_dial(dial, value=value or None, overrides=overrides)
        raise ValueError(f"unknown op {op!r} — dials ops are list | describe | set.")
