"""
Load and use SQLAlchemy models for ETL configuration.
This module provides a bridge between models.py and the ETL system.
"""
from __future__ import annotations

import os
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path

# Try to import models - user needs to provide path or we'll use a default
def load_models_module(models_path: Optional[str] = None) -> Any:
    """Load the models module from a file path or import it.
    
    Args:
        models_path: Path to models.py file, or None to try importing 'models'
    
    Returns:
        The models module
    """
    if models_path:
        # Load from file path
        models_file = Path(models_path)
        if not models_file.exists():
            raise FileNotFoundError(f"Models file not found: {models_path}")
        
        # Add parent directory to path
        sys.path.insert(0, str(models_file.parent))
        
        # Import the module
        import importlib.util
        spec = importlib.util.spec_from_file_location("models", models_path)
        models_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(models_module)
        
        return models_module
    else:
        # Try to import as a module
        try:
            import models
            return models
        except ImportError:
            # Try common locations
            project_root = Path(__file__).parent.parent
            possible_paths = [
                project_root / "models.py",
                project_root / "app" / "db" / "models" / "models.py",
                project_root / "app" / "models.py",
            ]
            
            for path in possible_paths:
                if path.exists():
                    return load_models_module(str(path))
            
            raise ImportError(
                "Could not find models.py. Please specify --models-path or place models.py in project root."
            )


def get_etl_config_from_models(models_module: Any) -> Dict[str, Any]:
    """Generate ETL configuration from models module.
    
    This creates a structure compatible with the existing YAML-based config,
    but sourced from models.py instead.
    """
    from .models_utils import (
        get_all_models_from_module,
        get_primary_keys_from_model,
        get_column_types_from_model,
        get_foreign_keys_from_model,
    )
    
    models = get_all_models_from_module(models_module)
    
    # Build tables configuration (like tables.yaml)
    tables_config = {}
    for table_name, model_class in models.items():
        tables_config[table_name] = {
            'primary_key': get_primary_keys_from_model(model_class)
        }
    
    # Build mappings configuration (like mappings.yaml)
    # Note: We still need YAML for Excel-specific mappings (column_renames, load_order)
    # But we can auto-generate the dtypes and table structure
    mappings_config = {
        'load_order': {
            'masters': [],
            'core': [],
            'relationship': [],
            'transactional': []
        },
        'tables': {}
    }
    
    for table_name, model_class in models.items():
        # Auto-generate basic table config
        column_types = get_column_types_from_model(model_class)
        
        mappings_config['tables'][table_name] = {
            'target_table': table_name,
            'column_renames': {},  # Still need YAML for Excel column name mappings
            'dtypes': column_types,
            'incremental': {
                'strategy': 'business_key_upsert'
            }
        }
    
    return {
        'tables': tables_config,
        'mappings': mappings_config,
        'models': models
    }

