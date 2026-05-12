import asyncio
import logging
import pandas as pd
from config import get_settings
from db import repository
from services.dataset_service import get_dataset, get_dataframe
from services.llm_client import chat_completion
from engines.context_builder import build_context, build_system_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_flow():
    # 1. Get latest dataset
    datasets = repository.list_datasets("daa28ffc-368b-46bd-b254-3c6a68769f3d") # Use the ID from logs
    if not datasets:
        print("No datasets found for user.")
        return
    
    dataset = datasets[0]
    print(f"Testing with dataset: {dataset['file_name']} (ID: {dataset['id']})")
    print(f"Storage Path: {dataset['storage_path']}")
    
    # 2. Try to get dataframe
    try:
        print("Downloading dataframe...")
        df = get_dataframe(dataset)
        print(f"Dataframe loaded: {len(df)} rows")
    except Exception as e:
        print(f"ERROR downloading dataframe: {e}")
        return

    # 3. Build context
    try:
        print("Building context...")
        context = build_context(df, dataset)
        system_prompt = build_system_prompt(context)
        print("Context built successfully.")
    except Exception as e:
        print(f"ERROR building context: {e}")
        return

    # 4. Test AI
    try:
        print("Calling AI...")
        response = await chat_completion(
            system_prompt=system_prompt,
            user_message="Summarize this data.",
        )
        print("AI Response Success!")
        print(f"Answer: {response.answer[:100]}...")
    except Exception as e:
        print(f"ERROR calling AI: {e}")

if __name__ == "__main__":
    asyncio.run(test_flow())
