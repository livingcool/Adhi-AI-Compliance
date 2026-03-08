import os
from datetime import datetime
from typing import Optional
from supabase import create_client, Client

# Initialize Supabase Client (Lazy or Global)
# We use environment variables directly or from config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") # Use Service Role for logging/admin tasks if possible, else Anon

_supabase: Optional[Client] = None

def get_supabase() -> Optional[Client]:
    global _supabase
    if _supabase:
        return _supabase
    
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            return _supabase
        except Exception as e:
            print(f"[LOGGING] Failed to init Supabase: {e}")
            return None
    return None

def log_ai_usage(
    query_id: str,
    query_text: str,
    response_text: str,
    model_name: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    user_id: Optional[str] = None,
    org_id: Optional[str] = None,
    service_name: str = "general_qa"
):
    """
    Logs AI usage metrics to the 'ai_usage_logs' table in Supabase.
    """
    client = get_supabase()
    if not client:
        print(f"[LOGGING] Skipped log for {query_id} (No Supabase connection)")
        return

    try:
        data = {
            "query_id": query_id,
            "user_id": user_id,
            "org_id": org_id,
            "model_name": model_name,
            "service_name": service_name,
            "prompt_tokens": int(float(prompt_tokens)),
            "completion_tokens": int(float(completion_tokens)),
            "total_tokens": int(float(total_tokens)),
            "created_at": datetime.utcnow().isoformat(),
            # Optional: Log snippets for debugging (truncate to save space/privacy if needed)
            "meta": {
                "query_snippet": query_text[:100],
                "response_len": len(response_text)
            }
        }
        
        # Async-like fire and forget usually requires a task queue, 
        # but for now we run blocking or rely on fast Supabase inserts.
        client.table("ai_usage_logs").insert(data).execute()
        print(f"[LOGGING] Logged usage for {query_id}: {total_tokens} tokens ({model_name})")

    except Exception as e:
        print(f"[LOGGING] Error inserting log: {e}")

def log_service_event(
    service_name: str,
    event_type: str,
    details: dict,
    org_id: Optional[str] = None
):
    """
    Logs general service events (e.g. "ingestion_start", "client_created").
    """
    client = get_supabase()
    if not client:
        return

    try:
        data = {
            "service_name": service_name,
            "event_type": event_type,
            "org_id": org_id,
            "details": details,
            "created_at": datetime.utcnow().isoformat()
        }
        client.table("service_logs").insert(data).execute()
        print(f"[LOGGING] Service Event: {service_name} -> {event_type}")

    except Exception as e:
        print(f"[LOGGING] Error logging service event: {e}")
