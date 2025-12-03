import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from etl.models_loader import load_models_module, get_etl_config_from_models
from etl.utils import load_yaml

# Redirect output to file
output_file = open('diagnostic_output.txt', 'w', encoding='utf-8')
sys.stdout = output_file

# Load models and get expected tables
models_module = load_models_module("etl/models.py")
models_config = get_etl_config_from_models(models_module)

# Load mappings
mappings = load_yaml("etl/config/mappings.yaml")

# Get actual sheets from Excel
xl = pd.ExcelFile('export.xlsx')
actual_sheets = set(xl.sheet_names)

# Get expected tables from models
from etl.models_utils import get_all_models_from_module
models = get_all_models_from_module(models_module)
expected_tables = set(models.keys())

# Get load order
load_order = mappings.get("load_order", {})
masters = load_order.get("masters", [])

print("=" * 80)
print("DIAGNOSTIC: Sheet Names vs Table Names")
print("=" * 80)

print(f"\nTotal sheets in Excel: {len(actual_sheets)}")
print(f"Total tables in models.py: {len(expected_tables)}")

print("\n" + "=" * 80)
print("MASTER TABLES (from load_order):")
print("=" * 80)
for table in masters:
    in_excel_exact = table in actual_sheets
    in_models = table in expected_tables
    
    # Check if there's a mapping
    mapping_cfg = mappings.get("tables", {}).get(table, {})
    target_table = mapping_cfg.get("target_table", table)
    
    status = "✓" if in_excel_exact else "✗"
    print(f"{status} {table:40s} | Excel: {in_excel_exact:5} | Models: {in_models:5} | Target: {target_table}")

print("\n" + "=" * 80)
print("MISSING MASTER TABLES (in load_order but not in Excel):")
print("=" * 80)
missing_masters = [t for t in masters if t not in actual_sheets]
for table in missing_masters:
    # Try to find similar names
    similar = [s for s in actual_sheets if table.lower() in s.lower() or s.lower() in table.lower()]
    print(f"  {table:40s} | Similar: {similar[:3]}")

print("\n" + "=" * 80)
print("ALL SHEET NAMES IN EXCEL:")
print("=" * 80)
for i, sheet in enumerate(sorted(actual_sheets), 1):
    in_models = sheet in expected_tables
    print(f"  {i:2d}. {sheet:50s} | In models: {in_models}")

output_file.close()
print("Output saved to diagnostic_output.txt", file=sys.__stdout__)

