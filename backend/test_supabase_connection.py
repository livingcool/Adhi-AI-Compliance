"""
Test Supabase Connection
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def test_supabase_connection():
    """Test basic Supabase connection"""
    
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    print(f"SUPABASE_URL: {supabase_url}")
    print(f"SERVICE_ROLE_KEY: {service_role_key[:20]}..." if service_role_key else "SERVICE_ROLE_KEY: Not set")
    
    if not supabase_url or not service_role_key:
        print("[ERROR] Supabase configuration missing")
        return False
    
    try:
        print("[INFO] Testing Supabase connection...")
        supabase: Client = create_client(supabase_url, service_role_key)
        
        # Try a simple query
        result = supabase.table('users').select('id, email').limit(1).execute()
        
        print("[SUCCESS] Supabase connection successful!")
        print(f"Sample data: {result.data}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Supabase connection failed: {e}")
        return False

if __name__ == "__main__":
    test_supabase_connection()