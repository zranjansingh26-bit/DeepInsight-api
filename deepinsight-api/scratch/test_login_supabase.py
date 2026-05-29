import sys
import os
import asyncio
import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_settings

async def test_direct_login():
    settings = get_settings()
    email = "zranjansingh26@gmail.com"
    # We will test login with a dummy password to see the error details
    password = "wrong-password"
    
    print(f"Testing authentication with Supabase URL: {settings.supabase_url}")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.supabase_url}/auth/v1/token?grant_type=password",
                json={
                    "email": email,
                    "password": password,
                },
                headers={
                    "apikey": settings.supabase_anon_key,
                    "Content-Type": "application/json",
                },
                timeout=15.0,
            )
        print(f"Status Code: {resp.status_code}")
        print(f"Response Headers: {dict(resp.headers)}")
        print(f"Response JSON: {resp.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_direct_login())
