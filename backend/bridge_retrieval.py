import sys
import json
import os

# Add current directory to path to find 'app' module
sys.path.append(os.getcwd())

try:
    from app.retrieval.retriever import get_retriever
    from app.api.schemas import QueryRequest
except ImportError as e:
    print(json.dumps({"success": False, "error": f"Import Error: {e}"}))
    sys.exit(1)

def main():
    try:
        if len(sys.argv) < 3:
            raise ValueError("Usage: python bridge_retrieval.py <query> <org_id>")

        query = sys.argv[1]
        org_id = sys.argv[2]
        
        # Initialize Retriever
        retriever = get_retriever()
        
        # Create Request Object
        req = QueryRequest(query=query, organization_id=org_id, top_k=3)
        
        # Execute Search
        chunks = retriever.retrieve_chunks(req)
        
        # Serialize Results
        results = [{
            "text": c.chunk_text,
            "score": c.score,
            "source": c.source_file,
            "page": c.metadata.get("page_number", "N/A")
        } for c in chunks]
        
        print(json.dumps({"success": True, "count": len(results), "data": results}))

    except Exception as e:
        # Catch logic errors and print as JSON
        print(json.dumps({"success": False, "error": str(e)}))

if __name__ == "__main__":
    main()
