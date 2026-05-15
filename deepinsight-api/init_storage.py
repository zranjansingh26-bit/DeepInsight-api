import asyncio
import logging
from config import get_settings
from db.client import get_service_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_storage():
    settings = get_settings()
    client = get_service_client()
    
    buckets_to_create = [
        settings.supabase_storage_bucket,
        settings.supabase_models_bucket
    ]
    
    try:
        existing_buckets = client.storage.list_buckets()
        existing_names = [b.name for b in existing_buckets]
        
        for bucket_name in buckets_to_create:
            if bucket_name not in existing_names:
                logger.info(f"Creating bucket: {bucket_name}")
                client.storage.create_bucket(bucket_name, options={"public": True})
            else:
                logger.info(f"Bucket already exists: {bucket_name}")
                
    except Exception as e:
        logger.error(f"Error initializing storage: {e}")

if __name__ == "__main__":
    asyncio.run(init_storage())
