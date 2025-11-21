#run_etl.py
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from typing import Dict, List

import pandas as pd
from dotenv import load_dotenv

from .db import get_engine, get_primary_keys
from .extract import read_sheet
from .transform import (
    clean_dataframe,
    apply_column_renames,
    coerce_types_for_table,
    split_valid_invalid,
    auto_generate_missing_keys,
    apply_json_transforms,
    map_material_type_desc_to_id,
    map_location_type_desc_to_id,
    apply_uom_conversion_transforms,
    map_purchasing_org_name_to_id,
)
from .load import stage_and_upsert
from .report import RunReporter
from .notify import send_run_report
from .utils import download_excel_from_s3, load_yaml
from .schema import ensure_database_schema, get_schema_info


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="APOLLO ETL: Excel → Postgres over SSH tunnel")
    parser.add_argument("--tables", type=str, help="Comma-separated list of sheet/table names", default="")
    parser.add_argument("--category", type=str, choices=["masters", "core", "relationship", "transactional", "all"], default="all")
    parser.add_argument("--mode", type=str, choices=["initial", "incremental"], default="initial")
    parser.add_argument("--excel", type=str, default=os.getenv("EXCEL_PATH", "Data Model + Tables + Data_processed.xlsx"))
    parser.add_argument("--mappings", type=str, default=os.path.join(os.path.dirname(__file__), "config", "mappings.yaml"))
    parser.add_argument("--tables-config", type=str, default=os.path.join(os.path.dirname(__file__), "config", "tables.yaml"))
    parser.add_argument("--reports-dir", type=str, default=os.getenv("REPORTS_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")))
    parser.add_argument("--dry-run", action="store_true", help="Validate only, no writes")
    parser.add_argument("--create-schema", action="store_true", help="Create database schema if it doesn't exist")
    parser.add_argument("--schema-only", action="store_true", help="Only create schema, don't run ETL")
    parser.add_argument("--force-schema", action="store_true", help="Force recreate schema (dangerous!)")
    return parser.parse_args()


def parse_args_from(argv: list[str]) -> argparse.Namespace:
    """Custom parser for when argv is passed programmatically."""
    parser = argparse.ArgumentParser(description="APOLLO ETL: Excel → Postgres over SSH tunnel")
    parser.add_argument("--tables", type=str, default="")
    parser.add_argument("--category", type=str, choices=["masters", "core", "relationship", "transactional", "all"], default="all")
    parser.add_argument("--mode", type=str, choices=["initial", "incremental"], default="initial")
    parser.add_argument("--excel", type=str, required=True)
    parser.add_argument("--mappings", type=str, default=os.path.join(os.path.dirname(__file__), "config", "mappings.yaml"))
    parser.add_argument("--tables-config", type=str, default=os.path.join(os.path.dirname(__file__), "config", "tables.yaml"))
    parser.add_argument("--reports-dir", type=str, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--create-schema", action="store_true")
    parser.add_argument("--schema-only", action="store_true")
    parser.add_argument("--force-schema", action="store_true")
    return parser.parse_args(argv)


def resolve_worklist(args: argparse.Namespace, mappings: dict) -> List[str]:
    if args.tables:
        return [t.strip() for t in args.tables.split(",") if t.strip()]
    if args.category == "all":
        return list(mappings.get("load_order", {}).get("masters", [])) + \
               list(mappings.get("load_order", {}).get("core", [])) + \
               list(mappings.get("load_order", {}).get("relationship", [])) + \
               list(mappings.get("load_order", {}).get("transactional", []))
    return list(mappings.get("load_order", {}).get(args.category, []))



def main(argv: list[str] | None = None):
    """Entry point for ETL. Accepts sys.argv style list for programmatic use."""
    load_dotenv()  # .env optional
    args = parse_args() if argv is None else parse_args_from(argv)

    print(f"[ETL] Starting run with mode={args.mode}, excel={args.excel}")

    mappings = load_yaml(args.mappings)
    tables_conf = load_yaml(args.tables_config)

    worklist = resolve_worklist(args, mappings)
    print(f"[ETL] Worklist resolved: {worklist}")
    if not worklist:
        print("Nothing to load: check --tables or --category and mappings.yaml")
        sys.exit(1)

    os.makedirs(args.reports_dir, exist_ok=True)
    run_id = datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")
    reporter = RunReporter(args.reports_dir, run_id)

    # Database connection
    print("[ETL] Connecting to database...")
    engine = get_engine()
    
    # Handle schema creation if requested
    with engine.begin() as conn:
        if args.create_schema or args.schema_only or args.force_schema:
            print("[ETL] Setting up database schema...")
            schema_created = ensure_database_schema(conn, force_recreate=args.force_schema)
            if not schema_created:
                print("[ETL] ERROR: Failed to create database schema")
                sys.exit(3)
            
            schema_info = get_schema_info(conn)
            if 'error' not in schema_info:
                print(f"[ETL] Database ready with {schema_info['table_count']} tables")
            
            if args.schema_only:
                print("[ETL] Schema creation complete. Exiting (--schema-only mode)")
                return
        
        # Ensure we can introspect PKs
        pk_map = get_primary_keys(conn)

    # Process each sheet in the worklist
    for sheet_name in worklist:
        print(f"--- Processing sheet: {sheet_name} ---")
        cfg = mappings.get("tables", {}).get(sheet_name, {})
        target_table = cfg.get("target_table", sheet_name)
        column_renames: Dict[str, str] = cfg.get("column_renames", {})
        types_cfg: Dict[str, str] = cfg.get("dtypes", {})
        incr_cfg = cfg.get("incremental", {"strategy": "business_key_upsert"})

        try:
            if args.excel.startswith("s3://"):
                _, _, bucket, *key_parts = args.excel.split("/")
                key = "/".join(key_parts)
                args.excel = download_excel_from_s3(bucket, key)
            print(f"Reading sheet {sheet_name} from {args.excel}")
            df = read_sheet(args.excel, sheet_name)
            df = clean_dataframe(df)
            if column_renames:
                df = apply_column_renames(df, column_renames)

            # Determine PK/keys
            table_pk = tables_conf.get(target_table, {}).get("primary_key") or pk_map.get(target_table)
            if not table_pk:
                raise RuntimeError(f"No primary key configured/found for table {target_table}")

            # Table-specific transforms
            if target_table == 'material_master':
                # Map material_type text to material_type_id using Material_Type_Master sheet
                df = map_material_type_desc_to_id(df, args.excel)
            elif target_table == 'location_master':
                # Map location_Type text to location_type_id using Location_Type_Master sheet
                df = map_location_type_desc_to_id(df, args.excel)
            elif target_table == 'plant_material_purchase_org_supplier':
                # Map purchasing org names/descs to IDs (e.g., "Global" -> 1)
                df = map_purchasing_org_name_to_id(df, args.excel)

            # Apply JSON transformations for specific tables
            df = apply_json_transforms(df, target_table)

            # Apply UoM conversion transformations for uom_conversion table
            if target_table == 'uom_conversion':
                df = apply_uom_conversion_transforms(df)

            # Auto-generate missing primary keys where applicable
            df = auto_generate_missing_keys(df, table_pk, target_table)

            # Split rows with valid vs missing primary keys
            df, pk_invalid, pk_reasons = split_valid_invalid(df, table_pk)
            
            # Type coercion for valid rows
            df, type_invalid, type_reasons = coerce_types_for_table(df, types_cfg)
            
            # Combine all rejected rows and reasons
            rejected = pd.concat([pk_invalid, type_invalid], ignore_index=True) if not pk_invalid.empty or not type_invalid.empty else pd.DataFrame()
            reasons = pk_reasons + type_reasons

            # Deduplicate on primary key(s) to avoid ON CONFLICT affecting same row twice
            if table_pk and not df.empty:
                before = len(df)
                df = df.drop_duplicates(subset=table_pk, keep='last')
                after = len(df)
                if after < before:
                    reasons.append(f"Deduplicated {before - after} duplicate rows on keys {table_pk}")

            inserted = updated = 0
            if args.dry_run:
                pass
            else:
                with engine.begin() as conn:
                    replace = args.mode == 'initial'
                    # Allow FK violations for relationship tables
                    allow_fk = target_table in ['plant_material_purchase_org_supplier', 'where_to_use_each_price_type']
                    inserted, updated, fk_rejected, fk_rejected_df = stage_and_upsert(conn, target_table, df, table_pk, replace=replace, allow_fk_violations=allow_fk)

            total_rejected = len(rejected) + fk_rejected
            # Add FK rejection reasons to the reasons list
            if fk_rejected > 0:
                fk_reason = f"{fk_rejected} rows rejected due to missing foreign key references"
                reasons.append(fk_reason)
            
            reporter.record_table(sheet_name, target_table, len(df) + len(rejected), inserted, total_rejected, inserted, updated, reasons)
            
            # Write both types of rejected rows to CSV
            reporter.write_rejected(sheet_name, rejected)
            if not fk_rejected_df.empty:
                reporter.write_rejected(f"{sheet_name}_fk_violations", fk_rejected_df)
            
            print(f"Loaded {target_table}: inserted={inserted}, updated={updated}, rejected={total_rejected} (data issues: {len(rejected)}, FK violations: {fk_rejected})")

        except Exception as e:
            reporter.record_error(sheet_name, target_table, str(e))
            print(f"ERROR loading {target_table}: {e}")

    # Finalize reporting
    reporter.finalize()
    
    # Generate business-friendly missing materials report and add to main report
    missing_materials = _get_missing_materials_list(worklist, args.excel)
    if missing_materials:
        reporter.add_missing_materials(missing_materials)
    
    print(f"Report: {reporter.summary_path}")
    # Email report if SMTP env vars present
    send_run_report(os.path.dirname(reporter.summary_path), run_id)


def _get_missing_materials_list(worklist: List[str], excel_path: str) -> dict:
    """Get missing materials list for inclusion in main report."""
    import pandas as pd
    from pandas import ExcelFile
    
    # Only generate if plant material table was in the worklist
    plant_tables = ['plant_material_purchase_org_sup', 'plant_material_purchase_org_supplier']
    if not any(table in worklist for table in plant_tables):
        return {}
    
    try:
        xl = ExcelFile(excel_path)
        
        # Get material IDs from material_master
        if 'material_master' in xl.sheet_names:
            materials_df = pd.read_excel(xl, 'material_master')
            existing_materials = set(materials_df['material_id'].unique())
            
            # Get referenced material IDs from plant table
            plant_sheet = 'plant_material_purchase_org_sup' if 'plant_material_purchase_org_sup' in xl.sheet_names else None
            if plant_sheet:
                plant_df = pd.read_excel(xl, plant_sheet)
                referenced_materials = set(plant_df['material_id'].unique())
                
                # Find missing materials
                missing_materials = referenced_materials - existing_materials
                
                if missing_materials:
                    return {
                        'missing_materials': sorted(list(missing_materials)),
                        'total_missing': len(missing_materials),
                        'existing_count': len(existing_materials),
                        'referenced_count': len(referenced_materials),
                        'loaded_count': len(existing_materials & referenced_materials)
                    }
    except Exception as e:
        print(f"Could not generate missing materials list: {e}")
    
    return {}


if __name__ == "__main__":
    main()


