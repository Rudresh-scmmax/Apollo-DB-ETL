from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

from sqlalchemy import create_engine as sa_create_engine, text
from sqlalchemy.engine import Engine, Connection


def get_engine() -> Engine:
    """Create engine for database connection.
    
    If USE_DB_QUERY_LAMBDA is set to 'true', uses Lambda function for all operations.
    Otherwise, uses direct VPC connection (requires DB_USER, DB_PASS, DB_HOST).
    """
    # Check if we should use db_query.py Lambda function for ALL operations
    use_lambda = os.getenv('USE_DB_QUERY_LAMBDA', 'false').lower() == 'true'
    
    if use_lambda:
        # Use Lambda-based database adapter
        try:
            from .db_lambda import get_engine as get_lambda_engine
            return get_lambda_engine()
        except ImportError as e:
            raise RuntimeError(
                f"Failed to import Lambda database adapter: {e}. "
                "Ensure db_query.py exists in project root."
            )
    
    # Use direct connection (requires DB credentials)
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASS')
    dbname = os.getenv('DB_NAME', 'apollo')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT', '5432')
    
    if not all([user, password, host]):
        raise RuntimeError(
            'Missing DB_USER, DB_PASS, or DB_HOST in environment. '
            'Set USE_DB_QUERY_LAMBDA=true to use Lambda function instead.'
        )
    
    dsn = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}'
    return sa_create_engine(dsn, pool_pre_ping=True)


def get_primary_keys(conn: Connection, models_module: Optional[Any] = None) -> Dict[str, List[str]]:
    """Get primary keys from database or from models if provided.
    
    Args:
        conn: Database connection
        models_module: Optional SQLAlchemy models module. If provided, uses models instead of querying DB.
    
    Returns:
        Dict mapping table_name -> list of primary key column names
    """
    # Check if using Lambda connection - delegate to Lambda version
    if hasattr(conn, '__class__') and 'Lambda' in conn.__class__.__name__:
        try:
            from .db_lambda import get_primary_keys as get_lambda_primary_keys
            return get_lambda_primary_keys(conn, models_module)
        except ImportError:
            pass  # Fall through to regular implementation
    
    # If models provided, use them (faster and more reliable)
    if models_module:
        try:
            from .models_utils import get_primary_keys_dict_from_models
            return get_primary_keys_dict_from_models(models_module)
        except Exception as e:
            print(f"Warning: Could not load primary keys from models: {e}. Falling back to database query.")
    
    # Fallback to database query
    sql = text(
        """
        SELECT tc.table_name,
               kcu.column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema NOT IN ('pg_catalog','information_schema');
        """
    )
    rows = conn.execute(sql).fetchall()
    pk_map: Dict[str, List[str]] = {}
    for table, col in rows:
        pk_map.setdefault(table, []).append(col)
    return pk_map


def get_table_columns(conn: Connection, table_name: str, models_module: Optional[Any] = None) -> List[str]:
    """Get table columns from database or from models if provided.
    
    Args:
        conn: Database connection
        table_name: Name of the table
        models_module: Optional SQLAlchemy models module. If provided, uses models instead of querying DB.
    
    Returns:
        List of column names
    """
    # Check if using Lambda connection - delegate to Lambda version
    if hasattr(conn, '__class__') and 'Lambda' in conn.__class__.__name__:
        try:
            from .db_lambda import get_table_columns as get_lambda_table_columns
            return get_lambda_table_columns(conn, table_name, models_module)
        except ImportError:
            pass  # Fall through to regular implementation
    
    # If models provided, use them
    if models_module:
        try:
            from .models_utils import get_all_models_from_module, get_table_columns_from_model
            models = get_all_models_from_module(models_module)
            if table_name in models:
                return get_table_columns_from_model(models[table_name])
        except Exception as e:
            print(f"Warning: Could not load columns from models: {e}. Falling back to database query.")
    
    # Fallback to database query
    sql = text(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = :t
        ORDER BY ordinal_position
        """
    )
    rows = conn.execute(sql, {"t": table_name}).fetchall()
    return [r[0] for r in rows]
