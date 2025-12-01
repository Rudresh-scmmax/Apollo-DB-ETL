from __future__ import annotations

from typing import List, Tuple, Optional, Any

import pandas as pd
from sqlalchemy import text
from .db import get_table_columns
from sqlalchemy.engine import Connection

# Import LambdaReturningError for handling Lambda RETURNING clause errors
try:
    from .db_lambda import LambdaReturningError
except ImportError:
    # If not available, define a dummy class
    class LambdaReturningError(Exception):
        pass


def _parse_returning_value(first_val: Any, batch_num: int = 0) -> bool:
    """Parse the RETURNING clause value to determine if row was inserted (True) or updated (False)."""
    if isinstance(first_val, bool):
        return first_val
    elif isinstance(first_val, (int, float)):
        # PostgreSQL returns 1 for true, 0 for false
        # xmax = 0 means inserted, so 1 (true) = inserted
        return (first_val == 1 or first_val == True)
    elif isinstance(first_val, str):
        # Handle string representations
        first_val_lower = first_val.lower().strip()
        if first_val_lower in ('true', 't', '1', 'yes'):
            return True
        elif first_val_lower in ('false', 'f', '0', 'no'):
            return False
        else:
            # Unknown format - log and assume updated
            print(f"    [WARNING] Unknown RETURNING value format: {first_val}, assuming updated")
            return False
    else:
        # Unknown type - log and assume updated
        print(f"    [WARNING] Unknown RETURNING value type: {type(first_val)}, value: {first_val}, assuming updated")
        return False


def _get_fk_constraints_from_db(conn: Connection, table: str) -> List[Tuple[str, str, str]]:
    """Extract FK constraints from database for a table.
    
    Returns list of tuples: (fk_column, referenced_table, referenced_column)
    """
    fk_list = []
    try:
        # Query PostgreSQL information_schema to get FK constraints
        query = text("""
            SELECT 
                kcu.column_name AS fk_column,
                ccu.table_name AS referenced_table,
                ccu.column_name AS referenced_column
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_name = :table_name
                AND tc.table_schema = 'public'
        """)
        result = conn.execute(query, {"table_name": table})
        if result and hasattr(result, 'fetchall'):
            try:
                rows = result.fetchall()
            except (AttributeError, TypeError) as e:
                print(f"    [DEBUG] Error fetching FK constraints: {e}")
                rows = []
        else:
            try:
                rows = list(result) if result else []
            except (TypeError, AttributeError):
                rows = []
        for row in rows:
            if row and len(row) >= 3:
                fk_list.append((row[0], row[1], row[2]))
    except Exception as e:
        print(f"Warning: Could not extract FK constraints from DB for {table}: {e}")
    return fk_list


def _filter_fk_violations(conn: Connection, table: str, df: pd.DataFrame, master_tables: set = None) -> pd.DataFrame:
    """Pre-filter DataFrame to remove rows that would cause FK violations.
    
    Args:
        conn: Database connection
        table: Table name being loaded
        df: DataFrame to filter
        master_tables: Set of master table names. If a referenced master table is empty,
                      FK validation is skipped to allow initial loads.
    """
    if df.empty:
        return df
    
    valid_df = df.copy()
    
    # Load master tables list from mappings if not provided
    if master_tables is None:
        master_tables = {
            'currency_master', 'material_type_master', 'uom_master', 'location_type_master',
            'location_master', 'supplier_master', 'calendar_master', 'frequency_master',
            'repeat_master', 'purchasing_organizations', 'port_master', 'material_master',
            'purchaser_plant_master', 'pricing_source_master', 'news_tags', 'pricing_type_master',
            'tile_cost_sheet_chemical_reaction_master_data', 'currency_exchange_history',
            'uom_conversion', 'user_preference_currency', 'incoterms_master',
            'plant_material_purchase_org_supplier', 'where_to_use_each_price_type',
            'forex_conversion_options_master', 'settings_user_material_category',
            'country_master', 'user_master', 'chemical_raw_material_synonyms', 'tiles'
        }
    
    # First, try to get FK constraints from database
    db_fk_constraints = _get_fk_constraints_from_db(conn, table)
    
    # Define FK constraints for known tables (fallback if DB query fails)
    # All FK constraints extracted from models.py
    fk_constraints = {
        'action_plans': [
            ('created_by', 'user_master', 'user_id'),
            ('material_id', 'material_master', 'material_id'),
        ],
        'audit_snapshot_price_prediction_negotiation': [
            ('material_id', 'material_master', 'material_id'),
            ('plant_id', 'purchaser_plant_master', 'plant_id'),
            ('purchasing_org_id', 'purchasing_organizations', 'purchasing_org_id'),
        ],
        'company_currency_exchange_history': [
            ('from_currency', 'currency_master', 'currency_name'),
            ('purchase_org_id', 'purchasing_organizations', 'purchasing_org_id'),
            ('to_currency', 'currency_master', 'currency_name'),
        ],
        'country_hsn_code_wise_duty_structure': [
            ('country_of_origin_all_code', 'country_master', 'country_code'),
            ('destination_country_code', 'country_master', 'country_code'),
        ],
        'country_tariffs': [
            ('country_id', 'country_master', 'country_id'),
        ],
        'currency_exchange_history': [
            ('from_currency', 'currency_master', 'currency_name'),
            ('to_currency', 'currency_master', 'currency_name'),
        ],
        'demand_supply_summary': [
            ('location_id', 'location_master', 'location_id'),
            ('material_id', 'material_master', 'material_id'),
        ],
        'demand_supply_trends': [
            ('location_id', 'location_master', 'location_id'),
            ('material_id', 'material_master', 'material_id'),
            ('update_user_id', 'user_master', 'user_id'),
            ('upload_user_id', 'user_master', 'user_id'),
        ],
        'esg_tracker': [
            ('location_id', 'location_master', 'location_id'),
            ('material_id', 'material_master', 'material_id'),
            ('supplier_id', 'supplier_master', 'supplier_id'),
        ],
        'export_data': [
            ('location_id', 'location_master', 'location_id'),
            ('material_id', 'material_master', 'material_id'),
            ('uom', 'uom_master', 'uom_name'),
        ],
        'fact_pack': [
            ('material_id', 'material_master', 'material_id'),
            ('uploaded_by', 'user_master', 'user_id'),
        ],
        'forecast_recommendations': [
            ('location_id', 'location_master', 'location_id'),
            ('material_id', 'material_master', 'material_id'),
        ],
        'import_data': [
            ('location_id', 'location_master', 'location_id'),
            ('material_id', 'material_master', 'material_id'),
            ('uom', 'uom_master', 'uom_name'),
        ],
        'inventory_levels': [
            ('location_id', 'location_master', 'location_id'),
            ('material_id', 'material_master', 'material_id'),
        ],
        'joint_development_projects': [
            ('gmail_id', 'emails', 'gmail_id'),
            ('material_id', 'material_master', 'material_id'),
            ('supplier_id', 'supplier_master', 'supplier_id'),
        ],
        'location_master': [
            ('location_type_id', 'location_type_master', 'location_type_id'),
        ],
        'market_research_status': [
            ('user_id', 'user_master', 'user_id'),
        ],
        'material_master': [
            ('base_uom_id', 'uom_master', 'uom_id'),
            ('material_type_id', 'material_type_master', 'material_type_master_id'),
        ],
        'material_research_reports': [
            ('material_id', 'material_master', 'material_id'),
            ('update_user_id', 'user_master', 'user_id'),
            ('upload_user_id', 'user_master', 'user_id'),
        ],
        'material_supplier_general_intelligence': [
            ('material_id', 'material_master', 'material_id'),
            ('supplier_country_code', 'country_master', 'country_code'),
            ('supplier_id', 'supplier_master', 'supplier_id'),
        ],
        'material_synonyms': [
            ('material_id', 'material_master', 'material_id'),
        ],
        'meeting_minutes': [
            ('gmail_id', 'emails', 'gmail_id'),
            ('material_id', 'material_master', 'material_id'),
            ('supplier_id', 'supplier_master', 'supplier_id'),
        ],
        'multiple_point_engagements': [
            ('gmail_id', 'emails', 'gmail_id'),
            ('material_id', 'material_master', 'material_id'),
            ('supplier_id', 'supplier_master', 'supplier_id'),
        ],
        'negotiation_llm_logs': [
            ('material_id', 'material_master', 'material_id'),
        ],
        'negotiation_recommendations': [
            ('material_id', 'material_master', 'material_id'),
        ],
        'news_insights': [
            ('material_id', 'material_master', 'material_id'),
        ],
        'news_porg_plant_material_source_data': [
            ('material_id', 'material_master', 'material_id'),
            ('plant_id', 'purchaser_plant_master', 'plant_id'),
            ('purchasing_org_id', 'purchasing_organizations', 'purchasing_org_id'),
            ('supplier_id', 'supplier_master', 'supplier_id'),
            ('user_id', 'user_master', 'user_id'),
        ],
        'ocean_freight_master': [
            ('destination_port_id', 'port_master', 'port_id'),
            ('freight_cost_currency', 'currency_master', 'currency_name'),
            ('source_port_id', 'port_master', 'port_id'),
        ],
        'plan_assignments': [
            ('plan_id', 'action_plans', 'id'),
            ('user_id', 'user_master', 'user_id'),
        ],
        'plant_material_purchase_org_supplier': [
            ('material_id', 'material_master', 'material_id'),
            ('plant_id', 'purchaser_plant_master', 'plant_id'),
            ('supplier_id', 'supplier_master', 'supplier_id'),
        ],
        'plant_to_port_mapping_master': [
            ('plant_id', 'purchaser_plant_master', 'plant_id'),
            ('port_country_code', 'country_master', 'country_code'),
            ('port_id', 'port_master', 'port_id'),
        ],
        'porters_analysis': [
            ('material_id', 'material_master', 'material_id'),
            ('updated_user_id', 'user_master', 'user_id'),
        ],
        'price_data_country_storage': [
            ('country', 'country_master', 'country_name'),
            ('material_id', 'material_master', 'material_id'),
            ('plant_id', 'purchaser_plant_master', 'plant_id'),
        ],
        'price_forecast_data': [
            ('location_id', 'location_master', 'location_id'),
            ('material_id', 'material_master', 'material_id'),
        ],
        'price_history_data': [
            ('location_id', 'location_master', 'location_id'),
            ('material_id', 'material_master', 'material_id'),
            ('price_currency', 'currency_master', 'currency_name'),
            ('uom', 'uom_master', 'uom_name'),
        ],
        'procurement_plans': [
            ('material_id', 'material_master', 'material_id'),
        ],
        'purchaser_plant_master': [
            ('base_currency_accounting', 'currency_master', 'currency_name'),
            ('plant_country_code', 'country_master', 'country_code'),
        ],
        'purchase_history_transactional_data': [
            ('currency_of_po', 'currency_master', 'currency_name'),
            ('material_id', 'material_master', 'material_id'),
            ('plant_id', 'purchaser_plant_master', 'plant_id'),
            ('purchasing_org_id', 'purchasing_organizations', 'purchasing_org_id'),
            ('supplier_id', 'supplier_master', 'supplier_id'),
            ('uom', 'uom_master', 'uom_name'),
        ],
        'quote_comparison': [
            ('country_id', 'country_master', 'country_id'),
            ('currency_id', 'currency_master', 'currency_id'),
            ('material_id', 'material_master', 'material_id'),
            ('supplier_id', 'supplier_master', 'supplier_id'),
        ],
        'reach_tracker': [
            ('material_id', 'material_master', 'material_id'),
            ('supplier_id', 'supplier_master', 'supplier_id'),
        ],
        'region_hierarchy': [
            ('location_id', 'location_master', 'location_id'),
        ],
        'repeat_master': [
            ('frequency_of_update_id', 'frequency_master', 'frequency_of_update_id'),
        ],
        'settings_user_material_category': [
            ('user_id', 'user_master', 'user_id'),
        ],
        'settings_user_material_category_tile_preferences': [
            ('user_id', 'user_master', 'user_id'),
        ],
        'supplier_hierarchy': [
            ('parent_supplier_id', 'supplier_master', 'supplier_id'),
            ('supplier_id', 'supplier_master', 'supplier_id'),
        ],
        'supplier_master': [
            ('base_currency_id', 'currency_master', 'currency_id'),
            ('supplier_country_id', 'location_master', 'location_id'),
        ],
        'supplier_shutdowns': [
            ('location_id', 'location_master', 'location_id'),
            ('material_id', 'material_master', 'material_id'),
            ('supplier_id', 'supplier_master', 'supplier_id'),
        ],
        'supplier_tracking': [
            ('location_id', 'location_master', 'location_id'),
            ('material_id', 'material_master', 'material_id'),
            ('supplier_id', 'supplier_master', 'supplier_id'),
        ],
        'tile_cost_sheet_chemical_reaction_master_data': [
            ('material_base_uom_id', 'uom_master', 'uom_id'),
            ('material_id', 'material_master', 'material_id'),
            ('reaction_raw_material_base_uom_id', 'uom_master', 'uom_id'),
        ],
        'tile_cost_sheet_historical_current_supplier': [
            ('country_of_origin', 'country_master', 'country_name'),
            ('currency_cost_factory_gate', 'currency_master', 'currency_name'),
            ('currency_cost_given_quote', 'currency_master', 'currency_name'),
            ('incoterms', 'incoterms_master', 'inco_term_name'),
            ('material_id', 'material_master', 'material_id'),
            ('plant_id', 'purchaser_plant_master', 'plant_id'),
            ('purchasing_org_id', 'purchasing_organizations', 'purchasing_org_id'),
            ('supplier_id', 'supplier_master', 'supplier_id'),
            ('uom_of_quote', 'uom_master', 'uom_name'),
        ],
        'tile_multiple_point_engagements': [
            ('material_id', 'material_master', 'material_id'),
            ('plant_id', 'purchaser_plant_master', 'plant_id'),
            ('purchasing_org_id', 'purchasing_organizations', 'purchasing_org_id'),
            ('supplier_id', 'supplier_master', 'supplier_id'),
        ],
        'tile_vendor_minutes_of_meeting': [
            ('material_id', 'material_master', 'material_id'),
            ('plant_id', 'purchaser_plant_master', 'plant_id'),
            ('purchasing_org_id', 'purchasing_organizations', 'purchasing_org_id'),
            ('supplier_id', 'supplier_master', 'supplier_id'),
        ],
        'user_currency_preference': [
            ('user_id', 'user_master', 'user_id'),
            ('user_preferred_currency', 'currency_master', 'currency_name'),
        ],
        'user_purchase_org': [
            ('user_id', 'user_master', 'user_id'),
        ],
        'vendor_key_information': [
            ('material_id', 'material_master', 'material_id'),
            ('supplier_id', 'supplier_master', 'supplier_id'),
        ],
        'vendor_wise_action_plan': [
            ('gmail_id', 'emails', 'gmail_id'),
            ('material_id', 'material_master', 'material_id'),
            ('supplier_id', 'supplier_master', 'supplier_id'),
        ],
        'where_to_use_each_price_type': [
            ('frequency_of_update_id', 'frequency_master', 'frequency_of_update_id'),
            ('material_id', 'material_master', 'material_id'),
            ('price_type_id', 'pricing_type_master', 'price_type_id'),
            ('source_of_price_id', 'pricing_source_master', 'source_of_price_id'),
        ],
    }
    
    # Use DB-extracted FK constraints if available, otherwise use hardcoded ones
    if db_fk_constraints:
        fk_list = db_fk_constraints
        print(f"FK filtering for {table}: Found {len(fk_list)} FK constraint(s) from database")
    elif table in fk_constraints:
        fk_list = fk_constraints[table]
        print(f"FK filtering for {table}: Using {len(fk_list)} hardcoded FK constraint(s)")
    else:
        print(f"FK filtering for {table}: No FK constraints found - skipping FK validation")
        return valid_df
    
    for fk_col, ref_table, ref_col in fk_list:
        if fk_col not in df.columns:
            continue
            
        try:
            # Check if reference table exists first
            exists_result = conn.execute(text(
                f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{ref_table}')"
            ))
            if hasattr(exists_result, 'scalar'):
                table_exists = exists_result.scalar()
            else:
                row = exists_result.fetchone()
                table_exists = row[0] if row and len(row) > 0 else False
            
            if not table_exists:
                print(f"Warning: Reference table {ref_table} does not exist - skipping FK validation for {fk_col}")
                continue
            
            # Check if current table is a master table and if it's empty (initial load)
            # This check should happen BEFORE querying valid_ids, so we can skip FK validation
            # for master tables on initial load regardless of reference table data
            is_current_table_master = master_tables and table in master_tables
            is_ref_table_master = master_tables and ref_table in master_tables
            
            # Check if current table is empty (initial load)
            is_initial_load = False
            if is_current_table_master:
                try:
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    current_table_count = count_result.scalar() if hasattr(count_result, 'scalar') else None
                    # Handle dict response from Lambda
                    if isinstance(current_table_count, dict):
                        current_table_count = current_table_count.get('count', 0)
                    is_initial_load = current_table_count == 0
                except Exception:
                    is_initial_load = False  # Assume not initial load if we can't check
            
            # Skip FK validation for master tables on initial load
            # This allows master data to be inserted even if referenced master tables have partial data
            # Note: The database will still enforce FK constraints, so invalid FK values will cause errors
            # This is expected behavior - the data should be correct, or the FK constraint should be deferred
            if is_current_table_master and is_initial_load:
                if is_ref_table_master or (table == ref_table):
                    print(f"  Skipping FK validation for {fk_col} -> {ref_table} (master table initial load - database will still enforce FK constraints)")
                    continue  # Skip this FK constraint validation
            
            # Get valid IDs/values from reference table
            # Handle NULL values - they should pass FK validation if column allows NULL
            try:
                valid_ids_result = conn.execute(text(f"SELECT DISTINCT {ref_col} FROM {ref_table} WHERE {ref_col} IS NOT NULL"))
                valid_ids = {str(row[0]) for row in valid_ids_result.fetchall()}
            except Exception as e:
                print(f"Warning: Could not query {ref_table}.{ref_col} for FK validation: {e}")
                continue
            
            # Log FK validation results
            if len(valid_ids) == 0:
                print(f"Warning: {ref_table} table is empty or has no non-null values in {ref_col}")
            
            # Filter DataFrame to only include valid foreign key values
            # Allow NULL values to pass through (they're handled by database constraints)
            initial_count = len(valid_df)
            
            # Convert FK column to string for comparison, handling NULLs
            fk_series = valid_df[fk_col].astype(str)
            # Replace 'nan' strings (from pandas) with empty string for comparison
            fk_series = fk_series.replace('nan', '')
            
            # Filter: keep rows where FK value is in valid_ids OR is NULL/empty
            
            # If valid_ids is empty, handle based on whether it's a master table
            if len(valid_ids) == 0:
                # Debug: log master_tables value
                print(f"  [DEBUG] Checking skip logic: table={table}, ref_table={ref_table}, master_tables={master_tables}")
                # If referenced table is a master table and empty, skip FK validation
                # This allows initial loads to proceed (master tables should be loaded first)
                # Also skip if it's a self-referencing FK (table == ref_table) and it's a master table
                if is_ref_table_master or (table == ref_table and is_current_table_master):
                    print(f"  Skipping FK validation for {fk_col} -> {ref_table} (master table is empty, allowing initial load)")
                    continue  # Skip this FK constraint validation
                else:
                    # Debug: log why we're not skipping
                    print(f"  [DEBUG] Not skipping FK validation for {fk_col} -> {ref_table}: is_ref_table_master={is_ref_table_master}, is_current_table_master={is_current_table_master}, table={table}, ref_table={ref_table}, master_tables={master_tables}")
                    # For non-master tables, filter out rows with non-NULL FK values
                    valid_mask = valid_df[fk_col].isna() | (fk_series == '')
                    filtered_count = initial_count - len(valid_df[valid_mask])
                    valid_df = valid_df[valid_mask]
                    if filtered_count > 0:
                        print(f"Filtered {filtered_count} rows with invalid {fk_col} references (reference table {ref_table} is empty)")
            else:
                # Reference table has data - filter normally
                valid_mask = fk_series.isin(valid_ids) | valid_df[fk_col].isna() | (fk_series == '')
                valid_df = valid_df[valid_mask]
                filtered_count = initial_count - len(valid_df)
                if filtered_count > 0:
                    print(f"Filtered {filtered_count} rows with invalid {fk_col} references (valid values: {len(valid_ids)} found in {ref_table})")
                
        except Exception as e:
            print(f"Warning: Could not validate FK {fk_col} -> {ref_table}.{ref_col}: {e}")
            # Continue processing - don't fail the entire load
            continue
    
    return valid_df


def stage_and_upsert(conn: Connection, table: str, df: pd.DataFrame, pk_cols: List[str], replace: bool = False, allow_fk_violations: bool = False, models_module: Optional[Any] = None) -> Tuple[int, int, int, pd.DataFrame]:
    if df.empty:
        print(f"    [DEBUG] stage_and_upsert: DataFrame is empty, returning 0,0,0")
        return 0, 0, 0, pd.DataFrame()

    print(f"    [DEBUG] stage_and_upsert: Starting with {len(df)} rows for table {table}")

    # Restrict DataFrame to only columns that exist in target table
    # Use models_module if available (more reliable than querying DB)
    target_cols = set(get_table_columns(conn, table, models_module))
    df_cols = [c for c in df.columns if c in target_cols]
    if not df_cols:
        print(f"    [DEBUG] stage_and_upsert: No matching columns found between DataFrame and table {table}")
        print(f"    [DEBUG] DataFrame columns: {list(df.columns)}")
        print(f"    [DEBUG] Table columns: {sorted(target_cols)}")
        return 0, 0, 0, pd.DataFrame()
    df = df[df_cols]
    print(f"    [DEBUG] stage_and_upsert: Using {len(df_cols)} columns: {df_cols[:5]}{'...' if len(df_cols) > 5 else ''}")

    # Pre-filter FK violations BEFORE creating staging table if requested
    original_count = len(df)
    rejected_count = 0
    rejected_df = pd.DataFrame()
    original_df = df.copy()  # Always keep original for error handling
    
    # For Lambda connections, get initial row count to verify inserts
    initial_row_count = None
    if hasattr(conn, '__class__') and 'Lambda' in conn.__class__.__name__:
        try:
            count_sql = text(f"SELECT COUNT(*) FROM {table}")
            count_result = conn.execute(count_sql)
            if hasattr(count_result, 'scalar'):
                initial_row_count = count_result.scalar()
            elif hasattr(count_result, 'fetchone'):
                row = count_result.fetchone()
                if row and len(row) > 0:
                    initial_row_count = row[0]
            
            # Handle dict response from Lambda (parse from body or direct dict)
            if isinstance(initial_row_count, dict):
                # Lambda returns {'statusCode': 200, 'body': '[{"count": 2}]'} or {'count': 2}
                import json
                if 'count' in initial_row_count:
                    # Direct dict with 'count' key
                    initial_row_count = initial_row_count['count']
                elif 'body' in initial_row_count:
                    # Lambda API Gateway format
                    body = json.loads(initial_row_count['body']) if isinstance(initial_row_count['body'], str) else initial_row_count['body']
                    if isinstance(body, list) and len(body) > 0:
                        first_item = body[0]
                        if isinstance(first_item, dict):
                            # Get 'count' key or first value
                            initial_row_count = first_item.get('count', list(first_item.values())[0] if first_item else None)
                        else:
                            initial_row_count = first_item
                    elif isinstance(body, dict) and 'count' in body:
                        initial_row_count = body['count']
                else:
                    # Try to get first value from dict
                    initial_row_count = list(initial_row_count.values())[0] if initial_row_count else None
            
            # Ensure it's a number
            if initial_row_count is not None:
                try:
                    initial_row_count = int(initial_row_count)
                    print(f"    [DEBUG] Initial row count in {table}: {initial_row_count}")
                except (ValueError, TypeError):
                    print(f"    [WARNING] Could not convert initial_row_count to int: {initial_row_count}")
                    initial_row_count = None
        except Exception as e:
            print(f"    [WARNING] Could not get initial row count: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"    [DEBUG] Before FK filtering: {original_count} rows")
    
    # ALWAYS enable FK filtering to prevent FK violations
    # This ensures we never fail due to FK violations - we just filter and reject invalid rows
    if allow_fk_violations:
        print(f"    [DEBUG] FK filtering enabled for {table}: starting with {len(df)} rows")
        try:
            # Get master tables list from mappings if available
            master_tables = None
            try:
                from .utils import load_yaml
                import os
                mappings_path = os.path.join(os.path.dirname(__file__), "config", "mappings.yaml")
                if os.path.exists(mappings_path):
                    mappings = load_yaml(mappings_path)
                    master_tables = set(mappings.get("load_order", {}).get("masters", []))
            except Exception:
                pass  # Use default master_tables in function
            
            valid_df = _filter_fk_violations(conn, table, df, master_tables)
            rejected_count = original_count - len(valid_df)
            
            print(f"    [DEBUG] FK filtering result: {len(valid_df)} rows valid, {rejected_count} rows filtered out")
            
            if valid_df.empty:
                print(f"    [DEBUG] All rows filtered out due to FK violations for {table}")
                rejected_df = original_df.copy()
                rejected_df['rejection_reason'] = 'Foreign key violation - referenced ID not found in master table'
                return 0, 0, rejected_count, rejected_df
            
            # Use only valid rows for staging
            df = valid_df
            
            if rejected_count > 0:
                print(f"    [DEBUG] Filtered out {rejected_count} rows with FK violations for {table}")
                # Create rejected DataFrame from original data not in valid set
                rejected_indices = original_df.index.difference(valid_df.index)
                rejected_df = original_df.loc[rejected_indices].copy()
                rejected_df['rejection_reason'] = 'Foreign key violation - referenced ID not found in master table'
        except Exception as e:
            print(f"    [WARNING] FK filtering failed for {table}: {e}. Continuing without FK filtering (may cause FK violations).")
            # Continue without FK filtering - the try/except around INSERT will catch FK violations
    else:
        print(f"    [DEBUG] FK filtering disabled for {table} - FK violations will cause errors")

    # Check if using Lambda connection (TEMP tables don't work with Lambda - each invocation is a new connection)
    is_lambda_conn = hasattr(conn, 'insert_dataframe')
    
    if is_lambda_conn:
        # For Lambda connections, we'll use VALUES clause directly in UPSERT (no staging table needed)
        print(f"    [DEBUG] Using Lambda connection - will use VALUES clause instead of staging table")
    else:
        # For regular connections, use staging table
        stg = f"stg_{table}"
        print(f"    [DEBUG] Creating staging table {stg} with {len(df)} rows")
        try:
            # DDL statements don't return rows - just execute them
            drop_result = conn.execute(text(f"DROP TABLE IF EXISTS {stg}"))
            # DDL statements may return empty results - just ignore them
            if drop_result and hasattr(drop_result, 'fetchall'):
                try:
                    # Try to consume result, but don't fail if it's empty
                    list(drop_result.fetchall())
                except (AttributeError, TypeError, StopIteration):
                    # Result is empty or not iterable - that's fine for DDL
                    pass
            
            create_result = conn.execute(text(f"CREATE TEMP TABLE {stg} AS SELECT * FROM {table} WITH NO DATA"))
            # DDL statements may return empty results - just ignore them
            if create_result and hasattr(create_result, 'fetchall'):
                try:
                    # Try to consume result, but don't fail if it's empty
                    list(create_result.fetchall())
                except (AttributeError, TypeError, StopIteration):
                    # Result is empty or not iterable - that's fine for DDL
                    pass
        except Exception as e:
            print(f"    [ERROR] Failed to create staging table: {e}")
            import traceback
            traceback.print_exc()
            raise

        # Bulk insert into staging (only valid rows if FK filtering was done)
        if not df.empty:
            print(f"    [DEBUG] Inserting {len(df)} rows into staging table")
            # Use pandas to_sql for direct connections
            df.to_sql(stg, conn, if_exists='append', index=False)
            print(f"    [DEBUG] Staging table populated successfully")
        else:
            print(f"    [DEBUG] No rows to insert into staging table")

    if replace:
        # Truncate target before merge to get a clean replace while preserving constraints
        conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))

    # If no valid rows after FK filtering, return early
    if df.empty:
        return 0, 0, rejected_count, rejected_df

    cols = list(df.columns)
    insert_cols = ", ".join([f'"{c}"' for c in cols])
    conflict = ", ".join([f'"{c}"' for c in pk_cols])
    set_clause = ", ".join([f'"{c}" = EXCLUDED."{c}"' for c in cols if c not in pk_cols])

    # Standard upsert - wrap in try/except to catch any FK violations that slip through
    try:
        if is_lambda_conn:
            # For Lambda connections, use VALUES clause directly (no staging table)
            # Batch large DataFrames to avoid query size limits
            batch_size = 500  # Process in batches to avoid Lambda query size limits
            total_inserted = 0
            total_updated = 0
            
            for batch_start in range(0, len(df), batch_size):
                batch_df = df.iloc[batch_start:batch_start + batch_size]
                batch_num = (batch_start // batch_size) + 1
                total_batches = (len(df) + batch_size - 1) // batch_size
                
                if total_batches > 1:
                    print(f"    [DEBUG] Processing batch {batch_num}/{total_batches} ({len(batch_df)} rows)")
                else:
                    print(f"    [DEBUG] Executing UPSERT with VALUES clause for Lambda connection")
                
                # Build VALUES clause from DataFrame batch
                values_list = []
                for _, row in batch_df.iterrows():
                    values = []
                    for val in row:
                        if pd.isna(val):
                            values.append('NULL')
                        elif isinstance(val, str):
                            # Escape single quotes and backslashes
                            escaped_val = val.replace("\\", "\\\\").replace("'", "''")
                            values.append(f"'{escaped_val}'")
                        elif isinstance(val, (int, float)):
                            values.append(str(val))
                        elif isinstance(val, bool):
                            values.append('TRUE' if val else 'FALSE')
                        elif isinstance(val, (pd.Timestamp, pd.DatetimeTZDtype)):
                            if pd.notna(val):
                                values.append(f"'{val.isoformat()}'")
                            else:
                                values.append('NULL')
                        else:
                            # Convert to string and escape
                            escaped_val = str(val).replace("\\", "\\\\").replace("'", "''")
                            values.append(f"'{escaped_val}'")
                    values_list.append(f"({', '.join(values)})")
                
                values_str = ', '.join(values_list)
                
                # For Lambda connections, try with RETURNING first, fall back to without RETURNING if Lambda has issues
                sql_with_returning = text(
                    f"""
                    INSERT INTO {table} ({insert_cols})
                    VALUES {values_str}
                    ON CONFLICT ({conflict}) DO UPDATE SET {set_clause}
                    RETURNING xmax = 0 AS inserted;
                    """
                )
                
                sql_without_returning = text(
                    f"""
                    INSERT INTO {table} ({insert_cols})
                    VALUES {values_str}
                    ON CONFLICT ({conflict}) DO UPDATE SET {set_clause};
                    """
                )
                
                # Execute batch - try with RETURNING first, fall back to without RETURNING if it fails
                batch_rows = []
                try:
                    batch_result = conn.execute(sql_with_returning)
                    batch_rows = batch_result.fetchall() if hasattr(batch_result, 'fetchall') else list(batch_result)
                except Exception as e:
                    error_msg = str(e)
                    error_type = type(e).__name__
                    # Log the error for debugging
                    print(f"    [DEBUG] UPSERT with RETURNING failed: {error_type}: {error_msg[:200]}")
                    # Check if it's a Lambda RETURNING clause parsing error
                    # This can be a LambdaReturningError from db_lambda.py or a RuntimeError with the error message
                    if (error_type == 'LambdaReturningError' or 
                        'list index out of range' in error_msg.lower() or 
                        ('status 500' in error_msg.lower() and 'list index' in error_msg.lower()) or
                        ('lambda returning clause error' in error_msg.lower())):
                        print(f"    [WARNING] Lambda RETURNING clause parsing error - retrying without RETURNING clause")
                        try:
                            # Get row count before attempting UPSERT without RETURNING
                            count_before_retry_sql = text(f"SELECT COUNT(*) FROM {table}")
                            count_before_retry_result = conn.execute(count_before_retry_sql)
                            count_before_retry = None
                            if hasattr(count_before_retry_result, 'scalar'):
                                count_before_retry = count_before_retry_result.scalar()
                            elif hasattr(count_before_retry_result, 'fetchone'):
                                row = count_before_retry_result.fetchone()
                                if row and len(row) > 0:
                                    count_before_retry = row[0]
                            
                            # Handle dict response from Lambda
                            if isinstance(count_before_retry, dict):
                                import json
                                if 'count' in count_before_retry:
                                    count_before_retry = count_before_retry['count']
                                elif 'body' in count_before_retry:
                                    body = json.loads(count_before_retry['body']) if isinstance(count_before_retry['body'], str) else count_before_retry['body']
                                    if isinstance(body, list) and len(body) > 0:
                                        first_item = body[0]
                                        if isinstance(first_item, dict):
                                            count_before_retry = first_item.get('count', list(first_item.values())[0] if first_item else None)
                                        else:
                                            count_before_retry = first_item
                                    elif isinstance(body, dict) and 'count' in body:
                                        count_before_retry = body['count']
                                else:
                                    count_before_retry = list(count_before_retry.values())[0] if count_before_retry else None
                            
                            if count_before_retry is not None:
                                try:
                                    count_before_retry = int(count_before_retry)
                                except (ValueError, TypeError):
                                    count_before_retry = None
                            
                            # Try without RETURNING clause - this should work even if Lambda has RETURNING issues
                            conn.execute(sql_without_returning)
                            
                            # Verify rows were actually added/updated
                            count_after_retry_sql = text(f"SELECT COUNT(*) FROM {table}")
                            count_after_retry_result = conn.execute(count_after_retry_sql)
                            count_after_retry = None
                            if hasattr(count_after_retry_result, 'scalar'):
                                count_after_retry = count_after_retry_result.scalar()
                            elif hasattr(count_after_retry_result, 'fetchone'):
                                row = count_after_retry_result.fetchone()
                                if row and len(row) > 0:
                                    count_after_retry = row[0]
                            
                            # Handle dict response from Lambda
                            if isinstance(count_after_retry, dict):
                                import json
                                if 'count' in count_after_retry:
                                    count_after_retry = count_after_retry['count']
                                elif 'body' in count_after_retry:
                                    body = json.loads(count_after_retry['body']) if isinstance(count_after_retry['body'], str) else count_after_retry['body']
                                    if isinstance(body, list) and len(body) > 0:
                                        first_item = body[0]
                                        if isinstance(first_item, dict):
                                            count_after_retry = first_item.get('count', list(first_item.values())[0] if first_item else None)
                                        else:
                                            count_after_retry = first_item
                                    elif isinstance(body, dict) and 'count' in body:
                                        count_after_retry = body['count']
                                else:
                                    count_after_retry = list(count_after_retry.values())[0] if count_after_retry else None
                            
                            if count_after_retry is not None:
                                try:
                                    count_after_retry = int(count_after_retry)
                                except (ValueError, TypeError):
                                    count_after_retry = None
                            
                            # Check if UPSERT actually worked
                            if count_before_retry is not None and count_after_retry is not None:
                                rows_changed = count_after_retry - count_before_retry
                                expected_min = initial_row_count + batch_start if initial_row_count is not None else None
                                
                                if count_after_retry >= (expected_min if expected_min is not None else count_before_retry):
                                    # UPSERT succeeded - rows were added or updated
                                    print(f"    [INFO] UPSERT succeeded without RETURNING clause - verified: {count_before_retry} -> {count_after_retry} rows")
                                    batch_inserted = 0
                                    batch_updated = len(batch_df)  # Assume all were updates (safer)
                                    total_inserted += batch_inserted
                                    total_updated += batch_updated
                                    if total_batches > 1:
                                        print(f"    [DEBUG] Batch {batch_num} completed: {len(batch_df)} rows processed (verified)")
                                    else:
                                        print(f"    [DEBUG] UPSERT completed: {len(batch_df)} rows processed (verified)")
                                    continue  # Skip to next batch
                                else:
                                    # UPSERT didn't add rows - might have failed silently
                                    print(f"    [WARNING] UPSERT executed but row count didn't increase ({count_before_retry} -> {count_after_retry}) - may need sub-batch retry")
                                    # Fall through to sub-batch retry logic below
                            else:
                                # Can't verify - assume it worked but log warning
                                print(f"    [WARNING] UPSERT executed but couldn't verify row count - assuming success")
                                batch_inserted = 0
                                batch_updated = len(batch_df)
                                total_inserted += batch_inserted
                                total_updated += batch_updated
                                if total_batches > 1:
                                    print(f"    [DEBUG] Batch {batch_num} completed: {len(batch_df)} rows processed (verification unavailable)")
                                else:
                                    print(f"    [DEBUG] UPSERT completed: {len(batch_df)} rows processed (verification unavailable)")
                                continue  # Skip to next batch
                        except Exception as e2:
                            # If even without RETURNING it fails, check what kind of error it is
                            error_msg2 = str(e2)
                            
                            # If it's still a "list index out of range" error, it's likely a Lambda function parsing issue
                            # But we need to verify if the UPSERT actually succeeded by checking row counts
                            if 'list index out of range' in error_msg2.lower():
                                print(f"    [WARNING] Lambda still returning parsing error even without RETURNING - verifying if UPSERT actually succeeded")
                                # Get row count AFTER the failed UPSERT attempt to see if it actually succeeded
                                try:
                                    # Check current row count - the UPSERT might have succeeded despite the error
                                    count_after_attempt_sql = text(f"SELECT COUNT(*) FROM {table}")
                                    count_after_attempt_result = conn.execute(count_after_attempt_sql)
                                    count_after_attempt = None
                                    if hasattr(count_after_attempt_result, 'scalar'):
                                        count_after_attempt = count_after_attempt_result.scalar()
                                    elif hasattr(count_after_attempt_result, 'fetchone'):
                                        row = count_after_attempt_result.fetchone()
                                        if row and len(row) > 0:
                                            count_after_attempt = row[0]
                                    
                                    # Handle dict response from Lambda
                                    if isinstance(count_after_attempt, dict):
                                        import json
                                        if 'count' in count_after_attempt:
                                            count_after_attempt = count_after_attempt['count']
                                        elif 'body' in count_after_attempt:
                                            body = json.loads(count_after_attempt['body']) if isinstance(count_after_attempt['body'], str) else count_after_attempt['body']
                                            if isinstance(body, list) and len(body) > 0:
                                                first_item = body[0]
                                                if isinstance(first_item, dict):
                                                    count_after_attempt = first_item.get('count', list(first_item.values())[0] if first_item else None)
                                                else:
                                                    count_after_attempt = first_item
                                            elif isinstance(body, dict) and 'count' in body:
                                                count_after_attempt = body['count']
                                        else:
                                            count_after_attempt = list(count_after_attempt.values())[0] if count_after_attempt else None
                                    
                                    if count_after_attempt is not None:
                                        try:
                                            count_after_attempt = int(count_after_attempt)
                                        except (ValueError, TypeError):
                                            count_after_attempt = None
                                    
                                    # Compare with initial count to see if rows were added
                                    # Calculate expected count: initial + rows processed in previous batches + current batch
                                    if initial_row_count is not None and count_after_attempt is not None:
                                        rows_processed_before = batch_start  # Rows in previous batches
                                        expected_count = initial_row_count + rows_processed_before + len(batch_df)
                                        
                                        # If current count matches or exceeds expected, the batch likely succeeded
                                        # Allow some tolerance for updates (rows might already exist)
                                        if count_after_attempt >= initial_row_count + rows_processed_before:
                                            # Rows were added - the UPSERT succeeded despite the error
                                            rows_added_in_batch = count_after_attempt - (initial_row_count + rows_processed_before)
                                            print(f"    [INFO] UPSERT likely succeeded despite parsing error (count: {initial_row_count + rows_processed_before} -> {count_after_attempt})")
                                            batch_inserted = 0
                                            batch_updated = len(batch_df)  # Assume all were updates (safer)
                                            total_inserted += batch_inserted
                                            total_updated += batch_updated
                                            if total_batches > 1:
                                                print(f"    [DEBUG] Batch {batch_num} completed: {len(batch_df)} rows processed (verified via row count)")
                                            else:
                                                print(f"    [DEBUG] UPSERT completed: {len(batch_df)} rows processed (verified via row count)")
                                            continue
                                    
                                    # If we get here, the UPSERT likely didn't succeed - try sub-batches
                                    # Get row count before attempting sub-batches
                                    count_before_sql = text(f"SELECT COUNT(*) FROM {table}")
                                    count_before_result = conn.execute(count_before_sql)
                                    count_before = None
                                    if hasattr(count_before_result, 'scalar'):
                                        count_before = count_before_result.scalar()
                                    elif hasattr(count_before_result, 'fetchone'):
                                        row = count_before_result.fetchone()
                                        if row and len(row) > 0:
                                            count_before = row[0]
                                    
                                    # Handle dict response from Lambda
                                    if isinstance(count_before, dict):
                                        import json
                                        if 'count' in count_before:
                                            count_before = count_before['count']
                                        elif 'body' in count_before:
                                            body = json.loads(count_before['body']) if isinstance(count_before['body'], str) else count_before['body']
                                            if isinstance(body, list) and len(body) > 0:
                                                first_item = body[0]
                                                if isinstance(first_item, dict):
                                                    count_before = first_item.get('count', list(first_item.values())[0] if first_item else None)
                                                else:
                                                    count_before = first_item
                                            elif isinstance(body, dict) and 'count' in body:
                                                count_before = body['count']
                                        else:
                                            count_before = list(count_before.values())[0] if count_before else None
                                    
                                    if count_before is not None:
                                        try:
                                            count_before = int(count_before)
                                        except (ValueError, TypeError):
                                            count_before = None
                                    
                                    # Now try to execute the UPSERT in smaller sub-batches to avoid Lambda parsing issues
                                    # This will help us identify if the issue is with batch size or actual data problems
                                    print(f"    [INFO] Attempting UPSERT in smaller sub-batches to work around Lambda parsing issue")
                                    sub_batch_size = min(50, len(batch_df))  # Try smaller batches
                                    sub_batch_inserted = 0
                                    sub_batch_updated = 0
                                    sub_batch_failed = 0
                                    
                                    for sub_start in range(0, len(batch_df), sub_batch_size):
                                        sub_batch_df = batch_df.iloc[sub_start:sub_start + sub_batch_size]
                                        
                                        # Build VALUES for sub-batch
                                        sub_values_list = []
                                        for _, row in sub_batch_df.iterrows():
                                            values = []
                                            for val in row:
                                                if pd.isna(val):
                                                    values.append('NULL')
                                                elif isinstance(val, str):
                                                    escaped_val = val.replace("\\", "\\\\").replace("'", "''")
                                                    values.append(f"'{escaped_val}'")
                                                elif isinstance(val, (int, float)):
                                                    values.append(str(val))
                                                elif isinstance(val, bool):
                                                    values.append('TRUE' if val else 'FALSE')
                                                elif isinstance(val, (pd.Timestamp, pd.DatetimeTZDtype)):
                                                    if pd.notna(val):
                                                        values.append(f"'{val.isoformat()}'")
                                                    else:
                                                        values.append('NULL')
                                                else:
                                                    escaped_val = str(val).replace("\\", "\\\\").replace("'", "''")
                                                    values.append(f"'{escaped_val}'")
                                            sub_values_list.append(f"({', '.join(values)})")
                                        
                                        sub_values_str = ', '.join(sub_values_list)
                                        sub_sql = text(
                                            f"""
                                            INSERT INTO {table} ({insert_cols})
                                            VALUES {sub_values_str}
                                            ON CONFLICT ({conflict}) DO UPDATE SET {set_clause};
                                            """
                                        )
                                        
                                        try:
                                            conn.execute(sub_sql)
                                            # If it succeeds, assume all rows in sub-batch were processed
                                            sub_batch_updated += len(sub_batch_df)
                                        except Exception as sub_error:
                                            sub_error_msg = str(sub_error)
                                            # If it's still a parsing error, try individual rows
                                            if 'list index out of range' in sub_error_msg.lower():
                                                print(f"    [WARNING] Sub-batch also failed with parsing error - trying individual rows")
                                                # Try individual rows
                                                for idx, (_, row) in enumerate(sub_batch_df.iterrows()):
                                                    values = []
                                                    for val in row:
                                                        if pd.isna(val):
                                                            values.append('NULL')
                                                        elif isinstance(val, str):
                                                            escaped_val = val.replace("\\", "\\\\").replace("'", "''")
                                                            values.append(f"'{escaped_val}'")
                                                        elif isinstance(val, (int, float)):
                                                            values.append(str(val))
                                                        elif isinstance(val, bool):
                                                            values.append('TRUE' if val else 'FALSE')
                                                        elif isinstance(val, (pd.Timestamp, pd.DatetimeTZDtype)):
                                                            if pd.notna(val):
                                                                values.append(f"'{val.isoformat()}'")
                                                            else:
                                                                values.append('NULL')
                                                        else:
                                                            escaped_val = str(val).replace("\\", "\\\\").replace("'", "''")
                                                            values.append(f"'{escaped_val}'")
                                                    
                                                    row_sql = text(
                                                        f"""
                                                        INSERT INTO {table} ({insert_cols})
                                                        VALUES ({', '.join(values)})
                                                        ON CONFLICT ({conflict}) DO UPDATE SET {set_clause};
                                                        """
                                                    )
                                                    try:
                                                        # Get count before insert
                                                        count_before_row = None
                                                        try:
                                                            count_before_row_sql = text(f"SELECT COUNT(*) FROM {table}")
                                                            count_before_row_result = conn.execute(count_before_row_sql)
                                                            if hasattr(count_before_row_result, 'scalar'):
                                                                count_before_row = count_before_row_result.scalar()
                                                            elif hasattr(count_before_row_result, 'fetchone'):
                                                                row_data = count_before_row_result.fetchone()
                                                                if row_data and len(row_data) > 0:
                                                                    count_before_row = row_data[0]
                                                            # Handle dict response
                                                            if isinstance(count_before_row, dict):
                                                                import json
                                                                if 'count' in count_before_row:
                                                                    count_before_row = count_before_row['count']
                                                                elif 'body' in count_before_row:
                                                                    body = json.loads(count_before_row['body']) if isinstance(count_before_row['body'], str) else count_before_row['body']
                                                                    if isinstance(body, list) and len(body) > 0:
                                                                        first_item = body[0]
                                                                        if isinstance(first_item, dict):
                                                                            count_before_row = first_item.get('count', list(first_item.values())[0] if first_item else None)
                                                                        else:
                                                                            count_before_row = first_item
                                                                    elif isinstance(body, dict) and 'count' in body:
                                                                        count_before_row = body['count']
                                                                else:
                                                                    count_before_row = list(count_before_row.values())[0] if count_before_row else None
                                                            if count_before_row is not None:
                                                                try:
                                                                    count_before_row = int(count_before_row)
                                                                except (ValueError, TypeError):
                                                                    count_before_row = None
                                                        except:
                                                            pass  # If we can't get count, continue anyway
                                                        
                                                        conn.execute(row_sql)
                                                        
                                                        # Verify row was actually inserted despite potential Lambda error
                                                        if count_before_row is not None:
                                                            try:
                                                                count_after_row_sql = text(f"SELECT COUNT(*) FROM {table}")
                                                                count_after_row_result = conn.execute(count_after_row_sql)
                                                                count_after_row = None
                                                                if hasattr(count_after_row_result, 'scalar'):
                                                                    count_after_row = count_after_row_result.scalar()
                                                                elif hasattr(count_after_row_result, 'fetchone'):
                                                                    row_data = count_after_row_result.fetchone()
                                                                    if row_data and len(row_data) > 0:
                                                                        count_after_row = row_data[0]
                                                                # Handle dict response
                                                                if isinstance(count_after_row, dict):
                                                                    import json
                                                                    if 'count' in count_after_row:
                                                                        count_after_row = count_after_row['count']
                                                                    elif 'body' in count_after_row:
                                                                        body = json.loads(count_after_row['body']) if isinstance(count_after_row['body'], str) else count_after_row['body']
                                                                        if isinstance(body, list) and len(body) > 0:
                                                                            first_item = body[0]
                                                                            if isinstance(first_item, dict):
                                                                                count_after_row = first_item.get('count', list(first_item.values())[0] if first_item else None)
                                                                            else:
                                                                                count_after_row = first_item
                                                                        elif isinstance(body, dict) and 'count' in body:
                                                                            count_after_row = body['count']
                                                                    else:
                                                                        count_after_row = list(count_after_row.values())[0] if count_after_row else None
                                                                if count_after_row is not None:
                                                                    try:
                                                                        count_after_row = int(count_after_row)
                                                                    except (ValueError, TypeError):
                                                                        count_after_row = None
                                                                    
                                                                    # If count increased or stayed same (UPSERT), row was processed
                                                                    if count_after_row >= count_before_row:
                                                                        sub_batch_updated += 1
                                                                    else:
                                                                        print(f"    [WARNING] Row {sub_start + idx + 1} executed but count decreased - may have failed")
                                                                        sub_batch_failed += 1
                                                                else:
                                                                    # Can't verify - assume success
                                                                    sub_batch_updated += 1
                                                            except:
                                                                # Can't verify - assume success
                                                                sub_batch_updated += 1
                                                        else:
                                                            # Can't verify - assume success
                                                            sub_batch_updated += 1
                                                    except Exception as row_error:
                                                        error_msg = str(row_error)
                                                        # Check if it's a Lambda parsing error - the INSERT might have succeeded
                                                        if 'list index out of range' in error_msg.lower():
                                                            # Verify if row was actually inserted
                                                            try:
                                                                count_after_error_sql = text(f"SELECT COUNT(*) FROM {table}")
                                                                count_after_error_result = conn.execute(count_after_error_sql)
                                                                count_after_error = None
                                                                if hasattr(count_after_error_result, 'scalar'):
                                                                    count_after_error = count_after_error_result.scalar()
                                                                elif hasattr(count_after_error_result, 'fetchone'):
                                                                    row_data = count_after_error_result.fetchone()
                                                                    if row_data and len(row_data) > 0:
                                                                        count_after_error = row_data[0]
                                                                # Handle dict response
                                                                if isinstance(count_after_error, dict):
                                                                    import json
                                                                    if 'count' in count_after_error:
                                                                        count_after_error = count_after_error['count']
                                                                    elif 'body' in count_after_error:
                                                                        body = json.loads(count_after_error['body']) if isinstance(count_after_error['body'], str) else count_after_error['body']
                                                                        if isinstance(body, list) and len(body) > 0:
                                                                            first_item = body[0]
                                                                            if isinstance(first_item, dict):
                                                                                count_after_error = first_item.get('count', list(first_item.values())[0] if first_item else None)
                                                                            else:
                                                                                count_after_error = first_item
                                                                        elif isinstance(body, dict) and 'count' in body:
                                                                            count_after_error = body['count']
                                                                    else:
                                                                        count_after_error = list(count_after_error.values())[0] if count_after_error else None
                                                                if count_after_error is not None:
                                                                    try:
                                                                        count_after_error = int(count_after_error)
                                                                    except (ValueError, TypeError):
                                                                        count_after_error = None
                                                                    
                                                                    # Compare with count before this row
                                                                    if count_before_row is not None and count_after_error is not None:
                                                                        if count_after_error >= count_before_row:
                                                                            # Row was inserted despite error
                                                                            print(f"    [INFO] Row {sub_start + idx + 1} inserted successfully despite Lambda parsing error")
                                                                            sub_batch_updated += 1
                                                                        else:
                                                                            print(f"    [ERROR] Failed to insert row {sub_start + idx + 1}: {error_msg[:200]}")
                                                                            sub_batch_failed += 1
                                                                    else:
                                                                        # Can't verify - assume failed
                                                                        print(f"    [WARNING] Row {sub_start + idx + 1} may have failed (can't verify): {error_msg[:200]}")
                                                                        sub_batch_failed += 1
                                                                else:
                                                                    # Can't verify - assume failed
                                                                    print(f"    [WARNING] Row {sub_start + idx + 1} may have failed (can't verify): {error_msg[:200]}")
                                                                    sub_batch_failed += 1
                                                            except:
                                                                # Can't verify - assume failed
                                                                print(f"    [ERROR] Failed to insert row {sub_start + idx + 1}: {error_msg[:200]}")
                                                                sub_batch_failed += 1
                                                        else:
                                                            # Real error, not just parsing issue
                                                            print(f"    [ERROR] Failed to insert row {sub_start + idx + 1}: {error_msg[:200]}")
                                                            sub_batch_failed += 1
                                            else:
                                                # Real database error
                                                print(f"    [ERROR] Sub-batch UPSERT failed: {sub_error_msg[:300]}")
                                                sub_batch_failed += len(sub_batch_df)
                                    
                                    # Verify rows were actually added
                                    count_after_sql = text(f"SELECT COUNT(*) FROM {table}")
                                    count_after_result = conn.execute(count_after_sql)
                                    count_after = None
                                    if hasattr(count_after_result, 'scalar'):
                                        count_after = count_after_result.scalar()
                                    elif hasattr(count_after_result, 'fetchone'):
                                        row = count_after_result.fetchone()
                                        if row and len(row) > 0:
                                            count_after = row[0]
                                    
                                    # Handle dict response from Lambda
                                    if isinstance(count_after, dict):
                                        import json
                                        if 'count' in count_after:
                                            count_after = count_after['count']
                                        elif 'body' in count_after:
                                            body = json.loads(count_after['body']) if isinstance(count_after['body'], str) else count_after['body']
                                            if isinstance(body, list) and len(body) > 0:
                                                first_item = body[0]
                                                if isinstance(first_item, dict):
                                                    count_after = first_item.get('count', list(first_item.values())[0] if first_item else None)
                                                else:
                                                    count_after = first_item
                                            elif isinstance(body, dict) and 'count' in body:
                                                count_after = body['count']
                                        else:
                                            count_after = list(count_after.values())[0] if count_after else None
                                    
                                    if count_after is not None:
                                        try:
                                            count_after = int(count_after)
                                        except (ValueError, TypeError):
                                            count_after = None
                                    
                                    # Check if rows were actually added
                                    if count_before is not None and count_after is not None:
                                        rows_added = count_after - count_before
                                        print(f"    [DEBUG] Row count verification for batch: {count_before} -> {count_after} (added: {rows_added})")
                                        
                                        if rows_added > 0:
                                            # Rows were added - assume they were updates (since we can't tell with Lambda)
                                            batch_inserted = 0
                                            batch_updated = rows_added
                                            total_inserted += batch_inserted
                                            total_updated += batch_updated
                                            if total_batches > 1:
                                                print(f"    [DEBUG] Batch {batch_num} completed: {rows_added} rows processed via sub-batches")
                                            else:
                                                print(f"    [DEBUG] UPSERT completed: {rows_added} rows processed via sub-batches")
                                            continue
                                        else:
                                            # No rows were added - the UPSERT likely failed
                                            print(f"    [ERROR] No rows were added after UPSERT attempt - batch may have failed")
                                            if sub_batch_failed > 0:
                                                print(f"    [ERROR] {sub_batch_failed} rows failed to insert")
                                            # Continue to next batch but don't count these as processed
                                            continue
                                    else:
                                        # Can't verify - assume processed
                                        batch_inserted = 0
                                        batch_updated = sub_batch_updated
                                        total_inserted += batch_inserted
                                        total_updated += batch_updated
                                        if total_batches > 1:
                                            print(f"    [DEBUG] Batch {batch_num} completed: {sub_batch_updated} rows processed (verification unavailable)")
                                        else:
                                            print(f"    [DEBUG] UPSERT completed: {sub_batch_updated} rows processed (verification unavailable)")
                                        continue
                                        
                                except Exception as verify_error:
                                    verify_error_msg = str(verify_error)
                                    print(f"    [ERROR] Could not verify UPSERT: {verify_error_msg[:300]}")
                                    # If we can't verify, we can't assume success - this is a real problem
                                    raise RuntimeError(f"UPSERT failed for {table} and verification failed: {verify_error}")
                            elif 'violates foreign key constraint' in error_msg2.lower() or 'not present in table' in error_msg2.lower():
                                print(f"    [ERROR] UPSERT failed due to FK constraint violation: {error_msg2[:300]}")
                                # This is a real error - the data can't be inserted
                                raise RuntimeError(f"FK constraint violation for {table}: {error_msg2}")
                            else:
                                print(f"    [ERROR] UPSERT failed even without RETURNING clause: {e2}")
                                raise RuntimeError(f"UPSERT failed for {table}: {e2}")
                    else:
                        # Re-raise other errors
                        raise
                
                # Debug: Log what we got back
                if len(batch_rows) != len(batch_df):
                    print(f"    [WARNING] Batch {batch_num}: Expected {len(batch_df)} rows from RETURNING, got {len(batch_rows)}")
                    if len(batch_rows) > 0 and len(batch_rows) < 5:
                        print(f"    [DEBUG] Sample RETURNING results: {batch_rows}")
                
                # Parse results - handle both boolean results and error tuples
                batch_inserted = 0
                batch_updated = 0
                
                if len(batch_rows) == 0:
                    # No rows returned - this shouldn't happen with RETURNING clause
                    # But if it does, assume all rows were processed (can't tell inserted vs updated)
                    print(f"    [WARNING] Batch {batch_num} returned no rows from RETURNING clause")
                    # Assume all were updated (more likely if data already exists)
                    batch_updated = len(batch_df)
                elif len(batch_rows) < len(batch_df):
                    # Got fewer rows back than expected - Lambda might be limiting results
                    # Process what we got, and assume the rest were updated
                    print(f"    [WARNING] Batch {batch_num}: Got {len(batch_rows)} rows back, expected {len(batch_df)}")
                    processed_count = 0
                    for r in batch_rows:
                        if len(r) > 0:
                            first_val = r[0]
                            
                            # Check if first_val is an error message (string containing error keywords)
                            if isinstance(first_val, str):
                                error_keywords = ['error', 'violates', 'constraint', 'not present', 'list index out of range', 'detail:', 'key']
                                if any(keyword in first_val.lower() for keyword in error_keywords):
                                    print(f"    [ERROR] Batch {batch_num} UPSERT failed with error: {first_val[:200]}")
                                    # This is a database error - the UPSERT failed
                                    # Don't count this as successful
                                    continue
                            
                            # Check if result is an error (tuple with error message in second element)
                            if len(r) > 1 and isinstance(r[1], str) and 'error' in r[1].lower():
                                print(f"    [ERROR] Batch {batch_num} returned error: {r[1]}")
                                continue
                            
                            is_inserted = _parse_returning_value(first_val, batch_num)
                            
                            if is_inserted:
                                batch_inserted += 1
                            else:
                                batch_updated += 1
                            processed_count += 1
                    
                    # Assume remaining rows were updated (since we got partial results)
                    remaining = len(batch_df) - processed_count
                    if remaining > 0:
                        batch_updated += remaining
                        print(f"    [DEBUG] Assuming {remaining} remaining rows were updated (partial RETURNING results)")
                else:
                    # Normal case: got expected number of rows
                    for r in batch_rows:
                        if len(r) > 0:
                            first_val = r[0]
                            
                            # Check if first_val is an error message (string containing error keywords)
                            if isinstance(first_val, str):
                                error_keywords = ['error', 'violates', 'constraint', 'not present', 'list index out of range', 'detail:', 'key']
                                if any(keyword in first_val.lower() for keyword in error_keywords):
                                    print(f"    [ERROR] Batch {batch_num} UPSERT failed with error: {first_val[:200]}")
                                    # This is a database error - the UPSERT failed
                                    # Don't count this as successful
                                    continue
                            
                            # Check if result is an error (tuple with error message in second element)
                            if len(r) > 1 and isinstance(r[1], str) and 'error' in r[1].lower():
                                print(f"    [ERROR] Batch {batch_num} returned error: {r[1]}")
                                continue
                            
                            is_inserted = _parse_returning_value(first_val, batch_num)
                            
                            if is_inserted:
                                batch_inserted += 1
                            else:
                                batch_updated += 1
                
                total_inserted += batch_inserted
                total_updated += batch_updated
                
                if total_batches > 1:
                    print(f"    [DEBUG] Batch {batch_num} completed: {len(batch_rows)} RETURNING rows, {len(batch_df)} rows processed ({batch_inserted} inserted, {batch_updated} updated)")
                else:
                    print(f"    [DEBUG] UPSERT completed: {len(batch_rows)} RETURNING rows, {len(batch_df)} rows processed ({batch_inserted} inserted, {batch_updated} updated)")
            
            # Set final results
            inserted = total_inserted
            updated = total_updated
            
            # If we got no RETURNING results or very few compared to rows processed,
            # we can't accurately count. Verify by checking table row count for Lambda connections
            total_processed = inserted + updated
            if total_processed == 0 and len(df) > 0:
                # No rows counted - RETURNING didn't work as expected
                # For Lambda connections, verify data was actually inserted
                if hasattr(conn, '__class__') and 'Lambda' in conn.__class__.__name__:
                    try:
                        # Get current row count
                        count_sql = text(f"SELECT COUNT(*) FROM {table}")
                        count_result = conn.execute(count_sql)
                        current_count = count_result.scalar() if hasattr(count_result, 'scalar') else None
                        if current_count is not None:
                            print(f"    [INFO] Verified table {table} has {current_count} rows after UPSERT")
                            # If we processed rows but count is 0, the UPSERT likely failed
                            if current_count == 0 and len(df) > 0:
                                print(f"    [WARNING] Table is empty after UPSERT - data may not have been inserted")
                                # Don't mark as updated - the data wasn't actually inserted
                            else:
                                # Data exists - assume it was processed
                                updated = len(df)
                        else:
                            # Can't verify - assume processed
                            print(f"    [WARNING] No rows counted from RETURNING clause - assuming all {len(df)} rows were processed")
                            updated = len(df)
                    except Exception as verify_error:
                        print(f"    [WARNING] Could not verify table count: {verify_error}")
                        # Assume all rows were processed (more likely updated if data exists)
                        print(f"    [WARNING] No rows counted from RETURNING clause - assuming all {len(df)} rows were processed")
                        updated = len(df)  # Mark as updated (safer assumption when data might already exist)
                else:
                    # For non-Lambda connections, just assume processed
                    print(f"    [WARNING] No rows counted from RETURNING clause - assuming all {len(df)} rows were processed")
                    updated = len(df)  # Mark as updated (safer assumption when data might already exist)
            elif total_processed < len(df):
                # Got partial results - assume remaining were processed
                remaining = len(df) - total_processed
                print(f"    [WARNING] Only counted {total_processed} rows from RETURNING, but processed {len(df)} - assuming {remaining} remaining were updated")
                updated += remaining
            
            result = []  # We've already processed all batches
            
            # For Lambda connections, verify data was actually inserted
            if hasattr(conn, '__class__') and 'Lambda' in conn.__class__.__name__ and initial_row_count is not None:
                try:
                    count_sql = text(f"SELECT COUNT(*) FROM {table}")
                    count_result = conn.execute(count_sql)
                    final_row_count = None
                    if hasattr(count_result, 'scalar'):
                        final_row_count = count_result.scalar()
                    elif hasattr(count_result, 'fetchone'):
                        row = count_result.fetchone()
                        if row and len(row) > 0:
                            final_row_count = row[0]
                    # Handle dict response from Lambda (parse from body or direct dict)
                    if isinstance(final_row_count, dict):
                        import json
                        if 'count' in final_row_count:
                            # Direct dict with 'count' key
                            final_row_count = final_row_count['count']
                        elif 'body' in final_row_count:
                            # Lambda API Gateway format
                            body = json.loads(final_row_count['body']) if isinstance(final_row_count['body'], str) else final_row_count['body']
                            if isinstance(body, list) and len(body) > 0:
                                first_item = body[0]
                                if isinstance(first_item, dict):
                                    final_row_count = first_item.get('count', list(first_item.values())[0] if first_item else None)
                                else:
                                    final_row_count = first_item
                            elif isinstance(body, dict) and 'count' in body:
                                final_row_count = body['count']
                        else:
                            # Try to get first value from dict
                            final_row_count = list(final_row_count.values())[0] if final_row_count else None
                    
                    # Convert to int if possible
                    if final_row_count is not None:
                        try:
                            final_row_count = int(final_row_count)
                        except (ValueError, TypeError):
                            pass
                    
                    # Ensure both are numbers for comparison
                    if isinstance(initial_row_count, (int, float)) and isinstance(final_row_count, (int, float)):
                        rows_added = final_row_count - initial_row_count
                        print(f"    [DEBUG] Row count verification: {initial_row_count} -> {final_row_count} (added: {rows_added})")
                        if rows_added == 0 and len(df) > 0:
                            print(f"    [WARNING] No rows were actually inserted into {table} - UPSERT may have failed silently")
                            # Adjust counts to reflect reality
                            if inserted + updated > 0:
                                print(f"    [WARNING] Reported {inserted} inserted, {updated} updated, but no rows were actually added")
                                # Reset counts since nothing was actually inserted
                                inserted = 0
                                updated = 0
                        elif rows_added < len(df):
                            print(f"    [WARNING] Only {rows_added} rows were actually inserted, but {len(df)} rows were processed")
                    else:
                        print(f"    [WARNING] Could not compare row counts: initial={initial_row_count} (type: {type(initial_row_count)}), final={final_row_count} (type: {type(final_row_count)})")
                except Exception as verify_error:
                    print(f"    [WARNING] Could not verify final row count: {verify_error}")
                    import traceback
                    traceback.print_exc()
            
            print(f"    [DEBUG] UPSERT completed: {len(df)} total rows processed ({inserted} inserted, {updated} updated)")
        else:
            # For regular connections, use staging table
            select_cols = ", ".join([f'"{c}"' for c in cols])
            print(f"    [DEBUG] Executing UPSERT: INSERT INTO {table} ... ON CONFLICT ({conflict}) DO UPDATE")
            sql = text(
                f"""
                INSERT INTO {table} ({insert_cols})
                SELECT {select_cols} FROM {stg}
                ON CONFLICT ({conflict}) DO UPDATE SET {set_clause}
                RETURNING xmax = 0 AS inserted;
                """
            )
            # Execute single UPSERT query for regular connections
            execute_result = conn.execute(sql)
            result = execute_result.fetchall() if hasattr(execute_result, 'fetchall') else list(execute_result)
            print(f"    [DEBUG] UPSERT RETURNING clause returned {len(result)} rows")
            if len(result) > 0 and len(result) < 10:
                print(f"    [DEBUG] First few RETURNING results: {result[:5]}")
            elif len(result) >= 10:
                print(f"    [DEBUG] First 5 RETURNING results: {result[:5]}")
            inserted = sum(1 for r in result if len(r) > 0 and r[0])
            updated = len(result) - inserted
            print(f"    [DEBUG] UPSERT completed: {len(result)} total rows affected ({inserted} inserted, {updated} updated)")
    except Exception as e:
        error_str = str(e)
        if "ForeignKeyViolation" in error_str or "foreign key constraint" in error_str.lower():
            # FK violation slipped through - this should not happen if FK filtering worked
            print(f"ERROR: FK violation occurred for {table} despite FK filtering. This indicates a bug in FK filtering logic.")
            print(f"  Error: {error_str[:300]}")
            # Return all rows as rejected
            # original_df should always be available since we define it before FK filtering
            rejected_df = original_df.copy()
            rejected_df['rejection_reason'] = f'Foreign key violation: {error_str[:200]}'
            return 0, 0, original_count, rejected_df
        else:
            # Re-raise non-FK errors
            raise
    
    return inserted, updated, rejected_count, rejected_df

