#!/usr/bin/env python3
"""
Export all data from PostgreSQL database to Excel file.

This script connects to a database, fetches all data from all tables,
and exports them to an Excel file with one sheet per table.
Tables with no data are skipped.

Usage:
    python scripts/export_db_to_excel.py --db-url "postgresql://user:pass@host:port/db" --output export.xlsx
"""
import argparse
import pandas as pd
from pathlib import Path
import sys
from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path to import etl module
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine


def parse_database_url(db_url: str) -> str:
    """
    Parse database URL and convert to standard PostgreSQL URL format.
    Handles asyncpg:// URLs by converting to postgresql://
    """
    # Replace asyncpg with psycopg2 (for SQLAlchemy)
    if db_url.startswith('postgresql+asyncpg://'):
        db_url = db_url.replace('postgresql+asyncpg://', 'postgresql+psycopg2://')
    elif db_url.startswith('postgresql://'):
        # Ensure we use psycopg2
        if '+psycopg2' not in db_url:
            db_url = db_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    
    return db_url


def get_all_tables(engine: Engine) -> List[str]:
    """Get all table names from the database."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return sorted(tables)


def get_table_data(engine: Engine, table_name: str) -> Optional[pd.DataFrame]:
    """
    Fetch all data from a table.
    Returns None if table is empty or error occurs.
    """
    try:
        with engine.connect() as conn:
            # Check if table has data
            count_query = text(f'SELECT COUNT(*) FROM "{table_name}"')
            count_result = conn.execute(count_query)
            row_count = count_result.scalar()
            
            if row_count == 0:
                print(f"  [SKIP] {table_name} - No data (0 rows)")
                return None
            
            # Fetch all data
            query = text(f'SELECT * FROM "{table_name}"')
            df = pd.read_sql(query, conn)
            
            # Convert timezone-aware datetimes to timezone-naive (Excel doesn't support timezones)
            for col in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    try:
                        # Check if timezone-aware
                        if hasattr(df[col].dtype, 'tz') and df[col].dtype.tz is not None:
                            df[col] = df[col].dt.tz_localize(None)
                        elif str(df[col].dtype) == 'datetime64[ns, UTC]':
                            df[col] = pd.to_datetime(df[col]).dt.tz_localize(None)
                        # Also handle object columns that might contain datetime strings
                        elif df[col].dtype == 'object':
                            # Try to detect datetime objects
                            sample = df[col].dropna()
                            if len(sample) > 0 and isinstance(sample.iloc[0], pd.Timestamp):
                                if sample.iloc[0].tz is not None:
                                    df[col] = pd.to_datetime(df[col]).dt.tz_localize(None)
                    except Exception:
                        # If conversion fails, leave as is
                        pass
            
            print(f"  [OK] {table_name} - {len(df)} rows, {len(df.columns)} columns")
            return df
            
    except Exception as e:
        print(f"  [ERROR] {table_name} - {str(e)}")
        return None


def export_database_to_excel(db_url: str, output_path: str, schema: Optional[str] = None):
    """
    Export all data from database to Excel file.
    
    Args:
        db_url: Database connection URL
        output_path: Path to output Excel file
        schema: Optional schema name (default: 'public')
    """
    print(f"[CONNECT] Connecting to database...")
    
    # Parse and normalize database URL
    db_url = parse_database_url(db_url)
    
    # Create engine
    try:
        engine = create_engine(db_url, echo=False)
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"[OK] Database connection successful")
    except Exception as e:
        print(f"[ERROR] Failed to connect to database: {e}")
        sys.exit(1)
    
    # Get all tables
    print(f"\n[SCAN] Scanning database for tables...")
    try:
        tables = get_all_tables(engine)
        print(f"[INFO] Found {len(tables)} tables in database")
    except Exception as e:
        print(f"[ERROR] Failed to get table list: {e}")
        sys.exit(1)
    
    if not tables:
        print("[WARN] No tables found in database")
        sys.exit(0)
    
    # Fetch data from each table
    print(f"\n[EXPORT] Exporting data from tables...")
    sheets = {}
    tables_with_data = 0
    tables_skipped = 0
    
    for table_name in tables:
        df = get_table_data(engine, table_name)
        if df is not None:
            sheets[table_name] = df
            tables_with_data += 1
        else:
            tables_skipped += 1
    
    if not sheets:
        print(f"\n[WARN] No data found in any table. Excel file not created.")
        sys.exit(0)
    
    # Write to Excel
    print(f"\n[WRITE] Writing Excel file: {output_path}")
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for sheet_name, df in sorted(sheets.items()):
                # Excel sheet names are limited to 31 characters
                excel_sheet_name = sheet_name[:31] if len(sheet_name) > 31 else sheet_name
                df.to_excel(writer, sheet_name=excel_sheet_name, index=False)
                print(f"  [OK] Wrote sheet: {excel_sheet_name} ({len(df)} rows)")
        
        print(f"\n[SUCCESS] Excel file created successfully!")
        print(f"   Output: {output_path}")
        print(f"   Tables with data: {tables_with_data}")
        print(f"   Tables skipped (empty): {tables_skipped}")
        print(f"   Total sheets: {len(sheets)}")
        
    except Exception as e:
        print(f"[ERROR] Failed to write Excel file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        engine.dispose()


def main():
    parser = argparse.ArgumentParser(
        description="Export all data from PostgreSQL database to Excel"
    )
    parser.add_argument(
        '--db-url',
        required=True,
        help='Database connection URL (e.g., postgresql://user:pass@host:port/db)'
    )
    parser.add_argument(
        '--output',
        default='database_export.xlsx',
        help='Output Excel file path (default: database_export.xlsx)'
    )
    parser.add_argument(
        '--schema',
        default='public',
        help='Database schema name (default: public)'
    )
    
    args = parser.parse_args()
    
    try:
        export_database_to_excel(
            args.db_url,
            args.output,
            args.schema
        )
    except KeyboardInterrupt:
        print("\n[INFO] Export cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Export failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

