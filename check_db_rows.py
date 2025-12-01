import os
import sys
from pathlib import Path
from sqlalchemy import text

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set env var for Lambda
os.environ['USE_DB_QUERY_LAMBDA'] = 'true'

from etl.db import get_engine

def check_table(table_name):
    engine = get_engine()
    with engine.connect() as conn:
        print(f"--- {table_name} ---")
        try:
            result = conn.execute(text(f"SELECT count(*) FROM {table_name}")).scalar()
            if isinstance(result, dict) and 'count' in result:
                print(f"Count: {result['count']}")
            else:
                print(f"Count: {result}")
            
            rows = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 5")).fetchall()
            print("First 5 rows:")
            for row in rows:
                print(row)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_table('location_type_master')
