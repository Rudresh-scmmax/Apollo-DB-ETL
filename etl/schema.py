from __future__ import annotations

import os
from typing import Optional, Any
from sqlalchemy import text, Engine
from sqlalchemy.engine import Connection


def check_database_exists(conn: Connection) -> bool:
    """Check if the APOLLO database schema exists by testing a key table."""
    try:
        result = conn.execute(text("SELECT 1 FROM currency_master LIMIT 1"))
        return True
    except Exception:
        return False


def create_database_schema_from_models(engine: Engine, conn: Optional[Connection] = None, models_module: Optional[Any] = None) -> None:
    """Create database schema from SQLAlchemy models.
    
    Supports both standard engines (using metadata.create_all) and Lambda engines
    (by generating DDL and executing via connection).
    """
    if models_module is None:
        # Try to load models from default location
        import sys
        from pathlib import Path
        current_dir = os.path.dirname(os.path.dirname(__file__))
        models_path = os.path.join(current_dir, "etl", "models.py")
        
        if not os.path.exists(models_path):
            raise FileNotFoundError(f"Models file not found: {models_path}")
        
        sys.path.insert(0, current_dir)
        from etl.models_loader import load_models_module
        models_module = load_models_module(models_path)
    
    # Import Base from models
    from etl.models import Base
    
    print("Creating APOLLO database schema from SQLAlchemy models...")
    
    # Check if using Lambda engine
    is_lambda = hasattr(engine, '__class__') and 'Lambda' in engine.__class__.__name__
    
    if is_lambda:
        print("Using Lambda engine - generating DDL for manual execution...")
        if conn is None:
            raise ValueError("Connection object required for Lambda schema creation")
            
        from sqlalchemy.schema import CreateTable
        from sqlalchemy.dialects import postgresql
        
        # Create tables in dependency order
        # sort_tables returns tables in dependency order (parents first)
        tables = Base.metadata.sorted_tables
        
        # Handle Enums first (Postgres specific)
        from sqlalchemy import Enum
        
        # Collect all Enums
        enums = set()
        for table in tables:
            for column in table.columns:
                if isinstance(column.type, Enum) and column.type.name:
                    enums.add(column.type)
        
        # Create Enums
        for enum in enums:
            try:
                # Manually generate CREATE TYPE SQL to avoid dependency on CreateType or bind.dialect
                # This is safer for Lambda environment
                if not enum.name:
                    continue
                    
                # Get enum values
                values = ", ".join(f"'{v}'" for v in enum.enums)
                sql = f"CREATE TYPE {enum.name} AS ENUM ({values})"
                
                conn.execute(text(sql))
                print(f"  [OK] Created type: {enum.name}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"  - Type {enum.name} already exists")
                else:
                    print(f"  [ERROR] Failed to create type {enum.name}: {e}")
                    raise e

        
        count = 0
        for table in tables:
            try:
                # Generate DDL
                ddl = CreateTable(table).compile(dialect=postgresql.dialect())
                # Execute DDL
                conn.execute(text(str(ddl)))
                print(f"  [OK] Created table: {table.name}")
                count += 1
            except Exception as e:
                # If table already exists, we might get an error, which is fine
                if "already exists" in str(e):
                    print(f"  - Table {table.name} already exists")
                else:
                    print(f"  [ERROR] Failed to create table {table.name}: {e}")
                    raise e
                    
        print(f"Database schema creation complete. Created/Verified {count} tables.")
        
    else:
        # Standard SQLAlchemy creation
        Base.metadata.create_all(engine)
        
        # Get list of created tables
        created_tables = list(Base.metadata.tables.keys())
        print(f"Database schema creation complete. Created {len(created_tables)} tables.")
        for table_name in sorted(created_tables):
            print(f"  [OK] {table_name}")


def create_database_schema_from_sql(conn: Connection, schema_file_path: str = None) -> None:
    """Create the APOLLO database schema from SQL file (legacy method)."""
    if schema_file_path is None:
        # Default to Create-APOLLO-SQL.sql in project root
        current_dir = os.path.dirname(os.path.dirname(__file__))
        schema_file_path = os.path.join(current_dir, "Create-APOLLO-SQL.sql")
    
    if not os.path.exists(schema_file_path):
        raise FileNotFoundError(f"Schema file not found: {schema_file_path}")
    
    print(f"Creating APOLLO database schema from: {schema_file_path}")
    
    with open(schema_file_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Split SQL by statements (simple approach - split by semicolon)
    statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
    
    created_tables = []
    for i, statement in enumerate(statements):
        if statement.strip():
            try:
                conn.execute(text(statement))
                # Extract table name from CREATE TABLE statements
                if 'CREATE TABLE' in statement.upper():
                    table_match = statement.upper().split('CREATE TABLE')[1].split('(')[0]
                    table_name = table_match.strip().replace('"', '').replace(' ', '')
                    created_tables.append(table_name)
                    print(f"Created table: {table_name}")
            except Exception as e:
                print(f"Warning: Statement {i+1} failed: {str(e)[:100]}...")
                # Continue with next statement - some may fail due to dependencies
    
    print(f"Database schema creation complete. Created {len(created_tables)} tables.")


def create_database_schema(conn: Connection, models_module: Optional[Any] = None, engine: Optional[Engine] = None) -> bool:
    """Create the APOLLO database schema from SQLAlchemy models.
    
    Uses models.py as the source of truth. Models module and engine are required.
    """
    if engine is None:
        raise ValueError("Engine is required to create schema from models")
    
    # Load models if not provided
    if models_module is None:
        import sys
        current_dir = os.path.dirname(os.path.dirname(__file__))
        models_path = os.path.join(current_dir, "etl", "models.py")
        
        if not os.path.exists(models_path):
            raise FileNotFoundError(f"Models file not found: {models_path}. Cannot create schema without models.py")
        
        sys.path.insert(0, current_dir)
        from etl.models_loader import load_models_module
        models_module = load_models_module(models_path)
    
    create_database_schema_from_models(engine, conn=conn, models_module=models_module)


def ensure_database_schema(conn: Connection, engine: Engine, force_recreate: bool = False, models_module: Optional[Any] = None) -> bool:
    """Ensure database schema exists, create if missing.
    
    Uses models.py as the source of truth for schema creation.
    
    Args:
        conn: Database connection
        engine: SQLAlchemy engine (required)
        force_recreate: Force recreate schema (drops existing tables)
        models_module: Optional SQLAlchemy models module (auto-loaded if not provided)
    """
    if not force_recreate and check_database_exists(conn):
        print("Database schema already exists")
        return True
    
    if force_recreate:
        print("Force recreating database schema...")
        # Note: This would drop all tables first - implement if needed
    
    try:
        create_database_schema(conn, models_module=models_module, engine=engine)
        return True
    except Exception as e:
        print(f"ERROR: Failed to create database schema: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_schema_info(conn: Connection) -> dict:
    """Get information about existing database schema."""
    try:
        # Get list of tables
        tables_result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """))
        tables = [row[0] for row in tables_result.fetchall()]
        
        # Get total row counts for each table
        table_info = {}
        for table in tables:
            try:
                count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                row_count = count_result.scalar()
                table_info[table] = {'rows': row_count}
            except Exception:
                table_info[table] = {'rows': 'Error'}
        
        return {
            'table_count': len(tables),
            'tables': table_info
        }
    except Exception as e:
        return {'error': str(e)}
