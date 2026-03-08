"""
Diagnostic script to check the status of documents and vector store.
"""
from app.store.metadata_store import get_db, Document, TextChunk
from app.store.vector_store import get_vector_store

def check_status():
    print("=" * 60)
    print("DATABASE STATUS")
    print("=" * 60)
    
    with get_db() as db:
        documents = db.query(Document).all()
        print(f"\nTotal documents in database: {len(documents)}\n")
        
        for doc in documents:
            print(f"Document: {doc.source_file_name}")
            print(f"  - Type: {doc.doc_type}")
            print(f"  - Status: {doc.status}")
            print(f"  - Source ID: {doc.source_id}")
            print(f"  - Storage Path: {doc.storage_path}")
            
            # Count chunks for this document
            chunks = db.query(TextChunk).filter(TextChunk.document_id == doc.id).all()
            print(f"  - Text Chunks: {len(chunks)}")
            if chunks:
                print(f"    Sample chunk: {chunks[0].text_content[:100]}...")
            print()
    
    print("=" * 60)
    print("VECTOR STORE STATUS")
    print("=" * 60)
    
    try:
        vector_store = get_vector_store()
        print(f"\nTotal vectors in FAISS index: {vector_store.index.ntotal}")
        print(f"Index dimension: {vector_store.embedding_dim}")
        print(f"Index path: {vector_store.index_path}")
        print(f"Index exists on disk: {vector_store.index_path.exists()}")
    except Exception as e:
        print(f"\nError accessing vector store: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_status()
