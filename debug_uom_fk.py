import os
import sys
from sqlalchemy import text
from etl.db_lambda import LambdaConnection

# Force Lambda connection
os.environ['USE_DB_QUERY_LAMBDA'] = 'true'
sys.stdout.reconfigure(encoding='utf-8')

def debug_uom():
    print("Connecting to database via Lambda...")
    conn = LambdaConnection()
    
    print("\n--- Debugging uom_master FK check ---")
    
    # 1. Check count
    print("1. Checking count(*)")
    try:
        count_res = conn.execute(text("SELECT count(*) FROM uom_master"))
        count = count_res.scalar()
        print(f"Count result type: {type(count)}")
        print(f"Count result value: {count}")
    except Exception as e:
        print(f"Count failed: {e}")

    # 2. Check DISTINCT uom_id
    print("\n2. Checking DISTINCT uom_id")
    try:
        distinct_res = conn.execute(text("SELECT DISTINCT uom_id FROM uom_master WHERE uom_id IS NOT NULL"))
        rows = distinct_res.fetchall()
        print(f"Fetchall result type: {type(rows)}")
        print(f"Number of rows: {len(rows)}")
        if len(rows) > 0:
            print(f"First row type: {type(rows[0])}")
            print(f"First row value: {rows[0]}")
            
        valid_ids = {str(row[0]) for row in rows}
        print(f"Valid IDs count: {len(valid_ids)}")
        print(f"First 5 IDs: {list(valid_ids)[:5]}")
    except Exception as e:
        print(f"Distinct check failed: {e}")

    # 3. Check specific column
    print("\n3. Checking SELECT uom_id LIMIT 5")
    try:
        col_res = conn.execute(text("SELECT uom_id FROM uom_master LIMIT 5"))
        rows = col_res.fetchall()
        print(f"Rows: {rows}")
    except Exception as e:
        print(f"Column select failed: {e}")

    # 4. Check SELECT *
    print("\n4. Checking SELECT * LIMIT 5")
    try:
        star_res = conn.execute(text("SELECT * FROM uom_master LIMIT 5"))
        rows = star_res.fetchall()
        print(f"Rows: {rows}")
    except Exception as e:
        print(f"Star select failed: {e}")

    # 5. Check columns
    print("\n5. Checking columns in information_schema")
    try:
        col_info = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'uom_master'"))
        rows = col_info.fetchall()
        print(f"Columns: {rows}")
    except Exception as e:
        print(f"Column info failed: {e}")

    # 6. Try INSERT
    print("\n6. Trying INSERT into uom_master")
    try:
        # Use a high ID to avoid conflict
        insert_sql = "INSERT INTO uom_master (uom_id, uom_name) VALUES (99999, 'TestUOM') RETURNING uom_id"
        print(f"Executing: {insert_sql}")
        insert_res = conn.execute(text(insert_sql))
        rows = insert_res.fetchall()
        print(f"Insert Result: {rows}")
        
        # Check if it exists
        check_res = conn.execute(text("SELECT * FROM uom_master WHERE uom_id = 99999"))
        print(f"Check Result: {check_res.fetchall()}")
        
        # Cleanup
        conn.execute(text("DELETE FROM uom_master WHERE uom_id = 99999"))
    except Exception as e:
        print(f"Insert failed: {e}")

if __name__ == "__main__":
    debug_uom()
