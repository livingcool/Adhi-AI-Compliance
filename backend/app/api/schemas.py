import uuid
from enum import Enum 
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# --- Enums ---

class IngestType(str, Enum):
    """Defines the type of media being ingested."""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    PDF = "pdf"
    
class TaskStatus(str, Enum):
    """Standard states for a Celery task."""
    PENDING = "PENDING"
    RETRY = "RETRY"
    FAILURE = "FAILURE"
    SUCCESS = "SUCCESS"
    STARTED = "STARTED"
    PROCESSING = "processing"
    UNKNOWN = "UNKNOWN"

# --- Schemas for /ingest ---

class IngestResponse(BaseModel):
    """Response model after submitting a file for ingestion."""
    task_id: str = Field(..., description="The unique ID for the background ingestion task.")
    status_url: str = Field(..., description="The URL to poll for task status.")
    message: str = "File received and queued for processing."

# --- Schemas for /task/{task_id} ---

class ArtifactModel(BaseModel):
    """Represents a processed artifact."""
    type: str = Field(..., description="Type of artifact (e.g., 'transcript', 'frame')")
    path: str = Field(..., description="Storage path of the artifact")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Any associated metadata")

class TaskStatusResponse(BaseModel):
    """Response model for checking the status of an ingestion task."""
    task_id: str
    status: TaskStatus
    progress_percent: float = Field(default=0.0, description="Estimated progress (0.0 to 100.0)")
    details: Optional[str] = Field(None, description="Current processing step or error message")
    artifacts: Dict[str, Any] = Field(default_factory=dict, description="Dict of generated artifacts")
    error: Optional[str] = Field(None, description="Detailed error message if status is 'failure'")

# --- Schemas for /query ---

class QueryFilter(BaseModel):
    """Optional filters to narrow down the search context."""
    source_id: Optional[str] = Field(None, description="Filter by the original 'source_id'")
    doc_type: Optional[IngestType] = Field(None, description="Filter by media type")
    date_from: Optional[str] = Field(None, description="ISO 8601 date string")
    date_to: Optional[str] = Field(None, description="ISO 8601 date string")
    organization_id: Optional[str] = Field(None, description="Filter by organization ID")
    
class QueryRequest(BaseModel):
    """Request model for POST /query."""
    query: str = Field(..., min_length=3, description="The natural language query.")
    filters: Optional[QueryFilter] = Field(default_factory=QueryFilter, description="Filters to apply")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of relevant chunks to retrieve")
    organization_id: str = Field(default="default_org", description="The ID of the organization making the query.")

class SourceChunk(BaseModel):
    """References a single piece of retrieved context used to generate the answer."""
    source_file: str = Field(..., description="The original file name or source identifier")
    chunk_text: str = Field(..., description="The actual text chunk (transcript, OCR, etc.)")
    start_time: Optional[float] = Field(None, description="Start time in seconds (for video/audio)")
    end_time: Optional[float] = Field(None, description="End time in seconds (for video/audio)")
    score: float = Field(..., description="Relevance score from the retriever")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Other metadata (page number, etc.)")
    image_path: Optional[str] = Field(None, description="Path to associated image (chart, graph, page)")
    chunk_type: str = Field(default="text", description="Type of chunk: text, image, or table")
    figure_ids: Optional[str] = Field(None, description="Comma-separated list of figure IDs found in this chunk")
    
class QueryResponse(BaseModel):
    """Response model for POST /query."""
    answer: str = Field(..., description="The final answer synthesized by the LLM")
    sources: List[SourceChunk] = Field(..., description="The list of source chunks used")
    query_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for this query")
    viz_data: Optional[Dict[str, Any]] = Field(None, description="Structured data for rendering charts/tables")