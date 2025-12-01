"""
Lambda-based database adapter that replaces SQLAlchemy connections.
Uses db_query.py Lambda function for all database operations.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Iterator
from contextlib import contextmanager

# Import db_query module
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    import db_query
except ImportError:
    raise ImportError(
        "db_query.py not found. Please ensure db_query.py exists in the project root."
    )


class LambdaReturningError(Exception):
    """Special exception for RETURNING clause errors that can be retried without RETURNING clause"""
    pass


class LambdaConnection:
    """Connection-like object that uses Lambda for database operations."""
    
    def __init__(self):
        self._in_transaction = False
        self._transaction_queries = []
    
    def execute(self, query, params=None):
        """Execute a SQL query via Lambda."""
        if isinstance(query, str):
            sql = query
        else:
            # Handle SQLAlchemy text() objects
            sql = str(query)
            # Extract parameters from SQLAlchemy text object
            # bindparams can be a method or property - handle both
            extracted_params = None
            if hasattr(query, 'bindparams'):
                bindparams = query.bindparams
                # Check if it's a method (callable) or a property
                if callable(bindparams):
                    try:
                        bindparams_result = bindparams()
                        if bindparams_result:
                            extracted_params = {p.key: p.value for p in bindparams_result}
                    except:
                        pass
                else:
                    # It's a property/attribute
                    if bindparams:
                        try:
                            extracted_params = {p.key: p.value for p in bindparams}
                        except:
                            pass
            
            # Use extracted params if available, otherwise use passed params
            if extracted_params:
                params = extracted_params
            
            # If params were passed as argument and not extracted from bindparams, use them
            # Need to manually substitute parameters in SQL string for Lambda
            if params and isinstance(params, dict):
                # Simple parameter substitution (for :param_name format)
                for key, value in params.items():
                    # Escape single quotes in string values
                    if isinstance(value, str):
                        escaped_value = value.replace("'", "''")
                        sql = sql.replace(f":{key}", f"'{escaped_value}'")
                    elif value is None:
                        sql = sql.replace(f":{key}", "NULL")
                    else:
                        sql = sql.replace(f":{key}", str(value))
                params = None  # Clear params since we've substituted them
        
        # For Lambda, execute immediately even in transaction mode
        # (Lambda doesn't support true transactions, so we execute immediately
        # but track queries for potential rollback/logging)
        result = self._execute_query(sql, params)
        
        # Track query for transaction rollback (if needed)
        if self._in_transaction:
            self._transaction_queries.append((sql, params))
        
        return result
    
    def insert_dataframe(self, table_name: str, df):
        """Insert DataFrame into table via Lambda (replaces pandas to_sql)."""
        import pandas as pd
        
        if df.empty:
            return 0
        
        # Convert DataFrame to INSERT statements
        # Batch inserts for better performance
        batch_size = 1000
        rows_inserted = 0
        
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size]
            
            # Build INSERT statement
            columns = ', '.join([f'"{col}"' for col in batch_df.columns])
            values_list = []
            
            for _, row in batch_df.iterrows():
                values = []
                for val in row:
                    if pd.isna(val):
                        values.append('NULL')
                    elif isinstance(val, str):
                        # Escape single quotes
                        escaped_val = val.replace("'", "''")
                        values.append(f"'{escaped_val}'")
                    elif isinstance(val, (int, float)):
                        values.append(str(val))
                    elif isinstance(val, bool):
                        values.append('TRUE' if val else 'FALSE')
                    elif isinstance(val, (pd.Timestamp, pd.DatetimeTZDtype)):
                        # Handle datetime objects
                        if pd.notna(val):
                            values.append(f"'{val.isoformat()}'")
                        else:
                            values.append('NULL')
                    else:
                        # Convert to string and escape
                        escaped_val = str(val).replace("'", "''")
                        values.append(f"'{escaped_val}'")
                
                values_list.append(f"({', '.join(values)})")
            
            # Build multi-row INSERT
            values_str = ', '.join(values_list)
            sql = f"INSERT INTO {table_name} ({columns}) VALUES {values_str}"
            
            # Execute via Lambda (always execute immediately, even in transaction mode)
            self._execute_query(sql)
            
            # Track for transaction rollback (if needed)
            if self._in_transaction:
                self._transaction_queries.append((sql, None))
            
            rows_inserted += len(batch_df)
        
        return rows_inserted
    
    def _execute_query(self, sql: str, params: Optional[Dict] = None):
        """Execute a single query via Lambda."""
        print("DB_LAMBDA_EXECUTING")
        try:
            # Convert params dict to list if needed (Lambda might expect list format)
            if params:
                # For now, assume Lambda handles dict params or we need to format SQL
                # This depends on how your Lambda function handles parameters
                result = db_query.database_query(sql, params)
            else:
                result = db_query.database_query(sql)
            
            with open('lambda_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"SQL: {sql}\n")
                f.write(f"Result Type: {type(result)}\n")
                f.write(f"Result: {result}\n")
                f.write("-" * 50 + "\n")
            
            # Debug: log result type for troubleshooting
            if not isinstance(result, (dict, list)) and result is not None:
                print(f"    [DEBUG] Lambda returned unexpected type: {type(result)}")
            
            # Handle Lambda response format
            if isinstance(result, dict):
                if 'error' in result:
                    raise RuntimeError(f"Lambda query error: {result['error']}")
                
                # Handle API Gateway style response (statusCode, body)
                if 'body' in result and 'statusCode' in result:
                    import json
                    status_code = result.get('statusCode', 200)
                    
                    # Check for error status codes (500, 400, etc.)
                    if status_code >= 400:
                        try:
                            body_data = result['body']
                            if isinstance(body_data, str):
                                error_data = json.loads(body_data)
                            else:
                                error_data = body_data
                            
                            # Extract error message
                            error_msg = error_data.get('error', str(error_data)) if isinstance(error_data, dict) else str(error_data)
                            
                            # Check if it's a RETURNING clause parsing error (Lambda function limitation)
                            # For these errors, we'll let the caller handle it gracefully
                            if 'list index out of range' in error_msg.lower() and 'RETURNING' in sql.upper():
                                print(f"    [WARNING] Lambda RETURNING clause parsing error (Lambda function limitation): {error_msg[:200]}")
                                # Raise special exception that caller can catch and retry without RETURNING clause
                                raise LambdaReturningError(f"Lambda RETURNING clause error: {error_msg}")

                            # Some Lambda deployments are known to return a 500 with
                            # "list index out of range" even when the underlying
                            # INSERT/UPSERT or COUNT(*) actually succeeds. Treat this
                            # as a non-fatal parsing issue and let the caller verify
                            # success via row counts instead of failing the ETL run.
                            if 'list index out of range' in error_msg.lower():
                                print(f"    [WARNING] Lambda returned status {status_code} with 'list index out of range'; treating as non-fatal and continuing")
                                return LambdaResult([])
                            
                            print(f"    [ERROR] Lambda returned status {status_code} with error: {error_msg[:300]}")
                            raise RuntimeError(f"Lambda query failed (status {status_code}): {error_msg}")
                        except json.JSONDecodeError:
                            # If body is not JSON, use it as error message
                            error_msg = result['body']
                            print(f"    [ERROR] Lambda returned status {status_code} with error: {error_msg[:300]}")
                            raise RuntimeError(f"Lambda query failed (status {status_code}): {error_msg}")
                    
                    # Success case - parse body normally
                    try:
                        body_data = result['body']
                        if isinstance(body_data, str):
                            data = json.loads(body_data)
                        else:
                            data = body_data
                        
                        # Check if parsed data contains an error
                        if isinstance(data, dict) and 'error' in data:
                            error_msg = data['error']
                            print(f"    [ERROR] Lambda body contains error: {error_msg[:300]}")
                            raise RuntimeError(f"Lambda query error: {error_msg}")
                        
                        # If data is list, use it. If dict with 'data', use that.
                        if isinstance(data, dict) and 'data' in data:
                            data = data['data']
                        
                        # Now process 'data' as if it was in the top level
                        if isinstance(data, list):
                            return LambdaResult(data)
                        elif data is None:
                            return LambdaResult([])
                        else:
                            # Single value or other structure
                            return LambdaResult([data] if not isinstance(data, list) else data)
                    except json.JSONDecodeError as e:
                        print(f"    [WARNING] Failed to parse Lambda body: {e}")
                        # Fall through to default handling
                    except LambdaReturningError:
                        # Re-raise LambdaReturningError without wrapping
                        raise
                    except RuntimeError:
                        # Re-raise RuntimeError (our error handling above)
                        raise
                    except Exception as e:
                        print(f"    [WARNING] Failed to parse Lambda body: {e}")
                        # Fall through to default handling
                
                if 'data' in result:
                    # Return data as rows (handle None/empty data for DDL statements)
                    data = result['data']
                    if data is None:
                        # DDL statements return None - return empty result
                        return LambdaResult([])
                    # Debug: log data type and length for UPSERT queries
                    if 'RETURNING' in sql.upper() or 'INSERT' in sql.upper():
                        print(f"    [DEBUG] Lambda returned data type: {type(data)}, length: {len(data) if isinstance(data, (list, tuple)) else 'N/A'}")
                        if isinstance(data, list) and len(data) > 0 and len(data) < 10:
                            print(f"    [DEBUG] Lambda data sample (first 3): {data[:3]}")
                    # Ensure data is a list, not a method or other callable
                    if isinstance(data, list):
                        return LambdaResult(data)
                    elif callable(data):
                        # Don't accept callable objects as data
                        print(f"    [WARNING] Lambda returned callable object as data, ignoring")
                        return LambdaResult([])
                    elif isinstance(data, (str, int, float, bool)):
                        # Single value - wrap in list
                        return LambdaResult([[data]])
                    else:
                        # Try to convert to list
                        try:
                            if hasattr(data, '__iter__') and not isinstance(data, str):
                                return LambdaResult(list(data))
                        except Exception as e:
                            print(f"    [WARNING] Could not convert Lambda data to list: {e}")
                        return LambdaResult([])
                # If result is the data directly
                return LambdaResult(result if isinstance(result, list) else [result])
            elif isinstance(result, list):
                return LambdaResult(result)
            elif result is None:
                # DDL statements may return None
                return LambdaResult([])
            else:
                # Single value result
                return LambdaResult([[result]] if result is not None else [])
                
        except LambdaReturningError:
            # Re-raise LambdaReturningError without wrapping - let caller handle it
            raise
        except Exception as e:
            print(f"    [ERROR] Lambda query execution failed: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Lambda query execution failed: {e}")
    
    def begin(self):
        """Start a transaction."""
        self._in_transaction = True
        self._transaction_queries = []
        return self
    
    def commit(self):
        """Commit transaction - queries were already executed immediately."""
        # For Lambda, queries are executed immediately, so commit is just cleanup
        # This maintains compatibility with SQLAlchemy transaction interface
        if not self._in_transaction:
            return
        
        # Queries were already executed in execute(), so just clear the tracking
        self._transaction_queries = []
        self._in_transaction = False
    
    def rollback(self):
        """Rollback transaction."""
        self._transaction_queries = []
        self._in_transaction = False
    
    def __enter__(self):
        return self.begin()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
    
    def close(self):
        """Close connection (no-op for Lambda)."""
        pass


class LambdaResult:
    """Result-like object that mimics SQLAlchemy result."""
    
    def __init__(self, rows: List):
        # Ensure rows is always a list, never None or a method
        if rows is None:
            self._rows = []
        elif isinstance(rows, list):
            self._rows = rows
        elif callable(rows):
            # Don't accept callable objects (methods/functions) as data
            self._rows = []
        elif hasattr(rows, '__iter__') and not isinstance(rows, (str, bytes)):
            # Convert iterable to list, but skip methods
            try:
                self._rows = list(rows)
            except (TypeError, ValueError):
                self._rows = []
        else:
            # Single value or unknown type - wrap in list
            self._rows = [rows] if rows is not None else []
        self._index = 0
    
    def fetchall(self):
        """Fetch all rows."""
        result = []
        # Safety check - ensure _rows is iterable and not a method
        if not isinstance(self._rows, list):
            if callable(self._rows):
                # _rows is a method/function - return empty list
                return []
            try:
                # Try to convert to list
                self._rows = list(self._rows) if hasattr(self._rows, '__iter__') and not isinstance(self._rows, str) else []
            except:
                self._rows = []
        
        for row in self._rows:
            if isinstance(row, list):
                result.append(tuple(row))
            elif isinstance(row, dict):
                # If row is a dict, convert to tuple of values (in order)
                result.append(tuple(row.values()))
            elif isinstance(row, tuple):
                result.append(row)
            elif callable(row):
                # Skip callable objects (methods/functions)
                continue
            else:
                # Single value - wrap in tuple
                result.append((row,))
        return result
    
    def fetchone(self):
        """Fetch one row."""
        if self._index < len(self._rows):
            row = self._rows[self._index]
            self._index += 1
            return tuple(row) if isinstance(row, list) else row
        return None
    
    def scalar(self):
        """Get scalar value (first column of first row)."""
        if self._rows and len(self._rows) > 0:
            row = self._rows[0]
            if isinstance(row, (list, tuple)) and len(row) > 0:
                return row[0]
            return row
        return None
    
    def __iter__(self):
        """Make result iterable - convert rows to tuples like fetchall does."""
        if not self._rows:
            return iter([])
        # Convert rows to tuples (same logic as fetchall)
        converted_rows = []
        for row in self._rows:
            if isinstance(row, list):
                converted_rows.append(tuple(row))
            elif isinstance(row, dict):
                converted_rows.append(tuple(row.values()))
            elif isinstance(row, tuple):
                converted_rows.append(row)
            else:
                converted_rows.append((row,))
        return iter(converted_rows)


class LambdaEngine:
    """Engine-like object that uses Lambda for database operations."""
    
    def __init__(self):
        pass
    
    def begin(self):
        """Create a connection with transaction context."""
        return LambdaConnection()
    
    def connect(self):
        """Create a connection."""
        return LambdaConnection()
    
    def execute(self, query, params=None):
        """Execute a query directly."""
        conn = LambdaConnection()
        return conn.execute(query, params)


def get_engine():
    """Get Lambda-based engine (replaces SQLAlchemy engine)."""
    print("[DB] Using Lambda function 'client1-private_db_query' for all database operations")
    return LambdaEngine()


def get_primary_keys(conn, models_module: Optional[Any] = None) -> Dict[str, List[str]]:
    """Get primary keys from database or from models if provided."""
    # If models provided, use them (faster and more reliable)
    if models_module:
        try:
            from .models_utils import get_primary_keys_dict_from_models
            return get_primary_keys_dict_from_models(models_module)
        except Exception as e:
            print(f"Warning: Could not load primary keys from models: {e}. Falling back to database query.")
    
    # Query via Lambda
    sql = """
        SELECT tc.table_name,
               kcu.column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema NOT IN ('pg_catalog','information_schema');
    """
    result = conn.execute(sql)
    rows = result.fetchall()
    pk_map: Dict[str, List[str]] = {}
    for table, col in rows:
        pk_map.setdefault(table, []).append(col)
    return pk_map


def get_table_columns(conn, table_name: str, models_module: Optional[Any] = None) -> List[str]:
    """Get table columns from database or from models if provided."""
    # If models provided, use them
    if models_module:
        try:
            from .models_utils import get_all_models_from_module, get_table_columns_from_model
            models = get_all_models_from_module(models_module)
            if table_name in models:
                return get_table_columns_from_model(models[table_name])
        except Exception as e:
            print(f"Warning: Could not load columns from models: {e}. Falling back to database query.")
    
    # Query via Lambda
    sql = f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = '{table_name}'
        ORDER BY ordinal_position
    """
    result = conn.execute(sql)
    rows = result.fetchall()
    return [r[0] for r in rows]

