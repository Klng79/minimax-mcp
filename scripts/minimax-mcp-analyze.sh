#!/bin/bash
# minimax-mcp-analyze.sh - Analyze images using MiniMax MCP
# Usage: minimax-mcp-analyze.sh "<prompt>" "<image_source>"
#   prompt: Question about the image (required)
#   image_source: URL or path to image (required)

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

export MINIMAX_API_KEY
export MINIMAX_API_HOST="${MINIMAX_API_HOST:-https://api.minimax.io}"

PROMPT="$1"
IMAGE_SOURCE="$2"

[ -z "$PROMPT" ] || [ -z "$IMAGE_SOURCE" ] && echo "Usage: minimax-mcp-analyze <prompt> <image_source>" && exit 1

ESCAPED_PROMPT=$(echo "$PROMPT" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))")
ESCAPED_IMAGE=$(echo "$IMAGE_SOURCE" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))")

(
  echo '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"openclaw","version":"1.0"}},"id":0}'
  sleep 1
  echo "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"understand_image\",\"arguments\":{\"prompt\":$ESCAPED_PROMPT,\"image_source\":$ESCAPED_IMAGE}},\"id\":2}"
  sleep 5
) | timeout 25 uvx minimax-coding-plan-mcp 2>/dev/null | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        data = json.loads(line)
        if 'result' in data and 'content' in data['result']:
            for item in data['result']['content']:
                if item.get('type') == 'text':
                    print(item['text'])
    except:
        pass
"
