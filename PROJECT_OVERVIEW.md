# Adhi - Multimodal RAG Intelligence System

## 🎯 Problem Statement
Traditional RAG systems only process text documents, leaving 90% of corporate knowledge trapped in multimedia formats like videos, audio recordings, and images inaccessible for intelligent search and retrieval.

## 🚀 Project Vision
Adhi is a production-grade multimodal RAG (Retrieval-Augmented Generation) system that unlocks "dark data" from multimedia sources. It processes videos, audio files, images, and PDFs to extract meaningful content through transcription, OCR, and visual analysis. The system uses asynchronous processing with Celery workers to handle resource-intensive tasks like audio transcription via Sarvam AI and video frame analysis. Users can then query this processed multimedia content using natural language and receive contextual answers with source citations, making previously inaccessible corporate knowledge searchable and actionable.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Client    │    │  Streamlit UI    │    │   Mobile App    │
│   (React/Next)  │    │   (Python)       │    │   (Future)      │
└─────────┬───────┘    └─────────┬────────┘    └─────────────────┘
          │                      │
          └──────────────────────┼──────────────────────────────────┐
                                 │                                  │
                    ┌────────────▼──────────────┐                   │
                    │      FastAPI Server       │                   │
                    │   (Async REST API)        │                   │
                    └────────────┬──────────────┘                   │
                                 │                                  │
                    ┌────────────▼──────────────┐                   │
                    │     Redis Message         │                   │
                    │    Broker & Cache         │                   │
                    └────────────┬──────────────┘                   │
                                 │                                  │
        ┌────────────────────────┼────────────────────────┐         │
        │                       │                        │         │
┌───────▼────────┐    ┌─────────▼────────┐    ┌─────────▼─────────┐ │
│  CPU Workers   │    │   GPU Workers    │    │  Storage Layer    │ │
│  (Audio/PDF)   │    │ (Video/Images)   │    │  (Local/S3)       │ │
└───────┬────────┘    └─────────┬────────┘    └─────────┬─────────┘ │
        │                       │                       │           │
        └───────────────────────┼───────────────────────┘           │
                                │                                   │
        ┌───────────────────────▼───────────────────────┐           │
        │            External Services                   │           │
        │  ┌─────────────┐  ┌──────────────────────────┐ │           │
        │  │  Sarvam AI  │  │     Google Gemini        │ │           │
        │  │(Transcribe) │  │   (LLM Generation)       │ │           │
        │  └─────────────┘  └──────────────────────────┘ │           │
        └───────────────────────────────────────────────┘           │
                                │                                   │
        ┌───────────────────────▼───────────────────────┐           │
        │              Vector Store                      │           │
        │        (FAISS + Metadata DB)                   │           │
        └───────────────────────────────────────────────┘           │
                                                                    │
        ┌───────────────────────────────────────────────────────────▼─┐
        │                    Query Engine                               │
        │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
        │  │  Retriever  │  │  Reranker   │  │   Answer Generator  │   │
        │  │  (Vector)   │  │ (Optional)  │  │     (LLM + RAG)     │   │
        │  └─────────────┘  └─────────────┘  └─────────────────────┘   │
        └─────────────────────────────────────────────────────────────┘
```

## 🔄 Process Flow

```
[File Upload] → [FastAPI Server] → [Task Queue (Redis)]
                      ↓
[Celery Workers] → [Media Processing Pipeline]
     ↓                    ↓                ↓
[Audio/Video]      [Image Analysis]   [PDF Processing]
     ↓                    ↓                ↓
[Sarvam AI]        [OCR/Vision]      [Text Extraction]
[Transcription]    [Analysis]        [Page Images]
     ↓                    ↓                ↓
[Text Chunks] → [Vector Embeddings] → [Vector Store]
                      ↓
[Query Interface] → [Semantic Search] → [LLM Generation]
                      ↓
[Contextual Answer + Source Citations]
```

## 🎯 Unique Value Proposition

### How it's Different from Existing Solutions:
- **Multimodal Processing**: Unlike traditional RAG systems that only handle text, Adhi processes videos, audio, images, and PDFs in a unified pipeline
- **Asynchronous Architecture**: Uses Celery with Redis for scalable background processing, unlike synchronous solutions
- **Smart Task Routing**: Automatically routes different media types to appropriate processing queues (GPU for video, CPU for audio)
- **Production-Ready**: Built with FastAPI, includes proper error handling, retry mechanisms, and task status tracking

### Problem-Solving Approach:
- **Content Extraction**: Converts multimedia to searchable text through transcription (Sarvam AI), OCR, and visual analysis
- **Intelligent Indexing**: Creates vector embeddings for semantic search across all content types
- **Unified Query Interface**: Single API endpoint to search across all ingested multimedia content
- **Source Attribution**: Provides citations with timestamps, page numbers, and visual references

### Key USPs:
- **90% Dark Data Unlock**: Specifically targets the untapped multimedia knowledge in organizations
- **Language Support**: Supports multiple languages including Tamil (ta-IN) through Sarvam AI
- **Visual Grounding**: Maintains connections between text content and source images/frames
- **Enterprise-Ready**: Multi-organization support with proper data isolation and scalability

## ✨ Core Features

### 📥 Ingestion Capabilities
- **Multi-format Support**: Video (MP4), Audio (various formats), Images (JPG, PNG), PDFs
- **Asynchronous Processing**: Non-blocking file uploads with background processing
- **Real-time Status Tracking**: Task progress monitoring with detailed status updates
- **Smart Task Routing**: Automatic routing to appropriate processing queues

### 🧠 Processing Intelligence
- **Intelligent Transcription**: Audio-to-text conversion with language detection
- **Visual Analysis**: Frame extraction and image content analysis
- **OCR Processing**: Text extraction from images and PDF pages
- **Content Chunking**: Intelligent segmentation for optimal retrieval

### 🔍 Query & Retrieval
- **Semantic Search**: Vector-based similarity search across all content
- **Natural Language Queries**: Ask questions in plain English
- **Source Attribution**: Detailed citations with timestamps and visual references
- **Multi-modal Results**: Text answers with supporting images and media

### 🏢 Enterprise Features
- **Multi-organization Support**: Tenant isolation for enterprise deployments
- **RESTful API**: Complete API with ingestion, query, and status endpoints
- **Web Interface**: Modern React-based dashboard for file management and querying
- **Alternative UI**: Streamlit interface for quick testing and demos

## 🛠️ Technology Stack

### Backend Technologies
- **FastAPI**: Async REST API framework
- **Celery**: Distributed task queue for background processing
- **Redis**: Message broker and caching layer
- **SQLAlchemy**: Database ORM with PostgreSQL/SQLite support
- **Pydantic**: Data validation and settings management
- **FAISS**: Vector similarity search engine
- **Sentence Transformers**: Text embedding generation
- **FFmpeg**: Video/audio processing
- **OpenCV**: Computer vision and image processing

### Frontend Technologies
- **Next.js 16**: React framework with server-side rendering
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Animation library
- **React Dropzone**: File upload component

### External Services
- **Sarvam AI**: Audio transcription service
- **Google Gemini**: Large language model for answer generation
- **Supabase**: Optional cloud database and storage

### Infrastructure
- **PostgreSQL**: Production database
- **AWS S3**: Optional cloud storage backend
- **Docker**: Containerization support

## 📊 Project Status

### ✅ Completed Features (55% Complete)
- FastAPI server with all endpoints
- Async pipeline with Redis/Celery
- Task routing and status tracking
- Video-to-text pipeline (live)
- Audio transcription via Sarvam AI
- Basic web interface
- Multi-organization support

### 🚧 In Progress
- Vector embedding and storage
- Visual analysis for video frames
- Query engine with LLM integration
- Advanced UI components

### 📋 Upcoming Features
- PDF processing with OCR
- Image analysis pipeline
- Advanced search filters
- Performance optimization
- Mobile application

## 💰 Implementation Cost Estimate

### Development Phase (3-4 months)
- **Senior Full-Stack Developer**: $40,000 - $50,000
- **ML/AI Engineer**: $32,500 - $40,000
- **DevOps Engineer**: $18,700 - $23,800
- **Total Development**: $91,200 - $113,800

### Annual Infrastructure Costs
- **Cloud Hosting**: $2,400 - $6,000
- **API Services** (Sarvam + Gemini): $3,000 - $8,400
- **Storage & Bandwidth**: $1,200 - $2,400
- **Monitoring & Security**: $600 - $1,200
- **Total Infrastructure**: $7,200 - $18,000

### Total First Year: $98,400 - $131,800
### Annual Operating Cost: $27,200 - $48,000

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Redis server
- FFmpeg
- Node.js 18+ (for webapp)

### Quick Setup
```bash
# Backend setup
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Start services
uvicorn app.main:app --reload
celery -A app.workers.celery_app worker --loglevel=info -Q cpu_tasks -P eventlet

# Frontend setup
cd webapp
npm install
npm run dev
```

### Environment Configuration
Create `.env` files in both `backend/` and `webapp/` directories with required API keys:
- `SARVAM_API_KEY`
- `GOOGLE_API_KEY`
- `REDIS_URL`

## 📈 Business Impact

### ROI Drivers
- **Knowledge Accessibility**: 90% increase in searchable corporate content
- **Decision Speed**: Faster access to multimedia insights
- **Operational Efficiency**: Reduced time searching across media files
- **Compliance**: Better audit trails with source attribution

### Target Markets
- **Enterprise Knowledge Management**
- **Legal Document Review**
- **Medical Records Analysis**
- **Educational Content Management**
- **Media & Broadcasting**

## 🔮 Future Roadmap

### Phase 2 (6 months)
- Real-time streaming ingestion
- Advanced visual understanding
- Multi-language expansion
- Performance optimization

### Phase 3 (12 months)
- Mobile applications
- Advanced analytics dashboard
- Integration marketplace
- AI-powered insights

---

**Adhi** - Transforming how organizations interact with their multimedia knowledge base, one query at a time.