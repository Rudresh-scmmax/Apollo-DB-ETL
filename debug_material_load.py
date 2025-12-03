import os
import pandas as pd
from etl.db import get_engine
from etl.extract import read_sheet
from etl.load import stage_and_upsert
from etl.utils import load_yaml

# Setup
os.environ['USE_DB_QUERY_LAMBDA'] = 'true'
excel_path = 'export.xlsx'
mappings_path = 'etl/config/mappings.yaml'
mappings = load_yaml(mappings_path)
sheet_name = 'material_master'
table_name = 'material_master'

import sys
sys.stdout = open('debug_log_internal.txt', 'w', encoding='utf-8')
sys.stderr = sys.stdout

print(f"Reading {sheet_name}...")
df = read_sheet(excel_path, sheet_name)
print(f"Read {len(df)} rows")

if df.empty:
    print("DataFrame is empty!")
    exit()

# Connect
print("Connecting to DB...")
engine = get_engine()
with engine.begin() as conn:
    # Check dependencies
    from sqlalchemy import text
    uom_count = conn.execute(text("SELECT count(*) FROM uom_master")).scalar()
    type_count = conn.execute(text("SELECT count(*) FROM material_type_master")).scalar()
    print(f"Dependencies: uom_master={uom_count}, material_type_master={type_count}")

    # Run stage_and_upsert
    print("Running stage_and_upsert...")
    pk_cols = ['material_id']
    
    # Enable verbose debug in stage_and_upsert by monkeypatching or just relying on existing prints
    # We'll just run it and see the output
    import etl.models as models_module
    inserted, updated, rejected, rejected_df = stage_and_upsert(
        conn, table_name, df, pk_cols, replace=False, allow_fk_violations=True, models_module=models_module
    )
    
    print(f"Result: inserted={inserted}, updated={updated}, rejected={rejected}")
    if not rejected_df.empty:
        print("Rejected reasons:")
        print(rejected_df['rejection_reason'].value_counts())

    # Verify
    final_count = conn.execute(text(f"SELECT count(*) FROM {table_name}")).scalar()
    print(f"Final count in DB: {final_count}")
