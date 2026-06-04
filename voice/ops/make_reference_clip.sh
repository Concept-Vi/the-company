#!/usr/bin/env bash
# voice/ops/make_reference_clip.sh — POST-RESTART: mint the shared COMPANY_VOICE_REF clip.
#
# Tim has no specific voice in mind; he wants a refined, mature, Australian female. The three CLONE
# engines (chatterbox/xtts/cosyvoice) need a REAL reference wav (COMPANY_VOICE_REF) and FAIL LOUD
# without one — no clip was fabricated. Qwen3-VoiceDesign needs NO clip: it DESIGNS the voice from a
# text description. So the plan is:
#
#   1. Start qwen3tts (:4128).                          voice-stack start qwen3tts
#   2. Have it synthesize a sample IN the designed character (personas.VOICE_BASE description).
#   3. Save that wav as COMPANY_VOICE_REF.
#   4. The clone engines then clone THAT designed voice → all five characters share ONE identity,
#      shaded per persona. No human recording, no licensed clip needed.
#
# This makes Qwen3-VoiceDesign the IDENTITY SOURCE and the other engines realism/character variations
# of the same voice — exactly the trial's "same woman underneath, five souls on top".
#
# Run AFTER the 40GB restart, once qwen3tts is up on :4128. Pre-restart this cannot run (model load
# needs the GPU). Idempotent: re-run to regenerate with a tweaked description.
set -euo pipefail

REF_DIR=/home/tim/company/voice/ref
REF_PATH="${COMPANY_VOICE_REF:-$REF_DIR/company_voice_ref.wav}"
QWEN_URL="http://127.0.0.1:4128"

# The reference text — a few sentences so the clone engines get enough timbre/prosody (~6-12s).
REF_TEXT="${COMPANY_VOICE_REF_TEXT:-Hello. This is the voice of the Company. Let us take a look at what you are building together, and see where it leads.}"

# The designed voice description (personas.VOICE_BASE — the refined mature Australian base).
REF_DESC="${COMPANY_VOICE_REF_DESC:-A refined, educated Australian woman in her early forties. Clear and articulate, not broad, country, or ocker. Warm, mid-low pitch; unhurried, composed pace. Dry, understated wit with a sense of refinement and a little mystery.}"

mkdir -p "$REF_DIR"

echo "[ref] checking qwen3tts is up on :4128 ..."
if ! curl -sf -m 5 "$QWEN_URL/health" >/dev/null; then
  echo "[ref] FAIL: qwen3tts (:4128) is not up. Start it first: voice-stack start qwen3tts" >&2
  exit 1
fi

echo "[ref] synthesizing the designed reference voice → $REF_PATH"
# Build the JSON safely (handles quotes/newlines in the text/description).
payload=$(REF_TEXT="$REF_TEXT" REF_DESC="$REF_DESC" python3 -c \
  'import json,os; print(json.dumps({"text":os.environ["REF_TEXT"],"voice":os.environ["REF_DESC"]}))')
# Qwen3-VoiceDesign takes the description as the `voice` arg (the engine passes it as `instruct`).
http_code=$(curl -sS -m 300 -o "$REF_PATH" -w '%{http_code}' \
  -X POST "$QWEN_URL/tts" \
  -H 'Content-Type: application/json' \
  --data "$payload")

if [ "$http_code" != "200" ]; then
  echo "[ref] FAIL: qwen3tts /tts returned HTTP $http_code" >&2
  head -c 400 "$REF_PATH" >&2 || true
  exit 1
fi

bytes=$(stat -c%s "$REF_PATH")
if [ "$bytes" -le 44 ]; then
  echo "[ref] FAIL: produced an empty/header-only wav ($bytes bytes)" >&2
  exit 1
fi

echo "[ref] OK: $REF_PATH ($bytes bytes)."
echo "[ref] Set this for the clone engines (already the default in voice/ops/voice.env):"
echo "        export COMPANY_VOICE_REF=$REF_PATH"
echo "[ref] Then start the clone engines: voice-stack start chatterbox; voice-stack start xtts; voice-stack start cosyvoice"
