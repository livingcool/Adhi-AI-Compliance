"""
Quick Authentication Test - Run after Supabase Dashboard Setup
"""
import requests
import json

def test_auth_quick():
    """Quick test of authentication setup"""
    
    print("=== QUICK AUTHENTICATION TEST ===")
    print("Run this AFTER completing Supabase Dashboard setup")
    print("")
    
    # Test data
    login_url = "http://localhost:8000/api/v1/auth/login"
    credentials = {
        "email": "ganeshkhovalan2203@gmail.com",
        "password": "[REDACTED_PASSWORD]"
    }
    
    try:
        print("ðŸ§ª Testing login...")
        response = requests.post(login_url, json=credentials, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("âœ… SUCCESS! Authentication working!")
            print(f"   Token: {data['access_token'][:30]}...")
            print(f"   Type: {data['token_type']}")
            
            # Test user profile
            print("\nðŸ§ª Testing user profile...")
            profile_response = requests.get(
                "http://localhost:8000/api/v1/auth/me",
                headers={"Authorization": f"Bearer {data['access_token']}"},
                timeout=10
            )
            
            if profile_response.status_code == 200:
                user_data = profile_response.json()
                print("âœ… User profile accessible!")
                print(f"   Name: {user_data.get('name', 'N/A')}")
                print(f"   Role: {user_data.get('role', 'N/A')}")
                print(f"   Email: {user_data.get('email', 'N/A')}")
                
                print("\nðŸŽ‰ ALL TESTS PASSED!")
                print("ðŸš€ Ready for production!")
                return True
            else:
                print(f"âŒ Profile test failed: {profile_response.status_code}")
                return False
                
        else:
            print(f"âŒ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 401:
                print("\nðŸ’¡ SOLUTION:")
                print("   1. Go to Supabase Dashboard")
                print("   2. Create auth user: ganeshkhovalan2203@gmail.com")
                print("   3. Update database user email")
                print("   4. Run this test again")
            
            return False
            
    except requests.exceptions.ConnectionError:
        print("âŒ Cannot connect to API")
        print("ðŸ’¡ Make sure backend server is running: py -m uvicorn app.main:app --reload --port 8000")
        return False
    except Exception as e:
        print(f"âŒ Error: {e}")
        return False

def check_server():
    """Check if backend server is running"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("âœ… Backend server is running")
            return True
        else:
            print("âš ï¸  Backend server responding but with error")
            return False
    except:
        print("âŒ Backend server is NOT running")
        print("ðŸ’¡ Start it with: py -m uvicorn app.main:app --reload --port 8000")
        return False

if __name__ == "__main__":
    print("Backend Server Check:")
    if check_server():
        print("\nAuthentication Test:")
        test_auth_quick()
    else:
        print("âŒ Cannot proceed without backend server")
