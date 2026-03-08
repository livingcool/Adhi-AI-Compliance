import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pypdf
from pdf2image import convert_from_path
from pdf2image.exceptions import PDFInfoNotInstalledError
from app.config import get_settings

def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extracts raw text from a PDF file using pypdf.
    """
    text = ""
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"[PDF Processor] Error extracting text from {pdf_path}: {e}")
    return text

def convert_pdf_to_images(pdf_path: Path, output_dir: Path) -> List[str]:
    """
    Converts each page of a PDF into an image file.
    Returns a list of paths to the generated images.
    """
    image_paths = []
    try:
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert PDF to images
        # Poppler is required for this.
        images = convert_from_path(str(pdf_path))
        
        for i, image in enumerate(images):
            image_filename = f"page_{i+1}.jpg"
            image_path = output_dir / image_filename
            image.save(image_path, "JPEG")
            image_paths.append(str(image_path))
            
    except PDFInfoNotInstalledError:
        print("[PDF Processor] CRITICAL: Poppler is not installed or not in PATH.")
        raise Exception(
            "Poppler is required for PDF image conversion but was not found.\n"
            "Please install Poppler and add it to your PATH.\n"
            "1. Download the latest binary from: https://github.com/oschwartz10612/poppler-windows/releases/\n"
            "2. Extract the zip file.\n"
            "3. Add the 'bin' folder (e.g., C:\\poppler\\bin) to your System PATH environment variable.\n"
            "4. Restart your terminal/IDE."
        )
    except Exception as e:
        print(f"[PDF Processor] Error converting PDF to images: {e}")
        raise # Re-raise other errors to ensure we don't silently fail
        
    return image_paths

def process_pdf(pdf_path: Path, source_id: str) -> Dict[str, Any]:
    """
    Main entry point for PDF processing.
    Extracts text and converts pages to images for vision analysis.
    """
    settings = get_settings()
    
    # 1. Extract Text
    raw_text = extract_text_from_pdf(pdf_path)
    
    # 2. Convert to Images (for visual context/tables/charts)
    images_dir = settings.FRAME_DIR / source_id / "pages"
    image_paths = []
    
    try:
        image_paths = convert_pdf_to_images(pdf_path, images_dir)
    except Exception as e:
        print(f"[PDF Processor] Image conversion failed: {e}")
        # If text is also empty, this is a fatal error for this document
        if not raw_text.strip():
            raise Exception(f"Failed to extract both text and images from PDF. Error: {e}")
    
    # Final check
    if not raw_text.strip() and not image_paths:
        raise Exception("PDF processing yielded no text and no images. The file might be corrupted or empty.")

    # Create page-to-image mapping
    page_images = {}
    for i, img_path in enumerate(image_paths, 1):
        page_images[i] = img_path

    return {
        "text": raw_text,
        "images_dir": str(images_dir),
        "image_paths": image_paths,
        "page_images": page_images,
        "page_count": len(image_paths)
    }
