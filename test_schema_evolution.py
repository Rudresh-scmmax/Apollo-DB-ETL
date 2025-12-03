import pandas as pd
from etl.db import get_engine
from etl.load import stage_and_upsert
from sqlalchemy import text
import os

os.environ['USE_DB_QUERY_LAMBDA'] = 'true'

def test_evolution():
    engine = get_engine()
    table_name = 'uom_master'
    
    # Create a DataFrame with an extra column
    data = {
        'uom_id': [999],
        'uom_name': ['Test Unit'],
        'new_col': ['Test Value']
    }
    df = pd.DataFrame(data)
    
    print(f"Testing schema evolution for {table_name} with new column 'new_col'...")
    
    with engine.begin() as conn:
        try:
            # We need to pass pk_cols
            pk_cols = ['uom_id']
            stage_and_upsert(conn, table_name, df, pk_cols, replace=False)
            print("Success! stage_and_upsert completed.")
            
            # Verify column exists
            result = conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}' AND column_name = 'new_col'"))
            if result.fetchone():
                print("Verified: Column 'new_col' was added to the database.")
            else:
                print("Failed: Column 'new_col' was NOT added to the database.")
                
            # Clean up (drop column) - optional, but good for repeatability if we want to test again (though ALTER ADD fails if exists)
            # conn.execute(text(f'ALTER TABLE "{table_name}" DROP COLUMN "new_col"'))
            # print("Cleaned up: Dropped 'new_col'.")

        except Exception as e:
            print(f"Failed as expected: {e}")

if __name__ == "__main__":
    test_evolution()
