ORIGIN = 'system'  # brain-written (self-grown) — provenance layer
VERSION='1'
KIND='process'
PORTS_IN={'text':'Text'}
PORTS_OUT={'text':'Text'}
CONFIG: dict = {}   # no editable fields — pure transform, reads no config keys
def run(inputs, config):
    return str(len(inputs.get('text','').split()))
