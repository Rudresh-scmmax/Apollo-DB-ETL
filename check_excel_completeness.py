#!/usr/bin/env python3
"""
Check if all required tables and fields are present in the Excel file.
"""
import pandas as pd
import yaml
from pathlib import Path
from typing import Dict, List, Set

def load_mappings() -> Dict:
    """Load mappings.yaml to get expected tables."""
    with open('etl/config/mappings.yaml', 'r') as f:
        return yaml.safe_load(f)

def get_expected_tables(mappings: Dict) -> Set[str]:
    """Get all expected table names from mappings."""
    expected = set()
    
    # Get from load_order
    load_order = mappings.get('load_order', {})
    for category in ['masters', 'core', 'relationship', 'transactional']:
        tables = load_order.get(category, [])
        expected.update(tables)
    
    # Also get from tables section
    tables_section = mappings.get('tables', {})
    expected.update(tables_section.keys())
    
    return expected

def get_excel_sheets(excel_path: str) -> Set[str]:
    """Get all sheet names from Excel file."""
    xl = pd.ExcelFile(excel_path, engine='openpyxl')
    return set(xl.sheet_names)

def get_expected_columns_for_table(table_name: str, mappings: Dict) -> Dict[str, str]:
    """Get expected columns and their types for a table."""
    table_config = mappings.get('tables', {}).get(table_name, {})
    column_renames = table_config.get('column_renames', {})
    dtypes = table_config.get('dtypes', {})
    
    # The column_renames maps Excel columns to DB columns
    # So the Excel columns are the keys, DB columns are the values
    # But we also need to check dtypes which uses DB column names
    
    # Get all DB column names from dtypes
    db_columns = set(dtypes.keys())
    
    # Get Excel column names from column_renames (keys)
    excel_columns = set(column_renames.keys())
    
    # Also check reverse mapping - if DB column is not in column_renames values,
    # it might be that Excel column name = DB column name
    for db_col in db_columns:
        if db_col not in column_renames.values():
            excel_columns.add(db_col)  # Assume same name
    
    return {
        'excel_columns': excel_columns,
        'db_columns': db_columns,
        'column_renames': column_renames,
        'dtypes': dtypes
    }

def check_excel_completeness(excel_path: str):
    """Check if Excel file has all required tables and columns."""
    print("=" * 80)
    print("EXCEL FILE COMPLETENESS CHECK")
    print("=" * 80)
    print(f"\nChecking: {excel_path}\n")
    
    # Load mappings
    mappings = load_mappings()
    
    # Get expected tables
    expected_tables = get_expected_tables(mappings)
    
    # Get Excel sheets
    excel_sheets = get_excel_sheets(excel_path)
    
    # Filter out non-data sheets
    non_data_sheets = {'Export Summary', 'Summary & Sequence'}
    data_sheets = excel_sheets - non_data_sheets
    
    print(f"Expected tables (from mappings.yaml): {len(expected_tables)}")
    print(f"Excel sheets (data): {len(data_sheets)}")
    print(f"Excel sheets (total): {len(excel_sheets)}")
    print()
    
    # Find missing tables
    missing_tables = expected_tables - data_sheets
    extra_tables = data_sheets - expected_tables
    
    print("=" * 80)
    print("TABLE COMPARISON")
    print("=" * 80)
    
    if missing_tables:
        print(f"\n[WARNING] Missing tables in Excel ({len(missing_tables)}):")
        for table in sorted(missing_tables):
            print(f"  - {table}")
    else:
        print("\n[OK] All expected tables are present in Excel!")
    
    if extra_tables:
        print(f"\n[INFO] Extra tables in Excel (not in mappings) ({len(extra_tables)}):")
        for table in sorted(extra_tables):
            print(f"  - {table}")
    
    print("\n" + "=" * 80)
    print("COLUMN CHECK (for tables in Excel)")
    print("=" * 80)
    
    # Check columns for each table that exists in Excel
    issues_found = False
    
    for table_name in sorted(data_sheets):
        if table_name not in expected_tables:
            continue  # Skip tables not in mappings
        
        table_config = mappings.get('tables', {}).get(table_name, {})
        if not table_config:
            print(f"\n[SKIP] {table_name}: No configuration in mappings.yaml")
            continue
        
        # Read the sheet to get actual columns
        try:
            df = pd.read_excel(excel_path, sheet_name=table_name, nrows=0)  # Just headers
            actual_columns = set(df.columns.str.strip())
        except Exception as e:
            print(f"\n[ERROR] {table_name}: Could not read sheet - {e}")
            continue
        
        # Get expected columns
        expected_info = get_expected_columns_for_table(table_name, mappings)
        expected_excel_cols = expected_info['excel_columns']
        expected_db_cols = expected_info['db_columns']
        column_renames = expected_info['column_renames']
        
        # Check for missing columns
        # We need to check if Excel has columns that map to required DB columns
        missing_cols = []
        for db_col in expected_db_cols:
            # Find Excel column that maps to this DB column
            excel_col = None
            for excel_key, db_value in column_renames.items():
                if db_value == db_col:
                    excel_col = excel_key
                    break
            
            if not excel_col:
                # No mapping found, assume Excel column = DB column
                excel_col = db_col
            
            # Check if Excel column exists (case-insensitive)
            excel_col_lower = excel_col.lower().strip()
            actual_cols_lower = {c.lower().strip() for c in actual_columns}
            
            if excel_col_lower not in actual_cols_lower:
                # Also check if DB column name exists directly
                db_col_lower = db_col.lower().strip()
                if db_col_lower not in actual_cols_lower:
                    missing_cols.append((excel_col, db_col))
        
        if missing_cols:
            issues_found = True
            print(f"\n[WARNING] {table_name}: Missing columns ({len(missing_cols)}):")
            for excel_col, db_col in missing_cols:
                print(f"  - Excel: '{excel_col}' -> DB: '{db_col}'")
        else:
            print(f"\n[OK] {table_name}: All expected columns present ({len(actual_columns)} columns)")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if not missing_tables and not issues_found:
        print("\n[SUCCESS] Excel file appears complete!")
        print("  - All expected tables are present")
        print("  - All expected columns are present")
    else:
        print("\n[ACTION REQUIRED]")
        if missing_tables:
            print(f"  - Add {len(missing_tables)} missing table(s) to Excel")
        if issues_found:
            print("  - Add missing columns to existing tables (see details above)")
    
    print()

if __name__ == '__main__':
    excel_path = 'Data_processedv4_updated.xlsx'
    if not Path(excel_path).exists():
        print(f"Error: Excel file not found: {excel_path}")
        exit(1)
    
    check_excel_completeness(excel_path)

