"""
Test script to verify visual content retrieval with image_path and chunk_type.
Run this after re-ingesting a PDF with the new schema.
"""
from app.retrieval.retriever import get_retriever
from app.api.schemas import QueryRequest

def test_visual_retrieval():
    print("=" * 60)
    print("TESTING VISUAL CONTENT RETRIEVAL")
    print("=" * 60)
    
    # Test query
    query = "Show me charts about GDP growth"
    print(f"\nQuery: {query}\n")
    
    # Get retriever
    retriever = get_retriever()
    request = QueryRequest(query=query, top_k=5)
    
    # Retrieve chunks
    chunks = retriever.retrieve_chunks(request)
    
    print(f"\n{'=' * 60}")
    print(f"RESULTS: Found {len(chunks)} chunks")
    print("=" * 60)
    
    for i, chunk in enumerate(chunks, 1):
        print(f"\n[{i}] Score: {chunk.score:.4f}")
        print(f"Source: {chunk.source_file}")
        print(f"Type: {chunk.chunk_type}")
        print(f"Page: {chunk.metadata.get('page_number', 'N/A')}")
        print(f"Image Path: {chunk.image_path or 'None'}")
        print(f"Text: {chunk.chunk_text[:150]}...")
        
        if chunk.image_path:
            print(f"  ✓ HAS IMAGE: {chunk.image_path}")
    
    # Count visual chunks
    visual_chunks = [c for c in chunks if c.chunk_type == "image" and c.image_path]
    print(f"\n{'=' * 60}")
    print(f"Visual chunks with images: {len(visual_chunks)}/{len(chunks)}")
    print("=" * 60)
    
    if visual_chunks:
        print("\n✓ Visual content retrieval is working!")
        print("Images can now be displayed in the frontend.")
    else:
        print("\n⚠ No visual chunks found. Make sure:")
        print("  1. Poppler is installed for PDF-to-image conversion")
        print("  2. PDF has been re-ingested with new schema")
        print("  3. Database was recreated (old schema won't have image_path)")

if __name__ == "__main__":
    test_visual_retrieval()
