from db.client import get_service_client
print("Initializing client...")
client = get_service_client()
print("Client initialized.")
try:
    print("Testing connection with simple query...")
    # Using a simple RPC or health check if possible, or just a table check
    res = client.table('datasets').select('count', count='exact').limit(0).execute()
    print(f"Connection SUCCESS: {res}")
except Exception as e:
    print(f"Connection FAILED: {e}")
