from __future__ import annotations

from typing import List, Tuple

import pandas as pd
from sqlalchemy import text
from .db import get_table_columns
from sqlalchemy.engine import Connection


def _filter_fk_violations(conn: Connection, table: str, df: pd.DataFrame) -> pd.DataFrame:
    """Pre-filter DataFrame to remove rows that would cause FK violations."""
    valid_df = df.copy()
    
    # Define FK constraints for known tables
    fk_constraints = {
        'plant_material_purchase_org_supplier': [
            ('material_id', 'material_master', 'material_id'),
            ('supplier_id', 'supplier_master', 'supplier_id'),
            ('plant_id', 'purchaser_plant_master', 'plant_id'),
            ('purchasing_org_id', 'purchasing_organizations', 'purchasing_org_id'),
        ],
        'where_to_use_each_price_type': [
            ('material_id', 'material_master', 'material_id'),
        ]
    }
    
    if table not in fk_constraints:
        return valid_df
    
    for fk_col, ref_table, ref_col in fk_constraints[table]:
        if fk_col not in df.columns:
            continue
            
        try:
            # Get valid IDs from reference table
            valid_ids_result = conn.execute(text(f"SELECT DISTINCT {ref_col} FROM {ref_table}"))
            valid_ids = {str(row[0]) for row in valid_ids_result.fetchall()}
            
            # Log FK validation results
            if len(valid_ids) == 0:
                print(f"Warning: {ref_table} table is empty - all {fk_col} references will be invalid")
            
            # Filter DataFrame to only include valid foreign key values
            initial_count = len(valid_df)
            valid_df = valid_df[valid_df[fk_col].astype(str).isin(valid_ids)]
            filtered_count = initial_count - len(valid_df)
            
            if filtered_count > 0:
                print(f"Filtered {filtered_count} rows with invalid {fk_col} references")
                
        except Exception as e:
            print(f"Warning: Could not validate FK {fk_col} -> {ref_table}.{ref_col}: {e}")
            continue
    
    return valid_df


def stage_and_upsert(conn: Connection, table: str, df: pd.DataFrame, pk_cols: List[str], replace: bool = False, allow_fk_violations: bool = False) -> Tuple[int, int, int, pd.DataFrame]:
    if df.empty:
        return 0, 0, 0, pd.DataFrame()

    # Create staging table matching target schema
    stg = f"stg_{table}"
    conn.execute(text(f"DROP TABLE IF EXISTS {stg}"))
    conn.execute(text(f"CREATE TEMP TABLE {stg} AS SELECT * FROM {table} WITH NO DATA"))

    # Restrict DataFrame to only columns that exist in target table
    target_cols = set(get_table_columns(conn, table))
    df_cols = [c for c in df.columns if c in target_cols]
    if not df_cols:
        return 0, 0, 0, pd.DataFrame()
    df = df[df_cols]

    # Bulk insert into staging
    df.to_sql(stg, conn, if_exists='append', index=False)

    if replace:
        # Truncate target before merge to get a clean replace while preserving constraints
        conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))

    # Pre-filter FK violations AFTER truncation if requested
    original_count = len(df)
    rejected_count = 0
    rejected_df = pd.DataFrame()
    
    if allow_fk_violations:
        # Keep original df for rejected rows
        original_df = df.copy()
        valid_df = _filter_fk_violations(conn, table, df)
        rejected_count = original_count - len(valid_df)
        
        if valid_df.empty:
            print(f"All rows filtered out due to FK violations for {table}")
            rejected_df = original_df.copy()
            rejected_df['rejection_reason'] = 'Foreign key violation - referenced ID not found in master table'
            return 0, 0, rejected_count, rejected_df
        
        # Use only valid rows for staging - clear and repopulate staging
        df = valid_df
        conn.execute(text(f"TRUNCATE {stg}"))
        df.to_sql(stg, conn, if_exists='append', index=False)
        
        if rejected_count > 0:
            print(f"Filtered out {rejected_count} rows with FK violations for {table}")
            # Create rejected DataFrame from original data not in valid set
            rejected_indices = original_df.index.difference(valid_df.index)
            rejected_df = original_df.loc[rejected_indices].copy()
            rejected_df['rejection_reason'] = 'Foreign key violation - referenced ID not found in master table'

    cols = list(df.columns)
    insert_cols = ", ".join([f'"{c}"' for c in cols])
    select_cols = ", ".join([f'"{c}"' for c in cols])
    conflict = ", ".join([f'"{c}"' for c in pk_cols])
    set_clause = ", ".join([f'"{c}" = EXCLUDED."{c}"' for c in cols if c not in pk_cols])

    # Standard upsert
    sql = text(
        f"""
        INSERT INTO {table} ({insert_cols})
        SELECT {select_cols} FROM {stg}
        ON CONFLICT ({conflict}) DO UPDATE SET {set_clause}
        RETURNING xmax = 0 AS inserted;
        """
    )
    result = conn.execute(sql).fetchall()
    inserted = sum(1 for r in result if r[0])
    updated = len(result) - inserted
    
    return inserted, updated, rejected_count, rejected_df

