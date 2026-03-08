"""
Simple Authentication Test - No Unicode
"""
import requests

def test_auth():
    """Test authentication"""
    try:
        # Check server
        response = requests.get("http://localhost:8000/", timeout=5)
        print("[OK] Backend server running")
        
        # Test login
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json={
                "email": "ganeshkhovalan2203@gmail.com",
                "password": "[REDACTED_PASSWORD]"
            },
            timeout=10
        )
        
        if login_response.status_code == 200:
            print("[SUCCESS] Authentication working!")
            data = login_response.json()
            print(f"Token: {data['access_token'][:30]}...")
            return True
        else:
            print(f"[PENDING] Login failed: {login_response.status_code}")
            print("Need to create user in Supabase Dashboard first")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Backend server not running")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    test_auth()
