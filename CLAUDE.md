# MiniMax MCP Server

A Model Context Protocol (MCP) server that provides tools for web search, image understanding, text-to-speech, and image generation using the MiniMax API.

## Tools

### minimax_web_search
Search the web using MiniMax's search API.
- **Parameters:** `query` (string), `response_format` (markdown|json)
- **Returns:** Search results with titles, snippets, and links

### minimax_understand_image
Analyze images using MiniMax's vision model.
- **Parameters:** `prompt` (string), `image_source` (URL or local path), `response_format`
- **Returns:** Detailed image analysis

### minimax_text_to_speech
Generate speech audio from text.
- **Parameters:** `text` (string, max 5000), `voice_id` (enum), `speed` (0.5-2.0)
- **Returns:** Path to generated MP3 file

### minimax_generate_image
Generate images from text descriptions.
- **Parameters:** `prompt` (string, max 1500), `aspect_ratio` (enum), `n` (1-9)
- **Returns:** Image URL(s) (valid for 24 hours)

## Setup

### 1. Install dependencies
```bash
cd /Users/alexng/Desktop/Developer/mypanuc/minimax-mcp
pip install -r requirements.txt
```

### 2. Configure API key

Set the `MINIMAX_API_KEY` environment variable:
```bash
export MINIMAX_API_KEY="your_api_key_here"
```

Or add it to your shell profile (`~/.zshrc` or `~/.bashrc`).

### 3. Use with Claude Code

Add to your Claude Code configuration in `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "minimax": {
      "command": "python3",
      "args": ["/Users/alexng/Desktop/Developer/mypanuc/minimax-mcp/minimax_mcp.py"],
      "env": {
        "MINIMAX_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Or use via uvx (requires Python 3.11+):
```json
{
  "mcpServers": {
    "minimax": {
      "command": "uvx",
      "args": ["/Users/alexng/Desktop/Developer/mypanuc/minimax-mcp/minimax_mcp.py"]
    }
  }
}
```

### 4. Restart Claude Code

After updating settings, restart Claude Code to load the new MCP server.

## Available Voice IDs for TTS

- `English_expressive_narrator` (default)
- `Male_Narrator`
- `Female_Narrator`
- `english_expressive_c=clon`
- `english_expressive_n=clon`
- `male_narration_n=clon`

## Available Aspect Ratios for Image Generation

- `1:1` (1024x1024) - square
- `16:9` (1280x720) - widescreen
- `4:3` (1152x864) - standard
- `3:2` (1248x832) - photo
- `2:3` (832x1248) - portrait
- `3:4` (864x1152) - portrait tall
- `9:16` (720x1280) - story/vertical
- `21:9` (1344x576) - ultrawide

## Troubleshooting

### "MINIMAX_API_KEY is not set"
Make sure the environment variable is exported before running Claude Code, or add it to your settings.json.

### uvx not found
Install uvx with: `pip install uv`
