import asyncio
import httpx
from config import get_settings

async def check_supabase_health():
    settings = get_settings()
    url = f"{settings.supabase_url}/rest/v1/"
    headers = {
        "apikey": settings.supabase_anon_key,
        "Authorization": f"Bearer {settings.supabase_anon_key}"
    }
    
    print(f"Checking Supabase health at {url}...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"FAILED to reach Supabase: {e}")

if __name__ == "__main__":
    asyncio.run(check_supabase_health())
