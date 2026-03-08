"""
Manual PDF ingestion script to test the pipeline directly.
This bypasses Celery and runs the ingestion synchronously.
"""
from pathlib import Path
from app.services.ingestion_orchestrator import process_pdf_source
from app.api.schemas import IngestType
import uuid

# Mock task object for testing
class MockTask:
    def __init__(self):
        self.request = type('obj', (object,), {'id': str(uuid.uuid4())})()
    
    def update_state(self, state, meta):
        print(f"[Task Update] {state}: {meta.get('details', '')} ({meta.get('progress_percent', 0):.1f}%)")

def test_pdf_ingestion():
    print("=" * 60)
    print("MANUAL PDF INGESTION TEST")
    print("=" * 60)
    
    # Path to the uploaded PDF
    pdf_path = Path("data/uploads/qatar_test_doc.pdf.pdf")
    
    if not pdf_path.exists():
        print(f"\nERROR: PDF not found at {pdf_path}")
        print("Please upload a PDF through the frontend first.")
        return
    
    print(f"\nFound PDF: {pdf_path}")
    print(f"Size: {pdf_path.stat().st_size / 1024 / 1024:.2f} MB\n")
    
    # Create mock task
    mock_task = MockTask()
    source_id = f"manual_test_{uuid.uuid4().hex[:8]}"
    
    print(f"Starting ingestion with source_id: {source_id}\n")
    
    try:
        artifacts = process_pdf_source(
            task_self=mock_task,
            source_id=source_id,
            original_file_path=pdf_path,
            file_name=pdf_path.name,
            doc_type=IngestType.PDF
        )
        
        print("\n" + "=" * 60)
        print("INGESTION SUCCESSFUL!")
        print("=" * 60)
        print(f"\nArtifacts: {artifacts}")
        
        # Verify the results
        from app.store.vector_store import get_vector_store
        vector_store = get_vector_store()
        print(f"\nVectors in FAISS: {vector_store.index.ntotal}")
        
        import sqlite3
        conn = sqlite3.connect('data/metadata.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM text_chunks")
        chunk_count = cursor.fetchone()[0]
        print(f"Chunks in database: {chunk_count}")
        conn.close()
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("INGESTION FAILED!")
        print("=" * 60)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_ingestion()
