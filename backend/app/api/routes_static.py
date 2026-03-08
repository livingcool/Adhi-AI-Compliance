"""
Static file serving routes for images extracted from PDFs and videos.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from app.config import get_settings

router = APIRouter(prefix="/static", tags=["static"])

@router.get("/images/{source_id}/{filename}")
async def serve_image(source_id: str, filename: str):
    """
    Serves image files from the frames directory.
    Used to display PDF page images and video frames in the frontend.
    """
    settings = get_settings()
    
    # Security: Prevent directory traversal
    if ".." in source_id or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid path")
    
    # Try different possible locations
    possible_paths = [
        settings.FRAME_DIR / source_id / "pages" / filename,  # PDF pages
        settings.FRAME_DIR / source_id / "pdf_images" / filename,  # PDF images
        settings.FRAME_DIR / source_id / filename,  # Direct images or video frames
    ]
    
    for image_path in possible_paths:
        if image_path.exists() and image_path.is_file():
            return FileResponse(image_path)
    
    raise HTTPException(status_code=404, detail="Image not found")
