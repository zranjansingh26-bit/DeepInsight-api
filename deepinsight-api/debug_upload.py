import asyncio
import os
import pandas as pd
from fastapi import UploadFile
from services import dataset_service
from db.client import get_service_client
import io

async def simulate_upload():
    # Mock UploadFile
    file_path = "test.csv"
    with open(file_path, "rb") as f:
        content = f.read()
    
    # Use the real user ID we found in the database
    user_id = "daa28ffc-368b-46bd-b254-3c6a68769f3d"
    
    class MockFile:
        def __init__(self, filename, content):
            self.filename = filename
            self.content = content
            self.file = io.BytesIO(content)
        async def read(self):
            return self.content
        async def seek(self, pos):
            self.file.seek(pos)
    
    mock_file = MockFile("test.csv", content)
    
    print(f"Simulating upload for {user_id}...")
    try:
        result = await dataset_service.upload_dataset(mock_file, user_id)
        print("Upload SUCCESS:", result)
    except Exception as e:
        print("Upload FAILED!")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simulate_upload())
