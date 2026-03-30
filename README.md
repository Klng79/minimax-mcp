# MiniMax MCP Server

A Model Context Protocol (MCP) server that provides tools for web search, image understanding, text-to-speech, and image generation using the MiniMax API.

## Features

- **Web Search** — Search the web with MiniMax's search API
- **Image Understanding** — Analyze images from URLs or local files using vision models
- **Text-to-Speech** — Generate natural speech audio with multiple voice options
- **Image Generation** — Create images from text descriptions

## Requirements

- Python 3.11+
- MiniMax API key

## Installation

### Clone the repository

```bash
git clone https://github.com/Klng79/minimax-mcp.git
cd minimax-mcp
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Set your API key

Export your MiniMax API key as an environment variable:

```bash
export MINIMAX_API_KEY="your_api_key_here"
```

Or add it to your shell profile (`~/.zshrc` or `~/.bashrc`) for persistence.

### Windows Installation

On Windows, the steps are similar but paths and commands differ slightly.

**1. Install dependencies**

```cmd
pip install -r requirements.txt
```

**2. Set your API key**

Set the `MINIMAX_API_KEY` environment variable via Command Prompt or PowerShell:

```cmd
set MINIMAX_API_KEY=your_api_key_here
```

Or set it permanently via **System Properties → Environment Variables**.

**3. Add to Claude Code**

Open `%APPDATA%\Claude\settings.json` in a text editor and add:

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

**4. Restart Claude Code**

After updating settings, restart Claude Code to load the new MCP server.

## Usage

### Claude Code Integration

Add the server to your Claude Code configuration in `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "minimax": {
      "command": "python3",
      "args": ["/path/to/minimax-mcp/minimax_mcp.py"]
    }
  }
}
```

Make sure `MINIMAX_API_KEY` is set in your environment before launching Claude Code.

### Command Line

You can also use the Python server directly:

```bash
python minimax_mcp.py
```

## Tools

### minimax_web_search

Search the web using MiniMax's search API.

**Parameters:**
- `query` (string, required) — Search query (3-5 keywords recommended)
- `response_format` (string) — Output format: `markdown` (default) or `json`

### minimax_understand_image

Analyze images using MiniMax's vision model.

**Parameters:**
- `prompt` (string, required) — Question or instruction about the image
- `image_source` (string, required) — URL or local file path to the image
- `response_format` (string) — Output format: `markdown` (default) or `json`

### minimax_text_to_speech

Generate speech audio from text.

**Parameters:**
- `text` (string, required) — Text to convert (max 5000 characters)
- `voice_id` (string) — Voice selection (default: `English_expressive_narrator`)
- `speed` (float) — Speech speed 0.5-2.0 (default: 1.0)

**Available Voices:**
- `English_expressive_narrator` (default)
- `Male_Narrator`
- `Female_Narrator`
- `english_expressive_c=clon`
- `english_expressive_n=clon`
- `male_narration_n=clon`

### minimax_generate_image

Generate images from text descriptions.

**Parameters:**
- `prompt` (string, required) — Image description (max 1500 characters)
- `aspect_ratio` (string) — Image dimensions (default: `1:1`)
- `n` (int) — Number of images 1-9 (default: 1)

**Aspect Ratios:**
- `1:1` (1024x1024) — square
- `16:9` (1280x720) — widescreen
- `4:3` (1152x864) — standard
- `3:2` (1248x832) — photo
- `2:3` (832x1248) — portrait
- `3:4` (864x1152) — portrait tall
- `9:16` (720x1280) — story/vertical
- `21:9` (1344x576) — ultrawide

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MINIMAX_API_KEY` | Your MiniMax API key | Yes |
| `MINIMAX_API_HOST` | API host URL (default: `https://api.minimax.io`) | No |

### Claude Desktop App

For Claude Desktop App, add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

## Security Notes

- **Never commit your API key** to version control
- Use environment variables to pass sensitive credentials
- The server reads `MINIMAX_API_KEY` from the environment, never from config files in the repo

### Claude Desktop App

**macOS:**
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

**Windows:**
Add to `%APPDATA%\Claude\claude_desktop_config.json`:

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

## License

MIT
