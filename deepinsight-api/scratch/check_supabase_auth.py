import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.client import get_service_client

async def list_auth_users():
    client = get_service_client()
    try:
        # Supabase auth.admin.list_users() is available on supabase python client
        users = client.auth.admin.list_users()
        print("AUTH USERS IN SUPABASE:")
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Created At: {user.created_at}, Confirmed At: {user.confirmed_at}")
    except Exception as e:
        print(f"Error listing auth users: {e}")

if __name__ == "__main__":
    asyncio.run(list_auth_users())
