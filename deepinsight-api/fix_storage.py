import asyncio
import logging
from config import get_settings
from db.client import get_service_client

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fix_storage():
    settings = get_settings()
    client = get_service_client()
    bucket_name = settings.supabase_storage_bucket
    
    print(f"Target Bucket: {bucket_name}")
    
    try:
        print("Fetching existing buckets...")
        buckets = client.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        print(f"Existing buckets: {bucket_names}")
        
        if bucket_name not in bucket_names:
            print(f"Bucket '{bucket_name}' not found. Attempting to create...")
            # Create bucket with public access for ease of use in this starter suite
            res = client.storage.create_bucket(bucket_name, options={"public": True})
            print(f"Create response: {res}")
            print(f"Successfully created bucket '{bucket_name}'.")
        else:
            print(f"Bucket '{bucket_name}' already exists.")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if "403" in str(e):
            print("Permission denied. Check if your SUPABASE_SERVICE_ROLE_KEY is correct and has storage permissions.")
        elif "401" in str(e):
            print("Unauthorized. Check your SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")

if __name__ == "__main__":
    asyncio.run(fix_storage())
