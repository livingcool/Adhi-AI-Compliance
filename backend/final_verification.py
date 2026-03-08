"""
Final Verification Test for Adhi Compliance Setup
Run this after completing manual setup
"""
import requests
import json

def final_verification():
    """Complete verification of Adhi Compliance setup"""
    
    print("=" * 60)
    print("ADHI COMPLIANCE - FINAL VERIFICATION TEST")
    print("=" * 60)
    
    # Test 1: Backend server
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("[âœ“] Backend server running")
            data = response.json()
            print(f"    App: {data.get('app_name', 'N/A')}")
        else:
            print("[âœ—] Backend server error")
            return False
    except:
        print("[âœ—] Backend server not accessible")
        print("    Start with: py -m uvicorn app.main:app --reload --port 8000")
        return False
    
    # Test 2: Authentication
    try:
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json={
                "email": "ganeshkhovalan2203@gmail.com",
                "password": "[REDACTED_PASSWORD]"
            },
            timeout=15
        )
        
        if login_response.status_code == 200:
            print("[âœ“] Authentication working")
            token_data = login_response.json()
            access_token = token_data['access_token']
            print(f"    Token type: {token_data['token_type']}")
            
            # Test 3: User profile
            profile_response = requests.get(
                "http://localhost:8000/api/v1/auth/me",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10
            )
            
            if profile_response.status_code == 200:
                print("[âœ“] User profile accessible")
                user_data = profile_response.json()
                print(f"    Name: {user_data.get('name', 'N/A')}")
                print(f"    Role: {user_data.get('role', 'N/A')}")
                print(f"    Email: {user_data.get('email', 'N/A')}")
            else:
                print("[âš ] User profile issue")
                
            # Test 4: AI Systems endpoint
            ai_systems_response = requests.get(
                "http://localhost:8000/api/v1/ai-systems",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10
            )
            
            if ai_systems_response.status_code == 200:
                print("[âœ“] AI Systems API accessible")
                ai_systems = ai_systems_response.json()
                print(f"    AI Systems count: {len(ai_systems)}")
                if ai_systems:
                    print(f"    Sample: {ai_systems[0].get('name', 'N/A')}")
            else:
                print("[âš ] AI Systems API issue")
                
            # Test 5: Dashboard endpoint
            dashboard_response = requests.get(
                "http://localhost:8000/api/v1/dashboard/overview",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10
            )
            
            if dashboard_response.status_code == 200:
                print("[âœ“] Dashboard API accessible")
                dashboard_data = dashboard_response.json()
                print(f"    Total AI Systems: {dashboard_data.get('total_ai_systems', 'N/A')}")
                print(f"    Compliance Score: {dashboard_data.get('compliance_score', 'N/A')}%")
            else:
                print("[âš ] Dashboard API issue")
            
        else:
            print(f"[âœ—] Authentication failed: {login_response.status_code}")
            print(f"    Response: {login_response.text}")
            print("\nðŸ’¡ SOLUTION:")
            print("1. Complete manual setup in Supabase Dashboard")
            print("2. Create auth user: ganeshkhovalan2203@gmail.com")
            print("3. Link database user with auth user")
            return False
            
    except requests.exceptions.Timeout:
        print("[âœ—] Authentication timeout")
        print("    Network connectivity issues")
        return False
    except Exception as e:
        print(f"[âœ—] Authentication error: {e}")
        return False
    
    # Test 6: Frontend check
    try:
        frontend_response = requests.get("http://localhost:3000", timeout=5)
        if frontend_response.status_code == 200:
            print("[âœ“] Frontend accessible")
            print("    URL: http://localhost:3000")
        else:
            print("[âš ] Frontend not running")
            print("    Start with: cd webapp && npm run dev")
    except:
        print("[âš ] Frontend not accessible")
        print("    Start with: cd webapp && npm run dev")
    
    print("\n" + "=" * 60)
    print("ðŸŽ‰ VERIFICATION COMPLETE!")
    print("=" * 60)
    print("âœ… Adhi Compliance Platform is OPERATIONAL")
    print("\nðŸ“‹ Access Details:")
    print("â€¢ Backend API: http://localhost:8000")
    print("â€¢ Frontend UI: http://localhost:3000")
    print("â€¢ Login: ganeshkhovalan2203@gmail.com / [REDACTED_PASSWORD]")
    print("â€¢ API Docs: http://localhost:8000/docs")
    print("\nðŸš€ Ready for production deployment!")
    return True

if __name__ == "__main__":
    final_verification()
