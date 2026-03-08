from fastapi import APIRouter, Depends
from app.api.schemas import QueryRequest, QueryResponse
from app.retrieval.retriever import get_retriever
from app.llm.answer_generator import get_answer_generator
from app.config import get_settings, LLMProvider

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_system(
    request: QueryRequest,
    retriever = Depends(get_retriever),
    settings = Depends(get_settings)
):
    """
    Accepts a natural language query and returns a synthesized answer
    based on the ingested multimedia content (RAG).
    Automatically selects LLM provider based on configuration.
    """
    
    print(f"[QUERY] Received: {request.query}")
    
    # 1. Retrieve the relevant text chunks
    relevant_chunks = retriever.retrieve_chunks(request)
    print(f"[QUERY] Retrieved {len(relevant_chunks)} chunks")
    
    # 2. Select answer generator based on configured LLM provider
    if settings.LLM_PROVIDER == LLMProvider.HUGGINGFACE:
        from app.llm.hf_answer_generator import get_hf_answer_generator
        answer_generator = get_hf_answer_generator()
        print("[QUERY] Using HuggingFace (open-source) answer generator")
    else:
        answer_generator = get_answer_generator()
        print(f"[QUERY] Using {settings.LLM_PROVIDER.value} answer generator")
    
    # 3. Generate the grounded answer using the LLM
    response = answer_generator.generate_answer(request.query, relevant_chunks)
    
    return response