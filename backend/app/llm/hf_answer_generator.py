"""
HuggingFace-based Answer Generator
Replaces Gemini API with open-source models via HuggingFace Inference API
"""
from typing import List, Optional
import json
try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except ImportError:
    InferenceClient = None
    HF_AVAILABLE = False
from app.api.schemas import SourceChunk, QueryResponse
from app.config import get_settings
from app.llm.prompt_templates import SYSTEM_INSTRUCTION, RAG_PROMPT_TEMPLATE
from app.services.toon_formatter import format_to_toon


class HFAnswerGenerator:
    """
    Service responsible for generating answers using HuggingFace Inference API
    with open-source models like Mixtral or Llama
    """
    
    def __init__(self):
        settings = get_settings()
        
        # Get HuggingFace token from settings
        hf_token = getattr(settings, 'HF_TOKEN', None)
        if not hf_token:
            print("[WARN] HF_TOKEN not set, using public inference (rate limited)")
        
        # Initialize HuggingFace Inference Client
        # Default to Mixtral-8x7B-Instruct-v0.1 (good balance of quality & speed)
        self.model_name = getattr(settings, 'HF_MODEL_CHAT', 'mistralai/Mixtral-8x7B-Instruct-v0.1')
        
        self.client = InferenceClient(
            model=self.model_name,
            token=hf_token
        )
        
        print(f"[LLM] HuggingFace client initialized with model {self.model_name}")
    
    def generate_answer(self, query: str, chunks: List[SourceChunk]) -> QueryResponse:
        """
        Generates an answer grounded in the provided context chunks
        using HuggingFace Inference API
        """
        
        if not chunks:
            return QueryResponse(
                answer="I cannot answer this question because no relevant corporate knowledge was found.",
                sources=[],
                query_id="N/A"
            )
        
        # Format context using TOON
        context_string = format_to_toon(chunks)
        
        # Build messages for chat completion
        messages = [
            {
                "role": "system",
                "content": SYSTEM_INSTRUCTION
            },
            {
                "role": "user",
                "content": RAG_PROMPT_TEMPLATE.format(
                    context=context_string,
                    query=query
                )
            }
        ]
        
        print(f"[LLM] Sending query and {len(chunks)} chunks to HuggingFace ({self.model_name})...")
        
        try:
            # Call HuggingFace Inference API
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=2048,
                temperature=0.2,
                stream=False
            )
            
            # Extract answer text
            answer_text = response.choices[0].message.content
            viz_data = None
            
            # Parse visualization data if present
            if "[VIZ]" in answer_text and "[/VIZ]" in answer_text:
                try:
                    viz_part = answer_text.split("[VIZ]")[1].split("[/VIZ]")[0].strip()
                    viz_data = json.loads(viz_part)
                    # Clean answer by removing VIZ block
                    answer_text = answer_text.split("[VIZ]")[0].strip()
                except Exception as ve:
                    print(f"[LLM] Error parsing viz JSON: {ve}")
            
            return QueryResponse(
                answer=answer_text,
                sources=chunks,
                viz_data=viz_data
            )
        
        except Exception as e:
            print(f"[ERROR] HuggingFace API call failed: {e}")
            return QueryResponse(
                answer=f"The LLM failed to generate a response due to an API error. ({type(e).__name__})",
                sources=[],
                query_id="N/A"
            )


# Singleton setup
_hf_answer_generator: Optional[HFAnswerGenerator] = None

def get_hf_answer_generator() -> HFAnswerGenerator:
    """
    Dependency injector for the singleton HFAnswerGenerator service
    """
    global _hf_answer_generator
    if _hf_answer_generator is None:
        _hf_answer_generator = HFAnswerGenerator()
    return _hf_answer_generator
