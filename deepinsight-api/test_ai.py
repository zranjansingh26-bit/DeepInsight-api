import asyncio
import logging
from services.llm_client import chat_completion
from config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_ai():
    settings = get_settings()
    print(f"Testing AI connection...")
    print(f"Has Anthropic Key: {settings.has_anthropic}")
    print(f"Has OpenAI Key: {settings.has_openai}")
    
    try:
        response = await chat_completion(
            system_prompt="You are a helpful assistant.",
            user_message="Hello, are you working?",
        )
        print("AI Response Success!")
        print(f"Answer: {response.answer}")
    except Exception as e:
        print(f"AI Response ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_ai())
