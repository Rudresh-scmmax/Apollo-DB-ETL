#!/usr/bin/env python3
"""
Local ETL runner using db_query.py for database operations.
Uses export.xlsx file and runs ETL locally.

Set USE_DB_QUERY_LAMBDA=true in .env to use db_query.py Lambda function for reads.
Note: Direct DB connection is still required for writes/transactions.
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from etl.run_etl import main

if __name__ == "__main__":
    load_dotenv()
    
    # Default to using Lambda for database operations (since DB is in private VPC)
    # Can be overridden by setting USE_DB_QUERY_LAMBDA=false in .env
    use_lambda = os.getenv('USE_DB_QUERY_LAMBDA', 'true').lower() == 'true'
    if use_lambda:
        # Verify db_query.py exists
        db_query_path = project_root / "db_query.py"
        if not db_query_path.exists():
            print(f"WARNING: db_query.py not found at {db_query_path}")
            print("Falling back to direct database connection")
            use_lambda = False
        else:
            # Ensure the environment variable is set so etl.db.get_engine sees it
            os.environ['USE_DB_QUERY_LAMBDA'] = 'true'
            
            # Test import
            try:
                sys.path.insert(0, str(project_root))
                import db_query
                # Lambda function name defaults to 'client1-private_db_query' in db_query.py
                # Can be overridden with DB_QUERY_LAMBDA_FUNCTION or CLIENT1_PRIVATE_DB_QUERY env vars
                lambda_function = (
                    os.getenv('DB_QUERY_LAMBDA_FUNCTION') or
                    os.getenv('CLIENT1_PRIVATE_DB_QUERY') or
                    db_query.TARGET_FUNCTION  # Default from db_query.py
                )
                print(f"Using db_query.py with Lambda function: {lambda_function}")
            except ImportError as e:
                print(f"WARNING: Could not import db_query: {e}")
                print("Falling back to direct database connection")
                use_lambda = False
    
    # Use export.xlsx in the project root
    excel_file = project_root / "export.xlsx"
    if not excel_file.exists():
        print(f"ERROR: {excel_file} not found!")
        print(f"Please ensure export.xlsx exists in the project root: {project_root}")
        sys.exit(1)
    
    # Create reports directory
    reports_dir = project_root / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Models path
    models_path = project_root / "etl" / "models.py"
    if not models_path.exists():
        print(f"ERROR: {models_path} not found!")
        sys.exit(1)
    
    # Verify database connection settings
    # If using Lambda, no DB credentials needed
    # (use_lambda already set above, don't reset it)
    
    if not use_lambda:
        # Direct connection requires DB credentials
        required_env_vars = ['DB_USER', 'DB_PASS', 'DB_HOST']
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
            print("Please set these in your .env file or environment")
            print("OR set USE_DB_QUERY_LAMBDA=true to use Lambda function instead")
            sys.exit(1)
    else:
        print("Using Lambda function for database operations (no DB credentials needed)")
    
    # Run ETL with local settings
    argv = [
        "--mode", "incremental",
        "--excel", str(excel_file),
        "--reports-dir", str(reports_dir),
        "--models-path", str(models_path),
        "--create-schema",  # Create schema if needed
    ]
    
    print(f"\n{'='*60}")
    print(f"Running ETL locally")
    print(f"{'='*60}")
    print(f"  Excel file: {excel_file}")
    print(f"  Reports dir: {reports_dir}")
    print(f"  Models path: {models_path}")
    print(f"  DB connection: {'Lambda (db_query.py)' if use_lambda else 'Direct'}")
    print(f"{'='*60}\n")
    
    try:
        main(argv)
        print(f"\n{'='*60}")
        print("ETL completed successfully!")
        print(f"   Reports saved to: {reports_dir}")
        print(f"{'='*60}")
    except KeyboardInterrupt:
        print("\n\nETL interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"ETL failed: {e}")
        print(f"{'='*60}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
