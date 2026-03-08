"""
Quick Supabase API Test
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def quick_test():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    print(f"Testing: {url}")
    
    try:
        response = requests.get(f"{url}/rest/v1/", headers={
            "apikey": key,
            "Authorization": f"Bearer {key}"
        }, timeout=5)
        
        if response.status_code == 200:
            print("[SUCCESS] Supabase API accessible")
            return True
        else:
            print(f"[ERROR] API returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return False

if __name__ == "__main__":
    if quick_test():
        print("\n✅ Connection works!")
        print("Recommended approach: Manual setup in Supabase Dashboard")
        print("See: MANUAL_SETUP_COMPLETE.md")
    else:
        print("\n❌ Network connectivity issues")
        print("All automated approaches are being blocked")
        print("Manual dashboard setup is the only reliable option")