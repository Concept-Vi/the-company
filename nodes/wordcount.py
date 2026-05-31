VERSION='1'
KIND='process'
PORTS_IN={'text':'Text'}
PORTS_OUT={'text':'Text'}
def run(inputs, config):
    return str(len(inputs.get('text','').split()))
