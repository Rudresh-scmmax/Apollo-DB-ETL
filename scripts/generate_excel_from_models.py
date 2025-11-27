#!/usr/bin/env python3
"""
Generate Excel template file from SQLAlchemy models.

This script creates an Excel file with one sheet per database table,
each containing the column headers from the models. This is used locally
to create Excel templates for data entry.

Usage:
    python scripts/generate_excel_from_models.py --models-path etl/models.py --output template.xlsx
"""
import argparse
import pandas as pd
from pathlib import Path
import sys
from typing import Dict, List

# Add parent directory to path to import etl module
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl.models_loader import load_models_module
from etl.models_utils import (
    get_all_models_from_module,
    get_table_columns_from_model,
    get_primary_keys_from_model,
)


def generate_excel_from_models(models_path: str, output_path: str, include_summary: bool = True):
    """
    Generate Excel file with sheets for each table from models.
    
    Args:
        models_path: Path to models.py file
        output_path: Path to output Excel file
        include_summary: Whether to include a summary sheet with table info
    """
    print(f"[LOAD] Loading models from: {models_path}")
    
    # Load models
    models_module = load_models_module(models_path)
    models = get_all_models_from_module(models_module)
    
    print(f"[INFO] Found {len(models)} tables in models")
    
    # Dictionary to store all sheets
    sheets = {}
    
    # Create a summary sheet
    if include_summary:
        summary_data = []
        for table_name in sorted(models.keys()):
            model_class = models[table_name]
            columns = get_table_columns_from_model(model_class)
            primary_keys = get_primary_keys_from_model(model_class)
            
            summary_data.append({
                'Table Name': table_name,
                'Column Count': len(columns),
                'Primary Keys': ', '.join(primary_keys) if primary_keys else 'None',
                'Columns': ', '.join(columns)
            })
        
        summary_df = pd.DataFrame(summary_data)
        sheets['Summary'] = summary_df
        print(f"[OK] Created Summary sheet with {len(summary_data)} tables")
    
    # Create a sheet for each table with column headers
    for table_name in sorted(models.keys()):
        model_class = models[table_name]
        columns = get_table_columns_from_model(model_class)
        
        if columns:
            # Create empty DataFrame with column headers
            df = pd.DataFrame(columns=columns)
            sheets[table_name] = df
            print(f"[OK] Created sheet: {table_name} ({len(columns)} columns)")
        else:
            print(f"[WARN] No columns found for table: {table_name}")
    
    # Write Excel file
    print(f"\n[WRITE] Writing Excel file: {output_path}")
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Write summary first if included
        if include_summary and 'Summary' in sheets:
            sheets['Summary'].to_excel(writer, sheet_name='Summary', index=False)
        
        # Write all table sheets
        for sheet_name in sorted([s for s in sheets.keys() if s != 'Summary']):
            sheets[sheet_name].to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"\n[SUCCESS] Excel file generated successfully!")
    print(f"   Output: {output_path}")
    print(f"   Total sheets: {len(sheets)}")
    print(f"   Tables: {len([s for s in sheets.keys() if s != 'Summary'])}")
    print(f"\n[NOTE] This Excel file contains empty sheets with column headers.")
    print(f"       Fill in the data and upload to S3 for Lambda processing.")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Excel template from SQLAlchemy models"
    )
    parser.add_argument(
        '--models-path',
        default='etl/models.py',
        help='Path to models.py file (default: etl/models.py)'
    )
    parser.add_argument(
        '--output',
        default='apollo_template.xlsx',
        help='Output Excel file path (default: apollo_template.xlsx)'
    )
    parser.add_argument(
        '--no-summary',
        action='store_true',
        help='Skip creating summary sheet'
    )
    
    args = parser.parse_args()
    
    models_path = Path(args.models_path)
    if not models_path.exists():
        print(f"[ERROR] Models file not found: {models_path}")
        sys.exit(1)
    
    try:
        generate_excel_from_models(
            str(models_path),
            args.output,
            include_summary=not args.no_summary
        )
    except Exception as e:
        print(f"[ERROR] Failed to generate Excel: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

