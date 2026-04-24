# Test script for URL extraction feature
import requests
import json

# Test URL
test_url = "https://www.amazon.in/Apple-iPhone-15-128-GB/dp/B0CHX1W1XY"

print("Testing URL Extraction API...")
print(f"Test URL: {test_url}\n")

try:
    # Call the API
    response = requests.post(
        "http://localhost:8000/api/extract-url",
        json={"url": test_url}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS!")
        print(f"\nPlatform: {data.get('platform')}")
        print(f"\nExtracted Data:")
        print(f"  Title: {data['data']['title'][:100]}...")
        print(f"  Description length: {len(data['data']['description'])} chars")
        print(f"  First 200 chars: {data['data']['description'][:200]}...")
        print(f"\n  Features: {len(data['data'].get('features', []))} found")
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ ERROR: Cannot connect to server.")
    print("Make sure the backend server is running:")
    print("  cd backend")
    print("  python -m uvicorn main:app --reload --port 8000")
except Exception as e:
    print(f"❌ ERROR: {e}")
