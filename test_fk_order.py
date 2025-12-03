import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from etl.models_loader import load_models_module
from etl.models_utils import get_fk_dependency_order

# Load models
models_module = load_models_module("etl/models.py")

# Get FK dependency order
ordered_tables = get_fk_dependency_order(models_module)

print(f"Total tables: {len(ordered_tables)}")
print("\nFK Dependency Order (first 30 tables):")
print("=" * 80)
for i, table in enumerate(ordered_tables[:30], 1):
    print(f"{i:3d}. {table}")

print(f"\n... and {len(ordered_tables) - 30} more tables")

# Check if master tables are early in the list
master_tables = ['currency_master', 'uom_master', 'material_type_master', 'location_type_master', 'material_master']
print("\nPositions of key master tables:")
print("=" * 80)
for table in master_tables:
    if table in ordered_tables:
        pos = ordered_tables.index(table) + 1
        print(f"{table:30s} -> Position {pos:3d}")
