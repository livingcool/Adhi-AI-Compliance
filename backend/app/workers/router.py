from pathlib import Path
from app.workers.tasks import ingest_video, ingest_audio, ingest_image 

# --- Define Constants (Crucial for structural integrity) ---

VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.webm']
AUDIO_EXTENSIONS = ['.mp3', '.wav', '.flac', '.m4a']
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']

# --- The Routing Function ---

def route_ingestion_task(file_path: str, source_id: str, language: str = 'en'):
    """
    Routes the file to the correct worker task based on extension.
    Requires source_id and correctly packages language into metadata.
    """
    
    file_path_obj = Path(file_path)
    extension = file_path_obj.suffix.lower()
    
    # Required Celery task arguments
    metadata = {"language": language}
    
    # 1. Video Extensions (Priority)
    if extension in VIDEO_EXTENSIONS:
        print(f"[Router] Routing {file_path_obj.name} to ingest_video task.")
        return ingest_video.delay(file_path, source_id, metadata)
    
    # 2. Audio Extensions
    elif extension in AUDIO_EXTENSIONS:
        print(f"[Router] Routing {file_path_obj.name} to ingest_audio task.")
        return ingest_audio.delay(file_path, source_id, metadata)
    
    # 3. Image/Other
    elif extension in IMAGE_EXTENSIONS:
        print(f"[Router] Routing {file_path_obj.name} to ingest_image task.")
        # Image task currently doesn't use 'language', but we pass an empty dict for API consistency
        return ingest_image.delay(file_path, source_id, metadata={}) 
        
    else:
        raise ValueError(f"Unsupported file type for ingestion: {extension}. File: {file_path_obj.name}")