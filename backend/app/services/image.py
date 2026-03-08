import os
from pathlib import Path
from typing import Dict, List
import google.generativeai as genai
from PIL import Image

from app.config import get_settings, LLMProvider

class ImageProcessingError(Exception):
    """Custom exception for image processing failures."""
    pass

def analyze_frames_with_gemini(frames_dir: Path) -> Dict[str, str]:
    """
    Analyzes all images in a directory using Gemini Vision to generate captions/descriptions.
    
    Args:
        frames_dir: The directory containing the extracted JPEG frames.
        
    Returns:
        A dictionary mapping frame filename (e.g., 'frame_0001_30s.jpg') to its description.
    """
    settings = get_settings()
    
    if settings.LLM_PROVIDER != LLMProvider.GEMINI:
        raise ImageProcessingError("Gemini Vision requires LLM_PROVIDER to be 'gemini'.")
        
    print(f"[ImageService] Analyzing frames in {frames_dir} using Gemini Vision...")
    
    try:
        # Configure the Gemini Client (Standard SDK)
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        # Use a model appropriate for vision
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        descriptions: Dict[str, str] = {}
        frame_files = sorted(list(frames_dir.glob("*.jpg")))
        
        for frame_path in frame_files:
            print(f"[ImageService] Analyzing {frame_path.name}...")
            
            # Open the image using PIL
            img = Image.open(frame_path)
            
            # The prompt to guide the vision model
            prompt = (
                "Analyze this image in detail. "
                "1. Describe the visual content (charts, people, text). "
                "2. If there are any figure numbers (e.g., 'Figure 1', 'Fig. 3') or table numbers (e.g., 'Table 2'), "
                "explicitly list them at the start of your response in brackets, like [Figure 1] or [Table 2]. "
                "Then provide the description."
            )
            
            # Call the multimodal Gemini model
            response = model.generate_content([prompt, img])
            
            descriptions[frame_path.name] = response.text.strip()
            
        print(f"[ImageService] Successfully generated {len(descriptions)} frame descriptions.")
        return descriptions

    except Exception as e:
        print(f"[ImageService] FATAL: Gemini Vision analysis failed: {e}")
        raise ImageProcessingError(f"Gemini Vision failed: {e}")