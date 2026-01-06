"""
Image upload router for Cloudinary hosting.
Used to upload logos/brand images that need public URLs for image generation prompts.
"""

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, UploadFile, HTTPException, Depends
from pydantic import BaseModel

from ..config import get_settings, Settings


router = APIRouter(prefix="/uploads", tags=["uploads"])


class ImageUploadResponse(BaseModel):
    url: str


@router.post("/image", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile,
    settings: Settings = Depends(get_settings),
) -> ImageUploadResponse:
    """
    Upload an image to Cloudinary and return its public URL.

    Used for logo uploads that need to be included in image generation prompts
    (e.g., Midjourney supports image URLs as part of prompts).
    """
    if not settings.cloudinary_url:
        raise HTTPException(
            status_code=503,
            detail="Image upload service not configured. Please set CLOUDINARY_URL."
        )

    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed"
        )

    # Configure Cloudinary from URL
    cloudinary.config(cloudinary_url=settings.cloudinary_url)

    try:
        contents = await file.read()

        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            contents,
            folder="clarynt-logos",
            resource_type="image",
            # Use original filename without extension as public_id
            public_id=file.filename.rsplit(".", 1)[0] if file.filename else None,
            # Overwrite if same name uploaded again
            overwrite=True,
        )

        return ImageUploadResponse(url=result["secure_url"])

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image: {str(e)}"
        )
