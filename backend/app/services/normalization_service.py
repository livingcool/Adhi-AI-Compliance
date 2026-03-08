import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class UnifiedEntity(BaseModel):
    name: str
    type: str  # person, organization, location, concept, etc.
    context: str

class UnifiedIntelligenceRecord(BaseModel):
    source_type: str  # video, audio, image, pdf
    content_summary: str
    entities: List[UnifiedEntity]
    sentiment: Optional[str] = None
    structured_data: Dict[str, Any] = {}
    timestamp_offsets: List[float] = []

class NormalizationService:
    """
    Normalizes raw multimodal outputs (transcripts, vision labels, PDF text)
    into a unified 'Intelligence Record' for cross-modal querying.
    """
    
    @staticmethod
    def normalize_video_output(transcript: str, visual_descriptions: List[str], timestamps: List[float]) -> UnifiedIntelligenceRecord:
        # Placeholder for complex entity extraction logic
        return UnifiedIntelligenceRecord(
            source_type="video",
            content_summary=f"Visual Analysis: {len(visual_descriptions)} keyframes. Transcript: {transcript[:200]}...",
            entities=[], # Would be populated by an LLM-based NER service
            timestamp_offsets=timestamps,
            structured_data={
                "has_visuals": True,
                "transcript_length": len(transcript)
            }
        )

    @staticmethod
    def normalize_audio_output(transcript: str) -> UnifiedIntelligenceRecord:
        return UnifiedIntelligenceRecord(
            source_type="audio",
            content_summary=transcript[:500],
            entities=[],
            structured_data={
                "has_visuals": False,
                "transcript_length": len(transcript)
            }
        )

    @staticmethod
    def normalize_pdf_output(text: str, metadata: Dict[str, Any]) -> UnifiedIntelligenceRecord:
        return UnifiedIntelligenceRecord(
            source_type="pdf",
            content_summary=text[:500],
            entities=[],
            structured_data=metadata
        )

def get_normalization_service():
    return NormalizationService()
