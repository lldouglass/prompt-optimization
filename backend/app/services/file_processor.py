"""File processing service for extracting content from uploaded files."""

import base64
import io
import mimetypes
import os
from typing import Literal
from dataclasses import dataclass

from pypdf import PdfReader
from docx import Document
from PIL import Image
import openai


@dataclass
class FileContent:
    """Extracted content from a file."""
    text: str
    file_type: str
    file_name: str
    original_size_bytes: int
    extraction_method: Literal["text", "pdf", "docx", "vision", "code"]


class FileProcessingError(Exception):
    """Error during file processing."""
    pass


SUPPORTED_TEXT_TYPES = {
    "text/plain": "text",
    "text/markdown": "text",
    "text/csv": "text",
    "application/json": "text",
    "text/x-python": "code",
    "application/x-python": "code",
    "text/javascript": "code",
    "application/javascript": "code",
    "text/typescript": "code",
    "text/x-java": "code",
    "text/x-c": "code",
    "text/x-c++": "code",
    "text/x-rust": "code",
    "text/x-go": "code",
}

SUPPORTED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/gif", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_TEXT_LENGTH = 10000  # Truncate text content


async def process_file(
    file_data: str,  # base64 encoded
    file_name: str,
    mime_type: str | None = None,
    analysis_type: str = "general",  # "general" or "brand" for logo analysis
) -> FileContent:
    """
    Process an uploaded file and extract its content.

    Args:
        file_data: Base64-encoded file content
        file_name: Original filename
        mime_type: MIME type (inferred from filename if not provided)

    Returns:
        FileContent with extracted text/description

    Raises:
        FileProcessingError: If file cannot be processed
    """
    # Decode base64
    try:
        raw_bytes = base64.b64decode(file_data)
    except Exception as e:
        raise FileProcessingError(f"Invalid base64 encoding: {e}")

    # Check size
    if len(raw_bytes) > MAX_FILE_SIZE:
        raise FileProcessingError(f"File exceeds 5MB limit ({len(raw_bytes) / 1024 / 1024:.1f}MB)")

    # Infer MIME type if not provided
    if not mime_type:
        mime_type, _ = mimetypes.guess_type(file_name)
        if not mime_type:
            # Try to infer from extension
            ext = file_name.lower().split(".")[-1] if "." in file_name else ""
            ext_map = {
                "py": "text/x-python",
                "js": "text/javascript",
                "ts": "text/typescript",
                "java": "text/x-java",
                "c": "text/x-c",
                "cpp": "text/x-c++",
                "rs": "text/x-rust",
                "go": "text/x-go",
                "md": "text/markdown",
                "json": "application/json",
                "csv": "text/csv",
                "txt": "text/plain",
            }
            mime_type = ext_map.get(ext)
            if not mime_type:
                raise FileProcessingError(f"Cannot determine file type for: {file_name}")

    # Route to appropriate processor
    if mime_type == "application/pdf":
        return _extract_pdf(raw_bytes, file_name)
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return _extract_docx(raw_bytes, file_name)
    elif mime_type in SUPPORTED_TEXT_TYPES:
        return _extract_text(raw_bytes, file_name, mime_type)
    elif mime_type in SUPPORTED_IMAGE_TYPES:
        return await _analyze_image(raw_bytes, file_name, mime_type, file_data, analysis_type)
    else:
        raise FileProcessingError(f"Unsupported file type: {mime_type}")


def _extract_pdf(data: bytes, file_name: str) -> FileContent:
    """Extract text from PDF."""
    try:
        reader = PdfReader(io.BytesIO(data))
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)

        full_text = "\n\n".join(text_parts)
        if not full_text.strip():
            raise FileProcessingError("PDF contains no extractable text (may be image-based)")

        # Truncate if too long
        if len(full_text) > MAX_TEXT_LENGTH:
            full_text = full_text[:MAX_TEXT_LENGTH] + "\n\n[... content truncated ...]"

        return FileContent(
            text=full_text,
            file_type="pdf",
            file_name=file_name,
            original_size_bytes=len(data),
            extraction_method="pdf"
        )
    except FileProcessingError:
        raise
    except Exception as e:
        raise FileProcessingError(f"Failed to extract PDF text: {e}")


def _extract_docx(data: bytes, file_name: str) -> FileContent:
    """Extract text from Word document."""
    try:
        doc = Document(io.BytesIO(data))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        full_text = "\n\n".join(paragraphs)

        if not full_text.strip():
            raise FileProcessingError("Document contains no text")

        if len(full_text) > MAX_TEXT_LENGTH:
            full_text = full_text[:MAX_TEXT_LENGTH] + "\n\n[... content truncated ...]"

        return FileContent(
            text=full_text,
            file_type="docx",
            file_name=file_name,
            original_size_bytes=len(data),
            extraction_method="docx"
        )
    except FileProcessingError:
        raise
    except Exception as e:
        raise FileProcessingError(f"Failed to extract Word document text: {e}")


def _extract_text(data: bytes, file_name: str, mime_type: str) -> FileContent:
    """Extract content from plain text files."""
    try:
        # Try UTF-8, fall back to latin-1
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("latin-1")

        if len(text) > MAX_TEXT_LENGTH:
            text = text[:MAX_TEXT_LENGTH] + "\n\n[... content truncated ...]"

        extraction_method = SUPPORTED_TEXT_TYPES.get(mime_type, "text")
        file_type = mime_type.split("/")[-1]
        if file_type.startswith("x-"):
            file_type = file_type[2:]

        return FileContent(
            text=text,
            file_type=file_type,
            file_name=file_name,
            original_size_bytes=len(data),
            extraction_method=extraction_method
        )
    except Exception as e:
        raise FileProcessingError(f"Failed to read text file: {e}")


async def _analyze_image(
    data: bytes,
    file_name: str,
    mime_type: str,
    base64_data: str,
    analysis_type: str = "general"
) -> FileContent:
    """Analyze image using GPT-4o-mini Vision API."""
    # Validate it's actually an image
    try:
        img = Image.open(io.BytesIO(data))
        img.verify()
    except Exception:
        raise FileProcessingError("Invalid or corrupted image file")

    # Use OpenAI Vision API to describe the image
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise FileProcessingError("Vision API not configured")

    client = openai.OpenAI(api_key=api_key)

    # Use specialized prompt for brand/logo analysis
    if analysis_type == "brand":
        prompt_text = """Analyze this brand/logo image and extract precise brand style information.

CRITICAL: Be extremely accurate with colors. Look at the ACTUAL colors in the image.

Provide:
1. **Primary Colors** - List each distinct color with its hex code. Look carefully at the actual pixels.
   Format: "Primary: #XXXXXX (color name), Secondary: #XXXXXX (color name)"

2. **Logo Description** - What does the logo depict? (icon, wordmark, abstract shape, etc.)

3. **Typography** - If text is visible, describe the font style (serif, sans-serif, bold, light, etc.)

4. **Visual Style** - Overall aesthetic (modern, classic, playful, corporate, minimalist, etc.)

5. **Recommended Usage** - How should this brand be represented in generated images?

Be precise and factual. Only report colors you can actually see in the image. Do NOT guess or make up colors."""
    else:
        prompt_text = """Analyze this image and provide a detailed description that could be used as context for prompt optimization.

Include:
1. Main subject and composition
2. Style, colors, and mood
3. Technical aspects (lighting, perspective, quality)
4. Any text or UI elements visible
5. Context that would help someone create a similar image or understand its purpose

Be specific and detailed but concise (200-400 words)."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_text
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )

        description = response.choices[0].message.content or "Image analysis unavailable"

        return FileContent(
            text=description,
            file_type=mime_type.split("/")[-1],
            file_name=file_name,
            original_size_bytes=len(data),
            extraction_method="vision"
        )
    except Exception as e:
        raise FileProcessingError(f"Vision API error: {e}")
