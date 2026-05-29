import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.client import get_service_client

async def ensure_profile():
    client = get_service_client()
    uid = "daa28ffc-368b-46bd-b254-3c6a68769f3d"
    
    print(f"Checking profile for user {uid}...")
    try:
        res = client.table("profiles").select("*").eq("id", uid).execute()
        if res.data:
            print("Profile already exists:", res.data)
        else:
            print("Profile does not exist. Creating profile...")
            # We insert a profile record
            insert_res = client.table("profiles").insert({
                "id": uid,
                "display_name": "Ranjan Singh"
            }).execute()
            print("Profile created successfully:", insert_res.data)
    except Exception as e:
        print(f"Error ensuring profile: {e}")

if __name__ == "__main__":
    asyncio.run(ensure_profile())
