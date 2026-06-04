"""rhm_mode — the right-hand-man's presence mode, as a NODE (context-05).

"The mode IS a node in the canvas/composition system. Switching it is editing a parameter."
The operator's presence preference lives as a node config in the `system` graph; set_mode is
just create_node/set_config (the same verbs that build any graph). This is the self-architecting
fold: the same composition system that runs the operator's work also configures the system itself.
"""
VERSION = '1'
KIND = 'content'
PORTS_IN = {}
PORTS_OUT = {'mode': 'Text'}
CONFIG = {                     # the presence dial (migrated flat→nested for the inspector).
    'mode': {                  # static enum (the 8 modes = suite.py MODES), NOT options_from — that's for live model lists only
        'type': 'enum',
        'label': 'Mode',
        'default': 'listening',
        'options': ['listening', 'text-only', 'background', 'focus',
                    'walkthrough', 'watch-and-react', 'decide-for-me', 'off'],
    },
    # Per-mode voice toggle (voice-trial lane H). Schema-additive: an existing rhm node with no
    # `voice_enabled` reads as 'on' (the default), so behaviour is unchanged. Modelled as an enum
    # (on/off) rather than a raw bool because the inspector renders enum + string (the only widget
    # types any node CONFIG uses today); a bool widget does not exist yet, so on/off keeps the
    # toggle renderable without inventing a widget the canvas can't draw. The accessor + gate live
    # in suite.py (Suite.voice_enabled); the conversation loop / chat gate consult it.
    # NOTE (flagged): this CONFIG field is GLOBAL on the single rhm node, not literally per-mode.
    # See suite.py voice_enabled() + the build report for the per-mode-vs-global decision.
    'voice_enabled': {
        'type': 'enum',
        'label': 'Voice',
        'default': 'on',
        'options': ['on', 'off'],
    },
}


def run(inputs, config):
    return config.get('mode', 'listening')
