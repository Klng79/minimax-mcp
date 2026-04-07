# MiniMax MCP Server

A Model Context Protocol (MCP) server that provides tools for web search, image understanding, text-to-speech, and image generation using the MiniMax API.

## Tools

### minimax_web_search
Search the web using MiniMax's search API.
- **Parameters:** `query` (string), `response_format` (markdown|json)
- **Returns:** Search results with titles, snippets, and links

### minimax_understand_image
Analyze images using MiniMax's vision model. Calls `/v1/coding_plan/vlm` directly via HTTP — no subprocess, no external dependencies.
- **Parameters:** `prompt` (string), `image_source` (URL or local path), `response_format`
- **Returns:** Detailed image analysis
- **Supported formats:** JPEG, PNG, WebP

### minimax_text_to_speech
Generate speech audio from text.
- **Parameters:** `text` (string, max 5000), `voice_id` (enum), `speed` (0.5-2.0)
- **Returns:** Path to generated MP3 file
- **Recommended voice:** `English_expressive_narrator` (others may not be available on all plans)

### minimax_generate_image
Generate images from text descriptions.
- **Parameters:** `prompt` (string, max 1500), `aspect_ratio` (enum), `n` (1-9)
- **Returns:** Local path(s) to generated image file(s)

## Setup

### 1. Install dependencies
```bash
cd /path/to/minimax-mcp
pip install -r requirements.txt
```

### 2. Configure API key

Set the `MINIMAX_API_KEY` environment variable:
```bash
export MINIMAX_API_KEY="your_api_key_here"
```

Or add it to your shell profile (`~/.zshrc` or `~/.bashrc`).

### Windows Installation

On Windows, use the same pip command but set the environment variable differently:

**1. Install dependencies**
```cmd
pip install -r requirements.txt
```

**2. Set your API key**
```cmd
set MINIMAX_API_KEY=your_api_key_here
```
Or set permanently via **System Properties → Environment Variables**.

**3. Add to Claude Code**
Edit `%APPDATA%\Claude\settings.json` and add:
```json
{
  "mcpServers": {
    "minimax": {
      "command": "python",
      "args": ["C:\\path\\to\\minimax-mcp\\minimax_mcp.py"],
      "env": {
        "MINIMAX_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

> **Note:** Use `python` instead of `python3` on Windows.

### 3. Use with Claude Code

Add to your Claude Code configuration in `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "minimax": {
      "command": "python3",
      "args": ["/absolute/path/to/minimax-mcp/minimax_mcp.py"],
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
      "args": ["/absolute/path/to/minimax-mcp/minimax_mcp.py"]
    }
  }
}
```

### 4. Restart Claude Code

After updating settings, restart Claude Code to load the new MCP server.

## Hermes / mcporter Integration

The server is auto-discovered by Hermes's `mcporter` CLI once configured in `~/.claude.json` or OpenClaw config (same JSON structure as Claude Code above).

```bash
# List tools
mcporter list minimax --schema

# Web search
mcporter call minimax.minimax_web_search query="MiniMax AI API" --output json

# Image understanding (can be slow — set timeout explicitly)
MCPORTER_CALL_TIMEOUT=120000 mcporter call minimax.minimax_understand_image \
  params='{"prompt": "What is in this image?", "image_source": "https://example.com/photo.jpg"}' \
  --output json

# Text-to-speech
mcporter call minimax.minimax_text_to_speech \
  params='{"text": "Hello world", "voice_id": "English_expressive_narrator"}' --output json

# Image generation
mcporter call minimax.minimax_generate_image \
  params='{"prompt": "A sunset over the ocean", "aspect_ratio": "16:9"}' --output json
```

> **Important:** `minimax_understand_image` requires downloading the image and converting it to base64 before sending to the API. Default mcporter timeouts (60s) may not be enough. Use `MCPORTER_CALL_TIMEOUT=120000` (2 minutes) for this tool.

## Available Voice IDs for TTS

- `English_expressive_narrator` (default — confirmed working)
- `Male_Narrator` — may not be available on all API plans
- `Female_Narrator` — may not be available on all API plans
- `english_expressive_c=clon` — may not be available on all API plans
- `english_expressive_n=clon` — may not be available on all API plans
- `male_narration_n=clon` — may not be available on all API plans

> Only `English_expressive_narrator` is guaranteed to work. Other voice IDs may return "voice id not exist" depending on your plan.

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

### "minimax appears offline" in mcporter
The server process may be running old code. Kill stale processes and try again:
```bash
pkill -f "minimax_mcp"
```

### "voice id not exist" for TTS
Only `English_expressive_narrator` is confirmed working. Other voice IDs depend on your API plan.

### understand_image times out in mcporter
Use `MCPORTER_CALL_TIMEOUT=120000` to give the image download and encoding enough time.

### uvx not found
Install uvx with: `pip install uv`
