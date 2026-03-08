import uuid
import json
import traceback
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import (
    APIRouter, 
    Depends, 
    UploadFile, 
    File, 
    Form, 
    HTTPException, 
    status,
    Request,
    BackgroundTasks
)
from app.config import Settings, get_settings
from app.api.schemas import IngestResponse, TaskStatus, TaskStatusResponse, IngestType
from app.services.ingestion_orchestrator import (
    process_audio_source, 
    process_image_source, 
    process_pdf_source
)

# --- In-Memory Task Store (Simulating Celery Backend for HF Spaces) ---
# Format: { task_id: { 'status': ..., 'details': ..., 'progress': ..., 'artifacts': ..., 'error': ... } }
TASK_STORE: Dict[str, Dict[str, Any]] = {}

router = APIRouter()

# --- Mock Task Object for Orchestrator Compatibility ---
class MockCeleryTask:
    def __init__(self, task_id: str):
        self.request = type('obj', (object,), {'id': task_id, 'retries': 0})
        self.task_id = task_id
    
    def update_state(self, state, meta):
        """Simulates Celery's update_state by writing to global store."""
        # Update the global store
        if self.task_id in TASK_STORE:
            TASK_STORE[self.task_id].update({
                'status': state,
                'details': meta.get('details', ''),
                'progress_percent': meta.get('progress_percent', 0.0),
                'artifacts': meta.get('artifacts', {}),
                'error': meta.get('errors', None)
            })

# --- Background Worker Functions ---
def background_ingest_wrapper(
    task_id: str, 
    ingest_type: IngestType, 
    file_path: Path, 
    source_id: str, 
    metadata: dict, 
    organization_id: str
):
    """
    Wrapper to run ingestion logic in FastAPI BackgroundTasks.
    """
    print(f"[BackgroundWorker] Starting task {task_id} for {ingest_type.value}")
    
    # Initialize task in store
    TASK_STORE[task_id] = {
        'status': TaskStatus.PROCESSING.value,
        'details': "Starting ingestion pipeline...",
        'progress_percent': 5.0,
        'artifacts': {}
    }
    
    mock_task = MockCeleryTask(task_id)
    file_path_obj = Path(file_path)
    file_name = file_path_obj.name
    
    try:
        if ingest_type == IngestType.PDF or ingest_type == IngestType.TEXT:
            process_pdf_source(
                task_self=mock_task,
                source_id=source_id,
                original_file_path=file_path_obj,
                file_name=file_name,
                doc_type=IngestType.PDF,
                organization_id=organization_id
            )
        elif ingest_type == IngestType.IMAGE:
             process_image_source(
                task_self=mock_task,
                source_id=source_id,
                original_file_path=file_path_obj,
                file_name=file_name,
                doc_type=IngestType.IMAGE,
                organization_id=organization_id
            )
        elif ingest_type == IngestType.AUDIO:
             process_audio_source(
                task_self=mock_task,
                source_id=source_id,
                original_file_path=file_path_obj,
                file_name=file_name,
                doc_type=IngestType.AUDIO,
                language=metadata.get("language", "en-US"),
                organization_id=organization_id
            )
        elif ingest_type == IngestType.VIDEO:
             process_audio_source(
                task_self=mock_task,
                source_id=source_id,
                original_file_path=file_path_obj,
                file_name=file_name,
                doc_type=IngestType.VIDEO,
                language=metadata.get("language", "en-US"),
                organization_id=organization_id
            )
        else:
             raise ValueError(f"Unsupported ingest type: {ingest_type}")

        # Final Success State (if not set by orchestrator)
        if TASK_STORE[task_id]['status'] != TaskStatus.SUCCESS.value:
             TASK_STORE[task_id]['status'] = TaskStatus.SUCCESS.value
             TASK_STORE[task_id]['progress_percent'] = 100.0
             TASK_STORE[task_id]['details'] = "Processing complete."

    except Exception as e:
        print(f"[BackgroundWorker] Task {task_id} FAILED: {e}")
        traceback.print_exc()
        TASK_STORE[task_id]['status'] = TaskStatus.FAILURE.value
        TASK_STORE[task_id]['error'] = str(e)
        TASK_STORE[task_id]['details'] = f"Failed: {str(e)}"


@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_media(
    request: Request,
    background_tasks: BackgroundTasks,
    type: IngestType = Form(..., description="The type of media being uploaded"),
    file: UploadFile = File(..., description="The media file to process"),
    source_id: str = Form(None, description="Optional unique ID"),
    organization_id: str = Form("default_org", description="Organization ID"),
    metadata: str = Form("{}", description="JSON metadata"),
    settings: Settings = Depends(get_settings)
):
    """
    Accepts a media file and queues it for background processing (Serverless/HF friendly).
    """
    
    # 1. Setup ID
    if not source_id:
        source_id = str(uuid.uuid4())
    
    task_id = str(uuid.uuid4())
    
    # 2. Save File
    upload_dir = settings.UPLOAD_DIR
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    source_id_base = Path(source_id).stem
    file_extension = Path(file.filename).suffix
    saved_file_path = upload_dir / f"{source_id_base}{file_extension}"
    
    try:
        max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        file_size = 0
        with open(saved_file_path, "wb") as buffer:
            while True:
                chunk = await file.read(settings.UPLOAD_CHUNK_SIZE_BYTES)
                if not chunk: break
                file_size += len(chunk)
                if file_size > max_size_bytes:
                    saved_file_path.unlink(missing_ok=True)
                    raise HTTPException(status_code=413, detail="File too large")
                buffer.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")

    # 3. Parse Metadata
    try:
        metadata_dict = json.loads(metadata)
    except:
        metadata_dict = {}

    # 4. Initialize Task State
    TASK_STORE[task_id] = {
        'status': TaskStatus.PENDING.value,
        'details': "Queued for processing...",
        'progress_percent': 0.0
    }

    # 5. Dispatch Background Task
    background_tasks.add_task(
        background_ingest_wrapper,
        task_id,
        type,
        saved_file_path,
        source_id_base,
        metadata_dict,
        organization_id
    )

    # 6. Response
    status_url = request.url_for("get_task_status", task_id=task_id)
    return IngestResponse(task_id=task_id, status_url=str(status_url))


@router.get("/status/{task_id}", response_model=TaskStatusResponse, name="get_task_status")
def get_task_status(task_id: str):
    """
    Retrieves status from local memory store (shim for Celery).
    """
    task_data = TASK_STORE.get(task_id)
    
    if not task_data:
        # If not in memory, check if it was a real Celery task (legacy compatibility)
        # or just return Unknown
        return TaskStatusResponse(
            task_id=task_id,
            status=TaskStatus.UNKNOWN,
            details="Task not found in memory (node restart?)",
            progress_percent=0.0
        )
            
    return TaskStatusResponse(
        task_id=task_id,
        status=TaskStatus(task_data['status']),
        details=task_data['details'],
        progress_percent=task_data['progress_percent'],
        artifacts=task_data.get('artifacts'),
        error=task_data.get('error')
    )