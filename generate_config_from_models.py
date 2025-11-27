#!/usr/bin/env python3
"""
Generate ETL configuration YAML files from SQLAlchemy models.py

Usage:
    python generate_config_from_models.py --models-path path/to/models.py --output-dir etl/config
"""
import argparse
import yaml
from pathlib import Path
import sys

# Add etl to path
sys.path.insert(0, str(Path(__file__).parent))

from etl.models_loader import load_models_module, get_etl_config_from_models
from etl.models_utils import get_all_models_from_module


def generate_tables_yaml(models_module, output_path: Path):
    """Generate tables.yaml from models."""
    from etl.models_utils import get_primary_keys_from_model
    
    models = get_all_models_from_module(models_module)
    tables_config = {}
    
    for table_name, model_class in models.items():
        pk = get_primary_keys_from_model(model_class)
        tables_config[table_name] = {
            'primary_key': pk
        }
    
    with open(output_path, 'w') as f:
        yaml.dump(tables_config, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Generated {output_path} with {len(tables_config)} tables")


def generate_mappings_yaml(models_module, output_path: Path, load_order: dict = None):
    """Generate mappings.yaml from models."""
    from etl.models_utils import get_column_types_from_model
    
    models = get_all_models_from_module(models_module)
    
    mappings = {
        'load_order': load_order or {
            'masters': [],
            'core': [],
            'relationship': [],
            'transactional': []
        },
        'tables': {}
    }
    
    for table_name, model_class in models.items():
        column_types = get_column_types_from_model(model_class)
        
        mappings['tables'][table_name] = {
            'target_table': table_name,
            'column_renames': {},  # User needs to fill this based on Excel
            'dtypes': column_types,
            'incremental': {
                'strategy': 'business_key_upsert'
            }
        }
    
    with open(output_path, 'w') as f:
        yaml.dump(mappings, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"✅ Generated {output_path} with {len(mappings['tables'])} tables")
    print(f"⚠️  Note: You need to fill in 'column_renames' based on your Excel column names")


def main():
    parser = argparse.ArgumentParser(
        description="Generate ETL YAML config files from SQLAlchemy models.py"
    )
    parser.add_argument(
        '--models-path',
        required=True,
        help='Path to models.py file'
    )
    parser.add_argument(
        '--output-dir',
        default='etl/config',
        help='Output directory for generated YAML files (default: etl/config)'
    )
    parser.add_argument(
        '--tables-only',
        action='store_true',
        help='Only generate tables.yaml'
    )
    parser.add_argument(
        '--mappings-only',
        action='store_true',
        help='Only generate mappings.yaml'
    )
    
    args = parser.parse_args()
    
    # Load models
    print(f"Loading models from: {args.models_path}")
    models_module = load_models_module(args.models_path)
    models = get_all_models_from_module(models_module)
    print(f"✅ Loaded {len(models)} models")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate files
    if not args.mappings_only:
        generate_tables_yaml(models_module, output_dir / 'tables.yaml')
    
    if not args.tables_only:
        generate_mappings_yaml(models_module, output_dir / 'mappings.yaml')
    
    print("\n✅ Configuration generation complete!")
    print(f"\nNext steps:")
    print(f"1. Review generated files in {output_dir}")
    print(f"2. Add 'column_renames' to mappings.yaml based on your Excel column names")
    print(f"3. Update 'load_order' in mappings.yaml to specify processing order")
    print(f"4. Run ETL with: python -m etl.run_etl --models-path {args.models_path} ...")


if __name__ == '__main__':
    main()

