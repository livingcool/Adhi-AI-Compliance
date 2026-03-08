"""
Final Authentication Test for Adhi Compliance
Run this after creating the user in Supabase Dashboard
"""
import requests
import json

def test_authentication():
    """Test authentication with the API"""
    
    # API endpoint
    login_url = "http://localhost:8000/api/v1/auth/login"
    
    # Credentials
    credentials = {
        "email": "ganeshkhovalan2203@gmail.com",
        "password": "[REDACTED_PASSWORD]"
    }
    
    print("Testing Adhi Compliance Authentication")
    print("=" * 50)
    print(f"Email: {credentials['email']}")
    print(f"Password: {'*' * len(credentials['password'])}")
    
    try:
        print("\n[INFO] Attempting login...")
        
        response = requests.post(
            login_url,
            json=credentials,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("[SUCCESS] Login successful!")
            print(f"Access Token: {data['access_token'][:50]}...")
            print(f"Token Type: {data['token_type']}")
            print(f"Expires In: {data.get('expires_in', 'Not specified')} seconds")
            
            # Test protected endpoint
            test_protected_endpoint(data['access_token'])
            
        else:
            print(f"[ERROR] Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out. Check if backend server is running.")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to API. Check if backend server is running on port 8000.")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

def test_protected_endpoint(access_token):
    """Test a protected endpoint with the access token"""
    
    print("\n[INFO] Testing protected endpoint...")
    
    try:
        response = requests.get(
            "http://localhost:8000/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print("[SUCCESS] Protected endpoint accessible!")
            print(f"User ID: {user_data.get('id', 'N/A')}")
            print(f"Name: {user_data.get('name', 'N/A')}")
            print(f"Role: {user_data.get('role', 'N/A')}")
            print(f"Organization: {user_data.get('org_id', 'N/A')}")
            return True
        else:
            print(f"[ERROR] Protected endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Protected endpoint test failed: {e}")
        return False

if __name__ == "__main__":
    test_authentication()
