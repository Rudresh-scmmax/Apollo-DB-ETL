from etl.db import get_engine
from sqlalchemy import text
import os

os.environ['USE_DB_QUERY_LAMBDA'] = 'true'

def cleanup():
    engine = get_engine()
    table_name = 'uom_master'
    
    print(f"Cleaning up {table_name}...")
    
    with engine.begin() as conn:
        try:
            # Delete test row
            conn.execute(text(f"DELETE FROM {table_name} WHERE uom_id = 999"))
            print("Deleted test row (uom_id=999).")
            
            # Drop test column
            conn.execute(text(f'ALTER TABLE "{table_name}" DROP COLUMN "new_col"'))
            print("Dropped column 'new_col'.")
            
        except Exception as e:
            print(f"Cleanup failed: {e}")

if __name__ == "__main__":
    cleanup()
