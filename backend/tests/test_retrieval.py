"""
Test retrieval with the ingested PDF data.
"""
from app.retrieval.retriever import get_retriever
from app.api.schemas import QueryRequest

def test_retrieval():
    print("=" * 60)
    print("TESTING RETRIEVAL")
    print("=" * 60)
    
    # Create a query
    query = "Fiscal Policy: Enhance Resilience and Support Diversification"
    print(f"\nQuery: {query}\n")
    
    # Get retriever
    retriever = get_retriever()
    
    # Create request
    request = QueryRequest(query=query, top_k=5)
    
    # Retrieve chunks
    chunks = retriever.retrieve_chunks(request)
    
    print(f"\n{'=' * 60}")
    print(f"RESULTS: Found {len(chunks)} chunks")
    print("=" * 60)
    
    for i, chunk in enumerate(chunks, 1):
        print(f"\n[{i}] Score: {chunk.score:.4f}")
        print(f"Source: {chunk.source_file}")
        print(f"Text: {chunk.chunk_text[:200]}...")
    
    if not chunks:
        print("\nNO RESULTS FOUND - This indicates a problem with retrieval!")
    else:
        print(f"\n✓ Retrieval working! Found {len(chunks)} relevant chunks.")

if __name__ == "__main__":
    test_retrieval()
