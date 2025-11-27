#!/usr/bin/env python3
"""
Add missing tables and columns to Excel file.
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
    load_order = mappings.get('load_order', {})
    for category in ['masters', 'core', 'relationship', 'transactional']:
        tables = load_order.get(category, [])
        expected.update(tables)
    tables_section = mappings.get('tables', {})
    expected.update(tables_section.keys())
    return expected

def get_excel_sheets(excel_path: str) -> Set[str]:
    """Get all sheet names from Excel file."""
    xl = pd.ExcelFile(excel_path, engine='openpyxl')
    return set(xl.sheet_names)

def get_columns_for_table(table_name: str, mappings: Dict) -> List[str]:
    """Get expected Excel column names for a table."""
    table_config = mappings.get('tables', {}).get(table_name, {})
    column_renames = table_config.get('column_renames', {})
    dtypes = table_config.get('dtypes', {})
    
    # Get Excel column names (keys of column_renames, or DB column names if no rename)
    excel_columns = []
    db_columns = list(dtypes.keys())
    
    for db_col in db_columns:
        # Find Excel column that maps to this DB column
        excel_col = None
        for excel_key, db_value in column_renames.items():
            if db_value == db_col:
                excel_col = excel_key
                break
        
        if not excel_col:
            # No mapping found, assume Excel column = DB column
            excel_col = db_col
        
        if excel_col not in excel_columns:
            excel_columns.append(excel_col)
    
    return excel_columns

def add_missing_tables_to_excel(excel_path: str, output_path: str = None, add_empty_sheets: bool = True):
    """Add missing tables and columns to Excel file."""
    if output_path is None:
        output_path = excel_path.replace('.xlsx', '_complete.xlsx')
    
    print(f"[READ] Reading Excel file: {excel_path}")
    
    # Load mappings
    mappings = load_mappings()
    expected_tables = get_expected_tables(mappings)
    
    # Read existing Excel file
    excel_file = pd.ExcelFile(excel_path, engine='openpyxl')
    existing_sheets = set(excel_file.sheet_names)
    non_data_sheets = {'Export Summary', 'Summary & Sequence'}
    data_sheets = existing_sheets - non_data_sheets
    
    # Find missing tables
    missing_tables = expected_tables - data_sheets
    
    print(f"[INFO] Existing tables: {len(data_sheets)}")
    print(f"[INFO] Expected tables: {len(expected_tables)}")
    print(f"[INFO] Missing tables: {len(missing_tables)}")
    
    # Read all existing sheets
    all_sheets = {}
    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        all_sheets[sheet_name] = df
    
    # Fix port_master missing column
    if 'port_master' in all_sheets:
        if 'freight_mode' not in all_sheets['port_master'].columns:
            all_sheets['port_master']['freight_mode'] = ''  # Empty string default
            print("[FIX] Added missing 'freight_mode' column to port_master")
    
    # Add missing tables as empty sheets with headers
    if add_empty_sheets and missing_tables:
        print(f"\n[ADD] Creating {len(missing_tables)} missing table(s) with column headers...")
        for table_name in sorted(missing_tables):
            columns = get_columns_for_table(table_name, mappings)
            if columns:
                # Create empty DataFrame with column headers
                df = pd.DataFrame(columns=columns)
                all_sheets[table_name] = df
                print(f"  [OK] Created sheet: {table_name} ({len(columns)} columns)")
            else:
                print(f"  [WARN] No column configuration for: {table_name}")
    
    # Write updated Excel file
    print(f"\n[WRITE] Writing updated Excel file: {output_path}")
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Write non-data sheets first
        for sheet_name in ['Export Summary', 'Summary & Sequence']:
            if sheet_name in all_sheets:
                all_sheets[sheet_name].to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Write data sheets
        for sheet_name in sorted([s for s in all_sheets.keys() if s not in non_data_sheets]):
            all_sheets[sheet_name].to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"\n[SUCCESS] Updated Excel file saved to: {output_path}")
    print(f"  - Fixed missing columns")
    if add_empty_sheets:
        print(f"  - Added {len(missing_tables)} missing table(s) with column headers")
    print(f"  - Total sheets: {len(all_sheets)}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Add missing tables and columns to Excel file")
    parser.add_argument('--excel', default='Data_processedv4_updated.xlsx', help='Input Excel file')
    parser.add_argument('--output', help='Output Excel file (default: adds _complete suffix)')
    parser.add_argument('--no-empty-sheets', action='store_true', help='Do not add empty sheets for missing tables')
    
    args = parser.parse_args()
    
    if not Path(args.excel).exists():
        print(f"[ERROR] Excel file not found: {args.excel}")
        exit(1)
    
    add_missing_tables_to_excel(
        args.excel, 
        args.output, 
        add_empty_sheets=not args.no_empty_sheets
    )

