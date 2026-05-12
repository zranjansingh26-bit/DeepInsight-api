
import asyncio
import logging
from db import repository
from db.client import get_service_client

logging.basicConfig(level=logging.INFO)

async def test_insert_session():
    # Use a valid dataset ID from the DB
    client = get_service_client()
    datasets = client.table("datasets").select("id, user_id").limit(1).execute().data
    if not datasets:
        print("No datasets found in DB. Please upload a dataset first.")
        return
    
    dataset_id = datasets[0]["id"]
    user_id = "daa28ffc-368b-46bd-b254-3c6a68769f3d" # The bypass user ID
    
    print(f"Using dataset_id: {dataset_id}")
    print(f"Using user_id: {user_id}")
    
    try:
        session = repository.create_chat_session(
            dataset_id=dataset_id,
            user_id=user_id,
            title="Test Session"
        )
        print("Session created successfully:", session)
    except Exception as e:
        print("Caught exception:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_insert_session())
