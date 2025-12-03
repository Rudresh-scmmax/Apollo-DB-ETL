"""
Utilities to extract schema information from SQLAlchemy models.
This allows the ETL to use models.py as the single source of truth.
"""
from __future__ import annotations

import inspect
from typing import Dict, List, Optional, Type, Any
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Numeric, Text, Enum
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm.decl_api import DeclarativeMeta

# Import your models - adjust the import path as needed
try:
    # Try to import from a models module
    # You may need to adjust this path based on where your models.py is located
    import sys
    import os
    # Add the path where models.py might be located
    # For now, we'll create a function that accepts the models module
    pass
except ImportError:
    pass


def get_primary_keys_from_model(model_class: Type[DeclarativeBase]) -> List[str]:
    """Extract primary key column names from a SQLAlchemy model."""
    # Most reliable: Use the table's primary key columns
    if hasattr(model_class, '__table__') and model_class.__table__.primary_key:
        return [col.name for col in model_class.__table__.primary_key.columns]
    
    # Fallback: Check mapped columns
    pk_cols = []
    for attr_name in dir(model_class):
        attr = getattr(model_class, attr_name, None)
        if hasattr(attr, 'property') and hasattr(attr.property, 'columns'):
            for col in attr.property.columns:
                if col.primary_key:
                    pk_cols.append(col.name)
    
    return pk_cols


def get_column_types_from_model(model_class: Type[DeclarativeBase]) -> Dict[str, str]:
    """Extract column names and Python types from a SQLAlchemy model."""
    type_map = {}
    
    if not hasattr(model_class, '__table__'):
        return type_map
    
    for column in model_class.__table__.columns:
        col_name = column.name
        col_type = column.type
        
        # Map SQLAlchemy types to Python/ETL types
        if isinstance(col_type, (Integer,)):
            type_map[col_name] = 'int'
        elif isinstance(col_type, (Numeric,)):
            type_map[col_name] = 'float'
        elif isinstance(col_type, (Date,)):
            type_map[col_name] = 'date'
        elif isinstance(col_type, (DateTime,)):
            type_map[col_name] = 'date'  # DateTime treated as date for ETL
        elif isinstance(col_type, (Boolean,)):
            type_map[col_name] = 'bool'
        elif isinstance(col_type, (JSONB,)):
            type_map[col_name] = 'dict'
        elif isinstance(col_type, (String, Text, Enum)):
            type_map[col_name] = 'str'
        else:
            # Default to string for unknown types
            type_map[col_name] = 'str'
    
    return type_map


def get_table_name_from_model(model_class: Type[DeclarativeBase]) -> str:
    """Get the database table name from a SQLAlchemy model."""
    if hasattr(model_class, '__tablename__'):
        return model_class.__tablename__
    return model_class.__name__.lower()


def get_foreign_keys_from_model(model_class: Type[DeclarativeBase]) -> List[tuple]:
    """Extract foreign key relationships from a SQLAlchemy model.
    
    Returns list of tuples: (fk_column, referenced_table, referenced_column)
    """
    fk_list = []
    
    if not hasattr(model_class, '__table__'):
        return fk_list
    
    for fk in model_class.__table__.foreign_keys:
        fk_col = fk.parent.name
        ref_table = fk.column.table.name
        ref_col = fk.column.name
        fk_list.append((fk_col, ref_table, ref_col))
    
    return fk_list


def get_all_models_from_module(models_module: Any) -> Dict[str, Type[DeclarativeBase]]:
    """Extract all SQLAlchemy model classes from a module.
    
    Returns dict mapping table_name -> model_class
    """
    models = {}
    
    for name, obj in inspect.getmembers(models_module):
        if (inspect.isclass(obj) and 
            issubclass(obj, DeclarativeBase) and 
            obj is not DeclarativeBase and
            hasattr(obj, '__tablename__')):
            table_name = obj.__tablename__
            models[table_name] = obj
    
    return models


def build_schema_from_models(models_module: Any) -> Dict[str, Dict[str, Any]]:
    """Build complete schema information from models module.
    
    Returns:
        {
            'table_name': {
                'primary_key': ['col1', 'col2'],
                'columns': ['col1', 'col2', ...],
                'types': {'col1': 'int', 'col2': 'str', ...},
                'foreign_keys': [('fk_col', 'ref_table', 'ref_col'), ...]
            },
            ...
        }
    """
    schema = {}
    models = get_all_models_from_module(models_module)
    
    for table_name, model_class in models.items():
        schema[table_name] = {
            'primary_key': get_primary_keys_from_model(model_class),
            'columns': [col.name for col in model_class.__table__.columns],
            'types': get_column_types_from_model(model_class),
            'foreign_keys': get_foreign_keys_from_model(model_class),
            'model_class': model_class
        }
    
    return schema


def get_primary_keys_dict_from_models(models_module: Any) -> Dict[str, List[str]]:
    """Get primary keys dictionary compatible with current ETL code.
    
    Returns: {'table_name': ['pk_col1', 'pk_col2'], ...}
    """
    models = get_all_models_from_module(models_module)
    pk_dict = {}
    
    for table_name, model_class in models.items():
        pk_dict[table_name] = get_primary_keys_from_model(model_class)
    
    return pk_dict


def get_table_columns_from_model(model_class: Type[DeclarativeBase]) -> List[str]:
    """Get list of column names from a model."""
    if not hasattr(model_class, '__table__'):
        return []
    return [col.name for col in model_class.__table__.columns]


def get_fk_dependency_order(models_module: Any) -> List[str]:
    """Build topological sort of tables based on FK dependencies.
    
    Returns list of table names in order: tables with no dependencies first,
    then tables that depend on them, etc.
    """
    models = get_all_models_from_module(models_module)
    
    # Build dependency graph: table -> set of tables it depends on
    dependencies = {}
    for table_name, model_class in models.items():
        fks = get_foreign_keys_from_model(model_class)
        deps = set()
        for fk_col, ref_table, ref_col in fks:
            # Ignore self-references (they're handled by database)
            if ref_table != table_name and ref_table in models:
                deps.add(ref_table)
        dependencies[table_name] = deps
    
    # Topological sort using DFS
    sorted_tables = []
    visited = set()
    visiting = set()  # For cycle detection
    
    def visit(table):
        if table in visited:
            return
        if table in visiting:
            # Cycle detected - this is OK, database handles it
            # Just mark as visited and continue
            visited.add(table)
            return
        
        visiting.add(table)
        for dep in dependencies.get(table, []):
            if dep in models:
                visit(dep)
        visiting.remove(table)
        visited.add(table)
        sorted_tables.append(table)
    
    # Visit all tables
    for table in sorted(models.keys()):  # Sort for deterministic order
        visit(table)
    
    return sorted_tables

