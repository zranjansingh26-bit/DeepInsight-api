import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import pandas as pd
from db.client import get_service_client
from services.dataset_service import get_dataset, get_dataframe

async def main():
    client = get_service_client()
    res = client.table('datasets').select('*').order('created_at', desc=True).limit(5).execute()
    print("Latest datasets in DB:")
    for row in res.data:
        print(f"ID: {row['id']}, Name: {row['file_name']}, Columns: {[c['name'] for c in row['column_metadata']]}")

if __name__ == "__main__":
    asyncio.run(main())
