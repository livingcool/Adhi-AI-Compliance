"""
Setup Supabase Auth User for Adhi Compliance Platform
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_supabase_auth():
    """Create Supabase Auth user and update database"""
    
    # Supabase configuration
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not service_role_key:
        print("[ERROR] Supabase configuration missing in .env file")
        return False
    
    # Create Supabase client with service role (admin privileges)
    supabase: Client = create_client(supabase_url, service_role_key)
    
    # User credentials
    email = "ganeshkhovalan2203@gmail.com"
    password = "[REDACTED_PASSWORD]"
    
    try:
        print(f"[INFO] Setting up Supabase Auth user: {email}")
        
        # Create user in Supabase Auth
        response = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True  # Skip email confirmation
        })
        
        user_id = response.user.id
        print(f"[SUCCESS] Created Supabase Auth user with ID: {user_id}")
        
        # Update the database user record with the correct Supabase user ID
        result = supabase.table('users').update({
            'id': user_id,
            'email': email
        }).eq('email', 'ganesh@rootedai.co.in').execute()
        
        if result.data:
            print(f"[SUCCESS] Updated database user record")
        else:
            # If no existing user, create new one
            supabase.table('users').insert({
                'id': user_id,
                'email': email,
                'name': 'Ganesh Khovalan',
                'role': 'admin',
                'org_id': 'rooted-ai-org'
            }).execute()
            print(f"[SUCCESS] Created new database user record")
        
        print(f"\n[COMPLETE] Authentication setup complete!")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"User ID: {user_id}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error setting up authentication: {e}")
        return False

def test_login():
    """Test the login functionality"""
    
    supabase_url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not anon_key:
        print("[ERROR] Supabase configuration missing")
        return False
    
    # Create client with anon key (public access)
    supabase: Client = create_client(supabase_url, anon_key)
    
    try:
        print(f"\n[TEST] Testing login...")
        
        # Attempt login
        response = supabase.auth.sign_in_with_password({
            "email": "ganeshkhovalan2203@gmail.com",
            "password": "[REDACTED_PASSWORD]"
        })
        
        if response.user and response.session:
            print(f"[SUCCESS] Login successful!")
            print(f"Access Token: {response.session.access_token[:50]}...")
            print(f"User ID: {response.user.id}")
            return True
        else:
            print(f"[ERROR] Login failed: No user or session returned")
            return False
            
    except Exception as e:
        print(f"[ERROR] Login test failed: {e}")
        return False

if __name__ == "__main__":
    print("Adhi Compliance - Authentication Setup")
    print("=" * 50)
    
    # Setup the auth user
    if setup_supabase_auth():
        # Test the login
        test_login()
    else:
        print("[ERROR] Authentication setup failed")
