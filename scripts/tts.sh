#!/bin/bash
# tts.sh - Text-to-Speech using MiniMax API
# Usage: tts.sh "<text>" [voice_id] [speed]
#   text: Text to convert to speech (required)
#   voice_id: Voice ID (default: English_expressive_narrator)
#   speed: Speech speed 0.5-2.0 (default: 1)
# Output: Path to generated MP3 file

set -e

# Load API key from environment or config file
load_api_key() {
    if [ -n "$MINIMAX_API_KEY" ]; then
        return
    fi

    # Try to load from config
    CONFIG_PATH="$HOME/.openclaw/config.json"
    if [ -f "$CONFIG_PATH" ]; then
        MINIMAX_API_KEY=$(grep -o '"apiKey"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_PATH" 2>/dev/null | head -1 | sed 's/.*"\([^"]*\)"$/\1/')
    fi
}

load_api_key

if [ -z "$MINIMAX_API_KEY" ]; then
    echo "Error: MINIMAX_API_KEY not set. Set it in environment or config.json" >&2
    exit 1
fi

TEXT="$1"
VOICE_ID="${2:-English_expressive_narrator}"
SPEED="${3:-1}"

# Validate speed range
if (( $(echo "$SPEED < 0.5 || $SPEED > 2.0" | bc -l) )); then
    echo "Error: Speed must be between 0.5 and 2.0" >&2
    exit 1
fi

API_HOST="${MINIMAX_API_HOST:-https://api.minimax.io}"

# Create temp directory for output
TEMP_DIR="${TMPDIR:-/tmp}/minimax_tts_$$"
mkdir -p "$TEMP_DIR"
OUTPUT_FILE="$TEMP_DIR/tts_$(date +%s).mp3"

# Escape JSON string
ESCAPED_TEXT=$(printf '%s' "$TEXT" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")

# Call MiniMax TTS API
RESPONSE=$(curl -s -X POST "${API_HOST}/v1/t2a_v2" \
    -H "Authorization: Bearer ${MINIMAX_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
        \"model\": \"speech-2.8-hd\",
        \"text\": $ESCAPED_TEXT,
        \"stream\": false,
        \"output_format\": \"hex\",
        \"voice_setting\": {
            \"voice_id\": \"$VOICE_ID\",
            \"speed\": $SPEED,
            \"vol\": 1,
            \"pitch\": 0
        },
        \"audio_setting\": {
            \"sample_rate\": 32000,
            \"bitrate\": 128000,
            \"format\": \"mp3\",
            \"channel\": 1
        }
    }")

# Check for errors in response
if echo "$RESPONSE" | grep -q '"status_code"'; then
    STATUS=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('base_resp',{}).get('status_code', -1))" 2>/dev/null || echo "-1")
    if [ "$STATUS" != "0" ]; then
        MSG=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('base_resp',{}).get('status_msg', 'Unknown error'))" 2>/dev/null || echo "Parse error")
        echo "Error: API returned status $STATUS - $MSG" >&2
        rm -rf "$TEMP_DIR"
        exit 1
    fi
fi

# Extract hex audio and decode to binary
HEX_AUDIO=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('audio',''))" 2>/dev/null)

if [ -z "$HEX_AUDIO" ]; then
    echo "Error: No audio data in response" >&2
    echo "Response: $RESPONSE" >&2
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Convert hex to binary MP3
echo "$HEX_AUDIO" | xxd -r -p > "$OUTPUT_FILE"

# Verify the file is valid
if [ ! -s "$OUTPUT_FILE" ]; then
    echo "Error: Failed to create audio file" >&2
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Check file size is reasonable (at least 100 bytes for valid MP3)
FILE_SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null || echo "0")
if [ "$FILE_SIZE" -lt 100 ]; then
    echo "Error: Generated audio file is too small ($FILE_SIZE bytes)" >&2
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo "$OUTPUT_FILE"
