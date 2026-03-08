"""
Setup Adhi Compliance Database via Supabase REST API
More reliable than direct PostgreSQL connections
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def setup_via_supabase_api():
    """Setup database using Supabase REST API"""
    
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not service_key:
        print("[ERROR] Supabase credentials missing")
        return False
    
    print("Adhi Compliance - API-Based Setup")
    print("=" * 40)
    print(f"URL: {supabase_url}")
    
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    try:
        # Test connection
        print("\n[TEST] Testing Supabase API connection...")
        response = requests.get(f"{supabase_url}/rest/v1/", headers=headers, timeout=10)
        if response.status_code == 200:
            print("[SUCCESS] Supabase API connection working")
        else:
            print(f"[ERROR] API test failed: {response.status_code}")
            return False
        
        # Check what tables currently exist
        print("\n[CHECK] Checking existing tables...")
        # We can't easily create tables via REST API, but we can check if they exist
        
        # Try to access ai_systems table
        try:
            response = requests.get(
                f"{supabase_url}/rest/v1/ai_systems?limit=1", 
                headers=headers, 
                timeout=5
            )
            if response.status_code == 200:
                print("[SUCCESS] ai_systems table exists")
                data = response.json()
                print(f"[INFO] Found {len(data)} AI systems")
            elif response.status_code == 404:
                print("[INFO] ai_systems table does not exist - needs to be created via SQL")
            else:
                print(f"[INFO] ai_systems table check: {response.status_code}")
        except Exception as e:
            print(f"[INFO] ai_systems table check failed: {e}")
        
        # Try to access users table  
        try:
            response = requests.get(
                f"{supabase_url}/rest/v1/users?limit=1", 
                headers=headers, 
                timeout=5
            )
            if response.status_code == 200:
                print("[SUCCESS] users table exists")
                data = response.json()
                print(f"[INFO] Found {len(data)} users")
            elif response.status_code == 404:
                print("[INFO] users table does not exist - needs to be created via SQL")
            else:
                print(f"[INFO] users table check: {response.status_code}")
        except Exception as e:
            print(f"[INFO] users table check failed: {e}")
        
        print("\n[CONCLUSION] API connection works!")
        print("The tables need to be created via SQL Editor in Supabase Dashboard.")
        print("REST API can only read/write data, not create schema.")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] API setup failed: {e}")
        return False

def check_auth_user():
    """Check if auth user exists"""
    
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print("\n[AUTH] Checking auth user...")
        
        # Try to get user info via Supabase Auth Admin API
        response = requests.get(
            f"{supabase_url}/auth/v1/admin/users",
            headers=headers,
            params={"filter": "email:eq.ganeshkhovalan2203@gmail.com"},
            timeout=10
        )
        
        if response.status_code == 200:
            users = response.json()
            if users and len(users) > 0:
                user = users[0]
                print(f"[SUCCESS] Auth user found: {user['email']}")
                print(f"[INFO] User ID: {user['id']}")
                print(f"[INFO] Confirmed: {user.get('email_confirmed_at') is not None}")
                return True
            else:
                print("[INFO] Auth user not found")
                print("[ACTION] Create user in Supabase Dashboard: Authentication > Users")
                return False
        else:
            print(f"[ERROR] Auth API check failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Auth user check failed: {e}")
        return False

if __name__ == "__main__":
    if setup_via_supabase_api():
        check_auth_user()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("1. Go to Supabase Dashboard SQL Editor")
    print("2. Run the 3 SQL files in order:")
    print("   - backend/supabase_schema_fixed.sql")
    print("   - backend/supabase_tables_uuid.sql")  
    print("   - backend/supabase_seed_data_uuid.sql")
    print("3. Create auth user if not exists")
    print("4. Test: py test_auth_simple.py")
    print("=" * 60)