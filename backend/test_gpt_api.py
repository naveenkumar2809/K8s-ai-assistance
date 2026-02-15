"""
Test script to verify GPT-5 Nano API connection
"""
import httpx
import asyncio
import json

API_KEY = "euri-94cdcc6563a978b4319b0ba3d4c6582edf5394006ce71c2b88545920bc699f2c"
MODEL = "gpt-5-nano"

# Common API endpoints to try
ENDPOINTS = {
    "OpenAI": "https://api.openai.com/v1/chat/completions",
    "Custom (Euri)": "https://api.euri.ai/v1/chat/completions",  # Guessing based on key prefix
    "Azure OpenAI": "https://YOUR_RESOURCE.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT/chat/completions?api-version=2023-05-15",
}

async def test_endpoint(name, url):
    """Test a specific API endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, test successful!'"}
        ],
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS!")
                print(f"Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"❌ FAILED")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        return False

async def main():
    print("GPT-5 Nano API Connection Test")
    print(f"API Key: {API_KEY[:20]}...{API_KEY[-10:]}")
    print(f"Model: {MODEL}")
    
    # Test OpenAI endpoint first
    success = await test_endpoint("OpenAI", ENDPOINTS["OpenAI"])
    
    if not success:
        print("\n⚠️  OpenAI endpoint failed. This is expected if you're using a custom provider.")
        print("\nPlease provide the correct API endpoint URL for your GPT-5 Nano service.")
        print("\nCommon patterns:")
        print("  - https://api.yourprovider.com/v1/chat/completions")
        print("  - https://api.euri.ai/v1/chat/completions")
        print("  - Custom self-hosted endpoint")

if __name__ == "__main__":
    asyncio.run(main())
