import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.client import get_service_client

async def reset_password():
    client = get_service_client()
    uid = "daa28ffc-368b-46bd-b254-3c6a68769f3d"
    new_password = "password123"
    
    print(f"Attempting to reset password for user {uid} to '{new_password}'...")
    try:
        # Check client.auth.admin methods
        # Try both supabase-py v2 styles
        # Direct dictionary update or attributes model
        try:
            res = client.auth.admin.update_user_by_id(uid, {"password": new_password})
            print("Successfully updated using dict: ", res)
        except Exception as e1:
            print(f"Failed with dict: {e1}")
            print("Trying with AdminUserAttributes...")
            from gotrue.models import AdminUserAttributes
            attrs = AdminUserAttributes(password=new_password)
            res = client.auth.admin.update_user_by_id(uid, attributes=attrs)
            print("Successfully updated using AdminUserAttributes: ", res)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(reset_password())
