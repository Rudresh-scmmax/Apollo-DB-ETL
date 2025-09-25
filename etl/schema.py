from __future__ import annotations

import os
from sqlalchemy import text
from sqlalchemy.engine import Connection


def check_database_exists(conn: Connection) -> bool:
    """Check if the APOLLO database schema exists by testing a key table."""
    try:
        result = conn.execute(text("SELECT 1 FROM currency_master LIMIT 1"))
        return True
    except Exception:
        return False


def create_database_schema(conn: Connection, schema_file_path: str = None) -> None:
    """Create the APOLLO database schema from SQL file."""
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


def ensure_database_schema(conn: Connection, force_recreate: bool = False) -> bool:
    """Ensure database schema exists, create if missing."""
    if not force_recreate and check_database_exists(conn):
        print("Database schema already exists")
        return True
    
    if force_recreate:
        print("Force recreating database schema...")
        # Note: This would drop all tables first - implement if needed
    
    try:
        create_database_schema(conn)
        return True
    except Exception as e:
        print(f"ERROR: Failed to create database schema: {e}")
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
