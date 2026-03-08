import json
import re
from pathlib import Path
from typing import Dict, List, Any, Set
import numpy as np
import uuid

from app.api.schemas import IngestType, TaskStatus
from app.config import get_settings
from app.services.pdf_processor import process_pdf
from app.services.normalization_service import get_normalization_service
from app.store.metadata_store import get_db, Document, TextChunk, get_organization_by_slug, ensure_default_provider, create_organization

# A helper to update task state (used by the orchestrator via task_self)
def update_task_state(task, status: TaskStatus, details: str, progress: float = 0.0):
    """Helper function to update Celery task state and metadata."""
    meta = {
        'status': status.value,
        'details': details,
        'progress_percent': progress,
    }
    task.update_state(state=status.value, meta=meta)

def extract_figure_ids(text: str) -> str:
    """
    Extracts figure and table identifiers from text using regex.
    Returns a comma-separated string of unique IDs (e.g., "Figure 1,Table 2").
    """
    # Regex to match "Figure 1", "Fig. 2", "Table 3", etc.
    # Case insensitive, handles optional period and whitespace
    pattern = r"(?:Figure|Fig\.?|Table)\s+(\d+)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    unique_ids = set()
    for match in matches:
        # Normalize to "Figure X" or "Table X" based on context if needed, 
        # but for now just storing the raw number might be ambiguous.
        # Let's try to capture the type too.
        pass
    
    # Better regex to capture type and number
    pattern_full = r"(Figure|Fig\.?|Table)\s+(\d+)"
    matches_full = re.findall(pattern_full, text, re.IGNORECASE)
    
    for type_str, num_str in matches_full:
        norm_type = "Table" if "table" in type_str.lower() else "Figure"
        unique_ids.add(f"{norm_type} {num_str}")
        
    return ",".join(sorted(unique_ids)) if unique_ids else None

def process_audio_source(
    task_self, # The Celery task instance passed here
    source_id: str,
    original_file_path: Path,
    file_name: str,
    doc_type: IngestType,
    language: str,
    organization_id: str = "default_org"
) -> Dict[str, Any]:
    """
    The main processing pipeline for any file with an audio track (AUDIO or VIDEO).
    Handles segmentation, transcription, chunking, and embedding.
    """
    
    # Get all singleton services
    settings = get_settings()
    sarvam_client = get_sarvam_client()
    text_chunker = get_text_chunker()
    embed_service = get_embedding_service()
    vector_store = get_vector_store()
    
    artifacts: Dict[str, Any] = {}
    
    with get_db() as db:
        # --- 1. Resolve Organization (Multi-tenant) ---
        provider = ensure_default_provider(db)
        org = get_organization_by_slug(db, organization_id)
        if not org:
            # For POC, auto-create if missing
            org = create_organization(db, f"Org {organization_id}", organization_id, provider.id)
        
        # --- 1.5 Set RLS Context (for Supabase) ---
        if not settings.DATABASE_URL.startswith("sqlite"):
            db.execute(f"SET app.current_organization_id = '{org.id}'")
        
        # --- 2. Create Document Record ---
        print(f"[Orchestrator] Creating document record for {source_id}")
        doc = Document(
            source_id=source_id,
            source_file_name=file_name,
            doc_type=doc_type,
            storage_path=str(original_file_path),
            organization_id=org.id, # Now using the real UUID
            status="processing"
        )
        db.add(doc)
        db.commit() 
        db.refresh(doc)
        
        try:
            # --- 2. Prepare Audio (FFmpeg) ---
            update_task_state(task_self, TaskStatus.PROCESSING, "Extracting/Standardizing audio...", 10.0)
            prepared_audio_path = prepare_audio_for_transcription(
                input_path=original_file_path,
                output_dir=settings.TRANSCRIPT_DIR,
                source_id=source_id
            )
            
            # --- 3. Segment Audio (FIX for 30s limit) ---
            update_task_state(task_self, TaskStatus.PROCESSING, "Splitting audio for API limits...", 20.0)
            # Use 29 seconds to strictly adhere to the API's 30s limit
            segment_paths = split_audio_file(
                prepared_audio_path,
                settings.TRANSCRIPT_DIR,
                segment_duration_sec=29 
            )
            if not segment_paths:
                raise Exception("Audio file was split, but no segments were created.")

            # --- 4. Transcribe Segments (Sarvam) & Combine (Full Loop) ---
            update_task_state(task_self, TaskStatus.PROCESSING, f"Transcribing {len(segment_paths)} segments (Sarvam)...", 40.0)
            
            full_transcript_text = ""
            combined_segments = []
            
            for i, segment_path in enumerate(segment_paths):
                # Update progress for user feedback
                progress = 40.0 + (i / len(segment_paths)) * 10.0
                update_task_state(task_self, TaskStatus.PROCESSING, f"Transcribing segment {i+1}/{len(segment_paths)}...", progress)
                
                segment_transcript_data = sarvam_client.transcribe_audio_file(
                    file_path=segment_path,
                    language_code=language
                )
                
                # Combine results
                segment_text = segment_transcript_data.get('transcript', '')
                if segment_text:
                    full_transcript_text += segment_text + " "
                    combined_segments.extend(segment_transcript_data.get('segments', [{'text': segment_text, 'start': 0.0, 'end': 0.0}]))
            
            transcript_data = {"transcript": full_transcript_text.strip(), "segments": combined_segments}
            
            # Save the raw combined transcript
            transcript_path = settings.TRANSCRIPT_DIR / f"{source_id}_transcript.json"
            with open(transcript_path, 'w', encoding='utf-8') as f:
                json.dump(transcript_data, f, ensure_ascii=False, indent=2)
            
            artifacts['transcript_path'] = str(transcript_path)
            
            # --- 5. Chunk Transcript & Embed Text ---
            update_task_state(task_self, TaskStatus.PROCESSING, "Chunking and embedding transcript...", 55.0)
            chunks_with_times = text_chunker.chunk_transcript(transcript_data)
            
            if not chunks_with_times:
                raise Exception("Transcript was empty or could not be chunked.")
                
            text_chunks = [chunk[0] for chunk in chunks_with_times]
            vectors = embed_service.embed_texts(text_chunks)
            vector_ids = vector_store.add_vectors(vectors, file_type='audio')
            
            # Link Text Chunks to Metadata DB (SQL)
            new_chunk_records = []
            for i, chunk_data in enumerate(chunks_with_times):
                text, start, end = chunk_data
                vector_id = int(vector_ids[i]) if vector_ids[i] is not None else None
                
                db_chunk = TextChunk(
                    document_id=doc.id,
                    vector_id=vector_id,
                    text_content=text,
                    start_time=start,
                    end_time=end,
                    # If using Supabase, we store the embedding directly in DB
                    embedding=vectors[i].tolist() if vector_store.use_supabase else None
                )
                new_chunk_records.append(db_chunk)
            
            db.add_all(new_chunk_records)
            
            # --- 6. Video Frame Analysis (Multimodal Step) ---
            if doc_type == IngestType.VIDEO:
                update_task_state(task_self, TaskStatus.PROCESSING, "Extracting video frames...", 70.0)
                
                # 6a. Extract Frames
                frames_output_dir = settings.FRAME_DIR / source_id
                frames_output_dir.mkdir(parents=True, exist_ok=True)
                
                extract_key_frames(original_file_path, frames_output_dir)
                artifacts['frames_dir'] = str(frames_output_dir)
                
                # 6b. Analyze Frames (Gemini Vision)
                update_task_state(task_self, TaskStatus.PROCESSING, "Analyzing frames with Gemini Vision...", 80.0)
                frame_descriptions = analyze_frames_with_gemini(frames_output_dir)
                
                # 6c. Embed Frame Descriptions and Link
                frame_texts = list(frame_descriptions.values())
                
                if frame_texts:
                    frame_vectors = embed_service.embed_texts(frame_texts)
                    frame_vector_ids = vector_store.add_vectors(frame_vectors, file_type='video')
                    
                    new_frame_chunk_records = []
                    frame_filenames = list(frame_descriptions.keys())

                    for i, text in enumerate(frame_texts):
                        frame_filename = frame_filenames[i]
                        # Time extraction
                        try:
                            time_sec = float(frame_filename.split('_')[-1].replace('s.jpg', ''))
                        except ValueError:
                            time_sec = 0.0

                        db_chunk = TextChunk(
                            document_id=doc.id,
                            vector_id=int(frame_vector_ids[i]) if frame_vector_ids[i] is not None else None,
                            text_content=text,
                            start_time=time_sec,
                            end_time=time_sec,
                            chunk_type="image",
                            image_path=str(frames_output_dir / frame_filename),
                            # Store embedding directly for Supabase
                            embedding=frame_vectors[i].tolist() if vector_store.use_supabase else None
                        )
                        new_frame_chunk_records.append(db_chunk)
                        
                    db.add_all(new_frame_chunk_records)
                    artifacts['visual_count'] = len(frame_vector_ids)
            
            # --- 7. Finalize and Commit ---
            update_task_state(task_self, TaskStatus.PROCESSING, "Normalizing intelligence and finalizing...", 95.0)
            
            norm_service = get_normalization_service()
            if doc_type == IngestType.VIDEO:
                visual_texts = list(frame_descriptions.values()) if 'frame_descriptions' in locals() else []
                # Simple heuristic: timestamps are every X seconds based on frame extraction
                ts_offsets = [float(i) for i in range(len(visual_texts))] 
                intel_record = norm_service.normalize_video_output(
                    transcript=artifacts.get('transcript', ""),
                    visual_descriptions=visual_texts,
                    timestamps=ts_offsets
                )
            else:
                intel_record = norm_service.normalize_audio_output(
                    transcript=artifacts.get('transcript', "")
                )
            
            doc.intelligence_summary = intel_record.json()
            doc.status = "completed"
            db.commit()
            # Final artifact counts
            artifacts['vector_count'] = len(new_chunk_records) + artifacts.get('visual_count', 0)
            artifacts['metadata_count'] = artifacts['vector_count']
            
            print(f"[Orchestrator] Successfully processed {source_id}.")
            return artifacts
        
        except Exception as e:
            # --- Error Handling ---
            print(f"[Orchestrator] FAILED processing for {source_id}: {e}")
            db.rollback()
            doc.status = "failed"
            db.add(doc)
            db.commit()
            raise

def process_image_source(
    task_self,
    source_id: str,
    original_file_path: Path,
    file_name: str,
    doc_type: IngestType,
    organization_id: str = "default_org"
) -> Dict[str, Any]:
    """
    The main processing pipeline for image files.
    """
    print(f"[Orchestrator] Processing image {source_id}")
    
    settings = get_settings()
    embed_service = get_embedding_service()
    vector_store = get_vector_store()
    
    artifacts: Dict[str, Any] = {}
    
    with get_db() as db:
        # --- 1. Resolve Organization (Multi-tenant) ---
        provider = ensure_default_provider(db)
        org = get_organization_by_slug(db, organization_id)
        if not org:
            org = create_organization(db, f"Org {organization_id}", organization_id, provider.id)
            
        # --- 1.5 Set RLS Context (for Supabase) ---
        if not settings.DATABASE_URL.startswith("sqlite"):
            db.execute(f"SET app.current_organization_id = '{org.id}'")
            
        # --- 2. Create Document Record ---
        doc = Document(
            source_id=source_id,
            source_file_name=file_name,
            doc_type=doc_type,
            storage_path=str(original_file_path),
            organization_id=org.id, # Now using the real UUID
            status="processing"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        try:
            # 2. Analyze Image with Gemini
            update_task_state(task_self, TaskStatus.PROCESSING, "Analyzing image with Gemini Vision...", 50.0)
            
            image_dir = settings.FRAME_DIR / source_id
            image_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy the image to this dir so the existing function works
            import shutil
            target_image_path = image_dir / original_file_path.name
            shutil.copy(original_file_path, target_image_path)
            
            frame_descriptions = analyze_frames_with_gemini(image_dir)
            
            # 3. Embed and Store
            update_task_state(task_self, TaskStatus.PROCESSING, "Embedding image description...", 80.0)
            
            description = frame_descriptions.get(original_file_path.name, "")
            if not description:
                # Fallback if filename mismatch
                if frame_descriptions:
                    description = list(frame_descriptions.values())[0]
            
            if description:
                vector = embed_service.embed_texts([description])[0]
                vector_id = vector_store.add_vectors([vector], file_type='image')[0]
                
                # Extract figure IDs from description if any
                fig_ids = extract_figure_ids(description)
                
                db_chunk = TextChunk(
                    document_id=doc.id,
                    vector_id=int(vector_id),
                    text_content=description,
                    start_time=0.0,
                    end_time=0.0,
                    chunk_type="image",
                    image_path=str(target_image_path),
                    figure_ids=fig_ids
                )
                db.add(db_chunk)
                artifacts['visual_count'] = 1
            
            # 4. Finalize
            update_task_state(task_self, TaskStatus.SUCCESS, "Image processed successfully.", 100.0)
            doc.status = "completed"
            db.commit()
            vector_store.save_index()
            
            return artifacts
            
        except Exception as e:
            print(f"[Orchestrator] FAILED processing for {source_id}: {e}")
            db.rollback()
            doc.status = "failed"
            db.add(doc)
            db.commit()
            raise

def process_pdf_source(
    task_self,
    source_id: str,
    original_file_path: Path,
    file_name: str,
    doc_type: IngestType,
    organization_id: str = "default_org"
) -> Dict[str, Any]:
    """
    The main processing pipeline for PDF files.
    """
    print(f"[Orchestrator] Processing PDF {source_id}")
    
    settings = get_settings()
    embed_service = get_embedding_service()
    vector_store = get_vector_store()
    
    artifacts: Dict[str, Any] = {}
    
    with get_db() as db:
        # --- 1. Resolve Organization (Multi-tenant) ---
        provider = ensure_default_provider(db)
        org = get_organization_by_slug(db, organization_id)
        if not org:
            org = create_organization(db, f"Org {organization_id}", organization_id, provider.id)
            
        # --- 1.5 Set RLS Context (for Supabase) ---
        if not settings.DATABASE_URL.startswith("sqlite"):
            db.execute(f"SET app.current_organization_id = '{org.id}'")
            
        doc = Document(
            source_id=source_id,
            source_file_name=file_name,
            doc_type=doc_type,
            storage_path=str(original_file_path),
            organization_id=org.id, # Now using the real UUID
            status="processing"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        try:
            update_task_state(task_self, TaskStatus.PROCESSING, "Extracting text and images from PDF...", 20.0)
            
            # 1. Process PDF (Text + Images)
            pdf_result = process_pdf(original_file_path, source_id)
            raw_text = pdf_result["text"]
            image_paths = pdf_result["image_paths"]
            
            # 2. Chunk and Embed Text
            update_task_state(task_self, TaskStatus.PROCESSING, "Chunking and embedding text...", 40.0)
            
            # Simple paragraph-based chunking for PDFs
            text_chunks = [p for p in raw_text.split('\n\n') if p.strip()]
            
            total_text_chunks = 0
            if text_chunks:
                vectors = embed_service.embed_texts(text_chunks)
                vector_ids = vector_store.add_vectors(vectors, file_type='pdf')
                
                new_chunk_records = []
                for i, text in enumerate(text_chunks):
                    # Extract figure IDs from text
                    fig_ids = extract_figure_ids(text)
                    
                    db_chunk = TextChunk(
                        document_id=doc.id,
                        vector_id=int(vector_ids[i]) if vector_ids[i] is not None else None,
                        text_content=text,
                        start_time=0.0,
                        end_time=0.0,
                        chunk_type="text",
                        figure_ids=fig_ids,
                        embedding=vectors[i].tolist() if vector_store.use_supabase else None
                    )
                    new_chunk_records.append(db_chunk)
                
                db.add_all(new_chunk_records)
                total_text_chunks = len(new_chunk_records)
            
            # 3. Process Images from PDF
            update_task_state(task_self, TaskStatus.PROCESSING, "Analyzing extracted images...", 60.0)
            
            total_visual_chunks = 0
            if image_paths:
                # Create a temp directory for the images
                pdf_image_dir = settings.FRAME_DIR / source_id / "pdf_images"
                pdf_image_dir.mkdir(parents=True, exist_ok=True)
                
                # Analyze images with Gemini
                image_descriptions = analyze_frames_with_gemini(pdf_image_dir)
                
                if image_descriptions:
                    desc_texts = list(image_descriptions.values())
                    image_vectors = embed_service.embed_texts(desc_texts)
                    image_vector_ids = vector_store.add_vectors(image_vectors, file_type='pdf')
                    
                    new_image_chunk_records = []
                    frame_filenames = list(image_descriptions.keys())
                    
                    for i, text in enumerate(desc_texts):
                        frame_filename = frame_filenames[i]
                        
                        # Extract figure IDs from description (Gemini might have put them in brackets)
                        fig_ids = extract_figure_ids(text)
                        
                        # Also check if we can map page number to image path to get page number
                        # (This part is tricky without the page mapping from process_pdf being passed fully)
                        # But we have the filename which usually contains page info if we named it right.
                        # For now, just rely on Gemini's description.
                        
                        db_chunk = TextChunk(
                            document_id=doc.id,
                            vector_id=int(image_vector_ids[i]) if image_vector_ids[i] is not None else None,
                            text_content=text,
                            start_time=0.0,
                            end_time=0.0,
                            chunk_type="image",
                            image_path=str(pdf_image_dir / frame_filename),
                            figure_ids=fig_ids,
                            embedding=image_vectors[i].tolist() if vector_store.use_supabase else None
                        )
                        new_image_chunk_records.append(db_chunk)
                    
                    db.add_all(new_image_chunk_records)
                    total_visual_chunks = len(new_image_chunk_records)
            
            # 4. Finalize
            total_vectors = total_text_chunks + total_visual_chunks
            
            if total_vectors == 0:
                raise Exception("PDF processed but no text or images were extracted/indexed. Check if the PDF is empty or corrupted.")
            
            update_task_state(task_self, TaskStatus.PROCESSING, "Normalizing PDF intelligence...", 95.0)
            norm_service = get_normalization_service()
            intel_record = norm_service.normalize_pdf_output(
                text=raw_text,
                metadata={"image_count": len(image_paths)}
            )
            doc.intelligence_summary = intel_record.json()
            
            artifacts['metadata_count'] = total_vectors
            update_task_state(task_self, TaskStatus.SUCCESS, f"PDF processed successfully. Indexed {total_vectors} chunks.", 100.0)
            doc.status = "completed"
            db.commit()
            vector_store.save_index()
            
            return artifacts
            
        except Exception as e:
            print(f"[Orchestrator] FAILED processing for {source_id}: {e}")
            db.rollback()
            doc.status = "failed"
            db.add(doc)
            db.commit()
            raise