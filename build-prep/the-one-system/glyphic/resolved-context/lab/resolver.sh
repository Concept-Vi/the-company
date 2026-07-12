#!/bin/bash
# resolver.sh — SLICE-S1 turn-resolution (C2): UserPromptSubmit hook → resolve context from the
# LIVE ctx substrate (local Supabase PG) → emit it on stdout (exit 0 = injected into the turn).
# LOUD-FAIL (C2.4): any substrate failure prints RESOLVER ERROR — never silent, never fabricated.
set -u
LAB_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$LAB_DIR/resolutions.jsonl"

IN=$(cat 2>/dev/null || echo '{}')
PROMPT=$(printf '%s' "$IN" | python3 -c "import json,sys; print(json.load(sys.stdin).get('prompt',''))" 2>/dev/null || echo '')
SID=$(printf '%s' "$IN" | python3 -c "import json,sys; print(json.load(sys.stdin).get('session_id',''))" 2>/dev/null || echo '')

export PGPASSWORD="${CTX_PGPASSWORD:-postgres}"
PGH="${CTX_PGHOST:-127.0.0.1}"; PGP="${CTX_PGPORT:-15432}"

# term extraction for v0 relevance (words >3 chars from the prompt)
TERMS=$(printf '%s' "$PROMPT" | tr -cs '[:alnum:]' '\n' | awk 'length($0)>3' | head -8 | tr '\n' ' ')

SQL="
with rel as (
  select address_path, type, state, body, ts,
    (case when state='open' then 2 else 0 end)"
for w in $TERMS; do
  w_esc=$(printf '%s' "$w" | sed "s/'/''/g")
  SQL="$SQL + (case when body ilike '%${w_esc}%' then 1 else 0 end)"
done
SQL="$SQL as score
  from ctx.unit where body is not null and type <> 'resolver_log'
)
select '['||state||'] '||address_path||' :: '||left(body,240) from rel
where score > 0 order by score desc, ts desc limit 8;"

ROWS=$(psql -h "$PGH" -p "$PGP" -U postgres -d postgres -tA -c "$SQL" 2>&1)
RC=$?
if [ $RC -ne 0 ]; then
  echo "RESOLVER ERROR: ctx substrate unreachable or query failed (psql rc=$RC): $(printf '%s' "$ROWS" | head -2)"
  printf '{"ts":"%s","session":"%s","error":true}\n' "$(date -Is)" "$SID" >> "$LOG"
  exit 0   # inject the LOUD error line itself; never block the turn silently
fi

if [ -n "$ROWS" ]; then
  echo "RESOLVED CONTEXT (from the ctx substrate — units matching this turn; [open] = awaiting resolution):"
  echo "$ROWS"
  N=$(printf '%s\n' "$ROWS" | wc -l)
else
  echo "RESOLVED CONTEXT: no matching units in the substrate for this turn."
  N=0
fi
printf '{"ts":"%s","session":"%s","units":%s}\n' "$(date -Is)" "$SID" "$N" >> "$LOG"
exit 0
