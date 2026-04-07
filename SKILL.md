---
name: minimax-mcp
description: "Use MiniMax MCP tools: web_search, understand_image, text-to-speech, and image_generation via Hermes mcporter or direct Python. Use when: (1) searching the web (2) analyzing images (3) generating voice audio (4) generating images from text. Requires MINIMAX_API_KEY environment variable."
---

# MiniMax MCP Skill

Provides access to MiniMax's web search, image understanding, text-to-speech, and image generation tools.

## Prerequisites

- MINIMAX_API_KEY environment variable
- Python 3.11+
- httpx, fastmcp, pydantic (see requirements.txt)

## Tools

### web_search

Search the web using MiniMax's search API.

**Parameters:**
- `query` (string, required): Search query (3-5 keywords recommended)
- `response_format` (string, optional): `markdown` (default) or `json`

**Usage via mcporter:**
```bash
mcporter call minimax.minimax_web_search query="MiniMax AI API" --output json
```

### understand_image

Analyze images using MiniMax's vision model. Calls `/v1/coding_plan/vlm` directly via HTTP — no subprocess, no external dependencies.

**Parameters:**
- `prompt` (string, required): Question about the image
- `image_source` (string, required): HTTP/HTTPS URL, local file path, or base64 data URL
- `response_format` (string, optional): `markdown` (default) or `json`

**Supported formats:** JPEG, PNG, WebP

**Usage via mcporter:**
```bash
# Image from URL (set higher timeout — downloads + encodes the image)
MCPORTER_CALL_TIMEOUT=120000 mcporter call minimax.minimax_understand_image \
  params='{"prompt": "What is in this image?", "image_source": "https://example.com/photo.jpg"}' \
  --output json

# Local image
mcporter call minimax.minimax_understand_image \
  params='{"prompt": "Describe this image", "image_source": "/path/to/image.png"}' --output json
```

### tts (Text-to-Speech)

Generate speech audio from text using MiniMax's TTS API.

**Parameters:**
- `text` (string, required): Text to convert to speech (max 5000 chars)
- `voice_id` (string, optional): Voice ID
- `speed` (float, optional): Speech speed 0.5-2.0 (default: 1.0)

**Recommended voice:** `English_expressive_narrator` — this is the only voice confirmed to work on all API plans.

**Other available voice IDs** (may return "voice id not exist" depending on plan):
- `Male_Narrator`
- `Female_Narrator`
- `english_expressive_c=clon`
- `english_expressive_n=clon`
- `male_narration_n=clon`

**Usage via mcporter:**
```bash
mcporter call minimax.minimax_text_to_speech \
  params='{"text": "Hello world", "voice_id": "English_expressive_narrator", "speed": 1.0}' \
  --output json
```

**Returns:** Path to a generated MP3 file.

### image_gen (Image Generation)

Generate images from text using MiniMax's image generation model.

**Parameters:**
- `prompt` (string, required): Image description (max 1500 characters)
- `aspect_ratio` (string, optional): Image aspect ratio (default: `1:1`)
- `n` (int, optional): Number of images 1-9 (default: 1)

**Aspect Ratios:**
- `1:1` (1024x1024) - square
- `16:9` (1280x720) - widescreen
- `4:3` (1152x864) - standard
- `3:2` (1248x832) - photo
- `2:3` (832x1248) - portrait
- `3:4` (864x1152) - portrait tall
- `9:16` (720x1280) - story/vertical
- `21:9` (1344x576) - ultrawide

**Usage via mcporter:**
```bash
mcporter call minimax.minimax_generate_image \
  params='{"prompt": "A beautiful sunset over the ocean", "aspect_ratio": "16:9", "n": 1}' \
  --output json
```

**Returns:** Local path to the generated image file (JPEG).

## Hermes / mcporter Setup

### 1. Add to your Hermes config

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

### 2. Restart Hermes

After updating the config, restart Hermes to load the MCP server.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MINIMAX_API_KEY` | Your MiniMax API key | Yes |
| `MINIMAX_API_HOST` | API host URL (default: `https://api.minimax.io`) | No |

## Troubleshooting

### "minimax appears offline" in mcporter
The server process is running stale code. Kill it and restart:
```bash
pkill -f "minimax_mcp"
```

### "voice id not exist" for TTS
Only `English_expressive_narrator` is confirmed working. Switch to the default voice.

### understand_image times out
Use `MCPORTER_CALL_TIMEOUT=120000` when calling this tool via mcporter.

## Implementation Notes

- **understand_image**: Direct HTTP POST to `/v1/coding_plan/vlm` using httpx. Image is downloaded (remote) or read (local), converted to base64 data URL, then sent in the request body.
- **web_search**: Direct HTTP POST to `/v1/text/chatcompletion_pro`.
- **tts**: Direct HTTP POST to `/v1/t2a_v2` with hex-encoded MP3 output decoded to binary file.
- **image_gen**: Direct HTTP POST to `/v1/image_generation` returning local file paths.
- No subprocess or external server process is used by any tool.
