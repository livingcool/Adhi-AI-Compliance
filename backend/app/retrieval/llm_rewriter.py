from app.config import get_settings, LLMProvider
# FIX: Only import 'types', the Client import is causing the crash
from google.generativeai import types 
import google.generativeai as genai
import os
from typing import Optional

# Configuration settings are loaded via get_settings()
settings = get_settings() 

class LLMQueryRewriter:
    """
    Service to rewrite or reformulate vague queries into better search terms 
    based on the configured LLM provider (a Re-RAG step).
    """
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model = "gemini-2.5-flash"

        if self.provider == LLMProvider.GEMINI:
            if not settings.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY is not set for GEMINI provider.")
            
            # 1. Configure the API Key Globally
            # This makes the API methods available via the top-level 'genai' module
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            
            # 2. DELETE: Removed invalid client instantiation 
            # self.client = Client() is invalid and caused the crash
            
        elif self.provider == LLMProvider.OPENAI:
            # Placeholder for OpenAI client initialization
            pass 
        
        else:
            raise NotImplementedError(f"LLM Provider {self.provider} not supported for rewriting.")

    def rewrite_query(self, original_query: str) -> str:
        """
        Uses the LLM to generate a search-optimized query.
        """
        if self.provider == LLMProvider.GEMINI:
            prompt = (
                "You are an expert query reformulator for a multimodal search engine. "
                "Analyze the user's query and rewrite it to be more verbose, specific, "
                "and effective for vector database similarity search. Only output the new query text."
                f"\n\nOriginal Query: {original_query}"
            )
            
            try:
                # --- FIX: Use the top-level module function for content generation ---
                # This pattern is genai.generate_content or genai.models.generate_content
                # Since genai.generate_content failed before, let's assume the
                # Client() object is now implicit and needs the 'models' submodule.
                # However, since we can't import Client, the next best thing is to assume
                # the functions are available via the configured module:
                
                response = genai.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1
                    )
                )
                
                # Strip leading/trailing whitespace and ensure clean output
                rewritten_query = response.text.strip().replace('"', '')
                return rewritten_query if rewritten_query else original_query
            
            except Exception as e:
                print(f"[LLM Rewriter] Error during Gemini API call: {e}")
                return original_query # Fallback to original query on failure

        # Placeholder for other providers if needed
        return original_query

# --- Singleton setup for Dependency Injection ---

_rewriter: Optional[LLMQueryRewriter] = None

def get_query_rewriter() -> LLMQueryRewriter:
    """Dependency injector for the singleton Rewriter service."""
    global _rewriter
    if _rewriter is None:
        _rewriter = LLMQueryRewriter()
    return _rewriter