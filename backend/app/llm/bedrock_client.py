"""
Amazon Bedrock Client
Replaces google-genai (Gemini) and openai SDK calls.
Invokes:
  - Anthropic Claude 3.5 Sonnet  → chat / RAG answer generation
  - Amazon Titan Embeddings V2   → vector embeddings (replaces sentence-transformers)
"""
import json
import logging
from typing import List, Optional

import boto3
from botocore.config import Config

from app.api.schemas import SourceChunk, QueryResponse
from app.config import get_settings
from app.llm.prompt_templates import SYSTEM_INSTRUCTION, RAG_PROMPT_TEMPLATE
from app.services.toon_formatter import format_to_toon

logger = logging.getLogger("adhi.llm.bedrock")


def _make_bedrock_runtime(region: str, access_key: Optional[str], secret_key: Optional[str]):
    """Create a boto3 Bedrock runtime client. Falls back to IAM role if keys are absent."""
    kwargs = {
        "service_name": "bedrock-runtime",
        "region_name": region,
        "config": Config(retries={"max_attempts": 3, "mode": "adaptive"}),
    }
    if access_key and secret_key:
        kwargs["aws_access_key_id"] = access_key
        kwargs["aws_secret_access_key"] = secret_key
    return boto3.client(**kwargs)


class BedrockAnswerGenerator:
    """
    Drop-in replacement for AnswerGenerator (Gemini).
    Uses Amazon Bedrock → Claude 3.5 Sonnet for generation.
    """

    def __init__(self):
        settings = get_settings()
        self.client = _make_bedrock_runtime(
            region=settings.AWS_BEDROCK_REGION,
            access_key=settings.AWS_ACCESS_KEY_ID,
            secret_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        self.model_id = settings.AWS_BEDROCK_CHAT_MODEL_ID
        logger.info("bedrock_chat_client_initialized", extra={"model_id": self.model_id})

    def generate_answer(
        self,
        query: str,
        chunks: List[SourceChunk],
        query_id: str = "N/A",
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
    ) -> QueryResponse:
        """Generates a grounded RAG answer via Claude on Bedrock."""
        from app.services.usage_logger import log_ai_usage

        context_string = ""
        if chunks:
            context_string = format_to_toon(chunks)
            
        # Add Live Internet Context
        try:
            from app.services.web_search import search_internet_snippets
            live_snippets = search_internet_snippets(query, max_results=4)
            if live_snippets:
                context_string += "\n\n--- LIVE INTERNET SEARCH RESULTS ---\n"
                context_string += "Use these real-time internet results to answer if they are relevant:\n"
                for snip in live_snippets:
                    context_string += f"Source: {snip['title']} ({snip['link']})\nSnippet: {snip['snippet']}\n\n"
                    
                    # Add as a pseudo-source for the frontend citation
                    chunks.append(
                        SourceChunk(
                            text=snip['snippet'],
                            metadata={"document_name": snip['title'], "source_type": "web", "url": snip['link']},
                            score=0.99
                        )
                    )
        except Exception as e:
            logger.warning("live_search_failed", extra={"error": str(e)})

        if not chunks and not context_string.strip():
            return QueryResponse(
                answer="I cannot answer this question because no relevant database content or web search results were found.",
                sources=[],
                query_id=query_id,
            )

        final_prompt = RAG_PROMPT_TEMPLATE.format(context=context_string, query=query)

        # Bedrock Messages API (Claude)
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "system": SYSTEM_INSTRUCTION,
            "messages": [
                {"role": "user", "content": final_prompt}
            ],
            "temperature": 0.2,
        })

        logger.info("bedrock_generate", extra={"query_id": query_id, "chunks": len(chunks)})

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType="application/json",
                accept="application/json",
            )
            result = json.loads(response["body"].read())
            answer_text: str = result["content"][0]["text"]

            # Token logging
            usage = result.get("usage", {})
            try:
                log_ai_usage(
                    query_id=query_id,
                    query_text=query,
                    response_text=answer_text,
                    model_name=self.model_id,
                    prompt_tokens=int(usage.get("input_tokens", 0)),
                    completion_tokens=int(usage.get("output_tokens", 0)),
                    total_tokens=int(usage.get("input_tokens", 0)) + int(usage.get("output_tokens", 0)),
                    user_id=user_id,
                    org_id=org_id,
                )
            except Exception as log_err:
                logger.warning("token_logging_failed", extra={"error": str(log_err)})

            # VIZ parsing (same logic as Gemini client)
            viz_data = None
            if "[VIZ]" in answer_text and "[/VIZ]" in answer_text:
                try:
                    viz_part = answer_text.split("[VIZ]")[1].split("[/VIZ]")[0].strip()
                    viz_data = json.loads(viz_part)
                    answer_text = answer_text.split("[VIZ]")[0].strip()
                except Exception as ve:
                    logger.warning("viz_parse_failed", extra={"error": str(ve)})

            return QueryResponse(
                answer=answer_text,
                sources=chunks,
                viz_data=viz_data,
                query_id=query_id,
            )

        except Exception as e:
            logger.error("bedrock_api_error", extra={"error": str(e), "query_id": query_id})
            return QueryResponse(
                answer=f"Bedrock LLM failed to generate a response. ({type(e).__name__}: {e})",
                sources=[],
                query_id=query_id,
            )


class BedrockEmbedder:
    """
    Drop-in replacement for sentence-transformers.
    Uses Amazon Titan Text Embeddings V2 via Bedrock.
    Returns a list of floats (1024-dim by default).
    """

    def __init__(self):
        settings = get_settings()
        self.client = _make_bedrock_runtime(
            region=settings.AWS_BEDROCK_REGION,
            access_key=settings.AWS_ACCESS_KEY_ID,
            secret_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        self.model_id = settings.AWS_BEDROCK_EMBED_MODEL_ID
        logger.info("bedrock_embedder_initialized", extra={"model_id": self.model_id})

    def embed(self, text: str) -> List[float]:
        """Generate a single embedding vector for the given text."""
        body = json.dumps({"inputText": text})
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=body,
            contentType="application/json",
            accept="application/json",
        )
        result = json.loads(response["body"].read())
        return result["embedding"]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts. Bedrock Titan is per-request, so we loop."""
        return [self.embed(t) for t in texts]


# --- Singletons ---
_bedrock_generator: Optional[BedrockAnswerGenerator] = None
_bedrock_embedder: Optional[BedrockEmbedder] = None


def get_bedrock_answer_generator() -> BedrockAnswerGenerator:
    global _bedrock_generator
    if _bedrock_generator is None:
        _bedrock_generator = BedrockAnswerGenerator()
    return _bedrock_generator


def get_bedrock_embedder() -> BedrockEmbedder:
    global _bedrock_embedder
    if _bedrock_embedder is None:
        _bedrock_embedder = BedrockEmbedder()
    return _bedrock_embedder
