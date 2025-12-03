import os
import sys
from etl.db import get_engine
from etl.extract import read_sheet
from etl.load import stage_and_upsert
from etl.utils import load_yaml
import etl.models as models_module # Import models module

# Setup logging
sys.stdout = open('debug_uom_log.txt', 'w', encoding='utf-8')
sys.stderr = sys.stdout

os.environ['USE_DB_QUERY_LAMBDA'] = 'true'
excel_path = 'export.xlsx'
mappings_path = 'etl/config/mappings.yaml'
mappings = load_yaml(mappings_path)
sheet_name = 'uom_master'
target_table = 'uom_master'
actual_sheet = sheet_name
for s, cfg in mappings.get('tables', {}).items():
    if cfg.get('target_table') == target_table:
        actual_sheet = s
        break

print(f"Reading {actual_sheet} for table {target_table}...")
df = read_sheet(excel_path, actual_sheet)
print(f"Read {len(df)} rows")

if df.empty:
    print("DataFrame is empty!")
    exit()

# Connect
print("Connecting to DB...")
engine = get_engine()
with engine.begin() as conn:
    # Run stage_and_upsert
    print("Running stage_and_upsert...")
    pk_cols = ['uom_id']
    
    # Pass models_module to enable JSONB fix
    inserted, updated, rejected, rejected_df = stage_and_upsert(
        conn, target_table, df, pk_cols, replace=False, allow_fk_violations=True, models_module=models_module
    )
    
    print(f"Result: inserted={inserted}, updated={updated}, rejected={rejected}")
    if not rejected_df.empty:
        print("Rejected reasons:")
        print(rejected_df['rejection_reason'].value_counts())

    # Verify
    from sqlalchemy import text
    final_count = conn.execute(text(f"SELECT count(*) FROM {target_table}")).scalar()
    print(f"Final count in DB: {final_count}")
