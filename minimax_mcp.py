#!/usr/bin/env python3
"""
MiniMax MCP Server.

Provides tools for web search, image understanding, text-to-speech,
and image generation using the MiniMax API.
"""

import os
import json
import time
import tempfile
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
import httpx

from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("minimax_mcp")

# Constants
API_HOST = os.environ.get("MINIMAX_API_HOST", "https://api.minimax.io")
API_KEY = os.environ.get("MINIMAX_API_KEY", "")

# Validate API key on startup
if not API_KEY:
    # Try to load from config file
    config_path = os.path.expanduser("~/.openclaw/config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                API_KEY = config.get("apiKey", "")
        except Exception:
            pass


# Enums
class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"


class AspectRatio(str, Enum):
    """Image aspect ratios for generation."""
    RATIO_1_1 = "1:1"
    RATIO_16_9 = "16:9"
    RATIO_4_3 = "4:3"
    RATIO_3_2 = "3:2"
    RATIO_2_3 = "2:3"
    RATIO_3_4 = "3:4"
    RATIO_9_16 = "9:16"
    RATIO_21_9 = "21:9"


class VoiceId(str, Enum):
    """Available TTS voice IDs."""
    ENGLISH_EXPRESSIVE_NARRATOR = "English_expressive_narrator"
    MALE_NARRATOR = "Male_Narrator"
    FEMALE_NARRATOR = "Female_Narrator"
    ENGLISH_EXPRESSIVE_CLON = "english_expressive_c=clon"
    ENGLISH_EXPRESSIVE_N_CLON = "english_expressive_n=clon"
    MALE_NARRATION_N_CLON = "male_narration_n=clon"


# Pydantic Models for Input Validation
class WebSearchInput(BaseModel):
    """Input model for web search."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    query: str = Field(
        ...,
        description="Search query (3-5 keywords recommended for best results)",
        min_length=1,
        max_length=500
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable"
    )

    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class UnderstandImageInput(BaseModel):
    """Input model for image understanding."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    prompt: str = Field(
        ...,
        description="Question or instruction about the image (e.g., 'What is in this image?', 'Describe the contents')",
        min_length=1,
        max_length=2000
    )
    image_source: str = Field(
        ...,
        description="URL or local file path to the image. Supports PNG, JPEG, WebP formats."
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable"
    )

    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()

    @field_validator('image_source')
    @classmethod
    def validate_image_source(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Image source cannot be empty")
        return v.strip()


class TextToSpeechInput(BaseModel):
    """Input model for text-to-speech generation."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    text: str = Field(
        ...,
        description="Text to convert to speech",
        min_length=1,
        max_length=5000
    )
    voice_id: VoiceId = Field(
        default=VoiceId.ENGLISH_EXPRESSIVE_NARRATOR,
        description="Voice ID for the speech generation"
    )
    speed: float = Field(
        default=1.0,
        description="Speech speed, ranging from 0.5 to 2.0",
        ge=0.5,
        le=2.0
    )

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Text cannot be empty")
        return v.strip()


class ImageGenerationInput(BaseModel):
    """Input model for image generation."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    prompt: str = Field(
        ...,
        description="Image description/prompt (max 1500 characters). Be detailed and specific for best results.",
        min_length=1,
        max_length=1500
    )
    aspect_ratio: AspectRatio = Field(
        default=AspectRatio.RATIO_1_1,
        description="Image aspect ratio"
    )
    n: int = Field(
        default=1,
        description="Number of images to generate (1-9)",
        ge=1,
        le=9
    )

    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()


# Shared utility functions
def _get_api_key() -> str:
    """Get the API key, raising an error if not available."""
    if not API_KEY:
        raise ValueError(
            "MINIMAX_API_KEY is not set. Please set it in your environment "
            "or in ~/.openclaw/config.json"
        )
    return API_KEY


def _handle_api_error(e: Exception, operation: str) -> str:
    """Consistent error formatting across all tools."""
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        if status == 401:
            return f"Error: Invalid API authentication. Please check your MINIMAX_API_KEY."
        elif status == 403:
            return f"Error: Permission denied. You don't have access to this resource."
        elif status == 429:
            return f"Error: Rate limit exceeded. Please wait before making more requests."
        elif status == 400:
            try:
                resp = e.response.json()
                msg = resp.get("base_resp", {}).get("status_msg", "Bad request")
                return f"Error: {msg}"
            except Exception:
                pass
            return f"Error: Bad request (400)"
        return f"Error: API request failed with status {status}"
    elif isinstance(e, httpx.TimeoutException):
        return f"Error: Request timed out. Please try again."
    elif isinstance(e, ValueError):
        return f"Error: {str(e)}"
    return f"Error: {operation} failed: {type(e).__name__}"


async def _make_api_request(
    endpoint: str,
    method: str = "POST",
    json_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Reusable function for all API calls."""
    api_key = _get_api_key()
    url = f"{API_HOST}{endpoint}"

    async with httpx.AsyncClient(timeout=60.0) as client:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        response = await client.request(
            method,
            url,
            headers=headers,
            json=json_data
        )
        response.raise_for_status()
        return response.json()


# Tool definitions
@mcp.tool(
    name="minimax_web_search",
    annotations={
        "title": "Search the Web",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def minimax_web_search(params: WebSearchInput) -> str:
    """Search the web using MiniMax's search API.

    This tool performs a web search and returns relevant results including
    titles, snippets, and links. Best for general knowledge queries,
    news, and informational searches.

    Args:
        params (WebSearchInput): Validated input parameters containing:
            - query (str): Search query (3-5 keywords recommended)
            - response_format (ResponseFormat): Output format (markdown or json)

    Returns:
        str: Search results in the requested format.

    Examples:
        - Use when: "Search for recent AI news" -> query="AI news 2024"
        - Use when: "Find information about Python" -> query="Python programming language"
        - Don't use when: You need to analyze an image (use minimax_understand_image)
        - Don't use when: You want to generate an image (use minimax_generate_image)
    """
    try:
        # Build JSON-RPC request to MiniMax MCP server via stdio
        # Since MiniMax's search is exposed through their MCP server,
        # we use JSON-RPC over stdio to call it
        import asyncio
        import subprocess
        import sys

        query_json = json.dumps(params.query)
        rpc_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "web_search",
                "arguments": {"query": params.query}
            },
            "id": 1
        }

        initialize_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "minimax_mcp", "version": "1.0"}
            },
            "id": 0
        }

        # Run the MiniMax MCP server and communicate via JSON-RPC
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "uvx", "minimax-coding-plan-mcp",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Send initialize
        init_data = json.dumps(initialize_request) + "\n"
        await process.stdin.write(init_data.encode())
        await process.stdin.drain()
        await asyncio.sleep(1)

        # Send search request
        req_data = json.dumps(rpc_request) + "\n"
        await process.stdin.write(req_data.encode())
        await process.stdin.drain()
        await asyncio.sleep(4)

        # Read response
        try:
            stdout_data, stderr_data = await asyncio.wait_for(
                process.communicate(),
                timeout=2.0
            )
        except asyncio.TimeoutError:
            process.kill()
            stdout_data, _ = await process.communicate()

        output = stdout_data.decode()

        # Parse JSON-RPC responses
        results_text = ""
        for line in output.strip().split("\n"):
            if not line.strip():
                continue
            try:
                resp = json.loads(line)
                if "result" in resp and "content" in resp["result"]:
                    for item in resp["result"]["content"]:
                        if item.get("type") == "text":
                            results_text = item["text"]
                            break
            except json.JSONDecodeError:
                continue

        if not results_text:
            # Fallback: try to parse raw output
            for line in output.strip().split("\n"):
                try:
                    resp = json.loads(line)
                    if "result" in resp:
                        content = resp.get("result", {}).get("content", [])
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "text":
                                results_text = item["text"]
                                break
                except (json.JSONDecodeError, AttributeError):
                    continue

        if params.response_format == ResponseFormat.JSON:
            try:
                parsed = json.loads(results_text)
                return json.dumps(parsed, indent=2)
            except json.JSONDecodeError:
                return json.dumps({"raw_output": results_text, "query": params.query}, indent=2)
        else:
            # Format as markdown
            try:
                parsed = json.loads(results_text)
                if "organic" in parsed:
                    lines = [f"# Web Search Results: '{params.query}'", ""]
                    for i, r in enumerate(parsed.get("organic", [])[:10], 1):
                        lines.append(f"**{i}. {r.get('title', 'N/A')}**")
                        if r.get("snippet"):
                            lines.append(f"   {r['snippet']}")
                        if r.get("link"):
                            lines.append(f"   [Link]({r['link']})")
                        lines.append("")
                    return "\n".join(lines)
            except json.JSONDecodeError:
                pass

            if results_text:
                return results_text
            return f"No search results found for '{params.query}'"

    except Exception as e:
        return _handle_api_error(e, "Web search")


@mcp.tool(
    name="minimax_understand_image",
    annotations={
        "title": "Analyze Image",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def minimax_understand_image(params: UnderstandImageInput) -> str:
    """Analyze images using MiniMax's vision model.

    This tool examines an image and provides a detailed description or
    answers questions about it. Supports both image URLs and local files.

    Args:
        params (UnderstandImageInput): Validated input parameters containing:
            - prompt (str): Question or instruction about the image
            - image_source (str): URL or local file path to the image
            - response_format (ResponseFormat): Output format (markdown or json)

    Returns:
        str: Analysis results in the requested format.

    Examples:
        - Use when: "What's in this image?" with image_source="https://example.com/photo.png"
        - Use when: "Describe this image" with image_source="/path/to/local/image.jpg"
        - Use when: "Read the text in this image" with image_source="screenshot.png"
        - Don't use when: You want to generate an image (use minimax_generate_image)
    """
    try:
        import asyncio
        import subprocess
        import sys

        prompt_json = json.dumps(params.prompt)
        image_json = json.dumps(params.image_source)

        rpc_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "understand_image",
                "arguments": {"prompt": params.prompt, "image_source": params.image_source}
            },
            "id": 1
        }

        initialize_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "minimax_mcp", "version": "1.0"}
            },
            "id": 0
        }

        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "uvx", "minimax-coding-plan-mcp",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        init_data = json.dumps(initialize_request) + "\n"
        await process.stdin.write(init_data.encode())
        await process.stdin.drain()
        await asyncio.sleep(1)

        req_data = json.dumps(rpc_request) + "\n"
        await process.stdin.write(req_data.encode())
        await process.stdin.drain()
        await asyncio.sleep(5)

        try:
            stdout_data, stderr_data = await asyncio.wait_for(
                process.communicate(),
                timeout=2.0
            )
        except asyncio.TimeoutError:
            process.kill()
            stdout_data, _ = await process.communicate()

        output = stdout_data.decode()

        analysis_text = ""
        for line in output.strip().split("\n"):
            if not line.strip():
                continue
            try:
                resp = json.loads(line)
                if "result" in resp and "content" in resp["result"]:
                    for item in resp["result"]["content"]:
                        if item.get("type") == "text":
                            analysis_text = item["text"]
                            break
            except json.JSONDecodeError:
                continue

        if params.response_format == ResponseFormat.JSON:
            return json.dumps({"analysis": analysis_text, "prompt": params.prompt}, indent=2)
        else:
            if analysis_text:
                return f"# Image Analysis\n\n**Prompt:** {params.prompt}\n\n**Analysis:**\n{analysis_text}"
            return "No analysis could be generated for this image."

    except Exception as e:
        return _handle_api_error(e, "Image understanding")


@mcp.tool(
    name="minimax_text_to_speech",
    annotations={
        "title": "Generate Speech from Text",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def minimax_text_to_speech(params: TextToSpeechInput) -> str:
    """Generate speech audio from text using MiniMax's TTS API.

    This tool converts text into natural-sounding speech audio. Useful for
    creating voiceovers, accessibility features, or audio content.

    Args:
        params (TextToSpeechInput): Validated input parameters containing:
            - text (str): Text to convert to speech (max 5000 chars)
            - voice_id (VoiceId): Voice selection (default: English_expressive_narrator)
            - speed (float): Speech speed from 0.5 to 2.0 (default: 1.0)

    Returns:
        str: Path to the generated MP3 audio file.

    Examples:
        - Use when: "Create a voiceover saying 'Hello world'"
        - Use when: "Generate audio for this announcement" with text and custom voice
        - Don't use when: You need to search the web (use minimax_web_search)
        - Don't use when: You want to analyze or generate images
    """
    try:
        api_key = _get_api_key()
        url = f"{API_HOST}/v1/t2a_v2"

        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "speech-2.8-hd",
                "text": params.text,
                "stream": False,
                "output_format": "hex",
                "voice_setting": {
                    "voice_id": params.voice_id.value,
                    "speed": params.speed,
                    "vol": 1,
                    "pitch": 0
                },
                "audio_setting": {
                    "sample_rate": 32000,
                    "bitrate": 128000,
                    "format": "mp3",
                    "channel": 1
                }
            }

            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # Check for API-level errors
            if "base_resp" in data:
                status = data["base_resp"].get("status_code", 0)
                if status != 0:
                    msg = data["base_resp"].get("status_msg", "Unknown error")
                    return f"Error: API returned status {status} - {msg}"

            # Extract hex audio
            hex_audio = data.get("data", {}).get("audio", "")
            if not hex_audio:
                return "Error: No audio data in response"

            # Convert hex to binary and save
            audio_bytes = bytes.fromhex(hex_audio)

            temp_dir = tempfile.mkdtemp(prefix="minimax_tts_")
            output_file = os.path.join(temp_dir, f"tts_{int(time.time())}.mp3")

            with open(output_file, "wb") as f:
                f.write(audio_bytes)

            return f"Audio generated successfully:\n- File: {output_file}\n- Voice: {params.voice_id.value}\n- Speed: {params.speed}x\n- Duration: {len(audio_bytes)} bytes"

    except Exception as e:
        return _handle_api_error(e, "Text-to-speech")


@mcp.tool(
    name="minimax_generate_image",
    annotations={
        "title": "Generate Image from Text",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def minimax_generate_image(params: ImageGenerationInput) -> str:
    """Generate images from text descriptions using MiniMax's image generation model.

    This tool creates images based on textual prompts. Be descriptive and
    specific for best results. Generated images are returned as URLs that
    expire after 24 hours.

    Args:
        params (ImageGenerationInput): Validated input parameters containing:
            - prompt (str): Image description (max 1500 chars)
            - aspect_ratio (AspectRatio): Image dimensions (default: 1:1)
            - n (int): Number of images to generate (1-9)

    Returns:
        str: Generated image URL(s) in the requested format.

    Examples:
        - Use when: "Generate an image of a sunset over mountains"
        - Use when: "Create a portrait photo" with aspect_ratio="2:3"
        - Use when: "Make an abstract artwork" with n=4 for multiple variations
        - Don't use when: You need to analyze an existing image (use minimax_understand_image)
    """
    try:
        data = await _make_api_request(
            "/v1/image_generation",
            json_data={
                "model": "image-01",
                "prompt": params.prompt,
                "aspect_ratio": params.aspect_ratio.value,
                "response_format": "url",
                "n": params.n
            }
        )

        images = data.get("data", [])
        if not images:
            return "Error: No images were generated"

        # Extract URLs
        urls = []
        for img in images:
            if isinstance(img, dict):
                url = img.get("url", "")
            else:
                url = img
            if url:
                urls.append(url)

        if params.response_format == ResponseFormat.JSON:
            return json.dumps({
                "prompt": params.prompt,
                "aspect_ratio": params.aspect_ratio.value,
                "images": [{"url": u} for u in urls]
            }, indent=2)
        else:
            lines = [f"# Generated Image(s)", ""]
            lines.append(f"**Prompt:** {params.prompt}")
            lines.append(f"**Aspect Ratio:** {params.aspect_ratio.value}")
            lines.append(f"**Count:** {len(urls)}")
            lines.append("")
            lines.append("## Image URLs (expire in 24 hours)")
            lines.append("")
            for i, url in enumerate(urls, 1):
                lines.append(f"{i}. {url}")
            lines.append("")
            lines.append("---")
            lines.append("*Note: URLs expire after 24 hours. Download images if you need to preserve them.*")
            return "\n".join(lines)

    except Exception as e:
        return _handle_api_error(e, "Image generation")


if __name__ == "__main__":
    mcp.run()
