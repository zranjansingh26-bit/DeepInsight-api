import asyncio
from config import get_settings
from db.client import get_service_client

async def list_buckets():
    settings = get_settings()
    client = get_service_client()
    
    print(f"Current Config URL: {settings.supabase_url}")
    print(f"Target Bucket in Config: {settings.supabase_storage_bucket}")
    
    try:
        buckets = client.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        print(f"Buckets existing in this project: {bucket_names}")
    except Exception as e:
        print(f"Error listing buckets: {e}")

if __name__ == "__main__":
    asyncio.run(list_buckets())
