"""
Network Diagnostic Tool for Supabase Connection Issues
"""
import socket
import requests
import os
from dotenv import load_dotenv
import subprocess
import platform

load_dotenv()

def test_basic_connectivity():
    """Test basic internet connectivity"""
    print("=== BASIC CONNECTIVITY TEST ===")
    
    try:
        # Test basic internet
        response = requests.get("https://httpbin.org/ip", timeout=5)
        if response.status_code == 200:
            ip_info = response.json()
            print(f"[OK] Internet working - Your IP: {ip_info['origin']}")
            return True
        else:
            print("[ERROR] Internet connectivity issue")
            return False
    except Exception as e:
        print(f"[ERROR] No internet connection: {e}")
        return False

def test_dns_resolution():
    """Test DNS resolution for Supabase"""
    print("\n=== DNS RESOLUTION TEST ===")
    
    domains = [
        "supabase.co",
        "[REDACTED_PROJECT_ID].supabase.co"
    ]
    
    for domain in domains:
        try:
            ip = socket.gethostbyname(domain)
            print(f"[OK] {domain} -> {ip}")
        except Exception as e:
            print(f"[ERROR] Failed to resolve {domain}: {e}")
            return False
    
    return True

def test_port_connectivity():
    """Test if specific ports are accessible"""
    print("\n=== PORT CONNECTIVITY TEST ===")
    
    host = "[REDACTED_PROJECT_ID].supabase.co"
    ports = [443, 5432]  # HTTPS and PostgreSQL
    
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            if result == 0:
                print(f"[OK] Port {port} accessible")
            else:
                print(f"[BLOCKED] Port {port} blocked/filtered")
            sock.close()
        except Exception as e:
            print(f"[ERROR] Port {port} test failed: {e}")

def test_supabase_api():
    """Test Supabase API accessibility"""
    print("\n=== SUPABASE API TEST ===")
    
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not service_key:
        print("[ERROR] Supabase credentials missing")
        return False
    
    endpoints = [
        f"{supabase_url}/",
        f"{supabase_url}/rest/v1/",
        f"{supabase_url}/auth/v1/settings"
    ]
    
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}"
    }
    
    for endpoint in endpoints:
        try:
            print(f"Testing: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=5)
            print(f"[{response.status_code}] Response time: {response.elapsed.total_seconds():.2f}s")
            
            if response.status_code == 200:
                print("[OK] Endpoint accessible")
            else:
                print(f"[WARNING] HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("[TIMEOUT] Request timed out after 5 seconds")
        except requests.exceptions.ConnectionError:
            print("[BLOCKED] Connection refused/blocked")
        except Exception as e:
            print(f"[ERROR] {e}")

def check_firewall_status():
    """Check Windows Firewall status"""
    print("\n=== FIREWALL STATUS ===")
    
    if platform.system() == "Windows":
        try:
            # Check Windows Firewall
            result = subprocess.run(
                ["netsh", "advfirewall", "show", "allprofiles", "state"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if "ON" in result.stdout:
                print("[INFO] Windows Firewall is enabled")
            else:
                print("[INFO] Windows Firewall is disabled")
                
        except Exception as e:
            print(f"[ERROR] Could not check firewall: {e}")
    else:
        print("[INFO] Not Windows - firewall check skipped")

def suggest_solutions():
    """Suggest solutions based on test results"""
    print("\n=== RECOMMENDED SOLUTIONS ===")
    print("1. ðŸ“± MOBILE HOTSPOT (Most Effective):")
    print("   - Enable hotspot on your phone")
    print("   - Connect laptop to phone WiFi")
    print("   - Retry the setup scripts")
    print()
    print("2. ðŸŒ BROWSER-BASED SETUP (100% Reliable):")
    print("   - Use Supabase Dashboard directly")
    print("   - Follow: MANUAL_SETUP_COMPLETE.md")
    print("   - Copy-paste SQL scripts")
    print()
    print("3. ðŸ›¡ï¸ VPN/PROXY:")
    print("   - Use VPN to change your IP/location")
    print("   - Try different VPN servers")
    print()
    print("4. ðŸ”§ NETWORK FIXES:")
    print("   - Change DNS to 8.8.8.8 or 1.1.1.1")
    print("   - Temporarily disable firewall")
    print("   - Try different network location")

def main():
    """Run complete diagnostic"""
    print("ADHI COMPLIANCE - NETWORK DIAGNOSTIC TOOL")
    print("=" * 50)
    
    # Run all tests
    tests = [
        test_basic_connectivity,
        test_dns_resolution,
        test_port_connectivity,
        test_supabase_api,
        check_firewall_status
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"[ERROR] Test failed: {e}")
    
    # Provide solutions
    suggest_solutions()

if __name__ == "__main__":
    main()
