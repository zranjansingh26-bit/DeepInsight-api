import asyncio
from db.client import get_service_client

async def check_db():
    client = get_service_client()
    try:
        res = client.table('datasets').select('*').order('created_at', desc=True).limit(5).execute()
        print("Latest Datasets:")
        for ds in res.data:
            print(f"ID: {ds['id']}, Name: {ds['file_name']}, Path: {ds['storage_path']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_db())
