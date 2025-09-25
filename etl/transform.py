from __future__ import annotations

from typing import Dict, List, Tuple

import pandas as pd
import json
from pandas import ExcelFile


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].astype(str).str.strip()
    return df


def apply_column_renames(df: pd.DataFrame, renames: Dict[str, str]) -> pd.DataFrame:
    # renames: excel_col -> target_col
    return df.rename(columns=renames)


def convert_to_json_array(text_value) -> str:
    """Convert comma-separated text to JSON array format."""
    if pd.isna(text_value) or text_value in ("", "nan", "NaN"):
        return None
    
    # Split by comma and clean up
    items = [item.strip() for item in str(text_value).split(',') if item.strip()]
    return json.dumps(items) if items else None


def auto_generate_missing_keys(df: pd.DataFrame, pk_cols: List[str], table_name: str) -> pd.DataFrame:
    """Auto-generate missing primary keys for specific tables."""
    df = df.copy()
    
    # Tables that support auto-generated primary keys
    auto_gen_tables = {
        'settings_user_material_category': 'user_material_category_id',
        'tile_cost_sheet_chemical_reaction_master_data': 'm_cr_rrm_id',
        'where_to_use_each_price_type': 'porg_material_price_type_id',
        'plant_material_purchase_org_supplier': 'porg_plant_material_id',
        'user_currency_preference': 'user_id'
    }
    
    if table_name in auto_gen_tables:
        pk_col = auto_gen_tables[table_name]
        if pk_col in pk_cols and pk_col in df.columns:
            # Find rows with missing primary keys
            missing_mask = df[pk_col].isna() | (df[pk_col] == "") | (df[pk_col] == "nan")
            if missing_mask.any():
                # Generate sequential IDs starting from 1
                missing_count = missing_mask.sum()
                generated_ids = list(range(1, missing_count + 1))
                df.loc[missing_mask, pk_col] = generated_ids
                # Ensure the column is proper integer type
                df[pk_col] = df[pk_col].astype('Int64')
                print(f"Auto-generated {missing_count} IDs for {table_name}.{pk_col}")
    
    return df


def split_valid_invalid(df: pd.DataFrame, pk_cols: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """Split dataframe into valid and invalid rows based on primary key presence."""
    if df.empty:
        return df, df.iloc[0:0], []
    
    # Check for missing primary keys
    valid_mask = True
    for col in pk_cols:
        if col in df.columns:
            valid_mask = valid_mask & df[col].notna() & (df[col] != "") & (df[col] != "nan")
    
    valid_df = df[valid_mask].copy()
    invalid_df = df[~valid_mask].copy()
    
    reasons = []
    for idx in invalid_df.index:
        missing_cols = [col for col in pk_cols if col in df.columns and (pd.isna(df.loc[idx, col]) or df.loc[idx, col] in ("", "nan"))]
        if missing_cols:
            reasons.append(f"Missing required data in columns: {missing_cols} (Row {idx})")
    
    return valid_df, invalid_df, reasons


def apply_json_transforms(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """Apply JSON transformations for specific table columns."""
    df = df.copy()
    
    # Define JSON column mappings per table
    json_transforms = {
        'uom_master': ['synonyms'],
        'repeat_master': ['repeat_choices']
    }
    
    if table_name in json_transforms:
        for col in json_transforms[table_name]:
            if col in df.columns:
                df[col] = df[col].apply(convert_to_json_array)
                print(f"Applied JSON transform to {table_name}.{col}")
    
    return df


def apply_uom_conversion_transforms(df: pd.DataFrame) -> pd.DataFrame:
    """Handle special conversion factors for uom_conversion table."""
    if 'conversion_factor' not in df.columns:
        return df
    
    # Create syn column if it doesn't exist
    if 'syn' not in df.columns:
        df['syn'] = None
    
    def process_conversion_factor(row):
        factor = str(row['conversion_factor']).strip()
        
        # Check if it's a formula/special text (contains letters or special chars beyond numbers and decimal)
        if any(char in factor for char in ['=', '°', '×', '÷', '(', ')', '+', '-', 'K', 'C', 'F']) or \
           any(word in factor for word in ['Depends', 'Varies', 'substance', 'pack', 'box']):
            # Move to syn column and set conversion_factor to 0 (NOT NULL constraint)
            row['syn'] = factor
            row['conversion_factor'] = 0.0
        else:
            # Try to clean numeric values
            try:
                # Handle scientific notation variations
                factor_clean = factor.replace('×', 'e').replace('⁻', '-').replace(' - 10', 'e-')
                # Try to convert to float to validate it's numeric
                float(factor_clean)
                row['conversion_factor'] = factor_clean
            except ValueError:
                # If can't convert to number, move to syn
                row['syn'] = factor
                row['conversion_factor'] = 0.0
        
        return row
    
    # Apply the transformation
    df = df.apply(process_conversion_factor, axis=1)
    
    return df


def map_purchasing_org_name_to_id(df: pd.DataFrame, excel_path: str) -> pd.DataFrame:
    """Map purchasing_org_id values that are names/descriptions to their numeric/string IDs
    using the `purchasing_organizations` sheet. Leaves values as-is if already IDs.
    """
    if 'purchasing_org_id' not in df.columns:
        return df

    df = df.copy()
    try:
        xl = ExcelFile(excel_path)
        candidate_sheets = ['purchasing_organizations', 'Purchasing_Organizations', 'purchasing org']
        sheet_name = next((s for s in candidate_sheets if s in xl.sheet_names), None)
        if not sheet_name:
            return df

        porg = pd.read_excel(xl, sheet_name=sheet_name)
        porg.columns = [str(c).strip() for c in porg.columns]

        id_col = next((c for c in porg.columns if c.lower() == 'purchasing_org_id'), None)
        desc_col = next((c for c in porg.columns if c.lower() in ('purchasing_org_desc', 'purchasing_org_name')), None)
        if not id_col:
            return df

        # Build mapping from description/name -> id
        mapping = {}
        if desc_col:
            mapping = porg[[desc_col, id_col]].dropna().drop_duplicates().set_index(desc_col)[id_col].to_dict()

        def _map_val(val):
            if pd.isna(val) or val in ("", "nan", "NaN"):
                return None
            s = str(val).strip()
            # If it already matches an existing ID in the sheet, keep it
            if s in set(porg[id_col].astype(str)):
                return s
            # Otherwise try mapping by description/name
            return str(mapping.get(s, s))

        df['purchasing_org_id'] = df['purchasing_org_id'].apply(_map_val)
        return df
    except Exception:
        return df


def map_material_type_desc_to_id(df: pd.DataFrame, excel_path: str) -> pd.DataFrame:
    """Map material_type text to material_type_id using Material_Type_Master sheet.
    Always ensure material_type_id exists with detailed logging.
    """
    if 'material_type_id' not in df.columns:
        return df

    df = df.copy()
    
    try:
        xl = ExcelFile(excel_path)
        candidate_sheets = ['Material_Type_Master', 'Material Type Master', 'material_type_master']
        sheet_name = next((s for s in candidate_sheets if s in xl.sheet_names), None)
        if not sheet_name:
            print(f"Warning: No material type master sheet found in {candidate_sheets}")
            return df
            
        mtm = pd.read_excel(xl, sheet_name=sheet_name)
        mtm.columns = [str(c).strip() for c in mtm.columns]
        id_col = next((c for c in mtm.columns if c.lower() == 'material_type_master_id'), None)
        desc_col = next((c for c in mtm.columns if c.lower() == 'material_type_master_desc'), None)
        if not id_col or not desc_col:
            print(f"Warning: Expected columns not found in {sheet_name}: {list(mtm.columns)}")
            return df
            
        mapping = mtm[[desc_col, id_col]].dropna().drop_duplicates().set_index(desc_col)[id_col].to_dict()
        print(f"Material type mapping: {mapping}")
        
        mapped_count = 0
        unmapped_values = set()
        
        def _map_val(val):
            nonlocal mapped_count, unmapped_values
            if pd.isna(val):
                return None
            try:
                return int(val)
            except Exception:
                pass
            mapped_id = mapping.get(str(val).strip(), None)
            if mapped_id is not None:
                mapped_count += 1
                return mapped_id
            else:
                unmapped_values.add(str(val).strip())
                return None

        df['material_type_id'] = df['material_type_id'].apply(_map_val)
        print(f"Material type mapping results: {mapped_count} mapped, {len(unmapped_values)} unmapped: {unmapped_values}")
        return df
        
    except Exception as e:
        print(f"Error in material type mapping: {e}")
        if 'material_type_id' in df.columns:
            df['material_type_id'] = None
        return df


def map_location_type_desc_to_id(df: pd.DataFrame, excel_path: str) -> pd.DataFrame:
    """Map location_Type text to numeric location_type_id using Location_Type_Master sheet."""
    if 'location_type_id' not in df.columns:
        return df
    try:
        xl = ExcelFile(excel_path)
        candidate_sheets = ['Location_Type_Master', 'Location Type Master', 'location_type_master']
        sheet_name = next((s for s in candidate_sheets if s in xl.sheet_names), None)
        if not sheet_name:
            return df
        ltm = pd.read_excel(xl, sheet_name=sheet_name)
        ltm.columns = [str(c).strip() for c in ltm.columns]
        id_col = next((c for c in ltm.columns if c.lower() == 'location_type_id'), None)
        desc_col = next((c for c in ltm.columns if c.lower() == 'location_type_desc'), None)
        if not id_col or not desc_col:
            return df
        mapping = ltm[[desc_col, id_col]].dropna().drop_duplicates().set_index(desc_col)[id_col].to_dict()
        def _map_val(val):
            if pd.isna(val):
                return None
            try:
                return int(val)
            except Exception:
                return mapping.get(str(val).strip(), None)
        df = df.copy()
        df['location_type_id'] = df['location_type_id'].apply(_map_val)
        return df
    except Exception:
        return df


def coerce_types_for_table(df: pd.DataFrame, types_cfg: Dict[str, str]) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    ok_rows = []
    rej_rows = []
    reasons: List[str] = []
    for idx, row in df.iterrows():
        rec = row.to_dict()
        try:
            for col, want in types_cfg.items():
                if col not in rec:
                    continue
                val = rec[col]
                # Handle empty/null values
                if val in (None, "", "nan", "NaN") or pd.isna(val):
                    rec[col] = None
                    continue
                if want == 'int':
                    rec[col] = int(str(val).replace(",", ""))
                elif want == 'float':
                    rec[col] = float(str(val).replace(",", ""))
                elif want == 'date':
                    # Handle extreme dates that cause overflow
                    try:
                        # Special handling for 9999-12-31 (common "end of time" value)
                        if isinstance(val, str) and '9999-12-31' in val:
                            # Create a date object directly for 9999-12-31
                            from datetime import date
                            rec[col] = date(9999, 12, 31)
                        elif hasattr(val, 'year') and val.year == 9999:
                            # Handle datetime objects with year 9999
                            from datetime import date
                            rec[col] = date(val.year, val.month, val.day)
                        else:
                            parsed_date = pd.to_datetime(val)
                            # Check for extreme dates (beyond pandas limits)
                            if parsed_date.year > 2200:
                                rec[col] = None  # Set extreme dates to NULL
                            else:
                                rec[col] = parsed_date.date()
                    except (pd.errors.OutOfBoundsDatetime, ValueError):
                        # Try to handle 9999 dates manually
                        if hasattr(val, 'year') and val.year == 9999:
                            from datetime import date
                            rec[col] = date(val.year, val.month, val.day)
                        else:
                            rec[col] = None  # Set invalid dates to NULL
                else:
                    rec[col] = str(val)
            ok_rows.append(rec)
        except Exception as e:
            rej_rows.append(row)
            reasons.append(f"Type coercion failed for row {idx}: {str(e)}")
    ok_df = pd.DataFrame(ok_rows) if ok_rows else df.iloc[0:0]
    rej_df = pd.DataFrame(rej_rows) if rej_rows else df.iloc[0:0]
    return ok_df, rej_df, reasons