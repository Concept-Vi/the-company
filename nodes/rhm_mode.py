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
CONFIG = {'mode': 'listening'}


def run(inputs, config):
    return config.get('mode', 'listening')
