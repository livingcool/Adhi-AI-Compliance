import logging
from typing import List, Optional

from app.api.schemas import SourceChunk, QueryResponse
from app.config import get_settings, LLMProvider

logger = logging.getLogger("adhi.llm")

_gemini_generator = None


def get_answer_generator():
    """
    Factory / Dependency injector.
    Returns Bedrock generator when LLM_PROVIDER=bedrock,
    otherwise returns Gemini generator (existing behaviour).
    """
    settings = get_settings()

    if settings.LLM_PROVIDER == LLMProvider.BEDROCK:
        from app.llm.bedrock_client import get_bedrock_answer_generator
        return get_bedrock_answer_generator()

    # --- Legacy Gemini path ---
    global _gemini_generator
    if _gemini_generator is None:
        _gemini_generator = _GeminiAnswerGenerator()
    return _gemini_generator


class _GeminiAnswerGenerator:
    """
    Legacy Gemini-based generator.
    Activated when LLM_PROVIDER=gemini (default).
    """

    def __init__(self):
        from google import genai
        from google.genai import types as genai_types
        from app.llm.prompt_templates import SYSTEM_INSTRUCTION, RAG_PROMPT_TEMPLATE
        from app.services.toon_formatter import format_to_toon

        self._genai_types = genai_types
        self._SYSTEM_INSTRUCTION = SYSTEM_INSTRUCTION
        self._RAG_PROMPT_TEMPLATE = RAG_PROMPT_TEMPLATE
        self._format_to_toon = format_to_toon

        settings = get_settings()
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is missing.")
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self.model_name = "gemini-1.5-flash"
        logger.info("gemini_client_initialized", extra={"model": self.model_name})

    def generate_answer(
        self,
        query: str,
        chunks: List[SourceChunk],
        query_id: str = "N/A",
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
    ) -> QueryResponse:
        from app.services.usage_logger import log_ai_usage
        import json

        if not chunks:
            return QueryResponse(
                answer="I cannot answer this question because no relevant content was found.",
                sources=[],
                query_id=query_id,
            )

        context_string = self._format_to_toon(chunks)
        final_prompt = self._RAG_PROMPT_TEMPLATE.format(context=context_string, query=query)

        logger.info("gemini_generate", extra={"query_id": query_id, "chunks": len(chunks)})

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=final_prompt,
                config=self._genai_types.GenerateContentConfig(
                    system_instruction=self._SYSTEM_INSTRUCTION,
                    temperature=0.2,
                    max_output_tokens=2048,
                ),
            )
            answer_text = response.text
            viz_data = None

            if response.usage_metadata:
                try:
                    usage = response.usage_metadata
                    log_ai_usage(
                        query_id=query_id, query_text=query, response_text=answer_text,
                        model_name=self.model_name,
                        prompt_tokens=int(float(usage.prompt_token_count or 0)),
                        completion_tokens=int(float(usage.candidates_token_count or 0)),
                        total_tokens=int(float(usage.total_token_count or 0)),
                        user_id=user_id, org_id=org_id,
                    )
                except Exception as log_err:
                    logger.warning("token_logging_failed", extra={"error": str(log_err)})

            if "[VIZ]" in answer_text and "[/VIZ]" in answer_text:
                try:
                    viz_part = answer_text.split("[VIZ]")[1].split("[/VIZ]")[0].strip()
                    viz_data = json.loads(viz_part)
                    answer_text = answer_text.split("[VIZ]")[0].strip()
                except Exception as ve:
                    logger.warning("viz_parse_failed", extra={"error": str(ve)})

            return QueryResponse(answer=answer_text, sources=chunks, viz_data=viz_data, query_id=query_id)

        except Exception as e:
            logger.error("gemini_api_error", extra={"error": str(e), "query_id": query_id})
            return QueryResponse(
                answer=f"The LLM failed to generate a response. ({type(e).__name__})",
                sources=[], query_id=query_id,
            )