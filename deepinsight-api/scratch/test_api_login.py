import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

def test_login():
    client = TestClient(app)
    payload = {
        "email": "zranjansingh26@gmail.com",
        "password": "password123"
    }
    print("Sending login request to FastAPI app...")
    response = client.post("/api/auth/login", json=payload)
    print("Status Code:", response.status_code)
    print("JSON Response:", response.json())

if __name__ == "__main__":
    test_login()
