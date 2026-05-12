import asyncio
from config import get_settings
from db.client import get_service_client

async def test():
    settings = get_settings()
    client = get_service_client()
    
    print("Testing DB connection...")
    try:
        res = client.table("datasets").select("id").limit(1).execute()
        print("DB OK:", res.data)
    except Exception as e:
        print("DB ERROR:", e)
        
    print(f"Testing Storage bucket '{settings.supabase_storage_bucket}'...")
    try:
        res = client.storage.from_(settings.supabase_storage_bucket).list()
        print("Storage OK:", res)
    except Exception as e:
        print("Storage ERROR:", e)

if __name__ == "__main__":
    asyncio.run(test())
