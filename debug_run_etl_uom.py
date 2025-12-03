import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from etl.run_etl import (
    read_sheet, clean_dataframe, apply_column_renames, 
    coerce_types_for_table, split_valid_invalid, 
    auto_generate_missing_keys, apply_json_transforms
)
from etl.load import stage_and_upsert
from etl.db import get_engine, get_primary_keys
from etl.models_loader import load_models_module, get_etl_config_from_models

def debug_uom_flow():
    load_dotenv()
    os.environ['USE_DB_QUERY_LAMBDA'] = 'true'
    
    excel_path = "export.xlsx"
    models_path = "etl/models.py"
    
    print("Loading models...")
    models_module = load_models_module(models_path)
    models_config = get_etl_config_from_models(models_module)
    
    sheet_name = "uom_master"
    target_table = "uom_master"
    
    print(f"Reading {sheet_name}...")
    df = read_sheet(excel_path, sheet_name)
    df = clean_dataframe(df)
    
    # Config
    table_config = models_config['mappings']['tables'].get(target_table, {})
    types_cfg = table_config.get('dtypes', {})
    pk_cols = ['uom_id'] # Hardcoded for debug
    
    print(f"Types config: {types_cfg}")
    
    # Transforms
    print("Applying JSON transforms...")
    df = apply_json_transforms(df, target_table)
    
    print("Coercing types...")
    df, type_invalid, type_reasons = coerce_types_for_table(df, types_cfg)
    if not type_invalid.empty:
        print(f"Type invalid rows: {len(type_invalid)}")
        print(type_reasons)
    
    print(f"Rows ready: {len(df)}")
    
    # DB Load
    engine = get_engine()
    with engine.begin() as conn:
        print("Calling stage_and_upsert...")
        try:
            stage_and_upsert(conn, target_table, df, pk_cols, replace=False, allow_fk_violations=True, models_module=models_module)
            print("Success!")
        except Exception as e:
            print(f"FAILED: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_uom_flow()
