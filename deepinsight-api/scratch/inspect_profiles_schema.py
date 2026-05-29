import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.client import get_service_client

async def inspect_profiles():
    client = get_service_client()
    try:
        # We can run a query to get table info or just query profiles table
        res = client.table("profiles").select("*").limit(1).execute()
        print("Profiles schema query executed successfully.")
        print(f"Data: {res.data}")
        # To get actual columns we can try to insert a dummy record and catch the error, or query postgrest/swagger if available,
        # or just inspect what keys are in res.data if any row existed.
        # But let's check if there is an error when querying specific fields:
        test_fields = ["id", "display_name", "subscription_plan", "subscription_status", "trial_end", "role", "last_login"]
        for field in test_fields:
            try:
                r = client.table("profiles").select(field).limit(1).execute()
                print(f"Field '{field}' exists.")
            except Exception as fe:
                print(f"Field '{field}' does NOT exist: {fe}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(inspect_profiles())
