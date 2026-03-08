from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey, Enum as SqlEnum, DateTime
from sqlalchemy.orm import sessionmaker, relationship, Session, joinedload
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from app.config import settings 
from app.api.schemas import IngestType

# --- SQLAlchemy Setup ---

# Detect if we are using SQLite or Postgres (Supabase)
is_sqlite = settings.DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Models (Tables) ---

class ServiceProvider(Base):
    """Represents a service business (subscriber) using Adhi."""
    __tablename__ = "service_providers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_name = Column(String, nullable=False)
    subscription_plan = Column(String, default="professional")
    admin_email = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    organizations = relationship("Organization", back_populates="service_provider", cascade="all, delete-orphan")

class Organization(Base):
    """Represents a client organization managed by a service provider."""
    __tablename__ = "organizations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    service_provider_id = Column(String, ForeignKey("service_providers.id"), nullable=False)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    settings = Column(Text, default="{}") # JSON settings
    created_at = Column(DateTime, default=datetime.utcnow)
    
    service_provider = relationship("ServiceProvider", back_populates="organizations")
    documents = relationship("Document", back_populates="organization", cascade="all, delete-orphan")

class Document(Base):
    """
    Represents a single ingested file (video, audio, PDF, etc.).
    A Document has many TextChunks.
    """
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    source_file_name = Column(String, index=True)
    source_id = Column(String, unique=True, index=True)
    doc_type = Column(SqlEnum(IngestType), nullable=False)
    storage_path = Column(String)
    status = Column(String, default="processing")
    intelligence_summary = Column(Text, nullable=True) # JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="documents")
    chunks = relationship("TextChunk", back_populates="document", cascade="all, delete-orphan")

class TextChunk(Base):
    """
    Represents a single chunk of text or visual content from a document.
    Links vector store to text content and associated images.
    """
    __tablename__ = "text_chunks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    vector_id = Column(Integer, unique=True, index=True, nullable=True)
    
    text_content = Column(Text, nullable=False)
    start_time = Column(Float, nullable=True)
    end_time = Column(Float, nullable=True)
    page_number = Column(Integer, nullable=True)
    
    image_path = Column(String, nullable=True)
    chunk_type = Column(String, default="text")
    figure_ids = Column(String, nullable=True)
    
    document = relationship("Document", back_populates="chunks")

# --- Pydantic Models ---

class TextChunkCreate(BaseModel):
    vector_id: Optional[int] = None
    text_content: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    page_number: Optional[int] = None
    image_path: Optional[str] = None
    chunk_type: str = "text"
    figure_ids: Optional[str] = None
    
    class Config:
        from_attributes = True

# --- Database Initialization ---

def create_db_and_tables():
    """Initializes the database and creates tables."""
    try:
        print(f"[MetadataStore] Initializing database at {settings.DATABASE_URL}")
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[MetadataStore] Error creating tables: {e}")
        raise

@contextmanager
def get_db(org_id: Optional[str] = None) -> Session:
    db = SessionLocal()
    try:
        if org_id and not is_sqlite:
            # Set the organization ID in the session for Row Level Security (RLS)
            # This allows Supabase/Postgres to enforce data isolation automatically
            db.execute(f"SET app.current_organization_id = '{org_id}'")
            
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# --- CRUD Functions ---

def get_chunk_by_vector_id(db: Session, vector_id: int) -> Optional[TextChunk]:
    return (
        db.query(TextChunk)
        .filter(TextChunk.vector_id == vector_id)
        .options(joinedload(TextChunk.document).joinedload(Document.organization))
        .first()
    )

def get_chunks_by_vector_ids(db: Session, vector_ids: List[int]) -> List[TextChunk]:
    if not vector_ids:
        return []
    return (
        db.query(TextChunk)
        .filter(TextChunk.vector_id.in_(vector_ids))
        .options(joinedload(TextChunk.document).joinedload(Document.organization))
        .all()
    )

# --- Organization & Service Provider Helpers ---

def get_organization_by_slug(db: Session, slug: str) -> Optional[Organization]:
    return db.query(Organization).filter(Organization.slug == slug).first()

def create_organization(db: Session, name: str, slug: str, service_provider_id: str) -> Organization:
    org = Organization(name=name, slug=slug, service_provider_id=service_provider_id)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org

def ensure_default_provider(db: Session) -> ServiceProvider:
    provider = db.query(ServiceProvider).first()
    if not provider:
        provider = ServiceProvider(
            business_name="Adhi Default Services",
            admin_email="admin@adhi.ai"
        )
        db.add(provider)
        db.commit()
        db.refresh(provider)
    return provider


# ---------------------------------------------------------------------------
# Register compliance models with Base so create_all() picks them up.
# MUST stay at the bottom: models.py imports Base/engine/SessionLocal from
# this file (defined above), so those symbols are already available by the
# time Python reaches this line, making the circular import safe.
# ---------------------------------------------------------------------------
import app.store.models as _compliance_models  # noqa: F401, E402