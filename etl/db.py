from __future__ import annotations

import os
from typing import Dict, List, Optional, Any

from sqlalchemy import create_engine as sa_create_engine, text
from sqlalchemy.engine import Engine, Connection


def get_engine() -> Engine:
    """Create engine for direct VPC connection."""
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASS')
    dbname = os.getenv('DB_NAME', 'apollo')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT', '5432')
    
    if not all([user, password, host]):
        raise RuntimeError('Missing DB_USER, DB_PASS, or DB_HOST in environment')
    
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
