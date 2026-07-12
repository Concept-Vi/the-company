#!/usr/bin/env python3
"""validator.py — Stop-hook FORM VALIDATOR (C3.3). stdin = the Stop hook JSON; rules from rules.json
(DATA, C3.4). Violation → exit 2 + feedback on stderr (the model must redo). Clean → exit 0. Loud on own errors."""
import json, re, sys, os

def main():
    lab = os.path.dirname(os.path.abspath(__file__))
    try:
        data = json.load(sys.stdin)
    except Exception as e:
        print(f'VALIDATOR ERROR: bad stdin JSON: {e} — passing loudly', file=sys.stderr); return 0
    if data.get('stop_hook_active'):           # loop guard
        return 0
    tp = data.get('transcript_path', '')
    if not tp or not os.path.exists(tp):
        print('VALIDATOR ERROR: no readable transcript_path in Stop input — passing loudly', file=sys.stderr); return 0
    draft = ''
    try:
        with open(tp, errors='replace') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                try: o = json.loads(line)
                except Exception: continue
                m = o.get('message', {}) if isinstance(o.get('message'), dict) else {}
                if (o.get('type') or m.get('role')) == 'assistant':
                    c = m.get('content'); t = ''
                    if isinstance(c, str): t = c
                    elif isinstance(c, list):
                        t = ''.join(x.get('text', '') for x in c if isinstance(x, dict) and x.get('type') == 'text')
                    if t.strip(): draft = t
    except Exception as e:
        print(f'VALIDATOR ERROR: could not read transcript: {e} — passing loudly', file=sys.stderr); return 0
    if not draft:
        return 0
    rules = json.load(open(os.path.join(lab, 'rules.json')))['rules']
    for r in rules:
        if re.search(r['violation_regex'], draft, re.I):
            ab = r.get('absolver_regex')
            if ab and re.search(ab, draft, re.I):
                continue
            print(r['feedback'], file=sys.stderr)
            return 2
    return 0

sys.exit(main())
