from db.client import get_service_client
import logging

logging.basicConfig(level=logging.INFO)

def create_datasets_bucket():
    client = get_service_client()
    try:
        # Check if it already exists
        buckets = client.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        
        if 'datasets' in bucket_names:
            print("Bucket 'datasets' already exists.")
            return

        print("Creating bucket 'datasets'...")
        client.storage.create_bucket('datasets', options={'public': False})
        print("Bucket 'datasets' created successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_datasets_bucket()
