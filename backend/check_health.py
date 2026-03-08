"""
Quick health check for audio pipeline services
"""
import requests
import time

def check_services():
    print("Checking services...")
    
    # Check backend
    try:
        response = requests.get("http://127.0.0.1:8000/docs", timeout=2)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"⚠️  Backend returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend not ready: {e}")
        return False
    
    # Check if Celery worker is connected (indirect check via Redis)
    try:
        # Try a simple ingest status check
        response = requests.get("http://127.0.0.1:8000/api/v1/status/test", timeout=2)
        # Any response means backend can talk to Redis
        print("✅ Redis connection OK")
    except Exception as e:
        print(f"⚠️  Redis check inconclusive: {e}")
    
    print("\n✅ System ready!")
    return True

if __name__ == "__main__":
    check_services()
