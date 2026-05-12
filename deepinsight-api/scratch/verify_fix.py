
import io
import pandas as pd
import logging
from engines.file_parser import parse_bytes

logging.basicConfig(level=logging.INFO)

def test_latin1_csv():
    # Create a CSV with latin-1 characters (e.g., accent marks)
    # '©' is \xa9 in latin-1
    content = b"id,name,value\n1,test\xa9,10"
    
    print("Testing latin-1 encoded CSV parsing...")
    try:
        df = parse_bytes(content, "csv")
        print("Success! Parsed DataFrame:")
        print(df)
        assert df.iloc[0, 1] == "test\xa9" or df.iloc[0, 1] == "test©"
    except Exception as e:
        print(f"Failed: {e}")
        raise

if __name__ == "__main__":
    test_latin1_csv()
