from etl.db import get_engine
from sqlalchemy import text
import os

os.environ['USE_DB_QUERY_LAMBDA'] = 'true'

def check_counts():
    engine = get_engine()
    tables = ['uom_master', 'material_type_master', 'material_master']
    
    with engine.connect() as conn:
        for table in tables:
            try:
                count = conn.execute(text(f"SELECT count(*) FROM {table}")).scalar()
                print(f"{table}: {count}")
            except Exception as e:
                print(f"{table}: Error {e}")

if __name__ == "__main__":
    check_counts()
