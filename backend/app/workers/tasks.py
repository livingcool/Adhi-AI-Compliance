from pathlib import Path
from app.workers.celery_app import celery_app
from app.api.schemas import TaskStatus, IngestType
from app.services.ingestion_orchestrator import (
    process_audio_source, 
    process_image_source,
    process_pdf_source
)
from celery.exceptions import MaxRetriesExceededError, Retry

# --- Helper Function for State Update ---

def update_task_state(task, status: TaskStatus, details: str, progress: float = 0.0):
    """Helper function to update Celery task state and metadata."""
    meta = {
        'status': status.value,
        'details': details,
        'progress_percent': progress,
    }
    task.update_state(state=status.value, meta=meta)

# --- The Main Ingestion Tasks ---

@celery_app.task(bind=True, name="app.workers.tasks.ingest_video")
def ingest_video(self, file_path: str, source_id: str, metadata: dict, organization_id: str = "default_org"):
    """Celery task to process a video file."""
    task_id = self.request.id
    print(f"[TASK {task_id}] Received video: {file_path}")
    
    try:
        update_task_state(self, TaskStatus.PROCESSING, "Starting video ingestion pipeline...", 5.0)
        
        language_code = metadata.get("language", "ta-IN")
        original_file_path = Path(file_path)
        file_name = original_file_path.name

        artifacts = process_audio_source(
            task_self=self,
            source_id=source_id,
            original_file_path=original_file_path,
            file_name=file_name,
            doc_type=IngestType.VIDEO,
            language=language_code,
            organization_id=organization_id
        )
        
        meta = {
            'status': TaskStatus.SUCCESS.value,
            'details': "Video processed and indexed successfully (Multimodal).",
            'progress_percent': 100.0,
            'artifacts': artifacts
        }
        self.update_state(state=TaskStatus.SUCCESS.value, meta=meta)
        return meta

    except Exception as e:
        print(f"[TASK {task_id}] FAILED: {e}")
        meta = {
            'status': TaskStatus.FAILURE.value,
            'details': f"Failed to process video: {str(e)}",
            'progress_percent': 0.0,
            'errors': str(e)
        }
        self.update_state(state=TaskStatus.FAILURE.value, meta=meta)
        raise

@celery_app.task(bind=True, name="app.workers.tasks.ingest_audio")
def ingest_audio(self, file_path: str, source_id: str, metadata: dict, organization_id: str = "default_org"):
    """Celery task to process an audio file."""
    task_id = self.request.id
    print(f"[TASK {task_id}] Received audio: {file_path}")
    
    try:
        update_task_state(self, TaskStatus.PROCESSING, "Starting audio ingestion pipeline...", 5.0)
        
        language_code = metadata.get("language", "ta-IN")
        original_file_path = Path(file_path)
        file_name = original_file_path.name

        artifacts = process_audio_source(
            task_self=self,
            source_id=source_id,
            original_file_path=original_file_path,
            file_name=file_name,
            doc_type=IngestType.AUDIO,
            language=language_code,
            organization_id=organization_id
        )
        
        meta = {
            'status': TaskStatus.SUCCESS.value,
            'details': "Audio processed and indexed successfully.",
            'progress_percent': 100.0,
            'artifacts': artifacts
        }
        self.update_state(state=TaskStatus.SUCCESS.value, meta=meta)
        return meta

    except Exception as e:
        print(f"[TASK {task_id}] FAILED: {e}")
        meta = {
            'status': TaskStatus.FAILURE.value,
            'details': f"Failed to process audio: {str(e)}",
            'progress_percent': 0.0, 
            'errors': str(e)
        }
        self.update_state(state=TaskStatus.FAILURE.value, meta=meta)
        raise


@celery_app.task(bind=True, max_retries=5, name="app.workers.tasks.ingest_image")
def ingest_image(self, file_path: str, source_id: str, metadata: dict, organization_id: str = "default_org"):
    """Celery task to process an image file with retry logic."""
    task_id = self.request.id
    print(f"[TASK {task_id}] Received image: {file_path}")
    
    try:
        update_task_state(self, TaskStatus.PROCESSING, "Starting image pipeline...", 5.0)
        
        original_file_path = Path(file_path)
        file_name = original_file_path.name

        artifacts = process_image_source(
            task_self=self,
            source_id=source_id,
            original_file_path=original_file_path,
            file_name=file_name,
            doc_type=IngestType.IMAGE,
            organization_id=organization_id
        )
        
        meta = {
            'status': TaskStatus.SUCCESS.value,
            'details': "Image processed successfully (placeholder).",
            'progress_percent': 100.0,
            'artifacts': artifacts
        }
        self.update_state(state=TaskStatus.SUCCESS.value, meta=meta)
        return meta

    except Exception as e:
        print(f"[TASK {task_id}] FAILED: {e} | Current attempt: {self.request.retries + 1}")
        meta = {
            'status': TaskStatus.FAILURE.value,
            'details': f"Failed to process image: {str(e)}",
            'progress_percent': 0.0,
            'errors': str(e)
        }

        try:
            self.retry(countdown=2 ** self.request.retries)
        except MaxRetriesExceededError:
            print(f"[TASK {task_id}] Max retries exceeded for image task.")
            self.update_state(state=TaskStatus.FAILURE.value, meta=meta)
            raise 
        except Retry:
            raise

@celery_app.task(bind=True, name="app.workers.tasks.ingest_pdf")
def ingest_pdf(self, file_path: str, source_id: str, metadata: dict, organization_id: str = "default_org"):
    """Celery task to process a PDF file."""
    task_id = self.request.id
    print(f"[TASK {task_id}] Received PDF: {file_path}")
    
    try:
        update_task_state(self, TaskStatus.PROCESSING, "Starting PDF ingestion pipeline...", 5.0)
        
        original_file_path = Path(file_path)
        file_name = original_file_path.name

        artifacts = process_pdf_source(
            task_self=self,
            source_id=source_id,
            original_file_path=original_file_path,
            file_name=file_name,
            doc_type=IngestType.PDF,
            organization_id=organization_id
        )
        
        meta = {
            'status': TaskStatus.SUCCESS.value,
            'details': "PDF processed and indexed successfully (Text + Visual).",
            'progress_percent': 100.0,
            'artifacts': artifacts
        }
        self.update_state(state=TaskStatus.SUCCESS.value, meta=meta)
        return meta

    except Exception as e:
        print(f"[TASK {task_id}] FAILED: {e}")
        meta = {
            'status': TaskStatus.FAILURE.value,
            'details': f"Failed to process PDF: {str(e)}",
            'progress_percent': 0.0,
            'errors': str(e)
        }
        self.update_state(state=TaskStatus.FAILURE.value, meta=meta)
        raise