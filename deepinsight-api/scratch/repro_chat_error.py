
import asyncio
import logging
from services import chat_service
from db.client import get_service_client

logging.basicConfig(level=logging.INFO)

async def test_create_session():
    dataset_id = "string"
    user_id = "test-user"
    title = "Test Session"
    
    try:
        print(f"Attempting to create session for dataset_id: {dataset_id}")
        session = await chat_service.create_session(dataset_id, user_id, title)
        print("Session created successfully:", session)
    except ValueError as e:
        print("Caught expected ValueError:", e)
    except Exception as e:
        print("Caught unexpected exception:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_create_session())
