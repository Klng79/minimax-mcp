#!/bin/bash
# minimax-mcp-search.sh - Search web using MiniMax MCP
# Usage: minimax-mcp-search.sh "<query>"
#   query: Search query (required)

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

QUERY="$1"
[ -z "$QUERY" ] && echo "Usage: minimax-mcp-search <query>" && exit 1

ESCAPED_QUERY=$(echo "$QUERY" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))")

(
  echo '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"openclaw","version":"1.0"}},"id":0}'
  sleep 1
  echo "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"web_search\",\"arguments\":{\"query\":$ESCAPED_QUERY}},\"id\":2}"
  sleep 4
) | timeout 20 uvx minimax-coding-plan-mcp 2>/dev/null | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        data = json.loads(line)
        if 'result' in data and 'content' in data['result']:
            for item in data['result']['content']:
                if item.get('type') == 'text':
                    text = item['text']
                    try:
                        parsed = json.loads(text)
                        if 'organic' in parsed:
                            for r in parsed['organic'][:5]:
                                print('• ' + r.get('title', 'N/A'))
                                if r.get('snippet'):
                                    s = r['snippet']
                                    print('  ' + (s[:150] + '...' if len(s) > 150 else s))
                                if r.get('link'):
                                    print('  ' + r['link'])
                                print()
                    except:
                        if text.strip():
                            print(text[:500])
    except:
        pass
"
