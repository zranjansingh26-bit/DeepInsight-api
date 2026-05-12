
import asyncio
import logging
from fastapi import HTTPException
from models.schemas import ChatSessionCreate, UserContext
from services import chat_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def simulate_api_call():
    request = ChatSessionCreate(dataset_id="string", title="string")
    user = UserContext(user_id="daa28ffc-368b-46bd-b254-3c6a68769f3d", email="researcher@local.dev")
    
    print("Simulating POST /api/chat/sessions with dataset_id='string'")
    try:
        session = await chat_service.create_session(
            dataset_id=request.dataset_id,
            user_id=user.user_id,
            title=request.title,
        )
        print("Success:", session)
    except ValueError as e:
        print("Caught ValueError (Expected for invalid ID):", e)
        # This would result in 404
    except Exception as e:
        print("Caught unexpected Exception (This results in 500):")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simulate_api_call())
