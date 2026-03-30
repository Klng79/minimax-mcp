#!/bin/bash
# image_gen.sh - Image generation using MiniMax API
# Usage: image_gen.sh "<prompt>" [aspect_ratio] [n]
#   prompt: Image description (required, max 1500 chars)
#   aspect_ratio: 1:1, 16:9, 4:3, 3:2, 2:3, 3:4, 9:16, 21:9 (default: 1:1)
#   n: Number of images 1-9 (default: 1)

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

PROMPT="$1"
ASPECT_RATIO="${2:-1:1}"
N="${3:-1}"

if [ -z "$PROMPT" ]; then
    echo "Error: Prompt required"
    exit 1
fi

API_HOST="${MINIMAX_API_HOST:-https://api.minimax.io}"

RESPONSE=$(curl -s -X POST "${API_HOST}/v1/image_generation" \
    -H "Authorization: Bearer $MINIMAX_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
        \"model\": \"image-01\",
        \"prompt\": \"$PROMPT\",
        \"aspect_ratio\": \"$ASPECT_RATIO\",
        \"response_format\": \"url\",
        \"n\": $N
    }")

echo "$RESPONSE" | jq -r '.data[0].url // .data[].url // empty'
