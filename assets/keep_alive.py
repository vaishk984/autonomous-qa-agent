"""Keep the Render service alive by pinging it every 10 minutes."""
import requests
import time
import os
from datetime import datetime

BACKEND_URL = os.getenv("BACKEND_URL", "https://qa-agent-backend-s7bb.onrender.com")
PING_INTERVAL = 600  # 10 minutes in seconds

def ping_backend():
    """Ping the backend to keep it awake."""
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if response.status_code == 200:
            print(f"[{timestamp}] ✓ Backend is alive")
            return True
        else:
            print(f"[{timestamp}] ⚠ Backend returned {response.status_code}")
            return False
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] ✗ Ping failed: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"Keep-Alive Service Started")
    print(f"Pinging: {BACKEND_URL}")
    print(f"Interval: {PING_INTERVAL}s ({PING_INTERVAL/60} minutes)")
    print("-" * 50)
    
    while True:
        ping_backend()
        time.sleep(PING_INTERVAL)