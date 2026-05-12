
import asyncio
from db.client import get_service_client

async def check_tables():
    client = get_service_client()
    tables = ["datasets", "chat_sessions", "chat_messages", "analysis_results"]
    for table in tables:
        try:
            result = client.table(table).select("id").limit(1).execute()
            print(f"Table '{table}' exists. Rows: {len(result.data)}")
        except Exception as e:
            print(f"Table '{table}' error: {e}")

if __name__ == "__main__":
    asyncio.run(check_tables())
