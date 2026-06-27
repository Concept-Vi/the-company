#!/bin/bash
for i in $(seq 1 40); do
  curl -s -m 5 http://localhost:8000/v1/models >/dev/null 2>&1 && break
  grep -qE "CUDA out of memory|Traceback" ~/vllm-tests/serve_scan_restart.log && { echo "SERVER ERROR"; exit 1; }
  sleep 8
done
curl -s -m 5 http://localhost:8000/v1/models >/dev/null 2>&1 || { echo "still not up"; exit 1; }
echo ":8000 UP"
ROOT='/mnt/c/Users/Workstation001/Documents/Claude/Projects/Visual Designer'
REL='packages/elevenlabs-mcp/vault/ElevenLabs-Wizard/_discovery/vi-sync-design-context/03-REQUIREMENTS.md'
echo "distinct vi_sync_* in FILE: $(grep -oE 'vi_sync_[a-z_]+' "$ROOT/$REL" | sort -u | wc -l)"
python3 -c "
import json,urllib.request,re,capture2
ROOT='$ROOT'; rel='$REL'
body=open(ROOT+'/'+rel,encoding='utf-8',errors='ignore').read()
infile=set(re.findall(r'vi_sync_[a-z_]+', body))
p={'model':'cyankiwi/Qwen3.5-4B-AWQ-4bit','messages':[{'role':'system','content':capture2.SYS},{'role':'user','content':'PATH:'+rel+chr(10)+chr(10)+body}],'max_tokens':8000,'temperature':0,'repetition_penalty':1.2,'response_format':{'type':'json_schema','json_schema':{'name':'cap','schema':capture2.SCHEMA}}}
r=json.loads(urllib.request.urlopen(urllib.request.Request('http://localhost:8000/v1/chat/completions',data=json.dumps(p).encode(),headers={'Content-Type':'application/json'}),timeout=300).read())
d=json.loads(r['choices'][0]['message']['content'])
out=json.dumps(d)
inout=set(re.findall(r'vi_sync_[a-z_]+', out))
print('vi_sync_* in OUTPUT:', len(inout), '/ in file:', len(infile))
print()
for k,v in d.items():
    if isinstance(v,list):
        print(f'{k} ({len(v)}):')
        for x in v: print('   •', str(x)[:95])
    else: print(f'{k}: {str(v)[:130]}')
"
