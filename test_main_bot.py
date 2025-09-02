import requests
from datetime import datetime, timedelta, UTC

# Import your main bot functions
from app import send_message, fetch_jobs, send_daily_digest

def test_main_bot():
    print("Testing main bot functions...")
    
    # Test 1: Send a direct message
    print("\n1. Testing direct message...")
    try:
        send_message("🧪 Test message from main bot! This should work.")
        print("✅ Direct message sent successfully!")
    except Exception as e:
        print(f"❌ Direct message failed: {e}")
    
    # Test 2: Fetch jobs
    print("\n2. Testing job fetching...")
    try:
        fetch_jobs()
        print("✅ Jobs fetched successfully!")
    except Exception as e:
        print(f"❌ Job fetching failed: {e}")
    
    # Test 3: Force daily digest
    print("\n3. Testing daily digest...")
    try:
        send_daily_digest()
        print("✅ Daily digest sent successfully!")
    except Exception as e:
        print(f"❌ Daily digest failed: {e}")

if __name__ == "__main__":
    test_main_bot()
