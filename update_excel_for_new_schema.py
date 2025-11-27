#!/usr/bin/env python3
"""
Update Excel file to match new database schema.

This script will:
1. Add new required columns
2. Rename columns to match new schema
3. Convert data types (especially IDs to integers)
4. Remove deprecated columns
5. Add default values for new required columns where possible
"""
from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path
import sys
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

def update_supplier_master(df: pd.DataFrame) -> pd.DataFrame:
    """Update supplier_master sheet."""
    df = df.copy()
    
    # Rename columns
    rename_map = {
        'VENDOR_ID': 'VENDOR_ID',  # Keep for now, will convert to int
        'VENDOR_NAME': 'VENDOR_NAME',
        'COUNTRY': 'COUNTRY',
        'PAYMENT_CURRENCY_CODE': 'PAYMENT_CURRENCY_CODE',
        'BASE_CURRENCY_ID': 'BASE_CURRENCY_ID',
        'STATE': 'STATE',
        'NAME': 'NAME',
        'PARTY_NUMBER': 'PARTY_NUMBER',
    }
    
    # Add new required columns if missing
    if 'SUPPLIER_PLANT_NAME' not in df.columns:
        # Try to derive from supplier_name or set default
        if 'VENDOR_NAME' in df.columns:
            df['SUPPLIER_PLANT_NAME'] = df['VENDOR_NAME'].astype(str) + ' Plant'
        else:
            df['SUPPLIER_PLANT_NAME'] = 'Default Plant'
        print("  [ADD] Added SUPPLIER_PLANT_NAME column")
    
    if 'SUPPLIER_STATUS' not in df.columns:
        df['SUPPLIER_STATUS'] = 'Active'  # Default value
        print("  [ADD] Added SUPPLIER_STATUS column (default: 'Active')")
    
    if 'SUPPLIER_COUNTRY_ID' not in df.columns:
        df['SUPPLIER_COUNTRY_ID'] = None  # Optional, will be NULL
        print("  [ADD] Added SUPPLIER_COUNTRY_ID column (optional)")
    
    # Convert VENDOR_ID to integer if possible
    if 'VENDOR_ID' in df.columns:
        try:
            # Try to convert to numeric, keeping non-numeric as NaN
            df['VENDOR_ID'] = pd.to_numeric(df['VENDOR_ID'], errors='coerce')
            print("  [CONVERT] Converted VENDOR_ID to numeric")
        except Exception as e:
            print(f"  [WARN] Could not convert VENDOR_ID to numeric: {e}")
    
    return df


def update_purchasing_organizations(df: pd.DataFrame) -> pd.DataFrame:
    """Update purchasing_organizations sheet."""
    df = df.copy()
    
    # Convert purchasing_org_id to integer
    if 'purchasing_org_id' in df.columns:
        try:
            df['purchasing_org_id'] = pd.to_numeric(df['purchasing_org_id'], errors='coerce')
            print("  [CONVERT] Converted purchasing_org_id to numeric")
        except Exception as e:
            print(f"  [WARN] Could not convert purchasing_org_id to numeric: {e}")
    
    # Add org_code if missing
    if 'org_code' not in df.columns:
        df['org_code'] = None
        print("  [ADD] Added org_code column (optional)")
    
    return df


def update_purchaser_plant_master(df: pd.DataFrame) -> pd.DataFrame:
    """Update purchaser_plant_master sheet."""
    df = df.copy()
    
    # Rename plant_country to plant_country_code (keep both for compatibility)
    if 'plant_country' in df.columns and 'plant_country_code' not in df.columns:
        df['plant_country_code'] = df['plant_country']
        print("  [ADD] Added plant_country_code column (copied from plant_country)")
    
    # Convert plant_id to integer
    if 'plant_id' in df.columns:
        try:
            df['plant_id'] = pd.to_numeric(df['plant_id'], errors='coerce')
            print("  [CONVERT] Converted plant_id to numeric")
        except Exception as e:
            print(f"  [WARN] Could not convert plant_id to numeric: {e}")
    
    # Convert special_economic_zone to string if boolean
    if 'special_economic_zone' in df.columns:
        if df['special_economic_zone'].dtype == bool:
            df['special_economic_zone'] = df['special_economic_zone'].map({True: 'true', False: 'false'})
            print("  [CONVERT] Converted special_economic_zone from boolean to string")
        elif df['special_economic_zone'].dtype == 'object':
            # Try to normalize boolean-like strings
            df['special_economic_zone'] = df['special_economic_zone'].astype(str).str.lower()
            df['special_economic_zone'] = df['special_economic_zone'].replace({
                'true': 'true', 'false': 'false', '1': 'true', '0': 'false',
                'yes': 'true', 'no': 'false', 'y': 'true', 'n': 'false'
            })
    
    # Remove deprecated columns
    deprecated = ['nearest_port', 'logistic_cost_per_container']
    for col in deprecated:
        if col in df.columns:
            df = df.drop(columns=[col])
            print(f"  [REMOVE] Removed deprecated column: {col}")
    
    return df


def update_plant_material_purchase_org_sup(df: pd.DataFrame) -> pd.DataFrame:
    """Update plant_material_purchase_org_sup sheet."""
    df = df.copy()
    
    # Convert IDs to integer
    for col in ['plant_id', 'supplier_id']:
        if col in df.columns or col.upper() in df.columns:
            col_name = col if col in df.columns else col.upper()
            try:
                df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
                print(f"  [CONVERT] Converted {col_name} to numeric")
            except Exception as e:
                print(f"  [WARN] Could not convert {col_name} to numeric: {e}")
    
    # Add new required columns
    plant_id_col = None
    for col in ['plant_id', 'PLANT_ID']:
        if col in df.columns:
            plant_id_col = col
            break
    
    supplier_id_col = None
    for col in ['supplier_id', 'SUPPLIER_ID']:
        if col in df.columns:
            supplier_id_col = col
            break
    
    if 'plant_name' not in df.columns and 'PLANT_NAME' not in df.columns:
        # Try to get from purchaser_plant_master or set default
        if plant_id_col:
            df['plant_name'] = 'Plant ' + df[plant_id_col].astype(str)
        else:
            df['plant_name'] = 'Unknown Plant'
        print("  [ADD] Added plant_name column")
    
    if 'supplier_name' not in df.columns and 'SUPPLIER_NAME' not in df.columns:
        # Try to get from supplier_master or set default
        if supplier_id_col:
            df['supplier_name'] = 'Supplier ' + df[supplier_id_col].astype(str)
        else:
            df['supplier_name'] = 'Unknown Supplier'
        print("  [ADD] Added supplier_name column")
    
    if 'supplier_plant' not in df.columns and 'SUPPLIER_PLANT' not in df.columns:
        # Default value - try to use supplier_name if available
        if 'supplier_name' in df.columns:
            df['supplier_plant'] = df['supplier_name']
        elif 'SUPPLIER_NAME' in df.columns:
            df['supplier_plant'] = df['SUPPLIER_NAME']
        else:
            df['supplier_plant'] = 'Default Plant'
        print("  [ADD] Added supplier_plant column")
    
    # Rename User_ID to user_id (keep both for compatibility)
    if 'User_ID' in df.columns and 'user_id' not in df.columns:
        df['user_id'] = pd.to_numeric(df['User_ID'], errors='coerce')
        print("  [ADD] Added user_id column (from User_ID)")
    
    # Rename User_Purchase_Org_ID to user_purchase_org_id
    if 'User_Purchase_Org_ID' in df.columns and 'user_purchase_org_id' not in df.columns:
        df['user_purchase_org_id'] = pd.to_numeric(df['User_Purchase_Org_ID'], errors='coerce')
        print("  [ADD] Added user_purchase_org_id column (from User_Purchase_Org_ID)")
    
    return df


def update_where_to_use_each_price_type(df: pd.DataFrame) -> pd.DataFrame:
    """Update where_to_use_each_price_type sheet."""
    df = df.copy()
    
    # Convert price_type_id to integer
    if 'price_type_id' in df.columns:
        try:
            df['price_type_id'] = pd.to_numeric(df['price_type_id'], errors='coerce')
            print("  [CONVERT] Converted price_type_id to numeric")
        except Exception as e:
            print(f"  [WARN] Could not convert price_type_id to numeric: {e}")
    
    # Add new required columns with defaults
    required_new_cols = {
        'material_description': lambda d: d.get('material_id', pd.Series([''])).astype(str) + ' Description',
        'price_type_desc': 'Price Type',
        'source_of_price_id': 1,  # Default to 1
        'data_series_to_extract_from_source': 'Default Series',
        'frequency_of_update_id': 1,  # Default to 1
        'repeat_choice': 'Daily',
    }
    
    for col, default in required_new_cols.items():
        if col not in df.columns:
            if callable(default):
                df[col] = default(df)
            else:
                df[col] = default
            print(f"  [ADD] Added {col} column (with default value)")
    
    # Convert boolean columns to string
    bool_cols = ['use_in_cost_sheet', 'use_in_price_benchmarking', 'use_in_spend_analytics']
    for col in bool_cols:
        if col in df.columns:
            if df[col].dtype == bool:
                df[col] = df[col].map({True: 'true', False: 'false'})
                print(f"  [CONVERT] Converted {col} from boolean to string")
    
    return df


def update_settings_user_material_category(df: pd.DataFrame) -> pd.DataFrame:
    """Update settings_user_material_category sheet."""
    df = df.copy()
    
    # Convert user_id to integer
    if 'user_id' in df.columns:
        try:
            df['user_id'] = pd.to_numeric(df['user_id'], errors='coerce')
            print("  [CONVERT] Converted user_id to numeric")
        except Exception as e:
            print(f"  [WARN] Could not convert user_id to numeric: {e}")
    
    return df


def update_excel_file(excel_path: str, output_path: Optional[str] = None) -> str:
    """Update Excel file with new schema changes."""
    
    if output_path is None:
        # Create backup and new file
        path = Path(excel_path)
        backup_path = path.parent / f"{path.stem}_backup{path.suffix}"
        output_path = path.parent / f"{path.stem}_updated{path.suffix}"
        
        # Copy original to backup
        import shutil
        shutil.copy2(excel_path, backup_path)
        print(f"[BACKUP] Created backup: {backup_path}")
    
    print(f"[READ] Reading Excel file: {excel_path}")
    
    # Read all sheets
    excel_file = pd.ExcelFile(excel_path, engine='openpyxl')
    sheet_names = excel_file.sheet_names
    
    print(f"[INFO] Found {len(sheet_names)} sheets")
    
    # Dictionary to store updated sheets
    updated_sheets = {}
    
    # Sheet update mappings
    sheet_updaters = {
        'supplier_master': update_supplier_master,
        'purchasing_organizations': update_purchasing_organizations,
        'purchaser_plant_master': update_purchaser_plant_master,
        'plant_material_purchase_org_sup': update_plant_material_purchase_org_sup,
        'where_to_use_each_price_type': update_where_to_use_each_price_type,
        'settings_user_material_category': update_settings_user_material_category,
    }
    
    # Process each sheet
    for sheet_name in sheet_names:
        print(f"\n[PROCESS] Processing sheet: {sheet_name}")
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        original_cols = len(df.columns)
        original_rows = len(df)
        
        # Check if this sheet needs updating
        updater = None
        for key, func in sheet_updaters.items():
            if key.lower() in sheet_name.lower() or sheet_name.lower() in key.lower():
                updater = func
                break
        
        if updater:
            df = updater(df)
            new_cols = len(df.columns)
            print(f"  [OK] Updated: {original_cols} -> {new_cols} columns, {original_rows} rows")
        else:
            print(f"  [SKIP] No updates needed (keeping as-is)")
        
        updated_sheets[sheet_name] = df
    
    # Write updated Excel file
    print(f"\n[WRITE] Writing updated Excel file: {output_path}")
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for sheet_name, df in updated_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"  [OK] Wrote sheet: {sheet_name} ({len(df)} rows, {len(df.columns)} columns)")
    
    print(f"\n[SUCCESS] Excel file updated successfully!")
    print(f"   Original: {excel_path}")
    print(f"   Updated:  {output_path}")
    print(f"   Backup:   {backup_path if 'backup_path' in locals() else 'N/A'}")
    
    return str(output_path)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Update Excel file to match new database schema"
    )
    parser.add_argument(
        '--excel',
        default='Data_processedv4.xlsx',
        help='Path to Excel file to update (default: Data_processedv4.xlsx)'
    )
    parser.add_argument(
        '--output',
        help='Output file path (default: creates _updated version)'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating backup file'
    )
    
    args = parser.parse_args()
    
    excel_path = Path(args.excel)
    if not excel_path.exists():
        print(f"[ERROR] Excel file not found: {excel_path}")
        sys.exit(1)
    
    try:
        output_path = update_excel_file(str(excel_path), args.output)
        print(f"\n[SUCCESS] Done! Updated file saved to: {output_path}")
        print(f"\n[IMPORTANT] Review the updated file and fill in:")
        print(f"   - Required columns that were auto-filled with defaults")
        print(f"   - Any NULL values in ID columns")
        print(f"   - Verify data types are correct")
    except Exception as e:
        print(f"[ERROR] Error updating Excel file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

