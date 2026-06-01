ORIGIN = 'system'  # brain-written (self-grown) — provenance layer
VERSION='1'
KIND='process'
PORTS_IN={'open': 'Boolean'}
PORTS_OUT={'html': 'Text', 'settings': 'Record'}

def run(inputs, config):
    open_val = inputs.get('open', False)
    fields = config.get('fields', [])
    html = '<details'
    if open_val:
        html += ' open'
    html += '>\n<summary>Settings</summary>\n<div style="padding: 0.5em;">\n'
    settings = {}
    for f in fields:
        key = f['key']
        label = f.get('label', key)
        ftype = f.get('type', 'text')
        default = f.get('default', None)
        if default is not None:
            settings[key] = default
        html += f'  <label style="display: block; margin-bottom: 0.5em;">{label}</label>\n'
        if ftype == 'text':
            val = str(default) if default is not None else ''
            html += f'  <input type="text" id="{key}" value="{val}" style="width: 100%; margin-bottom: 0.5em;">\n'
        elif ftype == 'number':
            val = str(default) if default is not None else '0'
            html += f'  <input type="number" id="{key}" value="{val}" style="width: 100%; margin-bottom: 0.5em;">\n'
        elif ftype == 'select':
            options = f.get('options', [])
            html += f'  <select id="{key}" style="width: 100%; margin-bottom: 0.5em;">\n'
            for opt in options:
                selected = ' selected' if default is not None and default == opt else ''
                html += f'    <option value="{opt}"{selected}>{opt}</option>\n'
            html += '  </select>\n'
        elif ftype == 'boolean':
            checked = ' checked' if default else ''
            html += f'  <input type="checkbox" id="{key}"{checked} style="margin-bottom: 0.5em;">\n'
    html += '</div>\n</details>'
    return {'html': html, 'settings': settings}
