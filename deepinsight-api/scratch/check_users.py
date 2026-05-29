import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.client import get_service_client

async def list_users():
    client = get_service_client()
    try:
        res = client.table("profiles").select("*").execute()
        print("PROFILES IN DB:")
        for profile in res.data:
            print(profile)
    except Exception as e:
        print(f"Error listing profiles: {e}")

if __name__ == "__main__":
    asyncio.run(list_users())
