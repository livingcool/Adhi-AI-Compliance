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
        print(f"ðŸ”§ Setting up Supabase Auth user: {email}")
        
        # Create user in Supabase Auth
        response = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True  # Skip email confirmation
        })
        
        user_id = response.user.id
        print(f"âœ… Created Supabase Auth user with ID: {user_id}")
        
        # Update the database user record with the correct Supabase user ID
        result = supabase.table('users').update({
            'id': user_id,
            'email': email
        }).eq('email', 'ganesh@rootedai.co.in').execute()
        
        if result.data:
            print(f"âœ… Updated database user record")
        else:
            # If no existing user, create new one
            supabase.table('users').insert({
                'id': user_id,
                'email': email,
                'name': 'Ganesh Khovalan',
                'role': 'admin',
                'org_id': 'rooted-ai-org'
            }).execute()
            print(f"âœ… Created new database user record")
        
        print(f"\nðŸŽ‰ Authentication setup complete!")
        print(f"ðŸ“§ Email: {email}")
        print(f"ðŸ”‘ Password: {password}")
        print(f"ðŸ‘¤ User ID: {user_id}")
        
        return True
        
    except Exception as e:
        print(f"âŒ Error setting up authentication: {e}")
        return False

def test_login():
    """Test the login functionality"""
    
    supabase_url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not anon_key:
        print("âŒ Supabase configuration missing")
        return False
    
    # Create client with anon key (public access)
    supabase: Client = create_client(supabase_url, anon_key)
    
    try:
        print(f"\nðŸ§ª Testing login...")
        
        # Attempt login
        response = supabase.auth.sign_in_with_password({
            "email": "ganeshkhovalan2203@gmail.com",
            "password": "[REDACTED_PASSWORD]"
        })
        
        if response.user and response.session:
            print(f"âœ… Login successful!")
            print(f"ðŸŽŸï¸ Access Token: {response.session.access_token[:50]}...")
            print(f"ðŸ‘¤ User ID: {response.user.id}")
            return True
        else:
            print(f"âŒ Login failed: No user or session returned")
            return False
            
    except Exception as e:
        print(f"âŒ Login test failed: {e}")
        return False

if __name__ == "__main__":
    print("ðŸš€ Adhi Compliance - Authentication Setup")
    print("=" * 50)
    
    # Setup the auth user
    if setup_supabase_auth():
        # Test the login
        test_login()
    else:
        print("âŒ Authentication setup failed")
