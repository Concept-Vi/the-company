ORIGIN = 'system'  # brain-written (self-grown) — provenance layer
VERSION='1'
KIND='process'
PORTS_IN={'text':'Text'}
PORTS_OUT={'text':'Text'}

def run(inputs, config):
    return str(inputs.get('text', ''))[::-1]
