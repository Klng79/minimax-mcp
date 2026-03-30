---
name: minimax-mcp
description: "Use MiniMax MCP tools: web_search, understand_image, text-to-speech, and image_generation. Use when: (1) searching the web (2) analyzing images (3) generating voice audio (4) generating images from text. Requires MINIMAX_API_KEY environment variable or apiKey in config."
---

# MiniMax MCP Skill

Provides access to MiniMax's web search, image understanding, text-to-speech, and image generation tools.

## Prerequisites

- MINIMAX_API_KEY environment variable or config apiKey
- uvx (auto-installed if not present)
- bc (for floating point calculations)

## Tools

### web_search

Search the web using MiniMax's search API.

**Parameters:**
- `query` (string, required): Search query (3-5 keywords recommended)

**Usage:**
```bash
# Direct search
minimax-mcp-search "OpenClaw AI news"

# Returns JSON with search results
```

### understand_image

Analyze images using MiniMax's vision model.

**Parameters:**
- `prompt` (string, required): Question about the image
- `image_source` (string, required): URL or local file path

**Usage:**
```bash
# Analyze image from URL
minimax-mcp-analyze "What is in this image?" "https://example.com/photo.png"

# Analyze local image
minimax-mcp-analyze "Describe this" "/path/to/image.png"
```

### tts (Text-to-Speech)

Generate speech audio from text using MiniMax's TTS API.

**Parameters:**
- `text` (string, required): Text to convert to speech
- `voice_id` (string, optional): Voice ID (default: English_expressive_narrator)
- `speed` (float, optional): Speech speed 0.5-2.0 (default: 1)

**Available Voice IDs:**
- `English_expressive_narrator` (default)
- `Male_Narrator`
- `Female_Narrator`
- `english_expressive_c=clon`
- `english_expressive_n=clon`
- `male_narration_n=clon`

**Usage:**
```bash
# Basic TTS - default voice
tts.sh "Hello, this is a test message"

# Specify voice
tts.sh "Hello there!" "Male_Narrator"

# With custom speed (0.5-2.0)
tts.sh "Speak faster!" "English_expressive_narrator" 1.5

# Returns path to MP3 file
# Output: /tmp/minimax_tts_123456/tts_1234567890.mp3
```

**For Discord:** The returned file path can be sent as a Discord attachment.

### image_gen (Image Generation)

Generate images from text using MiniMax's image-01 model.

**Parameters:**
- `prompt` (string, required): Image description (max 1500 characters)
- `aspect_ratio` (string, optional): Image aspect ratio (default: 1:1)
- `n` (int, optional): Number of images 1-9 (default: 1)

**Aspect Ratios:**
- `1:1` (1024x1024) - square
- `16:9` (1280x720) - widescreen
- `4:3` (1152x864) - standard
- `3:2` (1248x832) - photo
- `2:3` (832x1248) - portrait
- `3:4` (864x1152) - portrait
- `9:16` (720x1280) - story/vertical
- `21:9` (1344x576) - ultrawide

**Usage:**
```bash
# Basic image generation
image_gen.sh "A beautiful sunset over the ocean"

# Specify aspect ratio
image_gen.sh "City skyline at night" "16:9"

# Generate multiple images
image_gen.sh "Abstract art" "1:1" 3

# Returns image URL (expires in 24 hours)
```

**For Discord:** The returned URL can be sent as an image attachment or embedded link.

## Environment

Set in config or environment:
```
MINIMAX_API_KEY=your_api_key_here
MINIMAX_API_HOST=https://api.minimax.io
```

## Implementation

- **web_search** and **understand_image**: Use uvx to run the MiniMax MCP server via JSON-RPC over stdio
- **tts**: Direct REST API call to MiniMax TTS endpoint, outputs hex-encoded MP3 decoded to binary file
- **image_gen**: Direct REST API call to MiniMax image generation endpoint, returns URL to generated image
